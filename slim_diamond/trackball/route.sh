#!/bin/sh
# The trackball's board: footprints -> KiCad board -> Freerouting -> pours + stitching -> DRC.
# PY: a Python with requirements.txt installed. FREEROUTING: Freerouting 2.x jar (needs Java 25).
# SENSOR_ROUTING: optional routed board with the same sensor circuit; reuse its sensor copper.
set -e
cd "$(dirname "$(readlink -f "$0")")/.."
PY=${PY:-python3}
JAVA=${JAVA:-java}
FREEROUTING=$(readlink -f "${FREEROUTING:-freerouting.jar}")
if [ -n "${SENSOR_ROUTING:-}" ]; then
    mkdir -p .render
    if [ "$(readlink -f "$SENSOR_ROUTING")" != "$(readlink -f .render/trackball_route_reference.kicad_pcb)" ]; then
        cp -f "$SENSOR_ROUTING" .render/trackball_route_reference.kicad_pcb
    fi
fi
$PY trackball/footprints.py >/dev/null
mkdir -p trackball/pcb
rm -rf trackball/pcb/trackball.pretty && cp -r trackball/trackball.pretty trackball/pcb/
cp pcb/slim_diamond.kicad_dru trackball/pcb/trackball.kicad_dru
rm -f trackball/pcb/trackball.ses trackball/pcb/trackball.kicad_pcb
./kicad.sh python3 trackball/build_pcb.py build
if [ -n "${SENSOR_ROUTING:-}" ]; then
    ./kicad.sh python3 trackball/build_pcb.py reuse-sensor-unfilled .render/trackball_route_reference.kicad_pcb
    ./kicad.sh python3 trackball/build_pcb.py main-keepouts
    ./kicad.sh python3 trackball/build_pcb.py main-dsn
    ./kicad.sh python3 trackball/build_pcb.py export-main
    (cd trackball/pcb && timeout 300 "$JAVA" -jar "$FREEROUTING" -de trackball.dsn -do trackball.ses \
        -mp 20 -mt 2 --gui.enabled=false > route.log 2>&1)
    # SES import replaces tracks wholesale. Restore the verified sensor circuit afterwards,
    # then pour/stitch exactly once, so a main-only session cannot erase sensor connections.
    ./kicad.sh python3 trackball/build_pcb.py import-main
    ./kicad.sh python3 trackball/build_pcb.py reuse-sensor .render/trackball_route_reference.kicad_pcb
else
    (cd trackball/pcb && timeout 1200 "$JAVA" -jar "$FREEROUTING" -de trackball.dsn -do trackball.ses \
        -mp 6 --gui.enabled=false > route.log 2>&1)
    grep -E 'session completed' trackball/pcb/route.log | sed 's/.*final score/final score/' | cut -c1-80
    ./kicad.sh python3 trackball/build_pcb.py import
fi
./kicad.sh kicad-cli pcb drc --format json --severity-all -o trackball/pcb/drc.json trackball/pcb/trackball.kicad_pcb >/dev/null 2>&1
$PY - <<'PY'
import json, collections, sys
d = json.load(open('trackball/pcb/drc.json'))
print('errors', dict(collections.Counter(v['type'] for v in d['violations'] if v['severity'] == 'error')))
print('warnings', dict(collections.Counter(v['type'] for v in d['violations'] if v['severity'] == 'warning')))
for v in d['violations']:
    if v['severity'] == 'error':
        print('  ', v['type'], '|', ' || '.join(i['description'][:60] + str(i.get('pos')) for i in v['items']))
print('unconnected', len(d['unconnected_items']))
for v in d['unconnected_items']:
    print('  ', ' -> '.join(i['description'][:50] + str(i.get('pos')) for i in v['items']))
sys.exit(1 if d['unconnected_items'] or any(v['severity'] == 'error' for v in d['violations']) else 0)
PY
