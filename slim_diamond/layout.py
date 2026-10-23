"""Diamond Air key layout: the Diamond's angles and stagger, packed at Choc spacing.

Coordinates are KiCad's: millimetres, y grows downwards. Angles are QMK-style
(degrees clockwise on screen); KiCad footprint orientation is the negative.
Everything is computed for the LEFT half; the right half is its mirror.
"""
import json
import math

from shapely import affinity
from shapely.geometry import Polygon, box

CAP_W, CAP_H = 17.5, 16.5  # Kailh Choc v1 keycap
CAP_GAP = 0.5               # minimum gap between keycaps
ROW_PITCH = 17.0            # Choc vertical pitch

# Diamond geometry, measured from diamond-layout.json (body_right.stl).
SPLAY = 10.0                # whole half, clockwise
RING_REL = -3.1             # ring column relative to middle
PINKY_REL = -6.9            # pinky key relative to middle
THUMB_REL = 17.1            # thumb pair relative to middle
INDEX_STAGGER = 6.37        # index home below middle home (mm)
RING_STAGGER = 4.38         # ring home below middle home (mm)


def rot(p, deg, origin=(0.0, 0.0)):
    a = math.radians(deg)
    x, y = p[0] - origin[0], p[1] - origin[1]
    return (origin[0] + x * math.cos(a) - y * math.sin(a),
            origin[1] + x * math.sin(a) + y * math.cos(a))


def cap(c, r, w=CAP_W, h=CAP_H):
    return affinity.rotate(box(c[0] - w / 2, c[1] - h / 2, c[0] + w / 2, c[1] + h / 2),
                           r, origin=c)


def closest(make, lo, hi, others):
    """Smallest offset t in [lo, hi] where cap make(t) keeps CAP_GAP from all others."""
    def ok(t):
        poly = cap(*make(t))
        return all(poly.distance(o) >= CAP_GAP for o in others)
    assert ok(hi), "upper bound collides"
    for _ in range(60):
        mid = (lo + hi) / 2
        if ok(mid):
            hi = mid
        else:
            lo = mid
    return hi


def column(home, r, names):
    keys = {}
    for i, n in enumerate(names):
        keys[n] = (rot((home[0], home[1] + (i - 1) * ROW_PITCH), r, home), r)
    return keys


def layout_midframe():
    """Keys in the middle column's frame (middle column vertical)."""
    k = {}
    k.update(column((0.0, 0.0), 0.0, ["middle_top", "middle_home", "middle_bottom"]))
    k.update(column((18.0, INDEX_STAGGER), 0.0, ["index_top", "index_home", "index_bottom"]))
    placed = [cap(*v) for v in k.values()]

    def ring_at(t):
        return column((-t, RING_STAGGER), RING_REL, ["ring_top", "ring_home", "ring_bottom"])

    t = closest(lambda t: ring_at(t)["ring_bottom"], 17, 30, placed)
    t = max(t, closest(lambda t: ring_at(t)["ring_home"], 17, 30, placed))
    t = max(t, closest(lambda t: ring_at(t)["ring_top"], 17, 30, placed))
    k.update(ring_at(t))
    placed = [cap(*v) for v in k.values()]

    # Pinky: halfway between ring home and ring bottom, pushed out along the ring's row axis.
    rh, rb = k["ring_home"][0], k["ring_bottom"][0]
    mid = ((rh[0] + rb[0]) / 2, (rh[1] + rb[1]) / 2)
    ax = rot((-1.0, 0.0), RING_REL)
    t = closest(lambda t: ((mid[0] + ax[0] * t, mid[1] + ax[1] * t), PINKY_REL), 10, 30, placed)
    k["pinky"] = ((mid[0] + ax[0] * t, mid[1] + ax[1] * t), PINKY_REL)
    placed.append(cap(*k["pinky"]))

    # Thumbs: outer thumb straight below the index column, inner one 18 mm along the thumb row.
    ib = k["index_bottom"][0]

    def thumbs(t):
        outer = (ib[0], ib[1] + t)
        inner = (outer[0] + 18.0 * math.cos(math.radians(THUMB_REL)),
                 outer[1] + 18.0 * math.sin(math.radians(THUMB_REL)))
        return {"thumb_outer": (outer, THUMB_REL), "thumb_inner": (inner, THUMB_REL)}

    t = closest(lambda t: thumbs(t)["thumb_outer"], 10, 40, placed)
    t = max(t, closest(lambda t: thumbs(t)["thumb_inner"], 10, 40, placed))
    k.update(thumbs(t))
    return k


def layout_left():
    """Left half, splayed SPLAY degrees clockwise, as on the desk."""
    out = {}
    for n, (c, r) in layout_midframe().items():
        out[n] = (rot(c, SPLAY), r + SPLAY)
    return out


if __name__ == "__main__":
    keys = layout_left()
    caps = [cap(*v) for v in keys.values()]
    from shapely.ops import unary_union
    u = unary_union(caps)
    print("bounds", [round(b, 2) for b in u.bounds],
          "size", round(u.bounds[2] - u.bounds[0], 2), round(u.bounds[3] - u.bounds[1], 2))
    for n, (c, r) in keys.items():
        print(f"{n:14s} ({c[0]:7.2f},{c[1]:7.2f}) r={r:5.1f}")
    json.dump({n: {"x": c[0], "y": c[1], "r": r} for n, (c, r) in keys.items()},
              open("keys.json", "w"), indent=1)
