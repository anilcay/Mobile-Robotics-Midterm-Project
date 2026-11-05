#!/usr/bin/env python3
"""Coverage, inspections and clearance of a camera_track_record.py run (owner: Member B).

Uses the Gazebo ground-truth pose when the run recorded it (--ground-truth), else
the /odom path moved to world coordinates with the spawn pose; odometry drifts by
tens of centimetres after many in-place turns, so only ground-truth clearances are
evidence. Clearance is the smallest distance between the robot's collision
footprint (chassis box + wheel spheres, docs/INTERFACES.md section 4) and the beds,
pots and walls (section 4.2); <= 0 would mean contact.

Usage: python3 scripts/sim/camera_track_stats.py RUN_DIR [--spawn -4.0 0.875 0.0]
"""

import argparse
import csv
import math
import os

# Robot footprint in base_link (INTERFACES.md section 4, ADR-019)
CHASSIS_X = (-0.105, 0.345)
CHASSIS_HALF_WIDTH = 0.15
WHEEL_Y = 0.18
WHEEL_RADIUS = 0.08
# World (INTERFACES.md section 4.2)
INNER_X, INNER_Y = 5.0, 3.0
BEDS = [(-3.0, 3.0, y - 0.25, y + 0.25) for y in (-1.75, 0.0, 1.75)]
POTS = ((-0.5, 1.30), (1.0, -0.45), (-1.6, -1.30), (4.2, -1.20), (-4.2, -1.80))
POT_RADIUS = 0.15
CELL = 1.0


def footprint_points(step: float = 0.02):
    """Chassis outline points (and wheel centres separately), base_link frame."""
    x0, x1 = CHASSIS_X
    w = CHASSIS_HALF_WIDTH
    pts = []
    n = int((x1 - x0) / step)
    for i in range(n + 1):
        x = x0 + (x1 - x0) * i / n
        pts += [(x, -w), (x, w)]
    m = int(2 * w / step)
    for i in range(m + 1):
        y = -w + 2 * w * i / m
        pts += [(x0, y), (x1, y)]
    return pts, [(0.0, -WHEEL_Y), (0.0, WHEEL_Y)]


def rect_distance(px: float, py: float, rect) -> float:
    x0, x1, y0, y1 = rect
    dx = max(x0 - px, 0.0, px - x1)
    dy = max(y0 - py, 0.0, py - y1)
    if dx == 0.0 and dy == 0.0:
        return -min(px - x0, x1 - px, py - y0, y1 - py)
    return math.hypot(dx, dy)


def obstacle_distance(px: float, py: float) -> float:
    d = min(INNER_X - abs(px), INNER_Y - abs(py))
    d = min([d] + [rect_distance(px, py, b) for b in BEDS])
    return min([d] + [math.hypot(px - cx, py - cy) - POT_RADIUS for cx, cy in POTS])


def to_world(x, y, yaw_rad, spawn):
    sx, sy, syaw = spawn
    c, s = math.cos(syaw), math.sin(syaw)
    return sx + c * x - s * y, sy + s * x + c * y, syaw + yaw_rad


def world_pose(row: dict, spawn):
    """(x, y, yaw_rad) in the world: ground truth if recorded, else odom + spawn."""
    if row.get('gt_x'):
        return float(row['gt_x']), float(row['gt_y']), math.radians(float(row['gt_yaw_deg']))
    return to_world(float(row['x']), float(row['y']), math.radians(float(row['yaw_deg'])),
                    spawn)


def odom_drift(path, spawn) -> float:
    """Largest distance between the odom-based and the ground-truth position."""
    drift = 0.0
    for r in path:
        if r.get('gt_x'):
            ox, oy, _ = to_world(float(r['x']), float(r['y']), 0.0, spawn)
            drift = max(drift, math.hypot(ox - float(r['gt_x']), oy - float(r['gt_y'])))
    return drift


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('run_dir')
    parser.add_argument('--spawn', type=float, nargs=3, default=(-4.0, 0.875, 0.0),
                        metavar=('X', 'Y', 'YAW'))
    args = parser.parse_args()

    with open(os.path.join(args.run_dir, 'camera_track_path.csv')) as f:
        path = [r for r in csv.DictReader(f) if r['state']]
    with open(os.path.join(args.run_dir, 'camera_track_states.csv')) as f:
        transitions = list(csv.DictReader(f))

    outline, wheels = footprint_points()
    length, cells = 0.0, set()
    worst = (math.inf, None)
    prev = None
    for r in path:
        wx, wy, wyaw = world_pose(r, args.spawn)
        if prev is not None:
            length += math.hypot(wx - prev[0], wy - prev[1])
        prev = (wx, wy)
        cells.add((math.floor(wx / CELL), math.floor(wy / CELL)))
        c, s = math.cos(wyaw), math.sin(wyaw)
        for bx, by in outline:
            d = obstacle_distance(wx + c * bx - s * by, wy + s * bx + c * by)
            if d < worst[0]:
                worst = (d, r)
        for bx, by in wheels:
            d = obstacle_distance(wx + c * bx - s * by, wy + s * bx + c * by) - WHEEL_RADIUS
            if d < worst[0]:
                worst = (d, r)

    total_cells = int(2 * INNER_X / CELL) * int(2 * INNER_Y / CELL)
    entries = {}
    for t in transitions:
        entries[t['to']] = entries.get(t['to'], 0) + 1
    span = float(path[-1]['t']) - float(path[0]['t'])
    w = worst[1]
    wx, wy, _ = world_pose(w, args.spawn)
    source = 'ground truth' if path[0].get('gt_x') else 'odometry (not evidence)'
    print(f'run: {os.path.basename(os.path.normpath(args.run_dir))}, {span:.0f} s sim, '
          f'pose from {source}')
    if path[0].get('gt_x'):
        print(f'max odometry drift {odom_drift(path, args.spawn):.3f} m')
    print(f'path length {length:.1f} m, visited {len(cells)}/{total_cells} '
          f'{CELL:.0f} m cells, x {min(c[0] for c in cells):+d}..{max(c[0] for c in cells):+d}')
    print('state entries: ' + ', '.join(f'{k} {v}' for k, v in sorted(entries.items())))
    print(f'min clearance {worst[0]:.3f} m at t={float(w["t"]):.1f} s '
          f'({w["state"]}, world {wx:+.2f}, {wy:+.2f})')


if __name__ == '__main__':
    main()
