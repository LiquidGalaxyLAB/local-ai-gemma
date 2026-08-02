# VM Bridged LAN: Network Fix + Earth Dialog Dismiss

## Problem: No Internet on VM

On VirtualBox VM rigs with bridged LAN, the default route may point to the
internal network (`255.255.255.0` via `enp0s8`) instead of the LAN gateway.
This blocks internet access on the VM, causing Google Earth to show
"cannot contact login server" on every launch.

### Symptoms
- `ip route show` shows `default via 255.255.255.0 dev enp0s8`
- `ping google.com` fails
- `/etc/resolv.conf` is empty
- Earth shows login dialog every time

## Fix 1: Temporary (lives until reboot)

SCP a helper to lg1 and run:

```bash
sshpass -p 'lg' scp fix-vm-network.sh lg@<LG-IP>:/home/lg/
sshpass -p 'lg' ssh lg@<LG-IP> "bash /home/lg/fix-vm-network.sh"
```

Helper script (`fix-vm-network.sh`):
```bash
#!/bin/bash
echo "lg" | sudo -S route del default 2>/dev/null
echo "lg" | sudo -S route add default gw 192.168.1.1 dev enp0s9
echo "lg" | sudo -S bash -c 'echo nameserver 8.8.8.8 > /etc/resolv.conf'
```

## Fix 2: Permanent (survives reboot)

Edit `/etc/network/interfaces` on lg1 to add the gateway to the LAN interface:

```bash
# Add to the enp0s9 (bridged LAN) stanza:
gateway 192.168.1.1
dns-nameservers 8.8.8.8 1.1.1.1
```

## Fix 3: Auto-Dismiss the Earth Login Dialog

Even without internet, Earth works fine after dismissing the dialog. Install
the dismiss script as an autostart entry:

**1. Deploy script + autostart entry:**
```bash
sshpass -p 'lg' scp dismiss-earth-dialogs.py lg@<LG-IP>:/home/lg/
```

**2. Create autostart .desktop file on lg1:**
```bash
echo 'lg' | sudo -S tee /home/lg/.config/autostart/dismiss-earth-dialogs.desktop > /dev/null <<'EOF'
[Desktop Entry]
Type=Application
Name=Dismiss Earth Dialogs
Exec=sh -c "sleep 10 && DISPLAY=:0 python3 /home/lg/dismiss-earth-dialogs.py"
Terminal=false
X-GNOME-Autostart-enabled=true
EOF
```

**3.** Relaunch Earth once. The dialog auto-dismisses ~10s after Earth starts.

The autostart entry is in `lg-kml-tours` skill at `scripts/dismiss-earth-dialogs.py`.

## Verification

```bash
# Check route
sshpass -p 'lg' ssh lg@<LG-IP> "ip route show | grep default"
# Expected: default via 192.168.1.1 dev enp0s9

# Check internet
sshpass -p 'lg' ssh lg@<LG-IP> "ping -c 1 google.com"
# Expected: 1 packets transmitted, 1 received, 0% packet loss
```
