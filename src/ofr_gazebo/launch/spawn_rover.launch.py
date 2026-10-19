#!/usr/bin/env python3

import os
import subprocess
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    ofr_description_dir = get_package_share_directory("ofr_description")
    ofr_gazebo_dir = get_package_share_directory("ofr_gazebo")

    use_sim_time = LaunchConfiguration("use_sim_time", default="true")
    world_file = os.path.join(ofr_gazebo_dir, "worlds", "open_field.sdf")
    urdf_xacro = os.path.join(ofr_description_dir, "urdf", "rover.urdf.xacro")

    # Process xacro to URDF
    try:
        result = subprocess.run(["xacro", urdf_xacro], capture_output=True, text=True, check=True)
        robot_desc = result.stdout
    except Exception as e:
        print(f"Error processing xacro: {e}")
        robot_desc = ""

    ld = LaunchDescription(
        [
            DeclareLaunchArgument(
                "use_sim_time",
                default_value="true",
                description="Use simulation (Gazebo) clock if true",
            ),
            # Gazebo server (headless)
            ExecuteProcess(
                cmd=["gz", "sim", "-r", "-s", "--headless-rendering", world_file], output="screen"
            ),
            # Spawn rover into Gazebo
            Node(
                package="ros_gz_sim",
                executable="create",
                arguments=[
                    "-name",
                    "rover",
                    "-topic",
                    "robot_description",
                    "-x",
                    "0.0",
                    "-y",
                    "0.0",
                    "-z",
                    "0.2",
                ],
                output="screen",
            ),
            # Robot state publisher
            Node(
                package="robot_state_publisher",
                executable="robot_state_publisher",
                output="screen",
                parameters=[{"robot_description": robot_desc}, {"use_sim_time": use_sim_time}],
            ),
            # Joint state publisher
            Node(
                package="joint_state_publisher",
                executable="joint_state_publisher",
                output="screen",
                parameters=[{"use_sim_time": use_sim_time}],
            ),
            # ROS-Gazebo bridge: map Gazebo topics to ROS 2
            Node(
                package="ros_gz_bridge",
                executable="parameter_bridge",
                arguments=[
                    "/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist",
                    "/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry",
                    "/imu/data@sensor_msgs/msg/Imu[gz.msgs.IMU",
                    "/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan",
                    "/gps/fix@sensor_msgs/msg/NavSatFix[gz.msgs.NavSat",
                ],
                output="screen",
            ),
        ]
    )

    return ld


if __name__ == "__main__":
    print(generate_launch_description())
