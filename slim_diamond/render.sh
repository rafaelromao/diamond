#!/bin/sh
# Renders the board variants made by render_boards.py.
set -eu
cd "$(dirname "$(readlink -f "$0")")"
r() {
    if ./kicad.sh kicad-cli pcb render --quality high --background opaque -w 1600 -h 1200 "$@" > .render/render-command.log 2>&1; then
        return 0
    else
        cat .render/render-command.log >&2
        exit 1
    fi
}
r --side top    -o renders/board_top.png      .render/bare.kicad_pcb
r --side bottom -o renders/board_bottom.png   .render/bare.kicad_pcb
r --rotate '-40,0,25'  --zoom 0.85 -o renders/parts_top.png    .render/parts.kicad_pcb
r --rotate '140,0,-25' --zoom 0.85 -o renders/parts_bottom.png .render/parts.kicad_pcb
r --rotate '-40,0,25'  --zoom 0.85 -o renders/full.png         .render/full.kicad_pcb
r --rotate '-40,0,25'  --zoom 0.0016 -o renders/case.png         .render/case.kicad_pcb
r --rotate '-40,0,25'  --zoom 0.0016 -o renders/plate.png        .render/plate.kicad_pcb
r --rotate '140,0,-25' --zoom 0.0016 -o renders/plate_under.png  .render/plate.kicad_pcb
r --side front --zoom 1.1 -o renders/full_side.png .render/full.kicad_pcb
# both halves: joined as a unibody, and stacked back to back
r --side top              --zoom 0.001 -o renders/unibody_top.png   .render/unibody.kicad_pcb
r --rotate '-40,0,25'     --zoom 0.001 -o renders/unibody.png       .render/unibody.kicad_pcb
r --rotate '-60,0,25'     --zoom 0.0016 -o renders/stacked.png       .render/stacked.kicad_pcb
r --side front            --zoom 0.0016 -o renders/stacked_side.png  .render/stacked.kicad_pcb
r --rotate '-35,0,25'     --zoom 0.00065 -o renders/independent_tenting.png .render/independent_tenting.kicad_pcb

# the cyberdeck dock (scene.py): with both halves and the phone on its stand, and the dock alone
r --rotate '-58,0,-25'    --zoom 0.00055 -o renders/cyberdeck.png      .render/cyberdeck.kicad_pcb
r --side front            --zoom 0.0007 -o renders/cyberdeck_front.png .render/cyberdeck.kicad_pcb
r --side top              --zoom 0.0007 -o renders/cyberdeck_top.png   .render/cyberdeck.kicad_pcb
r --side right            --zoom 0.0006 -o renders/cyberdeck_side.png  .render/cyberdeck.kicad_pcb
r --rotate '-50,0,-25'    --zoom 0.0009 -o renders/dock_unibody.png    .render/dock_unibody.kicad_pcb
r --side left             --zoom 0.0009 -o renders/dock_unibody_side.png .render/dock_unibody.kicad_pcb
r --rotate '-50,0,-25'    --zoom 0.0009 -o renders/dock_insert.png     .render/dock_insert.kicad_pcb
r --rotate '-40,0,25'     --zoom 0.001  -o renders/dock.png            .render/dock.kicad_pcb
r --rotate '140,0,-25'    --zoom 0.001  -o renders/dock_under.png      .render/dock.kicad_pcb
r --rotate '-50,0,-150'   --zoom 0.001  -o renders/dock_base.png       .render/dock_base.kicad_pcb

# the drawer modules (scene.py): closed, cut open down the middle, and snapped onto the left half
r --rotate '-45,0,-30'    --zoom 0.0018 -o renders/trackball.png           .render/trackball.kicad_pcb
r --rotate '-45,0,-30'    --zoom 0.0018 -o renders/trackball_choc.png      .render/trackball_choc.kicad_pcb
r --rotate '-35,0,-60'    --zoom 0.0022 -o renders/trackball_open.png      .render/trackball_open.kicad_pcb
r --rotate '-45,0,-20'    --zoom 0.0011 -o renders/trackball_with_half.png .render/trackball_with_half.kicad_pcb
r --rotate '-45,0,-30'    --zoom 0.0015 -o renders/trackpad.png            .render/trackpad.kicad_pcb
r --rotate '-35,0,-60'    --zoom 0.0015 -o renders/trackpad_open.png       .render/trackpad_open.kicad_pcb
r --rotate '-45,0,-20'    --zoom 0.0011 -o renders/trackpad_with_half.png  .render/trackpad_with_half.kicad_pcb
for kind in trackball trackpad; do
    r --rotate '-55,0,-25' --zoom 0.0013 -o renders/${kind}_assembly.png .render/${kind}_assembly.kicad_pcb
    r --rotate '140,0,-30' --zoom 0.0017 -o renders/${kind}_under.png .render/${kind}.kicad_pcb
    r --side back --zoom 0.0045 -o renders/${kind}_rear.png .render/${kind}_rear.kicad_pcb
    r --rotate '-35,0,150' --zoom 0.0013 -o renders/${kind}_usb.png .render/${kind}_usb.kicad_pcb
    r --rotate '-25,0,-130' --zoom 0.0013 -o renders/${kind}_usb_open.png .render/${kind}_usb_open.kicad_pcb
    r --rotate '-30,0,150' --zoom 0.00095 -o renders/${kind}_usb_dock.png .render/${kind}_usb_dock.kicad_pcb
done
for kind in trackball trackball_choc trackpad; do
    r --rotate '-55,0,-25' --zoom 0.0013 -o renders/${kind}_structure.png .render/${kind}_structure.kicad_pcb
    r --rotate '-55,0,-25' --zoom 0.0017 -o renders/${kind}_seam.png .render/${kind}_seam.kicad_pcb
    r --rotate '-40,0,-25' --zoom 0.0017 -o renders/${kind}_tray.png .render/${kind}_tray.kicad_pcb
    r --rotate '-40,0,-25' --zoom 0.0017 -o renders/${kind}_stack.png .render/${kind}_stack.kicad_pcb
    r --rotate '140,0,-25' --zoom 0.0016 -o renders/${kind}_reset.png .render/${kind}_reset.kicad_pcb
done

# the routed trackball board (when generated)
r --rotate '-40,0,-25' --zoom 0.0017 -o renders/trackball_xiao_stack.png .render/trackball_xiao_stack.kicad_pcb
r --rotate '-25,0,-130' --zoom 0.0013 -o renders/trackball_xiao_usb_open.png .render/trackball_xiao_usb_open.kicad_pcb
if [ -f trackball/pcb/trackball.kicad_pcb ]; then
    r --side top    --zoom 0.85 -o renders/trackball_board_top.png    trackball/pcb/trackball.kicad_pcb
    r --side bottom --zoom 0.85 -o renders/trackball_board_bottom.png trackball/pcb/trackball.kicad_pcb
fi

# BUILD.md's close-ups of the Xiao area on each half's switch face (mask and silkscreen; the right
# half mirrored, as you see it turned over).
for side in F B; do
    ./kicad.sh kicad-cli pcb export svg --mode-single --layers $side.Mask,$side.Silkscreen,Edge.Cuts \
        --exclude-drawing-sheet --fit-page-to-board $( [ $side = B ] && echo --mirror ) \
        -o .render/guide_$side.svg pcb/slim_diamond.kicad_pcb >/dev/null 2>&1
    rsvg-convert -w 1750 -b white .render/guide_$side.svg -o .render/guide_$side.png
done
magick .render/guide_F.png -crop 700x700+434+869 +repage -resize 900x900 .render/xiao_left_half.png
magick .render/guide_B.png -crop 700x700+617+869 +repage -resize 900x900 .render/xiao_right_half.png
for f in xiao_left_half xiao_right_half; do
    magick .render/$f.png -modulate 55,300 -level 0%,90% renders/$f.png
done

# All views on one sheet.
${PY:-python3} render_notes.py
magick montage \
    -label 'Board, top' renders/board_top.png \
    -label 'Board, bottom' renders/board_bottom.png \
    -label 'Left half with parts, top' renders/parts_top.png \
    -label 'Left half with parts, bottom' renders/parts_bottom.png \
    -label 'Case' renders/case.png \
    -label 'Top plate' renders/plate.png \
    -label 'Top plate, underside' renders/plate_under.png \
    -label 'Full build' renders/full.png \
    -label 'Full build, side (tent)' renders/full_side.png \
    -label 'Joined as a unibody, top' renders/unibody_top.png \
    -label 'Joined as a unibody' renders/unibody.png \
    -label 'Stacked back to back' renders/stacked.png \
    -label 'Stacked back to back, side' renders/stacked_side.png \
    -label 'Placement, top view' design.png \
    -label 'Anti-slip pads, from below' renders/pads.png \
    -tile 5x3 -geometry 800x600+12+12 -pointsize 26 -background white \
    -title 'Slim Diamond' renders/all.png
