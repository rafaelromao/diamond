# Diamond

## A 24 keys handwired split keyboard.

Diamond is a handwired board originally designed by me but heavily inspired by the [Rommana](https://github.com/AlaaSaadAbdo/Rommana) and using the switch holders from the [Dactyl Cygnus](https://github.com/juhakaup/keyboards).
- It contains 24 keys only, in the format 1333+2.
- It should be handwired, ideally using single switch PCBs.
- The MCU, reset button and on/off switch goes in the base, below a cover used to hide them.
- These components should be mounted upside down, under this cover.
- The cables for column and rows will pass through holes or cutouts in the cover and can be tightened in the end of assembling to make them less visible in the final build. 

# Diamond Builds

## [Diamond](builds/diamond/diamond.md)

![img](builds/diamond/diamond.jpeg)

## [Wired Diamond](builds/wired_diamond/wired_diamond.md)

![img](builds/wired_diamond/wired_diamond.jpeg)

## [Choc Diamond](builds/choc_diamond/choc_diamond.md)

![img](builds/choc_diamond/choc_diamond.jpeg)

## [Slim Diamond](slim_diamond/README.md)

A wireless Choc version on a reversible PCB: XIAO nRF52840, 752025 battery,
tented by the battery underneath, and magnets to join the halves or stack
them back to back.

![img](slim_diamond/renders/full.png)

# STL Files

The STL files are provided for the right side only. To print the left side you will have to mirror them.

- [Base Right](stls/v2/base_right.stl)
- [Cover Right](stls/v2/cover_right.stl)
- [Cover Right with Cutout](stls/v2/cover_right_with_cutout.stl)
- [MX Body Right](stls/v2/body_right.stl)
- [MX Body Right - Tilted Thumbs](stls/v2/body_right_tilted.stl)
- [Choc Body Right](stls/v2/choc_body_right.stl)
- [Choc Body Right - Tilted Thumbs](stls/v2/choc_body_right_tilted.stl)

## Slim Diamond

Both halves are provided, already oriented for printing: the bases floor-down, the plates top face down. See the [build guide](slim_diamond/BUILD.md) for the print settings.

- [Case Left](stls/slim_diamond/case_left.stl)
- [Case Right](stls/slim_diamond/case_right.stl)
- [Plate Left](stls/slim_diamond/plate_left.stl)
- [Plate Right](stls/slim_diamond/plate_right.stl)

# Firmware

Check my [keyboards](https://github.com/rafaelromao/keyboards) repo to find the ZMK firmware for these boards.