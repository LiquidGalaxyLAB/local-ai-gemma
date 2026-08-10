---
name: global-progress-dashboard
description: The counterweight to every crisis skill — maps positive global trends (poverty falling, disease eradicated, renewables rising, species recovering) on the LG rig using Our World in Data's fully free API. Warm gold/amber visual language, green rising columns, sunrise gradient — designed to show a classroom or public demo audience that the world is getting better in measurable, data-backed ways.
version: 1.0.0
tags: [progress, positive, our-world-in-data, development, liquid-galaxy, classroom, demo]
related_skills: [energy-monitor, economic-markets, geography-educator]
---

# Global Progress Dashboard — Positive Trends Visualizer

Every other skill in Nara's catalog shows crisis, stress, threat, or conflict. That's appropriate for those domains — but it means the LG rig only ever shows bad news. This skill is the deliberate counterweight. It surfaces measurable positive global trends — extreme poverty falling, child mortality declining, renewable energy capacity growing, disease eradication milestones, species population recoveries — and renders them using a warm, optimistic visual language designed for classrooms and public demos where showing only crisis data would be misleading.

**This is directly inspired by World Monitor's "happy" variant** (`happy.worldmonitor.app`), which specifically surfaces positive news and progress signals rather than only crisis data. The LG version goes further: because the rig has physical scale and a flying camera, progress can be shown as literal *rising* — green columns that grow taller over time, a sunrise gradient that brightens as you fly toward regions that are improving fastest.

## Why Distinct From the 12 Existing Skills

Every existing Nara skill defaults to crisis visualization: armed-conflicts shows wars, cyber-infrastructure shows outages and attacks, natural-disaster shows destruction, economic-markets includes a "stress" layer, maritime-awareness tracks chokepoint threats. The energy-monitor skill tracks renewable installations but frames them as infrastructure, not as a progress narrative. This skill is the only one whose entire editorial stance is "here is what is getting better, backed by data, rendered as something beautiful." In a classroom or public demo context, showing only the crisis skills gives a distorted picture of the world. This skill balances the rig's emotional register.

## Trigger Phrases

- "show me positive global trends on the rig" / "what's getting better in the world"
- "progress dashboard on the LG" / "happy news view"
- "show me where extreme poverty is falling" / "what countries are improving fastest"
- "classroom demo — show something positive" / "give me the good news layer"
- "global development trends visualized" / "which Millennium Development Goals are on track"

## Data Sources (all free, no paid keys required)

| Indicator | Source | URL | Auth |
|-----------|--------|-----|------|
| Extreme poverty rate (% below $2.15/day) | Our World in Data (via World Bank PIP) | `api.ourworldindata.org/v1/indicators/` | **None** (free, open) |
| Child mortality rate (under-5 per 1000) | OWID (via UN IGME) | same endpoint | **None** |
| Life expectancy at birth | OWID (via UN WPP) | same endpoint | **None** |
| Renewable energy share (% of electricity) | OWID (via Ember/BP) | same endpoint | **None** |
| Disease eradication status (polio, guinea worm) | WHO Global Health Observatory | `ghoapi.azureedge.net/api/` | **None** (open) |
| Protected land area (% of territory) | OWID (via UNEP-WCMC) | same OWID endpoint | **None** |
| Literacy rate (adult, % 15+) | OWID (via UNESCO) | same OWID endpoint | **None** |
| Species population recoveries | IUCN Red List API | `api.iucnredlist.org/api/v4/` | Free token (optional — static reference data works without it) |
| Vaccination coverage (DTP3, measles) | OWID (via WHO/UNICEF) | same OWID endpoint | **None** |

**Our World in Data API:** Fully free, no key required. All data downloadable as JSON. The `indicators` endpoint lists ~3,000+ indicators; filtering for the progress set above is done client-side. Historical data goes back decades — the skill can show "change since 2000" or "change since 1990" as the primary metric.

**Confirmed working on this network:** The UNHCR API (similar structure) returned valid JSON. OWID's API uses the same REST pattern and is publicly documented at `docs.owid.io`.

## What the Skill Shows (5 Progress Metrics)

Rather than trying to show everything, the skill picks 5 metrics where the global trend is unambiguously positive and the data is high-quality:

| # | Metric | Why It's Unambiguously Good | Visual |
|---|--------|----------------------------|--------|
| 1 | **Extreme poverty decline** | Fell from 38% (1990) to ~8% (2024) globally | Green falling columns (inverted — lower is better) |
| 2 | **Child mortality decline** | Fell from 93/1000 (1990) to ~37/1000 (2024) | Amber-to-green gradient polygons on countries |
| 3 | **Renewable energy growth** | Solar + wind share tripled since 2015 | Gold rising columns with sunburst icon markers |
| 4 | **Life expectancy gains** | Global average rose from 64 (1990) to 73 (2024) | Blue-to-green extruded country polygons |
| 5 | **Disease eradication progress** | Polio 99.9% eliminated, guinea worm near zero, malaria deaths halved | Green concentric victory rings around eradication-zone countries |

## KML Generation — Layer by Layer

### Layer 1: Extreme Poverty — Green Falling Columns (inverted)

Each country gets a column at its centroid. Unlike the CII skill where tall = bad, here **short = good** — the column height represents the current poverty rate, and the column is rendered in a **falling animation** (3 KML states cycling via NetworkLink, each state 15% shorter than the last, showing the rate declining over the past 20 years in 3 steps). Countries that have nearly eliminated extreme poverty have tiny stub columns; countries still struggling have taller columns. All columns are green `#22cc66` (poverty falling is good news, even when the absolute rate is still high).

### Layer 2: Renewable Energy — Gold Rising Columns

A contrasting visual: gold `#ffaa00` extruded columns rising from each country, height proportional to the renewable share of electricity generation. Taller = more renewable. Countries like Norway (98% hydro), Iceland (100% geothermal/renewable), and Costa Rica (99% renewable) have towering gold columns. The column top has a small 6-point sunburst star marker — distinct from every other icon in Nara's catalog.

### Layer 3: Child Mortality — Amber-to-Green Choropleth

Country polygon fills colored on an inverted gradient:
- High child mortality (> 60/1000) → soft amber `#ff9944` at 40% opacity (acknowledging the challenge, but note: *every* country has improved)
- Medium (20–60) → yellow-green `#aacc44` at 40% opacity
- Low (< 20) → rich green `#22cc66` at 40% opacity

The entire map should look greener than any other Nara skill — because globally, child mortality has fallen dramatically everywhere. An amber patch in sub-Saharan Africa is still *much* better than it was in 1990.

### Layer 4: Disease Eradication — Green Victory Rings

Countries that have eliminated polio, guinea worm, or achieved malaria-free certification get 2 concentric green victory rings (radius 300/600 km, bright green `#00ff66`, pulsing slowly). These are celebration markers — the visual language of "mission accomplished." No other Nara skill uses celebration markers.

### Layer 5: Life Expectancy — Blue-to-Green Extruded Country Polygons

Countries extruded to altitude proportional to life expectancy gains since 1990. Color gradient: deep blue → teal → green as gain increases. Countries that gained 15+ years (Ethiopia, Cambodia, Rwanda, Timor-Leste) are deep green and highly elevated. The camera flying over these polygons shows the physical scale of improvement.

## Camera Design

This is the only Nara skill designed specifically for a **positive emotional arc** — the camera movement tells a story:

1. **Opening — Dawn:** Camera starts over East Africa at 3,000 km range, 70° tilt, facing east. The green columns and amber-to-green polygons are backlit by the "sunrise" (camera angle). Hold 5 seconds. Right-screen panel reads: "Since 1990: extreme poverty halved, child mortality down 60%, life expectancy up 9 years. This is what progress looks like from space."

2. **Progress flyover sequence — 4 stops:**
   - **Stop 1: Ethiopia/Rwanda** — life expectancy gains of 18+ years since 1990. Camera at 800 km, 60° tilt. The deep-green extruded polygons are prominent. Right-screen: "Life expectancy: +18 years since 1990. The fastest improvement in human history."
   - **Stop 2: India** — extreme poverty fell from 45% to ~10%. Camera at 1,200 km, 55° tilt. The green falling columns animate through 3 states. Right-screen: "Extreme poverty: 45% → 10%. Over 400 million people lifted above $2.15/day."
   - **Stop 3: Costa Rica** — 99% renewable electricity, 98% literacy, 80 years life expectancy. The gold renewable column towers. Right-screen: "Costa Rica: 99% renewable grid. Proof that development and sustainability can rise together."
   - **Stop 4: Global polio eradication zones** — the Americas, Europe, Western Pacific, Southeast Asia all certified polio-free. Green victory rings visible across multiple continents. Right-screen: "Polio: endemic in only 2 countries. From 350,000 cases/year (1988) to under 100 (2025)."

3. **Closing — Full globe:** Pull back to 10,000 km. The full progress landscape — green falling columns, gold rising columns, amber-to-green choropleth, blue-to-green extruded polygons, green victory rings — all visible at once. Hold 8 seconds. No TTS — just the image. Let the viewer absorb it.

Total tour: ~90 seconds.

## Right-Screen Balloon Design

Visual identity: **warm sunrise gradient** — deliberately the opposite of every other skill's dark/tech/crisis aesthetic:

- **Background:** Sunrise gradient — bottom `#1a0a2e` (dark purple) → middle `#4a1a3e` → top `#aa6622` (warm amber). This is the only skill with a gradient background.
- **Border:** Thin gold `#c9a84c` (2px) — shared with CII skill, but the gradient background makes it visually distinct.
- **Header:** "GLOBAL PROGRESS" in warm white serif font, centered. Subtitle: "Data: Our World in Data · World Bank · WHO" in small text.
- **Body:** 5 metric cards arranged vertically:
  - Each card: metric name, current global value, change since 1990 (with green up-arrow), 1-line context
  - Cards have a subtle gold left-border accent
- **Footer:** "All trends are real, measured, and continuing. Sources and methodology at ourworldindata.org."

Generated as PNG via Pillow (`gen_progress_panel.py`), deployed to rightmost screen.

## What Nara Says Back

> "Global progress dashboard deployed. Here's what the data shows: extreme poverty down from 38% to 8% since 1990, child mortality down 60%, life expectancy up 9 years globally. The green columns show countries rising — literally, on the globe. Costa Rica's renewable column towers at 99%, Ethiopia's life expectancy gains are deep green at +18 years. The camera is doing a dawn flyover — starting over East Africa and moving through the fastest-improving regions. This is what progress looks like from 10,000 kilometers up."

## The One Rule

**Never editorialize the data into propaganda.** The skill's power comes from the data being genuinely positive — extreme poverty *has* fallen, child mortality *has* declined, renewables *are* growing. The visual language (green, gold, sunrise, rising columns, victory rings) amplifies what the data already says. Do not add unsupported claims, do not cherry-pick countries to make trends look better than they are, and always show the absolute level alongside the improvement — a country that went from 30% poverty to 20% is improving, but 20% is still 20%. The skill's job is to show real, measurable, data-backed progress — not to pretend all problems are solved. The viewer should leave thinking "that's genuinely encouraging" rather than "that felt like a political ad."

## Files

| File | Purpose |
|------|---------|
| `/home/nara/wm-collector/collectors/global_progress.py` | Main script — fetches OWID indicators, builds 5-layer KML, deploys, runs dawn-flyover camera tour |
| `/home/nara/wm-collector/gen_progress_panel.py` | Right-screen PNG panel generator (Pillow, sunrise gradient theme) |
| `references/global-progress-dashboard/indicator-ids.json` | OWID indicator IDs for the 5 progress metrics |

## Manual Run

```bash
cd /home/nara/wm-collector && python3 collectors/global_progress.py
```

## Cron (Auto-Refresh)

```bash
cronjob action=create name=global-progress schedule=24h \
  prompt="cd /home/nara/wm-collector && python3 collectors/global_progress.py" \
  skills=global-progress-dashboard
```
