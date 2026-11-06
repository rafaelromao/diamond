# Assembled-hardware review

Use this checklist for a mechanical blind review or print-readiness review. Inspect the final exported
meshes, populated assemblies, carrier PCB, build instructions and fabrication outputs. Read previous
findings only after recording an independent assessment.

## Required checks

1. **Opposing pockets:** inventory every magnet and fastener on both faces of the dock, drawer floor,
   modules and halves. Transform them into the assembled frame. For every neighbouring pair, measure
   hardware overlap, pocket overlap and the minimum intervening web/backing. Include underside stand
   magnets beneath top-facing retention magnets, not just magnets on the same face. Check full pocket
   diameters, depths, adhesive and realistic dimensional error; report the coordinates and minimum gap.
2. **Hardware stacks:** check actual screw head, tip and thread-engagement envelopes against PCB holes,
   printed posts, floor, batteries and nearby pockets. Separate intentional thread interference from
   bottoming or floor penetration. Check every lid variant and sensor-shim limit.
3. **Assembly paths:** sweep populated board insertion, controller insertion, lid hooks/closure, cable
   insertion and horizontal drawer removal. Include solder joints, insulation, flat-cable bends and wire
   service loops; describe any simplified envelopes rather than treating them as measured hardware.
4. **Native USB:** locate each MCU's own receptacle mouth and insertion axis from controller-specific
   source geometry. Check its height, overhang, support, retention, plug and cable against the shared
   opening and dock in both insertion and seated poses. Qualify controller revisions and clone dimensions.
5. **Electrical and RF:** trace all used GPIO, supply, ground, battery and reset connections through the
   actual PCB nets, controller pinout and merged firmware device tree. Check peripheral pin conflicts,
   interface selection, voltage, pull-ups and antenna clearances for each controller option.
6. **Printability:** inspect minimum walls, disconnected fragments, supports and trapped support-removal
   paths in the specified print orientations. Check separately printed mating parts with a defined
   tolerance budget, including warping, elephant foot and support-facing surfaces.
7. **Deliverables:** verify that the single orderable carrier panel, Gerbers, STLs, public copies, renders,
   BOM and build steps agree. Check interface-specific instructions: the trackpad uses its supplied I²C
   breakout/FFC plus a separate DR lead; the controller is wired below the common carrier.

## Completion evidence

Give a disposition for each check: measured nominal result, confirmed defect, or unverified physical
gate. State the method, coordinates/clearances and assumptions for each finding. A passing topology
check, DRC or firmware build proves only that check; physical fit, retention, charging, optical height
and bus operation remain unqualified until tested on the actual hardware.
