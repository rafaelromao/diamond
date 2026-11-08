"""Nominal checks for the wired XIAO option; not a physical fit qualification."""
import unittest
from pathlib import Path
import json
import re

from trackball import trackball as B
from trackball.controller_pinout import SIGNALS, gpio, pin_description
from trackball.controllers import xiao, xiao_usb_z
from trackpad import trackpad as T
import module_shell as M
import dock as K


class XiaoOptionTest(unittest.TestCase):
    def test_all_signal_pins_match_each_firmware_overlay(self):
        for kind, controllers in SIGNALS.items():
            for controller, signals in controllers.items():
                name = 'slim_diamond_' + kind + ('_xiao' if controller == 'xiao' else '')
                text = (Path('zmk/boards/shields') / name / (name + '.overlay')).read_text()
                with self.subTest(shield=name):
                    pins = [gpio(kind, controller, signal) for signal in signals]
                    self.assertEqual(len(pins), len(set(pins)))
                    keys = re.search(r'input-gpios\s*=\s*(.*?);', text, re.S).group(1)
                    self.assertEqual([(int(p), int(n)) for p, n in re.findall(r'&gpio(\d) (\d+) ', keys)],
                                     [gpio(kind, controller, key) for key in ('K1', 'K2')])
                    bus = ({'SPIM_SCK': 'SCLK', 'SPIM_MOSI': 'SDIO', 'SPIM_MISO': 'SDIO'}
                           if kind == 'trackball' else {'TWIM_SDA': 'SDA', 'TWIM_SCL': 'SCL'})
                    for function, signal in bus.items():
                        port, pin = gpio(kind, controller, signal)
                        self.assertEqual(text.count(f'NRF_PSEL({function}, {port}, {pin})'), 2)
                    props = [('irq-gpios', 'MOTION'), ('cs-gpios', 'NCS')] if kind == 'trackball' else [('data-ready-gpios', 'DR')]
                    for prop, signal in props:
                        port, pin = gpio(kind, controller, signal)
                        self.assertRegex(text, rf'{prop} = <&gpio{port} {pin} ')

    def test_only_one_panel_is_advertised(self):
        self.assertFalse(Path('trackball/pcb_xiao/trackball_xiao.kicad_pcb').exists())
        self.assertFalse(Path('trackball/fab/trackball_xiao_jlcpcb.zip').exists())
        for path in ('BOM.md', 'BUILD.md', 'README.md', 'build-log.html'):
            with self.subTest(path=path):
                text = Path(path).read_text()
                self.assertNotIn('trackball_xiao_jlcpcb.zip', text)
                self.assertNotIn('XIAO-labelled', text)

    def test_build_tables_match_both_complete_signal_maps(self):
        guide = Path('BUILD.md').read_text()
        for kind, controllers in SIGNALS.items():
            head = '| Pad |' if kind == 'trackball' else '| Trackpad signal |'
            table = guide.split(head, 1)[1].split('\n\n', 1)[0]
            for signal in controllers['nice_nano']:
                nice = pin_description(kind, 'nice_nano', signal)
                xiao_pin = pin_description(kind, 'xiao', signal)
                with self.subTest(module=kind, signal=signal):
                    self.assertIn(f'| {nice} | {xiao_pin} |', table)

    def test_xiao_shields_release_i2c_key_pin(self):
        for kind in ('trackball', 'trackpad'):
            name = 'slim_diamond_' + kind + '_xiao'
            overlay = (Path('zmk/boards/shields') / name / (name + '.overlay')).read_text()
            with self.subTest(shield=name):
                self.assertIn('&uart0 { status = "disabled"; };', overlay)
                if kind == 'trackball':
                    self.assertIn('&i2c1 { status = "disabled"; };', overlay)
                    self.assertIn('NRF_PSEL(SPIM_SCK, 0, 4)', overlay)
                else:
                    self.assertNotIn('&i2c1 { status = "disabled"; };', overlay)
                    self.assertIn('reg = <0x2a>;', overlay)

    def test_trackpads_enable_active_high_data_ready_and_primary_tap(self):
        for suffix, port, pin in (('', 0, 22), ('_xiao', 1, 11)):
            name = 'slim_diamond_trackpad' + suffix
            overlay = (Path('zmk/boards/shields') / name / (name + '.overlay')).read_text()
            with self.subTest(shield=name):
                self.assertIn(f'data-ready-gpios = <&gpio{port} {pin} GPIO_ACTIVE_HIGH>;', overlay)
                self.assertIn('primary-tap-enable;', overlay)

    def test_reference_xiao_clears_parts_and_uses_the_same_usb_opening(self):
        layout = B.place()
        tray = B.tray(layout)
        back = B.xiao_back(layout)
        floor = B.SOCKET_BOT - B.NANO_GAP - B.NANO[2]
        controller = xiao(back, floor)
        self.assertAlmostEqual(controller.bounding_box()[4], back, places=5)
        self.assertAlmostEqual(xiao_usb_z(floor), B.usb_z(layout), delta=.01)
        self.assertGreaterEqual(B.SOCKET_BOT - controller.bounding_box()[5], 1.3)    # a soldered wire fits
        self.assertLess(abs((controller ^ tray).volume()), 1e-3)
        main, sensor = B.main_board_plan(layout), B.sensor_board_plan(layout)
        for kind in ('mx', 'choc', 'trackpad'):
            parts = B.parts(layout, main, sensor, kind) if kind != 'trackpad' else T.parts(T.place(), main, sensor)
            lid = B.lid(layout, kind) if kind != 'trackpad' else T.lid(T.place())
            with self.subTest(module=kind):
                self.assertLess(abs((controller ^ lid).volume()), 1e-3)
                for name, part in parts:
                    if name not in ('nice!nano', 'controller header'):
                        self.assertLess(abs((controller ^ part).volume()), 1e-3, name)
                _, body, cable = M.usb_connection(back, xiao_usb_z(floor))
                self.assertLess(abs(((body + cable) ^ (lid + tray)).volume()), 1e-3)
        dock = K.make()
        self.assertLess(abs(((body + cable).translate((0, 0, M.FLOOR_Z)) ^ dock.solid).volume()), 1e-3)

    def test_the_board_rests_on_seats_between_printed_stops(self):
        layout = B.place()
        tray = B.tray(layout)
        top = B.controller_top()
        seat = top - B.CB_T
        plan = B.controller_board_plan()
        board = M.extrude(plan, seat, top)
        self.assertLess(abs((board ^ tray).volume()), 1e-3)
        self.assertGreater((M.extrude(plan, seat - .1, seat) ^ tray).volume(), 1.5)   # it rests on the seats
        forward = board.translate((0, -.5, 0))
        backward = board.translate((0, .6, 0))
        self.assertGreater((forward ^ tray).volume(), .1)                             # a plug's push stops here
        self.assertGreater((backward ^ tray).volume(), .1)                            # and its pull here

    def test_header_rows_are_the_nice_nanos_and_a_xiaos_after_its_setback(self):
        layout = B.place()
        self.assertAlmostEqual(B.pin_y(layout, 1), -18.95, places=2)
        self.assertAlmostEqual(B.pin_y(layout, 7), -34.19, places=2)
        xiao_row_1 = B.xiao_back(layout) - 1.527 - 20.955 / 2 + 3 * 2.54
        self.assertAlmostEqual(xiao_row_1, B.pin_y(layout, 1), places=2)
        points = B.controller_points(layout)
        plan = B.controller_board_plan()
        for name, pin in points["pins"].items():
            self.assertTrue(plan.contains(B.Point(*pin["xy"]).buffer(1.15)), name)
        for name, link in points["links"].items():
            self.assertTrue(plan.contains(B.Point(*link["xy"]).buffer(1.15)), name)

    def test_stacking_pins_pass_beside_either_controller_and_meet_the_main_board(self):
        layout = B.place()
        main = B.main_board_plan(layout)
        floor = B.SOCKET_BOT - B.NANO_GAP - B.NANO[2]
        over = B.PCB_TOP - B.controller_top() + B.CB_T
        self.assertLess(over, B.LINK_PIN)                      # an extra-long pin passes through both boards
        board = dict(B.parts(layout, main, B.sensor_board_plan(layout)))
        pins = M.extrude(B.unary_union([B.Point(*l["xy"]).buffer(.45) for l in B.controller_points(layout)["links"].values()]),
                         B.controller_top() - B.CB_T, B.PCB_TOP)
        self.assertLess(abs((pins ^ xiao(B.xiao_back(layout), floor)).volume()), 1e-3)
        self.assertLess(abs((pins ^ board['nice!nano']).volume()), 1e-3)
        self.assertLess(abs((pins ^ B.tray(layout)).volume()), 1e-3)
        for name in ('battery', 'socket 1', 'socket 2'):
            self.assertLess(abs((pins ^ board[name]).volume()), 1e-3, name)
        pads = B.board_layout(layout, main)
        plastic = board["stacking pins' plastic"]
        for lid in (B.lid(layout, 'mx'), B.lid(layout, 'choc')):
            for link in B.controller_points(layout)["links"].values():
                joint = M.extrude(B.Point(*link["xy"]).buffer(.8), B.PCB_TOP, B.PCB_TOP + .7)
                self.assertLess(abs((joint ^ lid).volume()), 1e-3)
        for x, y in pads["wires"] + pads["controller"]:              # a wire reaches every hole from below
            hole = M.extrude(B.Point(x, y).buffer(.5), B.PCB_TOP - B.PCB_T - 3, B.PCB_TOP)
            self.assertLess(abs((hole ^ plastic).volume()), 1e-3, (x, y))

    def test_the_wiring_diagrams_draw_the_module_frame_not_the_panel(self):
        design = json.loads(Path('trackball/design.json').read_text())
        layout = B.place()
        plan = design['controller_plan']
        self.assertEqual(plan['pins']['L3'], [-7.62, round(B.pin_y(layout, 3), 4)])
        self.assertGreater(plan['pins']['L3'][1], plan['pins']['L7'][1])      # the USB end is up
        self.assertLess(max(abs(x) for x, _ in plan['outline']), 13.5)
        source = Path('trackball/controller_diagram.py').read_text()
        self.assertIn('D["controller_plan"]', source)
        self.assertNotIn('D["controller_pins"]', source)
        self.assertNotIn('D["controller_board"]', source)

    def test_the_routed_boards_stacking_holes_coincide(self):
        # Written by check_controller_pcb.py from the routed board, the panel's turn and offset undone.
        import hashlib
        data = json.loads(Path('trackball/pcb/stack_alignment.json').read_text())
        board = hashlib.sha256(Path('trackball/pcb/trackball.kicad_pcb').read_bytes()).hexdigest()
        self.assertEqual(data['board'], board, 'measured on a different board: rerun check_controller_pcb.py')
        pairs = data['pairs']
        self.assertEqual(len(pairs), 8)
        for name, pair in pairs.items():
            with self.subTest(hole=name):
                self.assertLess(pair['offset'], 1e-3)
                self.assertEqual(pair['main_net'], pair['net'])
                self.assertEqual(pair['controller_net'], 'M_' + dict(NCS='CS', SCLK='CK', SDIO='IO', MOTION='MO', VCC='3V').get(pair['net'], pair['net']))

    def test_either_controller_stands_clear_of_its_board_and_header(self):
        layout = B.place()
        top = B.controller_top()
        board = M.extrude(B.controller_board_plan(), top - B.CB_T, top)
        floor = B.SOCKET_BOT - B.NANO_GAP - B.NANO[2]
        self.assertAlmostEqual(top + B.HEADER_T, floor)
        main, sensor = B.main_board_plan(layout), B.sensor_board_plan(layout)
        parts = dict(B.parts(layout, main, sensor))
        self.assertLess(abs((xiao(B.xiao_back(layout), floor) ^ board).volume()), 1e-3)
        self.assertLess(abs((parts['nice!nano'] ^ board).volume()), 1e-3)
        self.assertGreater(parts['controller board'].bounding_box()[2], B.BAT_Z + B.BAT[2] - .4)
        self.assertLess(abs((parts['controller board'] ^ parts['battery']).volume()), 1e-3)

    def test_the_stack_tilts_in_past_its_stops(self):
        from manifold3d import Manifold
        layout = B.place()
        tray = B.tray(layout)
        floor = B.SOCKET_BOT - B.NANO_GAP - B.NANO[2]
        top = B.controller_top()
        board = M.extrude(B.controller_board_plan(), top - B.CB_T, top)
        parts = dict(B.parts(layout, B.main_board_plan(layout), B.sensor_board_plan(layout)))
        nano = parts['nice!nano']
        board = board + parts['controller header'] + parts["stacking pins' plastic"] + B.stacking_pins(layout)
        for name, stack in (('xiao', xiao(B.xiao_back(layout), floor) + board), ('nano', nano + board)):
            tilted = lambda a: stack.translate((0, 16, -15.4)).rotate((-a, 0, 0)).translate((0, -16, 15.4))
            for tenths in range(0, 181, 30):
                with self.subTest(stack=name, angle=tenths / 10):
                    self.assertLess(abs((tilted(tenths / 10) ^ tray).volume()), .02)
            # At that angle: forward, out of the wall's pockets, then straight up and out.
            for dy, dz in [(-i * .5, 0) for i in range(7)] + [(-3.0, i * 3) for i in range(11)]:
                with self.subTest(stack=name, offset=(dy, dz)):
                    self.assertLess(abs((tilted(18).translate((0, dy, dz)) ^ tray).volume()), .02)


if __name__ == "__main__":
    unittest.main()
