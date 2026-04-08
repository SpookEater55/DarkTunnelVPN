# DarkTunnelVPN

**A simple, dark-themed VPN manager for Nobara OS**

DarkTunnelVPN is a lightweight Python GUI application designed specifically for Nobara OS (Fedora-based). It allows users to easily import, manage, connect, and disconnect OpenVPN (`.ovpn`) and WireGuard (`.conf`) configurations using NetworkManager.

## Features
- Modern dark interface optimized for KDE Plasma
- Import `.ovpn` and `.conf` files directly
- List, connect, and disconnect VPN connections
- One-click installation of required VPN packages
- Full integration with Nobara’s native network settings and system tray

## Installation
1. Install dependencies:
   ```bash
   sudo dnf install -y wireguard-tools NetworkManager-openvpn python3-tkinter
   sudo systemctl restart NetworkManager
      created by spookeater55
