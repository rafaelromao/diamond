"""Assembly regressions: the shared tray and lids, screws, drop-in order, controls and magnets."""
import math
import unittest

from manifold3d import Manifold
from shapely.geometry import Point, box

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
                       ("choc", B.lid(L, "choc"), B.parts(L, cls.main_plan, cls.sensor_plan, "choc"), M.CHOC_TOP),
                       ("trackpad", T.lid(P), T.parts(P, cls.main_plan, cls.sensor_plan), T.H)]

    def test_every_print_is_one_solid(self):
        for name, solid in [("tray", self.tray)] + [(m[0], m[1]) for m in self.modules]:
            with self.subTest(part=name):
                self.assertEqual(sum(c.volume() > 1e-6 for c in solid.decompose()), 1)

    def test_one_tray_and_one_screw_type(self):
        self.assertEqual(T.H, M.CHOC_TOP)
        self.assertEqual(M.SCREW["length"], 8.0)
        self.assertEqual(M.SCREW["pilot"], 2.5)
        self.assertLess(abs((T.parts(self.P, self.main_plan, self.sensor_plan)[0][1]).volume()
                            - dict(self.modules[1][2])["CHOC 1"].volume()), 1e-6)

    def test_every_hole_is_a_plain_countersink_at_the_top(self):
        for name, lid, _, height in self.modules:
            for x, y in M.lid_screws():
                head = Manifold.cylinder(1.45, 1.75, 3.1, circular_segments=48).translate((x, y, height - 1.45))
                seat = Manifold.cylinder(.3, 2.6, 3.2, circular_segments=48).translate((x, y, height - 1.75))
                with self.subTest(module=name, screw=(x, y)):
                    self.assertLess(hit(head, lid), TOL)
                    self.assertGreater((seat ^ lid).volume(), .25 * seat.volume())

    def test_screws_bite_the_post_and_do_not_bottom(self):
        for height in (B.H, M.CHOC_TOP):
            tip = height - M.SCREW["length"]
            for x, y in M.lid_screws():
                with self.subTest(height=height, screw=(x, y)):
                    self.assertGreaterEqual(M.PCB_TOP - tip, 3.0 - 1e-6)
                    pilot = Manifold.cylinder(M.PCB_TOP - tip + .5, 1.2, circular_segments=40).translate((x, y, tip - .3))
                    self.assertLess(hit(pilot, self.tray), TOL)
                    ring = Manifold.cylinder(M.PCB_TOP - tip - .2, 2.0, circular_segments=48) - Manifold.cylinder(M.PCB_TOP - tip, 1.3, circular_segments=48)
                    self.assertLess(abs((ring.translate((x, y, tip + .1)) - self.tray).volume()), TOL)
                    under = Manifold.cylinder(.05, 1.0, circular_segments=40).translate((x, y, 13.6))
                    self.assertLess(abs((under - self.tray).volume()), TOL)

    def test_main_board_rests_on_the_post_shoulders(self):
        for x, y in B.board_holes():
            pin = Manifold.cylinder(.5, 1.9, circular_segments=48) - Manifold.cylinder(.5, 1.3, circular_segments=48)
            pin = pin.translate((x, y, B.PCB_TOP - .8))
            self.assertLess(abs((pin - self.tray).volume()), TOL)
            self.assertTrue(self.main_plan.contains(Point(x, y).buffer(B.POST_PIN + .2 + .4)))
            ledge = Manifold.cylinder(.2, 3.4, circular_segments=48) - Manifold.cylinder(.2, 2.5, circular_segments=48)
            ledge = ledge.translate((x, y, B.PCB_TOP - B.PCB_T - .2))
            self.assertGreater((ledge ^ self.tray).volume(), .4 * ledge.volume())

    def test_usb_opening_has_no_bottom(self):
        L = self.L
        for z in (0, 4, 8, 12):
            slab = B.box3(-6.3, L["back"] - M.WALL, z, 6.3, L["back"] + 2, z + 1)
            self.assertLess(hit(slab, self.tray), TOL)

    def test_side_bevel_runs_from_the_top_to_the_halves(self):
        for name, lid, _, height in self.modules:
            inset = min(height - M.FLUSH, M.UPPER_BEVEL)
            for z, frac in ((M.FLUSH + .05, .05 / (height - M.FLUSH)), ((M.FLUSH + height) / 2, .5)):
                probe = B.box3(M.OUTLINE.bounds[0] - 1, -60, z - .01, -15, -50, z + .01)
                section = probe ^ lid
                with self.subTest(module=name, z=z):
                    expected_gain = inset * frac
                    edge = section.bounding_box()[0]
                    plain = (B.box3(-99, -60, z - .01, -15, -50, z + .01) ^ M.extrude(M.OUTLINE, 0, 40)).bounding_box()[0]
                    self.assertAlmostEqual(edge - plain, expected_gain, delta=.05)

    def test_sensor_board_screws_do_not_break_through_the_floor(self):
        tip = B.PLATE_TOP + B.SENSOR_BELOW - B.SENSOR_SHIM + B.PCB_T + M.SCREW["head_h"] - M.SCREW["length"]
        for x, y in B.sensor_holes(self.L):
            self.assertGreater(tip, .95 - 1e-6)     # no shim at all
            skin = Manifold.cylinder(.4, 2.0, circular_segments=40).translate((x, y, M.FEET + .02))
            self.assertLess(abs((skin - self.tray).volume()), TOL)

    def test_front_facet_runs_the_full_height_of_the_upper_bevel(self):
        from shapely.geometry import LineString
        base = M.profile(M.FLUSH).intersection(LineString([(0, -200), (0, 0)])).bounds[1]
        for name, lid, _, height in self.modules:
            inset = min(height - M.FLUSH, M.UPPER_BEVEL, M.FRONT_BEVEL)
            for fraction in (.1, .5, .9):
                z = M.FLUSH + fraction * (height - M.FLUSH)
                section = lid ^ B.box3(-.01, -110, z - .001, .01, -90, z + .001)
                with self.subTest(module=name, fraction=fraction):
                    self.assertFalse(section.is_empty())
                    self.assertAlmostEqual(section.bounding_box()[1], base + fraction * inset, delta=.02)

    def test_a_driver_reaches_every_screw_from_above(self):
        for name, lid, parts, height in self.modules:
            for x, y in M.lid_screws():
                tool = Manifold.cylinder(40, 1.5, circular_segments=32).translate((x, y, height + .01))
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
                    self.assertTrue(top.buffer(-.2).contains(Point(x, y).buffer(M.SCREW["head"] / 2)))

    def test_electronics_drop_straight_into_the_tray_in_order(self):
        low = {"battery", "sensor board", "sensor's parts", "lens", "reset"}
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

    def test_nano_lowers_in_then_slides_back_into_the_wall(self):
        nano = dict(self.modules[1][2])["nice!nano"]
        path = [(-3.2, z * .5) for z in range(80, -1, -1)] + [(-3.2 + i * .1, 0) for i in range(33)]
        for dy, dz in path:
            with self.subTest(offset=(dy, dz)):
                self.assertLess(hit(nano.translate((0, dy, dz)), self.tray), TOL)

    def test_usb_c_is_flush_with_the_back(self):
        nano = dict(self.modules[1][2])["nice!nano"]
        self.assertAlmostEqual(nano.bounding_box()[4], self.L["back"], places=4)

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
                hooks += Manifold.cube((2, .55, .7)).translate((x - 1, inner_back + 1.3, M.FLUSH - 2.03))
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

    def test_fits_survive_a_print_that_is_0_2_mm_off(self):
        d = .2
        offsets = [(d, 0), (-d, 0), (0, d), (0, -d)]
        board = Manifold()
        for label, part in self.modules[1][2]:
            if label in ("main board", "power switch", "socket 1", "socket 2"):
                board += part
        for name, lid, _, _ in self.modules:
            for dx, dy in offsets:
                with self.subTest(module=name, shift=(dx, dy)):
                    self.assertLess(hit(lid.translate((dx, dy, 0)), self.tray), TOL)
        for dx, dy in offsets:
            with self.subTest(board=(dx, dy)):
                self.assertLess(hit(board.translate((dx, dy, 0)), self.tray), TOL)

    def test_a_large_protected_cell_still_lowers_in(self):
        x, y = self.L["battery"]
        cell = B.box3(x - 10.2, y - .3, B.BAT_Z, x + 10.2, y + 25.3, B.BAT_Z + 8)
        for lift in range(0, 41):
            self.assertLess(hit(cell.translate((0, 0, lift)), self.tray), TOL)

    def test_lens_height_can_be_set_with_a_shim(self):
        for x, y in B.sensor_holes(self.L):
            over = Manifold.cylinder(.3, 2.5, circular_segments=40).translate(
                (x, y, B.PLATE_TOP + B.SENSOR_BELOW - B.SENSOR_SHIM + .02))
            self.assertLess(hit(over, self.tray), TOL)

    def test_pad_wires_have_a_way_down(self):
        # The separate DR lead passes beside, not through, the retained FFC bend envelope.
        wires = Manifold.cylinder(6.2, .45, circular_segments=32).translate((4.8, -60.2, 10.8))
        for label, solid in self.modules[2][2]:
            if label not in ("pad's back parts", "pad"):
                self.assertLess(hit(wires, solid), TOL, label)

    def test_i2c_breakout_and_ffc_have_reserved_space_without_a_holder(self):
        parts = dict(self.modules[2][2])
        board = parts['I2C breakout envelope']
        cable = parts['FFC bend envelope']
        self.assertEqual(T.BREAKOUT, (24.0, 18.0, 4.5))
        for name, part in parts.items():
            if name not in ('I2C breakout envelope', 'FFC bend envelope'):
                with self.subTest(part=name):
                    self.assertLess(hit(board, part), TOL)
                    self.assertLess(hit(cable, part), TOL)
        for part in (self.tray, self.modules[2][1]):
            self.assertLess(hit(board + cable, part), TOL)
        for x, y in B.sensor_holes(self.L):
            screw = M.flat_screw(x, y, B.PLATE_TOP + B.SENSOR_BELOW + B.PCB_T + M.SCREW['head_h'])
            self.assertLess(hit(board + cable, screw), TOL)
        self.assertLess(abs((T.breakout_visual(self.P) - board).volume()), TOL)
        self.assertLess(abs((T.ffc_visual(self.P) - cable).volume()), TOL)
        self.assertGreater(cable.bounding_box()[5] - cable.bounding_box()[2], 1.5)

    def test_countersinks_keep_a_printable_web_from_the_pad_seat(self):
        px, py = self.P['pad']
        seat = T.PAD['d'] / 2 + T.PAD['clr']
        for x, y in M.lid_screws():
            web = math.dist((x, y), (px, py)) - seat - M.SCREW['head'] / 2
            with self.subTest(screw=(x, y)):
                self.assertGreaterEqual(web, .8)       # two 0.4 mm perimeters at least

    def test_trackpad_is_clear_of_both_keys_after_front_bevel(self):
        px, py = self.P['pad']
        pad = Point(px, py).buffer(T.PAD['d'] / 2)
        for x, y in self.P['keys']:
            cap = box(x - 9, y - 9, x + 9, y + 9)
            self.assertGreater(pad.distance(cap), .2)


if __name__ == "__main__":
    unittest.main()
