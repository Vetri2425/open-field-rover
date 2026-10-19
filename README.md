# open-field-rover

A simulated differential-drive field rover built on ROS 2 Jazzy and Gazebo Harmonic, heading towards GNSS waypoint navigation with Nav2 and a web dashboard. Everything runs in Docker, so it is reproducible on Apple Silicon (arm64) and x86.

## Roadmap

| Phase | Goal | Status |
|-------|------|--------|
| 1 | Simulation: Gazebo Harmonic rover with real sensors, `ros_gz_bridge`, safety watchdog | Done |
| 2 | EKF localisation (`robot_localization`: IMU + GNSS fusion) | Planned |
| 3 | Nav2 with GNSS waypoint following | Planned |
| 4 | Web dashboard (rosbridge, live telemetry) | Planned |
| 5 | Demo video, extended tests, documentation | Planned |

## Quick start

Requirements: Docker (Docker Desktop or Colima) with Compose, and `make`.

```bash
git clone https://github.com/Vetri2425/open-field-rover.git
cd open-field-rover
make build          # build the image (ROS 2 Jazzy + Gazebo Harmonic + noVNC)
make up             # start the container
make sim            # colcon build, then launch the simulation
```

The simulation runs headless by default. A desktop is available in the browser at <http://localhost:6080> (noVNC); raw VNC is on port 5900.

Drive the rover from a second terminal (`make shell`):

```bash
ros2 topic pub -r 10 /cmd_vel geometry_msgs/msg/Twist '{linear: {x: 0.5}}'
ros2 topic echo /odom --field pose.pose.position
```

Other targets: `make shell`, `make down`, `make clean`, `make logs`, `make help`.

## Topics

| ROS topic | Type | Source |
|-----------|------|--------|
| `/cmd_vel` | `geometry_msgs/Twist` | input; passes through the watchdog |
| `/cmd_vel_safe` | `geometry_msgs/Twist` | watchdog output, bridged to the Gazebo DiffDrive plugin |
| `/odom` | `nav_msgs/Odometry` | Gazebo odometry publisher, 50 Hz |
| `/imu/data` | `sensor_msgs/Imu` | Gazebo IMU sensor, 100 Hz |
| `/scan` | `sensor_msgs/LaserScan` | Gazebo `gpu_lidar` sensor, 10 Hz |
| `/gps/fix` | `sensor_msgs/NavSatFix` | Gazebo `navsat` sensor, 10 Hz |

All sensor data comes from Gazebo Harmonic sensor plugins bridged with `ros_gz_bridge`. There is no mock or fake data in the repo. The world origin is Munich (48.137 N, 11.575 E, set through `spherical_coordinates` in the world file), which the NavSat sensor needs in order to produce fixes.

## Safety watchdog

`ofr_safety/cmd_vel_watchdog` subscribes to `/cmd_vel` and republishes on `/cmd_vel_safe` at 20 Hz. If no command has arrived for 0.5 s (parameter `timeout`) it publishes zero velocity, so the rover stops when whoever is driving it goes silent. The simulator's DiffDrive plugin otherwise keeps executing its last command forever.

## Phase 1 verified

Measured inside the container with `scripts/smoke_test.sh` (headless Gazebo, Apple Silicon, Colima):

| Topic | Measured rate |
|-------|---------------|
| `/odom` | 50.0 Hz |
| `/imu/data` | 100.0 Hz |
| `/scan` | 10.0 Hz |
| `/gps/fix` | 10.0 Hz |

GPS origin: a `/gps/fix` message reports latitude 48.137000, longitude 11.575001, altitude 520.3 m, matching the Munich origin in the world file.

`/cmd_vel` test: `/odom` x is -0.001 m at rest. Publishing `linear.x = 0.5` at 10 Hz for 6 s drives the rover forward (x = 0.53 m three seconds in). Once the publisher stops, the watchdog zeroes the command and x settles at 0.67 m and stays there. Without the watchdog the rover keeps rolling at its last commanded speed.

The same script runs in CI. Unit tests (`colcon test`) cover the watchdog logic and the node itself.

## Project structure

```
open-field-rover/
├── src/
│   ├── ofr_description/   # URDF/xacro: chassis, wheels, lidar, IMU, GNSS + Gazebo plugins
│   ├── ofr_gazebo/        # Open-field world and spawn/bridge launch file
│   ├── ofr_safety/        # cmd_vel watchdog node + tests
│   └── ofr_bringup/       # Top-level launch (wraps the simulation)
├── scripts/smoke_test.sh  # Headless end-to-end check used locally and in CI
├── dashboard/             # Web dashboard (Phase 4 placeholder)
├── docs/                  # Architecture notes
├── Dockerfile, docker-compose.yml, supervisord.conf, Makefile
└── .devcontainer/         # VS Code dev container
```

## Development

- **Dev container:** open the folder in VS Code and choose "Reopen in Container".
- **Pre-commit:** `pip install pre-commit && pre-commit install` (black, ruff, whitespace and YAML checks).
- **CI** (`.github/workflows/ci.yml`): pre-commit, image build, `colcon build` and `colcon test`, then the headless smoke test above.

## License

MIT. See [LICENSE](LICENSE).

## Author

Vetri, [vetri96anitha@gmail.com](mailto:vetri96anitha@gmail.com)
