# SeraBot development image: ROS 2 Lyrical + Gazebo Jetty (via ros_gz) on Ubuntu 26.04.
# Used when the host cannot run Lyrical natively (e.g. an older Ubuntu VM).
FROM ros:lyrical

ARG DEBIAN_FRONTEND=noninteractive
ARG USERNAME=dev
ARG USER_UID=1000
ARG USER_GID=1000

RUN apt-get update && apt-get install -y --no-install-recommends \
        ros-${ROS_DISTRO}-ros-gz \
        ros-${ROS_DISTRO}-rviz2 \
        ros-${ROS_DISTRO}-xacro \
        ros-${ROS_DISTRO}-robot-state-publisher \
        ros-${ROS_DISTRO}-joint-state-publisher-gui \
        ros-${ROS_DISTRO}-teleop-twist-keyboard \
        ros-${ROS_DISTRO}-rqt-image-view \
        ros-${ROS_DISTRO}-rqt-plot \
        ros-${ROS_DISTRO}-cv-bridge \
        ros-${ROS_DISTRO}-ament-flake8 \
        python3-opencv \
        python3-pytest \
        liburdfdom-tools \
        mesa-utils \
        sudo \
    && rm -rf /var/lib/apt/lists/*

# Non-root user whose UID/GID match the host user, so files written to the
# mounted workspace keep the host user's ownership.
RUN if getent passwd ${USER_UID} >/dev/null; then \
        userdel -r "$(getent passwd ${USER_UID} | cut -d: -f1)"; \
    fi \
    && if ! getent group ${USER_GID} >/dev/null; then groupadd --gid ${USER_GID} ${USERNAME}; fi \
    && useradd --uid ${USER_UID} --gid ${USER_GID} -m -s /bin/bash ${USERNAME} \
    && echo "${USERNAME} ALL=(root) NOPASSWD:ALL" > /etc/sudoers.d/${USERNAME} \
    && chmod 0440 /etc/sudoers.d/${USERNAME} \
    && echo "source /opt/ros/${ROS_DISTRO}/setup.bash" >> /home/${USERNAME}/.bashrc \
    && echo '[ -f /ws/install/setup.bash ] && source /ws/install/setup.bash' >> /home/${USERNAME}/.bashrc

USER ${USERNAME}
WORKDIR /ws
CMD ["bash"]
