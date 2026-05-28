#!/usr/bin/env bash
set -euo pipefail

if [[ "${EUID:-$(id -u)}" -ne 0 ]]; then
  exec sudo -E bash "$0" "$@"
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if ! command -v python3 >/dev/null 2>&1; then
  echo "[*] python3 not found. Installing dependencies..."
  apt-get update
  apt-get install -y python3 ca-certificates curl tar
fi

if [[ ! -f "$SCRIPT_DIR/installer.py" ]]; then
  echo "[!] installer.py not found in: $SCRIPT_DIR"
  exit 1
fi

python3 "$SCRIPT_DIR/installer.py"
