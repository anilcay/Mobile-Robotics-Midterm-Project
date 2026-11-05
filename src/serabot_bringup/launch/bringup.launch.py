"""Single entry point: greenhouse world, SeraBot, ROS-Gazebo bridges and RViz.

Steps (docs/ARCHITECTURE.md section 5, arguments in docs/INTERFACES.md section 6):
1. Gazebo with serabot_gazebo/worlds/<world> (server only with headless:=true).
2. robot_state_publisher with the default xacro (RViz mesh colours).
3. Spawn from a separate xacro run with gazebo_mesh_colors:=true (ADR-019).
4. One parameter_bridge per non-empty config/bridge/*.yaml.
5. RViz with rviz/serabot.rviz.
6. Optional helper nodes; nodes whose module is not written yet are skipped
   with a log message instead of crashing the launch. Each node gets its
   config/<file>.yaml (NODE_CONFIGS); use_camera overrides behavior.yaml.
"""

import importlib.util
import os
from pathlib import Path
import tempfile
from typing import List

from ament_index_python.packages import get_package_share_directory
from launch import LaunchContext, LaunchDescription
from launch.actions import (DeclareLaunchArgument, IncludeLaunchDescription, LogInfo,
                            OpaqueFunction)
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import (Command, LaunchConfiguration, PathJoinSubstitution,
                                  PythonExpression)
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare
import xacro
import yaml

ROBOT_NAME = 'serabot'
SIM_TIME = {'use_sim_time': True}
# Parameter file under serabot_bringup/config for each helper node.
NODE_CONFIGS = {'behavior_node': 'behavior.yaml', 'color_detector': 'color_detector.yaml'}


def _is_true(context: LaunchContext, name: str) -> bool:
    return LaunchConfiguration(name).perform(context).lower() == 'true'


def _xacro_path() -> str:
    return os.path.join(get_package_share_directory('serabot_description'),
                        'urdf', 'serabot.urdf.xacro')


def _spawn(context: LaunchContext) -> List:
    """Write the Gazebo-colour URDF to a temp file and spawn it from there."""
    urdf = xacro.process_file(_xacro_path(),
                              mappings={'gazebo_mesh_colors': 'true'}).toxml()
    with tempfile.NamedTemporaryFile('w', prefix='serabot_gazebo_', suffix='.urdf',
                                     delete=False) as f:
        f.write(urdf)
    return [Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-name', ROBOT_NAME,
            '-file', f.name,
            '-x', LaunchConfiguration('x').perform(context),
            '-y', LaunchConfiguration('y').perform(context),
            '-Y', LaunchConfiguration('yaw').perform(context),
        ],
        parameters=[SIM_TIME],
        output='screen',
    )]


def _bridges(context: LaunchContext) -> List:
    """One parameter_bridge per bridge yaml, so sensor owners stay independent."""
    bridge_dir = Path(get_package_share_directory('serabot_bringup')) / 'config' / 'bridge'
    actions: List = []
    for path in sorted(bridge_dir.glob('*.yaml')):
        entries = yaml.safe_load(path.read_text(encoding='utf-8'))
        if not entries:
            actions.append(LogInfo(msg=f'[bringup] {path.name} is empty, no bridge started'))
            continue
        actions.append(Node(
            package='ros_gz_bridge',
            executable='parameter_bridge',
            name=f'bridge_{path.stem}',
            parameters=[{'config_file': str(path)}, SIM_TIME],
            output='screen',
        ))
    return actions


def _module_ready(module: str) -> bool:
    try:
        return importlib.util.find_spec(module) is not None
    except ModuleNotFoundError:
        return False


def _helper_nodes(context: LaunchContext) -> List:
    """Start behavior/sensor helper nodes only if their module exists."""
    wanted = []
    if _is_true(context, 'sensors'):
        wanted += [('serabot_sensors', 'color_detector'), ('serabot_sensors', 'imu_monitor')]
    if _is_true(context, 'behavior'):
        wanted.append(('serabot_behavior', 'behavior_node'))

    config_dir = os.path.join(get_package_share_directory('serabot_bringup'), 'config')
    use_camera = _is_true(context, 'use_camera')
    actions: List = []
    if use_camera and _is_true(context, 'behavior') and not _is_true(context, 'sensors'):
        actions.append(LogInfo(msg='[bringup] use_camera:=true needs sensors:=true '
                                   '(color_detector publishes /camera/target)'))
    for package, executable in wanted:
        if not _module_ready(f'{package}.{executable}'):
            actions.append(LogInfo(
                msg=f'[bringup] {package}/{executable} is not implemented yet, skipped'))
            continue
        params: List = []
        config = os.path.join(config_dir, NODE_CONFIGS.get(executable, ''))
        if executable in NODE_CONFIGS and os.path.isfile(config):
            params.append(config)
        if executable == 'behavior_node':
            params.append({'use_camera': use_camera})
        params.append(SIM_TIME)
        actions.append(Node(package=package, executable=executable,
                            parameters=params, output='screen'))
    return actions


def generate_launch_description() -> LaunchDescription:
    world_path = PathJoinSubstitution(
        [FindPackageShare('serabot_gazebo'), 'worlds', LaunchConfiguration('world')])
    server_only = PythonExpression(
        ["'-s ' if '", LaunchConfiguration('headless'), "'.lower() == 'true' else ''"])
    robot_description = ParameterValue(Command(['xacro ', _xacro_path()]), value_type=str)

    return LaunchDescription([
        DeclareLaunchArgument(
            'world', default_value='greenhouse.sdf',
            description='World file under serabot_gazebo/worlds'),
        DeclareLaunchArgument('rviz', default_value='true', description='Start RViz2'),
        DeclareLaunchArgument(
            'behavior', default_value='false', description='Start the behavior node'),
        DeclareLaunchArgument(
            'sensors', default_value='true',
            description='Start helper sensor nodes (color_detector, imu_monitor)'),
        DeclareLaunchArgument(
            'use_camera', default_value='false',
            description='Behavior camera layer: steer to and inspect red produce '
                        '(TRACK / INSPECT); needs behavior:=true and sensors:=true'),
        DeclareLaunchArgument(
            'headless', default_value='false',
            description='Run Gazebo without its GUI (server only); RViz stays the viewer'),
        # Default spawn: west turning area, at the entry of the y = +0.875 corridor.
        DeclareLaunchArgument('x', default_value='-4.0', description='Spawn x [m]'),
        DeclareLaunchArgument('y', default_value='0.875', description='Spawn y [m]'),
        DeclareLaunchArgument('yaw', default_value='0.0', description='Spawn yaw [rad]'),

        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(PathJoinSubstitution(
                [FindPackageShare('ros_gz_sim'), 'launch', 'gz_sim.launch.py'])),
            launch_arguments={'gz_args': ['-r ', server_only, world_path],
                              'on_exit_shutdown': 'true'}.items(),
        ),
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            parameters=[{'robot_description': robot_description}, SIM_TIME],
            output='screen',
        ),
        OpaqueFunction(function=_spawn),
        OpaqueFunction(function=_bridges),
        Node(
            package='rviz2',
            executable='rviz2',
            arguments=['-d', PathJoinSubstitution(
                [FindPackageShare('serabot_bringup'), 'rviz', 'serabot.rviz'])],
            parameters=[SIM_TIME],
            condition=IfCondition(LaunchConfiguration('rviz')),
        ),
        OpaqueFunction(function=_helper_nodes),
    ])
