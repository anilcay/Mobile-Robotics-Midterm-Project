#!/usr/bin/env python3
"""Record a run of behavior_node with the camera layer on (owner: Member B).

Logs every /behavior/state change with the /odom pose and the latest /camera/target,
the /odom path at 10 Hz, and saves /camera/image_annotated at the first TRACK and
INSPECT entries. Start it, then start behavior_node with use_camera:=true:

    python3 scripts/sim/camera_track_record.py OUT_DIR --seconds 90 &
    ros2 run serabot_behavior behavior_node --ros-args \
        --params-file install/serabot_bringup/share/serabot_bringup/config/behavior.yaml \
        -p use_camera:=true -p use_sim_time:=true

Outputs: OUT_DIR/camera_track_states.csv, camera_track_path.csv,
camera_track_{track,inspect}_<n>.png

Ground truth: odometry drifts after many in-place turns. With --ground-truth the
path also records the model pose from Gazebo; bridge it first:
    ros2 run ros_gz_bridge parameter_bridge \
        /world/greenhouse/dynamic_pose/info@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V
"""

import argparse
import csv
import math
import os

import cv2
from cv_bridge import CvBridge
from geometry_msgs.msg import PointStamped
from nav_msgs.msg import Odometry
import rclpy
from rclpy.experimental import EventsExecutor
from rclpy.node import Node
from rclpy.parameter import Parameter
from rclpy.qos import HistoryPolicy, QoSProfile, ReliabilityPolicy
from sensor_msgs.msg import Image
from std_msgs.msg import String
from tf2_msgs.msg import TFMessage

IMAGE_QOS = QoSProfile(history=HistoryPolicy.KEEP_LAST, depth=1,
                       reliability=ReliabilityPolicy.RELIABLE)
TARGET_FRESH = 0.5  # s, same as target_timeout
FRAMES_PER_STATE = 2
GT_TOPIC = '/world/greenhouse/dynamic_pose/info'
MODEL = 'serabot'


def yaw_deg(q) -> float:
    return math.degrees(math.atan2(2.0 * (q.w * q.z + q.x * q.y),
                                   1.0 - 2.0 * (q.y * q.y + q.z * q.z)))


class TrackRecorder(Node):
    def __init__(self, out_dir: str, ground_truth: bool) -> None:
        super().__init__('camera_track_record',
                         parameter_overrides=[Parameter('use_sim_time', value=True)])
        self.out_dir = out_dir
        self.bridge = CvBridge()
        self.state = None
        self.pose = (0.0, 0.0, 0.0)
        self.gt = None  # world x, y, yaw_deg of the model (Gazebo)
        self.target = None
        self.image = None
        self.transitions = []
        self.path = []
        self.steps = {}
        self.saved = {}
        self.create_subscription(String, '/behavior/state', self._on_state, 10)
        self.create_subscription(Odometry, '/odom', self._on_odom, 10)
        self.create_subscription(PointStamped, '/camera/target', self._on_target, 10)
        self.create_subscription(Image, '/camera/image_annotated', self._on_image, IMAGE_QOS)
        if ground_truth:
            self.create_subscription(TFMessage, GT_TOPIC, self._on_ground_truth, 10)

    def now(self) -> float:
        return self.get_clock().now().nanoseconds * 1e-9

    def _on_ground_truth(self, msg: TFMessage) -> None:
        # The bridge leaves the frame ids empty (Lyrical + Jetty 10.5.0). The topic
        # holds only non-static entities, the robot model first and then its links
        # (checked with `gz topic -e`), so the first transform is the model pose.
        named = [tf for tf in msg.transforms if tf.child_frame_id == MODEL]
        tfs = named or msg.transforms[:1]
        if tfs:
            t = tfs[0].transform.translation
            self.gt = (t.x, t.y, yaw_deg(tfs[0].transform.rotation))

    def _on_odom(self, msg: Odometry) -> None:
        p = msg.pose.pose.position
        self.pose = (p.x, p.y, yaw_deg(msg.pose.pose.orientation))
        if not self.path or self.now() - self.path[-1][0] >= 0.1:
            gt = list(self.gt) if self.gt else ['', '', '']
            self.path.append([self.now(), *self.pose, self.state or '', *gt])

    def _on_target(self, msg: PointStamped) -> None:
        self.target = (self.now(), msg.point.x, msg.point.y)

    def _on_image(self, msg: Image) -> None:
        self.image = msg

    def _on_state(self, msg: String) -> None:
        state = msg.data
        self.steps[state] = self.steps.get(state, 0) + 1
        if state == self.state:
            return
        fresh = self.target is not None and self.now() - self.target[0] <= TARGET_FRESH
        offset, area = (self.target[1], self.target[2]) if fresh else ('', '')
        gt = list(self.gt) if self.gt else ['', '', '']
        self.transitions.append([self.now(), self.state or '', state, *self.pose, offset, area,
                                 *gt])
        target_text = f'offset {offset:+.2f} area {area:.4f}' if fresh else 'no target'
        print(f't={self.now():7.2f} {self.state} -> {state} at ({self.pose[0]:+.2f}, '
              f'{self.pose[1]:+.2f}, {self.pose[2]:+.0f} deg), {target_text}', flush=True)
        self.state = state
        if state in ('TRACK', 'INSPECT') and self.image is not None \
                and self.saved.get(state, 0) < FRAMES_PER_STATE:
            self.saved[state] = self.saved.get(state, 0) + 1
            name = f'camera_track_{state.lower()}_{self.saved[state]}.png'
            cv2.imwrite(os.path.join(self.out_dir, name),
                        self.bridge.imgmsg_to_cv2(self.image, 'bgr8'))

    def write(self) -> None:
        with open(os.path.join(self.out_dir, 'camera_track_states.csv'), 'w', newline='') as f:
            w = csv.writer(f)
            w.writerow(['t', 'from', 'to', 'x', 'y', 'yaw_deg', 'target_offset', 'target_area',
                        'gt_x', 'gt_y', 'gt_yaw_deg'])
            w.writerows(self.transitions)
        with open(os.path.join(self.out_dir, 'camera_track_path.csv'), 'w', newline='') as f:
            w = csv.writer(f)
            w.writerow(['t', 'x', 'y', 'yaw_deg', 'state', 'gt_x', 'gt_y', 'gt_yaw_deg'])
            w.writerows(self.path)
        print('state steps (control ticks):', self.steps)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('out_dir')
    parser.add_argument('--seconds', type=float, default=90.0, help='duration, sim time')
    parser.add_argument('--ground-truth', action='store_true',
                        help=f'also record the Gazebo model pose from {GT_TOPIC}')
    args = parser.parse_args()
    os.makedirs(args.out_dir, exist_ok=True)

    rclpy.init()
    node = TrackRecorder(args.out_dir, args.ground_truth)
    executor = EventsExecutor()
    executor.add_node(node)
    try:
        while node.now() == 0.0:
            executor.spin_once(timeout_sec=0.1)
        end = node.now() + args.seconds
        while node.now() < end:
            executor.spin_once(timeout_sec=0.1)
    finally:
        node.write()
        executor.shutdown()
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
