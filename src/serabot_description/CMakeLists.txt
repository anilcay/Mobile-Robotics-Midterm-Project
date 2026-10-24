cmake_minimum_required(VERSION 3.16)
project(serabot_description)

find_package(ament_cmake REQUIRED)

install(
  DIRECTORY urdf meshes launch rviz
  DESTINATION share/${PROJECT_NAME}
)

# Lets Gazebo resolve package://serabot_description/meshes/... URIs.
ament_environment_hooks("${CMAKE_CURRENT_SOURCE_DIR}/hooks/${PROJECT_NAME}.dsv.in")

ament_package()
