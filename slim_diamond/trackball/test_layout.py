"""Layout regressions for the trackball's boards.

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

    def test_controller_retains_rear_usb_and_floor_service_clearance(self):
        layout = T.place()
        recess = layout["back"] - (layout["nano"][1] + T.NANO[1])
        self.assertGreater(recess, 0)
        self.assertLess(recess, 14.0)
        x, y = layout["nano"]
        self.assertTrue(T.M.inner().buffer(-.15).covers(
            box(x - T.NANO[0] / 2, y, x + T.NANO[0] / 2, y + T.NANO[1])))

    def test_wire_rows_clear_the_screw_holes(self):
        layout = T.place()
        main_plan = T.main_board_plan(layout)
        pads = T.board_layout(layout, main_plan)
        self.assertEqual(len(pads["wires"]), 7)
        self.assertEqual(len(pads["bat"]), 2)
        self.assertEqual(len(pads["controller"]), 3)
        for x, y in T.board_holes():
            self.assertTrue(main_plan.contains(Point(x, y).buffer(T.M.SCREW["hole"] / 2 + .8)))
            for px, py in pads["wires"] + pads["bat"] + pads["controller"]:
                self.assertGreater(Point(x, y).distance(Point(px, py)), T.M.SCREW["boss"] / 2 + .4)
        for x, y in pads["wires"] + pads["bat"] + pads["controller"]:
            self.assertTrue(main_plan.contains(Point(x, y).buffer(1.6)))

    def test_mx_and_choc_share_the_boards_and_the_tray(self):
        layout = T.place()
        main_plan, sensor_plan = T.main_board_plan(layout), T.sensor_board_plan(layout)
        tray = T.tray(layout)
        for switch, spec in (("mx", T.MX), ("choc", T.CHOC)):
            lid = T.lid(layout, switch)
            parts = T.parts(layout, main_plan, sensor_plan, switch)
            T.M.check_common(switch, lid, tray, parts)
            T.M.check_dock_and_desk(lid, tray, T.PCB_TOP + spec["below_plate"], parts)

    def test_boards_stand_far_apart_on_the_panel(self):
        layout = T.place()
        main_plan, sensor_plan = T.main_board_plan(layout), T.sensor_board_plan(layout)
        outline, bites, shift = T.panel(layout, main_plan, sensor_plan)
        x0, y0, x1, y1 = outline.bounds
        self.assertLessEqual(max(x1 - x0, y1 - y0), 100.0)
        self.assertGreater(shift, 15.0)
        self.assertEqual(outline.geom_type, "Polygon")
        rows = sorted({y for _, y in bites})
        self.assertGreater(rows[1] - rows[0], 15.0)


if __name__ == "__main__":
    unittest.main()
