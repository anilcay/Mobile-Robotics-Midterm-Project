"""Render the SeraBot preview assembly (run after build_serabot.py).

Run through the bridge. Optional globals set beforehand with ``-c``:
  RENDER_DIR  output folder (default: <package>/doc/renders)
  VIEWS       subset of VIEW_SETUPS keys (default: all)
  RES         (width, height) in pixels (default: (1200, 800))
"""

import math
import os

import bpy
from mathutils import Vector

PKG = os.path.dirname(os.path.dirname(__file__))

# name: (camera location, look-at point, orthographic scale or None for perspective)
VIEW_SETUPS = {
    'persp_front': (Vector((1.15, -0.95, 0.75)), Vector((0.0, 0.0, 0.21)), None),
    'persp_back': (Vector((-1.1, 0.95, 0.72)), Vector((0.0, 0.0, 0.21)), None),
    'front': (Vector((2.0, 0.0, 0.24)), Vector((0.0, 0.0, 0.24)), 0.85),
    'side': (Vector((0.0, -2.0, 0.24)), Vector((0.0, 0.0, 0.24)), 0.85),
    'top': (Vector((0.0, 0.0, 2.0)), Vector((0.0, 0.0, 0.0)), 0.85),
}


def setup_stage() -> bpy.types.Object:
    """Ground, lights, world and camera in a 'render_stage' collection."""
    scene = bpy.context.scene
    stage = bpy.data.collections.get('render_stage')
    if stage is None:
        stage = bpy.data.collections.new('render_stage')
        scene.collection.children.link(stage)
    for obj in list(stage.objects):
        bpy.data.objects.remove(obj)
    for obj in [o for o in scene.objects if o.type in {'LIGHT', 'CAMERA'}]:
        bpy.data.objects.remove(obj)

    ground_mat = bpy.data.materials.get('stage_ground') or bpy.data.materials.new('stage_ground')
    ground_mat.use_nodes = True
    ground_mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (
        0.36, 0.34, 0.31, 1.0)
    mesh = bpy.data.meshes.new('stage_ground')
    mesh.from_pydata([(-4, -4, 0), (4, -4, 0), (4, 4, 0), (-4, 4, 0)], [], [(0, 1, 2, 3)])
    mesh.materials.append(ground_mat)
    stage.objects.link(bpy.data.objects.new('stage_ground', mesh))

    for name, energy, rot, angle in (('key', 3.0, (50, 0, 35), 8),
                                     ('fill', 1.0, (65, 0, 215), 30)):
        light = bpy.data.lights.new(name, 'SUN')
        light.energy = energy
        light.angle = math.radians(angle)
        obj = bpy.data.objects.new(name, light)
        obj.rotation_euler = [math.radians(a) for a in rot]
        stage.objects.link(obj)

    cam = bpy.data.objects.new('render_camera', bpy.data.cameras.new('render_camera'))
    stage.objects.link(cam)
    scene.camera = cam

    world = scene.world or bpy.data.worlds.new('World')
    scene.world = world
    world.use_nodes = True
    world.node_tree.nodes['Background'].inputs['Color'].default_value = (0.78, 0.80, 0.83, 1)
    world.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.9
    scene.render.engine = 'BLENDER_EEVEE'
    scene.view_settings.view_transform = 'Standard'
    return cam


def render(names, out_dir, res) -> list:
    cam = setup_stage()
    scene = bpy.context.scene
    scene.render.resolution_x, scene.render.resolution_y = res
    os.makedirs(out_dir, exist_ok=True)
    paths = []
    for name in names:
        loc, look, ortho = VIEW_SETUPS[name]
        cam.location = loc
        if name == 'top':
            cam.rotation_euler = (0, 0, -math.pi / 2)  # robot front (+X) at image top
        else:
            cam.rotation_euler = (look - loc).to_track_quat('-Z', 'Y').to_euler()
        cam.data.type = 'PERSP' if ortho is None else 'ORTHO'
        if ortho is None:
            cam.data.lens = 50
        else:
            cam.data.ortho_scale = ortho
        cam.data.clip_start = 0.01
        scene.render.filepath = os.path.join(out_dir, f'serabot_{name}.png')
        bpy.ops.render.render(write_still=True)
        paths.append(scene.render.filepath)
    return paths


result = render(globals().get('VIEWS', list(VIEW_SETUPS)),
                globals().get('RENDER_DIR', os.path.join(PKG, 'doc', 'renders')),
                globals().get('RES', (1200, 800)))
