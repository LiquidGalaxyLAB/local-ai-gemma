---
name: lg-user-guide
description: User guide for the Liquid Galaxy + WM-LG Data Collector system — first-time setup, capabilities, example prompts, LG Wiki standards, and extensibility for both technical and non-technical users.
version: 1.1.0
author: Nara
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [LiquidGalaxy, user-guide, reference, capabilities, prompts, setup]
    related_skills: [lg-ssh-control, lg-data-visualization, lg-kml-tours, lg-orbit-workflow, lg-wiki-reference]
---

# Liquid Galaxy User Guide

> Welcome! This system turns a multi-screen Google Earth setup into a live,
> voice-driven geo-intelligence display. You can show real-time earthquakes,
> air traffic, weather, news, disasters, military activity — anything with
> a location — on a panoramic Liquid Galaxy rig of any screen count.
>
> **Just describe what you want to see. Nara builds it.**

---

## 1. Getting Started

### First-Time Setup (One Time Only)

When you start using this project for the first time on your system, Nara will
collect your Liquid Galaxy details exactly once and save them for all future
sessions. **This is mandatory** — the system needs to know how to reach your rig.

Nara will ask for **all of these at once**:

```
1. IP address of the LG master computer (e.g. 192.168.1.200)
2. SSH port (usually 22, but VM tunnels often use 2222)
3. SSH username (usually "lg")
4. SSH password (standard: "lg", but can vary)
5. Number of screens (3, 5, 7, etc. — works with any count)
```

> **Important:** Before answering, check your LG setup to confirm these details.
> The standard LG password across official rigs is `lg`, but your rig may differ.

After you provide these, Nara:
1. **Verifies** the connection by SSHing into the master computer
2. **Detects** whether it's a real machine or a VirtualBox VM
3. **Saves** the details to persistent memory so you never need to repeat them
4. **Reports** the connection status

On every future session, Nara auto-connects and picks up where you left off.
If SSH ever fails (IP changed, rig powered off), you'll be asked again.

> **Reference:** The official LG Wiki at https://lg-wiki-coral.vercel.app/ is the
> authoritative source for standard LG architecture, screen counts, yaw offsets,
> and content conventions. Nara references it when verifying your setup.

### New Rig Checklist (Restoring Backup on a Different System)

When someone restores this project backup on a DIFFERENT Liquid Galaxy rig,
Nara runs an automatic telemetry check after collecting credentials:

1. **Detect Earth user** — Earth may run as `lg1` not `lg`. This determines
   which `myplaces.kml` gets edited. Patching the wrong file is the #1 cause
   of "KML invisible" issues.
2. **Verify correct myplaces path** — Confirms Earth's myplaces.kml location.
3. **Check Apache port** — LG standard is port 81, not 80.
4. **Verify KML serving** — `curl http://lg1:81/kml/master.kml` must return 200.
5. **Check query.txt daemon** — If absent, flytoview commands won't work;
   camera positioning relies on KML `<LookAt>` + `flyToView=1`.
6. **Check slave reachability** — Slaves are on internal 10.42.42.x network.
   Nara reaches them through the master as a gateway.
7. **Apply slave master refresh** — All frames need refreshInterval on their
   Master KML NetworkLink so KML updates propagate without restart.
8. **One-time Earth restart** — Required after myplaces.kml edits. After that,
   all future KML updates appear within 3 seconds on all screens without
   any restart.
9. **Deploy test KML** — Simple polygon or placemark to confirm display.

This all happens automatically — you just provide credentials once.

### After Setup — Just Talk

Once connected, just describe what you want:

```
Nara, show earthquakes in Japan
Nara, start an orbit over the Taj Mahal
Nara, run the full World Monitor for the Middle East
Nara, connect to the LG
```

### What Happens When You Make a Request

The system follows a consistent pipeline:

1. **Connect** — Nara verifies the LG rig is reachable (auto if remembered)
2. **Understand** — Clarifies what, where, and how you want it shown
3. **Build** — Fetches data, generates KML, or writes animation scripts
4. **Deploy** — Sends to the LG screens via SSH (no manual copying needed)
5. **Verify** — Reports what was deployed and what to look for

---

## 2. Capabilities

### Live Geo-Data Visualization

Show real-time data from multiple independent sources on the LG screens.
Every live-data layer is cross-checked against a second API — if sources
disagree, a "Data may be approximate" warning appears automatically.

| What To Show | Data Source(s) | Example Prompt |
|-------------|----------------|---------------|
| **Earthquakes** | USGS + EMSC (dual-source) | "Show recent earthquakes in the Middle East" |
| **Air Traffic** | OpenSky Network | "Show flights over Europe right now" |
| **Weather Alerts** | NOAA NWS + wttr.in (global) | "Are there any weather warnings in India?" |
| **Disasters & Crises** | GDACS + Wikipedia Current Events | "What disasters are happening in the world?" |
| **Military Bases** | 37 strategic bases (config) | "Show me all US military bases in the Middle East" |
| **Major Airports** | 35 international airports | "Highlight all major airports in Europe" |
| **Maritime / Ships** | Naval bases, ports, chokepoints (config) | "Show Indian Navy bases and major ports" |
| **News Headlines** | 8 RSS feeds (BBC, AP, Al Jazeera, France24, DW, NPR, Reuters) | "Show today's news on the right screen" |

**All at once:** `"Nara, run a full World Monitor on the Middle East"`
This deploys every data layer to the main screen + news on the right screen.

### Regions (Pre-Configured)

The system has 9 regions ready to go. Just name one:

| Region | Covers | Bounding Box |
|--------|--------|-------------|
| `middle-east` (default) | Israel, Iran, Iraq, Arabia, Turkey, Egypt | 12-40°N, 35-60°E |
| `india` | Indian subcontinent + Indian Ocean | 5-37°N, 65-100°E |
| `europe` | All of Europe | 35-70°N, 10°W-40°E |
| `ukraine` | Ukraine + Eastern Europe | 44-55°N, 22-40°E |
| `south-china-sea` | South China Sea, Philippines | 0-25°N, 100-125°E |
| `africa` | Entire African continent | 35°S-37°N, 20°W-52°E |
| `india-ocean` | Indian Ocean rim | 30°S-30°N, 40-100°E |
| `pacific-rim` | Pacific Ring of Fire | 45°S-60°N, 115°E-70°W |
| `world` | Everywhere | Global |

### Data Quality & Cross-Verification

Every live-data layer uses TWO independent APIs. Nara compares them and tells
you if sources disagree. When there's significant variance, the LG screens
show a yellow warning: **"Data may be approximate — cross-reference with
official channels for critical decisions."**

Pairing:
- **Earthquakes**: USGS (global, M4.5+) + EMSC (European network, M2.5+)
- **Weather**: NOAA NWS (US only) + wttr.in / WMO codes (global)
- **Disasters**: GDACS (automated alerts) + Wikipedia Current Events (human reports)

### Camera & Animation

| What | How It Looks | Example Prompt |
|------|-------------|---------------|
| **Static view** | Camera locks on a location | "Show me the Taj Mahal" |
| **Smooth orbit** | Camera circles around a landmark | "Orbit around the Burj Khalifa" |
| **Fly-through tour** | Camera travels between locations | "Create a tour visiting Mumbai, Delhi, and Bangalore" |
| **Multi-stop cinematic** | Slow fly-in, zoom, orbit | "Show me a cinematic tour of the Himalayas" |

### LG System Control

| Command | What It Does | Example Prompt |
|---------|-------------|---------------|
| **Connect** | Verifies SSH connection to LG | "Connect to the LG" |
| **Relaunch** | Restarts Google Earth on all screens | "Relaunch Earth" |
| **Reboot** | Reboots all LG computers | "Reboot the LG rig" |
| **Power off** | Shuts down all screens | "Power off" |
| **Refresh KML** | Sets 3-second auto-refresh for new data | "Make data update automatically" |
| **Clear display** | Removes all placemarks from screen | "Clear the display" |
| **Fly camera** | Moves camera to coordinates | "Fly to 27.17°N, 78.04°E" |

---

## 3. Cool Ideas & Example Prompts

### For the Curious Explorer

```
"Show me everything happening in the South China Sea right now"
"Any major earthquakes in the Pacific Ring of Fire today?"
"What's the air traffic like over Europe?"
"Are there any active wildfires?"
"Show me the news from the Middle East"
```

### For Presentations & Demos

```
"Start with a wide view of the world, then fly to active earthquake zones"
"Give me a 2-minute cinematic tour of the top 10 highest mountains"
"Create a fly-over of the Himalayas with peak labels"
"Show a smooth orbit around the Eiffel Tower"
```

### For Monitoring & Operations

```
"Run the full World Monitor for Ukraine"
"Start continuous updates for the Middle East, data only"
"Now turn on the news on the right screen too"
"What changed since the last update?"
"Any data sources showing different results today?"
```

### For Custom Content

```
"Draw a polygon showing the flood extent in Kerala"
"Place a 3D marker showing the height of Mount Everest"
"Put a logo in the top-left corner of the left screen"
"Add a custom icon for my office location"
"Show a line connecting Beijing to Moscow"
```

### For System Management

```
"Check if the LG is online"
"Restart the displays, they've been running all day"
"Clear everything and show a blank screen"
"What was the data discrepancy yesterday?"
"How long has the LG been running?"
"Schedule this to update every hour"
```

---

## 4. Understanding the Screens

### Frame-Count-Agnostic Design

This system works with **any number of screens** — 3, 5, 7, or more. It never
hardcodes a screen count. Instead, it reads `$LG_FRAMES` from the rig's
`shell.conf` and adapts all layout decisions dynamically.

You tell Nara your screen count once during first-time setup, and everything
adjusts automatically.

### Standard LG Screen Layout

Per the [LG Wiki](https://lg-wiki-coral.vercel.app/), a Liquid Galaxy rig
follows a predictable naming and positioning convention:

```
Center screen  → lg1 (0° yaw, the master)
Left screens   → lg{N-1}, lg{N-3}, ... (negative yaw, working outward)
Right screens   → lg2, lg4, ... (positive yaw, working outward)
```

Each slave screen beyond the two sides has its own yaw offset: -80°, -40°,
0°, +40°, +80° for a 5-screen rig, for example.

### LG Wiki Content Placement Standards

The LG Wiki defines two key content positioning rules:

#### 1. Logo → Leftmost Slave Screen

Logos and branding overlays go only on the **leftmost screen**. Formula (root): 
```
leftRig = floor(N/2) + 2     # leftmost screen number
```

| Screens N | Leftmost Slave (Logo Here) |
|-----------|---------------------------|
| 3 | slave_3.kml (lg3) |
| 5 | slave_4.kml (lg4) |
| 7 | slave_5.kml (lg5) |

The logo file (PNG) is served from `http://lg1:81/kml/logo.png` and placed
as a ScreenOverlay in the top-left corner.

#### 2. News / Heavy Balloons → Rightmost Slave Screen

HTML-heavy content like news articles, data tables, and detailed balloon
descriptions go **only on the rightmost screen**. **Use the news-card balloon
pattern** — dark HUD cards with category color bars, large headlines,
source+timestamp, summary, and category badges, stacked in one auto-opened
balloon (`scripts/news_card_balloon.py` in `lg-kml-tours`, escaped HTML —
VM-safe). Root formula (LG Wiki
standard): screen numbering starts at 1 with the master (lg1), total screens
= N (lg1..lgN). **Right-most screen = floor(N/2) + 1; left-most = floor(N/2) + 2.**
```
rightRig = floor(N/2) + 1     # rightmost screen number
leftRig  = floor(N/2) + 2     # leftmost screen number
```

| Screens N | Rightmost Slave (News/Balloons ONLY Here) | Leftmost Slave (Logo) |
|-----------|------------------------------------------|-----------------------|
| 3 | slave_2.kml (lg2) | slave_3.kml (lg3) |
| 5 | slave_3.kml (lg3) | slave_4.kml (lg4) |
| 7 | slave_4.kml (lg4) | slave_5.kml (lg5) |

**Hard rule:** balloons, news, text panels, and data cards go ONLY on the
rightmost screen — never on master.kml (center) and never on left/odd slaves.

#### 3. Master Data → All Screens (via master.kml)

All data placemarks (earthquakes, flights, weather, etc.) go to `master.kml`
on all screens. ViewSync ensures the camera is synchronised across every
display. This file auto-updates every 3 seconds via the master NetworkLink
refresh — no relaunch needed.

### Example Layouts

**3-Screen Rig:**
```
┌──────────┬──────────┬──────────┐
│  lg3     │  lg1     │  lg2     │
│  LEFT    │  CENTER  │  RIGHT   │
│ -36.5°   │  0°      │  +36.5°  │
│          │          │          │
│  Logo    │  All     │  Data    │
│  + News  │  data    │  layers  │
│          │  layers  │          │
└──────────┴──────────┴──────────┘
```

**5-Screen Rig:**
```
┌──────────┬──────────┬──────────┬──────────┬──────────┐
│  lg4     │  lg3     │  lg1     │  lg2     │  lg5     │
│  LEFT-2  │  LEFT-1  │  CENTER  │  RIGHT-1 │  RIGHT-2 │
│  -80°    │  -40°    │  0°      │  +40°    │  +80°    │
│          │          │          │          │          │
│  Logo    │  View    │  All     │  Data    │  News    │
│  only    │  only    │  data    │  layers  │  + data  │
└──────────┴──────────┴──────────┴──────────┴──────────┘
```

### How ViewSync Works

The master (lg1) broadcasts its camera position via UDP at 60 Hz. All slaves
receive this broadcast and apply their fixed yaw offset. This means:

- Camera movement on the master automatically syncs to all screens
- Each screen shows a slightly different angle based on its yaw offset
- The panoramic effect comes from these overlapping, offset views
- Data placemarks appear on every screen because they're rendered by each
  Earth instance independently

---

## 5. How To Add New Capabilities

The system is designed to be extended — when you need something new,
the foundation already handles the hard parts (SSH, KML deploy, refresh,
animation). A new use case needs just 2-3 things:

### For Non-Technical Users

Just describe what you want:

> "Nara, I want to show live cyclone tracking data on the LG"

Nara will:
1. Research available free APIs for the data
2. Present a plan with data sources and region
3. Build the collector after you approve
4. Deploy and verify on the LG
5. Ask if you want to save it as a reusable skill

### For Technical Users (The Architecture)

The system has three extension points:

#### 1. New Data Layer (Real-Time API)

Create a Python collector in `/home/nara/wm-collector/collectors/`:

```
collectors/
├── your_new_layer.py        # Your collector (10-60 lines)
├── your_new_layer_v2.py     # Optional: second source for cross-verify
├── __init__.py
```

Use the `@register_layer('your-layer')` decorator and inherit from
`BaseCollector`. Implement `fetch(region) → list[GeoFeature]`.
Import it in `run.py` — done.

**Already-working patterns you can copy:**
- Live API: `earthquakes.py` (HTTP fetch + transform + KML)
- Static config: `military_bases.py` (hardcoded coord list)
- Text-parsed: `disasters_v2.py` (HTML scrape → geo-locate)

#### 2. New KML Content (Static)

Add a template KML file — Nara can deploy any valid KML. See
existing templates for coordinate format, style blocks, and LookAt.

#### 3. New Animation / Camera Pattern

Add a Python script to the orbit library. Copy `templates/vm-orbit-template.py`
or `templates/pi-orbit-template.sh` and edit the parameters.

### What the Foundation Handles

When you add something new, these work automatically:

| Feature | How It's Handled |
|---------|-----------------|
| **SSH connection** | lg-ssh-control pre-flight |
| **KML deploy** | write → scp → sudo cp (no-touch) |
| **Screen refresh** | 3s NetworkLink auto-picks up changes |
| **Camera control** | `/tmp/query.txt` daemon accepts flytoview |
| **Multi-screen** | ViewSync syncs camera across all screens |
| **Screen roles** | Leftmost = logo, rightmost = news (auto-calculated by frame count) |
| **Dual-source** | framework.py `compare_layers()` built in |
| **Disclaimers** | KML generator injects warnings automatically |
| **Cron scheduling** | cronjob tool schedules recurring runs |

---

## 6. CLI Reference

For users comfortable with the command line:

```
cd /home/nara/wm-collector

python3 run.py                                          # Middle East, all layers
python3 run.py --region india                           # India region
python3 run.py --region world --layers all              # Everything
python3 run.py --region europe --layers air-traffic     # Just flights
python3 run.py --dry-run                                # Generate without deploy
python3 run.py --single-source                          # Skip v2 comparison
python3 run.py --no-disclaimers                         # Suppress data warnings
python3 run.py --data-only                              # Skip news (master only)
python3 run.py --news-only                              # News to right screen only
python3 run.py --list-regions                           # Show all regions
python3 run.py --list-layers                            # Show all data layers
```

---

## 7. Troubleshooting Quick Guide

| Symptom | Likely Cause | What Nara Will Do |
|---------|-------------|-------------------|
| "Connection refused" | LG IP changed or rig off | Re-check IP, ask for new one if needed |
| "Earth not starting" | Stuck launch script on VM | Kill stuck process, start Earth directly |
| "Data not appearing" | NetworkLink refresh not set | Run `lg-refresh-set` + `lg-master-refresh-set` |
| "Camera not moving" | flytoview command not processed | Check /tmp/query.txt was consumed |
| "Red X icons" | Image path wrong in KML | Fix URL to use lg1:81/ pattern |
| "News on wrong screen" | Frame-count mismatch | Update screen count in memory, redeploy |
| "Sources disagree" | Normal — dual-source mismatch | Yellow disclaimer appears — data is approximate |
| "Blank screen after clear" | KML was deleted, not overwritten | Deploy fresh blank KML |

---

## 8. Data Pipeline Architecture

```
User says "show earthquakes in Japan"
  │
  ▼
Nara loads lg-ssh-control → checks SSH → connects to lg1
  │
  ▼
Nara loads lg-data-visualization
  ├── Fetches from USGS (primary earthquake API)
  └── Fetches from EMSC (secondary, for cross-check)
  │
  ▼
Nara calls compare_layers() → 7 vs 2 events → some variance
  │
  ▼
KML generator creates master.kml with:
  ├── Placemarks for each earthquake (color-coded by magnitude)
  ├── LookAt centered on Japan (camera auto-positions)
  └── Data Accuracy folder (if sources disagree)
  │
  ▼
Deploy: write → scp to lg1 → sudo cp → 3s refresh
  │
  ▼
LG screens update automatically. Nara reports:
  "7 earthquakes from USGS, 2 from EMSC — sources differ slightly.
   Yellow warning on screen. Data may be approximate."
```

**Screen assignment** is always frame-count-agnostic:
- `master.kml` → all screens (via master NetworkLink + ViewSync)
- `slave_<N>.kml` → news on rightmost screen (automatically calculated)
- Logo overlay → leftmost slave screen (formula: `floor(N/2) + 2`)

---

## 9. Project Structure

```
/home/nara/wm-collector/          # Main data pipeline
├── run.py                        # CLI orchestrator
├── framework.py                  # Region model, GeoFeature, @register_layer
├── kml/generator.py              # LG-compliant KML with local icons
├── collectors/                   # Data source collectors
│   ├── earthquakes.py            # USGS (primary)
│   ├── earthquakes_v2.py         # EMSC (secondary)
│   ├── weather.py                # NOAA NWS (primary)
│   ├── weather_v2.py             # wttr.in (secondary)
│   ├── disasters.py              # GDACS (primary)
│   ├── disasters_v2.py           # Wikipedia Current Events (secondary)
│   ├── air_traffic.py            # OpenSky Network
│   ├── news.py                   # 8 RSS feeds
│   ├── military_bases.py         # Static config
│   ├── airports.py               # Static config
│   ├── ships.py                  # Maritime config
│   └── natural_events.py         # NASA EONET

/home/nara/wiki/                  # Knowledge base (20+ pages)
├── concepts/
│   ├── wm-lg-collector.md        # Full pipeline documentation
│   ├── lg-kml-patterns.md        # KML format reference
│   ├── lg-orbit-animation.md     # Animation patterns
│   ├── lg-architecture-overview.md
│   ├── lg-vm-quirks.md
│   └── ...
├── log.md                        # All changes recorded here
└── index.md

/home/nara/lg-architecture.md     # Foundation architecture document
```

---

## 10. Skill Reference

| Skill | What It Does | When Nara Loads It |
|-------|-------------|-------------------|
| `lg-ssh-control` | SSH connection, reboot, poweroff, KML deploy, refresh, first-time setup | Every LG operation (mandatory first) |
| `lg-data-visualization` | Data pipeline: collectors, APIs, KML generation, dual-source | Showing geo-data on screen |
| `lg-kml-tours` | KML animation, orbit scripts, 3D shapes, playtour= | Camera movement, tours, orbits |
| `lg-orbit-workflow` | Smooth orbit via SSH with overlap timing | When flytoview orbits stutter |
| `lg-wiki-reference` | LG community wiki knowledge | Troubleshooting, architecture questions |
| `lg-vm-network-setup` | VM network topology, SSH tunnel setup | First-time VM setup or network issues |
| `lg-user-guide` | This guide — capabilities, prompts, setup | On "what can you do" or "show me around" |
| `lg-use-cases` | 10 high-impact use cases with layer stacks & camera patterns | Setting up a specific monitoring scenario |
| `geography-educator` | Educational KML generators — Date Line, Monsoon, Turkey EQ, Ports of India | Teaching geography concepts on LG |
| `india-news-storyteller` | Autonomous BBC India RSS → KML tour pipeline | Daily India news auto-tour |
| `liquid-galaxy-control` | Quick SSH control actions | Fast relaunch/reboot/poweroff |

### Implemented Use Cases

These are pre-configured scenarios you can run immediately:

| # | Use Case | What You See | Command |
|---|----------|-------------|---------|
| 1 | **Global Situational Awareness Wall** | All conflict zones, hotspots, military bases, air traffic, earthquakes simultaneously — auto-rotating global view | `python3 run.py --region world --layers all` |
| 2 | **Maritime Domain Awareness** | Ports, naval bases, chokepoints (Hormuz, Malacca, Suez), tanker terminals across 3 screens | `python3 run.py --region middle-east --layers ships` |
| 3 | **Natural Disaster Command Center** | Auto-fly to latest M5+ earthquake or large wildfire — one screen shows disaster zone, another shows damage | `python3 run.py --region world --layers earthquakes,disasters,natural-events` |
| 4 | **Energy & Infrastructure Monitoring** | Gulf oil terminals, Hormuz chokepoints, bulk carrier routes — belt-and-road corridor view | `python3 run.py --region middle-east --layers ships` |
| 5 | **Geopolitical Briefing Room** | Military bases, naval forces, conflict zones, news headlines with narration | `python3 run.py --region world --layers military-bases,ships,news` |
| 6 | **Live Aviation Watch** | 100 aircraft with heading-rotated icons at actual altitude — track corridors over Ukraine, NATO frontiers | `python3 run.py --region europe --layers air-traffic` |
| 7 | **Supply Chain & Trade Flow** | Port capacities, chokepoint status, major trade lanes with color-coded flow intensity | `python3 run.py --region world --layers ships` |
| 8 | **Cyber / Undersea Infrastructure** | Undersea cable routes, internet outage overlay | (requires cable data collector) |
| 9 | **Geography Education — Date Line** | Red zigzag date line vs cyan 180° meridian, "Tomorrow" west, "Yesterday" east | Pre-built KML via geography-educator skill |
| 10 | **Geography Education — India Monsoon** | Wind arrows, Western Ghats orographic effect, rain shadow, wettest/driest locations | Pre-built KML via geography-educator skill |
| 11 | **Geography Education — Turkey Earthquake** | M7.8 epicenter, East Anatolian Fault rupture, plate boundaries, aftershocks | Pre-built KML via geography-educator skill |
| 12 | **Geography Education — Ports of India** | 9 major ports with capacities, naval bases, strategic chokepoints | Pre-built KML via geography-educator skill |
| 13 | **India News Storyteller** | Autonomous daily news tour — fetches BBC India RSS, extracts locations, generates tour KML, deploys, positions camera, prints narration | Cron job: runs every 30 min |

### Voiceover & Narration

For presentations and teaching, use voiceover alongside visuals:

```bash
# Generate narration for the current display
"Explain the International Date Line with voiceover"
"Show me the Turkey earthquake and explain how it happened"

# Nara generates two audio clips:
# 1. General explanation (the concept)
# 2. Screen guide (what you're seeing on the LG)
```

Audio plays via Bluetooth headphones connected to the Pi. Kill previous playback with `pkill -f pw-play` before generating new audio.
