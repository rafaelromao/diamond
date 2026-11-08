#!/bin/sh
# JLCPCB fab files from the routed trackball board: gerbers (copper, mask, silkscreen on both faces,
# the outline with the tab and its bites) and drill files, zipped flat into
# trackball/fab/trackball_jlcpcb.zip; and 1:1 prints of both faces to lay the parts on.
set -e
cd "$(dirname "$(readlink -f "$0")")/.."
rm -rf .render/fab_trackball && mkdir -p .render/fab_trackball trackball/fab
./kicad.sh kicad-cli pcb export gerbers --no-protel-ext --subtract-soldermask \
    --layers F.Cu,B.Cu,F.Mask,B.Mask,F.Silkscreen,B.Silkscreen,Edge.Cuts \
    -o .render/fab_trackball/ trackball/pcb/trackball.kicad_pcb >/dev/null
./kicad.sh kicad-cli pcb export drill --excellon-separate-th --excellon-units mm \
    -o .render/fab_trackball/ trackball/pcb/trackball.kicad_pcb >/dev/null
rm -f trackball/fab/trackball_jlcpcb.zip
zip -jq trackball/fab/trackball_jlcpcb.zip .render/fab_trackball/*
unzip -l trackball/fab/trackball_jlcpcb.zip | tail -n +4 | head -n -2 | awk '{print $4}'
for face in F B; do
    ./kicad.sh kicad-cli pcb export pdf --mode-single --black-and-white --drill-shape-opt 2 --sp --ibt \
        $( [ $face = B ] && echo --mirror ) --layers $face.Silkscreen,$face.Fab,Edge.Cuts \
        -o trackball/fab/print_1to1_${face}_face.pdf trackball/pcb/trackball.kicad_pcb >/dev/null
done
