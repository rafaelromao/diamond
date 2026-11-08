"""Topology-checked STL meshes after the format's mandatory float32 quantization."""
import numpy as np
from manifold3d import Manifold, Mesh


def _weld(vertices, faces):
    vertices, inverse = np.unique(np.asarray(vertices, dtype=np.float32), axis=0, return_inverse=True)
    return vertices, inverse[np.asarray(faces)]


def _material_faces(vertices, faces):
    """Discard zero-volume boundary scraps, never individual sliver faces of a real solid.
    Face adjacency uses only edges with exactly two incident faces, as an ordinary STL
    importer does. Preserve negative-volume enclosed void boundaries as well as material.
    """
    edges = np.sort(np.concatenate([faces[:, [0, 1]], faces[:, [1, 2]], faces[:, [2, 0]]]), axis=1)
    face_ids = np.tile(np.arange(len(faces)), 3)
    _, inverse, counts = np.unique(edges, axis=0, return_inverse=True, return_counts=True)
    order = np.argsort(inverse, kind="stable")
    starts = np.r_[0, np.cumsum(counts)[:-1]]
    pairs = starts[counts == 2]
    parent = np.arange(len(faces))

    def root(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    for a, b in zip(face_ids[order[pairs]], face_ids[order[pairs + 1]]):
        a, b = root(a), root(b)
        if a != b:
            parent[b] = a
    labels = np.array([root(i) for i in range(len(faces))])
    tri = vertices[faces].astype(np.float64)
    # Translate before signed-volume summation to reduce cancellation far from the origin.
    tri -= vertices.mean(axis=0)
    signed = np.einsum("ij,ij->i", tri[:, 0], np.cross(tri[:, 1], tri[:, 2])) / 6
    totals = np.bincount(labels, weights=signed, minlength=len(faces))
    return faces[np.abs(totals[labels]) > 1e-9]


def clean_mesh(solid):
    """Return float32 vertices/faces with no degenerate triangles or non-manifold edges."""
    mesh = solid.to_mesh()
    vertices, faces = _weld(np.asarray(mesh.vert_properties)[:, :3], np.asarray(mesh.tri_verts))
    faces = _material_faces(vertices, faces)
    # A second float32 round-trip can expose collinear slivers attached to the real
    # material. Simplify topology rather than deleting those faces and leaving holes.
    # Maximum displacement is 0.0001 mm, far below print/manufacturing tolerances.
    for tolerance in (1e-5, 1e-4):
        rebuilt = Mesh(vert_properties=vertices, tri_verts=np.asarray(faces, dtype=np.uint32))
        rebuilt.merge()
        repaired = Manifold(rebuilt)
        if repaired.is_empty():
            raise ValueError("STL cleanup did not retain a valid solid")
        mesh = repaired.set_tolerance(tolerance).to_mesh()
        vertices, faces = _weld(np.asarray(mesh.vert_properties)[:, :3], np.asarray(mesh.tri_verts))
        faces = _material_faces(vertices, faces)
    triangles = vertices[faces].astype(np.float64)
    areas = np.linalg.norm(np.cross(triangles[:, 1] - triangles[:, 0], triangles[:, 2] - triangles[:, 0]), axis=1) / 2
    edges = np.sort(np.concatenate([faces[:, [0, 1]], faces[:, [1, 2]], faces[:, [2, 0]]]), axis=1)
    _, counts = np.unique(edges, axis=0, return_counts=True)
    if np.any(areas < 1e-10) or np.any(counts != 2):
        raise ValueError("STL cleanup left degenerate faces or non-manifold welded edges")
    return vertices, faces
