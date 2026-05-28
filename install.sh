#!/usr/bin/env bash
set -euo pipefail

# 1. Check if running as root
if [[ "${EUID:-$(id -u)}" -ne 0 ]]; then
  exec sudo -E bash "$0" "$@"
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 2. Optimized Dependency Check
if ! command -v python3 >/dev/null 2>&1 || ! command -v curl >/dev/null 2>&1 || ! command -v tar >/dev/null 2>&1; then
  echo "[*] Missing core dependencies. Updating and installing..."
  apt-get update -y
  apt-get install -y python3 ca-certificates curl tar wget
fi

INSTALLER_PATH="/tmp/sudomtproto_installer.py"

# 4. Cleanup Function
cleanup() {
  if [[ -f "$INSTALLER_PATH" && "$SCRIPT_DIR" == "/dev/fd" ]]; then
    rm -f "$INSTALLER_PATH"
  fi
}
trap cleanup EXIT

# 3. Smart execution logic with Cache-Busting and Fallbacks
if [[ "$SCRIPT_DIR" == "/dev/fd" || ! -f "$SCRIPT_DIR/installer.py" ]]; then
  echo "[*] Fetching installer.py from repository..."
  
  # Generate a timestamp to bypass GitHub CDN Cache
  CACHE_BUSTER=$(date +%s)
  
  URLS=(
    "https://raw.githubusercontent.com/roseshayan/SudoMTProto/main/installer.py?v=$CACHE_BUSTER"
    "https://mirror.ghproxy.com/https://raw.githubusercontent.com/roseshayan/SudoMTProto/main/installer.py?v=$CACHE_BUSTER"
  )
  
  DOWNLOADED=false
  
  for url in "${URLS[@]}"; do
    echo "[*] Trying to fetch from: $url"
    
    if command -v curl >/dev/null 2>&1; then
      if curl -fsSL "$url" -o "$INSTALLER_PATH"; then
        DOWNLOADED=true
        break
      fi
    fi
    
    if command -v wget >/dev/null 2>&1; then
      if wget -qO "$INSTALLER_PATH" "$url"; then
        DOWNLOADED=true
        break
      fi
    fi
  done

  if [ "$DOWNLOADED" = false ]; then
    echo "[!] Error: Unable to download installer.py from all available sources."
    exit 1
  fi
else
  echo "[*] Running installer from local repository..."
  INSTALLER_PATH="$SCRIPT_DIR/installer.py"
fi

# Run the python installation core safely
python3 "$INSTALLER_PATH"