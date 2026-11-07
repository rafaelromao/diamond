"""Controller placement relative to the shared rear USB datum.

XIAO measurements come from the Seeed-published STEP mesh in models/.
The nice!nano envelope is nominal; clone connector dimensions must be measured.
Both stand on the same header on the controller board, on the nice!nano's rows: a XIAO's rows are
XIAO_SETBACK further from the USB-C mouth, so its mouth sits that far inside the rear plane.
"""
from functools import lru_cache
from pathlib import Path

XIAO_WIDTH = 17.78
XIAO_LENGTH = 20.955
XIAO_USB_OVERHANG = 1.527
XIAO_PCB_MAX_T = 1.25
XIAO_SETBACK = 0.2155
# Coordinates from the mouth plane of Seeed's STEP, not the overall shell tabs.
XIAO_MOUTH_X = 13.808639836
XIAO_MOUTH_Z = -6.118725947
XIAO_MOUTH_Y = 2.605
XIAO_COMPONENT_FACE_Y = 1.0


@lru_cache
def reference_model():
    import numpy as np
    from manifold3d import Manifold, Mesh

    with np.load(Path(__file__).parent / 'models/xiao_reference.npz') as data:
        return Manifold(Mesh(data['vertices'], data['triangles']))


def xiao(back, component_face_z):
    """Face down (turned over, not mirrored); STEP mouth at the rear plane, on the USB passage."""
    return reference_model().transform([
        [0, 0, -1, XIAO_MOUTH_Z],
        [1, 0, 0, back - XIAO_MOUTH_X],
        [0, -1, 0, component_face_z + XIAO_COMPONENT_FACE_Y],
    ])


def xiao_usb_z(component_face_z):
    return component_face_z + XIAO_COMPONENT_FACE_Y - XIAO_MOUTH_Y
