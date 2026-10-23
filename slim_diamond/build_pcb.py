"""Builds the Slim Diamond KiCad board from design.json (runs in KiCad's Python).

    python3 build_pcb.py build    -> pcb/slim_diamond.kicad_pcb + pcb/slim_diamond.dsn (unrouted)
    python3 build_pcb.py import   -> imports pcb/slim_diamond.ses (Freerouting), fills zones, saves

One reversible board serves both halves. Left half: parts on the B face.
Right half: board turned over, parts on the F face.
"""
import json
import math
import os
import sys

import pcbnew

HERE = os.path.dirname(os.path.abspath(__file__))
PCB_DIR = os.path.join(HERE, "pcb")
BOARD = os.path.join(PCB_DIR, "slim_diamond.kicad_pcb")
LIB = os.path.join(PCB_DIR, "slim_diamond.pretty")
OFF = (100.0, 100.0)          # design origin on the KiCad page

D = json.load(open(os.path.join(HERE, "design.json")))


def mm(v):
    return pcbnew.FromMM(v)


def pt(x, y):
    return pcbnew.VECTOR2I(mm(x + OFF[0]), mm(y + OFF[1]))


def local(c, ang, p):
    """Point p of a part placed at c, rotated ang degrees clockwise on screen."""
    a = math.radians(ang)
    return (c[0] + p[0] * math.cos(a) - p[1] * math.sin(a),
            c[1] + p[0] * math.sin(a) + p[1] * math.cos(a))


def add_fp(board, name, ref, c, ang, value=None):
    fp = pcbnew.FootprintLoad(LIB, name)
    fp.SetFPID(pcbnew.LIB_ID("slim_diamond", name))
    fp.SetReference(ref)
    fp.SetValue(value or name)
    fp.SetPosition(pt(*c))
    fp.SetOrientationDegrees(-ang)     # design angles are clockwise on screen
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


def outline(board, pts, layer=pcbnew.Edge_Cuts, width=0.1):
    for a, b in zip(pts, pts[1:] + pts[:1]):
        s = pcbnew.PCB_SHAPE(board)
        s.SetShape(pcbnew.SHAPE_T_SEGMENT)
        s.SetStart(pt(*a))
        s.SetEnd(pt(*b))
        s.SetLayer(layer)
        s.SetWidth(mm(width))
        board.Add(s)


def zone(board, pts, layer, netitem=None, rule=None, priority=0, hole=None):
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
        z.SetAssignedPriority(priority)
        z.SetMinThickness(mm(0.25))
        z.SetThermalReliefGap(mm(0.4))
        z.SetThermalReliefSpokeWidth(mm(0.4))
        z.SetLocalClearance(mm(0.3))
    board.Add(z)
    return z


def text(board, s, c, layer, size=1.0, ang=0, mirror=False):
    t = pcbnew.PCB_TEXT(board)
    t.SetText(s)
    t.SetPosition(pt(*c))
    t.SetLayer(layer)
    t.SetTextSize(pcbnew.VECTOR2I(mm(size), mm(size)))
    t.SetTextThickness(mm(size * 0.15))
    t.SetTextAngleDegrees(-ang)
    t.SetMirrored(mirror)
    board.Add(t)


def build():
    os.makedirs(PCB_DIR, exist_ok=True)
    board = pcbnew.NewBoard(BOARD)
    board.SetCopperLayerCount(2)
    ds = board.GetDesignSettings()
    nc = ds.m_NetSettings.GetDefaultNetclass()
    # JLCPCB allows 0.127 mm; the margin covers Freerouting's rounding. Freerouting's result
    # depends on these, so route.sh can try a few pairs (TRACK_W, CLEARANCE).
    nc.SetTrackWidth(mm(float(os.environ.get("TRACK_W", 0.2))))
    nc.SetClearance(mm(float(os.environ.get("CLEARANCE", 0.15))))
    nc.SetViaDiameter(mm(0.6))
    nc.SetViaDrill(mm(0.3))
    ds.m_CopperEdgeClearance = mm(0.3)     # JLCPCB: 0.3 mm copper to routed edge
    ds.m_TentViasFront = True
    ds.m_TentViasBack = True
    nets = {}

    outline(board, [tuple(p) for p in D["pcb_outline"][:-1]])

    # --- switches: pad 1 to GND, pad 2 to the key's own line.
    key_fp = {}
    for i, (name, k) in enumerate(D["keys"].items(), 1):
        fp = add_fp(board, "SW_Choc_V1_Hotswap_Reversible", f"SW{i}", (k["x"], k["y"]), k["r"], name)
        set_pads(fp, {"1": "GND", "2": f"K_{name}"}, board, nets)
        key_fp[name] = fp

    # --- Xiao.
    xc, xa = (D["xiao"]["x"], D["xiao"]["y"]), D["xiao"]["r"]
    xiao = add_fp(board, "XIAO_nRF52840_Reversible", "U1", xc, xa, "XIAO nRF52840")

    # Which Xiao input each key gets. Candidates: L4..L11 directly, the three jumpered
    # pairs (D0..D2), and NFC1. Keys and inputs are both sorted by angle around the Xiao
    # and matched with the cyclic shift that keeps wires shortest.
    # Jumpers live inside the Xiao's outline (local frame), stacked along the pin column.
    jrows = {"JA": -2.4, "JB": 0.0, "JC": 2.4}
    jl = D["jumpers_local"]
    inputs = {}
    for pad in xiao.Pads():
        num = pad.GetNumber()
        if num in {f"L{i}" for i in range(4, 12)} | {"NFC1"}:
            p = pad.GetPosition()
            inputs.setdefault(num, (pcbnew.ToMM(p.x) - OFF[0], pcbnew.ToMM(p.y) - OFF[1]))
    for j, y in jrows.items():
        inputs[j] = local(xc, xa, (jl["F"][0], jl["F"][1] + y))
    keypos = {}
    for name, fp in key_fp.items():
        ps = [p.GetPosition() for p in fp.Pads() if p.GetNumber() == "2"]
        keypos[name] = (sum(pcbnew.ToMM(p.x) for p in ps) / len(ps) - OFF[0],
                        sum(pcbnew.ToMM(p.y) for p in ps) / len(ps) - OFF[1])

    def ang_of(p):
        return math.atan2(p[1] - xc[1], p[0] - xc[0])
    ins = sorted(inputs, key=lambda n: ang_of(inputs[n]))
    ks = sorted(keypos, key=lambda n: ang_of(keypos[n]))
    best = min(range(len(ins)), key=lambda s: sum(math.dist(keypos[ks[i]], inputs[ins[(i + s) % len(ins)]])
                                                  for i in range(len(ks))))
    assign = {ks[i]: ins[(i + best) % len(ins)] for i in range(len(ks))}

    xmap = {"VBAT": "VBAT", "GND": "GND"}
    for k, inp in assign.items():
        if inp.startswith("L") or inp == "NFC1":
            xmap[inp] = f"K_{k}"
    # jumpered pairs: Li on the B face (left half), L(15-i) on the F face (right half)
    pairs = {"JA": (1, 14), "JB": (2, 13), "JC": (3, 12)}
    for j, (lb, lf) in pairs.items():
        xmap[f"L{lb}"] = f"X_L{lb}"
        xmap[f"L{lf}"] = f"X_L{lf}"
    set_pads(xiao, xmap, board, nets)
    for j, (lb, lf) in pairs.items():
        key = next(k for k, v in assign.items() if v == j)
        # left half (module on B): bridge on F; right half (module on F): bridge on B
        cf = local(xc, xa, (jl["F"][0], jl["F"][1] + jrows[j]))
        cb = local(xc, xa, (jl["B"][0], jl["B"][1] + jrows[j]))
        jf = add_fp(board, "SolderJumper_F", f"JP{lb}", cf, xa, f"D{lb - 1} left")
        jb = add_fp(board, "SolderJumper_B", f"JP{lf}", cb, xa, f"D{lb - 1} right")
        set_pads(jf, {"1": f"X_L{lb}", "2": f"K_{key}"}, board, nets)
        set_pads(jb, {"1": f"X_L{lf}", "2": f"K_{key}"}, board, nets)

    # --- power: Xiao VBAT -> switch -> JST. Lever pokes out next to the USB port.
    pw = add_fp(board, "SW_MSK12C02_Reversible", "SW13", (D["power_switch"]["x"], D["power_switch"]["y"]),
                D["power_switch"]["r"] + 180, "MSK-12C02")
    # Unused throw (3) on VBAT: in the off position the switch just joins VBAT to itself.
    # Every pad gets a net, so the router keeps its clearance from all of them.
    set_pads(pw, {"2": "VBAT", "1": "BAT+", "3": "VBAT", "SH": "GND"}, board, nets)
    # JST: placed by design.py (footprint origin and angle), its opening towards the plug room.
    jst = add_fp(board, "JST_PH_S2B_Reversible", "J1", (D["jst"]["x"], D["jst"]["y"]), D["jst"]["r"],
                 "JST PH 2.0 battery")
    set_pads(jst, {"1": "BAT+", "2": "GND", "MP": "GND"}, board, nets)

    for i, h in enumerate(D["mount_holes"], 1):
        add_fp(board, f"MountingHole_{D['screw']['name']}", f"H{i}", tuple(h), 0, D["screw"]["name"])

    # --- ground pour on both faces; none under the Xiao's antenna, no vias under the module.
    pcb_pts = [tuple(p) for p in D["pcb_outline"][:-1]]
    # (the GND pours are added after routing, so Freerouting draws real GND tracks to every pad)
    # Freerouting ignores the copper-to-edge rule: fence the edge off with a thin ring.
    ring_in = [tuple(p) for p in D["pcb_inner_ring"][:-1]]
    for layer in (pcbnew.F_Cu, pcbnew.B_Cu):
        zone(board, pcb_pts, layer, rule={"tracks", "vias"}, hole=ring_in)

    # (the antenna's no-pour area is added after routing: Freerouting would read it as a keepout.
    # Vias under the module are fine: they are tented, and the module's underside is solder mask.)

    # --- labels
    # titles run up the strip along the inner wall, between the battery and the inner thumb
    tx = D["wall_in"] - 4.5
    ty = (D["battery"]["bounds"][3] + D["keys"]["thumb_inner"]["y"]) / 2 - 4
    text(board, "SLIM DIAMOND", (tx, ty), pcbnew.F_SilkS, 1.4, -90)
    text(board, "SLIM DIAMOND", (tx, ty), pcbnew.B_SilkS, 1.4, -90, mirror=True)
    text(board, "RIGHT: parts on this face", (tx + 2.2, ty), pcbnew.F_SilkS, 0.8, -90)
    text(board, "LEFT: parts on this face", (tx + 2.2, ty), pcbnew.B_SilkS, 0.8, -90, mirror=True)
    for j, (lb, lf) in pairs.items():
        text(board, f"D{lb - 1}", local(xc, xa, (jl["F"][0] - 2.3, jl["F"][1] + jrows[j])),
             pcbnew.F_SilkS, 0.8, xa)
        text(board, f"D{lb - 1}", local(xc, xa, (jl["B"][0] + 2.3, jl["B"][1] + jrows[j])),
             pcbnew.B_SilkS, 0.8, xa, mirror=True)

    pcbnew.SaveBoard(BOARD, board)
    # GND is routed too (the pours and stitching vias come on top, after routing).
    pcbnew.ExportSpecctraDSN(board, os.path.join(PCB_DIR, "slim_diamond.dsn"))

    pins = {}
    for k, inp in assign.items():
        if inp in pairs:
            lb = pairs[inp][0]
            pins[k] = {"left": f"D{lb - 1}", "right": f"D{lb - 1}"}
        elif inp == "NFC1":
            pins[k] = {"left": "P0.09 (NFC1)", "right": "P0.09 (NFC1)"}
        else:
            i = int(inp[1:])
            pins[k] = {"left": f"D{i - 1}", "right": f"D{14 - i}"}
    json.dump({"assign": assign, "pins": pins}, open(os.path.join(PCB_DIR, "pinout.json"), "w"), indent=1)
    for k in D["keys"]:
        print(f"{k:14s} {assign[k]:5s} left {pins[k]['left']:14s} right {pins[k]['right']}")


def stitch(board, pitch=4.0):
    """GND vias wherever both pours have room, so every GND pad reaches both faces' pours."""
    gnd = board.FindNet("GND")
    outline = board.GetBoardEdgesBoundingBox()
    poly = pcbnew.SHAPE_POLY_SET()
    board.GetBoardPolygonOutlines(poly)
    filled = {}
    for z in board.Zones():
        if not z.GetIsRuleArea() and z.GetNetname() == "GND":
            filled[z.GetLayer()] = z.GetFilledPolysList(z.GetLayer())
    no_via = [z for z in board.Zones() if z.GetIsRuleArea() and z.GetDoNotAllowVias()]
    r = mm(0.6 / 2 + 0.3)
    vias = [t.GetPosition() for t in board.GetTracks() if t.Type() == pcbnew.PCB_VIA_T]
    added = 0
    x = outline.GetLeft()
    while x < outline.GetRight():
        y = outline.GetTop()
        while y < outline.GetBottom():
            p = pcbnew.VECTOR2I(int(x), int(y))
            # the via plus its clearance must sit wholly inside both faces' pour
            ring = [p] + [pcbnew.VECTOR2I(int(x + r * math.cos(a)), int(y + r * math.sin(a)))
                          for a in (i * math.pi / 6 for i in range(12))]
            ok = all(f.Contains(q) for f in filled.values() for q in ring)
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


def import_ses():
    board = pcbnew.LoadBoard(BOARD)
    ses = os.path.join(PCB_DIR, "slim_diamond.ses")
    if os.path.exists(ses):
        pcbnew.ImportSpecctraSES(board, ses)
    gnd = board.FindNet("GND")
    pcb_pts = [tuple(p) for p in D["pcb_outline"][:-1]]
    for layer in (pcbnew.F_Cu, pcbnew.B_Cu):
        zone(board, pcb_pts, layer, gnd)
    # no ground pour under the Xiao's antenna end
    xc, xa = (D["xiao"]["x"], D["xiao"]["y"]), D["xiao"]["r"]
    ant = [local(xc, xa, p) for p in ((-9.5, 5.0), (9.5, 5.0), (9.5, 11.5), (-9.5, 11.5))]
    for layer in (pcbnew.F_Cu, pcbnew.B_Cu):
        zone(board, ant, layer, rule={"pour"})
    filler = pcbnew.ZONE_FILLER(board)
    filler.Fill(board.Zones())
    print("stitching vias", stitch(board))
    filler.Fill(board.Zones())
    pcbnew.SaveBoard(BOARD, board)
    print("tracks", len(board.GetTracks()))


if __name__ == "__main__":
    {"build": build, "import": import_ses}[sys.argv[1]]()
