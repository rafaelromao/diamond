"""Create the wired-XIAO-labelled panel from the common routed panel (KiCad Python).

The controllers are wired, not mounted to this board, so the copper, panel outline,
mouse bites and sensor board remain identical. Only the identification changes.
Run after routing the common panel; regenerate both fabrication archives afterwards.
"""
from pathlib import Path
import shutil

import pcbnew

root = Path(__file__).resolve().parent
source = root / "pcb" / "trackball.kicad_pcb"
dest = root / "pcb_xiao" / "trackball_xiao.kicad_pcb"
dest.parent.mkdir(exist_ok=True)
board = pcbnew.LoadBoard(str(source))
matches = [item for item in board.GetDrawings()
           if isinstance(item, pcbnew.PCB_TEXT) and item.GetText() == "SD TRACKBALL"]
if len(matches) != 1:
    raise RuntimeError(f"Expected one panel label, found {len(matches)}")
matches[0].SetText("XIAO")
matches[0].SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(100), pcbnew.FromMM(140)))
pcbnew.SaveBoard(str(dest), board)
shutil.copyfile(source.with_suffix(".kicad_dru"), dest.with_suffix(".kicad_dru"))
shutil.copyfile(source.with_suffix(".kicad_pro"), dest.with_suffix(".kicad_pro"))
(dest.parent / "fp-lib-table").write_text(
    '(fp_lib_table\n  (lib (name "trackball")(type "KiCad")'
    '(uri "${KIPRJMOD}/../pcb/trackball.pretty")(options "")(descr ""))\n)\n'
)
print(dest)
