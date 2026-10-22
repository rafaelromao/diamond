#!/bin/sh
# Renders the board variants made by render_boards.py.
cd "$(dirname "$(readlink -f "$0")")"
r() { ./kicad.sh kicad-cli pcb render --quality high --background opaque -w 1600 -h 1200 "$@" 2>&1 | grep -E "Error|error" ; }
r --side top    -o renders/board_top.png      .render/bare.kicad_pcb
r --side bottom -o renders/board_bottom.png   .render/bare.kicad_pcb
r --rotate '-40,0,25'  --zoom 0.85 -o renders/parts_top.png    .render/parts.kicad_pcb
r --rotate '140,0,-25' --zoom 0.85 -o renders/parts_bottom.png .render/parts.kicad_pcb
r --rotate '-40,0,25'  --zoom 0.85 -o renders/full.png         .render/full.kicad_pcb
r --rotate '-40,0,25'  --zoom 0.0055 -o renders/case.png         .render/case.kicad_pcb
r --side front --zoom 1.1 -o renders/full_side.png .render/full.kicad_pcb

# All views on one sheet.
magick montage \
    -label 'Board, top' renders/board_top.png \
    -label 'Board, bottom' renders/board_bottom.png \
    -label 'Left half with parts, top' renders/parts_top.png \
    -label 'Left half with parts, bottom' renders/parts_bottom.png \
    -label 'Case' renders/case.png \
    -label 'Full build' renders/full.png \
    -label 'Full build, side (tent)' renders/full_side.png \
    -label 'Placement, top view' design.png \
    -tile 4x2 -geometry 800x600+12+12 -pointsize 26 -background white \
    -title 'Slim Diamond' renders/all.png
