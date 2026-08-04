#!/usr/bin/env python3
import argparse
import json
import math
import os
import xml.etree.ElementTree as ET


DEFAULT_WORLD_ROOTS = [
    "src/vrx/vrx_gz/worlds",
    "install/share/vrx_gz/worlds",
]


def parse_floats(text, expected=None):
    values = [float(part) for part in (text or "").split()]

    if expected is not None and len(values) < expected:
        values.extend([0.0] * (expected - len(values)))

    return values


def pose_xy_yaw(element):
    pose = parse_floats(element.findtext("pose", "0 0 0 0 0 0"), 6)
    return pose[0], pose[1], pose[5]


def rotate_point(x, y, yaw):
    c = math.cos(yaw)
    s = math.sin(yaw)
    return x * c - y * s, x * s + y * c


def footprint_polygon(cx, cy, yaw, length, width):
    hx = max(0.01, length) * 0.5
    hy = max(0.01, width) * 0.5
    local = [(-hx, -hy), (hx, -hy), (hx, hy), (-hx, hy)]
    points = []

    for x, y in local:
        rx, ry = rotate_point(x, y, yaw)
        points.append([cx + rx, cy + ry])

    return points


def polygon_bounds(points):
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    return min(xs), max(xs), min(ys), max(ys)


def merge_bounds(bounds_list):
    if not bounds_list:
        return None

    return {
        "min_x": min(item["min_x"] for item in bounds_list),
        "max_x": max(item["max_x"] for item in bounds_list),
        "min_y": min(item["min_y"] for item in bounds_list),
        "max_y": max(item["max_y"] for item in bounds_list),
    }


def single_marker(markers):
    if not markers:
        return []

    x = sum(marker["x"] for marker in markers) / len(markers)
    y = sum(marker["y"] for marker in markers) / len(markers)

    return [
        {
            "name": "suspect_target_placeholder",
            "kind": "suspect_target",
            "x": x,
            "y": y,
            "yaw": 0.0,
        }
    ]


def expand_bounds(bounds, padding):
    if bounds is None:
        return {
            "min_x": -500.0,
            "max_x": 500.0,
            "min_y": -500.0,
            "max_y": 500.0,
        }

    return {
        "min_x": bounds["min_x"] - padding,
        "max_x": bounds["max_x"] + padding,
        "min_y": bounds["min_y"] - padding,
        "max_y": bounds["max_y"] + padding,
    }


def ensure_min_span(bounds, min_span_m):
    min_span_m = max(1.0, float(min_span_m))
    width = bounds["max_x"] - bounds["min_x"]
    height = bounds["max_y"] - bounds["min_y"]
    center_x = (bounds["min_x"] + bounds["max_x"]) * 0.5
    center_y = (bounds["min_y"] + bounds["max_y"]) * 0.5

    if width < min_span_m:
        half = min_span_m * 0.5
        bounds["min_x"] = center_x - half
        bounds["max_x"] = center_x + half

    if height < min_span_m:
        half = min_span_m * 0.5
        bounds["min_y"] = center_y - half
        bounds["max_y"] = center_y + half

    return bounds


def geometry_size(geometry):
    if geometry is None:
        return None

    box = geometry.find("box")
    if box is not None:
        size = parse_floats(box.findtext("size", "1 1 1"), 3)
        return "box", size[0], size[1]

    cylinder = geometry.find("cylinder")
    if cylinder is not None:
        radius = float(cylinder.findtext("radius", "0.5"))
        length = float(cylinder.findtext("length", str(radius * 2.0)))
        return "cylinder", max(radius * 2.0, length), radius * 2.0

    sphere = geometry.find("sphere")
    if sphere is not None:
        radius = float(sphere.findtext("radius", "0.5"))
        return "sphere", radius * 2.0, radius * 2.0

    return None


def material_color(element, model_name):
    material = element.find("material")
    values = []

    if material is not None:
        diffuse = material.findtext("diffuse")
        ambient = material.findtext("ambient")
        values = parse_floats(diffuse or ambient or "", 4)

    if len(values) >= 3:
        return [
            max(0, min(255, int(values[0] * 255))),
            max(0, min(255, int(values[1] * 255))),
            max(0, min(255, int(values[2] * 255))),
        ]

    return fallback_color(model_name)


def fallback_color(model_name):
    lower = model_name.lower()

    if "raft" in lower:
        return [245, 108, 20]
    if "survivor" in lower:
        return [245, 235, 35]
    if "black_box" in lower:
        return [18, 18, 16]
    if "smoke" in lower:
        return [220, 35, 25]
    if "crash" in lower:
        return [105, 112, 116]
    if "debris" in lower:
        return [95, 101, 104]

    return [120, 130, 132]


def model_kind(name):
    lower = name.lower()

    if "survivor" in lower or "black_box" in lower or "smoke" in lower or "raft" in lower:
        return "target"

    if "debris" in lower or "crash" in lower or "wreck" in lower:
        return "obstacle"

    return "obstacle"


def scan_model(model):
    name = model.attrib.get("name", "unnamed")

    if name.lower() in {"coast waves", "coast_waves", "ocean", "waves"}:
        return [], []

    model_x, model_y, model_yaw = pose_xy_yaw(model)
    footprints = []
    markers = []

    for link in model.findall("link"):
        link_x, link_y, link_yaw = pose_xy_yaw(link)
        link_rx, link_ry = rotate_point(link_x, link_y, model_yaw)
        base_x = model_x + link_rx
        base_y = model_y + link_ry
        base_yaw = model_yaw + link_yaw

        shapes = list(link.findall("visual"))
        if not shapes:
            shapes = list(link.findall("collision"))

        for shape in shapes:
            geom_info = geometry_size(shape.find("geometry"))
            if geom_info is None:
                continue

            shape_x, shape_y, shape_yaw = pose_xy_yaw(shape)
            shape_rx, shape_ry = rotate_point(shape_x, shape_y, base_yaw)
            cx = base_x + shape_rx
            cy = base_y + shape_ry
            yaw = base_yaw + shape_yaw
            geom_type, length, width = geom_info
            polygon = footprint_polygon(cx, cy, yaw, length, width)
            min_x, max_x, min_y, max_y = polygon_bounds(polygon)

            footprints.append(
                {
                    "name": name,
                    "kind": model_kind(name),
                    "geometry": geom_type,
                    "x": cx,
                    "y": cy,
                    "yaw": yaw,
                    "length": length,
                    "width": width,
                    "color": material_color(shape, name),
                    "polygon": polygon,
                    "bounds": {
                        "min_x": min_x,
                        "max_x": max_x,
                        "min_y": min_y,
                        "max_y": max_y,
                    },
                }
            )

    if model_kind(name) == "target":
        markers.append(
            {
                "name": name,
                "kind": "suspect_target",
                "x": model_x,
                "y": model_y,
                "yaw": model_yaw,
            }
        )

    return footprints, markers


def find_world_file(world, search_roots=None):
    if world and os.path.isfile(world):
        return os.path.abspath(world)

    roots = search_roots or candidate_world_roots()
    candidates = []

    for root in roots:
        candidates.append(os.path.join(root, f"{world}.sdf"))
        candidates.append(os.path.join(root, world))

    for candidate in candidates:
        if os.path.isfile(candidate):
            return os.path.abspath(candidate)

    return ""


def candidate_world_roots():
    roots = []

    def add(path):
        if path and path not in roots:
            roots.append(path)

    for prefix in os.environ.get("AMENT_PREFIX_PATH", "").split(os.pathsep):
        add(os.path.join(prefix, "share", "vrx_gz", "worlds"))

    anchors = [os.getcwd(), os.path.dirname(__file__)]

    for anchor in anchors:
        current = os.path.abspath(anchor)

        for _ in range(8):
            for root in DEFAULT_WORLD_ROOTS:
                add(os.path.join(current, root))

            parent = os.path.dirname(current)
            if parent == current:
                break
            current = parent

    for root in DEFAULT_WORLD_ROOTS:
        add(root)

    return roots


def occupancy_grid(bounds, obstacles, grid_size_m):
    grid_size_m = max(0.1, float(grid_size_m))
    width = max(1, int(math.ceil((bounds["max_x"] - bounds["min_x"]) / grid_size_m)))
    height = max(1, int(math.ceil((bounds["max_y"] - bounds["min_y"]) / grid_size_m)))
    max_cells = 20000

    if width * height > max_cells:
        scale = math.sqrt((width * height) / max_cells)
        grid_size_m *= scale
        width = max(1, int(math.ceil((bounds["max_x"] - bounds["min_x"]) / grid_size_m)))
        height = max(1, int(math.ceil((bounds["max_y"] - bounds["min_y"]) / grid_size_m)))

    occupied = []

    for row in range(height):
        for col in range(width):
            cell = {
                "min_x": bounds["min_x"] + col * grid_size_m,
                "max_x": bounds["min_x"] + (col + 1) * grid_size_m,
                "min_y": bounds["min_y"] + row * grid_size_m,
                "max_y": bounds["min_y"] + (row + 1) * grid_size_m,
            }

            for obstacle in obstacles:
                if obstacle.get("kind") != "obstacle":
                    continue

                box = obstacle["bounds"]

                if boxes_intersect(cell, box):
                    occupied.append(row * width + col)
                    break

    return {
        "origin_x": bounds["min_x"],
        "origin_y": bounds["min_y"],
        "resolution": grid_size_m,
        "width": width,
        "height": height,
        "occupied_indices": occupied,
    }


def sector_grid(bounds):
    return {
        "id": "overview_sector_8x8",
        "frame_id": "world",
        "bounds": dict(bounds),
        "columns": "ABCDEFGH",
        "rows": "12345678",
        "column_origin": "min_x",
        "row_origin": "max_y",
    }


def boxes_intersect(a, b):
    return not (
        a["max_x"] < b["min_x"]
        or a["min_x"] > b["max_x"]
        or a["max_y"] < b["min_y"]
        or a["min_y"] > b["max_y"]
    )


def scan_world(
    world="air_crash_sar",
    world_file="",
    search_roots=None,
    padding=80.0,
    grid_size_m=10.0,
    min_map_span_m=800.0,
):
    path = world_file or find_world_file(world, search_roots)

    if not path:
        bounds = ensure_min_span(expand_bounds(None, padding), min_map_span_m)
        return {
            "world": world,
            "world_file": "",
            "bounds": bounds,
            "grid_size_m": grid_size_m,
            "obstacles": [],
            "markers": [],
            "occupancy": occupancy_grid(bounds, [], grid_size_m),
            "sector_grid": sector_grid(bounds),
        }

    root = ET.parse(path).getroot()
    world_element = root.find("world")
    if world_element is None:
        world_element = root

    obstacles = []
    markers = []

    for model in world_element.findall("model"):
        model_obstacles, model_markers = scan_model(model)
        obstacles.extend(model_obstacles)
        markers.extend(model_markers)

    merged = merge_bounds([item["bounds"] for item in obstacles])
    bounds = ensure_min_span(expand_bounds(merged, padding), min_map_span_m)

    return {
        "world": world_element.attrib.get("name", world),
        "world_file": path,
        "bounds": bounds,
        "grid_size_m": grid_size_m,
        "obstacles": obstacles,
        "markers": single_marker(markers),
        "occupancy": occupancy_grid(bounds, obstacles, grid_size_m),
        "sector_grid": sector_grid(bounds),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--world", default="air_crash_sar")
    parser.add_argument("--world-file", default="")
    parser.add_argument("--padding", type=float, default=80.0)
    parser.add_argument("--grid-size-m", type=float, default=10.0)
    parser.add_argument("--min-map-span-m", type=float, default=800.0)
    args = parser.parse_args()

    print(
        json.dumps(
            scan_world(
                world=args.world,
                world_file=args.world_file,
                padding=args.padding,
                grid_size_m=args.grid_size_m,
                min_map_span_m=args.min_map_span_m,
            ),
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
