# Static IP Configuration for LG VM Bridged Interface

LG VMs use DHCP on the bridged interface, causing IP drift on every reboot. Set a static IP to ensure the agent can always find the rig.

## Identify the bridged interface

```bash
sshpass -p 'lg' ssh lg@<current-ip> 'ip addr show | grep "inet 192.168"'
```

This shows which interface has the 192.168.x.x address. Usually `enp0s8` or `enp0s9`.

## Set static IP via /etc/network/interfaces

```bash
sshpass -p 'lg' ssh lg@<current-ip> 'sudo cp /etc/network/interfaces /etc/network/interfaces.backup'

# Write new config
sudo tee /etc/network/interfaces << 'CONFIG'
# interfaces(5) file used by ifup(8) and ifdown(8)
auto lo
iface lo inet loopback

# NAT (internet access)
auto enp0s3
iface enp0s3 inet dhcp

# Bridged LAN - static IP
auto enp0s8
iface enp0s8 inet static
    address 192.168.1.12
    netmask 255.255.255.0
    gateway 192.168.1.1
    dns-nameservers 8.8.8.8 1.1.1.1
CONFIG
```

## Apply without reboot

```bash
sudo ifdown enp0s8 && sudo ifup enp0s8
```

Or reboot to confirm the static IP persists.

## Update all references

After changing the IP, update it in:
- Memory (`LG credentials: IP=...`)
- `/home/nara/wm-collector/run.py` (LG_IP constant)
- `/home/nara/wm-collector/news_storyteller.py` (LG_IP constant)
- Any cron job scripts that reference the old IP
