#!/usr/bin/env bash
set -euo pipefail

# 1. Check if running as root
if [[ "${EUID:-$(id -u)}" -ne 0 ]]; then
  exec sudo -E bash "$0" "$@"
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 2. Optimized Dependency Check: Only run apt-get update if packages are missing
if ! command -v python3 >/dev/null 2>&1 || ! command -v curl >/dev/null 2>&1 || ! command -v tar >/dev/null 2>&1; then
  echo "[*] Missing core dependencies. Updating and installing..."
  apt-get update -y
  apt-get install -y python3 ca-certificates curl tar wget
fi

INSTALLER_PATH="/tmp/sudomtproto_installer.py"

# 4. Cleanup Function: Automatically triggers on exit (success or failure)
cleanup() {
  if [[ -f "$INSTALLER_PATH" && "$SCRIPT_DIR" == "/dev/fd" ]]; then
    rm -f "$INSTALLER_PATH"
  fi
}
trap cleanup EXIT

# 3. Smart execution logic with Fallbacks for restricted networks (Iran)
if [[ "$SCRIPT_DIR" == "/dev/fd" || ! -f "$SCRIPT_DIR/installer.py" ]]; then
  echo "[*] Fetching installer.py from repository..."
  
  # List of alternative URLs (Primary GitHub + Reliable Mirror Proxy for Iran)
  URLS=(
    "https://raw.githubusercontent.com/roseshayan/SudoMTProto/main/installer.py"
    "https://mirror.ghproxy.com/https://raw.githubusercontent.com/roseshayan/SudoMTProto/main/installer.py"
  )
  
  DOWNLOADED=false
  
  for url in "${URLS[@]}"; do
    echo "[*] Trying to fetch from: $url"
    
    # Try with curl first
    if command -v curl >/dev/null 2>&1; then
      if curl -fsSL "$url" -o "$INSTALLER_PATH"; then
        DOWNLOADED=true
        break
      fi
    fi
    
    # Fallback to wget if curl fails or isn't behaving
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