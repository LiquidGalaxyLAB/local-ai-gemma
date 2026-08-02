---
name: lg-vm-network-setup
description: Network topology and SSH tunnel setup for connecting to a Liquid Galaxy VM through a laptop bridge.
---

# LG VM Network Setup

## Topology

### External Host Topology (VirtualBox on separate x86 machine)
```
Raspberry Pi (Nara/Agent) --wlan0: 192.168.1.29-- Laptop: 192.168.1.3 -- LG VM: 192.168.53.3

> ⚠️ **These IPs change on DHCP.** Verify Pi IP with `hostname -I` and laptop IP with `ping <laptop-ip>` before each session. Edit this skill when they change.
```

- **Pi (Nara):** 192.168.1.29 (wlan0) — runs the Hermes agent (DHCP, may change)
- **Laptop:** 192.168.1.3 — bridges between Pi's subnet and LG VM's subnet (DHCP, may change)
- **LG VM:** 192.168.53.3 — the Liquid Galaxy VM running on the laptop (should be static)

### Local KVM Topology (QEMU VMs running directly on Pi)
When VMs run on the Pi itself (via qemu-system-aarch64 + KVM), no external bridge is needed:

```
Pi (Hermes Agent + KVM host) — QEMU VMs on internal NAT network
  ├── lg1 (master): 10.42.69.1 — Apache, Earth, ViewSync send
  ├── lg2 (slave):  10.42.69.2 — Earth, ViewSync receive, yawOffset=-36.5
  └── lg3 (slave):  10.42.69.3 — Earth, ViewSync receive, yawOffset=+36.5
```

Each VM connects to the Pi via SSH through port forwarding rules set up in QEMU's user-mode networking (`-netdev user,hostfwd=...`).

## Port Forwarding Rules

### External Host Topology (VirtualBox on laptop)

| Service | VM | Port (Host) | Port (VM) |
|---------|----|-------------|-----------|
| SSH | lg1 | 2222 | 22 |
| Apache | lg1 | 8081 | 81 |
| SSH | lg2 | 2223 | 22 |
| SSH | lg3 | 2224 | 22 |

### Local KVM Topology (QEMU on Pi)

| Service | VM | Port (Pi host) | Port (VM) |
|---------|----|----------------|-----------|
| SSH | lg1 | 2222 | 22 |
| Apache | lg1 | 8081 | 81 |
| SSH | lg2 | 2223 | 22 |
| SSH | lg3 | 2224 | 22 |

Connection from the agent: `ssh -p 2222 lg@localhost` → lg1, `ssh -p 2223 lg@localhost` → lg2, etc.

## Establishing Connection (Reverse Tunnel Mode)

1. **From the laptop**, run:
   ```bash
   ssh -R 2222:192.168.53.3:22 nara@192.168.1.29 -fN
   ```
   This makes the Pi listen on localhost:2222. Connections there tunnel through the laptop to the LG VM's port 22.

2. **From the Pi (Nara)**, connect:
   ```bash
   ssh -p 2222 lg@localhost
   ```
   Password: `lg`

## Troubleshooting

- **SSH connection refused on fresh VMs:** Ubuntu 16.04 often doesn't have SSH installed or running. From the VM console: first fix EOL repos (`sudo sed -i 's/archive.ubuntu.com/old-releases.ubuntu.com/g' /etc/apt/sources.list && sudo sed -i 's/security.ubuntu.com/old-releases.ubuntu.com/g' /etc/apt/sources.list`), then `sudo apt-get clean && sudo apt-get update && sudo apt-get install -y openssh-server && sudo service ssh start && sudo update-rc.d ssh enable`. See `lg-installation-setup` skill for the full EOL repo fix.
- **Bridge machine (laptop) not on network:** Before setting up the tunnel, verify the laptop is on the same subnet. Run `ping 192.168.1.3` from the Pi. If unreachable, bring the laptop onto the same WiFi/LAN.
- **Pi IP changed:** Run `hostname -I` on the Pi. The tunnel command on the laptop must target the current Pi IP, not a hardcoded one.
- If the LG VM can't reach the Pi, it's because they're on different subnets (192.168.53.x vs 192.168.1.x). The laptop must bridge the connection.
- Verify tunnel is up: `ssh -p 2222 -o ConnectTimeout=5 lg@localhost`
- If connection refused, the laptop needs to re-run the reverse tunnel command.
- **VM pingable but all ports closed:** The VM is on the network but no services are listening. The most common cause is a fresh Ubuntu install with no SSH server. See first entry above.

### NAT-Only Slave Topology (Simplest, Slaves Reachable Only Through Master)

In this topology, only **lg1 (master)** has extra adapters (host-only + bridged). The slaves (lg2, lg3) have **only a single NAT adapter** (enp0s3) and are NOT directly reachable from the Pi/agent or the LAN. They communicate with the master and the outside world through VirtualBox's internal NAT Network (10.0.2.x), where all VMs on the same NAT Network can reach each other.

```text
Pi (Nara/Agent) --wlan0: 192.168.1.x
  │
  └── lg1 (master) --3 adapters-- 
        enp0s3: 10.0.2.11 (NAT - internet)
        enp0s8: 192.168.53.3 (Host-only - LG internal, static)  
        enp0s9: 192.168.1.7 (Bridged - agent access, static)
        │
        ├── SSH jumpbox to lg2: sshpass -p 'lg' ssh lg2@10.0.2.12
        │
        └── SSH jumpbox to lg3: sshpass -p 'lg' ssh lg3@10.0.2.13

Internal VirtualBox NAT Network (10.0.2.x):
  ├── lg1: 10.0.2.11  (master, has extra adapters)
  ├── lg2: 10.0.2.12  (slave, NAT only)
  └── lg3: 10.0.2.13  (slave, NAT only)
```

**Reaching slaves from the agent — always through the master:**
```bash
# From the agent/Pi, SSH to master, then jump to slave
sshpass -p 'lg' ssh -o StrictHostKeyChecking=no lg1@<lg1-ip> \
  'sshpass -p "lg" ssh -o StrictHostKeyChecking=no lg2@10.0.2.12 "hostname"'
```

**Reaching slaves directly from the agent — NOT possible.**
The NAT adapter (10.0.2.x) is VirtualBox-internal and not routable from the LAN or the Pi.

**When to use this topology:**
- You only need one VM (the master) to be externally accessible
- You want a simpler VirtualBox setup (fewer adapters per VM)
- You're okay with the agent always using the master as a jumpbox
- The VMs can reach each other through the NAT Network (no host-only adapter needed for inter-VM communication)

**Prerequisites:**
- All VMs on the **same VirtualBox NAT Network** (not separate NAT adapters)
- sshpass installed on lg1 (the master)
- SSH running on all VMs (see lg-installation-setup skill for fixing EOL repos and installing openssh-server)
- Username/password may vary per VM if the user chose different names during Ubuntu install (e.g. `lg1`, `lg2`, `lg3` instead of `lg`)

**Pitfalls:**
- **Slave IPs are DHCP on the NAT network.** VirtualBox's NAT DHCP gives predictable sequential IPs based on VM creation order (10.0.2.4, 10.0.2.5, ...), but if VMs are started in a different order, IPs can shift. The 10.0.2.1x range used here was stable across this session.
- **No direct agent-to-slave file transfer.** All scp/rsync to slaves goes through the master: `scp` to lg1, then `sshpass scp` from lg1 to the slave.
- **LG install.sh on slaves** must have the master's NAT IP (10.0.2.11) as the "master machine IP" — not the bridged IP — because slaves can only reach the master through the NAT network.
- **Ubuntu usernames** on this rig were `lg1`, `lg2`, `lg3` (not the standard `lg`). The LG install script refers to `$HOME` paths that assume `/home/lg`. Files owned by `lg1` may need chown adjustments. Always verify: `whoami`, `echo $HOME`, `cat /etc/passwd | grep $(whoami)`.

### Bridged Direct LAN Topology (VM on Agent's Subnet)

When each VM has a **bridged adapter** on the same LAN as the Pi/agent, no tunnel is needed — the agent SSHes directly to each VM by IP:

```text
Pi (Nara/Agent) --wlan0: 192.168.1.x
  ├── lg1 (master): 192.168.1.23 — SSH, Apache, Earth, ViewSync send
  ├── lg2 (slave):  192.168.1.24 — SSH, Earth, ViewSync receive
  └── lg3 (slave):  192.168.1.25 — SSH, Earth, ViewSync receive

Internal LG network (host-only): 192.168.53.x or 10.42.69.x (static IPs)
  ├── lg1: 192.168.53.1 or 10.42.69.1
  ├── lg2: 192.168.53.2 or 10.42.69.2
  └── lg3: 192.168.53.3 or 10.42.69.3

NAT network (VirtualBox, internet access): 10.0.2.x (auto)
  ├── lg1: 10.0.2.15
  ├── lg2: 10.0.2.15
  └── lg3: 10.0.2.15
```

**Connection from the agent:** Direct SSH to bridged IP:
```bash
sshpass -p 'lg' ssh -o StrictHostKeyChecking=no lg@192.168.1.23 'hostname'     # lg1
sshpass -p 'lg' ssh -o StrictHostKeyChecking=no lg@192.168.1.24 'hostname'     # lg2
sshpass -p 'lg' ssh -o StrictHostKeyChecking=no lg@192.168.1.25 'hostname'     # lg3
```

**When to use this topology:**
- The VM host machine (laptop/desktop) is on the same physical LAN as the Pi/agent
- You can add bridged adapters to the VMs through VirtualBox
- You want the simplest possible SSH path (no tunnels, no port forwarding)
- You need to SSH to slaves directly (e.g. for debugging, without going through master)

**Prerequisites:**
- VirtualBox bridged adapter enabled on each VM (Adapter 3 or whichever slot)
- DHCP enabled on the bridged interface inside the VM
- SSH installed and running on each VM (see `lg-installation-setup` skill)
- LG-internal adapter (Adapter 2) has a **static IP** for ViewSync stability

**Pitfalls:**
- DHCP may change the bridged IPs after reboots. Use your router's DHCP reservation or set a static IP on the bridged interface too.
- The install.sh auto-detects the **NAT** adapter's IP (10.0.2.15) as the master address. When prompted for the master IP on slaves, enter the **bridged** IP (e.g. 192.168.1.23) so slaves can reach master.
- No cross-frame root SSH keys in bridged LAN mode — use sshpass-based helpers (lg-ssh-control).

## Wiki Awareness

A companion knowledge base lives at `~/wiki/` covering all LG architecture, VM network topology, and known quirks. **When you discover a new network quirk or fix, update the relevant wiki page.** The wiki is the durable reference — this skill is the executable procedure.

### Wiki Sync After Skill Updates

Whenever this skill is updated:
1. Check if [[lg-vm-network-setup]] or [[lg-vm-quirks]] needs updating
2. Update the wiki page and append to `~/wiki/log.md`

Network fixes and topology changes are especially important to keep in sync — they affect all SSH operations.
