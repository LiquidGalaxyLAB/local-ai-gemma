---
name: armed-conflicts
description: Armed Conflicts Global Watch — 10 conflict zones with unique dynamic KMLs per zone (front arrows, siege rings, displacement arrows, faction markers, wave spreads, blockade rings, ethnic polygons, crisis spirals, border lines). Right-screen text panel + synced TTS voiceover + slow camera tour (12s dwell).
tags: [liquid-galaxy, conflict, military, intelligence, tts, camera-tour]
---

# Armed Conflicts Global Watch

## Skill Name
Armed Conflicts Monitor

## Sample Inputs (what user says)
- "Show global conflicts"
- "Where are active wars right now?"
- "Armed conflicts briefing"
- "Show me conflict zones worldwide"

## Prompt (inputs used by the skill)
- Static conflict zone database (10 zones: Ukraine, Gaza, Sudan, Myanmar, DRC, Sahel, Yemen, Ethiopia, Haiti, Kashmir)
- BBC World News RSS — conflict-keyword-filtered articles
- Unique KML visual per zone (not recycled styles):
  - Ukraine: red front line arrow + 3D column + destroyed city dots
  - Gaza: 4 concentric siege rings + 25 random damage dots
  - Sudan: 2 orange displacement flow arrows at 5km altitude
  - Myanmar: 20 scattered jungle conflict dots
  - DRC: 4 colored faction markers (red/orange/yellow/green)
  - Sahel: 3 fading semi-transparent wave polygons
  - Yemen: circular blockade LineString perimeter
  - Ethiopia: 3 overlapping ethnic polygons
  - Haiti: 20 crisis dots at varying altitudes (5000-35000m)
  - Kashmir: LoC dotted border LineString
- 1-line text labels (2.2x scale) offset from each zone
- Camera tour: 10 zones at 600km range, 55° tilt, 12s dwell each
- Right-screen panel per zone: name, description, intensity bar, status light
- TTS: 2-4 lines per zone, synced with camera arrival

## What It Does
1. Loads 10 static conflict zones + fetches BBC conflict news
2. Generates unique dynamic KML visuals for EACH zone (no recycled styles)
3. Adds big 1-line text labels (2.2x scale) for each zone
4. Deploys KML to master.kml + initial right-screen text panel
5. Starts slow camera tour: global overview → 10 hotspots (12s dwell each)
6. At each zone: updates right-screen panel → dwells for voiceover
7. Ends with wide global overview showing all active zones
8. Generates TTS: "Ukraine War. Europe's deadliest conflict since 1945..."

## Expected Output
```
=== Dynamic Armed Conflicts ===
  188 features, 10 zones
  KML deployed. Starting camera tour...
    Ukraine War — red front line arrow + 3D column
    Gaza Strip — 4 siege rings + 25 damage dots
    Sudan — displacement flow arrows
    ...
✅ Tour complete. 10 zones visited with narration.
```

## Deploy
```bash
cd /home/nara/wm-collector && python3 collectors/armed_conflicts.py
```

## Data Sources
| Source | Type | Coverage |
|--------|------|----------|
| Static conflict zones (10) | Config | Ukraine, Gaza, Sudan, Myanmar, DRC, Sahel, Yemen, Ethiopia, Haiti, Kashmir |
| BBC World News RSS | Live (per-run) | Conflict-keyword-filtered articles |
