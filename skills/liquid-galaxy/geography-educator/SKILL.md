---
name: geography-educator
description: Generate educational KML visualizations + right-screen text panels for teaching geography concepts on Liquid Galaxy — reference lines (equator, tropics, meridians), tectonic plates, mountain ranges, rivers, volcanoes, world capitals, with live earthquake overlay. All text goes to rightmost screen panel (LG Wiki convention), Earth shows only visuals.
version: 1.1.0
tags: [liquid-galaxy, education, geography, kml, text-panel]
related_skills: [lg-use-cases, lg-kml-patterns, india-news-storyteller]
---

# Geography Educator for Liquid Galaxy

Generate educational geography KMLs with clean Earth visuals and a right-screen text panel.

## Critical Rules

- **No text on Earth globe** — placemarks have `<name></name>` (empty), no descriptions
- **All text content** goes to a right-screen ScreenOverlay PNG (dark bg, bullet points) — **or the news-card balloon** (dark HUD cards via `lg-kml-tours/scripts/news_card_balloon.py`, escaped HTML, auto-opened) for richer text
- **No CDATA** — VM Earth 7.3.3 silently drops placemarks with CDATA descriptions
- **No gx: namespace** — use standard KML `xmlns="http://www.opengis.net/kml/2.2"`
- **Google CDN icons** — `http://maps.google.com/mapfiles/kml/paddle/*.png`
- **Text panel** deployed to `right_panel.png` → loaded by `slave_2.kml` (rightmost = floor(N/2)+1; for N=3 → lg2)

## Concepts Covered

| Concept | KML Feature | Visual |
|---------|------------|--------|
| Latitude | Equator (cyan), Tropics of Cancer/Capricorn (yellow) | Colored LineStrings wrapping the globe |
| Longitude | Prime Meridian (orange line) | LineString at 0° |
| Plate Tectonics | Volcanoes (orange icons), live earthquakes | Point data + USGS feed |
| Mountains | Himalayas, Andes, Rockies, Alps | 3D extruded blue polygons |
| Rivers | Nile, Amazon, Mississippi, Ganges | Blue LineStrings |
| Continents | 7 labeled latitude/longitude markers | Large coordinate labels (text on right panel) |
| Capitals | 10 world capitals | Red pushpins (unnamed on globe) |

## Pre-Built Lessons (right + screen text panel + clean Earth visuals)

### International Date Line
- **Earth:** Red zigzag (actual date line) vs cyan 180° meridian, "Tomorrow" west / "Yesterday" east labels, city dots
- **Right panel:** Date change mechanics, Kiribati/Fiji/Aleutian deviations, explanation text
- **Camera:** Pacific at 15,000km

### India Monsoon Rainfall
- **Earth:** Blue wind arrows (monsoon paths), brown ridge (Western Ghats), orange rain shadow zone, wettest spot pins
- **Right panel:** Monsoon timing, orographic effect, rainfall statistics
- **Camera:** India at 3,000km

### Turkey-Syria Earthquake M7.8
- **Earth:** Red earthquake icon, orange fault line (300km rupture), cyan plate boundary, aftershock dots, city dots
- **Right panel:** Magnitude, casualties, tectonic cause, affected cities
- **Camera:** Turkey at 600km

### Ports of India
- **Earth:** Blue port markers (9 major ports), anchor icons (naval bases), cyan chokepoints
- **Right panel:** Port capacities, trade volumes, strategic significance
- **Camera:** India at 2,500km

## Right-Screen Text Panel Generator

```python
from right_panel import make_panel

lines = ["## TITLE", "", "• Bullet point one", "• Bullet point two"]
make_panel("TITLE", lines, "/tmp/right_panel.png")
# Deploy: scp → sudo cp to lg1:/var/www/html/kml/right_panel.png
```

## Pre-Built KML Generators

See `references/prebuilt-kmls.md` for the full command reference for each of these generators, including camera positions, expected file sizes, and deployment commands.

## Files

- `/home/nara/wm-collector/right_panel.py` — Reusable Pillow generator
- `/tmp/slave_2.kml` — ScreenOverlay KML for rightmost screen (lg2 on 3-screen rig)
- `/tmp/slave_3.kml` — Logo overlay KML for leftmost screen (lg3)
- Pre-built generators: `gen_date_line.py`, `gen_monsoon.py`, `gen_eq_visual.py`
