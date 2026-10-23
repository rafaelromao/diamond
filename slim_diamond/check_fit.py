"""Interference check: every part against the case and plate, all must read 0 mm3.

  - each part under the PCB, and the PCB itself, against the solid base
  - the battery against the base and the sockets
  - the plate against the case, the switch bodies through it, and the solder blobs
  - the reset button: its body against the plate, its plunger open from above and just under the
    plate top, the reset fill holes' solder blobs, and its cone off the keycaps (3 mm margin)
  - each screw against every pocket, each magnet against every pocket and opening
  - a USB-C cable plugged in, and the power switch's lever as the PCB drops in
  - the anti-slip pad slots, with a 0.5 mm skin, against every pocket, magnet and pilot hole;
    stacked (the exported right half turned over), each half's pads against the other's floor;
    and the balance: every key centre inside each half's pads, PAD_BALANCE in
"""
import json
from itertools import permutations
import math

from manifold3d import Manifold
from shapely.geometry import MultiPoint, Point, Polygon
from shapely.ops import unary_union

from shapely.geometry import box

import case as C
import design as DZ

D = json.load(open("design.json"))
PL = D["plate"]
results = []


def overlap(name, a, b):
    v = (a ^ b).volume()
    results.append(v)
    print(f"{name:34s} {v:8.3f} mm3")


base = C.build()
parts = C.part_footprints()
for name, poly, h in parts:
    overlap(f"{name} vs base", C.to_desk_solid(C.slab(poly, -h, 0)), base)
overlap("pcb vs base", C.to_desk_solid(C.slab(Polygon(D["pcb_outline"]), 0, C.PCB_T)), base)
batt = C.battery()
sockets = next(p for n, p, h in parts if n == "sockets")
overlap("battery vs base", batt, base)
overlap("battery vs sockets", batt, C.to_desk_solid(C.slab(sockets, -DZ.SOCKET_DEPTH, 0)))

# The plate, in place.
plate, _ = C.plate()
z_plate = C.PCB_T + PL["gap"]
plate_desk = C.to_desk_solid(plate.translate((0, 0, z_plate)))
overlap("plate vs base", plate_desk, base)
keys = DZ.layout_left()
bodies = unary_union([DZ.place(DZ.rect(PL["cut"], PL["cut"]), *keys[n]) for n in DZ.KEY_ORDER])
overlap("switch bodies vs plate", C.slab(bodies, C.PCB_T, z_plate + PL["thick"]),
        plate.translate((0, 0, z_plate)))
blob = Polygon(D["blob_zone"]).buffer(-0.5)          # blobs up to 1.4 mm tall over the Xiao area
overlap("solder blobs vs plate", C.slab(blob, C.PCB_T, C.PCB_T + 1.4), plate.translate((0, 0, z_plate)))

# The reset button (switch face): its body, collar and plunger against the plate; the plunger's
# column up through the plate must be open (pressed straight down from above); a solder blob
# on each reset fill hole (switch face) against the plate; and the cone's top, with margin,
# off every keycap's footprint in plan.
RB = D["reset_button"]
rbc, rbr = (RB["x"], RB["y"]), RB["r"]
plate_at = plate.translate((0, 0, z_plate))
cyl = lambda h, d: Manifold.cylinder(h, d / 2, circular_segments=48)
button = (C.slab(DZ.place(DZ.rect(RB["body"], RB["body"]), rbc, rbr), C.PCB_T, C.PCB_T + RB["cover_h"])
          + cyl(RB["collar_h"], RB["collar_d"]).translate((*rbc, C.PCB_T))
          + cyl(RB["h"], RB["plunger_d"]).translate((*rbc, C.PCB_T)))
overlap("reset button body vs plate", button, plate_at)
overlap("reset plunger column (reachable)", cyl(20, RB["plunger_d"]).translate((*rbc, C.PCB_T)), plate_at)
top_z = z_plate + PL["thick"]
under_top = top_z - (C.PCB_T + RB["h"])
print(f"{'  plunger top under the plate top':34s} {under_top:8.3f} mm (travel {RB['travel']})")
results.append(0.0 if 0 <= under_top <= 0.5 else 1.0)
import footprints as FP
xc_, xa_ = (D["xiao"]["x"], D["xiao"]["y"]), D["xiao"]["r"]
for nm, sx in (("RSTR", 1), ("RSTL", -1)):
    hx, hy = DZ.local_to_board(xc_, xa_, (sx * FP.XIAO_RST[0], FP.XIAO_RST[1]))
    overlap(f"{nm} hole solder blob vs plate", cyl(1.4, 2.0).translate((hx, hy, C.PCB_T)), plate_at)
from layout import cap
caps = unary_union([cap(*keys[n]) for n in DZ.KEY_ORDER])
cone_top = Point(rbc).buffer(RB["throat"] / 2 + PL["thick"] + PL["gap"] - RB["pocket_h"])
margin = 3.0
a = cone_top.buffer(margin).intersection(caps).area
results.append(a)
print(f"{'reset cone (+%.0f mm) vs keycaps, plan' % margin:34s} {a:8.3f} mm2   "
      f"(plunger {caps.distance(Point(rbc)):.2f} mm, cone edge {caps.distance(cone_top):.2f} mm from a cap)")

# Screws (8 mm from the plate top, 3 mm shank) and magnets against every pocket.
pockets = Manifold()
for name, poly, h in parts:
    pockets += C.to_desk_solid(C.slab(poly.buffer(C.TOL, join_style=2), -(h + C.TOL), 0))
bay = Polygon(D["jst"]["bay"]).buffer(C.TOL, join_style=2)
pockets += C.section(list(bay.exterior.coords)[:-1]).extrude(60).translate((0, 0, C.FLOOR))
for cut in C.openings().values():
    pockets += cut
top = z_plate + PL["thick"]
for i, (hx, hy) in enumerate(D["mount_holes"], 1):
    screw = C.to_desk_solid(Manifold.cylinder(D["screw"]["length"], 1.5, circular_segments=20)
                            .translate((hx, hy, top - D["screw"]["length"])))
    overlap(f"screw {i} vs pockets", screw, pockets)
# Every magnet pocket with 0.5 mm all round must lie in solid base: clear of the cavity, the part
# pockets, the openings, the pad slots, the pilot holes and each other (the base built without
# magnet pockets). The probes stop 0.01 mm short of the face they open on.
mf_d, mf_h = D["magnet_floor_size"]
ms_d, ms_h = D["magnet_side_size"]
floor, side = C.D["magnets_floor"], C.D["magnets_side_y"]
C.D["magnets_floor"], C.D["magnets_side_y"] = [], []
solid = C.build()
C.D["magnets_floor"], C.D["magnets_side_y"] = floor, side
everything = Manifold.cube((1e3, 1e3, 1e3), center=True)
pockets_m, probes = [], []
for i, (mx, my) in enumerate(floor, 1):
    X, Y = C.plan([(mx, my)])[0]
    m = Manifold.cylinder(mf_h + 0.5, mf_d / 2 + 0.5, circular_segments=32).translate((X, Y, 0.01))
    pockets_m.append(Manifold.cylinder(mf_h, mf_d / 2, circular_segments=32).translate((X, Y, 0)))
    probes.append(m)
    overlap(f"floor magnet {i} (+0.5 all round) vs voids", m - solid, everything)
for i, my in enumerate(side, 1):
    at = (C.WALL_OUT - 0.01, my, D["magnet_side_z"])
    m = Manifold.cylinder(ms_h + 0.5, ms_d / 2 + 0.5, circular_segments=32).rotate((0, -90, 0)).translate(at)
    pockets_m.append(Manifold.cylinder(ms_h, ms_d / 2, circular_segments=32).rotate((0, -90, 0)).translate(at))
    probes.append(m)
    overlap(f"seam magnet {i} (+0.5 all round) vs voids", m - solid, everything)
# each pocket keeps 0.5 mm of plastic from every other magnet's pocket
near = Manifold()
for i, j in permutations(range(len(probes)), 2):
    near += probes[i] ^ pockets_m[j]
overlap("magnets (+0.5) vs each other", near, everything)


# A USB-C cable, plugged in: the overmold (12.35 x 6.5 mm, the Type-C maximum) stops 0.1 mm
# short of the receptacle's face. And the lever (1.3 wide, 1.45 past the switch body, travel
# 1.5) swept up the PCB's normal: the path it takes as the PCB drops into the base.
xc, xa = (D["xiao"]["x"], D["xiao"]["y"]), D["xiao"]["r"]
plug = C.to_desk_solid(C.slab(DZ.place(box(-6.175, -C.XIAO_END - 30, 6.175, -C.XIAO_END - 0.1), xc, xa),
                              C.USB_Z - 3.25, C.USB_Z + 3.25))
overlap("usb plug vs base", plug, base)
overlap("usb plug vs pcb", plug, C.to_desk_solid(C.slab(Polygon(D["pcb_outline"]), 0, C.PCB_T)))
# The Super52840's USB-C shell (8.94 x 3.2) sticks out further than the Xiao's: its face is 11.34
# from the pins' centre, not 10.55. Checked out to 11.6, in the shared case.
shell = C.to_desk_solid(C.slab(DZ.place(box(-4.6, -11.6, 4.6, -9.0), xc, xa), C.USB_Z - 1.7, C.USB_Z + 1.7))
overlap("super52840 usb shell vs base", shell, base)
pw = D["power_switch"]
lever = DZ.place(box(-1.5, -1.4 - 1.45, 1.5, -1.4), (pw["x"], pw["y"]), pw["r"])
overlap("switch lever (dropping in) vs base", C.to_desk_solid(C.slab(lever, -1.2, 40)), base)

# Pad slots: 0.5 mm of plastic around and above each one, clear of every pocket, magnet and pilot
# hole, and of the chamfer (the ring around a slot is solid).
SKIN = 0.5
slots = Manifold()
grown = Manifold()
for a, b in C.PADS["slots"]:
    slots += C.pad_slot(a, b)
    grown += C.pad_slot(a, b, SKIN)
magnets = Manifold()
for mx, my in D["magnets_floor"]:
    X, Y = C.plan([(mx, my)])[0]
    magnets += Manifold.cylinder(mf_h, mf_d / 2, circular_segments=32).translate((X, Y, 0))
pilots = Manifold()
for hx, hy in D["mount_holes"]:
    X, Y = C.plan([(hx, hy)])[0]
    pilots += Manifold.cylinder(60, C.PILOT_R, circular_segments=20).translate((X, Y, C.PILOT_FLOOR))
overlap("pad slots (+0.5 skin) vs pockets", grown, pockets)
overlap("pad slots (+0.5 skin) vs magnets", grown, magnets)
overlap("pad slots (+0.5 skin) vs pilot holes", grown, pilots)
ring = (grown - slots).trim_by_plane((0, 0, 1), 0)            # above the desk only
v = (ring - base).volume()
results.append(v)
print(f"{'pad slots: 0.5 mm skin all round':34s} {v:8.3f} mm3")

# Stacked: the right half as exported, turned over about the seam (x -> 2 seam - x, z -> -z),
# under the left one, floor to floor. Each half's pads must sit in the other's empty slot ends.
seam = C.WALL_OUT
turn = lambda m: m.mirror((1, 0, 0)).translate((2 * seam, 0, 0)).mirror((0, 0, 1))
left_real = C.real(base)
right_real = C.mirrored(left_real)                                  # case_right.stl
left_pads = C.real(C.pads(0))
right_pads = C.mirrored(C.real(C.pads(1)))                           # on the right half, z up
overlap("stacked: left pads vs right floor", left_pads, turn(right_real))
overlap("stacked: right pads vs left floor", turn(right_pads), left_real)
overlap("stacked: left pads vs right pads", left_pads, turn(right_pads))

# Balance: every key centre, on the floor, inside each half's pads (their hull) by PAD_BALANCE.
keys_floor = [C.plan([(k["x"], k["y"])])[0] for k in D["keys"].values()]
flip = lambda p: (2 * seam - p[0], p[1])
need = DZ.PAD_BALANCE
supports = {"left half": [C.plan([e[0]])[0] for e in C.PADS["slots"]],
            "right half (stacked frame)": [C.plan([e[1]])[0] for e in C.PADS["slots"]]}
supports["unibody"] = supports["left half"] + [flip(p) for p in supports["right half (stacked frame)"]]
for name, pts in supports.items():
    keys_ = keys_floor + ([flip(p) for p in keys_floor] if name == "unibody" else [])
    hull = MultiPoint(pts).convex_hull
    inside = hull.buffer(-need, join_style=2)
    out = [p for p in keys_ if not inside.contains(Point(p))]
    m = min(hull.exterior.distance(Point(p)) * (1 if hull.contains(Point(p)) else -1) for p in keys_)
    results.append(len(out))
    print(f"balance, {name:26s} nearest key {m:5.2f} mm inside ({need} needed): "
          f"{'ok' if not out else f'{len(out)} keys outside'}")

print("ALL CLEAR" if max(results) < 1e-3 else "INTERFERENCE")
