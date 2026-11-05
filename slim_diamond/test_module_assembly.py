"""Independent-audit regressions: screws, service path, foot roofs and the switch lever."""
import unittest

from manifold3d import Manifold

import module_shell as M
from trackball import trackball as B
from trackpad import trackpad as T


class ModuleAssemblyTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.modules = []
        for name, mod, switch in (("mx", B, "mx"), ("choc", B, "choc"), ("trackpad", T, None)):
            layout = mod.place()
            built = mod.shell_and_plate(layout, switch) if switch else mod.shell_and_plate(layout)
            parts = mod.parts(layout, built[4], built[5], switch) if switch else mod.parts(layout)
            cls.modules.append((name, built[0], built[1], built[2], parts))

    def test_screw_heads_clear_shells_and_have_complete_plate_seats(self):
        for name, shell, plate, posts, _ in self.modules:
            for x, y in posts:
                head = Manifold.cylinder(0.95, 1.95, 1.0, circular_segments=48).translate((x, y, M.FEET))
                seat = (Manifold.cylinder(0.2, 2.35, circular_segments=48)
                        - Manifold.cylinder(0.2, 2.05, circular_segments=48)).translate((x, y, M.FEET + 0.1))
                with self.subTest(module=name, screw=(x, y)):
                    self.assertLess(abs((head ^ shell).volume()), 1e-3)
                    self.assertLess(abs((head ^ plate).volume()), 1e-3)
                    self.assertLess(abs((seat - plate).volume()), 1e-3)

    def test_populated_bottom_plates_drop_straight_down(self):
        carried = {"battery", "nice!nano", "sensor board", "sensor's parts", "lens", "FFC adapter", "reset"}
        for name, shell, plate, _, parts in self.modules:
            assembly = plate
            for part_name, solid in parts:
                if part_name in carried and not (name in ("mx", "choc") and part_name == "nice!nano"):
                    assembly += solid
            for step in range(1, 81):
                with self.subTest(module=name, drop=step * 0.5):
                    self.assertLess(abs((assembly.translate((0, 0, -step * 0.5)) ^ shell).volume()), 1e-3)

    def test_foot_recesses_keep_at_least_point_six_mm_of_roof(self):
        for name, _, plate, _, _ in self.modules:
            for x, y in M.feet_spots():
                roof = Manifold.cylinder(0.6, M.BUMPON[0] / 2, circular_segments=48).translate(
                    (x, y, M.BUMPON[1] + 0.05))
                with self.subTest(module=name, foot=(x, y)):
                    self.assertLess(abs((roof - plate).volume()), 1e-3)

    def test_trackpad_lever_has_no_membrane_after_final_cuts(self):
        layout = T.place()
        shell = T.shell_and_plate(layout)[0]
        z = T.switch_z(layout)
        for x in (-2, 0, 2):
            lever = Manifold.cube((1, 4, 1)).translate((x - 0.5, layout["back"] - M.WALL - 0.2, z - 0.5))
            self.assertLess(abs((lever ^ shell).volume()), 1e-3)


if __name__ == "__main__":
    unittest.main()
