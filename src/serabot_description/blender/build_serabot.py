"""Build the SeraBot visual meshes, concept B "flower pot" (saksı).

Run through the bridge:  python bridge_client.py build_serabot.py
Creates one object per link in the "serabot_links" collection with its origin at
the URDF link frame (docs/INTERFACES.md section 4.1), places linked copies at
their link poses in "serabot_assembly" for previews, and saves
meshes/source/serabot.blend. Dimensions follow urdf/properties.xacro.
"""

import importlib
import math
import os
import sys

import bpy

sys.path.insert(0, os.path.dirname(__file__))
import mesh_kit as mk  # noqa: E402

importlib.reload(mk)

PKG = os.path.dirname(os.path.dirname(__file__))
BLEND = os.path.join(PKG, 'meshes', 'source', 'serabot.blend')

# --- Contract dimensions (INTERFACES.md section 4, urdf/properties.xacro) ---
CHASSIS_L, CHASSIS_W, CHASSIS_H = 0.45, 0.30, 0.12
WHEEL_R, WHEEL_W, WHEEL_SEP, WHEEL_X = 0.08, 0.04, 0.36, -0.12
BASE_Z = WHEEL_R
CASTER_R, CASTER_X = 0.03, 0.17
MAST_X, MAST_Z, MAST_H = -0.15, CHASSIS_H / 2, 0.30
LIDAR_X, LIDAR_Z = 0.10, 0.10
TOP = CHASSIS_H / 2           # chassis top face in base_link
SOIL = TOP - 0.010            # soil surface, 1 cm under the rim
WALL_SLOPE = 0.025 / 0.17     # pot wall: outward run per unit rise (sides and ends)
WALL_INSET = 0.0185           # wall inset from the chassis box at z = -0.055

# --- Palette (display sRGB) ---
TERRACOTTA = mk.material('sb_terracotta', mk.srgb(0.78, 0.39, 0.23), 0.85)
RIM = mk.material('sb_rim', mk.srgb(0.64, 0.30, 0.17), 0.8)
SOIL_MAT = mk.material('sb_soil', mk.srgb(0.27, 0.19, 0.14), 0.95)
SAUCER = mk.material('sb_cream', mk.srgb(0.91, 0.85, 0.71), 0.6)
LEAF = mk.material('sb_leaf', mk.srgb(0.42, 0.66, 0.27), 0.55)
STEM = mk.material('sb_stem', mk.srgb(0.27, 0.50, 0.22), 0.6)
SEPAL = mk.material('sb_sepal', mk.srgb(0.20, 0.40, 0.17), 0.6)
TIRE = mk.material('sb_tire', mk.srgb(0.20, 0.16, 0.14), 0.9)
PEBBLE = mk.material('sb_pebble', mk.srgb(0.72, 0.70, 0.65), 0.7)
WINDOW = mk.material('sb_window', mk.srgb(0.08, 0.08, 0.09), 0.15)
METAL = mk.material('sb_metal', mk.srgb(0.62, 0.62, 0.64), 0.35, 0.6)


def pot_outline(z: float, base_l: float, base_w: float, z0: float, r: float):
    """Rounded-rect outline of the pot wall at height z (wall widens upwards)."""
    grow = 2 * WALL_SLOPE * (z - z0)
    return mk.rounded_rect(base_l + grow, base_w + grow, r)


def leaf_emblem(link: mk.LinkMesh, side: int) -> None:
    """Two-leaf sprout embossed on the +Y (side=1) or -Y (side=-1) pot wall."""
    tilt = math.atan(WALL_SLOPE)
    base_u, base_v = 0.0, -0.035
    for theta in (math.radians(55), math.radians(125)):
        u = base_u + 0.026 * math.cos(theta)
        v = base_v + 0.026 * math.sin(theta)
        y = side * (CHASSIS_W / 2 - WALL_INSET + WALL_SLOPE * (v + 0.055) + 0.0008)
        link.ellipsoid((0.028, 0.0022, 0.010), LEAF, loc=(u, y, v),
                       rot=(-side * tilt, -theta, 0), order='YXZ', segments=16, rings=8)
    y = side * (CHASSIS_W / 2 - WALL_INSET + WALL_SLOPE * (base_v - 0.010 + 0.055) + 0.0008)
    link.ellipsoid((0.0025, 0.0022, 0.012), STEM, loc=(base_u, y, base_v - 0.010),
                   rot=(-side * tilt, 0, 0), segments=8, rings=6)


def build_chassis() -> mk.LinkMesh:
    link = mk.LinkMesh('chassis')
    z_bot, z_mid = -TOP, 0.030
    # Pot body, narrower at the bottom; top outline is 0.438 x 0.288 at z_mid.
    l0, w0 = CHASSIS_L - 0.045, CHASSIS_W - 0.045
    link.loft([(z_bot, pot_outline(z_bot + 0.005, l0, w0, z_bot + 0.005, 0.045)),
               (z_bot + 0.005, pot_outline(z_bot + 0.005, l0 + 0.008, w0 + 0.008,
                                           z_bot + 0.005, 0.047)),
               (z_mid, pot_outline(z_mid, l0 + 0.008, w0 + 0.008, z_bot + 0.005, 0.05))],
              TERRACOTTA, cap_top=False)
    # Rim band with soil inside.
    rim_r = 0.05
    link.loft([(z_mid, mk.rounded_rect(CHASSIS_L - 0.012, CHASSIS_W - 0.012, rim_r)),
               (z_mid + 0.004, mk.rounded_rect(CHASSIS_L, CHASSIS_W, rim_r)),
               (TOP, mk.rounded_rect(CHASSIS_L, CHASSIS_W, rim_r)),
               (TOP, mk.rounded_rect(CHASSIS_L - 0.022, CHASSIS_W - 0.022, rim_r - 0.011)),
               (SOIL, mk.rounded_rect(CHASSIS_L - 0.022, CHASSIS_W - 0.022, rim_r - 0.011))],
              RIM, cap_bottom=False, cap_mat=SOIL_MAT)
    # Saucer under the pot doubles as the bumper ring.
    link.loft([(z_bot, mk.rounded_rect(0.424, 0.274, 0.05)),
               (z_bot + 0.016, mk.rounded_rect(0.432, 0.282, 0.052)),
               (z_bot + 0.018, mk.rounded_rect(0.426, 0.276, 0.049))],
              SAUCER)
    # Pebbles on the soil, clear of the mast and LiDAR feet.
    for x, y, s in ((0.02, 0.07, 1.0), (-0.05, -0.08, 0.8), (0.17, -0.09, 0.9),
                    (-0.08, 0.07, 0.7), (0.18, 0.08, 0.8), (-0.19, -0.05, 0.9)):
        link.ellipsoid((0.012 * s, 0.009 * s, 0.005), PEBBLE, loc=(x, y, SOIL + 0.001),
                       rot=(0, 0, x * 20), segments=12, rings=6)
    leaf_emblem(link, 1)
    leaf_emblem(link, -1)
    # Plant tag on the back wall.
    tilt = math.atan(WALL_SLOPE)
    x_back = -(CHASSIS_L / 2 - WALL_INSET + WALL_SLOPE * 0.055) - 0.0018
    link.box((0.003, 0.07, 0.034), SAUCER, loc=(x_back, 0, 0.0), rot=(0, tilt, 0),
             bevel=0.001)
    link.box((0.0015, 0.04, 0.006), STEM, loc=(x_back - 0.0018, 0, 0.004), rot=(0, tilt, 0))
    return link


def build_wheel() -> mk.LinkMesh:
    """Symmetric wheel (same mesh left and right); axis along link Y."""
    link = mk.LinkMesh('wheel')
    half = WHEEL_W / 2
    tire_r = WHEEL_R - 0.003
    profile = [(0.050, -half), (0.066, -half), (tire_r - 0.006, -half + 0.002),
               (tire_r, -half + 0.008), (tire_r, half - 0.008),
               (tire_r - 0.006, half - 0.002), (0.066, half), (0.050, half), (0.050, -half)]
    link.revolve(profile, TIRE, segments=48, rot=(math.pi / 2, 0, 0))
    for k in range(20):
        a = 2 * math.pi * k / 20
        r = tire_r + 0.0005
        link.box((0.013, WHEEL_W - 0.008, 0.005), TIRE,
                 loc=(r * math.cos(a), 0, r * math.sin(a)), rot=(0, math.pi / 2 - a, 0),
                 bevel=0.0008)
    # Cream hub with a flower of leaf petals on both faces, terracotta centre.
    link.cylinder(0.050, 0.050, WHEEL_W - 0.010, SAUCER, rot=(math.pi / 2, 0, 0),
                  segments=32)
    for side in (1, -1):
        y = side * (half - 0.0045)
        for k in range(6):
            a = 2 * math.pi * k / 6
            link.ellipsoid((0.016, 0.0018, 0.0065), LEAF,
                           loc=(0.028 * math.cos(a), y, 0.028 * math.sin(a)),
                           rot=(0, -a, 0), segments=12, rings=6)
    link.cylinder(0.012, 0.012, WHEEL_W - 0.004, TERRACOTTA, rot=(math.pi / 2, 0, 0),
                  segments=20)
    return link


def build_caster() -> mk.LinkMesh:
    link = mk.LinkMesh('caster')
    link.ellipsoid((CASTER_R,) * 3, METAL, segments=24, rings=12)
    link.cylinder(0.031, 0.034, 0.012, SAUCER, loc=(0, 0, -0.013), segments=24)
    return link


def mast_leaf(link: mk.LinkMesh, z: float, side: int, length: float, lift_deg: float):
    """Leaf growing sideways (+Y side=1 / -Y side=-1) out of the stem at height z."""
    beta = math.radians(lift_deg)
    reach = 0.010 + length * math.cos(beta)
    link.ellipsoid((length, length * 0.36, 0.0025), LEAF,
                   loc=(0, side * reach, z + length * math.sin(beta)),
                   rot=(0, -beta, side * math.pi / 2), segments=16, rings=8)
    # Midrib
    link.ellipsoid((length * 0.9, 0.0018, 0.0032), STEM,
                   loc=(0, side * reach, z + length * math.sin(beta) + 0.0006),
                   rot=(0, -beta, side * math.pi / 2), segments=8, rings=4)


def build_camera_mast() -> mk.LinkMesh:
    """Plant stem from the soil to the camera bud; origin at the chassis top face."""
    link = mk.LinkMesh('camera_mast')
    soil = SOIL - TOP
    stem_top = MAST_H - 0.015
    link.cylinder(0.016, 0.012, stem_top - soil, STEM, loc=(0, 0, (stem_top + soil) / 2),
                  segments=20)
    for z in (0.10, 0.20):
        link.cylinder(0.0145, 0.0145, 0.006, STEM, loc=(0, 0, z), segments=20)
    # Sprout leaves at the soil, below the LiDAR scan plane (mast-local z = 0.04).
    for k in range(3):
        a = 2 * math.pi * k / 3 + 0.4
        link.ellipsoid((0.022, 0.009, 0.0025), LEAF,
                       loc=(0.024 * math.cos(a), 0.024 * math.sin(a), soil + 0.004),
                       rot=(0, -0.25, a), segments=12, rings=6)
    # Side leaves stay above the scan plane so the LiDAR never sees them.
    mast_leaf(link, 0.17, 1, 0.045, 28)
    mast_leaf(link, 0.085, -1, 0.034, 22)
    return link


def build_camera() -> mk.LinkMesh:
    """Flower bud housing; origin at camera_link, lens facing +X."""
    link = mk.LinkMesh('camera')
    link.ellipsoid((0.036, 0.027, 0.028), LEAF, segments=24, rings=14)
    for k in range(4):
        psi = math.radians(45 + 90 * k)
        link.ellipsoid((0.022, 0.010, 0.0025), SEPAL,
                       loc=(-0.016, 0.0245 * math.cos(psi), 0.0245 * math.sin(psi)),
                       rot=(psi - math.pi / 2, 0, 0), segments=12, rings=6)
    link.cylinder(0.015, 0.015, 0.005, SAUCER, loc=(0.033, 0, 0), rot=(0, math.pi / 2, 0),
                  segments=24)
    link.cylinder(0.011, 0.011, 0.008, WINDOW, loc=(0.036, 0, 0), rot=(0, math.pi / 2, 0),
                  segments=24)
    return link


def build_lidar() -> mk.LinkMesh:
    """River pebble with a dark sensor window at the scan plane (link z = 0)."""
    link = mk.LinkMesh('lidar')
    bottom = SOIL - (LIDAR_Z)          # soil level in lidar_link
    link.ellipsoid((0.042, 0.038, 0.030), PEBBLE, loc=(0, 0, bottom + 0.030),
                   segments=28, rings=14)
    link.cylinder(0.0335, 0.0335, 0.008, WINDOW, segments=32)
    return link


def build_imu() -> mk.LinkMesh:
    """Small board inside the chassis (hidden, kept for completeness)."""
    link = mk.LinkMesh('imu')
    link.box((0.030, 0.025, 0.008), WINDOW, bevel=0.001)
    link.cylinder(0.003, 0.003, 0.0085, SAUCER, loc=(0.010, 0.008, 0.0005), segments=8)
    return link


# Link poses in base_footprint for the preview assembly: (link, mesh, xyz)
ASSEMBLY = [
    ('base_link', 'chassis', (0, 0, BASE_Z)),
    ('left_wheel_link', 'wheel', (WHEEL_X, WHEEL_SEP / 2, BASE_Z)),
    ('right_wheel_link', 'wheel', (WHEEL_X, -WHEEL_SEP / 2, BASE_Z)),
    ('caster_link', 'caster', (CASTER_X, 0, CASTER_R)),
    ('camera_mast_link', 'camera_mast', (MAST_X, 0, BASE_Z + MAST_Z)),
    ('camera_link', 'camera', (MAST_X, 0, BASE_Z + MAST_Z + MAST_H)),
    ('lidar_link', 'lidar', (LIDAR_X, 0, BASE_Z + LIDAR_Z)),
    ('imu_link', 'imu', (0, 0, BASE_Z)),
]


def main() -> dict:
    for name in ('urdf_preview', 'orientation_test'):
        coll = bpy.data.collections.get(name)
        if coll is not None:
            for obj in list(coll.objects):
                bpy.data.objects.remove(obj)
            bpy.data.collections.remove(coll)
    cube = bpy.data.objects.get('Cube')
    if cube is not None:
        bpy.data.objects.remove(cube)

    links = mk.collection('serabot_links')
    builders = (build_chassis, build_wheel, build_caster, build_camera_mast,
                build_camera, build_lidar, build_imu)
    objects = {}
    for build in builders:
        link = build()
        objects[link.name] = link.to_object(links)
    # Link originals stay at the origin (exported as-is) and hidden in previews.
    links.hide_render = True
    links.hide_viewport = True

    assembly = mk.collection('serabot_assembly')
    for link_name, mesh_name, xyz in ASSEMBLY:
        inst = bpy.data.objects.new(link_name, objects[mesh_name].data)
        inst.location = xyz
        assembly.objects.link(inst)

    os.makedirs(os.path.dirname(BLEND), exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=BLEND)
    if os.path.exists(BLEND + '1'):  # Blender's previous-version backup
        os.remove(BLEND + '1')

    def bbox(obj):
        return [[round(f(v.co[i] for v in obj.data.vertices), 4) for i in range(3)]
                for f in (min, max)]

    return {
        'triangles': {n: mk.triangle_count([o]) for n, o in objects.items()},
        'triangles_robot': mk.triangle_count(assembly.objects),
        'bbox': {n: bbox(o) for n, o in objects.items()},
        'blend': BLEND,
    }


result = main()
