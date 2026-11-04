#!/usr/bin/env python3
"""Check the SeraBot camera chain in a running simulation (owner: Member B).

Measures, in simulation time, the rate and largest gap of /camera/image_raw and
/camera/target, prints frame ids, image size and camera intrinsics, and saves the
latest raw and annotated frames as PNG files.

Usage (bringup running, color_detector started by it):
    python3 scripts/sim/camera_check.py [--seconds 10] [--out-dir docs/report/sensors]
"""

import argparse
import os
import time

import cv2
from cv_bridge import CvBridge
from geometry_msgs.msg import PointStamped
import rclpy
from rclpy.experimental import EventsExecutor
from rclpy.node import Node
from rclpy.qos import HistoryPolicy, QoSProfile, ReliabilityPolicy
from sensor_msgs.msg import CameraInfo, Image

# Large images need a reliable reader (see color_detector.py).
IMAGE_QOS = QoSProfile(history=HistoryPolicy.KEEP_LAST, depth=1,
                       reliability=ReliabilityPolicy.RELIABLE)


def stamp(msg) -> float:
    return msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9


def summary(name: str, stamps) -> str:
    stamps = sorted(set(stamps))
    if len(stamps) < 2:
        return f'{name}: {len(stamps)} messages'
    span = stamps[-1] - stamps[0]
    gap = max(b - a for a, b in zip(stamps, stamps[1:]))
    return (f'{name}: {len(stamps)} msgs, {(len(stamps) - 1) / span:.2f} Hz (sim), '
            f'max gap {gap:.3f} s')


class CameraCheck(Node):
    def __init__(self) -> None:
        super().__init__('camera_check')
        self.raw = []
        self.targets = []
        self.last_raw = None
        self.last_annotated = None
        self.last_target = None
        self.info = None
        self.create_subscription(Image, '/camera/image_raw', self._on_raw, IMAGE_QOS)
        self.create_subscription(Image, '/camera/image_annotated', self._on_annotated,
                                 IMAGE_QOS)
        self.create_subscription(CameraInfo, '/camera/camera_info', self._on_info, 10)
        self.create_subscription(PointStamped, '/camera/target', self._on_target, 10)

    def _on_raw(self, msg: Image) -> None:
        self.raw.append(stamp(msg))
        self.last_raw = msg

    def _on_annotated(self, msg: Image) -> None:
        self.last_annotated = msg

    def _on_info(self, msg: CameraInfo) -> None:
        self.info = msg

    def _on_target(self, msg: PointStamped) -> None:
        self.targets.append(stamp(msg))
        self.last_target = msg


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--seconds', type=float, default=10.0, help='wall-clock duration')
    parser.add_argument('--out-dir', default='.', help='where to save the PNG files')
    parser.add_argument('--prefix', default='camera', help='PNG file name prefix')
    args = parser.parse_args()

    rclpy.init()
    node = CameraCheck()
    executor = EventsExecutor()
    executor.add_node(node)
    end = time.time() + args.seconds
    while time.time() < end:
        executor.spin_once(timeout_sec=0.1)

    print(summary('/camera/image_raw', node.raw))
    print(summary('/camera/target', node.targets))
    if node.last_raw is not None:
        m = node.last_raw
        print(f'image: frame_id={m.header.frame_id} {m.width}x{m.height} {m.encoding}')
    if node.info is not None:
        i = node.info
        print(f'camera_info: frame_id={i.header.frame_id} {i.width}x{i.height} '
              f'fx={i.k[0]:.1f} fy={i.k[4]:.1f} cx={i.k[2]:.1f} cy={i.k[5]:.1f}')
    if node.last_target is not None:
        t = node.last_target
        print(f'last target: frame_id={t.header.frame_id} offset={t.point.x:+.3f} '
              f'area={t.point.y:.4f}')

    bridge = CvBridge()
    os.makedirs(args.out_dir, exist_ok=True)
    for suffix, msg in (('raw', node.last_raw), ('annotated', node.last_annotated)):
        if msg is not None:
            path = os.path.join(args.out_dir, f'{args.prefix}_{suffix}.png')
            cv2.imwrite(path, bridge.imgmsg_to_cv2(msg, 'bgr8'))
            print('saved', path)
    node.destroy_node()
    rclpy.try_shutdown()


if __name__ == '__main__':
    main()
