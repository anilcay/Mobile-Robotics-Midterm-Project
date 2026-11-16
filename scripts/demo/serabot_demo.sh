#!/usr/bin/env bash
# Windows launcher helper. It does not build or modify the ROS workspace.
set -eo pipefail

mode="${1:-check}"
case "$mode" in
    check|robot|imu|states) ;;
    *) printf 'Usage: serabot_demo.sh {check|robot|imu|states}\n' >&2; exit 2 ;;
esac

repo_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"
fail() { printf '\nERROR: %s\n' "$*" >&2; exit 1; }

[[ -f /opt/ros/lyrical/setup.bash ]] || fail 'ROS 2 Lyrical setup was not found.'
[[ -f "$repo_root/install/setup.bash" ]] || fail 'install/setup.bash is missing. Use the already built SeraBot workspace.'
cd -- "$repo_root"
export GALLIUM_DRIVER=d3d12
export MESA_D3D12_DEFAULT_ADAPTER_NAME=NVIDIA
export QT_QPA_PLATFORM=xcb
# ROS setup scripts are not compatible with nounset, so set -u is intentionally absent.
source /opt/ros/lyrical/setup.bash
source "$repo_root/install/setup.bash"

for required in ros2 flock pgrep timeout awk; do
    command -v "$required" >/dev/null || fail "Required command is unavailable: $required"
done

robot_running() {
    pgrep -u "$UID" -f '/lib/serabot_behavior/behavior_node([[:space:]]|$)' >/dev/null
}
launch_running() {
    pgrep -u "$UID" -f '(^|/)ros2 launch serabot_bringup bringup[.]launch[.]py([[:space:]]|$)' >/dev/null
}
require_no_robot() {
    if robot_running || launch_running; then
        fail 'A SeraBot demo is already running. Stop it with Ctrl+C in its original terminal before starting another.'
    fi
}

if [[ "$mode" == check ]]; then
    ros2 pkg prefix serabot_bringup >/dev/null || fail 'serabot_bringup is not available in the sourced workspace.'
    ros2 pkg prefix rqt_plot >/dev/null || fail 'rqt_plot is not installed.'
    require_no_robot
    printf 'Ready: Ubuntu-26.04, ROS 2 Lyrical, SeraBot workspace and rqt_plot.\n'
    exit 0
fi

# Locks prevent two copies of this launcher from starting the same component.
lock_dir="${TMPDIR:-/tmp}/serabot-demo-${UID}"
(umask 077; mkdir -p -- "$lock_dir")
exec 9>"$lock_dir/$mode.lock"
flock -n 9 || fail "The launcher already has an active $mode component."

if [[ "$mode" == robot ]]; then
    require_no_robot
    printf 'SeraBot: starting Gazebo, RViz, sensor nodes and autonomous behavior.\n'
    printf 'Stop the robot by pressing Ctrl+C in this terminal.\n\n'
    exec ros2 launch serabot_bringup bringup.launch.py behavior:=true use_camera:=true
fi

printf 'Waiting for behavior_node (up to 90 seconds)...\n'
ready=false
for ((attempt = 0; attempt < 90; attempt++)); do
    if robot_running; then ready=true; break; fi
    sleep 1
done
[[ "$ready" == true ]] || fail 'behavior_node did not start. Check the Robot and RViz terminal.'

if [[ "$mode" == imu ]]; then
    printf 'Opening the IMU angular velocity plot, in rad/s.\n'
    exec ros2 run rqt_plot rqt_plot /imu/angular_velocity/z
fi

printf 'Behavior state changes only. Observation ends after one hour; Ctrl+C stops it sooner.\n'
# Unbuffered Python output keeps the filtered state display live.
export PYTHONUNBUFFERED=1
timeout 3600 ros2 topic echo /behavior/state --field data |
    awk '/^(WAIT|CRUISE|AVOID|EMERGENCY|TRACK|INSPECT)$/ && $0 != previous {
        print;
        fflush();
        previous = $0;
    }'
