# SeraBot — Greenhouse Inspection Mobile Robot

[![CI](https://github.com/anilcay/Mobile-Robotics-Midterm-Project/actions/workflows/ci.yml/badge.svg)](https://github.com/anilcay/Mobile-Robotics-Midterm-Project/actions/workflows/ci.yml)

BIMU4101 – Introduction to Mobile Robotics, Midterm Project.

SeraBot is an original differential-drive mobile robot that patrols the aisles of a greenhouse, avoids obstacles with a 2D LiDAR, measures its turns with an IMU and detects ripe (red) produce with an RGB camera. It is modelled in URDF/Xacro, simulated in Gazebo and controlled through ROS 2.

> **Status:** Work in progress. Installation and run instructions will be completed as the packages are implemented.

## Team

| Member | Student ID | Responsibility |
|---|---|---|
| Member A (anilcay) | TBD | LiDAR (sensor A), IMU integration |
| Member B | TBD | Camera (sensor B), IMU visualization |

## Environment

- Ubuntu 26.04
- ROS 2 Lyrical
- Gazebo Jetty

## Packages

| Package | Description |
|---|---|
| `serabot_description` | Robot model (URDF/Xacro) |
| `serabot_gazebo` | Greenhouse world |
| `serabot_bringup` | Single launch file, ROS–Gazebo bridge config, RViz config |
| `serabot_sensors` | Sensor helper nodes (color detector, IMU monitor) |
| `serabot_behavior` | Sensor-based behavior node (obstacle avoidance, target tracking) |

## Installation

_TBD_

## Usage

_TBD_ — planned single command:

```bash
ros2 launch serabot_bringup bringup.launch.py
```
