"""Reload the actual binary STL format: no importer repair or topology assumptions."""
from pathlib import Path
import tempfile
import unittest

import numpy as np

import case as C
import dock
import insert
from trackball import trackball as B
from trackpad import trackpad as T


class StlExportTest(unittest.TestCase):
    def test_all_printable_variants_survive_binary_stl_quantization(self):
        half = C.real(C.build())
        plate = C.plate()[0]
        solids = {"left": half, "right": C.mirrored(half), "plate_left": plate,
                  "plate_right": plate.mirror((1, 0, 0)), "dock": dock.make().solid,
                  "cover": insert.build()[0]}
        layout = B.place()
        solids["tray"] = B.tray(layout).translate((0, 0, -B.M.FEET))
        for name, lid, height in (("mx", B.lid(layout, "mx"), B.H), ("choc", B.lid(layout, "choc"), B.M.HEAD_Z),
                                  ("trackpad", T.lid(T.place()), T.H)):
            solids[name] = lid.mirror((0, 0, 1)).translate((0, 0, height))
        record = np.dtype([("normal", "<f4", 3), ("vertices", "<f4", (3, 3)), ("attribute", "<u2")])
        with tempfile.TemporaryDirectory(dir="/tmp/opencode", prefix="diamond-stl-test-") as folder:
            for name, solid in solids.items():
                with self.subTest(variant=name):
                    path = Path(folder) / (name + ".stl")
                    C.stl(solid, path)
                    data = path.read_bytes()
                    count = int.from_bytes(data[80:84], "little")
                    self.assertEqual(len(data), 84 + 50 * count)
                    triangles = np.frombuffer(data, dtype=record, offset=84)["vertices"].astype(float)
                    vertices, inverse = np.unique(triangles.reshape(-1, 3), axis=0, return_inverse=True)
                    faces = inverse.reshape(-1, 3)
                    area = np.linalg.norm(np.cross(triangles[:, 1] - triangles[:, 0],
                                                   triangles[:, 2] - triangles[:, 0]), axis=1) / 2
                    self.assertTrue(np.all(area >= 1e-10), "degenerate STL faces")
                    directed = np.concatenate([faces[:, [0, 1]], faces[:, [1, 2]], faces[:, [2, 0]]])
                    _, edge_ids, incidence = np.unique(np.sort(directed, axis=1), axis=0,
                                                       return_inverse=True, return_counts=True)
                    self.assertTrue(np.all(incidence == 2), "non-manifold welded STL edges")
                    directions = np.where(directed[:, 0] < directed[:, 1], 1, -1)
                    self.assertTrue(np.all(np.bincount(edge_ids, weights=directions) == 0), "inconsistent winding")
                    signed_volume = np.einsum("ij,ij->i", triangles[:, 0],
                                               np.cross(triangles[:, 1], triangles[:, 2])).sum() / 6
                    self.assertAlmostEqual(signed_volume, solid.volume(), delta=0.05)


if __name__ == "__main__":
    unittest.main()
