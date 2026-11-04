"""ROS 2 node that finds ripe (red) produce in the SeraBot camera image.

Input:   /camera/image_raw (sensor_msgs/Image)
Outputs: /camera/target (geometry_msgs/PointStamped), only while a target is seen:
             point.x = horizontal offset [-1, 1] (left negative),
             point.y = image area ratio [0, 1], point.z = 0
         /camera/image_annotated (sensor_msgs/Image), every frame, for rqt_image_view
Image processing lives in serabot_sensors.color_detection; this node only does ROS I/O.
"""

from dataclasses import fields

from cv_bridge import CvBridge
from geometry_msgs.msg import PointStamped
import rclpy
from rclpy.node import Node
from rclpy.qos import HistoryPolicy, QoSProfile, ReliabilityPolicy
from sensor_msgs.msg import Image
from serabot_sensors.color_detection import annotate, ColorParams, detect_red
from serabot_sensors.spin import spin_node

# Deliberate exception to the qos_profile_sensor_data rule (docs/modules/sensor-camera.md):
# a 640x480 RGB frame is ~0.9 MB, larger than Fast DDS's shared-memory segment, so it
# travels as UDP fragments and a best-effort reader loses whole frames when one fragment
# is dropped (measured: 1.75 of 15 Hz, gaps up to 2.4 s). Reliable delivery (the bridge
# publishes reliably) gets every frame; depth 1 keeps only the newest one if processing
# falls behind, so the published target is always current.
LATEST_FRAME_QOS = QoSProfile(
    history=HistoryPolicy.KEEP_LAST,
    depth=1,
    reliability=ReliabilityPolicy.RELIABLE,
)


class ColorDetector(Node):
    """Thresholds every camera frame and publishes the largest red blob."""

    def __init__(self) -> None:
        super().__init__('color_detector')
        self.params = ColorParams(**{
            f.name: self.declare_parameter(f.name, f.default).value
            for f in fields(ColorParams)})
        self.bridge = CvBridge()
        self.seen = False

        self.target_pub = self.create_publisher(PointStamped, '/camera/target', 10)
        self.image_pub = self.create_publisher(Image, '/camera/image_annotated', 10)
        self.create_subscription(Image, '/camera/image_raw', self._on_image, LATEST_FRAME_QOS)
        self.get_logger().info(f'color_detector started: {self.params}')

    def _on_image(self, msg: Image) -> None:
        bgr = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        detection, mask = detect_red(bgr, self.params)

        if detection is not None:
            target = PointStamped()
            target.header = msg.header
            target.point.x = detection.offset
            target.point.y = detection.area_ratio
            self.target_pub.publish(target)
        if (detection is not None) != self.seen:
            self.seen = detection is not None
            self.get_logger().info(
                f'target seen: offset {detection.offset:+.2f}, '
                f'area {detection.area_ratio:.4f}' if self.seen else 'target lost')

        if self.image_pub.get_subscription_count() > 0:
            out = self.bridge.cv2_to_imgmsg(annotate(bgr, mask, detection), encoding='bgr8')
            out.header = msg.header
            self.image_pub.publish(out)


def main(args=None) -> None:
    rclpy.init(args=args)
    spin_node(ColorDetector())


if __name__ == '__main__':
    main()
