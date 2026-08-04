#!/usr/bin/env python3
from pathlib import Path
import argparse
import re


def remove_detachable_joint(text: str) -> str:
    pattern = re.compile(
        r'\s*<!-- === \[Un\]lock the robot to the world === -->\s*'
        r'<gazebo>\s*'
        r'<plugin filename="gz-sim-detachable-joint-system" name="gz::sim::systems::DetachableJoint">.*?'
        r'</plugin>\s*'
        r'</gazebo>\s*',
        re.DOTALL,
    )
    text, n = pattern.subn("\n", text)
    print(f"removed DetachableJoint blocks: {n}")
    return text


def patch_namespace(text: str, namespace: str) -> str:
    # 修复所有插件 namespace，避免仍然监听 wamv/thrusters
    text = re.sub(
        r'<namespace>.*?</namespace>',
        f'<namespace>{namespace}</namespace>',
        text,
        flags=re.DOTALL,
    )

    # 修复可能硬编码的转向舵 topic
    replacements = {
        "<topic>wamv/thrusters/left/pos</topic>":
            f"<topic>{namespace}/thrusters/left/pos</topic>",
        "<topic>wamv/thrusters/right/pos</topic>":
            f"<topic>{namespace}/thrusters/right/pos</topic>",
        "<topic>/wamv/thrusters/left/pos</topic>":
            f"<topic>/{namespace}/thrusters/left/pos</topic>",
        "<topic>/wamv/thrusters/right/pos</topic>":
            f"<topic>/{namespace}/thrusters/right/pos</topic>",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    text = text.replace("$(arg namespace)", namespace)

    return text


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--src", required=True)
    parser.add_argument("--dst", required=True)
    parser.add_argument("--namespace", required=True)
    args = parser.parse_args()

    src = Path(args.src).expanduser()
    dst = Path(args.dst).expanduser()

    text = src.read_text()
    text = remove_detachable_joint(text)
    text = patch_namespace(text, args.namespace)

    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(text)

    print(f"written: {dst}")
    print(f"namespace: {args.namespace}")


if __name__ == "__main__":
    main()
