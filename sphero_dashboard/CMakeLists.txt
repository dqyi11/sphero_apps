cmake_minimum_required(VERSION 2.8.3)
project(sphero_dashboard)

find_package(catkin REQUIRED COMPONENTS
             rospy
             std_msgs
            )


catkin_package(
)

include_directories(${catkin_INCLUDE_DIRS})

install(PROGRAMS src/sphero_dashboard.py
  DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)
install(DIRECTORY launch
  DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)
