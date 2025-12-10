#!/bin/sh

TARGET_DIR="/etc/hysteria"
TARGET_FILE="$TARGET_DIR/config.yaml"
NO_EDIT=0
SRC_FILE=""

for arg in "$@"; do
  case "$arg" in
    --no-edit) NO_EDIT=1 ;;
    --source=*) SRC_FILE="${arg#--source=}" ;;
  esac
done

mkdir -p "$TARGET_DIR" || { echo "Failed to create $TARGET_DIR" >&2; exit 1; }

if [ -z "$SRC_FILE" ]; then
  SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
  SRC_FILE="$SCRIPT_DIR/../config-obfs.yaml"
fi

cp -p "$SRC_FILE" "$TARGET_FILE" || { echo "Failed to copy $SRC_FILE to $TARGET_FILE" >&2; exit 1; }

chmod 644 "$TARGET_FILE" 2>/dev/null || true
if command -v chown >/dev/null 2>&1; then
  chown root:root "$TARGET_FILE" 2>/dev/null || true
fi

exit 0
