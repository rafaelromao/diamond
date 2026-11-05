# Slim Diamond — fresh exported-STL mechanical/DFM review

**Disposition: the meshes are healthy, but I would not call this a proven buildable, serviceable consumer-product design yet.** The highest-priority finding is a battery-loading restriction in the trackpad floor that a seated-component Boolean does not reveal. The short Choc main-board screw joint and delicate trackball controller supports also deserve design changes or explicit prototype gates.

Reviewed 2026-11-05, independently, against the frozen binaries in `/home/romao/projects/diamond`. No physical prototype was examined. No project file was changed; no generator or project test was executed; no previous audit, source generator, or test was read. Published BUILD/BOM/README, the three design JSON files, and nominal trackball KiCad placement were used. Four assembly/underside PNGs were examined **after** the initial STL findings, when notified that renders were stable. These images were used for instruction clarity, not geometry proof.

## Scope, evidence and coordinates

- **All 24 current Slim Diamond STL files covered:** 11 printable exports, their 11 public copies, and the two hidden `.render` helpers. Older `stls/v1` and `stls/v2` are outside this request.
- Binary record lengths, SHA-256, triangle counts, merged-vertex edge incidence, connected components, winding, signed volumes, Euler characteristic and Manifold import status were checked independently. Sections, ray thickness samples, and Manifold intersections were made from the exported triangles.
- There is one solid per printable file. The two disconnected halves in `dock_halves.stl` are expected; they are **not** a broken printable unibody. All 11 public copies are byte-identical to their corresponding printable exports.
- **No detected open mesh, nonmanifold edge, reversed component or accidental physical shell split.** No zero-area triangles detected. Every binary has the expected `84 + 50 × triangle_count` length. All import as `Error.NoError`. Topological validity is not an FDM/assembly certificate.
- Dimensions below are mm. For module assemblies, XY remain the exported XY; negative Y goes toward the ball/pad/front. Shell exports are top-down: `assembled_Z = H − STL_Z`, with H = 25.470856 MX, 22.670856 Choc, 21.470856 trackpad. Floors are exported bottom-down and sit at `assembled_Z = STL_Z + 0.5`. Thus floor bottoms stand 0.5 above the desk, with 2 mm pads in 1.5 mm recesses reaching the desk.
- Dock/insert/helper meshes already share their useful XY. Modules/insert translate upward by **9.180715** to seat in the dock. Findings explicitly marked **floor STL Z** use the floor's unshifted print coordinates.
- Tiny contact residues below roughly 0.002 mm³ are treated as STL float/contact artifacts, not persuasive interference defects. This is many orders below an FDM assembly tolerance.

## Ranked findings

### 1. P1 — trackpad battery loading is obstructed by the integral adapter shelf and adjacent cradles

**Confirmed geometry/access restriction; potential assembly blocker. Not a claim of an exhaustive six-degree-of-freedom impossibility proof.**

The nominal 752025 pack fits its final bay, but the printed bay is effectively a roofed compartment with adjacent obstacles at its only ordinary opening:

- Battery final envelope, **floor STL coordinates**: X `[-12.5, 12.5]`, Y `[-93.3, -73.3]`, Z `[2.2, 9.7]` (25 × 20 × 7.5; rotated in plan relative to the generic part designation).
- Bay side rails have inner faces X = ±12.8: only **0.3 lateral clearance per side**. The front stop is at Y = −93.6.
- The integral adapter shelf underside is **Z = 10.1**, its top Z = 11.3. The battery has only **0.4 total vertical clearance** beneath it. The roof extends to Y = −73.0.
- Immediately beyond that rear opening is the reset cradle: X `[1.5,10.5]`, Y `[-71.65,-62.65]`, extending to Z = 4.2. The controller cradle rear crosswall at approximately Y = −62.5 adds another obstruction.
- At X = 6, the opening between the roof corner `(Y −73.0, Z 10.1)` and reset-cradle corner `(Y −71.65, Z 4.2)` has a diagonal separation **6.052**, less than the nominal pack's 7.5 thickness. Ordinary planar pitch does not solve this pinch.
- The battery's seated intersection with the floor is **0 mm³**. Pull it rearward by 2 mm, without any other electronic parts installed, and the floor collision is **6.300 mm³**; at 5 mm it is **31.920 mm³**. The reverse loading path is equally obstructed.
- An independent X = 6 sagittal translation/pitch search at 0.25 mm/1° resolution found no connected path from the seated rectangle to an external rear position. This is supporting evidence, not a complete 3D motion proof. Pouch flexibility must not be used as the assembly strategy.

**Why it matters:** BUILD says to assemble battery/adapter/controller/reset into the printed floor. The roof is already printed in place. “Battery fits” is not enough: a protected cell with tabs and leads must get into the chamber without compression, bending or scraping. The shelf also creates a support-removal problem (finding 4).

**Recommended correction:** make the adapter bridge a separate part installed after the battery; alternatively open a loading side and add a removable retainer, or move the reset/controller barriers sufficiently away. Demonstrate insertion and removal of the complete protected-pack envelope, including tabs, leads and tape. Until a valid rigid loading motion is supplied or the geometry changed, treat trackpad assembly as blocked for release, rather than asking an assembler to improvise with a LiPo.

**Uncertainty:** a sufficiently elaborate out-of-plane maneuver has not been exhaustively excluded. If one exists, it should be demonstrated with a rigid dummy and documented, not assumed from final-position clearance.

### 2. P1 reliability / P2 prototype gate — Choc main-PCB screws have only 1.4 mm nominal engagement

**Confirmed dimensions; stripping, torque and cycle life require physical validation. Not a detected screw-head collision.**

The common 1.6 mm PCB sits with top Z = **20.470856**, underside Z = **18.870856**. At `(X ±10.5, Y −40.1917)`:

- MX's M2 × 5 upward screw has **3.4** nominal shaft length beyond the PCB into plastic.
- Choc's specified M2 × 3 has only **1.4**: **0.7 screw diameters / 3.5 nominal pitches**, before screw-end lead/chamfer and imperfect printed entry threads.
- Choc's printed blind pilot ends at Z = **21.960856**. A nominal M2 × 3 tip at Z = **21.870856** leaves just **0.09** pilot-end margin. The solid top ends at 22.670856. Screw length tolerance, entry deformation and thread-forming debris matter here.
- Simply changing to M2 × 4 would put its nominal tip at 22.870856, **0.2 beyond the Choc exterior top**. Do not substitute a longer screw without redesigning the joint.

Independent Ø3.8 pan-head envelopes below the PCB do **not** collide with the shell. These conclusions concern shallow axial engagement and bottoming tolerance, not confusion between screw head and threaded shaft.

**Recommended correction:** provide a deeper local fastening feature or captured metal thread, or revise seat/top geometry to permit a useful, non-bottoming thread length. Keep MX/Choc screw selection unmistakable. At minimum, prototype the exact material, screw type, torque and repeated switch/PCB servicing; do not describe this as a validated durable joint.

### 3. P2 — trackball floor's controller supports are unnecessarily fragile handling features

**Confirmed slender geometry; breakage is a mechanical risk, not a measured failure.**

The nice!nano is supported by four tall, unbraced fingers near Y `[-33.8368,-29.8368]`:

- Inner fingers at X `[6.9,8.1]` and `[-8.1,-6.9]` are **1.2 × 4.0** in section, reaching floor-STL Z = 15.220856.
- Outer fingers at X `[9.3,10.3]` and `[-10.3,-9.3]` are approximately **1.0 × 4.0**, locally clipped by the perimeter, reaching Z = **16.220856**.
- The broad battery cradle reaches only Z = **5.2**. The exposed outer fingers therefore have approximately **11 mm of unsupported height**, about an 11:1 ratio relative to their weak thickness. Their root has no obvious generous fillet/gusset.

These are awkward places to push a taped controller, route ten leads, remove tape, or react a tugged USB cable. Thin upright FDM walls loaded sideways concentrate bending at layer/root joints. Tough nylon helps but does not make the geometry robust.

**Recommended correction:** use a more continuous, gusseted cradle or bridge tying the fingers together, provide positive low-force controller location and strain relief, and preserve the already-clear floor extraction envelope. Keep tape removable without levering against the fingers. Test handling and service, not just static seated clearance.

### 4. P2 — support/bridge strategy is incomplete for the trackpad floor, and support removal competes with battery access

**Confirmed unsupported spans; acceptable print quality is printer/material dependent.**

- The trackpad floor's adapter shelf starts at **floor-STL Z = 10.1**, approximately **7.9 above the floor top**. It bridges **25.6 between inner side rails** around Y = −83, with roughly **527 mm²** of downward shelf surface. The shelf is only **1.2 thick**.
- “Print floors flat” does not explain this bridge, unlike the explicit dock/trackball support instructions. A well-tuned bridge might span 25.6, but sag here consumes the battery's 0.4 vertical allowance and changes the adapter seat. Conventional support underneath is difficult to remove through the low, obstructed loading opening from finding 1.
- Trackpad shell: the pad ledge begins at print Z ≈ **1.7**, growing inward from approximately Ø40.5 to Ø36.4, an abrupt **2.05 radial horizontal overhang**. The support/quality requirement at the pad seating face is not described. It may print acceptably, but the seating face is support/overhang-sensitive.

**Recommended correction:** separate the adapter shelf as in finding 1. Chamfer or otherwise self-support the pad ledge where compatible with pad fit, or publish a tested support/bridge strategy and a ledge coupon. Inspect the sliced underside, not only the top-facing render.

### 5. P2 — 0.5 mm module magnet backings and 0.7 mm foot roofs are marginal functional skins

**Confirmed continuous skins; not unintended holes. Their robustness and as-printed continuity are unvalidated.**

- All three pointing shells' six Ø8.2 side-magnet pockets retain approximately **0.500 normal backing thickness**, sampled across the pocket discs. Representative backing-plane centers are `(±23.460, −92.0785, 7.2)`, `(±16.0583, −57.2564, 7.2)`, `(±8.6567, −22.4344, 7.2)` in assembled coordinates.
- Both module floors have a **0.700 roof** above each approximately Ø8.4 foot recess: floor-STL recess ceiling Z = 1.5, floor top Z = 2.2. This is intentional material, not a missing floor.
- A nominal 0.5 wall is about a single 0.4-nozzle extrusion path, depending on slicer width; 0.7 is only 3–4 ordinary 0.2 mm layers. Neither deserves to be treated as a durable press-fit diaphragm. Magnet seating force, adhesive shrinkage, removal, and pad compression may damage them.
- Dock side caps are much better supported than the module skins: sampled minimum backing was approximately **0.635** at the rearmost pocket and **0.744** on the other sampled pocket discs; no through-break was found. The minimum over all geometry can be lower at tapered tips, which is not the same as a broad missing backing.

**Recommended correction:** prefer approximately 0.8–1.0 or more for a deliberately durable FDM backing where space permits; thicken foot roofs if pad loads permit. If retaining these values, prescribe glue-clearance installation without force, check every skin in the slicer, and print representative coupons. All magnets in this review are the specified **8 × 1.5 N52**, not thicker substitutes.

### 6. P2 — the drawer clears geometrically but has no dependable pull purchase

**Confirmed geometry and motion clearance; ergonomic adequacy requires real retention/grip testing.**

The complete meshes of placeholder, MX, Choc and trackpad all clear a horizontal pull toward negative Y in 0.5 mm increments through 120 mm. No lifting is geometrically required. However:

- The source insert nose reaches Y = **−100.3775**; the dock reaches Y = **−96.9131**. The central nose projects only about **3.46** beyond the dock's extremity; local exposed purchase varies across the faceted front.
- There is no positive pull tab, finger recess, underside grip feature or ejection feature. Smooth flush facets are not equivalent to an accessible handle, particularly with six retained magnets and a potentially warped sliding fit.
- Pulling on a trackball (which lifts out), keycaps, cable, or a small glued component is an undesirable substitute. “Hold the dock down and pull” does not establish a reliable grip.

**Recommended correction:** retain the clean front if required, but add a recessed underside pull surface or rear/underside ejector accessible with the assembly supported. Otherwise demonstrate a comfortable front-only grip with actual magnets, realistic skin friction, and users with short nails. Do not certify carry/lap retention from magnet grade alone.

### 7. P2 — serviceability relies on unspecified wire disconnects, gravity and tape rather than service provisions

**Design/service concern, not a claim that the shell is physically split or that all service is impossible.**

The three bottom screws and separate removable floor are real and well placed. The cutaway illustrations are not physical center splits. Nevertheless:

- After removing screws the floor is essentially flush, with roughly **0.25 per-side perimeter clearance** and no obvious dedicated pry/pull provision. A floor stuck by nylon distortion, tape or a cable may tempt levering on the USB receptacle or pulling its wiring.
- The controller moves with the floor; the trackball battery and sensor move too. This is a sensible layout, but the BOM predominantly specifies hookup wire and the guide says to “disconnect wiring” without identifying service connectors. A hardwired build has soldered connections, not a tool-free disconnect. Full battery/controller replacement can become desoldering inside a cramped partly opened housing.
- The trackpad's nominal Ø40 pad has approximately **0.25 radial clearance** in the Ø40.5 top opening, with a support ledge but no evident positive retainer. The guide should specify adhesive/retention and an inversion-safe service procedure; resting on a ledge is not retention when upside down.

**Recommended correction:** provide a hidden floor removal point; define wire lengths, routing, strain relief and disconnect locations; explicitly distinguish “lower gently on a service loop” from complete separation. Specify reversible pad retention and controller/battery tape. Avoid forcing an assembler to invent these while supporting a live pouch cell.

### 8. P2 validation gate — coupled fits and support-dependent mating surfaces need coupons, not a universal clearance claim

**Validation requirement, not a confirmed nominal collision.**

- Nominal magnet Ø8.2 pockets give an 8 mm disc only **0.1 radial allowance**. Horizontal circular pockets, extrusion width, nylon moisture, and elephant's foot can consume that easily. Do not prescribe a forced press fit. Adhesive thickness can also make magnets proud.
- Bare floors and docked modules clear nominally, but a long sliding interface with small clearance and the **0.25 normal rear 45° mating gap** can bind after warp/support scarring. The modules' rear hoods and dock support must be tested as a pair.
- MX and Choc top-down shells genuinely require rear-hood support at **4.0 / 1.2 bed gap**, as BUILD says. This is not solved by the assembled 45° mating face. The support-facing hood is also a mating feature, so its roughness matters.
- Dock underside pocket: the prescribed **85 mm support span** is substantial in nylon. Support interface/sag changes stand and magnet seating. The current dock is 82.887 cm³, not the 84.4 cm³ quoted in the BOM/README; that stale number is minor but suggests the published material estimate predates the final cuts.
- Independent Ugreen-platform contact patch, adhesive retention, tipping forces, the Cirque back-component envelope, actual protected battery envelope, lens/optical height and actual USB overmold/bend radius remain physical measurement requirements. Published caveats are appropriate; none is settled by the render.

**Recommended validation:** print small magnet/pilot coupons, the hood/support mating region and the battery/shelf revision first. Then assemble real hardware and cycle drawer removal, floor service, USB insertion, switch operation and tilted typing loads. Dry nylon is necessary but not a dimensional guarantee.

### 9. P3 — specify the actual driver and screw-head envelopes

**Measured tool restriction, not inaccessible screws. Procurement/inspection issue, not a proven head collision.**

The upward main-PCB screws are reachable with the floor removed. A Ø3.9 straight cylindrical driver envelope clears the shell at both main holes; **Ø4.0 starts touching** a lower internal feature (about 0.048 mm³ at either hole), and Ø4.5 overlaps by about 6.30 mm³. Specify a slender precision driver, preferably approximately Ø3 shaft or smaller near the access passage, rather than assuming an ordinary bit holder fits.

The floor countersink mouths are approximately **Ø4.1**, with Ø2.3 clearance bores and 90° seats. Half plates have approximately **Ø6.4** head mouths and Ø3.4 bores. “M2/M3 countersunk” alone does not bound head diameter, head style or drive access across suppliers. State the allowed head envelope or a qualified part number, and verify the actual screw under-head/overall length convention. Do not convert intended shaft engagement into a supposed plastic collision.

## Fastener and assembly checks: positive evidence and limits

| Joint | Measured placement / nominal engagement | Assessment |
|---|---|---|
| Half closure | Four M3 × 8 per half; 2.5 pilot, 3.4 clearance, 6.4 head seat; total plate/PCB stack above base 3.8; nominal plastic engagement **4.2** | Sensible basic joint in nylon. Pilot depth about **4.9**, giving about **0.7** nominal end clearance. Standard machine screws forming threads in printed material still need torque/cycle validation. |
| Module floors | M2 × 6, 2.3 clearance/4.1 countersink; shell pilots Ø1.6 start at assembled Z 2.7; nominal flush-head engagement **3.8** | No head collision with floor or shell in the checked 90° envelope. Actual smaller heads may sit slightly recessed and increase engagement. Three screw stations: MX/Choc `(−20,−90),(20,−90),(0,−20.5)`; trackpad `(−20,−90),(20,−90),(−12.5,−53.5)`. |
| Shell closure posts | Ø4.6 outside / Ø1.6 pilot, approximately 1.5 radial annulus | Not missing inserts/nuts: these are expressly self-threaded printed pilots. Some are long hanging posts, so avoid high installation torque and support lateral alignment. |
| Trackball main PCB, MX | Upward M2 × 5, PCB 1.6, **3.4** nominal plastic engagement | Checked pan-head envelope clears shell. Main screws installed before switches, with floor removed, is the right order. |
| Trackball main PCB, Choc | Upward M2 × 3, **1.4** nominal engagement | Finding 2. Same PCB and same floor, not separate PCB stack assumptions. |
| Trackball sensor | M2 × 5 downward at `(−11.5,−77.9368)` and `(0.5,−65.4368)`; post tops Z 5.7, PCB top 7.3; **3.4** nominal engagement | Ø4.4 post / Ø1.6 pilot, approximately 1.4 radial wall. Nominal tip Z 2.3 vs pilot bottom 2.1 gives **0.2** end margin. Head envelopes clear the shell seated; fit them from above **on the detached floor**, not through the installed ball cup. |

Additional independent positive checks:

1. **Shell/floor closure:** MX shell–floor contact residue 0.0000059 mm³, Choc 0, trackpad 0.0000050. All bare floors clear vertical extraction sampled every 0.5 through 27 mm. This supports the actual bottom-service concept; it does not certify the fully wired/populated motion.
2. **Rigid main PCB:** the actual nominal 1.6 mm main-board polygon from JSON clears both shells seated (under 0.0000004 mm³ contact residue). An independently constructed path introducing it 9 mm toward the ball, raising to 7.5 below the seat, sliding rearward and then upward clears at 0.2 mm samples. **This check excludes socket bodies, solder and wires**; I have not independently certified the published progressive Choc *populated* path.
3. **Dock seating:** dock vs exported seated halves has only 0.00135 mm³ contact residue; dock vs Ugreen-base helper is 0. Source insert seated residue is 0.000278; all pointing modules are 0. Their complete printed bodies clear the horizontal removal sweep, not just a planar outline.
4. **Instructions:** halves' screws are installed before switches/caps, avoiding avoidable top tool obstruction. Sensor fasteners are installed while the floor is detached. The assembly/underside PNGs show the three physical closure stations and the real floor seam clearly; they do not depict a snap-fit. Dark internals and omitted wires mean those renders should be supplemented with wire-routing/service details, not treated as evidence of cable access.
5. **Ball/pad and skins:** the trackball opening/cup nominal diameter is approximately 34.4 for a 34 ball, giving 0.2 radial nominal clearance; this is plausible geometry, not a rolling-quality certificate. Trackpad top opening is approximately 40.5 for the nominal 40 pad. Foot roofs and magnet backings are physically present. Small normal-ray thicknesses at chamfer tips, pocket intersections and spherical-cut edges were not misclassified as broad accidental holes.
6. **Printing orientations:** half cases and floors are bottom-down; half plates and pointing shells are top-down. The supplied top-down half plates place their pillars/bosses upward. Half pad-slot bridges are approximately 8.6 wide; published support-free bridging there is plausible but should be sliced/printed with the selected nylon. Dock/STL minimum Z = 0.5 is a placement offset, not an absent floor: put its flat underside on the bed. The two `.render` helpers are reference assets, not printable consumer parts.

## Complete artifact inventory / hashes

The paired source and public paths in each row below have **the same complete SHA-256, byte length and mesh statistics**. This explicitly inventories and hashes all 22 printable-path files; the two separate helper rows bring coverage to 24. Volumes are mm³. All rows are watertight, consistently wound, and have zero boundary/nonmanifold edges and zero detected zero-area triangles.

| Source path | Public copy (all under `stls/slim_diamond/`) | SHA-256 | Bytes | Triangles | Euler | Components | Volume |
|---|---|---|---:|---:|---:|---:|---:|
| `slim_diamond/case/case_left.stl` | `case_left.stl` | `b8419049fdd1cc62a28dfc311d2a59c5cf2109677ed8554a26ee961fcea9f7e5` | 415184 | 8302 | 0 | 1 | 65912.748 |
| `slim_diamond/case/case_right.stl` | `case_right.stl` | `1b8406b17fb5b485b6fa3f33d9f8132b6863bb90402ffd78170760430cc9b94b` | 415084 | 8300 | 0 | 1 | 65912.747 |
| `slim_diamond/case/plate_left.stl` | `plate_left.stl` | `e0f9723ff6dd5d13f46429d282257cd223edccb076a6ed47661ec6bbd5b3b3f4` | 147084 | 2940 | −32 | 1 | 4278.883 |
| `slim_diamond/case/plate_right.stl` | `plate_right.stl` | `33d01e9ab24619b3c2157b3f8f5374982a0402638635e6828fd7b3f24e14e8b2` | 147084 | 2940 | −32 | 1 | 4278.883 |
| `slim_diamond/case/dock.stl` | `dock.stl` | `19da4b71f7b7ac768fec66f0eec66b89765127edfc3eeba754d9952ce1fc2ece` | 433484 | 8668 | 2 | 1 | 82887.486 |
| `slim_diamond/case/insert.stl` | `insert.stl` | `24c74b28f2744cc8421c31f2b46d8620b672d944b8fbb5fea349d2b677e47f4f` | 88484 | 1768 | 2 | 1 | 64493.050 |
| `slim_diamond/trackball/case/shell.stl` | `trackball_shell.stl` | `430833cc36ac8bfd05cb5dd3f124e12a03fd7ef934a7314c8ae07a5506a1564e` | 547584 | 10950 | −10 | 1 | 14261.920 |
| `slim_diamond/trackball/case/shell_choc.stl` | `trackball_shell_choc.stl` | `d9ad24b6a52fe79716c3b7d7880d2f9ba6d9b22aa2e71f91b5179dcd4f524463` | 487284 | 9744 | −10 | 1 | 12369.409 |
| `slim_diamond/trackball/case/bottom_plate.stl` | `trackball_bottom_plate.stl` | `a3f4541bd04b99862951d0fbef2a5e4706cd26151d9b8e9389ed18687f476f21` | 97984 | 1958 | −6 | 1 | 5659.415 |
| `slim_diamond/trackpad/case/shell.stl` | `trackpad_shell.stl` | `deaac06d678e3af6b2f6e5021b8a3a4c2fd3e65db2fd3a24a4ed49cfb65c75cf` | 146084 | 2920 | −18 | 1 | 11782.042 |
| `slim_diamond/trackpad/case/bottom_plate.stl` | `trackpad_bottom_plate.stl` | `e50e47f3ba1f5c77747454fe1b046879ba6087a5893b3191d5928461b461b520` | 83984 | 1678 | −10 | 1 | 6610.357 |
| `slim_diamond/.render/dock_halves.stl` | helper only | `8174bced7f7b1fb87b611ad03c5bcf1b0003d489e48c11c5c3edbb9165037597` | 830284 | 16604 | 0 | **2** | 131825.491 |
| `slim_diamond/.render/dock_ugreen.stl` | helper only | `8cf0f0bc0398f529462518e13c606d5f74120183f30cc49167725a86f6ddc960` | 10284 | 204 | 2 | 1 | 35668.775 |

Exported bounding sizes (X × Y × Z), useful for slicer sanity checks:

| Variant | Size |
|---|---|
| Either half case | 93.013 × 100.451 × 20.648 |
| Either half plate | 87.553 × 92.251 × 2.200 |
| Dock | 195.072 × 110.957 × 30.152 |
| Placeholder | 52.406 × 100.573 × 21.471 |
| Trackball MX shell, print orientation | 52.406 × 100.573 × 24.971 |
| Trackball Choc shell, print orientation | 52.406 × 100.573 × 22.171 |
| Trackpad shell, print orientation | 52.406 × 100.573 × 20.971 |
| Trackball floor including supports | 46.970 × 78.985 × 16.221 |
| Trackpad floor including shelf/cradles | 46.970 × 78.985 × 12.500 |
| Seated-half helper | 215.853 × 111.946 × 30.032 |
| Ugreen-base helper | 85.000 × 105.000 × 4.000 |

## Reproduction and limitations

Scratch evidence, written only under `/tmp/opencode`:

- `designer_review.py`: inventory/hash/mesh checks; full 24-path records in `designer-review/inventory.json`.
- `designer_sections.py`: exported-STL sections and planar-face measurements. Generated section diagrams are scratch plots, not the project's renders.
- `designer_thickness.py`: deterministic 18,000-point surface-normal ray sampling per printable variant. This locates candidate thin features; local analytic sections/rays distinguish functional skins from feather edges. It is not an exhaustive minimum-thickness proof.
- `designer_fit.py`: independent printed-part intersections, screw/head/driver envelopes, bare-floor extraction and drawer sweeps. Shaft intersections in pilot material are **expected thread-forming volume**, not interference faults.
- `designer_pcbpath.py`: independent rigid unpopulated main-PCB insertion samples.
- `designer_battery.py`: the battery envelope, rearward motion collision volumes, X = 6 sagittal search, and `designer-review/trackpad_battery_insertion.png`.

Run these with `/tmp/opencode/diamond-venv/bin/python /tmp/opencode/<script>.py`; none imports a project generator or project test. All conclusions above come from the frozen exported STLs plus explicitly identified nominal hardware/instruction data. Sampled sweeps are not continuous certified motion planning. Screw head/driver checks against plastic do not certify vendor socket bodies or solder envelopes. Electrical design, PCB DRC/fabrication quality, optical tracking, real adhesive/nylon strength, battery swelling allowance, magnetic force, print shrinkage and human comfort were not physically tested or guaranteed.

**Recommended release order:** resolve battery loading first; strengthen/qualify the Choc screw joint and controller fingers; establish support-removal/bridge strategy; then validate actual wired assembly and repeated service before considering whole-keyboard retention, stand or lap use proven.
