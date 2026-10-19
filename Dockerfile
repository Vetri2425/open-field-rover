FROM ros:jazzy

SHELL ["/bin/bash", "-c"]

RUN apt-get update && apt-get install -y --no-install-recommends \
    ros-jazzy-desktop \
    ros-jazzy-ros-gz \
    ros-jazzy-ros-gz-bridge \
    ros-jazzy-navigation2 \
    ros-jazzy-nav2-bringup \
    ros-jazzy-robot-localization \
    ros-jazzy-rosbridge-suite \
    ros-jazzy-xacro \
    ros-jazzy-joint-state-publisher \
    python3-colcon-common-extensions \
    novnc \
    websockify \
    supervisor \
    x11vnc \
    xvfb \
    fluxbox \
    tmux \
    htop \
    iputils-ping \
    net-tools \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /home/ros

RUN mkdir -p /usr/local/etc/supervisord.d && \
    mkdir -p /tmp/.X11-unix && chmod 1777 /tmp/.X11-unix

COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

ENV DISPLAY=:1 \
    VNC_PORT=5900 \
    NOVNC_PORT=6080

WORKDIR /home/ros/ws

ENTRYPOINT ["/bin/bash"]
CMD ["-c", "supervisord -c /etc/supervisor/conf.d/supervisord.conf && tail -f /dev/null"]
