---
name: coral-reef-monitor
description: "Monitor global coral bleaching on Liquid Galaxy."
version: 1.0.0
platforms: [linux]
metadata:
  hermes:
    tags: [coral, reefs, bleaching, ocean, climate, marine, kml, liquid-galaxy]
    related_skills: [maritime-awareness, lg-data-visualization, lg-kml-tours, weather-monitor]
---

# Coral Reef Monitoring — Global Bleaching Heatmap

Turns the LG rig into a marine research station. Shows the world's 12 major reef systems, current bleaching alert levels from NOAA satellites, Degree Heating Weeks continuous heatmaps, historical mass bleaching event comparisons from 1998 to present, and cumulative local threat overlays. Coral reefs cover less than 1 percent of the ocean floor but support 25 percent of all marine life. They are the fastest-disappearing ecosystem on Earth. The LG panorama shows this at the scale it actually operates: global, relentless, accelerating.

**5 layers:** (1) Major Reef System Polygons, (2) Bleaching Alert Heatmap, (3) DHW Continuous Heatmap, (4) Historical Bleaching Events & Trend, (5) Local Threat Overlay.

## When to Use

Trigger phrases: "show me coral bleaching on the rig", "what is the state of the Great Barrier Reef", "show me global reef health", "which reefs are bleaching right now", "coral reef watch on the rig", "show me ocean heat stress on reefs", "how bad is coral bleaching this year compared to before", "are the Maldives reefs okay", "show me Caribbean coral health", "which reefs are most at risk right now", "coral reef heatmap", "show me where reefs are dying".

Extract from user input: global vs specific reef/region, current vs historical comparison, specific threat focus.

## Data Sources (all free and open)

| Source | URL | Auth | Purpose |
|--------|-----|------|---------|
| NOAA Coral Reef Watch | `coralreefwatch.noaa.gov` | None (FTP open) | DHW, SST anomalies, bleaching alert levels at 5km resolution |
| NOAA CRW FTP | `ftp.star.nesdis.noaa.gov/pub/sod/mecb/crw/` | None | GeoTIFF/NetCDF updated 2x per week |
| ReefBase | `reefbase.org` | None | Global reef polygon GIS, historical bleaching records |
| GCRMN | `gcrmn.net` | None | Status of Coral Reefs of the World reports |
| AIMS LTMP | `aims.gov.au` | None | Great Barrier Reef coral cover data 1986-present |
| OBIS | `obis.org` | None | Coral species occurrence and biodiversity data |
| WRI Reefs at Risk | `wri.org` | None | Local threat GIS (overfishing, coastal dev, pollution) |
| Copernicus Marine | `marine.copernicus.eu` | Free registration | High-res SST for EU ocean basins |

## NOAA Bleaching Alert Levels (COLOR CODING)

| Alert Level | DHW Range | KML Color | Meaning |
|------------|-----------|-----------|---------|
| No Stress | <4 | Faint teal/blue | Healthy conditions |
| Bleaching Watch | 4-8 | Pale yellow | Thermal stress building |
| Bleaching Warning | 8 | Warm orange | Bleaching likely |
| Alert Level 1 | 8-12 | Vivid red | Widespread bleaching expected |
| Alert Level 2 | >12 | Deep crimson (extruded) | Severe bleaching + significant mortality |

For Alert Level 1+2: add pulsing animated perimeter rings around the reef polygon.

## Major Reef Systems Tracked (12)

| Reef System | Region | Approx Area | Coral Species |
|------------|--------|-------------|---------------|
| Great Barrier Reef | NE Australia | 344,400 km² | 400+ coral |
| Coral Triangle | SE Asia/Pacific | 6M km² | 600+ coral (richest on Earth) |
| Mesoamerican Barrier Reef | Mexico→Honduras | 1,000 km | 65 coral |
| Caribbean Reefs | Florida→Antilles | 26,000 km² | 70+ coral |
| Red Sea Reefs | Egypt→Yemen | 2,000 km | 200+ coral |
| Maldives Atolls | Central Indian Ocean | 8,900 km² | 250+ coral |
| Chagos Archipelago | Central Indian Ocean | 15,000 km² | 220 coral |
| Seychelles | Western Indian Ocean | 1,690 km² | 300+ coral |
| Hawaiian Reefs | Central Pacific | 1,200 km² | 50+ coral |
| New Caledonia | SW Pacific | 24,000 km² | 300+ coral |
| Persian Gulf | Middle East | Scattered | 60+ coral |
| Mozambique Channel | SE Africa | Scattered | 250+ coral |

## Historical Mass Bleaching Events

| Event | Year | Severity | Global Mortality |
|-------|------|----------|-----------------|
| First Global | 1998 | Extreme | ~16% of world's coral killed |
| Second Global | 2010 | Severe | ~10% global coral killed |
| Third Global | 2014-2017 | Unprecedented | ~50% GBR shallow corals died |
| Fourth Global | Current | Ongoing | Monitored in real time |

## Procedure

1. Extract reef system or region from user request. "coral reef watch" → global, all 12 systems. "Great Barrier Reef" → GBR focus. "how has bleaching changed" → Layer 4 historical.
2. Fetch NOAA CRW DHW + bleaching alert data from open FTP.
3. Build KML layers:
   - Layer 1: reef polygon outlines in neutral teal following actual reef geography, floating labels with name/area/species count, GBR shown as actual reef matrix not bounding box
   - Layer 2: bleaching alert fills over reef polygons (teal→yellow→orange→red→crimson), Alert Level 1+2 with pulsing perimeter rings, balloon with DHW value + weeks stressed + record status + plain-language bleaching explanation
   - Layer 3: DHW 5km grid heatmap on blue→green→yellow→orange→red gradient, SST anomaly contour lines as thin white lines showing heat plume structure
   - Layer 4: three historical event polygon layers (1998/2010/2014-17) with severity colors, AIMS GBR coral cover trend 1986-present in balloon, recovery indicator split polygons, gx:Tour chronological time-lapse 1980s→present
   - Layer 5: cumulative threat stacked bars at each reef, polygon outlines colored by cumulative threat score (green→amber→orange→red→dark red)
4. Generate marine research station PNG panel: deep ocean blue `#0a1628`, bioluminescent teal `#00ffaa` border. "CORAL REEF WATCH" header with UTC + global alert status. 12-reef roster with colored dots. DHW thermometer gauge. "Reef in Focus" card with 3-sentence editorial.
5. TTS narration: marine biologist voice. "The Great Barrier Reef is experiencing its fifth mass bleaching event since 2016. Water here has been above threshold for 10 consecutive weeks. Last time it was this severe, more than half the reef's shallow corals died."
6. Deploy via scp → sudo cp → 3s refresh → no relaunch.

## Rightmost Screen — Marine Research Station Panel

Deep ocean blue `#0a1628`, bioluminescent teal `#00ffaa` border:

```
CORAL REEF WATCH  ⏱ 18:45 UTC
GLOBAL STATUS: BLEACHING EVENT ACTIVE
──────────────────────────────────────
■ GBR           🔴 ALERT 2   DHW 14.2
■ Coral Triangle🟠 WARNING   DHW 9.1
■ Maldives      🟡 WATCH      DHW 5.8
■ Caribbean     🟢 NO STRESS  DHW 2.1
■ Red Sea       🟠 WARNING   DHW 8.7
──────────────────────────────────────
DHW GAUGE: 6.8 / 8.0 threshold
████████████░░░░░░░ 85% to bleach point
──────────────────────────────────────
★ REEF IN FOCUS: Great Barrier Reef
5th mass bleaching since 2016. 10 weeks
above threshold. 50% mortality last time.
Recovery depends on cooling within weeks.
```

## The One Rule

Coral reefs cover less than 1 percent of the ocean floor but support 25 percent of all marine species and 500 million people's livelihoods. Never show current bleaching data without historical context. Never show historical data without the temperature trend. Never close the tour without the viewer understanding that what they saw is not a natural cycle but a human-caused acceleration that is still changeable.

## Narration Style (TTS)

Marine biologist voice. NOT "Bleaching alert level 2 at GBR." INSTEAD: "Coral bleaching happens when the ocean gets too warm for too long. The coral expels the algae living in its tissue and turns white. Without those algae, the coral starves. If the heat ends quickly, it can recover. If it does not, the reef dies. Right now, the Great Barrier Reef is in its fifth mass bleaching since 2016."

## Verification

- NOAA CRW FTP: `curl -sI ftp.star.nesdis.noaa.gov/pub/sod/mecb/crw/` responds
- ReefBase: `curl -sI https://reefbase.org` returns 200
- Master KML has 25+ styleUrl references
- lg2 fetches slave_2.kml + PNG every 3s
- GBR coral cover trend data from AIMS loads correctly

## Files

- `scripts/coral_visuals.py` — Coral KML generators
- `scripts/coral_run.py` — CLI entry point  
- `/home/nara/wm-collector/collectors/coral_*.py` — Per-layer collectors

## Free Data Access

| Source | How to Access |
|--------|-------------|
| NOAA CRW | Open FTP — no auth, updated 2x/week |
| ReefBase | Open web — no auth |
| AIMS LTMP | `aims.gov.au` open data |
| OBIS | Open API — no key |
| WRI Reefs at Risk | Open GIS downloads |
| Copernicus Marine | Free registration |
