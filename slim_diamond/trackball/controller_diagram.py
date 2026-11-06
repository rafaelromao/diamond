"""Wiring diagrams: which carrier pad goes to which pin of each controller.

Drawn from controller_pinout.py, the table the tests check against the firmware shields, so the
pictures cannot drift from the wiring. Run from slim_diamond/: python3 trackball/controller_diagram.py
Pin order follows the manufacturers' top views (components up, USB up):
  nice!nano v2: https://nicekeyboards.com/docs/nice-nano/pinout-schematic
  XIAO nRF52840: https://wiki.seeedstudio.com/XIAO_BLE/#hardware-overview
"""
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from controller_pinout import GPIO, SIGNALS

# The carrier's pad labels (silkscreen), by signal.
PADS = {
    "trackball": dict(SCLK="CK", SDIO="IO", NCS="CS", MOTION="MO", K1="K1", K2="K2"),
    "trackpad": dict(SDA="breakout SDA", SCL="breakout SCL", DR="Cirque DR (underside)", K1="K1", K2="K2"),
}
# (left column, right column), top to bottom, USB up, components up.
LAYOUT = {
    "xiao": (["D0", "D1", "D2", "D3", "D4", "D5", "D6"],
             ["5V", "GND", "3V3", "D10", "D9", "D8", "D7"]),
    "nice_nano": (["GND", "D1", "D0", "GND", "GND", "D2", "D3", "D4", "D5", "D6", "D7", "D8", "D9"],
                  ["B+", "B+", "GND", "RST", "3V3", "D21", "D20", "D19", "D18", "D15", "D14", "D16", "D10"]),
}
POWER = {   # pin label -> text; the same on both modules
    "xiao": {"GND": "G pad (and breakout GND)", "3V3": "3V pad (and breakout VDD)"},
    "nice_nano": {"GND": "G pad (and breakout GND)", "3V3": "3V pad (and breakout VDD)",
                  "B+": "VBAT pad", "RST": "RST pad"},
}
VIEW = "Seen from the component side, USB up. The board hangs face down under the carrier, so it is mirrored there: wire by name."
NOTES = {
    "xiao": ["Underside pads (see Seeed's back view): BAT+ -> VBAT pad, BAT- (with GND) -> G pad,",
             "RESET (P0.18) -> RST pad. The battery itself goes to the carrier's + and - pads."],
    "nice_nano": ["Either B+ pad serves for VBAT, any one GND pin for G; the 3.3 V pin is labelled VCC on the board.",
                  "The battery itself goes to the carrier's + and - pads."],
}
TITLE = {"xiao": "Plain Seeed XIAO nRF52840", "nice_nano": "nice!nano v2"}
GOLD, GREY = "#e0b020", "#c9ccd0"


def uses(controller):
    out = {}
    for kind, controllers in SIGNALS.items():
        for signal, pin in controllers[controller].items():
            out.setdefault(pin, []).append((kind, PADS[kind][signal]))
    return out


def label(pin, controller):
    if pin in GPIO[controller]:
        port, n = GPIO[controller][pin]
        return f"{pin}  P{port}.{n:02d}"
    return pin


def draw(controller, path):
    left, right = LAYOUT[controller]
    rows = max(len(left), len(right))
    used = uses(controller)
    pitch = 1.0
    width = 7.0
    fig_h = 1.25 * rows * 0.5 + 3.0
    fig, ax = plt.subplots(figsize=(13, fig_h), dpi=130)
    top = rows * pitch
    ax.add_patch(FancyBboxPatch((-width / 2, -0.8), width, top + 1.9, boxstyle="round,pad=0.1,rounding_size=0.5",
                                fc="#27313a", ec="#111", zorder=1))
    ax.add_patch(Rectangle((-1.5, top + 0.3), 3.0, 1.0, fc="#aab0b6", ec="#555", zorder=2))
    ax.text(0, top + 0.8, "USB-C", ha="center", va="center", fontsize=9, zorder=3)

    seen = set()

    def column(names, x, side):
        for i, name in enumerate(names):
            y = top - i * pitch - 0.5
            connections = []
            if name in used:
                connections = [f"{kind}: {pad}" for kind, pad in used[name]]
            elif name in POWER[controller] and name != "5V" and name not in seen:
                connections = [POWER[controller][name]]    # a repeated pin (GND, B+) is wired once
                seen.add(name)
            hot = bool(connections)
            ax.add_patch(Rectangle((x - 0.2, y - 0.2), 0.4, 0.4, fc=GOLD if hot else GREY, ec="#222", zorder=3))
            inner = x + (0.45 if side < 0 else -0.45)
            ax.text(inner, y, label(name, controller), ha="left" if side < 0 else "right", va="center",
                    fontsize=8.5, color="#f2f2f2" if hot else "#8e979f", zorder=3)
            if connections:
                outer = x + side * 0.4
                ax.plot([outer, x + side * 1.2], [y, y], color="#333", lw=0.8, zorder=2)
                ax.text(x + side * 1.3, y, "   |   ".join(connections), ha="left" if side > 0 else "right",
                        va="center", fontsize=9.5, fontweight="bold", color="#14301f")

    column(left, -width / 2 + 0.5, -1)
    column(right, width / 2 - 0.5, +1)
    for i, line in enumerate([VIEW] + NOTES[controller]):
        ax.text(0, -1.5 - 0.55 * i, line, ha="center", va="center", fontsize=9)
    ax.set_title(f"{TITLE[controller]}: which pin goes to which carrier pad (gold = wired)", fontsize=12, pad=12)
    ax.set_xlim(-12.5, 12.5)
    ax.set_ylim(-3.4, top + 2.0)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close(fig)


if __name__ == "__main__":
    root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "renders")
    draw("xiao", os.path.join(root, "wiring_xiao.png"))
    draw("nice_nano", os.path.join(root, "wiring_nice_nano.png"))
    print("wiring_xiao.png, wiring_nice_nano.png")
