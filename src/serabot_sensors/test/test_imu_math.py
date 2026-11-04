"""Tests for the quaternion -> roll/pitch/yaw conversion used by imu_monitor."""

import math

import pytest
from serabot_sensors.imu_math import quaternion_to_rpy, quaternion_to_rpy_degrees


def rpy_to_quaternion(roll: float, pitch: float, yaw: float):
    """Reference conversion (Z-Y-X), returns (x, y, z, w)."""
    cr, sr = math.cos(roll / 2), math.sin(roll / 2)
    cp, sp = math.cos(pitch / 2), math.sin(pitch / 2)
    cy, sy = math.cos(yaw / 2), math.sin(yaw / 2)
    return (sr * cp * cy - cr * sp * sy,
            cr * sp * cy + sr * cp * sy,
            cr * cp * sy - sr * sp * cy,
            cr * cp * cy + sr * sp * sy)


def test_identity_is_zero():
    assert quaternion_to_rpy(0.0, 0.0, 0.0, 1.0) == pytest.approx((0.0, 0.0, 0.0))


def test_yaw_left_turn_is_positive():
    # 90 deg about z: robot turned left (counter-clockwise seen from above, REP-103).
    s = math.sqrt(0.5)
    assert quaternion_to_rpy_degrees(0.0, 0.0, s, s) == pytest.approx((0.0, 0.0, 90.0))


def test_yaw_half_turn():
    roll, pitch, yaw = quaternion_to_rpy_degrees(0.0, 0.0, 1.0, 0.0)
    assert (roll, pitch) == pytest.approx((0.0, 0.0), abs=1e-9)
    assert abs(yaw) == pytest.approx(180.0)


def test_measured_gazebo_sample():
    # /imu sample while turning in place (docs/modules/sensor-imu.md): z=0.974 w=0.226
    _, _, yaw = quaternion_to_rpy_degrees(0.0, 0.0, 0.974, 0.226)
    assert yaw == pytest.approx(153.9, abs=0.1)


@pytest.mark.parametrize('roll,pitch,yaw', [
    (0.3, 0.0, 0.0),
    (0.0, -0.4, 0.0),
    (0.1, 0.2, -2.5),
    (-1.0, 0.7, 3.0),
])
def test_round_trip(roll, pitch, yaw):
    q = rpy_to_quaternion(roll, pitch, yaw)
    assert quaternion_to_rpy(*q) == pytest.approx((roll, pitch, yaw), abs=1e-9)


def test_unnormalised_quaternion_is_normalised():
    q = [2.0 * c for c in rpy_to_quaternion(0.2, -0.1, 1.0)]
    assert quaternion_to_rpy(*q) == pytest.approx((0.2, -0.1, 1.0), abs=1e-9)


def test_gimbal_lock_does_not_return_nan():
    q = rpy_to_quaternion(0.0, math.pi / 2, 0.0)
    q = (q[0], q[1] * (1 + 1e-12), q[2], q[3])  # rounding pushes |sin(pitch)| past 1
    _, pitch, _ = quaternion_to_rpy(*q)
    assert pitch == pytest.approx(math.pi / 2)


def test_zero_quaternion_raises():
    with pytest.raises(ValueError):
        quaternion_to_rpy(0.0, 0.0, 0.0, 0.0)
