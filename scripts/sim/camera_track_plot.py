#!/usr/bin/env python3
"""Plot a camera_track_record.py run on the greenhouse map (owner: Member B).

The path is drawn in world coordinates (odom + spawn pose), coloured by behavior
state, with numbered markers where the robot entered INSPECT. Plant beds, pots and
walls follow docs/INTERFACES.md section 4.2.

Usage: python3 scripts/sim/camera_track_plot.py RUN_DIR out.png [--spawn -4.0 0.875 0.0]
"""

import argparse
import csv
import math
import os

import matplotlib
matplotlib.use('Agg')
from matplotlib.patches import Circle, Rectangle  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

SURFACE = '#fcfcfb'
INK = '#0b0b0b'
INK_2 = '#52514e'
BED = '#d9cdbd'
POT = '#b5b3ad'
WALL = '#52514e'
# Fixed categorical order (validated palette, slots 1-4)
STATE_COLORS = {'CRUISE': '#2a78d6', 'AVOID': '#eb6834', 'TRACK': '#1baf7a',
                'INSPECT': '#eda100'}

BEDS_Y = (-1.75, 0.0, 1.75)
BED_X, BED_LEN, BED_WIDTH = -3.0, 6.0, 0.5
POTS = ((-0.5, 1.30), (1.0, -0.45), (-1.6, -1.30), (4.2, -1.20), (-4.2, -1.80))
POT_RADIUS = 0.15
INNER_X, INNER_Y = 5.0, 3.0


def to_world(row: dict, spawn) -> tuple:
    """World (x, y): Gazebo ground truth if recorded, else odom + spawn pose."""
    if row.get('gt_x'):
        return float(row['gt_x']), float(row['gt_y'])
    sx, sy, syaw = spawn
    x, y = float(row['x']), float(row['y'])
    c, s = math.cos(syaw), math.sin(syaw)
    return sx + c * x - s * y, sy + s * x + c * y


def runs(rows):
    """Split the path into consecutive pieces with the same state."""
    piece = [rows[0]]
    for r in rows[1:]:
        piece.append(r)
        if r['state'] != piece[0]['state']:
            yield piece[0]['state'], piece
            piece = [r]
    yield piece[0]['state'], piece


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('run_dir')
    parser.add_argument('out')
    parser.add_argument('--spawn', type=float, nargs=3, default=(-4.0, 0.875, 0.0),
                        metavar=('X', 'Y', 'YAW'))
    args = parser.parse_args()

    with open(os.path.join(args.run_dir, 'camera_track_path.csv')) as f:
        path = [r for r in csv.DictReader(f) if r['state']]
    with open(os.path.join(args.run_dir, 'camera_track_states.csv')) as f:
        transitions = list(csv.DictReader(f))
    for r in path:
        r['wx'], r['wy'] = to_world(r, args.spawn)

    plt.rcParams.update({'font.size': 10, 'text.color': INK, 'axes.labelcolor': INK,
                         'xtick.color': INK_2, 'ytick.color': INK_2,
                         'axes.edgecolor': INK_2})
    fig, ax = plt.subplots(figsize=(8, 6.2), dpi=150, facecolor=SURFACE)
    ax.set_facecolor(SURFACE)

    ax.add_patch(Rectangle((-INNER_X, -INNER_Y), 2 * INNER_X, 2 * INNER_Y, fill=False,
                           edgecolor=WALL, linewidth=2))
    for y in BEDS_Y:
        ax.add_patch(Rectangle((BED_X, y - BED_WIDTH / 2), BED_LEN, BED_WIDTH,
                               facecolor=BED, edgecolor='none'))
    for px, py in POTS:
        ax.add_patch(Circle((px, py), POT_RADIUS, facecolor=POT, edgecolor='none'))

    for state, piece in runs(path):
        ax.plot([r['wx'] for r in piece], [r['wy'] for r in piece],
                color=STATE_COLORS.get(state, INK_2), linewidth=2, solid_capstyle='round')
    # Legend in the fixed palette order; AVOID and INSPECT are in-place, so they
    # show as turns/dots rather than line segments.
    handles = [plt.Line2D([], [], color=c, linewidth=2) for c in STATE_COLORS.values()]
    labels = ['CRUISE', 'AVOID (turn in place)', 'TRACK', 'INSPECT (stop)']

    inspect = [t for t in transitions if t['to'] == 'INSPECT']
    stops = []  # [x, y, [numbers]]; stops closer than 0.15 m share one label
    for i, t in enumerate(inspect, 1):
        wx, wy = to_world(t, args.spawn)
        for s in stops:
            if math.hypot(s[0] - wx, s[1] - wy) < 0.15:
                s[2].append(i)
                break
        else:
            stops.append([wx, wy, [i]])
    for wx, wy, numbers in stops:
        ax.plot(wx, wy, marker='o', markersize=9, color=STATE_COLORS['INSPECT'],
                markeredgecolor=SURFACE, markeredgewidth=2, zorder=5)
        ax.annotate(', '.join(map(str, numbers)), (wx, wy), xytext=(8, 4),
                    textcoords='offset points', fontsize=9, fontweight='bold', color=INK)
    sx, sy, _ = args.spawn
    ax.plot(sx, sy, marker='s', markersize=7, color=INK, zorder=5)
    ax.annotate('start', (sx, sy), xytext=(-12, -14), textcoords='offset points',
                fontsize=9, color=INK)

    xs = [r['wx'] for r in path]
    # Crop to the path plus a margin, at least MIN_VIEW wide, inside the walls.
    margin, min_view = 1.0, 5.0
    x0, x1 = min(xs) - margin, max(xs) + margin
    if x1 - x0 < min_view:
        x1 = x0 + min_view
    ax.set_xlim(max(-INNER_X - 0.2, x0), min(INNER_X + 0.2, x1))
    ax.set_ylim(-INNER_Y - 0.2, INNER_Y + 0.2)
    ax.set_aspect('equal')
    ax.set_xlabel('x [m] (world)')
    ax.set_ylabel('y [m] (world)')
    span = float(path[-1]['t']) - float(path[0]['t'])
    source = 'Gazebo ground truth' if path[0].get('gt_x') else 'odometry'
    ax.set_title(f'Camera layer on: {len(inspect)} inspections in {span:.0f} s (sim)\n'
                 f'pose: {source}', loc='left')
    for side in ('top', 'right'):
        ax.spines[side].set_visible(False)
    ax.legend(handles, labels, loc='upper left', bbox_to_anchor=(1.01, 1.0), frameon=False,
              title='behavior state\n(dots: INSPECT stops,\nnumbered in order)')
    fig.tight_layout()
    fig.savefig(args.out, facecolor=SURFACE, bbox_inches='tight', pad_inches=0.15)
    print('saved', args.out)


if __name__ == '__main__':
    main()
