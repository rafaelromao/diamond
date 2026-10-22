"""Tiny VRML writer and the Slim Diamond's stand-in 3D models for KiCad renders.

KiCad reads VRML in 0.1-inch units, with model +Y = board -y and z = 0 on the
footprint's copper face.
"""
import os

import numpy as np
from manifold3d import Manifold

INCH10 = 2.54
SWITCH = (0.18, 0.18, 0.2)
STEM = (0.75, 0.55, 0.3)
KEYCAP = (0.24, 0.26, 0.3)
SOCKET = (0.1, 0.1, 0.1)
XIAO_PCB = (0.1, 0.25, 0.55)
SHIELD = (0.75, 0.75, 0.78)
METAL = (0.7, 0.7, 0.72)
JST = (0.92, 0.9, 0.85)
BATTERY = (0.55, 0.6, 0.7)
CASE = (0.16, 0.2, 0.32)


def write_parts(path, parts, z_from_pcb_bottom=False):
    """parts: [(manifold in footprint coords (mm, y down), rgb)]."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    out = ["#VRML V2.0 utf8"]
    for m, rgb in parts:
        mesh = m.to_mesh()
        v = np.asarray(mesh.vert_properties)[:, :3].copy()
        f = np.asarray(mesh.tri_verts)
        if z_from_pcb_bottom:
            v[:, 2] -= 1.6            # z = 0 on the board's top copper
        v[:, 1] = -v[:, 1]            # model +Y is board -y
        f = f[:, ::-1]                # keep the winding after the flip
        v /= INCH10
        pts = ",".join(f"{a:.4f} {b:.4f} {c:.4f}" for a, b, c in v)
        idx = ",".join(f"{a},{b},{c},-1" for a, b, c in f)
        out.append(
            "Shape { appearance Appearance { material Material { diffuseColor %.3f %.3f %.3f "
            "specularColor 0.2 0.2 0.2 shininess 0.3 } } geometry IndexedFaceSet { solid FALSE "
            "creaseAngle 0.5 coord Coordinate { point [ %s ] } coordIndex [ %s ] } }" % (*rgb, pts, idx))
    with open(path, "w") as fh:
        fh.write("\n".join(out) + "\n")


def box(x0, y0, z0, x1, y1, z1):
    return Manifold.cube((x1 - x0, y1 - y0, z1 - z0)).translate((x0, y0, z0))


def frustum(w0, h0, w1, h1, z0, z1, x=0, y=0):
    return Manifold.hull_points([(sx * w / 2 + x, sy * h / 2 + y, z) for w, h, z in ((w0, h0, z0), (w1, h1, z1))
                                 for sx in (-1, 1) for sy in (-1, 1)])


def models(d="pcb/3d"):
    # Kailh Choc v1 + low-profile keycap, socket hanging under the board (left half: socket on B).
    switch = [
        (box(-7.5, -7.5, 0, 7.5, 7.5, 2.5), SWITCH),
        (frustum(13.8, 13.8, 12.5, 12.5, 2.5, 5.0), SWITCH),
        (box(-2.6, -1.6, 5.0, 2.6, 1.6, 5.8), STEM),
        (frustum(17.5, 16.5, 15.6, 14.6, 5.8, 8.6), KEYCAP),
        (box(-2.45, -8.45, -1.6 - 1.85, 7.75, -1.25, -1.6), SOCKET),
    ]
    write_parts(f"{d}/choc_v1_with_cap.wrl", switch)
    # XIAO nRF52840, drawn as mounted on the F face (KiCad mirrors it when the footprint is flipped).
    xiao = [
        (box(-8.75, -10.5, 0, 8.75, 10.5, 1.0), XIAO_PCB),
        (box(-6.0, -3.0, 1.0, 6.0, 7.0, 2.4), SHIELD),
        (box(-4.5, -11.8, 1.0, 4.5, -4.4, 4.2), METAL),
    ]
    write_parts(f"{d}/xiao_nrf52840.wrl", xiao)
    write_parts(f"{d}/msk12c02.wrl", [(box(-3.35, -1.35, 0, 3.35, 1.35, 1.4), METAL),
                                      (box(-0.75, 1.35, 0.2, 0.75, 2.85, 1.2), SOCKET)])
    write_parts(f"{d}/jst_ph_s2b.wrl", [(box(-3.95, -1.35, 0, 3.95, 6.25, 4.75), JST)])


if __name__ == "__main__":
    models()
    print(sorted(os.listdir("pcb/3d")))
