> **Superseded.** This records the earlier shell-and-floor modules. The current modules are a shared tray and lid; see BUILD.md.

# Pointing-module revision and review dispositions

This is the request/finding ledger for the November 5 assembly revision. The
previous [blind review](STL_DESIGN_REVIEW.md) remains a frozen report with its
original hashes, not a report retroactively edited to describe new geometry.
No physical print, supplier quote, purchase, strength test or firmware build is
claimed. Independent re-review is recorded separately after artifact freeze.

## User requests

| Request | Implementation / answer | Evidence |
|---|---|---|
| Trackpad on/off | Rear SS12D00G3 body and slider; bottom-load full-body pocket, lever entry joined to USB opening, reversible tape retention. Battery+ through common/throw to B+. USB remains live when connected. | `trackpad.py`, rear/USB views; full travel and rigid switch insertion regressions. |
| Reset on both | TS-1187A on trackball sensor B.Cu; upside-down 6 mm tactile in trackpad floor. Both RST-to-GND with real downward plungers and pin-access holes. | Parts/PCB/wiring; `*_reset.png`; straight insulating-pin access tests. |
| Visible top/bottom division and screws | Actual shell/floor solids separated in color-coded, **unsectioned** structure views, closed underside perimeter-joint views, populated exploded and underside views. The floor is inset into the underside; there is no false horizontal mid-wall seam. Three M2×6 closure screws per module. | `*_structure.png`, `*_seam.png`, `*_assembly.png`, `*_under.png`; BUILD. |
| Flex like Leonardo KeycapRio | Leonardo is a **slotted compliant rigid PCB**, not PI flex or rigid-flex. The size tier alone does not qualify its strained copper/laminate. The generated rigid panel fits the 100 mm square; the non-coplanar sensor must remain mechanically supported. A bent FR4 neck is not substituted for wires. Detailed options and quote/strain caveats are in the flex study. **No qualified integrated flex PCB has been implemented.** | `trackball/FLEX_FEASIBILITY.md`; original designer/JLCPCB primary sources. This remains an explicit engineering/procurement gate, not silently marked complete. |
| Extra direct retention | One common 8×1.5 N52 disc in each pointing-module floor and one in the drawer at (13,−68), opposite poles facing; no rear magnet. | Generated STLs, floor/dock views and clearance/backing tests. Holding force still needs a real test. |
| All renders current | Regenerate scenes, scene boards, routed-board renders and all published views after final geometry/PCB; inventory freshness and visually inspect contact sheets. | Render manifest and final checks, recorded after regeneration. |

## Previous blind review: all nine findings

| # | Finding | Disposition in this revision | Still requires physical validation |
|---|---|---|---|
| 1 | Battery loading obstructed | Integral roof removed. Separate flat-print adapter bridge, two outboard M2×4 screws, battery top-load before bridge. Rigid 25×21×7.8 acceptance-gauge loading/removal regression; no pouch bending. | Actual protected-pack dimensions, insulated tab/lead exit, clearance and removal with real tape. |
| 2 | Choc 1.4 mm plastic engagement / bottoming | Both cases now use M2×5 through screws into full 1.6 mm M2 metal nuts in exterior hex wells. 0.8 mm load shoulders; screw tips clear open wells and modeled caps. No shallow blind Choc thread. | Actual head/nut dimensions, clamping torque, shoulder strength, socket insertion and service cycles. |
| 3 | Tall fragile controller fingers | Replaced 1–1.2 mm fingers with 3 mm side piers joined by a broad lower crossweb; web clears USB body and battery. Remaining free side-pier height is short. Lacing slots and explicit service connectors added. | Handling/cable tug load, tape removal, layer adhesion, antenna/RF effects. |
| 4 | Integral bridge/support removal, pad ledge | Separate bridge supplied flat; no support is trapped above the cell. Pad ledge grows inward at 45° in print direction. Hood/dock support strategy and test order explicitly retained. | Bridge flatness, pad seat quality, hood/support finish, 85 mm dock-roof support removal. |
| 5 | Thin magnet/foot skins | Side backings increased from 0.5 to 0.9 mm; floor magnet has 0.9 backing; foot roofs locally 1.1 instead of 0.7. Battery seats/sensor supports clear reinforced roofs. | Slicer continuity, adhesive seating without force, compression, magnet installation coupons. |
| 6 | No reliable drawer purchase | 8 mm textile ribbon bonded into a hidden underside recess; exposed flexible tongue pulls drawer, not ball/keys. Front facets remain uncut. Same recess on placeholder. | Bond strength and grip vs magnetic pull, ribbon drag at the dock entrance and wear. |
| 7 | No floor purchase / unspecified disconnects / loose pad | Ribbon also pulls the unscrewed floor. **True wire-to-wire Molex 51021/51047 PicoBlade** harnesses, manufacturer mating dimensions plus clearance, explicit nets, 25 mm service loops, ≤15 mm opening and lacing slots; separate pack-only disconnect. Reversible pad adhesive dots and insulating tape pull tabs specified. | Wired service operation, actual housing/grip access, insulation/strain relief, inversion-safe pad retention. |
| 8 | Coupled fits/supports need coupons | No universal clearance claim. Explicit staged prototype gates for pockets/pilots, hood/support pair, rigid battery dummy, screw life, drawer/USB/tilt loads; glue-clearance rather than press fit. Stale material estimate corrected. | **Open physical-validation gate**, not a geometry defect claimed fixed by tests. |
| 9 | Unspecified driver/head procurement | ≤3 mm precision shaft; explicit countersunk/pan head diameter, height and length conventions; M2 nut AF/thickness specified; modeled screw/tool access. | Inspect purchased hardware and qualify torque and repeated assembly. |

## Second blind review (STL_BLIND_REVIEW_2.md): dispositions

No new blocking STL, topology or extraction defect was found. All 26 STLs were checked and the 12 public pairs are byte-identical.

| # | Finding | Disposition |
|---|---|---|
| R1 | Trackpad FFC service operation undefined | BUILD now has a "Trackpad FFC" rule: record length, thickness, contact side and connector (Cirque end is non-ZIF Molex 78127-1128). Disconnect the adapter end first. Lower the floor only as far as the cable allows, not to 15 mm. **Still untested; needs a physical dry run.** |
| R2 | Harness exits and hand access unproved | Added a harness acceptance test and staggering/re-siting rule. **Physical gate; nothing in the geometry can close it.** |
| R3 | Bridge only 0.1 mm over the 7.8 mm gauge | Fixed in geometry: bridge raised 0.5 mm, now 0.6 mm over the gauge. Limit explicitly includes insulation and tape. Regression test added. Real-pack fit remains a gate. |
| R4 | Root readme omitted the bridge | Fixed: listed as a required third print. |
| R5 | 34 vs 35 discs; wrong trackball floor caption | Fixed: BUILD says 35; caption is generic. |

Still open: real-hardware dry fit, support removal on the hood, screw torque and life, magnet and ribbon bond strength, and USB plug and cable fit.
