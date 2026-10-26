"""Net audit of the routed board (runs in KiCad's Python): every net wired as intended.

    ./kicad.sh python3 check_pcb.py

Checks each key, the D0-D2 jumpers, the battery path and its selector, reset, and that no pad is
left on a net of its own; then that the pin map (pcb/pinout.json) is what the firmware lists.
Prints each check and ends with ALL CLEAR or the failures.
"""
import json
import math
import re
import sys

import pcbnew

D = json.load(open("design.json"))
PINOUT = json.load(open("pcb/pinout.json"))
board = pcbnew.LoadBoard("pcb/slim_diamond.kicad_pcb")
fails = []


def check(name, ok, detail=""):
    print(f"{'ok  ' if ok else 'FAIL'} {name}" + (f": {detail}" if detail and not ok else ""))
    if not ok:
        fails.append(name)


# every pad by net, as (reference, pad number)
nets = {}
for fp in board.GetFootprints():
    for p in fp.Pads():
        if p.GetAttribute() == pcbnew.PAD_ATTRIB_NPTH:
            continue
        nets.setdefault(p.GetNetname(), []).append((fp.GetReference(), p.GetNumber()))
ref_of = {fp.GetValue(): fp.GetReference() for fp in board.GetFootprints() if fp.GetReference().startswith("SW")}


def on(net):
    return sorted(set(nets.get(net, [])))


# --- keys: each key's socket pad 2 (both faces) on its own net, with exactly one way to the module
pairs = {"JA": (1, 14), "JB": (2, 13), "JC": (3, 12)}
for key, inp in PINOUT["assign"].items():
    net = f"K_{key}"
    sw = ref_of[key]
    pads = on(net)
    sockets = [p for p in pads if p[0] == sw]
    check(f"{key}: socket pad 2 on both faces", sockets == [(sw, "2")] and nets[net].count((sw, "2")) == 2,
          str(sockets))
    if inp in pairs:
        lb, lf = pairs[inp]
        want = {("U1", None)} if False else set()
        jumpers = sorted(p for p in pads if p[0].startswith("JP"))
        check(f"{key}: via jumpers JP{lb} and JP{lf} (D{lb - 1})", jumpers == [(f"JP{lf}", "2"), (f"JP{lb}", "2")]
              or jumpers == [(f"JP{lb}", "2"), (f"JP{lf}", "2")], str(jumpers))
        check(f"{key}: no direct module pad", not any(p[0] == "U1" for p in pads), str(pads))
    elif inp == "NFC1":
        check(f"{key}: the four P0.09 holes", [p for p in nets[net] if p[0] == "U1"].count(("U1", "NFC1")) == 4,
              str(pads))
    else:
        check(f"{key}: module pad {inp}", [p for p in pads if p[0] == "U1"] == [("U1", inp)], str(pads))
    check(f"{key}: nothing else on its net", all(p[0] in (sw, "U1") or p[0].startswith("JP") for p in pads),
          str(pads))
for key in PINOUT["assign"]:
    sw = ref_of[key]
    check(f"{key}: socket pad 1 on GND", nets["GND"].count((sw, "1")) == 2)

# --- D0-D2 jumpers: module side on its own net, one module pad and one jumper
for j, (lb, lf) in pairs.items():
    for loc in (lb, lf):
        check(f"X_L{loc}: module pad L{loc} and JP{loc} only", on(f"X_L{loc}") == sorted([("U1", f"L{loc}"), (f"JP{loc}", "1")]),
              str(on(f"X_L{loc}")))

# --- battery: JST + -> power switch -> VBAT; the selector picks which module hole is VBAT and GND
check("BAT+: JST pin 1 and the switch's throw", on("BAT+") == [("J1", "1"), ("SW13", "1")], str(on("BAT+")))
check("JST pin 2 and tabs on GND", ("J1", "2") in nets["GND"] and ("J1", "MP") in nets["GND"])
vbat = on("VBAT")
check("VBAT: the switch's common and spare throw", ("SW13", "2") in vbat and ("SW13", "3") in vbat, str(vbat))
check("VBAT: nothing but the switch and the selector", all(r == "SW13" or r.startswith("JS") for r, _ in vbat), str(vbat))
for hole in ("BATM", "BATU"):
    pads = on(hole)
    check(f"{hole}: the module's two holes and four selector jumpers",
          nets[hole].count(("U1", hole)) == 2 and len([p for p in pads if p[0].startswith("JS")]) == 4, str(pads))
# each selector row: one jumper per hole; +MID makes BATM VBAT, +USB makes BATU VBAT
rows = {}
for fp in board.GetFootprints():
    if fp.GetReference().startswith("JS"):
        row, hole = fp.GetValue().split()
        n = {p.GetNumber(): p.GetNetname() for p in fp.Pads()}
        other = (set(n.values()) - {hole}).pop()
        rows.setdefault(row, {}).setdefault(hole, set()).add(other)
check("selector +MID: BATM to VBAT, BATU to GND", rows.get("+MID") == {"BATM": {"VBAT"}, "BATU": {"GND"}}, str(rows.get("+MID")))
check("selector +USB: BATM to GND, BATU to VBAT", rows.get("+USB") == {"BATM": {"GND"}, "BATU": {"VBAT"}}, str(rows.get("+USB")))

# --- reset: each half's hole to its own copy of the button, the other side to GND
check("RST_L: the left half's hole and the F-face button", on("RST_L") == [("SW14", "1"), ("U1", "RSTL")], str(on("RST_L")))
check("RST_R: the right half's hole and the B-face button", on("RST_R") == [("SW14", "3"), ("U1", "RSTR")], str(on("RST_R")))
check("button's other side on GND", ("SW14", "2") in nets["GND"] and ("SW14", "4") in nets["GND"])

# --- no pad alone on a net, no pad without one
for net, pads in nets.items():
    if net == "":
        check("every plated pad has a net", False, str(pads))
    elif len(pads) < 2:
        check(f"net {net} has more than one pad", False, str(pads))
check("every net reaches at least two pads", True)

# --- the antenna end: no copper pour and no tracks under it, on either face
xc, xa = (D["xiao"]["x"], D["xiao"]["y"]), D["xiao"]["r"]
a = math.radians(-xa)


def local(p):
    x, y = pcbnew.ToMM(p.x) - 100 - xc[0], pcbnew.ToMM(p.y) - 100 - xc[1]
    return (x * math.cos(a) - y * math.sin(a), x * math.sin(a) + y * math.cos(a))


in_ant = lambda q: abs(q[0]) < 3.0 and 8.0 < q[1] < 12.5     # the strip build_pcb.py keeps clear
under = [t for t in board.GetTracks() if t.Type() == pcbnew.PCB_TRACE_T
         and (in_ant(local(t.GetStart())) or in_ant(local(t.GetEnd())))]
check("no tracks under the module's chip antenna", not under, f"{len(under)} track(s)")
rules = [z for z in board.Zones() if z.GetIsRuleArea() and z.GetDoNotAllowCopperPour()]
check("no-pour areas on both faces under the antenna", len(rules) == 2, f"{len(rules)}")

# --- the firmware lists the same pins, per half (rafaelromao/keyboards, zmk shield overlays)
fw = {}
for half, f in (("left", "fw_left.overlay"), ("right", "fw_right.overlay")):
    try:
        txt = open(f".render/{f}").read()
    except FileNotFoundError:
        fw = None
        break
    fw[half] = re.findall(r"<&(xiao_d (\d+)|gpio0 (\d+))\s", txt)
if fw is None:
    print("skip firmware pin lists (copy the overlays to .render/fw_left.overlay and fw_right.overlay)")
else:
    order = ["pinky", "ring_top", "ring_home", "ring_bottom", "middle_top", "middle_home", "middle_bottom",
             "index_top", "index_home", "index_bottom", "thumb_outer", "thumb_inner"]
    for half in ("left", "right"):
        got = [f"D{d}" if d else "P0.09 (NFC1)" for _, d, g in fw[half]]
        want = [PINOUT["pins"][k][half] for k in order]
        check(f"firmware {half} half: same 12 pins, in key order", got == want, f"firmware {got} vs board {want}")

print("ALL CLEAR" if not fails else f"{len(fails)} FAILED: {fails}")
sys.exit(1 if fails else 0)
