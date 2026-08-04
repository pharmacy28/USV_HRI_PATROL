#!/usr/bin/env bash
set -Eeuo pipefail

PLATFORM_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_DIR="$(cd -- "$PLATFORM_DIR/.." && pwd)"
VRX_DIR="$PLATFORM_DIR/src/vrx"
PATCH_FILE="$PLATFORM_DIR/patches/vrx-humble.patch"
EXPECTED_COMMIT="dc30ed8d17aa1083fd872edad9c77c69896d2b07"

git -C "$REPO_DIR" submodule update --init --recursive -- platform/src/vrx

actual_commit="$(git -C "$VRX_DIR" rev-parse HEAD)"
if [ "$actual_commit" != "$EXPECTED_COMMIT" ]; then
  echo "[setup_vrx] error: expected $EXPECTED_COMMIT, got $actual_commit" >&2
  exit 1
fi

if git -C "$VRX_DIR" apply --check "$PATCH_FILE" 2>/dev/null; then
  git -C "$VRX_DIR" apply "$PATCH_FILE"
  echo "[setup_vrx] applied USV_HRI_PATROL VRX patch"
elif git -C "$VRX_DIR" apply --reverse --check "$PATCH_FILE" 2>/dev/null; then
  echo "[setup_vrx] VRX patch is already applied"
else
  echo "[setup_vrx] error: VRX tree has conflicting local changes" >&2
  exit 1
fi

git -C "$VRX_DIR" diff --check
echo "[setup_vrx] ready: $VRX_DIR"
