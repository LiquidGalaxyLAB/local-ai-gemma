---
name: armed-conflicts
description: Map political violence, civil unrest, and warfare globally on Liquid Galaxy using static conflict zone data + BBC news conflict detection. Generates unique dynamic KMLs per zone (front line arrows, siege rings, displacement arrows, faction markers, spreading waves, blockade rings, ethnic polygons, crisis spirals, border lines) with 1-line text labels, right-screen text panel, synced TTS voiceover per zone, and slow camera tour.
version: 2.0.0
tags: [conflict, military, liquid-galaxy, intelligence, tts, camera-tour]
related_skills: [lg-use-cases, lg-data-visualization, news-storyteller]
---

# Armed Conflicts Global Watch

Maps political violence, civil unrest, and warfare across the globe using static known conflict zones + BBC news conflict detection. Each zone gets a **unique KML visual approach** — no recycled styles.

## Unique Visuals Per Zone

| Zone | Visual Style | KML Features |
|------|-------------|--------------|
| 🇺🇦 Ukraine War | Front line arrow | Red 6px arrow path + 3D column + destroyed city dots |
| 🇵🇸 Gaza Strip | Siege rings | 4 concentric circle LineStrings + 25 random damage dots |
| 🇸🇩 Sudan | Displacement arrows | 2 orange flow arrows at 5km altitude showing displacement |
| 🇲🇲 Myanmar | Jungle dots | 20 scattered small red dots across conflict region |
| 🇨🇩 DRC | Faction markers | 4 colored markers (red/orange/yellow/green) per armed group |
| 🇲🇱 Sahel | Spreading waves | 3 fading semi-transparent polygon waves (spread effect) |
| 🇾🇪 Yemen | Blockade ring | Circular LineString blockade perimeter + interior markers |
| 🇪🇹 Ethiopia | Ethnic polygons | 3 overlapping semi-transparent colored polygons |
| 🇭🇹 Haiti | Crisis spiral | 20 dots at varying altitudes (5000-35000m) in spiral pattern |
| 🇮🇳 Kashmir | LoC border | Dotted LineString along Line of Control + buffer zone |

Each zone also has a **big 2.2x scale 1-line text label** (e.g. "⚔ Russia-Ukraine: 300km front line") placed offset from the marker.

## Deployment Sequence

1. **Deploy KML** → 8s wait for NetworkLink refresh
2. **Camera tour** starts — flies to each zone (600km range, 55° tilt)
3. **At each zone:** deploys zone-specific right-screen text panel (name, description, intensity bar, status light)
4. **Voiceover:** TTS plays describing each zone (2-4 lines) — synced with camera arrival
5. **10s dwell** per zone, then flies to next

## TTS Voiceover

Included in all armed-conflicts runs. Format per zone:
> "[Zone name]. [Description of conflict key facts]."

Generated via Hermes TTS tool (Edge TTS provider). Plays alongside the camera tour for a narrated briefing experience.

## Data Sources

| Source | Type | Coverage |
|--------|------|----------|
| Static conflict zones (10) | Config | Ukraine, Gaza, Sudan, Myanmar, DRC, Sahel, Yemen, Ethiopia, Haiti, Kashmir |
| BBC World News RSS | Live (per-run) | Conflict-keyword-filtered articles mapped to countries |

## Files

| File | Purpose |
|------|---------|
| `/home/nara/wm-collector/collectors/armed_conflicts.py` | Main script — KML builder + deploy + camera + voiceover |
| `references/armed-conflicts/conflict-zone-data.md` | Zone coordinates, descriptions, polygon data |

## Manual Run

```bash
cd /home/nara/wm-collector && python3 collectors/armed_conflicts.py
```

## Cron (Auto-Refresh)

```bash
cronjob action=create name=armed-conflicts schedule=6h \
  prompt="cd /home/nara/wm-collector && python3 collectors/armed_conflicts.py" \
  skills=armed-conflicts
```
