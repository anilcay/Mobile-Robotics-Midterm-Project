"""Generate worlds/greenhouse.sdf (primitive-only greenhouse world).

The layout lives in the constants below so that later Blender decorations
(docs/INTERFACES.md section 4.2) can be aligned with the collision geometry.
Run from anywhere:  python src/serabot_gazebo/tools/generate_greenhouse.py

Frame: world origin at the greenhouse centre, x along the plant beds, z up.
"""

from pathlib import Path
from typing import List, Tuple

WORLD_NAME = 'greenhouse'

# Interior footprint (m): x in [-HALF_X, HALF_X], y in [-HALF_Y, HALF_Y].
HALF_X = 5.0
HALF_Y = 3.0
WALL_THICKNESS = 0.1
WALL_HEIGHT = 1.0

# Plant beds run along x. Corridors: 1.25 m between beds, 1.0 m at the walls,
# 2.0 m turning areas at both ends.
BED_LENGTH = 6.0
BED_WIDTH = 0.5
BED_HEIGHT = 0.40
BED_Y = (-1.75, 0.0, 1.75)
SOIL_DEPTH = 0.02

# Foliage: visual only, inside the bed footprint, above the LiDAR plane.
FOLIAGE_WIDTH = 0.36
FOLIAGE_HEIGHT = 0.35

# Tomatoes: visual only, pure red, at camera height (~0.44 m), on both bed
# edges facing the corridors.
TOMATO_RADIUS = 0.04
TOMATO_Z = 0.46
TOMATO_EDGE_OFFSET = 0.22
CLUSTER_X = (-2.4, -1.2, 0.0, 1.2, 2.4)
# Small triangle per cluster: (dx, dz) offsets.
CLUSTER_SHAPE = ((-0.05, 0.0), (0.05, 0.0), (0.0, 0.07))

# Pots (obstacles): cylinders, static.
POT_RADIUS = 0.15
POT_HEIGHT = 0.35
POTS: Tuple[Tuple[float, float], ...] = (
    (-0.5, 1.30),    # corridor y=+0.875, leaves 0.90 m
    (1.0, -0.45),    # corridor y=-0.875, leaves 0.90 m
    (-1.6, -1.30),   # corridor y=-0.875, leaves 0.90 m
    (4.2, -1.20),    # east turning area
    (-4.2, -1.80),   # west turning area
)

# Colours (RGB, linear-ish values as Gazebo uses them).
WALL_RGB = (0.80, 0.82, 0.80)
FLOOR_RGB = (0.55, 0.55, 0.52)
BED_RGB = (0.45, 0.32, 0.20)
SOIL_RGB = (0.20, 0.14, 0.10)
FOLIAGE_RGB = (0.10, 0.45, 0.12)
TOMATO_RGB = (1.0, 0.0, 0.0)
POT_RGB = (0.30, 0.34, 0.40)

OUTPUT = Path(__file__).resolve().parent.parent / 'worlds' / 'greenhouse.sdf'


def fmt(*values: float) -> str:
    """Format numbers for SDF, without trailing zeros."""
    return ' '.join(f'{v:.4f}'.rstrip('0').rstrip('.') if v != 0 else '0' for v in values)


def material(rgb: Tuple[float, float, float]) -> str:
    c = fmt(*rgb, 1.0)
    return (f'<material><ambient>{c}</ambient><diffuse>{c}</diffuse>'
            f'<specular>0.05 0.05 0.05 1</specular></material>')


def box_visual(name: str, pose: Tuple[float, ...], size: Tuple[float, ...],
               rgb: Tuple[float, float, float]) -> str:
    return (f'<visual name="{name}"><pose>{fmt(*pose)}</pose>'
            f'<geometry><box><size>{fmt(*size)}</size></box></geometry>'
            f'{material(rgb)}</visual>')


def box_collision(name: str, pose: Tuple[float, ...], size: Tuple[float, ...]) -> str:
    return (f'<collision name="{name}"><pose>{fmt(*pose)}</pose>'
            f'<geometry><box><size>{fmt(*size)}</size></box></geometry></collision>')


def walls() -> str:
    t, h = WALL_THICKNESS, WALL_HEIGHT
    lx = 2 * HALF_X + 2 * t
    ly = 2 * HALF_Y
    parts = []
    specs = [
        ('north', (0, HALF_Y + t / 2, h / 2, 0, 0, 0), (lx, t, h)),
        ('south', (0, -HALF_Y - t / 2, h / 2, 0, 0, 0), (lx, t, h)),
        ('east', (HALF_X + t / 2, 0, h / 2, 0, 0, 0), (t, ly, h)),
        ('west', (-HALF_X - t / 2, 0, h / 2, 0, 0, 0), (t, ly, h)),
    ]
    for name, pose, size in specs:
        parts.append(box_collision(f'{name}_collision', pose, size))
        parts.append(box_visual(f'{name}_visual', pose, size, WALL_RGB))
    body = '\n        '.join(parts)
    return f'''
    <model name="walls">
      <static>true</static>
      <link name="link">
        {body}
      </link>
    </model>'''


def bed(index: int, y: float) -> str:
    size = (BED_LENGTH, BED_WIDTH, BED_HEIGHT)
    centre = (0, 0, BED_HEIGHT / 2, 0, 0, 0)
    parts = [
        box_collision('collision', centre, size),
        box_visual('visual', centre, size, BED_RGB),
        box_visual('soil', (0, 0, BED_HEIGHT + SOIL_DEPTH / 2, 0, 0, 0),
                   (BED_LENGTH - 0.04, BED_WIDTH - 0.04, SOIL_DEPTH), SOIL_RGB),
        box_visual('foliage', (0, 0, BED_HEIGHT + FOLIAGE_HEIGHT / 2, 0, 0, 0),
                   (BED_LENGTH - 0.1, FOLIAGE_WIDTH, FOLIAGE_HEIGHT), FOLIAGE_RGB),
    ]
    parts.extend(tomatoes(y))
    body = '\n        '.join(parts)
    return f'''
    <model name="bed_{index}">
      <static>true</static>
      <pose>0 {fmt(y)} 0 0 0 0</pose>
      <link name="link">
        {body}
      </link>
    </model>'''


def tomatoes(bed_y: float) -> List[str]:
    """Tomato visuals on the bed edges that face a corridor."""
    out = []
    for side, sign in (('left', 1.0), ('right', -1.0)):
        # The outer beds' wall-side edges also face a (1.0 m) corridor.
        for ci, cx in enumerate(CLUSTER_X):
            for ti, (dx, dz) in enumerate(CLUSTER_SHAPE):
                pose = (cx + dx, sign * TOMATO_EDGE_OFFSET, TOMATO_Z + dz, 0, 0, 0)
                out.append(
                    f'<visual name="tomato_{side}_{ci}_{ti}"><pose>{fmt(*pose)}</pose>'
                    f'<geometry><sphere><radius>{fmt(TOMATO_RADIUS)}</radius></sphere>'
                    f'</geometry>{material(TOMATO_RGB)}</visual>')
    return out


def pot(index: int, x: float, y: float) -> str:
    geom = (f'<geometry><cylinder><radius>{fmt(POT_RADIUS)}</radius>'
            f'<length>{fmt(POT_HEIGHT)}</length></cylinder></geometry>')
    return f'''
    <model name="pot_{index}">
      <static>true</static>
      <pose>{fmt(x, y, POT_HEIGHT / 2)} 0 0 0</pose>
      <link name="link">
        <collision name="collision">{geom}</collision>
        <visual name="visual">{geom}{material(POT_RGB)}</visual>
      </link>
    </model>'''


def world() -> str:
    models = walls()
    models += ''.join(bed(i, y) for i, y in enumerate(BED_Y))
    models += ''.join(pot(i, x, y) for i, (x, y) in enumerate(POTS))
    floor = material(FLOOR_RGB)
    return f'''<?xml version="1.0"?>
<!--
  SeraBot greenhouse world (owner: S2). GENERATED by tools/generate_greenhouse.py,
  edit the generator, not this file.
  Interior 10 x 6 m, three plant beds along x, pots as corridor obstacles,
  pure red tomatoes at camera height. Collision geometry is primitive (ADR-018).
-->
<sdf version="1.10">
  <world name="{WORLD_NAME}">
    <physics name="1ms" type="ignored">
      <max_step_size>0.001</max_step_size>
      <real_time_factor>1.0</real_time_factor>
    </physics>

    <plugin filename="gz-sim-physics-system" name="gz::sim::systems::Physics"/>
    <plugin filename="gz-sim-user-commands-system" name="gz::sim::systems::UserCommands"/>
    <plugin filename="gz-sim-scene-broadcaster-system"
            name="gz::sim::systems::SceneBroadcaster"/>
    <plugin filename="gz-sim-sensors-system" name="gz::sim::systems::Sensors">
      <render_engine>ogre2</render_engine>
    </plugin>
    <plugin filename="gz-sim-imu-system" name="gz::sim::systems::Imu"/>

    <scene>
      <ambient>0.5 0.5 0.5 1</ambient>
      <background>0.75 0.85 0.95 1</background>
      <shadows>false</shadows>
    </scene>

    <light type="directional" name="sun">
      <cast_shadows>false</cast_shadows>
      <pose>0 0 10 0 0 0</pose>
      <diffuse>0.9 0.9 0.9 1</diffuse>
      <specular>0.2 0.2 0.2 1</specular>
      <direction>-0.4 0.2 -0.9</direction>
    </light>

    <model name="ground_plane">
      <static>true</static>
      <link name="link">
        <collision name="collision">
          <geometry><plane><normal>0 0 1</normal><size>30 30</size></plane></geometry>
        </collision>
        <visual name="visual">
          <geometry><plane><normal>0 0 1</normal><size>30 30</size></plane></geometry>
          {floor}
        </visual>
      </link>
    </model>
{models}
  </world>
</sdf>
'''


def main() -> None:
    OUTPUT.write_text(world(), encoding='utf-8', newline='\n')
    print(f'wrote {OUTPUT}')


if __name__ == '__main__':
    main()
