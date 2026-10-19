"""Stop the rover when velocity commands stop arriving.

Subscribes to `cmd_vel` and republishes on `cmd_vel_safe` at a fixed rate. If no command
has arrived within `timeout` seconds, zero velocity is published instead.
"""

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node


class WatchdogLogic:
    """Time-source-agnostic core, kept separate so it can be unit-tested without ROS."""

    def __init__(self, timeout):
        self.timeout = timeout
        self._last_cmd = Twist()
        self._last_time = None

    def on_command(self, msg, now):
        self._last_cmd = msg
        self._last_time = now

    def output(self, now):
        if self._last_time is None or (now - self._last_time) > self.timeout:
            return Twist()
        return self._last_cmd


class CmdVelWatchdog(Node):
    def __init__(self):
        super().__init__("cmd_vel_watchdog")
        self.declare_parameter("timeout", 0.5)
        self.declare_parameter("publish_rate", 20.0)
        self._logic = WatchdogLogic(self.get_parameter("timeout").value)
        self._pub = self.create_publisher(Twist, "cmd_vel_safe", 10)
        self.create_subscription(Twist, "cmd_vel", self._on_cmd, 10)
        period = 1.0 / self.get_parameter("publish_rate").value
        self.create_timer(period, self._tick)

    def _now(self):
        return self.get_clock().now().nanoseconds * 1e-9

    def _on_cmd(self, msg):
        self._logic.on_command(msg, self._now())

    def _tick(self):
        self._pub.publish(self._logic.output(self._now()))


def main(args=None):
    rclpy.init(args=args)
    node = CmdVelWatchdog()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == "__main__":
    main()
