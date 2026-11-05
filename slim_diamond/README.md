# Slim Diamond

A wireless Choc v1 Diamond: the Diamond's 1333+2 layout on one reversible
PCB per half, a XIAO-sized nRF52840 module, and a 7 × 20 × 40 mm (500 mAh) battery in
each half. The halves join magnetically into a unibody, or stack back to back for
transport.

## One board, either module

The board takes a Seeed XIAO nRF52840 (the genuine one) or a NologoTech Super52840
(also sold as "MINI NRF52840", "NRF52840 RE:1.4"). Both have the same 14 edge pins
on the same nRF52840 pins, so the firmware is the same; they differ underneath,
where the board reaches the battery, the 12th key and reset:

- **Battery.** Their battery pads are in the same two spots, but swapped: the XIAO's
  + (VBAT) is the pad nearer the module's middle, the Super52840's + (B+) the one
  nearer the USB end. A **battery selector** on the switch face picks which hole is
  +: bridge the row labelled `+MID` for a XIAO, `+USB` for a Super52840. Never both:
  that shorts the battery.
- **12th key (P0.09).** The XIAO's NFC1 pad, or the Super52840's P0.09 pad in its row
  of nine extra GPIO pads: a hole under each, on the same net. Under a XIAO, the
  Super52840's hole touches its NFC2 pad (P0.10), which is unused and idle.
- **Reset** is in the same place on both.
- The Super52840's USB-C legs come through its board: the PCB has clearance holes
  under them, and its USB-C sticks out 0.8 mm further, which the case's recess takes.

The Super52840's pads were measured from several photos, beside a ruler, against the
2.54 mm pin pitch. Its USB-C sits 0.3 to 0.6 mm off centre, towards the D0–D6 pins, so
the leg clearance holes, the notch in the board edge and the case's recess all allow
for that either way (its RST, GND and SWD pads land within 0.2 mm of the XIAO's). The
battery holes are small and sit inside both modules' pads, at least 0.25 mm from the
Super52840's GPIO row under the other half's module, wherever between the two photos'
readings that row really is.

![All views](renders/all.png)

| | |
|---|---|
| Keys | 24 (12 per half): 3×3, one pinky key, two thumbs, all 1u Choc |
| Key layout | The Diamond's angles and stagger (from `body_right.stl`), packed at Choc spacing (18 × 17 mm) |
| PCB | 87.6 × 92.3 mm, 2 layers, 1.6 mm, reversible: one design, order 5. Same cut-diamond outline, so two boards side by side form the diamond. A notch in the edge in front of the USB-C lets a cable's overmold reach the port |
| Wiring | Diodeless, one pin per key (11 Xiao pins + NFC1) |
| Case | Solid base, a pocket per part (0.6 mm clearance), 0.5 mm around the PCB and plate (0.3 at the seam), 93 × 100.5 mm per half at the girdle (the rim is 91.6 × 96.5), with a 45° chamfer under it; tent 6.6°; 20.4 mm at the seam, 10.5 mm at the outer edge (plate included, keycaps excluded). Five pad slots under the floor (below) |
| Anti-slip pads | 5 × 8×2 mm silicone bump-ons per half, as on the original Diamond's base: each slot under the floor (8.6 mm wide, 1.1 deep) holds two pad spots, 8.7 mm apart. Each half sticks its pad in a different end, so stacked, each pad drops into the other half's empty end and the floors (and magnets) still meet. Every key centre sits at least 2.8 mm inside each half's pads, so a press on a border key can't tip it |
| Top plate | Covers the whole board: 1.2 mm Choc v1 plate, 1.0 mm over the PCB (the flange sits 2.2 mm up), 14.0 mm cutouts (`cut_tol` 0.1 per side), a 0.5 mm pocket over the Xiao area for solder blobs, a pocket and cone over the reset button, support pillars, countersunk screw bosses, chamfered bottom edge |
| Power | XIAO nRF52840 or Super52840, 500 mAh 1S LiPo (nominal 7 × 20 × 40 mm) on a JST PH 2.0 socket, MSK-12C02 power switch next to the USB port on the lower outer facet. The wall has a recess the size of a USB-C overmold (14.6 × 7.4 mm, rounded corners, room for a module whose port sits off centre) in front of the port, and a slot open to the top for the lever, widening outwards for a fingernail, with a rounded floor |
| Reset | A 5.1 × 5.1 × 2.0 mm SMD tact switch (TS-1187A) on the switch face, in the nook between the index finger's bottom key and the thumbs, 7.6 mm from the nearest keycap. It reaches through a 45° cone in the plate (4.2 mm across at the top, 2.8 at the throat) with its plunger 0.2 mm under the plate's top: a fingertip presses it, keycaps and palms don't. Press once to reboot, twice for the bootloader, with the case closed |
| Screws | 4 × M3 × 8 flat head (90° countersunk) per half: through the plate and PCB, self-tapping into the solid Nylon base (2.5 mm pilot). `SCREW` in `design.py` switches to heat-set inserts |
| Magnets | One part everywhere: 8 × 1.5 mm N52 discs. Each half has 13: 4 original stacking positions, 3 stand contacts on a circle around the estimated centre of gravity, and 6 evenly spread across the inner wall at 17.8 mm pitch. Every pocket keeps 0.5 mm of plastic all round |
| Assembly | Iron only: no reflow-only parts |

The 500 mAh bay moves the battery away from the inner seam and raises the PCB **1.8 mm**,
keeping the existing 6.6° tent, PCB outline, connector and screw-hole positions. The nominal
7 × 20 × 40 mm finished pack is checked with a 7.5 × 20.5 × 41 mm envelope and the case's
clearance. Measure the actual protected pack, including tabs and wire exit, before printing;
never compress a pouch cell to make it fit. The electrical board and pin map are unchanged.
The trackball and trackpad retain their smaller 752025, 250 mAh batteries.

Use the updated half cases, dock and module cases together: their front facets and heights
are a matched revision. The unchanged keyboard PCB and top plates can be reused.

## Independent tenting on the Ugreen's tilting platform

Each half has three extra floor magnets on a **44 mm circle**, spaced **120° apart** around
the estimated assembled centre of gravity. The pattern is derived from a mass-weighted model
of the nylon case, PCB, battery, switches and magnets, checked by `stand_mount.py`; it is not
a measured balance point. Add three mates of the same **8 × 1.5 mm** size
to the **tilting phone platform**, not the stand's base, with opposite poles facing the half.
For both halves independently, use two stands and six platform magnets. Glue the mates
while aligned with their own half; the right pattern is mirrored. The stand magnets stand
1.5 mm above the platform, so the keyboard's bump-ons remain **0.6 mm clear** and cannot rock it.
The estimated gravity projection remains inside the three-contact triangle through 35° of tilt;
this does not certify the magnets' holding force or the stand's own stability.

`python3 stand_mount.py` checks the group and writes 1:1 templates:
[left](case/stand_magnet_template_left.svg), [right](case/stand_magnet_template_right.svg).
Print at 100%: the dashed contact boundary is **54 mm** across; the magnet-centre circle is 44 mm.
That is the required clear flat
patch, **not a confirmed Ugreen measurement**. Measure the real platform, including rubber,
lips and obstructions, before gluing. Magnet holding force, adhesive strength and stability at
the chosen tilt need a physical load test. The render uses an illustrative stand/platform.

![Each half on its own tilting stand](renders/independent_tenting.png)

## Before ordering

The board is made in one batch, so check what software can't:

1. **Print** `fab/print_1to1_F_face.pdf` and `fab/print_1to1_B_face.pdf` at 100 % ("Actual
   size", no fit to page). The board outline must measure 87.55 mm across.
2. **Lay the real parts on the prints**, each on the face it's soldered to. The module's
   castellations go over the edge pads, with its USB-C at the board edge. A Choc switch's pins and
   pegs go over one key's holes, and its hot-swap socket over the socket pads on the other face.
   Then the JST socket, the MSK-12C02 (its two pegs in the small holes) and the reset button.
3. **Super52840:** on the print, its B+ and B- pads must cover the two holes in the battery box,
   its `009` pad the round hole in the P0.09 box, and its USB-C legs land inside the two pairs of
   slots. Measure its height from its underside to the top of its USB-C shell: the case allows
   4.3 mm (the XIAO's).
4. **Firmware:** rebuild it before flashing (`b slim_diamond -c` in rafaelromao/keyboards, branch
   `slim-diamond`). `check_pcb.py` confirms that branch lists the board's pins, given the shield's
   `slim_diamond_peripheral_left.overlay` and `_right.overlay` copied to `.render/fw_left.overlay`
   and `.render/fw_right.overlay`.

Checked by the scripts: JLCPCB's limits in the DRC (`pcb/slim_diamond.kicad_dru`: annular ring
0.18, pad holes 0.45 apart, tracks and clearance 0.10, silkscreen 1.0 mm text with a 0.15 stroke),
no tracks under the module's antenna, every net against its intent and the firmware's pin lists
(`check_pcb.py`), both modules' underside pads against the board's copper, and every part, plug,
screw, magnet and pad against the case (`check_fit.py`).

## Files

| Path | What |
|---|---|
| `fab/slim_diamond_jlcpcb.zip` | Gerbers + drill files: upload to JLCPCB as they are |
| `fab/print_1to1_F_face.pdf`, `fab/print_1to1_B_face.pdf` | Both faces at full size, to lay the real parts on before ordering |
| `pcb/` | The KiCad 9 project, its footprint library, 3D stand-ins, and DRC rules |
| `case/case_left.stl`, `case/case_right.stl` | The printed base |
| `case/plate_left.stl`, `case/plate_right.stl` | The printed top plate, oriented top face down for printing |
| `case/dock.stl`, `case/insert.stl` | The cyberdeck dock, and the placeholder for its drawer (below) |
| `stand_mount.py`, `case/stand_magnet_template_*.svg` | Independent-stand contact check and 1:1 platform-magnet templates |
| `trackball/`, `trackpad/` | The drawer modules: scripts, `case/` STLs; the trackball's board in `pcb/` and `fab/` |
| `zmk/` | The modules' ZMK shields |
| `renders/` | Board, board with parts, case, full build; `all.png` has every view on one sheet |
| `BOM.md` | Parts list (AliExpress search terms) |
| `BUILD.md` | Hand-soldering and assembly guide, testing, printing |
| `build-log.html` | The project on one page: both boards, the renders, the BOM and the build guide (open it via raw.githack or GitHub Pages: GitHub shows .html as source) |
| `design.png` | Top view of the placement: sockets (red), Xiao, battery, JST, magnets, screws, the reset button (red, its cone white), pad slots (grey: left pads filled, the right half's dashed) |
| `renders/pads.png` | Both floors from below: where each half's pads go |
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

## Cyberdeck dock

A phone on a Ugreen folding stand (base 85 × 105 × 4 mm) is the computer and the screen;
`dock.py` makes one printed part, `case/dock.stl`, that holds both halves around it. Without the
stand it is a tented, splayed unibody, sturdier than the magnets at the seam alone.

- **Over the stand's base**, in a pocket in its underside: the base keeps its own feet on the
  desk and carries the phone. Behind the spine the base is left bare, its hinge (`HINGE`,
  30 × 28 mm, estimated from photos: measure yours) 0.5 mm (`HINGE_CLR`) off the halves, the
  wings and the spine, as far forward as their back corners let it. The pocket's fit holds the
  dock on the base, together with five pairs of the common **8 × 1.5 mm magnets**: five pressed
  into the pocket's roof and five glued on the aluminium base. The tent also keeps room for
  both discs and their backing below the drawer floor.
- **The board's lower half:** under each half's girdle, its widest line, every wall of the dock
  carries on the case's own 45° bottom chamfer down to the desk, one flat plane with it, front,
  back and sides, wings and spine alike. Each wall is built as a plane through its girdle edge, so
  none can fold. Below the girdle the spine and the wings are one piece; above it the spine stops
  0.2 mm short of the seam walls. The wing ends just short of the outer pad, which stands on the
  desk, and each pad recess is shaped to its bump-on's dome so none breaks out of a wall.
- **The halves on wings** the shape of their floors, inner side up, outer pad on the desk, splayed
  12° (`SPLAY`). The extra tent is the least that keeps 1.6 mm of plastic over the base and room
  under the magnets: 5.96°, about 12.5° in all. Every pad slot has a recess, both ends.
- **A spine** between the halves, level with their seam walls' top edges, its front and back
  carrying on both halves' walls, its point cut to a flat as wide as the joined board's front
  flat (about 20 mm). Its middle is a **drawer** (`DRAWER`), pulled out through the front, for a module
  (below) or the **placeholder** (`insert.py`, `case/insert.stl`): a solid block with the modules'
  outline and magnets, flush with the halves, the joined board's diamond cut into its top. The
  drawer is open at both the top and the front. Its sides are straight and uninterrupted: no
  raised ends at the mouth, no ribs or matching grooves. The insert's front is shaped in 3D by
  the halves' exact front facet planes, rather than set back to a vertical wall, so the assembled
  front reads as one element. Grip that front and pull horizontally; lifting is not necessary.
- **Six side magnets per half:** the dock's continuous walls are 2.4 mm thick at their
  thinnest and house six of the common **8 × 1.5 mm N52 magnets per side**, matching all six
  half seam magnets. The gap between the halves is widened by 1.25 mm to preserve insert space.
  Load them from outside, flush, and glue them in; a verified **0.6 mm inner skin** retains them
  inside. Each faces the keyboard half directly outside and the insert's own matching magnet
  through the inner wall at three of those positions. The insert still has only three side
  magnets per side, evenly spaced at y = -7.0, 28.6 and 64.2 mm (seam magnets 2, 4 and
  6, every other magnet in the six-position row). The same insert magnets meet either half directly on the desk.
  Check magnetic holding force with real magnets before relying on it to carry the assembly.
- **No rear retention magnet:** the rear is reserved for the USB-C connector, cable and power
  switch. The six side magnets retain each insert. The 2.2 mm bottom plates retain 0.7 mm above
  their foot recesses; neither the floor nor rear wall has an extra magnet pocket.
- **Lap use:** the rear hood recess and USB passage remove material from the dock spine. Previous
  stiffness estimates predate these cuts and must not be used to rate this revision. A removable
  insert is not bonded, and hollow modules and fit clearance reduce its contribution. Test a
  printed dock under load before relying on it for lap use.
- **Magnets in the wings** under six of each half's seven floor magnets. `MAG_COST` rejects
  positions that would add more than 1° to the tent needed for the base pocket. `MAG_ROOF`
  keeps 1 mm under a pocket over the base. Pockets near a 45° wall are nudged inwards to retain
  their surrounding plastic without losing alignment with the case's magnet.
- **Feet:** the underside is cut 0.5 mm (`FOOT_LIFT`) off the desk, and three 8 × 2 mm bump-ons
  under each wing, spread to the largest triangle, make that up.
- 195.1 × 111.0 × 30.2 mm, 84.4 cm³. `python3 dock.py` prints the fit check: each half, its pads, the
  base and the hinge against the dock, all 0 mm³, and the plastic round every magnet and foot.

| **With the phone** | **From the front** |
|---|---|
| ![](renders/cyberdeck.png) | ![](renders/cyberdeck_front.png) |
| **Without the stand: a unibody** | **From the side** |
| ![](renders/dock_unibody.png) | ![](renders/cyberdeck_side.png) |
| **The dock** | **Underneath** |
| ![](renders/dock.png) | ![](renders/dock_under.png) |

## Drawer modules: a trackball or a trackpad

### USB-C connection

Both modules retain their rear USB-C connection. These renders show an illustrative straight
plug (12.35 × 6.5 mm overmold), seated at the controller, with a cable extending through the rear.
The dock has a wide recess for the seated plug and a **12.8 mm wide upper rear passage**, leaving the
side-magnet skins intact below it. With the drawer empty, feed the plug through from the rear in
its normal orientation, connect the module and slide the module in while feeding the cable. The model
checks the 12.35 × 6.5 mm overmold along this threading path. A larger plug may not pass:
remove the module for charging instead. Unplug before
removing a module with a restrained cable. Actual cable dimensions and bend radius must be checked.

At the rear the inserts' tops extend over the dock's sloped support to the existing rear facet.
The common underside and its mating support are **45°**, separated by 0.25 mm normal clearance;
the lower module bodies do not extend over the support. The hood remains part of each shell (and
the solid cover), and the USB and switch openings remain accessible. Printed fit and support
strength need physical testing.

| Trackball: rear connection | Cutaway to the receptacle |
|---|---|
| ![](renders/trackball_usb.png) | ![](renders/trackball_usb_open.png) |
| Trackpad: rear connection | Cutaway to the receptacle |
| ![](renders/trackpad_usb.png) | ![](renders/trackpad_usb_open.png) |
| Trackball docked | Trackpad docked |
| ![](renders/trackball_usb_dock.png) | ![](renders/trackpad_usb_dock.png) |

Two standalone ZMK pointing devices, each with its own nice!nano, a 752025 (250 mAh) battery, a
power switch and a reset button, connecting over their own Bluetooth. Either slides into the dock's
drawer from the front, or snaps onto either half's inner wall on the desk, or sits on its own on its
bump-ons. Both share one shell (`module_shell.py`): the drawer's outline, vertical walls, a
  screwed bottom plate, and three common magnets a side where the halves' inner-wall magnets are
(the 2nd, 4th and 6th), at the same height over the plane both stand on. In the dock the module's
magnets face the dock's thin magnets through its inner skin; on the desk they face either half
directly. The standing plane remains z = 0 for both parts; their magnet centres are 7.2 mm above
it. In the dock the insert stands at z = 9.181 mm and its side magnets at z = 16.381 mm, level with
the tented halves' magnets. No part needs to be lifted or shimmed for the magnets to meet.

`python3 -m unittest test_stl_export test_half_battery test_drawer test_module_assembly trackball.test_layout`
runs the artifact and assembly regressions. `test_drawer` checks all three inserts: uninterrupted walls, at least two
dock-side magnet pairs per half (there are six), full inner skins, coplanar front facets,
seated USB plug clearance, the complete horizontal removal path in 0.5 mm steps,
and desk contact beside either half. `python3 -m unittest test_half_battery` checks the 500 mAh
half-battery envelope and the independent-stand contact group.
Both module scripts also check every part against the shell and bottom plate: all 0 mm³.
The [audit follow-up](STL_AUDIT.md) records the independent STL findings, source fixes
and remaining physical-validation limits; the initial report is retained alongside it.

| **Trackball** | **Cutaway (not a service position)** |
|---|---|
| ![](renders/trackball.png) | ![](renders/trackball_open.png) |
| **Choc v1 case, same PCB** | **Rear USB-C connection** |
| ![](renders/trackball_choc.png) | ![](renders/trackball_usb.png) |
| **On a half, on the desk** | **Its board (front / back)** |
| ![](renders/trackball_with_half.png) | ![](renders/trackball_board_top.png) ![](renders/trackball_board_bottom.png) |
| **Trackpad** | **Cutaway (not a service position)** |
| ![](renders/trackpad.png) | ![](renders/trackpad_open.png) |
| **On a half, on the desk** | **The placeholder in the drawer** |
| ![](renders/trackpad_with_half.png) | ![](renders/dock_insert.png) |

**Slim Diamond Trackball** (`trackball/trackball.py`): a 34 mm ball and two MX or Choc v1
hot-swap keys on one shared PCB. The MX shell is 4 mm taller than the halves; the Choc shell is
1.2 mm taller. Both bevel up at 45° and retain room for the battery and wired nice!nano below.

- The ball sits in a cup in the shell on three 3 mm Si3N4 balls and lifts straight out; its top
  is 20.2 mm over the MX shell (23.0 mm over the Choc shell). Under it, a PMW3610 on its own board looks up through an LM18-LSI
  lens (circuit after siderakb's pmw3610-pcb, CERN-OHL-P-2.0, at 3.3 V logic with a TLV74318).
- The shared main PCB accepts **MX or Choc v1 hot-swap sockets**, not both populated together.
  Choc sockets face 180° opposite the MX sockets. MX uses `trackball/case/shell.stl` (1.5 mm plate);
  Choc uses `trackball/case/shell_choc.stl` (1.2 mm plate, top 2.8 mm lower). Both use the same
  PCB, ball/sensor positions and bottom plate. Use **M2 × 3** main-board screws for Choc,
  **M2 × 5** for MX; both use M2 × 5 for the sensor. Choc v2 is not supported.
- The nice!nano is supported face down on shell-mounted ledges and wired to labelled pads rather
  than pinned through the switch PCB, avoiding socket/pin-hole collisions. Secure it with
  insulating tape without covering its antenna or USB opening. Ten leads connect GND, VCC, RST,
  VBAT → B+, and the six GPIO signals below. Shared sensor/controller pads take two leads.
  The main PCB also carries the power switch, battery and seven sensor-wire pads. The reset button is on the
  sensor board, facing down: press it with a pin through the bottom plate.
- Keys move 3.8 mm rearward on the trackball and 4 mm on the trackpad; the trackball controller moves 1.8 mm rearward
  to y = −58.4 mm, stopping short of the taper. A maximum 1.5 mm upper bevel retains
  at least 1 mm of plate around the rear switch. Both socket families rotate with the keys.
- Bottom plates fit a vertical extraction envelope. Remove the module from the dock,
  switch it off, remove its three floor screws and lower the floor gently with wire slack.
  The trackball controller stays in the shell; its battery and sensor board move with the floor.
  Do not pull on their wires. Disconnect leads before separating the pieces fully.
- The exported top-down MX and Choc shells **require supports beneath the rear hood**:
  its underside starts 4.0 / 1.2 mm above the bed. Paint build-plate supports under the
  entire projecting hood, excluding switch/ball openings; inspect the sliced first hood
  layers and support-removal access. Tune the interface gap for your printer and test-print
  this region first. This strategy is not physically validated; the 45° assembled mating
  face does not make the hood self-supporting in this print orientation.
- A [flex feasibility study](trackball/FLEX_FEASIBILITY.md) compares Leonardo-style
  routed FR4 springs with JLCPCB polyimide flex. Keep the rigid breakaway boards and
  wires as the baseline: a ≤100 × 100 mm bounding box alone does not establish quote
  eligibility, bend durability or a suitable stiffener stack.
- Controller wiring: sensor SCLK P0.11, SDIO P1.00 (SPI2, 3-wire), NCS P0.24, MOTION
  P0.22; key 1 P1.04, key 2 P0.17 (other legs to GND).
- One board to order (`trackball/fab/trackball_jlcpcb.zip`): the sensor board snaps off a tab.
  `trackball/route.sh` builds, routes and checks it (`build_pcb.py`, Freerouting, DRC).
   Sensor-routing reuse verifies the unchanged sensor circuit, translates its copper, then routes
   the shared switch board and refills both ground planes. Final DRC is the fabrication gate;
   fit checks alone do not certify routing. Library-reference and silkscreen warnings may remain.
  To reuse that sensor routing when regenerating, run
  `SENSOR_ROUTING=trackball/pcb/trackball.kicad_pcb ./trackball/route.sh` (with `PY` set if needed).
  The script verifies that the sensor circuit is unchanged and preserves the generator's placement.
- The ball is at y = −77.937 mm. The bottom-plate post search reserves the wire rows,
  sensor board and main-board posts first, keeping its notches clear; it uses an absolute 0.5 mm
  grid. The main-board screw holes sit between the keys, fully enclosed by the board and separate
  from the bottom-plate posts.
  `python3 -m unittest discover -s trackball -p 'test_*.py'` checks that layout.
- Unconfirmed, measure before printing: `LENS_ABOVE` (the lens's base over the sensor board, sets
  the ball's height) and `NANO_ROW1` (the nice!nano's first pin row from its USB end).

**Slim Diamond Trackpad** (`trackpad/trackpad.py`): a 40 mm Cirque (TM040040, SPI) and two Choc
keys stacked behind it, hand-wired, flush with the halves.

- The pad sits in the top on a ledge, open at the back for its cable. Under it, on the plate: the
  battery in a cradle and the cable's FFC adapter on a shelf over it; behind them a 13.5 mm gap
  for the wires and the reset button (pressed through the plate). The nice!nano sits in a cradle
  under the keys, USB-C out of the back wall; the power switch in a pocket over it.
- Unconfirmed: the pad's thickness and the parts on its back (`PAD`), the adapter's size.

| Wire | nice!nano pin |
|---|---|
| Pad SCK (FFC 1), SO (2), SS (3), DR (4), SI (5) | D3 (P0.20), D4 (P0.22), D6 (P1.00), D7 (P0.11), D5 (P0.24) |
| Pad GND (FFC 11), VDD (FFC 12) | GND, VCC (3.3 V) |
| Key 1, key 2 (other legs to GND) | D8 (P1.04), D9 (P1.06) |
| Reset (other leg to GND) | RST |
| Battery + (through the power switch), − | B+, B− |

**Firmware** (`zmk/`): a ZMK config with both shields, `slim_diamond_trackball` (the PMW3610 through
badjeff's zmk-pmw3610-driver) and `slim_diamond_trackpad` (the Cirque through petejohanson's
cirque-input-module), pinned in `zmk/config/west.yml`. Key 1 clicks left; key 2 clicks right, and
held turns pointing into scrolling; both together click middle. If the pointer runs the wrong way,
toggle `invert-x` / `invert-y` (trackball) or `x-invert` / `y-invert` (trackpad) in the overlay.

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

The reset button is wired the same way: the Xiao's reset test pad (pad 17 in
Seeed's footprint, `EN` in their symbol; TP2 on the nRF52840's P0.18/RESET in
Seeed's schematic) is reached through a plated hole filled from the switch face,
and the button joins it to GND. Each half's reset hole has its own net (`RST_L`,
`RST_R`) wired only to that half's button pads: turned over, one half's reset
hole lands under the other half's GND test pad. No pin changes, so the firmware
is unaffected.

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
python3 magnets.py       # only after a layout change: measures the base for the magnets to pin in design.py
python3 case.py          # base and plate STLs (and their 3D models for renders)
python3 check_fit.py     # parts, plate, solder blobs, the reset button and its cone, screws, magnets, pad slots, a USB-C plug and the lever against
                         # the case, the pads stacked, and the pads' balance: all 0 mm³, ALL CLEAR
./kicad.sh python3 check_pcb.py   # every net against its intent, and the firmware's pin lists: ALL CLEAR
python3 dock.py          # the cyberdeck dock's STL, and its fit check: all 0 mm³
python3 trackball/trackball.py && ./trackball/route.sh && ./trackball/fab.sh   # trackball module: case, board, gerbers
python3 trackpad/trackpad.py                       # trackpad module: case and fit check
python3 insert.py                                  # the drawer's placeholder
python3 vrml.py && python3 scene.py && ./kicad.sh python3 render_boards.py && ./render.sh
python3 page.py          # build-log.html's BOM and build-guide sections, from BOM.md and BUILD.md
```

`layout.py` holds the Diamond geometry. `design.py` places everything else and
holds the tolerances. The outline is the fewest-facet (`GEM_FACETS`) convex
polygon around both halves joined. `XIAO_SPOT` pins the Xiao's position;
set it to `None` to search again, and if the board won't route completely, try
the runners-up the search writes to `xiao_alternatives.json`. `RESET_SPOT` pins the reset button and `BUTTON` holds its datasheet heights
and the plate's pocket and cone; `design.py` asserts its clearances. `PAD_SLOTS` pins the
pad slots the same way (`None` searches again for the slots that keep every key
centre deepest inside both halves' pads). `MAG_FLOOR_SPOTS` and `MAG_SIDE_SPOTS` pin the
magnets, found by `magnets.py` against the solid base around the pads, parts and screws.

Credits: the Choc hot-swap footprint follows [kiswitch](https://github.com/kiswitch/kiswitch)
(MIT). The Xiao pad positions follow Seeed's
[OPL KiCad library](https://github.com/Seeed-Studio/OPL_Kicad_Library). The reset button's pads follow
KiCad's `Button_Switch_SMD:SW_SPST_TL3342` from the
[official footprint library](https://gitlab.com/kicad/libraries/kicad-footprints) (CC-BY-SA 4.0), which
matches XKB's TS-1187A land pattern.
