"""Tests for the ROS-free behavior logic (run with: python -m pytest src/serabot_behavior/test)."""

import math
from typing import Iterable, Optional, Tuple

import pytest

from serabot_behavior.logic import (
    analyze_scan, BehaviorParams, BehaviorStateMachine, clean_range, ScanData, State)

N = 360
ANGLE_MIN = -math.pi
INC = 2 * math.pi / N
RANGE_MIN = 0.25
RANGE_MAX = 8.0
DT = 0.1  # 10 Hz control tick

Obstacle = Tuple[float, float, float]  # lidar bearing from [deg], to [deg], range [m]


def make_scan(stamp: float = 0.0, obstacles: Iterable[Obstacle] = (),
              default: float = math.inf) -> ScanData:
    ranges = [default] * N
    for lo, hi, r in obstacles:
        for i in range(N):
            if lo <= math.degrees(ANGLE_MIN + i * INC) <= hi:
                ranges[i] = r
    return ScanData(ranges, ANGLE_MIN, INC, RANGE_MIN, RANGE_MAX, stamp)


FRONT_WALL = (-20.0, 20.0, 0.5)
RIGHT_CLOSE = (-90.0, -31.0, 1.0)
LEFT_CLOSE = (31.0, 90.0, 1.0)


class Sim:
    """Drives the state machine at 10 Hz with optional 100 Hz IMU samples."""

    def __init__(self, **overrides) -> None:
        self.p = BehaviorParams(**overrides)
        self.sm = BehaviorStateMachine(self.p)
        self.t = 0.0

    def step(self, obstacles: Iterable[Obstacle] = (), yaw_rate: Optional[float] = None):
        if yaw_rate is not None:
            for k in range(1, 11):
                self.sm.on_imu(self.t - DT + k * DT / 10, yaw_rate)
        summary = analyze_scan(make_scan(self.t, obstacles), self.p)
        cmd = self.sm.update(self.t, summary)
        self.t = round(self.t + DT, 6)
        return cmd


# -- scan analysis --------------------------------------------------------

def test_clean_range():
    assert clean_range(math.nan, RANGE_MIN, RANGE_MAX) is None
    assert clean_range(-math.inf, RANGE_MIN, RANGE_MAX) is None
    assert clean_range(0.1, RANGE_MIN, RANGE_MAX) is None
    assert clean_range(math.inf, RANGE_MIN, RANGE_MAX) == RANGE_MAX
    assert clean_range(12.0, RANGE_MIN, RANGE_MAX) == RANGE_MAX
    assert clean_range(1.5, RANGE_MIN, RANGE_MAX) == 1.5


def test_invalid_ranges_are_ignored():
    scan = make_scan(obstacles=[(-10, 0, math.nan), (0, 10, 0.1)])
    s = analyze_scan(scan, BehaviorParams())
    assert s.front_min == RANGE_MAX
    assert s.rotate_clear_left == RANGE_MAX


def test_swept_radius_is_front_corner():
    p = BehaviorParams()
    assert p.swept_radius == pytest.approx(math.hypot(0.345, 0.15))
    assert p.swept_radius == pytest.approx(0.376, abs=1e-3)


def test_body_corridor_catches_obstacle_outside_front_sector():
    # 50 deg from the lidar at 0.4 m lies 0.48 m ahead of base_link, 0.31 m aside:
    # outside the +-30 deg sector but inside the 0.52 m body corridor.
    s = analyze_scan(make_scan(obstacles=[(49, 51, 0.4)]), BehaviorParams())
    assert s.front_min == pytest.approx(0.4)


def test_rear_gap_measured_from_chassis_rear():
    s = analyze_scan(make_scan(obstacles=[(178, 180, 0.6)]), BehaviorParams())
    assert s.rear_gap == pytest.approx(0.6 - 0.22 - 0.105, abs=0.01)


# -- core state machine ---------------------------------------------------

def test_no_obstacle_cruises_forward():
    sim = Sim()
    cmd = sim.step()
    assert cmd.state == State.CRUISE
    assert cmd.linear == pytest.approx(0.25)
    assert cmd.angular == 0.0


@pytest.mark.parametrize('side, expected_sign', [((45, 95, 0.5), -1), ((-95, -45, 0.5), 1)])
def test_cruise_centers_away_from_closer_side(side, expected_sign):
    sim = Sim()
    cmd = sim.step([side])
    assert cmd.state == State.CRUISE
    assert math.copysign(1, cmd.angular) == expected_sign
    assert abs(cmd.angular) <= sim.p.max_centering
    assert Sim(centering_gain=0.0).step([side]).angular == 0.0


def test_front_obstacle_starts_turn_in_place():
    sim = Sim()
    sim.step()
    cmd = sim.step([FRONT_WALL])
    assert cmd.state == State.AVOID
    assert cmd.linear == 0.0
    assert cmd.angular != 0.0
    assert 'CRUISE -> AVOID' in cmd.reason


@pytest.mark.parametrize('side, expected_sign', [(RIGHT_CLOSE, 1), (LEFT_CLOSE, -1)])
def test_turns_towards_open_side(side, expected_sign):
    sim = Sim()
    cmd = sim.step([FRONT_WALL, side])
    assert cmd.state == State.AVOID
    assert math.copysign(1, cmd.angular) == expected_sign


def test_turn_ends_when_imu_angle_reached_and_front_clear():
    # IMU reports twice the commanded rate: the turn must finish on the IMU
    # angle (60 deg after ~0.65 s), well before the time-based estimate (1.3 s).
    sim = Sim()
    sim.step([FRONT_WALL])
    states = [sim.step(yaw_rate=1.6).state for _ in range(8)]
    assert states[4] == State.AVOID
    assert states[-1] == State.CRUISE
    assert sim.sm.turn_source == 'imu'


def test_turn_continues_until_front_clear():
    sim = Sim()
    sim.step([FRONT_WALL])
    for _ in range(20):
        cmd = sim.step([(-20, 20, 0.7)], yaw_rate=0.8)  # past 0.55 but below 0.8
    assert cmd.state == State.AVOID
    assert sim.sm.turned_deg > 60
    assert sim.step(yaw_rate=0.8).state == State.CRUISE


def test_time_fallback_without_imu():
    sim = Sim()
    sim.step([FRONT_WALL])  # t = 0.0
    for _ in range(12):     # t = 0.1 .. 1.2 -> 0.96 rad < 60 deg
        cmd = sim.step()
    assert cmd.state == State.AVOID
    sim.step()              # t = 1.3 -> 1.04 rad
    cmd = sim.step()        # t = 1.4 -> 1.12 rad
    assert cmd.state == State.CRUISE
    assert sim.sm.turn_source == 'time'


def test_imu_dropout_switches_to_time_fallback():
    sim = Sim()
    sim.step([FRONT_WALL])
    sim.step(yaw_rate=0.0)       # IMU alive but robot "stuck"
    for _ in range(20):          # IMU stops; time-based estimate takes over
        cmd = sim.step()
    assert cmd.state == State.CRUISE
    assert sim.sm.turn_source == 'time'


def test_emergency_backs_up_then_avoids():
    sim = Sim()
    cmd = sim.step([(-20, 20, 0.28)])
    assert cmd.state == State.EMERGENCY
    assert cmd.linear < 0.0
    assert cmd.angular == 0.0
    for _ in range(15):  # backup_duration 1.5 s
        cmd = sim.step([(-20, 20, 0.35)])
    assert cmd.state == State.AVOID


def test_emergency_does_not_back_into_rear_obstacle():
    sim = Sim()
    cmd = sim.step([(-20, 20, 0.28), (175, 180, 0.4), (-180, -175, 0.4)])
    assert cmd.state == State.EMERGENCY
    assert cmd.linear == 0.0


# Points ~0.39 m from base_link at +-45 deg (lidar bearing ~78 deg, 0.28 m):
# outside the body but inside the 0.376 m turn circle plus the 0.02 m margin.
LEFT_CORNER = (77, 80, 0.282)
RIGHT_CORNER = (-80, -77, 0.282)


def test_no_room_to_turn_goes_to_emergency():
    sim = Sim()
    cmd = sim.step([FRONT_WALL, LEFT_CORNER, RIGHT_CORNER])
    assert cmd.state == State.EMERGENCY
    assert 'no room to turn' in cmd.reason


def test_turn_direction_respects_turn_clearance():
    # Left is more open on average, but the left front corner would hit a pot.
    sim = Sim()
    cmd = sim.step([FRONT_WALL, RIGHT_CLOSE, LEFT_CORNER])
    assert cmd.state == State.AVOID
    assert cmd.angular < 0.0


def test_waits_without_scan():
    p = BehaviorParams()
    sm = BehaviorStateMachine(p)
    cmd = sm.update(0.0, None)
    assert (cmd.state, cmd.linear, cmd.angular) == (State.WAIT, 0.0, 0.0)
    stale = analyze_scan(make_scan(stamp=0.0), p)
    assert sm.update(0.2, stale).state == State.CRUISE
    cmd = sm.update(1.0, stale)
    assert (cmd.state, cmd.linear) == (State.WAIT, 0.0)


# -- camera layer ---------------------------------------------------------

def test_target_ignored_when_camera_disabled():
    sim = Sim()
    sim.sm.on_target(0.0, -0.5, 0.01)
    assert sim.step().state == State.CRUISE


@pytest.mark.parametrize('offset, expected_sign', [(-0.5, 1), (0.5, -1)])
def test_target_offset_sign(offset, expected_sign):
    sim = Sim(use_camera=True)
    sim.sm.on_target(0.0, offset, 0.01)
    cmd = sim.step()
    assert cmd.state == State.TRACK
    assert cmd.linear == pytest.approx(0.12)
    assert math.copysign(1, cmd.angular) == expected_sign


def test_target_lost_after_timeout():
    sim = Sim(use_camera=True)
    sim.sm.on_target(0.0, 0.0, 0.01)
    assert sim.step().state == State.TRACK
    for _ in range(6):
        cmd = sim.step()
    assert cmd.state == State.CRUISE


def test_inspect_then_turn_away_with_cooldown():
    sim = Sim(use_camera=True)
    sim.sm.on_target(0.0, 0.0, 0.1)
    cmd = sim.step()
    assert cmd.state == State.INSPECT
    assert (cmd.linear, cmd.angular) == (0.0, 0.0)
    while sim.t < 3.05:
        sim.sm.on_target(sim.t, 0.0, 0.1)
        cmd = sim.step()
    assert cmd.state == State.AVOID
    for _ in range(20):  # target still visible, but in cooldown
        sim.sm.on_target(sim.t, 0.0, 0.1)
        cmd = sim.step(yaw_rate=0.8)
    assert cmd.state == State.CRUISE


def test_reaching_bed_while_tracking_inspects():
    sim = Sim(use_camera=True)
    sim.sm.on_target(0.0, 0.0, 0.01)
    assert sim.step().state == State.TRACK
    sim.sm.on_target(sim.t, 0.0, 0.02)
    cmd = sim.step([FRONT_WALL])
    assert cmd.state == State.INSPECT
