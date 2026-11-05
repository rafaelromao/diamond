# Slim Diamond: bill of materials

Quantities are for **one keyboard (both halves)**. The PCB is reversible, so
both halves use the same board. "Spares" are worth ordering because AliExpress
packs come in round numbers anyway.

| # | Part | Qty | Search AliExpress for | Notes |
|---|------|-----|------------------------|-------|
| 1 | PCB, `fab/slim_diamond_jlcpcb.zip` | 2 (order 5) | (JLCPCB, not AliExpress) | 2 layers, 1.6 mm, 87.6 × 92.3 mm, HASL, any colour. The cheapest tier: 5 boards is 2 keyboards plus a spare. |
| 2 | Seeed Studio XIAO nRF52840, **or** NologoTech Super52840 | 2 | `Seeed XIAO nRF52840` / `Super52840` or `MINI NRF52840 18x21` | The same board takes either; set its battery selector to match (BUILD.md, step 1). XIAO: the plain one (not "Sense", not "Plus"), genuine Seeed, since the board relies on its bottom pads (BAT, GND, NFC1). Super52840: the one with B+/B- pads and a row of nine GPIO pads underneath. |
| 3 | Kailh Choc v1 switches | 24 (+2) | `Kailh choc low profile switch` | Any v1 (PG1350) switch. Not v2 (MX stem) and not Choc mini. |
| 4 | Kailh Choc hot-swap sockets | 24 (+4) | `Kailh choc hotswap socket PG1350` | CPG135001S30, the low-profile socket. |
| 5 | Choc keycaps, 1u | 24 | `MBK keycaps choc` / `CFX choc keycaps` | All 24 are 1u (17.5 × 16.5). Thumbs and pinky too. |
| 6 | LiPo battery, 500 mAh, 3.7 V | 2 | `702040 lipo 500mah JST PH 2.0` | Nominal **7 × 20 × 40 mm**, for the halves only. Verify the seller's actual dimensions, lead exit and protection board; ask for the **JST PH 2.0** plug and check polarity. |
| 7 | JST PH 2.0, 2-pin, SMD horizontal socket | 2 (+2) | `JST PH 2.0 2P SMD horizontal` | S2B-PH-SM4-TB footprint: side entry, two signal pads and two big mounting tabs. |
| 8 | Slide switch MSK-12C02 | 2 (+3) | `MSK-12C02 SMD slide switch` | The 7-pad SMD one with two locating pins. |
| 9 | Reset button: SMD tact switch 5.1 × 5.1 mm, **2.0 mm tall**, 4 gull-wing legs (XKB TS-1187A-B-D-B or equivalent) | 2 (+3) | `5.1x5.1x2.0 SMD tactile switch 4 pin` | On the switch face, in the nook above the thumbs: reset, or double-tap for the bootloader, with the case closed. The height matters: 2.0 mm puts the plunger 0.2 mm under the plate's top. The common 1.5 mm one (LCSC C318884) fits too, but then sits 0.7 mm down and needs a fingernail or a pen tip. |
| 10 | Disc magnets 8 × 1.5 mm, N52 | 26 (+4) | `8x1.5mm N52 neodymium magnet` | Thirteen per half: four stacking positions, three circular stand contacts, six inner-wall magnets evenly spread at 17.8 mm pitch. The same part is used in every accessory. |
| 11 | M3 × 8 flat-head screws, 90° countersunk (ISO 10642 / DIN 7991) | 8 | `M3x8 countersunk flat head screw` | Four per half: through the plate (the head sits flush in its countersink) and the PCB, threading into the solid base (2.5 mm pilot holes). |
| 12 | Silicone bump-ons 8 × 2 mm, self-adhesive | 10 (+6) | `8x2mm silicone bumpon self adhesive` | Five per half, in the slots under the floor (see BUILD.md). Use the specified 2.0 mm height to retain the checked stand-platform clearance. |
| 13 | Filament | ~170 g | Nylon (PA) | Case left + right (solid base, 65.9 cm³ each) and the two top plates (4.3 cm³ each); approximately 160 g solid nylon before print overhead. |

**Cyberdeck dock (optional):** `case/dock.stl` (84.4 cm³, about 96 g of Nylon), for a Ugreen folding phone
stand with an 85 × 105 × 4 mm base, or on its own as a tented unibody. Print it flat side down, with
supports inside the pocket (its roof spans 85 mm). It takes **34 additional common 8 × 1.5 mm discs**:
12 under the halves (six per half), 12 in the uninterrupted 2.4 mm drawer walls (six per side),
10 for the five base-magnet pairs. There is no rear retention magnet: that area is reserved for USB. The side magnets
face all six seam magnets outside; positions 2, 4 and 6 also face the insert through a 0.6 mm inner skin. Load them from
outside, flush, then glue in place. Seat each dock magnet by letting it snap onto the half it faces;
orient the insert's magnets to attract its other pole through the inner wall. A magnet chain must
attract throughout: half → dock → insert. Five base discs go in the dock and five are glued on the
aluminium Ugreen base, paired with opposite poles facing. Add **6 more 8 × 2 mm bump-ons**, three under each
wing: the underside is cut 0.5 mm off the desk for them.

**Independent tenting (optional):** two Ugreen stands and **6 common discs**, three glued to each
tilting phone platform. Use the mirrored 1:1 SVG templates in `case/`; the magnet centres form a
44 mm circle and require a **54 mm clear flat contact patch**. Measure the real platform and test
the adhesive, magnetic retention and stand stability before use; platform compatibility is unconfirmed.

**Drawer placeholder:** `case/insert.stl` (64.5 cm³, solid), for when neither module is in the drawer:
**6 common discs**, three a side.

**Drawer modules (optional):** either slides into the dock's drawer from the front, or snaps onto either
half's inner wall on the desk. Each needs **6 common discs** (three a side;
test every mating polarity before gluing), **3 × 8 × 2 mm
bump-ons** and **3 × M2 × 6 flat-head screws** for its bottom plate, a **752025, 250 mAh battery**
(7.5 × 20 × 25 mm, unchanged; not the halves' larger cell),
and its printed shell and bottom plate. Trackball shells print top down **with rear-hood
supports**; inspect the slicer and test-print that region first (see BUILD.md).

**Magnet total:** both halves 26 + dock/base 34 + independent stands 6 + all three inserts 18
= **84 discs**, before spares. One insert rather than all three gives 72 discs with both stand options.

| Slim Diamond Trackball | Qty | Search for | Notes |
|---|---|---|---|
| PCB, `trackball/fab/trackball_jlcpcb.zip` | 1 (order 5) | (JLCPCB) | One board: snap the sensor board off its tab. 2 layers, 1.6 mm |
| nice!nano v2 | 1 | `nice!nano v2` / `SuperMini nRF52840` | Face down on shell-mounted ledges, secured with insulating tape; wired to labelled PCB pads, not pinned through the switch footprints. USB-C at the back; leave floor-service slack |
| PixArt PMW3610DM-SUDU + LM18-LSI lens | 1 + 1 | `PMW3610` (eBay, Tindie: Randware) / `LM18-LSI` | Through-hole sensor in the sensor board's cut-out, on its back face; the lens clips on from the front, looking up |
| TLV74318PDBVR, SOT-23-5 | 1 | `TLV74318PDBVR` | The sensor's 1.8 V |
| 0805 capacitors: 10 µF, 3.3 µF, 1 µF ×2, 100 nF ×3, 10 nF ×2; 0805 resistor 10 kΩ | 9 + 1 | `0805 capacitor kit` | Values as siderakb's PMW3610 board (CERN-OHL-P), which this circuit follows |
| TS-1187A reset button (5.1 × 5.1 × 2.0 mm) | 1 | `5.1x5.1x2.0 SMD tactile switch 4 pin` | On the sensor board, facing down: press it with a pin through the bottom plate |
| MSK-12C02 power switch | 1 | `MSK-12C02 SMD slide switch` | Lever out of the back wall |
| MX switches + Kailh MX sockets + 1u DSA caps, **or** Choc v1 switches + Choc sockets + caps | 2 each | `Kailh MX hotswap socket` / `Kailh choc hotswap socket PG1350` | One shared PCB; populate only one socket family. MX uses `shell.stl`, Choc v1 uses `shell_choc.stl`; bottom plate is shared. Choc v2 is not supported. |
| 34 mm trackball, 3 mm Si3N4 balls | 1 + 3 | `34mm trackball` / `3mm ceramic ball Si3N4` | The ceramic balls glue into the cup's three pockets |
| M2 × 5 pan-head screws | 2 | | Sensor board to its posts, either case |
| M2 × 5 (MX) **or M2 × 3 (Choc)** pan-head screws | 2 | | Main board to the top-shell posts. The Choc shell needs the shorter screws; 5 mm screws would protrude through its lower top. |
| Hookup wire | 17 × ~50 mm | | Seven sensor-to-main wires plus ten controller wires: GND, VCC, RST, VBAT (to B+), SCLK, SDIO, NCS, MOTION, K1, K2. Leave slack for opening the bottom plate. |

| Slim Diamond Trackpad | Qty | Search for | Notes |
|---|---|---|---|
| Cirque TM040040, SPI | 1 | `TM040040` (Mouser) | The SPI version (the label's interface digit 4, R1 fitted): no change needed |
| 12-pin 0.5 mm FFC cable and FFC-to-2.54 mm adapter | 1 + 1 | `12P 0.5mm FFC adapter board` | The adapter sits on a shelf over the battery; the case allows 20 × 14 mm |
| nice!nano v2 | 1 | `nice!nano v2` | In a cradle on the bottom plate, USB-C at the back |
| Choc v1 switches and keycaps | 2 + 2 | `Kailh choc low profile switch` | Clip into the top; wired by hand |
| SS12D00G3 slide switch | 1 | `SS12D00G3 mini slide switch` | In its pocket on the back wall, lever out of it |
| 6 × 6 mm tact switch (through-hole) | 1 | `6x6x4.3 tactile switch` | In its cradle on the plate: press it with a pin from below |
| Hookup wire | ~15 × 60 mm | | See the wiring table in the README |

Consumables: thin solder (0.5–0.6 mm), flux, a little kapton tape, CA glue
or epoxy for the magnets.

Soldering, assembly and printing: see [BUILD.md](BUILD.md).
