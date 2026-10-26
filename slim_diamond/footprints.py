"""Writes slim_diamond.pretty: the reversible footprints of the Slim Diamond.

Every footprint carries its parts on both faces. The left half is built with
the parts on the bottom (B) face, the right half with the board turned over,
so the parts go on the F face. Only one face gets populated.

The Choc hot-swap geometry follows kiswitch's SW_Hotswap_Kailh_Choc_V1 (MIT);
the Xiao pad positions follow Seeed's XIAO-nRF52840-SMD footprint; the reset
button's pads follow KiCad's Button_Switch_SMD:SW_SPST_TL3342 (CC-BY-SA 4.0).
"""
import json
import os

from shapely.geometry import Point, box

OUT = "slim_diamond.pretty"
VERSION = "20241229"


def fmt(v):
    return f"{v:.4f}".rstrip("0").rstrip(".")


def mirror_layers(layers):
    return [l.replace("F.", "@").replace("B.", "F.").replace("@", "B.") for l in layers]


def header(name, descr, attr="smd"):
    return [f'(footprint "{name}"', f'  (version {VERSION})', '  (generator "slim_diamond")',
            '  (layer "F.Cu")', f'  (descr "{descr}")',
            '  (property "Reference" "REF**" (at 0 0 0) (layer "F.SilkS") hide'
            ' (effects (font (size 1 1) (thickness 0.15))))',
            f'  (property "Value" "{name}" (at 0 0 0) (layer "F.Fab") hide'
            ' (effects (font (size 1 1) (thickness 0.15))))',
            f'  (attr {attr})']


def line(x1, y1, x2, y2, layer, w=0.15):     # 0.15: JLCPCB's thinnest silkscreen line
    return (f'  (fp_line (start {fmt(x1)} {fmt(y1)}) (end {fmt(x2)} {fmt(y2)})'
            f' (stroke (width {w}) (type solid)) (layer "{layer}"))')


def rect_lines(x1, y1, x2, y2, layer, w=0.15):
    return [line(x1, y1, x2, y1, layer, w), line(x2, y1, x2, y2, layer, w),
            line(x2, y2, x1, y2, layer, w), line(x1, y2, x1, y1, layer, w)]


def text(s, x, y, layer, size=1.0, mirror=False):    # JLCPCB: text 1.0 high, 0.15 stroke
    j = " (justify mirror)" if mirror else ""
    return (f'  (fp_text user "{s}" (at {fmt(x)} {fmt(y)} 0) (layer "{layer}")'
            f' (effects (font (size {size} {size}) (thickness 0.15)){j}))')


def smd(num, x, y, w, h, layers, shape="roundrect", rot=0):
    lay = " ".join(f'"{l}"' for l in layers)
    extra = " (roundrect_rratio 0.2)" if shape == "roundrect" else ""
    return (f'  (pad "{num}" smd {shape} (at {fmt(x)} {fmt(y)} {fmt(rot)}) (size {fmt(w)} {fmt(h)})'
            f' (layers {lay}){extra})')


def tht(num, x, y, size, drill, shape="circle", size_y=None, drill_y=None):
    sy = size if size_y is None else size_y
    dr = fmt(drill) if drill_y is None else f"oval {fmt(drill)} {fmt(drill_y)}"
    return (f'  (pad "{num}" thru_hole {shape} (at {fmt(x)} {fmt(y)}) (size {fmt(size)} {fmt(sy)})'
            f' (drill {dr}) (layers "*.Cu" "*.Mask"))')


def npth(x, y, d):
    return (f'  (pad "" np_thru_hole circle (at {fmt(x)} {fmt(y)}) (size {fmt(d)} {fmt(d)})'
            f' (drill {fmt(d)}) (layers "*.Cu" "*.Mask"))')


def custom(num, x, y, poly, layers):
    """Custom SMD pad; poly in footprint coordinates, anchored at (x, y)."""
    pts = " ".join(f"(xy {fmt(px - x)} {fmt(py - y)})" for px, py in poly)
    lay = " ".join(f'"{l}"' for l in layers)
    return (f'  (pad "{num}" smd custom (at {fmt(x)} {fmt(y)}) (size 0.5 0.5) (layers {lay})'
            f' (options (clearance outline) (anchor circle))'
            f' (primitives (gr_poly (pts {pts}) (width 0) (fill yes))))')


def model(path, offset=(0, 0, 0), rot=(0, 0, 0)):
    o = " ".join(fmt(v) for v in offset)
    r = " ".join(fmt(v) for v in rot)
    return (f'  (model "{path}" (offset (xyz {o})) (scale (xyz 1 1 1)) (rotate (xyz {r})))')


def write(name, lines):
    with open(os.path.join(OUT, name + ".kicad_mod"), "w") as f:
        f.write("\n".join(lines + [")"]) + "\n")


# ------------------------------------------------------------------------------------------
def choc():
    """Kailh Choc v1, hot-swap socket on either face.

    B face: the left half's socket, as kiswitch places it. F face: its mirror,
    for the right half (switch mounted from the B face). Both sockets share the
    switch-pin hole at (0, -5.9); the other pin hole is at (+5, -3.8) for B and
    (-5, -3.8) for F. Pad 1 is trimmed where it would run into the other
    face's pin hole.
    """
    L = header("SW_Choc_V1_Hotswap_Reversible",
               "Kailh Choc V1 (PG1350), hot-swap socket on either face, after kiswitch (MIT)")
    L += [npth(0, 0, 3.45), npth(-5.5, 0, 1.9), npth(5.5, 0, 1.9),
          npth(0, -5.9, 3.05), npth(5, -3.8, 3.05), npth(-5, -3.8, 3.05)]
    for side, sx in (("B", 1), ("F", -1)):
        layers = [f"{side}.Cu", f"{side}.Mask"]
        p1 = box(-3.5 * sx - 1.3, -7.25, -3.5 * sx + 1.3, -4.75)
        p1 = p1.difference(Point(-5 * sx, -3.8).buffer(1.525 + 0.3, 32))
        p1 = p1.simplify(0.01)
        L.append(custom("1", -3.5 * sx, -6, list(p1.exterior.coords)[:-1], layers))
        L.append(smd("2", 8.5 * sx, -3.8, 2.55, 2.5, layers))
        L += rect_lines(-2.45, -8.45, 7.75, -1.25, f"{side}.CrtYd", 0.05) if side == "B" else \
            rect_lines(-7.75, -8.45, 2.45, -1.25, "F.CrtYd", 0.05)
    L += rect_lines(-7.5, -7.5, 7.5, 7.5, "F.Fab", 0.1)
    L += rect_lines(-8.75, -8.25, 8.75, 8.25, "Dwgs.User", 0.1)    # keycap
    L.append(model("${KIPRJMOD}/3d/choc_v1_with_cap.wrl"))
    write("SW_Choc_V1_Hotswap_Reversible", L)


# ------------------------------------------------------------------------------------------
# Xiao: pad positions relative to the module's centre, USB end at -y.
# Seeed's F-mount numbering (module on top of the host, seen from above):
# pins 1..7 down the left edge, 8..14 up the right edge.
XIAO_EDGE_X = 8.08
XIAO_PITCH = 2.54


def xiao_pin_xy(pin, mount):
    """Position of a Xiao edge pin when mounted on the given face (seen from F)."""
    if pin <= 7:
        x, y = -XIAO_EDGE_X, -7.62 + (pin - 1) * XIAO_PITCH
    else:
        x, y = XIAO_EDGE_X, 7.62 - (pin - 8) * XIAO_PITCH
    return (-x, y) if mount == "B" else (x, y)


# The board takes either Xiao-sized nRF52840 module: the Seeed XIAO nRF52840, or the NologoTech
# Super52840 (also sold as "MINI NRF52840", "NRF52840 RE:1.4"). Both have the same 14 castellated
# pins, on the same nRF52840 pins (D0..D10); they differ underneath. Positions are F-mount,
# relative to the pin rows' centre, USB at -y.
#  - Xiao (Seeed's OPL footprint): VBAT (-4.455, -0.315) and GND (-4.455, -2.215), 2.5 x 1.1
#    pads; NFC1 (P0.09) at (3.8, 9.31) and NFC2 at (5.705, 9.31), 1.1 x 2.5. Flat underneath: its
#    USB-C has no legs through the board (checked on a real one).
#  - Super52840, measured from two photos against the 2.54 mm pin pitch (its RST, GND and SWD
#    pads land within 0.2 mm of the Xiao's): B- (-4.46, -0.36) and B+ (-4.44, -2.27), about
#    2.0 x 1.0, so the battery's polarity is the Xiao's swapped; a row of nine GPIO pads 1.1 mm
#    wide at x 5.06 to 5.3 (the photos disagree), 1.54 apart from P0.09 at y 9.76 down to P0.31
#    at -2.56; four plated USB-C leg slots, about 0.7 x 2.0, at y -4.76 and -8.94. Its USB-C sits
#    0.3 to 0.6 off centre, towards the D0..D6 side: legs at x about -4.65 and +4.05. Mirrored on
#    the other half, so the clearance covers 3.55 to 5.15 on both sides.
# Battery: one hole per pad spot, as large as the pads allow so solder flows through: a 0.6 drill
# inside both modules' pads (x -3.58..-4.18 of the pads' -3.46..-5.49), 0.18 annular (JLCPCB's
# minimum); a taller ring would close the one track channel to L1/L13 past the USB-C leg holes.
# Its mirror, under the other half's module, stays 0.15 mm clear of the Super52840's GPIO row at
# the nearest of the photos' readings (0.29 at the middle one). Which is + is the selector's
# choice (build_pcb.py): BATM is the hole nearer the middle, BATU the one nearer the USB end.
# P0.09: a hole at each module's pad, on one net. Under a Xiao, the Super52840's hole touches its
# NFC2 pad: P0.10, unused and idle, so the contact is harmless.
BOTTOM = {"BATM": ((-3.88, -0.33), (0.96, 0.96), (0.6, 0.6)),
          "BATU": ((-3.88, -2.25), (0.96, 0.96), (0.6, 0.6)),
          "NFC1": ((3.78, 9.24), (1.2, 2.2), (0.6, 1.4))}
P009 = ((5.2, 9.76), (1.0, 1.0), (0.6, 0.6))         # the Super52840's P0.09, also NFC1's net:
                                                     # the drill stays in the pad at x 5.06..5.39
# non-plated clearance under the Super52840's USB-C legs
KEEPOUT = [((sx * 4.35, y), (1.6, 2.6)) for sx in (1, -1) for y in (-4.76, -8.94)]
# The battery selector (build_pcb.py's SELECTOR) sits inside the outline too, between the D0-D2
# jumpers and the antenna end, clear of both modules' bottom pads.


# The reset test pad (Seeed's pad 17, "EN" in their symbol: test point TP2 on the nRF52840's
# P0.18/RESET in Seeed's schematic), Seeed (7.62, -16.5285) less the centre (8.9, -10.5). Its
# GND neighbour (pad 18) mirrors onto it: the other mount's reset hole sits under this mount's
# GND pad. So each mount's hole gets its own net, wired only to that half's button (see
# reset_button()), and the hole the module grounds only grounds the unused button's pads.
XIAO_RST = (-1.28, -6.03)


def xiao():
    """A Xiao-sized nRF52840 module soldered flat (castellated), on either face.

    Pads are named by LOCATION, numbered as the left half (module on B) sees
    them: L1 is where pin 1 (D0) sits on the left half. On the right half the
    module is on the F face, mirrored, so location Li carries pin 15-i.

    Each location has a pad on both faces, joined by a small plated hole just
    outside the module's edge, so you solder it from the outside with an iron.
    The module's bottom pads (battery, P0.09, reset) are reached through
    plated holes: feed solder from the opposite face. Both mount positions are
    provided; the unused face's holes sit under the other mount's bare areas.
    """
    L = header("nRF52840_Module_Reversible",
               "Seeed XIAO nRF52840 or NologoTech Super52840, castellated, on either face; "
               "bottom pads via plated holes")
    for loc in range(1, 15):
        x, y = xiao_pin_xy(loc, "B")
        sx = 1 if x > 0 else -1
        cx = x + sx * 0.57                     # pad reaches 1.5 mm past the module for the iron
        # one pad on both faces, its hole right under the module's castellation
        L.append(f'  (pad "L{loc}" thru_hole roundrect (at {fmt(cx)} {fmt(y)}) (size 3.2 1.7)'
                 f' (drill 0.5) (layers "*.Cu" "*.Mask") (roundrect_rratio 0.2))')
    for name, ((x, y), (w, h), (dw, dh)) in [*BOTTOM.items(), ("NFC1", P009)]:
        for mount in ("F", "B"):
            px = x if mount == "F" else -x
            if (w, dw) == (h, dh):
                L.append(tht(name, px, y, w, dw))
            else:
                L.append(tht(name, px, y, w, dw, shape="oval", size_y=h, drill_y=None if dw == dh else dh))
    for (x, y), (w, h) in KEEPOUT:
        L.append(f'  (pad "" np_thru_hole oval (at {fmt(x)} {fmt(y)}) (size {fmt(w)} {fmt(h)})'
                 f' (drill oval {fmt(w)} {fmt(h)}) (layers "*.Cu" "*.Mask"))')
    # Reset: RSTR is the F-mount hole (right half), RSTL the B-mount one (left half).
    rx, ry = XIAO_RST
    L.append(tht("RSTR", rx, ry, 1.4, 0.8))
    L.append(tht("RSTL", -rx, ry, 1.4, 0.8))
    # Mark the holes to fill with solder, on the face they are filled from (the one without the
    # module): the B-mount holes on F (left half), the F-mount holes on B (right half).
    (vx, vy), (_, gy) = BOTTOM["BATM"][0], BOTTOM["BATU"][0]
    (nx, ny), (px, py) = BOTTOM["NFC1"][0], P009[0]
    for mount, feed in (("B", "F"), ("F", "B")):
        sx = 1 if mount == "F" else -1
        # silkscreen boxes round the holes to fill: the battery pair, both P0.09 holes, reset
        L += rect_lines(sx * vx - 0.75, gy - 0.75, sx * vx + 0.75, vy + 0.75, f"{feed}.SilkS")
        L += rect_lines(min(sx * nx, sx * px) - 0.95, ny - 1.45, max(sx * nx, sx * px) + 0.95, py + 0.8,
                        f"{feed}.SilkS")
        L += rect_lines(sx * rx - 1.0, ry - 1.0, sx * rx + 1.0, ry + 1.0, f"{feed}.SilkS")
    for side in ("F", "B"):
        L += rect_lines(-8.75, -10.5, 8.75, 10.5, f"{side}.Fab", 0.1)
        L += rect_lines(-10.6, -11.6, 10.6, 10.8, f"{side}.CrtYd", 0.05)
        L.append(text("USB", 0, -8.9, f"{side}.Fab", 0.8, mirror=(side == "B")))
    # antenna end: no copper pour under it (done with a rule area on the board)
    L.append(model("${KIPRJMOD}/3d/xiao_nrf52840.wrl"))
    write("nRF52840_Module_Reversible", L)


# ------------------------------------------------------------------------------------------
def mirrored_pair(name, descr, pads, holes, outline, model_path=None, attr="smd"):
    """A footprint with the same part on F and, mirrored, on B."""
    L = header(name, descr, attr)
    for x, y in holes:
        L.append(npth(x, y, 0.9))
    for side, sx in (("F", 1), ("B", -1)):
        for num, x, y, w, h in pads:
            L.append(smd(num, x * sx, y, w, h, [f"{side}.Cu", f"{side}.Mask"]))
        x1, y1, x2, y2 = outline
        L += rect_lines(x1, y1, x2, y2, f"{side}.Fab", 0.1)
        L += rect_lines(x1 - 0.3, y1 - 0.3, x2 + 0.3, y2 + 0.3, f"{side}.CrtYd", 0.05)
    if model_path:
        L.append(model(model_path))
    return L


def power_switch():
    # Shouhan MSK-12C02 (pads as KiCad's SW_SPDT_Shouhan_MSK12C02); lever at +y.
    pads = [("1", -2.25, -1.95, 0.7, 1.5), ("2", 0.75, -1.95, 0.7, 1.5), ("3", 2.25, -1.95, 0.7, 1.5),
            ("SH", -3.675, -1.1, 1.05, 0.7), ("SH", -3.675, 1.1, 1.05, 0.7),
            ("SH", 3.675, -1.1, 1.05, 0.7), ("SH", 3.675, 1.1, 1.05, 0.7)]
    L = mirrored_pair("SW_MSK12C02_Reversible", "Shouhan MSK-12C02 slide switch, either face, lever at +y",
                      pads, [(-1.5, 0), (1.5, 0)], (-3.35, -1.35, 3.35, 1.35), "${KIPRJMOD}/3d/msk12c02.wrl")
    write("SW_MSK12C02_Reversible", L)


def jst():
    # JST PH S2B-PH-SM4-TB (pads as KiCad's JST_PH_S2B-PH-SM4-TB); opening at +y.
    pads = [("1", -1, -2.85, 1, 3.5), ("2", 1, -2.85, 1, 3.5),
            ("MP", -3.35, 2.9, 1.5, 3.4), ("MP", 3.35, 2.9, 1.5, 3.4)]
    L = mirrored_pair("JST_PH_S2B_Reversible", "JST PH 2-pin SMD horizontal, either face, opening at +y",
                      pads, [], (-3.95, -1.35, 3.95, 6.25), "${KIPRJMOD}/3d/jst_ph_s2b.wrl")
    for side, sx in (("F", 1), ("B", -1)):
        L.append(text("+", -2.4 * sx, -3.2, f"{side}.SilkS", 1.0, mirror=(side == "B")))
        L.append(text("BAT", 0, 7.5, f"{side}.SilkS", 1.0, mirror=(side == "B")))
    write("JST_PH_S2B_Reversible", L)


def reset_button():
    """Reset button (XKB TS-1187A, 5.1 x 5.1 mm, gull-wing legs) on either face, plunger at the
    origin. Pads as KiCad's SW_SPST_TL3342: the two pads at y = -1.9 are joined inside the
    switch, and so are the two at +1.9; pressing joins the pairs.

    F face: the left half's button (its switch face is F), pad 1 on RSTL, the left half's Xiao
    reset hole. B face: the right half's, pad 3 on RSTR. Pads 2 and 4 to GND.
    """
    L = header("SW_TS1187A_Reversible", "XKB TS-1187A 5.1x5.1 mm SMD tact switch, either face; "
               "pads after KiCad's SW_SPST_TL3342")
    for side, (rst, gnd) in (("F", ("1", "2")), ("B", ("3", "4"))):
        layers = [f"{side}.Cu", f"{side}.Mask"]
        for sx in (-1, 1):
            L.append(smd(rst, sx * 3.15, -1.9, 1.7, 1.0, layers, shape="rect"))
            L.append(smd(gnd, sx * 3.15, 1.9, 1.7, 1.0, layers, shape="rect"))
        L += rect_lines(-2.55, -2.55, 2.55, 2.55, f"{side}.Fab", 0.1)
        L += rect_lines(-4.25, -3.0, 4.25, 3.0, f"{side}.CrtYd", 0.05)
        # silkscreen: the body's top and bottom edges (the sides run into the pads)
        L.append(line(-1.9, -2.75, 1.9, -2.75, f"{side}.SilkS"))
        L.append(line(-1.9, 2.75, 1.9, 2.75, f"{side}.SilkS"))
        L.append(text("RST", 0, -3.85, f"{side}.SilkS", 1.0, mirror=(side == "B")))
    L.append(model("${KIPRJMOD}/3d/ts1187a.wrl"))
    write("SW_TS1187A_Reversible", L)


def jumper(name, side):
    """2-pad solder jumper, open, on one face; bridge it with the iron."""
    L = header(name, f"Solder jumper, open, {side} face")
    L.append(smd("1", -0.65, 0, 0.9, 1.4, [f"{side}.Cu", f"{side}.Mask"]))
    L.append(smd("2", 0.65, 0, 0.9, 1.4, [f"{side}.Cu", f"{side}.Mask"]))
    write(name, L)


def mount_hole():
    """Case screw hole, sized by design.json's screw (the head sits in the plate, not here)."""
    screw = json.load(open("design.json"))["screw"]
    name = f"MountingHole_{screw['name']}"
    L = header(name, f"{screw['name']} screw hole", attr="exclude_from_pos_files exclude_from_bom")
    L.append(npth(0, 0, screw["pcb_hole"]))
    write(name, L)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    choc()
    xiao()
    power_switch()
    jst()
    reset_button()
    jumper("SolderJumper_F", "F")
    jumper("SolderJumper_B", "B")
    mount_hole()
    print(sorted(os.listdir(OUT)))
