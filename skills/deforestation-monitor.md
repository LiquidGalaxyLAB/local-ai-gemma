---
name: deforestation-monitor
description: Live deforestation alerts, tree cover loss trends, and biodiversity hotspot stress mapped on Liquid Galaxy — the forest floor as a physical landscape the camera flies over.
version: 1.0.0
tags: [deforestation, biodiversity, forest, conservation, fire, liquid-galaxy, kml]
related_skills: [natural-disaster, coral-reef-monitor, animal-migrations, global-progress-dashboard]
---

# Deforestation & Biodiversity Monitor

Turns the LG rig into a forest watch station — the kind of display you'd see in a conservation NGO's operations center. Shows where forests are being lost right now (active fire/deforestation alerts from NASA satellites), how much tree cover each country has lost over the past two decades (long-term trend), where the world's most biodiverse forests are under pressure, and where protected areas form green strongholds against the tide.

This skill treats the forest floor as a physical landscape the camera moves through — you fly along deforestation fronts, hover over intact primary forest blocks, and see protected area boundaries glowing as green ramparts. The visual language is deliberately organic: deep forest greens, charcoal burn-scars, amber alert markers. No other Nara skill shows ecosystem-scale environmental change.

## Why Distinct From Existing Skills

- **natural-disaster** tracks earthquakes, wildfires, and weather alerts as point-in-time events. This skill tracks *forest cover change over decades* and *biodiversity pressure* — structural, not episodic.
- **coral-reef-monitor** covers marine bleaching. This is terrestrial forests.
- **animal-migrations** follows individual species. This shows the habitats those species depend on disappearing (or surviving).
- **global-progress-dashboard** shows positive trends. This skill shows a genuinely negative trend (forest loss) — but frames it as actionable monitoring, not doom.

## Trigger Phrases

- "show me deforestation on the rig" / "where are forests being lost right now"
- "tree cover loss by country on the LG" / "Amazon deforestation watch"
- "show me the world's most endangered forests" / "biodiversity hotspot view"
- "where are the protected areas holding" / "show me deforestation fronts globally"
- "Indonesia forest loss on the rig" / "Congo Basin tree cover trend"
- "primary forest loss since 2000" / "which countries lost the most forest last year"

## Data Sources

All sources verified — free or free-tier, minimal or no auth required.

### Layer 1: Live Fire Alerts (Active Deforestation Proxy)

| Source | URL | Auth | Notes |
|--------|-----|------|-------|
| NASA FIRMS (VIIRS thermal anomalies) | `firms.modaps.eosdis.nasa.gov/api/country/` | **None** (free, no key) | 375m resolution, updated every 3 hours. Fires on/near forest edges = active deforestation in many regions. |
| NASA FIRMS MODIS | same API | **None** | 1km resolution, 24h coverage. Coarser but longer historical record. |

**Confirmed:** Already used successfully by the natural-disaster skill. No auth needed. Response includes lat/lon/brightness/confidence for each fire detection. Filter to fires within 5km of known forest boundaries to isolate deforestation-relevant fires.

### Layer 2: Tree Cover Loss by Country (Long-Term Trend)

| Source | URL | Auth | Notes |
|--------|-----|------|-------|
| GFW Open Data Portal | `data-api.globalforestwatch.org` | **None** for CSV download | Hansen/UMD tree cover loss data (2001–2024), annual, 30m resolution. Country-level summaries downloadable as CSV. |
| GFW Tree Cover Loss API | `production-api.globalforestwatch.org/v2/` | Free registration token | Finer-grained analysis (subnational, by driver). Token is free — register at globalforestwatch.org. |

**What we use:** Country-level annual tree cover loss totals (hectares per year, 2001–2024) from the public CSV. This gives us the long-term trend — which countries are losing forest fastest, and whether the rate is accelerating or slowing. We bundle a pre-fetched country summary (updated monthly) and refresh on each run.

### Layer 3: Biodiversity Hotspots and Intact Forest Landscapes

| Source | URL | Auth | Notes |
|--------|-----|------|-------|
| RESOLVE Ecoregions | `ecoregions.appspot.com` (static GeoJSON) | **None** | 847 terrestrial ecoregions, freely redistributable as simplified polygons. |
| Conservation International Hotspots | Static KMZ published at `conservation.org` | **None** | 36 biodiversity hotspots covering 2.3% of Earth's land but holding >50% of plant species. |
| Intact Forest Landscapes | `intactforests.org` (static GeoJSON) | **None** | IFL 2020 dataset — the world's last large unfragmented forest blocks. Public domain. |
| IUCN Red List | `api.iucnredlist.org/api/v4/` | Free token (register at iucnredlist.org) | Species threat status by country. Token is instant and free. |
| Protected Planet WDPA | `api.protectedplanet.net/v5/` | Free token (register at protectedplanet.net) | World Database on Protected Areas — 280,000+ protected sites. Token is instant and free. |

### Layer 4: Forest Gain and Restoration

| Source | URL | Auth | Notes |
|--------|-----|------|-------|
| GFW tree cover gain | Same data-api portal as loss | **None** | Areas that gained tree cover 2000–2020, from Hansen/UMD data. |
| Bonn Challenge barometer | `infoflr.org/bonn-challenge-barometer` | **None** (PDF/open data) | Country restoration pledges vs actual progress. Static annual report. |

## What the Skill Shows (4 Layers)

### Layer 1: Active Fire Alerts — Red Heat Dots

Fire detections from the past 24 hours, filtered to forest-proximate zones. Each fire is a small red-orange dot (paddle icon) at the detection coordinates. Fire intensity (FRP — Fire Radiative Power) mapped to icon scale: faint dot (<10 MW) → bright dot (10-50 MW) → pulsing marker (>50 MW, large active fire).

Dots cluster at low zoom. At country zoom, individual fires are visible. The Amazon arc, Congo Basin edges, and Indonesian peatland zones are the most active clusters.

Color: **#ff3300** (bright red-orange), distinct from natural-disaster's wildfire markers (which are broader polygons). These are precise point detections.

### Layer 2: Tree Cover Change — Green-to-Red Country Choropleth

Each country colored by its **annual tree cover loss rate** relative to total forest area:

| Loss Rate | Color | Meaning |
|-----------|-------|---------|
| <0.1% / year | Deep green `#115522` | Forest stable or growing |
| 0.1–0.5% | Bright green `#22aa44` | Low pressure |
| 0.5–1.0% | Yellow-amber `#ddaa00` | Moderate — watching |
| 1.0–2.0% | Orange `#ee6600` | High loss rate |
| >2.0% | Red `#cc1111` | Crisis — accelerating loss |

Countries with **net forest gain** (more gain than loss) get a green border ring (2 concentric LineStrings, 100/200 km radius from centroid) — the "restoration halo." This flips the visual narrative: some places are actually getting greener.

### Layer 3: Biodiversity Hotspot Polygons

The 36 Conservation International hotspots as semi-transparent magenta-outlined polygons at ground level. Color: rich magenta `#aa2288` at 25% fill, 80% outline — a completely new color in Nara's palette (no other skill uses magenta). These polygons show where the highest concentrations of endemic species face the highest habitat loss.

Intact Forest Landscapes (IFL 2020) as deep green polygons: `#003311` at 40% fill. These are the world's last large unfragmented forests — the camera treats them as sacred ground, flying slowly over them.

### Layer 4: Protected Areas — Green Stronghold Borders

Protected areas (WDPA) rendered as green boundary LineStrings: `#00ff44` at 60% opacity, 2px width. National parks, nature reserves, indigenous territories — the green ramparts. When a protected area boundary is adjacent to active deforestation (fire dots within 10 km), the boundary line pulses amber: the stronghold is under pressure.

**Key visual:** A protected area in the Amazon with green borders but red dots flickering at its edges — the camera tells the story without a single word.

## Camera Design

The camera treats forests as terrain — altitude changes to match the canopy:

1. **Opening — Global canopy view:** Camera at 6,000 km, centered on the Amazon. Green-to-red choropleth visible globally, biodiversity hotspots highlighted in magenta, protected areas as green boundary webs. Hold 8 seconds. Right-screen: "Forest cover change since 2000. Green = stable/growing. Red = losing. Magenta = biodiversity at risk."

2. **Deforestation front fly-down — 4 stops:**
   - **Amazon arc (Brazil/Paraguay border):** Camera at 500 km, 55° tilt. The line where deep IFL green meets the agriculture frontier — red fire dots clustered along the boundary. Right-screen: "Amazon deforestation arc. Primary forest (green) meets agricultural expansion (red dots)."
   - **Congo Basin (DRC):** Camera at 600 km. One of Earth's last intact tropical forest blocks, surrounded by amber-to-red countries. Right-screen: "Congo Basin: the world's second-largest rainforest. Deforestation rate lower than Amazon but accelerating."
   - **Indonesia (Sumatra/Kalimantan):** Camera at 500 km. Red-orange country coloring, fire dots dense on peatlands near palm oil concessions. Right-screen: "Indonesia: highest deforestation rate for palm oil expansion. Peatland fires visible as dense red clusters."
   - **West Africa (Ghana/Cote d'Ivoire):** Camera at 400 km. Some of the highest deforestation rates globally (>2%/year). Small remnant forest blocks surrounded by red. Right-screen: "West Africa: >80% of original forest gone. Remaining blocks under extreme pressure."

3. **Restoration contrast:** Fly to Costa Rica — a country that went from net deforestation to net reforestation. Green country fill + restoration halo rings. Right-screen: "Costa Rica: from 26% forest cover (1983) to >52% (2024). Proof that reversal is possible."

4. **Final pull-back:** 8,000 km, full landscape. Hold 5 seconds. Total tour: ~140 seconds.

## Right-Screen Balloon Design

Visual identity: **field researcher's clipboard** — organic, data-dense, deliberately non-military:

- **Background:** Deep forest green `#0a1a0a` with a thin organic green `#22aa44` border (2px). This is the only skill with a green-dominant dark palette.
- **Header:** "FOREST MONITOR" in warm amber `#ddaa00` serif font, left-aligned. Subtitle shows current date and data freshness.
- **Body — 4-panel grid:**
  - Top-left: Annual tree cover loss (global total for current year, with trend arrow vs previous year). Large number + unit ("4.1 Mha lost in 2024 ↓12% vs 2023").
  - Top-right: Top 5 countries by loss rate, ranked, with country flags and loss bars.
  - Bottom-left: Active fire count (total + top 3 countries). "1,247 active forest fires detected in past 24h."
  - Bottom-right: Protected area status — "14.7% of global land protected. 5 biodiversity hotspots >80% degraded."
- **Footer:** "Data: NASA FIRMS · GFW / Hansen-UMD · RESOLVE Ecoregions · WDPA · All sources free and open."

Generated as PNG via Pillow (`gen_forest_panel.py`), deployed to rightmost screen.

## What Nara Says Back

> "Forest monitor deployed. Current picture: 4.1 million hectares lost globally this year — that's down 12% from last year's pace. Brazil still leads in absolute loss but the rate is slowing. Indonesia's peatland fires are active — I'm seeing 340+ fire detections in the past 24 hours on Kalimantan alone. The camera is flying the Amazon arc now, then moving to the Congo Basin and West Africa. Protected areas are showing as green borders — you can see where the pressure is by watching which boundaries have red dots near them."

## The One Rule

**Show the forest, not just the loss.** Every deforestation dashboard defaults to showing only damage — red everywhere, the viewer walks away depressed. This skill must balance loss with intactness. The Intact Forest Landscapes layer (deep green polygons), the protected areas (green borders), and the restoration halo (green rings around reforesting countries) are not afterthoughts — they are co-equal visual layers. The viewer should see both what is being lost AND what is still standing AND what is coming back. The camera's slow flyover of an intact Congo Basin block should feel the same way the coral-reef-monitor's healthy reef flyover feels: awe at what exists, urgency to protect it.

## Files

| File | Purpose |
|------|---------|
| `/home/nara/wm-collector/collectors/deforestation_monitor.py` | Main script — fetches FIRMS fire data, loads tree cover loss CSV, WDPA boundaries, RESOLVE ecoregions; builds 4-layer KML; deploys; runs camera tour |
| `/home/nara/wm-collector/data/tree_cover_loss_country.csv` | Pre-fetched GFW country-level annual tree cover loss (updated monthly via cron) |
| `/home/nara/wm-collector/data/ecoregions_simplified.geojson` | RESOLVE ecoregions simplified to 110m resolution |
| `/home/nara/wm-collector/data/ifl_2020_simplified.geojson` | Intact Forest Landscapes 2020 — simplified polygons |
| `/home/nara/wm-collector/gen_forest_panel.py` | Right-screen PNG panel generator (Pillow, forest green theme) |
| `references/deforestation-monitor/hotspot-list.json` | 36 CI biodiversity hotspots with centroid coordinates and descriptions |

## Manual Run

```bash
cd /home/nara/wm-collector && python3 collectors/deforestation_monitor.py
```

## Cron (Auto-Refresh)

```bash
cronjob action=create name=deforestation-monitor schedule=6h \
  prompt="cd /home/nara/wm-collector && python3 collectors/deforestation_monitor.py" \
  skills=deforestation-monitor
```
