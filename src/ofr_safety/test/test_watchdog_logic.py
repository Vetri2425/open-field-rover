from geometry_msgs.msg import Twist

from ofr_safety.cmd_vel_watchdog import WatchdogLogic


def _twist(x):
    msg = Twist()
    msg.linear.x = x
    return msg


def test_zero_before_any_command():
    assert WatchdogLogic(0.5).output(now=10.0).linear.x == 0.0


def test_forwards_fresh_command():
    logic = WatchdogLogic(0.5)
    logic.on_command(_twist(0.7), now=1.0)
    assert logic.output(now=1.4).linear.x == 0.7


def test_zero_after_timeout():
    logic = WatchdogLogic(0.5)
    logic.on_command(_twist(0.7), now=1.0)
    assert logic.output(now=1.6).linear.x == 0.0


def test_new_command_rearms_watchdog():
    logic = WatchdogLogic(0.5)
    logic.on_command(_twist(0.7), now=1.0)
    assert logic.output(now=2.0).linear.x == 0.0
    logic.on_command(_twist(0.3), now=2.0)
    assert logic.output(now=2.2).linear.x == 0.3
