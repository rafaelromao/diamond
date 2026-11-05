# Slim Diamond Trackball: flexible interconnect feasibility

Research date: **2026-11-04**. Manufacturing and price statements below refer to
the official pages accessed on that date, not a completed fabrication quote.
This is a feasibility note; no PCB, case or generator changes are proposed as
already validated.

## Recommendation

**Keep the two supported 1.6 mm rigid boards and the seven-wire interconnect for
the strict cheapest-rigid, at-most-100 × 100 mm requirement.** A flexible
interconnect is electrically plausible, but a polyimide board is a different
manufacturing selection, not something unlocked by fitting inside that square.
Leonardo-style routed FR4 springs are the relevant single-board experiment if
remaining in the rigid material class is mandatory; they are not a proven
replacement for this trackball's breakaway tab.

If an additional cable/connector budget is acceptable, first investigate a
stock FFC and two connectors, or a separate custom polyimide jumper between
the existing rigid islands. If the objective is instead **one continuous
circuit with no cable solder joints**, investigate an all-flex circuit with
local stiffeners and independent mechanical supports, subject to a new quote.
True laminated rigid-flex is not currently supported by JLCPCB's published
capability table.[4]

**Important current-price qualification:** JLCPCB now advertises both FR4 and
flex from **US$2 / 5 pieces**. Its flex pricing article explicitly describes
an entry offer for five 2-layer flex boards up to 100 × 100 mm. It would be
incorrect to claim that flex necessarily has a large minimum price, or that
any flex design below 100 × 100 mm receives that price. Stiffeners, panelization
and other options require a quote.[5][6]

## What the Leonardo reference actually demonstrates

The [KBD.news article][1] links to **StephanMoeller/Leonardo-KeycapRio**.
The designer's v0.1 README says that PCB **squiggles** allow bending and identifies
the photographed black board as 1.6 mm thick and the white board as 1.0 mm.
The original KiCad board has two copper layers (`F.Cu`, `B.Cu`), a global
`(thickness 1.6)`, and the routed `Edge.Cuts` geometry. Its production ZIP
contains ordinary copper, mask, paste, outline and drill files; there is no
separate flex/stiffener definition in that ZIP.[2][3]

This is evidence for a **geometrically compliant, slotted rigid-style PCB**, not
evidence for a polyimide flex stackup or true rigid-flex. The inspected original
KiCad file does not explicitly declare a laminate material or an engineered
flex stackup: FR4 is the intended ordinary-rigid interpretation, not a recovered
supplier order specification. Do not treat the article's phrase “single
flexible PCB” as a material declaration.[1][2][3]

The designer's later history is especially relevant: v0.4 changed from 1.6 mm
to 1.0 mm because the PLA tenting support started to bend; v0.6 used 1.2 mm
at JLCPCB; v0.7 returned to 1.6 mm because hot-swap socket pins were taller
than 1.2 mm. These are useful prototype observations, **not a bend-radius,
fatigue-life or manufacturing guarantee** for another outline.[2]

Sources [2] and [3] are pinned to repository commit
`b6f588dc99da9befac5b50a15a0b9ba1617df79e`.

## Trackball constraints checked in the current inputs

- [`design.json`](design.json) gives a **28 × 30 mm sensor island** and an overall
  flat panel bounding box of **35.497 × 76.6368 mm** (min/max of `panel`). Thus
  the present outline fits the user's 100 × 100 mm envelope. A longer spring,
  flex tail, handling border or different panel arrangement must be checked
  again; folded dimensions are not fabrication dimensions.
  Rechecked after the 3.8 mm rearward key shift and 270° footprint rotation: the
  regenerated panel retains these same bounding dimensions.
- [`trackball.py`](trackball.py) specifies `PCB_T = 1.6`, two alternative
  **MX / Choc v1 hot-swap sockets per key**, a nice!nano below the main board,
  and seven wires: **VCC, GND, RST, SCLK, SDIO, NCS, MOTION**. The existing
  breakaway tab is for manufacturing/depanelization, not a live flex hinge.
- The main PCB top is **20.470856 mm**, from `design.json`'s `pcb_top`.
  The sensor PCB top is **7.3 mm**: `PLATE_TOP + SENSOR_BELOW + PCB_T`, or
  `0.5 + 2.2 + 3.0 + 1.6`, using `MODULE_FEET` in
  [`../dock.py`](../dock.py), `BOTTOM_T` in
  [`../module_shell.py`](../module_shell.py), and `trackball.py`.
  Their top-plane offset is therefore **13.170856 mm**. This is not a flex
  length calculation: endpoint locations, bend tangents and clearance determine
  the needed developed length.
- The code labels the lens reference height and nice!nano first-row position
  as unconfirmed. Changing board/stiffener thickness must preserve the optical
  height, socket engagement, screw support and controller/battery clearance;
  the current elevations are design inputs, not measured hardware proof.

## Manufacturing and price comparison

| Construction | What bends / what supports components | Budget consequence and verdict |
|---|---|---|
| Present breakaway FR4 pair + wires | Wires bend; rigid PCB and case support sensor, sockets and controller | Best baseline for the rigid-material constraint. Present size fits, but the final panel/design-count treatment still needs confirmation. |
| One slotted/serpentine FR4 PCB, Leonardo-style | Long, routed laminate springs between rigid islands; retain supported switch/sensor islands | Only integral option here that stays ordinary rigid material. Size, routing charges, minimum web/slot dimensions and mechanical life remain unverified. Experimental, not a foldable tab. |
| Thin FR4, straight neck | Glass/epoxy and copper are strained directly; all islands also become thinner unless special construction is bought | Not a safe shortcut to flex. Thin-stock availability is not proof of cheap-tier eligibility or fold endurance. Socket and optical geometry need redesign. |
| Two FR4 islands + stock FFC | Purchased flat cable bends; connector bodies and islands remain rigid | Preserves rigid PCB ordering, but adds cable, connectors, soldering and clearance costs. FFC pitch, contact orientation and thickness must match connectors. No supplier price verified here. |
| Two FR4 islands + custom PI flex jumper | Separate copper/PI ribbon bends; solder pads or connectors attach it to the rigid boards | Technically attractive retrofit, but an additional flex fabrication item, not a free FR4 feature. Direct soldering needs strain relief; detachable connectors need reinforced cable ends. |
| One all-flex PI circuit + stiffeners | Continuous flex copper spans sensor and main regions; bonded stiffeners/case support the component regions | Supported in principle by JLCPCB's FPC service. **Not true rigid-flex.** New FPC quote including local supports, holes and assembly provisions required; not proven to meet the rigid-tier budget. |
| True rigid-flex | Routed rigid copper stacks laminated to shared flex copper through designed transitions | JLCPCB explicitly says “Rigid-flex PCBs are not yet supported.” No current JLCPCB rigid-flex price exists in the verified offering; another supplier would need to quote it. |

JLCPCB's quote form defines “Different Design” as designs separated by V-cuts,
mouse bites or milling slots. Therefore the present two-island breakaway panel
cannot be assumed to count as one design just because it is uploaded in one
ZIP. Ask CAM/support how this particular functional assembly is classified.[7]

### What is, and is not, a verified price

- **Rigid:** the official homepage advertises FR4 “From $2.00 / 5 pcs.” The
  user's **100 × 100 mm rigid-tier constraint** is the envelope used here;
  the retrieved current pages do not establish the complete rigid-promotion
  eligibility matrix for this particular tabbed panel.[5]
- **Flex:** the official pricing article, published 2026-11-04, states
  **$2.00 for five 2-layer boards up to 100 × 100 mm**, as an entry price,
  excluding shipping, taxes and duties. It distinguishes coupons from that
  starting price and identifies stiffeners and other special features as cost
  drivers. That is a separate flex offer, not the rigid offer.[6]
- **Ordering-channel caveat:** JLCPCB's 2026-08-22 announcement says the
  signature $2 deal moved exclusively to **JLCONE Desktop**, while current web
  pages still advertise $2 starting prices. The applicable channel and offer
  for this order must be confirmed; marketing headings are not a payable
  quotation.[5][8]
- No exact price for this trackball, its flex jumper, a stiffened all-flex
  replacement, shipping or connectors was obtained. No purchase or design
  upload was made. The quote page's uncalculated `$0.00` is not a price.[7]

## Verified JLCPCB rules relevant to a PI interconnect

The dedicated capability table is the primary process reference.[4]

| Feature | Published capability / implication |
|---|---|
| Layers and substrate | 1, 2 or 4 copper layers; PI dielectric 25 µm or 50 µm. Transparent PET is a different option, not the assumed solderable PI construction. |
| Example finished thicknesses | With 25 µm PI: 1-layer 0.07 / 0.11 mm; 2-layer 0.11 / 0.12 / 0.20 mm. These are **finished FPC thicknesses excluding stiffeners**, not the PI dielectric alone. Copper and coverlay choices determine the stackup. |
| Copper | Single-sided: 18 / 35 µm; double-sided: 12 / 18 / 35 µm. At 18 µm copper, published regular minimum trace/space is 3.5 / 3.5 mil. |
| Outline and holes | Laser outline: copper-to-edge and copper-to-slot clearance ≥0.3 mm. NPTH-to-copper ≥0.20 mm. Regular via hole/diameter 0.3 / 0.55 mm; smaller extreme options may cost extra. |
| Finish | ENIG, 1 or 2 µin gold. Do not carry rigid HASL pricing assumptions into FPC. |
| Stiffeners | PI: 0.1, 0.15, 0.20, 0.225, 0.25 mm. FR4: 0.1, 0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.6 mm. Stainless: 0.1, 0.2, 0.3 mm. Finished reinforced thickness is FPC + stiffener; confirm actual bonded stack and tolerance. |
| Fabrication files | For KiCad/other EDA, put stiffener outlines, material and thickness on a separate annotation layer and select corresponding options manually when ordering. Ordinary copper Gerbers do not specify this automatically. |
| Size | Regular maximum 234 × 490 mm; 250 × 600 mm with rails requires support confirmation. Sub-20 × 20 mm FPCs are best panelized. These are manufacturing limits, **not price thresholds**. |

Seven conductors do not require an exotic trace density: as an illustrative
packing calculation, seven 0.25 mm traces with six 0.25 mm gaps and two 0.3 mm
edge clearances occupy **3.85 mm**. This is not a proposed final width: ground
return, current/voltage drop, tail strength, pad fanout and signal integrity
must be designed. Retain local sensor decoupling and verify PMW3610 operation
at the intended interconnect length and clock rate. An eighth ground conductor
may be useful if a stock cable format provides it; it is not required by the
current seven-net interface.

For a panelized FPC, JLCPCB lists 5 mm handling borders on all four sides,
typically 2 mm inter-board spacing (3 mm with metal stiffeners), and 0.7–1.0 mm
support tabs. Its panel guide uses laser-cut bridge tabs rather than rigid
mouse bites/V-cuts. Do not reuse the existing rigid breakaway geometry without
FPC CAM review.[4][9]

## Bending and mechanical support

**PI flex:** the capabilities page recommends a minimum radius of **6× total
flex thickness for a single layer** and **10× for multiple layers**, with no
vias/pads in the bend. For a 0.11 mm 2-layer FPC, 10× gives **1.1 mm** as a
published starting recommendation, not an approved final radius. Its separate
bend-design article instead gives **12× for static multilayer** and much larger
**100–150× for dynamic multilayer** bends; the capabilities page mentions
10–15× for dynamic use. These official pages disagree. Use a generous static
service loop here and have JLCPCB approve the actual stackup, radius and
assembly/service cycles; do not claim a guaranteed cycle life or silently
choose the smallest multiplier. None of these PI ratios applies to FR4.[4][10]

**All-flex with stiffeners:** copper still runs on the flex laminate. Bonding
an unpatterned FR4 support beneath a region does not create a separately routed
rigid copper stack. Support the sensor plane and screw loads, both MX and Choc
socket solder lands, switch insertion/removal forces and main-board/controller
attachments. A thin PI connector stiffener is not automatically an adequate
switch plate. FR4/metal stiffeners may require clearance holes or cutouts for
switch pins, socket bodies and sensor optics, and the board must not flex at
solder joints. The exact construction needs supplier approval and a physical
hot-swap insertion/removal test.[4][7]

**FR4 springs:** the current rigid capability table lists 0.4 / 0.6 / 0.8 /
1.0 / 1.2 / 1.6 / 2.0 mm thicknesses and does not provide a qualified bending
radius or cycle life for compliant links. It explicitly disallows HASL at
≤0.4 mm, so “just order 0.4 mm” may also change finish/cost. A more general
product-page marketing paragraph mentions 0.2 mm, conflicting with the detailed
table; do not assume 0.2 mm standard stock or promo eligibility.[11][12]

Long, rounded serpentine beams can distribute elastic bending/torsion, as
Leonardo demonstrates, but a short straight FR4 neck cannot be treated as a
fold line. Approximate simple-beam surface strain scales as `t / (2R)`;
thinning helps but does not establish allowable strain for this laminate,
copper, plating and soldermask. Keep components/vias away from the strained
sections, avoid sharp roots and breakaway perforations there, constrain the
islands mechanically, and prototype the assembled displacement. Accommodating
the **13.17 mm height offset** within the available planar spring length is
unproven; a 100 × 100 mm outline alone says nothing about bend survival.

## Before changing the design

1. Obtain a baseline JLCPCB/JLCONE quote for the existing **1.6 mm FR4** panel,
   including its actual design count and routed slots. Confirm promo eligibility,
   shipping and tax rather than assuming that fitting the square is sufficient.
2. If an integral rigid experiment is wanted, submit a dimensioned serpentine
   concept for minimum routed slot/web, copper-edge clearance, routing charges
   and handling approval. Build one for static assembly and repeated servicing
   tests before committing to it.
3. If leaving the rigid tier is allowed, compare **separate jumper** and
   **single all-flex with stiffeners** quotes, specifying developed outline,
   copper/PI/coverlay stack, finished thickness, support regions, holes, assembly
   method and bend radius. The latter has no inter-island connector joints,
   but changes both PCB islands' mechanical construction.
4. Resolve the contradictory bend guidance with support, and confirm actual
   socket/stiffener/optical heights and available cable route around the cup,
   battery and nice!nano. No mesh audit or fit certification was performed here.

## Sources

All web sources accessed **2026-11-04**. Local geometry sources are linked above.

[1]: https://kbd.news/Leonardo-KeycapRio-2845.html
[2]: https://github.com/StephanMoeller/Leonardo-KeycapRio/blob/b6f588dc99da9befac5b50a15a0b9ba1617df79e/README.md
[3]: https://github.com/StephanMoeller/Leonardo-KeycapRio/tree/b6f588dc99da9befac5b50a15a0b9ba1617df79e/v0.1
[4]: https://jlcpcb.com/capabilities/flex-pcb-capabilities
[5]: https://jlcpcb.com/
[6]: https://jlcpcb.com/blog/flexible-pcb-cost
[7]: https://cart.jlcpcb.com/quote?plateType=7
[8]: https://jlcpcb.com/news/jlcpcb-jlcone-desktop-app
[9]: https://jlcpcb.com/blog/design-guidelines-flex-pcb-panels
[10]: https://jlcpcb.com/blog/flexible-pcb-bend-radius
[11]: https://jlcpcb.com/capabilities/pcb-capabilities
[12]: https://jlcpcb.com/pcb-fabrication/fr4-pcb

- [1] KBD.news, *Leonardo KeycapRio*, 2026-04-24 (discovery/reference article).
- [2] Designer's version history; [v0.1 README](https://github.com/StephanMoeller/Leonardo-KeycapRio/blob/b6f588dc99da9befac5b50a15a0b9ba1617df79e/v0.1/README.md)
  contains the original thickness/flexibility description.
- [3] Original [KiCad PCB](https://github.com/StephanMoeller/Leonardo-KeycapRio/blob/b6f588dc99da9befac5b50a15a0b9ba1617df79e/v0.1/kicad_poc.kicad_pcb)
  and [production Gerber ZIP](https://github.com/StephanMoeller/Leonardo-KeycapRio/blob/b6f588dc99da9befac5b50a15a0b9ba1617df79e/v0.1/production/kicad_poc.zip), inspected directly.
- [4] JLCPCB, *Flexible PCB Manufacturing Capabilities*, including stackup diagrams.
- [5] JLCPCB homepage, current starting-price advertisements.
- [6] JLCPCB, *Flexible PCB Price: Key Cost Factors and Ways to Save*, 2026-11-04.
- [7] JLCPCB quote form, definitions and stiffener instructions; no calculated quote.
- [8] JLCPCB JLCONE pricing-channel announcement, 2026-08-22.
- [9] JLCPCB flex panel guidelines, updated 2026-10-19.
- [10] JLCPCB bend-radius article, updated 2026-10-28; differs from [4].
- [11] JLCPCB detailed rigid capability table; [12] general FR4 product page.
