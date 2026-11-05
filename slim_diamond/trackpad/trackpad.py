"""Slim Diamond Trackpad: a 40 mm Cirque trackpad and two Choc keys, hand-wired, in a drawer module.

Everything stands on the shared shell (module_shell.py): flush with the halves' top edges, three
magnets per side, a screwed bottom plate on bump-ons. The pad sits at the front, in the top, on a
ledge (open at the back for its cable); the two keys stack behind it. Under the pad, on the plate:
the battery (the halves' 752025) in a cradle, and the pad's cable adapter on a shelf over it, with
room for the wires round them. Under the keys: the nice!nano, USB-C out of the back wall; the power switch in the
back wall over it; the reset button on the plate, pressed through it from below.

Writes trackpad/design.json (placement, wiring), case/*.stl, and prints the fit check.
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

H = M.FLUSH                    # flush with the halves' top edges, in the dock and on the desk
TOP_T = 1.2                    # the top: a Choc plate (the switches clip into 1.2 to 1.3 mm)
PAD = dict(d=40.0, t=1.7, back=2.0, clr=0.25, rim=1.0, ledge=1.8, gap=12.0)   # TM040040: check t, back
CHOC_CUT = 13.8 + 0.2          # Choc v1 plate cutout
CHOC = dict(cap=(17.5, 16.5), pitch=17.0, body=2.2, pins=3.0)
NANO = (18.0, 33.3, 1.0, 3.2)  # w, l, PCB, USB-C receptacle height (on its top face)
BAT = (25.0, 20.0, 7.5)        # 752025 lying across: w (x), l (y), thickness
ADAPTER = (20.0, 14.0, 1.6, 2.2)   # 12-pin 0.5 mm FFC to 2.54 mm adapter: w, l, PCB, its connector
SWITCH = (8.7, 3.7, 3.5, 4.0)  # SS12D00 slide switch: body l, w, h; lever length
ADAPTER_OVER = 4.0             # the adapter's solder-hole end, past the shelf's back edge
TACT = (6.0, 6.0, 3.5)         # 6 x 6 mm through-hole tact switch, plunger through the plate
CRADLE = (1.2, 3.0, 0.3)       # cradle walls: thickness, height, clearance round the part
PLATE_TOP = M.FEET + M.BOTTOM_T


def place():
    room = M.room()
    top = M.profile(H)
    # the pad: as far forward as fits with PAD['rim'] of top round it
    r = PAD["d"] / 2 + PAD["clr"]
    pad_y = next(y for y in np.arange(top.bounds[1] + r, -30, 0.1)
                 if top.buffer(-PAD["rim"]).contains(Point(0, y).buffer(r)))
    k1 = pad_y + r + 1.2 + CHOC["cap"][1] / 2 + 4.0  # both keys rearward, keeping the pad clear
    keys = [k1, k1 + CHOC["pitch"]]
    # the nice!nano on the plate, as far back as it fits: USB-C end at the back wall
    n_y = max(y for y in np.arange(-90, -10, 0.1)
              if room.buffer(-CRADLE[2]).contains(box(-NANO[0] / 2, y, NANO[0] / 2, y + NANO[1])))
    # the battery under the pad, as far forward as it fits
    b_y = min(y for y in np.arange(-95, -40, 0.1)
              if room.buffer(-CRADLE[0] - CRADLE[2]).contains(box(-BAT[0] / 2, y, BAT[0] / 2, y + BAT[1]))
              and M.service_plan().buffer(-CRADLE[2]).contains(box(-BAT[0] / 2, y, BAT[0] / 2, y + BAT[1])))
    # the cable adapter on a shelf over the battery (the battery slides in under it), its FFC
    # connector forwards; it overhangs the shelf at the back by ADAPTER_OVER, so its row of solder
    # holes sits over the open gap behind the battery, where the wires go down
    a_y = b_y + BAT[1] + CRADLE[2] + ADAPTER_OVER - ADAPTER[1]
    # the reset button: on the plate between the battery's cradle and the nano's, off the middle
    gap0 = b_y + BAT[1] + CRADLE[0] + CRADLE[2]
    gap1 = n_y - CRADLE[0] - CRADLE[2]
    t_spot = None
    for x in np.arange(6.0, 30, 0.5):
        y = (gap0 + gap1) / 2
        if room.buffer(-CRADLE[0] - CRADLE[2]).contains(box(x - TACT[0] / 2, y - TACT[1] / 2, x + TACT[0] / 2, y + TACT[1] / 2)):
            t_spot = (x, y)
            break
    assert t_spot, "no room for the reset button"
    back_y = M.OUTLINE.bounds[3]
    return dict(pad=(0.0, pad_y), keys=[(0.0, y) for y in keys], nano=(0.0, n_y), battery=(0.0, b_y),
                adapter=(0.0, a_y), reset=t_spot, switch=(0.0, back_y), back=back_y)


def box3(x0, y0, z0, x1, y1, z1):
    return Manifold.cube((x1 - x0, y1 - y0, z1 - z0)).translate((x0, y0, z0))


def parts(L):
    """The parts as solids, for the checks and the renders."""
    out = []
    px, py = L["pad"]
    pz = H - PAD["t"]
    out.append(("pad", Manifold.cylinder(PAD["t"], PAD["d"] / 2, circular_segments=96).translate((px, py, pz))))
    out.append(("pad's back parts", Manifold.cylinder(PAD["back"], PAD["d"] / 2 - PAD["ledge"] - 0.3,
                                                      circular_segments=96).translate((px, py, pz - PAD["back"]))))
    for i, (kx, ky) in enumerate(L["keys"]):
        z = H - TOP_T
        body = box3(kx - 6.9, ky - 6.9, z - CHOC["body"], kx + 6.9, ky + 6.9, z)
        pins = box3(kx - 6.0, ky - 3.0, z - CHOC["body"] - CHOC["pins"], kx + 6.0, ky + 6.0, z - CHOC["body"])
        cap = box3(kx - CHOC["cap"][0] / 2, ky - CHOC["cap"][1] / 2, H + 2.2, kx + CHOC["cap"][0] / 2,
                   ky + CHOC["cap"][1] / 2, H + 5.2)
        out.append(("choc %d" % (i + 1), body + pins))
        out.append(("keycap %d" % (i + 1), cap))
    nx, ny = L["nano"]
    z = PLATE_TOP + 0.5
    nano = box3(nx - NANO[0] / 2, ny, z, nx + NANO[0] / 2, ny + NANO[1], z + NANO[2])
    nano += box3(nx - 4.5, ny + NANO[1] - 7.3, z + NANO[2], nx + 4.5, ny + NANO[1] + 0.6, z + NANO[2] + NANO[3])
    out.append(("nice!nano", nano))
    bx, by = L["battery"]
    out.append(("battery", box3(bx - BAT[0] / 2, by, PLATE_TOP, bx + BAT[0] / 2, by + BAT[1], PLATE_TOP + BAT[2])))
    ax, ay = L["adapter"]
    az = shelf_top()
    out.append(("FFC adapter", box3(ax - ADAPTER[0] / 2, ay, az, ax + ADAPTER[0] / 2, ay + ADAPTER[1],
                                    az + ADAPTER[2] + ADAPTER[3])))
    tx, ty = L["reset"]
    out.append(("reset", box3(tx - TACT[0] / 2, ty - TACT[1] / 2, PLATE_TOP, tx + TACT[0] / 2, ty + TACT[1] / 2,
                              PLATE_TOP + TACT[2])))
    sx, sy = L["switch"]
    zc = switch_z(L)
    sw = box3(sx - SWITCH[0] / 2, sy - M.WALL - SWITCH[1] - 0.2, zc - SWITCH[2] / 2, sx + SWITCH[0] / 2,
              sy - M.WALL - 0.2, zc + SWITCH[2] / 2)
    out.append(("power switch", sw))
    return out


SHELF_T = 1.2


def shelf_top():
    """The adapter's shelf, over the battery."""
    return PLATE_TOP + BAT[2] + 0.4 + SHELF_T


def usb_z(L):
    return PLATE_TOP + 0.5 + NANO[2] + NANO[3] / 2


def switch_z(L):
    """Over the USB-C opening, under the keys' pins."""
    return usb_z(L) + NANO[3] / 2 + 1.5 + SWITCH[2] / 2 + 0.5


def shell_and_plate(L):
    posts = M.screw_spots(3, keep_out=unary_union([
        Point(*L["pad"]).buffer(PAD["d"] / 2 + PAD["clr"] + 0.5),
        Point(*L["nano"]).buffer(1).union(box(-NANO[0] / 2 - 0.5, L["nano"][1] - 1, NANO[0] / 2 + 0.5, L["nano"][1] + NANO[1] + 1)),
        box(-BAT[0] / 2 - 2, L["battery"][1] - 2, BAT[0] / 2 + 2, L["battery"][1] + BAT[1] + 2)] +
        [box(kx - 7.5, ky - 7.5, kx + 7.5, ky + 7.5) for kx, ky in L["keys"]] +
        [box(-SWITCH[0] / 2 - 2, L["back"] - M.WALL - SWITCH[1] - 2.5, SWITCH[0] / 2 + 2, L["back"])]))
    sh = M.shell(H, TOP_T, posts)
    # the pad's seat: through the top, and a ledge round it under its rim, open at the back
    px, py = L["pad"]
    r = PAD["d"] / 2 + PAD["clr"]
    sh -= Manifold.cylinder(TOP_T + 1, r, circular_segments=120).translate((px, py, H - TOP_T - 0.5))
    sh -= Manifold.cylinder(PAD["t"] - TOP_T + 0.01, r, circular_segments=120).translate((px, py, H - PAD["t"] - 0.005))
    ledge_z = H - PAD["t"]
    ring = Point(px, py).buffer(r + 3.0).difference(Point(px, py).buffer(PAD["d"] / 2 - PAD["ledge"]))
    ring = ring.difference(box(px - PAD["gap"] / 2, py, px + PAD["gap"] / 2, py + 40)).intersection(M.inner().buffer(0.01))
    sh += M.extrude(ring, ledge_z - 1.5, ledge_z)
    # the keys' plate cutouts
    for kx, ky in L["keys"]:
        sh -= Manifold.cube((CHOC_CUT, CHOC_CUT, TOP_T + 1)).translate((kx - CHOC_CUT / 2, ky - CHOC_CUT / 2, H - TOP_T - 0.5))
    # the back wall: USB-C opening, and the switch's lever slot
    bx, by = L["switch"]
    uz = usb_z(L)
    usb = Manifold.cube((12.8, M.WALL + 3, 7.2)).translate((-6.4, by - M.WALL - 1.5, uz - 3.6))
    sh -= usb
    sh -= M.usb_clearance(L["nano"][1] + NANO[1] + 0.6, uz)
    lever = Manifold.cube((SWITCH[0] - 2.0, M.WALL + 8, 2.2)).translate((-(SWITCH[0] - 2.0) / 2, by - M.WALL - 1.5,
                                                                        switch_z(L) - 1.1))
    sh -= lever
    plate = M.bottom_plate(posts)
    # cradles on the plate: battery, adapter, nano (a stop at its front), reset
    def cradle(x0, y0, x1, y1, h, open_back=False):
        c = CRADLE[2]
        outer = box(x0 - c - CRADLE[0], y0 - c - CRADLE[0], x1 + c + CRADLE[0], y1 + c + CRADLE[0])
        ring = outer.difference(box(x0 - c, y0 - c, x1 + c, y1 + c))
        if open_back:
            ring = ring.difference(box(x0 - c - 5, y1, x1 + c + 5, y1 + c + CRADLE[0] + 1))
        return M.extrude(ring.intersection(M.room().buffer(-M.PLATE_CLR)), PLATE_TOP - 0.01, PLATE_TOP + h)
    # the battery: a cradle open at the back (it slides in under the shelf, leads first), its
    # side walls up to a shelf over it that carries the adapter, with a lip round the adapter
    bx_, by_ = L["battery"]
    c = CRADLE[2]
    x0, x1, y0, y1 = bx_ - BAT[0] / 2 - c, bx_ + BAT[0] / 2 + c, by_ - c, by_ + BAT[1] + c
    walls = box(x0 - CRADLE[0], y0 - CRADLE[0], x1 + CRADLE[0], y1).difference(box(x0, y0, x1, y1 + 1))
    sz = shelf_top() - SHELF_T
    plate += M.extrude(walls.intersection(M.room().buffer(-M.PLATE_CLR)), PLATE_TOP - 0.01, sz)
    plate += M.extrude(box(x0 - CRADLE[0], y0 - CRADLE[0], x1 + CRADLE[0], y1).intersection(M.room().buffer(-M.PLATE_CLR)),
                       sz, shelf_top())
    ax, ay = L["adapter"]
    lip = box(ax - ADAPTER[0] / 2 - c - 1.0, ay - c - 1.0, ax + ADAPTER[0] / 2 + c + 1.0, ay + ADAPTER[1] + c + 1.0)
    lip = lip.difference(box(ax - ADAPTER[0] / 2 - c, ay - c, ax + ADAPTER[0] / 2 + c, ay + ADAPTER[1] + c + 5))
    lip = lip.intersection(box(-99, -200, 99, y1))
    plate += M.extrude(lip, shelf_top() - 0.01, shelf_top() + 1.2)
    nx, ny = L["nano"]
    plate += cradle(nx - NANO[0] / 2, ny, nx + NANO[0] / 2, ny + NANO[1], 2.0, open_back=True)
    plate += M.extrude(box(nx - NANO[0] / 2 + 3, ny + 4, nx + NANO[0] / 2 - 3, ny + NANO[1] - 9), PLATE_TOP - 0.01,
                       PLATE_TOP + 0.5)                                   # its seat, under the pins' row
    tx, ty = L["reset"]
    plate += cradle(tx - TACT[0] / 2, ty - TACT[1] / 2, tx + TACT[0] / 2, ty + TACT[1] / 2, 2.0)
    plate -= Manifold.cylinder(M.BOTTOM_T + 1, 1.6, circular_segments=24).translate((tx, ty, M.FEET - 0.5))
    # the switch: a pocket in a block on the back wall's inside
    sx, sy = L["switch"]
    zc = switch_z(L)
    blk = box(-SWITCH[0] / 2 - 1.5, sy - M.WALL - SWITCH[1] - 1.7, SWITCH[0] / 2 + 1.5, sy - M.WALL + 0.1)
    sh += M.extrude(blk.intersection(M.inner().buffer(0.5)), zc - SWITCH[2] / 2 - 1.5, zc + SWITCH[2] / 2 + 1.0)
    sh -= Manifold.cube((SWITCH[0] + 0.3, SWITCH[1] + 0.3, SWITCH[2] + 0.3)).translate(
        (-(SWITCH[0] + 0.3) / 2, sy - M.WALL - SWITCH[1] - 0.35, zc - (SWITCH[2] + 0.3) / 2))
    sh -= Manifold.cube((SWITCH[0] - 1.0, SWITCH[1] + 0.3, 3.0)).translate(
        (-(SWITCH[0] - 1.0) / 2, sy - M.WALL - SWITCH[1] - 0.35, zc - SWITCH[2] / 2 - 3.0))   # its pins, down
    # The cradle follows the faceted front too, with the same clearance as the plate itself.
    plate = M.K.module_front(plate, M.P, M.WALL + M.PLATE_CLR)
    sh = M.bevel(sh, H)          # trim the pad ledge and switch block to the shared front facets too
    passage = M.usb_clearance(L["nano"][1] + NANO[1] + 0.6, usb_z(L))
    sh -= passage
    plate -= passage
    plate -= M.extrude(unary_union([Point(x, y).buffer(M.SCREW["post"] / 2 + 0.3) for x, y in posts]),
                       PLATE_TOP, H + 1)
    # Apply this last: the switch-support block is added after the original lever cut.
    sh -= lever
    plate ^= M.extrude(M.service_plan(), M.FEET - 1, H + 1)
    return sh, plate, posts


def wiring():
    """nice!nano pins (Pro Micro names, nRF52840 port.pin) for each wire."""
    return {
        "pad SCK (FFC 1)": ("D3", "P0.20"), "pad SO (FFC 2)": ("D4", "P0.22"),
        "pad SS (FFC 3)": ("D6", "P1.00"), "pad DR (FFC 4)": ("D7", "P0.11"),
        "pad SI (FFC 5)": ("D5", "P0.24"), "pad GND (FFC 11)": ("GND", ""), "pad VDD (FFC 12)": ("VCC", "3.3 V"),
        "key 1": ("D8", "P1.04"), "key 2": ("D9", "P1.06"), "keys' common": ("GND", ""),
        "reset": ("RST", ""), "reset's other leg": ("GND", ""),
        "battery +": ("B+ via the power switch", ""), "battery -": ("B-", ""),
    }


def main():
    L = place()
    sh, plate, posts = shell_and_plate(L)
    ps = parts(L)
    vol = M.check_common("Slim Diamond Trackpad", sh, plate, ps)
    M.check_dock_and_desk(sh, plate, H, ps)
    pz = H - PAD["t"]
    below = pz - PAD["back"] - (shelf_top() + ADAPTER[2] + ADAPTER[3])
    print("  under the pad's back parts: %.1f mm over the adapter on its shelf; %.1f mm between the battery's"
          " cradle and the nano's for the wires and the reset button" % (below, L["nano"][1] - L["battery"][1] - BAT[1] - 2 * (CRADLE[0] + CRADLE[2])))
    print("  height %.2f mm (flush), pad centre y %.2f, keys at y %s" % (H, L["pad"][1], ["%.1f" % k[1] for k in L["keys"]]))
    print("  shell %.1f cm3, plate %.1f cm3, genus %d / %d" % (sh.volume() / 1000, plate.volume() / 1000, sh.genus(), plate.genus()))
    os.makedirs(os.path.join(HERE, "case"), exist_ok=True)
    flip = lambda m: m.mirror((0, 0, 1)).translate((0, 0, H))      # top down, for printing
    C.stl(flip(C.real(sh)) if False else sh.mirror((0, 0, 1)).translate((0, 0, H)), os.path.join(HERE, "case", "shell.stl"))
    C.stl(plate.translate((0, 0, -M.FEET)), os.path.join(HERE, "case", "bottom_plate.stl"))
    os.makedirs(os.path.join(HERE, "..", C.STLS), exist_ok=True)
    for name in ("shell", "bottom_plate"):          # and the repo's STL folder
        shutil.copyfile(os.path.join(HERE, "case", name + ".stl"),
                        os.path.join(HERE, "..", C.STLS, "trackpad_" + name + ".stl"))
    json.dump(dict(layout={k: v for k, v in L.items()}, height=H, posts=posts, feet=M.feet_spots(),
                   wiring=wiring()), open(os.path.join(HERE, "design.json"), "w"), indent=1,
              default=lambda o: [float(v) for v in o])
    return L, sh, plate, ps


if __name__ == "__main__":
    main()
