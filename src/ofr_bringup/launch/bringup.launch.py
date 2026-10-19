#!/usr/bin/env python3

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():
    ofr_gazebo_dir = get_package_share_directory("ofr_gazebo")

    spawn_rover = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(ofr_gazebo_dir, "launch", "spawn_rover.launch.py")
        )
    )

    ld = LaunchDescription(
        [
            spawn_rover,
        ]
    )

    return ld


if __name__ == "__main__":
    print(generate_launch_description())
