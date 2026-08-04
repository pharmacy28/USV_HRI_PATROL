from setuptools import find_packages, setup

package_name = 'usv_overview'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', ['launch/overview.launch.py']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='cyz',
    maintainer_email='cyz@todo.todo',
    description='Global overview support for multi WAM-V console',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'overview_server = usv_overview.overview_server:main',
            'fleet_state_node = usv_overview.fleet_state_node:main',
            'sensor_link_monitor = usv_overview.sensor_link_monitor:main',
            'selected_camera_relay = usv_overview.selected_camera_relay:main',
            'whisper_bridge_node = usv_overview.whisper_bridge_node:main',
            'voice_command_node = usv_overview.voice_command_node:main',
            'mission_gateway_node = usv_overview.mission_gateway_node:main',
            'scan_world = usv_overview.world_scan:main',
        ],
    },
)
