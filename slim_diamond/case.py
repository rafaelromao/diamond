"""Slim Diamond case: a faceted tray under the tented PCB. Writes case/*.stl.

Built in the desk frame: floor flat on the desk at z = 0, the PCB tilted up
towards the inner wall (the unibody seam) by design.json's tent angle.

The gem look: the outline is a cut-diamond silhouette (design.py), and the
outer walls lean in from a floor GIRDLE mm wider than the rim, each one flat
facet. Stacked back to back the floors meet at the widest line, so the pair
reads as a cut gem from the side: crown above, pavilion below. The seam stays
a vertical face for the unibody join.

Also writes the case, battery and keycaps as VRML in the PCB's frame, for
KiCad's 3D renders.
"""
import json
import math
import os

import numpy as np
from manifold3d import CrossSection, FillRule, JoinType, Manifold

D = json.load(open("design.json"))
OUT = "case"

TENT = math.radians(D["tent_deg"])
WALL_IN = D["wall_in"]
WALL_OUT = D["wall_out"]
FLOOR = D["floor"]
PCB_T = D["pcb_t"]
Z0 = FLOOR + D["z_in"]          # PCB bottom at the inner wall, over the desk
RIM = 1.6                       # wall rises this far above the PCB's top face
GIRDLE = 2.0                    # floor flare past the rim: the lean of the gem facets
STANDOFF_R = D["screw"]["standoff_d"] / 2
PILOT_R = D["screw"]["pilot_d"] / 2         # self-tapping pilot (or the heat-set insert's hole)
USB_W, USB_H = 10.0, 4.4
LEVER_W, LEVER_H = 5.0, 2.8


def to_desk(x, y, zp=0.0):
    """PCB-frame point (zp above the PCB's bottom face) to the desk frame."""
    u = x - WALL_IN
    return (WALL_IN + u * math.cos(TENT) - zp * math.sin(TENT), y,
            Z0 + u * math.sin(TENT) + zp * math.cos(TENT))


def pcb_bottom_z(X):
    """Desk height of the PCB's bottom face above desk-plan X."""
    return Z0 + (X - WALL_IN) * math.tan(TENT)


def plan(points):
    """PCB-plan outline to desk plan (the tilt shortens it a little across the tent)."""
    return [(WALL_IN + (x - WALL_IN) * math.cos(TENT), y) for x, y in points]


def section(points):
    # NonZero: the KiCad (y-down) outlines run clockwise
    return CrossSection([plan(points)], FillRule.NonZero)


def prism(points, z0, z1):
    return section(points).extrude(z1 - z0).translate((0, 0, z0))


def under_tilted_plane(m, zp):
    """Keep the part of m below the plane parallel to the PCB, zp above its bottom face."""
    # plane normal points up and towards the outer side
    n = (-math.sin(TENT), 0.0, math.cos(TENT))
    p = to_desk(WALL_IN, 0, zp)
    offset = n[0] * p[0] + n[2] * p[2]
    return m.trim_by_plane((-n[0], -n[1], -n[2]), -offset)


def local_frame(c, ang, p):
    a = math.radians(ang)
    return (c[0] + p[0] * math.cos(a) - p[1] * math.sin(a), c[1] + p[0] * math.sin(a) + p[1] * math.cos(a))


def through_wall_cut(center_xy, ang, w, h, zc, depth=8.0):
    """Box cut through the wall at a PCB-plan point, facing the part's local -y."""
    box = Manifold.cube((w, depth, h), center=True)
    box = box.rotate((0, 0, ang))
    X, Y = plan([center_xy])[0]
    return box.translate((X, Y, zc))


def build():
    case_pts = [tuple(p) for p in D["case_outline"][:-1]]
    cav_pts = [tuple(p) for p in D["cavity_outline"][:-1]]
    top_zp = PCB_T + RIM

    # Outer body: the hull of the rim (case outline on the tilted top plane) and the floor
    # (the outline grown by GIRDLE, except at the seam). The outline is convex, so every
    # wall is one flat facet.
    rim = plan(case_pts)
    girdle = section(case_pts).offset(GIRDLE, JoinType.Miter, miter_limit=10)
    girdle = [p for poly in girdle.to_polygons() for p in poly]
    n = (-math.sin(TENT), math.cos(TENT))           # top plane: n . (X, Z) = const
    p0 = to_desk(WALL_IN, 0, top_zp)
    const = n[0] * p0[0] + n[1] * p0[2]
    pts = [(x, y, (const - n[0] * x) / n[1]) for x, y in rim] + \
          [(min(x, WALL_OUT), y, 0.0) for x, y in girdle]
    body = Manifold.hull_points(pts)
    body = body.trim_by_plane((-1, 0, 0), -WALL_OUT)

    # Cavity: everything above the floor inside the cavity outline.
    cavity = prism(cav_pts, FLOOR, 80)
    shell = body - cavity

    # Standoffs up to the PCB's bottom face, with a pilot hole for the screw.
    for hx, hy in D["mount_holes"]:
        X, Y = plan([(hx, hy)])[0]
        post = Manifold.cylinder(60, STANDOFF_R, circular_segments=24).translate((X, Y, FLOOR - 0.5))
        post = under_tilted_plane(post, 0.0)
        hole = Manifold.cylinder(60, PILOT_R, circular_segments=20).translate((X, Y, FLOOR - 1.0))
        shell = (shell + post) - hole

    # Floor magnets (back-to-back), pressed in from below; 0.5 mm skin above.
    mf_d, mf_h = D["magnet_floor_size"]
    for mx, my in D["magnets_floor"]:
        X, Y = plan([(mx, my)])[0]
        shell -= Manifold.cylinder(mf_h, mf_d / 2, circular_segments=32).translate((X, Y, -0.01))
    # Seam magnets (unibody), pressed into the inner wall from outside.
    # The wall is thinner than the magnet: a boss inside backs each pocket. Kept low, under
    # the parts that hang beneath the PCB near the seam.
    ms_d, ms_h = D["magnet_side_size"]
    z_mid = FLOOR + 2.8
    for my in D["magnets_side_y"]:
        boss = Manifold.cube((ms_h + 1.2, ms_d + 3.0, z_mid + ms_d / 2 + 1.0 - FLOOR + 0.1))
        shell += boss.translate((WALL_OUT - (ms_h + 1.2), my - (ms_d + 3.0) / 2, FLOOR - 0.1))
        m = Manifold.cylinder(ms_h + 0.01, ms_d / 2, circular_segments=32).rotate((0, -90, 0))
        shell -= m.translate((WALL_OUT + 0.005, my, z_mid))

    # USB-C opening in front of the Xiao's USB end; the switch lever's in front of the switch.
    xc, xa = (D["xiao"]["x"], D["xiao"]["y"]), D["xiao"]["r"]
    usb_xy = local_frame(xc, xa, (0, -10.5 - 2.0))
    Xu = plan([usb_xy])[0][0]
    zc = pcb_bottom_z(Xu) - 1.0 - 1.65
    shell -= through_wall_cut(usb_xy, xa, USB_W, USB_H, zc)
    pw = D["power_switch"]
    lever_xy = local_frame((pw["x"], pw["y"]), pw["r"], (0, -1.7 - 2.0))
    Xl = plan([lever_xy])[0][0]
    shell -= through_wall_cut(lever_xy, pw["r"], LEVER_W, LEVER_H, pcb_bottom_z(Xl) - 0.75)

    # Battery: a low fence on the floor keeps it in place.
    b = D["battery"]["bounds"]
    fence = prism([(b[0] - 1.2, b[1] - 1.2), (b[2] + 1.2, b[1] - 1.2), (b[2] + 1.2, b[3] + 1.2),
                   (b[0] - 1.2, b[3] + 1.2)], FLOOR - 0.1, FLOOR + 1.5)
    fence -= prism([(b[0], b[1]), (b[2], b[1]), (b[2], b[3]), (b[0], b[3])], FLOOR - 0.5, FLOOR + 2)
    fence -= prism([(b[0] + 4, b[1] - 3), (b[2] - 4, b[1] - 3), (b[2] - 4, b[3] + 3), (b[0] + 4, b[3] + 3)],
                   FLOOR - 0.5, FLOOR + 2)   # gaps for the leads and fingers
    shell += fence
    return shell


def battery():
    """The battery as it lies on the floor (plan frame)."""
    b = D["battery"]["bounds"]
    t = D["battery_size"][2]
    return prism([(b[0] + 0.25, b[1] + 0.25), (b[2] - 0.25, b[1] + 0.25), (b[2] - 0.25, b[3] - 0.25),
                  (b[0] + 0.25, b[3] - 0.25)], FLOOR, FLOOR + t)


def real(m):
    """The plan uses KiCad's y-down coordinates; flip y for the real handedness (+y = away
    from the typist)."""
    return m.mirror((0, 1, 0))


def to_pcb_frame(m):
    """Desk-frame solid (plan coordinates) into the PCB's frame: x, y as on the board,
    z = height above the PCB's bottom face."""
    c, s = math.cos(TENT), math.sin(TENT)
    # u = (X - WALL_IN) c + (Z - Z0) s ; zp = -(X - WALL_IN) s + (Z - Z0) c
    m = m.translate((-WALL_IN, 0, -Z0))
    m = m.transform([[c, 0, s, 0], [0, 1, 0, 0], [-s, 0, c, 0]])
    return m.translate((WALL_IN, 0, 0))


def stl(m, path):
    mesh = m.to_mesh()
    v = np.asarray(mesh.vert_properties)[:, :3]
    f = np.asarray(mesh.tri_verts)
    with open(path, "wb") as fh:
        fh.write(b"slim diamond".ljust(80, b" "))
        fh.write(np.uint32(len(f)).tobytes())
        tri = v[f]
        n = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
        n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-12
        rec = np.zeros(len(f), dtype=[("n", "<f4", 3), ("v", "<f4", (3, 3)), ("a", "<u2")])
        rec["n"], rec["v"] = n, tri
        fh.write(rec.tobytes())


def mirrored(m):
    return m.mirror((1, 0, 0)).translate((2 * WALL_OUT, 0, 0))


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    plan_left = build()
    left = real(plan_left)
    stl(left, f"{OUT}/case_left.stl")
    stl(mirrored(left), f"{OUT}/case_right.stl")
    # for KiCad renders: case and battery in the PCB frame (plan coordinates)
    import vrml
    vrml.write_parts("pcb/3d/case.wrl", [(to_pcb_frame(plan_left), vrml.CASE)], z_from_pcb_bottom=True)
    vrml.write_parts("pcb/3d/battery.wrl", [(to_pcb_frame(battery()), vrml.BATTERY)], z_from_pcb_bottom=True)
    bb = left.bounding_box()
    print("case left: %.1f x %.1f x %.1f mm, volume %.1f cm3, genus %d" %
          (bb[3] - bb[0], bb[4] - bb[1], bb[5] - bb[2], left.volume() / 1000, left.genus()))
    print("height at seam %.1f mm, at outer edge %.1f mm (case only, keys excluded)" %
          (pcb_bottom_z(WALL_IN) + PCB_T + RIM, pcb_bottom_z(plan([(D['x_out'], 0)])[0][0]) + PCB_T + RIM))
