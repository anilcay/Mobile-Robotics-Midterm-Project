cmake_minimum_required(VERSION 3.16)
project(serabot_gazebo)

find_package(ament_cmake REQUIRED)

install(
  DIRECTORY worlds models
  DESTINATION share/${PROJECT_NAME}
)

# Lets Gazebo find the models in this package (model://<name>).
ament_environment_hooks("${CMAKE_CURRENT_SOURCE_DIR}/hooks/${PROJECT_NAME}.dsv.in")

ament_package()
