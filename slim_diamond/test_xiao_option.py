"""Nominal checks for the wired XIAO option; not a physical fit qualification."""
import unittest
from pathlib import Path

from trackball import trackball as B


class XiaoOptionTest(unittest.TestCase):
    def test_panel_changes_only_the_identifying_label(self):
        original = Path('trackball/pcb/trackball.kicad_pcb').read_text()
        xiao = Path('trackball/pcb_xiao/trackball_xiao.kicad_pcb').read_text()
        self.assertEqual(original.count('"SD TRACKBALL"'), 1)
        old = '"SD TRACKBALL"\n\t\t(at 100 120.85 0)'
        new = '"XIAO"\n\t\t(at 100 140 0)'
        self.assertIn(old, original)
        self.assertEqual(xiao, original.replace(old, new, 1))

    def test_xiao_shields_release_i2c_key_pin(self):
        for kind in ('trackball', 'trackpad'):
            name = 'slim_diamond_' + kind + '_xiao'
            overlay = (Path('zmk/boards/shields') / name / (name + '.overlay')).read_text()
            with self.subTest(shield=name):
                self.assertIn('&i2c1 { status = "disabled"; };', overlay)
                self.assertIn('<&gpio0 4 (GPIO_ACTIVE_LOW | GPIO_PULL_UP)>', overlay)

    def test_trackpads_enable_active_high_data_ready_and_primary_tap(self):
        for suffix, gpio in (('', 11), ('_xiao', 28)):
            name = 'slim_diamond_trackpad' + suffix
            overlay = (Path('zmk/boards/shields') / name / (name + '.overlay')).read_text()
            with self.subTest(shield=name):
                self.assertIn(f'data-ready-gpios = <&gpio0 {gpio} GPIO_ACTIVE_HIGH>;', overlay)
                self.assertIn('primary-tap-enable;', overlay)

    def test_controller_envelope_and_rear_supports(self):
        layout = B.place()
        tray = B.tray(layout)
        parts = dict(B.parts(layout, B.main_board_plan(layout), B.sensor_board_plan(layout), "mx"))
        nano = parts["nice!nano"]
        back = layout["back"]
        floor = B.SOCKET_BOT - B.NANO_GAP - B.NANO[2]
        # Seeed's 17.8 x 21 mm outline, aligned with the existing rear port.
        # USB housing/PCB thickness assumed equal to the nano's conservative model.
        xiao = B.box3(-8.9, back - 21.0, floor, 8.9, back - .6, floor + B.NANO[2])
        usb = B.box3(-4.5, back - 7.9, floor - B.NANO[3], 4.5, back, floor)
        self.assertLess(abs(((xiao + usb) - nano).volume()), 1e-3)
        self.assertLess(abs(((xiao + usb) ^ tray).volume()), 1e-3)
        for side in (-1, 1):
            probe = B.box3(side * 7.4 - .5, back - 8.0, floor - .2,
                           side * 7.4 + .5, back - 7.0, floor)
            self.assertGreater((probe ^ tray).volume(), .1)


if __name__ == "__main__":
    unittest.main()
