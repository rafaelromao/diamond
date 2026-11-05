"""A module for the dock's drawer: the shell every module shares.

Frame: the dock's plan (x right, y away from you, mm); z up from the plane the module stands on,
the desk or the drawer's floor. Its bump-on feet are FEET tall, so its body starts at z = FEET.

The outline is the drawer's, DRAWER_CLR in (dock.module_plan), so any module fits. The walls are
vertical at the sides, with the halves' exact facets at the front: in the dock they meet its
wedge-shaped walls (vertical inside, leaning with the
halves outside), and on the desk a half's own vertical inner wall, so a module sits flat against
either. Three magnets per side (dock.DRAWER_MAGS) sit where the halves' inner-wall magnets do, at
the same height over the plane both stand on: the module on its feet, a half on its pads. Pressed
in from outside, flush, like the case's, each backed by a boss. In the dock they meet its thin
magnets through the inner retaining skin; independently they meet the halves directly.

A module is two printed parts: the shell (walls and top, printed top down) and a bottom plate
(the floor, the feet and whatever stands on it), held by countersunk M2 screws into posts.
"""
import math
from functools import lru_cache

import numpy as np
from manifold3d import CrossSection, FillRule, Manifold
from shapely.geometry import LineString, Point, Polygon, box
from shapely.ops import unary_union

import dock as K

P = K.placement()
OUTLINE = K.module_plan(P)
FEET = K.MODULE_FEET
WALL = 1.6
BOTTOM_T = 2.2                     # retains a 0.7 mm skin over the foot recesses
BEVEL_WALL = 1.0                   # the wall under the bevel, square to it (2.5 perimeters at 0.4 mm)
UPPER_BEVEL = 1.5                  # maximum 45-degree rim width; retain material round rear switch holes
PLATE_CLR = 0.15                   # round the bottom plate, inside the walls
MAG_D, MAG_H = K.D["magnet_side_size"]          # common disc pocket, with fit clearance
MAG_Z = K.D["magnet_side_z"] + K.PAD_DROP       # over the standing plane: a half's, on its pads
BOSS = (MAG_D + 1.0, MAG_H + 0.1 + 0.5)         # behind each magnet: length along the wall, depth
SCREW = dict(pilot=1.6, post=4.6, head=3.9, hole=2.3)   # M2 x 6 flat head (90-degree countersunk)
BUMPON = (8.0, 2.0)                # the case's 8 x 2 mm bump-ons, recessed to stand FEET proud
SPINE_TOP = K.spine_height(P)
FLOOR_Z = K.drawer_floor(P)        # the drawer's floor over the desk
FLUSH = SPINE_TOP - FLOOR_Z        # a module this tall is flush with the halves' top edges


def extrude(poly, z0, z1):
    polys = getattr(poly, "geoms", [poly])
    rings = []
    for p in polys:
        rings.append(list(p.exterior.coords)[:-1])
        rings += [list(i.coords)[:-1] for i in p.interiors]
    return CrossSection(rings, FillRule.EvenOdd).extrude(z1 - z0).translate((0, 0, z0))


def inner():
    return OUTLINE.buffer(-WALL, join_style=2)


def profile(height):
    """The actual outer plan at height above the module's standing plane."""
    return K.module_plan(P, FLOOR_Z + height)


def magnets():
    """Each magnet's place on the module's outer wall: (point (x, y), outward normal), both sides."""
    out = []
    ring = OUTLINE.exterior
    for m in K.drawer_magnets(P):
        for sx in (1, -1):
            q = np.array((sx * m[0], m[1]))
            w = np.array(ring.interpolate(ring.project(Point(q))).coords[0])
            n = (q - w) / np.linalg.norm(q - w)
            out.append((w, n))
    return out


def _along(w, n, length, depth):
    """A rectangle on the wall at w: `length` along it, `depth` in from the outer face."""
    t = np.array((-n[1], n[0]))
    a = w - t * length / 2
    b = w + t * length / 2
    return Polygon([tuple(a), tuple(b), tuple(b - n * depth), tuple(a - n * depth)])


def magnet_bosses():
    return [_along(w, n, *BOSS) for w, n in magnets()]


def magnet_pockets():
    out = Manifold()
    for w, n in magnets():
        c = Manifold.cylinder(MAG_H + 0.1 + 0.01, MAG_D / 2, circular_segments=40)
        ang = math.degrees(math.atan2(-n[1], -n[0]))
        c = c.rotate((0, 90, 0)).rotate((0, 0, ang))          # along -n, into the wall
        out += c.translate((w[0] + n[0] * 0.01, w[1] + n[1] * 0.01, MAG_Z))
    return out


def room():
    """Inside the walls, clear of the magnet bosses (with 0.3 mm round them)."""
    return inner().difference(unary_union(magnet_bosses()).buffer(0.3))


@lru_cache(maxsize=1)
def service_plan():
    """Vertical extraction envelope inside the narrowest, lowest front facet.
    A plate following the expanding facet higher up cannot pass its lower lip.
    """
    column = K.module_front(extrude(inner().buffer(-PLATE_CLR, join_style=2), FEET - 0.1, FEET + 0.1),
                            P, WALL + PLATE_CLR)
    plan = Polygon()
    for ring in column.slice(FEET).to_polygons():
        plan = plan.symmetric_difference(Polygon(ring))
    return plan


def screw_spots(n=3, keep_out=None):
    """Posts for the bottom plate's screws: in the corners of what's inside (front two, back
    one), each merging 1 mm into the walls (or a boss), and clear of `keep_out` (a plan polygon)."""
    ok = inner().buffer(1.0 - SCREW["post"] / 2, join_style=2)
    ok = ok.intersection(service_plan().buffer(-SCREW["head"] / 2 - 0.6))
    if keep_out is not None:
        ok = ok.difference(keep_out.buffer(SCREW["post"] / 2 + 0.3))
    x0, y0, x1, y1 = ok.bounds
    pts = [(x, y) for x in np.arange(math.ceil(x0 * 2) / 2, x1 + 0.01, 0.5)
           for y in np.arange(math.ceil(y0 * 2) / 2, y1 + 0.01, 0.5)
            if ok.contains(Point(x, y))]
    front_l = min(pts, key=lambda q: q[1] + 0.5 * q[0])
    front_r = (-front_l[0], front_l[1])
    back = max(pts, key=lambda q: q[1] - 0.2 * abs(q[0]))
    back = (0.0, back[1]) if ok.contains(Point(0, back[1])) else back
    return [front_l, front_r, back][:n]


def feet_spots():
    """Bump-ons under the bottom plate: the front corners and the back, inset to stay on it."""
    ok = service_plan().buffer(-BUMPON[0] / 2 - 1.0)
    # Keep the rear recess in front of the USB overmold passage, retaining its full roof.
    ok = ok.intersection(box(-200, -200, 200, -31.0))
    for x, y in screw_spots()[:2]:
        ok = ok.difference(Point(x, y).buffer(BUMPON[0] / 2 + SCREW["head"] / 2 + 0.6))
    x0, y0, x1, y1 = ok.bounds
    pts = [(x, y) for x in np.arange(x0, x1 + 0.01, 0.5) for y in np.arange(y0, y1 + 0.01, 0.5)
           if ok.contains(Point(x, y))]
    front_l = min(pts, key=lambda q: q[1] + 0.6 * q[0])
    back = max(pts, key=lambda q: q[1])
    return [front_l, (-front_l[0], front_l[1]), (0.0, back[1])]


def shell(height, top_t, posts, post_tops=None):
    """The walls and the top, with the magnets' bosses and pockets, and the bottom plate's posts
    (screw pilot holes from below). The module's own openings are cut by its script."""
    body = K.module_front(extrude(OUTLINE, FEET, height) ^ bevel_hull(OUTLINE, height), P)
    # the inside follows the bevel, its wall BEVEL_WALL thick square to it
    bevel_start = max(FLUSH, height - UPPER_BEVEL)
    cavity = extrude(inner(), FEET - 1, height - top_t) ^ bevel_hull(inner(), height - top_t,
                                                                 bevel_start + WALL - BEVEL_WALL * math.sqrt(2))
    body -= K.module_front(cavity, P, WALL)
    for b in magnet_bosses():
        body += extrude(b, FEET + BOTTOM_T + PLATE_CLR, MAG_Z + MAG_D / 2 + 1.5) ^ extrude(OUTLINE, 0, height)
    for x, y in posts:
        top = (post_tops or {}).get((x, y), height - top_t)
        post = Manifold.cylinder(top - (FEET + BOTTOM_T) + 0.01, SCREW["post"] / 2, circular_segments=32)
        body += post.translate((x, y, FEET + BOTTOM_T))
        body -= Manifold.cylinder(8.0, SCREW["pilot"] / 2, circular_segments=20).translate((x, y, FEET + BOTTOM_T - 0.01))
    return (bevel(body, height) + rear_hood()) - magnet_pockets()


def rear_hood():
    """Top-only rear extension, common to both trackball shells and the trackpad.
    Its underside rises one millimetre per millimetre rearwards; the dock keeps the
    matching support underneath. Forward removal increases the gap rather than hooking.
    """
    blank = extrude(K.rear_hood_plan(P), FEET, FLUSH)
    normal = (0, -1 / math.sqrt(2), 1 / math.sqrt(2))
    return blank.trim_by_plane(normal, K.rear_hood_datum(P) / math.sqrt(2))


def bevel_hull(poly, top, start=None):
    """Over `start` (the halves' top edges, FLUSH), the outline drawn in at 45 degrees up to `top`:
    a module taller than the halves meets them with a bevel, not a step. Below it, the outline."""
    start = max(FLUSH, top - UPPER_BEVEL) if start is None else start
    b = top - start
    ring = lambda p, z: [(x, y, z) for x, y in p.exterior.coords[:-1]]
    if b <= 0:
        return extrude(poly, -1, top + 1)
    return Manifold.hull_points(ring(poly, -1) + ring(poly, start) + ring(poly.buffer(-b, join_style=2), top))


def bevel(m, height):
    """A module's solid trimmed to its bevel (the shell and anything added to it)."""
    return K.module_front(m ^ (bevel_hull(OUTLINE, height) + rear_hood()), P)


def bottom_plate(posts):
    """The floor: inside the walls, with the bump-ons' recesses and the screws' countersinks."""
    plate = extrude(service_plan(), FEET, FEET + BOTTOM_T)
    d, h = BUMPON
    for x, y in feet_spots():
        plate -= Manifold.cylinder(h - FEET + 0.01, d / 2 + 0.2, circular_segments=40).translate((x, y, FEET - 0.01))
    for x, y in posts:
        plate -= Manifold.cylinder(BOTTOM_T + 0.02, SCREW["hole"] / 2, circular_segments=20).translate((x, y, FEET - 0.01))
        # 90-degree countersink from below, as deep as the head is wide over two
        plate -= Manifold.cylinder(SCREW["head"] / 2 + 0.11, SCREW["head"] / 2 + 0.1, 0.0, circular_segments=48).translate(
            (x, y, FEET - 0.01))
    return plate


def bumpons():
    d, h = BUMPON
    out = Manifold()
    for x, y in feet_spots():
        out += Manifold.cylinder(h, d / 2 - 0.8, d / 2, circular_segments=40).translate((x, y, 0))
    return out


def usb_connection(front, z):
    """Illustrative straight USB-C plug, fully seated: metal, overmold and cable.
    Dimensions match the keyboard's conservative 12.35 x 6.5 mm overmold envelope.
    `front` is the receptacle's front face; insertion extends 6 mm into the receptacle.
    """
    metal = Manifold.cube((8.4, 7.0, 2.6)).translate((-4.2, front - 6.0, z - 1.3))
    body = Manifold.cube((12.35, 16.0, 6.5)).translate((-6.175, front + 1.0, z - 3.25))
    cable = Manifold.cylinder(30.0, 1.8, circular_segments=32).rotate((-90, 0, 0)).translate(
        (0, front + 17.0, z))
    return metal, body, cable


def usb_clearance(front, z):
    """Cable-plug passage from the receptacle to outside the rear wall, with fit allowance."""
    return Manifold.cube((12.8, OUTLINE.bounds[3] - front + 20, 7.2)).translate(
        (-6.4, front + 0.8, z - 3.6))


def check_common(name, shell_m, plate_m, parts):
    """The checks every module needs: every part against the shell, the plate and the others; the
    module in the dock's drawer, against the dock and the halves; on the desk against a half."""
    def vol(a, b):
        return (a ^ b).volume()
    print(name)
    print("  shell x plate              %.3f mm3" % vol(shell_m, plate_m))
    assert abs(vol(shell_m, plate_m)) < 1e-3, "shell interferes with the bottom plate"
    for pname, pm in parts:
        print("  %-26s %.3f mm3 x shell, %.3f x plate" % (pname, vol(pm, shell_m), vol(pm, plate_m)))
        assert abs(vol(pm, shell_m)) < 1e-3 and abs(vol(pm, plate_m)) < 1e-3, pname
    body = extrude(OUTLINE, 0, 99)
    for w, n in magnets():
        c = Manifold.cylinder(MAG_H + 0.1, MAG_D / 2 + 0.5, circular_segments=40)
        ang = math.degrees(math.atan2(-n[1], -n[0]))
        c = c.rotate((0, 90, 0)).rotate((0, 0, ang)).translate((w[0], w[1], MAG_Z))
        print("  magnet at (%5.1f, %5.1f): its pocket's 0.5 mm surround %.2f mm3 outside the module" %
              (w[0], w[1], (c - body).volume()))
    names = [n for n, _ in parts]
    for i in range(len(parts)):
        for j in range(i + 1, len(parts)):
            v = vol(parts[i][1], parts[j][1])
            if v > 1e-3:
                print("  %s x %s  %.3f mm3" % (names[i], names[j], v))
                raise AssertionError("parts interfere: " + names[i] + " / " + names[j])
    return vol


def check_dock_and_desk(shell_m, plate_m, height, parts=(), feet=None, k=None):
    """Check seated fit, horizontal front removal, and desk use beside either half.
    Use the feet's standing plane for alignment, never lift a part just to align magnets."""
    k = K.make() if k is None else k
    dock_m = k.solid
    half = k.p(K.HALF)
    module = (shell_m + plate_m).translate((0, 0, FLOOR_Z))
    print("  in the dock: module x dock %.3f mm3, x left half %.3f, x right half %.3f; top %.2f mm over"
          " the halves' top edges" % ((module ^ dock_m).volume(), (module ^ half).volume(),
                                        (module ^ half.mirror((1, 0, 0))).volume(), height + FLOOR_Z - SPINE_TOP))
    assert all(abs((module ^ other).volume()) < 1e-3
               for other in (dock_m, half, half.mirror((1, 0, 0)))), "seated module interferes"
    mags_half = K.drawer_magnets(P)
    for (w, n), m in zip(magnets()[::2], mags_half):
        gap = (np.array(m[:2]) - w) @ n
        print("    magnet chain spans %.2f mm (dock magnet and wall between), heights %.2f / %.2f"
               % (gap, MAG_Z + FLOOR_Z, m[2]))
        assert abs(MAG_Z + FLOOR_Z - m[2]) < 1e-4, "docked magnet heights do not align"
    # on the desk: the half untented, moved along the wall's normal onto the module
    flat = K.Placement(0.0)
    mag_local = [(K.WALL_OUT, -K.D["magnets_side_y"][i], K.D["magnet_side_z"]) for i in K.DRAWER_MAGS]
    m0 = flat.points(mag_local)
    w, n = magnets()[0 if magnets()[0][0][0] < 0 else 1]
    shift = (w - np.array(m0[0][:2])) @ n
    half_desk = flat(K.HALF).translate((n[0] * shift, n[1] * shift, 0))
    body = shell_m + plate_m
    print("  on the desk with the left half: module x half %.3f mm3" % (body ^ half_desk).volume())
    for (w, n), m in zip([mm for mm in magnets() if mm[0][0] < 0], m0):
        q = np.array(m[:2]) + n * shift
        along = np.linalg.norm(q - w)
        print("    magnet: centres %.2f mm apart along the wall, heights %.2f / %.2f (module / half)"
               % (along, MAG_Z, m[2]))
        assert along < 1e-4, "standalone side magnets are not aligned"
        assert abs(MAG_Z - m[2]) < 1e-4, "standalone magnets require lifting a part"

    # The standing plane is the datum, not the printed floor: both devices stand on their feet.
    feet = bumpons() if feet is None else feet
    body += feet
    for _, part in parts:
        body += part
    assert abs(body.bounding_box()[2]) < 1e-4, "module does not stand on z = 0"
    pads_desk = flat(K.PADS).translate((n[0] * shift, n[1] * shift, 0))
    assert abs(pads_desk.bounding_box()[2]) < 1e-4, "keyboard feet do not stand on z = 0"
    for name, other in (("left", half_desk), ("right", half_desk.mirror((1, 0, 0)))):
        overlap = abs((body ^ other).volume())
        print("  standalone with %s half: %.3f mm3, both standing planes z = 0" % (name, overlap))
        assert overlap < 1e-3, "module collides with the " + name + " half"
    obstacles = dock_m + half + half.mirror((1, 0, 0))
    seated = body.translate((0, 0, FLOOR_Z))
    assert abs(seated.bounding_box()[2] - FLOOR_Z) < 1e-4
    length = OUTLINE.bounds[3] - OUTLINE.bounds[1] + 5
    worst = max(abs((seated.translate((0, -float(travel), 0)) ^ obstacles).volume())
                for travel in np.arange(0, length + 0.5, 0.5))
    print("  horizontal front removal, 0..%.1f mm: %.3f mm3 at worst; no lifting" % (length, worst))
    assert worst < 1e-3, "module cannot pull straight out through the front"
