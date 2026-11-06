"""Wiring diagrams at true position: the carrier seen from above, the controller under it.

Pads come from design.json and pins from controller_pinout.py, the table the tests check against
the firmware shields. Run from slim_diamond/: python3 trackball/controller_diagram.py
Pin order follows the manufacturers' top views, turned over: the controllers hang face down.
  nice!nano v2: https://nicekeyboards.com/docs/nice-nano/pinout-schematic
  XIAO nRF52840: https://wiki.seeedstudio.com/XIAO_BLE/#hardware-overview
"""
import json
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Rectangle

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from controller_pinout import PADS
from controllers import XIAO_LENGTH, XIAO_USB_OVERHANG, XIAO_WIDTH

D = json.load(open(os.path.join(HERE, "design.json")))
BACK = -D["back"] if D["back"] < 0 else D["back"]
# Top views, USB end first: (column on the pin's left, column on its right). Face down, the first
# lands on the carrier's +x side.
PINS = {
    "xiao": (["D0", "D1", "D2", "D3", "D4", "D5", "D6"],
             ["5V", "GND", "3V3", "D10", "D9", "D8", "D7"]),
    "nice_nano": (["GND", "D1", "D0", "GND", "GND", "D2", "D3", "D4", "D5", "D6", "D7", "D8", "D9"],
                  ["B+", "B+", "GND", "RST", "VCC", "D21", "D20", "D19", "D18", "D15", "D14", "D16", "D10"]),
}
POWER = {"xiao": dict(G="GND", **{"3V": "3V3"}), "nice_nano": dict(VBAT="B+", G="GND", RST="RST", **{"3V": "VCC"})}
TITLE = {"xiao": "Plain XIAO nRF52840", "nice_nano": "nice!nano v2"}
# Seeed's footprint pads as they lie here, from the module's centre: already turned over.
BACK_PADS = dict(VBAT=(4.455, -.315), RST=(1.28, -6.03))
UNDER = {"xiao": "BAT+ and RST are pads on the XIAO's back, the side facing the carrier: solder those two wires first,\nand keep them flat, not crossing, off to the rear of the sockets. Leave 5V empty.",
         "nice_nano": "Wire the battery to the carrier's + and - pads, never to B+: that would bypass the power switch.\nExcept VBAT and G, each wire runs one row or more along the board: follow the names, not the rows."}


def geometry(controller):
    if controller == "xiao":
        rear = BACK + XIAO_USB_OVERHANG
        return rear, rear + XIAO_LENGTH, XIAO_WIDTH, rear + XIAO_LENGTH / 2 - 7.62, 8.89
    rear = BACK + .6
    return rear, rear + 33.3, 18.0, rear + 4.0 - 2.54, 7.62    # the first row is the extra GND / B+ pair


def pad_names():
    names = ["CK", "IO", "CS", "MO", "RST", "3V", "G"]
    out = dict(zip(names, D["wire_pads"]))
    out.update(zip(["VBAT", "K1", "K2"], D["controller_pads"]))
    return out


def draw(controller, path):
    rear, front, width, first, column_x = geometry(controller)
    fig, ax = plt.subplots(figsize=(9, 11), dpi=120)
    ax.add_patch(Polygon(D["main_board"], fc="#d9dfd2", ec="#46604f", lw=1.2, zorder=1))
    ax.add_patch(Rectangle((-width / 2, rear), width, front - rear, fc="#27313a", ec="#111", alpha=.92, zorder=2))
    ax.add_patch(Rectangle((-4.5, BACK), 9, 7.3, fc="#aab0b6", ec="#444", zorder=3))
    ax.text(0, BACK + 3.6, "USB-C", ha="center", va="center", fontsize=8, zorder=4)
    plus, minus = D["battery_pads"]
    pins = {}
    for sign, names in ((1, PINS[controller][0]), (-1, PINS[controller][1])):
        for i, name in enumerate(names):
            y = first + i * 2.54
            pins.setdefault(name, []).append((sign * column_x, y))
            ax.plot([sign * column_x], [y], "o", ms=4.5, color="#c9ccd0", zorder=4)
            ax.text(sign * (column_x - (2.3 if controller == "xiao" else 1.0)), y, name, ha="left" if sign < 0 else "right", va="center",
                    fontsize=7, color="#f2f2f2", zorder=4)
    links = dict(PADS[controller], **POWER[controller])
    middle = rear + (front - rear) / 2
    if controller == "xiao":
        for pad, (x, y) in BACK_PADS.items():
            pins[pad] = [(x, middle + y)]
            links[pad] = pad
            ax.text(x, middle + y + .9, "BAT+" if pad == "VBAT" else "RST", ha="center", fontsize=7, color="#ffd27a", zorder=8)
    for pad, (x, y) in pad_names().items():
        ax.plot([x], [y], "o", ms=9, mfc="#e0b020", mec="#6b5200", zorder=6)
        ax.text(x + (1.1 if x > 0 else -1.1), y, pad, ha="left" if x > 0 else "right", va="center", fontsize=8.5,
                fontweight="bold", zorder=7)
        if pad in links:
            name = links[pad]
            px, py = min(pins[name], key=lambda q: (q[0] - x) ** 2 + (q[1] - y) ** 2)
            ax.plot([x, px], [y, py], color="#c8102e", lw=1.6, zorder=5)
            ax.plot([px], [py], "o", ms=5, color="#e0b020", zorder=5)
    for (x, y), name in ((plus, "+ battery"), (minus, "- battery")):
        ax.plot([x], [y], "o", ms=9, mfc="#e0b020", mec="#6b5200", zorder=6)
        ax.text(x - 1.1, y, name, ha="right", va="center", fontsize=8.5, fontweight="bold")
    ax.set_title(TITLE[controller] + " under the carrier, seen from above through the board.\n"
                 "Rear at the top. Red: the wire from each pad to its pin.\n" + UNDER[controller], fontsize=10)
    ax.set_xlim(-23, 23)
    ax.set_ylim(70, 12)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close(fig)


if __name__ == "__main__":
    root = os.path.join(HERE, "..", "renders")
    draw("xiao", os.path.join(root, "wiring_xiao.png"))
    draw("nice_nano", os.path.join(root, "wiring_nice_nano.png"))
    print("wiring_xiao.png, wiring_nice_nano.png")
