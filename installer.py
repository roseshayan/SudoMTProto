#!/usr/bin/env python3
import os
import sys
import subprocess
import urllib.request
import json
import secrets
import binascii
import platform

GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"

def check_root():
    if os.getuid() != 0:
        print(f"{RED}[!] Error: This script must be run as root.{RESET}")
        print(f"{RED}[!] Please use: sudo python3 installer.py{RESET}")
        sys.exit(1)

def require_packages():
    print(f"{YELLOW}[*] Checking and installing required core packages...{RESET}")
    try:
        subprocess.run(["apt-get", "update", "-y"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["apt-get", "install", "-y", "ca-certificates", "curl", "tar"], check=True, stdout=subprocess.DEVNULL)
    except Exception as e:
        print(f"{RED}[!] Warning: Package manager busy or failed: {e}{RESET}")

def get_latest_mtg_version():
    print(f"{YELLOW}[*] Fetching latest mtg version from GitHub...{RESET}")
    url = "https://api.github.com/repos/9seconds/mtg/releases/latest"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            return data['tag_name']
    except Exception as e:
        print(f"{RED}[!] Failed to fetch latest version: {e}{RESET}")
        print(f"{YELLOW}[*] Falling back to default version: v2.2.8{RESET}")
        return "v2.2.8"

def get_valid_port():
    while True:
        try:
            user_input = input(f"{YELLOW}Enter port number [Default: 443]: {RESET}").strip()
            if not user_input:
                return 443
            port = int(user_input)
            if 1 <= port <= 65535:
                return port
            print(f"{RED}[!] Invalid range. Port must be between 1 and 65535.{RESET}")
        except ValueError:
            print(f"{RED}[!] Invalid input. Please enter a valid integer port number.{RESET}")

def get_valid_domain():
    while True:
        user_input = input(f"{YELLOW}Enter Fake-TLS domain [Default: google.com, type 'none' to skip]: {RESET}").strip()
        if not user_input:
            return "google.com"
        if user_input.lower() == 'none':
            return None
        domain = user_input.replace("https://", "").replace("http://", "").split("/")[0]
        if " " not in domain and "." in domain and len(domain) >= 4:
            return domain
        print(f"{RED}[!] Invalid domain format. Examples: google.com, github.com{RESET}")

def detect_arch():
    machine = platform.machine().lower()
    if machine in ("x86_64", "amd64"):
        return "amd64"
    if machine in ("aarch64", "arm64"):
        return "arm64"
    return "amd64"

def download_and_install_mtg(version):
    arch = detect_arch()
    clean_version = version.lstrip('v')
    print(f"{YELLOW}[*] Downloading mtg {version} for {arch}...{RESET}")

    download_url = f"https://github.com/9seconds/mtg/releases/download/{version}/mtg-{clean_version}-linux-{arch}.tar.gz"
    archive_path = "/tmp/mtg.tar.gz"

    try:
        urllib.request.urlretrieve(download_url, archive_path)
        print(f"{YELLOW}[*] Extracting and installing components...{RESET}")
        subprocess.run(["tar", "-xzf", archive_path, "-C", "/tmp"], check=True)
        extracted_dir = f"/tmp/mtg-{clean_version}-linux-{arch}"
        subprocess.run(["install", "-m", "0755", f"{extracted_dir}/mtg", "/usr/local/bin/mtg"], check=True)
        if os.path.exists(archive_path):
            os.remove(archive_path)
        print(f"{GREEN}[+] mtg core installed successfully.{RESET}")
    except Exception as e:
        print(f"{RED}[!] Critical Error during installation: {e}{RESET}")
        sys.exit(1)

def optimize_network_performance():
    print(f"{YELLOW}[*] Optimizing Linux network stack and enabling BBR...{RESET}")
    try:
        sysctl_params = [
            "net.core.default_qdisc=fq\n",
            "net.ipv4.tcp_congestion_control=bbr\n",
            "net.ipv4.tcp_rmem=4096 87380 16777216\n",
            "net.ipv4.tcp_wmem=4096 65536 16777216\n"
        ]
        with open("/etc/sysctl.conf", "r") as f:
            current_lines = f.readlines()
        is_updated = False
        for param in sysctl_params:
            key = param.split("=")[0]
            if not any(key in line for line in current_lines):
                current_lines.append(param)
                is_updated = True
        if is_updated:
            with open("/etc/sysctl.conf", "w") as f:
                f.writelines(current_lines)
            subprocess.run(["sysctl", "-p"], check=True, stdout=subprocess.DEVNULL)
            print(f"{GREEN}[+] BBR congestion control and network buffers optimized.{RESET}")
    except Exception:
        print(f"{RED}[!] Warning: Could not apply network optimizations.{RESET}")

def generate_secret(domain):
    """Generates a secure secret. If domain is None, prefixes with 'dd' for raw padded mode."""
    try:
        random_key = secrets.token_hex(16)
        if domain is None:
            return f"dd{random_key}"  # Raw Obfuscated mode with random padding indicator
        
        hex_domain = binascii.hexlify(domain.encode()).decode()
        return f"ee{random_key}{hex_domain}"  # Fake-TLS mode indicator
    except Exception as e:
        print(f"{RED}[!] Error generating secret: {e}{RESET}")
        sys.exit(1)

def get_public_ip():
    urls = ["https://api.ipify.org", "https://ifconfig.me/ip", "https://icanhazip.com"]
    for url in urls:
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=5) as response:
                return response.read().decode().strip()
        except Exception:
            continue
    return "YOUR_SERVER_IP"

def create_systemd_service(secret, port):
    print(f"{YELLOW}[*] Configuring systemd service...{RESET}")
    service_content = f"""[Unit]
Description=MTProxy Telegram (mtg)
Documentation=https://github.com/9seconds/mtg
After=network.target

[Service]
Type=simple
ExecStart=/usr/local/bin/mtg simple-run 0.0.0.0:{port} {secret}
Restart=always
RestartSec=3
LimitNOFILE=65536

[Install]
WantedBy=multi-user.target
"""
    service_path = "/etc/systemd/system/mtg.service"
    try:
        with open(service_path, "w", encoding="utf-8") as f:
            f.write(service_content)
        subprocess.run(["systemctl", "daemon-reload"], check=True)
        subprocess.run(["systemctl", "enable", "mtg.service"], check=True)
        subprocess.run(["systemctl", "restart", "mtg.service"], check=True)
        print(f"{GREEN}[+] Service created and started successfully.{RESET}")
    except Exception as e:
        print(f"{RED}[!] Error configuring systemd: {e}{RESET}")
        sys.exit(1)

def install_flow():
    print(f"\n{YELLOW}[*] Starting Installation Flow...{RESET}")
    require_packages()
    port = get_valid_port()
    domain = get_valid_domain()

    version = get_latest_mtg_version()
    download_and_install_mtg(version)
    optimize_network_performance()

    secret = generate_secret(domain)
    ip = get_public_ip()
    create_systemd_service(secret, port)

    telegram_link = f"https://t.me/proxy?server={ip}&port={port}&secret={secret}"

    print(f"\n{GREEN}==============================================={RESET}")
    print(f"{GREEN}[+] MTProto Proxy deployed successfully!{RESET}")
    print(f"{YELLOW}Proxy Configuration Details:{RESET}")
    print(f"Server IP  : {ip}")
    print(f"Port       : {port}")
    print(f"Secret     : {secret}")
    print(f"Mode       : { 'Fake-TLS (' + domain + ')' if domain else 'Raw Obfuscated (dd-secret)' }")
    print(f"\n{YELLOW}Direct Telegram Connection Link:{RESET}")
    print(f"{GREEN}{telegram_link}{RESET}")
    print(f"==============================================={RESET}")

def view_logs():
    print(f"{YELLOW}[*] Fetching live proxy logs (Press Ctrl+C to exit logs)...{RESET}\n")
    try:
        subprocess.run(["journalctl", "-u", "mtg", "-f"])
    except KeyboardInterrupt:
        print(f"\n{YELLOW}[*] Exited log view.{RESET}")

def check_status():
    print(f"\n{YELLOW}[*] Checking MTProto Service Status...{RESET}")
    subprocess.run(["systemctl", "status", "mtg"])

def uninstall_proxy():
    confirm = input(f"{RED}[!] Are you sure you want to completely remove SudoMTProto? (y/N): {RESET}").strip().lower()
    if confirm == 'y':
        print(f"{YELLOW}[*] Stopping and disabling service...{RESET}")
        subprocess.run(["systemctl", "stop", "mtg.service"], stderr=subprocess.DEVNULL)
        subprocess.run(["systemctl", "disable", "mtg.service"], stderr=subprocess.DEVNULL)
        
        print(f"{YELLOW}[*] Removing files...{RESET}")
        if os.path.exists("/etc/systemd/system/mtg.service"):
            os.remove("/etc/systemd/system/mtg.service")
        if os.path.exists("/usr/local/bin/mtg"):
            os.remove("/usr/local/bin/mtg")
            
        subprocess.run(["systemctl", "daemon-reload"], check=True)
        print(f"{GREEN}[+] MTProto Proxy uninstalled successfully.{RESET}")
    else:
        print(f"{YELLOW}[*] Uninstallation cancelled.{RESET}")

def main():
    check_root()
    while True:
        print(f"\n{GREEN}==============================================={RESET}")
        print(f"{GREEN}       SudoMTProto Management Dashboard        {RESET}")
        print(f"{GREEN}==============================================={RESET}")
        print("1) Install / Reinstall MTProto Proxy")
        print("2) View Live Service Logs (Troubleshooting)")
        print("3) Check Proxy Service Status")
        print("4) Completely Uninstall Proxy")
        print("5) Exit Dashboard")
        print(f"{GREEN}==============================================={RESET}")
        
        choice = input(f"{YELLOW}Select an option [1-5]: {RESET}").strip()
        
        if choice == '1':
            install_flow()
        elif choice == '2':
            view_logs()
        elif choice == '3':
            check_status()
        elif choice == '4':
            uninstall_proxy()
        elif choice == '5':
            print(f"{GREEN}[+] Goodbye!{RESET}")
            break
        else:
            print(f"{RED}[!] Invalid choice. Please enter a number between 1 and 5.{RESET}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{RED}[!] Script terminated by user.{RESET}")
        sys.exit(0)