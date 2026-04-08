#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import threading

class DarkTunnelVPN:
    def __init__(self, root):
        self.root = root
        self.root.title("DarkTunnelVPN")
        self.root.geometry("850x560")
        self.root.configure(bg="#121212")

        # Title
        title = tk.Label(root, text="DarkTunnelVPN", font=("Arial", 22, "bold"), 
                        fg="#00ff9d", bg="#121212")
        title.pack(pady=20)

        # Dark Treeview Style
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", background="#1e1e1e", foreground="#e0e0e0", fieldbackground="#1e1e1e", rowheight=28)
        style.configure("Treeview.Heading", background="#2a2a2a", foreground="#00ff9d", font=("Arial", 10, "bold"))
        style.map("Treeview", background=[('selected', '#00ff9d')], foreground=[('selected', 'black')])

        # Treeview for connections
        self.tree = ttk.Treeview(root, columns=("Name", "Type", "Status"), show="headings")
        self.tree.heading("Name", text="Connection Name")
        self.tree.heading("Type", text="Type")
        self.tree.heading("Status", text="Status")
        self.tree.column("Name", width=400)
        self.tree.column("Type", width=140)
        self.tree.column("Status", width=130)
        self.tree.pack(fill="both", expand=True, padx=20, pady=10)

        # Buttons Frame
        btn_frame = tk.Frame(root, bg="#121212")
        btn_frame.pack(pady=15)

        btns = [
            ("Refresh", self.refresh_list),
            ("Connect", self.connect_selected),
            ("Disconnect", self.disconnect_selected),
            ("Import .ovpn / .conf", self.import_config),
            ("Install VPN Support", self.setup_vpn_support)
        ]

        for text, cmd in btns:
            btn = tk.Button(btn_frame, text=text, command=cmd, 
                          font=("Arial", 10, "bold"), bg="#1f1f1f", fg="#00ff9d",
                          activebackground="#00ff9d", activeforeground="black",
                          padx=15, pady=8, relief="flat")
            btn.pack(side="left", padx=8)

        self.status_label = tk.Label(root, text="Ready", fg="#00ff9d", bg="#121212", font=("Arial", 11))
        self.status_label.pack(pady=10)

        self.refresh_list()

    def run_command(self, cmd, sudo=False):
        if sudo:
            cmd = ["sudo"] + cmd
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            return f"Error: {e.stderr.strip()}"

    def get_connections(self):
        try:
            output = subprocess.check_output(["nmcli", "-t", "-f", "NAME,TYPE,UUID", "connection", "show"], text=True)
            connections = []
            for line in output.strip().splitlines():
                if not line: continue
                parts = line.split(':', 2)
                if len(parts) == 3:
                    name, conn_type, uuid = parts
                    if conn_type.lower() in ['wireguard', 'vpn']:
                        connections.append((name, conn_type, uuid))

            active_output = subprocess.check_output(["nmcli", "-t", "-f", "NAME,TYPE,UUID", "connection", "show", "--active"], text=True)
            active = {line.split(':', 2)[0] for line in active_output.strip().splitlines() if line}

            result = []
            for name, ctype, uuid in connections:
                status = "Connected" if name in active else "Disconnected"
                result.append((name, ctype, status, uuid))
            return result
        except:
            return []

    def refresh_list(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        conns = self.get_connections()
        for name, ctype, status, uuid in conns:
            self.tree.insert("", "end", values=(name, ctype, status), tags=(uuid,))

    def connect_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("DarkTunnelVPN", "Please select a VPN connection.")
            return
        name = self.tree.item(selected[0])['values'][0]
        threading.Thread(target=self._connect, args=(name,), daemon=True).start()

    def _connect(self, name):
        self.status_label.config(text=f"Connecting to {name}...", fg="#ffaa00")
        self.run_command(["nmcli", "connection", "up", name])
        self.refresh_list()
        self.status_label.config(text=f"Connected to {name}", fg="#00ff9d")

    def disconnect_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("DarkTunnelVPN", "Please select a VPN connection.")
            return
        name = self.tree.item(selected[0])['values'][0]
        threading.Thread(target=self._disconnect, args=(name,), daemon=True).start()

    def _disconnect(self, name):
        self.status_label.config(text=f"Disconnecting {name}...", fg="#ffaa00")
        self.run_command(["nmcli", "connection", "down", name])
        self.refresh_list()
        self.status_label.config(text="Disconnected", fg="#00ff9d")

    def import_config(self):
        file_path = filedialog.askopenfilename(
            title="Select VPN Config",
            filetypes=[("VPN Configs", "*.ovpn *.conf"), ("OpenVPN", "*.ovpn"), ("WireGuard", "*.conf")]
        )
        if not file_path:
            return

        conn_type = "openvpn" if file_path.endswith('.ovpn') else "wireguard"
        self.status_label.config(text="Importing configuration...", fg="#ffaa00")
        
        result = self.run_command(["nmcli", "connection", "import", "type", conn_type, "file", file_path])
        
        if "successfully" in result.lower():
            messagebox.showinfo("DarkTunnelVPN", "Configuration imported successfully!")
            self.refresh_list()
        else:
            messagebox.showerror("Import Failed", result)

    def setup_vpn_support(self):
        if messagebox.askyesno("DarkTunnelVPN", "Install WireGuard & OpenVPN support?"):
            self.status_label.config(text="Installing packages...", fg="#ffaa00")
            result = self.run_command(["dnf", "install", "-y", "wireguard-tools", "NetworkManager-openvpn"], sudo=True)
            messagebox.showinfo("Success", "VPN support installed!")
            self.status_label.config(text="Ready", fg="#00ff9d")

if __name__ == "__main__":
    root = tk.Tk()
    app = DarkTunnelVPN(root)
    root.mainloop()
