#!/usr/bin/env bash
set -euo pipefail

# Check if running as root
if [[ "${EUID:-$(id -u)}" -ne 0 ]]; then
  exec sudo -E bash "$0" "$@"
fi

# Detect execution directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Ensure initial packages for download and python are available
if ! command -v python3 >/dev/null 2>&1 || ! command -v curl >/dev/null 2>&1; then
  echo "[*] Core dependencies missing. Installing python3 and curl..."
  apt-get update
  apt-get install -y python3 ca-certificates curl tar
fi

# Smart check: If running via curl/pipe or installer.py is missing locally
if [[ "$SCRIPT_DIR" == "/dev/fd" || ! -f "$SCRIPT_DIR/installer.py" ]]; then
  echo "[*] Running installer from remote repository..."
  INSTALLER_PATH="/tmp/sudomtproto_installer.py"
  
  # Download installer.py from your main GitHub branch
  curl -fsSL "https://raw.githubusercontent.com/roseshayan/SudoMTProto/main/installer.py" -o "$INSTALLER_PATH"
else
  # Running from a locally cloned repository
  echo "[*] Running installer from local repository..."
  INSTALLER_PATH="$SCRIPT_DIR/installer.py"
fi

# Execute the python installation core
python3 "$INSTALLER_PATH"