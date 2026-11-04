"""Orientation maths for the IMU monitor, independent of ROS.

Converts the unit quaternion of a sensor_msgs/Imu message to roll, pitch and yaw
(intrinsic Z-Y-X / aerospace convention, as in tf2 `getRPY`): yaw about z, then
pitch about the new y, then roll about the new x.
"""

import math
from typing import Tuple


def quaternion_to_rpy(x: float, y: float, z: float, w: float) -> Tuple[float, float, float]:
    """Roll, pitch, yaw in radians from a quaternion; normalises it first.

    Pitch is clamped to +-pi/2 so rounding near gimbal lock does not produce NaN.
    """
    norm = math.sqrt(x * x + y * y + z * z + w * w)
    if norm == 0.0:
        raise ValueError('zero quaternion has no orientation')
    x, y, z, w = x / norm, y / norm, z / norm, w / norm

    roll = math.atan2(2.0 * (w * x + y * z), 1.0 - 2.0 * (x * x + y * y))
    sin_pitch = max(-1.0, min(1.0, 2.0 * (w * y - z * x)))
    pitch = math.asin(sin_pitch)
    yaw = math.atan2(2.0 * (w * z + x * y), 1.0 - 2.0 * (y * y + z * z))
    return roll, pitch, yaw


def quaternion_to_rpy_degrees(x: float, y: float, z: float,
                              w: float) -> Tuple[float, float, float]:
    """Roll, pitch, yaw in degrees (yaw in (-180, 180])."""
    return tuple(math.degrees(a) for a in quaternion_to_rpy(x, y, z, w))
