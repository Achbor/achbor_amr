AMR ROBOT
This project encapsulates Autonomous Mobile Robot implementation. 
The core implementation includes SLAM and Navigation ROS2 pakcages for 2d-map creation, localization and autonomous Navigation of the Robot.

The ROS version is Humble, but can be updated and upgraded to other versions (note that when not using microros, refactoring of serial communication packages for Differential Drive control will be required to match the respective ROS2 distribution).

MAin COmponents required:
1. ROS2 Humble
2. ROS2 runnig platform (jetson, raspberrypi or a computer)
3. Motor controller and sensor fusion low level controller (ESP32 or Arduino)
4. Encoded DC Motors
5. lidar (in this case ldlidar was used)
6. A cjoystick controller (optional).
