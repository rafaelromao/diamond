"""Wiring diagrams: the controller board seen from above, with one controller on it.

Pads and pins come from design.json and controller_pinout.py, the tables the tests check against the
firmware shields. Run from slim_diamond/: python3 trackball/controller_diagram.py
  nice!nano v2: https://nicekeyboards.com/docs/nice-nano/pinout-schematic
  XIAO nRF52840: https://wiki.seeedstudio.com/XIAO_BLE/#hardware-overview
"""
import json
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Polygon, Rectangle

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from controller_pinout import HEADER, PADS, PINS

D = json.load(open(os.path.join(HERE, "design.json")))
TITLE = {"xiao": "Plain XIAO nRF52840", "nice_nano": "nice!nano v2"}
NOTE = {
    "xiao": "Jumper: bridge 3V to X.\n"
            "Two wires, from the pads on the XIAO's back: BAT+ to the main board's VBAT, reset to R2.\n"
            "Leave 5V empty.",
    "nice_nano": "Jumper: bridge 3V to N.\n"
                 "Two wires: B+ to the main board's VBAT, RST to R2.\n"
                 "Never wire the cell straight to B+: that would bypass the power switch.",
}
GOLD, GREY, RED = "#e0b020", "#8a8f94", "#c8102e"


def draw(controller, path):
    """In the module's plan, not the panel's: the board lies a quarter turn round there."""
    P = D["controller_plan"]
    fig, ax = plt.subplots(figsize=(9.4, 8.2), dpi=120)
    ax.add_patch(Polygon(P["outline"], fc="#2e6b45", ec="#17382a", lw=1.2, zorder=1))
    row = lambda r: P["pins"]["L3"][1] - (r - 3) * 2.54
    # the controller's outline, drawn thin: it lies over the board and on past its front
    length = 20.955 if controller == "xiao" else 26.0    # a nice!nano runs on past the drawing's edge
    ax.add_patch(Rectangle((-9, row(1) + 3.4 - length), 18, length, fc="none", ec="#222", ls="--", lw=1, zorder=2))
    ax.text(0, row(1) + 2.2, "USB-C, rear", ha="center", fontsize=9)
    for column, sign in (("left", -1), ("right", 1)):
        for r, name in enumerate(PINS[controller][column], 1):
            x, y = sign * 7.62, row(r)
            used = HEADER[column].get(r) is not None
            ax.add_patch(Circle((x, y), .55, fc=GOLD if used else "white", ec="#333", zorder=4))
            ax.text(x - sign * 1.1, y, name, ha="right" if sign > 0 else "left", va="center", fontsize=10, zorder=6,
                    fontweight="bold" if used else "normal", color="#111" if used else GREY,
                    bbox=dict(fc="white", ec="none", pad=1.2))
    names = dict(NCS="CS", SCLK="CK", SDIO="IO", MOTION="MO", VCC="3V", GND="G")
    for link in P["links"].values():
        x, y = link["xy"]
        ax.add_patch(Circle((x, y), .7, fc="#7fd0f0", ec="#333", zorder=4))
        ax.text(x + (1.0 if x > 0 else -1.0), y, names.get(link["net"], link["net"]), ha="left" if x > 0 else "right",
                va="center", fontsize=9, color="#111", fontweight="bold", zorder=6, bbox=dict(fc="white", ec="none", pad=.8))
    # the jumper, with the bridge to make
    x, y = P["jumper"]
    for dx in (-1.3, 0, 1.3):
        ax.add_patch(Rectangle((x + dx - .5, y - .8), 1, 1.6, fc=GOLD, ec="#333", zorder=4))
    bridge = (-1.3, 0) if controller == "xiao" else (0, 1.3)
    ax.plot([x + bridge[0], x + bridge[1]], [y, y], color=RED, lw=5, solid_capstyle="round", zorder=5)
    for dx, name in ((-1.3, "X"), (0, "3V"), (1.3, "N")):
        ax.text(x + dx, y - 1.5, name, ha="center", color="white", fontsize=9)
    # where the two wires start
    if controller == "nice_nano":
        for r, name in ((1, "B+"), (3, "RST")):
            ax.add_patch(Circle((-7.62, row(r)), .85, fc="none", ec=RED, lw=2.2, zorder=6))
    else:
        for px, py, name, dy, colour in ((4.455, row(4) + .315, "BAT+ (back)", -1.2, "white"),
                                         (1.28, row(4) + 6.03, "reset (back)", 1.2, "#111")):
            ax.add_patch(Circle((px, py), .75, fc="none", ec=RED, lw=2.2, zorder=6))
            ax.text(px, py + dy, name, ha="center", va="top" if dy < 0 else "bottom", fontsize=8, color=colour, zorder=6)
    ax.set_title(f"{TITLE[controller]} on the controller board, seen from above, rear at the top.\n"
                 "Gold pins join the board; white ones are unused. Blue pins join the main board. Red rings: the two wires start here.",
                 fontsize=10.5)
    ax.text(0, row(8) - 7.0, NOTE[controller], ha="center", va="top", fontsize=10.5)
    ax.set_xlim(-18, 18)
    ax.set_ylim(row(8) - 13, row(1) + 5)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close(fig)


if __name__ == "__main__":
    root = os.path.join(HERE, "..", "renders")
    draw("xiao", os.path.join(root, "wiring_xiao.png"))
    draw("nice_nano", os.path.join(root, "wiring_nice_nano.png"))
    print("wiring_xiao.png, wiring_nice_nano.png")
