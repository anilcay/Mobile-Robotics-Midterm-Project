"""Pure decision logic for the SeraBot behavior node (no ROS imports).

The node feeds scans, IMU yaw rates and camera targets into
`BehaviorStateMachine` and publishes the returned `Command`. All times are
simulation seconds, so the logic is independent of the real-time factor.

Geometry (docs/INTERFACES.md section 4): base_link is the axle centre (the
rotation centre), lidar_link is `lidar_offset_x` ahead of it. Scan points are
moved into base_link so the body footprint and the circle swept by an
in-place turn can be checked directly.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import math
from typing import List, Optional, Sequence


class State(str, Enum):
    """Behavior states published on /behavior/state."""

    WAIT = 'WAIT'
    CRUISE = 'CRUISE'
    AVOID = 'AVOID'
    EMERGENCY = 'EMERGENCY'
    TRACK = 'TRACK'
    INSPECT = 'INSPECT'


@dataclass
class BehaviorParams:
    """Tunable parameters; defaults mirror config/behavior.yaml."""

    # Contract parameters (docs/INTERFACES.md section 7)
    forward_speed: float = 0.25
    turn_speed: float = 0.8
    front_sector_deg: float = 30.0
    obstacle_distance: float = 0.55
    clear_distance: float = 0.8
    emergency_distance: float = 0.3
    turn_angle_deg: float = 60.0
    use_camera: bool = False
    inspect_area: float = 0.08
    inspect_duration: float = 3.0
    # Scan sectors
    side_sector_deg: float = 100.0
    # Body geometry relative to base_link (docs/INTERFACES.md section 4)
    lidar_offset_x: float = 0.22
    body_front_x: float = 0.345
    body_rear_x: float = -0.105
    chassis_half_width: float = 0.15
    body_half_width: float = 0.26
    side_margin: float = 0.05
    rotate_margin: float = 0.02
    rotate_sweep_deg: float = 90.0
    # Emergency back-up
    backup_speed: float = 0.1
    backup_duration: float = 1.5
    rear_clear_distance: float = 0.15
    # Input timeouts
    scan_timeout: float = 0.5
    imu_timeout: float = 0.3
    target_timeout: float = 0.5
    # Camera layer
    track_gain: float = 0.8
    track_speed: float = 0.12
    target_cooldown: float = 8.0
    # Corridor centering while cruising (0 disables it)
    centering_gain: float = 0.5
    centering_range: float = 1.0
    max_centering: float = 0.3

    @property
    def swept_radius(self) -> float:
        """Distance from base_link to the farthest body point (in-place turn circle)."""
        return max(math.hypot(self.body_front_x, self.chassis_half_width),
                   math.hypot(self.body_rear_x, self.chassis_half_width),
                   self.body_half_width)


@dataclass(frozen=True)
class ScanData:
    """The LaserScan fields the logic needs."""

    ranges: Sequence[float]
    angle_min: float
    angle_increment: float
    range_min: float
    range_max: float
    stamp: float


@dataclass(frozen=True)
class ScanSummary:
    """Scan reduced to the distances the state machine decides on [m]."""

    stamp: float
    front_min: float          # lidar range: front sector or body corridor ahead
    left_mean: float          # mean lidar range, left side sector
    right_mean: float
    left_min: float
    right_min: float
    rear_gap: float           # gap between chassis rear and nearest point behind
    rotate_clear_left: float  # clearance of a counter-clockwise in-place turn
    rotate_clear_right: float


@dataclass(frozen=True)
class Target:
    """Last /camera/target message."""

    stamp: float
    offset: float  # horizontal offset [-1, 1], left negative
    area: float    # image area ratio [0, 1]


@dataclass(frozen=True)
class Command:
    """Velocity command and state for one control tick."""

    linear: float
    angular: float
    state: State
    reason: str = ''  # non-empty when the state changed during this tick


def _wrap(angle: float) -> float:
    return math.atan2(math.sin(angle), math.cos(angle))


def _clamp(value: float, limit: float) -> float:
    return max(-limit, min(limit, value))


def clean_range(value: float, range_min: float, range_max: float) -> Optional[float]:
    """Return a usable range, `range_max` for "no return", or None to drop it."""
    if math.isnan(value) or value < range_min:  # also drops -inf
        return None
    return min(value, range_max)  # +inf means nothing within range


def _inside_body(x: float, y: float, p: BehaviorParams) -> bool:
    return p.body_rear_x <= x <= p.body_front_x and abs(y) <= p.body_half_width


def analyze_scan(scan: ScanData, p: BehaviorParams) -> ScanSummary:
    """Reduce a scan to front/side/rear distances and in-place turn clearances."""
    front_half = math.radians(p.front_sector_deg)
    side_limit = math.radians(p.side_sector_deg)
    corridor_half = p.body_half_width + p.side_margin
    corner = math.atan2(p.chassis_half_width, p.body_front_x)
    sweep = math.radians(p.rotate_sweep_deg)
    swept = p.swept_radius
    far = scan.range_max

    front_min = rear_gap = far
    rot_left = rot_right = far
    left: List[float] = []
    right: List[float] = []

    for i, raw in enumerate(scan.ranges):
        r = clean_range(raw, scan.range_min, scan.range_max)
        if r is None:
            continue
        theta = _wrap(scan.angle_min + i * scan.angle_increment)
        x = p.lidar_offset_x + r * math.cos(theta)
        y = r * math.sin(theta)
        if _inside_body(x, y, p):
            continue  # self-detection

        ahead = x > p.body_front_x and abs(y) <= corridor_half
        if abs(theta) <= front_half or ahead:
            front_min = min(front_min, r)
        if front_half < theta <= side_limit:
            left.append(r)
        elif -side_limit <= theta < -front_half:
            right.append(r)
        if x < p.body_rear_x and abs(y) <= corridor_half:
            rear_gap = min(rear_gap, p.body_rear_x - x)

        if r >= far:
            continue  # free ray, no obstacle point
        # A turn sweeps the front corners over `swept`; elsewhere only the
        # wheels and rear corners move, all within body_half_width.
        dist = math.hypot(x, y)
        bearing = math.atan2(y, x)
        inner = dist - p.body_half_width
        outer = dist - swept
        rot_left = min(rot_left, outer if -corner <= bearing <= corner + sweep else inner)
        rot_right = min(rot_right, outer if -corner - sweep <= bearing <= corner else inner)

    return ScanSummary(
        stamp=scan.stamp,
        front_min=front_min,
        left_mean=sum(left) / len(left) if left else far,
        right_mean=sum(right) / len(right) if right else far,
        left_min=min(left, default=far),
        right_min=min(right, default=far),
        rear_gap=rear_gap,
        rotate_clear_left=rot_left,
        rotate_clear_right=rot_right,
    )


class YawIntegrator:
    """Integrates IMU yaw rate over message timestamps (unwrapped yaw)."""

    def __init__(self, max_gap: float) -> None:
        self.max_gap = max_gap
        self.yaw = 0.0
        self.last_stamp: Optional[float] = None

    def add(self, stamp: float, yaw_rate: float) -> None:
        if self.last_stamp is not None:
            dt = stamp - self.last_stamp
            if dt <= 0.0:
                return  # duplicate or out-of-order sample
            if dt <= self.max_gap:  # skip integration across dropouts
                self.yaw += yaw_rate * dt
        self.last_stamp = stamp

    def is_fresh(self, now: float, timeout: float) -> bool:
        return self.last_stamp is not None and now - self.last_stamp <= timeout


class BehaviorStateMachine:
    """CRUISE / AVOID / EMERGENCY core with an optional TRACK / INSPECT layer.

    Call `on_imu` and `on_target` as messages arrive and `update` at the
    control rate with the latest `ScanSummary`.
    """

    def __init__(self, params: BehaviorParams) -> None:
        self.p = params
        self.state = State.WAIT
        self.imu = YawIntegrator(params.imu_timeout)
        self.turn_source = ''  # 'imu' or 'time', how the last turn was measured
        self._target: Optional[Target] = None
        self._since = 0.0
        self._reasons: List[str] = []
        self._direction = 1
        self._turned = 0.0
        self._turn_prev_time = 0.0
        self._turn_prev_yaw = 0.0
        self._cooldown_until = -math.inf

    # -- inputs -------------------------------------------------------------

    def on_imu(self, stamp: float, yaw_rate: float) -> None:
        self.imu.add(stamp, yaw_rate)

    def on_target(self, stamp: float, offset: float, area: float) -> None:
        self._target = Target(stamp, offset, area)

    @property
    def turned_deg(self) -> float:
        """Angle turned in the current or last AVOID, degrees."""
        return math.degrees(self._turned)

    # -- main step ----------------------------------------------------------

    def update(self, now: float, scan: Optional[ScanSummary]) -> Command:
        """Advance one control tick and return the command to publish."""
        self._reasons = []
        if scan is None or now - scan.stamp > self.p.scan_timeout:
            if self.state != State.WAIT:
                self._enter(State.WAIT, now, 'no recent /scan')
            return self._command(0.0, 0.0)
        handler = {
            State.WAIT: self._wait,
            State.CRUISE: self._cruise,
            State.AVOID: self._avoid,
            State.EMERGENCY: self._emergency,
            State.TRACK: self._track,
            State.INSPECT: self._inspect,
        }[self.state]
        return handler(now, scan)

    # -- state handlers -----------------------------------------------------

    def _wait(self, now: float, scan: ScanSummary) -> Command:
        self._enter(State.CRUISE, now, 'scan received')
        return self._cruise(now, scan)

    def _cruise(self, now: float, scan: ScanSummary) -> Command:
        p = self.p
        if scan.front_min < p.emergency_distance:
            return self._start_emergency(
                now, scan, f'front {scan.front_min:.2f} m < {p.emergency_distance} m')
        if scan.front_min < p.obstacle_distance:
            return self._start_avoid(
                now, scan, f'front {scan.front_min:.2f} m < {p.obstacle_distance} m')
        if self._target_ready(now):
            self._enter(State.TRACK, now, 'target seen')
            return self._track(now, scan)
        return self._command(p.forward_speed, self._centering(scan))

    def _avoid(self, now: float, scan: ScanSummary) -> Command:
        p = self.p
        self._measure_turn(now)
        clearance = scan.rotate_clear_left if self._direction > 0 else scan.rotate_clear_right
        if clearance < p.rotate_margin:
            return self._start_emergency(now, scan, 'no room to keep turning')
        if (self._turned >= math.radians(p.turn_angle_deg)
                and scan.front_min > p.clear_distance):
            self._enter(State.CRUISE, now,
                        f'turned {self.turned_deg:.0f} deg ({self.turn_source}), '
                        f'front {scan.front_min:.2f} m')
            return self._cruise(now, scan)
        return self._command(0.0, self._direction * p.turn_speed)

    def _emergency(self, now: float, scan: ScanSummary) -> Command:
        p = self.p
        if now - self._since >= p.backup_duration:
            return self._start_avoid(now, scan, 'back-up finished')
        linear = -p.backup_speed if scan.rear_gap > p.rear_clear_distance else 0.0
        return self._command(linear, 0.0)

    def _track(self, now: float, scan: ScanSummary) -> Command:
        p = self.p
        if scan.front_min < p.emergency_distance:
            return self._start_emergency(
                now, scan, f'front {scan.front_min:.2f} m < {p.emergency_distance} m')
        if not self._target_ready(now):
            self._enter(State.CRUISE, now, 'target lost')
            return self._cruise(now, scan)
        target = self._target
        assert target is not None
        if target.area >= p.inspect_area:
            self._enter(State.INSPECT, now, f'target area {target.area:.3f}')
            return self._command(0.0, 0.0)
        if scan.front_min < p.obstacle_distance:
            # The target sits on a plant bed; reaching the bed means arrival.
            self._enter(State.INSPECT, now, f'bed reached, front {scan.front_min:.2f} m')
            return self._command(0.0, 0.0)
        # offset < 0 (left) -> positive angular.z (turn left)
        return self._command(p.track_speed, _clamp(-p.track_gain * target.offset, p.turn_speed))

    def _inspect(self, now: float, scan: ScanSummary) -> Command:
        if now - self._since >= self.p.inspect_duration:
            self._cooldown_until = now + self.p.target_cooldown
            return self._start_avoid(now, scan, 'inspection done')
        return self._command(0.0, 0.0)

    # -- helpers ------------------------------------------------------------

    def _start_avoid(self, now: float, scan: ScanSummary, reason: str) -> Command:
        """Pick the more open side that has room to turn; else back up."""
        p = self.p
        can_left = scan.rotate_clear_left >= p.rotate_margin
        can_right = scan.rotate_clear_right >= p.rotate_margin
        if not (can_left or can_right):
            return self._start_emergency(now, scan, reason + '; no room to turn')
        if can_left and can_right:
            self._direction = 1 if scan.left_mean >= scan.right_mean else -1
        else:
            self._direction = 1 if can_left else -1
        side = 'left' if self._direction > 0 else 'right'
        self._enter(State.AVOID, now, f'{reason}; turning {side}')
        self._turned = 0.0
        self._turn_prev_time = now
        self._turn_prev_yaw = self.imu.yaw
        return self._command(0.0, self._direction * p.turn_speed)

    def _start_emergency(self, now: float, scan: ScanSummary, reason: str) -> Command:
        self._enter(State.EMERGENCY, now, reason)
        return self._emergency(now, scan)

    def _measure_turn(self, now: float) -> None:
        """Accumulate the turned angle: IMU when fresh, otherwise turn_speed * dt."""
        yaw = self.imu.yaw
        if self.imu.is_fresh(now, self.p.imu_timeout):
            self._turned += self._direction * (yaw - self._turn_prev_yaw)
            self.turn_source = 'imu'
        else:
            self._turned += self.p.turn_speed * (now - self._turn_prev_time)
            self.turn_source = 'time'
        self._turn_prev_time = now
        self._turn_prev_yaw = yaw

    def _target_ready(self, now: float) -> bool:
        t = self._target
        return (self.p.use_camera and t is not None
                and now - t.stamp <= self.p.target_timeout
                and now >= self._cooldown_until)

    def _centering(self, scan: ScanSummary) -> float:
        p = self.p
        if p.centering_gain == 0.0:
            return 0.0
        left = min(scan.left_min, p.centering_range)
        right = min(scan.right_min, p.centering_range)
        return _clamp(p.centering_gain * (left - right), p.max_centering)

    def _enter(self, state: State, now: float, reason: str) -> None:
        self._reasons.append(f'{self.state.value} -> {state.value}: {reason}')
        self.state = state
        self._since = now

    def _command(self, linear: float, angular: float) -> Command:
        return Command(linear, angular, self.state, '; '.join(self._reasons))
