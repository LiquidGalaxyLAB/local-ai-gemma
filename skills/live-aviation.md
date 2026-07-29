---
name: live-aviation
description: Live Aviation Watch — 100 aircraft with heading-rotated icons at actual altitude. Uses OpenSky Network ADS-B data. Right-screen panel with airports + TTS.
tags: [liquid-galaxy, aviation, flights, air-traffic]
---

# Live Aviation Watch

## Skill Name
Live Aviation Monitor

## Sample Inputs (what user says)
- "Show flights over Germany"
- "Air traffic over Europe right now"
- "What planes are flying over the Middle East?"
- "Show me live aviation near Ukraine"

## Prompt (inputs used by the skill)
- User query (region) → `--region` flag (europe / middle-east / world)
- wm-collector pipeline: OpenSky Network API
- 100 aircraft icons rotated by heading direction
- Aircraft displayed at actual altitude (`relativeToGround`)
- 35 major airports as reference points (static config)
- Camera centered on region at 800km range
- Right-screen panel with key airports + corridors + TTS

## What It Does
1. Fetches live ADS-B transponder data from OpenSky Network (100 aircraft)
2. Generates KML with heading-rotated plane icons at actual flight altitude
3. Adds major airport markers as reference points
4. Deploys to master.kml + right-screen airport info panel
5. Flies camera to region center (800km range, 55° tilt)
6. Generates TTS with aircraft count + key hubs + corridors

## Expected Output
```
🌍 WM-LG Monitor — Europe
   Layers: air-traffic
📡 Air Traffic... 100
✅ Deployed — 100 aircraft over Germany
Camera: 51N, 10E at 800km
Right screen: Frankfurt, Munich, Berlin hubs + TTS
```

## Deploy
```bash
# Europe
cd /home/nara/wm-collector && python3 run.py --region europe --layers air-traffic --single-source --data-only

# Middle East
cd /home/nara/wm-collector && python3 run.py --region middle-east --layers air-traffic --single-source --data-only

# World
cd /home/nara/wm-collector && python3 run.py --region world --layers air-traffic --single-source --data-only
```

## Data Sources
| Layer | Source | Type |
|-------|--------|------|
| Air Traffic | OpenSky Network | Live (5 min refresh) |
| Airports | Static config (35 major) | Static |
