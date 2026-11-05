"""Audit actual exported STL bytes, including every public copy, without repair."""
import hashlib
import json
from pathlib import Path

import numpy as np


def inspect(path):
    data = path.read_bytes()
    count = int.from_bytes(data[80:84], "little")
    assert len(data) == 84 + 50 * count, path
    record = np.dtype([("normal", "<f4", 3), ("vertices", "<f4", (3, 3)), ("attr", "<u2")])
    tri = np.frombuffer(data, dtype=record, offset=84)["vertices"].astype(float)
    vertices, inverse = np.unique(tri.reshape(-1, 3), axis=0, return_inverse=True)
    faces = inverse.reshape(-1, 3)
    area = np.linalg.norm(np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0]), axis=1) / 2
    assert np.all(area >= 1e-10), (path, "degenerate triangle")
    directed = np.concatenate([faces[:, [0, 1]], faces[:, [1, 2]], faces[:, [2, 0]]])
    edges, ids, incidence = np.unique(np.sort(directed, axis=1), axis=0, return_inverse=True, return_counts=True)
    assert np.all(incidence == 2), (path, "nonmanifold edge")
    signs = np.where(directed[:, 0] < directed[:, 1], 1, -1)
    assert np.all(np.bincount(ids, weights=signs) == 0), (path, "inconsistent winding")
    parent = list(range(len(vertices)))
    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a
    for a, b in edges:
        parent[find(int(a))] = find(int(b))
    components = len({find(i) for i in range(len(vertices))})
    expected = 2 if path.name == "dock_halves.stl" else 1
    assert components == expected, (path, components)
    volume = float(np.einsum("ij,ij->i", tri[:, 0], np.cross(tri[:, 1], tri[:, 2])).sum() / 6)
    assert volume > 0, (path, "reversed surface")
    return dict(path=str(path), sha256=hashlib.sha256(data).hexdigest(), bytes=len(data),
                triangles=count, components=components, volume_mm3=round(volume, 5),
                size_mm=(vertices.max(axis=0) - vertices.min(axis=0)).round(5).tolist(),
                watertight=True, winding=True)


def main():
    public = Path("../stls/slim_diamond")
    inventory, pairs = [], []
    for folder, prefix in ((Path("case"), ""), (Path("trackball/case"), "trackball_"),
                           (Path("trackpad/case"), "trackpad_")):
        for source in sorted(folder.glob("*.stl")):
            copy = public / (prefix + source.name)
            assert source.read_bytes() == copy.read_bytes(), (source, copy)
            inventory += [inspect(source), inspect(copy)]
            pairs.append([str(source), str(copy)])
    inventory += [inspect(p) for p in sorted(Path(".render").glob("*.stl"))]
    result = dict(files=inventory, identical_public_pairs=pairs,
                  note="Binary topology/copy integrity only; not a physical buildability certificate.")
    Path("STL_EXPORT_MANIFEST.json").write_text(json.dumps(result, indent=2) + "\n")
    print(f"{len(inventory)} actual STLs valid; {len(pairs)} public pairs byte-identical")


if __name__ == "__main__":
    main()
