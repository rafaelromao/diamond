"""Interference check: every part against the case and plate, all must read 0 mm3.

  - each part under the PCB, and the PCB itself, against the solid base
  - the battery against the base and the sockets
  - the plate against the case, the switch bodies through it, and the solder blobs
  - each screw against every pocket, each magnet against every pocket and opening
  - a USB-C cable plugged in, and the power switch's lever as the PCB drops in
"""
import json

from manifold3d import Manifold
from shapely.geometry import Polygon
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
mf_d, mf_h = D["magnet_floor_size"]
for i, (mx, my) in enumerate(D["magnets_floor"], 1):
    X, Y = C.plan([(mx, my)])[0]
    overlap(f"floor magnet {i} (+0.5 skin) vs pockets",
            Manifold.cylinder(mf_h + 0.5, mf_d / 2, circular_segments=32).translate((X, Y, 0)), pockets)
ms_d, ms_h = D["magnet_side_size"]
for i, my in enumerate(D["magnets_side_y"], 1):
    m = Manifold.cylinder(ms_h + 0.5, ms_d / 2, circular_segments=32).rotate((0, -90, 0))
    overlap(f"seam magnet {i} (+0.5 wall) vs pockets", m.translate((C.WALL_OUT, my, C.FLOOR + 2.8)), pockets)


# A USB-C cable, plugged in: the overmold (12.35 x 6.5 mm, the Type-C maximum) stops 0.1 mm
# short of the receptacle's face. And the lever (1.3 wide, 1.45 past the switch body, travel
# 1.5) swept up the PCB's normal: the path it takes as the PCB drops into the base.
xc, xa = (D["xiao"]["x"], D["xiao"]["y"]), D["xiao"]["r"]
plug = C.to_desk_solid(C.slab(DZ.place(box(-6.175, -C.XIAO_END - 30, 6.175, -C.XIAO_END - 0.1), xc, xa),
                              C.USB_Z - 3.25, C.USB_Z + 3.25))
overlap("usb plug vs base", plug, base)
overlap("usb plug vs pcb", plug, C.to_desk_solid(C.slab(Polygon(D["pcb_outline"]), 0, C.PCB_T)))
pw = D["power_switch"]
lever = DZ.place(box(-1.5, -1.4 - 1.45, 1.5, -1.4), (pw["x"], pw["y"]), pw["r"])
overlap("switch lever (dropping in) vs base", C.to_desk_solid(C.slab(lever, -1.2, 40)), base)

print("ALL CLEAR" if max(results) < 1e-3 else "INTERFERENCE")
