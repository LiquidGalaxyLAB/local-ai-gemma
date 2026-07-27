---
name: geography-educator
description: Generate educational KMLs for teaching geography concepts on Liquid Galaxy — reference lines (equator, tropics, meridians), mountain ranges, rivers, volcanoes, world capitals, with live earthquake overlay.
version: 1.0.0
---

# Geography Educator

Teach geography concepts on Liquid Galaxy with real-world KML visualizations.

## Concepts Covered
| Concept | KML Feature | Real-World Data |
|---------|------------|----------------|
| Latitude | Equator (cyan), Tropics (yellow) | LineStrings at 0°, 23.5°N/S |
| Longitude | Prime Meridian (orange) | LineString at 0° |
| Plate Tectonics | 10 active volcanoes | Named with 🌋 icons |
| | Live earthquake data (USGS) | 123+ weekly events |
| Mountains | Himalayas, Andes, Rockies, Alps | 3D extruded polygons |
| Rivers | Nile, Amazon, Mississippi, Ganges | Blue LineStrings |
| Continents | 7 labeled continents | Large text labels |
| Capitals | 10 world capitals | 🏙 red pushpins |

## Files
- `/tmp/gen_geo_kml.py` — Generator script (run on Pi)
- Generated KML: ~78 placemarks, 9KB

## Usage
```bash
# Generate and deploy
python3 /tmp/gen_geo_kml.py
sshpass -p 'lg' scp /tmp/geography.kml lg@<LG-IP>:/home/lg/
# sudo cp to Apache
```

## Layer Switcher
Combine with wm-collector layers:
```
# Earthquakes on geography base:
python3 run.py --region world --layers earthquakes --single-source --data-only

# Air traffic:
python3 run.py --region world --layers air-traffic --single-source --data-only
```

## Camera
```
Center: 0°N, 0°E at 20,000km — full Earth view
```
