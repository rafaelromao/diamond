"""Writes trackball.pretty: the Slim Diamond Trackball's footprints (one board, two parts).

The main board carries MX / Choc v1 alternative hot-swap sockets and a power switch. The
nice!nano is mounted separately and wired to labelled pads. The sensor board's parts all sit
on its back face, which faces the plate, so the PMW3610's lens looks up at the ball: those
footprints are drawn already on the back face (x mirrored, B layers).

The PMW3610 footprint follows siderakb's pmw3610-pcb (CERN-OHL-P-2.0): sixteen through-hole pins in
two staggered rows, the sensor's body in a cut-out, the optical centre 2.988 mm off its origin. The
MX hot-swap pads are Kailh's CPG151101S11 as in the usual open libraries; the 0805 and SOT-23-5
pads are KiCad's (hand-soldering sizes, as siderakb's board uses).
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import footprints as F                     # the Slim Diamond's helpers

F.OUT = os.path.join(HERE, "trackball.pretty")
B = ["B.Cu", "B.Mask", "B.Paste"]
FR = ["F.Cu", "F.Mask", "F.Paste"]

NANO_ROW1 = 4.0              # first pin row from the USB end (trackball.py's NANO_ROW1)
NANO_L, NANO_W = 33.3, 18.0
# Seen from above the main board, the nice!nano hangs face down: its two columns swap sides.
NANO_LEFT = ["B+", "GND", "RST", "VCC", "P0.31", "P0.29", "P0.02", "P1.15", "P1.13", "P1.11", "P0.10", "P0.09"]
NANO_RIGHT = ["P0.06", "P0.08", "GND", "GND", "P0.17", "P0.20", "P0.22", "P0.24", "P1.00", "P0.11", "P1.04", "P1.06"]

PMW_TOP = [(1, 6.168), (2, 4.388), (3, 2.608), (4, 0.828), (5, -0.952), (6, -2.732), (7, -4.512), (8, -6.292)]
PMW_BOT = [(9, -7.182), (10, -5.402), (11, -3.622), (12, -1.842), (13, -0.062), (14, 1.718), (15, 3.498), (16, 5.278)]


def mx_hotswap():
    """MX switch from the front, Kailh hot-swap socket on the back."""
    L = F.header("SW_MX_Hotswap", "MX switch, Kailh CPG151101S11 hot-swap socket on the back face")
    L += [F.npth(0, 0, 4.0), F.npth(-5.08, 0, 1.75), F.npth(5.08, 0, 1.75),
          F.npth(-3.81, -2.54, 3.0), F.npth(2.54, -5.08, 3.0)]
    L.append(F.smd("1", -7.085, -2.54, 2.55, 2.5, B))
    L.append(F.smd("2", 5.842, -5.08, 2.55, 2.5, B))
    L += F.rect_lines(-7.0, -7.0, 7.0, 7.0, "F.Fab", 0.1)
    L += F.rect_lines(-9.0, -9.0, 9.0, 9.0, "Dwgs.User", 0.1)        # keycap
    L += F.rect_lines(-8.6, -7.5, 7.4, -0.9, "B.CrtYd", 0.05)
    L += F.rect_lines(-7.3, -7.3, 7.3, 7.3, "F.CrtYd", 0.05)
    F.write("SW_MX_Hotswap", L)


def mx_choc_hotswap():
    """Alternative sockets, never both populated. Choc v1 is rotated 180° relative to MX.
    Choc pad geometry follows kiswitch (MIT), as in the keyboard's footprint generator.
    Merged peg slots accept both families without overlapping drill hits.
    """
    L = F.header("SW_MX_Choc_V1_Hotswap", "MX / Choc v1 alternative back-face hot-swap sockets; Choc reversed")
    L.append(F.npth(0, 0, 4.0))
    for x in (-5.29, 5.29):
        L.append(f'  (pad "" np_thru_hole oval (at {x} 0) (size 2.32 1.9) (drill oval 2.32 1.9) (layers "*.Cu" "*.Mask"))')
    for x, y in ((-3.81, -2.54), (2.54, -5.08)):
        L.append(F.npth(x, y, 3.0))
    for x, y in ((0, 5.9), (-5, 3.8)):
        L.append(F.npth(x, y, 3.05))
    for num, x, y, w, h in (("1", -7.085, -2.54, 2.55, 2.5), ("2", 5.842, -5.08, 2.55, 2.5),
                            ("1", 3.5, 6.0, 2.6, 2.5), ("2", -8.5, 3.8, 2.55, 2.5)):
        L.append(F.smd(num, x, y, w, h, B))
    L += F.rect_lines(-7.3, -7.3, 7.3, 7.3, "F.CrtYd", 0.05)
    L += F.rect_lines(-9.8, -8.5, 8.6, 8.5, "B.CrtYd", 0.05)
    L += F.rect_lines(-7.0, -7.0, 7.0, 7.0, "F.Fab", 0.1)
    F.write("SW_MX_Choc_V1_Hotswap", L)


def nice_nano():
    """nice!nano hanging face down under the board on bare pins, USB end at -y."""
    L = F.header("NiceNano_FaceDown", "nice!nano v2 face down under the board, USB end at -y", attr="through_hole")
    # pads numbered 1-12 down the left column, 13-24 down the right (seen from above), so the
    # router reads them: names like "B+" or "P0.17" trip its parser. NANO_LEFT / NANO_RIGHT name them.
    for i in range(12):
        y = -NANO_L / 2 + NANO_ROW1 + i * 2.54
        L.append(F.tht(str(i + 1), -7.62, y, 1.7, 1.0, shape="rect" if i == 0 else "circle"))
        L.append(F.tht(str(i + 13), 7.62, y, 1.7, 1.0))
    # no courtyard: it hangs below the sockets, so it can't meet the parts over it
    L += F.rect_lines(-NANO_W / 2, -NANO_L / 2, NANO_W / 2, NANO_L / 2, "B.Fab", 0.1)
    L.append(F.text("USB", 0, -NANO_L / 2 + 1.5, "B.SilkS", 1.0, mirror=True))
    for i, n in enumerate(NANO_LEFT):
        if n in ("B+", "RST", "VCC"):
            L.append(F.text(n, -4.9, -NANO_L / 2 + NANO_ROW1 + i * 2.54, "F.SilkS", 1.0))
    F.write("NiceNano_FaceDown", L)


def pmw3610_back():
    """PMW3610 on the board's back face (its lens on the front, looking up), origin as siderakb's,
    x mirrored. The optical centre is at (-2.988, 0)."""
    L = F.header("PMW3610_Back", "PixArt PMW3610DM-SUDU on the back face, LM18-LSI lens on the front; "
                 "after siderakb/pmw3610-pcb (CERN-OHL-P-2.0)", attr="through_hole")
    for num, x in PMW_TOP:
        L.append(F.tht(str(num), -x, -5.35, 1.25, 0.75, shape="rect" if num == 1 else "circle"))
    for num, x in PMW_BOT:
        L.append(F.tht(str(num), -x, 5.35, 1.25, 0.75))
    # the cut-out the sensor's body sits in (on Edge.Cuts, part of the board's outline)
    x0, x1 = -8.948, 8.252
    L += F.rect_lines(x0, -4.35, x1, 4.35, "Edge.Cuts", 0.1)
    L += F.rect_lines(x0 - 0.5, -6.6, x1 + 0.5, 6.6, "B.CrtYd", 0.05)
    L.append(F.line(-6.9, -6.3, -6.2, -6.3, "B.SilkS"))                # pin 1
    L.append(F.line(-2.988 - 1, 0, -2.988 + 1, 0, "Dwgs.User", 0.1))  # optical centre
    L.append(F.line(-2.988, -1, -2.988, 1, "Dwgs.User", 0.1))
    F.write("PMW3610_Back", L)


def c0805(name, layers, mirror):
    s = -1 if mirror else 1
    L = F.header(name, "0805 (hand soldering), %s face" % ("back" if mirror else "front"))
    L.append(F.smd("1", -0.95 * s, 0, 1.0, 1.45, layers))
    L.append(F.smd("2", 0.95 * s, 0, 1.0, 1.45, layers))
    side = "B" if mirror else "F"
    L += F.rect_lines(-1.7, -1.0, 1.7, 1.0, f"{side}.CrtYd", 0.05)
    L += F.rect_lines(-1.0, -0.62, 1.0, 0.62, f"{side}.Fab", 0.1)
    F.write(name, L)


def sot23_5_back():
    L = F.header("SOT-23-5_Back", "SOT-23-5 (hand soldering) on the back face")
    pads = [("1", -1.35, -0.95), ("2", -1.35, 0), ("3", -1.35, 0.95), ("4", 1.35, 0.95), ("5", 1.35, -0.95)]
    for num, x, y in pads:
        L.append(F.smd(num, -x, y, 1.56, 0.65, B))
    L += F.rect_lines(-2.4, -1.75, 2.4, 1.75, "B.CrtYd", 0.05)
    L += F.rect_lines(-0.8, -1.45, 0.8, 1.45, "B.Fab", 0.1)
    L.append(F.line(1.9, -1.6, 1.4, -1.6, "B.SilkS"))                # pin 1 (mirrored: at +x)
    F.write("SOT-23-5_Back", L)


def power_switch_front():
    pads = [("1", -2.25, -1.95, 0.7, 1.5), ("2", 0.75, -1.95, 0.7, 1.5), ("3", 2.25, -1.95, 0.7, 1.5),
            ("SH", -3.675, -1.1, 1.05, 0.7), ("SH", -3.675, 1.1, 1.05, 0.7),
            ("SH", 3.675, -1.1, 1.05, 0.7), ("SH", 3.675, 1.1, 1.05, 0.7)]
    L = F.header("SW_MSK12C02", "Shouhan MSK-12C02 slide switch, lever at +y")
    L += [F.npth(-1.5, 0, 0.9), F.npth(1.5, 0, 0.9)]
    for num, x, y, w, h in pads:
        L.append(F.smd(num, x, y, w, h, FR))
    L += F.rect_lines(-3.35, -1.35, 3.35, 1.35, "F.Fab", 0.1)
    L += F.rect_lines(-4.4, -2.9, 4.4, 3.4, "F.CrtYd", 0.05)
    L.append(F.text("ON", -3.0, 3.0, "F.SilkS", 1.0))
    F.write("SW_MSK12C02", L)


def reset_back():
    """TS-1187A on the back face, plunger at the origin: pads 1 (RST) and 2 (GND)."""
    L = F.header("SW_TS1187A_Back", "XKB TS-1187A 5.1 x 5.1 mm tact switch on the back face")
    for sx in (-1, 1):
        L.append(F.smd("1", sx * 3.15, -1.9, 1.7, 1.0, B, shape="rect"))
        L.append(F.smd("2", sx * 3.15, 1.9, 1.7, 1.0, B, shape="rect"))
    L += F.rect_lines(-2.55, -2.55, 2.55, 2.55, "B.Fab", 0.1)
    L += F.rect_lines(-4.25, -3.0, 4.25, 3.0, "B.CrtYd", 0.05)
    L.append(F.text("RST", 0, -3.85, "B.SilkS", 1.0, mirror=True))
    F.write("SW_TS1187A_Back", L)


def wire_pad():
    L = F.header("WirePad", "Through-hole pad for a wire", attr="through_hole")
    L.append(F.tht("1", 0, 0, 1.7, 1.0))
    F.write("WirePad", L)


def mount_hole():
    L = F.header("MountingHole_M2", "M2 screw hole", attr="exclude_from_pos_files exclude_from_bom")
    L.append(F.npth(0, 0, 2.2))
    F.write("MountingHole_M2", L)


def bite():
    L = F.header("MouseBite", "Breakaway tab hole", attr="exclude_from_pos_files exclude_from_bom")
    L.append(F.npth(0, 0, 0.5))
    F.write("MouseBite", L)


if __name__ == "__main__":
    os.makedirs(F.OUT, exist_ok=True)
    mx_hotswap()
    mx_choc_hotswap()
    nice_nano()
    pmw3610_back()
    c0805("C_0805_Back", B, True)
    sot23_5_back()
    power_switch_front()
    reset_back()
    wire_pad()
    mount_hole()
    bite()
    print(sorted(os.listdir(F.OUT)))
