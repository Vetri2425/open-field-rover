from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription(
        [Node(package="ofr_safety", executable="cmd_vel_watchdog", output="screen")]
    )
