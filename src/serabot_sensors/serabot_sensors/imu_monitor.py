"""ROS 2 node that turns the IMU orientation into roll/pitch/yaw angles for plotting.

Input:  /imu (sensor_msgs/Imu)
Output: /imu/rpy (geometry_msgs/Vector3Stamped): vector.x = roll, vector.y = pitch,
        vector.z = yaw, in degrees; header copied from the IMU message.
Plot:   ros2 run rqt_plot rqt_plot /imu/rpy/vector/z /imu/angular_velocity/z
The conversion lives in serabot_sensors.imu_math; this node only does ROS I/O.
"""

from geometry_msgs.msg import Vector3Stamped
import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import Imu
from serabot_sensors.imu_math import quaternion_to_rpy_degrees
from serabot_sensors.spin import spin_node


class ImuMonitor(Node):
    """Republishes every IMU orientation as roll/pitch/yaw in degrees."""

    def __init__(self) -> None:
        super().__init__('imu_monitor')
        self.rpy_pub = self.create_publisher(Vector3Stamped, '/imu/rpy', 10)
        self.create_subscription(Imu, '/imu', self._on_imu, qos_profile_sensor_data)
        self.get_logger().info('imu_monitor started: /imu -> /imu/rpy (degrees)')

    def _on_imu(self, msg: Imu) -> None:
        q = msg.orientation
        try:
            roll, pitch, yaw = quaternion_to_rpy_degrees(q.x, q.y, q.z, q.w)
        except ValueError:
            self.get_logger().warning('IMU message without orientation, skipped',
                                      throttle_duration_sec=5.0)
            return
        out = Vector3Stamped()
        out.header = msg.header
        out.vector.x, out.vector.y, out.vector.z = roll, pitch, yaw
        self.rpy_pub.publish(out)


def main(args=None) -> None:
    rclpy.init(args=args)
    spin_node(ImuMonitor())


if __name__ == '__main__':
    main()
