"""Makes render-only copies of the board (runs in KiCad's Python).

  bare        no 3D models
  parts       left half as built: switches on top, Xiao / switch / JST on the bottom, battery
  case        just the case (on a tiny hidden board inside the inner wall)
  full        parts + case
"""
import json
import os
import shutil

import pcbnew

D = json.load(open("design.json"))
SRC = "pcb/slim_diamond.kicad_pcb"
OUT = ".render"   # scratch boards for kicad-cli; the images go to renders/
OFF = (100.0, 100.0)


def mm(v):
    return pcbnew.FromMM(v)


def model_fp(board, name, wrl):
    fp = pcbnew.FOOTPRINT(board)
    fp.SetReference(name)
    fp.SetPosition(pcbnew.VECTOR2I(mm(OFF[0]), mm(OFF[1])))
    m = pcbnew.FP_3DMODEL()
    m.m_Filename = wrl
    fp.Models().push_back(m)
    board.Add(fp)


def save(board, name):
    path = os.path.join(OUT, f"{name}.kicad_pcb")
    pcbnew.SaveBoard(path, board)
    os.makedirs(os.path.join(OUT, "3d"), exist_ok=True)


def main():
    os.makedirs(OUT, exist_ok=True)
    if os.path.exists(os.path.join(OUT, "3d")):
        shutil.rmtree(os.path.join(OUT, "3d"))
    shutil.copytree("pcb/3d", os.path.join(OUT, "3d"))

    b = pcbnew.LoadBoard(SRC)
    for fp in b.GetFootprints():
        fp.Models().clear()
    save(b, "bare")

    b = pcbnew.LoadBoard(SRC)
    for fp in b.GetFootprints():
        if fp.GetReference() in ("U1", "SW13", "J1"):
            fp.Flip(fp.GetPosition(), pcbnew.FLIP_DIRECTION_LEFT_RIGHT)
    model_fp(b, "BT1", "${KIPRJMOD}/3d/battery.wrl")
    save(b, "parts")
    model_fp(b, "CASE", "${KIPRJMOD}/3d/case.wrl")
    save(b, "full")

    # case alone: a 0.6 mm speck of board at the case's centre (the camera centres on the board)
    b = pcbnew.NewBoard(os.path.join(OUT, "case.kicad_pcb"))
    xs = [p[0] for p in D["case_outline"]]
    ys = [p[1] for p in D["case_outline"]]
    x, y = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
    pts = [(x - 0.3, y - 0.3), (x + 0.3, y - 0.3), (x + 0.3, y + 0.3), (x - 0.3, y + 0.3)]
    for a, c in zip(pts, pts[1:] + pts[:1]):
        s = pcbnew.PCB_SHAPE(b)
        s.SetShape(pcbnew.SHAPE_T_SEGMENT)
        s.SetStart(pcbnew.VECTOR2I(mm(a[0] + OFF[0]), mm(a[1] + OFF[1])))
        s.SetEnd(pcbnew.VECTOR2I(mm(c[0] + OFF[0]), mm(c[1] + OFF[1])))
        s.SetLayer(pcbnew.Edge_Cuts)
        b.Add(s)
    model_fp(b, "CASE", "${KIPRJMOD}/3d/case.wrl")
    save(b, "case")


if __name__ == "__main__":
    main()
