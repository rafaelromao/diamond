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

**Cyberdeck dock (optional):** `case/dock.stl` (about 83 cm³, 95 g of Nylon), for a Ugreen folding phone
stand with an 85 × 105 × 4 mm base, or on its own as a tented unibody. Print it flat side down, with
supports inside the pocket (its roof spans 85 mm). It takes **31 common 8 × 1.5 mm discs**:
12 under the halves (six per half), 12 in the drawer walls (six per side), 6 for the three base-magnet
pairs and one in the drawer floor. The side magnets face all six seam magnets outside; positions 2, 4
and 6 also face the insert through a 0.6 mm inner skin. Load them from outside, flush, then glue in
place. A magnet chain must attract throughout: half → dock → insert. Three base discs go in the dock
and three are glued on the aluminium Ugreen base, paired with opposite poles facing. Add **6 more
8 × 2 mm bump-ons**, three under each wing.

**Independent tenting (optional):** two Ugreen stands and **6 common discs**, three glued to each
tilting phone platform, using the mirrored 1:1 SVG templates in `case/`. The platform needs a
**54 mm clear flat contact patch**.

**Drawer placeholder:** `case/insert.stl` (71.5 cm³, solid), for when neither module is in the drawer:
**6 common discs**, three a side.

**Magnet total:** both halves 26 + dock and base 31 + stands 6 + placeholder 6 + both pointing modules 14
= **83 discs**, before spares.

**Drawer modules (optional).** Either slides into the dock's drawer from the front, or snaps onto either
half's inner wall on the desk. Everything below is per module, and most of it is the same part you already
buy for the halves.

| Every module | Qty | Search for | Notes |
|---|---|---|---|
| Printed tray, `case/module_tray.stl` | 1 | | The same print for every module |
| Printed lid | 1 | | `trackball/case/lid.stl` (MX), `trackball/case/lid_choc.stl` (Choc v1) or `trackpad/case/lid.stl` |
| PCB, `trackball/fab/trackball_jlcpcb.zip` | 1 (order 5) | (JLCPCB) | 2 layers, 1.6 mm, 53.7 × 99.5 mm. One breakaway panel of three boards (main, sensor, controller), for both pointing modules and either controller: nice!nano v2 or plain XIAO nRF52840. JLCPCB may count this as three designs and add a fee: enter Different Design = 3 and confirm on the quote |
| M3 × 8 flat-head screws | 6 | same as item 11 | Four through the lid, two intended for the sensor board; check sensor screw depth before installing the battery |
| Disc magnets 8 × 1.5 mm, N52 | 7 | same as item 10 | Three a side, one in the floor |
| Silicone bump-ons 8 × 2 mm | 3 | same as item 12 | |
| Slide switch MSK-12C02 | 1 | same as item 8 | On the main board, lever out of the back wall |
| Reset button TS-1187A | 1 | same as item 9 | On the sensor board, facing down |
| nice!nano v2 or clone | 1 | `nice!nano v2` / `SuperMini nRF52840` | Face down on the controller board's header, USB-C flush with the back. Only a genuine nice!nano v2's pin rows have been checked: compare a clone's against the wiring diagram before soldering |
| **Alternative** to nice!nano: plain XIAO nRF52840 or Super52840 | 1 | same as item 2 | Same panel and header; set its jumper and use its own firmware. Its USB-C mouth sits 0.2 mm inside the back. Real fit and operation remain unverified; Super52840 support is experimental |
| 2.54 mm pin header | 11 pins | `2.54 mm male header` | Two 5-pin lengths and a loose pin, under the controller. Plastic 2.5 mm thick |
| Extra-long 2.54 mm pin header, 15 mm | 8 pins | `2.54 mm header 15 mm long` | Stacking pins between the controller board and main board: two 3-pin lengths and two single pins. Check where the plastic sits: short end at least 2.35 mm, long end at least 6.7 mm |
| LiPo battery 752025, 250 mAh | 1 | `752025 lipo 250mah` | 7.5 × 20 × 25 mm, not the halves' larger cell. Over 20.5 mm wide, it fouls the controller board's arms |
| 30 AWG stranded wire | 80 to 100 mm per wire | `30 AWG silicone wire` | About 25 mm for the two wires from the controller |

| Trackball | Qty | Search for | Notes |
|---|---|---|---|
| PixArt PMW3610DM-SUDU + LM18-LSI lens | 1 + 1 | `PMW3610` (eBay, Tindie: Randware) / `LM18-LSI` | Through-hole sensor in the sensor board's cut-out, on its back face; the lens clips on from the front, looking up |
| TLV74318PDBVR, SOT-23-5 | 1 | `TLV74318PDBVR` | The sensor's 1.8 V |
| 0805 capacitors: 10 µF, 3.3 µF, 1 µF ×2, 100 nF ×3, 10 nF ×2; 0805 resistor 10 kΩ | 9 + 1 | `0805 capacitor kit` | Values as siderakb's PMW3610 board (CERN-OHL-P), which this circuit follows |
| MX switches + Kailh MX sockets + 1u DSA caps, **or** Choc v1 switches + Choc sockets + caps | 2 each | `Kailh MX hotswap socket` / item 4 | Populate only one socket family. Choc v2 is not supported |
| 34 mm trackball, 3 mm Si3N4 balls | 1 + 3 | `34mm trackball` / `3mm ceramic ball Si3N4` | The ceramic balls glue into the cup's three pockets |

| Trackpad | Qty | Search for | Notes |
|---|---|---|---|
| Cirque TM040040-2023-302 or I²C-configured kit | 1 | `Cirque 40mm I2C flat overlay` | Use the supplied I²C breakout and flat cable; on SPI-labelled kits remove R1 for I²C, keeping R7/R8 for 3.3 V |
| Supplied I²C breakout with pull-ups + 12-pin FFC | 1 + 1 | supplied with the kit | Reserved maximum breakout envelope 24 × 18 × 4.5 mm; confirm actual size and FFC contact orientation. Four MCU wires to breakout, separate DR wire directly to Cirque underside |
| Choc v1 switches, sockets and keycaps | 2 + 2 + 2 | same as items 3, 4, 5 | |

Consumables: thin solder (0.5–0.6 mm), flux, a little kapton tape, thin double-sided tape (0.25 mm at most) for the controller, CA glue
or epoxy for the magnets, removable adhesive dots for the trackpad, thin card for the sensor's
shims, and a 2.5 mm insulating spacer/tape stack for the I²C breakout (no printed holder).

Soldering, assembly and printing: see [BUILD.md](BUILD.md).
