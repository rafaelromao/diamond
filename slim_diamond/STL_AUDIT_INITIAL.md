# Slim Diamond: independent read-only artifact audit

## Scope and method

Inspected the existing artifacts, not regenerated models. No project files were edited, no project generators/tests executed, no commits/pushes. No applicable AGENTS.md was found in the project or checked ancestor locations. All 24 STL hashes were unchanged at the end of the audit. Scratch code/results are under `/tmp/opencode`.

`/tmp/opencode/diamond-venv/bin/python` was available. Its original geometry packages included NumPy, manifold3d and Shapely; I added trimesh, scipy, rtree and networkx to that scratch venv for independent diagnostics.

Topology was checked after ordinary exact-coordinate STL vertex welding. For Boolean tests I retained the largest connected material component of each printable STL; I did not globally delete all small-area faces (that can destroy valid topology at float32 slivers). Every such material component was watertight and accepted by manifold3d. Zero-volume scraps are separately reported below. Dimensions are mm, volumes mm³. Near-zero Boolean overlaps below 0.001 mm³ were treated as float32/tessellation noise.

Assembly frames were reconstructed from STL print orientation, saved layout metadata, actual dock seating-face normals and bump-on geometry, without evaluating project generators. The actual dock gives extra tent 5.95718°, splay 12°, and drawer standing-plane height 9.18078 mm. Module shells are flipped back from their top-down exports; bottom plates are lifted 0.5 mm into their assembled positions.

## Confirmed findings, ranked

### P1 — Both front bottom-plate screw heads collide with the shell, and their intended plate seats have been cut away

Affected: `slim_diamond/trackball/case/bottom_plate.stl`, `slim_diamond/trackpad/case/bottom_plate.stl`, together with `trackball/case/shell.stl`, `trackball/case/shell_choc.stl`, and `trackpad/case/shell.stl`; all corresponding `stls/slim_diamond` copies are identical.

The front screw axes are `(x,y)=(−22,−95)` and `(22,−95)`. At the intended flush head location, assembled z=0.5, the 3D front-facet trim has removed the bottom plate around both countersinks. A 0.05 mm witness band just outside the intended 90° conical seats intersects **0.000 mm³** of bottom-plate material at both positions (rear-screw controls give 0.3038/0.3132 mm³). Only partial edge notches remain at greater heights; these are not enclosed countersunk holes.

More seriously, a standard Ø3.8 mm M2 flat head, modeled as a 90° truncated cone tapering to Ø2 mm over 0.9 mm, intersects the shell by **4.2204 mm³** at `(22,−95)`. The intended Ø3.9 mm envelope intersects each shell by **4.6427 mm³ per head**, while intersecting no bottom-plate material. Representative collision bounds are x=20.05..23.945, y=−96.010..−93.05, assembled z=0.5..1.45. This is not an intentional threaded-shaft interference: it is the screw head versus the lower front shell lip.

**Action:** move the front screws behind the actual 3D front-facet clearance boundary, or redesign the local shell/plate seating geometry. Check the whole fastener head against both printed parts, plus retained plate material around the countersink, rather than only checking pilot axes in plan. Do not rely on these two screws seating flush in the present exports.

Proof: `slim_fasteners.py`, `slim_fasteners.txt`, `slim_fasteners.png`.

### P1 — The trackpad power-switch lever passage is closed by a 0.15 mm membrane

Affected: `slim_diamond/trackpad/case/shell.stl` and `stls/slim_diamond/trackpad_shell.stl`.

At x=−2, 0 and +2 mm, the outward lever path passes through plastic at y=−15.850000..−15.699999. At the switch center height assembled z=11.15, even a conservative **1×1 mm** lever shaft from y=−16 to −12 intersects **0.1500006 mm³** of the actual shell at every tested lateral position. The membrane is visible in a direct x=0 cross-section. Example blocking point: assembled `(0,−15.75,11.15)`, or exported-shell `(0,−15.75,10.320856)`.

The switch body itself fits, so body-only clearance checks miss this. A 0.15 mm wall is not a usable open slot; whether a slicer drops it is not a reliable design provision.

**Action:** cut a continuous lever swept envelope through the completed shell/pocket and verify both travel endpoints and the intervening path. Include the lever, not just the switch housing, in fit validation.

Proof: `slim_confirm.py`, `slim_confirm.txt`, `slim_sections.png`.

### P2 — Trackpad rear bump-on recess has only a 0.20 mm roof

Affected: `slim_diamond/trackpad/case/bottom_plate.stl` and `stls/slim_diamond/trackpad_bottom_plate.stl`.

The USB clearance cut reduces the roof above the rear foot. Vertical rays at exported `(x,y)=(0,−21),(2,−21),(0,−18),(0,−24)` hit material only between **z=1.500000 and 1.700000**. The remaining thickness is **0.200000 mm**, not the documented 0.7 mm. This spans the rear Ø8.4 mm recess, rather than being a knife-edge artifact. It is essentially a single 0.2 mm layer carrying the rear bump-on; real breakage depends on print/material/load, but the geometric thickness loss is confirmed.

**Action:** restore a deliberate roof thickness without obstructing USB, e.g. move the rear foot or locally redesign the clearance/floor. Recheck the actual STL after all cuts. Update the retained-skin claim only after measuring it.

Proof: `slim_confirm.py`; `slim_thickness.json`.

### P2 — MX and Choc trackball exports have a large unsupported rear hood in the supplied print orientation

Affected: `slim_diamond/trackball/case/shell.stl`, `slim_diamond/trackball/case/shell_choc.stl`, and their public copies.

These files are top-down, but the common rear hood's first downward-facing horizontal surface begins at exported **z=4.0 mm (MX)** or **z=1.2 mm (Choc)**. It extends from y=−14.2 to +0.195553: **14.3956 mm** beyond the main rear wall. At `(x,y)=(0,−5)` a vertical ray meets no material until those heights; intersections are z=4..7.75 for MX and z=1.2..4.95 for Choc. At y=0 it is likewise unsupported below the roof. The rear tip is an open cantilever, not a bridge spanning two supports. The 45° assembled underside does not make the first printed hood layer self-supporting in this inverted orientation.

**Action:** provide local supports and a tested removal strategy, change orientation, split the hood, or redesign its printable growth. Do not assume the delivered orientation is support-free. Actual sag/finish severity depends on printer and material.

Proof: `slim_details.py`, `slim_confirm.py`, `slim_sections.png`.

### P2 — Exported STLs contain zero-area scraps and non-manifold edge incidences

Seven of eleven unique printable exports fail ordinary welded-STL watertightness because of zero-area disconnected scraps; the dock is watertight but also contains degenerate triangles. Counts are in the coverage table. Examples:

- `case/case_left.stl`: repeated vertex `(35.222622,−9.15,16.245794)` creates a zero-area edge component. Right half has the mirrored issue.
- `trackball/case/shell.stl`: 63 zero-area triangles; 58 connected components in total, of which only one has material volume. Example repeated vertex `(−8.644373,−14.2,4)`.
- Choc shell: 57 zero-area triangles, 54 components.
- `case/dock.stl`: collinear face through `(−42.398075,−71.7,4.3)`, `(−36.5,−71.7,4.3)`, `(36.5,−71.7,4.3)`.

**Qualification:** this does NOT establish missing structural surfaces or detached printable fragments. Every largest material component is individually watertight, consistently wound, positive-volume and accepted by manifold3d; all other components have zero volume. Typical slicers may silently repair them. The actual defect is non-clean interchange geometry and dependence on importer repair.

**Action:** weld/clean at the export boundary with topology-preserving handling of float32 slivers; independently reload the binary STL and require edge incidence two, no zero-area faces and the expected material-component count. Blindly dropping every tiny-area face is not sufficient and can introduce holes.

Proof: `slim_audit.py`, `slim_mesh_audit.json`.

### P3 — The dock-half helper STL is stale, and the documented extra tent is stale

Affected: `slim_diamond/.render/dock_halves.stl`; README's extra-tent figure.

The helper's floor normals imply **5.38416°**, whereas the actual dock seat normals imply **5.95718°**. Each helper half is **64,239.06 mm³**, versus **65,912.75 mm³** for the actual printable case. A helper half intersects the actual dock by **3,671.88 mm³**. Placing the actual case using the actual dock's seating planes gives only **0.000277 mm³**, numerical noise. The README still says 5.38° extra tent; the actual supplied dock gives about 12.52° total with the case's 6.56079° tent.

**Action:** retire/regenerate the stale helper alongside exports, and derive documentation figures from the published STL revision. Do not use this helper as assembly evidence. This does not imply that the PNG renders are stale: the render-scene geometry comparisons below match current STLs.

Proof: `slim_fit.py`, `slim_fit.txt`.

## Confirmed geometric concern with unproven full assembly consequence

**Bottom plates cannot drop straight down through the lower front lip.** For both trackball variants, lowering the seated plate 1 mm gives **37.5775 mm³** shell overlap. At −0.5 mm the overlap is 18.0780 mm³. Interference is at x=±23.94, y=−97.124..−92.643 near the faceted front. Trackpad lowering 1 mm gives **49.5292 mm³**, 2 mm gives **60.4605 mm³**, and the tall battery cradle keeps approximately 52.98 mm³ of interference at 5–8 mm drops.

This proves the obvious axial assembly/service path is obstructed. It does **not** prove there is no possible tilted six-degree-of-freedom path. Simple front-edge tilts also encounter interference, but I did not exhaustively search rigid-body configuration space. Components/wires mounted on these plates further constrain practical manipulation.

**Action:** explicitly design/document a collision-free bottom-plate insertion/removal path and test it with the populated module, or clearance the front lip for normal downward removal. Check this separately from horizontal module removal from the dock, which passed. Scratch `slim_paths.py` explores limited translations/tilts; it is not a completeness proof.

## Coverage: every STL

All public copies in the second column are byte-identical to the corresponding first-column export. Sizes are exported bounding-box extents. “Bad edges” means welded edges with incidence other than two. “Degenerate” means triangle area <1e−10 mm².

| Source path under `slim_diamond/` | Copy under `stls/slim_diamond/` | Size mm | Bad edges | Degenerate |
|---|---|---:|---:|---:|
| `case/case_left.stl` | `case_left.stl` | 93.013×100.451×20.648 | 2 | 2 |
| `case/case_right.stl` | `case_right.stl` | 93.013×100.451×20.648 | 2 | 2 |
| `case/plate_left.stl` | `plate_left.stl` | 87.553×92.251×2.200 | 0 | 0 |
| `case/plate_right.stl` | `plate_right.stl` | 87.553×92.251×2.200 | 0 | 0 |
| `case/dock.stl` | `dock.stl` | 195.072×110.957×30.152 | 0 | 2 |
| `case/insert.stl` (solid cover/placeholder) | `insert.stl` | 52.406×100.573×21.471 | 8 | 10 |
| `trackball/case/shell.stl` (MX) | `trackball_shell.stl` | 52.406×100.573×24.971 | 42 | 63 |
| `trackball/case/shell_choc.stl` | `trackball_shell_choc.stl` | 52.406×100.573×22.171 | 36 | 57 |
| `trackball/case/bottom_plate.stl` (shared) | `trackball_bottom_plate.stl` | 47.879×81.174×16.221 | 4 | 6 |
| `trackpad/case/shell.stl` | `trackpad_shell.stl` | 52.406×100.573×20.971 | 18 | 22 |
| `trackpad/case/bottom_plate.stl` | `trackpad_bottom_plate.stl` | 47.879×81.174×12.500 | 0 | 0 |
| `.render/dock_halves.stl` | none | 214.753×111.960×29.141 | 4 | 4 |
| `.render/dock_ugreen.stl` | none | 85×105×4 | 0 | 0 |

No separate file named cover was present: `insert.stl` is the documented solid cover/placeholder. Total coverage: 22 printable/copy files plus 2 helper STLs = **24**.

## Other tests and positive evidence

- Checked SHA-256 equality for every source/public pair and rechecked the 24 initial hashes at audit end.
- Checked bounds, signed volumes, winding, edge incidence, area degeneracy and all connected components. No inverted positive-material component or additional nonzero-volume detached component was found.
- Right case is the correct mirror about x=40.254360, vertex mismatch <=0.0000078 mm; right plate mirrors left about x=0 exactly. Plate-to-case seated clearance passed after undoing the supplied print orientation.
- Actual left case versus dock, using normals measured from the actual dock: 0.000277 mm³ overlap. Right-side mirror is geometrically equivalent. The stale helper was deliberately not used as the fit authority.
- Actual dock versus MX shell+plate, Choc shell+shared plate, trackpad shell+plate, and solid insert: zero seated overlap. Horizontal front removal sampled at 0.5 mm increments over 0..115.5 mm against the actual dock and both correctly placed cases: zero overlap for all four variants.
- Each module's actual shell versus its actual bottom plate: <=0.0000045 mm³ seated overlap, numerical noise. This is a seated-fit result only, not assembly-path proof.
- Independently constructed nominal 34 mm ball, three 3 mm bearing spheres, board substrates, battery, controller and key-body envelopes clear both trackball shell variants and the shared plate. Trackpad nominal pad, battery, adapter, controller and receptacle also clear within numerical noise. These tests use stated part dimensions and saved placements, not measured vendor hardware.
- Nominal 20.5×41×7.5 mm protected-pack envelope clears the actual keyboard case; pack swelling, wire exits and vendor dimensional variance still require measurement.
- All thirteen nominal Ø8×1.5 mm keyboard-half magnets clear the actual case. All six nominal side magnets clear each module/insert; their actual inferred centers are approximately `(±10.1532,−21.2984,7.2)`, `(±17.6380,−56.5117,7.2)`, `(±25.1228,−91.7250,7.2)`. Docked magnet height mismatch is <0.000061 mm. This establishes nominal seating/alignment, not holding force, adhesive strength or printer fit.
- Independently modeled 12.35×6.5 mm seated USB overmolds and Ø3.6 mm cables clear each module shell and the actual dock, for MX, Choc and trackpad. The full rear threading maneuver and real cable bend radius were not exhaustively certified.
- Inspected M2 bottom-plate bore cross-sections and head clearance independently; this exposed the front-seat issue above. Half M3 and internal board/sensor screw strength/torque were not physically certified.
- Random surface-normal material-thickness probes: 20,000 samples each on nine representative unique meshes, mirrored counterparts covered by exact mirror checks. Edge/chamfer knife-edge minima were not automatically treated as defects. The meaningful thin-wall findings were reconfirmed by exact rays/sections, not inferred from random minima alone.

## Render review

Inspected **all 43 PNGs** in `slim_diamond/renders` using four labeled contact sheets, with full-size spot checks of board, dock, Choc and USB cutaway views. No definite unintended object clipping/cropping was found. Board renders have tight margins but retain their outlines. The keyboard “opened” module pictures are actually x=0 cutaways, including sectioned balls/pads, not exploded removable covers; the captions would be clearer as “Cutaway”. USB cutaways intentionally retain the full plug/cable. They should not be mistaken for physical assembly access.

Parsed the saved VRML render-scene meshes independently and compared vertices against the actual exports after frame/orientation reversal: MX shell, Choc shell, trackpad shell, both module bottom plates, dock and dock-base render geometry all agree within **0.000214 mm**, consistent with four-decimal VRML rounding. Thus the principal render geometry is faithful, but it faithfully hides the same thin internal membrane/foot roof unless sectioned appropriately. The stale `.render/dock_halves.stl` is a separate cache problem, not evidence that current PNGs use stale cases.

Physical uncertainties remain: real Cirque backside/FFC geometry, sensor lens datum and working distance, bearing press/retention fit, battery tolerances/wire routing, actual USB plugs and bending, nylon shrinkage/bridges, screw engagement strength, magnet polarity/holding force, stand-platform dimensions, glue, lap load and tipping stability. None is certified by collision-free nominal CAD.

## Reproduction

From any directory, run the scratch scripts with `/tmp/opencode/diamond-venv/bin/python`:

1. `slim_audit.py`: all-file manifest, hashes and topology (`slim_mesh_audit.json`).
2. `slim_fit.py`: infer actual dock seat transform, seated fits, horizontal drawer removal and axial plate obstruction (`slim_fit.txt` captured).
3. `slim_confirm.py`: exact trackpad membrane/foot rays and trackball print-hood evidence (`slim_confirm.txt`, `slim_sections.png`).
4. `slim_fasteners.py`: seat witness bands and head/shell collisions (`slim_fasteners.txt`, `slim_fasteners.png`).
5. `slim_components.py`: independent nominal component envelopes, mirrors and bore sections (`slim_components.txt`).
6. `slim_magnets_usb.py`: actual nominal magnet alignment/seating and seated USB clearance (`slim_magnets_usb.txt`; run after `slim_fit.py`).
7. `slim_thickness.py`: independent random thickness probes (`slim_thickness.json`, `slim_thickness.txt`).
8. `slim_render_compare.py`: saved render-scene versus STL comparison (`slim_render_compare.txt`).
9. `slim_contacts.py`: four contact sheets `slim_contact_0.jpg` .. `slim_contact_3.jpg` covering all render PNGs.

No existing project test result was used as proof, and no exports were regenerated.
