---
name: lg-use-cases
description: Ten high-impact Liquid Galaxy use cases for situational awareness, maritime monitoring, disaster response, energy, geopolitics, aviation, cyber infrastructure, and trade visualization — with layer stacks, camera patterns, and refresh cadences.
version: 1.0.0
author: Nara
license: MIT
platforms: [linux]
---

# LG Use Cases — Agentic Situational Awareness Wall

This skill documents 10 production-ready use cases for Liquid Galaxy as a multi-screen situational awareness platform. Each use case defines the layer stack, data sources, camera movement pattern, refresh cadence, and LG screen layout.

**Core Tools:** wm-collector (`/home/nara/wm-collector/`), India News Storyteller, Geography Educator, Date Line Educator, Monsoon Educator, Ports of India Educator.
## KML Prerequisites for VM Earth 7.3.3
No gx namespace, no CDATA in descriptions, use Google CDN icons (`http://maps.google.com/mapfiles/kml/...`), avoid local icon URLs.

## Text Placement Rule (Critical)
**All text content goes to the right-screen text panel only** — never as placemark labels on the Earth globe. See `references/right-screen-panel.md` for the ScreenOverlay PNG generator and deployment pattern. See `references/right-screen-text-panel.md` for the original reference.

---

## 1. Global Situational Awareness Wall
All conflict zones, hotspots, military bases plotted simultaneously.

| Layer | Source | Type |
|-------|--------|------|
| 🌍 Earthquakes | USGS + EMSC | Live (dual) |
| 🌋 Natural Events | NASA EONET | Live |
| ✈ Air Traffic | OpenSky Network | Live (5 min) |
| ✈ Military Bases | Static config (37 bases) | Static |
| 🚢 Ships & Maritime | Static config (ports, bases, chokepoints) | Static |
| ⛈ Weather Alerts | NOAA NWS | Live (5 min) |

**Camera:** Auto-rotating global view at 12,000km range, or 5-min loop flying between top 10 hotspots. Use `flytoview` via query.txt with 30s dwell per location.

**LG Advantage:** 3 screens show 120° of horizon — wider AoI than any single monitor.

**Refresh:** WM collector cron (30 min) → Apache master.kml → 3s NetworkLink on all frames.

**Deploy:**
```
cd /home/nara/wm-collector && python3 run.py --region world --layers earthquakes,air-traffic,military-bases,ships,weather --single-source
```

---

## 3. Maritime Domain Awareness
AIS density zones, trade routes, chokepoint status, tanker tracking, cable advisories.

| Layer | Source | Type |
|-------|--------|------|
| 🚢 Ships & Maritime | Expanded static config | Static (50+ ports, bases, chokepoints) |
| 🚢 Strait of Hormuz chokepoints | Custom Middle East data | Static (3 chokepoints) |
| 🔵 Indian Ocean chokepoints | Malacca, Six Degree, Nine Degree | Static |

**Camera:** Focus on chokepoints — dedicate one screen per chokepoint:
- lg1: Strait of Hormuz (26.5°N, 56°E, 500km)
- lg2: Strait of Malacca (5°N, 95°E, 500km)  
- lg3: Bab-el-Mandeb (12.5°N, 43.5°E, 500km)

**Ships data** includes: 37 naval bases, 25+ ports, 8 strategic chokepoints across India, Middle East, and US East Coast.

**Deploy:**
```
cd /home/nara/wm-collector && python3 run.py --region world --layers ships --single-source --data-only
```

---

## 4. Natural Disaster Command Center
Earthquakes, wildfires, weather alerts, climate anomalies, displacement flows.

| Layer | Source | Type |
|-------|--------|------|
| 🌍 Earthquakes | USGS GeoJSON (M4.5+, week) | Live (5-10 min) |
| 🌋 Natural Events | NASA EONET | Live (15-30 min) |
| ⛈ Weather Alerts | NOAA NWS API | Live (5 min) |
| 📰 Related News | RSS feeds (BBC, Al Jazeera, France24) | Live (30 min) |

**Camera:** Auto-fly to the latest M5+ earthquake or large wildfire. Poll USGS every 30 min; if new M5+ detected, deploy KML centered on epicenter at 500km range.

**LG Advantage:** One screen shows the disaster zone (Earth view), another shows displacement/destruction data (slave_3.kml news).

**Auto-fly trigger pattern:**
```
rm -f /tmp/query.txt && echo "flytoview=<LookAt><longitude>EPI_LON</longitude><latitude>EPI_LAT</latitude><range>500000</range><tilt>60</tilt>...</LookAt>" > /tmp/query.txt
```

**Deploy:**
```
cd /home/nara/wm-collector && python3 run.py --region world --layers earthquakes,natural-events,weather --single-source
```

---

## 5. Energy & Infrastructure Monitoring
Pipelines, energy infrastructure, fuel shortages, renewable installations, mining sites.

| Layer | Source | Type |
|-------|--------|------|
| 🚢 Gulf ports & tanker terminals | Expanded ships config | Static (Ras Tanura, Bandar Abbas, Jebel Ali, etc.) |
| 🚢 Chokepoints | Strait of Hormuz (3 points) | Static |
| 📰 Energy news | RSS feeds filtered for energy keywords | Live |

**Camera:** Belt-and-Road corridor view, or Strait of Hormuz with tanker overlay at 500km range.

**Key infrastructure points:** Ras Tanura (Saudi Aramco — largest oil terminal), Bandar Abbas (Iran), Jebel Ali (UAE), Strait of Hormuz chokepoints.

**Deploy:**
```
cd /home/nara/wm-collector && python3 run.py --region middle-east --layers ships,news --single-source
```

---

## 6. Geopolitical Briefing Room
Conflict zones, military bases, sanctions, cyber threats, instability indices.

| Layer | Source | Type |
|-------|--------|------|
| ✈ Military Bases | Static config (37 bases) | Static |
| 🚢 Naval Bases | Expanded config (India + Middle East + US) | Static |
| 🌍 Earthquakes | USGS (proxy for conflict-zone infrastructure stress) | Live |
| 📰 News | RSS feeds (conflict-focused filtering) | Live |

**Camera:** Country-level flythrough for top 10 most unstable regions. Each stop at 2,000km range, 5s dwell, with TTS narration.

**TTS narration pattern:** "This is the [region], [key fact]. [Current event headline]."

**LG Advantage:** 3 screens compare different theaters simultaneously — Ukraine on lg1, Middle East on lg2, South China Sea on lg3.

**Deploy:**
```
cd /home/nara/wm-collector && python3 run.py --region world --layers military-bases,ships,earthquakes,news --single-source
```

---

## 8. Live Aviation Watch
Military flights, flight delays, NOTAM rings, airport status.

| Layer | Source | Type |
|-------|--------|------|
| ✈ Air Traffic | OpenSky Network (100 aircraft) | Live (5 min) |
| 🏗 Airports | Static config (35 major airports) | Static |

**Camera:** Track specific military flight corridors — Ukraine frontier (50°N, 30°E), NATO frontiers, South China Sea (12°N, 112°E).

**Aircraft visualization:** Icons rotated by heading (`<heading>` in IconStyle), altitude shown via 3D coordinates (`relativeToGround`), color-coded by type (civilian/military).

**Deploy:**
```
cd /home/nara/wm-collector && python3 run.py --region world --layers air-traffic,airports --single-source --data-only
```

---

## 9. Cyber / Undersea Infrastructure Map
Undersea cables, internet outages, GPS jamming, cyber threat heat zones.

| Layer | Source | Type |
|-------|--------|------|
| 💻 Cables | Static config (major undersea cable routes) | Static |
| 📰 News | RSS filtered for cyber/outage keywords | Live |

**Camera:** Atlantic cable corridor view — damage zones overlaid. Focus on cable landing stations in Egypt (Suez), Singapore, Marseille.

**Data structure for cable routes:** Use KML LineString with coordinates tracing major cable paths. Color-code by status (green=active, yellow=degraded, red=damaged).

**Deploy (placeholder — cable data needs building):**
```
cd /home/nara/wm-collector && python3 run.py --region world --layers news --single-source --data-only
# Then overlay cable LineStrings via geo_kml generator
```

---

## 10. Supply Chain & Trade Flow Visualization
Trade routes, chokepoint status, commodity ports, tanker positions.

| Layer | Source | Type |
|-------|--------|------|
| 🚢 Ships & Maritime | Expanded config (50+ ports) | Static |
| 🚢 Chokepoints | 8 strategic chokepoints | Static |
| 🏗 Major Ports | Ports with capacity data | Static |

**Camera:** Pan across the major global trade lanes with color-coded flow intensity. Sequence: Shanghai → Singapore → Malacca → Colombo → Hormuz → Suez → Rotterdam.

**Trade route flows:** Use KML LineStrings with varying width/color to indicate trade volume intensity (thicker = more traffic).

**Port capacity data** embedded in placemark names:
- "Mumbai Port - 25% of India's seaborne trade"
- "JNPT - 5M TEUs annually"
- "Mundra - 140M tonnes (largest private)"
- "Ras Tanura - Saudi Aramco oil terminal"
- "Jebel Ali - Top 10 global container port"

**Deploy:**
```
cd /home/nara/wm-collector && python3 run.py --region world --layers ships --single-source --data-only
# Then add educational port labels via ports_edu workflow
```

---

## Camera Control Quick Reference

| Action | Command |
|--------|---------|
| Fly to location | `rm -f /tmp/query.txt && echo "flytoview=<LookAt><longitude>LON</longitude><latitude>LAT</latitude><range>RNG</range><tilt>TILT</tilt><heading>HDG</heading><altitudeMode>relativeToGround</altitudeMode></LookAt>" > /tmp/query.txt` |
| Stop tour | `rm -f /tmp/query.txt && echo "exittour=true" > /tmp/query.txt` |
| Reset query daemon | `rm -f /tmp/query.txt` (then write fresh flytoview) |

**Key ranges:** Continent=3,000-5,000km, Region=500-1,000km, City=50-200km, Port=10-50km.

## Standard Screen Layout (3-screen LG)

### Screen Roles
| Screen | Yaw Offset | Content |
|--------|-----------|---------|
| lg1 (center) | 0° | **Earth KML visualization** — main data layers (master.kml via NetworkLink) |
| lg2 (left) | -36.5° | **Logo overlay** (top-left) + **Earth KML visualization** (same master.kml, ViewSync-synced) |
| lg3 (right) | +36.5° | **Text panel overlay** (right edge) + **Earth KML visualization** (same master.kml, ViewSync-synced) |

### Overlay Files
| Asset | Location | Purpose |
|-------|----------|---------|
| Logo PNG | `http://lg1:81/kml/logo_overlay.png` | Project branding on left screen |
| Text panel PNG | `http://lg1:81/kml/right_panel.png` | Educational content on right screen |
| slave_2.kml | `http://lg1:81/kml/slave_2.kml` | ScreenOverlay for lg2 (logo) |
| slave_3.kml | `http://lg1:81/kml/slave_3.kml` | ScreenOverlay for lg3 (text panel) |

### Text Panel Generator
Use Python Pillow on the Pi to generate the right-screen text panel:
```python
from PIL import Image, ImageDraw, ImageFont
import textwrap

img = Image.new('RGBA', (500, 600), (10, 12, 20, 230))
draw = ImageDraw.Draw(img)
font_t = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
font_b = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 13)

# Draw title, sections, body text with wrapping
draw.text((20, 12), "TITLE", font=font_t, fill=(255, 204, 0))
for item in lines:
    # wrap text with textwrap.fill(item, width=55)
    ...

img.save("/tmp/right_panel.png")
```

### Deployment
```bash
# Deploy overlay images and KMLs
sshpass -p 'lg' scp /tmp/right_panel.png /tmp/logo_overlay.png lg@<LG-IP>:/home/lg/
sshpass -p 'lg' ssh lg@<LG-IP> 'sudo cp /home/lg/right_panel.png /var/www/html/kml/'
sshpass -p 'lg' ssh lg@<LG-IP> 'sudo cp /home/lg/logo_overlay.png /var/www/html/kml/'

# Deploy slave KMLs
sshpass -p 'lg' scp /tmp/slave_2.kml /tmp/slave_3.kml lg@<LG-IP>:/home/lg/
sshpass -p 'lg' ssh lg@<LG-IP> 'sudo cp /home/lg/slave_2.kml /var/www/html/kml/slave_2.kml'
sshpass -p 'lg' ssh lg@<LG-IP> 'sudo cp /home/lg/slave_3.kml /var/www/html/kml/slave_3.kml'
```

### Slave KML Refresh
Both lg2 and lg3 must have `refreshInterval=3` on their Solo KML NetworkLink:
```xml
<Link>
  <href>http://lg1:81/kml/slave_<N>.kml</href>
  <refreshMode>onInterval</refreshMode>
  <refreshInterval>3</refreshInterval>
</Link>
```
This ensures overlay images update within 3 seconds of deployment.

### Benefit
- **KMLs are clean** — just Earth visualizations, no text clutter on the globe
- **Text is readable** — dark panel with high-contrast text, positioned at 98% screen edge
- **Logo is permanent** — always visible in top-left of left screen
- **Panels update independently** — redeploy just the PNG without touching Earth

## Data Quality Overlay
When dual-source is active, the right screen text panel includes:
- ✅ Verified (both sources agree)
- ⚠️ Approximate (single source only)
- 📰 Headlines with topic emojis
