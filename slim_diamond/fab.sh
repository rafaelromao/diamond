#!/bin/sh
# JLCPCB fab files from the routed board: gerbers (copper, mask, silkscreen on both faces, and the
# outline) and drill files, zipped flat into fab/slim_diamond_jlcpcb.zip.
set -e
cd "$(dirname "$(readlink -f "$0")")"
rm -rf .render/fab && mkdir -p .render/fab fab
./kicad.sh kicad-cli pcb export gerbers --no-protel-ext --subtract-soldermask \
    --layers F.Cu,B.Cu,F.Mask,B.Mask,F.Silkscreen,B.Silkscreen,Edge.Cuts \
    -o .render/fab/ pcb/slim_diamond.kicad_pcb >/dev/null
./kicad.sh kicad-cli pcb export drill --excellon-separate-th --excellon-units mm \
    -o .render/fab/ pcb/slim_diamond.kicad_pcb >/dev/null
rm -f fab/slim_diamond_jlcpcb.zip
zip -jq fab/slim_diamond_jlcpcb.zip .render/fab/*
unzip -l fab/slim_diamond_jlcpcb.zip | tail -n +4 | head -n -2 | awk '{print $4}'
# 1:1 prints of both faces (pads outlined, silkscreen, part outlines, holes) to lay the real parts
# on before ordering: print at 100 % ("Actual size"), the board outline measures 87.55 mm across.
for face in F B; do
    ./kicad.sh kicad-cli pcb export pdf --mode-single --black-and-white --drill-shape-opt 2 --sp --ibt \
        $( [ $face = B ] && echo --mirror ) --layers $face.Silkscreen,$face.Fab,Edge.Cuts \
        -o fab/print_1to1_${face}_face.pdf pcb/slim_diamond.kicad_pcb >/dev/null
done
