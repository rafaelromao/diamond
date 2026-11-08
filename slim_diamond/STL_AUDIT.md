# STL audit follow-up

**Current status: revised prototype, physical qualification still open.** The
[frozen blind designer review](STL_DESIGN_REVIEW.md) prompted the removable bridge,
metal-thread main-PCB joints, reinforced controller frame, thicker skins, direct
floor retention, power/reset access and service provisions documented in
[the current disposition matrix](ASSEMBLY_REVISION.md). Follow that matrix and
the current BUILD/BOM, not the superseded dimensions in this historical log.

## Earlier audit dispositions (superseded where noted above)

The [initial independent artifact audit](STL_AUDIT_INITIAL.md) examined all 24
STLs and 43 rendered PNGs without running the generators or changing project
files. It found two assembly blockers and several service/export defects.

## Source fixes and regression gates

| Finding | Disposition | Regression |
|---|---|---|
| Front flat-head screws collide with shells / incomplete seats | Front screws moved inward to (±20, −90); complete countersinks include 0.1 mm radial clearance | `test_module_assembly`: shell/plate clearance and full annular seats |
| Trackpad lever blocked by a 0.15 mm membrane | Recut the full lever passage after adding the switch support | `test_module_assembly`: swept lever samples |
| Rear foot roof only 0.2 mm | Feet moved forward of USB clearance and away from countersinks; modeled roof 0.7 mm | `test_module_assembly`: ≥0.6 mm complete roof |
| Trackball hood unsupported in top-down print | Explicit build-plate support requirement in README, BUILD and BOM; slicer inspection and test-print required | Physical printing/support removal still unverified |
| Zero-area STL scraps / importer-repair dependence | Weld float32 coordinates, remove zero-volume boundary scraps, simplify topology at sub-micron tolerances; preserve real sliver faces and void boundaries | `test_stl_export`: actual binary-STL area, edge incidence, winding and volume |
| Stale dock helper | Regenerate both helper STLs with current placement; update extra tent to 5.96° | Actual-STL replay: combined overlap 0.00136 mm³, float32 coplanar-surface noise (previously 7343.76 mm³) |
| Populated floor cannot drop through front lip | Use narrowest-facet service envelope; relocate battery/cradles; both MCUs now travel with their floors; rear screw post stops below USB | `test_module_assembly`: populated floor drop, 0.5 mm steps through 40 mm |
| “Opened” views imply a service position | Relabel as cutaways; document gentle floor lowering with wire slack and disconnection before full separation | README / BUILD |

All geometry regressions use modeled envelopes, not measurements of purchased
parts. They do not establish bearing/lens performance, magnetic holding force,
printed tolerances, wire strain, support removability, platform fit or load
stability. Firmware has not been compiled or tested on hardware.

## Export verification

The independent follow-up agent exhausted its usage limit before producing a
second report. Its preliminary 24-file mesh manifest was retained in scratch
storage; the implementor then reran that manifest and replayed the artifact
measurements locally. This is **not a completed second blind review**.

- All 24 persisted STLs: watertight, consistent winding, no bad welded edges,
  no zero-area faces; all eleven public copies match their source files.
- Actual STL screw-head clearance and complete annular seats pass for all
  three module shells. All feet retain a complete ≥0.6 mm roof witness.
- Actual STL floor drops and horizontal module extraction pass in 0.5 mm steps;
  the trackpad lever witnesses are clear. Populated-floor checks additionally
  pass against the source component envelopes in `test_module_assembly`.
- These tests do not certify slicer output or physical assembly.

## PCB and render gate

The rearward 270° trackball layout was regenerated and routed afresh, preserving
only the unchanged sensor circuit's verified copper. Final KiCad DRC reports
**zero errors and zero unconnected items**; the keyboard-half board also passes
those gates. Non-blocking library-reference, dangling-via and silkscreen warnings
remain. Gerbers/drills and 1:1 prints were refreshed from the final routed board.
The trackball panel remains 35.497 × 76.6368 mm.

KiCad's SWIG collection iterators became invalid when queried after object
removal during main-only routing export. Snapshotting zones, footprints and
tracks before mutating the temporary board fixes the reproducible crash.
DSN export also treats vias/pour-only keepouts as track obstacles, so antenna
rules are excluded only from that temporary router input and retained in the
master board for final DRC. Explicit outboard socket escapes keep vias away
from the antenna; the battery's front-face route clears both socket families.

Rendered views were visually checked via contact sheets, with enlarged inspections
of the USB views, MX/Choc rims and cutaways. The rearward-key renders exposed
cropped rear edges in the closed trackball views; their zoom was reduced and
the corrected views checked again. Board renders were refreshed after routing.

## Additional requested changes

- Full 12.8 mm dock USB cut through the underside; plug sweep uses normal
  orientation, not an edge-on threading maneuver.
- Keys move 3.8 mm rearward on the trackball, 4 mm on the trackpad. The trackball MCU
  now stops at y = −60.8 mm for populated-floor removal, rather than the earlier
  −58.4 mm seated-only fit. Maximum 1.5 mm side bevel retains the switch rim.
- Six seam magnets at 17.8 mm pitch; inserts use alternate magnets at 35.6 mm.
  All magnets remain 8 × 1.5 mm N52; no rear retention magnet.
- [Flex research](trackball/FLEX_FEASIBILITY.md) remains feasibility-only;
  rigid boards and wires are the release baseline, not an unvalidated flex PCB.

## Assembly and rear-shoulder correction

The prior checks omitted the trackball power-switch body, all fastener render
models and a populated main-PCB insertion path. They also excluded the controller
from floor removal because it sat on shell ledges. Those omissions made the
cutaway misleading and did not prove that the internal stack could be assembled.

The current revision removes those ledges, carries the controller on the floor,
clears the main PCB outline around low magnet bosses, and checks both socket
families through explicit rigid insertion paths. The power-switch body and full
slider travel are now included; a local roof pocket clears the Choc switch body.
Its rear service channel connects to USB clearance but stops above the rear
screw-support beam. The broad rear shoulder is replaced with a full-height 45°
chamfer, independent of the small functional slider opening.

Three closure screws, two main-board screws and two sensor-board screws are now
rendered for the trackball; the trackpad shows its three closure screws. New
unsectioned exploded and underside views show how the floors actually close.
Driver access is checked from below. These are geometric checks and instructions,
not claims of a printed prototype or validated screw pull-out strength.

Pilot bores are recut after structural unions so the rear beam cannot refill
them. Main-PCB pilots are blind, retaining 0.7 mm at the visible top; sensor
pilots extend far enough into the floor for the specified screws. Regression
witnesses cover complete engagement bores and the retained top caps.
