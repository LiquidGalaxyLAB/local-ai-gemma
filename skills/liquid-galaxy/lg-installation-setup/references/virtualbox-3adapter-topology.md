# VirtualBox 3-Adapter Network Topology

Discovered during a Session LG installation on a 3-VM VirtualBox cluster
(July 2026).

## Adapter Configuration per VM

| Adapter | VirtualBox Type | Ubuntu Iface | Purpose | IP Config |
|---------|----------------|-------------|---------|-----------|
| 1 | NAT | `enp0s3` | Internet (apt, install.sh downloads) | `10.0.2.x` DHCP — default gateway via `10.0.2.1` |
| 2 | Host-only or Internal Network | `enp0s8` | LG internal (ViewSync, frame-to-frame SSH) | Static — e.g. `192.168.53.3/24` |
| 3 | Bridged | `enp0s9` | Agent/Pi SSH access from LAN | DHCP or static — `192.168.1.x/24` via `192.168.1.1` |

## Actual IPs Used

| Machine | enp0s3 (NAT) | enp0s8 (Internal) | enp0s9 (Bridged) |
|---------|-------------|-------------------|-----------------|
| lg1 (master) | 10.0.2.11 | 192.168.53.3 | 192.168.1.7 |
| lg2 (slave) | 10.0.2.x | 192.168.53.2 | 192.168.1.8 |
| lg3 (slave) | 10.0.2.x | 192.168.53.1 | ? |

## Network Configuration Files

### `/etc/network/interfaces` (lg1)

```
# interfaces(5) file used by ifup(8) and ifdown(8)
auto lo
iface lo inet loopback

# NAT - internet access (DHCP)
auto enp0s3
iface enp0s3 inet dhcp

# LG internal network (static)
auto enp0s8
iface enp0s8 inet static
  address 192.168.53.3
  netmask 255.255.255.0

# Bridged - remote access (static)
auto enp0s9
iface enp0s9 inet static
  address 192.168.1.7
  netmask 255.255.255.0
  gateway 192.168.1.1
```

### Persistent DNS (`/etc/resolvconf/resolv.conf.d/head`)

```
nameserver 8.8.8.8
nameserver 1.1.1.1
```

### Hostname

Default from Ubuntu 16.04 + VirtualBox: `lg1-VirtualBox`
Fixed to: `lg1`
Also fix `/etc/hosts` to match.

## Key Observations

1. **install.sh auto-detects the wrong IP.** The script uses `NETWORK_INTERFACE` from the default route, which is `enp0s3` (NAT). The shown IP (e.g. 10.0.2.11) is not reachable from the LAN. After install, `hostname -I` gives the actual reachable IPs.

2. **SSH not installed by default.** openssh-server must be installed from the VM console before the agent can connect.

3. **EOL repos.** Ubuntu 16.04 archive repos are dead. Must use `old-releases.ubuntu.com` before any apt operation.

4. **apt-get is slow.** Through VirtualBox NAT, apt-get update can take 2-5 minutes. Background processes with `notify_on_complete` are recommended.

5. **Cross-VM SSH needs sshpass.** The install script's SSH key distribution often fails on VirtualBox. `sshpass` must be installed on lg1 to reach lg2/lg3 from within the internal network.

6. **Agent tool guard blocks `echo | sudo -S`.** All privileged operations must use the helper-script pattern: write locally, scp to VM, then remote bash.
