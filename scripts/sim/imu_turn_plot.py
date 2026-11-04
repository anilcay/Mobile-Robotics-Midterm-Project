#!/usr/bin/env python3
"""Plot a CSV from imu_turn_record.py for the report (owner: Member B).

Two panels sharing the time axis: yaw from imu_monitor (/imu/rpy) vs. /odom, and
the gyroscope rate /imu angular_velocity.z vs. the commanded rate.

Usage: python3 scripts/sim/imu_turn_plot.py in.csv out.png
"""

import csv
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402

SURFACE = '#fcfcfb'
INK = '#0b0b0b'
INK_2 = '#52514e'
GRID = '#e4e3df'
SERIES_1 = '#2a78d6'  # IMU (imu_monitor)
SERIES_2 = '#eb6834'  # odometry / command


def unwrap(deg):
    """Remove the +-180 deg jumps so a full turn plots as one continuous line."""
    out, offset = [], 0.0
    for i, d in enumerate(deg):
        if i and d - deg[i - 1] > 180.0:
            offset -= 360.0
        elif i and d - deg[i - 1] < -180.0:
            offset += 360.0
        out.append(d + offset)
    return out


def main() -> None:
    src, out = sys.argv[1], sys.argv[2]
    with open(src) as f:
        rows = [{k: float(v) for k, v in r.items()} for r in csv.DictReader(f)]
    t0 = rows[0]['t']
    t = [r['t'] - t0 for r in rows]

    plt.rcParams.update({'font.size': 10, 'axes.edgecolor': INK_2, 'axes.labelcolor': INK,
                         'xtick.color': INK_2, 'ytick.color': INK_2,
                         'axes.titlecolor': INK, 'text.color': INK})
    fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, figsize=(8, 5.5), dpi=150,
                                   facecolor=SURFACE)
    for ax in (ax1, ax2):
        ax.set_facecolor(SURFACE)
        ax.grid(True, color=GRID, linewidth=0.8)
        ax.spines[['top', 'right']].set_visible(False)

    ax1.plot(t, unwrap([r['odom_yaw_deg'] for r in rows]), color=SERIES_2, linewidth=2,
             linestyle=(0, (4, 2)), label='/odom yaw (DiffDrive)')
    ax1.plot(t, unwrap([r['yaw_deg'] for r in rows]), color=SERIES_1, linewidth=2,
             label='/imu/rpy yaw (imu_monitor)')
    ax1.set_ylabel('yaw, unwrapped [deg]')
    ax1.set_title('Turning in place: yaw from the IMU orientation vs. odometry', loc='left')
    ax1.legend(loc='lower left', frameon=False)

    ax2.plot(t, [r['cmd_wz'] for r in rows], color=SERIES_2, linewidth=2,
             linestyle=(0, (4, 2)), label='/cmd_vel angular.z (command)')
    ax2.plot(t, [r['wz_rad_s'] for r in rows], color=SERIES_1, linewidth=2,
             label='/imu angular_velocity.z (gyroscope)')
    ax2.set_ylabel('yaw rate [rad/s]')
    ax2.set_xlabel('simulation time [s]')
    ax2.legend(loc='center right', frameon=False)

    fig.tight_layout()
    fig.savefig(out, facecolor=SURFACE)
    print('saved', out)


if __name__ == '__main__':
    main()
