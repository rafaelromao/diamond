# Slim Diamond: bill of materials

Quantities are for **one keyboard (both halves)**. The PCB is reversible, so
both halves use the same board. "Spares" are worth ordering because AliExpress
packs come in round numbers anyway.

| # | Part | Qty | Search AliExpress for | Notes |
|---|------|-----|------------------------|-------|
| 1 | PCB, `fab/slim_diamond_jlcpcb.zip` | 2 (order 5) | (JLCPCB, not AliExpress) | 2 layers, 1.6 mm, 87.6 × 92.3 mm, HASL, any colour. The cheapest tier: 5 boards is 2 keyboards plus a spare. |
| 2 | Seeed Studio XIAO nRF52840 | 2 | `Seeed XIAO nRF52840` | The plain one (not "Sense", not "Plus"). Prefer the genuine Seeed board: the build relies on its bottom pads (BAT, GND, NFC1) being where Seeed puts them. |
| 3 | Kailh Choc v1 switches | 24 (+2) | `Kailh choc low profile switch` | Any v1 (PG1350) switch. Not v2 (MX stem) and not Choc mini. |
| 4 | Kailh Choc hot-swap sockets | 24 (+4) | `Kailh choc hotswap socket PG1350` | CPG135001S30, the low-profile socket. |
| 5 | Choc keycaps, 1u | 24 | `MBK keycaps choc` / `CFX choc keycaps` | All 24 are 1u (17.5 × 16.5). Thumbs and pinky too. |
| 6 | LiPo battery 752025, 250 mAh, 3.7 V | 2 | `752025 lipo 250mah JST PH 2.0` | 7.5 × 20 × 25 mm. Ask for the **JST PH 2.0** plug. Check polarity before plugging in (see below). |
| 7 | JST PH 2.0, 2-pin, SMD horizontal socket | 2 (+2) | `JST PH 2.0 2P SMD horizontal` | S2B-PH-SM4-TB footprint: side entry, two signal pads and two big mounting tabs. |
| 8 | Slide switch MSK-12C02 | 2 (+3) | `MSK-12C02 SMD slide switch` | The 7-pad SMD one with two locating pins. |
| 9 | Reset button: SMD tact switch 5.1 × 5.1 mm, **2.0 mm tall**, 4 gull-wing legs (XKB TS-1187A-B-D-B or equivalent) | 2 (+3) | `5.1x5.1x2.0 SMD tactile switch 4 pin` | On the switch face, in the nook above the thumbs: reset, or double-tap for the bootloader, with the case closed. The height matters: 2.0 mm puts the plunger 0.2 mm under the plate's top. The common 1.5 mm one (LCSC C318884) fits too, but then sits 0.7 mm down and needs a fingernail or a pen tip. |
| 10 | Disc magnets 6 × 2 mm, N52 | 8 (+4) | `6x2mm N52 neodymium magnet` | Four in each floor: the halves stack back to back. |
| 11 | Disc magnets 5 × 2 mm, N52 | 4 (+4) | `5x2mm N52 neodymium magnet` | Two in each inner wall: the halves join as a unibody. |
| 12 | M3 × 8 flat-head screws, 90° countersunk (ISO 10642 / DIN 7991) | 8 | `M3x8 countersunk flat head screw` | Four per half: through the plate (the head sits flush in its countersink) and the PCB, threading into the solid base (2.5 mm pilot holes). |
| 13 | Silicone bump-ons 8 × 2 mm, self-adhesive | 10 (+6) | `8x2mm silicone bumpon self adhesive` | Five per half, in the slots under the floor (see BUILD.md). Clear or black, round, 8 mm diameter, 2 mm tall; up to 2.2 mm still lets the floors meet. |
| 14 | Filament | ~170 g | Nylon (PA) | Case left + right (solid base, 58.7 cm³ each) and the two top plates (4.3 cm³ each). |

Consumables: thin solder (0.5–0.6 mm), flux, a little kapton tape, CA glue
or epoxy for the magnets.

Soldering, assembly and printing: see [BUILD.md](BUILD.md).
