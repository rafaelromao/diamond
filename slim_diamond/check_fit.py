"""Interference check: parts under the PCB, and the PCB itself, against the case."""
import json
import math

from manifold3d import CrossSection, FillRule, Manifold
from shapely import affinity
from shapely.geometry import box

import case as C
from design import XIAO_DEPTH, JST_H, PWR_H, SOCKET_DEPTH, under_switch, place, rect
from layout import layout_left

D = json.load(open("design.json"))
c, s = math.cos(C.TENT), math.sin(C.TENT)


def to_desk(m):
    """PCB frame (z above the PCB's bottom face) into the desk frame."""
    m = m.translate((-C.WALL_IN, 0, 0))
    m = m.transform([[c, 0, -s, 0], [0, 1, 0, 0], [s, 0, c, 0]])
    return m.translate((C.WALL_IN, 0, C.Z0))


def slab(poly, z0, z1):
    polys = getattr(poly, "geoms", [poly])
    cs = CrossSection([list(p.exterior.coords)[:-1] for p in polys], FillRule.NonZero)
    return cs.extrude(z1 - z0).translate((0, 0, z0))


case = C.build()
keys = layout_left()
parts = {
    "sockets": (Manifold.batch_boolean if False else None, None),
}
items = []
from shapely.ops import unary_union
socks = unary_union([under_switch(*keys[n]) for n in keys])
items.append(("sockets+pins", slab(socks, -SOCKET_DEPTH, 0)))
x = D["xiao"]
items.append(("xiao", slab(place(rect(17.5, 21.0), (x["x"], x["y"]), x["r"]), -XIAO_DEPTH, 0)))
jb = D["jst"]["bounds"]
items.append(("jst", slab(box(*jb), -JST_H, 0)))
p = D["power_switch"]
items.append(("power switch", slab(place(rect(6.7, 2.7), (p["x"], p["y"]), p["r"]), -PWR_H, 0)))
from shapely.geometry import Polygon
items.append(("pcb", slab(Polygon(D["pcb_outline"]), 0, C.PCB_T)))
for name, solid in items:
    v = (to_desk(solid) ^ case).volume()
    print(f"{name:14s} overlap with case: {v:.3f} mm3")
batt = C.battery()
print(f"{'battery':14s} overlap with case: {(batt ^ case).volume():.3f} mm3")
# battery top vs PCB/sockets above it
under_parts = to_desk(slab(socks, -SOCKET_DEPTH, 0))
print(f"{'battery':14s} overlap with sockets: {(batt ^ under_parts).volume():.3f} mm3")
