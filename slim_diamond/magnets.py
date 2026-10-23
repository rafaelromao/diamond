"""Finds the magnets by measuring the solid base: the floor's four, then the seam's row.

Floor: the base built without magnet pockets, sliced flat from the desk up to the pocket's depth
plus SKIN, overlaps in the plastic a pocket can sink into. Shrunk by the pocket's radius plus
SKIN, and kept to design.py's room (off the Xiao's antenna, the pad slots, the screws and a strip
along the seam), that leaves where centres may go. The four go as far apart as they can: the
smallest distance between any two is as large as it gets.

Seam: the same, sliced parallel to the seam face from the face to the pocket's depth plus SKIN,
in the base with the floor pockets cut. Each height gets the most centres the free stretches
hold, GAP apart, spread evenly from end to end; the height holding the most wins.

Prints the lines to pin in design.py (MAG_FLOOR_SPOTS, MAG_SIDE_SPOTS). Run after design.py.
"""
import math
from functools import reduce
from itertools import combinations

from shapely.geometry import LineString, Point, Polygon
from shapely.ops import unary_union

import case as C
import design as DZ

SKIN = 0.5           # plastic round each pocket
GAP = 2.5            # plastic between neighbouring seam pockets


def region(m, levels):
    """Where m is solid at every one of the slice levels (z of m)."""
    def section(z):
        ps = [Polygon(p) for p in m.slice(z).to_polygons()]
        return reduce(lambda a, p: a.symmetric_difference(p), ps[1:], ps[0]).buffer(0)
    return reduce(lambda a, b: a.intersection(b), [section(z) for z in levels])


def levels(depth):
    return [0.05] + [0.25 * i for i in range(1, int(depth / 0.25) + 2)]


def floor_spots(base):
    d, h = DZ.MAG_FLOOR
    room = unary_union([Polygon(C.plan(p)) for p in C.D["magnet_floor_room"]])
    ok = region(base, levels(h + SKIN)).buffer(-(d / 2 + SKIN)).intersection(room)
    x0, y0, x1, y1 = ok.bounds
    grid = [(x0 + i * 0.5, y0 + j * 0.5) for i in range(int((x1 - x0) * 2) + 1)
            for j in range(int((y1 - y0) * 2) + 1) if ok.contains(Point(x0 + i * 0.5, y0 + j * 0.5))]
    # candidates near the region's edge, then the best four of them by their closest pair
    edge = ok.boundary
    rim = [p for p in grid if edge.distance(Point(p)) < 0.6][::3]
    best = max(combinations(rim, 4), key=lambda q: min(math.dist(a, b) for a, b in combinations(q, 2)))
    # polish: move each spot over the whole grid while the closest pair grows
    spots = list(best)
    for _ in range(3):
        for i in range(4):
            others = spots[:i] + spots[i + 1:]
            spots[i] = max(grid, key=lambda p: min(min(math.dist(p, o) for o in others),
                                                   min(math.dist(a, b) for a, b in combinations(others, 2))))
    gap = min(math.dist(a, b) for a, b in combinations(spots, 2))
    # back to the PCB plan (the tilt shortens x across the tent)
    c = math.cos(C.TENT)
    return [[round(C.WALL_IN + (x - C.WALL_IN) / c, 2), round(y, 2)] for x, y in spots], gap


def seam_spots(base):
    d, h = DZ.MAG_SIDE
    turned = base.rotate((0, 90, 0))            # desk X becomes -z: slice at constant X
    ok = region(turned, [-(C.WALL_OUT - t) for t in levels(h + SKIN)]).buffer(-(d / 2 + SKIN))  # (z, y)
    pitch = d + GAP
    zmin, _, zmax, _ = ok.bounds
    best = None
    for i in range(int((zmax - zmin) * 4) + 1):
        z = round(zmin + i / 4, 2)
        cut = ok.intersection(LineString([(z, -1e3), (z, 1e3)]))
        spans = sorted(sorted((g.coords[0][1], g.coords[-1][1]))
                       for g in getattr(cut, "geoms", [cut]) if not g.is_empty)
        ys = []
        for a, b in spans:
            n = int((b - a) // pitch) + 1
            for k in range(n):
                y = a + (b - a) * k / (n - 1) if n > 1 else (a + b) / 2
                if not ys or y - ys[-1] >= pitch - 1e-6:
                    ys.append(round(y, 2))
        if best is None or len(ys) > len(best[1]):
            best = (z, ys)
    return best


def main():
    C.D["magnets_floor"], C.D["magnets_side_y"] = [], []
    floor, gap = floor_spots(C.build())
    print(f"MAG_FLOOR_SPOTS = {floor}   # closest pair {gap:.1f} mm apart")
    C.D["magnets_floor"] = floor
    z, ys = seam_spots(C.build())
    print(f"MAG_SIDE_SPOTS = ({z}, {ys})")


if __name__ == "__main__":
    main()
