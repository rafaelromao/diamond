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
                    self.assertTrue(top.buffer(-.7, join_style=2).covers(cut),
                                    "switch aperture breaks out of the plate rim")

    def test_controller_retains_rear_usb_and_floor_service_clearance(self):
        layout = T.place()
        recess = layout["back"] - (layout["nano"][1] + T.NANO[1])
        self.assertGreater(recess, 0)
        self.assertAlmostEqual(recess, .6)                  # the receptacle's overhang: flush
        x, y = layout["nano"]
        self.assertTrue(T.M.inner().covers(box(x - T.NANO[0] / 2 - .1, y, x + T.NANO[0] / 2 + .1, T.M.inner().bounds[3] - .01)))

    def test_wire_rows_clear_the_screw_holes(self):
        layout = T.place()
        main_plan = T.main_board_plan(layout)
        pads = T.board_layout(layout, main_plan)
        self.assertEqual(len(pads["wires"]), 7)
        self.assertEqual(len(pads["bat"]), 2)
        self.assertEqual(len(pads["controller"]), 3)
        for x, y in T.board_holes():
            self.assertTrue(main_plan.contains(Point(x, y).buffer(T.POST_PIN + .2 + .6)))
            for px, py in pads["wires"] + pads["bat"] + pads["controller"]:
                self.assertGreater(Point(x, y).distance(Point(px, py)), T.M.SCREW["boss"] / 2 + .4)
        for x, y in pads["wires"] + pads["bat"] + pads["controller"]:
            self.assertTrue(main_plan.contains(Point(x, y).buffer(1.5)))

    def test_wire_pads_sit_beside_the_xiao_pins_and_clear_everything(self):
        layout = T.place()
        main_plan = T.main_board_plan(layout)
        pads = T.board_layout(layout, main_plan)
        rows = [T.xiao_pin_y(layout, r) for r in range(1, 8)]
        close = pads["wires"] + pads["controller"]
        self.assertEqual(len(close), 10)
        for _, y in close:
            self.assertLess(min(abs(y - r) for r in rows), 1e-6)
        for x, _ in close:
            self.assertLess(abs(abs(x) - 8.89), 2.1)   # within reach of the XIAO's edge pins
        for spec_name in ("mx", "choc"):
            parts = dict(T.parts(layout, main_plan, T.sensor_board_plan(layout), spec_name))
            for x, y in close + pads["bat"]:
                ring = T.M.extrude(Point(x, y).buffer(.85), T.PCB_TOP - T.PCB_T - 1.2, T.PCB_TOP - T.PCB_T)
                for name in ("socket 1", "socket 2"):
                    with self.subTest(switch=spec_name, pad=(x, y), part=name):
                        self.assertLess(abs((ring ^ parts[name]).volume()), 1e-3)
                joint = T.M.extrude(Point(x, y).buffer(.8), T.PCB_TOP, T.PCB_TOP + .5)
                with self.subTest(switch=spec_name, joint=(x, y)):
                    self.assertLess(abs((joint ^ T.lid(layout, spec_name)).volume()), 1e-3)

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
