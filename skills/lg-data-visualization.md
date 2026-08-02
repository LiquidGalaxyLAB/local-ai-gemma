---
name: lg-data-visualization
description: "Generate data-driven KML from external geospatial APIs for Liquid Galaxy — data-source discovery, API polling, KML transformation, screen-placement rules, and deployment cadence."
version: 3.3.0
author: Nara
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [LiquidGalaxy, KML, Data, API, Visualization, Geospatial]
    related_skills: [lg-kml-tours, lg-ssh-control, lg-orbit-workflow]
---

# LG Data Visualization Pipeline

**Class of work:** Sourcing real-time, near-real-time, or static geospatial data from external APIs and rendering it as KML on Liquid Galaxy's multi-screen Google Earth.

**When to load this skill:** User asks to visualize data on LG — earthquake activity, military movements, natural events, ship traffic, pipelines, infrastructure, or any geospatial data from an external source.

**Do NOT load for:** Tour/animation creation (use `lg-kml-tours`), control commands (use `lg-ssh-control`), orbit workflows (use `lg-orbit-workflow`).

---

### Architecture (Dual-Source + Fusion)

```
┌─────────────┐     ┌────────────────┐     ┌──────────────┐     ┌──────────┐
│ Pi cron job  │────>│ collector.py    │────>│ FUSION ENGINE│────>│ scp to   │
│ (5-30 min)   │     │ (Python via Pi) │     │ (fusion.py)  │     │ lg1:81/  │
└─────────────┘     └───────┬────────┘     └──────┬───────┘     └─────┬────┘
                            │                      │                   │
                    ┌───────┴───────┐      ┌───────┴────────┐     3s NetworkLink
                    │ Primary API   │      │ DataQualityNote│          │
                    │ Secondary API │      │ + disclaimer   │   ┌──────┴──────┐
                    └───────┬───────┘      └───────┬────────┘   │ LG screens  │
                            │                      │            │ auto-update │
                     compare_layers()     slave_2.kml gets     └─────────────┘
                     (terminal output)    quality summary
```

**Key principle:** Do NOT call a secondary aggregator API (like World Monitor). Call the **underlying external data sources directly** — USGS, EONET, OpenSky, GDACS, NOAA, etc. For live-data layers, use TWO independent sources and cross-check them.

**Dual-source verification (MANDATORY for live-data layers):** Every live-data layer MUST have TWO independent sources. One source alone creates blind spots — API outages, stale data, one-sided coverage. Collect from both, compare results, and inject a data-quality disclaimer on LG screens when sources diverge.

---

## Workflow (Do Not Execute Without User Approval)

This is a **plan-first, execute-second** workflow. Present the architecture, data sources, and region scope to the user. Get explicit approval before writing any code.

### Step 1: Identify Data Layers

Match user needs to available free/open APIs. **Every live-data layer MUST have a secondary (v2) source** for cross-verification. Static config layers (military bases, airports, ships) are fine with one source.

| Layer | Primary API | Secondary API (v2) | Update cadence | Ref. file |
|-------|-----------|-------------------|---------------|-----------|
| Earthquakes | USGS GeoJSON (`earthquake.usgs.gov/.../4.5_week.geojson`) | **EMSC** seismicportal.eu (`format=json&minmag=2.5`) | 5-10 min | `collectors/earthquakes.py`, `earthquakes_v2.py` |
| Natural Events | NASA EONET (`eonet.gsfc.nasa.gov/api/v3/events`) | N/A (single authoritative source) | 15-30 min | `collectors/natural_events.py` |
| Weather Alerts | NOAA NWS (`api.weather.gov/alerts/active`) | **wttr.in / WMO** (`wttr.in/~lat/lon?format=j1`) | 5 min | `collectors/weather.py`, `weather_v2.py` |
| GDACS Disasters | GDACS (`gdacs.org/gdacsapi/api/events/geteventlist/MAP`) | **Wikipedia Current Events** (`en.wikipedia.org/w/api.php?parse&page=Portal:Current_events`) | 10-30 min | `collectors/disasters.py`, `disasters_v2.py` |
| Military Bases | Static config (37 bases, operator-colored) | N/A (static) | Static | `collectors/military_bases.py` |
| Major Airports | Static config (35 major international airports) | N/A (static) | Static | `collectors/airports.py` |
| Air Traffic | OpenSky Network (`opensky-network.org/api/states/all`) | N/A (sole free ADS-B source) | 5 min | `collectors/air_traffic.py` |
| Ships / Maritime | Config-based (naval bases, ports, chokepoints) | N/A (static) | Static — expanded Jul 2026 to cover Middle East/Gulf (Strait of Hormuz chokepoints, Gulf ports, ME naval bases) AND US East Coast (NY/NJ, Baltimore, Boston, Norfolk, etc.) | `collectors/ships.py` |
| News (RSS) | 8 RSS feeds (BBC, Al Jazeera, France24, AP, NPR, DW) | Already multi-source | 15-30 min | `collectors/news.py` |

**Why dual-source?** Single-API reliance creates blind spots. USGS may lag on regional quakes that EMSC catches. NOAA NWS is US-only — useless for Middle East/India/Africa. GDACS APIs can go stale while Wikipedia editors report disasters in real time. Cross-verifying catches these gaps and flags them on-screen.

**Avoid GDELT for news:** The GDELT Project Doc API rate-limits aggressively (429 after 3-4 requests). RSS feeds from major news orgs are more reliable, need no keys, and return well-structured headline/summary/link data. If you must use GDELT (e.g. need geo-tagged articles), use a single broad query with 5s+ delays between retries.

### Step 2: Choose Region First

**Always geofilter to a single region initially.** Adding all world data at once degrades Earth performance (too many placemarks). User must approve the region.

Define bounding box as `[lat_min, lat_max, lon_min, lon_max]`. Bounding box must be tight enough to be useful but loose enough to capture events at the edges.

**Recommended starter regions with rich data:** (listed in `framework.py` REGIONS dict)
- Middle East: `[12, 40, 35, 60]`, center 26N 48E
- Ukraine/Eastern Europe: `[44, 55, 22, 40]`, center 49N 32E
- South China Sea: `[0, 25, 100, 125]`, center 12N 112E
- India / Indian Ocean: `[5, 37, 65, 100]`, center 20N 80E
- Europe: `[35, 70, -10, 40]`, center 50N 10E
- Africa: `[-35, 37, -20, 52]`, center 5N 20E
- Pacific Rim: `[-45, 60, 115, -70]`, center 10N 150E
- World: `[-90, 90, -180, 180]`, center 0N 0E

### Step 3: Dual-Source Collection & Fusion

Each live-data layer (earthquakes, weather, disasters) MUST be collected from
TWO independent APIs, then **fused** into a clean single output.

The framework's `DUAL_SOURCE_MAP` in `framework.py` defines the pairing;
`fusion.py` defines the per-layer fusion policy.

```python
DUAL_SOURCE_MAP = {
    'earthquakes': 'earthquakes-v2',   # USGS + EMSC
    'disasters': 'disasters-v2',       # GDACS + Wikipedia
    'weather': 'weather-v2',           # NOAA NWS + wttr.in
}
```

**Fusion Pipeline:**

```
Primary API → raw features           Secondary API → raw features
        │                                      │
        └──────────┬──────────┬────────────────┘
                   │          │
           compare_layers()  fuse_layer()
           (source report)   (per policy)
                   │          │
                   ▼          ▼
            Terminal output  Clean merged feature list
            (✅ℹ️⚠️🔴)      + DataQualityNotes for right screen
                                │
                    ┌───────────┴────────────┐
                    ▼                        ▼
            master.kml (main)        slave_2.kml (right screen)
            Confidence-encoded       📊 DATA QUALITY section
            icons by scale:          ✅ verified  ⚠️ approximate
            verified=1.0x
            single_source=0.8x
            approximate=0.6x
```

#### Fusion Policies (defined in `fusion.py`)

| Policy | Layers | Behavior |
|--------|--------|----------|
| `union_dedup` | earthquakes, disasters | Merge both sources. Remove 0.5° proximity duplicates (≈55km). Prefer primary attributes for overlapping events. All features merged into one clean folder per layer — no sub-folders per source. |
| `primary_fallback` | weather | Use primary (NOAA NWS) for US/Canada. If primary returns nothing, use secondary (wttr.in) as fallback. Never both at once. |

#### Confidence Encoding on Master Screen

| Data Quality | Icon Scale | Visual Meaning |
|-------------|-----------|----------------|
| `verified` | 1.0× (full) | Both sources found this event |
| `single_source` | 0.8× | Only one source — slightly smaller icon |
| `approximate` | 0.6× | Unverified — smallest, least prominent |

All features share the same folder and icon type — the viewer sees a clean
display where less-confident events are subtly smaller rather than visually noisy.

#### Data Quality Summary on Right Screen

`slave_2.kml` now includes a `📊 DATA QUALITY` section at the top, above news
headlines. Each fused layer has one line:

```
📊 DATA QUALITY
✅ Earthquakes: 2 (USGS) + 2 (EMSC), no overlap
⚠️ Weather: 1 from wttr.in only (NOAA NWS unavailable)
⚠️ Disasters: 6 from Wikipedia only (GDACS unavailable)

📰 HEADLINES — MIDDLE EAST
• BBC: ...  (starts below quality section)
```

Color coding: **green** = verified, **yellow** = approximate/single_source,
**blue** = informational. Icons: ✅ ⚠️ ℹ️.

#### Proximity Matching

Used by both `compare_layers()` and `fuse_layer()` — haversine distance
between two lat/lon points. 0.5° threshold (≈55km at equator) is tight
enough to distinguish separate events but loose enough to catch same
event reported by different APIs at slightly different coordinates.

#### CLI Flags

```bash
python3 run.py                              # Dual-source + fusion ON (default)
python3 run.py --single-source              # Skip v2, no fusion (fast, no disclaimers)
python3 run.py --no-disclaimers             # Still fuse but suppress quality overlay
python3 run.py --region europe --single-source
```

### Step 4: Build Collector (Python on Pi)

Each collector is a standalone Python script:
1. HTTP GET to the source API (with User-Agent header, timeout)
2. Parse response (usually GeoJSON or JSON)
3. Geofilter to region bounding box
4. Transform to KML placemarks/polygons/paths
5. Merge into master.kml (or write separate .kml per layer)
6. SCP to lg1 via sshpass, then sudo-cp to `/var/www/html/kml/`

**Collector template (see `templates/lg-data-visualization/collector-base.py`):**
```python
import requests, json, os, subprocess, tempfile

API_URL = "..."
BOUNDING_BOX = [44, 56, 22, 42]  # lat_min, lat_max, lon_min, lon_max

def in_bbox(lat, lon):
    return BOUNDING_BOX[0] <= lat <= BOUNDING_BOX[1] and BOUNDING_BOX[2] <= lon <= BOUNDING_BOX[3]

def build_kml(items) -> str:
    # Build KML string with LookAt, Placemarks, Styles
    ...

def deploy(kml_str):
    local = "/tmp/master.kml"
    with open(local, "w") as f:
        f.write(kml_str)
    remote = "lg@192.168.1.200:/home/lg/master.kml"
    subprocess.run(["sshpass", "-p", LG_PASS, "scp", local, remote])
    # Python subprocess on lg1 for sudo cp — echo | sudo -S hangs over sshpass
    deploy_cmd = (
        'python3 -c "import subprocess; '
        'subprocess.run([\'sudo\', \'-S\', \'cp\', '
        '\'/home/lg/master.kml\', \'/var/www/html/kml/master.kml\'], '
        'input=b\'lg\\\\n\', check=True)"'
    )
    subprocess.run(["sshpass", "-p", LG_PASS, "ssh", "lg@192.168.1.200", deploy_cmd])
```

### Step 5: KML Generation Rules (LG Standards)

Enforced by the KML writer module. See `references/lg-data-visualization/kml-generation-rules.md` for the full reference.

**Mandatory (VM Earth 7.3.3 rules — verified empirically):**
- Every KML MUST have `<LookAt>` in `<Document>` or camera stays at Paris default
- Use plain `<altitudeMode>` NOT `<gx:altitudeMode>` inside LookAt (VM rejects gx namespace there)
- **No CDATA anywhere** — CDATA in `<description>` causes Earth VM to silently drop the entire placemark. The only safe description format is plain escaped text: `<description>Callsign: ABC123 | Altitude: 35,000 ft</description>`. This also applies to `<BalloonStyle><text>` — never use `<![CDATA[` in any KML element. **Tested: even `<description><![CDATA[plain text]]></description>` (no HTML) still fails.** The CDATA byte sequence itself triggers the parser bug. Always use Python's `html.escape()` and pass text directly.
- **Icon URLs: prefer Google CDN paddle pins over both local PNGs AND shape icons on VM rigs.** Earth 7.3.3 on VirtualBox sometimes fails to load PNGs from `http://lg1:81/kml/icons/*.png` despite HTTP 200. Use `http://maps.google.com/mapfiles/kml/paddle/ylw-circle.png` or `/paddle/red-circle.png` etc. — these paddle pins ALWAYS render reliably. **DO NOT use `shapes/air.png`, `shapes/fire_station.png`, or `shapes/shaded_dot.png`** — they return 404 on this rig (confirmed Aug 2026). If custom shapes are needed, host them on lg1 Apache. ⚠️ **Check /etc/hosts** — if `maps.google.com` is blocked there (from sign-in dialog suppression), Google CDN URLs will also fail. Remove the block: `sudo sed -i '/maps.google.com/d' /etc/hosts`.
- **No text labels on placemarks** — All text content (titles, explanations, bullet points, data quality, sources) goes to the rightmost screen (rightmost = floor(N/2)+1; for N=3 → slave_2.kml = lg2) as a ScreenOverlay PNG **or the news-card balloon** (dark HUD cards, category color bars — `scripts/lg-kml-tours/news_card_balloon.py`, escaped HTML). Placemarks in master.kml should have no `<name>` or `<name> </name>` (single space) — just visual elements (icons, lines, polygons). Right-screen text panel is generated via `right_panel.py` (Python Pillow, 500x600, dark bg, bullet points in light blue, headers in bright blue).
- Colors in ABGR hex: `ffff0000` = red, `ff00ff00` = green, `ff0000ff` = blue
- Range ≥ 1,500,000m for VM reliability at country level; ≥ 100,000m for local spots
- `xmlns="http://www.opengis.net/kml/2.2"` — never add `xmlns:gx` on NetworkLink-loaded KML (it will be silently rejected)
- **Test with a minimal KML first**: `<Placemark><name>Test</name><Point><coordinates>lon,lat,0</coordinates></Point></Placemark>` — if this doesn't render, Earth's NetworkLink subsystem is broken (check launch flags: need `--no_system_check --no_signin`)

### Label Style Font Size
Labels MUST be large enough to read on LG screens (3-8m away):
- **Base LabelStyle scale: 1.4** (up from 0.8 default in Earth). The KML generator uses `LabelStyle <scale>1.4</scale>` for all data features.
- **News header: 1.8** for the section title
- **News articles: 1.2** for headline text in the right-screen column
- **Icon scale: 1.1** (default GeoFeature scale, up from 0.8)
- Individual layers can override scale per feature (e.g., severe earthquakes at 1.6, minor ones at 0.6)

Two-seat rule: if you're sitting 2+ meters from the screen and can't read the label, the font is too small.

### KML Symbol Icons (Instead of Default Pins)

Two icon strategies — prefer locally-hosted icons for reliability.

#### Strategy 1: Locally-Hosted Icons (Recommended)
Host custom-generated PNG icons on lg1's Apache (port 81), served from `/var/www/html/kml/icons/`. Generated via Python Pillow:

```
http://lg1:81/kml/icons/
├── plane.png        → Air traffic (rotated by heading)
├── earthquake.png   → Earthquakes (concentric rings)
├── military.png     → Military bases (shield)
├── news.png         → News articles (document)
├── wildfire.png     → Wildfires (flame shape)
├── storm.png        → Storms (spiral)
├── flood.png        → Floods (water drop)
├── alert.png        → Weather alerts (exclamation)
└── circle-{color}.png → Generic colored dots (8 colors)
```

**To generate and deploy icons:**
```bash
# Generate 48x48 PNG icons via Pillow (see references/lg-data-visualization/icon-generation.md)
python3 generate_icons.py  # -> /tmp/lg-icons/*.png

# SCP to lg1 then deploy via Python subprocess sudo cp
for f in /tmp/lg-icons/*.png; do
  sshpass -p 'lg' scp "$f" lg@<LG-IP>:/home/lg/icons-$(basename $f)
done
# On lg1: sudo cp to /var/www/html/kml/icons/ (use Python subprocess, not echo|sudo)
```

Verify accessibility: `curl -s -I http://lg1:81/kml/icons/plane.png` should return 200.

#### Strategy 2: Google Maps CDN (Fallback)
Use Google's built-in palette when local hosting is unavailable: `http://maps.google.com/mapfiles/kml/shapes/<name>.png`

**Layer->icon mapping (from `kml/generator.py`):** earthquake->earthquake.png, wildfire->fire_station.png, military_base->military.png, weather_alert->caution.png, news->info-i.png, airport->airports.png, ship->sailing.png, plus flood, storm, volcano, pipeline, target, and colored fallbacks.

**Fallback:** If `icon_url` is empty, falls back to colored pushpins (ABGR `color` field).

### Icon Heading Rotation (Air Traffic)

For directional data (flights, ships), rotate the icon to match true heading using `<heading>` inside `<IconStyle>`:

```xml
<IconStyle>
  <heading>237</heading>
  <scale>1.2</scale>
  <Icon><href>http://lg1:81/kml/icons/plane.png</href></Icon>
</IconStyle>
```

**In the collector:** Pass heading in `extra['heading']` — the generator reads it via `extra.get('heading')` and injects `<heading>` into the style. If 0 or None, the tag is omitted.

### Altitude-Mode Placemarks (Flights)

For air traffic, use `relativeToGround` with actual altitude in the coordinates:

```xml
<Placemark>
  <Point><coordinates>lon,lat,10668</coordinates></Point>
  <altitudeMode>relativeToGround</altitudeMode>
</Placemark>
```

In the collector, pass `extra['altitude']` in meters. The generator checks `f.extra.get('altitude', 0)` — if truthy it emits 3D coords + altitudeMode; if 0 it falls back to flat coords.

### Folder-Organized KML

Group placemarks by layer using `<Folder>` for toggleable layers in Earth's Places panel:

```xml
<Folder><name>✈ Air Traffic</name><visibility>1</visibility>...placemarks...</Folder>
<Folder><name>🌍 Earthquakes</name><visibility>1</visibility>...placemarks...</Folder>
```

Generator groups by `kind` in a defined `folder_order` list. Layers not in the ordered list get their own folder by kind name. Empty folders are omitted.

### Screen Placement Rules (from LG Wiki + Nara's conventions)

**Dual-output architecture:** Generate TWO KMLs — data on master, news on right screen.

| Content | Target | KML File | Notes |
|---------|--------|----------|-------|
| Data placemarks (all layers) | All screens | `master.kml` | ViewSync syncs camera, content renders on all |
| Logo/branding | Leftmost slave only | `slave_<N>.kml` (leftmost) | Formula: floor(N/2)+2 (lg3 for 3-screen) |
| News balloons / article index | Right screen only | `slave_<N>.kml` (rightmost) | Heavy HTML balloons don't scale well to all screens; rightmost = floor(N/2)+1 (lg2 for N=3) |
| Control overlays | Master only (lg1) | N/A (Earth UI) | Master has keyboard/mouse |

For N=3: leftmost = floor(3/2)+2 = lg3 (data only, -36.5 yaw), lg1=center (data+control), rightmost = floor(3/2)+1 = lg2 (data+news, +36.5 yaw)

**Right screen news placement:** News articles are fanned-out in a vertical column on the right side of the viewport (center_lon + 8 degrees, starting above center_lat, stepping -0.18 degrees each article). This puts them in the right screen's viewing area on a 3-screen rig. Each article has a compact label with topic emoji + headline, and an HTML balloon description with source, date, summary, and link.

**Implementation:** The orchestrator (`run.py`) always generates two KML outputs:
1. `master.kml` — all data layers (earthquakes, flights, bases, weather, etc.)
2. `slave_2.kml` — news articles only, formatted as a right-side column (rightmost screen on 3-screen rig)

The `--data-only` flag skips news; `--news-only` skips data. Both are deployed on every run by default.

**Deploy command for each:** Python subprocess on lg1 with sudo cp, same as data deploy pattern. The slave KML goes to `/var/www/html/kml/slave_2.kml` which lg2 (rightmost) loads via its PHP-resolved NetworkLink.

### Step 6: Deploy Cadence

- Earthquakes: ~~ every 30 min (USGS updates ~5-10 min, but daily data is sufficient for LG)
- Wildfires/Natural: every 2-6 h (GDACS/EONET cadence)
- Military flights: every 5 min (real-time ADS-B)
- Static configs: deploy once, never touch

**Refresh chain:**
1. Pi runs collector on cron
2. Collector writes KML to `/tmp/`, scp to lg1
3. lg1: `sudo cp` to `/var/www/html/kml/master.kml`
4. LG master NetworkLink (3s refresh) picks up new file
5. Earth re-renders on all screens via ViewSync

**No relaunch needed after KML updates.** Only relaunch when editing myplaces.kml directly (flyToView, refreshInterval changes). After a power cycle, Earth is NOT running on VM rigs — see the VM Startup Pitfall below.

### Step 7: Auto-Refresh (Cron Job)

Use Hermes cronjob tool for recurring data refreshes:

```bash
hermes cron create \
  --schedule "5min" \
  --name "wm-lg-india-refresh" \
  --prompt 'Run: cd /home/nara/wm-collector && python3 run.py --region india --layers military-bases,ships,air-traffic --data-only. Report feature counts per layer.'
```

Or use raw cronjob API:
```python
cronjob(action='create', name='wm-lg-india-refresh',
        schedule='5min',
        prompt='Run /home/nara/wm-collector/collector.py for India region...')
```

**Key considerations:**
- Use `--data-only` to skip news on refresh cycles (news changes less frequently)
- Keep refresh cadence appropriate to data source: air traffic every 5 min, earthquakes every 30 min, static data once
- Local-delivery cron jobs save output but don't push to this session — use `deliver='all'` if you want notifications
- To stop: `cronjob action='list'` to find job_id, then `cronjob action='remove' job_id=<id>`

### Step 8: Camera Control

Use LG's **Two-Layer Architecture** — never embed camera animation in master.kml (re-writing it every 3s causes flicker).

- **Static KML (Layer 1):** Deploy placemarks/polygons to master.kml once or on a long cadence
- **Camera (Layer 2):** Animate separately via `/tmp/query.txt`:
  - `echo "flytoview=<LookAt>...</LookAt>" > /tmp/query.txt`
  - `echo "playtour=Orbit" > /tmp/query.txt` (if gx:Tour deployed)
  - `echo "exittour=true" > /tmp/query.txt` (stop)

See `lg-kml-tours` skill for full camera control patterns and `lg-orbit-workflow` for smooth orbit parameters.

---

## Rules & Pitfalls

### Python 3.5 on lg1 (No f-strings)
lg1 runs Ubuntu 14.04 with Python 3.5. Any script deployed or executed ON lg1 must avoid f-strings:

```python
# WRONG — SyntaxError on lg1:
dest = f'/var/www/html/kml/icons/{name}'

# RIGHT — Python 3.5 compatible:
dest = '/var/www/html/kml/icons/' + name
```

Use `.format()` or `+` concatenation in any script that runs on lg1. Scripts running on the Pi (Python 3.13) can use f-strings freely.

### Known Bug: News Generator Crashes with UnboundLocalError

When `run.py` runs with news and another layer (e.g. `python3 run.py --region india --layers earthquakes,news`), the data-collection phase succeeds and deploys master.kml, but the news generation at line ~272 crashes with:

```
UnboundLocalError: cannot access local variable 'dq_lat_start' where it is not associated with a value
```

This happens because `generate_news_kml()` tries to read `dq_lat_start` which is only set when `quality_notes` is non-empty. When running with `--single-source` (or with no live-data layers that produce quality notes), the variable is never assigned but the function tries to use it for positioning the data-quality section header.

**Workaround A — run data and news separately:**
```bash
# Deploy data (master.kml)
python3 run.py --region india --layers earthquakes --single-source --data-only

# Build slave_2.kml manually via the RSSNewsCollector, or
# run with --no-disclaimers to skip quality notes:
python3 run.py --region india --layers earthquakes,news --single-source 2>&1 | grep -v "Quality"
```

**Workaround B — manual right-screen KML:**
When the generator crashes, master.kml is already deployed — the error only affects slave_2.kml. Generate a minimal news list separately:
```python
from framework import REGIONS
from collectors.news import RSSNewsCollector
nc = RSSNewsCollector()
features = nc.fetch(REGIONS['india'])
# Build a simple KML with Placemarks in a vertical column
# at (center_lon + 8, center_lat - i*0.18)
```

### Do NOT
- Do NOT build for the whole world initially. Start with one region bounding box. Get user approval to expand.
- Do NOT skip dual-source for live-data layers — every earthquake/weather/disaster layer MUST collect from two independent APIs
- Do NOT embed camera animation in the KML file that gets refreshed every 3s — use the Two-Layer Architecture
- Do **NOT** use `echo \\\\\\\"$PW\\\\\\\" | sudo -S` in the SSH deploy command — sshpass consumes SSH's stdin, breaking the pipe to sudo and causing a silent hang. **Always use Python `subprocess.run` with `input=b'PW\\\\\\\\\\\\\\\\n'` for the sudo step.**
- Do NOT use CDATA in BalloonStyle on VM rigs
- Do NOT delete or touch-empty master.kml — always overwrite with a valid blank KML
- Do NOT rely on `launch-earth.sh` autostart on VM rigs — it hangs on SSH to unreachable slaves (lg2/lg3). Start Earth directly: `sshpass -p 'lg' ssh -f lg@<IP> \\\"nohup /opt/google/earth/pro/googleearth > /home/lg/earth-start.log 2>&1\\\"`

### VM Earth Startup (CRITICAL)

On VM rigs, the autostart `launch-earth.sh` tries to SSH to all frames (`lg-run killall ...`) which hangs forever on unreachable slaves (lg2/lg3 in single-VM setups). This blocks Earth from ever starting.

**Fix:** Kill the stuck SSH/lg-run processes, then start Earth directly:
```bash
# Kill stuck processes (use exact PIDs, NOT pkill -f which can kill your own SSH)
sshpass -p 'lg' ssh lg@<IP> "kill <pid_of_launch-earth> <pid_of_ssh_to_lg2>"

# Remove stale lock file
sshpass -p 'lg' ssh lg@<IP> "rm -f /home/lg/.googleearth/instance-running-lock"

# Start Earth directly
sshpass -p 'lg' ssh -f lg@<IP> \\
  "nohup /opt/google/earth/pro/googleearth > /home/lg/earth-start.log 2>&1"
```

**Earth may show "Google Earth Options" dialog on first launch** — dismiss it with:
```bash
DISPLAY=:0 xdotool search --name 'Google Earth Options' key alt+a
sleep 1
DISPLAY=:0 xdotool search --name 'Google Earth Options' key Return
```

**After power cycle**, Earth is not running until you start it. The autostart `lg.desktop` launches `launch-earth.sh` which will hang. You must use the manual start pattern above.

### Always
- Present the plan first. Get user approval before writing any code. Say "Here's the plan..." then wait.
- Include a `<LookAt>` in every KML Document or the camera stays at Paris
- Check the LG wiki (`lg-wiki-reference` skill) before deciding screen placement or KML format
- Use 1,500,000m+ range for VM rigs at country levels
- Color-code placemarks meaningfully (red=conflict/high, orange=warning, green=safe, blue=infrastructure)
- Test with a single static placemark KML first before adding dynamic data

### CRITICAL: Deploy Pattern

**CRITICAL: Post-deploy verification — KML may be invisible despite HTTP 200.**

Apache returning 200 + Earth fetching the KML does NOT mean placemarks render. Earth 7.3.3 on VirtualBox silently drops placemarks when:
- The KML uses the `xmlns:gx` namespace (use plain `xmlns="http://www.opengis.net/kml/2.2"` only)
- Icon PNGs referenced in `<Icon><href>` return 404 — verify each URL returns HTTP 200
- Earth was launched without `--no_system_check --no_signin` (3s NetworkLink refresh works but placemarks don't render)
- Descriptions contain CDATA that triggers the VM's BalloonStyle parser bug

**Post-deploy checklist:**
1. `curl -sI http://lg1:81/kml/master.kml` — returns 200
2. `sudo grep "GoogleEarth.*kml/master.kml" /var/log/apache2/other_vhosts_access.log | tail -3` — Earth actively fetching
3. For each icon in the KML: `curl -s -o /dev/null -w "%{http_code}" http://lg1:81/kml/icons/<name>.png` — must be 200
4. Check Earth flags: `cat /proc/$(pgrep -f googleearth-bin | head -1)/cmdline | tr "\0" " "` should show `--no_system_check --no_signin`

Do NOT use `echo "lg" | sudo -S` for the sudo cp step — it hangs over sshpass because sshpass consumes SSH's stdin, breaking the pipe to sudo. Use Python subprocess with input=b"lg\n":

```python
import subprocess
subprocess.run(["sudo", "-S", "cp", src, dst],
               input=b"lg\n", check=True)
```

The `[sudo] password for lg:` message on stderr is **cosmetic** — exit code 0 means success. Do not treat it as a failure signal.

### Reference Project (This Rig)

The full modular collector lives at `/home/nara/wm-collector/` — a pluggable architecture with a registration-based layer system:

```
/home/nara/wm-collector/
├── run.py                  # CLI entry point (dual-source + fusion by default)
├── framework.py            # Region model, GeoFeature, @register_layer,
│                           # SourceComparison, compare_layers(), DUAL_SOURCE_MAP
├── fusion.py               # Fusion engine: FusionPolicy, DataQualityNote,
│                           # fuse_layer(), union_dedup + primary_fallback
├── kml/generator.py        # LG-compliant KML + confidence encoding + disclaimer
├── collectors/
│   ├── __init__.py
│   ├── earthquakes.py      # USGS — @register_layer('earthquakes')
│   ├── earthquakes_v2.py   # EMSC    — @register_layer('earthquakes-v2')
│   ├── natural_events.py   # EONET — @register_layer('natural-events')
│   ├── military_bases.py   # 37 strategic bases — @register_layer('military-bases')
│   ├── weather.py          # NOAA NWS alerts — @register_layer('weather')
│   ├── weather_v2.py       # wttr.in / WMO  — @register_layer('weather-v2')
│   ├── disasters.py        # GDACS — @register_layer('disasters')
│   ├── disasters_v2.py     # Wikipedia Current Events — @register_layer('disasters-v2')
│   ├── airports.py         # 35 major airports — @register_layer('airports')
│   ├── air_traffic.py      # OpenSky Network — @register_layer('air-traffic')
│   ├── ships.py             # Naval bases, ports, chokepoints (India + ME/Gulf — Jul 2026 expanded) — @register_layer('ships')
│   └── news.py             # RSS feeds (BBC, AJ, AP, etc.) — @register_layer('news')
```

**Dual-source pairing** (defined in `framework.py`):
```python
DUAL_SOURCE_MAP = {
    'earthquakes': 'earthquakes-v2',   # USGS + EMSC
    'disasters': 'disasters-v2',       # GDACS + Wikipedia
    'weather': 'weather-v2',           # NOAA NWS + wttr.in
}
```
V2 collectors are automatically paired with their primary by `run_dual_source_collection()`.
To add a new v2 source, drop a `*_v2.py` file in `collectors/`, register it, and add
the pairing to `DUAL_SOURCE_MAP`.

**Usage:**
```
python3 run.py                              # Middle East, all layers
python3 run.py --region ukraine             # Ukraine region
python3 run.py --region world --layers all  # Everything, everywhere
python3 run.py --region europe --layers weather,airports  # Selected layers
python3 run.py --region middle-east --dry-run            # Generate without deploy
python3 run.py --list-regions               # Show 8 defined regions
python3 run.py --list-layers                # Show all registered layers
```

**Available regions:** `middle-east`, `europe`, `south-china-sea`, `ukraine`, `africa`, `india-ocean`, `pacific-rim`, `world`

**Adding a new layer:** Create a file in `collectors/`, add `@register_layer('my-layer')` decorator with a class inheriting `BaseCollector`, implement `fetch(region) -> list[GeoFeature]`, then import in `run.py`. That's it — no wiring changes needed.

## Adding a New Layer from Scratch

See `references/lg-data-visualization/worldmonitor-sources.md` for a catalog of ~20 additional
data layers that World Monitor uses and how to integrate each one (ACLED
for conflict, NASA FIRMS for wildfires, AISStream for ship tracking, etc.).

If a user asks for data that isn't in our collector set yet:
1. Check `references/lg-data-visualization/worldmonitor-sources.md` for a known free API
2. If not listed, search for `open source <topic> api free` or check
   `references/lg-data-visualization/dual-source-apis.md` for secondary-source patterns
3. Present a plan to the user (source URL, auth, cadence, expected output)
4. Build collector + optional v2, register, test with --dry-run, deploy

### What to capture as reference files
- Each data source API gets its own `references/<source>.md` with: URL, auth method, rate limits, response format, example
- KML generation conventions in `references/lg-data-visualization/kml-generation-rules.md`
- Screen placement decisions in `references/lg-data-visualization/screen-placement.md`

---

## References

Loaded references convention:
- `references/lg-data-visualization/kml-generation-rules.md` — Complete KML ruleset for data visualization
- `references/lg-data-visualization/screen-placement.md` — What goes where on which screen (LG Wiki + Nara conventions)
- `references/lg-data-visualization/dual-source-comparison.md` — Dual-source architecture, proximity matching algorithm, status levels, adding new v2 collectors
- `references/lg-data-visualization/symbol-icons.md` — Google Maps KML icon palette mappings
- `references/lg-data-visualization/usgs-earthquakes.md` — USGS earthquake feed: URL, response format, KML generation pattern
- `references/lg-data-visualization/eonet-natural-events.md` — NASA EONET natural events API
- `references/lg-data-visualization/noaa-weather.md` — NOAA NWS weather alerts API
- `references/lg-data-visualization/gdacs-disasters.md` — GDACS global disaster events API
- `references/lg-data-visualization/military-bases-config.md` — Static military bases configuration
- `references/lg-data-visualization/vm-startup-pitfall.md` — VM Earth startup fix (launch-earth.sh hangs on unreachable slaves)
- `references/lg-data-visualization/opensky-air-traffic.md` — OpenSky API, ICAO hex prefixes, rate limits
- `references/lg-data-visualization/rss-news-feeds.md` — RSS news aggregation, topic classification, fan-out geo-positioning
- `references/lg-data-visualization/icon-generation.md` — Custom PNG icon generation via Pillow (16 icons, heading rotation support)
- `references/lg-data-visualization/dual-source-apis.md` — Secondary source APIs: EMSC endpoint quirks (format=json NOT geojson, ISO time not Unix), wttr.in WMO code mapping, Wikipedia Current Events parser approach with place-based geo-location
- `references/lg-data-visualization/fusion-engine.md` — Fusion engine API: FusionPolicy, DataQualityNote, FusionResult, confidence encoding, status logic, adding new policies for new layers
- `references/lg-data-visualization/worldmonitor-sources.md` — Catalog of ~30 data layers from the World Monitor (74k star) project including ACLED conflict events, NASA FIRMS wildfires, AISStream ship tracking, NGA maritime warnings, Safecast radiation, HDX humanitarian data — with verified-working URLs and auth requirements for each
- `references/lg-data-visualization/dual-source-apis.md` — Secondary source APIs (EMSC, wttr.in, Wikipedia Current Events), source comparison logic, disclaimer overlay pattern

## Templates
- `templates/lg-data-visualization/collector-base.py` — Base Python collector scaffold with KML generation and deploy
- `templates/lg-data-visualization/placeholder.kml` — Minimal valid KML with LookAt (start here for any test)

## Related Skills
- `lg-kml-tours` — Tour KML generation, gx:Tour patterns, camera animation
- `lg-orbit-workflow` — Smooth orbit parameters, flyToView conflicts, Pi-based SSH orbit
- `lg-ssh-control` — KML deployment helpers, refresh controls, relaunch
- `lg-wiki-reference` — LG Wiki lookup for screen placement, KLM debugging
