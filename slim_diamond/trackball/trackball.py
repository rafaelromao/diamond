"""Slim Diamond Trackball: a 34 mm ball and two MX or Choc v1 hot-swap keys, on shared boards.

On the shared shell (module_shell.py), 4 mm taller than the halves' top edges (the 250 mAh battery
and the nice!nano stack under the keys), bevelled at 45 degrees from their top edges up. The ball sits at the front in a cup in the shell, on three
3 mm ceramic balls, and lifts out from above. Under it, on the bottom plate, the sensor board: a
PMW3610 looking up through its LM18-LSI lens, and the reset button facing down, pressed with a pin
through the plate. Behind the ball the main board hangs under the top
(MX or Choc plate): two alternative hot-swap sockets per key, the nice!nano wired below the
sockets (USB-C out of the back wall), the power switch (lever out of the back wall), pads for
the battery's leads. The battery lies on the
plate under the nano. Seven wires join the two boards.

Frames: the dock's plan (x right, y away from you), z up from the standing plane, as the shell.
KiCad's frame for the boards: x the same, y = -y.

Writes trackball/design.json (the boards' outlines and parts, for build_pcb.py), case/*.stl and the
fit check.

Unconfirmed, measure before printing: LENS_ABOVE (the lens's reference plane over the sensor
board's top), NANO_ROW1 (the nice!nano's first pin row from its USB end).
"""
import json
import math
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

import numpy as np
from manifold3d import Manifold
from shapely.geometry import Point, Polygon, box
from shapely.ops import unary_union

import case as C
import module_shell as M

H = M.FLUSH + 4.0
TOP_T = 1.5                    # the top: an MX plate (1.5 mm)
MX_CUT = 14.0 + 0.1            # MX plate cutout
MX_PITCH = 19.05
SWITCH_ANGLE = 270             # sockets face the wider side of the rearward key's offset centre
KEYS_REAR_SHIFT = 3.8          # rearward, retaining assembly clearance to the power switch
KEYS_X = -0.45                 # common centres for both socket families and case variants
MX = dict(cap=18.0, below_plate=5.0, socket=1.85, cap_top=8.0 + 7.6)   # cap_top: over the plate (DSA)
CHOC = dict(cap=18.0, below_plate=2.2, socket=1.8, cap_top=7.5)
PLATE_TOP = M.FEET + M.BOTTOM_T
PCB_T = 1.6
PCB_TOP = H - MX["below_plate"]                     # MX: PCB top 5 mm under the plate's top
SOCKET_BOT = PCB_TOP - PCB_T - MX["socket"]
BALL = 34.0
BEARING = 3.0                  # Si3N4 balls in the cup, three of them
BEARING_ANGLE = 40.0           # contact angle below the ball's equator
SENSOR_BELOW = 3.0             # the sensor board's parts face down: room under it
LENS_ABOVE = 2.0               # UNCONFIRMED: lens reference plane over the sensor board's top
WORK = 2.4                     # PMW3610: lens reference plane to the ball (2.2 to 2.6)
SENSOR_BOARD = (28.0, 30.0)    # w, l, centred on the ball's axis: the sensor, its parts, wires, reset
OPT = (2.988, 0.0)             # the optical centre in the PMW3610 footprint (siderakb, CERN-OHL-P),
                               # mirrored on the board's back face: the footprint sits +2.988 off it
# The sensor board's parts, in KiCad's frame (y towards you) from the board's centre (the ball's
# axis), all on its back face (which faces the plate): the PMW3610 (its footprint's origin, which
# sits OPT off its optical centre), the regulator, capacitors, the reset button, two screw holes,
# and seven wire pads to the main board (VCC, GND, SCLK, SDIO, NCS, MOTION, RST).
SENSOR_PARTS = {
    "U1": (OPT[0], 0.0), "U2": (-4.5, 10.0),
    "C6": (11.2, 9.0), "C7": (11.2, 11.6), "C5": (7.6, 9.0), "C4": (4.0, 9.0), "C1": (0.5, 9.0),
    "C2": (0.5, 11.6), "C9": (-9.0, 9.0), "C8": (-9.0, 11.6), "C3": (5.0, -7.9), "R1": (8.6, -7.9),
    "SW1": (8.0, -12.2),
    "J1": [(-11.5, -12.6), (-8.96, -12.6), (-6.42, -12.6), (-3.88, -12.6), (-11.5, -10.06), (-8.96, -10.06),
           (-6.42, -10.06)],
    "H": [(-11.5, 0.0), (0.5, -12.5)],
}
NANO = (18.0, 33.3, 1.0, 3.2)  # w, l, PCB, USB-C receptacle
NANO_ROW1 = 4.0                # UNCONFIRMED: first pin row from the USB end
NANO_GAP = 0.3                 # its back under the sockets
NANO_Y_MAX = -58.4             # keep the controller forward of the rear USB/power access
BAT = (20.0, 25.0, 7.5)        # 752025 lengthwise: w (x), l (y), thickness
CRADLE = (1.2, 3.0, 0.3)
CUP_WALL = 1.6
BALL_CLR = 0.6                 # the cup's inside off the ball
BCZ = PLATE_TOP + SENSOR_BELOW + PCB_T + LENS_ABOVE + WORK + BALL / 2


def place():
    room = M.room()
    top = M.profile(H)
    r_top = math.sqrt((BALL / 2) ** 2 - (BCZ - H) ** 2) + 0.5 if BCZ > H else BALL / 2 + 0.5
    # the ball's bore (ball and clearance) inside the walls, 0.8 mm off them; the cup's sleeve
    # merges into the walls where they meet
    r_bore = BALL / 2 + BALL_CLR + 0.8
    bc = next(y for y in np.arange(top.bounds[1] + r_bore, -30, 0.1)
              if top.buffer(-M.WALL, join_style=2).contains(Point(0, y).buffer(r_bore)))
    k1 = bc + r_top + 0.5 + MX["cap"] / 2 + KEYS_REAR_SHIFT
    keys = [k1, k1 + MX_PITCH]
    # The wired nano rests in printed supports below the board, USB-C end towards the back.
    n_top = M.inner().bounds[3] - 0.3                      # its USB end
    n_y0 = max(y for y in np.arange(-90, n_top - NANO[1] + 0.01, 0.1)
               if y <= NANO_Y_MAX + 1e-6
               and M.inner().buffer(-0.3).contains(box(-NANO[0] / 2, y, NANO[0] / 2, y + NANO[1])))
    # the battery on the plate under the nano, as far forward as the cup lets it
    b_y0 = min(y for y in np.arange(bc, -10, 0.1)
               if room.buffer(-CRADLE[2]).contains(box(-BAT[0] / 2, y, BAT[0] / 2, y + BAT[1]))   # its cradle merges into the walls
               and Point(0, bc).distance(box(-BAT[0] / 2, y, BAT[0] / 2, y + BAT[1])) >= cup_floor_r() + 0.5
               and y >= bc + SENSOR_BOARD[1] / 2 + 1.0 + CRADLE[0] + CRADLE[2])
    return dict(ball=(0.0, bc), keys=[(KEYS_X, y) for y in keys], nano=(0.0, n_y0), battery=(0.0, b_y0),
                back=M.OUTLINE.bounds[3], r_top=r_top)


def cup_floor_r():
    """How far the cup's lowest part reaches out from the ball's axis, near the plate."""
    z = bearing_z() - BEARING
    return math.sqrt(max((BALL / 2 + BALL_CLR + CUP_WALL) ** 2 - (BCZ - z) ** 2, 0)) + 1.0


def bearing_z():
    return BCZ - (BALL / 2 + BEARING / 2) * math.sin(math.radians(BEARING_ANGLE))


def bearings(L):
    """The three bearing balls' centres."""
    bx, by = L["ball"]
    rr = (BALL / 2 + BEARING / 2) * math.cos(math.radians(BEARING_ANGLE))
    return [(bx + rr * math.cos(math.radians(a)), by + rr * math.sin(math.radians(a)), bearing_z())
            for a in (90, 210, 330)]


def box3(x0, y0, z0, x1, y1, z1):
    return Manifold.cube((x1 - x0, y1 - y0, z1 - z0)).translate((x0, y0, z0))


def sensor_board_plan(L):
    """The sensor board's outline (plan), centred on the ball's axis (the sensor's optical centre).
    Its parts are on its back face, which faces the plate; the lens looks up from its front."""
    bx, by = L["ball"]
    w, l = SENSOR_BOARD
    return box(bx - w / 2, by - l / 2, bx + w / 2, by + l / 2)


def main_board_plan(L, posts):
    """The main board: inside the walls (0.5 mm off), behind the ball's cup, round the posts."""
    bx, by = L["ball"]
    outline = M.inner().buffer(-0.5, join_style=2)
    outline = outline.difference(Point(bx, by).buffer(cup_outer_r() + 0.5, 64))
    outline = outline.intersection(box(-99, by, 99, 99))
    for x, y in posts:
        outline = outline.difference(Point(x, y).buffer(M.SCREW["post"] / 2 + 0.5, 32))
    outline = max(getattr(outline, "geoms", [outline]), key=lambda g: g.area)
    return outline.buffer(-0.5).buffer(0.5)       # 0.5 mm round the corners


def board_posts(L):
    """Two posts under the top, holding the main board (M2 screws up through it), clear of the
    keys' sockets and the nano, merging into the walls."""
    keys = unary_union([box(kx - 9.5, ky - 9.5, kx + 9.5, ky + 9.5) for kx, ky in L["keys"]])
    nano = box(-NANO[0] / 2 - 1, L["nano"][1] - 1, NANO[0] / 2 + 1, L["nano"][1] + NANO[1] + 1)
    ok = M.inner().buffer(1.0 - M.SCREW["post"] / 2, join_style=2).difference(keys.union(nano)).difference(
        Point(*L["ball"]).buffer(cup_outer_r() + M.SCREW["post"] / 2))        # merging 1 mm into the walls
    ok = ok.intersection(main_board_plan(L, []).buffer(-1.4))   # the 2.2 mm hole stays inside the board
    x0, y0, x1, y1 = ok.bounds
    pts = [(x, y) for x in np.arange(0, x1 + 0.01, 0.5) for y in np.arange(y0, y1 + 0.01, 0.5)
           if ok.contains(Point(x, y)) and ok.contains(Point(-x, y))]
    y0k, y1k = L["keys"][0][1] - 9.0, L["keys"][1][1] + 9.0
    pts = [q for q in pts if y0k <= q[1] <= y1k]               # beside the keys, under the main board
    q = max(pts, key=lambda q: q[0] - 0.5 * abs(q[1] - (L["keys"][0][1] + L["keys"][1][1]) / 2))
    return [(-q[0], q[1]), q]


def parts(L, main_plan, sensor_plan, switch="mx"):
    spec = MX if switch == "mx" else CHOC
    height = PCB_TOP + spec["below_plate"]
    pcb_top = PCB_TOP
    top_t = TOP_T if switch == "mx" else 1.2
    socket_bot = pcb_top - PCB_T - spec["socket"]
    out = []
    bx, by = L["ball"]
    out.append(("ball", Manifold.sphere(BALL / 2, 96).translate((bx, by, BCZ))))
    for i, (x, y, z) in enumerate(bearings(L)):
        out.append(("bearing %d" % (i + 1), Manifold.sphere(BEARING / 2, 24).translate((x, y, z))))
    for i, (kx, ky) in enumerate(L["keys"]):
        body = box3(kx - 6.95, ky - 6.95, pcb_top, kx + 6.95, ky + 6.95, height - top_t - 0.05)
        housing_h = 6.6 if switch == "mx" else 2.5
        housing_half = 7.8 if switch == "mx" else 7.5
        body += box3(kx - housing_half, ky - housing_half, height,
                     kx + housing_half, ky + housing_half, height + housing_h)
        out.append((switch.upper() + " %d" % (i + 1), body))
        out.append(("keycap %d" % (i + 1), box3(kx - spec["cap"] / 2, ky - spec["cap"] / 2, height + housing_h,
                                                  kx + spec["cap"] / 2, ky + spec["cap"] / 2, height + spec["cap_top"])))
        x0, x1 = (-6.9, -0.9) if switch == "mx" else (1.25, 8.45)
        out.append(("socket %d" % (i + 1), box3(kx + x0, ky - 7.75, socket_bot,
                                                   kx + x1, ky + 7.75, pcb_top - PCB_T)))
    out.append(("main board", M.extrude(main_plan, pcb_top - PCB_T, pcb_top)))
    nx, ny = L["nano"]
    nb = SOCKET_BOT - NANO_GAP                         # its back, under the sockets
    nano = box3(nx - NANO[0] / 2, ny, nb - NANO[2], nx + NANO[0] / 2, ny + NANO[1], nb)
    nano += box3(nx - 4.5, ny + NANO[1] - 7.3, nb - NANO[2] - NANO[3], nx + 4.5, ny + NANO[1] + 0.6, nb - NANO[2])
    out.append(("nice!nano", nano))
    bx_, by_ = L["battery"]
    out.append(("battery", box3(bx_ - BAT[0] / 2, by_, PLATE_TOP, bx_ + BAT[0] / 2, by_ + BAT[1], PLATE_TOP + BAT[2])))
    sz = PLATE_TOP + SENSOR_BELOW
    out.append(("sensor board", M.extrude(sensor_plan, sz, sz + PCB_T)))
    zone = sensor_plan.buffer(-0.5)
    for x, y in sensor_holes(L):
        zone = zone.difference(Point(x, y).buffer(2.6))
    out.append(("sensor's parts", M.extrude(zone, PLATE_TOP + 0.2, sz)))
    out.append(("lens", Manifold.cylinder(LENS_ABOVE, 5.5, circular_segments=48).translate((bx, by, sz + PCB_T))))
    return out


def usb_z(L):
    return SOCKET_BOT - NANO_GAP - NANO[2] - NANO[3] / 2


def cup(L):
    """The ball's cup: a spherical shell round the ball (BALL_CLR off it, CUP_WALL thick) from the
    top down past the bearings, a boss behind each bearing (its pocket is closed at the back), and
    a window under the ball for the sensor. All of it is under the ball's equator (over the
    module's top), so the ball lifts straight out."""
    bx, by = L["ball"]
    z0 = bearing_z() - BEARING
    r_in = BALL / 2 + BALL_CLR
    cupm = Manifold.sphere(r_in + CUP_WALL, 128).translate((bx, by, BCZ))
    for x, y, z in bearings(L):
        cupm += Manifold.sphere(BEARING / 2 + 1.2, 32).translate((x, y, z))
    cupm -= Manifold.sphere(r_in, 128).translate((bx, by, BCZ))
    for x, y, z in bearings(L):
        cupm -= Manifold.sphere(BEARING / 2 + 0.05, 32).translate((x, y, z))
    cupm = cupm.trim_by_plane((0, 0, 1), z0).trim_by_plane((0, 0, -1), -H)
    cupm -= Manifold.cylinder(H, 7.0, circular_segments=48).translate((bx, by, z0 - 1))        # the sensor's window
    return cupm ^ M.extrude(M.inner().buffer(0.01), 0, H)          # merged into the walls where they meet


def cup_outer_r():
    """The cup's widest radius (at the top), the main board keeps clear of."""
    return math.sqrt((BALL / 2 + BALL_CLR + CUP_WALL) ** 2 - max(BCZ - H, 0) ** 2) + 0.4


def shell_and_plate(L, switch="mx"):
    spec = MX if switch == "mx" else CHOC
    height = PCB_TOP + spec["below_plate"]
    pcb_top = PCB_TOP
    top_t = TOP_T if switch == "mx" else 1.2
    bx, by = L["ball"]
    # Reserve the wire rows before placing the bottom-plate posts. A post's board notch is
    # 0.5 mm wider than the post; pad_row also needs 1.6 mm of board around its 0.8 mm envelope.
    # screw_spots adds 0.3 mm itself, leaving 1.6 + 0.5 - 0.3 = 1.8 mm to reserve here.
    pads = board_layout(L, main_board_plan(L, []))
    wire_keep = unary_union([box(x - 0.8, y - 0.8, x + 0.8, y + 0.8)
                             for x, y in pads["wires"] + pads["bat"] + pads["controller"]]).buffer(1.8)
    keep = unary_union([Point(bx, by).buffer(cup_outer_r() + 0.5),
                        sensor_board_plan(L).buffer(0.3),
                        wire_keep,
                        unary_union([Point(x, y).buffer(M.SCREW["post"] / 2 + 0.3)
                                     for x, y in board_posts(L)]),
                        box(-BAT[0] / 2 - 2, L["battery"][1] - 2, BAT[0] / 2 + 2, L["battery"][1] + BAT[1] + 2),
                         box(-NANO[0] / 2 - 0.5, L["nano"][1] - 1, NANO[0] / 2 + 0.5, M.OUTLINE.bounds[3])])
    posts = M.screw_spots(2, keep_out=keep) + [(0.0, -20.5)]
    rear_post_top = 8.7             # below the USB overmold, not through the controller board
    sh = M.shell(height, top_t, posts, post_tops={posts[2]: rear_post_top})
    sh += box3(-M.SCREW["post"] / 2, posts[2][1], rear_post_top - 3,
               M.SCREW["post"] / 2, L["back"], rear_post_top)
    # the bottom plate's posts pass the main board: stop them short of it where they're under it
    sh += cup(L)
    sh -= Manifold.cylinder(top_t + 1, L["r_top"], circular_segments=120).translate((bx, by, height - top_t - 0.5))
    for kx, ky in L["keys"]:
        sh -= Manifold.cube((MX_CUT, MX_CUT, top_t + 1)).translate((kx - MX_CUT / 2, ky - MX_CUT / 2, height - top_t - 0.5))
    bp = board_posts(L)
    for x, y in bp:
        post = Manifold.cylinder(height - top_t - pcb_top + 0.01, M.SCREW["post"] / 2, circular_segments=32)
        sh += post.translate((x, y, pcb_top))
        sh -= Manifold.cylinder(6.0, M.SCREW["pilot"] / 2, circular_segments=20).translate((x, y, pcb_top - 0.01))
    main_plan = main_board_plan(L, posts[:2])  # the short rear post stops well below this board
    sensor_plan = sensor_board_plan(L)
    # the back wall: USB-C opening and the power switch's lever slot
    nb = SOCKET_BOT - NANO_GAP
    uz = nb - NANO[2] - NANO[3] / 2
    back = L["back"]
    sh -= Manifold.cube((12.8, M.WALL + 3, 7.2)).translate((-6.4, back - M.WALL - 1.5, uz - 3.6))
    # Keep the power lever opening local to the rear wall; a long groove across the
    # hood is unnecessary and visually interrupts the continuous rear surface.
    sh -= Manifold.cube((5.0, M.WALL + 3, 2.4)).translate((-2.5, back - M.WALL - 1.5, pcb_top + 0.2))
    sh = M.bevel(sh, height)          # the cup and the posts too
    plate = M.bottom_plate(posts)
    # the battery's cradle, the sensor board's posts
    c = CRADLE[2]
    bx_, by_ = L["battery"]
    outer = box(bx_ - BAT[0] / 2 - c - CRADLE[0], by_ - c - CRADLE[0], bx_ + BAT[0] / 2 + c + CRADLE[0], by_ + BAT[1] + c + CRADLE[0])
    ring = outer.difference(box(bx_ - BAT[0] / 2 - c, by_ - c, bx_ + BAT[0] / 2 + c, by_ + BAT[1] + c))
    plate += M.extrude(ring.intersection(M.room().buffer(-M.PLATE_CLR)), PLATE_TOP - 0.01, PLATE_TOP + CRADLE[1])
    # The wired controller sits on shell-mounted ledges, not on the removable floor.
    # This keeps its wider PCB above the seam-magnet bosses during bottom-plate servicing.
    nano_floor = SOCKET_BOT - NANO_GAP - NANO[2]
    ny = L["nano"][1]
    support_y = max(L["battery"][1] + BAT[1] + 1.5, ny + NANO[1] - 8.0)
    for sx in (-1, 1):
        pad = box(7.2, support_y, M.OUTLINE.bounds[2], support_y + 4.0)
        if sx < 0:
            from shapely import affinity
            pad = affinity.scale(pad, xfact=-1, yfact=1, origin=(0, 0))
        sh += M.extrude(pad.intersection(M.OUTLINE), nano_floor - 1.6, nano_floor)
        lip = box(sx * 9.8 - 0.5, support_y, sx * 9.8 + 0.5, support_y + 4.0)
        sh += M.extrude(lip, nano_floor - 0.01, nano_floor + NANO[2])
    sh = M.bevel(sh, height)
    for x, y in sensor_holes(L):
        plate += Manifold.cylinder(SENSOR_BELOW + 0.01, 2.2, circular_segments=32).translate((x, y, PLATE_TOP - 0.01))
        plate -= Manifold.cylinder(SENSOR_BELOW + 1, M.SCREW["pilot"] / 2, circular_segments=20).translate((x, y, PLATE_TOP))
    # reset: the button faces down from the sensor board; a pin hole through the plate under it
    rx, ry = sensor_reset(L)
    plate -= Manifold.cylinder(M.BOTTOM_T + 2, 1.25, circular_segments=24).translate((rx, ry, M.FEET - 1))
    passage = M.usb_clearance(L["nano"][1] + NANO[1] + 0.6, usb_z(L))
    sh -= passage
    plate -= passage
    plate -= M.extrude(unary_union([Point(x, y).buffer(M.SCREW["post"] / 2 + 0.3) for x, y in posts]),
                       PLATE_TOP, height + 1)
    plate ^= M.extrude(M.service_plan(), M.FEET - 1, height + 1)
    return sh, plate, posts, bp, main_plan, sensor_plan


def sensor_holes(L):
    """The sensor board's two screw holes (dock frame)."""
    bx, by = L["ball"]
    return [(bx + x, by - y) for x, y in SENSOR_PARTS["H"]]


def sensor_reset(L):
    bx, by = L["ball"]
    x, y = SENSOR_PARTS["SW1"]
    return (bx + x, by - y)


def pad_row(main_plan, L, n, side, avoid=(), preferred_y=None):
    """A row of n THT pads (2.54 mm apart, along y) on the main board beside the keys, on `side`
    (-1 left, +1 right): clear of the keys' switch and socket holes and the nano below.
    Prefer `preferred_y` for the row's front when aligning it with the nano's pins."""
    keys = unary_union([box(kx - 8.5, ky - 8.0, kx + 8.5, ky + 8.0) for kx, ky in L["keys"]])   # switch + socket
    nano = box(-NANO[0] / 2 - 0.5, L["nano"][1] - 0.5, NANO[0] / 2 + 0.5, L["nano"][1] + NANO[1] + 0.5)
    ok = main_plan.buffer(-1.6).difference(keys).difference(nano)
    for a in avoid:
        ok = ok.difference(a)
    length = (n - 1) * 2.54
    best = None
    for x in sorted(np.arange(0, 20, 0.25), key=lambda v: v):
        ys = np.arange(-90, -10, 0.25)
        if preferred_y is not None:
            ys = sorted(ys, key=lambda y: abs(y - preferred_y))
        for y in ys:
            row = box(side * x - 0.8, y - 0.8, side * x + 0.8, y + length + 0.8)
            if ok.contains(row):
                best = (side * x, y)
                break
        if best:
            break
    if best is None:
        raise ValueError("no room for %d wire pads on the %s side" % (n, "left" if side < 0 else "right"))
    return [(best[0], best[1] + i * 2.54) for i in range(n)]


def panel(L, main_plan, sensor_plan):
    """One board to order: the main board and the sensor board joined by a breakaway tab at x = 0,
    with mouse bites at both ends of it. Returns the outline and the bite holes."""
    sb = sensor_plan.bounds
    front = min(y for x, y in main_plan.exterior.coords if abs(x) < 3.0)
    tab = box(-2.8, sb[3] - 0.5, 2.8, front + 0.5)
    outline = unary_union([main_plan, tab, sensor_plan]).buffer(0)
    bites = [(x, y) for y in (sb[3] + 0.35, front - 0.35) for x in (-2.0, -1.0, 0.0, 1.0, 2.0)]   # 0.5 mm webs
    return outline, bites


def board_layout(L, main_plan):
    """The main board's own pads: the sensor board's seven wires (four right of the keys, three
    left) and the battery's two (left, in front of them), each level with its nano pin."""
    avoid = [Point(x, y).buffer(2.6) for x, y in board_posts(L)]
    left = pad_row(main_plan, L, 5, -1, avoid=avoid,
                   preferred_y=L["keys"][0][1] - 6.0)  # battery -, +, GND, VCC, RST
    # Keep the sensor wire pads near their corresponding controller pins for short wiring.
    sclk_y = L["nano"][1] + NANO[1] - NANO_ROW1 - 9 * 2.54
    right = pad_row(main_plan, L, 4, +1, avoid=avoid, preferred_y=sclk_y - 1.3)
    wires = right[:4] + [left[4], left[3], left[2]]
    mid_y = sum(y for _, y in L["keys"]) / 2
    return dict(wires=wires, bat=[left[1], left[0]], controller=[(-3.0, mid_y - 1.7), (0.0, mid_y), (3.0, mid_y)])


def main():
    L = place()
    sh, plate, posts, bp, main_plan, sensor_plan = shell_and_plate(L)
    ps = parts(L, main_plan, sensor_plan)
    M.check_common("Slim Diamond Trackball", sh, plate, ps)
    M.check_dock_and_desk(sh, plate, H, ps)
    nb = SOCKET_BOT - NANO_GAP
    print("  ball centre %.1f over the standing plane, top %.1f (%.1f over the module's top); keys at y %s"
          % (BCZ, BCZ + BALL / 2, BCZ + BALL / 2 - H, ["%.1f" % k[1] for k in L["keys"]]))
    print("  nano %.1f..%.1f, battery %.1f..%.1f (%.1f mm apart)" % (nb - NANO[2] - NANO[3], nb, PLATE_TOP,
          PLATE_TOP + BAT[2], nb - NANO[2] - NANO[3] - PLATE_TOP - BAT[2]))
    print("  USB-C end %.1f mm in from the back wall's outside" % (L["back"] - (L["nano"][1] + NANO[1])))
    print("  shell %.1f cm3, plate %.1f cm3, genus %d / %d; height %.2f" % (sh.volume() / 1000, plate.volume() / 1000,
          sh.genus(), plate.genus(), H))
    os.makedirs(os.path.join(HERE, "case"), exist_ok=True)
    C.stl(sh.mirror((0, 0, 1)).translate((0, 0, H)), os.path.join(HERE, "case", "shell.stl"))
    C.stl(plate.translate((0, 0, -M.FEET)), os.path.join(HERE, "case", "bottom_plate.stl"))
    os.makedirs(os.path.join(HERE, "..", C.STLS), exist_ok=True)
    for name in ("shell", "bottom_plate"):          # and the repo's STL folder
        shutil.copyfile(os.path.join(HERE, "case", name + ".stl"),
                         os.path.join(HERE, "..", C.STLS, "trackball_" + name + ".stl"))
    choc_sh, choc_plate, choc_posts, choc_bp, choc_main, choc_sensor = shell_and_plate(L, "choc")
    choc_parts = parts(L, choc_main, choc_sensor, "choc")
    M.check_common("Slim Diamond Trackball / Choc v1", choc_sh, choc_plate, choc_parts)
    choc_height = PCB_TOP + CHOC["below_plate"]
    M.check_dock_and_desk(choc_sh, choc_plate, choc_height, choc_parts)
    assert posts == choc_posts and bp == choc_bp
    assert main_plan.equals(choc_main) and sensor_plan.equals(choc_sensor)
    assert abs((plate - choc_plate).volume()) < 1e-3 and abs((choc_plate - plate).volume()) < 1e-3
    C.stl(choc_sh.mirror((0, 0, 1)).translate((0, 0, choc_height)), os.path.join(HERE, "case", "shell_choc.stl"))
    shutil.copyfile(os.path.join(HERE, "case", "shell_choc.stl"),
                    os.path.join(HERE, "..", C.STLS, "trackball_shell_choc.stl"))
    kicad = lambda pts: [(round(float(x), 4), round(float(-y), 4)) for x, y in pts]
    bl = board_layout(L, main_plan)
    wires, bat = bl["wires"], bl["bat"]
    outline, bites = panel(L, main_plan, sensor_plan)
    json.dump(dict(
        panel=kicad(outline.exterior.coords), panel_inner=kicad(outline.buffer(-0.35, join_style=2).exterior.coords),
        bites=kicad(bites), wire_pads=kicad(wires), battery_pads=kicad(bat),
        controller_pads=kicad(bl["controller"]),
        height=H, ball=L["ball"], keys=L["keys"], switch_angle=SWITCH_ANGLE, nano=L["nano"], battery=L["battery"],
        main_board=kicad(main_plan.exterior.coords), sensor_board=kicad(sensor_plan.exterior.coords),
        main_holes=kicad(bp), sensor_holes=kicad(sensor_holes(L)), sensor_parts=SENSOR_PARTS,
        nano_row1=NANO_ROW1, opt=OPT, pcb_top=PCB_TOP, back=L["back"]),
        open(os.path.join(HERE, "design.json"), "w"), indent=1, default=lambda o: [float(v) for v in o])
    return L, sh, plate, ps


if __name__ == "__main__":
    main()
