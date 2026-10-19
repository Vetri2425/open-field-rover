#!/usr/bin/env bash
# Headless smoke test: launch the sim, check every sensor topic, drive, then check the watchdog stops the rover.
set -eo pipefail

source /opt/ros/jazzy/setup.bash
source "${WS:-/home/ros/ws}/install/setup.bash"

cleanup() {
  kill -INT "$LAUNCH_PID" 2>/dev/null || true
  sleep 3
  pkill -f "gz sim" 2>/dev/null || true
  pkill -f parameter_bridge 2>/dev/null || true
}
cleanup_stale() {
  pkill -f "gz sim" 2>/dev/null || true
  pkill -f parameter_bridge 2>/dev/null || true
  pkill -f cmd_vel_watchdog 2>/dev/null || true
  sleep 2
}

cleanup_stale
ros2 launch ofr_gazebo spawn_rover.launch.py >/tmp/launch.log 2>&1 &
LAUNCH_PID=$!
trap cleanup EXIT

sleep 25

for topic in /odom /imu/data /scan /gps/fix; do
  rate=$(timeout 10 ros2 topic hz "$topic" 2>&1 | grep -m1 "average rate" || true)
  echo "$topic: ${rate:-NO DATA}"
  [ -n "$rate" ] || { tail -30 /tmp/launch.log; exit 1; }
done

odom_x() {
  for _ in 1 2 3 4 5; do
    x=$(timeout 10 ros2 topic echo --once /odom --field pose.pose.position.x 2>/dev/null | grep -m1 -E '^-?[0-9]' || true)
    [ -n "$x" ] && { echo "$x"; return; }
    sleep 1
  done
  echo "odom read failed" >&2
  return 1
}
x0=$(odom_x)
timeout 6 ros2 topic pub -r 10 /cmd_vel geometry_msgs/msg/Twist '{linear: {x: 0.5}}' >/dev/null &
sleep 3
x1=$(odom_x)
sleep 6
x2=$(odom_x)
sleep 2
x3=$(odom_x)
echo "odom x: idle=$x0 driving=$x1 after-timeout=$x2 later=$x3"

python3 - "$x0" "$x1" "$x2" "$x3" <<'PY'
import sys

x0, x1, x2, x3 = map(float, sys.argv[1:])
assert x2 - x0 > 0.3, "rover did not move under /cmd_vel"
assert abs(x3 - x2) < 0.05, "rover kept moving after commands stopped (watchdog failed)"
print("smoke test passed")
PY
