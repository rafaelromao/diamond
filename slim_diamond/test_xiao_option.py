"""Nominal checks for the wired XIAO option; not a physical fit qualification."""
import unittest
from pathlib import Path
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
            table = guide.split(f'| {kind.capitalize()} signal |', 1)[1].split('\n\n', 1)[0]
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
                if kind == 'trackball':
                    self.assertIn('&i2c1 { status = "disabled"; };', overlay)
                    self.assertIn('<&gpio0 4 (GPIO_ACTIVE_LOW | GPIO_PULL_UP)>', overlay)
                else:
                    self.assertNotIn('&i2c1 { status = "disabled"; };', overlay)
                    self.assertIn('<&gpio0 3 (GPIO_ACTIVE_LOW | GPIO_PULL_UP)>', overlay)
                    self.assertIn('reg = <0x2a>;', overlay)

    def test_trackpads_enable_active_high_data_ready_and_primary_tap(self):
        for suffix, gpio in (('', 11), ('_xiao', 28)):
            name = 'slim_diamond_trackpad' + suffix
            overlay = (Path('zmk/boards/shields') / name / (name + '.overlay')).read_text()
            with self.subTest(shield=name):
                self.assertIn(f'data-ready-gpios = <&gpio0 {gpio} GPIO_ACTIVE_HIGH>;', overlay)
                self.assertIn('primary-tap-enable;', overlay)

    def test_reference_xiao_clears_parts_and_uses_the_same_usb_opening(self):
        layout = B.place()
        tray = B.tray(layout)
        back = layout["back"]
        floor = B.SOCKET_BOT - B.NANO_GAP - B.NANO[2]
        controller = xiao(back, floor)
        self.assertAlmostEqual(controller.bounding_box()[4], back, places=5)
        self.assertAlmostEqual(xiao_usb_z(floor), B.usb_z(layout), delta=.01)
        self.assertGreaterEqual(B.SOCKET_BOT - controller.bounding_box()[5], .35 - 1e-5)
        self.assertLess(abs((controller ^ tray).volume()), 1e-3)
        main, sensor = B.main_board_plan(layout), B.sensor_board_plan(layout)
        for kind in ('mx', 'choc', 'trackpad'):
            parts = B.parts(layout, main, sensor, kind) if kind != 'trackpad' else T.parts(T.place(), main, sensor)
            lid = B.lid(layout, kind) if kind != 'trackpad' else T.lid(T.place())
            with self.subTest(module=kind):
                self.assertLess(abs((controller ^ lid).volume()), 1e-3)
                for name, part in parts:
                    if name != 'nice!nano':
                        self.assertLess(abs((controller ^ part).volume()), 1e-3, name)
                _, body, cable = M.usb_connection(back, xiao_usb_z(floor))
                self.assertLess(abs(((body + cable) ^ (lid + tray)).volume()), 1e-3)
        dock = K.make()
        self.assertLess(abs(((body + cable).translate((0, 0, M.FLOOR_Z)) ^ dock.solid).volume()), 1e-3)
        # Bare reference component model only: wires, tape and clone variations aren't certified.
        for side in (-1, 1):
            probe = B.box3(side * 8.2 - .3, back - 8.0, floor - .2,
                           side * 8.2 + .3, back - 7.0, floor)
            self.assertGreater((probe ^ tray).volume(), .1)

    def test_xiao_reference_can_be_inserted(self):
        layout = B.place()
        tray = B.tray(layout)
        controller = xiao(layout['back'], B.SOCKET_BOT - B.NANO_GAP - B.NANO[2])
        path = [(-3.2, z * .5) for z in range(80, -1, -1)] + [(-3.2 + i * .1, 0) for i in range(33)]
        for dy, dz in path:
            with self.subTest(offset=(dy, dz)):
                self.assertLess(abs((controller.translate((0, dy, dz)) ^ tray).volume()), 1e-3)


if __name__ == "__main__":
    unittest.main()
