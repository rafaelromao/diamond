"""Slim Diamond Trackpad: a 40 mm Cirque trackpad and two Choc hot-swap keys, in a drawer module.

It is the trackball's module with a different lid. The tray, the main board (keys, sockets, power
switch), the nice!nano, the battery and a sensor board are all the same, in the same places: the
power switch and USB-C at the back, the reset button pressed from below. Only the lid differs: it
carries the pad, on a ledge. The sensor board carries nothing but its reset button. No ribbon cable:
seven wires go straight from the pad's labelled test pads to the nice!nano.

Writes trackpad/design.json (placement, wiring), case/lid.stl, and prints the fit check.
"""
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

import numpy as np
from manifold3d import Manifold
from shapely.geometry import Point, box

import case as C
import module_shell as M
from trackball import trackball as B

H = M.PCB_TOP + B.CHOC["below_plate"]   # the Choc trackball's height
TOP_T = 1.2                    # the top: a Choc plate (the switches clip into 1.2 to 1.3 mm)
# TM040040 spec: 0.99 mm PCB + overlay, 5.15 +/- 0.2 mm with components, none in the outer 2 mm ring.
# The seat is 1.2 deep: the difference is the adhesive dots. The ledge sits under that free ring.
PAD = dict(d=40.0, t=1.2, back=4.4, clr=0.3, rim=1.0, ledge=1.8, gap=12.0)
NANO = B.NANO
box3 = B.box3
usb_z = B.usb_z
PLATE_TOP = B.PLATE_TOP


def place():
    L = dict(B.place())
    top = M.profile(H)
    r = PAD["d"] / 2 + PAD["clr"]
    # the pad: as far forward as fits with PAD['rim'] of top round it
    L["pad"] = (0.0, next(y for y in np.arange(top.bounds[1] + r, -30, 0.1)
                          if top.buffer(-PAD["rim"]).contains(Point(0, y).buffer(r))))
    L["reset"] = B.sensor_reset(L)
    return L


def parts(L, main_plan, sensor_plan):
    """The parts as solids, for the checks and the renders."""
    out = [p for p in B.parts(L, main_plan, sensor_plan, "choc")
           if not p[0].startswith(("ball", "bearing", "lens", "sensor's parts"))]
    px, py = L["pad"]
    pz = H - PAD["t"]
    out.append(("pad", Manifold.cylinder(PAD["t"], PAD["d"] / 2, circular_segments=96).translate((px, py, pz))))
    out.append(("pad's back parts", Manifold.cylinder(PAD["back"], PAD["d"] / 2 - PAD["ledge"] - 0.3,
                                                      circular_segments=96).translate((px, py, pz - PAD["back"]))))
    return out


def lid(L):
    sh = B.lid(L, "choc", ball=False)
    # the pad's seat: through the top, and a ledge round it under its rim, open at the back
    px, py = L["pad"]
    r = PAD["d"] / 2 + PAD["clr"]
    sh -= Manifold.cylinder(TOP_T + 1, r, circular_segments=120).translate((px, py, H - TOP_T - 0.5))
    ledge_z = H - PAD["t"]
    ring = Point(px, py).buffer(r + 3.0).difference(Point(px, py).buffer(PAD["d"] / 2 - PAD["ledge"]))
    ring = ring.difference(box(px - PAD["gap"] / 2, py, px + PAD["gap"] / 2, py + 40))
    ring = ring.difference(B.main_board_plan(L).buffer(.3)).intersection(M.inner().buffer(-M.LID_CLR, join_style=2))
    for x, y in M.lid_screws()[:2]:
        ring = ring.difference(Point(x, y).buffer(M.SCREW["post"] / 2 + .3))
    # It grows inwards at 45 degrees as the lid prints, top down, so its seat needs no support
    seat = M.K.module_front(M.extrude(ring, ledge_z - 1.0, ledge_z + .01), M.P, M.WALL + M.LID_CLR)
    cone = Manifold.cylinder(1.0, PAD["d"] / 2 - PAD["ledge"] + 1.0, PAD["d"] / 2 - PAD["ledge"],
                             circular_segments=120).translate((px, py, ledge_z - 1.0))
    sh += seat - cone
    sh -= Manifold.cylinder(TOP_T + 1, r, circular_segments=120).translate((px, py, ledge_z))
    return M.lid_holes(M.bevel(sh, H), H)


def wiring():
    """nice!nano pins (Pro Micro names, nRF52840 port.pin) for each wire, from the pad's labelled test
    pads. The keys, reset and power go through the main board's pads, as on the trackball."""
    return {
        "pad SCK": ("D3", "P0.20"), "pad SO": ("D4", "P0.22"), "pad SS": ("D6", "P1.00"), "pad DR": ("D7", "P0.11"),
        "pad SI": ("D5", "P0.24"), "pad GND": ("GND", ""), "pad VDD": ("VCC", "3.3 V"),
        "main board K1": ("D8", "P1.04"), "main board K2": ("D9", "P1.06"),
        "main board GND": ("GND", ""), "main board VBAT": ("B+", ""), "main board RST": ("RST", ""),
    }


def main():
    L = place()
    tray_m, main_plan, sensor_plan = B.tray(L), B.main_board_plan(L), B.sensor_board_plan(L)
    lid_m = lid(L)
    ps = parts(L, main_plan, sensor_plan)
    M.check_common("Slim Diamond Trackpad", lid_m, tray_m, ps)
    M.check_dock_and_desk(lid_m, tray_m, H, ps)
    print("  height %.2f mm, pad centre y %.2f, keys at y %s" % (H, L["pad"][1], ["%.1f" % k[1] for k in L["keys"]]))
    print("  lid %.1f cm3, genus %d" % (lid_m.volume() / 1000, lid_m.genus()))
    os.makedirs(os.path.join(HERE, "case"), exist_ok=True)
    B.stl_lid(lid_m, H, os.path.join(HERE, "case", "lid.stl"))
    shutil.copyfile(os.path.join(HERE, "case", "lid.stl"), os.path.join(HERE, "..", C.STLS, "trackpad_lid.stl"))
    json.dump(dict(layout={k: v for k, v in L.items()}, height=H, screws=M.lid_screws(), feet=M.feet_spots(),
                   wiring=wiring()), open(os.path.join(HERE, "design.json"), "w"), indent=1,
              default=lambda o: [float(v) for v in o])
    return L, lid_m, tray_m, ps


if __name__ == "__main__":
    main()
