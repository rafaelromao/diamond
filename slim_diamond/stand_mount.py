"""Check the independent-stand contact and write 1:1 magnet-placement templates.

This specifies the minimum clear flat contact patch, not unmeasured Ugreen platform dimensions.
Glue three of the common 8 x 1.5 mm discs to each platform, on the circular pattern.
Run from slim_diamond/: python3 stand_mount.py
"""
import math
from pathlib import Path

import numpy as np
from shapely.geometry import Point, Polygon
from shapely.ops import unary_union

import case as C


def mesh_centroid(solid):
    """Volume centroid from signed mesh tetrahedra (Manifold has no Python mass-properties API)."""
    mesh = solid.to_mesh()
    vertices = np.asarray(mesh.vert_properties, dtype=float)[:, :3]
    faces = np.asarray(mesh.tri_verts)
    a, b, c = (vertices[faces[:, i]] for i in range(3))
    volumes = np.einsum("ij,ij->i", a, np.cross(b, c)) / 6
    return np.sum(volumes[:, None] * (a + b + c) / 4, axis=0) / np.sum(volumes)


def estimated_centre_of_gravity():
    """Mass-weighted estimate, not a measured balance point. Assumptions: solid nylon 1.14 g/cc,
    FR4 1.85 g/cc, battery 12 g, each switch/cap/socket 2/0.6/0.3 g, MCU/JST/switch 3/0.7/0.3 g,
    neodymium 7.5 g/cc. The right half mirrors this estimate. Verify the assembled hardware.
    """
    parts = []
    def add(mass, solid):
        parts.append((mass, mesh_centroid(solid)))
    body = C.build()
    add(body.volume() / 1000 * 1.14, body)
    plate, _ = C.plate()
    add(plate.volume() / 1000 * 1.14,
        C.to_desk_solid(plate.translate((0, 0, C.PCB_T + C.PLATE["gap"]))))
    pcb = C.to_desk_solid(C.slab(Polygon(C.D["pcb_outline"]), 0, C.PCB_T))
    add(pcb.volume() / 1000 * 1.85, pcb)
    add(12, C.battery())
    for key in C.D["keys"].values():
        for mass, z in ((2, C.PCB_T + 3), (0.6, C.PCB_T + 7), (0.3, -1)):
            parts.append((mass, np.array(C.to_desk(key["x"], key["y"], z))))
    for name, mass, z in (("xiao", 3, -2), ("jst", 0.7, -2), ("power_switch", 0.3, -0.8)):
        part = C.D[name]
        parts.append((mass, np.array(C.to_desk(part["x"], part["y"], z))))
    d, h = C.D["magnet_nominal_size"]
    magnet_mass = math.pi * (d / 2) ** 2 * h / 1000 * 7.5
    for x, y in C.plan(C.D["magnets_floor"]):
        parts.append((magnet_mass, np.array((x, y, h / 2))))
    for y in C.D["magnets_side_y"]:
        parts.append((magnet_mass, np.array((C.WALL_OUT - h / 2, y, C.D["magnet_side_z"]))))
    mass = sum(m for m, _ in parts)
    return sum(m * p for m, p in parts) / mass, mass


def check():
    mount = C.D["stand_mount"]
    centre = C.plan([mount["centre"]])[0]
    points = C.plan(mount["magnets"])
    radius = mount["contact_diameter"] / 2
    magnet_radius = C.D["magnet_floor_size"][0] / 2
    all_pockets = C.D["magnets_floor"]
    assert len(points) == 3, "the stand contact uses exactly three magnets"
    assert all(p in all_pockets for p in mount["magnets"]), "stand magnets missing from the case"
    assert all(math.dist(p, centre) + magnet_radius < radius for p in points)
    floor_room = unary_union([Polygon(C.plan(p)) for p in C.D["magnet_floor_room"]])
    assert all(floor_room.covers(Point(p)) for p in points), "stand contacts enter the antenna/floor exclusion"
    radii = [math.dist(p, centre) for p in points]
    assert max(radii) - min(radii) < 1e-4, "stand magnets must lie on one circle"
    assert all(abs(r - mount["ring_radius"]) < 1e-4 for r in radii)
    assert np.linalg.norm(np.mean(points, axis=0) - centre) < 1e-4, "triangle must be equally spaced"
    cog, mass = estimated_centre_of_gravity()
    assert np.linalg.norm(cog[:2] - centre) < 0.5, "ring is no longer centred on the estimated mass"
    assert Polygon(points).contains(Point(cog[:2])), "centre of gravity lies outside the support triangle"
    # Floor pockets open at the case's floor plane. The common stand magnets meet them flush,
    # leaving the bump-ons above the platform rather than rocking the keyboard on its feet.
    stand_disc = C.D["magnet_nominal_size"][1]
    triangle = Polygon(points)
    for tilt in (0, 20, 35):
        shift = (cog[2] + stand_disc) * math.tan(math.radians(tilt))
        for direction in range(0, 360, 30):
            load = Point(cog[0] + shift * math.cos(math.radians(direction)),
                         cog[1] + shift * math.sin(math.radians(direction)))
            assert triangle.contains(load), "gravity projection leaves the stand-contact triangle"
    for half in (0, 1):
        clearance = C.pads(half).bounding_box()[2] + stand_disc
        assert clearance > 0.5
        print("  %s half: three platform magnets, feet %.2f mm clear of the platform" %
              ("left" if half == 0 else "right", clearance))
    print("  required flat contact circle: %.1f mm; real platform fit remains unconfirmed" %
          mount["contact_diameter"])
    print("  ring radius %.1f mm, estimated COG (%.2f, %.2f) mm, estimated assembled mass %.1f g" %
          (mount["ring_radius"], cog[0], cog[1], mass))
    print("  estimated gravity projection stays inside the triangle through 35 degrees of tilt")
    return centre, points


def main():
    centre, points = check()
    diameter = C.D["stand_mount"]["contact_diameter"]
    radius = diameter / 2
    for name, sx in (("left", 1), ("right", -1)):
        circles = []
        for x, y in points:
            x, y = sx * (x - centre[0]), y - centre[1]
            circles.append('<circle cx="%.4f" cy="%.4f" r="%g"/>' % (x, y, C.D["magnet_floor_size"][0] / 2))
            circles.append('<path d="M %.4f %.4f h 2 M %.4f %.4f v 2"/>' % (x - 1, y, x, y - 1))
        svg = ('<svg xmlns="http://www.w3.org/2000/svg" width="%gmm" height="%gmm" '
               'viewBox="%g %g %g %g"><title>%s half stand magnets: print at 100%%</title>'
               '<g fill="none" stroke="black" stroke-width="0.15">'
               '<circle r="%g" stroke-dasharray="1 1"/><circle r="%g" stroke-dasharray="0.5 1"/>%s</g>'
               '<text x="0" y="1" text-anchor="middle" font-size="2">%s / 100%%</text></svg>') % (
                   diameter, diameter, -radius, -radius, diameter, diameter, name,
                   radius - 0.1, C.D["stand_mount"]["ring_radius"], "".join(circles), name)
        path = Path("case") / ("stand_magnet_template_" + name + ".svg")
        path.parent.mkdir(exist_ok=True)
        path.write_text(svg)
        print("  wrote", path)


if __name__ == "__main__":
    main()
