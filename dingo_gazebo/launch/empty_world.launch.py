#!/usr/bin/env python3
#
# Copyright 2019 ROBOTIS CO., LTD.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Authors: Darby Lim

import os
from pathlib import Path

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import ExecuteProcess, SetEnvironmentVariable
from launch.actions import IncludeLaunchDescription
from launch_ros.actions import Node
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, Command, EnvironmentVariable, PathJoinSubstitution

def generate_launch_description():
    use_sim_time = LaunchConfiguration('use_sim_time', default='True')
    world = os.path.join(get_package_share_directory('dingo_gazebo'),
                         'worlds', 'empty.world')

    pkg_gazebo_ros = get_package_share_directory('gazebo_ros')

    xacro_path = os.path.join(get_package_share_directory('dingo_description'),
                              'urdf', 'dingo-d.urdf.xacro')
    robot_description = {'robot_description' : Command(['xacro', ' ', xacro_path])}

    rviz_config = os.path.join(get_package_share_directory('dingo_description'),
                              'rviz', 'dingo.rviz')

    # We need to append to the GAZEBO_MODEL_PATH for gazebo to find the Dingo's meshes
    dingo_path = str(Path(get_package_share_directory('dingo_description')).parent.absolute())

    return LaunchDescription([
        ExecuteProcess(
            cmd=['ros2', 'param', 'set', '/gazebo', 'use_sim_time', use_sim_time],
            output='screen'),

        SetEnvironmentVariable(name='GAZEBO_MODEL_PATH', value=[EnvironmentVariable('GAZEBO_MODEL_PATH'), os.pathsep, dingo_path]),

        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(pkg_gazebo_ros, 'launch', 'gzserver.launch.py')
            ),
            launch_arguments={'world': world, 'verbose': ' '}.items(),
        ),

        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(pkg_gazebo_ros, 'launch', 'gzclient.launch.py')
            ),
        ),

        Node(package='gazebo_ros',
             executable='spawn_entity.py',
             arguments=['-entity', 'dingo',
                        '-topic', 'robot_description',
                        '-package_to_model'],
             output='screen'),

        Node(package='robot_state_publisher',
             name='robot_state_publisher',
             executable='robot_state_publisher',
             output='screen',
             parameters=[robot_description]
        ),
    ])
