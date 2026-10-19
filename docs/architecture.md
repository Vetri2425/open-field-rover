# System Architecture

## Overview

open-field-rover is a modular ROS 2 system that progressively adds autonomy from Phase 1 (simulation + safe teleop) through Phase 5 (full autonomous navigation with web dashboard).

### Phase 1: Simulation and safe teleop (current)

```
 ros2 topic pub / any driver
          │  /cmd_vel
          ▼
 ┌──────────────────────┐   /cmd_vel_safe   ┌────────────────┐   gz topic    ┌──────────────────────┐
 │ ofr_safety           │ ────────────────► │ ros_gz_bridge  │ ────────────► │ Gazebo Harmonic      │
 │ cmd_vel_watchdog     │                   │ parameter_     │               │  DiffDrive plugin    │
 │ zero after 0.5 s     │                   │ bridge         │               │  Odometry publisher  │
 └──────────────────────┘                   │                │ ◄──────────── │  gpu_lidar, IMU,     │
                                            └────────────────┘  sensor data  │  NavSat sensors      │
                                                   │                          └──────────────────────┘
                                                   ▼
                                  /odom  /imu/data  /scan  /gps/fix
```

`robot_state_publisher` and `joint_state_publisher` provide `/tf` and `/joint_states` from the URDF. The world defines `spherical_coordinates` (Munich) so the NavSat sensor can report latitude and longitude. A noVNC desktop (`localhost:6080`) is provided for the Gazebo GUI; simulation itself runs headless.

### Phase 2: EKF Localization (Planned)

Addition of `robot_localization` node for GNSS + IMU fusion:

```
Gazebo Topics          robot_localization (EKF)         Nav2 Stack (Phase 3)
─────────────────      ──────────────────────            ────────────────
/imu/data      ┐
                ├─→ EKF Filter ─→ /tf (base_link→odom)
/gps/fix       ┘                      ↓
                                   /odometry/filtered
```

### Phase 3: Nav2 Navigation (Planned)

```
Waypoint input          Nav2 Stack              Controller
────────────────        ─────────────           ──────────
[lat, lon, alt]   ─→   Cost maps         ┌─→  Regulated Pure Pursuit
                        Global planner   │      /cmd_vel → Gazebo
                        Local planner  ──┘
```

### Phase 4: Web Dashboard (Planned)

```
Docker Container                    Host Browser
────────────────                    ───────────
ROS 2 (Node)                       React App
  ↓
rosbridge_server @ :9090  ─(WebSocket)─→  Dashboard
  ├─ /tf (transforms)
  ├─ /odom (pose)
  ├─ /cmd_vel (goal input)
  ├─ /gps/fix (GNSS status)
  └─ /imu/data (orientation)
```

---

## Package Dependencies

### Build-time
- `ament_cmake` (ROS 2 build system)
- `xacro` (URDF preprocessor)
- `catkin_pkg` (metadata)

### Runtime
- `ros_gz_sim`, `ros_gz_bridge` (Gazebo Harmonic integration)
- `robot_state_publisher`, `joint_state_publisher` (URDF state)
- `robot_localization` (Phase 2)
- `navigation2` (Phase 3)
- `rosbridge_suite` (Phase 4)

---

## Sensor Definitions (Phase 1 → Simulation)

| Sensor | Link | Type | Purpose | Phase |
|--------|------|------|---------|-------|
| Lidar | lidar_link | Ray scanner | 360° planar obstacle detection | 3 |
| IMU | imu_link | 6-axis accelerometer + gyro | Odometry fusion | 2 |
| GNSS | gnss_link | GPS + compass | Global localization | 2 |
| Encoders | left/right wheels | Wheel odometry | Dead reckoning | 2 |

---

## TF Tree (Transforms)

### Phase 1
```
world
  └─ base_footprint (ground contact point, z=wheel_radius)
      └─ base_link (chassis origin, z=0 in base_footprint)
          ├─ left_wheel_link
          ├─ right_wheel_link
          ├─ front_caster_link
          ├─ lidar_link
          ├─ imu_link
          └─ gnss_link
```

### Phase 2 (with EKF)
```
world (map frame, fixed)
  └─ odom (EKF-estimated pose)
      └─ base_footprint
          └─ base_link
              └─ [sensor links]
```

---

## Design Decisions

### Differential Drive
- **Why:** Simple, underactuated system. Easier to control, test, scale.
- **Kinematics:** Unicycle model (2 wheels, 1 free caster).

### URDF over SDF
- **Why:** ROS 2 convention. Easier integration with Nav2, SLAM, visualization.
- **SDF for Gazebo:** Gazebo config separate; better for physics tuning.

### Docker + noVNC
- **Why:** Reproducible on ARM64 (Apple Silicon) without VM overhead.
- **noVNC:** Browser-native GUI. No X11 forwarding overhead.

### Gazebo Harmonic (via ros:jazzy)
- **Why:** Latest stable, supports modern plugins, better ARM64 support.

### robot_localization (Phase 2)
- **Why:** Proven EKF. Handles sensor fusion, covariance management.
- **Alternative:** Particle filters (raobot), Kalman filters (custom). EKF is standard.

---

## Future Improvements

- [ ] GPU acceleration for Gazebo (if available on hardware)
- [ ] SLAM for map building (Phase 5)
- [ ] Hardware-in-loop sim (HIL) with real rover
- [ ] Multi-robot coordination (swarm navigation)
- [ ] Behavior trees for mission planning
