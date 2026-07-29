---
name: natural-disaster
description: Natural Disaster Command Center — auto-fly to latest M5+ earthquakes, wildfires, weather alerts on Liquid Galaxy. Uses USGS, NASA EONET, and NOAA APIs with 3D extruded columns colored by magnitude/severity.
tags: [liquid-galaxy, disaster, earthquake, wildfire, weather]
---

# Natural Disaster Command Center

Monitors earthquakes, wildfires, and natural events globally. Auto-fly to the latest M5+ earthquake or large wildfire.

## Data Sources

| Layer | Source | Type |
|-------|--------|------|
| Earthquakes | USGS GeoJSON (M4.5+, week) | Live (5-10 min) |
| Natural Events | NASA EONET | Live (15-30 min) |
| Weather Alerts | NOAA NWS API | Live (5 min) |

## Deploy

```bash
cd /home/nara/wm-collector && python3 run.py --region world --layers earthquakes,natural-events,weather --single-source
```

## What You See

- 🔴 Red 3D columns for M5+ quakes (height = magnitude × 20km)
- 🟠 Orange markers for wildfires
- 🔵 Blue markers for weather alerts
- Auto-fly to latest event at 500km range
- Right-screen panel with event details + TTS briefing
