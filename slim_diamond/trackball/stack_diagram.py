"""How the controller board's stacking pins meet the main board, in the module, from the routed PCB.

On the panel the controller board lies a quarter turn round; here it is where it sits in the module,
under the main board. Hole positions come from trackball/pcb/stack_alignment.json, which
check_controller_pcb.py writes from the routed board after undoing the panel's turn and offset.
Run from slim_diamond/: python3 trackball/stack_diagram.py
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
import trackball as B                       # trackball/trackball.py, beside this file

D = json.load(open(os.path.join(HERE, "design.json")))
A = json.load(open(os.path.join(HERE, "pcb", "stack_alignment.json")))
NAMES = dict(NCS="CS", SCLK="CK", SDIO="IO", MOTION="MO", VCC="3V", GND="GND")
MAIN, CTRL, PLASTIC, PIN = "#8a9a5b", "#2e6b45", "#222", "#b8b8bc"


def plan(ax):
    ax.add_patch(Polygon([(x, -y) for x, y in D["main_board"]], fc=MAIN, ec="#4a5530", alpha=.35, lw=1.2, zorder=1))
    ax.add_patch(Polygon(D["controller_plan"]["outline"], fc=CTRL, ec="#17382a", alpha=.75, lw=1.2, zorder=2))
    ax.add_patch(Rectangle((-8.89, -14.35 - .2155 - 1.527 - 20.955), 17.78, 20.955, fc="none", ec="#333",
                           ls="--", lw=1, zorder=3))
    ax.text(0, -16.9, "controller's USB-C, rear", ha="center", fontsize=8)
    for name, p in A["pairs"].items():
        (mx, my), (cx, cy) = p["main"], p["controller"]
        ax.add_patch(Circle((mx, my), .85, fc="none", ec="#c8102e", lw=2, zorder=5))      # the main board's pad
        ax.add_patch(Circle((cx, cy), .32, fc="#1e5bd8", ec="none", zorder=6))            # the controller board's pin
        side = 1 if mx > 0 else -1
        ax.text(mx + side * 1.3, my, "%s  %.3f mm" % (NAMES.get(p["net"], p["net"]), p["offset"]),
                ha="left" if side > 0 else "right", va="center", fontsize=8.5, fontweight="bold", zorder=7,
                bbox=dict(fc="white", ec="none", pad=.6))
    for name, (x, y) in A["header"].items():
        ax.add_patch(Circle((x, y), .3, fc="#e0b020", ec="#333", lw=.5, zorder=4))
    ax.set_title("From above, in the module. Red rings: the main board's stacking holes.\n"
                 "Blue dots: the controller board's, from the same routed PCB. Numbers: how far apart.", fontsize=10)
    ax.set_xlim(-21, 21)
    ax.set_ylim(-45, -13)
    ax.set_aspect("equal")
    ax.axis("off")


def side(ax):
    """Section across the module at row 6, looking from the front, to scale."""
    top = B.controller_top()
    under = B.PCB_TOP - B.PCB_T
    face = top + B.HEADER_T
    rows = [
        ((-13, under, 26, B.PCB_T), MAIN, "main board"),
        ((-8.95, top - B.CB_T, 17.9, B.CB_T), CTRL, "controller board"),
        ((-8.89, face, 17.78, 1.25), "#1d4f9c", "controller, face down"),
        ((-7.35, B.SOCKET_BOT, 6.0, under - B.SOCKET_BOT), "#555", "MX socket"),
    ]
    for (x, z, w, h), colour, label in rows:
        ax.add_patch(Rectangle((x, z), w, h, fc=colour, ec="#111", lw=.6, alpha=.85))
    ax.text(-12.6, under + .8, "main board", va="center", fontsize=8, color="white")
    ax.text(0, top - .8, "controller board", ha="center", va="center", fontsize=8, color="white")
    ax.text(0, face + .62, "controller, face down", ha="center", va="center", fontsize=8, color="white")
    ax.text(-4.35, (B.SOCKET_BOT + under) / 2, "socket", ha="center", va="center", fontsize=7, color="white")
    for s in (-1, 1):
        x = s * B.LINK_X[6]
        ax.add_patch(Rectangle((x - 1.27, under - B.LINK_GAP - B.HEADER_T), 2.54, B.HEADER_T, fc=PLASTIC))
        ax.add_patch(Rectangle((x - .32, top - B.CB_T - 1.0), .64, B.PCB_TOP + .6 - (top - B.CB_T - 1.0), fc=PIN, ec="#555", lw=.4))
        hx = s * 7.62
        ax.add_patch(Rectangle((hx - 1.27, top), 2.54, B.HEADER_T, fc=PLASTIC))
        ax.add_patch(Rectangle((hx - .32, top - B.CB_T - 1.0), .64, face + 1.25 + .6 - (top - B.CB_T - 1.0), fc=PIN, ec="#555", lw=.4))
    ax.annotate("stacking pin", (B.LINK_X[6], under - 3.5), (15.5, under - 3.5), fontsize=8, va="center",
                arrowprops=dict(arrowstyle="-", lw=.6))
    ax.annotate("its plastic", (B.LINK_X[6] + 1.27, under - 1.5), (15.5, under - 1.5), fontsize=8, va="center",
                arrowprops=dict(arrowstyle="-", lw=.6))
    ax.annotate("header under\nthe controller", (8.89, top + 1.3), (15.5, top + 1.0), fontsize=8, va="center",
                arrowprops=dict(arrowstyle="-", lw=.6))
    ax.set_title("Across the module at row 6, from the front, to scale (mm)", fontsize=10)
    ax.set_xlim(-15, 22)
    ax.set_ylim(top - B.CB_T - 2, B.PCB_TOP + 1.5)
    ax.set_aspect("equal")
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    ax.set_ylabel("height over the standing plane")


if __name__ == "__main__":
    fig = plt.figure(figsize=(10, 12.5), dpi=120)
    plan(fig.add_axes([0.03, 0.36, 0.94, 0.62]))
    side(fig.add_axes([0.08, 0.03, 0.86, 0.3]))
    fig.savefig(os.path.join(HERE, "..", "renders", "stack_alignment.png"), facecolor="white")
    print("stack_alignment.png, worst offset %.4f mm" % max(p["offset"] for p in A["pairs"].values()))
