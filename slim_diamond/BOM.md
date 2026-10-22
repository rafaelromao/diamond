# Slim Diamond: bill of materials

Quantities are for **one keyboard (both halves)**. The PCB is reversible, so
both halves use the same board. "Spares" are worth ordering because AliExpress
packs come in round numbers anyway.

| # | Part | Qty | Search AliExpress for | Notes |
|---|------|-----|------------------------|-------|
| 1 | PCB, `fab/slim_diamond_jlcpcb.zip` | 2 (order 5) | (JLCPCB, not AliExpress) | 2 layers, 1.6 mm, 87.4 × 92.1 mm, HASL, any colour. The cheapest tier: 5 boards is 2 keyboards plus a spare. |
| 2 | Seeed Studio XIAO nRF52840 | 2 | `Seeed XIAO nRF52840` | The plain one (not "Sense", not "Plus"). Prefer the genuine Seeed board: the build relies on its bottom pads (BAT, GND, NFC1) being where Seeed puts them. |
| 3 | Kailh Choc v1 switches | 24 (+2) | `Kailh choc low profile switch` | Any v1 (PG1350) switch. Not v2 (MX stem) and not Choc mini. |
| 4 | Kailh Choc hot-swap sockets | 24 (+4) | `Kailh choc hotswap socket PG1350` | CPG135001S30, the low-profile socket. |
| 5 | Choc keycaps, 1u | 24 | `MBK keycaps choc` / `CFX choc keycaps` | All 24 are 1u (17.5 × 16.5). Thumbs and pinky too. |
| 6 | LiPo battery 752025, 250 mAh, 3.7 V | 2 | `752025 lipo 250mah JST PH 2.0` | 7.5 × 20 × 25 mm. Ask for the **JST PH 2.0** plug. Check polarity before plugging in (see below). |
| 7 | JST PH 2.0, 2-pin, SMD horizontal socket | 2 (+2) | `JST PH 2.0 2P SMD horizontal` | S2B-PH-SM4-TB footprint: side entry, two signal pads and two big mounting tabs. |
| 8 | Slide switch MSK-12C02 | 2 (+3) | `MSK-12C02 SMD slide switch` | The 7-pad SMD one with two locating pins. |
| 9 | Disc magnets 6 × 2 mm, N52 | 8 (+4) | `6x2mm N52 neodymium magnet` | Four in each floor: the halves stack back to back. |
| 10 | Disc magnets 5 × 2 mm, N52 | 4 (+4) | `5x2mm N52 neodymium magnet` | Two in each inner wall: the halves join as a unibody. |
| 11 | M3 × 6 self-tapping screws, button head (ISO 7380) | 8 | `M3x6 self tapping screw button head` | Four per half, threading into the printed standoffs (2.5 mm pilot holes). 6 mm is the longest that fits the short standoffs on the outer side. The low button head sits between the switches. |
| 12 | Filament | ~60 g | PLA or PETG | Case left + right, 22 cm³ each. |

Consumables: thin solder (0.5–0.6 mm), flux, a little kapton tape, CA glue
or epoxy for the magnets.

## Before you solder

- **Battery polarity.** Silkscreen `+` marks pin 1 of the JST socket. Cheap
  752025 cells ship with either polarity. Check the plug with a multimeter
  first. If it's reversed, swap the two crimps in the plug housing (lift the
  tab with a needle).
- **Magnet polarity.** Every left-half magnet goes in with the same pole facing
  out, and every right-half magnet with the other pole facing out. That makes
  both stacking and the unibody join attract. Mark one face of each magnet
  stack before you start.

## Assembly order (per half)

1. **Pick the face.** The left half gets its parts on the face silkscreened
   `LEFT: parts on this face`. The right half gets them on the other face.
   Switches always go on the opposite face from the sockets.
2. **Jumpers.** On the face *without* the Xiao, bridge the three solder
   jumpers labelled D0, D1, D2 (inside the Xiao's outline). Leave the other
   three open.
3. **Xiao.** Lay it flat on its face, USB towards the board edge. Tack one
   corner, check alignment, then solder each castellated pad from the outside.
   Feed solder into the plated holes for **GND, VBAT and NFC1** from the other
   face until it wicks through to the module's bottom pads. Use a small chisel
   tip.
4. **Power switch and JST socket** on the same face as the Xiao.
5. **Hot-swap sockets**, 12, on the same face.
6. **Test** before closing. Flash the firmware, short each socket's two pads
   with tweezers, and check every key registers.
7. **Case.** Glue the magnets in (polarity!), drop the battery in its fence,
   plug it in, and screw the PCB onto the four standoffs. Then insert the
   switches and keycaps.

## Printing

Print each half floor-down, no supports: the openings are bridged. Use 0.2 mm
layers, 3 walls and 20% infill. Nylon suits the self-tapping screws: it's
tough enough to take a thread without cracking. Dry the filament before
printing, and print the standoffs solid (perimeters reaching the pilot hole)
so the screws bite into plastic, not infill. The floor pockets for the 6 × 2 mm magnets open
on the underside. Press the magnets in and wick a drop of CA glue around them.
