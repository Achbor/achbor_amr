# import os
# from ament_index_python.packages import get_package_share_directory

# from launch import LaunchDescription
# from launch.actions import IncludeLaunchDescription
# from launch.launch_description_sources import PythonLaunchDescriptionSource

# from launch_ros.actions import Node

# def generate_launch_description():
#     package_name = 'my_robot' # Custom Name
#     rsp = IncludeLaunchDescription(
#         PythonLaunchDescriptionSource([os.path.join(
#             get_package_share_directory(package_name), 'launch', 'rsp.launch.py'
#         )]), launch_arguments={'use_sim_time': 'true', 'use_ros2_control':'true'}.items()
#     )

#     # Include the gazebo launch file, Provided by the Gazebo ros package
#     gazebo_params_file = os.path.join(
#         get_package_share_directory(package_name), 'config', 'gazebo_params.yaml'
#     )
#     gazebo  = IncludeLaunchDescription(
#         PythonLaunchDescriptionSource([os.path.join(
#             get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py'
#         )]), launch_arguments={'gz_args': '--ros-args --params-file '+ gazebo_params_file}.items()
#     )

#     # run the spawner node form teh gazebo_ros package. The
#     spawn_entity = Node(package='ros_gz_sim', 
#                         #executable='spawn_entity.py',
#                         executable = 'create',
#                         arguments=['-topic', 'robot_description', '-entity', 'my_robot'],
#                         output='screen',)

#     # Node to spawn teh differential drive controller
#     diff_drive_spawner =Node(
#         package="controller_manager",
#         executable="spawner",
#         arguments=["diff_cont"],
#     )
#     # Node to spawn the joint Boradcaster
#     joint_broad_spawner =Node(
#         package="controller_manager",
#         executable="spawner",
#         arguments=["joint_broad"],
#     )
    
#     # Return them all!
#     return LaunchDescription([
#         rsp,
#         gazebo,
#         spawn_entity,
#         diff_drive_spawner,
#         joint_broad_spawner,
#     ])


#***************************EDITED VERSION*********************************#
import os
from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration

from launch_ros.actions import Node

def generate_launch_description():
    package_name = 'my_robot'

    # --- world launch arg (so CLI world:=... actually works) ---
    default_world = os.path.join(
        get_package_share_directory(package_name),
        'worlds',
        'obstacles.sdf'   # <-- change to your actual file name
    )
    world = LaunchConfiguration('world')

    declare_world = DeclareLaunchArgument(
        'world',
        default_value=default_world,
        description='Full path to world SDF file'
    )

    # Robot State Publisher + robot_description (your existing)
    rsp = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory(package_name), 'launch', 'rsp.launch.py')
        ),
        launch_arguments={'use_sim_time': 'true', 'use_ros2_control': 'true'}.items()
    )

    # calling in Joystick controller launch file
    joystick = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(
            get_package_share_directory(package_name), 'launch', 'joystick.launch.py'
        )]), launch_arguments={'use_sim_time':'true'}.items()
    )

    # Adding in a Tist multiplexer launcher
    twist_mux_params = os.path.join(get_package_share_directory(package_name), 'config', 'twist_mux.yaml')
    twist_mux = Node(
        package = 'twist_mux',
        executable = 'twist_mux',
        parameters = [twist_mux_params, {'use_sim_time': True}],
        remappings = [('/cmd_vel_out', '/diff_cont/cmd_vel_unstamped')]
    )

    # Gazebo params
    gazebo_params_file = os.path.join(
        get_package_share_directory(package_name), 'config', 'gazebo_params.yaml'
    )

    # --- Launch Gazebo (ros_gz_sim) correctly ---
    # gz_args is the key one. We include:
    # -r (run), -v 3 verbosity, the world file,
    # and pass ROS params to Gazebo’s ROS node with --ros-args
    gz_args = [
        '-r -v 3 ',
        world,
        ' --ros-args --params-file ',
        gazebo_params_file
    ]

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={'gz_args': ''.join([str(x) for x in gz_args])}.items()
    )

    # Spawn entity from robot_description
    spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=['-topic', 'robot_description', '-name', 'my_robot'],
        output='screen',
    )

    # Spawners (these need /controller_manager to exist)
    diff_drive_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["diff_cont", "--controller-manager", "/controller_manager"],
        output="screen",
    )

    joint_broad_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_broad", "--controller-manager", "/controller_manager"],
        output="screen",
    )

    return LaunchDescription([
        #declare_world,
        rsp,
        joystick,
        twist_mux,
        gazebo,
        spawn_entity,
        joint_broad_spawner,
        diff_drive_spawner,
    ])
