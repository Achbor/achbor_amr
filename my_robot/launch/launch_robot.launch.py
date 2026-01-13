import os
from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction, RegisterEventHandler
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.event_handlers import OnProcessStart
from launch.substitutions import Command
from launch_ros.actions import Node

def generate_launch_description():
    package_name = 'my_robot' # Custom Name
    rsp = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(
            get_package_share_directory(package_name), 'launch', 'rsp.launch.py'
        )]), launch_arguments={'use_sim_time': 'false', 'use_ros2_control':'true'}.items() # Changed use_sim_time to false for real robot
    )

    # Include the gazebo launch file, Provided by the Gazebo ros package
    # gazebo_params_file = os.path.join(
    #     get_package_share_directory(package_name), 'config', 'gazebo_params.yaml'
    # )

    robot_description= Command(['ros2 param get --hide-type /robot_state_publisher robot_description'])
    controller_params_file = os.path.join(get_package_share_directory(package_name), 'config', 'my_controllers.yaml')
    # gazebo  = IncludeLaunchDescription(
    #     PythonLaunchDescriptionSource([os.path.join(
    #         get_package_share_directory('gazebo_ros'), 'launch', 'gazebo.launch.py'
    #     )]), launch_arguments={'extra_gazebo_arsgs': '--ros-args --params-file '+ gazebo_params_file}.items()
    # )

    # # run the spawner node form teh gazebo_ros package. The
    # spawn_entity = Node(package='gazebo_ros', 
    #                     executable='spawn_entity.py',
    #                     arguments=['-topic', 'robot_description', '-entity', 'my_robot'],
    #                     output='screen',)

    # Node to spawn controller manager
    controller_manager =Node(
        package="controller_manager",
        executable="ros2_control_node",
        parameters=[{'robot_description': robot_description}, 
                    controller_params_file,],
    )

    delayed_controller_manager = TimerAction(
        period = 3.0,
        actions=[controller_manager],    )

    # Node to spawn teh differential drive controller
    diff_drive_spawner =Node(
        package="controller_manager",
        executable="spawner",
        arguments=["diff_cont"],
    )
    # DElay the diff drive spawner to ensure controller manager is running
    delayed_diff_drive_spawner = RegisterEventHandler(
        event_handler=OnProcessStart(
            target_action=controller_manager,
            on_start=[diff_drive_spawner]
        )
    )

    # Node to spawn the joint Boradcaster
    joint_broad_spawner =Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_broad"],
    )
    # DElay the jpint_broad spawner to ensure controller manager is running
    delayed_joint_broad_spawner = RegisterEventHandler(
        event_handler=OnProcessStart(
            target_action=controller_manager,
            on_start=[joint_broad_spawner]
        )
    )
    
    # Return them all!
    return LaunchDescription([
        rsp,
        delayed_controller_manager,
        delayed_diff_drive_spawner,
        delayed_joint_broad_spawner
        # gazebo,
        # spawn_entity,
    ])