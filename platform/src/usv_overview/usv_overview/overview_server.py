#!/usr/bin/env python3
import json

import rclpy
from rclpy.node import Node
from std_msgs.msg import String

from usv_overview.world_scan import scan_world


class OverviewServer(Node):
    def __init__(self):
        super().__init__('overview_server')

        self.declare_parameter('world', 'air_crash_sar')
        self.declare_parameter('world_file', '')
        self.declare_parameter('map_padding_m', 80.0)
        self.declare_parameter('min_map_span_m', 800.0)
        self.declare_parameter('grid_size_m', 10.0)

        self.metadata = self.scan_metadata()

        self.pub = self.create_publisher(String, '/overview/metadata', 1)
        self.timer = self.create_timer(1.0, self.publish_metadata)
        self.publish_metadata()

    def scan_metadata(self):
        world = str(self.get_parameter('world').value)
        world_file = str(self.get_parameter('world_file').value)
        padding = float(self.get_parameter('map_padding_m').value)
        min_map_span_m = float(self.get_parameter('min_map_span_m').value)
        grid_size_m = float(self.get_parameter('grid_size_m').value)

        metadata = scan_world(
            world=world,
            world_file=world_file,
            padding=padding,
            grid_size_m=grid_size_m,
            min_map_span_m=min_map_span_m,
        )
        bounds = metadata['bounds']
        self.get_logger().info(
            'overview map scanned: '
            f"{metadata['world']} "
            f"[x {bounds['min_x']:.1f}..{bounds['max_x']:.1f}, "
            f"y {bounds['min_y']:.1f}..{bounds['max_y']:.1f}], "
            f"{len(metadata['obstacles'])} footprints, "
            f"{len(metadata['markers'])} markers"
        )

        if not metadata.get('world_file'):
            self.get_logger().warn('overview map is using fallback bounds; world file not found')

        return metadata

    def publish_metadata(self):
        msg = String()
        msg.data = json.dumps(self.metadata)
        self.pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = OverviewServer()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
