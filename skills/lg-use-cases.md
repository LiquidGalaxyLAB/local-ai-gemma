---
name: lg-use-cases
description: 20 production-ready Liquid Galaxy use cases covering situational awareness, weather, news, geography, history, natural disasters, maritime, energy, aviation, cyber, supply chain, economic markets, armed conflicts, animal migrations, coral reefs, country instability index, prediction markets, global progress, deforestation, and orbital tracking.
version: 3.0.0
tags: [liquid-galaxy, use-cases, situational-awareness]
related_skills: [lg-ssh-control, news-storyteller, geography-educator, country-instability-index, satellite-orbital-tracker]
---

# LG Use Cases — Complete Reference

20 production-ready use cases for Liquid Galaxy as a multi-screen situational awareness, environmental monitoring, and education platform.

## Quick Reference

| # | Use Case | Status | Tool/Skill |
|---|----------|--------|------------|
| 1 | **LG Command Execution** | ✅ Done | `lg-ssh-control` |
| 2 | **Weather Monitoring** | ⚡ Ready | `wm-collector weather layer` |
| 3 | **News & Geopolitical** | ✅ Done | `news-storyteller` |
| 4 | **Geography Educator** | ✅ Done | `geography-educator` |
| 5 | **History Educator** | 🆕 New | `history-educator` |
| 6 | **Natural Disaster Command** | ⚡ Ready | `wm-collector earthquakes,disasters,weather` |
| 7 | **Maritime Domain Awareness** | ⚡ Ready | `wm-collector ships layer` |
| 8 | **Energy & Infrastructure** | ⚡ Ready | `wm-collector ships + middle-east` |
| 9 | **Live Aviation Watch** | ⚡ Ready | `wm-collector air-traffic` |
| 10 | **Cyber/Undersea Infrastructure** | 📋 Planned | Needs cable data collector |
| 11 | **Supply Chain & Trade** | ⚡ Ready | `wm-collector ships + ports` |
| 12 | **Economic Markets** | 🆕 New | Finnhub + FRED API (needs collector) |
| 13 | **Armed Conflicts** | ✅ Done | `python3 collectors/armed_conflicts.py` — 10 zones, unique KMLs per zone, synced voiceover+camera+text panel |
| 14 | **Animal Migrations** | ✅ Done | `animal-migrations` — 4-layer wildlife tracking, Movebank+IUCN+eBird, TTS nature doc narration |
| 15 | **Coral Reef Monitor** | ✅ Done | `coral-reef-monitor` — 5-layer NOAA bleaching heatmap, 12 reef systems, DHW columns |
| 16 | **Country Instability Index** | 🆕 New | `country-instability-index` — meta-skill, composites 4 skills into 3D column landscape, GDELT+free APIs |
| 17 | **Prediction Markets Geo-Forecast** | 🆕 New | `prediction-markets-geo` — Polymarket probability rings on globe, amber uncertainty pulses |
| 18 | **Global Progress Dashboard** | 🆕 New | `global-progress-dashboard` — positive trends counterweight, warm sunrise visuals, Our World in Data |
| 19 | **Deforestation Monitor** | 🆕 New | `deforestation-monitor` — 4-layer forest watch, NASA FIRMS+GFW+RESOLVE, biodiversity hotspots |
| 20 | **Satellite Orbital Tracker** | 🆕 New | `satellite-orbital-tracker` — 27,000 objects at actual altitude, CelesTrak TLE+SGP4, camera flies through orbital shells |

## Standard Deploy Sequence

Every use case follows this sequence (see `references/lg-ssh-control/kml-deploy-sequence.md`):
1. **Generate KML** — visual-only, no text labels, no CDATA
2. **Deploy to Apache** — overwrite master.kml
3. **Wait 6-8s** — NetworkLink 3s refresh cycle
4. **Deploy right-screen panel** — PNG to right_panel.png
5. **Start TTS + camera together** — voiceover in background, flytoview in foreground

### Per-Location Tour Timing
When visiting multiple locations in sequence:
- **Fly to location** via flytoview, wait 2s for camera to settle
- **Update right-screen text panel** — SCP new zone-specific PNG
- **TTS + dwell** — 10-12s per location for voiceover + reading
- **Next location** — repeat

### 1-Line Text Labels on Earth
Each location gets one 1-line label (max 80 chars) placed 1.8° lon + 0.8° lat offset from marker. Scale 2.2, no icon. This makes labels readable during flythrough without cluttering the view:

```xml
<Style id="txt"><IconStyle><scale>0.0</scale></IconStyle>
  <LabelStyle><color>ffffffff</color><scale>2.2</scale></LabelStyle></Style>
<Placemark><name>One line label</name>
  <styleUrl>#txt</styleUrl>
  <Point><coordinates>lon+1.8,lat+0.8,0</coordinates></Point>
</Placemark>
```

### Smart Visual Types

All use cases use the shared visual type system:
- Flood/rain → 🔵 blue 3D extruded blocks (50km)
- Protest/reform → 🟠 orange semi-transparent zones
- Battle/conflict → 🔴 red 3D columns + concentric glow rings
- Sport/gold → 🟡 gold paddle icons
- Military → 🟢 green markers
- Fire/disaster → 🔴 red-orange zones
- Default → 🔵 blue circle icons

---

## 1. LG Command Execution
SSH-based control: relaunch, reboot, poweroff Earth on all frames. See `lg-ssh-control` skill.

```bash
# Relaunch
sshpass -p 'lg' ssh lg@LG-IP '/home/lg/bin/lg-relaunch-direct'

# Reboot
sshpass -p 'lg' ssh lg@LG-IP '/home/lg/bin/lg-reboot-direct'

# Poweroff
sshpass -p 'lg' ssh lg@LG-IP '/home/lg/bin/lg-poweroff-direct'
```

---

## 2. Weather Monitoring
Live weather data from NOAA NWS + wttr.in visualized on LG.

| Layer | Source | Type |
|-------|--------|------|
| ⛈ Weather alerts | NOAA NWS API | Live (5 min) |
| 🌡 Global conditions | wttr.in / WMO codes | Live (15 min) |

```bash
cd /home/nara/wm-collector && python3 run.py --region world --layers weather --single-source
```

---

## 3. News & Geopolitical Visualization
Fetches RSS from multiple sources, extracts locations, deploys 3D context-aware KMLs + right-screen text panel + TTS. See `news-storyteller` skill.

```bash
cd /home/nara/wm-collector && python3 news_storyteller.py --query="world"
```

---

## 4. Geography Educator
Teaches geography concepts with real-world KMLs. See `geography-educator` skill.

| Lesson | Content |
|--------|---------|
| International Date Line | Red zigzag line vs cyan 180° meridian |
| India Monsoon | Wind arrows, rain shadow, wettest/driest spots |
| Turkey Earthquake | Fault lines, epicenter, plate boundaries |
| Ports of India | 9 major ports with capacities |

---

## 5. History Educator
Shows how historical events unfolded — wars, battles, invasions — using animated KML tours with timeline placemarks, troop movement arrows, and TTS narration. See `history-educator` skill.

*Planned topics: World War II fronts, Cold War flashpoints, Indian independence movement, Silk Road routes.*

---

## 6. Natural Disaster Command Center
Earthquakes, wildfires, weather alerts — auto-fly to latest M5+ or large wildfire.

```bash
cd /home/nara/wm-collector && python3 run.py --region world --layers earthquakes,natural-events,weather --single-source
```

**Auto-fly:** Poll USGS every 30 min; if new M5+ detected, deploy KML at 500km range.

---

## 7. Maritime Domain Awareness
Ports, naval bases, chokepoints (Hormuz, Malacca, Suez, Bab-el-Mandeb) across 3 screens.

```bash
cd /home/nara/wm-collector && python3 run.py --region world --layers ships --single-source
```

**Camera:** One chokepoint per screen:
- lg1: Hormuz (26.5°N, 56°E, 500km)
- lg2: Malacca (5°N, 95°E, 500km)
- lg3: Bab-el-Mandeb (12.5°N, 43.5°E, 500km)

---

## 8. Energy & Infrastructure Monitoring
Gulf oil terminals, tanker routes, pipeline corridors.

```bash
cd /home/nara/wm-collector && python3 run.py --region middle-east --layers ships --single-source
```

**Key points:** Ras Tanura (Saudi Aramco), Bandar Abbas (Iran), Jebel Ali (UAE), Strait of Hormuz.

---

## 9. Live Aviation Watch
100 aircraft with heading-rotated icons at actual altitude.

```bash
cd /home/nara/wm-collector && python3 run.py --region world --layers air-traffic,airports --single-source
```

**Corridors:** Ukraine frontier (50°N, 30°E), NATO frontiers, South China Sea (12°N, 112°E).

---

## 10. Cyber / Undersea Infrastructure Map
Undersea cable routes, internet outages, GPS jamming. *Needs cable route data collector.*

```bash
# Placeholder — deploy news overlay only
cd /home/nara/wm-collector && python3 run.py --region world --layers news --single-source
```

---

## 11. Supply Chain & Trade Flow
Trade routes, chokepoint status, commodity ports with capacity data.

```bash
cd /home/nara/wm-collector && python3 run.py --region world --layers ships --single-source
```

**Trade lane sequence:** Shanghai → Singapore → Malacca → Colombo → Hormuz → Suez → Rotterdam

---

## 12. Economic Markets
Monitors financial trends via Finnhub and FRED APIs — stock indices, economic indicators mapped to regions. *Needs collector (see economic-markets skill).*

| Indicator | Source |
|-----------|--------|
| S&P 500, FTSE, Nikkei, Sensex | Finnhub |
| GDP, inflation, unemployment | FRED (Federal Reserve) |
| Trade volumes by region | World Bank API |

---

## 13. Armed Conflicts

Maps political violence, civil unrest, warfare globally. Uses **static config of 10 active conflict zones** (Ukraine, Gaza, Sudan, Myanmar, DRC, Sahel, Yemen, Ethiopia, Haiti, Kashmir) + BBC World News RSS filtered by conflict keywords.

| Data | Source | Coverage |
|------|--------|----------|
| Conflict zones | Static config (10 zones with poly data) | Current hotspots |
| Conflict-related news | BBC World RSS (keyword-filtered) | Live (30 min) |
| (Future) ACLED/UCDP | Free API | Daily |

### Unique Visuals Per Zone
Each zone gets a **distinct KML approach** — never recycled styles:
- **Ukraine** → Red front line arrow with 3D destroyed city columns
- **Gaza** → 4 concentric siege rings with 25 dense damage dots
- **Sudan** → Orange displacement flow arrows (5km altitude)
- **Myanmar** → 20 scattered jungle conflict dots
- **DRC** → 4 colored faction markers (M23, Wazalendo, etc.)
- **Sahel** → 3 spreading wave polygons (insurgency diffusion)
- **Yemen** → Blockade ring (Houthi containment)
- **Ethiopia** → 3 overlapping ethnic region polygons
- **Haiti** → 20 downward spiral dots at varying altitude (crisis depth)
- **Kashmir** → LoC dotted border line

### Synced Sequence
```
Deploy KML → wait 8s (NetworkLink refresh) → 
  for each zone:
    fly to zone (600km, 55 tilt)
    update right-screen text panel (zone name, desc, intensity bar, lat/lon)
    play TTS voiceover (2-4 lines explaining the zone)
    dwell 10-12s
  → final wide overview
```

### Deploy
```bash
cd /home/nara/wm-collector && python3 collectors/armed_conflicts.py
```

### Files
- `/home/nara/wm-collector/collectors/armed_conflicts.py` — Main collector

---

## 14. Animal Migrations
Track wildlife migrations with live data from Movebank, IUCN, eBird, and OBIS. 4 layers: migration routes, species cards, historical comparison, global overview. Camera moves like a nature documentary. See `animal-migrations` skill.

```bash
cd /home/nara/wm-collector && python3 run.py --region world --layers migrations --single-source
```

---

## 15. Coral Reef Monitor
5-layer NOAA bleaching heatmap at 5km resolution. 12 major reef systems tracked with Degree Heating Weeks as extruded ocean heat columns. Historical mass bleaching comparison from 1998-present. See `coral-reef-monitor` skill.

```bash
cd /home/nara/wm-collector && python3 run.py --region world --layers coral --single-source
```

---

## 16. Country Instability Index (Meta-Skill)
Composite geopolitical stress score for 30+ countries rendered as a physical landscape of extruded 3D columns. Ties armed-conflicts, economic-markets, cyber-infrastructure, and natural-disaster data into one cross-stream correlation view. Camera slow-laps the columns so unstable regions visibly tower. GDELT Doc API for tone/volume signal (free, no key). See `country-instability-index` skill.

```bash
cd /home/nara/wm-collector && python3 collectors/cii_composite.py
```

---

## 17. Prediction Markets Geo-Forecast
Polymarket prediction probabilities rendered as pulsing geo-forecast rings at country centroids. Amber rings = high uncertainty (probability near 50%), white rings = consensus. Shows what the world's aggregate money believes will happen next. Polymarket CLOB API — free, no key. See `prediction-markets-geo` skill.

```bash
cd /home/nara/wm-collector && python3 collectors/prediction_markets.py
```

---

## 18. Global Progress Dashboard
The counterweight to every crisis skill — maps positive global trends (extreme poverty falling, child mortality declining, renewables rising, life expectancy gains, disease eradication) using warm sunrise-gradient visuals. Designed for classrooms and public demos. Our World in Data + WHO GHO — free, no keys. See `global-progress-dashboard` skill.

```bash
cd /home/nara/wm-collector && python3 collectors/global_progress.py
```

---

## 19. Deforestation & Biodiversity Monitor
4-layer forest watch: live fire alerts (NASA FIRMS), tree cover loss by country choropleth (GFW), biodiversity hotspot polygons (RESOLVE + CI), protected area green borders (WDPA). Camera flies deforestation fronts — Amazon arc, Congo Basin, Indonesia, West Africa. All sources free or free-token. See `deforestation-monitor` skill.

```bash
cd /home/nara/wm-collector && python3 collectors/deforestation_monitor.py
```

---

## 20. Satellite Orbital Tracker
Orbital objects at actual altitude on a multi-screen 3D globe — the killer app no browser dashboard can touch. ISS at 423 km, Tiangong at 392 km, Starlink at 550 km, GPS ring at 20,200 km. 27,000+ objects from CelesTrak TLE (free, no key) + SGP4 propagation. Camera rises through orbital shells. Missions-control right-screen panel in cyan-on-black. See `satellite-orbital-tracker` skill.

```bash
cd /home/nara/wm-collector && python3 collectors/orbital_tracker.py
```

## Standard Screen Layout

| Screen | Position | Content |
|--------|----------|---------|
| lg1 (center) | 0° | Earth KML visualization — visual-only |
| lg2 (left) | -36.5° | Logo overlay (top-left) + Earth KML |
| lg3 (right) | +36.5° | Text panel overlay (right edge) + Earth KML |

**Right-screen formula:** screen N (LG Wiki) — all text goes here.
**Left-screen formula:** floor(N/2)+2 — logo goes here.
