"""Both halves together, for renders: joined as a unibody, and stacked back to back.

Builds the left half as it sits on the desk (case, PCB, switches with keycaps,
battery) and writes two VRML scenes into .render/:

  unibody.wrl   the right half beside it, mirrored about the seam
  stacked.wrl   the right half under it, floor to floor: turned over, the
                mirrored half is the left one mirrored in z

render_boards.py hangs each scene on a speck of board hidden in a floor, and
records where that speck is in .render/scenes.json.
"""
import json
import math

from manifold3d import Manifold

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
    return parts


def main():
    left = left_half()
    seam = D["wall_out"]
    unibody = left + [(m.mirror((1, 0, 0)).translate((2 * seam, 0, 0)), rgb) for m, rgb in left]
    stacked = left + [(m.mirror((0, 0, 1)), rgb) for m, rgb in left]
    # the speck of board render_boards.py adds: a point inside a floor, and the scene's
    # z shift that puts that floor around z = 0 (the board's top face)
    xs = [p[0] for p in D["case_outline"]]
    ys = [p[1] for p in D["case_outline"]]
    centre_y = (min(ys) + max(ys)) / 2
    scenes = {
        "unibody": {"speck": [seam - 12, centre_y], "z": -2.0, "size": 2 * (seam - min(xs))},
        "stacked": {"speck": [(min(xs) + seam) / 2, centre_y], "z": 0.0, "size": max(ys) - min(ys)},
    }
    for name, parts in (("unibody", unibody), ("stacked", stacked)):
        dz = scenes[name]["z"]
        vrml.write_parts(f".render/3d/{name}.wrl", [(m.translate((0, 0, dz)), rgb) for m, rgb in parts])
    json.dump(scenes, open(".render/scenes.json", "w"), indent=1)


if __name__ == "__main__":
    main()
