"""The drawer's placeholder: a solid insert, for when neither the trackball nor the trackpad is in.

It has the modules' outline and magnets (module_shell.py), flush with the halves' top edges, solid
down to the drawer's floor (no feet: it stands on the floor directly, so its magnets sit where a
module's do), and the joined board's diamond cut into its top. Printed solid (any infill), it
carries the dock's middle as the old spine did.

Writes case/insert.stl (and the repo's STL folder), and checks it against the dock and the halves.
"""
import os
import shutil

import case as C
import dock as K
import module_shell as M

H = M.FLUSH


def build():
    body = M.bevel(M.extrude(M.OUTLINE, 0.0, H) + M.rear_hood(), H)
    body -= M.magnet_pockets()
    art, scale = K.relief(M.OUTLINE, H)
    return body - art, scale


def main():
    ins, scale = build()
    k = K.make()
    half = k.p(K.HALF)
    docked = ins.translate((0, 0, M.FLOOR_Z))
    print("Placeholder insert: x dock %.3f mm3, x left half %.3f, x right half %.3f; top %.2f mm over the"
          " halves' top edges; diamond at %.0f %% scale" % ((docked ^ k.solid).volume(), (docked ^ half).volume(),
          (docked ^ half.mirror((1, 0, 0))).volume(), H + M.FLOOR_Z - M.SPINE_TOP, 100 * scale))
    b = ins.bounding_box()
    print("  %.1f x %.1f x %.1f mm, %.1f cm3, genus %d" % (b[3] - b[0], b[4] - b[1], b[5] - b[2],
                                                           ins.volume() / 1000, ins.genus()))
    C.stl(ins, "case/insert.stl")
    shutil.copyfile("case/insert.stl", os.path.join(C.STLS, "insert.stl"))


if __name__ == "__main__":
    main()
