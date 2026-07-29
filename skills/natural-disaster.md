---
name: natural-disaster
description: Natural Disaster Command Center — auto-fly to latest M5+ earthquakes, wildfires, weather alerts. Uses USGS, NASA EONET, and NOAA APIs with colored 3D columns. Right-screen panel + TTS.
tags: [liquid-galaxy, disaster, earthquake, wildfire, weather]
---

# Natural Disaster Command Center

## Skill Name
Natural Disaster Monitor

## Sample Inputs (what user says)
- "Show earthquakes in Japan"
- "Any wildfires happening right now?"
- "Natural disasters in the Pacific Ring of Fire"
- "What's shaking in the world today?"

## Prompt (inputs used by the skill)
- User query (region/topic) → `--region` flag
- wm-collector pipeline: USGS GeoJSON + NASA EONET + NOAA NWS
- KML generator with 3D extruded columns (height = magnitude × 20km)
- Color coding: red = M5+, orange = M4+, yellow = M3+
- Auto-fly to latest M5+ epicenter via /tmp/query.txt flytoview
- Right-screen text panel + TTS voiceover briefing

## What It Does
1. Fetches live earthquake data (USGS, M4.5+, past week)
2. Fetches natural events (NASA EONET — wildfires, volcanoes, storms)
3. Fetches weather alerts (NOAA NWS)
4. Generates KML with 3D colored columns for each quake/event
5. Deploys to master.klm + right-screen panel
6. Auto-flies camera to the latest M5+ event at 500km range
7. Generates TTS narration: "M5.2 earthquake detected near Tokyo..."

## Expected Output
```
🌍 WM-LG Monitor — World
   Layers: earthquakes, natural-events, weather
📡 Earthquakes... 12  |  Natural Events... 3  |  Weather... 2
✅ 17 features deployed
Auto-fly to: M5.2 near Tokyo (35.7N, 139.7E)
Right screen: event details + TTS briefing
```

## Deploy
```bash
cd /home/nara/wm-collector && python3 run.py --region world --layers earthquakes,natural-events,weather --single-source
```

## Data Sources
| Layer | Source | Type |
|-------|--------|------|
| Earthquakes | USGS GeoJSON (M4.5+, week) | Live (5-10 min) |
| Natural Events | NASA EONET | Live (15-30 min) |
| Weather Alerts | NOAA NWS API | Live (5 min) |
