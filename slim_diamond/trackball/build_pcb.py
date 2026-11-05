"""Builds the Slim Diamond Trackball's board from design.json (runs in KiCad's Python).

    python3 trackball/build_pcb.py build   -> trackball/pcb/trackball.kicad_pcb + .dsn (unrouted)
    python3 trackball/build_pcb.py import  -> imports the Freerouting session, pours, stitches, saves

One board to order: the main board and the sensor board, joined by a long breakaway bridge. The
main board sits at its place in the module's plan (trackball.py), in KiCad's frame (x the same, y
towards you); the sensor board is moved sensor_shift away along y for the panel.
Seven wires join them once snapped apart: VCC, GND, RST, SCLK, SDIO, NCS, MOTION. The sensor
board's nets carry an S_ prefix: the wires join them, not copper, so the router mustn't try.

nice!nano pins (PINS): MOTION P0.22 (D4), NCS P0.24 (D5), SDIO P1.00 (D6), SCLK P0.11 (D7), key 1
P1.04 (D8), key 2 P0.17 (D2); the battery through the power switch to B+.
"""
import json
import math
import os
import sys

import pcbnew

HERE = os.path.dirname(os.path.abspath(__file__))
PCB_DIR = os.path.join(HERE, "pcb")
BOARD = os.path.join(PCB_DIR, "trackball.kicad_pcb")
LIB = os.path.join(PCB_DIR, "trackball.pretty")
OFF = (100.0, 100.0)
D = json.load(open(os.path.join(HERE, "design.json")))
NANO_L = 33.3

# each on the nano's right-column pin level with its wire pad or socket pad, so the tracks run
# short and straight, none crossing
PINS = {"MOTION": "P0.22", "NCS": "P0.24", "SDIO": "P1.00", "SCLK": "P0.11", "K1": "P1.04", "K2": "P0.17"}
NANO_LEFT = ["B+", "GND", "RST", "VCC", "P0.31", "P0.29", "P0.02", "P1.15", "P1.13", "P1.11", "P0.10", "P0.09"]
NANO_RIGHT = ["P0.06", "P0.08", "GND", "GND", "P0.17", "P0.20", "P0.22", "P0.24", "P1.00", "P0.11", "P1.04", "P1.06"]
WIRES_MAIN = ["SCLK", "SDIO", "NCS", "MOTION", "RST", "VCC", "GND"]     # right four, then left three
PAD_LABELS = {"SCLK": "CK", "SDIO": "IO", "NCS": "CS", "MOTION": "MO", "VCC": "3V", "GND": "G"}
WIRES_SENSOR = ["VCC", "GND", "RST", "SCLK", "SDIO", "NCS", "MOTION"]   # trackball.py SENSOR_PARTS J1 order
SENSOR_NETS = {   # PMW3610 pins (siderakb's 3.3 V logic configuration)
    "1": "VCSEL", "10": "VCSEL", "15": "XYL", "16": "XYL", "12": "CP", "13": "CN", "9": "VCP",
    "14": "V1V8", "11": "GND", "6": "VCC", "7": "NRST_S", "2": "SDIO", "3": "SCLK", "5": "NCS", "8": "MOTION"}
CAPS = {"C1": ("V1V8", "GND", "3.3uF"), "C2": ("V1V8", "GND", "100nF"), "C3": ("VCC", "GND", "100nF"),
        "C4": ("CP", "CN", "100nF"), "C5": ("VCSEL", "GND", "10nF"), "C6": ("VCP", "GND", "10uF"),
        "C7": ("VCP", "GND", "10nF"), "C8": ("VCC", "GND", "1uF"), "C9": ("V1V8", "GND", "1uF"),
        "R1": ("VCC", "NRST_S", "10k")}


def mm(v):
    return pcbnew.FromMM(v)


def pt(x, y):
    return pcbnew.VECTOR2I(mm(x + OFF[0]), mm(y + OFF[1]))


def kicad(p):
    """Dock frame (y away from you) to KiCad's (y towards you)."""
    return (p[0], -p[1])


def add_fp(board, name, ref, c, ang=0, value=None):
    fp = pcbnew.FootprintLoad(LIB, name)
    fp.SetFPID(pcbnew.LIB_ID("trackball", name))
    fp.SetReference(ref)
    fp.SetValue(value or name)
    fp.SetPosition(pt(*c))
    fp.SetOrientationDegrees(-ang)
    board.Add(fp)
    return fp


def net(board, nets, name):
    if name not in nets:
        n = pcbnew.NETINFO_ITEM(board, name)
        board.Add(n)
        nets[name] = n
    return nets[name]


def set_pads(fp, mapping, board, nets):
    for pad in fp.Pads():
        name = mapping.get(pad.GetNumber())
        if name:
            pad.SetNet(net(board, nets, name))


def outline(board, pts, width=0.1):
    for a, b in zip(pts, pts[1:] + pts[:1]):
        s = pcbnew.PCB_SHAPE(board)
        s.SetShape(pcbnew.SHAPE_T_SEGMENT)
        s.SetStart(pt(*a))
        s.SetEnd(pt(*b))
        s.SetLayer(pcbnew.Edge_Cuts)
        s.SetWidth(mm(width))
        board.Add(s)


def zone(board, pts, layer, netitem=None, rule=None, hole=None):
    z = pcbnew.ZONE(board)
    z.SetLayer(layer)
    o = z.Outline()
    o.NewOutline()
    for p in pts:
        v = pt(*p)
        o.Append(v.x, v.y)
    if hole:
        o.NewHole()
        for p in hole:
            v = pt(*p)
            o.Append(v.x, v.y, 0, 0)
    if rule:
        z.SetIsRuleArea(True)
        z.SetDoNotAllowCopperPour("pour" in rule)
        z.SetDoNotAllowVias("vias" in rule)
        z.SetDoNotAllowTracks("tracks" in rule)
        z.SetDoNotAllowPads(False)
        z.SetDoNotAllowFootprints(False)
    else:
        z.SetNet(netitem)
        z.SetMinThickness(mm(0.25))
        z.SetThermalReliefGap(mm(0.4))
        z.SetThermalReliefSpokeWidth(mm(0.4))
        z.SetLocalClearance(mm(0.3))
    board.Add(z)
    return z


def text(board, s, c, layer, size=1.0, mirror=False):
    t = pcbnew.PCB_TEXT(board)
    t.SetText(s)
    t.SetPosition(pt(*c))
    t.SetLayer(layer)
    t.SetTextSize(pcbnew.VECTOR2I(mm(size), mm(size)))
    t.SetTextThickness(mm(0.15))
    t.SetMirrored(mirror)
    board.Add(t)


def pad_at(fp, number):
    p = next(q for q in fp.Pads() if q.GetNumber() == number).GetPosition()
    return (pcbnew.ToMM(p.x) - OFF[0], pcbnew.ToMM(p.y) - OFF[1])


def track(board, nets, name, pts, layer, width=0.2):
    for a, b in zip(pts, pts[1:]):
        t = pcbnew.PCB_TRACK(board)
        t.SetStart(pt(*a))
        t.SetEnd(pt(*b))
        t.SetLayer(layer)
        t.SetWidth(mm(width))
        t.SetNet(net(board, nets, name))
        board.Add(t)


def via(board, nets, name, c):
    v = pcbnew.PCB_VIA(board)
    v.SetPosition(pt(*c))
    v.SetWidth(mm(0.6))
    v.SetDrill(mm(0.3))
    v.SetNet(net(board, nets, name))
    board.Add(v)


def prerouted(board, nets, fps):
    """Join the power switch's two VBAT contacts.
    The sensor's VCSEL connection runs round its optical cut-out. Other main-board nets are
    auto-routed; the controller connects through the labelled wire pads, not a pin footprint.
    """
    F, B = pcbnew.F_Cu, pcbnew.B_Cu
    # Socket orientation and wire rows follow the generated placement. Route these
    # nets afresh rather than retaining escapes tied to the previous 90-degree layout.
    # The forward K1 socket contact needs an outboard via: the router otherwise
    # puts it over the controller antenna. Derive the escape from the actual pad.
    p = max((p for p in fps["SW1"].Pads() if p.GetNumber() == "2"),
            key=lambda p: p.GetPosition().y)
    start = (pcbnew.ToMM(p.GetPosition().x) - OFF[0], pcbnew.ToMM(p.GetPosition().y) - OFF[1])
    # Between the right wire row and the main board's screw hole.
    escape = (12.5, max(p[1] for p in D["wire_pads"] if p[0] > 0) + 1.75)
    track(board, nets, "K1", [start, (start[0] + 3.4, start[1]), (start[0] + 5.2, escape[1]), escape], B)
    via(board, nets, "K1", escape)
    # Back to its wire pad on the front face, inside the right wire row, between the keys.
    k1 = pad_at(fps["K1"], "1")
    track(board, nets, "K1", [escape, (8.3, escape[1]), (8.3, k1[1] + 2.2), (7.1, k1[1] + 1.6),
                              (k1[0] + 1.5, k1[1] + 1.6), k1], F)
    ground = max((p for p in fps["SW1"].Pads() if p.GetNumber() == "1"),
                 key=lambda p: p.GetPosition().y)
    start = (pcbnew.ToMM(ground.GetPosition().x) - OFF[0], pcbnew.ToMM(ground.GetPosition().y) - OFF[1])
    escape = (-8.0, -D["nano"][1] - 6.6)
    track(board, nets, "GND", [start, (-8.0, start[1]), escape], B)
    via(board, nets, "GND", escape)
    # Front-face path round both socket families' drills at the 270-degree placement, from the
    # left wire row to the power switch. The autorouter strands this power net.
    bat = pad_at(fps["BAT+"], "1")
    track(board, nets, "BAT+", [bat, (-8.85, bat[1] - 1.15), (-8.85, 45.4), (-4.2, 40.75),
          (-2.55, 40.75), (-2.1, 40.45), (-.6, 36.1), (.9, 34.6),
          (2.1, 28.15), pad_at(fps["SW3"], "1")], F)
    sw = fps["SW3"]
    p2, p3, p1 = pad_at(sw, "2"), pad_at(sw, "3"), pad_at(sw, "1")
    track(board, nets, "VBAT", [p2, p3], F)              # both switch contacts share VBAT
    # the via left of key 2's socket pad and its peg hole; on the front, 1.6 mm under the
    # switch's other pads, then up to its pin 1
    # the sensor board: VCSEL from pin 1 (top row, left end) round the cut-out to pin 10
    u = fps["S1"]
    a, b = pad_at(u, "1"), pad_at(u, "10")
    cut_left = pcbnew.ToMM(u.GetPosition().x) - OFF[0] - 8.948 - 1.0      # 1 mm off the cut-out's left edge
    below = b[1] + 1.6
    track(board, nets, "S_VCSEL", [a, (cut_left, a[1]), (cut_left, below), (b[0], below), b], F)


def tab_box():
    """The breakaway tab's outline, from the bites' rows."""
    ys = sorted({y for _, y in D["bites"]})
    return [(-2.8, ys[0] - 0.4), (2.8, ys[0] - 0.4), (2.8, ys[-1] + 0.4), (-2.8, ys[-1] + 0.4)]


def nano_antenna():
    """The nice!nano's antenna end (away from the USB): no pour or vias over it."""
    nx, ny = D["nano"]
    y0 = -(ny + 6.0)
    y1 = -ny + 0.5
    return [(-9.5, y0), (9.5, y0), (9.5, y1), (-9.5, y1)]


def build():
    os.makedirs(PCB_DIR, exist_ok=True)
    rules = open(os.path.join(HERE, "..", "pcb", "slim_diamond.kicad_dru")).read()
    # Persist the intended 0.3 mm copper-edge clearance in a real DRC rule: KiCad can reset
    # a generated project's board-setup default to 0.5 mm when saving it.
    rules += '\n(rule "Trackball: copper to routed edge"\n  (constraint edge_clearance (min 0.3mm)))\n'
    open(os.path.join(PCB_DIR, "trackball.kicad_dru"), "w").write(rules)
    board = pcbnew.NewBoard(BOARD)
    board.SetCopperLayerCount(2)
    ds = board.GetDesignSettings()
    nc = ds.m_NetSettings.GetDefaultNetclass()
    nc.SetTrackWidth(mm(0.2))
    nc.SetClearance(mm(0.15))
    nc.SetViaDiameter(mm(0.6))
    nc.SetViaDrill(mm(0.3))
    ds.m_CopperEdgeClearance = mm(0.3)
    nets = {}
    outline(board, [tuple(p) for p in D["panel"][:-1]])

    # --- the main board
    fps = {"wires": {}}
    for i, k in enumerate(D["keys"], 1):
        # Quarter-turned: socket pads sit within 6.4 mm of the key's centre, clear
        # of the nice!nano's pin columns (7.62 mm) under it
        fp = add_fp(board, "SW_MX_Choc_V1_Hotswap", f"SW{i}", kicad(k), D["switch_angle"], f"MX / Choc v1 key {i}")
        set_pads(fp, {"1": "GND", "2": f"K{i}"}, board, nets)
        fps[f"SW{i}"] = fp
    for i, (p, name) in enumerate(zip(D["controller_pads"], ["VBAT", "K1", "K2"]), 10):
        fp = add_fp(board, "WirePad", f"J{i}", tuple(p), 0, name)
        set_pads(fp, {"1": name}, board, nets)
        fps[name] = fp
        text(board, name, (p[0] - 1.3, p[1] + 1.6) if p[0] < 0 else (p[0], p[1] - 1.6), pcbnew.F_SilkS, 0.8)
    back = min(y for _, y in D["main_board"])
    pw = add_fp(board, "SW_MSK12C02", "SW3", (0.0, back + 1.8), 180, "MSK-12C02 power")
    set_pads(pw, {"1": "BAT+", "2": "VBAT", "3": "VBAT", "SH": "GND"}, board, nets)
    fps["SW3"] = pw
    for i, (p, name) in enumerate(zip(D["wire_pads"], WIRES_MAIN), 1):
        fp = add_fp(board, "WirePad", f"J{i}", tuple(p), 0, name)
        set_pads(fp, {"1": name}, board, nets)
        fps["wires"][name] = fp
        side = 1 if p[0] > 0 else -1
        label = PAD_LABELS.get(name, name)      # short: the keys' drills sit close to these rows
        if abs(p[0]) < 8:
            text(board, label, (p[0], p[1] - 1.6), pcbnew.F_SilkS, 0.8)
        else:
            text(board, label, (p[0] - side * 1.15 - side * len(label) * 0.42, p[1]), pcbnew.F_SilkS, 0.8)
    for i, (p, name) in enumerate(zip(D["battery_pads"], ["BAT+", "GND"]), 8):
        fp = add_fp(board, "WirePad", f"J{i}", tuple(p), 0, name)
        set_pads(fp, {"1": name}, board, nets)
        fps[name if name == "BAT+" else "BAT-"] = fp
        text(board, "+" if name == "BAT+" else "-", (p[0] + 1.8, p[1]), pcbnew.F_SilkS, 1.0)
    for i, h in enumerate(D["main_holes"], 1):
        add_fp(board, "MountingHole_M3", f"H{i}", tuple(h), 0, "M3")
    text(board, "SD TRACKBALL", (0.0, back + 4.4), pcbnew.F_SilkS, 1.0)

    # --- the sensor board (its parts on the back face)
    bx, by = kicad(D["ball"])
    by += D["sensor_shift"]           # apart from the main board on the panel
    sp = D["sensor_parts"]
    S = lambda m: {k: "S_" + v for k, v in m.items()}
    u = add_fp(board, "PMW3610_Back", "S1", (bx + sp["U1"][0], by + sp["U1"][1]), 0, "PMW3610DM-SUDU + LM18-LSI")
    fps["S1"] = u
    set_pads(u, S(SENSOR_NETS), board, nets)
    ldo = add_fp(board, "SOT-23-5_Back", "S2", (bx + sp["U2"][0], by + sp["U2"][1]), 0, "TLV74318PDBVR")
    set_pads(ldo, S({"1": "VCC", "3": "VCC", "2": "GND", "5": "V1V8"}), board, nets)
    for ref, (a, b, value) in CAPS.items():
        fp = add_fp(board, "C_0805_Back", "S" + ref, (bx + sp[ref][0], by + sp[ref][1]), 0, value)
        set_pads(fp, S({"1": a, "2": b}), board, nets)
    sw = add_fp(board, "SW_TS1187A_Back", "S3", (bx + sp["SW1"][0], by + sp["SW1"][1]), 0, "TS-1187A reset")
    set_pads(sw, S({"1": "RST", "2": "GND"}), board, nets)
    for i, (p, name) in enumerate(zip(sp["J1"], WIRES_SENSOR), 1):
        fp = add_fp(board, "WirePad", f"SJ{i}", (bx + p[0], by + p[1]), 0, name)
        set_pads(fp, {"1": "S_" + name}, board, nets)
        text(board, name, (bx + p[0], by + p[1] - 1.7 if i <= 4 else by + p[1] + 1.7), pcbnew.B_SilkS, 1.0, mirror=True)
    for i, h in enumerate(D["sensor_holes"], 1):
        add_fp(board, "MountingHole_M3", f"SH{i}", tuple(h), 0, "M3")
    for i, b in enumerate(D["bites"], 1):
        add_fp(board, "MouseBite", f"MB{i}", tuple(b), 0, "bite")
    text(board, "LENS UP", (bx - 9.0, by - 6.0), pcbnew.F_SilkS, 1.0)
    ys = sorted({y for _, y in D["bites"]})
    text(board, "SNAP", (0.0, sum(ys) / 2), pcbnew.F_SilkS, 0.8)

    prerouted(board, nets, fps)

    # no copper on the tab; none over the nano's antenna
    for layer in (pcbnew.F_Cu, pcbnew.B_Cu):
        zone(board, tab_box(), layer, rule={"tracks", "vias", "pour"})
        zone(board, nano_antenna(), layer, rule={"vias", "pour"})       # thin tracks may cross
    pcbnew.SaveBoard(BOARD, board)
    pcbnew.ExportSpecctraDSN(board, os.path.join(PCB_DIR, "trackball.dsn"))
    json.dump({"pins": PINS, "wires_main": WIRES_MAIN, "wires_sensor": WIRES_SENSOR},
              open(os.path.join(PCB_DIR, "pinout.json"), "w"), indent=1)
    print("pins:", PINS)


def stitch(board, name, pitch=3.0):
    """Ground vias wherever both of a ground net's pours have room."""
    gnd = board.FindNet(name)
    box = board.GetBoardEdgesBoundingBox()
    filled = {}
    for z in board.Zones():
        if not z.GetIsRuleArea() and z.GetNetname() == name:
            filled[z.GetLayer()] = z.GetFilledPolysList(z.GetLayer())
    no_via = [z for z in board.Zones() if z.GetIsRuleArea() and z.GetDoNotAllowVias()]
    r = mm(0.6 / 2 + 0.3)
    vias = [t.GetPosition() for t in board.GetTracks() if t.Type() == pcbnew.PCB_VIA_T]
    added = 0
    x = box.GetLeft()
    while x < box.GetRight():
        y = box.GetTop()
        while y < box.GetBottom():
            p = pcbnew.VECTOR2I(int(x), int(y))
            ring = [p] + [pcbnew.VECTOR2I(int(x + r * math.cos(a)), int(y + r * math.sin(a)))
                          for a in (i * math.pi / 6 for i in range(12))]
            ok = len(filled) == 2 and all(f.Contains(q) for f in filled.values() for q in ring)
            ok = ok and not any(z.Outline().Contains(q) for z in no_via for q in ring)
            ok = ok and all((v - p).EuclideanNorm() > mm(1.0) for v in vias)
            if ok:
                v = pcbnew.PCB_VIA(board)
                v.SetPosition(p)
                v.SetWidth(mm(0.6))
                v.SetDrill(mm(0.3))
                v.SetNet(gnd)
                board.Add(v)
                vias.append(p)
                added += 1
            y += mm(pitch)
        x += mm(pitch)
    return added


def clean_ses(path):
    """The session without its degenerate wires: an empty path, or two points under 1 um apart
    (the router leaves both round fixed tracks and pads off its grid, and KiCad then refuses the
    whole file). Returns the cleaned file's path."""
    import re
    s = open(path).read()
    def keep(m):
        nums = [int(v) for v in re.findall(r"-?\d+", m.group(2))]
        pts = list(zip(nums[0::2], nums[1::2]))
        if len(pts) < 2:
            return ""
        if len(pts) == 2 and abs(pts[0][0] - pts[1][0]) + abs(pts[0][1] - pts[1][1]) < 100:
            return ""
        return m.group(0)
    s = re.sub(r"\(wire\s*\(path (\S+) \d+((?:\s+-?\d+)*)\s*\)\s*(?:\(type \w+\)\s*)?\)", keep, s)
    out = path.replace(".ses", "_clean.ses")
    open(out, "w").write(s)
    return out


def import_ses(fill=True):
    board = pcbnew.LoadBoard(BOARD)
    # The generator owns placement. A reusable routing session may contain older mounting
    # hole positions; import its copper without moving the newly generated footprints back.
    placements = {fp.GetReference(): (fp.GetPosition(), fp.GetOrientationDegrees())
                  for fp in board.GetFootprints()}
    ses = os.path.join(PCB_DIR, "trackball.ses")
    if os.path.exists(ses):
        ok = pcbnew.ImportSpecctraSES(board, clean_ses(ses))
        print("session imported:", ok)
        if not ok:
            raise RuntimeError("could not import the routing session")
        for fp in board.GetFootprints():
            pos, angle = placements[fp.GetReference()]
            fp.SetPosition(pos)
            fp.SetOrientationDegrees(angle)
    if not any(z.GetIsRuleArea() and z.GetDoNotAllowVias() and not z.GetDoNotAllowTracks() for z in board.Zones()):
        for layer in (pcbnew.F_Cu, pcbnew.B_Cu):
            zone(board, nano_antenna(), layer, rule={"vias", "pour"})
    if fill:
        finish(board)
    else:
        pcbnew.SaveBoard(BOARD, board)


def finish(board):
    """Pour and stitch the current geometry after its signal tracks have been installed."""
    board.GetDesignSettings().m_CopperEdgeClearance = mm(0.3)
    for name, key in (("GND", "main_board"), ("S_GND", "sensor_board")):
        pts = [tuple(p) for p in D[key][:-1]]
        for layer in (pcbnew.F_Cu, pcbnew.B_Cu):
            zone(board, pts, layer, board.FindNet(name))
    filler = pcbnew.ZONE_FILLER(board)
    filler.Fill(board.Zones())
    n = stitch(board, "GND") + stitch(board, "S_GND")
    filler.Fill(board.Zones())
    pcbnew.SaveBoard(BOARD, board)
    print("stitching vias:", n)


def reuse_sensor(path, fill=True):
    """Reuse the unchanged sensor circuit's copper, translated with its optical centre.
    The main board is routed separately at its current footprint positions. No placement or
    outline is imported from the reference board.
    """
    board = pcbnew.LoadBoard(BOARD)
    old = pcbnew.LoadBoard(path)
    fp = lambda b: next(f for f in b.GetFootprints() if f.GetReference() == "S1")
    delta = fp(board).GetPosition() - fp(old).GetPosition()
    sensor_fps = lambda b: {f.GetReference(): f for f in b.GetFootprints()
                            if f.GetReference().startswith("S") and not f.GetReference().startswith("SW")}
    current, previous = sensor_fps(board), sensor_fps(old)
    if current.keys() != previous.keys():
        raise ValueError("sensor circuit changed: route it again instead of reusing copper")
    for ref, part in current.items():
        key = lambda p: (p.GetNumber(), p.GetPosition().x, p.GetPosition().y)
        pads, old_pads = sorted(part.Pads(), key=key), sorted(previous[ref].Pads(), key=key)
        if len(pads) != len(old_pads) or any(
                p.GetNumber() != q.GetNumber() or p.GetNetname() != q.GetNetname()
                or (p.GetPosition() - q.GetPosition() - delta).EuclideanNorm() > mm(0.001)
                for p, q in zip(pads, old_pads)):
            raise ValueError("sensor placement changed at " + ref + ": route it again")
    fixed = [t for t in board.GetTracks() if t.GetNetname().startswith("S_")]
    count = 0
    for item in old.GetTracks():
        name = item.GetNetname()
        if not name.startswith("S_"):
            continue
        if item.Type() != pcbnew.PCB_VIA_T and any(
                t.GetNetname() == name and t.GetLayer() == item.GetLayer()
                and (t.GetStart() - (item.GetStart() + delta)).EuclideanNorm() < mm(0.001)
                and (t.GetEnd() - (item.GetEnd() + delta)).EuclideanNorm() < mm(0.001) for t in fixed):
            continue                       # retain the generator's fixed VCSEL segments only once
        if item.Type() == pcbnew.PCB_VIA_T:
            if any(t.Type() == pcbnew.PCB_VIA_T and t.GetNetname() == name
                   and (t.GetPosition() - (item.GetPosition() + delta)).EuclideanNorm() < mm(0.001)
                   for t in fixed):
                continue
            new = pcbnew.PCB_VIA(board)
            new.SetPosition(item.GetPosition() + delta)
            new.SetDrill(item.GetDrillValue())
            new.SetViaType(item.GetViaType())
            new.SetLayerPair(item.TopLayer(), item.BottomLayer())
            new.SetWidth(item.GetWidth(pcbnew.F_Cu))
        else:
            new = pcbnew.PCB_TRACK(board)
            new.SetStart(item.GetStart() + delta)
            new.SetEnd(item.GetEnd() + delta)
            new.SetLayer(item.GetLayer())
            new.SetWidth(item.GetWidth())
        new.SetNet(board.FindNet(name))
        board.Add(new)
        count += 1
    print("translated sensor tracks/vias:", count)
    if fill:
        finish(board)
    else:
        pcbnew.SaveBoard(BOARD, board)


def main_keepouts():
    # Export before any ground pours or stitching. Fences compensate for the router's
    # incomplete support for KiCad's copper-edge and drill-clearance constraints.
    board = pcbnew.LoadBoard(BOARD)
    for layer in (pcbnew.F_Cu, pcbnew.B_Cu):
        zone(board, D["panel"][:-1], layer, rule={"tracks", "vias"}, hole=D["panel_inner"][:-1])
        for fp in board.GetFootprints():
            if fp.GetReference() not in ("SW1", "SW2", "H1", "H2"):
                continue
            for pad in fp.Pads():
                if pad.GetAttribute() != pcbnew.PAD_ATTRIB_NPTH:
                    continue
                c = pad.GetPosition()
                x, y = pcbnew.ToMM(c.x) - OFF[0], pcbnew.ToMM(c.y) - OFF[1]
                radius = pcbnew.ToMM(max(pad.GetDrillSize().x, pad.GetDrillSize().y)) / 2 + 0.18
                pts = [(x + radius * math.cos(i * math.pi / 24), y + radius * math.sin(i * math.pi / 24)) for i in range(48)]
                zone(board, pts, layer, rule={"tracks", "vias"})
    pcbnew.SaveBoard(BOARD, board)


def main_dsn():
    """Route only the main circuit. Keep the verified sensor copper in the master board;
    omitting it from the router input avoids false DSN clearance conflicts and needless work.
    """
    board = pcbnew.LoadBoard(BOARD)
    # SWIG's board iterators can become invalid after object removal; snapshot
    # every collection before mutating this temporary routing board.
    # DSN otherwise turns vias/pour-only antenna rules into track keepouts.
    areas = list(board.Zones())
    tracks = list(board.GetTracks())
    footprints = list(board.GetFootprints())
    for area in areas:
        if area.GetIsRuleArea() and not area.GetDoNotAllowTracks():
            board.Remove(area)
    for fp in footprints:
        ref = fp.GetReference()
        if ref.startswith("S") and not ref.startswith("SW"):
            board.Remove(fp)
    for t in tracks:
        if t.GetNetname().startswith("S_"):
            board.Remove(t)
    pcbnew.SaveBoard(os.path.join(HERE, "..", ".render", "trackball_main_router.kicad_pcb"), board)


def export_main():
    board = pcbnew.LoadBoard(os.path.join(HERE, "..", ".render", "trackball_main_router.kicad_pcb"))
    pcbnew.ExportSpecctraDSN(board, os.path.join(PCB_DIR, "trackball.dsn"))


if __name__ == "__main__":
    {"build": build, "import": import_ses,
     "import-main": lambda: import_ses(fill=False),
     "reuse-sensor": lambda: reuse_sensor(sys.argv[2]),
     "reuse-sensor-unfilled": lambda: reuse_sensor(sys.argv[2], fill=False),
     "main-keepouts": main_keepouts, "main-dsn": main_dsn, "export-main": export_main}[sys.argv[1]]()
