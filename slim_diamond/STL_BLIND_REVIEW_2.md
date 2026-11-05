# Slim Diamond — second fresh blind product/mechanical review

**Review date:** 2026-11-05. **Repository:** `/home/romao/projects/diamond`.
**Disposition:** coherent prototype geometry, **not yet a physically qualified build**.

## Executive conclusion

I found **no confirmed new blocking STL topology, separated-floor, or bare drawer-extraction defect** in the frozen exports. All 26 scoped STLs were independently hashed and inspected. All 12 public copies are byte-for-byte identical to their printable originals. The two-component `dock_halves.stl` is appropriately a two-half rendering helper, not an accidentally fragmented print.

The most important unresolved practical issue is **the trackpad FFC's service operation**. It crosses the shell/floor boundary, but its purchased length, stored slack, bend route and explicit disconnect procedure are not defined. The guide's 30 AWG wire/service-loop prescription and PicoBlade disconnection instruction do not establish that this different cable can tolerate the first 15 mm of opening. This is a confirmed instruction/specification omission, **not proof that every possible FFC installation is geometrically impossible**.

The rest of the leading risks are prototype qualification gates, particularly real harness wire exits, the trackpad's **0.1 mm acceptance-gauge-to-bridge vertical allowance**, supported rear-hood printing/removal, actual populated-board handling, screw life, and adhesive/magnetic retention. The existing documents acknowledge many of these appropriately. I would not release this as a proven consumer-ready assembly without those tests, but I also would not demand a speculative wholesale shell redesign on this evidence.

## 1. Independence, inputs and method

- I did **not read** `STL_AUDIT*.md`, `STL_DESIGN_REVIEW*.md`, `ASSEMBLY_REVISION.md`, generators, project tests, or old temporary audit scripts. I did not follow the review/disposition links embedded in the current instructions.
- I did not execute a generator, a project test, or a pre-existing project verification script. **No source clarification was used**; all findings below remain artifact/instruction/manufacturer-based.
- Inputs read: current root `readme.md`; `slim_diamond/{BUILD,BOM,README}.md`; all three current `design.json` files; both final electrical KiCad PCBs; the 26 STLs; the 63 published PNGs; and manufacturer-origin hardware documentation. Fabrication ZIP directory contents and hashes were also recorded, but their electrical validity was not independently certified.
- New analysis files only were written under `/tmp/opencode`, using the `blind2_` prefix, plus this requested report. No project edit, regeneration, commit, push or other agent was used.
- Tools: independent Python using `trimesh`, `numpy`, `manifold3d`, Pillow and Matplotlib; a small independent KiCad S-expression reader; `pdftotext`/`pdftoppm` for manufacturer documents.
- Mesh checks merge coincident STL vertices without a winding repair. They check edge incidence, watertightness, winding, positive component volumes, degeneracy and Manifold acceptance. Raw binary facet normals were additionally compared with triangle cross products: no reversed or zero stored normals in the 14 distinct assets. Public duplicates have identical bytes.
- Geometry intersection results below concern the **exported solids**, not generator intent. A numerical contact sliver below `0.00001 mm³` is treated as float32 contact noise, not a physical clash.

### Coordinate reconstruction — important

All coordinates below are millimetres. Module X/Y are the exported module plan coordinates: front/ball/pad is toward negative Y, rear USB is toward increasing Y. The supplied shells are top-down prints:

| Part | Reconstruct assembled Z from print STL |
|---|---|
| Trackball MX shell | `Z = 25.4708560147435 - Z_print` |
| Trackball Choc shell | `Z = 22.6708560147435 - Z_print` |
| Trackpad shell | `Z = 21.4708560147435 - Z_print` |
| Either bottom plate | `Z = Z_print + 0.5` |
| Trackpad bridge | `Z = Z_print + 11.0` |

The floor's **+0.5 mm** is essential: its 2.2 mm print-space perimeter top seats at the shell's assembled Z=2.7 mm ledge. Treating a bed-normalized floor as already assembled understates its component heights by 0.5 mm. With 2 mm feet seated against Z=2.0 mm recess roofs, the standing plane is Z=0 as published.

The drawer samples used the README's published module standing-plane elevation **9.181 mm**, rather than assuming the module print bed is the drawer floor. This rounded value is adequate for the sampled clearance check, not an exact seating/adhesive tolerance specification.

## 2. Ranked findings and recommendations

### R1 — Medium: explicitly engineer the trackpad FFC service operation

**Classification: confirmed instruction/specification defect; unproven geometric blockage.**

**Evidence:** `BUILD.md:232–236,247–256,293–301,314–330`; `BOM.md:73`.

- The pad is retained to the shell; the adapter is taped to a removable bridge on the floor. Their FFC therefore remains a shell/floor tether when opening.
- The BOM specifies only 12 positions/0.5 mm pitch and a generic 20×14 mm adapter. It does not specify the FFC length, stiffener/thickness, exact adapter connector, installed contact orientation or a slack-storage route.
- The service instruction permits lowering the floor up to 15 mm and then disconnecting the identified friction-lock connectors. It does not explicitly tell the builder **which FFC end to disconnect, how, or how the initial opening is accommodated**. The 25 mm loop specification is given with flexible stranded hookup wire; it cannot simply be applied to a flat cable with reinforced ends.
- Cirque's TM040040 specification v1.2, p.9, identifies its connector as **Molex 78127-1128, vertical, non-ZIF**. That end needs axial cable withdrawal/support; it is not a generic rear-facing flip-latch connector. A purchased adapter may have a different latch operation.
- Nominal pad data also differs from a featureless thin disk: **0.99 mm PCB+overlay and 5.15±0.20 mm total PCB+overlay+components**, with component keep-out/alignment information on pp.6–7. The README correctly calls real back-component fit unconfirmed.

**Practical failure mode:** an otherwise plausible short FFC can work closed but become the opening stop before the PicoBlades are reachable. Following “disconnect the connectors, then separate” can then pull on the pad retention, cable stiffener or non-ZIF receptacle. A longer unspecified cable can instead become a trapped fold over the bridge/battery/seam. Neither is resolved by a seated adapter box.

**Recommended correction:** choose a specific adapter and FFC; publish a contact-side drawing, installed routing/slack drawing and service sequence. State that the floor is lowered **only until cable slack permits**, never automatically 15 mm. Prefer a defined accessible adapter-end disconnect, with the latch and stiffener gripped/supported correctly. Prove the closed cable-storage volume and the first opening/withdrawal envelope, then cycle a powerless assembly. Do not adopt an arbitrary cable length without checking both states.

### R2 — High-priority qualification gate: real harness exits and hand access remain unproved

**Classification: physical/harness validation gate, not a confirmed impossible layout.**

The prescribed seated body boxes clear the exported shell and floor, but the two larger pairs are packed almost end-to-end:

| Pair | Accepted envelope, assembled coordinates |
|---|---|
| Trackball 10-way | X −7.35..7.35, Y −50.7..−41.3, Z 11..14.5 |
| Trackball 9-way | X −6.75..6.75, Y −60.7..−51.3, Z 11..14.5 |
| Trackball pack 2-way, rotated across X | X 3.3..12.7, Y −65.9..−61.1, Z 8..11.5 |
| Trackpad keys 3-way | X −3..3, Y −52.2..−42.8, Z 8..11.5 |
| Trackpad switch 2-way | X −2.4..2.4, Y −62.2..−52.8, Z 8..11.5 |
| Trackpad pack 2-way | X −8.9..−4.1, Y −72.2..−62.8, Z 3.1..6.6 |

There is only **0.6 mm longitudinal separation** between the accepted 10/9-way boxes, and between the trackpad key/switch boxes. Actual nominal housing lengths are 9 mm, so the physical housings have slightly more separation, but neither number includes a complete wire-exit bend, wire bundle or gripping tool. This is not an assertion that 30 AWG wires cannot be staggered or routed vertically/laterally.

The selected hardware family is credible: the Molex catalogue independently confirms 51047 mates with 51021, 9 mm mated length, 3.3 mm housing height, widths **14.25/13.0 mm** for 10/9 circuits, and appropriate male/female terminal families. The tolerance envelopes are not obviously fictional connector dimensions.

**Positive service evidence:** once a connector moving with its floor is lowered 15 mm, the trackball larger connector boxes end at Z=−0.5, below the shell's Z=0.5 lower edge; the trackpad larger boxes end at Z=−3.5. There is then substantially better axial handling access. Additional ±3 mm X / ±4 mm Y body-operating corridor bounds also cleared shell plastic in the tested locations. Thus the intended **lower-before-unmating** strategy is sensible. It still depends on the shell-side leads actually supplying the opening slack, and the floor-side connector being located/retained accordingly.

**Recommended acceptance test:** build the exact pre-crimped harness with its actual insulation OD; identify and retain the connector bodies on the appropriate moving side; mark 15 mm opening travel; demonstrate housing grip and axial separation without pulling wires. Photograph wire exits, folds and strain relief closed and open, including FFC operation separately. Qualify the soft lacing/tape anchors without using the LiPo as an anchor. The current words about flexible wire, soft lacing, no seam crossing and battery-only disconnect are good; a routed harness drawing is the missing practical evidence.

### R3 — High-priority fit gate: trackpad protected-pack/tape stack has very little roof allowance

**Classification: measured tolerance/pack validation gate, not a confirmed nominal interference.**

- Independent rigid gauge: **25×21×7.8 mm**, X −12.5..12.5, Y −93.3..−72.3, Z 3.1..10.9.
- It has **0 mm³** intersection with the actual detached floor and the installed bridge.
- Bridge-post seats are at **Z=11.0**; bridge thickness is **1.2 mm**, so its underside is only **0.1 mm above the 7.8 mm gauge** where it covers the battery.
- Nominal 7.5 mm cell height has 0.4 mm geometric allowance, but real protection tabs, tape, lead exit, print error and the prescribed removable tape strap must all be accounted for. A rigid gauge without the final strap stack is not the complete installed pack envelope.

**Recommended correction/acceptance:** retain the battery-first/removable-bridge architecture; it is materially better than forcing a pack under a fixed roof. Specify whether the 7.8 mm limit includes insulation/retention tape and the actual vertical clearance target. Gauge the printed assembly with that complete stack before fitting a cell. If reliable manufactured clearance is inadequate, raise/recess the bridge or choose a thinner verified pack rather than compressing the pouch. Keep the bridge screw/tool paths outboard of the pack, as they currently are.

### R4 — Low: the root public STL list omits the mandatory trackpad bridge

**Classification: confirmed publication omission.**

Root `readme.md:55–56` links the trackpad shell and bottom plate but not `stls/slim_diamond/trackpad_adapter_bridge.stl`. The public bridge file exists and is correct, but a builder following only the root download list receives an incomplete set for the current adapter/battery assembly.

**Correction:** add the bridge to that trackpad download line and call it a required third print, not an optional replacement floor.

### R5 — Low: magnet-count and floor-render captions need a small consistency pass

**Classification: confirmed instruction/render-caption defects.**

- `BUILD.md:150` says the optional dock takes **34 discs total**. `BOM.md:25–31` correctly includes the new upward-facing drawer-floor mate and specifies **35**. The BUILD line's listed groups also add to 34 because it omits that extra mate; the later BUILD floor-retention paragraph does identify it. Unify the count so the builder does not order one short.
- Both `trackball_floor.png` and `trackball_choc_floor.png` carry the footer **“remove trackpad bridge BEFORE lifting the battery”**. Those are trackball floor views and contain no trackpad bridge. Restrict that caption to the trackpad floor view, or use a generic warning in the shared footer.

These do not make the meshes unprintable. The engineering contrast colors are intentional and helpful; they are not a finding.

## 3. Mechanical coverage and positive evidence

### Main keyboard halves and plates

- Each case is approximately **93.013×100.451×20.648 mm**, **65.913 cm³**. Each plate is approximately **87.553×92.251×2.2 mm**, **4.279 cm³**. Both cases are single solids; the left/right two-triangle triangulation difference is not a fragmentation or volume defect.
- Plate construction is consistent with the documented **1.2 mm Choc plate + 1.0 mm PCB gap**, 14.0 mm openings and top-face-down print orientation. There is no basis here for treating intentional screw thread bite in a 2.5 mm pilot as a clearance collision.
- M3×8 overall flat-head length minus the documented plate/gap/PCB stack gives approximately **4.2 mm nominal base engagement**. Actual pilot/countersink reproduction, thread forming and repeated service in dried Nylon remain coupon/torque tests. The specified head-envelope limit matters; a purchased ISO/DIN-labelled screw is not accepted merely because its thread is M3.
- The halves' battery-first, plug-before-lowering sequence is physically sensible: the battery is not asked to pass through a closed PCB aperture; the populated board approaches open-top part pockets; the lever slot opens toward the loading direction. Protected 702040 packs still require actual tab/lead measurements, not just a nominal pouch designation.
- Half feet: 2 mm pads in 1.1 mm deep alternating slots project 0.9 mm. The published complementary-end stacking scheme is coherent. Adhesion, real domed pad dimensions and rocking need a physical stack test. Independent-stand clear-patch size, actual stand geometry, magnetic pull, adhesive and typing/tipping loads are correctly left unqualified.

### Trackball MX and Choc assembly

- Shells are real single-piece cups/plates with removable inset floors, not horizontally split shells. The **same floor seats without material interference** in MX and Choc. MX/floor contact noise was `0.0000053 mm³`; Choc/floor was zero.
- The assembly order correctly keeps switches/caps out while introducing the populated socket PCB from below, and installs keys after the board is seated. The documented rearward/upward manoeuvre is more credible than a fictional straight push through the upper plate.
- Final KiCad corroborates the alternative socket placement and main mounting centres **(±10.5,−39.8536)**. The MSK power-switch footprint's signal pads are on **F.Cu**; the socket pads are on **B.Cu**. Do not transfer the keyboard-half “all parts face down” assumption to this board's power switch.
- Main-PCB geometry measured at those screw centres: seat at **Z=20.470856**, **0.8 mm** shoulder up to Z=21.270856, then the open nut well. With a 1.6 mm PCB, 1.6 mm nut and M2×5 pan screw, the nominal full metal thread and roughly **1 mm tip beyond the nut** are coherent. On Choc, the 22.670856 mm plate makes the tip about **1.2 mm proud**. Check the actual chosen cap skirt/travel and nut fit; this is not a blind pilot that inevitably bottoms out.
- Sensor-board supports were measured at the **actual final PCB** SH1/SH2 positions **(−11.5,−77.9368)** and **(0.5,−65.4368)**: assembled **Z=6.1**, giving PCB top **Z=7.7**. M2×5 screws from that top have approximately **3.4 mm printed-post engagement**.
- The reset at **(8,−65.736806)** is on the sensor board's underside: its nominal 2 mm plunger projects down to **Z=4.1**. It is therefore **below**, not in conflict with, the pack connector at Z=8..11.5. Independent reset-body and Ø1.1 straight-pin envelope intersections with that accepted connector box were zero. Confusing the taller controller supports with the sensor seats would generate a false collision.
- The pack connector is only **0.3 mm above the sensor PCB's bare top plane**; solder, component and screw-head location matter. Its X extent starts at 3.3 mm; the nearby SH2 head bounded to Ø3.8 ends at X=2.4, leaving **0.9 mm nominal X separation**. This is reasonable seated placement, not proof of every wire route or connector grip.
- Controller support steps distinguish the USB region (**Z=12.220856**) from the higher PCB support (**Z=15.720856**). The blue board in the render is not evidence that the board/components can be replaced with a full-height solid box. Real nice!nano/clone underside components and solder still need checking.
- Trackball/lens optical height, real PMW3610/LM18 stack, cup-to-ball clearance and bearing glue seating remain physical fit/function gates. The loose lift-out ball should be removed before inverting the assembly for servicing.

### Trackpad assembly

- Shell/floor are actual separate solids. Seated intersection was `0.0000044 mm³` contact noise. The adapter bridge is an independent **36.6×20.6×1.2 mm**, **0.725 cm³** print.
- The detached floor gives genuine top loading and removal of the pack with the bridge off. Bridge screws at approximately **(±16,−83)** are outboard of the 25 mm-wide gauge. M2×4 screws through the 1.2 mm bridge provide approximately **2.8 mm nominal pilot engagement**. They are not driven over the pouch.
- The face-up controller, reversed underside reset switch and separate switched-battery harness are practical arrangements if the real components, insulation and wires fit. The rear switch's body retention is tape, not an unseen printed snap; its full travel, finger/tool purchase and terminal insulation must be proved after taping.
- Pad support/retention is no longer merely “rest a disk on a ledge”: three reversible adhesive dots and an inside removal procedure are specified. That is a plausible prototype strategy. Actual adhesive thickness, compatible bond surfaces, pad orientation/back-component keep-out and retention during inversion are still unqualified; see R1.

### Closure, floor removal and tools

- Each module has three underside countersunk closure joints. With floor bottom Z=0.5, floor top/seat Z=2.7 and M2×6 overall screw length, the tip is at about **Z=6.5**: approximately **3.8 mm nominal pilot engagement** above the seat. This is not the separate PCB/nut joint.
- The specified **Ø≤3.9×≤0.95 mm, 90°** closure-head and **Ø≤3.8×≤1.2 mm** pan-head constraints are meaningful. A generic M2 fastener or 4 mm bit holder is not an access substitute. Qualify the actual purchase against these dimensions and use the stated ≤3 mm precision shaft.
- Bare floor extraction was independently sampled downward **0..30 mm in 0.5 mm increments**, for MX, Choc and trackpad. All samples were clear apart from the seated numerical contact noted above.
- This is **not complete populated-floor path certification**. Boards, actual wires/FFC, solder, tape, plug housings during handling, human fingers and compliance were not all swept as validated physical models. A powerless dry build is required, particularly for the multi-stage main-PCB manoeuvre.

### Drawer, bottom retention and pull purchase

- Placeholder, all three shells and both floors were individually intersected with the actual dock at the published seating elevation, then sampled in horizontal negative-Y withdrawal **0..110 mm at 0.5 mm increments**. The six component checks at all sampled positions were zero. This supports the intended slide-out concept without lifting; it is not continuous-path certification, a friction model or a populated/cabled operation test.
- The floor retention pocket at **(13,−68)** is real. Its measured floor backing is **0.9 mm**: floor-magnet pocket ceiling Z=2.1, outer backing top Z=3.0. It does not replace the side row. Flush/recessed glue seating, not forcing an 8 mm disc into an undersized hole, is the correct approach.
- The front ribbon is a genuine grip provision rather than a request to pull the ball, caps or USB cable. The sampled underside front recess depth is **0.34 mm** in the exported floors (nominal instruction 0.35). The **≤0.25 mm** ribbon limit leaves only about 0.09 mm before accounting for adhesive if flushness is required. Qualify the adhesive layer and bond length on the selected filament. The placeholder's standing/sliding drag needs its own check.
- Seven magnets/module, 8×1.5 N52 nominal, do not establish a carry/lap retention rating. Side-wall friction, floor-face gap, recess/adhesive thickness, loads and peel moments must be measured. The instruction to hold the dock down while pulling horizontally is appropriate.
- USB service procedure sensibly removes the module first, feeds the chosen plug through the rear passage and slides in while feeding cable. The stated 12.35 mm overmold within a 12.8 mm passage leaves only **0.45 mm total width allowance**. Real plugs, cable bend radius and externally restrained cables are still gates. My drawer sweeps did not certify a flexible USB cable path.

### Printability, skins and support removal

- Bases/floors/bridge/plates have sensible supplied print orientations. The bridge is a flat separate print; there is no reason to request support extraction from inside a closed battery roof.
- MX/Choc rear hoods do require build-plate support in their top-down orientation, with documented **4.0/1.2 mm initial gap**. The support must not invade the ball/switch openings or nut wells. A 45° assembled hood/dock interface does not eliminate the top-down printing problem. Test-print the hood and its support-removal route; current prose correctly does not claim that test has passed.
- Floor rays at the three trackball foot centres measured **Z=2.0..3.1**, hence **1.1 mm local roof**, not a guessed 0.7 mm. The trackpad rear foot has the same 1.1 mm roof; its forward foot regions merge into taller cradle/post material. The floor-magnet backing is 0.9 mm on both floors.
- Thin **0.5/0.6/0.9 mm** documented skins require deliberate slicing/line-width inspection. At 0.2 mm layers, a 0.9 mm horizontal backing is only roughly 4–5 layers; a 0.6 mm vertical skin should not be assumed to become two ordinary 0.4 mm walls. Check the actual slicer's variable-width/thin-wall output and pocket continuity. These are manufacturing gates, not evidence of non-manifold geometry.
- The dock's broad stand-pocket roof (documented **85 mm span**) needs accessible support and a warpage/mating-surface check. Its underside opening makes support removal conceptually accessible, but no actual support job or Nylon print was inspected. Test dock bending/torsion only on this cut-out revision; do not reuse earlier stiffness numbers.

## 4. Frozen STL inventory, equality and topology

**Coverage:** 12 printable originals + 12 public counterparts + 2 hidden render helpers = **26**. `stls/v1` and `stls/v2` were excluded. All hashes were re-read at the end and were unchanged.

All 26 are watertight, consistently wound, have zero non-two-manifold edges and zero detected degenerate faces, and are accepted by Manifold. Every connected component has positive signed volume. All prints have one component. Euler characteristics below describe intended apertures, not failed meshes.

Paths in the table are relative to `slim_diamond/`. The public counterpart is under `stls/slim_diamond/` with the listed name and **exactly the same full SHA-256**.

| Original | Public name | Faces | Components | Volume cm³ | Euler | SHA-256 |
|---|---|---:|---:|---:|---:|---|
| `case/case_left.stl` | `case_left.stl` | 8302 | 1 | 65.913 | 0 | `b8419049fdd1cc62a28dfc311d2a59c5cf2109677ed8554a26ee961fcea9f7e5` |
| `case/case_right.stl` | `case_right.stl` | 8300 | 1 | 65.913 | 0 | `1b8406b17fb5b485b6fa3f33d9f8132b6863bb90402ffd78170760430cc9b94b` |
| `case/plate_left.stl` | `plate_left.stl` | 2940 | 1 | 4.279 | −32 | `e0f9723ff6dd5d13f46429d282257cd223edccb076a6ed47661ec6bbd5b3b3f4` |
| `case/plate_right.stl` | `plate_right.stl` | 2940 | 1 | 4.279 | −32 | `33d01e9ab24619b3c2157b3f8f5374982a0402638635e6828fd7b3f24e14e8b2` |
| `case/dock.stl` | `dock.stl` | 8860 | 1 | 82.803 | 2 | `ecacd2c7d66482015c98d44fcd02f2be2b0be1dad96718f25db830ad168e186e` |
| `case/insert.stl` | `insert.stl` | 1784 | 1 | 64.428 | 2 | `560bf24db651df285848669ffdd421a34e3a4f0dbb4b2ed4beb708c8871f0479` |
| `trackball/case/shell.stl` | `trackball_shell.stl` | 10974 | 1 | 14.340 | −18 | `f57fe658a504167ac1422288515b12d590c41e95fefe42955e22224d16ac6c86` |
| `trackball/case/shell_choc.stl` | `trackball_shell_choc.stl` | 9856 | 1 | 12.475 | −18 | `d432c113588fb58b0e378106131f0e59a5eabe8086f460bbc1998e158258c1f1` |
| `trackball/case/bottom_plate.stl` | `trackball_bottom_plate.stl` | 2894 | 1 | 6.219 | −8 | `b9f8a70d8f5fb3c4da05b4f01a4b56b6b1df690189a9f01a61c5857fcad27ed2` |
| `trackpad/case/shell.stl` | `trackpad_shell.stl` | 3608 | 1 | 11.816 | −18 | `8f9e6bcf81d81a607a974e98f744d2569366d18ccd601facaf7c2383a11a9417` |
| `trackpad/case/bottom_plate.stl` | `trackpad_bottom_plate.stl` | 2896 | 1 | 6.250 | −10 | `ef1656d1dfdd2aed993d4ca9158267a839afc505d6e77c3a57cdf04e53eaa487` |
| `trackpad/case/adapter_bridge.stl` | `trackpad_adapter_bridge.stl` | 684 | 1 | 0.725 | −2 | `70eada31ac4fa2371496220f198a0359013b9c83327e6ca2ad59edc2a872082e` |
| `.render/dock_halves.stl` | render helper only | 16604 | **2** | 131.825 | 0 | `8174bced7f7b1fb87b611ad03c5bcf1b0003d489e48c11c5c3edbb9165037597` |
| `.render/dock_ugreen.stl` | render helper only | 204 | 1 | 35.669 | 2 | `8cf0f0bc0398f529462518e13c606d5f74120183f30cc49167725a86f6ddc960` |

`blind2_inventory.json` retains exact bounds, bytes, face/vertex counts, component volumes, hashes and topology per **all 26 paths**, including the duplicate public paths. The separate artifact hash manifest records all **63 PNGs**, current documents/JSONs, both electrical PCBs and both fabrication ZIPs.

## 5. Render and instruction coverage

All **63 current PNGs** were visually reviewed on six labelled contact sheets; the key structure, seam, battery, floor, assembly, underside, rear and USB views were additionally examined at useful detail where needed. These are published artifacts, not newly generated project renders.

- The grey shell/blue floor/amber bridge/orange screw views depict actual separately exported solids and correctly communicate the inset underside floor. I did not infer an impossible horizontal seam from the arbitrary illustrative cutaways.
- The assembled underside views show the three closure heads and the textile pull, and the exploded 30 mm illustrations are expressly distinguished in BUILD from a wired service position.
- Rear/reset views make the control locations legible and distinguish an orange reset tool from a printed plunger. The explicit remove-from-dock reset instruction is important.
- The main visual limitation is absent real wiring/FFC/tape details. Clean render space is not evidence that the cable operating envelope has been allocated; see R1–R2.
- Cosmetic contrast colors, exposed prototype hardware and deliberate cutaways were not treated as manufacturing defects. The two incorrect trackball floor footers are the specific render problem found.

## 6. Reproduction and evidence files

Run from any working directory; these scripts read the absolute repository paths and write only the new scratch evidence:

```sh
/tmp/opencode/diamond-venv/bin/python /tmp/opencode/blind2_inventory.py
/tmp/opencode/diamond-venv/bin/python /tmp/opencode/blind2_pcb.py
/tmp/opencode/diamond-venv/bin/python /tmp/opencode/blind2_mechanics.py
/tmp/opencode/diamond-venv/bin/python /tmp/opencode/blind2_service.py
/tmp/opencode/diamond-venv/bin/python /tmp/opencode/blind2_final_checks.py
```

Main outputs:

- `/tmp/opencode/blind2_inventory.json` — all 26 STL records.
- `/tmp/opencode/blind2_artifact_hashes.json` — 74 associated published/input artifact hashes.
- `/tmp/opencode/blind2_mechanics.json` — shell/floor, drawer samples, connector boxes, section/seat measurements.
- `/tmp/opencode/blind2_service.json` — independent sensor-seat/reset/pack-connector check.
- `/tmp/opencode/blind2_final_checks.json` — gauge, foot roofs, floor magnet backing, connector operating-corridor bounds and end-of-review STL hash stability.
- `/tmp/opencode/blind2_pcb.json` — independently parsed final PCB component/pad coordinates and PCB hashes.
- `/tmp/opencode/blind2_sections.png`, `/tmp/opencode/blind2_plan_sections.png` — actual exported-solid sections in the reconstructed assembly frame, with prescribed connector-box overlays.
- `/tmp/opencode/blind2_contact_1.jpg` through `_6.jpg` — all 63 published renders with names.
- `/tmp/opencode/blind2_independent_findings.md` — artifact-stage independence checkpoint, including the rejected false reset collision.

Manufacturer references used:

1. **Cirque, TM040040 Trackpad Specification, v1.2 (2017)**, pp.6–9,12–13. Manufacturer document hosted by distributor: <https://keycapsss.com/media/43/54/77/1758718807/tm040040_spi-i2c-pinntrackpad_spec1-2-1223705.pdf>. Download `/tmp/opencode/blind2_tm040040.pdf`; extracted text and mechanical drawing are adjacent with the same prefix.
2. **Molex 51047 catalogue sheet**, mating dimensions and ordering table, manufacturer-origin catalogue hosted by distributor: <https://www.talmir.co.il/gallery/1501883128.pdf>. Download `/tmp/opencode/blind2_picoblade_catalog.pdf`, text and PNG adjacent. Molex's direct URLs did not fetch reliably, so this is not a claim that the newest drawing revision was retrieved.
3. **nice!nano manufacturer documentation and pinout/schematic:** <https://nicekeyboards.com/docs/nice-nano/> and <https://nicekeyboards.com/docs/nice-nano/pinout-schematic>. Photo/pinout/schematic saved with the `blind2_nicenano` prefix. The manufacturer specifically cautions against components/pins puncturing a battery; a clone is not automatically equivalent in envelope.

## 7. Explicit limits and release gate

- No physical prototype, slicer toolpath, material coupon, support-removal trial, mating-cycle, screw-torque/life, adhesive peel, magnet force, lap-load or drop test was available.
- The motion checks are **discrete samples of stated rigid paths**, not a proof of every intermediate configuration or of human ability to execute the populated-board manoeuvre.
- Only the stated connector body/operating-corridor bounds were checked. Actual individual male/female housing geometry, split unmating stroke, gripping fingers/tweezers, crimp exits, every wire, solder blob, FFC and USB cable were not certified as a complete assembly model.
- The KiCad files were used to identify nominal hardware, sides and placement. I did not independently approve routing, DRC, netlists, charger configuration, firmware or fabrication correctness. ZIP hashes/listings are coverage evidence, not electrical sign-off.
- Envelopes, nominal engagement and skins are not strength or fatigue ratings. In particular, intentional screw thread engagement is **not clearance interference**.
- Generic protected cells, nice!nano clones, Cirque overlays/adapters, keycap skirts, silicone feet and USB overmolds vary. The cited nominal BOM is not a universal interchangeability specification.

**Recommended next physical gate:** prove the trackpad floor/bridge with a complete insulated rigid pack gauge and an explicitly routed/serviceable FFC; then perform a powerless populated MX and Choc assembly/service cycle with the purchased harness and fasteners. In parallel, test-print/support-remove the hood and qualify ribbon/magnet/pilot coupons. Only after those succeed should the full dock and retained battery builds be treated as mechanically qualified.
