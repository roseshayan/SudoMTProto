#!/usr/bin/env python3
import os
import sys
import subprocess
import urllib.request
import json
import secrets
import binascii

# ANSI Color Codes for terminal UI
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"

def check_root():
    """Ensure the script is running with root privileges."""
    if os.getuid() != 0:
        print(f"{RED}[!] Error: This script must be run as root.{RESET}")
        print(f"{RED}[!] Please use: sudo python3 installer.py{RESET}")
        sys.exit(1)

def get_latest_mtg_version():
    """Fetch the latest release tag from GitHub API."""
    print(f"{YELLOW}[*] Fetching latest mtg version from GitHub...{RESET}")
    url = "https://api.github.com/repos/9seconds/mtg/releases/latest"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            return data['tag_name']
    except Exception as e:
        print(f"{RED}[!] Failed to fetch latest version: {e}{RESET}")
        print(f"{YELLOW}[*] Falling back to default version: v2.1.7{RESET}")
        return "v2.1.7"

def get_valid_port():
    """Prompt user for a port number and validate it."""
    while True:
        try:
            user_input = input(f"{YELLOW}Enter port number [Default: 443]: {RESET}").strip()
            if not user_input:
                return 443
            
            port = int(user_input)
            if 1 <= port <= 65535:
                return port
            else:
                print(f"{RED}[!] Invalid range. Port must be between 1 and 65535.{RESET}")
        except ValueError:
            print(f"{RED}[!] Invalid input. Please enter a valid integer port number.{RESET}")

def get_valid_domain():
    """Prompt user for a Fake-TLS domain and validate its basic format."""
    while True:
        user_input = input(f"{YELLOW}Enter Fake-TLS domain [Default: cloudflare.com]: {RESET}").strip()
        if not user_input:
            return "cloudflare.com"
        
        # Validation: No spaces, must contain at least one dot, and reasonable length
        if " " not in user_input and "." in user_input and len(user_input) >= 4:
            # Remove protocol if user accidentally included it
            domain = user_input.replace("https://", "").replace("http://", "").split("/")[0]
            return domain
        else:
            print(f"{RED}[!] Invalid domain format. Examples: google.com, cloudflare.com{RESET}")

def download_and_install_mtg(version):
    """Download mtg binary and move it to system PATH."""
    print(f"{YELLOW}[*] Downloading mtg {version}...{RESET}")
    clean_version = version.lstrip('v')
    
    download_url = f"https://github.com/9seconds/mtg/releases/download/{version}/mtg-{clean_version}-linux-amd64.tar.gz"
    archive_path = "/tmp/mtg.tar.gz"
    
    try:
        urllib.request.urlretrieve(download_url, archive_path)
        print(f"{YELLOW}[*] Extracting and installing components...{RESET}")
        
        # Extract archive safely
        subprocess.run(["tar", "-xzf", archive_path, "-C", "/tmp"], check=True)
        
        # Move binary to local bin
        extracted_dir = f"/tmp/mtg-{clean_version}-linux-amd64"
        subprocess.run(["mv", f"{extracted_dir}/mtg", "/usr/local/bin/mtg"], check=True)
        subprocess.run(["chmod", "+x", "/usr/local/bin/mtg"], check=True)
        
        # Clean up tmp files
        if os.path.exists(archive_path):
            os.remove(archive_path)
            
        print(f"{GREEN}[+] mtg core installed successfully.{RESET}")
    except Exception as e:
        print(f"{RED}[!] Critical Error during installation: {e}{RESET}")
        sys.exit(1)

def generate_fake_tls_secret(domain):
    """Generate a valid Fake-TLS secret based on the verified domain."""
    try:
        hex_domain = binascii.hexlify(domain.encode()).decode()
        random_key = secrets.token_hex(16)
        secret = f"ee{random_key}{hex_domain}"
        return secret
    except Exception as e:
        print(f"{RED}[!] Error generating secret: {e}{RESET}")
        sys.exit(1)

def get_public_ip():
    """Retrieve public IP address of the server."""
    urls = ["https://api.ipify.org", "https://ifconfig.me/ip", "https://icanhazip.com"]
    for url in urls:
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=5) as response:
                return response.read().decode().strip()
        except:
            continue
    return "YOUR_SERVER_IP"

def create_systemd_service(secret, port):
    """Create and start systemd service to keep proxy running in background."""
    print(f"{YELLOW}[*] Configuring systemd service...{RESET}")
    
    service_content = f"""[Unit]
Description=MTProxy Telegram (mtg)
After=network.target

[Service]
Type=simple
ExecStart=/usr/local/bin/mtg run {secret} -b 0.0.0.0:{port}
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
"""
    
    service_path = "/etc/systemd/system/mtg.service"
    try:
        with open(service_path, "w") as f:
            f.write(service_content)
        
        # Reload systemd, enable and start service
        subprocess.run(["systemctl", "daemon-reload"], check=True)
        subprocess.run(["systemctl", "enable", "mtg.service"], check=True)
        subprocess.run(["systemctl", "start", "mtg.service"], check=True)
        print(f"{GREEN}[+] Service created and started successfully.{RESET}")
    except Exception as e:
        print(f"{RED}[!] Error configuring systemd: {e}{RESET}")
        sys.exit(1)

def main():
    print(f"{GREEN}==============================================={RESET}")
    print(f"{GREEN}   MTProto Telegram Proxy Auto-Installer v1.0  {RESET}")
    print(f"{GREEN}==============================================={RESET}")
    
    # 1. Verification Checklist
    check_root()
    
    # 2. Interactive Inputs with Strict Validation
    print(f"\n{YELLOW}[*] Configuration Setup:{RESET}")
    port = get_valid_port()
    domain = get_valid_domain()
    
    # 3. System Update & Dependencies Setup
    print(f"\n{YELLOW}[*] Updating system package lists...{RESET}")
    subprocess.run(["apt-get", "update", "-y"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # 4. Deployment Core
    version = get_latest_mtg_version()
    download_and_install_mtg(version)
    
    # 5. Secret & IP Processing
    secret = generate_fake_tls_secret(domain)
    ip = get_public_ip()
    
    # 6. Service Automation
    create_systemd_service(secret, port)
    
    # 7. Print Clean Deployment Results
    telegram_link = f"https://t.me/proxy?server={ip}&port={port}&secret={secret}"
    
    print(f"\n{GREEN}==============================================={RESET}")
    print(f"{GREEN}[+] MTProto Proxy deployed successfully!{RESET}")
    print(f"{YELLOW}Proxy Configuration Details:{RESET}")
    print(f"Server IP : {ip}")
    print(f"Port      : {port}")
    print(f"Secret    : {secret}")
    print(f"Fake Domain: {domain}")
    print(f"\n{YELLOW}Direct Telegram Connection Link:{RESET}")
    print(f"{GREEN}{telegram_link}{RESET}")
    print(f"{GREEN}==============================================={RESET}")

if __name__ == "__main__":
    main()