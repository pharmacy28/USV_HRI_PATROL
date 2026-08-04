from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration, PythonExpression
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
import sys


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument('world', default_value='air_crash_sar'),
        DeclareLaunchArgument(
            'target_names',
            default_value="['wamv_01','wamv_02','wamv_03','wamv_04','wamv_05','wamv_06','wamv_07','wamv_08','wamv_09','wamv_10']",
        ),
        DeclareLaunchArgument('config_file', default_value=''),
        DeclareLaunchArgument('map_padding_m', default_value='80.0'),
        DeclareLaunchArgument('min_map_span_m', default_value='800.0'),
        DeclareLaunchArgument('grid_size_m', default_value='10.0'),
        DeclareLaunchArgument('enable_voice', default_value='false'),
        DeclareLaunchArgument('voice_python', default_value=sys.executable),
        DeclareLaunchArgument('voice_model', default_value='base'),
        DeclareLaunchArgument('voice_model_dir', default_value=''),
        DeclareLaunchArgument('voice_language', default_value='zh'),
        DeclareLaunchArgument('voice_audio_backend', default_value='auto'),
        DeclareLaunchArgument('voice_audio_device', default_value=''),
        DeclareLaunchArgument('voice_udp_bind', default_value='0.0.0.0'),
        DeclareLaunchArgument('voice_udp_port', default_value='15556'),
        DeclareLaunchArgument('voice_udp_source_ip', default_value=''),
        DeclareLaunchArgument('voice_udp_timeout_sec', default_value='1.0'),
        DeclareLaunchArgument('voice_udp_preroll_sec', default_value='0.15'),
        DeclareLaunchArgument('voice_chunk_sec', default_value='1.5'),
        DeclareLaunchArgument('voice_energy_threshold', default_value='0.02'),
        DeclareLaunchArgument('voice_audio_gain', default_value='1.0'),
        DeclareLaunchArgument('voice_no_speech_threshold', default_value='0.8'),
        DeclareLaunchArgument(
            'voice_initial_prompt',
            default_value=(
                '普通话多艇任务口令。常见短口令包括：二号船去E5、WAMV十号到A1、'
                '选择一号船、打开网格、切换全局态势。请保留船号和棋盘格编号，按原文输出。'
            )
        ),
        DeclareLaunchArgument('voice_push_to_talk', default_value='true'),
        DeclareLaunchArgument('voice_ptt_button', default_value='0'),
        DeclareLaunchArgument('voice_cancel_button', default_value='1'),
        DeclareLaunchArgument('voice_ptt_release_debounce_sec', default_value='0.2'),
        Node(
            package='usv_overview',
            executable='overview_server',
            output='screen',
            parameters=[
                {
                    'world': LaunchConfiguration('world'),
                    'map_padding_m': LaunchConfiguration('map_padding_m'),
                    'min_map_span_m': LaunchConfiguration('min_map_span_m'),
                    'grid_size_m': LaunchConfiguration('grid_size_m'),
                }
            ],
        ),
        Node(
            package='usv_overview',
            executable='fleet_state_node',
            output='screen',
            parameters=[
                {
                    'target_names': LaunchConfiguration('target_names'),
                    'config_file': LaunchConfiguration('config_file'),
                    'world': LaunchConfiguration('world'),
                }
            ],
        ),
        Node(
            package='usv_overview',
            executable='sensor_link_monitor',
            output='screen',
            parameters=[
                {
                    'target_names': LaunchConfiguration('target_names'),
                }
            ],
        ),
        Node(
            package='usv_overview',
            executable='selected_camera_relay',
            output='screen',
            parameters=[
                {
                    'world': LaunchConfiguration('world'),
                    'target_names': LaunchConfiguration('target_names'),
                }
            ],
        ),
        Node(
            package='ros_gz_bridge',
            executable='parameter_bridge',
            name='overview_dynamic_pose_bridge',
            output='screen',
            arguments=[
                PythonExpression([
                    "'/world/",
                    LaunchConfiguration('world'),
                    "/dynamic_pose/info@geometry_msgs/msg/PoseArray[ignition.msgs.Pose_V'",
                ]),
            ],
            remappings=[
                (
                    PythonExpression([
                        "'/world/",
                        LaunchConfiguration('world'),
                        "/dynamic_pose/info'",
                    ]),
                    '/overview/dynamic_pose',
                ),
            ],
        ),
        Node(
            package='usv_overview',
            executable='whisper_bridge_node',
            output='screen',
            condition=IfCondition(LaunchConfiguration('enable_voice')),
            parameters=[
                {
                    'voice_python': LaunchConfiguration('voice_python'),
                    'model': LaunchConfiguration('voice_model'),
                    'model_dir': LaunchConfiguration('voice_model_dir'),
                    'language': LaunchConfiguration('voice_language'),
                    'audio_backend': LaunchConfiguration('voice_audio_backend'),
                    'audio_device': ParameterValue(
                        LaunchConfiguration('voice_audio_device'),
                        value_type=str,
                    ),
                    'udp_bind': LaunchConfiguration('voice_udp_bind'),
                    'udp_port': LaunchConfiguration('voice_udp_port'),
                    'udp_source_ip': LaunchConfiguration('voice_udp_source_ip'),
                    'udp_timeout_sec': LaunchConfiguration('voice_udp_timeout_sec'),
                    'udp_preroll_sec': LaunchConfiguration('voice_udp_preroll_sec'),
                    'chunk_sec': LaunchConfiguration('voice_chunk_sec'),
                    'energy_threshold': LaunchConfiguration('voice_energy_threshold'),
                    'audio_gain': LaunchConfiguration('voice_audio_gain'),
                    'no_speech_threshold': LaunchConfiguration('voice_no_speech_threshold'),
                    'initial_prompt': LaunchConfiguration('voice_initial_prompt'),
                    'push_to_talk': LaunchConfiguration('voice_push_to_talk'),
                    'ptt_button': LaunchConfiguration('voice_ptt_button'),
                    'cancel_button': LaunchConfiguration('voice_cancel_button'),
                    'ptt_release_debounce_sec': LaunchConfiguration('voice_ptt_release_debounce_sec'),
                }
            ],
        ),
        Node(
            package='usv_overview',
            executable='voice_command_node',
            output='screen',
            condition=IfCondition(LaunchConfiguration('enable_voice')),
            parameters=[
                {
                    'target_names': LaunchConfiguration('target_names'),
                }
            ],
        ),
        Node(
            package='usv_overview',
            executable='mission_gateway_node',
            output='screen',
            parameters=[
                {
                    'target_names': LaunchConfiguration('target_names'),
                }
            ],
        ),
    ])
