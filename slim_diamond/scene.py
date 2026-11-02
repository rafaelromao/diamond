"""Both halves together, for renders: joined as a unibody, and stacked back to back.

Builds the left half as it sits on the desk (case, PCB, switches with keycaps,
battery) and writes two VRML scenes into .render/:

  unibody.wrl   the right half beside it, mirrored about the seam
  stacked.wrl   the right half under it, floor to floor: turned over, the
                mirrored half is the left one mirrored in z

Each half carries its own anti-slip pads: the left's in one end of each floor slot,
the right's in the other end (case.pads), so stacked they interleave.

render_boards.py hangs each scene on a speck of board hidden in a floor, and
records where that speck is in .render/scenes.json.
"""
import json
import math

from manifold3d import CrossSection, FillRule, Manifold
from shapely.geometry import box

import case as C
import vrml
from layout import layout_left

D = json.load(open("design.json"))
c, s = math.cos(C.TENT), math.sin(C.TENT)
PCB_GREEN = (0.1, 0.32, 0.18)


def to_desk(m):
    """PCB frame (z above the PCB's bottom face) into the desk frame."""
    m = m.translate((-C.WALL_IN, 0, 0))
    m = m.transform([[c, 0, -s, 0], [0, 1, 0, 0], [s, 0, c, 0]])
    return m.translate((C.WALL_IN, 0, C.Z0))


def left_half():
    parts = [(C.build(), vrml.CASE), (C.battery(), vrml.BATTERY)]
    plate, _ = C.plate()
    parts.append((to_desk(plate.translate((0, 0, C.PCB_T + C.PLATE["gap"]))), vrml.CASE))
    pcb = C.section([tuple(p) for p in D["pcb_outline"][:-1]]).extrude(C.PCB_T)
    parts.append((to_desk(pcb), PCB_GREEN))
    t = C.PCB_T                                   # switch models start on the PCB's top face
    switch = [
        (vrml.box(-6.9, -6.9, t, 6.9, 6.9, t + 2.2), vrml.SWITCH),
        (vrml.box(-7.5, -7.5, t + 2.2, 7.5, 7.5, t + 3.0), vrml.SWITCH),
        (vrml.frustum(14.5, 14.5, 12.5, 12.5, t + 3.0, t + 5.0), vrml.SWITCH),
        (vrml.frustum(17.5, 16.5, 15.6, 14.6, t + 5.8, t + 8.6), vrml.KEYCAP),
    ]
    for (x, y), r in layout_left().values():
        for m, rgb in switch:
            parts.append((to_desk(m.rotate((0, 0, r)).translate((x, y, 0))), rgb))
    rb = D["reset_button"]                         # the reset button, on the switch face
    parts.append((to_desk(Manifold.cylinder(rb["h"], rb["plunger_d"] / 2, circular_segments=32)
                          .translate((rb["x"], rb["y"], t))), vrml.SOCKET))
    return parts


UGREEN = (0.42, 0.43, 0.47)
PHONE = (0.2, 0.2, 0.22)
SCREEN = (0.04, 0.07, 0.11)
PHONE_SIZE = (160.0, 78.0, 10.0)   # in its case, landscape: width, height, thickness
PHONE_TILT = 15.0                  # leaning back from upright
PHONE_BOTTOM = 70.0                # its lower edge over the desk


def rounded_slab(w, h, t, r):
    """A w x h plate, t thick along y, its corners rounded r: centred, face towards -y."""
    ring = list(box(-w / 2 + r, -h / 2 + r, w / 2 - r, h / 2 - r).buffer(r, quad_segs=8).exterior.coords)[:-1]
    return CrossSection([ring], FillRule.NonZero).extrude(t).translate((0, 0, -t / 2)).rotate((90, 0, 0))


def stand_and_phone(yb):
    """The Ugreen stand (base, hinge, arm, holder) with a phone on it, in the dock's real frame
    (x right, y away from the typist): the base's back edge at y = yb. A stand-in, from photos."""
    import dock as K
    w, d, t = K.UG
    parts = [(K.extrude(K.rounded_rect(w, d, 8.0, 0, yb), 0, t), UGREEN)]
    hinge_y, hinge_z = yb - 12.0, t + 6.0
    parts.append((Manifold.cylinder(26, 6, circular_segments=40).rotate((0, 90, 0)).translate((-13, hinge_y, hinge_z)), UGREEN))
    pw, ph, pt = PHONE_SIZE
    tilt = math.radians(PHONE_TILT)
    centre_z = PHONE_BOTTOM + ph / 2 * math.cos(tilt)
    centre_y = hinge_y + 6.0 + ph / 2 * math.sin(tilt)
    back = (centre_y + pt / 2 * math.cos(tilt), centre_z - pt / 2 * math.sin(tilt))
    puck = Manifold.cylinder(8, 30, circular_segments=60).rotate((-90 - PHONE_TILT, 0, 0))
    parts.append((puck.translate((0, back[0], back[1])), UGREEN))
    for x in (-12, 12):                      # two flat bars from the hinge to the holder
        bar = Manifold.hull_points([(x + sx * 2.5, y + sy * 1.5, z) for sx in (-1, 1) for sy in (-1, 1)
                                    for y, z in ((hinge_y, hinge_z), (back[0] + 6, back[1]))])
        parts.append((bar, UGREEN))
    phone = rounded_slab(pw, ph, pt, 9.0)
    screen = rounded_slab(pw - 6, ph - 6, 0.4, 6.0).translate((0, -pt / 2 - 0.15, 0))
    for m, rgb in ((phone, PHONE), (screen, SCREEN)):
        parts.append((m.rotate((-PHONE_TILT, 0, 0)).translate((0, centre_y, centre_z)), rgb))
    return parts


def dock_scenes():
    """The cyberdeck: the dock on the Ugreen base, both halves on it, the phone on the stand;
    the halves on the dock alone (a tented unibody, no stand); the dock alone, and on the base. In the plan frame (y down), like the other scenes."""
    import dock as K
    k = K.make()
    plan = C.real                                   # real frame <-> plan frame (flip y)
    placed = lambda m: plan(k.p(plan(m)))
    left = [(placed(m), rgb) for m, rgb in left_half() + [(C.pads(0), vrml.PAD)]]
    right = [(plan(k.p(plan(m)).mirror((1, 0, 0))), rgb) for m, rgb in left_half() + [(C.pads(1), vrml.PAD)]]
    dock = [(plan(k.solid), vrml.CASE), (plan(K.magnet_solids(k)), vrml.METAL), (plan(K.feet_solids(k)), vrml.PAD)]
    stand = [(plan(m), rgb) for m, rgb in stand_and_phone(k.yb)]
    base = stand[:1]
    return {"cyberdeck": dock + left + right + stand, "dock": dock, "dock_base": dock + base,
            "dock_unibody": dock + left + right}


def main():
    left = left_half()
    seam = D["wall_out"]
    pads_left, pads_right = (C.pads(0), vrml.PAD), (C.pads(1), vrml.PAD)
    unibody = left + [pads_left] + [(m.mirror((1, 0, 0)).translate((2 * seam, 0, 0)), rgb)
                                    for m, rgb in left + [pads_right]]
    stacked = left + [pads_left] + [(m.mirror((0, 0, 1)), rgb) for m, rgb in left + [pads_right]]
    # the speck of board render_boards.py adds: a point inside a floor, and the scene's
    # z shift that puts that floor around z = 0 (the board's top face)
    xs = [p[0] for p in D["case_outline"]]
    ys = [p[1] for p in D["case_outline"]]
    centre_y = (min(ys) + max(ys)) / 2
    scenes = {
        "unibody": {"speck": [seam - 12, centre_y], "z": -2.0, "size": 2 * (seam - min(xs))},
        "stacked": {"speck": [(min(xs) + seam) / 2, centre_y], "z": 0.0, "size": max(ys) - min(ys)},
    }
    # the dock scenes: the speck in the spine, between the base's magnets, above the base
    dock = dock_scenes()
    for name in dock:
        scenes[name] = {"speck": [0.0, 20.0], "z": -12.0, "size": 215.0}
    for name, parts in (("unibody", unibody), ("stacked", stacked), *dock.items()):
        dz = scenes[name]["z"]
        vrml.write_parts(f".render/3d/{name}.wrl", [(m.translate((0, 0, dz)), rgb) for m, rgb in parts])
    json.dump(scenes, open(".render/scenes.json", "w"), indent=1)


if __name__ == "__main__":
    main()
