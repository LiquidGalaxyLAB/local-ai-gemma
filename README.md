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

### Voice/Audio (TTS)
- Hermes speaks responses via **Edge TTS** (free) → **pw-play** → **PipeWire** → **Bluetooth headphones**
- Kill old playback before new TTS: `pkill -f pw-play`
- Midterm-ready documentation in `voice-tts-setup.md`

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

## WM-LG Data Collector (World Monitor-inspired)

Modular Python pipeline that fetches free API data → generates KML → deploys to LG's 3s refresh pipeline.

### Quick Start
```bash
cd /home/nara/wm-collector

# India: military bases + ships + live air traffic
python3 run.py --region india --layers military-bases,ships,air-traffic

# Middle East: all data layers
python3 run.py --region middle-east

# Whole world, all layers
python3 run.py --region world --layers all

# Just test (no deploy)
python3 run.py --region ukraine --dry-run
```

### Available Layers (9 collectors)
| Layer | Data Source | Type |
|-------|------------|------|
| `earthquakes` | USGS GeoJSON | Live (real-time) |
| `natural-events` | NASA EONET | Live (2h refresh) |
| `air-traffic` | OpenSky Network | Live (5min refresh) |
| `news` | RSS feeds (8 sources) | Live (15min refresh) |
| `weather` | NOAA NWS | Live (real-time) |
| `disasters` | GDACS | Live (2h refresh) |
| `military-bases` | Config (37 bases) | Static |
| `airports` | Config (35 airports) | Static |
| `ships` | Config (naval+ports+chokepoints) | Static |

### Implemented Use Cases
The `lg-use-cases` skill documents 10 high-impact use cases for the LG:

| # | Use Case | Layers | Camera |
|---|----------|--------|--------|
| 1 | **Global Situational Awareness Wall** | quakes, flights, bases, ships, weather | Auto-rotating global view |
| 3 | **Maritime Domain Awareness** | ports, chokepoints, tanker terminals | Focus on Hormuz/Malacca/Suez |
| 4 | **Natural Disaster Command Center** | quakes, wildfires, weather alerts | Auto-fly to latest M5+ |
| 5 | **Energy & Infrastructure Monitoring** | pipelines, terminals, tankers | Gulf/Hormuz corridor |
| 6 | **Geopolitical Briefing Room** | bases, conflicts, sanctions, news | Fly through hotspots |
| 8 | **Live Aviation Watch** | 100 aircraft, heading-rotated icons | Track corridors |
| 9 | **Cyber / Undersea Infrastructure** | cable routes, outage overlay | Atlantic corridor |
| 10 | **Supply Chain & Trade Flow** | port capacities, trade routes | Global trade lanes |

### Geography Educator KMLs
Pre-built educational visualizations generated via `lg-geography-educator` skill:
- **International Date Line** — Red zigzag line vs cyan 180° meridian
- **India Monsoon Rainfall** — Wind arrows, rain shadow zones
- **Turkey-Syria Earthquake M7.8** — Fault lines, epicenter, plate boundaries
- **Ports of India** — 9 major ports, naval bases, chokepoints

### Screen Layout (LG Wiki Standard)
For 3 screens (frame-count-agnostic formula):
| Screen | Position | Content |
|--------|----------|---------|
| lg1 (center) | master | Earth KML visualization — visual-only, no text |
| lg2 (left) | floor(N/2)+2 | Logo overlay (ScreenOverlay PNG) |
| lg3 (right) | N | **Text info panel** (ScreenOverlay PNG, bullet points) |

### Visual Features
- Custom icons via **Google CDN**: `http://maps.google.com/mapfiles/kml/`
- Airplane icons **rotated by heading** direction
- Flights displayed at actual altitude
- **No CDATA in KML** — plain text descriptions only
- **No gx: namespace** in KML

### Available Regions
`middle-east`, `india`, `europe`, `south-china-sea`, `ukraine`, `africa`, `india-ocean`, `pacific-rim`, `world`

### Auto-Refresh (Cron)
```bash
cronjob action=create name=wm-lg-refresh schedule=5min \
  prompt="cd /home/nara/wm-collector && python3 run.py --region india --layers military-bases,ships,air-traffic --data-only"
```

### Architecture
```
Pi: run.py → collectors/*.py → kml/generator.py → scp → lg1 → sudo cp → /var/www/html/kml/
                                                                              │
                                                                         3s NetworkLink
                                                                              │
                                                                         LG screens
```

### Key Learnings
- **Python 3.5 on lg1** — No f-strings! Use `.format()` or `+` concatenation
- **sudo pipe over sshpass** — `echo "pw" | sudo -S` hangs over sshpass. Use `subprocess.run(['sudo', '-S', ...], input=b'pw\\n')` instead
- **Custom icons** — Must `chown lg:lg` + `chmod 755` for Apache to serve them
- **VM limitation** — Earth 7.3.3 on VirtualBox rejects gx: namespace in LookAt, BalloonStyle/CDATA, and external icon URLs from arbitrary hosts
- **VM Earth crash after lightdm restart** — Qt5 XCB GL integration segfaults (Signal 6). Fix: `QT_XCB_GL_INTEGRATION=none` env var
- **X authority cookie mismatch** — After lightdm restart, X server cookie changes. Fix: `sudo xauth extract+merge` or use `XAUTHORITY=/var/run/lightdm/root/:0`
- **Slave Earth restart** — Must SSH as the display user (lg3/lg2), not as `lg`. Use `sshpass -f lg3@localhost` to start Earth as the correct user
- **KML CDATA rejection** — Even `<description><![CDATA[...]]></description>` causes placemarks to be invisible. Use plain text `escape()` only
- **External icon URLs** — `http://lg1:81/kml/icons/*.png` 404s unless icons are deployed. Use Google CDN: `http://maps.google.com/mapfiles/kml/`
- **Text goes to right screen only** — All text (titles, explanations, bullet points) goes to a ScreenOverlay PNG on the rightmost screen (LG Wiki formula: N). Earth KML is visual-only.

> **⚠️ Important for backup users:** The LG troubleshooting steps documented here (`QT_XCB_GL_INTEGRATION=none`, X authority sync, Earth 7.3.3 crash workarounds, CDATA rejection, slave restart via display-user SSH) are **specific to this setup** (VirtualBox VMs, Ubuntu 16.04, Google Earth Pro 7.3.3.7786). These issues are caused by the VM environment and the specific Earth version. Users who restore this backup to real LG hardware (physical machines with proper GPUs) or newer Earth versions may NOT need any of these workarounds.

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
sshpass -p 'lg' ssh -p 2222 lg@localhost 'printf \"http://lg1:81/kmls/myfile.kml\\n\" > /var/www/html/kmls.txt'

# Clear KML without relaunch
sshpass -p 'lg' ssh -p 2222 lg@localhost 'printf '\\''<?xml version=\"1.0\"?><kml xmlns=\"http://www.opengis.net/kml/2.2\"><Document><name>Empty</name></Document></kml>'\\'' > /var/www/html/kml/master.kml'
```

---

## 🚨 CRITICAL: Earth 7.3.3 VM KML Rules

This LG runs **Google Earth 7.3.3.7786** on a **VirtualBox VM**. It silently rejects KML features that work on desktop Earth.
**These issues are specific to this VM environment — real LG hardware does NOT have these problems.**

| Feature | Works? | Notes |
|---------|--------|-------|
| `<LookAt>` in Document | ✅ Yes | Use `<altitudeMode>` NOT `<gx:altitudeMode>` |
| Basic `<Placemark><Point>` | ✅ Yes | Just coordinates, no styles |
| `flytoview` via `/tmp/query.txt` | ✅ Yes | **The only reliable camera positioning on this rig** |
| `xmlns:gx` namespace | ❌ No | Causes entire KML to be invisible |
| `<Style>` with CDATA balloon | ❌ No | Balloon styles make KML invisible |
| External icon URLs from arbitrary hosts | ❌ No | Icons from non-Google hosts fail silently |
| Google CDN icon URLs | ✅ Yes | `http://maps.google.com/mapfiles/kml/` |
| `QT_XCB_GL_INTEGRATION=none` | ✅ Required | Prevents Signal 6 crash after lightdm restart |
| NetworkLink refreshInterval | ✅ Yes | 3s works on all frames (after --no_system_check fix)

**Rule: Keep KMLs minimal.** No gx namespace, no Style/CDATA, no external icons. Just:

```xml
<LookAt>...</LookAt>
<Placemark>
  <name>Place</name>
  <Point><coordinates>lon,lat,0</coordinates></Point>
</Placemark>
```

### Camera Positioning: Always Use `/tmp/query.txt`

`<flyToView>1</flyToView>` on NetworkLink does NOT reliably move the camera on this rig. The proven method:

```bash
ssh lg@lg1 'echo "flytoview=<gx:duration>3.0</gx:duration><gx:flyToMode>smooth</gx:flyToMode><LookAt><longitude>LON</longitude><latitude>LAT</latitude><range>200000</range><tilt>60</tilt><altitudeMode>relativeToGround</altitudeMode></LookAt>" > /tmp/query.txt'
```

Always send this after every KML deploy.

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
- **Position:** Top-left (`x=\"0\" y=\"1\"`)

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
sed -i '\\|<href>[^<]*master.kml</href>|{n;s|</Link>|<refreshMode>onInterval</refreshMode><refreshInterval>3</refreshInterval></Link>|}' ~/earth/kml/master/myplaces.kml

# Slave (2s) — uses slave_x.kml (PHP variable form)
sed -i '\\|<href>[^<]*slave_x.kml</href>|{n;s|</Link>|<refreshMode>onInterval</refreshMode><refreshInterval>2</refreshInterval></Link>|}' ~/earth/kml/slave/myplaces.kml

# Reset (slave)
sed -i '\\|<href>[^<]*slave_x.kml</href>|{n;s|<refreshMode>onInterval</refreshMode><refreshInterval>[0-9]\\{1,\\}</refreshInterval></Link>|</Link>|}' ~/earth/kml/slave/myplaces.kml
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
| **KML invisible despite correct XML** | **Earth 7.3.3 VM rejects gx namespace, styles/CDATA/icons** | **Use minimal KML: no gx, no Style, no CDATA, no external icons** |
| KML has CDATA in description | VM rejects all CDATA content | Use plain `escape()` text in descriptions |
| Earth crashes after lightdm restart | Qt5 XCB GL integration fails | Set `QT_XCB_GL_INTEGRATION=none` in environment |
| X authority mismatch: "Invalid MIT-MAGIC-COOKIE" | X server cookie changed after restart | `sudo xauth extract /tmp/xc && xauth merge /tmp/xc` |
| Camera stays at Paris | flyToView=1 unreliable | Always send flytoview to `/tmp/query.txt` after deploy |
| `Connection refused` on :2222 | Tunnel down | Ask laptop for reverse tunnel |
| lg2 didn't power off | Self-first bug in helper | Auto-deploy fixed helper (remote-first) via skill |
| Helper not on lg1 | Not deployed | Run deploy script |
| `lg-relaunch` not found | Not in SSH PATH | Use full path: `/home/lg/bin/lg-relaunch` |
| Slaves unreachable after `lg-relaunch-direct` | Lightdm restart may leave VMs in bad state | Power-cycle slave VMs from VirtualBox console |

> **Note:** These troubleshooting steps are specific to this VirtualBox/VM setup. Users on real LG hardware will not encounter most of these issues.
| Earth not found after reboot | `launch-earth.sh` stuck on unreachable slave | `sudo kill <ssh-pid-targeting-slave>` |
