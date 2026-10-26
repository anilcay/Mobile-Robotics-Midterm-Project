"""ROS 2 wrapper around the SeraBot behavior state machine.

Inputs:  /scan (LaserScan), /imu (Imu), /camera/target (PointStamped, if use_camera)
Outputs: /cmd_vel (Twist), /behavior/state (String)
Decision logic lives in serabot_behavior.logic; this node only does ROS I/O.
"""

from dataclasses import fields
import signal
import time
from typing import Optional

from geometry_msgs.msg import PointStamped, Twist
import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from rclpy.signals import SignalHandlerOptions
from sensor_msgs.msg import Imu, LaserScan
from serabot_behavior.logic import (
    analyze_scan, BehaviorParams, BehaviorStateMachine, Command, ScanData, ScanSummary)
from std_msgs.msg import String


class BehaviorNode(Node):
    """Subscribes to sensors, runs the state machine at control_rate, publishes commands."""

    def __init__(self) -> None:
        super().__init__('behavior_node')
        self.params = self._declare_params()
        control_rate = float(self.declare_parameter('control_rate', 10.0).value)

        self.machine = BehaviorStateMachine(self.params)
        self._scan: Optional[ScanSummary] = None

        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.state_pub = self.create_publisher(String, '/behavior/state', 10)
        self.create_subscription(LaserScan, '/scan', self._on_scan, qos_profile_sensor_data)
        self.create_subscription(Imu, '/imu', self._on_imu, qos_profile_sensor_data)
        if self.params.use_camera:
            self.create_subscription(
                PointStamped, '/camera/target', self._on_target, qos_profile_sensor_data)

        # Timers follow the node clock, i.e. simulation time with use_sim_time.
        self.create_timer(1.0 / control_rate, self._on_timer)
        self.get_logger().info(
            f'behavior_node started: {control_rate:.0f} Hz, use_camera={self.params.use_camera}, '
            f'turn radius {self.params.swept_radius:.3f} m')

    def _declare_params(self) -> BehaviorParams:
        values = {f.name: self.declare_parameter(f.name, f.default).value
                  for f in fields(BehaviorParams)}
        return BehaviorParams(**values)

    def _now(self) -> float:
        return self.get_clock().now().nanoseconds * 1e-9

    def _stamp(self, msg) -> float:
        """Message stamp in seconds; node time if the sender left it empty."""
        stamp = msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9
        return stamp if stamp > 0.0 else self._now()

    def _on_scan(self, msg: LaserScan) -> None:
        scan = ScanData(msg.ranges, msg.angle_min, msg.angle_increment,
                        msg.range_min, msg.range_max, self._stamp(msg))
        self._scan = analyze_scan(scan, self.params)

    def _on_imu(self, msg: Imu) -> None:
        self.machine.on_imu(self._stamp(msg), msg.angular_velocity.z)

    def _on_target(self, msg: PointStamped) -> None:
        self.machine.on_target(self._stamp(msg), msg.point.x, msg.point.y)

    def _on_timer(self) -> None:
        cmd = self.machine.update(self._now(), self._scan)
        if cmd.reason:
            self.get_logger().info(cmd.reason)
        self._publish(cmd)

    def _publish(self, cmd: Command) -> None:
        twist = Twist()
        twist.linear.x = float(cmd.linear)
        twist.angular.z = float(cmd.angular)
        self.cmd_pub.publish(twist)
        self.state_pub.publish(String(data=cmd.state.value))

    def stop(self) -> None:
        """Publish a zero velocity a few times so the robot halts on shutdown."""
        for _ in range(3):
            self.cmd_pub.publish(Twist())
            time.sleep(0.05)


def _interrupt(signum, frame) -> None:
    raise KeyboardInterrupt


def main(args=None) -> None:
    # Own SIGINT/SIGTERM handling keeps the context alive long enough to send the
    # stop command; set explicitly because SIGINT may be inherited as ignored.
    signal.signal(signal.SIGINT, _interrupt)
    signal.signal(signal.SIGTERM, _interrupt)
    rclpy.init(args=args, signal_handler_options=SignalHandlerOptions.NO)
    node = BehaviorNode()
    try:
        # spin_once with a wall-time timeout returns to Python regularly, so the
        # signal handler runs even when no /clock arrives (sim-time timers idle).
        while True:
            rclpy.spin_once(node, timeout_sec=0.1)
    except KeyboardInterrupt:
        pass
    finally:
        node.stop()
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
