"""Slim Diamond case and top plate. Writes case/*.stl.

The case is a solid base under the tented PCB: plastic everywhere up to the
PCB's underside (sturdy, and no hollow body to ring), with a pocket for each
part plus TOL clearance on every side and above it. The plate covers the whole
top: the switches clip into it, flat-head screws countersink into it, and a
shallow pocket in its underside clears the solder blobs around the Xiao.

Built in the desk frame: floor flat on the desk at z = 0, the PCB tilted up
towards the inner wall (the unibody seam) by design.json's tent angle. The
plate is built flat, in the PCB's frame.

The gem look: the outline is a cut-diamond silhouette (design.py), and the
outer walls lean in from a girdle GIRDLE mm wider than the rim, each one flat
facet, with a CHAMFER under the girdle. Stacked back to back the chamfers meet
in a V at the widest line, so the pair reads as a cut gem from the side. The
seam stays a vertical face for the unibody join.

Also writes the case, battery and keycaps as VRML in the PCB's frame, for
KiCad's 3D renders.
"""
import json
import math
import os

import numpy as np
from manifold3d import CrossSection, FillRule, JoinType, Manifold

import design as DZ
from shapely import affinity
from shapely.geometry import Polygon, box
from shapely.ops import unary_union

D = json.load(open("design.json"))
OUT = "case"

TENT = math.radians(D["tent_deg"])
WALL_IN = D["wall_in"]
WALL_OUT = D["wall_out"]
FLOOR = D["floor"]
PCB_T = D["pcb_t"]
Z0 = FLOOR + D["z_in"]          # PCB bottom at the inner wall, over the desk
PLATE = D["plate"]
SCREW = D["screw"]
RIM = PLATE["gap"] + PLATE["thick"]   # the wall rises flush with the plate's top
GIRDLE = 2.0                    # floor flare past the rim: the lean of the gem facets
CHAMFER = 1.5                   # 45-degree cut under the girdle
TOL = 0.6                       # clearance around and above every part in the base
PILOT_R = SCREW["pilot_d"] / 2  # self-tapping pilot (or the heat-set insert's hole)
PILOT_FLOOR = 0.6               # pilot holes stop this far above the desk
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


def to_desk_solid(m):
    """PCB-frame solid (z above the PCB's bottom face) into the desk frame."""
    c, s_ = math.cos(TENT), math.sin(TENT)
    m = m.translate((-WALL_IN, 0, 0))
    m = m.transform([[c, 0, -s_, 0], [0, 1, 0, 0], [s_, 0, c, 0]])
    return m.translate((WALL_IN, 0, Z0))


def slab(poly, z0, z1):
    """A shapely polygon (PCB plan) extruded between PCB-frame heights z0 and z1."""
    polys = getattr(poly, "geoms", [poly])
    cs = CrossSection([list(p.exterior.coords)[:-1] for p in polys], FillRule.NonZero)
    return cs.extrude(z1 - z0).translate((0, 0, z0))


def part_footprints():
    """What hangs under the PCB, as (name, PCB-plan polygon, height)."""
    keys = DZ.layout_left()
    xc, xa = (D["xiao"]["x"], D["xiao"]["y"]), D["xiao"]["r"]
    pw, jt = D["power_switch"], D["jst"]
    return [
        ("sockets", unary_union([DZ.under_switch(*keys[n]) for n in DZ.KEY_ORDER]), DZ.SOCKET_DEPTH),
        ("xiao", DZ.place(DZ.rect(DZ.XIAO_W, DZ.XIAO_L), xc, xa), DZ.XIAO_DEPTH),
        ("power switch", DZ.place(box(-DZ.PWR_W / 2, -1.75, DZ.PWR_W / 2, DZ.PWR_D - 1.75),
                                  (pw["x"], pw["y"]), pw["r"]), DZ.PWR_H),
        ("jst", DZ.place(box(-DZ.JST_W / 2, -4.6, DZ.JST_W / 2, 6.25), (jt["x"], jt["y"]), jt["r"]),
         DZ.JST_H),
    ]


def build():
    case_pts = [tuple(p) for p in D["case_outline"][:-1]]
    cav_pts = [tuple(p) for p in D["cavity_outline"][:-1]]
    top_zp = PCB_T + RIM

    # Outer body: the hull of the rim (case outline on the tilted top plane), the girdle (the
    # outline grown by GIRDLE) CHAMFER above the desk, and the girdle cut back by CHAMFER on
    # the desk. The outline is convex, so every face is one flat facet.
    rim = plan(case_pts)
    girdle = section(case_pts).offset(GIRDLE, JoinType.Miter, miter_limit=10)
    foot = girdle.offset(-CHAMFER, JoinType.Miter, miter_limit=10)
    ring = lambda cs: [p for poly in cs.to_polygons() for p in poly]
    n = (-math.sin(TENT), math.cos(TENT))           # top plane: n . (X, Z) = const
    p0 = to_desk(WALL_IN, 0, top_zp)
    const = n[0] * p0[0] + n[1] * p0[2]
    pts = [(x, y, (const - n[0] * x) / n[1]) for x, y in rim] + \
          [(min(x, WALL_OUT), y, CHAMFER) for x, y in ring(girdle)] + \
          [(min(x, WALL_OUT - CHAMFER), y, 0.0) for x, y in ring(foot)]
    body = Manifold.hull_points(pts)
    body = body.trim_by_plane((-1, 0, 0), -WALL_OUT)

    # The PCB and plate sit in the cavity above the PCB's bottom plane; below it the base is
    # solid except for a pocket per part.
    above = to_desk_solid(slab(Polygon(cav_pts), 0, 60))
    voids = [above]
    for name, poly, h in part_footprints():
        voids.append(to_desk_solid(slab(poly.buffer(TOL, join_style=2), -(h + TOL), 0.5)))
    # battery bay: the battery and the room for its plug and leads, from the floor up
    bay = Polygon(D["jst"]["bay"]).buffer(TOL, join_style=2)
    voids.append(section(list(bay.exterior.coords)[:-1]).extrude(60).translate((0, 0, FLOOR)))
    shell = body
    for v in voids:
        shell -= v

    # Screw pilot holes, from the PCB down into the solid base.
    for hx, hy in D["mount_holes"]:
        X, Y = plan([(hx, hy)])[0]
        shell -= Manifold.cylinder(60, PILOT_R, circular_segments=20).translate((X, Y, PILOT_FLOOR))

    # Floor magnets (back-to-back), pressed in from below; 0.5 mm skin above.
    mf_d, mf_h = D["magnet_floor_size"]
    for mx, my in D["magnets_floor"]:
        X, Y = plan([(mx, my)])[0]
        shell -= Manifold.cylinder(mf_h, mf_d / 2, circular_segments=32).translate((X, Y, -0.01))
    # Seam magnets (unibody), pressed into the inner wall from outside.
    ms_d, ms_h = D["magnet_side_size"]
    z_mid = FLOOR + 2.8
    for my in D["magnets_side_y"]:
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
    return shell


def plate():
    """The top plate, flat, in the PCB's frame: z = 0 is its underside (PLATE gap over the PCB)."""
    t, gap, ch = PLATE["thick"], PLATE["gap"], PLATE["chamfer"]
    outline = Polygon(D["pcb_outline"])
    pts = [(x, y, ch) for x, y in outline.exterior.coords] + \
          [(x, y, t) for x, y in outline.exterior.coords] + \
          [(x, y, 0.0) for x, y in outline.buffer(-ch, join_style=2).exterior.coords]
    body = Manifold.hull_points(pts)                       # bottom edge chamfered all round

    keys = DZ.layout_left()
    cut = PLATE["cut"] + 2 * PLATE["cut_tol"]
    lower = PLATE["cut"] + 2 * TOL                          # switch body under the plate, with room
    housings = unary_union([DZ.place(DZ.rect(lower, lower), *keys[n]) for n in DZ.KEY_ORDER])
    blob = Polygon(D["blob_zone"])
    head_r, hole_r, boss_r = SCREW["head_d"] / 2, SCREW["pcb_hole"] / 2, SCREW["boss_d"] / 2

    # Spacer bosses under the screws, down to the PCB; pillars wherever the PCB's top is free.
    adds = []
    for hx, hy in D["mount_holes"]:
        adds.append(Manifold.cylinder(gap + 0.01, boss_r, circular_segments=32).translate((hx, hy, -gap)))
    free = (outline.buffer(-(ch + 1.6), join_style=2).difference(housings.buffer(1.5))
            .difference(blob.buffer(1.5)))
    for h in D["mount_holes"]:
        free = free.difference(Polygon(box(h[0] - 1, h[1] - 1, h[0] + 1, h[1] + 1)).buffer(boss_r + 1.5))
    pillars = []
    for gx in range(-60, 50, 6):
        for gy in range(-35, 75, 6):
            if free.contains(Polygon(box(gx - 1.4, gy - 1.4, gx + 1.4, gy + 1.4))):
                pillars.append((gx, gy))
                adds.append(Manifold.cylinder(gap + 0.01, 1.4, circular_segments=16).translate((gx, gy, -gap)))
    for a_ in adds:
        body += a_

    # Switch cutouts, countersinks, and the solder-blob pocket.
    for (x, y), r in keys.values():
        body -= Manifold.cube((cut, cut, 10), center=True).rotate((0, 0, r)).translate((x, y, 0))
    for hx, hy in D["mount_holes"]:
        depth = head_r - hole_r                              # 90-degree cone
        body -= Manifold.cylinder(depth + 0.01, hole_r, head_r, circular_segments=40).translate(
            (hx, hy, t - depth))
        body -= Manifold.cylinder(t + gap + 1, hole_r, circular_segments=24).translate((hx, hy, -gap - 0.5))
    body -= slab(blob, -gap - 1, PLATE["blob_pocket"])
    return body, pillars


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
    plate_left, pillars = plate()
    # print the plate top-down: its top is flat, the bosses and pillars point up
    flat = real(plate_left).mirror((0, 0, 1)).translate((0, 0, PLATE["thick"]))
    stl(flat, f"{OUT}/plate_left.stl")
    stl(flat.mirror((1, 0, 0)), f"{OUT}/plate_right.stl")
    # for KiCad renders: case, plate and battery in the PCB frame (plan coordinates)
    import vrml
    vrml.write_parts("pcb/3d/case.wrl", [(to_pcb_frame(plan_left), vrml.CASE)], z_from_pcb_bottom=True)
    vrml.write_parts("pcb/3d/plate.wrl", [(plate_left.translate((0, 0, PCB_T + PLATE["gap"])), vrml.CASE)],
                     z_from_pcb_bottom=True)
    vrml.write_parts("pcb/3d/battery.wrl", [(to_pcb_frame(battery()), vrml.BATTERY)], z_from_pcb_bottom=True)
    bb = left.bounding_box()
    print("case left: %.1f x %.1f x %.1f mm, volume %.1f cm3, genus %d" %
          (bb[3] - bb[0], bb[4] - bb[1], bb[5] - bb[2], left.volume() / 1000, left.genus()))
    pb = plate_left.bounding_box()
    print("plate: %.1f x %.1f mm, %.1f cm3, %d support pillars" %
          (pb[3] - pb[0], pb[4] - pb[1], plate_left.volume() / 1000, len(pillars)))
    print("height at seam %.1f mm, at outer edge %.1f mm (case only, keys excluded)" %
          (pcb_bottom_z(WALL_IN) + PCB_T + RIM, pcb_bottom_z(plan([(D['x_out'], 0)])[0][0]) + PCB_T + RIM))
