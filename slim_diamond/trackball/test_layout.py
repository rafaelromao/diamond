"""Regression check for the bottom-plate post that used to block the five-pad wire row.

Run from slim_diamond/: python3 -m unittest discover -s trackball -p 'test_*.py'
"""
import unittest

from shapely.geometry import Point, box

if __package__:
    from . import trackball as T
else:
    import trackball as T


class LayoutTest(unittest.TestCase):
    def test_rearward_keys_retain_a_closed_plate_rim(self):
        layout = T.place()
        for name, spec in (("mx", T.MX), ("choc", T.CHOC)):
            height = T.PCB_TOP + spec["below_plate"]
            inset = min(max(height - T.M.FLUSH, 0), T.M.UPPER_BEVEL)
            top = T.M.OUTLINE.buffer(-inset, join_style=2)
            for x, y in layout["keys"]:
                cut = box(x - T.MX_CUT / 2, y - T.MX_CUT / 2,
                          x + T.MX_CUT / 2, y + T.MX_CUT / 2)
                with self.subTest(switch=name, key_y=y):
                    self.assertTrue(top.buffer(-1.0, join_style=2).covers(cut),
                                    "switch aperture breaks out of the plate rim")

    def test_controller_moves_rearward_without_forcing_the_taper(self):
        layout = T.place()
        recess = layout["back"] - (layout["nano"][1] + T.NANO[1])
        self.assertGreater(recess, 0)
        self.assertLess(recess, 11.0)

    def test_wire_rows_clear_bottom_plate_posts(self):
        layout = T.place()
        shell, plate, posts, board_posts, main_plan, sensor_plan = T.shell_and_plate(layout)
        pads = T.board_layout(layout, main_plan)
        self.assertEqual(len(pads["wires"]), 7)
        self.assertEqual(len(pads["bat"]), 2)
        sclk_y = layout["nano"][1] + T.NANO[1] - T.NANO_ROW1 - 9 * 2.54
        self.assertEqual(len(pads["controller"]), 3)
        self.assertGreater(posts[-1][1], layout["ball"][1] + T.SENSOR_BOARD[1] / 2)
        for x, y in board_posts:
            self.assertTrue(main_plan.contains(Point(x, y).buffer(1.4)))
            for px, py in posts:
                self.assertGreater(Point(x, y).distance(Point(px, py)), T.M.SCREW["post"] + 0.3)
        for name, part in T.parts(layout, main_plan, sensor_plan):
            self.assertLess(abs((part ^ shell).volume()), 1e-3, name)
            self.assertLess(abs((part ^ plate).volume()), 1e-3, name)
        for x, y in pads["wires"] + pads["bat"] + pads["controller"]:
            self.assertTrue(main_plan.contains(Point(x, y).buffer(1.6)))
            for px, py in posts:
                self.assertGreater(Point(x, y).distance(Point(px, py)), T.M.SCREW["post"] / 2 + 1.6)

    def test_mx_and_choc_use_one_board_and_bottom_plate(self):
        layout = T.place()
        mx = T.shell_and_plate(layout, "mx")
        choc = T.shell_and_plate(layout, "choc")
        self.assertEqual(mx[2:4], choc[2:4])
        self.assertTrue(mx[4].equals(choc[4]))
        self.assertTrue(mx[5].equals(choc[5]))
        self.assertLess(abs((mx[1] - choc[1]).volume()), 1e-3)
        self.assertLess(abs((choc[1] - mx[1]).volume()), 1e-3)
        for switch, built in (("mx", mx), ("choc", choc)):
            parts = T.parts(layout, built[4], built[5], switch)
            T.M.check_common(switch, built[0], built[1], parts)
            height = T.PCB_TOP + (T.MX if switch == "mx" else T.CHOC)["below_plate"]
            T.M.check_dock_and_desk(built[0], built[1], height, parts)


if __name__ == "__main__":
    unittest.main()
