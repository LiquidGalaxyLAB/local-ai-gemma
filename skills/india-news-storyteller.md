---
name: india-news-storyteller
description: Autonomous India news KML tour generator — fetches BBC India RSS, extracts locations, generates gx-free KML placemarks, deploys to LG, positions camera, prints narration.
version: 2.0.0
tags: [india, news, kml, liquid-galaxy]
---

# India News Storyteller

Autonomous news-driven KML visualization for Liquid Galaxy on VirtualBox VM rigs (Earth 7.3.3).

## ⚠️ Critical VM Limitations

| Feature | Works? | Why |
|---------|--------|-----|
| `xmlns:gx` anywhere in KML | ❌ | Earth 7.3.3 silently rejects the **entire** KML |
| `<gx:Tour>` / `<gx:FlyTo>` | ❌ | Requires gx namespace — KML won't render at all |
| `playtour=` via `/tmp/query.txt` | ❌ | Only works for tours pre-loaded in Places panel |
| Styled `<Placemark>` with `<Point>` | ✅ | Basic KML renders reliably |
| `<LookAt>` in `<Document>` + flyToView=1 | ✅ | Camera auto-positions on 3s refresh |
| `flytoview=` via `/tmp/query.txt` | ✅ | Most reliable camera control (rm -f before write) |

**Rule:** Never add `xmlns:gx` to any KML on this rig. Use plain `<LookAt>` and `flytoview=` via query.txt.

## Pipeline

```
Cron (30 min) -> fetch BBC India RSS -> CDATA-strip -> pick top story
  -> find_locations(title + desc) -> expand if < 2 found
  -> generate gx-free KML (styled pins + Document LookAt)
  -> scp to lg1 -> sudo cp to Apache
  -> flytoview= via /tmp/query.txt
  -> print narration
```

## Location Matching

`india_locations.py` has dict of `{keyword: (lat, lon, display_name)}`. Sort by longest key first. Dedup by proximity (< 2 degrees apart). Max 8 locations.

**Must include `"india"` as fallback key** — many BBC descriptions only say "India."

## Files
- `/home/nara/wm-collector/news_storyteller.py` — Main script (LG_IP=192.168.1.12)
- `/home/nara/wm-collector/india_locations.py` — 70+ Indian locations

## Manual Run
```
cd /home/nara/wm-collector && python3 news_storyteller.py
```

## Known Issues
- BBC RSS uses CDATA — strip before item extraction
- Short BBC descriptions (1 sentence) often lack city names — falls back to India default
- Rate limit: BBC RSS 429s if fetched > once per 15 min
- Camera fighting: flyToView=1 in myplaces overrides flytoview commands — set to 0 during active camera sequences
- **Stale query.txt after deploy**: If the script was stopped mid-run, `/tmp/query.txt` on lg1 may contain a stale flytoview. Always `rm -f /tmp/query.txt` before writing fresh commands.
- **gx:Tour doesn't work via NetworkLink**: `playtour=` only finds tours in Places panel. NetworkLink-loaded tours render visually but never register. Use flytoview via query.txt instead.