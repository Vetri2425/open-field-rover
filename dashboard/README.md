# open-field-rover Dashboard

## Phase 4: Web-based Telemetry & Control

This directory will contain the React-based web dashboard for monitoring and controlling the rover in real-time.

### Planned Features

- **Telemetry Display**
  - Real-time robot pose (x, y, θ) from `/odom`
  - IMU orientation (roll, pitch, yaw)
  - GNSS coordinates (lat, lon, altitude)
  - Battery status, motor currents

- **Interactive Controls**
  - Joystick input (desktop/mobile) → `/cmd_vel`
  - Waypoint goal setter (click on map)
  - Mission planner (upload path)

- **Visualization**
  - Live map with robot position
  - Sensor readings (lidar costmap, IMU axes)
  - Odometry trail breadcrumb
  - Camera feed (if added in later phases)

### Architecture

- **Frontend:** React + TypeScript (Vite)
- **Communication:** rosbridge_suite (WebSocket @ localhost:9090)
- **State Management:** Redux or Zustand
- **Visualization:** Deck.gl or Mapbox for map rendering

### Setup (Phase 4)

```bash
# In dashboard/
npm install
npm run dev

# Opens http://localhost:5173
# Backend: localhost:9090 (rosbridge)
```

### Status

⏳ **Planned for Phase 4.** Awaiting EKF localization (Phase 2) and Nav2 stack (Phase 3).
