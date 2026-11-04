#!/usr/bin/env python3
"""Turn SeraBot in place and record /imu/rpy against /odom (owner: Member B).

Publishes /cmd_vel (pause, turn, pause), records every /imu/rpy message with the
latest /imu angular velocity and /odom yaw, writes a CSV and prints a summary.
Do not run it together with behavior_node (both publish /cmd_vel).

Usage (bringup running, imu_monitor started by it):
    python3 scripts/sim/imu_turn_record.py out.csv [--turn-seconds 6] [--rate 0.8]
"""

import argparse
import csv
import math

from geometry_msgs.msg import Twist, Vector3Stamped
from nav_msgs.msg import Odometry
import rclpy
from rclpy.node import Node
from rclpy.parameter import Parameter
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import Imu

HEADER = ['t', 'roll_deg', 'pitch_deg', 'yaw_deg', 'wz_rad_s', 'odom_yaw_deg', 'cmd_wz']


def wrap180(deg: float) -> float:
    return (deg + 180.0) % 360.0 - 180.0


class Recorder(Node):
    def __init__(self) -> None:
        super().__init__('imu_turn_record',
                         parameter_overrides=[Parameter('use_sim_time', value=True)])
        self.rows = []
        self.wz = None
        self.odom_yaw = None
        self.cmd_wz = 0.0
        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.create_subscription(Vector3Stamped, '/imu/rpy', self._on_rpy, 10)
        self.create_subscription(Imu, '/imu', self._on_imu, qos_profile_sensor_data)
        self.create_subscription(Odometry, '/odom', self._on_odom, 10)

    def now(self) -> float:
        return self.get_clock().now().nanoseconds * 1e-9

    def _on_imu(self, msg: Imu) -> None:
        self.wz = msg.angular_velocity.z

    def _on_odom(self, msg: Odometry) -> None:
        q = msg.pose.pose.orientation
        self.odom_yaw = math.degrees(math.atan2(2.0 * (q.w * q.z + q.x * q.y),
                                                1.0 - 2.0 * (q.y * q.y + q.z * q.z)))

    def _on_rpy(self, msg: Vector3Stamped) -> None:
        if self.wz is None or self.odom_yaw is None:
            return
        t = msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9
        v = msg.vector
        self.rows.append([t, v.x, v.y, v.z, self.wz, self.odom_yaw, self.cmd_wz])

    def drive(self, seconds: float, wz: float) -> None:
        self.cmd_wz = wz
        cmd = Twist()
        cmd.angular.z = wz
        end = self.now() + seconds
        while self.now() < end:
            self.cmd_pub.publish(cmd)
            rclpy.spin_once(self, timeout_sec=0.05)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('csv', help='output CSV path')
    parser.add_argument('--turn-seconds', type=float, default=6.0, help='turn time (sim)')
    parser.add_argument('--rate', type=float, default=0.8, help='angular.z command [rad/s]')
    args = parser.parse_args()

    rclpy.init()
    node = Recorder()
    while not node.rows:
        rclpy.spin_once(node, timeout_sec=0.1)
    node.rows.clear()
    node.drive(1.0, 0.0)
    node.drive(args.turn_seconds, args.rate)
    node.drive(2.0, 0.0)
    node.cmd_pub.publish(Twist())

    rows = node.rows
    with open(args.csv, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(HEADER)
        writer.writerows(rows)
    span = rows[-1][0] - rows[0][0]
    diff = [abs(wrap180(r[3] - r[5])) for r in rows]
    print(f'{len(rows)} samples, {span:.2f} s sim, {(len(rows) - 1) / span:.1f} Hz')
    print(f'yaw imu {rows[0][3]:+.2f} -> {rows[-1][3]:+.2f} deg, '
          f'odom {rows[0][5]:+.2f} -> {rows[-1][5]:+.2f} deg')
    print(f'max |imu yaw - odom yaw| {max(diff):.2f} deg, mean {sum(diff) / len(diff):.2f}')
    print(f'max |roll| {max(abs(r[1]) for r in rows):.3f}, '
          f'max |pitch| {max(abs(r[2]) for r in rows):.3f} deg')
    print('saved', args.csv)
    node.destroy_node()
    rclpy.try_shutdown()


if __name__ == '__main__':
    main()
