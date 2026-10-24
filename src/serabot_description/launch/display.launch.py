"""Show the SeraBot model in RViz without Gazebo.

Starts robot_state_publisher, joint_state_publisher_gui (to turn the wheels) and
RViz with rviz/model.rviz. Without Gazebo there is no /clock, so use_sim_time
defaults to false here; simulation launch files keep use_sim_time true.
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import Command, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare


def generate_launch_description() -> LaunchDescription:
    pkg_share = FindPackageShare('serabot_description')
    use_sim_time = LaunchConfiguration('use_sim_time')

    robot_description = ParameterValue(
        Command([
            'xacro ', PathJoinSubstitution([pkg_share, 'urdf', LaunchConfiguration('model')]),
            ' use_lidar:=', LaunchConfiguration('use_lidar'),
            ' use_camera:=', LaunchConfiguration('use_camera'),
            ' use_imu:=', LaunchConfiguration('use_imu'),
        ]),
        value_type=str,
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'model', default_value='serabot.urdf.xacro',
            description='Xacro file under urdf/, e.g. test/mesh_test.urdf.xacro'),
        DeclareLaunchArgument(
            'use_sim_time', default_value='false',
            description='Use /clock time (only when a simulator is running)'),
        DeclareLaunchArgument(
            'rviz', default_value='true', description='Start RViz'),
        DeclareLaunchArgument(
            'use_lidar', default_value='true', description='Include the LiDAR in the model'),
        DeclareLaunchArgument(
            'use_camera', default_value='true', description='Include the camera in the model'),
        DeclareLaunchArgument(
            'use_imu', default_value='true', description='Include the IMU in the model'),

        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            parameters=[{
                'robot_description': robot_description,
                'use_sim_time': use_sim_time,
            }],
            output='screen',
        ),
        Node(
            package='joint_state_publisher_gui',
            executable='joint_state_publisher_gui',
            parameters=[{'use_sim_time': use_sim_time}],
        ),
        Node(
            package='rviz2',
            executable='rviz2',
            arguments=['-d', PathJoinSubstitution([pkg_share, 'rviz', 'model.rviz'])],
            parameters=[{'use_sim_time': use_sim_time}],
            condition=IfCondition(LaunchConfiguration('rviz')),
        ),
    ])
