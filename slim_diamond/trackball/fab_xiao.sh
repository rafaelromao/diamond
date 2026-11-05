#!/bin/sh
# Generate and verify the XIAO-labelled variant from the current routed panel.
set -eu
cd "$(dirname "$(readlink -f "$0")")/.."
./kicad.sh python3 trackball/xiao_variant.py
./kicad.sh kicad-cli pcb drc --format json --severity-all -o trackball/pcb_xiao/drc.json trackball/pcb_xiao/trackball_xiao.kicad_pcb >/dev/null
python3 - <<'PY'
import json
from pathlib import Path
base = Path('trackball/pcb/trackball.kicad_pcb').read_text()
variant = Path('trackball/pcb_xiao/trackball_xiao.kicad_pcb').read_text()
assert base.count('"SD TRACKBALL"') == 1
old = '"SD TRACKBALL"\n\t\t(at 100 120.85 0)'
new = '"XIAO"\n\t\t(at 100 140 0)'
assert old in base and variant == base.replace(old, new, 1), 'variant differs beyond label'
d = json.loads(Path('trackball/pcb_xiao/drc.json').read_text())
assert not d['unconnected_items'] and not any(v['severity'] == 'error' for v in d['violations']), 'XIAO panel DRC failed'
PY
mkdir -p .render
stage=$(mktemp -d .render/fab_xiao.XXXXXXXX)
./kicad.sh kicad-cli pcb export gerbers --no-protel-ext --subtract-soldermask --layers F.Cu,B.Cu,F.Mask,B.Mask,F.Silkscreen,B.Silkscreen,Edge.Cuts -o "$stage/" trackball/pcb_xiao/trackball_xiao.kicad_pcb >/dev/null
./kicad.sh kicad-cli pcb export drill --excellon-separate-th --excellon-units mm -o "$stage/" trackball/pcb_xiao/trackball_xiao.kicad_pcb >/dev/null
python3 - "$stage" <<'PY'
from pathlib import Path
import sys
from zipfile import ZipFile, ZIP_DEFLATED
folder = Path(sys.argv[1])
suffixes = ('-F_Cu.gbr', '-B_Cu.gbr', '-F_Mask.gbr', '-B_Mask.gbr',
            '-F_Silkscreen.gbr', '-B_Silkscreen.gbr', '-Edge_Cuts.gbr',
            '-PTH.drl', '-NPTH.drl', '-job.gbrjob')
files = [folder / ('trackball_xiao' + suffix) for suffix in suffixes]
def normalize(data):
    return b'\n'.join(line for line in data.splitlines() if not any(
        token in line for token in (b'TF.CreationDate,', b'TF.ProjectId,',
                                    b'Created by KiCad', b'; DRILL file')))
with ZipFile('trackball/fab/trackball_jlcpcb.zip') as original:
    for suffix, path in zip(suffixes, files):
        if suffix not in ('-F_Silkscreen.gbr', '-job.gbrjob'):
            assert normalize(path.read_bytes()) == normalize(original.read('trackball' + suffix)), suffix
with ZipFile('trackball/fab/trackball_xiao_jlcpcb.zip', 'w', ZIP_DEFLATED) as z:
    for p in files:
        z.write(p, p.name)
print('XIAO panel: no DRC errors or unconnected items; 10 fabrication files')
PY
