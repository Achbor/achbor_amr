import os
from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource

from launch_ros.actions import Node

def generate_launch_description():
    package_name = 'my_robot' # Custom Name
    rsp = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(
            get_package_share_directory(package_name), 'launch', 'rsp.launch.py'
        )]), launch_arguments={'use_sim_time': 'true', 'use_ros2_control':'true'}.items()
    )

    # Include the gazebo launch file, Provided by the Gazebo ros package
    gazebo_params_file = os.path.join(
        get_package_share_directory(package_name), 'config', 'gazebo_params.yaml'
    )
    gazebo  = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(
            get_package_share_directory('gazebo_ros'), 'launch', 'gazebo.launch.py'
        )]), launch_arguments={'extra_gazebo_arsgs': '--ros-args --params-file '+ gazebo_params_file}.items()
    )

    # run the spawner node form teh gazebo_ros package. The
    spawn_entity = Node(package='gazebo_ros', 
                        executable='spawn_entity.py',
                        arguments=['-topic', 'robot_description', '-entity', 'my_robot'],
                        output='screen',)

    # Node to spawn teh differential drive controller
    diff_drive_spawner =Node(
        package="controller_manager",
        executable="spawner",
        arguments=["diff_cont"],
    )
    # Node to spawn the joint Boradcaster
    joint_broad_spawner =Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_broad"],
    )
    
    # Return them all!
    return LaunchDescription([
        rsp,
        gazebo,
        spawn_entity,
        diff_drive_spawner,
        joint_broad_spawner,
    ])