# VM Internal Network Topology

This document describes the internal network layout of the Nara LG VM rig accessed via reverse tunnel.

## Addressing

- **Pi (this host):** `192.168.1.27` (DHCP — verify each session with `hostname -I`)
- **Laptop (bridge):** `192.168.1.8` (static)
- **Laptop tunnel command:** `ssh -R 2222:<lg-master-ip>:22 nara@<pi-ip> -fN`
- **VM subnet:** `192.168.53.x` (from Pi's perspective via tunnel)
- **VM internal network:** `10.42.69.x` (between VMs on the host)

## Frame Addressing (internal 10.42.69.x)

| Host | IP | SSH Auth |
|------|-----|----------|
| lg1 | 10.42.69.1 | tunnel port 2222 → lg:lg |
| lg2 | 10.42.69.2 | sshpass -p lg ssh lg@lg2 (from lg1) |
| lg3 | 10.42.69.3 | sshpass -p lg ssh lg@lg3 (from lg1) |

All 3 frames use password `lg` for user `lg`. Sudo on all frames also uses password `lg`.

## Built-in Scripts

The VM rig ships with helpers in `/home/lg/bin/` that use **root SSH keys** for cross-frame auth:

- `/home/lg/bin/lg-reboot` — `ssh -t -x root@$lg "reboot"` (others first, self last)
- `/home/lg/bin/lg-poweroff` — likely same pattern

These work from the VM console but fail over SSH tunnel because root's SSH keys aren't forwarded through the tunnel. Use the `lg-*-direct` fallback helpers instead.

## Frame Order

From `~/etc/shell.conf`:
```
LG_FRAMES="lg3 lg1 lg2"
```
Iteration order matters for helper scripts. The current host (lg1) is skipped during the "others first" loop, leaving lg3 then lg2 to be processed.

## Cross-Frame SSH Validation

From within lg1, test access to other frames:
```bash
sshpass -p "lg" ssh -o ConnectTimeout=5 lg@lg2 "hostname"
sshpass -p "lg" ssh -o ConnectTimeout=5 lg@lg3 "hostname"
```

The `echo | sudo -S` pipe inside these inner SSH sessions works correctly (the sshpass issue only affects the outer tunnel SSHs).
