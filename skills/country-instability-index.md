---
name: country-instability-index
description: Composite geopolitical stress score for 30+ countries, rendered as a physical landscape of extruded 3D columns the camera flies through. Ties armed-conflicts, economic-markets, cyber-infrastructure, and natural-disaster data into one cross-stream correlation view.
version: 1.0.0
tags: [instability, composite, meta-skill, liquid-galaxy, columns, camera-flythrough, cross-stream]
related_skills: [armed-conflicts, economic-markets, cyber-infrastructure, natural-disaster, lg-use-cases]
---

# Country Instability Index — Composite Meta-Skill

Turns the LG rig into a physical instability landscape. Each tracked country becomes an extruded 3D column whose height is its composite stress score, colored on a calm-to-crisis gradient. The camera flies a slow lap around the columns so unstable regions visibly tower over calm ones — a room full of people can see at a glance where the world is under strain. This is the "cross-stream correlation" idea from World Monitor, rebuilt for a multi-screen flying camera instead of a browser sidebar.

**This skill is a meta-skill:** it does not fetch new APIs itself. It composites data Nara's other skills are already fetching — conflict intensity, economic stress, internet shutdowns, disaster frequency — and gives them geographic, physical form so they can be compared side by side. A viewer standing in front of a 3-screen LG rig can literally see which countries are rising and which are calming down.

## Why Distinct From the 12 Existing Skills

Every existing skill is a domain silo: armed-conflicts shows wars, economic-markets shows GDP/inflation, cyber-infrastructure shows outages, natural-disaster shows quakes/fires. None of them answer the question "which countries are under the most stress *across all domains at once* right now?" The CII answers that question by compositing the signals those skills already fetch, then rendering them as a single physical landscape where height = total stress and the camera can actually fly between the columns.

This is also the closest Nara gets to World Monitor's "cross-stream correlation" — flagging when multiple independent signals converge on the same country. A country with active conflict AND internet shutdown AND currency freefall AND recent M5+ earthquake should tower over a country with just one of those things, and on a physical 3D globe with extruded columns, it visibly will.

## Trigger Phrases

- "show me the country instability index on the rig" / "which countries are most unstable right now"
- "composite stress picture on the globe" / "cross-stream correlation view"
- "CII on the LG" / "show me where the world is under strain"
- "instability landscape — let me see the columns"

## Data Sources (all free, no paid keys required for core functionality)

| Signal | Source | Key Required? | Existing Skill That Already Fetches It |
|--------|--------|---------------|----------------------------------------|
| Conflict intensity | Static zone config + BBC conflict news | No | armed-conflicts |
| Economic stress | FRED (unemployment, yield curve, inflation) + World Bank | FRED free key | economic-markets |
| Internet shutdown status | Cloudflare Radar outages | Free CF token | cyber-infrastructure |
| Natural disaster frequency | USGS M4.5+ earthquakes + NASA EONET events | No | natural-disaster |
| ACLED event count trend | ACLED API (free academic tier — armed-conflicts already uses this indirectly via static config) | Free key | Can be added as lightweight fetch |
| GDELT tone/volume | GDELT Doc API (fully free, no key, rate-limited to ~100 req/day) | **None** | New — single REST call per run |

**Composite formula:** each signal normalized to 0–100, then weighted:

| Component | Weight | Rationale |
|-----------|--------|-----------|
| Armed conflict intensity | 30% | Active war is the strongest instability driver |
| Economic stress | 25% | Currency freefall, inflation, yield curve inversion |
| Internet/cyber disruption | 20% | Government shutdowns, GPS jamming, BGP anomalies |
| Natural disaster frequency | 15% | Recent M5+ quakes, active wildfires, flood alerts |
| GDELT tone/volume trend | 10% | News media tone (negative spike) + mention volume spike |

## KML Generation — Layer by Layer

### Base Layer: Country Polygons

Each tracked country gets a semi-transparent polygon fill on the ground at altitude 0. Color = the composite score mapped to a gradient:

- 0–25 (calm) → pale cyan `#88ccff` at 30% opacity
- 26–50 (watching) → yellow `#ffcc00` at 40% opacity
- 51–75 (elevated) → orange `#ff6600` at 50% opacity
- 76–100 (critical) → deep red `#cc0000` at 60% opacity

Polygons sourced from a bundled simplified GeoJSON (Natural Earth 110m resolution, ~200 countries, freely redistributable).

### Column Layer: 3D Extruded Instability Towers

For each of the 30+ tracked countries, a 3D extruded column rising from the country centroid. Column properties:

- **Height:** composite score mapped to 0–50 km altitude (score of 75 = 37.5 km column, score of 100 = 50 km). This means unstable countries literally tower into space.
- **Width:** 0.5° lat/lon square cross-section — wide enough to be visible at global zoom, narrow enough that neighboring countries don't overlap.
- **Color:** same gradient as polygon base, but fully opaque. Critical countries glow with a subtle red-orange pulsing effect via altitude oscillation (±5%).
- **Shape:** hexagonal prism (6-sided) to differentiate from the rectangular columns used by other skills.

KML construction (VM-safe — no CDATA, no gx: namespace):

```xml
<Style id="cii_col_75">
  <PolyStyle><color>cc0000ff</color><fill>1</fill><outline>1</outline></PolyStyle>
</Style>
<Placemark>
  <name>Ukraine: 82</name>
  <styleUrl>#cii_col_75</styleUrl>
  <Polygon><extrude>1</extrude><altitudeMode>absolute</altitudeMode>
    <outerBoundaryIs><LinearRing>
      <coordinates>...6 hex vertices at 37500m altitude...</coordinates>
    </LinearRing></outerBoundaryIs>
  </Polygon>
</Placemark>
```

### Label Layer: 1-Line Country Score Labels

Each column gets a 1-line label at the column's top altitude + 3km offset. Format: "🇺🇦 Ukraine 82 ↑" (flag emoji, country name, score, trend arrow). Scale 2.2, white, no icon.

### Rings Layer: Top-5 Pulse Rings

The 5 highest-scoring countries get concentric pulse rings at ground level (3 concentric LineString circles, radius 200/400/600 km, opacity fading outward). This draws the eye to the towers that matter most.

## Camera Design

The camera movement is the whole point of this skill — it turns a numeric index into something you can physically perceive:

1. **Opening position:** Global altitude (~8,000 km range), camera centered on the Atlantic so all columns are visible. Hold 8 seconds — the viewer sees the full landscape, towers rising from unstable regions.

2. **Slow rotation lap:** Camera orbits Earth at 6,000 km range, 55° tilt, completing one full 360° rotation over 60 seconds. During this lap, the viewer sees columns pass by — Europe (moderate heights), Middle East (tall red towers), East Asia (mixed), Africa (varied), Americas (generally lower). No per-country stops — this is a landscape scan.

3. **Top-5 fly-down sequence:** Camera descends to each of the 5 highest-scoring countries in sequence:
   - Fly to country at 1,200 km range, 60° tilt
   - Dwell 8 seconds — column fills the view
   - Right-screen panel updates with country name and component breakdown
   - TTS plays 2-line summary of why this country scores high
   
4. **Final pull-back:** Camera returns to global altitude, full landscape visible. Hold 5 seconds. Tour complete.

Total tour: ~130 seconds.

## Right-Screen Balloon Design

Visual identity: **intelligence briefing dossier** — distinct from every other skill:

- **Background:** Deep navy `#0a1628` (intelligence-community dark blue, not the pure black of cyber-infrastructure). Thin gold `#c9a84c` border (2px).
- **Header:** "INSTABILITY INDEX" in gold Impact-style font, centered. UTC timestamp below in small monospace.
- **Body — 3-column layout:**
  - Left column: Country list (top 10 by score), each row showing flag, country name, score bar (gold fill proportional to score), trend arrow
  - Center column: Current country detail — score ring (SVG donut, 0–100, gold fill proportional), 5 component breakdown bars (Armed Conflict / Economic / Cyber / Natural Disaster / GDELT Tone), each labeled with its weighted contribution
  - Right column: "Convergence Alerts" — list of countries where 3+ signals are active simultaneously (the cross-stream correlation detection). Each alert shows which signals converged and when.
- **Footer:** "COMPOSITE SCORE — Weighted Multi-Signal Blend" in small gold text.

Generated as PNG via Pillow (`gen_cii_panel.py`), deployed to rightmost screen as ScreenOverlay.

## What Nara Says Back

> "Country Instability Index deployed. 34 countries tracked — I'm seeing elevated towers across the Middle East, East Africa, and Eastern Europe. Ukraine leads at 82, driven by active conflict plus economic stress. The camera is doing a slow orbit now — you can see the columns rise as we pass unstable regions. I'll fly down to the top 5 for a closer look."

## The One Rule

**Height is the whole interface.** Every design decision — extruded columns instead of flat polygons, 0–50 km mapping instead of subtle color differences, hexagonal prisms, top-5 pulse rings, slow-rotation camera — serves the single purpose of making instability visible as physical scale. If a viewer standing in the room cannot point to the most unstable country without reading a label, the skill has failed. The columns must do the work.

## Files

| File | Purpose |
|------|---------|
| `/home/nara/wm-collector/collectors/cii_composite.py` | Main script — fetches GDELT tone, composites all signals, builds KML, deploys, runs camera tour + TTS |
| `/home/nara/wm-collector/templates/cii_polygons.geojson` | Simplified country polygon GeoJSON (Natural Earth 110m) |
| `/home/nara/wm-collector/gen_cii_panel.py` | Right-screen PNG panel generator (Pillow) |
| `references/country-instability-index/cii-countries.json` | Tracked countries list with centroids, baseline scores, aliases |

## Manual Run

```bash
cd /home/nara/wm-collector && python3 collectors/cii_composite.py
```

## Cron (Auto-Refresh)

```bash
cronjob action=create name=cii-composite schedule=6h \
  prompt="cd /home/nara/wm-collector && python3 collectors/cii_composite.py" \
  skills=country-instability-index,armed-conflicts,economic-markets,cyber-infrastructure,natural-disaster
```
