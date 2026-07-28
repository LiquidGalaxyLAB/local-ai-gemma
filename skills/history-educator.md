---
name: history-educator
description: Create historical event visualizations on Liquid Galaxy — battle maps, invasion routes, war fronts, timeline tours with animated KML paths, troop movement arrows, timeline placemarks, and TTS narration.
tags: [history, kml, liquid-galaxy, education, timeline]
related_skills: [lg-use-cases, lg-kml-patterns, geography-educator]
---

# History Educator

Shows how historical events unfolded on Liquid Galaxy. Each topic is a self-contained KML package with:
- Animated troop/path movements via sequential flytoview
- Timeline placemarks (color-coded by year/month)
- Battle front lines as extruded polygons
- Invasion routes as arrowed LineStrings
- Right-screen text panel with key facts + timeline
- TTS narration of the event

## Planned Topics

| Topic | Era | Visual Elements |
|-------|-----|----------------|
| World War II — European Front | 1939-1945 | Axis/Allied front lines, D-Day arrows, Battle of Berlin |
| World War II — Pacific Theater | 1941-1945 | Island hopping arrows, naval battle markers |
| Cold War Flashpoints | 1947-1991 | Berlin Airlift, Cuban Missile Crisis, Vietnam War |
| Indian Independence Movement | 1857-1947 | Key protests, Dandi March route, partition line |
| Silk Road Trade Routes | 200 BC - 1400 AD | Route paths, oasis cities, timeline of empires |
| Napoleonic Wars | 1803-1815 | Invasion of Russia route, Battle of Waterloo |
| Mongol Empire Expansion | 1206-1294 | Conquest arrows, empire extent polygons |

## KML Pattern

```xml
<!-- Arrow path for troop movements -->
<Placemark>
  <name></name>
  <styleUrl>#arrow_path</styleUrl>
  <LineString>
    <extrude>1</extrude>
    <altitudeMode>relativeToGround</altitudeMode>
    <coordinates>
      lon1,lat1,5000 lon2,lat2,5000 ... lonN,latN,5000
    </coordinates>
  </LineString>
</Placemark>

<!-- Timeline placemark -->
<Placemark>
  <name></name>
  <styleUrl>#event_1944</styleUrl>
  <Point><coordinates>lon,lat,0</coordinates></Point>
</Placemark>
```

## Camera Pattern

Fly along the timeline: sequential flytoview from earliest event to latest, with 6s dwell per stop. Start at wide overview, zoom in on each key location.

## Deployment

```bash
# Generate and deploy a historical topic
cd /home/nara/wm-collector && python3 history_educator.py --topic=ww2-europe
```

*Note: The history_educator.py script needs to be built. Currently these are manual KML creations demonstrated per-user request (e.g. Turkey Earthquake educator).*
