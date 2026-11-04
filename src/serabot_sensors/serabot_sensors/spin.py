"""Shared spin helper for the SeraBot sensor nodes.

With use_sim_time every node follows /clock, which Gazebo publishes at the physics
rate (~1 kHz). The default rclpy executor handles each message in Python and an
otherwise idle node then uses about half a CPU core, so camera frames get dropped.
rclpy's EventsExecutor does that work in C++ (about half the CPU, measured in the
SeraBot simulation); the default executor remains as a fallback.
"""

import rclpy
from rclpy.executors import Executor, ExternalShutdownException, SingleThreadedExecutor
from rclpy.node import Node


def make_executor() -> Executor:
    """EventsExecutor when this rclpy provides it, else SingleThreadedExecutor."""
    try:
        from rclpy.experimental import EventsExecutor
    except ImportError:
        return SingleThreadedExecutor()
    return EventsExecutor()


def spin_node(node: Node) -> None:
    """Spin until Ctrl-C, then destroy the node and shut rclpy down."""
    executor = make_executor()
    executor.add_node(node)
    node.get_logger().info(f'executor: {type(executor).__name__}')
    try:
        executor.spin()
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        executor.shutdown()
        node.destroy_node()
        rclpy.try_shutdown()
