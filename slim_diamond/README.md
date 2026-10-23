# Slim Diamond

A wireless Choc v1 Diamond: the Diamond's 1333+2 layout on one reversible
PCB per half, a Seeed XIAO nRF52840, and a 752025 (250 mAh) battery in each
half. The halves join magnetically into a unibody, or stack back to back for
transport.

![All views](renders/all.png)

| | |
|---|---|
| Keys | 24 (12 per half): 3×3, one pinky key, two thumbs, all 1u Choc |
| Key layout | The Diamond's angles and stagger (from `body_right.stl`), packed at Choc spacing (18 × 17 mm) |
| PCB | 87.6 × 92.3 mm, 2 layers, 1.6 mm, reversible: one design, order 5. Same cut-diamond outline, so two boards side by side form the diamond. A notch in the edge in front of the USB-C lets a cable's overmold reach the port |
| Wiring | Diodeless, one pin per key (11 Xiao pins + NFC1) |
| Case | Solid base, a pocket per part (0.6 mm clearance), 0.5 mm around the PCB and plate (0.3 at the seam), 93 × 100.5 mm per half at the girdle (the rim is 91.6 × 96.5), with a 45° chamfer under it; tent 6.6°; 18.6 mm at the seam, 8.7 mm at the outer edge (plate included, keycaps excluded) |
| Top plate | Covers the whole board: 1.2 mm Choc v1 plate, 1.0 mm over the PCB (the flange sits 2.2 mm up), 14.0 mm cutouts (`cut_tol` 0.1 per side), a 0.5 mm pocket over the Xiao area for solder blobs, support pillars, countersunk screw bosses, chamfered bottom edge |
| Power | XIAO nRF52840, 752025 LiPo on a JST PH 2.0 socket, MSK-12C02 power switch next to the USB port on the lower outer facet. The wall has a recess the size of a USB-C overmold (13 × 7 mm) in front of the port, and a slot open to the top for the lever, widening outwards for a fingernail |
| Screws | 4 × M3 × 8 flat head (90° countersunk) per half: through the plate and PCB, self-tapping into the solid Nylon base (2.5 mm pilot). `SCREW` in `design.py` switches to heat-set inserts |
| Magnets | 4 × 6×2 mm in each floor (back to back), 2 × 5×2 mm in each inner wall (unibody) |
| Assembly | Iron only: no reflow-only parts |

The tent isn't a setting. It is the smallest angle that leaves room under the
inner side of the PCB for the battery (which sits under the index keys' sockets)
and keeps the outer edge as low as the hot-swap sockets allow.

## Files

| Path | What |
|---|---|
| `fab/slim_diamond_jlcpcb.zip` | Gerbers + drill files: upload to JLCPCB as they are |
| `pcb/` | The KiCad 9 project, its footprint library, 3D stand-ins, and DRC rules |
| `case/case_left.stl`, `case/case_right.stl` | The printed base |
| `case/plate_left.stl`, `case/plate_right.stl` | The printed top plate, oriented top face down for printing |
| `renders/` | Board, board with parts, case, full build; `all.png` has every view on one sheet |
| `BOM.md` | Parts list (AliExpress search terms) |
| `BUILD.md` | Hand-soldering and assembly guide, testing, printing |
| `design.png` | Top view of the placement: sockets (red), Xiao, battery, JST, magnets, screws |
| `*.py`, `*.sh` | The generators: everything above is built from them |

## Renders

| Board, top | Board, bottom |
|---|---|
| ![](renders/board_top.png) | ![](renders/board_bottom.png) |
| **Left half with parts, top** | **Left half with parts, bottom** |
| ![](renders/parts_top.png) | ![](renders/parts_bottom.png) |
| **Case** | **Full build, side (the tent)** |
| ![](renders/case.png) | ![](renders/full_side.png) |
| **Top plate** | **Top plate, underside** |
| ![](renders/plate.png) | ![](renders/plate_under.png) |
| **Joined as a unibody** | **Joined, from above** |
| ![](renders/unibody.png) | ![](renders/unibody_top.png) |
| **Stacked back to back** | **Stacked, side** |
| ![](renders/stacked.png) | ![](renders/stacked_side.png) |

## How a reversible board makes two halves

The left half gets its parts on the bottom (B) face. The right half is the same
board turned over, so its parts go on the F face. Silkscreen says which face is
which (`LEFT: parts on this face`).

Turned over, the Xiao's pins land mirrored: where the left half has D0, D1 and D2,
the right half has VBUS, GND and 3V3. Those three pins reach their keys through
solder jumpers. **Bridge the three jumpers on the face without the Xiao** (inside its
outline, labelled D0–D2) and leave the other three open. The other eight edge pins
are GPIO either way. The firmware just lists different pins per half.

Diodeless needs 12 inputs and the Xiao's edge only has 11, so the 12th key uses
the NFC1 pad on the Xiao's underside, through a plated hole you solder from the
other face. NFC itself is not used.

Pin map (from `pcb/pinout.json`):

| Key | Left | Right |
|---|---|---|
| pinky | D0 | D0 |
| ring top / home / bottom | D4 / D3 / D1 | D9 / D10 / D1 |
| middle top / home / bottom | D5 / D2 / D6 | D8 / D2 / D7 |
| index top / home / bottom | NFC1 / D7 / D8 | NFC1 / D6 / D5 |
| thumb outer / inner | D9 / D10 | D4 / D3 |

## Firmware

ZMK shield `slim_diamond` in [rafaelromao/keyboards](https://github.com/rafaelromao/keyboards)
(`zmk/keyboards/rafaelromao/slim_diamond`). It builds for `xiao_ble//zmk` with the
same keymap as the other Diamonds:

```sh
b slim_diamond -c   # central left, peripheral left/right, dongle
```

## Regenerating

Requires Python 3 with `requirements.txt`, podman (KiCad 9 runs in the
`docker.io/kicad/kicad:9.0` image through `kicad.sh`), and Freerouting 2.x with
Java 25.

```sh
python3 design.py        # placement, tent, outlines, magnets, screws -> design.json, design.png
FREEROUTING=/path/freerouting.jar ./route.sh   # footprints, board, routing, pours, DRC
./fab.sh                 # gerbers and drill files -> fab/slim_diamond_jlcpcb.zip
python3 case.py          # base and plate STLs (and their 3D models for renders)
python3 check_fit.py     # parts, plate, solder blobs, screws, magnets, a USB-C plug and the lever against the case: all 0 mm³
python3 vrml.py && python3 scene.py && ./kicad.sh python3 render_boards.py && ./render.sh
```

`layout.py` holds the Diamond geometry. `design.py` places everything else and
holds the tolerances. The outline is the fewest-facet (`GEM_FACETS`) convex
polygon around both halves joined. `XIAO_SPOT` pins the Xiao's position;
set it to `None` to search again, and if the board won't route completely, try
the runners-up the search writes to `xiao_alternatives.json`.

Credits: the Choc hot-swap footprint follows [kiswitch](https://github.com/kiswitch/kiswitch)
(MIT). The Xiao pad positions follow Seeed's
[OPL KiCad library](https://github.com/Seeed-Studio/OPL_Kicad_Library).
