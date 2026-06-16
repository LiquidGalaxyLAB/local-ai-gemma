# LAN IP Drift — Verification Protocol

Pi and other device IPs change on DHCP LANs. Always verify before LG commands.

## Step 0: Connection Mode (ask user)

> "How are you connecting to Liquid Galaxy?"
> 1. **VM / Reverse Tunnel** — LG on VM behind laptop
> 2. **Direct LAN** — Real LG hardware on same network

## VM / Reverse Tunnel mode

```bash
# 1. Pi IP (your host)
hostname -I | awk '{print $1}'

# 2. Tunnel alive?
ss -tlnp | grep :2222

# 3. lg1 reachable through tunnel?
sshpass -p 'lg' ssh -p 2222 -o StrictHostKeyChecking=no lg@localhost "hostname -I"
```

## Direct LAN mode

```bash
# 1. This device IP
hostname -I | awk '{print $1}'

# 2. LG master reachable? (ask user for the IP first)
ping -c 1 <lg-master-ip> 2>&1

# 3. SSH reachable?
sshpass -p 'lg' ssh -o StrictHostKeyChecking=no lg@<lg-master-ip> "hostname -I"
```

## Tunnel not up (VM mode)

Tell the user to run this from their laptop:
```
ssh -N -R 2222:192.168.53.3:22 nara@<pi-ip>
```

Use the Pi IP from step 1 — it may have changed since last session.

## History

- Previously Pi was `192.168.29.20`, drifted to `192.168.1.21` in a later session.
- lg1 VM internal IP is stable at `192.168.53.3` (VM mode only; direct LAN may differ).
- Laptop user (Nara) may connect from any LAN IP — always check, never assume.
