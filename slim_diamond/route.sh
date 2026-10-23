#!/bin/sh
# Full board pipeline: placement JSON -> footprints -> KiCad board -> Freerouting -> pours + stitching -> DRC.
set -e
cd "$(dirname "$(readlink -f "$0")")"
# PY: a Python with requirements.txt installed. FREEROUTING: Freerouting 2.x jar (needs Java 25).
PY=${PY:-python3}
JAVA=${JAVA:-java}
FREEROUTING=$(readlink -f "${FREEROUTING:-freerouting.jar}")   # absolute: the router runs in pcb/
# MODULE: xiao (default, pcb/) or super52840 (pcb_super52840/, the project files copied from pcb/)
export MODULE=${MODULE:-xiao}
P=pcb; [ "$MODULE" = xiao ] || P=pcb_$MODULE
mkdir -p $P/3d
[ $P = pcb ] || cp pcb/slim_diamond.kicad_pro pcb/slim_diamond.kicad_dru pcb/fp-lib-table $P/
[ $P = pcb ] || cp pcb/3d/*.wrl $P/3d/
$PY footprints.py >/dev/null
rm -rf $P/slim_diamond.pretty && cp -r slim_diamond.pretty $P/
rm -f $P/slim_diamond.ses $P/slim_diamond.kicad_pcb
./kicad.sh python3 build_pcb.py build > $P/pinout.txt
(cd $P && timeout 2400 "$JAVA" -jar "$FREEROUTING" -de slim_diamond.dsn -do slim_diamond.ses \
    -mp 100 --gui.enabled=false > route.log 2>&1)
grep -E 'session completed' $P/route.log | sed 's/.*final score/final score/' | cut -c1-80
./kicad.sh python3 build_pcb.py import 2>&1 | grep -v swig
./kicad.sh kicad-cli pcb drc --format json -o $P/drc.json $P/slim_diamond.kicad_pcb >/dev/null 2>&1
P=$P python3 - <<'PY'
import json, collections, os
d = json.load(open(os.environ['P'] + '/drc.json'))
print('errors', dict(collections.Counter(v['type'] for v in d['violations'] if v['severity'] == 'error')))
for v in d['violations']:
    if v['severity'] == 'error':
        print('  ', v['type'], '|', ' || '.join(i['description'][:50] + str(i.get('pos')) for i in v['items']))
print('unconnected', len(d['unconnected_items']))
for v in d['unconnected_items']:
    print('  ', ' -> '.join(i['description'][:50] + str(i.get('pos')) for i in v['items']))
PY
