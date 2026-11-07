"""Both halves together, for renders: joined as a unibody, and stacked back to back.

Builds the left half as it sits on the desk (case, PCB, switches with keycaps,
battery) and writes two VRML scenes into .render/:

  unibody.wrl   the right half beside it, mirrored about the seam
  stacked.wrl   the right half under it, floor to floor: turned over, the
                mirrored half is the left one mirrored in z

Each half carries its own anti-slip pads: the left's in one end of each floor slot,
the right's in the other end (case.pads), so stacked they interleave.

render_boards.py hangs each scene on a speck of board hidden in a floor, and
records where that speck is in .render/scenes.json.
"""
import json
import math
import sys

import numpy as np

from manifold3d import CrossSection, FillRule, Manifold
from shapely.geometry import box

import case as C
import vrml
from layout import layout_left

D = json.load(open("design.json"))
c, s = math.cos(C.TENT), math.sin(C.TENT)
PCB_GREEN = (0.1, 0.32, 0.18)


def to_desk(m):
    """PCB frame (z above the PCB's bottom face) into the desk frame."""
    m = m.translate((-C.WALL_IN, 0, 0))
    m = m.transform([[c, 0, -s, 0], [0, 1, 0, 0], [s, 0, c, 0]])
    return m.translate((C.WALL_IN, 0, C.Z0))


def left_half():
    parts = [(C.build(), vrml.CASE), (C.battery(), vrml.BATTERY)]
    plate, _ = C.plate()
    parts.append((to_desk(plate.translate((0, 0, C.PCB_T + C.PLATE["gap"]))), vrml.CASE))
    pcb = C.section([tuple(p) for p in D["pcb_outline"][:-1]]).extrude(C.PCB_T)
    parts.append((to_desk(pcb), PCB_GREEN))
    t = C.PCB_T                                   # switch models start on the PCB's top face
    switch = [
        (vrml.box(-6.9, -6.9, t, 6.9, 6.9, t + 2.2), vrml.SWITCH),
        (vrml.box(-7.5, -7.5, t + 2.2, 7.5, 7.5, t + 3.0), vrml.SWITCH),
        (vrml.frustum(14.5, 14.5, 12.5, 12.5, t + 3.0, t + 5.0), vrml.SWITCH),
        (vrml.frustum(17.5, 16.5, 15.6, 14.6, t + 5.8, t + 8.6), vrml.KEYCAP),
    ]
    for (x, y), r in layout_left().values():
        for m, rgb in switch:
            parts.append((to_desk(m.rotate((0, 0, r)).translate((x, y, 0))), rgb))
    rb = D["reset_button"]                         # the reset button, on the switch face
    parts.append((to_desk(Manifold.cylinder(rb["h"], rb["plunger_d"] / 2, circular_segments=32)
                          .translate((rb["x"], rb["y"], t))), vrml.SOCKET))
    return parts


UGREEN = (0.42, 0.43, 0.47)
PHONE = (0.2, 0.2, 0.22)
SCREEN = (0.04, 0.07, 0.11)
PHONE_SIZE = (160.0, 78.0, 10.0)   # in its case, landscape: width, height, thickness
PHONE_TILT = 15.0                  # leaning back from upright
PHONE_BOTTOM = 70.0                # its lower edge over the desk


def rounded_slab(w, h, t, r):
    """A w x h plate, t thick along y, its corners rounded r: centred, face towards -y."""
    ring = list(box(-w / 2 + r, -h / 2 + r, w / 2 - r, h / 2 - r).buffer(r, quad_segs=8).exterior.coords)[:-1]
    return CrossSection([ring], FillRule.NonZero).extrude(t).translate((0, 0, -t / 2)).rotate((90, 0, 0))


def stand_and_phone(yb):
    """The Ugreen stand (base, hinge, arm, holder) with a phone on it, in the dock's real frame
    (x right, y away from the typist): the base's back edge at y = yb. A stand-in, from photos."""
    import dock as K
    w, d, t = K.UG
    parts = [(K.extrude(K.rounded_rect(w, d, 8.0, 0, yb), 0, t), UGREEN)]
    hinge_y, hinge_z = yb - 12.0, t + 6.0
    parts.append((Manifold.cylinder(26, 6, circular_segments=40).rotate((0, 90, 0)).translate((-13, hinge_y, hinge_z)), UGREEN))
    pw, ph, pt = PHONE_SIZE
    tilt = math.radians(PHONE_TILT)
    centre_z = PHONE_BOTTOM + ph / 2 * math.cos(tilt)
    centre_y = hinge_y + 6.0 + ph / 2 * math.sin(tilt)
    back = (centre_y + pt / 2 * math.cos(tilt), centre_z - pt / 2 * math.sin(tilt))
    puck = Manifold.cylinder(8, 30, circular_segments=60).rotate((-90 - PHONE_TILT, 0, 0))
    parts.append((puck.translate((0, back[0], back[1])), UGREEN))
    for x in (-12, 12):                      # two flat bars from the hinge to the holder
        bar = Manifold.hull_points([(x + sx * 2.5, y + sy * 1.5, z) for sx in (-1, 1) for sy in (-1, 1)
                                    for y, z in ((hinge_y, hinge_z), (back[0] + 6, back[1]))])
        parts.append((bar, UGREEN))
    phone = rounded_slab(pw, ph, pt, 9.0)
    screen = rounded_slab(pw - 6, ph - 6, 0.4, 6.0).translate((0, -pt / 2 - 0.15, 0))
    for m, rgb in ((phone, PHONE), (screen, SCREEN)):
        parts.append((m.rotate((-PHONE_TILT, 0, 0)).translate((0, centre_y, centre_z)), rgb))
    return parts


def dock_scenes():
    """The cyberdeck: the dock on the Ugreen base, both halves on it, the phone on the stand;
    the halves on the dock alone (a tented unibody, no stand); the dock alone, and on the base. In the plan frame (y down), like the other scenes."""
    import dock as K
    k = K.make()
    plan = C.real                                   # real frame <-> plan frame (flip y)
    placed = lambda m: plan(k.p(plan(m)))
    left = [(placed(m), rgb) for m, rgb in left_half() + [(C.pads(0), vrml.PAD)]]
    right = [(plan(k.p(plan(m)).mirror((1, 0, 0))), rgb) for m, rgb in left_half() + [(C.pads(1), vrml.PAD)]]
    dock = [(plan(k.solid), vrml.CASE), (plan(K.magnet_solids(k)), vrml.METAL), (plan(K.feet_solids(k)), vrml.PAD)]
    stand = [(plan(m), rgb) for m, rgb in stand_and_phone(k.yb)]
    base = stand[:1]
    import insert
    import module_shell as M
    ins = [(plan(insert.build()[0].translate((0, 0, M.FLOOR_Z))), vrml.CASE)]
    return {"cyberdeck": dock + left + right + stand, "dock": dock, "dock_base": dock + base,
            "dock_unibody": dock + left + right, "dock_insert": dock + ins + left + right}


BALL_RGB = (0.62, 0.12, 0.14)
PAD_RGB = (0.08, 0.08, 0.09)
PART_RGB = {"ball": BALL_RGB, "pad": PAD_RGB, "pad's back parts": vrml.CHIP, "battery": vrml.BATTERY,
             "nice!nano": vrml.XIAO_PCB, "controller board": (0.1, 0.32, 0.18), "controller header": (.07, .07, .08),
             "stacking pins' plastic": (.07, .07, .08),
             "I2C breakout envelope": (0.1, 0.32, 0.18),
             "FFC bend envelope": (.85, .85, .8), "main board": (0.1, 0.32, 0.18),
            "sensor board": (0.1, 0.32, 0.18), "sensor's parts": vrml.CHIP, "lens": (0.8, 0.8, 0.85),
            "reset": vrml.BUTTON, "power switch": vrml.METAL}


def _built(kind, switch="mx"):
    """(module, its layout, lid, tray, its parts): the trackpad shares the trackball's tray."""
    import importlib
    import trackball.trackball as B
    mod = importlib.import_module(kind + "." + kind)
    L = mod.place()
    main_plan, sensor_plan = B.main_board_plan(L), B.sensor_board_plan(L)
    if kind == "trackball":
        return mod, L, B.lid(L, switch), B.tray(L), B.parts(L, main_plan, sensor_plan, switch)
    return mod, L, mod.lid(L), B.tray(L), mod.parts(L, main_plan, sensor_plan)


def _height(mod, kind, switch):
    return mod.PCB_TOP + mod.CHOC["below_plate"] if kind == "trackball" and switch == "choc" else mod.H


def _shown(mod, kind, name, m, L):
    """A part as rendered: collision checks use the full lever travel, a picture one position."""
    import trackball.trackball as B
    if name == "power switch":
        return B.power_switch(B.main_board_plan(L), full_travel=False)
    if kind == 'trackpad' and name == 'I2C breakout envelope':
        return mod.breakout_visual(L)
    if kind == 'trackpad' and name == 'FFC bend envelope':
        return mod.ffc_visual(L)
    return m


def _colour(name):
    rgb = PART_RGB.get(name)
    if rgb is None:
        rgb = vrml.KEYCAP if name.startswith("keycap") else vrml.SWITCH if name[:2] in ("MX", "ch", "CH") else vrml.SOCKET
    return rgb


def _sensor_screws(L):
    import module_shell as M
    import trackball.trackball as B
    top = B.PLATE_TOP + B.SENSOR_BELOW + B.PCB_T + M.SCREW["head_h"]
    out = Manifold()
    for x, y in B.sensor_holes(L):
        out += M.flat_screw(x, y, top)
    return out


def _module(kind, switch="mx"):
    """A module's solids (dock frame) as (solid, rgb): lid, tray, bump-ons, magnets, screws, parts."""
    import module_shell as M
    mod, L, lid, tray, ps = _built(kind, switch)
    out = [(lid, vrml.CASE), (tray, vrml.CASE), (M.bumpons(), vrml.PAD), (_module_magnets(M), vrml.METAL),
           (M.lid_fasteners(_height(mod, kind, switch)), vrml.METAL), (_sensor_screws(L), vrml.METAL),
           (M.floor_magnet(), vrml.METAL)]
    for name, m in ps:
        m = _shown(mod, kind, name, m, L)
        if name == "nice!nano":
            front = L["nano"][1] + mod.NANO[1] + 0.6
            z = mod.usb_z(L)
            receptacle = Manifold.cube((9.0, 7.9, 3.2)).translate((-4.5, front - 7.9, z - 1.6))
            opening = Manifold.cube((8.4, 7.6, 2.6)).translate((-4.2, front - 7.5, z - 1.3))
            out.append((receptacle - opening, vrml.METAL))
            m -= receptacle
        out.append((m, _colour(name)))
    return out, _height(mod, kind, switch)


LID_RGB, TRAY_RGB, SCREW_RGB = (.72, .76, .8), (.08, .48, .68), (.9, .47, .08)
UP = {"ball", "bearing", "keycap", "MX", "CHOC", "pad"}


def _on_lid(name):
    return name.split(" ")[0] in UP or name.startswith("pad")


def module_assembly(kind):
    """Lid lifted 30 mm off the populated tray with its keys, screws 12 mm over it. No wires drawn."""
    import module_shell as M
    mod, L, lid, tray, ps = _built(kind)
    up = (0, 0, 30)
    out = [(lid.translate(up), vrml.CASE), (tray, vrml.CASE), (M.bumpons(), vrml.PAD), (_module_magnets(M), vrml.METAL),
           (M.floor_magnet(), vrml.METAL), (M.lid_fasteners(mod.H, 42), vrml.METAL), (_sensor_screws(L), vrml.METAL)]
    for name, solid in ps:
        solid = _shown(mod, kind, name, solid, L)
        out.append((solid.translate(up) if _on_lid(name) else solid, _colour(name)))
    return out


def module_instruction_scenes(kind, switch="mx"):
    """Engineering views in contrast colours: the real printed parts, nothing sectioned."""
    import module_shell as M
    mod, L, lid, tray, ps = _built(kind, switch)
    structure = [(lid.translate((0, 0, 24)), LID_RGB), (tray, TRAY_RGB), (M.lid_fasteners(_height(mod, kind, switch), 38), SCREW_RGB)]
    seam = [(lid, LID_RGB), (tray, TRAY_RGB), (M.lid_fasteners(_height(mod, kind, switch)), SCREW_RGB)]
    populated = [(tray, TRAY_RGB), (M.floor_magnet(), vrml.METAL), (_sensor_screws(L), SCREW_RGB)]
    for label, solid in ps:
        if not _on_lid(label):
            populated.append((_shown(mod, kind, label, solid, L), _colour(label)))
    empty = [(tray, TRAY_RGB), (_sensor_screws(L), SCREW_RGB)]
    for label, solid in ps:
        if label in ("battery", "nice!nano", "controller board", "controller header", "stacking pins' plastic", "reset", "sensor board", "lens", "sensor's parts", "I2C breakout envelope", "FFC bend envelope"):
            empty.append((_shown(mod, kind, label, solid, L), _colour(label)))
    from trackball import trackball as _B
    empty.append((_B.stacking_pins(L), vrml.METAL))
    rx, ry = L["reset"] if kind == "trackpad" else mod.sensor_reset(L)
    reset = dict(ps)["reset"]
    tool = Manifold.cylinder(12, .55, circular_segments=32).translate((rx, ry, reset.bounding_box()[2] - 14))
    reset_scene = [(tray, TRAY_RGB), (reset, (.88, .23, .08)), (tool, SCREW_RGB), (dict(ps)["sensor board"], PCB_GREEN)]
    return {"structure": structure, "seam": seam, "tray": populated, "stack": empty, "reset": reset_scene}


def _module_magnets(M):
    out = Manifold()
    for w, n in M.magnets():
        d, h = D["magnet_nominal_size"]
        c = Manifold.cylinder(h, d / 2, circular_segments=32)
        ang = math.degrees(math.atan2(-n[1], -n[0]))
        out += c.rotate((0, 90, 0)).rotate((0, 0, ang)).translate((w[0], w[1], M.MAG_Z))
    return out


def _usb_parts(kind):
    import importlib
    import module_shell as M
    mod = importlib.import_module(kind + "." + kind)
    L = mod.place()
    metal, body, cable = M.usb_connection(L["nano"][1] + mod.NANO[1] + 0.6, mod.usb_z(L))
    return [(metal, vrml.METAL), (body, (0.14, 0.15, 0.17)), (cable, (0.07, 0.08, 0.09))]


def independent_tenting():
    """One stand per half, using the compact floor-magnet group. Stand geometry is illustrative:
    the existing 60 mm holder proxy, not a measurement of the real tilting platform."""
    import dock as K
    centre = C.plan([D["stand_mount"]["centre"]])[0]
    cx, cy = centre[0], -centre[1]
    tilt = K.rot("y", -20.0)
    raised = lambda m: m.transform(tilt[:3]).translate((0, 0, 40))
    platform = raised(Manifold.cylinder(4, 30, circular_segments=64).translate((0, 0, -4)))
    base = K.extrude(K.rounded_rect(*K.UG[:2], 8, 0, K.UG[1] / 2), 0, K.UG[2])
    arm = Manifold.hull_points([(x, y, z) for x in (-5, 5) for y, z in ((22, 3.5), (28, 3.5), (-3, 37), (3, 37))])
    out = []
    for half, sx in ((0, 1), (1, -1)):
        parts = [(base, UGREEN), (arm, UGREEN), (platform, UGREEN)]
        for x, y in C.plan(D["stand_mount"]["magnets"]):
            d, h = D["magnet_nominal_size"]
            disc = Manifold.cylinder(h, d / 2, circular_segments=32).translate((x - cx, -y - cy, 0))
            parts.append((raised(disc), vrml.METAL))
        for m, rgb in left_half() + [(C.pads(half), vrml.PAD)]:
            parts.append((raised(C.real(m).translate((-cx, -cy, D["magnet_nominal_size"][1]))), rgb))
        for m, rgb in parts:
            if sx < 0:
                m = m.mirror((1, 0, 0))
            out.append((C.real(m.translate((-80 * sx, 0, 0))), rgb))
    return out


def module_scenes(k):
    """Each module on its own (closed, and cut open down the middle), the trackball module in the
    dock with the halves, and on the desk snapped onto the left half. Plan frame (y down)."""
    import dock as K
    import module_shell as M
    plan = C.real
    scenes = {}
    for kind in ("trackball", "trackpad"):
        parts, height = _module(kind)
        scenes[kind] = [(plan(m), rgb) for m, rgb in parts]
        scenes[kind + "_rear"] = scenes[kind]
        scenes[kind + "_assembly"] = [(plan(m), rgb) for m, rgb in module_assembly(kind)]
        for label, solids in module_instruction_scenes(kind).items():
            scenes[kind + "_" + label] = [(plan(m), rgb) for m, rgb in solids]
        cut = [(m.trim_by_plane((-1, 0, 0), 0.0), rgb) for m, rgb in parts]
        scenes[kind + "_open"] = [(plan(m), rgb) for m, rgb in cut if not m.trim_by_plane((-1, 0, 0), 0.0).is_empty()]
        scenes[kind + "_docked"] = [(plan(m.translate((0, 0, M.FLOOR_Z))), rgb) for m, rgb in parts]
        flat = K.Placement(0.0)
        mag = [(K.WALL_OUT, -K.D["magnets_side_y"][i], K.D["magnet_side_z"]) for i in K.DRAWER_MAGS]
        m0 = flat.points(mag)
        w, n = [q for q in M.magnets() if q[0][0] < 0][0]
        shift = (w - np.array(m0[0][:2])) @ n
        half = [(plan(flat(plan(m)).translate((n[0] * shift, n[1] * shift, 0))), rgb)
                for m, rgb in left_half() + [(C.pads(0), vrml.PAD)]]
        scenes[kind + "_with_half"] = scenes[kind] + half
        if kind == "trackball":
            choc_parts, _ = _module(kind, "choc")
            scenes["trackball_choc"] = [(plan(m), rgb) for m, rgb in choc_parts]
            for label, solids in module_instruction_scenes(kind, "choc").items():
                scenes["trackball_choc_" + label] = [(plan(m), rgb) for m, rgb in solids]
        connected = parts + _usb_parts(kind)
        scenes[kind + "_usb"] = [(plan(m), rgb) for m, rgb in connected]
        cut = [(m.trim_by_plane((-1, 0, 0), 0.0), rgb) for m, rgb in parts]
        scenes[kind + "_usb_open"] = [(plan(m), rgb) for m, rgb in cut if not m.is_empty()] + [
            (plan(m), rgb) for m, rgb in _usb_parts(kind)]
        k = K.make() if k is None else k
        scenes[kind + "_usb_dock"] = [(plan(k.solid), vrml.CASE)] + [
            (plan(m.translate((0, 0, M.FLOOR_Z))), rgb) for m, rgb in connected]
    # Alternative controller: actual published Seeed reference mesh, not the nano envelope.
    from trackball import trackball as B
    from trackball.controllers import xiao, xiao_usb_z
    mod, L, lid, tray, ps = _built('trackball', 'choc')
    floor = B.SOCKET_BOT - B.NANO_GAP - B.NANO[2]
    controller = xiao(B.xiao_back(L), floor)
    stack = [(tray, TRAY_RGB), (controller, vrml.METAL)]
    for label, solid in ps:
        if label in ('battery', 'sensor board', 'reset', 'lens', "sensor's parts", 'controller board', 'controller header', "stacking pins' plastic"):
            stack.append((solid, _colour(label)))
    stack.append((B.stacking_pins(L), vrml.METAL))
    scenes['trackball_xiao_stack'] = [(plan(m), rgb) for m, rgb in stack]
    populated = [(tray, TRAY_RGB), (lid, LID_RGB), (controller, vrml.METAL)] + [
        (solid, _colour(label)) for label, solid in ps if label != 'nice!nano']
    cut = [(m.trim_by_plane((-1, 0, 0), 0), rgb) for m, rgb in populated]
    plug = M.usb_connection(B.xiao_back(L), xiao_usb_z(floor))
    scenes['trackball_xiao_usb_open'] = [(plan(m), rgb) for m, rgb in cut if not m.is_empty()] + [
        (plan(m), rgb) for m, rgb in zip(plug, (vrml.METAL, (.14, .15, .17), (.07, .08, .09)))]
    return scenes


def main():
    left = left_half()
    seam = D["wall_out"]
    pads_left, pads_right = (C.pads(0), vrml.PAD), (C.pads(1), vrml.PAD)
    unibody = left + [pads_left] + [(m.mirror((1, 0, 0)).translate((2 * seam, 0, 0)), rgb)
                                    for m, rgb in left + [pads_right]]
    stacked = left + [pads_left] + [(m.mirror((0, 0, 1)), rgb) for m, rgb in left + [pads_right]]
    # the speck of board render_boards.py adds: a point inside a floor, and the scene's
    # z shift that puts that floor around z = 0 (the board's top face)
    xs = [p[0] for p in D["case_outline"]]
    ys = [p[1] for p in D["case_outline"]]
    centre_y = (min(ys) + max(ys)) / 2
    scenes = {
        "unibody": {"speck": [seam - 12, centre_y], "z": -2.0, "size": 2 * (seam - min(xs))},
        "stacked": {"speck": [(min(xs) + seam) / 2, centre_y], "z": 0.0, "size": max(ys) - min(ys)},
    }
    # the dock scenes: the speck in the spine's block behind the drawer, above the base
    dock = dock_scenes()
    import dock as K
    mods = module_scenes(None)
    dock["cyberdeck"] += mods.pop("trackball_docked")
    dock["dock_unibody"] += mods["trackpad_docked"]
    mods.pop("trackpad_docked")
    for name in dock:
        scenes[name] = {"speck": [0.0, 7.0], "z": -12.0, "size": 215.0}
    dock["independent_tenting"] = independent_tenting()
    scenes["independent_tenting"] = {"speck": [0.0, 0.0], "z": 0.0, "size": 270.0}
    # the modules: the speck in the battery (its front corner on the left, standing on the plate)
    import module_shell as M
    for name in mods:
        bat_y = -(json.load(open("%s/design.json" % name.split("_")[0]))["battery"][1]
                 if name.startswith("trackball") else json.load(open("trackpad/design.json"))["layout"]["battery"][1])
        scenes[name] = {"speck": [0.0, 55.0], "z": -(M.FEET + M.BOTTOM_T + 4.0), "size": 100.0}
        if name.endswith("_rear"):
            scenes[name] = {"speck": [0.0, 20.0], "z": -14.0, "size": 80.0}
        if "_usb" in name:
            scenes[name]["speck"] = [0.0, 40.0]
            if name.endswith("_dock"):
                scenes[name]["speck"] = [0.0, 7.0]
                scenes[name]["z"] = -12.0
                scenes[name]["size"] = 215.0
        dock[name] = mods[name]
    for name, parts in (("unibody", unibody), ("stacked", stacked), *dock.items()):
        dz = scenes[name]["z"]
        vrml.write_parts(f".render/3d/{name}.wrl", [(m.translate((0, 0, dz)), rgb) for m, rgb in parts])
    json.dump(scenes, open(".render/scenes.json", "w"), indent=1)


if __name__ == "__main__":
    main()
