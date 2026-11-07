"""Slim Diamond Trackball: a 34 mm ball and two MX or Choc v1 hot-swap keys, on shared boards.

On the shared tray (module_shell.py), with a lid that carries the keys' plate and the ball's cup.
The ball sits at the front in that cup on three 3 mm ceramic balls, and lifts out from above. Under
it, on the tray's floor, the sensor board: a PMW3610 looking up through its LM18-LSI lens, and the
reset button facing down, pressed with a pin through the floor. Behind the ball the main board rests
on the tray's posts: two alternative hot-swap sockets per key, the power switch (lever out of the back
wall), pads for the wires and the battery's leads. The controller stands under it on its own small
board, USB-C out of the back wall; the battery lies on the floor ahead of that. Eight stacking pins join
those two boards, and seven wires the sensor board.

This file owns the tray's insides, because the trackpad (trackpad/trackpad.py) uses the same tray,
main board and battery, and a sensor board for its reset button.

Frames: the dock's plan (x right, y away from you), z up from the standing plane, as the tray.
KiCad's frame for the boards: x the same, y = -y.

Writes trackball/design.json (the boards' outlines and parts, for build_pcb.py), case/*.stl and the
fit check.

The sensor posts print SENSOR_SHIM low: a card shim under the board sets the lens height exactly.
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
sys.path.append(os.path.dirname(os.path.abspath(__file__)))     # last: this file is itself "trackball"
from controller_pinout import HEADER, LINKS, ROWS
from controllers import XIAO_LENGTH, XIAO_SETBACK, XIAO_USB_OVERHANG

H = M.FLUSH + 4.0
TOP_T = 1.5                    # the top: an MX plate (1.5 mm)
MX_CUT = 14.0 + 0.2            # plate cutout: printed holes come out small
MX_PITCH = 19.05
SWITCH_ANGLE = 270             # sockets face the wider side of the rearward key's offset centre
KEYS_REAR_SHIFT = 4.2          # clears the trackpad front facet without crowding the power-switch pads
KEYS_X = -0.45                 # common centres for both socket families and case variants
MX = dict(cap=18.0, below_plate=5.0, socket=1.85, cap_top=8.0 + 7.6)   # cap_top: over the plate (DSA)
CHOC = dict(cap=18.0, below_plate=2.2, socket=1.8, cap_top=7.5)
PLATE_TOP = M.FEET + M.BOTTOM_T
BAT_Z = PLATE_TOP + .4          # insulating seat above reinforced floor roofs
PCB_T = M.PCB_T
PCB_TOP = M.PCB_TOP                                 # MX: 5 mm under the top; Choc: 2.2 mm
SOCKET_BOT = PCB_TOP - PCB_T - MX["socket"]
BALL = 34.0
BEARING = 3.0                  # Si3N4 balls in the cup, three of them
BEARING_ANGLE = 40.0           # contact angle below the ball's equator
SENSOR_BELOW = 3.4             # room under it, over the reinforced foot roofs
LENS_ABOVE = 2.0               # nominal lens reference plane over the sensor board's top
SENSOR_SHIM = 0.4              # the posts' top under the nominal board: shimmed at assembly
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
NANO_ROW1 = 4.0                # first pin row from the USB end
NANO_GAP = 1.6                 # room for wires soldered to a XIAO's back pads (its PCB is 1.25 thick)
HEADER_T = 2.54                # a standard pin header's plastic, between controller and its board
CB_T = 1.6                     # the controller board: on the same panel, so as thick as the others
CB_REAR, CB_FRONT = -20.1, -35.35     # its edges; the front stops short of the battery's end
CB_NOTCH = (5.0, -22.8)        # half-width, front edge: the notch round the USB receptacle
CB_EAR = (12.6, -35.4, -27.9)  # half-width, front, rear: the ears beside the controller
CB_ARM = (10.25, -38.2)        # the arms on past the battery's end: inner edge, front
CB_RIB = (-39.7, -38.45)       # the ribs ahead of the arms: y span
CB_COLUMN = 7.62               # the header's columns
LINK_X = {5: 10.05, 6: 10.05, 7: 10.05, 8: 11.4}   # the stacking pins, by row: past the battery they step out
LINK_Y8 = .3                   # row 8's pin, further along than the rows: its plastic clears the strip's end
LINK_GAP = .24                 # the plastic's gap under the main board, set by the 6.75 mm jig
LINK_PAD = 9.2                 # 3V's wire pad, beside row 8's pin and clear of its plastic
LINK_PIN = 15.0                # an extra-long header's length, plastic against the main board
BAT = (20.0, 25.0, 7.5)        # 752025 lengthwise: w (x), l (y), thickness
CRADLE = (1.2, 3.0, 0.3)
CUP_WALL = 1.6
PAD_TEXT = dict(SCLK="CK", SDIO="IO", NCS="CS", MOTION="MO", RST="RST", VCC="3V", GND="G", VBAT="VBAT", XR="R2")
PAD_X = 8.2                    # the wire pads' columns, from the centreline
PAD_EDGE = 1.5                 # wire pad centre to the board edge: its joint clears the lid's lip
POST_PIN = 2.2                 # the side posts' pin, up through the main board
PAD_KEEP = (-77.1, 18.9)       # the trackpad's back parts: centre y, radius
PANEL_LENGTH = 99.5            # the ordered panel's longest side, within the 100 mm tier
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
    # The nano stands on its board, its USB-C flush with the back wall.
    n_y0 = M.OUTLINE.bounds[3] - 0.6 - NANO[1]
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


def main_board_plan(L):
    """The main board: inside the walls (0.5 mm off), behind the ball's cup and the trackpad's back
    parts. It drops into the tray from above, so nothing lower constrains it."""
    bx, by = L["ball"]
    outline = M.inner().buffer(-0.5, join_style=2)
    outline = outline.difference(Point(bx, by).buffer(cup_outer_r() + 0.5, 64))
    outline = outline.difference(Point(0, PAD_KEEP[0]).buffer(PAD_KEEP[1], 64))
    outline = outline.intersection(box(-99, -68, 99, 99))
    outline = max(getattr(outline, "geoms", [outline]), key=lambda g: g.area)
    return outline.buffer(-0.5).buffer(0.5).simplify(.005, preserve_topology=True)  # round corners; no sub-micron routed edges


def board_holes():
    """The main board's two screw holes: the lid's rear pair."""
    return M.lid_screws()[2:]


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
    holes = unary_union([Point(x, y).buffer(POST_PIN + .2, 32) for x, y in board_holes()])
    out.append(("main board", M.extrude(main_plan.difference(holes), pcb_top - PCB_T, pcb_top)))
    out.append(("power switch", power_switch(main_plan)))
    nx, ny = L["nano"]
    nb = SOCKET_BOT - NANO_GAP                         # its back, under the sockets
    nano = box3(nx - NANO[0] / 2, ny, nb - NANO[2], nx + NANO[0] / 2, ny + NANO[1], nb)
    nano += box3(nx - 4.5, ny + NANO[1] - 7.3, nb - NANO[2] - NANO[3], nx + 4.5, ny + NANO[1] + 0.6, nb - NANO[2])
    out.append(("nice!nano", nano))
    top = controller_top()
    out.append(("controller board", M.extrude(controller_board_plan(), top - CB_T, top)))
    header = [box(s * CB_COLUMN - 1.27, pin_y(L, 7) - 1.27, s * CB_COLUMN + 1.27, pin_y(L, 3) + 1.27) for s in (-1, 1)]
    out.append(("controller header", M.extrude(unary_union(header), top, top + HEADER_T)))
    under = PCB_TOP - PCB_T
    links = [box(s * x - 1.27, link_y(L, b) - 1.27, s * x + 1.27, link_y(L, a) + 1.27)
             for s in (-1, 1) for x, a, b in ((LINK_X[5], 5, 7), (LINK_X[8], 8, 8))]
    out.append(("stacking pins' plastic", M.extrude(unary_union(links), under - LINK_GAP - HEADER_T, under - LINK_GAP)))
    bx_, by_ = L["battery"]
    out.append(("battery", box3(bx_ - BAT[0] / 2, by_, BAT_Z, bx_ + BAT[0] / 2, by_ + BAT[1], BAT_Z + BAT[2])))
    sz = PLATE_TOP + SENSOR_BELOW
    out.append(("sensor board", M.extrude(sensor_plan, sz, sz + PCB_T)))
    zone = sensor_plan.buffer(-0.5)
    for x, y in sensor_holes(L):
        zone = zone.difference(Point(x, y).buffer(3.0))
    rx, ry = sensor_reset(L)
    zone = zone.difference(box(rx - 2.8, ry - 2.8, rx + 2.8, ry + 2.8))
    out.append(("sensor's parts", M.extrude(zone, PLATE_TOP + 0.6, sz)))
    # TS-1187A, on B.Cu: the plunger points down towards the floor's pin hole.
    reset = box3(rx - 2.55, ry - 2.55, sz - 1.1, rx + 2.55, ry + 2.55, sz)
    reset += Manifold.cylinder(.9, 1, circular_segments=32).translate((rx, ry, sz - 2))
    out.append(("reset", reset))
    out.append(("lens", Manifold.cylinder(LENS_ABOVE, 5.5, circular_segments=48).translate((bx, by, sz + PCB_T))))
    return out


def power_switch(main_plan, full_travel=True):
    """MSK-12C02 body and full lever-travel envelope on the main PCB's front face."""
    sy = main_plan.bounds[3] - 1.8
    body = box3(-3.35, sy - 1.35, PCB_TOP, 3.35, sy + 1.35, PCB_TOP + 1.4)
    half = 2.25 if full_travel else .75
    lever = box3(-half, sy + 1.35, PCB_TOP + .4, half, sy + 3.4, PCB_TOP + 1.0)
    return body + lever


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
        cupm -= Manifold.sphere(BEARING / 2 + 0.15, 32).translate((x, y, z))
    cupm = cupm.trim_by_plane((0, 0, 1), z0).trim_by_plane((0, 0, -1), -H)
    cupm -= Manifold.cylinder(H, 7.0, circular_segments=48).translate((bx, by, z0 - 1))        # the sensor's window
    inside = M.K.module_front(M.extrude(M.inner().buffer(-M.LID_CLR, join_style=2), 0, H), M.P, M.WALL + M.LID_CLR)
    return cupm ^ inside                                           # it drops into the tray with the lid


def cup_outer_r():
    """The cup's widest radius (at the top), the main board keeps clear of."""
    return math.sqrt((BALL / 2 + BALL_CLR + CUP_WALL) ** 2 - max(BCZ - H, 0) ** 2) + 0.4


def tray(L):
    """The tray every module shares: M.tray() with the electronics' seats and the screw posts."""
    sh = M.tray()
    # the battery's cradle
    c = CRADLE[2]
    bx_, by_ = L["battery"]
    outer = box(bx_ - BAT[0] / 2 - c - CRADLE[0], by_ - c - CRADLE[0], bx_ + BAT[0] / 2 + c + CRADLE[0], by_ + BAT[1] + c + CRADLE[0])
    ring = outer.difference(box(bx_ - BAT[0] / 2 - c, by_ - c, bx_ + BAT[0] / 2 + c, by_ + BAT[1] + c))
    sh += M.extrude(ring.intersection(M.room()), PLATE_TOP - 0.01, PLATE_TOP + CRADLE[1])
    sh += M.extrude(box(bx_ - BAT[0] / 2, by_, bx_ + BAT[0] / 2, by_ + BAT[1]), PLATE_TOP - .01, BAT_Z)
    # The controller board drops between printed stops, which hold it until the main board is soldered on.
    nano_floor = SOCKET_BOT - NANO_GAP - NANO[2]
    top = controller_top()
    seat = top - CB_T
    for sx in (-1, 1):
        span = lambda x0, x1, y0, y1: box(min(sx * x0, sx * x1), y0, max(sx * x0, sx * x1), y1).intersection(M.inner().buffer(.05))
        sh += M.extrude(span(5.1, 6.5, CB_NOTCH[1] + .2, CB_REAR + .25), PLATE_TOP - .01, seat)       # under the arms at the rear
        sh += M.extrude(span(5.1, 8.4, CB_REAR + .4, -17.5), PLATE_TOP - .01, seat + 1.3)            # behind them
        sh += M.extrude(span(11.05, 20, CB_EAR[1], CB_EAR[2] - .3), PLATE_TOP - .01, seat)           # under the ears
        sh += M.extrude(span(CB_ARM[0] + .05, 20, CB_RIB[0], CB_RIB[1]), PLATE_TOP - .01, top)        # ahead of the arms
    # the sensor board's posts: M3 x 8 down through the board
    for x, y in sensor_holes(L):
        sh += Manifold.cylinder(SENSOR_BELOW - SENSOR_SHIM + 0.01, 2.8, circular_segments=32).translate((x, y, PLATE_TOP - 0.01))
    # the main board: two posts beside the battery, each widening over it, and a ledge at the back
    pcb_under = PCB_TOP - PCB_T
    for sx in (-1, 1):
        x, y = sx * M.PCB_SCREW[0], M.PCB_SCREW[1]
        r = M.SCREW["post"] / 2
        foot = box(min(sx * 11.8, sx * 17), y - r, max(sx * 11.8, sx * 17), y + r).intersection(M.inner().buffer(.05))
        sh += M.extrude(foot, PLATE_TOP - .01, 10.8)
        neck = (M.extrude(foot, 10.79, 10.8) + Manifold.cylinder(.01, r, circular_segments=48).translate((x, y, 13.2))).hull()
        # A wide shoulder under the board, and a pin up through it to the same height as the front
        # posts. Flat on the battery's side: the cell lowers straight in past both posts.
        post = Manifold.cylinder(pcb_under - 13.19, 3.7, circular_segments=48).translate((x, y, 13.19)) + neck
        post += Manifold.cylinder(PCB_TOP - pcb_under + .01, POST_PIN, circular_segments=48).translate((x, y, pcb_under - .01))
        side = box(min(sx * (BAT[0] / 2 + .2), sx * 20), y - 9, max(sx * (BAT[0] / 2 + .2), sx * 20), y + 9)
        sh += post ^ M.extrude(side.intersection(M.inner().buffer(.05)), 0, 30)
    # the rear of the board rests on a ledge across the back wall, a wedge for printing
    w = M.inner().bounds[3]
    wedge = Manifold.hull_points([(sx * 7.0, y, z) for sx in (-1, 1)
                                  for y, z in ((w + .05, pcb_under - 1.15), (w + .05, pcb_under), (w - 1.5, pcb_under))])
    sh += wedge ^ M.extrude(M.inner().buffer(.05), 0, 30)
    # the front posts, up to the main board's top, under the lid's bosses
    for sx in (-1, 1):
        x, y = sx * M.FRONT_SCREW[0], M.FRONT_SCREW[1]
        sh += Manifold.cylinder(PCB_TOP - PLATE_TOP + .01, M.SCREW["post"] / 2, circular_segments=48).translate(
            (x, y, PLATE_TOP - .01))
    # pilots: deep enough for the Choc lid's reach; the sensor's reach into the floor
    for x, y in M.lid_screws():
        sh -= Manifold.cylinder(PCB_TOP - 13.9 + 1, M.SCREW["pilot"] / 2, circular_segments=24).translate((x, y, 13.9))
    for x, y in sensor_holes(L):
        sh -= Manifold.cylinder(PLATE_TOP + SENSOR_BELOW, M.SCREW["pilot"] / 2, circular_segments=24).translate((x, y, .95))
    # reset: the button faces down from the sensor board; a pin hole through the floor under it
    rx, ry = sensor_reset(L)
    sh -= Manifold.cylinder(M.BOTTOM_T + 2, 1.25, circular_segments=24).translate((rx, ry, M.FEET - 1))
    # the back wall: USB-C opening, and a slot open to the top for the power lever
    back = L["back"]
    uz = usb_z(L)
    # The USB-C opening has no bottom: wall and hood are gone under the plug.
    sh -= box3(-6.4, back - M.WALL - .1, -1, 6.4, back + 30, uz + 3.6)
    # the nano's board slides back into two blind pockets in the back wall, either side of the port
    for sx in (-1, 1):
        pocket = box(min(sx * 6.3, sx * 9.25), back - M.WALL - .1, max(sx * 6.3, sx * 9.25), back - .45)
        sh -= M.extrude(pocket, nano_floor - .3, nano_floor + 1.25 + .3)
    sh -= box3(-2.5, back - M.WALL - 1.5, PCB_TOP - .3, 2.5, back + 1.5, M.FLUSH + 1)
    return sh


def lid(L, switch="mx", ball=True):
    """The top: the key cutouts, the power switch's pocket and notch; the ball's cup and bore."""
    spec = MX if switch == "mx" else CHOC
    height = PCB_TOP + spec["below_plate"]
    top_t = TOP_T if switch == "mx" else 1.2
    sh = M.lid_blank(height, top_t)
    if ball:
        bx, by = L["ball"]
        sh += cup(L)
        sh -= Manifold.cylinder(top_t + 1, L["r_top"], circular_segments=120).translate((bx, by, height - top_t - 0.5))
    for kx, ky in L["keys"]:
        sh -= Manifold.cube((MX_CUT, MX_CUT, top_t + 1)).translate((kx - MX_CUT / 2, ky - MX_CUT / 2, height - top_t - 0.5))
    main_plan = main_board_plan(L)
    back = L["back"]
    sh -= box3(-2.5, back - M.WALL - 1.5, PCB_TOP, 2.5, back + 1.5, PCB_TOP + 2.6)
    sh -= box3(-3.55, main_plan.bounds[3] - 3.35, PCB_TOP - .01, 3.55, main_plan.bounds[3] - .25, PCB_TOP + 1.55)
    return M.lid_holes(M.bevel(sh, height), height) if ball else sh


def build(L, switch="mx"):
    """lid, tray, the main board's plan, the sensor board's plan."""
    return lid(L, switch), tray(L), main_board_plan(L), sensor_board_plan(L)


def sensor_holes(L):
    """The sensor board's two screw holes (dock frame)."""
    bx, by = L["ball"]
    return [(bx + x, by - y) for x, y in SENSOR_PARTS["H"]]


def sensor_reset(L):
    bx, by = L["ball"]
    x, y = SENSOR_PARTS["SW1"]
    return (bx + x, by - y)


def stacking_pins(L):
    """The eight stacking pins, standing on the controller board, for the assembly's pictures and sweeps."""
    return M.extrude(unary_union([box(x - .32, y - .32, x + .32, y + .32) for link in controller_points(L)["links"].values()
                                  for x, y in [link["xy"]]]), controller_top() - CB_T - 1.0, PCB_TOP + .6)


def pin_y(L, row):
    """Plan y of a header row: the nice!nano's rows, with row 1 its first after the extra USB-end pair."""
    return L["nano"][1] + NANO[1] - NANO_ROW1 - (row - 1) * 2.54


def link_y(L, row):
    """Plan y of a stacking pin."""
    return pin_y(L, row) - (LINK_Y8 if row == 8 else 0)


def xiao_back(L):
    """Where a XIAO's USB-C mouth lies: its pin rows on the same header, a little inside the rear plane."""
    return L["back"] - XIAO_SETBACK


def controller_top():
    """The controller board's top: a header's plastic below the controller's component face."""
    return SOCKET_BOT - NANO_GAP - NANO[2] - HEADER_T


def controller_board_plan():
    """The board under the controller: a notch for the USB receptacle, ears beside the controller and
    arms on past the battery's end for the stacking pins, clear of the walls and the magnet bosses."""
    core = box(-8.95, CB_FRONT, 8.95, CB_REAR).difference(box(-CB_NOTCH[0], CB_NOTCH[1], CB_NOTCH[0], 0))
    ears = box(-CB_EAR[0], CB_EAR[1], CB_EAR[0], CB_EAR[2])
    arms = [box(min(s * CB_ARM[0], s * 12.6), CB_ARM[1], max(s * CB_ARM[0], s * 12.6), CB_EAR[1] + .1) for s in (-1, 1)]
    # The rear keeps to room()'s 0.3 mm round the bosses: row 2's pad needs all of it.
    fit = unary_union([M.room().buffer(-.25), M.room().intersection(box(-99, -27.3, 99, 0))])
    return unary_union([core, ears] + arms).intersection(fit).buffer(-.3).buffer(.3).simplify(.005)


def controller_points(L):
    """Plan positions on the controller board: header pins, stacking pins and jumpers."""
    pins = {}
    for column, rows in HEADER.items():
        sign = -1 if column == "left" else 1
        for row, name in rows.items():
            pins[f"{column[0].upper()}{row}"] = dict(xy=(sign * CB_COLUMN, pin_y(L, row)), net=name)
    links = {f"{column[0].upper()}{row}": dict(xy=((-1 if column == "left" else 1) * LINK_X[row], link_y(L, row)), net=net)
             for column, rows in LINKS.items() for row, net in rows.items()}
    return dict(pins=pins, links=links, jumpers=dict(JP1=(0.0, pin_y(L, 4))))


def column_pad(L, main_plan, side, row):
    """A wire pad level with a header row, in a straight column: the same x for every row."""
    y = link_y(L, row)
    x = LINK_PAD if row > 7 else PAD_X               # beside the stacking pins' step out
    assert main_plan.buffer(-PAD_EDGE).contains(Point(side * x, y)), (side, row)
    return (side * x, float(y))


def label_spot(main_plan, x, y, text):
    """Centre for a pad's 0.8 mm label: outboard of it when the board has the room, else just
    inboard of it and half a row along, clear of the sockets' pads."""
    width = 0.75 * len(text)
    cx = x + (1 if x > 0 else -1) * (1.05 + width / 2)
    if main_plan.buffer(-.2).contains(box(cx - width / 2, y - .45, cx + width / 2, y + .45)):
        return (round(cx, 3), float(y))
    # Over the pad's column if it fits, but no further out than the board's edge allows.
    across = main_plan.intersection(box(-99, y + .8, 99, y + 1.7))
    half = max(abs(across.bounds[0]), abs(across.bounds[2])) - .35
    return ((1 if x > 0 else -1) * min(abs(x), half - width / 2), y + 1.27)


def sensor_shift(main_plan, sensor_plan):
    return PANEL_LENGTH - (main_plan.bounds[3] - sensor_plan.bounds[1])


def controller_offset(main_plan, sensor_plan):
    """Where the controller board sits on the panel: beside the sensor board, a quarter turn round
    so that the tab from the sensor board's side meets it in its USB notch."""
    shift = sensor_shift(main_plan, sensor_plan)
    return (sensor_plan.bounds[2] + 2.0 + CB_REAR, (sensor_plan.bounds[1] + sensor_plan.bounds[3]) / 2 - shift)


def panel(L, main_plan, sensor_plan):
    """One board to order: the main board and the sensor board, as far apart as the 100 mm tier
    allows, on one long bridge with mouse bites at both ends: hold both boards and snap each end. The
    controller board hangs off the sensor board's side on a short tab with bites of its own.
    Returns the outline, the bridge's bites and how far the sensor board moved (plan y)."""
    shift = sensor_shift(main_plan, sensor_plan)
    sb = (sensor_plan.bounds[0], sensor_plan.bounds[1] - shift, sensor_plan.bounds[2], sensor_plan.bounds[3] - shift)
    moved = box(*sb)
    front = min(y for x, y in main_plan.exterior.coords if abs(x) < 3.0)
    tab = box(-2.8, sb[3] - 0.5, 2.8, front + 0.5)
    ox, oy = controller_offset(main_plan, sensor_plan)
    piece, side_tab, _ = controller_panel_piece(ox, oy, sensor_plan.bounds[2])
    outline = unary_union([main_plan, tab, moved, piece, side_tab]).buffer(0)
    bites = [(x, y) for y in (sb[3] + 0.35, front - 0.35) for x in (-2.0, -1.0, 0.0, 1.0, 2.0)]   # 0.5 mm webs
    return outline, bites, shift


def controller_panel_piece(ox, oy, sensor_edge):
    """The controller board on the panel, its tab and the tab's bites. The tab meets it in the USB
    notch: what is left there after snapping has only the receptacle's gap to clear, not the tray."""
    from shapely import affinity
    notch = -CB_NOTCH[1] + ox
    side_tab = box(sensor_edge - .5, oy - 2.8, notch + .5, oy + 2.8)
    bites = [(x, oy + d) for x in (sensor_edge + .35, notch - .35) for d in (-2.0, -1.0, 0.0, 1.0, 2.0)]
    return affinity.translate(affinity.rotate(controller_board_plan(), 90, origin=(0, 0)), ox, oy), side_tab, bites


def board_layout(L, main_plan):
    """The main board's wire pads: two straight columns level with the header rows. The battery's
    stay by the battery."""
    pad = {name: column_pad(L, main_plan, -1 if column == "left" else 1, row)
           for column, rows in ROWS.items() for name, row in rows.items()}
    wires = [pad[n] for n in ("SCLK", "SDIO", "NCS", "MOTION", "RST", "VCC", "GND")]
    bat = [(-10.0, -46.71), (-10.0, -49.25)]
    labels = {n: label_spot(main_plan, x, y, PAD_TEXT[n]) for n, (x, y) in pad.items()}
    # A stacking pin stands beside these: their labels go between the rows, over the pair.
    for n in ("SCLK", "SDIO", "MOTION", "NCS", "VCC"):
        x, y = pad[n]
        sign = 1 if x > 0 else -1
        labels[n] = (sign * (abs(x) + (LINK_X[8] if n == "VCC" else LINK_X[5])) / 2, y + (1.57 if n == "VCC" else 1.27))
    return dict(wires=wires, bat=bat, controller=[pad["VBAT"], pad["XR"]], labels=labels)


def controller_design(L, main_plan, sensor_plan):
    """The controller board in KiCad's frame, at its place on the panel."""
    ox, oy = controller_offset(main_plan, sensor_plan)
    at = lambda p: [round(float(-p[1] + ox), 4), round(float(-(p[0] + oy)), 4)]     # the quarter turn
    points = controller_points(L)
    piece, side_tab, bites = controller_panel_piece(ox, oy, sensor_plan.bounds[2])
    return dict(
        controller_plan=dict(outline=[[round(float(x), 4), round(float(y), 4)] for x, y in controller_board_plan().exterior.coords],
                             pins={k: [round(float(c), 4) for c in v["xy"]] for k, v in points["pins"].items()},
                             links={k: dict(xy=[round(float(c), 4) for c in v["xy"]], net=v["net"]) for k, v in points["links"].items()},
                             jumper=[round(float(c), 4) for c in points["jumpers"]["JP1"]]),
        main_links={k: dict(xy=[round(float(v["xy"][0]), 4), round(float(-v["xy"][1]), 4)], net=v["net"])
                    for k, v in points["links"].items()},
        controller_board=[[round(float(x), 4), round(float(-y), 4)] for x, y in piece.exterior.coords],
        controller_tab=[[round(float(x), 4), round(float(-y), 4)] for x, y in side_tab.exterior.coords],
        controller_bites=[[round(float(x), 4), round(float(-y), 4)] for x, y in bites],
        controller_pins={k: dict(xy=at(v["xy"]), net=v["net"]) for k, v in points["pins"].items()},
        controller_links={k: dict(xy=at(v["xy"]), net=v["net"]) for k, v in points["links"].items()},
        controller_jumpers={k: at(v) for k, v in points["jumpers"].items()})


def stl_lid(m, height, path):
    C.stl(m.mirror((0, 0, 1)).translate((0, 0, height)), path)           # top down, for printing


def main():
    L = place()
    lid_m, tray_m, main_plan, sensor_plan = build(L)
    ps = parts(L, main_plan, sensor_plan)
    M.check_common("Slim Diamond Trackball", lid_m, tray_m, ps)
    M.check_dock_and_desk(lid_m, tray_m, H, ps)
    nb = SOCKET_BOT - NANO_GAP
    print("  ball centre %.1f over the standing plane, top %.1f (%.1f over the module's top); keys at y %s"
          % (BCZ, BCZ + BALL / 2, BCZ + BALL / 2 - H, ["%.1f" % k[1] for k in L["keys"]]))
    print("  controller board %.2f..%.2f" % (controller_top() - CB_T, controller_top()))
    print("  nano %.1f..%.1f, battery %.1f..%.1f (%.1f mm apart)" % (nb - NANO[2] - NANO[3], nb, BAT_Z,
          BAT_Z + BAT[2], nb - NANO[2] - NANO[3] - BAT_Z - BAT[2]))
    print("  USB-C end %.1f mm in from the back wall's outside" % (L["back"] - (L["nano"][1] + NANO[1])))
    print("  lid %.1f cm3, tray %.1f cm3, genus %d / %d; height %.2f" % (lid_m.volume() / 1000, tray_m.volume() / 1000,
          lid_m.genus(), tray_m.genus(), H))
    os.makedirs(os.path.join(HERE, "case"), exist_ok=True)
    stl_lid(lid_m, H, os.path.join(HERE, "case", "lid.stl"))
    choc_height = PCB_TOP + CHOC["below_plate"]
    choc_lid, choc_tray, choc_main, choc_sensor = build(L, "choc")
    choc_parts = parts(L, choc_main, choc_sensor, "choc")
    M.check_common("Slim Diamond Trackball / Choc v1", choc_lid, choc_tray, choc_parts)
    M.check_dock_and_desk(choc_lid, choc_tray, choc_height, choc_parts)
    assert main_plan.equals(choc_main) and sensor_plan.equals(choc_sensor)
    stl_lid(choc_lid, choc_height, os.path.join(HERE, "case", "lid_choc.stl"))
    os.makedirs(os.path.join(HERE, "..", C.STLS), exist_ok=True)
    for name in ("lid", "lid_choc"):
        shutil.copyfile(os.path.join(HERE, "case", name + ".stl"),
                        os.path.join(HERE, "..", C.STLS, "trackball_" + name + ".stl"))
    C.stl(tray_m.translate((0, 0, -M.FEET)), os.path.join(HERE, "..", "case", "module_tray.stl"))
    shutil.copyfile(os.path.join(HERE, "..", "case", "module_tray.stl"), os.path.join(HERE, "..", C.STLS, "module_tray.stl"))
    kicad = lambda pts: [(round(float(x), 4), round(float(-y), 4)) for x, y in pts]
    bl = board_layout(L, main_plan)
    wires, bat = bl["wires"], bl["bat"]
    outline, bites, shift = panel(L, main_plan, sensor_plan)
    from shapely import affinity
    held = lambda pts: kicad([(x, y - shift) for x, y in pts])
    json.dump(dict(
        panel=kicad(outline.exterior.coords), panel_inner=kicad(outline.buffer(-0.35, join_style=2).exterior.coords),
        bites=kicad(bites), wire_pads=kicad(wires), battery_pads=kicad(bat),
        controller_pads=kicad(bl["controller"]), pad_labels={k: kicad([v])[0] for k, v in bl["labels"].items()},
        height=H, ball=L["ball"], keys=L["keys"], switch_angle=SWITCH_ANGLE, nano=L["nano"], battery=L["battery"],
        main_board=kicad(main_plan.exterior.coords), sensor_board=held(sensor_plan.exterior.coords),
        sensor_shift=shift, main_holes=kicad(board_holes()), sensor_holes=held(sensor_holes(L)), sensor_parts=SENSOR_PARTS,
        nano_row1=NANO_ROW1, opt=OPT, pcb_top=PCB_TOP, back=L["back"],
        xiao_front=-xiao_back(L) + XIAO_USB_OVERHANG + XIAO_LENGTH, **controller_design(L, main_plan, sensor_plan)),
        open(os.path.join(HERE, "design.json"), "w"), indent=1, default=lambda o: [float(v) for v in o])
    return L, lid_m, tray_m, ps


if __name__ == "__main__":
    main()
