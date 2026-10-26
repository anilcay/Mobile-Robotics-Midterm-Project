#!/usr/bin/env bash
# Manage the SeraBot development container (ROS 2 Lyrical + Gazebo Jetty).
#
#   docker/run.sh build          build the image
#   docker/run.sh start          start the container in the background
#   docker/run.sh shell          open an interactive shell in it
#   docker/run.sh exec <cmd...>  run a command with ROS and the workspace sourced
#   docker/run.sh stop           stop and remove the container
#
# The repository root is mounted at /ws and is the colcon workspace.
# GUI apps use the host X server (DISPLAY, default :0).
# Set SERABOT_SOFTWARE_GL=1 to force software rendering if Gazebo crashes.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
IMAGE="serabot-dev:lyrical"
NAME="serabot"

display="${DISPLAY:-:0}"
xauth="${XAUTHORITY:-}"
if [ -z "$xauth" ] || [ ! -f "$xauth" ]; then
    for candidate in "/run/user/$(id -u)/gdm/Xauthority" "$HOME/.Xauthority"; do
        if [ -f "$candidate" ]; then xauth="$candidate"; break; fi
    done
fi

running() {
    [ "$(docker inspect -f '{{.State.Running}}' "$NAME" 2>/dev/null)" = "true" ]
}

start() {
    if running; then return; fi
    docker rm -f "$NAME" >/dev/null 2>&1 || true
    local args=(
        --detach --name "$NAME" --init
        --network host --ipc host
        --volume "$REPO_ROOT:/ws"
        --volume /tmp/.X11-unix:/tmp/.X11-unix:ro
        --env DISPLAY="$display"
        --env QT_X11_NO_MITSHM=1
    )
    if [ -n "$xauth" ]; then
        args+=(--volume "$xauth:/tmp/.Xauthority:ro" --env XAUTHORITY=/tmp/.Xauthority)
    fi
    if [ -d /dev/dri ]; then
        args+=(--device /dev/dri)
    fi
    if [ "${SERABOT_SOFTWARE_GL:-0}" = "1" ]; then
        args+=(--env LIBGL_ALWAYS_SOFTWARE=1)
    fi
    docker run "${args[@]}" "$IMAGE" sleep infinity >/dev/null
    echo "Container '$NAME' started (workspace: $REPO_ROOT -> /ws)."
}

case "${1:-shell}" in
    build)
        docker build \
            --build-arg USER_UID="$(id -u)" --build-arg USER_GID="$(id -g)" \
            -t "$IMAGE" "$REPO_ROOT/docker"
        ;;
    start)
        start
        ;;
    shell)
        start
        docker exec -it "$NAME" bash
        ;;
    exec)
        shift
        start
        tty_flag=()
        if [ -t 0 ] && [ -t 1 ]; then tty_flag=(-it); fi
        docker exec "${tty_flag[@]}" "$NAME" bash -c \
            'source /opt/ros/$ROS_DISTRO/setup.bash
             [ -f /ws/install/setup.bash ] && source /ws/install/setup.bash
             eval "$*"' bash "$@"
        ;;
    stop)
        docker rm -f "$NAME" >/dev/null 2>&1 || true
        echo "Container '$NAME' removed."
        ;;
    *)
        sed -n '2,12p' "$0"
        exit 1
        ;;
esac
