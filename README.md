# Nara — Liquid Galaxy Hermes Agent

AI agent (Hermes profile: `liquid-galaxy-agent`) for operating a **Liquid Galaxy** rig. Manages SSH control (relaunch, reboot, poweroff), KML generation & deployment (no relaunch needed), system diagnostics, and KML auto-refresh via NetworkLink edits.

**Credentials:** `lg` / `lg` (standard for all LG rigs)

**Pi IP:** Checked automatically via `hostname -I` — never ask the operator.

---

## What We Can Do Now

### Liquid Galaxy Control
| Task | How |
|------|-----|
| Connect to LG | Via VM reverse tunnel or direct LAN (auto-detected) |
| Relaunch Earth | `/home/lg/bin/lg-relaunch` or `lg-relaunch-direct` (fallback) |
| Reboot all frames | `/home/lg/bin/lg-reboot-direct` (remote first, then self) |
| Poweroff all frames | `/home/lg/bin/lg-poweroff-direct` — **auto-deploys fix before every run** (powers off remote frames first, then self last, so lg2/lg3 aren't missed) |
| Set/Reset KML refresh | `lg-refresh-set` / `lg-refresh-reset` on slaves |
| Apply master refresh | `lg-master-refresh-set` (3s auto-refresh on master.kml) |

### KML Without Relaunch
- Write to `/var/www/html/kml/master.kml` → appears in 3s
- Dynamic sync via `kmls.txt` + `sync_nlc.php` → appears in 1s
- Write to `slave_*.kml` → appears in 2s
- Clear by writing blank KML → no relaunch needed
- Logo at `/var/www/html/kml/logo.png` (ScreenOverlay)

### GitHub Control
- Repo: `LiquidGalaxyLAB/local-ai-gemma` on `agent-branch`
- PAT-authenticated, push requires approval
- Skills + helpers versioned in repo

---

## Architecture

### Network Topology

```
Laptop (Windows)
  │
  │ ssh -N -R 2222:192.168.53.3:22 nara@<pi-ip>
  ▼
Raspberry Pi 5 (Hermes host) ─── 192.168.1.x (LAN, drifts)
  │
  │ SSH via tunnel ── localhost:2222 → lg1:22
  ▼
Liquid Galaxy Master (lg1) ─── 192.168.53.3
  │
  ├── lg2 (slave screen)
  ├── lg3 (slave screen)
  └── lg4+ (slave screens)
```

### Connection Modes

1. **VM / Reverse Tunnel** — LG VM runs behind a laptop. Use `-p 2222 lg@localhost`. Verify tunnel: `ss -tlnp | grep :2222`. If missing, ask laptop user to run:
   ```
   ssh -N -R 2222:192.168.53.3:22 nara@<pi-ip>
   ```

2. **Direct LAN** — Real LG hardware on same network. Use `lg@<lg-master-ip>`. Verify with `ping -c 1 <ip>`.

> ⚠️ **LAN IPs drift on DHCP** — always verify current IPs each session. Pi IP checked automatically.

---

## KML Deployment & Auto-Refresh

### The Core Challenge

`myplaces.kml` is read **ONCE at Earth startup**. Editing it while Earth runs has no effect until relaunch. But **NetworkLinks** within it can have `<refreshMode>` tags to auto-fetch linked KML.

### Available Delivery Channels

| Channel | Path | Default Refresh | Relaunch Needed? |
|---------|------|-----------------|------------------|
| **Master static** | `/var/www/html/kml/master.kml` | 3s (after fix) | Once after fix |
| **Dynamic sync** | `/var/www/html/kmls/` + `kmls.txt` | 1s (via `sync_nlc.php`) | No |
| **Slave Solo KML** | `/var/www/html/kml/slave_*.kml` | 2s (after fix) | Once after fix |

### After Fix: KMLs Auto-Appear Without Relaunch

```bash
# Write to master.kml — appears within 3s
cat myfile.kml | sshpass -p 'lg' ssh -p 2222 lg@localhost 'cat > /var/www/html/kml/master.kml'

# Dynamic sync — appears within 1s
cat myfile.kml | sshpass -p 'lg' ssh -p 2222 lg@localhost 'cat > /var/www/html/kmls/myfile.kml'
sshpass -p 'lg' ssh -p 2222 lg@localhost 'printf "http://lg1:81/kmls/myfile.kml\n" > /var/www/html/kmls.txt'

# Clear KML without relaunch
sshpass -p 'lg' ssh -p 2222 lg@localhost 'printf '\''<?xml version="1.0"?><kml xmlns="http://www.opengis.net/kml/2.2"><Document><name>Empty</name></Document></kml>'\'' > /var/www/html/kml/master.kml'
```

---

## Poweroff Fix: Remote-First Logic

**Problem discovered:** `lg-poweroff-direct` had a self-first bug — it powered off lg1 first, SSH connection dropped, and lg2/lg3 never received the poweroff command.

**Fix:** Rewrote helper to power off all remote frames first, then self last. The skill now auto-deploys the correct helper before every poweroff via scp.

```bash
# Before every poweroff, the agent auto-deploys:
sshpass -p 'lg' scp -P 2222 -o StrictHostKeyChecking=no \
  ~/.hermes/profiles/liquid-galaxy-agent/skills/liquid-galaxy/lg-ssh-control/scripts/lg-poweroff-direct \
  lg@localhost:/home/lg/bin/lg-poweroff-direct
```

This fix is versioned in `skills/liquid-galaxy/lg-ssh-control/scripts/lg-poweroff-direct` (remote-first) and the deployable copy at `scripts/helpers/lg-poweroff-direct` (identical). Both persist across new sessions.

---

## Logo Deployment

- **KML file:** `/var/www/html/kml/logo_overlay.kml`
- **Logo image:** `/var/www/html/kml/logo.png` (8086 bytes)
- **URL in KML:** `http://lg1/kml/logo.png`
- **Size:** 200×200 pixels
- **Position:** Top-left (`x="0" y="1"`)

---

## KML Authoring Rules

### Every KML Must Include a `<LookAt>`

Without `<LookAt>`, Earth loads the KML but stays at default view (Paris). Content exists but is invisible off-screen.

```xml
<LookAt>
  <longitude>76.5</longitude>
  <latitude>9.8</latitude>
  <range>500000</range>
  <tilt>45</tilt>
</LookAt>
```

Place `<LookAt>` inside `<Document>`, before any Placemarks.

### Color Format (aabbggrr)
- `ffffffff` = white (opaque), `ff00ffff` = cyan (opaque)

### Polygon Guidelines
- Close polygons (last coord = first coord)
- Order: `longitude,latitude,altitude`
- Use `<tessellate>1</tessellate>` for ground-level polygons

---

## sed Command Reference

```bash
# Master (3s auto-refresh)
sed -i '\|<href>[^<]*master.kml</href>|{n;s|</Link>|<refreshMode>onInterval</refreshMode><refreshInterval>3</refreshInterval></Link>|}' ~/earth/kml/master/myplaces.kml

# Slave (2s) — uses slave_x.kml (PHP variable form)
sed -i '\|<href>[^<]*slave_x.kml</href>|{n;s|</Link>|<refreshMode>onInterval</refreshMode><refreshInterval>2</refreshInterval></Link>|}' ~/earth/kml/slave/myplaces.kml

# Reset (slave)
sed -i '\|<href>[^<]*slave_x.kml</href>|{n;s|<refreshMode>onInterval</refreshMode><refreshInterval>[0-9]\{1,\}</refreshInterval></Link>|</Link>|}' ~/earth/kml/slave/myplaces.kml
```

> ⚠️ **Uses `slave_x.kml`** (PHP-resolved variable) — NOT `slave_2.kml`. All slaves share the same template.

---

## Helper Scripts

Deployed to `/home/lg/bin/` on lg1. All embed the `lg` password.

| Helper | Purpose | Scope |
|--------|---------|-------|
| `lg-relaunch` (built-in) | Restart Earth via root SSH keys | All frames |
| `lg-relaunch-direct` | Restart Earth (Python, sshpass fallback) | All frames |
| `lg-reboot-direct` | Reboot all frames (remote first, self last) | All frames |
| `lg-poweroff-direct` | Power off all frames (remote first, self last) | All frames |
| `lg-refresh-set` | Add 2s auto-refresh to slave Solo KML | Slaves |
| `lg-refresh-reset` | Remove auto-refresh from slave Solo KML | Slaves |
| `lg-master-refresh-set` | Add 3s auto-refresh to master KML link | Master |

### Auto-Deploy
```bash
# VM mode
bash skills/liquid-galaxy/lg-ssh-control/scripts/deploy-lg-reboot-direct.sh

# Direct LAN
LG_MASTER_IP=192.168.53.3 bash skills/liquid-galaxy/lg-ssh-control/scripts/deploy-lg-reboot-direct.sh
```

---

## Filesystem Reference

| Path | Purpose |
|------|---------|
| `/var/www/html/kml/master.kml` | Master screen KML (3s auto-refresh) |
| `/var/www/html/kml/slave_*.kml` | Per-slave static KML (2s auto-refresh) |
| `/var/www/html/kmls/` | Web-managed KML files (dynamic, 1s) |
| `/var/www/html/kmls.txt` | URL list for dynamic sync |
| `/var/www/html/kml/logo.png` | Logo image |
| `/var/www/html/kml/logo_overlay.kml` | Logo ScreenOverlay KML |
| `~/earth/kml/master/myplaces.kml` | Master Earth startup config — **NEVER overwrite** |
| `~/earth/kml/slave/myplaces.kml` | Slave startup config (uses `slave_x.kml`) |
| `/home/lg/bin/lg-*-direct` | Helper scripts |
| `/home/lg/bin/lg-refresh-*` | Refresh helpers |
| `/home/lg/bin/lg-master-refresh-set` | Master refresh helper |

---

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| KML not visible | No `<LookAt>` | Add LookAt before Placemarks |
| KML not appearing | No refreshInterval | Apply master/slave fix + relaunch once |
| `Connection refused` on :2222 | Tunnel down | Ask laptop for reverse tunnel |
| lg2 didn't power off | Self-first bug in helper | Auto-deploy fixed helper (remote-first) via skill |
| Helper not on lg1 | Not deployed | Run deploy script |
| `lg-relaunch` not found | Not in SSH PATH | Use full path: `/home/lg/bin/lg-relaunch` |
| Earth not found after reboot | `launch-earth.sh` stuck on unreachable slave | `sudo kill <ssh-pid-targeting-slave>` |
