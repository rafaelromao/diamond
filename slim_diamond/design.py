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
from shapely.geometry import Point, box
from shapely.ops import unary_union

from layout import cap, layout_left

# --- parts (sizes include tolerance) ----------------------------------------------
XIAO_W, XIAO_L = 20.8, 21.3        # 17.5 x 21 module; width includes the iron-friendly pads
XIAO_DEPTH = 1.0 + 3.3             # Xiao PCB + USB-C shell, hanging under our PCB
BATT_W, BATT_L, BATT_T = 20.5, 26.0, 7.5   # 752025, leads on a 20 mm side
SOCKET_DEPTH = 1.85                # Kailh hot-swap socket
JST_W, JST_D, JST_H = 9.2, 10.9, 4.9  # JST PH S2B-PH-SM4-TB, pads included
PWR_W, PWR_D, PWR_H = 8.8, 4.6, 1.6  # MSK-12C02, body + pads (lever pokes out of the wall)
PCB_T = 1.6
# Where the search below put the Xiao (centre, angle); pinned so layout tweaks don't move it.
# None runs the search again.
XIAO_SPOT = ((-13.5, 32.0), -95)
XIAO_CHANNEL = 1.6                 # routing room between the Xiao's pads and any socket
JLC_MAX = 100.0                    # JLCPCB's cheapest tier: up to 100 x 100 mm
AIR = 0.4                          # vertical clearance under every part

# --- case ---------------------------------------------------------------------
WALL = 1.6                         # case wall thickness
CAP_CLEAR = 0.75                   # keycap to wall
FLOOR = 2.6                        # floor; 6x2 magnets sit in pockets in it
MAG_FLOOR = (6.2, 2.1)             # pocket for 6x2 disc magnets (back-to-back)
MAG_SIDE = (5.2, 2.1)              # pocket for 5x2 disc magnets (unibody)

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


def largest(g):
    return max(getattr(g, "geoms", [g]), key=lambda p: p.area)


def local_to_board(c, ang, p):
    a = math.radians(ang)
    return (c[0] + p[0] * math.cos(a) - p[1] * math.sin(a),
            c[1] + p[0] * math.sin(a) + p[1] * math.cos(a))


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

    # --- Xiao + power switch: a spot clear of every socket, with the USB port and the
    # switch lever on an outside edge. Candidates are scored by how much they grow the case.
    base_area = smooth(body).area
    # The battery under the inner keys sets the tent (about 0.115 rise per mm); the Xiao
    # must not ask for more, so it has to sit far enough in.
    BATTERY_SLOPE = 0.115
    xiao_min_x = x_out + (XIAO_DEPTH - SOCKET_DEPTH) / BATTERY_SLOPE
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

    def search(cands):
      best = None
      for ang, gx, gy in cands:
                c = (gx, gy)
                xiao = place(rect(XIAO_W, XIAO_L), c, ang)
                if xiao.bounds[2] > wall_in or xiao.buffer(XIAO_CHANNEL).intersects(under) \
                        or not xiao.intersects(body) or xiao.bounds[0] < xiao_min_x:
                    continue
                front = place(box(-5, -XIAO_L / 2 - 8, 5, -XIAO_L / 2), c, ang)
                if front.intersects(body):
                    continue
                grown = smooth(unary_union([body, xiao]))
                gb = grown.bounds
                if grown.geom_type != "Polygon" or max(gb[2] - gb[0], gb[3] - gb[1]) > JLC_MAX - 0.5:
                    continue
                score = grown.area - base_area
                if best is None or score < best[0] - 1e-6:
                    best = (score, c, ang, xiao)
      return best

    if XIAO_SPOT:
        xiao_c, xiao_ang = XIAO_SPOT
        xiao = place(rect(XIAO_W, XIAO_L), xiao_c, xiao_ang)
    else:
        best = search(candidates())
        _, xiao_c, xiao_ang, xiao = search(refine(best[2], *best[1]))

    # --- power switch: in the notch between the Xiao and the outer thumb key, filled up to
    # the straight line joining them, lever poking out of that edge (towards the typist).
    hull = unary_union([xiao, caps["thumb_outer"].buffer(CAP_CLEAR, join_style=2)]).convex_hull
    # the new edge: the longest hull side running outside the board (the notch's open side)
    board_now = unary_union([body, xiao])
    edge = max((sg for sg in zip(hull.exterior.coords, hull.exterior.coords[1:])
                if not board_now.contains(Point((sg[0][0] + sg[1][0]) / 2, (sg[0][1] + sg[1][1]) / 2))),
               key=lambda sg: math.dist(*sg))
    (ex0, ey0), (ex1, ey1) = edge
    elen = math.dist(edge[0], edge[1])
    tx, ty = (ex1 - ex0) / elen, (ey1 - ey0) / elen
    nx, ny = ty, -tx                                   # pick the normal pointing away from the board
    if Point(ex0 + tx * elen / 2 + nx, ey0 + ty * elen / 2 + ny).within(unary_union([body, xiao, hull])):
        nx, ny = -nx, -ny
    pwr_ang = math.degrees(math.atan2(nx, -ny))        # local -y (the lever) along the normal
    blocked_sw = unary_union([under.buffer(0.4), xiao.buffer(0.8)])
    fits = []
    for k in range(0, 201):
        t = k / 200
        # front of the switch 0.65 mm inside the edge, like the Xiao's USB end
        fx, fy = ex0 + tx * elen * t - nx * 0.65, ey0 + ty * elen * t - ny * 0.65
        c = (fx - nx * PWR_D / 2, fy - ny * PWR_D / 2)
        cand = place(rect(PWR_W, PWR_D), c, pwr_ang)
        if not cand.intersects(blocked_sw) and hull.contains(cand):
            fits.append((cand, c))
    # the middle of the stretch that fits leaves routing room on both sides
    power, power_box_c = fits[len(fits) // 2] if fits else (None, None)
    assert power is not None, "no room for the power switch in the notch"
    # switch body centre 1.75 mm in from the edge: shield pads keep 0.3 mm, the lever pokes out
    power_c = local_to_board(power_box_c, pwr_ang, (0, -PWR_D / 2 + 1.75))
    usb_dir = (math.sin(math.radians(xiao_ang)), -math.cos(math.radians(xiao_ang)))

    def tent_for(items):
        """Smallest rise per mm giving each (shape, height) its room under the PCB."""
        z_out = SOCKET_DEPTH + AIR
        slope = 0.0
        for shape, h in items:
            slope = max(slope, (h + AIR - z_out) / (shape.bounds[0] - x_out))
        return z_out, slope

    def items_for(batt, extra=()):
        items = [(xiao, XIAO_DEPTH), (power, PWR_H), (batt, BATT_T), *extra]
        over = batt.intersection(under)
        if not over.is_empty:
            items.append((over, BATT_T + SOCKET_DEPTH))
        return items

    # --- battery: anywhere inside the case, clear of the Xiao and switch, where it needs
    # the least tent (sitting under sockets costs their depth on top of its own).
    inside = smooth(unary_union([body, xiao, power])).buffer(-0.3)
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

    # --- JST connector: in a socket-free spot near the battery's lead end.
    blocked = unary_union([under, batt, xiao, power]).buffer(0.4)
    jst = None
    for d in range(0, 160):
        for cy in (batt.bounds[1] - JST_D / 2 - 0.5 - d * 0.5, batt.bounds[1] - JST_D / 2 - 0.5 + d * 0.5):
            # 1 mm off the wall: the tilt swings the connector's bottom towards it
            for cx10 in range(int((wall_in - JST_W / 2 - 1.0) * 10), -400, -2):
                j = place(rect(JST_W, JST_D), (cx10 / 10, cy), 0)
                if body.contains(j) and not j.intersects(blocked):
                    jst = j
                    break
            if jst:
                break
        if jst:
            break
    assert jst is not None

    z_out, slope = tent_for(items_for(batt, [(jst, JST_H)]))
    tent = math.degrees(math.atan(slope))
    z_in = z_out + slope * (wall_in - x_out)

    # --- outline. The Diamond look: straight facets and mitred corners, no fillets.
    cav = unary_union([body, xiao.buffer(0.65, join_style=2), power.buffer(0.65, join_style=2),
                       hull.difference(hull.exterior.buffer(0.01)).buffer(0)])
    cav = cav.buffer(4.0, join_style=2).buffer(-4.0, join_style=2)   # no slots narrower than 8 mm
    cav = largest(cav.intersection(box(-1e3, -1e3, wall_in, 1e3)))
    case = largest(cav.buffer(WALL, join_style=2, mitre_limit=1.5)
                   .intersection(box(-1e3, -1e3, wall_in + WALL, 1e3)))
    pcb = largest(cav.buffer(-0.3, join_style=2))

    busy = unary_union([under, xiao, power, jst, batt.buffer(1.5)])   # standoffs stand on the floor

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
    # --- M2 mounting holes: head clear of switch housings on top, standoff clear underneath.
    room = pcb.buffer(-2.6).difference(housings.buffer(2.1)).difference(busy.buffer(2.8))
    grid = [(gx / 2, gy / 2) for gx in range(-120, 100) for gy in range(-80, 160)
            if room.contains(Point(gx / 2, gy / 2))]
    holes = []
    if grid:
        cx0, cy0 = pcb.centroid.x, pcb.centroid.y
        holes.append(max(grid, key=lambda p: (p[0] - cx0) ** 2 + (p[1] - cy0) ** 2))
        while len(holes) < 4:
            nxt = max(grid, key=lambda p: min(math.dist(p, q) for q in holes))
            if min(math.dist(nxt, q) for q in holes) < 15:
                break
            holes.append(nxt)

    # --- magnets. Floor: four, spread out, away from the Xiao's antenna and the screws.
    room = cav.buffer(-MAG_FLOOR[0] / 2 - 0.8).difference(xiao.buffer(8))
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
    side_spots = [wy0 + 7, wy1 - 7]

    result = {
        "name": "Slim Diamond",
        "keys": {n: {"x": keys[n][0][0], "y": keys[n][0][1], "r": keys[n][1]} for n in KEY_ORDER},
        "xiao": {"x": xiao_c[0], "y": xiao_c[1], "r": xiao_ang, "usb_dir": usb_dir},
        "power_switch": {"x": power_c[0], "y": power_c[1], "r": pwr_ang},
        "battery": {"bounds": list(batt.bounds)},
        "jst": {"x": jst.centroid.x, "y": jst.centroid.y, "bounds": list(jst.bounds)},
        "mount_holes": [list(h) for h in holes],
        "jumpers_local": jblocks,
        "wall_in": wall_in, "wall_out": wall_in + WALL, "wall": WALL, "x_out": x_out,
        "tent_deg": tent, "slope": slope, "z_out": z_out, "z_in": z_in, "floor": FLOOR, "pcb_t": PCB_T,
        "pcb_outline": list(pcb.exterior.coords),
        "pcb_inner_ring": list(pcb.buffer(-0.45, join_style=2).exterior.coords),
        "case_outline": list(case.exterior.coords),
        "cavity_outline": list(cav.exterior.coords),
        "magnets_floor": [list(map(float, p)) for p in floor_spots], "magnet_floor_size": MAG_FLOOR,
        "magnets_side_y": side_spots, "magnet_side_size": MAG_SIDE,
        "battery_size": [BATT_W, BATT_L, BATT_T],
    }
    json.dump(result, open("design.json", "w"), indent=1)

    pb, cb = pcb.bounds, case.bounds
    print(f"PCB  {pb[2]-pb[0]:.1f} x {pb[3]-pb[1]:.1f} mm   case {cb[2]-cb[0]:.1f} x {cb[3]-cb[1]:.1f} mm"
          f"   case area {case.area/100:.1f} cm2")
    print(f"tent {tent:.1f} deg; PCB bottom over floor: outer {z_out:.1f} mm, inner {z_in:.1f} mm")
    print("xiao", [round(v, 1) for v in xiao_c], xiao_ang, "usb", [round(v, 2) for v in usb_dir])
    print("battery", [round(v, 1) for v in batt.bounds], "jst", [round(v, 1) for v in jst.bounds])
    print("holes", holes, "floor magnets", floor_spots, "inner wall y", round(wy0, 1), round(wy1, 1))

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
    for lc in jblocks.values():
        draw(place(box(lc[0] - 1.6, lc[1] - 3.6, lc[0] + 1.6, lc[1] + 3.6), xiao_c, xiao_ang), color="#0a0")
    for h in holes:
        draw(Point(h).buffer(2.6).difference(Point(h).buffer(1.1)), color="#555")
    for p in floor_spots:
        draw(Point(p).buffer(MAG_FLOOR[0] / 2), color="#a3c", alpha=0.8)
    for sy in side_spots:
        draw(box(wall_in, sy - MAG_SIDE[0] / 2, wall_in + WALL, sy + MAG_SIDE[0] / 2), color="#a3c")
    ax.set_aspect("equal"); ax.invert_yaxis(); ax.grid(alpha=0.3)
    ax.set_title(f"Slim Diamond (left, top view)  case {cb[2]-cb[0]:.0f}x{cb[3]-cb[1]:.0f} mm, tent {tent:.1f}°")
    fig.savefig("design.png", dpi=110, bbox_inches="tight")


if __name__ == "__main__":
    main()
