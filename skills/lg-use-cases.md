---
name: lg-use-cases
description: Liquid Galaxy User Guide — getting started, 6 approved use cases (LG commands, weather, news, geography, natural disasters, live aviation), example prompts, screen layout, and TTS voiceover reference.
version: 3.0.0
tags: [liquid-galaxy, user-guide, use-cases, getting-started]
---

# Liquid Galaxy User Guide & Use Cases

> Just describe what you want. Nara builds it.

## Getting Started

When you first connect, Nara asks for 5 things once (IP, port, user, pass, screen count) and saves them. After that, auto-connects every session.

## 6 Approved Use Cases

| # | Use Case | What You Say | What Happens |
|---|----------|-------------|--------------|
| 1 | **LG Commands** | "Connect to LG", "Relaunch Earth", "Reboot the rig" | SSH into lg1, execute control commands (relaunch/reboot/poweroff) |
| 2 | **Weather Monitor** | "Show Pune weather", "What's the weather in Mumbai?" | Fetches live data, generates 3D temperature column (height=°C), wind arrow, right panel + TTS |
| 3 | **News & Geopolitical** | "Show today's news", "What's happening in Ukraine?" | Fetches BBC RSS, extracts locations, generates 3D context-aware KMLs, right panel + camera tour + TTS |
| 4 | **Geography Educator** | "Teach me about the Date Line", "Show India monsoon" | Generates educational KML with reference lines, 3D zones, right panel + voiceover |
| 5 | **Natural Disasters** | "Show earthquakes in Japan", "Any wildfires?" | Fetches USGS + NASA EONET, deploys quake columns + fire markers, auto-fly to latest M5+ |
| 6 | **Live Aviation** | "Show flights over Germany", "Air traffic over Europe" | Fetches OpenSky Network, 100 heading-rotated aircraft at altitude, right panel + TTS |

## Screen Layout (3 Screens)

| Screen | Content |
|--------|---------|
| lg1 (center) | Earth KML visualization — visual-only, no text |
| lg2 (left) | Logo overlay (top-left) + Earth KML |
| lg3 (right) | Text panel overlay (right edge) + Earth KML |

**Right-screen formula:** screen N (LG Wiki). All text goes here — never on the globe.

## TTS Voiceover

Most skills generate TTS narration:
- **Weather:** "Pune: 23C, patchy rain. Humidity 89%..."
- **News:** "Top stories: Assam floods, protests in Delhi..."
- **Geography:** "The International Date Line runs along the 180th meridian..."
- **Disasters:** "M5.2 earthquake detected near Tokyo..."
- **Aviation:** "100 aircraft over Germany. Frankfurt and Munich hubs active..."

## Example Prompts

```
"Connect to the LG"
"Show me Pune weather with voiceover"
"What's happening in the news today?"
"Teach me about the International Date Line"
"Show earthquakes in Japan"
"Show flights over Europe"
```

## Under Development

| Use Case | Status |
|----------|--------|
| History Educator (WWII, Cold War) | 📋 Planned |
| Economic Markets (Finnhub + FRED) | 📋 Planned |
| Armed Conflicts (ACLED data) | 📋 Planned |
| Maritime Domain Awareness | 📋 Planned |
| Supply Chain & Trade | 📋 Planned |
| Cyber Infrastructure | 📋 Planned |
