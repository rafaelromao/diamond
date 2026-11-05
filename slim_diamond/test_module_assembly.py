"""Assembly regressions: the shared tray and lids, screws, drop-in order, controls and magnets."""
import math
import unittest

from manifold3d import Manifold
from shapely.geometry import Point

import module_shell as M
from trackball import trackball as B
from trackpad import trackpad as T

TOL = 1e-3


def hit(a, b):
    return abs((a ^ b).volume())


class ModuleAssemblyTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        L = B.place()
        cls.L = L
        cls.tray = B.tray(L)
        cls.main_plan, cls.sensor_plan = B.main_board_plan(L), B.sensor_board_plan(L)
        P = T.place()
        cls.P = P
        cls.modules = [("mx", B.lid(L, "mx"), B.parts(L, cls.main_plan, cls.sensor_plan, "mx"), B.H),
                       ("choc", B.lid(L, "choc"), B.parts(L, cls.main_plan, cls.sensor_plan, "choc"), M.HEAD_Z),
                       ("trackpad", T.lid(P), T.parts(P, cls.main_plan, cls.sensor_plan), T.H)]

    def test_one_tray_and_one_screw_type(self):
        self.assertEqual(T.H, M.HEAD_Z)
        self.assertEqual(M.SCREW["length"], 8.0)
        self.assertEqual(M.SCREW["pilot"], 2.5)
        self.assertLess(abs((T.parts(self.P, self.main_plan, self.sensor_plan)[0][1]).volume()
                            - dict(self.modules[1][2])["CHOC 1"].volume()), 1e-6)

    def test_heads_seat_at_the_same_height_on_every_lid(self):
        for name, lid, _, height in self.modules:
            for x, y in M.lid_screws():
                head = Manifold.cylinder(1.45, 1.75, 3.1, circular_segments=48).translate((x, y, M.HEAD_Z - 1.45))
                well = Manifold.cylinder(height - M.HEAD_Z + 5, 3.1, circular_segments=48).translate((x, y, M.HEAD_Z))
                with self.subTest(module=name, screw=(x, y)):
                    self.assertLess(hit(head, lid), TOL)
                    self.assertLess(hit(well, lid), TOL)

    def test_screws_bite_as_deep_as_in_the_halves_without_bottoming(self):
        tip = M.HEAD_Z - M.SCREW["length"]
        for sx in (-1, 1):
            for x, y, top in ((sx * M.FRONT_SCREW[0], M.FRONT_SCREW[1], M.PCB_TOP),
                              (sx * M.PCB_SCREW[0], M.PCB_SCREW[1], M.PCB_TOP - M.PCB_T)):
                with self.subTest(screw=(x, y)):
                    self.assertGreaterEqual(top - tip, 4.2 - 1e-6)
                    pilot = Manifold.cylinder(top - tip + .5, 1.2, circular_segments=40).translate((x, y, tip - .5))
                    self.assertLess(hit(pilot, self.tray), TOL)
                    # solid plastic round the thread, and under its tip
                    ring = Manifold.cylinder(top - tip - .2, 2.1, circular_segments=48) - Manifold.cylinder(top - tip, 1.3, circular_segments=48)
                    self.assertLess(abs((ring.translate((x, y, tip + .1)) - self.tray).volume()), TOL)
                    under = Manifold.cylinder(.5, 1.0, circular_segments=40).translate((x, y, tip - 1.4))
                    self.assertLess(abs((under - self.tray).volume()), TOL)

    def test_sensor_board_screws_do_not_break_through_the_floor(self):
        tip = B.PLATE_TOP + B.SENSOR_BELOW + B.PCB_T + M.SCREW["head_h"] - M.SCREW["length"]
        for x, y in B.sensor_holes(self.L):
            self.assertGreater(tip, 1.1 - 1e-6)
            skin = Manifold.cylinder(.55, 2.0, circular_segments=40).translate((x, y, M.FEET + .02))
            self.assertLess(abs((skin - self.tray).volume()), TOL)

    def test_a_driver_reaches_every_screw_from_above(self):
        for name, lid, parts, height in self.modules:
            for x, y in M.lid_screws():
                tool = Manifold.cylinder(40, 1.5, circular_segments=32).translate((x, y, M.HEAD_Z + .01))
                wide = Manifold.cylinder(40, 2.0, circular_segments=32).translate((x, y, height + .01))
                with self.subTest(module=name, screw=(x, y)):
                    self.assertLess(hit(tool, lid), TOL)
                    for label, solid in parts:
                        self.assertLess(hit(wide, solid), TOL, label)

    def test_every_head_leaves_a_rim_on_every_lid(self):
        for name, lid, _, height in self.modules:
            inset = min(height - M.FLUSH, M.UPPER_BEVEL)
            top = M.profile(height).intersection(M.OUTLINE.buffer(-inset, join_style=2))
            for x, y in M.lid_screws():
                with self.subTest(module=name, screw=(x, y)):
                    self.assertTrue(top.buffer(-.45).contains(Point(x, y).buffer(M.SCREW["head"] / 2)))

    def test_electronics_drop_straight_into_the_tray_in_order(self):
        low = {"battery", "nice!nano", "sensor board", "sensor's parts", "lens", "reset", "FFC adapter"}
        high = {"main board", "power switch", "socket 1", "socket 2"}
        for name, _, parts, _ in self.modules:
            for group in (low, high):
                solid = Manifold()
                for label, part in parts:
                    if label in group:
                        solid += part
                for step in range(1, 41):
                    with self.subTest(module=name, group=sorted(group)[0], lift=step):
                        self.assertLess(hit(solid.translate((0, 0, step)), self.tray), TOL)

    def test_lid_hooks_in_at_the_rear_then_closes(self):
        pivot = M.OUTLINE.bounds[3]
        inner_back = pivot - M.WALL
        for name, lid, _, _ in self.modules:
            for tenth in range(0, 121, 5):
                angle = tenth / 10
                # swing the front up about the rear rim
                tilted = lid.translate((0, -pivot, -M.FLUSH)).rotate((-angle, 0, 0)).translate((0, pivot, M.FLUSH))
                with self.subTest(module=name, angle=angle):
                    self.assertLess(hit(tilted, self.tray), .05)
            hooks = Manifold()
            for x in M.FINGERS:
                hooks += Manifold.cube((2, .85, .7)).translate((x - 1, inner_back + 1.0, M.FLUSH - 2.03))
            self.assertGreater((hooks ^ lid).volume(), .9 * hooks.volume())
            over = hooks.translate((0, 0, 1.3))     # the tray's rear wall holds them down
            self.assertLess(abs((over - self.tray).volume()), .05)

    def test_controls_are_the_same_parts_in_the_same_places(self):
        reference = None
        for name, lid, parts, _ in self.modules:
            found = dict(parts)
            box = [found[k].bounding_box() for k in ("power switch", "reset", "nice!nano", "battery")]
            reference = reference or box
            with self.subTest(module=name):
                self.assertEqual(box, reference)

    def test_reset_pin_goes_straight_in(self):
        for name, lid, parts, _ in self.modules:
            x, y = B.sensor_reset(self.L)
            reset = dict(parts)["reset"]
            pin = Manifold.cylinder(reset.bounding_box()[2] + 10 - .01, .55, circular_segments=32).translate((x, y, -10))
            with self.subTest(module=name):
                self.assertLess(hit(pin, self.tray + lid), TOL)
                self.assertGreater(reset.volume(), 5)

    def test_power_lever_slides_in_its_slot(self):
        for name, lid, parts, _ in self.modules:
            with self.subTest(module=name):
                self.assertLess(hit(dict(parts)["power switch"], self.tray + lid), TOL)

    def test_floor_magnet_is_centred_backed_and_clear(self):
        x, y = M.K.DRAWER_FLOOR_MAG
        self.assertEqual(x, 0.0)
        mag = M.floor_magnet()
        self.assertLess(hit(mag, self.tray), TOL)
        roof = Manifold.cylinder(.85, 4, circular_segments=48).translate((x, y, M.FEET + 1.62))
        self.assertLess(abs((roof - self.tray).volume()), TOL)
        for name, _, parts, _ in self.modules:
            for label, solid in parts:
                with self.subTest(module=name, part=label):
                    self.assertLess(hit(mag, solid), TOL)

    def test_foot_recesses_keep_at_least_one_mm_of_roof(self):
        for x, y in M.feet_spots():
            roof = Manifold.cylinder(1.0, M.BUMPON[0] / 2, circular_segments=48).translate((x, y, M.BUMPON[1] + 0.05))
            self.assertLess(abs((roof - self.tray).volume()), TOL)

    def test_side_magnet_backings_keep_point_eight_mm(self):
        for w, n in M.magnets():
            skin = Manifold.cylinder(.8, 3.9, circular_segments=40)
            angle = math.degrees(math.atan2(-n[1], -n[0]))
            depth = M.MAG_H + .12
            skin = skin.rotate((0, 90, 0)).rotate((0, 0, angle)).translate(
                (w[0] - n[0] * depth, w[1] - n[1] * depth, M.MAG_Z))
            self.assertLess(abs((skin - self.tray).volume()), TOL)

    def test_pull_ribbon_clears_the_desk_and_the_tray(self):
        ribbon = M.pull_ribbon()
        self.assertGreater(ribbon.bounding_box()[2], 0)
        self.assertLess(hit(ribbon, self.tray), TOL)


if __name__ == "__main__":
    unittest.main()
