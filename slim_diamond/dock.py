"""Cyberdeck dock: a low tent over a Ugreen phone stand's base, the halves on its slopes.

The Ugreen base (85 x 105 x 4 mm) stays on the desk on its own feet, carrying the phone; the
dock sits over it, the base in a pocket in its underside, and behind the spine the base's back
strip with the arm's hinge is left bare. BASE_MAGS thin magnets in the pocket's roof (thin
enough to stack under the drawer's floor) snap onto as many glued on top of the base (it is
aluminium).

Each half lies on a wing the shape of its floor, inner side up, its outer pad on the desk; common
magnets in each wing face the half's own floor magnets. Between the halves a spine rises to the
seam walls' top edges, its front carrying on the halves' front facets (its point cut off square), with a magnet facing each
of the case's six seam magnets and the joined board's diamond cut in low relief on its top. With DRAWER its middle is a
drawer, open at the top and the front, for a module that faces DRAWER_MAGS of the seam magnets itself; the dock keeps
DOCK_MAGS in continuous side walls, behind DRAWER_SKIN on the inside. The insert's front carries
on the halves' facets and pulls out horizontally, without ribs or notches at the mouth. Under each half's girdle every wall
carries on the case's own 45-degree bottom chamfer down to the desk, one plane with it, so the dock
reads as the board's continuation. The
underside is cut FOOT_LIFT off the desk, and bump-ons under the wings make that up.

The tent is the least that keeps ROOF of plastic over the base's pocket under the halves, and
room under each magnet pocket (over the base pocket too, where a magnet lands over it).

Built in the left half's real frame (case.real: x right, y away from the typist, z up) and
placed by one matrix (tent, drop onto the outer pad, splay about the seam's back end); the right
half is the mirror in x. Writes case/dock.stl (and the repo's STL folder), prints the fit check.
"""
import math
import shutil
from functools import lru_cache

import numpy as np
from manifold3d import CrossSection, FillRule, Manifold
from shapely.geometry import Point, Polygon, box
from shapely import affinity
from shapely.ops import unary_union

import case as C

D = C.D
UG = (85.0, 105.0, 4.0)       # Ugreen base: width, depth, thickness
UG_TOL = 0.3                  # pocket clearance per side, and over the base
UG_R = 3.0                    # pocket corner radius: no larger than the base's own corners
HINGE = (30.0, 28.0)          # arm's hinge on the base: width, and depth from the base's back edge
HINGE_CLR = 0.5               # clearance round the hinge, to the halves and the dock
RING = 3.0                    # plastic round the pocket where the dock is flat
ROOF = 1.6                    # plastic over the base's pocket
MAG_ROOF = 1.0                # the roof under a magnet pocket over the base
SPLAY = 12.0                  # each half's turn, tops towards the middle (degrees)
GAP_BACK = 16.25              # preserve insert room with the thicker common-magnet walls
CLR = 0.2                     # lateral gap between the dock and a half
MIN_T = 1.0                   # thinnest wing edge kept (the outer side runs out to the desk)
UNDER = 0.6                   # plastic under a magnet pocket
FOOT_LIFT = 0.5               # the dock's underside, cut this far off the desk: bump-on feet make it up
FEET = 3                      # bump-ons under each wing (the case's 8 x 2 mm ones)
FOOT_SKIN = 0.6               # plastic over each foot's recess
RELIEF = (0.6, 1.0, 2.5)      # the diamond cut in the spine's top: depth, line width, margin round it
BASE_MAGS = 5                 # magnets between the dock and the base, at most (as many as fit)
BASE_MAG = D["magnet_floor_size"]  # the same 8 x 1.5 mm discs used everywhere else
DRAWER = True                 # the spine's middle is a drawer for a module, pulled out through the front
DRAWER_MAGS = (1, 3, 5)       # three evenly spaced mates across the insert's side walls
DOCK_MAGS = tuple(range(6))   # six per half; the insert still uses three side magnets per side
DOCK_SIDE_MAG = (D["magnet_side_size"][0], D["magnet_nominal_size"][1])
DRAWER_WALL = 2.4             # continuous walls house the common magnets and their inner skins
DRAWER_SKIN = 0.6             # dock wall between the drawer and the dock's own side magnets' pockets
DRAWER_BACK = -14.0           # the drawer's back (y): both modules end there
DRAWER_CLR = 0.2              # round a module in the drawer
DRAWER_FLOOR_MAG = (0.0, -48.3)   # on the centreline, midway between the stand magnets under the spine
MODULE_FEET = 0.5             # a module's bump-ons stand this far below it
BASE_MAG_SLOP = 0.3           # round the base's magnets, which are glued on by hand
MAG_COST = 1.0                # most extra tent (degrees) a floor magnet may add to get its pocket
PAD_DROP = D["pads"]["size"][1] - D["pads"]["depth"]   # bump-on below the floor
PAD_CLR = 0.3                 # round and under each pad
MAG_D, MAG_H = D["magnet_floor_size"]
SIDE_D, SIDE_H = DOCK_SIDE_MAG if DRAWER else D["magnet_side_size"]
WALL_OUT = C.WALL_OUT
POCKET_TOP = UG[2] + UG_TOL

HALF = C.real(C.build())
FOOT = Polygon(HALF.hull().slice(0.01).to_polygons()[0])     # the floor on the desk
_seam_y = [-y for x, y in D["case_outline"] if abs(x - WALL_OUT) < 1e-6]
SEAM_FRONT, SEAM_BACK = min(_seam_y), max(_seam_y)
MAGNETS = [(X, -Y) for X, Y in C.plan(D["magnets_floor"])]     # the case's, under each half's floor


def slot_solid(grow, z0, z1):
    """Every pad slot as a stadium (both pad spots), half's frame."""
    out = Manifold()
    w = D["pads"]["slot_w"] / 2 + grow
    for a, b in D["pads"]["slots"]:
        ends = [Manifold.cylinder(z1 - z0, w, circular_segments=48).translate((X, -Y, z0))
                for X, Y in C.plan([a, b])]
        out += Manifold.batch_hull(ends)
    return out


def pad_recess():
    """Room for the bump-ons under the floor (half's frame), at both ends of every slot: each one
    a dome, 8 mm across at its top 1.1 mm up in the slot and 1.6 mm less at its tip, PAD_CLR
    round and under it. Shaped to the dome, so it stays inside the wing's 45-degree walls."""
    d, h = D["pads"]["size"]
    depth = D["pads"]["depth"]
    r_floor = d / 2 - 0.8 * depth / h + PAD_CLR                  # its radius where it leaves the floor
    r_tip = d / 2 - 0.8 + PAD_CLR
    out = Manifold()
    for a, b in D["pads"]["slots"]:
        ends = [Manifold.cylinder(PAD_DROP + PAD_CLR + 0.5, r_tip, r_floor + 0.5 * 0.8 / h, circular_segments=48)
                .translate((X, -Y, -PAD_DROP - PAD_CLR)) for X, Y in C.plan([a, b])]
        out += Manifold.batch_hull(ends)
    return out


def pad_domes():
    """The bump-ons under the floor (half's frame), at both ends of every slot: domes, 8 mm
    across at their top 1.1 mm up in the slot, 6.4 mm at their tip PAD_DROP below the floor."""
    d, h = D["pads"]["size"]
    r_floor = d / 2 - 0.8 * D["pads"]["depth"] / h
    out = Manifold()
    for a, b in D["pads"]["slots"]:
        for X, Y in C.plan([a, b]):
            out += Manifold.cylinder(PAD_DROP, d / 2 - 0.8, r_floor, circular_segments=48).translate((X, -Y, -PAD_DROP))
    return out


PADS = pad_domes()


def rot(axis, deg):
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    m = np.eye(4)
    i, j = {"y": (2, 0), "z": (0, 1)}[axis]
    m[i, i], m[i, j], m[j, i], m[j, j] = c, -s, s, c
    return m


def move(x, y, z):
    m = np.eye(4)
    m[:3, 3] = (x, y, z)
    return m


def apply(m, pts):
    p = np.c_[np.asarray(pts, float), np.ones(len(pts))]
    return (p @ m.T)[:, :3]


class Placement:
    """Where the left half sits for a tent of `tent` degrees: its outer pad on the desk, the
    seam's back end at (-GAP_BACK / 2, 0)."""

    def __init__(self, tent):
        self.tent = tent
        tilt = rot("y", -tent)                      # raises +x, the inner side
        lo = PADS.transform(tilt[:3]).bounding_box()[2]      # the outer pad on the desk
        m = move(0, 0, -lo) @ tilt
        back = apply(m, [(WALL_OUT, SEAM_BACK, 0)])[0]
        self.m = move(-GAP_BACK / 2, 0, 0) @ rot("z", -SPLAY) @ move(-back[0], -back[1], 0) @ m
        self.lo = lo

    def __call__(self, solid):
        return solid.transform(self.m[:3])

    def points(self, pts):
        return apply(self.m, pts)

    def floor_z(self, x):
        """Height of the half's floor plane over the desk, at the half's own x."""
        return x * math.sin(math.radians(self.tent)) - self.lo

    def seam(self):
        """The seam's back and front ends on the floor plane, in the dock's plan."""
        return self.points([(WALL_OUT, SEAM_BACK, 0), (WALL_OUT, SEAM_FRONT, 0)])

    def plan(self, solid):
        return unary_union([Polygon(p) for p in self(solid).project().to_polygons()]).buffer(0)


def rounded_rect(w, d, r, cx, y_back):
    return box(cx - w / 2 + r, y_back - d + r, cx + w / 2 - r, y_back - r).buffer(r, quad_segs=12)


def extrude(poly, z0, z1):
    polys = getattr(poly, "geoms", [poly])
    rings = []
    for p in polys:
        rings.append(list(p.exterior.coords)[:-1])
        rings += [list(i.coords)[:-1] for i in p.interiors]
    return CrossSection(rings, FillRule.EvenOdd).extrude(z1 - z0).translate((0, 0, z0))


def mirror_x(poly):
    return Polygon([(-x, y) for x, y in poly.exterior.coords])


def base_back(p):
    """The base's back edge (y): as far forward as keeps its hinge HINGE_CLR clear of the halves,
    the wings and the spine, above the base's top face."""
    wing = wing_solid(p) + p(HALF.hull())
    above = (wing + wing.mirror((1, 0, 0)) + spine_solid(p)).trim_by_plane((0, 0, 1), UG[2])
    block = unary_union([Polygon(q) for q in above.project().to_polygons()]).buffer(0)
    hw, hd = HINGE
    # from behind the halves forwards, to the first touch (further on, the hinge could fit again
    # in the wide front of the gap between them, which isn't wanted)
    y = 100.0
    while not box(-hw / 2, y - 0.1 - hd, hw / 2, y - 0.1).buffer(HINGE_CLR).intersects(block):
        y -= 0.1
    return y


def pocket_plan(yb):
    w, d, _ = UG
    return rounded_rect(w + 2 * UG_TOL, d + 2 * UG_TOL, UG_R, 0, yb + UG_TOL)


def shortfall(tent, magnets):
    """How far the tightest spot is from enough plastic (<= 0: enough), for a tent: the roof
    over the base's pocket under the half, and room under each of the given magnets."""
    p = Placement(tent)
    pocket = pocket_plan(base_back(p))
    worst = -1e9
    x0, y0, x1, y1 = FOOT.bounds
    grid = [(x, y) for x in np.arange(x0, x1, 1.0) for y in np.arange(y0, y1, 1.0) if FOOT.contains(Point(x, y))]
    over = [x for (x, y), P in zip(grid, p.points([(x, y, 0) for x, y in grid])) if pocket.contains(Point(P[:2]))]
    if over:
        worst = max(worst, POCKET_TOP + ROOF - p.floor_z(min(over)))
    # the pad recesses sink into that roof
    r = D["pads"]["slot_w"] / 2 + PAD_CLR
    for a, b in D["pads"]["slots"]:
        for x, y in C.plan([a, b]):
            P = p.points([(x, -y, 0)])[0]
            if pocket.buffer(r).contains(Point(P[:2])):
                worst = max(worst, POCKET_TOP + ROOF + PAD_DROP + PAD_CLR - p.floor_z(x - r))
    for (x, y), P in zip(magnets, p.points([(x, y, 0) for x, y in magnets]) if magnets else []):
        need = MAG_H + 0.1 + UNDER
        if pocket.buffer(MAG_D / 2 + UNDER).contains(Point(P[:2])):
            need += POCKET_TOP + MAG_ROOF - UNDER  # a thinner roof under it than ROOF will do
        worst = max(worst, need - p.floor_z(x - MAG_D / 2))
    if DRAWER and BASE_MAGS:
        worst = max(worst, base_magnet_pocket(0, 0)[1] + UNDER - drawer_floor(p))
    return worst


def least_tent(magnets):
    lo, hi = 0.0, 30.0
    for _ in range(30):
        mid = (lo + hi) / 2
        lo, hi = (lo, mid) if shortfall(mid, magnets) <= 0 else (mid, hi)
    return hi


@lru_cache(maxsize=1)
def solve_tent():
    """The roof's tent, raised for each floor magnet that costs at most MAG_COST more; a magnet
    too near the outer pad (where the slope runs out) would need far more, and is left out. The
    magnets' pockets are nudged() clear of the wing's walls."""
    tent = least_tent([])
    spots = [nudged(x, y) for x, y in MAGNETS]
    used = [m for m in spots if least_tent([m]) <= tent + MAG_COST]
    return max([tent] + [least_tent([m]) for m in used]), used


def dock_side_mags():
    """The halves' inner-wall magnets the dock faces itself: all of them, or with a drawer
    DOCK_MAGS (a module faces DRAWER_MAGS)."""
    return list(DOCK_MAGS) if DRAWER else list(range(len(D["magnets_side_y"])))


def seam_magnets(grow=0.0):
    """Pockets in the spine, in the half's frame: one facing each seam magnet in dock_side_mags(),
    from the spine's face (CLR off the seam) SIDE_H deep, the magnet flush with the face (`grow`
    larger all round: the plastic they need round them)."""
    out = Manifold()
    for my in [D["magnets_side_y"][i] for i in dock_side_mags()]:
        m = Manifold.cylinder(SIDE_H + 0.1 + grow, SIDE_D / 2 + grow, circular_segments=40).rotate((0, 90, 0))
        out += m.translate((WALL_OUT + CLR - 0.05, -my, D["magnet_side_z"]))
    return out


def base_magnet_spots(dock, pocket):
    """Over the base, where the dock is solid from the pocket's roof up past both magnets plus
    UNDER, all round. Up to BASE_MAGS of them, symmetric about x = 0: the largest triangle first
    (one on the centre line, a mirrored pair) when there is room for one, then each next one (a
    pair, or one on the centre line) as far from the rest as it can be, while they keep apart."""
    r = BASE_MAG[0] / 2 + BASE_MAG_SLOP + 1.0
    top = base_magnet_pocket(0, 0)[1] + UNDER
    ok = solid_region(dock, POCKET_TOP + 0.05, top).intersection(pocket).buffer(-r)
    ok = ok.intersection(affinity.scale(ok, -1, 1, origin=(0, 0)))
    if ok.is_empty:
        return []
    x0, y0, x1, y1 = ok.bounds
    grid = [(x, y) for x in np.arange(0, x1, 0.5) for y in np.arange(y0, y1, 0.5) if ok.contains(Point(x, y))]
    apexes = [y for x, y in grid if x == 0]
    pairs = [q for q in grid if q[0] >= r]
    if apexes and pairs:
        (x, y), ya = max(((q, ya) for q in pairs for ya in apexes), key=lambda t: t[0][0] * abs(t[1] - t[0][1]))
        spots = [(0.0, ya), (-x, y), (x, y)]
    elif apexes:
        spots = [(0.0, apexes[len(apexes) // 2])]
    else:
        spots = [(-pairs[0][0], pairs[0][1]), pairs[0]] if pairs else []
    while spots and len(spots) < BASE_MAGS:
        room = BASE_MAGS - len(spots)
        options = [q for q in grid if (q[0] == 0 or (room >= 2 and q[0] >= r))]
        if not options:
            break
        q = max(options, key=lambda q: min(math.dist(q, s) for s in spots + ([(-q[0], q[1])] if q[0] else [])))
        if min(math.dist(q, s) for s in spots) < 2 * r:
            break                                   # no room for another
        spots += [q] if q[0] == 0 else [(-q[0], q[1]), q]
    return spots


def base_magnet_pocket(x, y):
    """Up from the pocket's roof: room for the base's magnet (glued on its top, BASE_MAG_SLOP
    round it), then the dock's own, pressed in from below, with 0.3 between the two."""
    bd, bh = BASE_MAG
    low_top = UG[2] + bh + 0.3
    low = Manifold.cylinder(low_top - POCKET_TOP + 0.01, bd / 2 + BASE_MAG_SLOP, circular_segments=48)
    high = Manifold.cylinder(bh, bd / 2, circular_segments=40)
    return (low.translate((x, y, POCKET_TOP - 0.01)) + high.translate((x, y, low_top))), low_top + bh


def spine_plan(p, top):
    """The spine in plan: between the seams, reaching under each half as far as its seam wall
    leans out up to the spine's top (seam_planes() then cuts the faces), and well past the
    seams' ends (front_planes(), front_flat() and back_flat() then cut them)."""
    lean = top * math.tan(math.radians(p.tent)) + 0.5
    pts = p.points([(WALL_OUT - lean, SEAM_BACK + 30, 0), (WALL_OUT - lean, SEAM_FRONT - 30, 0)])
    (bx, by, _), (fx, fy, _) = pts
    return Polygon([(bx, by), (fx, fy), (-fx, fy), (-bx, by)])


def extended_body():
    """Under the half, from its girdle down past the desk (half's frame): every wall carries on
    the case's own 45-degree bottom chamfer (girdle GIRDLE out at CHAMFER up, in by as much as it
    drops), each one flat plane through its girdle edge, so the board's chamfer and the dock's
    wall are one face. The seam stays a flat face."""
    girdle = Polygon(C.plan([tuple(q) for q in D["case_outline"][:-1]])).buffer(C.GIRDLE, join_style=2, mitre_limit=10)
    ring = [(x, -y) for x, y in girdle.exterior.coords[:-1]]           # real frame
    cx, cy = Polygon(ring).centroid.coords[0]
    x0, y0, x1, y1 = Polygon(ring).bounds
    body = Manifold.cube((x1 - x0 + 2, y1 - y0 + 2, 60)).translate((x0 - 1, y0 - 1, C.CHAMFER - 60))
    for (ax, ay), (bx, by) in zip(ring, ring[1:] + ring[:1]):
        n = np.array((by - ay, -(bx - ax)))
        n /= np.linalg.norm(n)
        if n @ (np.array((ax, ay)) - (cx, cy)) < 0:
            n = -n                                                     # outwards
        if n[0] > 0.99:
            continue                                                   # the seam: flat, below
        # keep n.(x, y) - z <= n.a - CHAMFER: in by as much as it drops below the girdle
        w = np.array((-n[0], -n[1], 1.0)) / math.sqrt(2)
        body = body.trim_by_plane(tuple(w), (-(n @ (ax, ay)) + C.CHAMFER) / math.sqrt(2))
    return body.trim_by_plane((-1, 0, 0), -WALL_OUT)


def nudged(x, y):
    """A floor magnet's pocket in the wing: right under the case's magnet, or moved the least it
    takes (up to 2 mm, any way) off the wing's 45-degree walls to leave 0.5 mm of plastic round
    it, as the case leaves round its own. Two 8 mm magnets that far apart still pull hard."""
    body = extended_body()
    def fits(px, py):
        shell = Manifold.cylinder(MAG_H + 0.6, MAG_D / 2 + 0.5, circular_segments=40).translate((px, py, -MAG_H - 0.6))
        return (shell - body).volume() < 1e-3
    for step in range(21):
        for ang in range(0, 360, 5) if step else [0]:
            px = x + 0.1 * step * math.cos(math.radians(ang))
            py = y + 0.1 * step * math.sin(math.radians(ang))
            if fits(px, py):
                return (px, py)
    raise ValueError("no room for the floor magnet at (%.1f, %.1f)" % (x, y))


def seam_planes(p):
    """Both seam walls as placed: (normal towards the middle, offset) each. The spine is cut to
    CLR inside them, so nothing of it is left over the halves' tops, which slope away from the
    seam."""
    a, b, c = p.points([(WALL_OUT, SEAM_BACK, 0), (WALL_OUT, SEAM_FRONT, 0), (WALL_OUT, SEAM_BACK, 10)])
    n = np.cross(b - a, c - a)
    n = n / np.linalg.norm(n) * (1 if n[0] > 0 else -1)
    m = n * (-1, 1, 1)
    return [(n, n @ a), (m, m @ (a * (-1, 1, 1)))]


def facet_planes(p, y_rim, y_girdle, lower):
    """The left half's facet along a straight front or back edge by the seam, and the right's,
    as placed: (outward normal, offset) each. The facet runs from the rim at y_rim to the girdle
    at y_girdle, CHAMFER up; `lower` is the case's 45-degree chamfer under it, carried on down."""
    top = HALF.bounding_box()[5]
    if lower:      # under the girdle: the case's 45-degree chamfer carried on, in as it drops
        inward = math.copysign(10.0, y_rim - y_girdle)
        first = (WALL_OUT, y_girdle + inward, C.CHAMFER - 10.0)
    else:
        first = (WALL_OUT, y_rim, top)
    a, b, c = p.points([first, (WALL_OUT, y_girdle, C.CHAMFER), (WALL_OUT - 10, y_girdle, C.CHAMFER)])
    n = np.cross(b - a, c - a)
    n = n / np.linalg.norm(n) * (1 if (n[1] > 0) == (y_girdle > y_rim) else -1)   # outwards
    m = n * (-1, 1, 1)
    return [(n, n @ a), (m, m @ (a * (-1, 1, 1)))]


def front_planes(p):
    """Both halves' front facets by the seam, over the girdle and mirrored under it: the spine's
    front carries them on, a V in profile like the halves' walls and the wings under them."""
    ends = (SEAM_FRONT, SEAM_FRONT - C.GIRDLE)
    return facet_planes(p, *ends, False) + facet_planes(p, *ends, True)


def back_planes(p):
    ends = (SEAM_BACK, SEAM_BACK + C.GIRDLE)
    return facet_planes(p, *ends, False) + facet_planes(p, *ends, True)


def girdle_height(p):
    """The halves' girdle where it meets the seam (the same at both ends: the seam runs level)."""
    return p.points([(WALL_OUT, SEAM_BACK, C.CHAMFER)])[0][2]


def flats(p, planes, corner):
    """A flat across the spine's end, leaning as the facets either side do, through `corner`
    (on the left facet), and under the girdle a 45-degree flat as the chamfers either side, the
    crease level with the halves' girdle where it meets the seam, so it runs on across the spine."""
    (n, d), (m, _), (nl, dl), (ml, _) = planes
    f = (n + m) / np.linalg.norm(n + m)
    upper = (f, f @ corner)
    z = girdle_height(p)
    crease = np.array((0.0, (upper[1] - f[2] * z) / f[1], z))
    fl = (nl + ml) / np.linalg.norm(nl + ml)
    return [upper, (fl, fl @ crease)]


def front_flat(p, top):
    """The spine's point cut off square: a flat across the front, as wide at the top as the
    joined board's own front flat (the front edge of each half by the seam, both together)."""
    seg = [x for x, y in D["case_outline"] if abs(-y - SEAM_FRONT) < 1e-6]
    width = 2 * (WALL_OUT - min(seg))
    planes = front_planes(p)
    (n, d) = planes[0]
    x, z = -width / 2, top
    y = (d - n[0] * x - n[2] * z) / n[1]                   # on the left facet, at the top
    return flats(p, planes, np.array((x, y, z)))


def board_diamond():
    """The joined board's outline (both PCBs, as seen from above), centred on the origin."""
    pcb = [(x, -y) for x, y in D["pcb_outline"]]
    seam = max(x for x, _ in pcb)
    both = unary_union([Polygon(pcb), Polygon([(2 * seam - x, y) for x, y in pcb])]).buffer(0.01).buffer(-0.01)
    cx, cy = both.centroid.x, both.centroid.y
    ys = [y for x, y in pcb if abs(x - seam) < 1e-6]
    from shapely.geometry import LineString
    line = LineString([(seam, min(ys)), (seam, max(ys))])
    return affinity.translate(both, -cx, -cy), affinity.translate(line, -cx, -cy)


def relief(top_poly, z):
    """The diamond drawn in sunk lines, RELIEF deep, on the spine's top (its outline and the seam between
    the halves), as large as fits RELIEF's margin inside the top, wherever along it that is."""
    h, w, margin = RELIEF
    shape, seam = board_diamond()
    room = top_poly.buffer(-margin)
    x0, y0, x1, y1 = room.bounds
    best = (0, None)
    for y in np.arange(y0, y1, 0.5):
        lo, hi = 0.0, 1.0
        for _ in range(20):
            k = (lo + hi) / 2
            fits = room.contains(affinity.translate(affinity.scale(shape, k, k, origin=(0, 0)), 0, y))
            lo, hi = (k, hi) if fits else (lo, k)
        if lo > best[0]:
            best = (lo, y)
    k, y = best
    place = lambda g: affinity.translate(affinity.scale(g, k, k, origin=(0, 0)), 0, y)
    shape = place(shape)
    drawing = unary_union([shape.exterior.buffer(w / 2), place(seam).buffer(w / 2, cap_style=2)])
    return extrude(drawing.intersection(shape.buffer(w / 2)), z - h, z + 1), k


def spine_back_y(p):
    return p.seam()[0][1]


def solid_region(m, z0, z1):
    """Where m is solid at every height from z0 to z1 (plan)."""
    out = None
    for z in np.arange(z0, z1 + 0.01, 0.25):
        sl = Polygon()
        for q in m.slice(z).to_polygons():          # even-odd: a hole's ring cuts it back out
            sl = sl.symmetric_difference(Polygon(q).buffer(0))
        out = sl if out is None else out.intersection(sl)
    return out


def widest(ok, n):
    """n points of the region `ok` spanning the largest triangle (a 1 mm grid's hull)."""
    from itertools import combinations
    from shapely.geometry import MultiPoint
    x0, y0, x1, y1 = ok.bounds
    pts = [(x, y) for x in np.arange(x0, x1, 1.0) for y in np.arange(y0, y1, 1.0) if ok.contains(Point(x, y))]
    hull = [tuple(c) for c in MultiPoint(pts).convex_hull.exterior.coords[:-1]]
    area = lambda a, b, c: abs((b[0] - a[0]) * (c[1] - a[1]) - (c[0] - a[0]) * (b[1] - a[1])) / 2
    return list(max(combinations(hull, n), key=lambda q: area(*q[:3])))


def foot_recess(x, y):
    d, h = D["pads"]["size"]
    return Manifold.cylinder(h - FOOT_LIFT + 0.01, d / 2 + PAD_CLR, circular_segments=48).translate((x, y, FOOT_LIFT - 0.01))


def foot_spots(dock):
    """FEET spots under the left wing (the right's are their mirror): where the dock is solid
    from its cut underside up to the recess plus FOOT_SKIN all over the foot, spread to the
    largest triangle for the steadiest stance."""
    d, h = D["pads"]["size"]
    ok = solid_region(dock, FOOT_LIFT + 0.05, h + FOOT_SKIN).buffer(-(d / 2 + PAD_CLR + 0.8))
    return widest(ok.intersection(box(-500, -500, -30, 500)), FEET)


def wing_solid(p):
    """A wing: the half's own body with its leaning walls carried on down to the desk, so the
    dock reads as the board's continuation; the seat cut leaves what is under the half (filling
    its chamfer too). Cut where thinner than MIN_T towards the outer side, where it runs out."""
    x_min = (MIN_T + FOOT_LIFT + p.lo) / math.sin(math.radians(p.tent))
    # and short of the outer slot, whose pad stands on the desk: its recess would hole the edge
    d, h = D["pads"]["size"]
    outer = min(D["pads"]["slots"], key=lambda s: min(x for x, _ in C.plan(s)))
    x_min = max(x_min, max(x for x, _ in C.plan(outer)) + d / 2 + PAD_CLR + 0.5)
    return p(extended_body().trim_by_plane((1, 0, 0), x_min))


def spine_height(p):
    return p.points([(WALL_OUT, SEAM_BACK, HALF.bounding_box()[5])])[0][2]


def spine_solid(p):
    """Between the halves, up both seam walls (over the magnets facing theirs), level with the
    walls' top edges; its front carries on both halves' front facets to a flat, its back is one
    flat flush with both halves' back walls. Above the halves' girdle it stops CLR short of their
    seam walls; below it, it runs on into the wings, one piece with them."""
    top = spine_height(p)
    full = extrude(spine_plan(p, top), 0, top)
    # the halves' back walls, carried across, would meet in a V pointing into the spine: its back
    # is the flat alone (the front's V points out, and the flat cuts its tip)
    for n, d in front_planes(p) + front_flat(p, top) + back_flat(p):
        full = full.trim_by_plane(tuple(-n), -d)
    upper = full
    for n, d in seam_planes(p):
        upper = upper.trim_by_plane(tuple(n), d + CLR)
    lower = Manifold()
    for (n, d), side in zip(girdle_planes(p), (-1, 1)):
        lower += full.trim_by_plane(tuple(-n), -d).trim_by_plane((side, 0, 0), 0)
    return upper + lower


def girdle_planes(p):
    """The left half's girdle plane (its floor plane CHAMFER up) and the right's, as placed:
    (upward normal, offset) each."""
    a, b, c = p.points([(0, 0, C.CHAMFER), (1, 0, C.CHAMFER), (0, 1, C.CHAMFER)])
    n = np.cross(b - a, c - a)
    n = n / np.linalg.norm(n) * (1 if n[2] > 0 else -1)
    m = n * (-1, 1, 1)
    return [(n, n @ a), (m, m @ (a * (-1, 1, 1)))]


def back_flat(p):
    """The spine's back: one flat through both halves' back corners at the rim, leaning back as
    their back walls do, and its mirror under the girdle."""
    planes = back_planes(p)
    top = HALF.bounding_box()[5]
    return flats(p, planes, p.points([(WALL_OUT, SEAM_BACK, top)])[0])


def drawer_magnets(p):
    """The halves' inner-wall magnets a module meets (left half), as placed: centres (x, y, z)."""
    return [p.points([(WALL_OUT, -D["magnets_side_y"][i], D["magnet_side_z"])])[0] for i in DRAWER_MAGS]


def drawer_floor(p):
    """The drawer's floor (z), where a module stands on its feet: its magnets, at a half's own
    height over the desk (the half on its pads, the module on its feet), meet the halves'."""
    return drawer_magnets(p)[0][2] - (D["magnet_side_z"] + PAD_DROP)


def drawer_plan(p, back=None):
    """The drawer in plan: vertical sides DRAWER_WALL in from each half's leaning inner wall where
    it is nearest (the girdle; above it the wall leans away); the back at DRAWER_BACK. The
    front is open and the sides uninterrupted, so every insert pulls straight out forwards."""
    (n, d), _ = seam_planes(p)
    nxy = n[:2] / np.linalg.norm(n[:2])
    c = (d - n[2] * girdle_height(p)) / np.linalg.norm(n[:2]) + DRAWER_WALL
    def half_plane(normal):
        t = np.array((-normal[1], normal[0]))
        o = normal * c
        return Polygon([tuple(o - t * 400), tuple(o + t * 400), tuple(o + t * 400 + normal * 400),
                        tuple(o - t * 400 + normal * 400)])
    sides = half_plane(nxy).intersection(half_plane(np.array((-nxy[0], nxy[1]))))
    return sides.intersection(box(-200, -300, 200, DRAWER_BACK if back is None else back))


REAR_HOOD_T = 1.2             # common top-only extension, flush with the halves at the rear
REAR_HOOD_GAP = 0.25          # normal clearance between the two parallel 45-degree surfaces
USB_EXIT_W = 12.8             # full plug width, open all the way through the dock's underside
USB_EXIT_PLUG_Z = 2.2         # low insertion height, measured above the drawer's standing plane


def rear_hood_end(p):
    """Stop just inside the dock's existing rear facet, without a protruding rear lip."""
    n, d = back_flat(p)[0]
    return (d - n[2] * spine_height(p)) / n[1] - REAR_HOOD_GAP


def rear_hood_plan(p):
    """Continue the insert's side planes rearwards; only its top extends, not its floor."""
    end = rear_hood_end(p)
    return drawer_plan(p, back=end + DRAWER_CLR).buffer(-DRAWER_CLR, join_style=2).intersection(
        box(-200, DRAWER_BACK - DRAWER_CLR - 1.6, 200, end))


def rear_hood_datum(p):
    """The module-frame underside is z = y + datum: exactly 45 degrees in side view."""
    return spine_height(p) - drawer_floor(p) - REAR_HOOD_T - rear_hood_end(p)


def rear_hood_cut(p):
    """Keep a matching 45-degree rear support below the removable module's top extension."""
    plan = rear_hood_plan(p).buffer(REAR_HOOD_GAP, join_style=2).intersection(
        box(-200, DRAWER_BACK, 200, 100))
    blank = extrude(plan, drawer_floor(p), spine_height(p) + 5)
    normal = (0, -1 / math.sqrt(2), 1 / math.sqrt(2))
    datum = drawer_floor(p) + rear_hood_datum(p) - REAR_HOOD_GAP * math.sqrt(2)
    return blank.trim_by_plane(normal, datum / math.sqrt(2))


def module_plan(p, z=None):
    """The insert's plan at global height z, or a plan envelope of its whole faceted front.
    The front is shaped in 3D, not set back to the most restrictive slice at every height."""
    top = spine_height(p)
    out = drawer_plan(p).buffer(-DRAWER_CLR, join_style=2)
    for n, d in front_planes(p) + front_flat(p, top):          # the spine keeps n.(x, y, z) <= d
        at = (drawer_floor(p) if n[2] > 0 else top) if z is None else z
        a, b, c = n[0], n[1], d - n[2] * at                     # a x + b y <= c
        line = [(x, (c - a * x) / b) for x in (-300, 300)]
        far = 600 if b > 0 else -600                            # the outside: a x + b y > c
        out = out.difference(Polygon(line + [(300, far), (-300, far)]))
    return out


def module_front(solid, p, inset=0.0):
    """Continue the halves' exact front planes onto an insert, in its standing-plane frame.
    inset offsets an internal cavity to retain a wall behind the faceted front."""
    for n, d in front_planes(p) + front_flat(p, spine_height(p)):
        solid = solid.trim_by_plane(tuple(-n), -(d - n[2] * drawer_floor(p) - inset))
    return solid


class Dock:
    pass


def build(tent, magnets):
    p = Placement(tent)
    yb = base_back(p)
    pocket = pocket_plan(yb)
    sin = math.sin(math.radians(tent))

    wing, spine, spine_top = wing_solid(p), spine_solid(p), spine_height(p)
    back, front = p.seam()
    side = p(seam_magnets())

    dock = wing + wing.mirror((1, 0, 0)) + spine
    dock = dock.trim_by_plane((0, 0, 1), 0)

    seat = p(HALF.hull().minkowski_sum(Manifold.cylinder(0.01, CLR, circular_segments=16)))
    pads = p(pad_recess())
    mags = Manifold()
    for x, y in magnets:
        mags += Manifold.cylinder(MAG_H + 0.1, MAG_D / 2, circular_segments=40).translate((x, y, -MAG_H - 0.1))
    mags = p(mags.translate((0, 0, 0.01)))
    for cut in (seat, pads, mags, side):
        dock -= cut + cut.mirror((1, 0, 0))
    dock -= extrude(pocket, -1, POCKET_TOP)
    if DRAWER:
        dock -= extrude(drawer_plan(p), drawer_floor(p), spine_top + 1)
        dock -= rear_hood_cut(p)
        # One continuous, full-width opening: no lower step, shelf or floor across it.
        dock -= Manifold.cube((USB_EXIT_W, 70, spine_top + 3)).translate(
            (-USB_EXIT_W / 2, DRAWER_BACK - 0.25, -1))
    spots = base_magnet_spots(dock, pocket)
    for x, y in spots:
        dock -= base_magnet_pocket(x, y)[0]
    if DRAWER:
        x, y = DRAWER_FLOOR_MAG
        dock -= Manifold.cylinder(1.61, 4.1, circular_segments=48).translate(
            (x, y, drawer_floor(p) - 1.6))

    # the underside cut FOOT_LIFT up, and a recess for each bump-on foot in the wings
    dock = dock.trim_by_plane((0, 0, 1), FOOT_LIFT)
    feet = foot_spots(dock)
    for x, y in feet:
        for sx in (1, -1):
            dock -= foot_recess(sx * x, y)

    # the diamond, on the finished top (seats and all cut); with a drawer the spine's top is gone
    scale = 0.0
    if not DRAWER:
        top_poly = unary_union([Polygon(q) for q in dock.slice(spine_top - 0.05).to_polygons()]).buffer(0)
        top_poly = max(getattr(top_poly, "geoms", [top_poly]), key=lambda g: g.area)
        art, scale = relief(top_poly, spine_top)
        dock -= art

    out = Dock()
    out.relief_scale, out.feet = scale, feet
    out.solid, out.p, out.yb, out.magnets, out.base_spots, out.spine_top = dock, p, yb, magnets, spots, spine_top
    return out


def feet_solids(k):
    """The bump-ons, in place (real frame), for renders."""
    d, h = D["pads"]["size"]
    out = Manifold()
    for x, y in k.feet:
        for sx in (1, -1):
            out += Manifold.cylinder(h, d / 2 - 0.8, d / 2, circular_segments=40).translate((sx * x, y, 0))
    return out


def magnet_solids(k):
    """Every magnet the dock holds, in place (real frame): the slopes', the spine's, the dock's
    over the base and the base's own glued on its top. For renders."""
    disc = lambda: Manifold.cylinder(MAG_H, MAG_D / 2 - 0.1, circular_segments=32)
    half = Manifold()
    for x, y in k.magnets:
        half += disc().translate((x, y, -MAG_H - 0.01))
    for my in [D["magnets_side_y"][i] for i in dock_side_mags()]:
        side_disc = Manifold.cylinder(SIDE_H, SIDE_D / 2 - 0.1, circular_segments=32)
        half += side_disc.rotate((0, 90, 0)).translate((WALL_OUT + CLR, -my, D["magnet_side_z"]))
    half = k.p(half)
    out = half + half.mirror((1, 0, 0))
    bd, bh = BASE_MAG
    low_top = UG[2] + bh + 0.3
    bdisc = lambda: Manifold.cylinder(bh - 0.1, bd / 2 - 0.1, circular_segments=32)
    for x, y in k.base_spots:
        out += bdisc().translate((x, y, low_top + 0.05)) + bdisc().translate((x, y, UG[2]))
    if DRAWER:
        x, y = DRAWER_FLOOR_MAG
        out += Manifold.cylinder(1.5, 4, circular_segments=48).translate(
            (x, y, drawer_floor(k.p) - 1.5))
    return out


def placement():
    """Where the halves sit, without building the dock (for the modules' design)."""
    return Placement(solve_tent()[0])


def make():
    tent, magnets = solve_tent()
    return build(tent, magnets)


def check(k):
    dock, p, yb, magnets = k.solid, k.p, k.yb, k.magnets
    half = p(HALF)
    pads = p(PADS)
    w, d, t = UG
    ugreen = extrude(rounded_rect(w, d, UG_R, 0, yb), 0, t)
    hinge = extrude(box(-HINGE[0] / 2, yb - HINGE[1], HINGE[0] / 2, yb), t, t + 40)
    print("extra tent %.2f deg (case's own %.1f: %.1f in all), splay %.0f deg per half" %
          (p.tent, D["tent_deg"], p.tent + D["tent_deg"], SPLAY))
    back, front = p.seam()
    print("seams %.1f mm apart at the back, %.1f at the front; spine top %.1f mm over the desk, the halves' "
          "seam tops %.1f; diamond at %.0f %% scale" %
          (-2 * back[0], -2 * front[0], k.spine_top, p(HALF).bounding_box()[5], 100 * k.relief_scale))
    print("base: back edge %.1f mm behind the seams' back ends, front edge %.1f mm from their front ends"
          % (yb, (yb - d) - front[1]))
    print("half's lowest point %.2f mm over the desk, its pads' %.2f (the outer pad stands on the desk)" %
          (half.bounding_box()[2], pads.bounding_box()[2]))
    for name, m in (("left half", half), ("right half", half.mirror((1, 0, 0))),
                    ("left pads", pads), ("right pads", pads.mirror((1, 0, 0))),
                    ("ugreen base", ugreen), ("hinge zone", hinge)):
        print("  dock x %-12s %.3f mm3" % (name, (dock ^ m).volume()))
    probe = p(HALF.hull().translate((0, 0, -0.05)))
    print("  slope contact (half lowered 0.05 mm) %.1f mm3" % (dock ^ probe).volume())
    # roof: within the dock's outline at the roof's underside (holes in it filled: they would be what
    # this looks for), every slice up to ROOF covers the pocket; behind that the walls lean in
    # under the girdle and the base's bare back strip runs on under them
    top_sl = unary_union([Polygon(q) for q in dock.slice(POCKET_TOP + 0.05).to_polygons()]).buffer(0)
    outline = unary_union([Polygon(g.exterior) for g in getattr(top_sl, "geoms", [top_sl])])
    under = pocket_plan(yb).intersection(outline.buffer(-0.05))
    for x, y in magnets:                     # a magnet over the base has MAG_ROOF under it
        P = p.points([(x, y, 0)])[0]
        for sx in (1, -1):
            under = under.difference(Point(sx * P[0], P[1]).buffer(MAG_D / 2 + 1.0))
    for x, y in k.base_spots:                # and the base's magnets have their own pockets
        under = under.difference(Point(x, y).buffer(BASE_MAG[0] / 2 + BASE_MAG_SLOP + 0.05))
    gaps = []
    for z in np.arange(POCKET_TOP + 0.05, POCKET_TOP + ROOF, 0.1):
        sl = Polygon()
        for q in dock.slice(z).to_polygons():      # even-odd: holes count as holes
            sl = sl.symmetric_difference(Polygon(q).buffer(0))
        gaps.append(under.difference(sl).area)
    print("  roof over the base, %.1f mm: %.2f mm2 uncovered at worst" % (ROOF, max(gaps)))
    print("  floor magnets: %d of %d per half" % (len(magnets), len(MAGNETS)))
    for x, y in magnets:
        r = MAG_D / 2
        pocket = Manifold.cylinder(MAG_H + 0.1, r, circular_segments=40).translate((x, y, -MAG_H - 0.09))
        shell = Manifold.cylinder(MAG_H + 0.1 + UNDER, r + 1.0, circular_segments=40).translate(
            (x, y, -MAG_H - 0.09 - UNDER)) - pocket
        shell = shell.trim_by_plane((0, 0, -1), 0)
        sh, pk = p(shell), p(pocket)
        print("  magnet at (%5.1f, %5.1f): %.1f %% of the shell round and under it is plastic, pocket %.1f %% open"
              % (x, y, 100 * (sh ^ dock).volume() / sh.volume(), 100 * (pk - dock).volume() / pk.volume()))
    side = Manifold()
    for my in [D["magnets_side_y"][i] for i in dock_side_mags()]:
        r = SIDE_D / 2
        pocket = Manifold.cylinder(SIDE_H + 0.1, r, circular_segments=40).rotate((0, 90, 0))
        shell = Manifold.cylinder(SIDE_H + 1.1, r + 1.0, circular_segments=40).rotate((0, 90, 0)) - pocket
        at = lambda m: p(m.translate((WALL_OUT + CLR - 0.05, -my, D["magnet_side_z"])))
        sh, pk = at(shell), at(pocket)
        print("  spine magnet y %5.1f: %.1f %% of the shell round and behind it is plastic, pocket %.1f %% open" %
              (my, 100 * (sh ^ dock).volume() / sh.volume(), 100 * (pk - dock).volume() / pk.volume()))
        if DRAWER:
            skin = Manifold.cylinder(DRAWER_SKIN, r, circular_segments=40).rotate((0, 90, 0))
            skin = at(skin.translate((SIDE_H + 0.1, 0, 0)))
            for name, cap in (("left", skin), ("right", skin.mirror((1, 0, 0)))):
                missing = abs((cap - dock).volume())
                print("    %s drawer skin %.1f mm: %.3f mm3 missing" % (name, DRAWER_SKIN, missing))
                assert missing < 1e-3, "side magnet backing skin is incomplete"
    for x, y in k.base_spots:
        pocket, top = base_magnet_pocket(x, y)
        shell = Manifold.cylinder(top - POCKET_TOP + UNDER, BASE_MAG[0] / 2 + BASE_MAG_SLOP + 1.0,
                                  circular_segments=48).translate((x, y, POCKET_TOP)) - pocket
        print("  base magnet (%5.1f, %5.1f): %.1f %% of the shell round and over it is plastic, pocket %.1f %% open" %
              (x, y, 100 * (shell ^ dock).volume() / shell.volume(), 100 * (pocket - dock).volume() / pocket.volume()))
    d_, h_ = D["pads"]["size"]
    for x, y in k.feet:
        rec = foot_recess(x, y)
        shell = Manifold.cylinder(h_ - FOOT_LIFT + FOOT_SKIN, d_ / 2 + PAD_CLR + 0.8,
                                  circular_segments=48).translate((x, y, FOOT_LIFT)) - rec
        print("  foot at (%6.1f, %6.1f) and its mirror: %.1f %% of the plastic round and over it there" %
              (x, y, 100 * (shell ^ dock).volume() / shell.volume()))
    print("  feet stand %.1f mm proud of the cut underside (pads %.1f mm tall)" % (FOOT_LIFT, h_))
    b = dock.bounding_box()
    print("dock: %.1f x %.1f x %.1f mm, %.1f cm3, genus %d, %d piece(s)" %
          (b[3] - b[0], b[4] - b[1], b[5] - b[2], dock.volume() / 1000, dock.genus(), len(dock.decompose())))
    hb = (half + half.mirror((1, 0, 0))).bounding_box()
    print("keyboard span %.1f mm, seam top %.1f mm over the desk" % (hb[3] - hb[0], hb[5]))
    return half, ugreen


if __name__ == "__main__":
    k = make()
    half, ugreen = check(k)
    C.stl(k.solid, "case/dock.stl")
    shutil.copyfile("case/dock.stl", f"{C.STLS}/dock.stl")
    C.stl(half + half.mirror((1, 0, 0)), ".render/dock_halves.stl")
    C.stl(ugreen, ".render/dock_ugreen.stl")
