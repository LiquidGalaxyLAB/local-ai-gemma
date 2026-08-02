# Armed Conflicts Collector

Live at `/home/nara/wm-collector/collectors/armed_conflicts.py`

## Data Sources

10 static conflict zones (no API key needed):
- Ukraine War, Gaza Conflict, Sudan Civil War, Myanmar Conflict, DRC Conflict
- Sahel Insurgency, Yemen War, Ethiopia Conflict, Haiti Crisis, Kashmir Dispute

Plus BBC World News RSS filtered for conflict keywords (war, attack, troops, etc.).

## Visual Layers Per Zone

| Layer | Element | Description |
|-------|---------|-------------|
| 3D column | Extruded square polygon | Height = intensity × 20km (20-100km) |
| Region polygon | Semi-transparent zone | Red for battle, orange for protest |
| Glow rings | 3x concentric volcano icons | Scale 3.0 to 1.2, alpha 40 to 70 to ff |

## Camera Tour

15,000km global overview to 10 hotspots at 800km, 55 tilt, 8s dwell each, back to global overview. Total tour time approximately 90 seconds.

## Deploy

cd /home/nara/wm-collector && python3 collectors/armed_conflicts.py

## Output

KML deployed to master.kml (88 features), right-screen panel populated, TTS narration, camera auto-flythrough after 8s settle time.
