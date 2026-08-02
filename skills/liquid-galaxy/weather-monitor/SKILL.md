---
name: weather-monitor
description: Live weather visualization for any city on Liquid Galaxy — 3D temperature column (height = temp), color-coded by heat (red=hot, blue=cool), weather icon at peak, wind direction arrow, right-screen text panel with conditions, and TTS voiceover briefing.
version: 1.0.0
tags: [weather, liquid-galaxy, kml, 3d, tts]
related_skills: [lg-use-cases, lg-data-visualization]
---

# Weather Monitor

Fetches live weather data from wttr.in for any city and generates:

- **3D extruded column** — height = temperature in °C × 1km (23°C = 23km tall)
- **Color-coded** by temperature: red (35+), orange (30+), yellow (25+), green (20+), blue (<20)
- **Weather icon** at column peak (red dot=rain, green=clouds, yellow=sun, blue=default)
- **Temperature label** floating at column height
- **Wind direction arrow** at 500m altitude
- **Right-screen text panel** with conditions, wind, humidity, pressure, visibility, UV
- **TTS voiceover** with full weather briefing

## Usage

```bash
python3 weather_kml.py
```

Change the city by editing `CITY, LAT, LON` at the top of the script.

## Deploy

```bash
python3 /tmp/weather_kml.py
```

## Example

```bash
# Change to any city
CITY="Mumbai" LAT=19.076 LON=72.8777 python3 weather_kml.py
```

## Files

- `/tmp/weather_kml.py` — Weather KML generator script
