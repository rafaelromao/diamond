"""Import Seeed's STEP for nominal fit checks and renders, not physical qualification.

Optional tooling: pip install cadquery-ocp==8.0.1.1.0 trimesh numpy manifold3d
Usage: python trackball/import_xiao_reference.py /path/to/manufacturer-3d.zip
"""
from pathlib import Path
from zipfile import ZipFile
import sys
import tempfile
import hashlib
import json
import numpy as np
import trimesh
from manifold3d import Manifold, Mesh, OpType
from OCP.STEPControl import STEPControl_Reader
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_SOLID, TopAbs_FACE, TopAbs_REVERSED
from OCP.TopoDS import TopoDS
from OCP.TopLoc import TopLoc_Location
from OCP.BRep import BRep_Tool
from OCP.BRepMesh import BRepMesh_IncrementalMesh

archive = Path(sys.argv[1])
with ZipFile(archive) as z:
    name = next(n for n in z.namelist() if n.endswith('.step'))
    step = z.read(name)
reader = STEPControl_Reader()
with tempfile.NamedTemporaryFile(suffix='.step') as f:
    f.write(step)
    f.flush()
    reader.ReadFile(f.name)
reader.TransferRoots()
whole = reader.OneShape()
BRepMesh_IncrementalMesh(whole, .03, False, .15, True).Perform()
solids = TopExp_Explorer(whole, TopAbs_SOLID)
components = []
records = []
index = 0
while solids.More():
    vertices, triangles = [], []
    faces = TopExp_Explorer(solids.Current(), TopAbs_FACE)
    while faces.More():
        face = TopoDS.Face(faces.Current())
        loc = TopLoc_Location()
        tri = BRep_Tool.Triangulation_s(face, loc)
        offset = len(vertices)
        for i in range(1, tri.NbNodes() + 1):
            p = tri.Node(i).Transformed(loc.Transformation())
            vertices.append((p.X(), p.Y(), p.Z()))
        for i in range(1, tri.NbTriangles() + 1):
            ids = [n - 1 + offset for n in tri.Triangle(i).Get()]
            triangles.append(ids[::-1] if face.Orientation() == TopAbs_REVERSED else ids)
        faces.Next()
    mesh = trimesh.Trimesh(vertices=vertices, faces=triangles, process=True)
    mesh.fix_normals()
    m = Manifold(Mesh(np.asarray(mesh.vertices, dtype=np.float32),
                      np.asarray(mesh.faces, dtype=np.uint32)))
    assert m.status().name == 'NoError', (index, m.status())
    records.append(dict(solid=index, bounds=mesh.bounds.tolist(), volume=float(m.volume())))
    components.append(m)
    index += 1
    solids.Next()
combined = Manifold.batch_boolean(components, OpType.Add)
assert combined.status().name == 'NoError'
mesh = combined.to_mesh()
folder = Path(__file__).resolve().parent / 'models'
folder.mkdir(exist_ok=True)
np.savez_compressed(folder / 'xiao_reference.npz', vertices=np.asarray(mesh.vert_properties)[:, :3],
                    triangles=np.asarray(mesh.tri_verts))
(folder / 'xiao_reference.json').write_text(json.dumps(dict(
    source='https://files.seeedstudio.com/wiki/XIAO-BLE/seeed-studio-xiao-nrf52840-3d-model.zip',
    archive_sha256=hashlib.sha256(archive.read_bytes()).hexdigest(),
    step_sha256=hashlib.sha256(step).hexdigest(),
    model=name, note='Published on Seeed XIAO nRF52840 Sense resources; component envelope is not a measurement of every plain XIAO or clone revision.',
    axes='X towards USB, Y PCB thickness / components up, Z across the PCB',
    linear_tessellation_mm=.03, solids=records), indent=2) + '\n')
print('mesh',len(mesh.vert_properties),len(mesh.tri_verts),combined.bounding_box(),combined.volume())
