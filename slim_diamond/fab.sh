#!/bin/sh
# JLCPCB fab files from the routed board: gerbers (copper, mask, silkscreen on both faces, and the
# outline) and drill files, zipped flat into fab/slim_diamond_jlcpcb.zip (MODULE=super52840:
# fab/slim_diamond_super52840_jlcpcb.zip, from pcb_super52840/).
set -e
cd "$(dirname "$(readlink -f "$0")")"
P=pcb; ZIP=fab/slim_diamond_jlcpcb.zip
[ "${MODULE:-xiao}" = xiao ] || { P=pcb_$MODULE; ZIP=fab/slim_diamond_${MODULE}_jlcpcb.zip; }
rm -rf .render/fab && mkdir -p .render/fab fab
./kicad.sh kicad-cli pcb export gerbers --no-protel-ext --subtract-soldermask \
    --layers F.Cu,B.Cu,F.Mask,B.Mask,F.Silkscreen,B.Silkscreen,Edge.Cuts \
    -o .render/fab/ $P/slim_diamond.kicad_pcb >/dev/null
./kicad.sh kicad-cli pcb export drill --excellon-separate-th --excellon-units mm \
    -o .render/fab/ $P/slim_diamond.kicad_pcb >/dev/null
rm -f $ZIP
zip -jq $ZIP .render/fab/*
unzip -l $ZIP | tail -n +4 | head -n -2 | awk '{print $4}'
