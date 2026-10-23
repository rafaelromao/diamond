#!/bin/sh
# Full board pipeline: placement JSON -> footprints -> KiCad board -> Freerouting -> pours + stitching -> DRC.
set -e
cd "$(dirname "$(readlink -f "$0")")"
# PY: a Python with requirements.txt installed. FREEROUTING: Freerouting 2.x jar (needs Java 25).
PY=${PY:-python3}
JAVA=${JAVA:-java}
FREEROUTING=$(readlink -f "${FREEROUTING:-freerouting.jar}")   # absolute: the router runs in pcb/
$PY footprints.py >/dev/null
rm -rf pcb/slim_diamond.pretty && cp -r slim_diamond.pretty pcb/
rm -f pcb/slim_diamond.ses pcb/slim_diamond.kicad_pcb
./kicad.sh python3 build_pcb.py build > pcb/pinout.txt
(cd pcb && timeout 2400 "$JAVA" -jar "$FREEROUTING" -de slim_diamond.dsn -do slim_diamond.ses \
    -mp 100 --gui.enabled=false > route.log 2>&1)
grep -E 'session completed' pcb/route.log | sed 's/.*final score/final score/' | cut -c1-80
./kicad.sh python3 build_pcb.py import 2>&1 | grep -v swig
./kicad.sh kicad-cli pcb drc --format json -o pcb/drc.json pcb/slim_diamond.kicad_pcb >/dev/null 2>&1
python3 - <<'PY'
import json, collections
d = json.load(open('pcb/drc.json'))
print('errors', dict(collections.Counter(v['type'] for v in d['violations'] if v['severity'] == 'error')))
for v in d['violations']:
    if v['severity'] == 'error':
        print('  ', v['type'], '|', ' || '.join(i['description'][:50] + str(i.get('pos')) for i in v['items']))
print('unconnected', len(d['unconnected_items']))
for v in d['unconnected_items']:
    print('  ', ' -> '.join(i['description'][:50] + str(i.get('pos')) for i in v['items']))
PY
