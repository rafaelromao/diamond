"""Front continuity, retention and standing-plane checks. Run: python3 -m unittest test_drawer."""
import unittest

from manifold3d import Manifold
from shapely.geometry import LineString, Polygon

import dock as K
import insert
import module_shell as M
from trackball import trackball
from trackpad import trackpad


class DrawerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dock = K.make()
        cls.modules = []
        tray = trackball.tray(trackball.place())
        cls.tray = tray
        for name, mod in (("trackball", trackball), ("trackpad", trackpad)):
            layout = mod.place()
            main_plan, sensor_plan = trackball.main_board_plan(layout), trackball.sensor_board_plan(layout)
            lid = mod.lid(layout)
            cls.modules.append((name, tray + lid, Manifold(), mod.H, mod.parts(layout, main_plan, sensor_plan), M.bumpons()))
        cover, _ = insert.build()
        cls.modules.append(("cover", cover, Manifold(), insert.H, [], Manifold()))

    def test_continuous_walls_and_magnet_retention(self):
        plan = K.drawer_plan(M.P)
        self.assertTrue(plan.equals(plan.convex_hull), "ribs or notches interrupt the drawer")
        self.assertGreaterEqual(len(K.DOCK_MAGS), 2)
        self.assertGreaterEqual(len(set(K.DOCK_MAGS) & set(K.DRAWER_MAGS)), 2)
        for i in K.DOCK_MAGS:
            cap = Manifold.cylinder(K.DRAWER_SKIN, K.SIDE_D / 2, circular_segments=40).rotate((0, 90, 0))
            cap = cap.translate((K.WALL_OUT + K.CLR - 0.05 + K.SIDE_H + 0.1,
                                 -K.D["magnets_side_y"][i], K.D["magnet_side_z"]))
            cap = M.P(cap)
            for side in (cap, cap.mirror((1, 0, 0))):
                self.assertLess(abs((side - self.dock.solid).volume()), 1e-3)

    def test_front_facets_continue_the_halves(self):
        for name, shell, _, _, _, _ in self.modules:
            for z in (1.0, 2.0, 5.0, M.FLUSH - 2):
                section = Polygon()
                for ring in shell.slice(z).to_polygons():
                    section = section.symmetric_difference(Polygon(ring))
                for x in (-15, -8, 0, 8, 15):
                    line = LineString([(x, -130), (x, -60)])
                    expected = M.profile(z).intersection(line)
                    actual = section.intersection(line)
                    with self.subTest(module=name, z=z, x=x):
                        self.assertFalse(actual.is_empty)
                        self.assertAlmostEqual(actual.bounds[1], expected.bounds[1], places=4)

    def test_one_magnet_size_everywhere(self):
        self.assertEqual(K.D["magnet_nominal_size"], [8, 1.5])
        self.assertEqual(K.D["magnet_floor_size"], K.D["magnet_side_size"])
        self.assertEqual(list(K.BASE_MAG), K.D["magnet_floor_size"])
        self.assertAlmostEqual(K.SIDE_H, 1.5)
        self.assertEqual(len(K.DOCK_MAGS), 6)
        self.assertEqual(len(K.DRAWER_MAGS), 3)
        ys = [K.D["magnets_side_y"][i] for i in K.DRAWER_MAGS]
        self.assertAlmostEqual(ys[1] - ys[0], ys[2] - ys[1])

    def test_direct_floor_retention_has_matching_open_pockets_and_dock_backing(self):
        x, y = K.DRAWER_FLOOR_MAG
        z = K.drawer_floor(self.dock.p)
        magnet = Manifold.cylinder(1.5, 4, circular_segments=48).translate((x, y, z - 1.5))
        backing = Manifold.cylinder(.9, 4, circular_segments=48).translate((x, y, z - 2.55))
        self.assertLess(abs((magnet ^ self.dock.solid).volume()), 1e-3)
        self.assertLess(abs((backing - self.dock.solid).volume()), 1e-3)
        mate = M.floor_magnet().translate((0, 0, z))
        self.assertAlmostEqual(mate.bounding_box()[2] - magnet.bounding_box()[5], .55)

    def test_seated_usb_plugs_clear_shell_plate_and_dock(self):
        for mod in (trackball, trackpad):
            layout = mod.place()
            front = layout["nano"][1] + mod.NANO[1] + 0.6
            _, body, cable = M.usb_connection(front, mod.usb_z(layout))
            envelope = body + cable
            for target in (self.tray, mod.lid(layout)):
                self.assertLess(abs((envelope ^ target).volume()), 1e-3)
            self.assertLess(abs((envelope.translate((0, 0, M.FLOOR_Z)) ^ self.dock.solid).volume()), 1e-3)

    def test_usb_plug_passes_straight_through_empty_dock(self):
        z = M.FLOOR_Z + K.USB_EXIT_PLUG_Z + 6.5 / 2 + 0.1
        plug = Manifold.cube((12.35, 16.0, 6.5)).translate((-12.35 / 2, 0, z - 6.5 / 2))
        for step in range(301):
            y = 30 - step * 0.5
            with self.subTest(y=y):
                self.assertLess(abs((plug.translate((0, y, 0)) ^ self.dock.solid).volume()), 1e-3)

    def test_rear_usb_cut_is_full_width_down_to_the_underside(self):
        opening = Manifold.cube((K.USB_EXIT_W, 45, M.SPINE_TOP + 2)).translate(
            (-K.USB_EXIT_W / 2, -6.5, -1))
        self.assertLess(abs((opening ^ self.dock.solid).volume()), 1e-3,
                        "rear passage has a lower step or a floor blocking the full plug width")

    def test_rear_switch_slot_is_accessible_when_docked(self):
        # The same switch in the same place on all three lids.
        layout = trackball.place()
        z, height, width = trackball.PCB_TOP + 0.2, 2.4, 5.0
        opening = Manifold.cube((width, 28, height)).translate((-width / 2, M.OUTLINE.bounds[3] - 1.0, z))
        self.assertLess(abs((opening.translate((0, 0, M.FLOOR_Z)) ^ self.dock.solid).volume()), 1e-3)
        section = Manifold.cube((width, 1.0, height)).translate((-width / 2, M.OUTLINE.bounds[3] - 0.5, z))
        for lid in (trackball.lid(layout), trackball.lid(layout, "choc"), trackpad.lid(trackpad.place())):
            self.assertLess(abs((section ^ (lid + self.tray)).volume()), 1e-3)

    def test_a_module_pushes_out_from_the_back(self):
        # A fingertip through the dock's rear passage meets the hood's tip, over the USB-C opening.
        end = self.tray.bounding_box()[4]
        finger = Manifold.cube((9, 40, 3)).translate((-4.5, end + .05, M.FLUSH - 3.2))
        self.assertLess(abs((finger.translate((0, 0, M.FLOOR_Z)) ^ self.dock.solid).volume()), 1e-3)
        self.assertGreater((finger.translate((0, -3, 0)) ^ self.tray).volume(), 5)

    def test_modules_sit_loose_in_a_print_that_is_0_2_mm_off(self):
        for name, shell, _, _, _, _ in self.modules:
            for dx in (-.2, .2):
                with self.subTest(module=name, dx=dx):
                    moved = shell.translate((dx, 0, M.FLOOR_Z))
                    self.assertLess(abs((moved ^ self.dock.solid).volume()), 1e-3)

    def test_rear_hood_is_top_only_with_a_45_degree_underside(self):
        hood = M.rear_hood()
        self.assertGreater(hood.volume(), 0)
        self.assertAlmostEqual(hood.bounding_box()[5], M.FLUSH)
        self.assertGreater(hood.bounding_box()[2], M.FEET + M.BOTTOM_T)
        self.assertLess(M.FLUSH - self.tray.bounding_box()[5], 1e-6)     # the tray carries it, floor down
        end = K.rear_hood_end(M.P)
        self.assertGreater(end, M.OUTLINE.bounds[3] + 10)
        datum = K.rear_hood_datum(M.P)
        # Lower surface rises exactly one millimetre for every millimetre rearwards.
        for y in (-12, -8, -4, -1):
            z = y + datum
            inside = Manifold.cube((0.2, 0.2, 0.05)).translate((-0.1, y - 0.1, z + 0.15))
            outside = inside.translate((0, 0, -0.4))
            self.assertLess(abs((inside - hood).volume()), 1e-6)
            self.assertLess(abs((outside ^ hood).volume()), 1e-6)

    def test_front_removal_and_both_standalone_sides(self):
        for name, shell, plate, height, parts, feet in self.modules:
            with self.subTest(module=name):
                M.check_common(name, shell, plate, parts)
                M.check_dock_and_desk(shell, plate, height, parts, feet=feet, k=self.dock)
                # decompose() also returns negative-volume boundaries of enclosed voids;
                # those are not detached pieces of printable material.
                if name == "cover":
                    self.assertEqual(sum(c.volume() > 1e-6 for c in shell.decompose()), 1)


if __name__ == "__main__":
    unittest.main()
