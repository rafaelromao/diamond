"""Slim Diamond: places the electronics, magnets and outlines around the key layout.

Writes design.json, the single source of truth for the PCB and case generators,
and design.png, a top view.

Coordinates: KiCad's (mm, y down), seen from the top of the LEFT half. The
PCB is reversible: the right half is the same board turned over, so it is the
mirror image about the inner wall (x = wall_out). Everything hanging under the
PCB is checked against both halves' hot-swap sockets.

Tenting: the case floor lies on the desk and the PCB tilts up towards the
inner wall, around an axis parallel to it. The angle is the smallest one that
gives every part hanging under the PCB (sockets, Xiao, battery, connector)
its height.
"""
import json
import math

from shapely import affinity
from shapely.geometry import LineString, MultiPoint, Point, Polygon, box
from shapely.ops import unary_union

from layout import cap, layout_left

# --- parts (sizes include tolerance) ----------------------------------------------
XIAO_W, XIAO_L = 20.8, 21.3        # 17.5 x 21 module; width includes the iron-friendly pads
XIAO_DEPTH = 1.0 + 3.3             # Xiao PCB + USB-C shell, hanging under our PCB
BATT_W, BATT_L, BATT_T = 20.5, 26.0, 7.5   # 752025, leads on a 20 mm side
SOCKET_DEPTH = 1.85                # Kailh hot-swap socket
JST_W, JST_D, JST_H = 9.2, 10.9, 4.9  # JST PH S2B-PH-SM4-TB, pads included
PLUG_L = 9.0                       # room in front of the JST opening for the plug and its wires
PWR_W, PWR_D, PWR_H = 8.8, 4.6, 1.6  # MSK-12C02, body + pads (the lever reaches into the wall)
PCB_T = 1.6
# Where the search below put the Xiao (centre, angle, power-switch offset); pinned so layout
# tweaks don't move it.
# None runs the search again.
XIAO_SPOT = ((-10.0, 34.0), -140, 16.4)
GEM_FACETS = 10                    # sides of the joined outline (both halves)
XIAO_CHANNEL = 1.6                 # routing room between the Xiao's pads and any socket
USB_NOTCH_W = 13.0                 # board-edge notch in front of the USB-C: overmolds are up to 12.35 wide
JLC_MAX = 100.0                    # JLCPCB's cheapest tier: up to 100 x 100 mm
AIR = 0.4                          # vertical clearance under every part

# --- case ---------------------------------------------------------------------
WALL = 1.6                         # case wall thickness
FIT = 0.5                          # PCB and plate to the outer walls: JLCPCB's outline is +-0.2 mm, and
                                   # printed walls come in a little (0.3 mm at the seam)
CAP_CLEAR = 0.75                   # keycap to wall
FLOOR = 2.6                        # floor; 6x2 magnets sit in pockets in it
# Case screws: M3 x 8 flat head (90-degree countersunk, ISO 10642 / DIN 7991), through the plate
# and the PCB, self-tapping into the solid Nylon base: a thread-forming screw grips well there
# and needs no heat. For heat-set inserts instead, set pilot_d to the insert's hole (about 4.0
# for an M3 x 4 x 4.2 insert).
SCREW = {"name": "M3", "pcb_hole": 3.4, "head_d": 6.4, "boss_d": 7.6, "pilot_d": 2.5, "length": 8.0}
# Top plate (Choc v1: 13.8 mm body through the plate, flange 2.2 mm over the PCB, clips take
# plates up to 1.3 mm). Printed holes come out small: the cutout gets CUT_TOL per side.
PLATE = {"thick": 1.2, "gap": 1.0, "cut": 13.8, "cut_tol": 0.1, "blob_pocket": 0.5, "chamfer": 0.6}
MAG_FLOOR = (6.2, 2.1)             # pocket for 6x2 disc magnets (back-to-back)
MAG_SIDE = (5.2, 2.1)              # pocket for 5x2 disc magnets (unibody)
GIRDLE = 2.0                       # floor flare past the rim: the lean of the gem facets
CHAMFER = 1.5                      # 45-degree cut under the girdle; the foot on the desk is inside it
# Anti-slip pads, as on the original Diamond's base: 8 x 2 mm silicone bump-ons in stadium slots
# under the floor, two pad spots per slot. Each half sticks its pad in one end and leaves the
# other empty: stacked, the other half's pad lands there, so the floors still meet. The case is
# the same for both halves; only where the pads go differs.
PAD = (8.0, 2.0)                   # bump-on diameter, height
PAD_SLOT_W = 8.6                   # slot width: the pad + 0.3 per side (the original's 8.6)
PAD_PITCH = 8.7                    # the slot's two spots, centre to centre (the original's 8.7)
PAD_DEPTH = 1.1                    # a pad sticks out 0.9; stacked, 0.2 to spare in the other slot
PAD_EDGE = 1.0                     # slot to the foot's edge, where the chamfer starts
PAD_KEEP = 0.5                     # slot to the magnets and screw pilots (the magnets' skin rule)
PAD_BALANCE = 2.0                  # every key centre this far inside each half's pads
PAD_COUNT = 5                      # four (the original's) leave the thumbs and pinky 0.5 mm inside
# Where the search below put the slots: centre (floor plan, mm) and angle (degrees); pinned so
# layout tweaks don't move them. None runs the search again.
PAD_SLOTS = [((-45.0, 10.0), 95), ((29.0, -24.0), 0), ((-25.5, -21.0), 135),
             ((18.0, 57.0), 20), ((33.0, 58.0), 85)]

KEY_ORDER = ["pinky", "ring_top", "ring_home", "ring_bottom",
             "middle_top", "middle_home", "middle_bottom",
             "index_top", "index_home", "index_bottom",
             "thumb_outer", "thumb_inner"]


def place(shape, c, r):
    return affinity.translate(affinity.rotate(shape, r, origin=(0, 0)), c[0], c[1])


def rect(w, h):
    return box(-w / 2, -h / 2, w / 2, h / 2)


def under_switch(c, r):
    """What hangs under the PCB at one switch, for either half: both sockets and the pins."""
    socket = unary_union([box(-2.45, -8.45, 7.75, -1.25),     # socket body
                          box(-4.8, -7.25, -2.2, -4.75),       # pad 1
                          box(7.225, -5.05, 9.775, -2.55)])    # pad 2
    pins = unary_union([Point(0, 0).buffer(2.0), Point(-5.5, 0).buffer(1.2),
                        Point(5.5, 0).buffer(1.2)])
    both = unary_union([socket, affinity.scale(socket, -1, 1, origin=(0, 0)), pins])
    return place(both, c, r)


def smooth(g):
    """Close slots narrower than 5 mm, keeping straight facets."""
    return g.buffer(2.5, join_style=2).buffer(-2.5, join_style=2)


def enclosing_polygon(shape, k):
    """The convex polygon of at most k sides around shape, with the least area: start from the
    convex hull and repeatedly drop the edge whose removal (extending its neighbours to meet)
    adds the least area."""
    pts = list(shape.convex_hull.exterior.coords)[:-1]

    def meet(a, b, c, d):
        den = (a[0] - b[0]) * (c[1] - d[1]) - (a[1] - b[1]) * (c[0] - d[0])
        if abs(den) < 1e-9:
            return None
        t = ((a[0] - c[0]) * (c[1] - d[1]) - (a[1] - c[1]) * (c[0] - d[0])) / den
        return (a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1]))

    while len(pts) > k:
        best = None
        n = len(pts)
        for i in range(n):
            m = meet(pts[i - 1], pts[i], pts[(i + 1) % n], pts[(i + 2) % n])
            if m is None:
                continue
            new = pts[:]
            new[i] = m
            del new[(i + 1) % n]
            p = Polygon(new)
            if p.is_valid and p.contains(shape.buffer(-1e-6)):
                cost = p.area
                if best is None or cost < best[0]:
                    best = (cost, new)
        if best is None:
            break
        pts = best[1]
    return Polygon(pts)


def largest(g):
    return max(getattr(g, "geoms", [g]), key=lambda p: p.area)


def local_to_board(c, ang, p):
    a = math.radians(ang)
    return (c[0] + p[0] * math.cos(a) - p[1] * math.sin(a),
            c[1] + p[0] * math.sin(a) + p[1] * math.cos(a))


def stadium(a, b, w):
    return LineString([a, b]).buffer(w / 2)


def support_margin(pads, points):
    """How far the closest point lies inside the pads' convex hull (negative: outside)."""
    hull = MultiPoint(pads).convex_hull
    return min((1 if hull.contains(Point(p)) else -1) * hull.exterior.distance(Point(p)) for p in points)


def slot_ends(c, ang, centre):
    """A pad slot's two spots, the left half's first: counterclockwise round the floor's centre
    seen from above (y down), so clockwise seen from below. The right half, the mirror image,
    uses the other end, which is then clockwise seen from below too."""
    a = math.radians(ang)
    d = (math.cos(a) * PAD_PITCH / 2, math.sin(a) * PAD_PITCH / 2)
    e1, e2 = (c[0] + d[0], c[1] + d[1]), (c[0] - d[0], c[1] - d[1])
    cross = (e1[0] - centre[0]) * (e2[1] - centre[1]) - (e1[1] - centre[1]) * (e2[0] - centre[0])
    return (e1, e2) if cross >= 0 else (e2, e1)


def pad_slot_ok(c, ang, foot, blockers):
    """The slot fits in the foot, PAD_EDGE in, and keeps clear of blockers [(point, radius)]."""
    e1, e2 = slot_ends(c, ang, (0, 0))
    seg = LineString([e1, e2])
    return foot.buffer(-PAD_EDGE, join_style=2).contains(seg.buffer(PAD_SLOT_W / 2)) and \
        all(seg.distance(Point(p)) >= r + PAD_SLOT_W / 2 for p, r in blockers)


def search_pad_slots(foot, blockers, keys):
    """PAD_COUNT slots near the foot's edge that keep every key centre deepest inside both
    halves' pads (each half's hull of its own ends). Hill-climbs from seeded random starts on a
    1 mm / 10 degree grid, then refines on 0.5 mm / 5 degrees."""
    import random
    centre = foot.centroid.coords[0]
    core = foot.buffer(-(PAD_EDGE + PAD_SLOT_W / 2), join_style=2)

    def cand(x, y, ang):
        if not pad_slot_ok((x, y), ang, foot, blockers):
            return None
        return ((x, y), ang, slot_ends((x, y), ang, centre))

    b = foot.bounds
    pool = [c for x in range(int(b[0]), int(b[2]) + 1) for y in range(int(b[1]), int(b[3]) + 1)
            if core.contains(Point(x, y)) and core.exterior.distance(Point(x, y)) < 3
            for ang in range(0, 180, 10) for c in [cand(x, y, ang)] if c]

    def score(sel):
        for i in range(len(sel)):
            for j in range(i):
                if LineString(sel[i][2]).distance(LineString(sel[j][2])) < PAD_SLOT_W + 1:
                    return (-99, 0)
        m = min(support_margin([s[2][k] for s in sel], keys) for k in (0, 1))
        return (round(m, 2), MultiPoint([p for s in sel for p in s[2]]).convex_hull.area)

    def climb(sel, options):
        best = score(sel)
        better = True
        while better:
            better = False
            for i in range(len(sel)):
                for o in options:
                    s = score(sel[:i] + [o] + sel[i + 1:])
                    if s > best:
                        sel, best, better = sel[:i] + [o] + sel[i + 1:], s, True
        return sel, best

    random.seed(0)
    sel, best = None, None
    for _ in range(8):
        s, sc = climb(random.sample(pool, PAD_COUNT), pool)
        if best is None or sc > best:
            sel, best = s, sc
    for _ in range(3):
        near = [c for (x, y), ang, _ in sel for dx in range(-3, 4) for dy in range(-3, 4)
                for da in (-10, -5, 0, 5, 10) for c in [cand(x + dx / 2, y + dy / 2, ang + da)] if c]
        sel, best = climb(sel, near)
    return [(c, ang) for c, ang, _ in sel]


def main():
    keys = layout_left()
    caps = {n: cap(*keys[n]) for n in KEY_ORDER}
    capu = unary_union(list(caps.values()))
    capzone = capu.buffer(CAP_CLEAR, join_style=2)
    under = unary_union([under_switch(*keys[n]) for n in KEY_ORDER])
    housings = unary_union([place(rect(15, 15), *keys[n]) for n in KEY_ORDER])
    wall_in = capu.bounds[2] + CAP_CLEAR      # tight: the inner thumb sets the seam
    x_out = capu.bounds[0]
    # The unibody seam: a straight inner wall from the back edge down to the inner thumb.
    seam = box(wall_in - 12, capzone.bounds[1], wall_in, caps["thumb_inner"].centroid.y)
    # socket pads of the outer keys reach past the keycaps: the board must cover them
    body = smooth(unary_union([capzone, seam, under.buffer(0.65, join_style=2)]))

    # --- Xiao + power switch, and the outline they shape. The outline is a cut-diamond
    # silhouette: the fewest-facet convex polygon (GEM_FACETS sides) around both halves joined at
    # the seam; side by side it reads as a gem, and each half is its seam side.
    # The Xiao sits clear of every socket, with its USB port and the switch lever (beside the USB
    # end) on the outline's edge. Score: the joined convex hull's area, i.e. the bulk it adds.
    # The battery under the inner keys sets the tent (about 0.115 rise per mm); the Xiao must
    # not ask for more, so it has to sit far enough in.
    BATTERY_SLOPE = 0.115
    xiao_min_x = x_out + (XIAO_DEPTH - SOCKET_DEPTH) / BATTERY_SLOPE

    def mirrored(g):
        return unary_union([g, affinity.scale(g, -1, 1, origin=(wall_in, 0))])

    def candidates():
        for ang in range(-180, 180, 5):
            for gx in range(-60, 40, 2):
                for gy in range(-40, 80, 2):
                    yield ang, gx, gy

    def refine(ang, x, y):
        for da in (-5, 0, 5):
            for dx in range(-4, 5):
                for dy in range(-4, 5):
                    yield ang + da, x + dx * 0.5, y + dy * 0.5

    def search(cands, ranked=None):
        best = None
        for ang, gx, gy in cands:
            c = (gx, gy)
            xiao = place(rect(XIAO_W, XIAO_L), c, ang)
            if xiao.bounds[2] > wall_in - 0.65 or xiao.bounds[0] < xiao_min_x \
                    or xiao.buffer(XIAO_CHANNEL).intersects(under):
                continue
            for side in (-1, 1):
                # a routing channel between the switch and the Xiao's pads, and around it
                off = side * (XIAO_W / 2 + XIAO_CHANNEL + PWR_W / 2)
                sw = place(box(off - PWR_W / 2, -XIAO_L / 2, off + PWR_W / 2, -XIAO_L / 2 + PWR_D), c, ang)
                if sw.bounds[2] > wall_in - 0.65 or sw.buffer(XIAO_CHANNEL).intersects(under):
                    continue
                hull = mirrored(unary_union([body, xiao.buffer(0.65, join_style=2),
                                             sw.buffer(0.65, join_style=2)])).convex_hull
                # USB end and lever on the edge: the strips 1-9 mm in front of them lie outside
                front = place(box(min(-5, off - PWR_W / 2), -XIAO_L / 2 - 9,
                                  max(5, off + PWR_W / 2), -XIAO_L / 2 - 1.65), c, ang)
                hb = hull.bounds
                if front.intersects(hull) or max(hb[2] - wall_in, hb[3] - hb[1]) > JLC_MAX - 1:
                    continue
                if ranked is not None:
                    ranked.append((hull.area, c, ang, off))
                if best is None or hull.area < best[0] - 1e-6:
                    best = (hull.area, c, ang, xiao, sw, off)
        return best

    if XIAO_SPOT:
        xiao_c, xiao_ang, pwr_off = XIAO_SPOT
        xiao = place(rect(XIAO_W, XIAO_L), xiao_c, xiao_ang)
        power = place(box(pwr_off - PWR_W / 2, -XIAO_L / 2, pwr_off + PWR_W / 2, -XIAO_L / 2 + PWR_D),
                      xiao_c, xiao_ang)
    else:
        ranked = []
        best = search(candidates(), ranked)
        _, xiao_c, xiao_ang, xiao, power, pwr_off = search(refine(best[2], *best[1]))
        print("Xiao spot (pin it in XIAO_SPOT):", (xiao_c, xiao_ang, round(pwr_off, 2)))
        # runners-up, at least 6 mm apart: alternatives when the board won't route
        alts = []
        for area, c, ang, off in sorted(ranked):
            if all(math.dist(c, a[0]) > 6 or ang != a[1] for a in alts):
                alts.append((c, ang, round(off, 2)))
            if len(alts) == 8:
                break
        json.dump(alts, open("xiao_alternatives.json", "w"))
    gem = enclosing_polygon(mirrored(unary_union([body, xiao.buffer(0.65, join_style=2),
                                                  power.buffer(0.65, join_style=2)])), GEM_FACETS)
    gem = largest(gem.intersection(box(-1e3, -1e3, wall_in, 1e3)))
    inner = gem.buffer(-0.65, join_style=2)       # where parts may sit, 0.65 mm off the edge
    pwr_ang = xiao_ang
    # switch body centre 1.75 mm in from the edge: shield pads keep 0.3 mm, the lever pokes out
    power_c = local_to_board(xiao_c, xiao_ang, (pwr_off, -XIAO_L / 2 + 1.75))
    usb_dir = (math.sin(math.radians(xiao_ang)), -math.cos(math.radians(xiao_ang)))

    def tent_for(items):
        """Smallest rise per mm giving each (shape, height) its room under the PCB."""
        z_out = SOCKET_DEPTH + AIR
        slope = 0.0
        for shape, h in items:
            run = shape.bounds[0] - x_out
            if h + AIR <= z_out:
                continue
            # past the outermost key the PCB is at its lowest: nothing taller fits there
            slope = max(slope, (h + AIR - z_out) / run if run > 1.0 else math.inf)
        return z_out, slope

    def items_for(batt, extra=()):
        items = [(xiao, XIAO_DEPTH), (power, PWR_H), (batt, BATT_T), *extra]
        over = batt.intersection(under)
        if not over.is_empty:
            items.append((over, BATT_T + SOCKET_DEPTH))
        return items

    # --- battery: anywhere inside the case, clear of the Xiao and switch, where it needs
    # the least tent (sitting under sockets costs their depth on top of its own).
    inside = gem.buffer(-0.3)
    keep_off = unary_union([xiao, power]).buffer(0.5)
    best = None
    for ang in (0, 90):
        w, l = (BATT_W, BATT_L) if ang == 0 else (BATT_L, BATT_W)
        for gx in range(-50, 40):
            for gy in range(-30, 70):
                batt = box(gx, gy, gx + w, gy + l)
                if batt.bounds[2] > wall_in or not inside.contains(batt) or batt.intersects(keep_off):
                    continue
                _, slope = tent_for(items_for(batt))
                # tie-break towards the inner wall
                key = (round(slope, 5), -batt.bounds[2])
                if best is None or key < best[0]:
                    best = (key, batt)
    batt = best[1]

    # --- JST connector: the spot needing the least tent, nearest the battery, with room in
    # front of its opening for the plug and its wires (PLUG_L). Any of four orientations.
    # 1 mm off the walls: the tilt swings the connector's bottom towards them.
    blocked = unary_union([under, batt, xiao, power]).buffer(0.4)
    plug_blocked = unary_union([xiao, power, batt]).buffer(0.4)
    room = gem.buffer(-1.0, join_style=2)
    best = None
    for jr in (0, 90, 180, 270):
        for gx in range(-60, 40):
            for gy in range(-40, 80):
                # footprint origin; the body spans local y -4.6..6.25, the opening is at +y
                j = place(box(-JST_W / 2, -4.6, JST_W / 2, 6.25), (gx, gy), jr)
                plug = place(box(-JST_W / 2, 6.25, JST_W / 2, 6.25 + PLUG_L), (gx, gy), jr)
                if not room.contains(j) or j.intersects(blocked) or not room.contains(plug) \
                        or plug.intersects(plug_blocked):
                    continue
                _, slope = tent_for(items_for(batt, [(j, JST_H), (plug, JST_H)]))
                key = (round(slope, 5), plug.distance(batt))
                if best is None or key < best[0]:
                    best = (key, j, plug, (gx, gy), jr)
    _, jst, plug, jst_c, jst_r = best
    # the battery bay reaches the plug: leads run from the battery's end into the plug's zone
    bay = unary_union([batt, plug]).convex_hull

    z_out, slope = tent_for(items_for(batt, [(jst, JST_H), (plug, JST_H)]))
    tent = math.degrees(math.atan(slope))
    z_in = z_out + slope * (wall_in - x_out)

    # --- the PCB is the gem, 0.3 mm in; the cavity is FIT - 0.3 mm out from the gem (the seam
    # stays at wall_in), and the case wall follows the cavity.
    cav = largest(gem.buffer(FIT - 0.3, join_style=2).intersection(box(-1e3, -1e3, wall_in, 1e3)))
    case = largest(cav.buffer(WALL, join_style=2, mitre_limit=1.5)
                   .intersection(box(-1e3, -1e3, wall_in + WALL, 1e3)))
    plate_outline = largest(gem.buffer(-0.3, join_style=2))
    # The receptacle hangs under the PCB, so a cable's overmold (up to 6.5 mm tall) reaches
    # above the PCB's underside: notch the edge in front of it, back to the module's USB end.
    # Rounded inner corners: the fab's router bit leaves them anyway.
    usb_notch = place(box(-USB_NOTCH_W / 2, -XIAO_L / 2 - 20, USB_NOTCH_W / 2, -XIAO_L / 2),
                      xiao_c, xiao_ang).buffer(-0.5, join_style=2).buffer(0.5)
    pcb = largest(plate_outline.difference(usb_notch))

    busy = unary_union([under, xiao, power, jst, plug, batt.buffer(1.5)])

    # --- solder jumpers (D0..D2), inside the Xiao's outline on the face opposite the module,
    # so they are bridged from the visible side: the F-face block next to pins L1..L3 (left
    # half), the B-face block next to L12..L14 (right half). Clear of the module's bottom pads
    # (only on its own face, but kept clear anyway) and of the switch housings on top.
    forbidden_local = unary_union([box(-2.4, -9.7, 2.4, -4.9),                      # SWD pads
                                   box(-5.7, -3.3, -3.2, -1.0), box(3.2, -3.3, 5.7, -1.0),  # VBAT/GND
                                   box(-4.9, 7.8, -2.6, 10.7), box(2.6, 7.8, 4.9, 10.7)])   # NFC
    housing_zone = housings.buffer(0.3)
    jblocks = {}
    for side, sx in (("F", 1), ("B", -1)):
        best_j = None
        for cx10 in range(0, 47):
            for cy10 in range(-68, 70):
                lc = (sx * cx10 / 10, cy10 / 10)
                lb = box(lc[0] - 1.6, lc[1] - 3.6, lc[0] + 1.6, lc[1] + 3.6)
                if abs(lc[0]) + 1.6 > 6.7 or lb.bounds[1] < -10.3 or lb.intersects(forbidden_local):
                    continue
                jb = place(lb, xiao_c, xiao_ang)
                if jb.intersects(housing_zone):
                    continue
                d = math.dist(lc, (sx * 8.4, -5.08))      # the middle of the three pins
                if best_j is None or d < best_j[0]:
                    best_j = (d, lc)
        assert best_j, f"no room for the {side} jumpers"
        jblocks[side] = best_j[1]
    # --- screw holes. A flat-head screw goes through the plate (countersunk, on a spacer boss
    # down to the PCB) and the PCB into the solid base. On top: the countersink clears the
    # switch flanges and the solder-blob zone. Underneath: the pilot hole keeps a wall from every
    # pocket, and the base there is deep enough for the screw.
    blob_zone = place(rect(XIAO_W + 2.0, XIAO_L + 2.0), xiao_c, xiao_ang)
    flanges = unary_union([place(rect(15.0, 15.0), *keys[n]) for n in KEY_ORDER])
    pockets = unary_union([under, xiao, power, jst, bay])
    boss_r = SCREW["boss_d"] / 2
    need = SCREW["length"] - PLATE["gap"] - PLATE["thick"] - PCB_T + 0.8   # pilot depth + margin
    deep_enough = box(x_out + (need - FLOOR - z_out) / slope, -1e3, 1e3, 1e3)
    room = (plate_outline.buffer(-(boss_r + 0.3)).intersection(deep_enough)
            .difference(flanges.buffer(SCREW["head_d"] / 2 + 0.4))
            .difference(blob_zone.buffer(boss_r + 0.3))
            .difference(pockets.buffer(SCREW["pilot_d"] / 2 + 1.5)))
    grid = [(gx / 2, gy / 2) for gx in range(-120, 100) for gy in range(-80, 160)
            if room.contains(Point(gx / 2, gy / 2))]
    holes = []
    if grid:
        cx0, cy0 = plate_outline.centroid.x, plate_outline.centroid.y
        holes.append(max(grid, key=lambda p: (p[0] - cx0) ** 2 + (p[1] - cy0) ** 2))
        while len(holes) < 4:
            nxt = max(grid, key=lambda p: min(math.dist(p, q) for q in holes))
            if min(math.dist(nxt, q) for q in holes) < 15:
                break
            holes.append(nxt)

    # --- anti-slip pads, on the floor: the desk plan, where the tent shortens x a little. The
    # foot is the case outline grown by GIRDLE and cut back by CHAMFER, ending CHAMFER short of
    # the seam (as case.py builds it).
    cos_t = math.cos(math.radians(tent))
    to_floor = lambda p: (wall_in + (p[0] - wall_in) * cos_t, p[1])
    from_floor = lambda p: (wall_in + (p[0] - wall_in) / cos_t, p[1])
    seam_x = wall_in + WALL
    foot = (Polygon([to_floor(p) for p in case.exterior.coords])
            .buffer(GIRDLE, join_style=2, mitre_limit=10).buffer(-CHAMFER, join_style=2, mitre_limit=10)
            .intersection(box(-1e3, -1e3, seam_x - CHAMFER, 1e3)))
    key_spots = [to_floor(keys[n][0]) for n in KEY_ORDER]
    pilots = [(to_floor(h), SCREW["pilot_d"] / 2 + PAD_KEEP) for h in holes]
    slots = PAD_SLOTS or search_pad_slots(foot, pilots, key_spots)
    if not PAD_SLOTS:
        print("pad slots (pin them in PAD_SLOTS):", slots)
    for c, ang in slots:
        assert pad_slot_ok(c, ang, foot, pilots), f"pad slot {c} doesn't fit: set PAD_SLOTS = None"
    ends = [slot_ends(c, ang, foot.centroid.coords[0]) for c, ang in slots]
    pads_left = [e[0] for e in ends]
    pads_right = [e[1] for e in ends]          # the right half's, where they land stacked on the left
    flip = lambda p: (2 * seam_x - p[0], p[1])
    balance = {"left": support_margin(pads_left, key_spots),
               "right": support_margin(pads_right, key_spots),
               "unibody": support_margin(pads_left + [flip(p) for p in pads_right],
                                         key_spots + [flip(p) for p in key_spots])}
    assert min(balance.values()) >= PAD_BALANCE, f"pads leave a key too close to tipping: {balance}"
    slot_zone = unary_union([stadium(from_floor(a), from_floor(b), PAD_SLOT_W) for a, b in ends])

    # --- magnets. Floor: four, spread out, away from the Xiao's antenna, the screws and the pads.
    room = (cav.buffer(-MAG_FLOOR[0] / 2 - 0.8).difference(xiao.buffer(8))
            .difference(slot_zone.buffer(MAG_FLOOR[0] / 2 + PAD_KEEP + 0.2)))
    for h in holes:
        room = room.difference(Point(h).buffer(MAG_FLOOR[0] / 2 + 3.5))
    grid = [(gx, gy) for gx in range(-60, 60) for gy in range(-40, 80) if room.contains(Point(gx, gy))]
    cx0, cy0 = cav.centroid.x, cav.centroid.y
    floor_spots = [max(grid, key=lambda p: (p[0] - cx0) ** 2 + (p[1] - cy0) ** 2)]
    while len(floor_spots) < 4:
        floor_spots.append(max(grid, key=lambda p: min(math.dist(p, q) for q in floor_spots)))
    # Inner wall: two, near the ends of its straight part.
    wall_pts = [c for c in case.exterior.coords if abs(c[0] - (wall_in + WALL)) < 1e-6]
    wy0, wy1 = min(c[1] for c in wall_pts), max(c[1] for c in wall_pts)
    # near the ends of the straight seam, with each magnet's boss (about 6 mm square, 4 mm deep)
    # clear of the parts that sit against the inner wall
    near_wall = unary_union([g for g in (batt, jst, xiao, power) if g.bounds[2] > wall_in - 5])
    free = [y / 2 for y in range(int((wy0 + 5) * 2), int((wy1 - 5) * 2))
            if not box(wall_in - 4.5, y / 2 - 4.5, wall_in, y / 2 + 4.5).intersects(near_wall)]
    side_spots = [min(free), max(free)]

    result = {
        "name": "Slim Diamond",
        "keys": {n: {"x": keys[n][0][0], "y": keys[n][0][1], "r": keys[n][1]} for n in KEY_ORDER},
        "xiao": {"x": xiao_c[0], "y": xiao_c[1], "r": xiao_ang, "usb_dir": usb_dir},
        "power_switch": {"x": power_c[0], "y": power_c[1], "r": pwr_ang},
        "battery": {"bounds": list(batt.bounds)},
        "jst": {"x": jst_c[0], "y": jst_c[1], "r": jst_r, "bounds": list(jst.bounds),
                "plug": list(plug.exterior.coords), "bay": list(bay.exterior.coords)},
        "plate": PLATE, "blob_zone": list(blob_zone.exterior.coords),
        "mount_holes": [list(h) for h in holes],
        "screw": SCREW,
        "jumpers_local": jblocks,
        "wall_in": wall_in, "wall_out": wall_in + WALL, "wall": WALL, "x_out": x_out,
        "tent_deg": tent, "slope": slope, "z_out": z_out, "z_in": z_in, "floor": FLOOR, "pcb_t": PCB_T,
        "pcb_outline": list(pcb.exterior.coords),
        "plate_outline": list(plate_outline.exterior.coords),
        "pcb_inner_ring": list(pcb.buffer(-0.45, join_style=2).exterior.coords),
        "case_outline": list(case.exterior.coords),
        "cavity_outline": list(cav.exterior.coords),
        "magnets_floor": [list(map(float, p)) for p in floor_spots], "magnet_floor_size": MAG_FLOOR,
        "magnets_side_y": side_spots, "magnet_side_size": MAG_SIDE,
        "battery_size": [BATT_W, BATT_L, BATT_T],
        "girdle": GIRDLE, "chamfer": CHAMFER,
        # pad slots under the floor, as their two spots (PCB plan, like everything here: case.py
        # maps them to the floor): the left half's pad in the first, the right half's (mirrored
        # about the seam) in the second. Balance: how far the nearest key centre lies inside
        # each half's pads, and the unibody's, on the floor.
        "pads": {"size": PAD, "slot_w": PAD_SLOT_W, "pitch": PAD_PITCH, "depth": PAD_DEPTH,
                 "slots": [[list(from_floor(a)), list(from_floor(b))] for a, b in ends],
                 "balance": balance},
    }
    json.dump(result, open("design.json", "w"), indent=1)

    pb, cb = pcb.bounds, case.bounds
    print(f"PCB  {pb[2]-pb[0]:.1f} x {pb[3]-pb[1]:.1f} mm   case {cb[2]-cb[0]:.1f} x {cb[3]-cb[1]:.1f} mm"
          f"   case area {case.area/100:.1f} cm2")
    print(f"tent {tent:.1f} deg; PCB bottom over floor: outer {z_out:.1f} mm, inner {z_in:.1f} mm")
    print("xiao", [round(v, 1) for v in xiao_c], xiao_ang, "usb", [round(v, 2) for v in usb_dir])
    print("battery", [round(v, 1) for v in batt.bounds], "jst", [round(v, 1) for v in jst.bounds])
    print("holes", holes, "floor magnets", floor_spots, "inner wall y", round(wy0, 1), round(wy1, 1))
    print("pads, on the floor: left", [tuple(round(v, 2) for v in p) for p in pads_left])
    print("                    right", [tuple(round(v, 2) for v in flip(p)) for p in pads_right])
    print("balance: nearest key centre inside the pads by",
          ", ".join(f"{k} {v:.2f} mm" for k, v in balance.items()))

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(9, 9))

    def draw(g, **kw):
        for p in getattr(g, "geoms", [g]):
            ax.fill(*p.exterior.xy, **kw)
    draw(case, color="#bbb")
    draw(cav, color="#f4f4f4")
    draw(pcb, color="#2a7", alpha=0.45)
    for n, c in caps.items():
        draw(c, color="#333", alpha=0.3)
        ax.text(keys[n][0][0], keys[n][0][1], n.replace("_", "\n"), ha="center", va="center", fontsize=6)
    draw(under, color="#c33", alpha=0.55)
    draw(batt, color="#ca3", alpha=0.55)
    draw(xiao, color="#36c", alpha=0.7)
    draw(power, color="#3cc")
    draw(jst, color="#e80")
    draw(plug, color="#fc6", alpha=0.6)
    for lc in jblocks.values():
        draw(place(box(lc[0] - 1.6, lc[1] - 3.6, lc[0] + 1.6, lc[1] + 3.6), xiao_c, xiao_ang), color="#0a0")
    for h in holes:
        draw(Point(h).buffer(2.6).difference(Point(h).buffer(1.1)), color="#555")
    for p in floor_spots:
        draw(Point(p).buffer(MAG_FLOOR[0] / 2), color="#a3c", alpha=0.8)
    for sy in side_spots:
        draw(box(wall_in, sy - MAG_SIDE[0] / 2, wall_in + WALL, sy + MAG_SIDE[0] / 2), color="#a3c")
    # pads: the slots, the left half's pads (filled) and where the right half's land (rings)
    draw(slot_zone, color="#777", alpha=0.35)
    for a, b in ends:
        draw(Point(from_floor(a)).buffer(PAD[0] / 2), color="#111", alpha=0.75)
        ax.plot(*Point(from_floor(b)).buffer(PAD[0] / 2).exterior.xy, color="#111", lw=1, ls="--")
    ax.set_aspect("equal"); ax.invert_yaxis(); ax.grid(alpha=0.3)
    ax.set_title(f"Slim Diamond (left, top view)  case {cb[2]-cb[0]:.0f}x{cb[3]-cb[1]:.0f} mm, tent {tent:.1f}°")
    fig.savefig("design.png", dpi=110, bbox_inches="tight")
    plt.close(fig)
    pad_guide(foot, ends, key_spots, seam_x, plt)


def pad_guide(foot, ends, key_spots, seam_x, plt):
    """renders/pads.png: both floors seen from below (each half turned over about its
    front-to-back axis), where to stick each half's pads."""
    fig, axs = plt.subplots(1, 2, figsize=(12, 6.5))
    halves = (("Left half, from below", lambda p: (-p[0], p[1]), 0),
              ("Right half, from below", lambda p: (p[0], p[1]), 1))
    for ax, (title, view, k) in zip(axs, halves):
        # turned over, the left floor reads mirrored; the right half (the left mirrored) reads
        # like the left's plan, with its pads on the other ends
        tr = lambda g: affinity.scale(g, -1 if k == 0 else 1, 1, origin=(0, 0))
        ax.fill(*tr(foot).exterior.xy, color="#cfd3dc")
        for a, b in ends:
            ax.fill(*tr(stadium(a, b, PAD_SLOT_W)).exterior.xy, color="#8d93a3")
            ax.fill(*tr(Point((a, b)[k]).buffer(PAD[0] / 2)).exterior.xy, color="#222")
        for p in key_spots:
            ax.plot(*view(p), "+", color="#555", ms=6)
        sx = view((seam_x, 0))[0]
        ax.axvline(sx, color="#c33", lw=1)
        ax.text(sx, foot.bounds[1] - 3, "seam", color="#c33", ha="center")
        ax.text(view(foot.centroid.coords[0])[0], foot.bounds[3] + 6, "thumbs (front)", ha="center")
        ax.set_title(title)
        ax.set_aspect("equal"); ax.invert_yaxis(); ax.axis("off")
    fig.suptitle("Anti-slip pads: one per slot, in the end you reach second going clockwise "
                 "round the floor (black). The other end stays empty for the other half's pad. + key centres.",
                 fontsize=10)
    fig.savefig("renders/pads.png", dpi=110, bbox_inches="tight")


if __name__ == "__main__":
    main()
