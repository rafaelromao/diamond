"""500 mAh bay and the independent-stand contact. Run: python3 -m unittest test_half_battery."""
import unittest

from shapely.geometry import Polygon

import case as C
import stand_mount


class HalfBatteryTest(unittest.TestCase):
    def test_larger_envelope_clears_case_and_all_board_parts(self):
        self.assertEqual(C.D["battery_capacity_mah"], 500)
        self.assertEqual(C.D["battery_nominal_size"], [20, 40, 7])
        self.assertEqual(C.D["battery_size"], [20.5, 41, 7.5])
        battery = C.battery()
        self.assertLess(abs((battery ^ C.build()).volume()), 1e-3)
        for name, polygon, height in C.part_footprints():
            part = C.to_desk_solid(C.slab(polygon, -height, 0))
            self.assertLess(abs((battery ^ part).volume()), 1e-3, name)
        pcb = C.to_desk_solid(C.slab(Polygon(C.D["pcb_outline"]), 0, C.PCB_T))
        self.assertLess(abs((battery ^ pcb).volume()), 1e-3)

    def test_platform_mount_clears_feet_on_both_halves(self):
        self.assertEqual(len(C.D["magnets_floor"]), 7)
        self.assertEqual(len(C.D["magnets_side_y"]), 6)
        self.assertEqual(C.D["magnet_nominal_size"], [8, 1.5])
        stand_mount.check()

    def test_side_magnets_span_wall_at_equal_pitch(self):
        ys = C.D["magnets_side_y"]
        self.assertEqual(len(ys), 6)
        for a, b in zip(ys, ys[1:]):
            self.assertAlmostEqual(b - a, 17.8)
        self.assertAlmostEqual(ys[0], -24.8)
        self.assertAlmostEqual(ys[-1], 64.2)


if __name__ == "__main__":
    unittest.main()
