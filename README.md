# SudoMTProto

Intelligent MTProto Telegram Proxy Installer for Ubuntu Linux servers.

SudoMTProto automatically installs and configures a high-performance MTProto proxy using `mtg`, creates a systemd service, generates a valid Fake-TLS secret, and provides a direct Telegram connection link.

---

# Features

- Automatic MTProto proxy deployment
- Uses modern `mtg` core
- Automatic Fake-TLS secret generation
- Systemd service auto configuration
- Auto-detect public IP
- Interactive installer
- Easy deployment
- Lightweight and fast
- Production-ready base structure

---

# Supported Systems

- Ubuntu 20.04+
- Ubuntu 22.04+
- Debian-based Linux servers
- AMD64 / x86_64

---

# Quick Install (Recommended)

Run this command on your server:

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/roseshayan/SudoMTProto/main/install.sh)
```

Or using wget:

```bash
bash <(wget -qO- https://raw.githubusercontent.com/roseshayan/SudoMTProto/main/install.sh)
```

---

# Manual Installation

## 1. Install dependencies

```bash
apt update
apt install -y git python3 curl wget
```

## 2. Clone repository

```bash
git clone https://github.com/roseshayan/SudoMTProto.git
```

## 3. Enter project directory

```bash
cd SudoMTProto
```

## 4. Run installer

```bash
chmod +x installer.py
sudo python3 installer.py
```

---

# Configuration

During installation you will be asked for:

## Port

Default:
```text
443
```

## Fake-TLS Domain

Default:
```text
cloudflare.com
```

Examples:

- google.com
- cloudflare.com
- amazon.com
- microsoft.com

---

# After Installation

The installer prints:

- Server IP
- Port
- Secret
- Fake-TLS domain
- Direct Telegram proxy link

Example:

```text
https://t.me/proxy?server=1.2.3.4&port=443&secret=YOUR_SECRET
```

Open the generated link inside Telegram.

---

# Service Management

## Check status

```bash
systemctl status mtg
```

## Restart service

```bash
systemctl restart mtg
```

## Stop service

```bash
systemctl stop mtg
```

## View logs

```bash
journalctl -u mtg -f
```

---

# Uninstall

```bash
systemctl stop mtg
systemctl disable mtg
rm -f /etc/systemd/system/mtg.service
rm -f /usr/local/bin/mtg
systemctl daemon-reload
```

---

# Performance

Actual capacity depends on:

- VPS CPU power
- Network quality
- Bandwidth
- Server location
- ISP filtering
- Latency

Approximate real-world capacity:

| VPS Type | Estimated Concurrent Users |
|---|---|
| 1 GB RAM VPS | 300 - 1200 |
| 2 GB RAM VPS | 2000 - 5000 |
| Dedicated Server | 10000+ |

`mtg` itself is very lightweight. Network quality is usually the main bottleneck.

---

# Security Recommendations

Recommended:

- Use port 443
- Use high-quality VPS providers
- Enable firewall
- Disable SSH password login
- Use SSH keys
- Keep system updated

---

# Project Structure

```text
SudoMTProto/
├── installer.py
├── install.sh
├── README.md
└── README_FA.md
```

---

# Future Improvements

Planned features:

- Docker support
- Docker Compose
- ARM support
- IPv6 support
- Web panel
- Auto-update
- Multi-user support
- Metrics & monitoring
- Fail2Ban integration
- System tuning

---

# License

MIT License
