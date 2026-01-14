#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUILD_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PROJECT_ROOT="$(cd "$BUILD_ROOT/.." && pwd)"

SRC="$BUILD_ROOT/Extras/UEBuildSDKPlugin/UEBuildSDK"
DST="$PROJECT_ROOT/Plugins/UEBuildSDK"

if [ ! -d "$SRC" ]; then
  echo "[error] Plugin source not found: $SRC" >&2
  exit 1
fi

mkdir -p "$DST"
rsync -a --delete "$SRC/" "$DST/"

echo "[ok] Installed. Enable plugin in Editor: Plugins -> UE Build SDK"

