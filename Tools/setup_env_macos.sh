#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUILD_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PROJECT_ROOT="$(cd "$BUILD_ROOT/.." && pwd)"

CONFIG_PATH="$PROJECT_ROOT/Config/BuildSystem/BuildConfig.json"
TEMPLATE_PATH="$BUILD_ROOT/Templates/BuildConfig.template.json"

echo "[info] ProjectRoot: $PROJECT_ROOT"
echo "[info] BuildRoot:   $BUILD_ROOT"
echo "[info] ConfigPath:  $CONFIG_PATH"

PYTHON_BIN="${PYTHON_BIN:-python3}"
if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  PYTHON_BIN=python
fi
if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  echo "[error] python3/python not found"
  exit 1
fi

if [ ! -f "$CONFIG_PATH" ]; then
  echo "[info] Creating default config from template..."
  mkdir -p "$(dirname "$CONFIG_PATH")"
  cp "$TEMPLATE_PATH" "$CONFIG_PATH"
  echo "[next] Please edit: $CONFIG_PATH"
fi

echo "[info] Checking Xcode CLT..."
if ! xcode-select -p >/dev/null 2>&1; then
  echo "[warn] Xcode Command Line Tools not installed. Run: xcode-select --install"
fi

echo "[info] Checking rsync/ssh..."
if ! command -v rsync >/dev/null 2>&1; then
  echo "[warn] rsync not found. If you use Homebrew: brew install rsync"
fi
if ! command -v ssh >/dev/null 2>&1; then
  echo "[warn] ssh not found (unexpected on macOS)."
fi

echo "[info] Running doctor..."
"$PYTHON_BIN" "$BUILD_ROOT/Tools/uebuild.py" --config-path "$CONFIG_PATH" doctor

echo "[ok] Environment ready."

