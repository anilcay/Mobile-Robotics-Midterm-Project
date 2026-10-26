"""Build the greenhouse decoration meshes (docs/INTERFACES.md section 4.2).

Run through S1's bridge (Blender started with bridge_server.py):
  python src/serabot_description/blender/bridge_client.py \
      src/serabot_gazebo/blender/build_greenhouse.py

Models (one object each, origin = the world link frame that uses it):
  planter_bed       wooden bed box, same outer size as the bed collision box
  tomato_row        plants, stakes, flowers, red and green tomatoes for one bed
  greenhouse_frame  arched steel frame; posts sit inside the wall collision boxes
  plant_pot         pot obstacle (same radius/height as its collision cylinder)

Exports models/<model>/meshes/<model>.obj + .mtl with Blender's linear colours
(the Gazebo colour set, ADR-019; the world is only rendered by Gazebo), saves
blender/greenhouse.blend and places linked copies in "greenhouse_preview".
Layout constants come from tools/generate_greenhouse.py.
"""

import importlib
import math
import os
import random
import sys
import tempfile

import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(PKG))
sys.path.insert(0, os.path.join(REPO, 'src', 'serabot_description', 'blender'))
sys.path.insert(0, os.path.join(PKG, 'tools'))
import generate_greenhouse as layout  # noqa: E402
import mesh_kit as mk  # noqa: E402

importlib.reload(mk)
importlib.reload(layout)

MODELS = os.path.join(PKG, 'models')
BLEND = os.path.join(HERE, 'greenhouse.blend')

L, W, H = layout.BED_LENGTH, layout.BED_WIDTH, layout.BED_HEIGHT
SOIL_Z = H - 0.015            # soil surface inside the bed
RIM_T = 0.012                 # top rim board thickness

# Camera target (INTERFACES 4.2): ripe tomatoes at 0.40-0.55 m, pure red.
TRUSS_Z = (0.45, 0.50)
TRUSS_Y = (0.18, 0.20)
TOMATO_R = (0.032, 0.040)
PLANT_SPACING = 0.5

# --- Palette (display sRGB, except the pure red target) ---
PLANK = mk.material('gh_plank', mk.srgb(0.62, 0.45, 0.30), 0.8)
POST = mk.material('gh_post', mk.srgb(0.45, 0.32, 0.21), 0.85)
BACKING = mk.material('gh_backing', mk.srgb(0.22, 0.16, 0.11), 0.9)
SOIL = mk.material('gh_soil', mk.srgb(0.27, 0.19, 0.14), 0.95)
PIPE = mk.material('gh_pipe', mk.srgb(0.08, 0.08, 0.08), 0.5)
BAMBOO = mk.material('gh_bamboo', mk.srgb(0.80, 0.70, 0.45), 0.7)
STEM = mk.material('gh_stem', mk.srgb(0.30, 0.50, 0.20), 0.7)
LEAF_A = mk.material('gh_leaf_a', mk.srgb(0.25, 0.55, 0.20), 0.6)
LEAF_B = mk.material('gh_leaf_b', mk.srgb(0.33, 0.62, 0.24), 0.6)
SEPAL = mk.material('gh_sepal', mk.srgb(0.20, 0.42, 0.15), 0.6)
FLOWER = mk.material('gh_flower', mk.srgb(0.95, 0.82, 0.20), 0.6)
RED = mk.material('gh_tomato_red', (1.0, 0.0, 0.0), 0.35)
UNRIPE = mk.material('gh_tomato_green', mk.srgb(0.50, 0.72, 0.28), 0.4)
STEEL = mk.material('gh_steel', mk.srgb(0.72, 0.74, 0.76), 0.4, 0.5)
POT = mk.material('gh_pot', mk.srgb(0.42, 0.48, 0.56), 0.6)


def segment(m: mk.LinkMesh, a, b, r0: float, r1: float, mat, sides: int = 6) -> None:
    """Cylinder (or cone) from point a to point b."""
    a, b = Vector(a), Vector(b)
    d = b - a
    rot = Vector((0, 0, 1)).rotation_difference(d.normalized()).to_euler()
    m.cylinder(r0, r1, d.length, mat, loc=tuple((a + b) / 2), rot=tuple(rot),
               segments=sides, smooth=False)


def planter_bed() -> mk.LinkMesh:
    m = mk.LinkMesh('planter_bed')
    plank_h, gap = (H - RIM_T) / 3, 0.004
    for k in range(3):
        z = k * plank_h + plank_h / 2
        size_h = plank_h - gap
        for s in (1, -1):
            m.box((L - 0.12, 0.03, size_h), PLANK, loc=(0, s * (W / 2 - 0.015), z),
                  bevel=0.004)
            m.box((0.03, W - 0.12, size_h), PLANK, loc=(s * (L / 2 - 0.015), 0, z),
                  bevel=0.004)
    for sx in (1, -1):
        for sy in (1, -1):
            m.box((0.06, 0.06, H - RIM_T), POST,
                  loc=(sx * (L / 2 - 0.03), sy * (W / 2 - 0.03), (H - RIM_T) / 2))
    # Dark backing seen through the plank gaps.
    m.box((L - 0.05, W - 0.05, H - RIM_T), BACKING, loc=(0, 0, (H - RIM_T) / 2))
    for s in (1, -1):
        m.box((L, 0.06, RIM_T), POST, loc=(0, s * (W / 2 - 0.03), H - RIM_T / 2))
        m.box((0.06, W - 0.12, RIM_T), POST, loc=(s * (L / 2 - 0.03), 0, H - RIM_T / 2))
    m.box((L - 0.12, W - 0.12, 0.02), SOIL, loc=(0, 0, SOIL_Z - 0.01))
    segment(m, (-(L / 2 - 0.08), 0, SOIL_Z + 0.005), (L / 2 - 0.08, 0, SOIL_Z + 0.005),
            0.008, 0.008, PIPE, 8)
    return m


def leaf(m: mk.LinkMesh, rng: random.Random, loc, size: float) -> None:
    m.ellipsoid((size, size * 0.5, 0.010), rng.choice((LEAF_A, LEAF_B)), loc=loc,
                rot=(rng.uniform(-0.4, 0.4), rng.uniform(-0.3, 0.3),
                     rng.uniform(0, math.pi)),
                segments=8, rings=4)


def tomato(m: mk.LinkMesh, loc, r: float, mat) -> None:
    m.ellipsoid((r, r, r * 0.88), mat, loc=loc, segments=10, rings=6)
    m.cylinder(r * 0.35, r * 0.15, 0.006, SEPAL, loc=(loc[0], loc[1], loc[2] + r * 0.88),
               segments=5, smooth=False)


def plant(m: mk.LinkMesh, rng: random.Random, x: float, low_side: int) -> None:
    top = 0.86
    segment(m, (x + 0.035, 0, SOIL_Z), (x + 0.035, 0, 0.90), 0.007, 0.006, BAMBOO)
    pts = [(x, 0, SOIL_Z)]
    for k in range(1, 6):
        z = SOIL_Z + (top - SOIL_Z) * k / 5
        pts.append((x + rng.uniform(-0.02, 0.02), rng.uniform(-0.02, 0.02), z))
    for k, (a, b) in enumerate(zip(pts, pts[1:])):
        segment(m, a, b, 0.009 - 0.0008 * k, 0.009 - 0.0008 * (k + 1), STEM)

    # Leaves above the trusses and towards the bed centre, so the corridor-side
    # tomatoes stay visible to the camera.
    for k in range(12):
        z = rng.uniform(0.56, top + 0.02)
        side = 1 if k % 2 else -1
        leaf(m, rng, (x + rng.uniform(-0.12, 0.12), side * rng.uniform(0.03, 0.15), z),
             rng.uniform(0.055, 0.075))
    for k in range(2):
        leaf(m, rng, (x + rng.uniform(-0.1, 0.1), rng.uniform(-0.06, 0.06),
                      rng.uniform(0.44, 0.52)), 0.05)

    # Ripe trusses: one per side, hanging over the bed edge at camera height.
    for side in (low_side, -low_side):
        cz = TRUSS_Z[0] if side == low_side else TRUSS_Z[1]
        cy = side * rng.uniform(*TRUSS_Y)
        cx = x + rng.uniform(-0.06, 0.06)
        segment(m, (x, 0, cz + 0.09), (cx, cy, cz + 0.05), 0.004, 0.003, STEM, 5)
        count = 3 if rng.random() < 0.6 else 4
        for k in range(count):
            a = 2 * math.pi * k / count + rng.uniform(-0.3, 0.3)
            off = 0.0 if k == 0 and count == 4 else 0.035
            # Spread around the truss end, mostly along the bed, slightly drooping.
            tomato(m, (cx + off * math.cos(a), cy + 0.5 * off * math.sin(a), cz - 0.012 * k),
                   rng.uniform(*TOMATO_R), RED)

    # Unripe truss higher up (green, ignored by the colour detector).
    if rng.random() < 0.6:
        side = rng.choice((1, -1))
        cx, cy, cz = x + rng.uniform(-0.08, 0.08), side * 0.15, rng.uniform(0.62, 0.70)
        for k in range(rng.randint(2, 3)):
            tomato(m, (cx + 0.03 * (k - 1), cy, cz + 0.02 * (k % 2)), 0.025, UNRIPE)

    for k in range(2):
        m.ellipsoid((0.012, 0.012, 0.008), FLOWER,
                    loc=(x + rng.uniform(-0.08, 0.08), rng.uniform(-0.12, 0.12),
                         rng.uniform(0.74, 0.86)), segments=6, rings=4)


def tomato_row() -> mk.LinkMesh:
    m = mk.LinkMesh('tomato_row')
    rng = random.Random(7)
    count = int(round(L / PLANT_SPACING))
    for i in range(count):
        x = -L / 2 + PLANT_SPACING * (i + 0.5)
        plant(m, rng, x, 1 if i % 2 else -1)
    return m


def greenhouse_frame() -> mk.LinkMesh:
    m = mk.LinkMesh('greenhouse_frame')
    t = layout.WALL_THICKNESS
    px = layout.HALF_X + t / 2           # end posts in the end walls
    py = layout.HALF_Y + t / 2           # side posts in the side walls
    eave, apex, r = 1.5, 2.5, 0.022
    # Circular arch through (+-py, eave) and (0, apex).
    zc = (apex ** 2 - eave ** 2 - py ** 2) / (2 * (apex - eave))
    radius = apex - zc
    a0 = math.atan2(eave - zc, py)
    n_arc = 14

    def arc_point(k: int, x: float, sign: int):
        a = a0 + (math.pi / 2 - a0) * k / (n_arc // 2)
        return (x, sign * radius * math.cos(a), zc + radius * math.sin(a))

    xs = [-px + 2 * px * i / 8 for i in range(9)]
    for x in xs:
        for sign in (1, -1):
            m.box((0.05, 0.05, eave), STEEL, loc=(x, sign * py, eave / 2))
            for k in range(n_arc // 2):
                segment(m, arc_point(k, x, sign), arc_point(k + 1, x, sign), r, r, STEEL)
    for x in (xs[0], xs[-1]):
        for y in (-1.2, 1.2):
            z_top = zc + math.sqrt(radius ** 2 - y ** 2)
            m.box((0.05, 0.05, z_top), STEEL, loc=(x, y, z_top / 2))
    # Ridge and purlins along x.
    for k, sign in ((n_arc // 2, 1), (2, 1), (2, -1), (5, 1), (5, -1)):
        a = arc_point(k, 0, sign)
        segment(m, (-px, a[1], a[2]), (px, a[1], a[2]), r, r, STEEL)
    for sign in (1, -1):
        segment(m, (-px, sign * py, eave), (px, sign * py, eave), r, r, STEEL)
    return m


def plant_pot() -> mk.LinkMesh:
    m = mk.LinkMesh('plant_pot')
    hz, rr = layout.POT_HEIGHT / 2, layout.POT_RADIUS
    profile = [(0, -hz), (rr, -hz), (rr, hz - 0.03), (rr + 0.008, hz - 0.027),
               (rr + 0.008, hz), (rr - 0.01, hz), (rr - 0.01, hz - 0.02), (0, hz - 0.02)]
    m.revolve(profile, POT, segments=24, smooth=False)
    m.cylinder(rr - 0.01, rr - 0.01, 0.006, SOIL, loc=(0, 0, hz - 0.017), segments=24)
    rng = random.Random(3)
    segment(m, (0, 0, hz - 0.015), (0.01, 0, hz + 0.20), 0.006, 0.004, STEM)
    for k in range(7):
        a = 2 * math.pi * k / 7
        z = hz + 0.05 + 0.025 * k
        leaf(m, rng, (0.05 * math.cos(a), 0.05 * math.sin(a), z), 0.06)
    return m


def place(obj, coll, loc=(0, 0, 0), yaw=0.0) -> None:
    inst = bpy.data.objects.new(f'{obj.name}_preview', obj.data)
    inst.location = loc
    inst.rotation_euler = (0, 0, yaw)
    coll.objects.link(inst)


def main():
    coll = mk.collection('greenhouse_models')
    # Hidden objects cannot be selected, and the OBJ export only writes selected ones.
    coll.hide_viewport = coll.hide_render = False
    objs = {b.name: b.to_object(coll)
            for b in (planter_bed(), tomato_row(), greenhouse_frame(), plant_pot())}
    srgb_dir = os.path.join(tempfile.gettempdir(), 'serabot_greenhouse_srgb')
    for name, obj in objs.items():
        mk.export_obj(obj, os.path.join(srgb_dir, f'{name}.obj'),
                      linear_dir=os.path.join(MODELS, name, 'meshes'))
    coll.hide_viewport = coll.hide_render = True

    preview = mk.collection('greenhouse_preview')
    for i, y in enumerate(layout.BED_Y):
        place(objs['planter_bed'], preview, (0, y, 0))
        place(objs['tomato_row'], preview, (0, y, 0), math.pi if i % 2 else 0.0)
    for x, y in layout.POTS:
        place(objs['plant_pot'], preview, (x, y, layout.POT_HEIGHT / 2))
    place(objs['greenhouse_frame'], preview)
    bpy.ops.wm.save_as_mainfile(filepath=BLEND)

    tris = {name: mk.triangle_count([o]) for name, o in objs.items()}
    world_tris = (tris['tomato_row'] * 3 + tris['planter_bed'] * 3 + tris['greenhouse_frame']
                  + tris['plant_pot'] * len(layout.POTS))
    return {'triangles': tris, 'world_triangles': world_tris,
            'bounds': {name: [list(map(lambda v: round(v, 4), c)) for c in bounds(o)]
                       for name, o in objs.items()}}


def bounds(obj):
    xs = [v.co for v in obj.data.vertices]
    return ([min(v[i] for v in xs) for i in range(3)], [max(v[i] for v in xs) for i in range(3)])


result = main()
