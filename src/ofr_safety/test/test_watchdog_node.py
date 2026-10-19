import time

import pytest
import rclpy
from geometry_msgs.msg import Twist
from rclpy.executors import SingleThreadedExecutor

from ofr_safety.cmd_vel_watchdog import CmdVelWatchdog


@pytest.fixture
def ros():
    rclpy.init()
    yield
    rclpy.try_shutdown()


def test_node_publishes_zero_after_commands_stop(ros):
    watchdog = CmdVelWatchdog()
    probe = rclpy.create_node("watchdog_probe")
    received = []
    probe.create_subscription(Twist, "cmd_vel_safe", received.append, 10)
    pub = probe.create_publisher(Twist, "cmd_vel", 10)

    executor = SingleThreadedExecutor()
    executor.add_node(watchdog)
    executor.add_node(probe)

    def spin_for(seconds, publish=False):
        end = time.monotonic() + seconds
        while time.monotonic() < end:
            if publish:
                cmd = Twist()
                cmd.linear.x = 0.5
                pub.publish(cmd)
            executor.spin_once(timeout_sec=0.02)

    spin_for(0.6, publish=True)
    assert any(m.linear.x == 0.5 for m in received)

    received.clear()
    spin_for(1.0)
    assert received and received[-1].linear.x == 0.0

    watchdog.destroy_node()
    probe.destroy_node()
