---
name: news-storyteller
description: Autonomous news KML storyteller — fetches from multiple RSS feeds based on user query, extracts locations, generates 3D dynamic KMLs by content type (flood=blue polygon, protest=orange zone, sport=gold), deploys text panel to rightmost screen, animates camera between stories, and generates TTS voiceover.
version: 3.0.0
tags: [news, kml, liquid-galaxy, text-panel, tts, 3d-polygons, camera-animation]
related_skills: [lg-use-cases, lg-kml-patterns]
---

# News Storyteller

Autonomous multi-article news visualization for Liquid Galaxy. Fetches from **multiple RSS feeds**, picks the relevant one based on user query, extracts locations from articles, deploys **3D context-aware visuals on Earth** (extruded polygons colored by content type) and a **numbered text panel on the rightmost screen** (LG Wiki formula: N), plus TTS voiceover and auto-camera flythrough.

**Not constrained to any region.** The user specifies what they want to see, and the system picks the right source.

## Usage

```bash
# World news (default)
python3 news_storyteller.py

# India news
python3 news_storyteller.py --source india

# User query — picks relevant source
python3 news_storyteller.py --query "ukraine war"
python3 news_storyteller.py --query "europe elections"
python3 news_storyteller.py --query "climate change"
```

## Available News Sources

| Source | Feed URL | When Used |
|--------|----------|-----------|
| BBC World | `feeds.bbci.co.uk/news/world/rss.xml` | Default, or generic queries |
| BBC India | `feeds.bbci.co.uk/news/world/asia/india/rss.xml` | Query contains "india", "delhi", etc. |
| BBC UK | `feeds.bbci.co.uk/news/uk/rss.xml` | Query contains "uk", "britain", "london" |
| BBC Business | `feeds.bbci.co.uk/news/business/rss.xml` | Query contains "business", "economy", "trade" |
| BBC Technology | `feeds.bbci.co.uk/news/technology/rss.xml` | Query contains "tech", "cyber", "ai" |
| BBC Science | `feeds.bbci.co.uk/news/science_and_environment/rss.xml` | Query contains "climate", "science", "space" |
| (Extensible) | Add any RSS feed URL | Custom source |

## How Feed Selection Works

When a user provides a query, the system:
1. Scans the query for keywords (`india` → BBC India, `tech` → BBC Tech, etc.)
2. If no keyword matches → uses BBC World
3. Falls back to BBC World + BBC India combined if a feed returns < 2 articles

## Pipeline

```
User query -> pick relevant RSS feed -> fetch top 10 articles -> 
  for each article:
    find_locations(title + description)
    detect_visual_type(title + description) -> flood/protest/sport/etc
    -> 3D extruded polygon if region has boundary data
    -> color-coded icon if city/point
  -> merge all features into single KML (no CDATA, no text on globe)
  -> generate right-screen text panel PNG (Pillow, 500x620, dark bg)
  -> deploy KML to master.kml + PNG to right_panel.png
  -> flytoview overview -> auto-fly to top 3 story locations
  -> TTS voiceover of top headlines
```

## Visual Types

| Keyword | Style | ABGR Fill | Visual |
|---------|-------|-----------|--------|
| flood, rain | flood | `7fff0000` | 🔵 Blue 3D extruded block (50km) |
| cyclone, storm | storm | `7f00aaff` | 🟤 Orange-brown zone |
| protest, education, reform | protest | `7f0088ff` | 🟠 Orange zone |
| sport, gold, boxer | sport | `7f00ccff` | 🟡 Gold icons |
| military, army | military | `7f00ff00` | 🟢 Green markers |
| earthquake | quake | `7f0000ff` | 🔴 Red zone |
| fire | fire | `7f0044ff` | 🔴 Red-orange |
| crime | crime | `7f0000ff` | 🔴 Red markers |

## World Location Database

80+ world countries, capitals, and regions with coordinates. 10+ region polygons with 3D boundary data. Extensible — add any location or polygon to `LOCATIONS` / `REGION_POLYGONS` dicts.

## Region Polygons (3D Extruded)

| Region | Used For |
|--------|----------|
| Assam (NE India) | Flood/rain stories |
| Delhi NCR | Protest/education |
| Gaza Strip | Conflict |
| Ukraine | War/conflict |
| Israel | Middle East stories |
| Kashmir | Border/conflict |
| Mumbai | Finance/trade |
| Kerala | Weather/tourism |

## Camera Animation

Auto-flies through top 3 story locations: close-up (500km) → tighter (300km) → wide overview (4,000km). Each step via `/tmp/query.txt` flytoview with 6s pause.

## Voiceover

TTS narration of top 3 headlines. Always generated. Format: "Top news stories. 1. [title]... 2. [title]..."

## Files

- `/home/nara/wm-collector/news_storyteller.py` — Main script
- `/home/nara/wm-collector/india_locations.py` — Location DB + visual detection + polygon/icon generators

## Cron (Auto-Refresh)

```bash
# World news every 30 min
cronjob action=create name=news-world schedule=30m \
  prompt="cd /home/nara/wm-collector && python3 news_storyteller.py --source world" \
  skills=news-storyteller

# India news separately  
cronjob action=create name=news-india schedule=30m \
  prompt="cd /home/nara/wm-collector && python3 news_storyteller.py --source india" \
  skills=news-storyteller
```
