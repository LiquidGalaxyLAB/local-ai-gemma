---
name: news-storyteller
description: Autonomous news KML storyteller — fetches from multiple RSS feeds based on user query, extracts locations, generates 3D dynamic KMLs by content type (flood=blue polygon, protest=orange zone, sport=gold), deploys text panel to rightmost screen, animates camera between stories, and generates TTS voiceover.
version: 3.0.0
tags: [news, kml, liquid-galaxy, text-panel, tts, 3d-polygons, camera-animation]
related_skills: [lg-use-cases, lg-kml-patterns]
---

# News Storyteller

Autonomous multi-article news visualization for Liquid Galaxy. Fetches from **multiple RSS feeds**, picks the relevant one based on user query, extracts locations from articles, deploys **3D context-aware visuals on Earth** (extruded polygons, rings, columns — colored by content category) and a **styled HUD news-card balloon on the rightmost screen** (rightmost = floor(N/2)+1; for N=3 → slave_2.kml = lg2), plus TTS voiceover and auto-camera flythrough.

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

# Limit to top N stories (default 10) — e.g. "top 5 spain news"
python3 news_storyteller.py --query "spain" --top=5
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
User query -> pick relevant RSS feed -> fetch top N articles ->
  for each article:
    find_locations(title + description)
    detect_category(title + description) -> breaking/conflict/disaster/
        geopolitics/economy/science/sport (news_visuals.py)
    -> 3D extruded polygon if region has boundary data
    -> breaking/conflict: concentric pulse rings + center icon
    -> disaster: 3D column at epicenter + radius rings + icon
    -> otherwise: color-coded icon by category
  -> merge all features into master.kml (no CDATA, no text on globe)
  -> generate right-screen PNG text panel (fallback)
  -> generate styled HUD news-card balloon KML (escaped HTML)
  -> deploy master.kml + deploy_rightmost_kml(card) to slave_<rightmost>.kml
  -> flytoview overview -> auto-fly to top 3 story locations
  -> TTS voiceover of top headlines
```

The script now handles the rightmost-screen balloon deployment itself via
`deploy_rightmost_kml()` (computes floor(N/2)+1 from `SCREENS=` in
`~/etc/shell.conf`, default 3). No manual overlay step needed when the card
balloon is the target.

## News Card Balloon UI (rightmost screen — user's preferred standard)

User requirement (Nara, July 2026): the rightmost screen balloon must be a
**styled HUD card feed**, not a plain text dump. Implemented in
`news_visuals.py` → `news_card_balloon_kml()`:

- Dark semi-transparent balloon (`bgColor=bb000000`) — feels like an overlay, never a light card.
- **Category color bar** at top of each card: red=breaking/conflict, orange=disaster, blue=geopolitics, green=economy, yellow=science/sport, grey=default.
- Bold white headline 27px, muted source+timestamp 13px, summary 17px, category badge at bottom.
- Multiple stories stack as separate cards in ONE balloon (scrollable feed), not separate balloon files.
- **VM-safe: escaped HTML entities, NOT CDATA** — Earth 7.3.3 drops any Placemark containing CDATA (see `lg-ssh-control` pitfalls). The card body is escaped with `&lt;div&gt;` etc.
- Auto-opens via `<gx:balloonVisibility>1</gx:balloonVisibility>`.

If the user asks for the balloon specifically, deploy the card balloon; the PNG panel remains as a fallback asset (`right_panel.png`) but is no longer the primary right-screen content.

## ⚠️ Rightmost Screen Content — Card Balloon (primary) + PNG overlay (fallback)

`news_storyteller.py` deploys:
1. story KML → `/var/www/html/kml/master.kml` (visuals, correct)
2. news-card balloon → `/var/www/html/kml/slave_<rightmost>.kml` via `deploy_rightmost_kml()` (auto-computed, floor(N/2)+1)
3. panel PNG → `/var/www/html/kml/right_panel.png` (fallback asset)

The script handles the rightmost-screen card balloon itself — **no manual agent step needed for the balloon path**. Only if the balloon fails to render (or the user wants the PNG panel style) do you deploy the ScreenOverlay KML manually:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <name>Right Screen Panel</name>
    <ScreenOverlay>
      <name>Text Panel</name>
      <Icon><href>http://lg1:81/kml/right_panel.png</href></Icon>
      <overlayXY x="1" y="0.5" xunits="fraction" yunits="fraction"/>
      <screenXY x="0.98" y="0.5" xunits="fraction" yunits="fraction"/>
      <size x="0" y="0" xunits="pixels" yunits="pixels"/>
    </ScreenOverlay>
  </Document>
</kml>
```

Deploy via the standard helper pattern (write local, scp to lg1, `sudo cp` to `/var/www/html/kml/slave_<rightmost>.kml`). The slave's 3s Solo KML refresh picks it up — no relaunch.

**Verification:** check Apache vhost log at `/var/log/apache2/other_vhosts_access.log` on lg1 for `GET /kml/slave_2.kml` (and `right_panel.png` for the fallback) returning 200 from the rightmost slave's IP (e.g. `10.42.42.2` for lg2) — that proves content is live on the right screen.

## Script Notes (July 2026 fixes)

- `main()` used to call a non-existent `deploy_and_play()` → NameError. Fixed to `deploy_kml()`. If you see that NameError again, the fix is the same one-line rename.
- `pick_feed()` now routes "pune"/"kolkata"/"chennai"/"hyderabad" → India feed, and "spain"/"madrid"/"barcelona"/"ceuta"/"europe" → world feed. `--query="pune"` alone previously fell through to the world feed (wrong stories).
- `--top=N` option added (default 10) — limits article count for "top 5" style requests.
- `deploy_rightmost_kml()` added — deploys the news-card balloon to `/var/www/html/kml/slave_<rightmost>.kml`, computing rightmost = floor(N/2)+1 from `SCREENS=` in `~/etc/shell.conf` (default 3).
- `deploy_right_panel()` docstring still says "slave_3.kml" — misleading; it only pushes the PNG. The card balloon (not the PNG) is now the primary right-screen content.

## Visual Types

**MULTI-SHAPE + MULTI-COLOR RULE (mandatory):** KMLs must NEVER be identical. Each story gets a unique shape + color combo seeded by story index (`story_shape(seed, cat, ...)` + `palette_for(cat, seed)`). Shapes rotate: rings, 3D columns, cones, diamonds, dot clouds, radials — colors vary within each category's palette (3 variants). Never recycle the same style.

**⚠️ NEWS vs CONFLICT SEPARATION:** news-storyteller and armed-conflicts are DIFFERENT skills with DIFFERENT visual languages. Conflict visuals (front-line arrows, siege rings, displacement arrows, faction markers, crisis spirals, border lines) belong ONLY to armed-conflicts. News uses its own shapes (rings, columns, cones, diamonds, dot clouds, radials, arcs). Do NOT mix them.

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

**Category palettes (news_visuals.CATEGORIES)** — each has 3 color variants cycled by seed: breaking/conflict (red family), disaster (orange family), economy (green family), science/sport (yellow family), geopolitics (blue family), default (grey).

**Category system (news_visuals.py `CATEGORIES` / `detect_category`)** — used
for the card balloon AND for choosing the Earth visual:
`breaking`, `conflict` → pulse rings (`ring_kml`); `disaster` → 3D column +
radius rings (`column_kml`); `geopolitics`, `economy`, `science`, `sport`,
`default` → category-colored icons. `line_kml` / `arc_kml` are available for
front lines, trade corridors, and launch trajectories. Category colors (bar
hex): breaking/conflict `#ff2d2d`, disaster `#ff8c1a`, geopolitics `#2d7fff`,
economy `#2dff6b`, science `#ffe32d`, sport `#ffd32d`, default `#9aa4b2`.

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

- `/home/nara/wm-collector/news_storyteller.py` — Main script (fetch → categorize → KML + card balloon → deploy → camera → TTS)
- `/home/nara/wm-collector/news_visuals.py` — **NEW July 2026**: category detection, HUD news-card balloon generator (`news_card_balloon_kml`), story-type KML generators (`ring_kml`, `column_kml`, `line_kml`, `arc_kml`, `style_block`, `viz_for_category`), HTML escaper (`esc`)
- `/home/nara/wm-collector/india_locations.py` — Location DB + visual detection + polygon/icon generators
- `references/news-visual-spec.md` — Full user spec: card balloon UI standard, story-type → KML-type mapping (breaking rings, country polygons, conflict layers, economy columns, disaster columns+rings, election choropleth, space arcs, multi-story pins), category color reference, implemented-vs-TODO status

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
