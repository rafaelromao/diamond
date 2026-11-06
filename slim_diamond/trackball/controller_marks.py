"""Silkscreen placement guide for the wired XIAO, without changing copper.

The outline is a top-view projection of a face-down controller UNDER the PCB,
not a direct-solder footprint. Lines are interrupted at holes and exposed pads.
Run with KiCad Python to update an already routed board; build_pcb.py also calls it.
"""
import json
import math
from pathlib import Path

import pcbnew
from controllers import XIAO_WIDTH, XIAO_LENGTH, XIAO_USB_OVERHANG
from controller_pinout import PADS

GROUP = "Wired XIAO placement guide"
WIDTH, LENGTH = XIAO_WIDTH, XIAO_LENGTH


def annotate(board, design):
    drawings = list(board.GetDrawings())
    footprints = list(board.GetFootprints())
    for group in list(board.Groups()):
        if group.GetName() == GROUP:
            items = list(group.GetItems())
            ids = {item.m_Uuid.AsString() for item in items}
            drawings = [item for item in drawings if item.m_Uuid.AsString() not in ids]
            for item in items:
                group.RemoveItem(item)
                board.Remove(item)
            board.Remove(group)
    group = pcbnew.PCB_GROUP(board)
    group.SetName(GROUP)
    board.Add(group)
    mm = pcbnew.FromMM
    point = lambda x, y: pcbnew.VECTOR2I(mm(x + 100), mm(y + 100))
    back = -design["nano"][1] - 33.3 - .6    # nice!nano model's rear port datum
    y0 = back + XIAO_USB_OVERHANG
    y1 = y0 + LENGTH
    edge = min(y for _, y in design["main_board"]) + .3
    blocked = []
    for item in drawings:
        if isinstance(item, pcbnew.PCB_TEXT) and item.GetLayer() == pcbnew.F_SilkS:
            if item.GetText() in ('SD TRACKBALL', 'WIRED BELOW'):
                item.SetText('MCU WIRED BELOW')
                item.SetPosition(point(0, 56.5))
            box = item.GetBoundingBox()
            blocked.append((pcbnew.ToMM(box.GetLeft()) - 100 - .2,
                            pcbnew.ToMM(box.GetTop()) - 100 - .2,
                            pcbnew.ToMM(box.GetRight()) - 100 + .2,
                            pcbnew.ToMM(box.GetBottom()) - 100 + .2))
    for fp in footprints:
        for pad in fp.Pads():
            if pad.GetLayerSet().Contains(pcbnew.F_Mask) or pad.GetAttribute() == pcbnew.PAD_ATTRIB_NPTH:
                box = pad.GetBoundingBox()
                blocked.append((pcbnew.ToMM(box.GetLeft()) - 100 - .3,
                                pcbnew.ToMM(box.GetTop()) - 100 - .3,
                                pcbnew.ToMM(box.GetRight()) - 100 + .3,
                                pcbnew.ToMM(box.GetBottom()) - 100 + .3))

    polygon = design['main_board']

    def on_board(p):
        inside = False
        for a, b in zip(polygon, polygon[1:] + polygon[:1]):
            dx, dy = b[0] - a[0], b[1] - a[1]
            if dx * dx + dy * dy < 1e-10:
                continue
            t = max(0, min(1, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / (dx * dx + dy * dy)))
            if math.hypot(p[0] - a[0] - t * dx, p[1] - a[1] - t * dy) < .3:
                return False
            if (a[1] > p[1]) != (b[1] > p[1]) and p[0] < a[0] + (p[1] - a[1]) * dx / dy:
                inside = not inside
        return inside

    def segment(a, b):
        # Clip horizontal/vertical strokes to exposed-pad clearance rectangles.
        horizontal = a[1] == b[1]
        axis, cross = (0, 1) if horizontal else (1, 0)
        lo, hi = sorted((a[axis], b[axis]))
        intervals = [(lo, hi)]
        for rect in blocked:
            if rect[cross] <= a[cross] <= rect[cross + 2]:
                start, end = rect[axis], rect[axis + 2]
                intervals = [(u, v) for left, right in intervals
                             for u, v in ((left, min(right, start)), (max(left, end), right))
                             if v - u > .4]
        for start, end in intervals:
            p, q = list(a), list(b)
            p[axis], q[axis] = start, end
            # Keep the ink on the PCB even at its angled/rounded rear corners.
            count = max(1, math.ceil((end - start) / .05))
            spans, run = [], None
            for i in range(count + 1):
                t = start + (end - start) * i / count
                sample = list(a)
                sample[axis] = t
                if on_board(sample):
                    run = t if run is None else run
                elif run is not None:
                    spans.append((run, t - (end - start) / count))
                    run = None
            if run is not None:
                spans.append((run, end))
            for start_on, end_on in spans:
                p[axis], q[axis] = start_on, end_on
                if end_on - start_on > .4:
                    stroke(p, q)

    def stroke(p, q):
        line = pcbnew.PCB_SHAPE(board)
        line.SetShape(pcbnew.SHAPE_T_SEGMENT)
        line.SetStart(point(*p))
        line.SetEnd(point(*q))
        line.SetLayer(pcbnew.F_SilkS)
        line.SetWidth(mm(.15))
        board.Add(line)
        group.AddItem(line)

    # The USB end overhangs the main PCB; only the on-board part can carry ink.
    for x in (-WIDTH / 2, WIDTH / 2):
        segment((x, max(y0, edge)), (x, y1))
    segment((-WIDTH / 2, y1), (WIDTH / 2, y1))
    # The open end of the U faces rearwards, towards the overhanging USB connector.
    def label(string, x, y, angle=0, left=False):
        text = pcbnew.PCB_TEXT(board)
        text.SetText(string)
        text.SetPosition(point(x, y))
        text.SetTextAngleDegrees(angle)
        text.SetLayer(pcbnew.F_SilkS)
        text.SetTextSize(pcbnew.VECTOR2I(mm(.8), mm(.8)))
        text.SetTextThickness(mm(.15))
        if left:
            text.SetHorizJustify(pcbnew.GR_TEXT_H_ALIGN_LEFT)
        board.Add(text)
        group.AddItem(text)

    label("XIAO: USB REAR", -3.4, y1 + .9)
    # Which controller pin each pad takes, in the free space beside the first key.
    for i, name in enumerate(("MO", "CK", "IO", "CS", "K1", "K2")):
        y = 43.0 + i * 1.25
        label(name, 7.1, y, left=True)
        label(PADS["xiao"][name], 9.2, y, left=True)
        label(PADS["nice_nano"][name], 12.4, y, left=True)
    label("XIAO", 9.2, 50.5, left=True)
    label("NANO", 12.4, 50.5, left=True)


if __name__ == "__main__":
    here = Path(__file__).resolve().parent
    path = here / "pcb/trackball.kicad_pcb"
    board = pcbnew.LoadBoard(str(path))
    annotate(board, json.loads((here / "design.json").read_text()))
    pcbnew.SaveBoard(str(path), board)
    from controller_pinout import write_pinout
    write_pinout(here / 'pcb/pinout.json')
