"""Build and export the mesh orientation / colour test object (ADR-015).

Run through the bridge:  python bridge_client.py make_orientation_test.py
A grey 0.2 m cube with a red arrow along +X, a green arrow along +Y and a blue
cap on +Z, exported as:
  meshes/test/orientation_cube_yup.glb  (glTF default "+Y Up" conversion)
  meshes/test/orientation_cube_zup.glb  (no conversion, raw Blender axes)
  meshes/test/orientation_cube.obj/.mtl (Z up, Y forward = raw Blender axes)
urdf/test/mesh_test.urdf.xacro shows them next to a primitive reference.
"""

import importlib
import math
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import mesh_kit as mk  # noqa: E402

importlib.reload(mk)

PKG = os.path.dirname(os.path.dirname(__file__))
OUT = os.path.join(PKG, 'meshes', 'test')

grey = mk.material('test_grey', (0.45, 0.45, 0.45))
red = mk.material('test_red', (0.8, 0.02, 0.02))
green = mk.material('test_green', (0.02, 0.6, 0.02))
blue = mk.material('test_blue', (0.02, 0.05, 0.8))

link = mk.LinkMesh('orientation_cube')
link.box((0.2, 0.2, 0.2), grey)
# +X: long red arrow (shaft + cone head)
link.cylinder(0.02, 0.02, 0.15, red, loc=(0.175, 0, 0), rot=(0, math.pi / 2, 0))
link.cylinder(0.04, 0.0, 0.06, red, loc=(0.28, 0, 0), rot=(0, math.pi / 2, 0))
# +Y: shorter green arrow
link.cylinder(0.015, 0.015, 0.08, green, loc=(0, 0.14, 0), rot=(-math.pi / 2, 0, 0))
link.cylinder(0.03, 0.0, 0.04, green, loc=(0, 0.2, 0), rot=(-math.pi / 2, 0, 0))
# +Z: blue cap
link.cylinder(0.05, 0.05, 0.03, blue, loc=(0, 0, 0.115))

coll = mk.collection('orientation_test')
obj = link.to_object(coll)
paths = [
    mk.export_glb(obj, os.path.join(OUT, 'orientation_cube_yup.glb'), yup=True),
    mk.export_glb(obj, os.path.join(OUT, 'orientation_cube_zup.glb'), yup=False),
    mk.export_obj(obj, os.path.join(OUT, 'orientation_cube.obj')),
]
result = {
    'triangles': mk.triangle_count([obj]),
    'bbox_min': [round(min(v.co[i] for v in obj.data.vertices), 3) for i in range(3)],
    'bbox_max': [round(max(v.co[i] for v in obj.data.vertices), 3) for i in range(3)],
    'files': {os.path.basename(p): os.path.getsize(p) for p in os.listdir(OUT)
              for p in [os.path.join(OUT, p)]},
}
