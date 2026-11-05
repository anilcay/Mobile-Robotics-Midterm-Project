# SeraBot — Greenhouse Inspection Mobile Robot

[![CI](https://github.com/anilcay/Mobile-Robotics-Midterm-Project/actions/workflows/ci.yml/badge.svg)](https://github.com/anilcay/Mobile-Robotics-Midterm-Project/actions/workflows/ci.yml)

BIMU4101 – Introduction to Mobile Robotics, Midterm Project.

SeraBot is an original differential-drive mobile robot that patrols the aisles of a greenhouse. It avoids walls, plant beds and pots with a 2D LiDAR, measures its turns with an IMU and finds ripe (red) tomatoes with an RGB camera: it steers to a truss, stops to "inspect" it and then resumes its patrol. The robot is modelled in URDF/Xacro, simulated in Gazebo and controlled through ROS 2.

## Team

| Member | Student ID | Responsibility |
|---|---|---|
| Ahmet Anıl Çay ([anilcay](https://github.com/anilcay)) | 1306220017 | LiDAR (integration, data, RViz), IMU integration, robot model, greenhouse world, behavior node |
| Enes Çelik ([enescelik00](https://github.com/enescelik00)) | 1306220032 | Camera (integration, red detector, image views), IMU visualization (`imu_monitor`, plot), camera-layer behavior and demo tuning |

## Environment

- Ubuntu 26.04
- ROS 2 Lyrical
- Gazebo Jetty (gz-sim 10, via `ros_gz`)

Tested on native Ubuntu 26.04 under WSL2 (Windows 11) and in the Docker image under `docker/` (see [Docker](#option-b-docker)).

## Packages

| Package | Contents |
|---|---|
| `serabot_description` | Robot model: URDF/Xacro, Blender meshes (`.obj`), model viewer launch |
| `serabot_gazebo` | Greenhouse world (primitive collision geometry + Blender decorations) |
| `serabot_bringup` | Single launch file, ROS–Gazebo bridge configs, node parameters, RViz config |
| `serabot_sensors` | `color_detector` (camera, red produce) and `imu_monitor` (IMU roll/pitch/yaw) |
| `serabot_behavior` | `behavior_node`: obstacle avoidance + camera target tracking state machine |

## Installation

### Option A: native Ubuntu 26.04 (also WSL2)

1. ROS 2 Lyrical apt repository and packages:

   ```bash
   sudo apt update && sudo apt install -y software-properties-common curl
   sudo add-apt-repository -y universe
   export ROS_APT_SOURCE_VERSION=$(curl -s https://api.github.com/repos/ros-infrastructure/ros-apt-source/releases/latest | grep -F '"tag_name"' | awk -F'"' '{print $4}')
   curl -L -o /tmp/ros2-apt-source.deb "https://github.com/ros-infrastructure/ros-apt-source/releases/download/${ROS_APT_SOURCE_VERSION}/ros2-apt-source_${ROS_APT_SOURCE_VERSION}.$(. /etc/os-release && echo ${UBUNTU_CODENAME:-${VERSION_CODENAME}})_all.deb"
   sudo dpkg -i /tmp/ros2-apt-source.deb
   sudo apt update && sudo apt upgrade -y
   sudo apt install -y ros-lyrical-desktop ros-dev-tools ros-lyrical-ros-gz \
       ros-lyrical-xacro ros-lyrical-robot-state-publisher ros-lyrical-joint-state-publisher-gui \
       ros-lyrical-teleop-twist-keyboard ros-lyrical-rqt-image-view ros-lyrical-rqt-plot \
       ros-lyrical-cv-bridge ros-lyrical-ament-flake8 python3-opencv python3-pytest \
       python3-yaml liburdfdom-tools
   sudo rosdep init && rosdep update
   ```

2. Clone and build (the repository root is the colcon workspace):

   ```bash
   git clone https://github.com/anilcay/Mobile-Robotics-Midterm-Project.git serabot_ws
   cd serabot_ws
   source /opt/ros/lyrical/setup.bash
   rosdep install --from-paths src --ignore-src -y
   colcon build
   source install/setup.bash
   ```

   Add `source /opt/ros/lyrical/setup.bash` and `source <path>/serabot_ws/install/setup.bash` to `~/.bashrc` so every new terminal has them.

3. **WSL2 only** (Windows 11; `wsl --install -d Ubuntu-26.04`): add to `~/.bashrc`

   ```bash
   export GALLIUM_DRIVER=d3d12                    # OpenGL on the GPU instead of llvmpipe
   export MESA_D3D12_DEFAULT_ADAPTER_NAME=NVIDIA  # pick the discrete GPU, if any
   export QT_QPA_PLATFORM=xcb                     # RViz needs X11, not Wayland
   ```

### Option B: Docker

For a Linux host without Ubuntu 26.04 (X11 desktop required for the GUIs):

```bash
docker/run.sh build                   # build the image (once)
docker/run.sh exec "colcon build"     # build the workspace inside the container
docker/run.sh shell                   # shell with ROS and the workspace sourced
```

Details: [docs/DEV_ENVIRONMENT.md](docs/DEV_ENVIRONMENT.md).

## Usage

Everything starts from one launch file: the greenhouse world, the robot, the ROS–Gazebo bridges, the sensor nodes and RViz.

```bash
# Robot waits for commands (drive it yourself)
ros2 launch serabot_bringup bringup.launch.py

# Autonomous obstacle avoidance (LiDAR + IMU)
ros2 launch serabot_bringup bringup.launch.py behavior:=true

# Full demo: patrol + steer to red tomatoes, inspect, resume (LiDAR + IMU + camera)
ros2 launch serabot_bringup bringup.launch.py behavior:=true use_camera:=true
```

Gazebo and RViz take 10–20 s to open. Stop everything with `Ctrl+C`.

| Argument | Default | Description |
|---|---|---|
| `behavior` | `false` | Start `behavior_node` (autonomous driving) |
| `use_camera` | `false` | Camera layer of the behavior (TRACK / INSPECT red produce); needs `behavior:=true` |
| `sensors` | `true` | Start `color_detector` and `imu_monitor` |
| `rviz` | `true` | Open RViz |
| `headless` | `false` | Gazebo without its window (faster); RViz stays the viewer |
| `world` | `greenhouse.sdf` | World file in `serabot_gazebo/worlds` (`greenhouse_primitive.sdf`: plain fallback) |
| `x`, `y`, `yaw` | `-4.0`, `0.875`, `0.0` | Spawn pose (west end of the north-middle aisle) |

### Drive manually

In a second terminal (with `behavior:=false`); keys work while this terminal has focus: `i` forward, `,` back, `j`/`l` turn, `k` stop.

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

### Sensor data and visualization

RViz shows the robot model, odometry, the LiDAR scan and two image panels (raw camera, red detection). Other views:

```bash
ros2 run rqt_image_view rqt_image_view /camera/image_annotated     # detection boxes
ros2 run rqt_plot rqt_plot /imu/rpy/vector/z /imu/angular_velocity/z  # IMU yaw and yaw rate
ros2 topic echo /behavior/state                                    # current behavior state
ros2 topic echo /camera/target                                     # x = offset, y = area
ros2 topic hz /scan                                                # sensor rates (wall clock)
```

| Sensor | Topic | Message type | Rate (sim time) | Frame |
|---|---|---|---|---|
| 2D LiDAR | `/scan` | `sensor_msgs/msg/LaserScan` | 10 Hz, 360 samples, 0.25–8 m | `lidar_link` |
| RGB camera | `/camera/image_raw`, `/camera/camera_info` | `sensor_msgs/msg/Image`, `CameraInfo` | 15 Hz, 640×480, 60° HFOV | `camera_optical_link` |
| IMU | `/imu` | `sensor_msgs/msg/Imu` | 100 Hz | `imu_link` |

| Node | Subscribes | Publishes |
|---|---|---|
| `color_detector` | `/camera/image_raw` | `/camera/target` (`geometry_msgs/msg/PointStamped`), `/camera/image_annotated` |
| `imu_monitor` | `/imu` | `/imu/rpy` (`geometry_msgs/msg/Vector3Stamped`, degrees) |
| `behavior_node` | `/scan`, `/imu`, `/camera/target` | `/cmd_vel` (`geometry_msgs/msg/Twist`), `/behavior/state` (`std_msgs/msg/String`) |

## Behavior

`behavior_node` runs a state machine at 10 Hz (simulation time):

- **CRUISE** — drive forward at 0.25 m/s, keep to the middle of the aisle.
- **AVOID** — obstacle closer than 0.55 m ahead: turn in place towards the open side that has room for the turning body; the turned angle is measured with the IMU.
- **EMERGENCY** — closer than 0.3 m: stop and back up briefly.
- **TRACK** (`use_camera:=true`) — a red target is seen: steer to it (`angular.z = -0.8 · offset`) at 0.12 m/s.
- **INSPECT** — the plant bed is reached: stop for 3 s, then turn back to the patrol heading and ignore targets for 20 s.
- **WAIT** — no recent LiDAR scan: stop.

Decision rule and parameters: [docs/modules/behavior.md](docs/modules/behavior.md), [docs/INTERFACES.md](docs/INTERFACES.md) section 7.

## Tests

```bash
colcon build && colcon test && colcon test-result --verbose   # unit tests + flake8 (Linux)
python3 -m pytest src/serabot_behavior/test                    # pure logic, also without ROS
```

Simulation measurement scripts (rates, frames, IMU turn plot, camera-layer runs with Gazebo ground truth): [scripts/sim/](scripts/sim/). Results and report figures: [docs/report/](docs/report/).

## Documentation

| Document | Contents |
|---|---|
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Scenario, packages, data flow, TF tree |
| [docs/INTERFACES.md](docs/INTERFACES.md) | Topics, frames, dimensions, launch arguments, parameters |
| [docs/DECISIONS.md](docs/DECISIONS.md) | Design decisions (ADRs) |
| [docs/modules/](docs/modules/) | Per-module tasks and verification results |
