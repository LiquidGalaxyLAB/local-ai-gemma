---
name: animal-migrations
description: "Track animal migrations with live data on Liquid Galaxy."
version: 1.0.0
platforms: [linux]
metadata:
  hermes:
    tags: [wildlife, migrations, conservation, species, kml, liquid-galaxy]
    related_skills: [lg-data-visualization, lg-kml-tours, lg-ssh-control, geography-educator]
---

# Animal Migration Skill

Turns the LG rig into a wildlife tracking center — the kind of display you see in a conservation research lab or a natural history museum. Shows migration routes, species status, historical comparisons over decades, and global migration overviews across 4 layers. Camera moves like a nature documentary: slow cinematic arcs following corridors across continents and oceans. The visualization should feel alive.

**4 layers:** (1) Migration Routes, (2) Species Cards & Status, (3) Historical Comparison, (4) Global Migration Overview.

**Key dependency stance:** Python + `wm-collector` framework. All free open APIs (Movebank, IUCN, eBird, OBIS, NOAA). VM-safe KML. Rightmost screen = floor(N/2)+1.

## When to Use

Trigger phrases:
- "show me where monarch butterflies migrate" / "track the wildebeest migration on the rig"
- "where do humpback whales travel" / "show me animal migrations globally"
- "which species are migrating right now" / "show me the great migration in Africa"
- "compare how bird migration has changed over the last 20 years"
- "show me endangered migratory species" / "where do arctic terns fly"
- "show migration routes for elephants" / "which animals migrate through India"
- "show me salmon migration" / "what is the longest animal migration on earth"
- "show me how climate change has affected bird migration timing"
- "migration watch on the rig"

**Extract 3 anchors from user input:** species or species group, geographic region, current data or historical comparison or both.

## Data Sources (all free and open)

| Source | URL | Auth | Purpose |
|--------|-----|------|---------|
| Movebank | `movebank.org` | Free registration | GPS tracking data, millions of individual animal journeys |
| IUCN Red List | `api.iucnredlist.org` | Free API token | Species status, population trends, range maps |
| eBird (Cornell) | `api.ebird.org` | Free API key | Bird observation records going back decades |
| OBIS | `api.obis.org` | None (open) | Marine species data (whales, turtles, fish) |
| Journey North | `journeynorth.org` | None (open) | Monarch butterfly tracking |
| NOAA Climate | `ncdc.noaa.gov/cdo-web` | Free API token | Temperature anomaly data for historical overlay |

## How to Run

```bash
cd /home/nara/wm-collector
python3 migrations_run.py --species=monarch --region=north-america
python3 migrations_run.py --species=all --season=current
python3 migrations_run.py --species=wildebeest --compare
python3 migrations_run.py --layer=global-overview
```

## Quick Reference

| Layer | Data Source | Update Cadence | Purpose |
|-------|------------|----------------|---------|
| Migration Routes | Movebank + IUCN range maps | Static (reference) + live tracking | Corridor LineStrings |
| Species Cards | IUCN Red List | Monthly | Status, population, threats |
| Historical Comparison | eBird + Movebank + NOAA | Yearly comparison | Route shifts over decades |
| Global Overview | Composite from all sources | Seasonal refresh | 15-20 major migrations |

## Species Tracked (Tier 1 — most visually striking)

| Species | Migration Distance | Route | Status |
|---------|------------------|-------|--------|
| Arctic Tern | 90,000 km/yr | Arctic → Antarctic → Arctic | Least Concern |
| Monarch Butterfly | 4,500 km | Canada → Central Mexico | Endangered |
| Wildebeest | 1,600 km circuit | Serengeti → Masai Mara loop | Near Threatened |
| Humpback Whale | 16,000 km | Alaska → Hawaii / Antarctica → Australia | Least Concern |
| Bar-tailed Godwit | 11,000 km nonstop | Alaska → New Zealand | Near Threatened |
| Caribou | 5,000 km | Arctic tundra → boreal forest | Vulnerable |
| Leatherback Turtle | 10,000 km | Pacific Ocean crossings | Vulnerable |
| Christmas Island Red Crab | 8 km | Forest → coast | Not Evaluated |
| European Eel | 6,000 km | European rivers → Sargasso Sea | Critically Endangered |
| Barn Swallow | 10,000 km | Europe → sub-Saharan Africa | Least Concern |

## Procedure

1. **Extract species + region + comparison mode from user request.** If "migration watch" → Global Overview layer. If "monarch butterflies" → Layers 1+2. If "how has bird migration changed" → Layer 3 historical comparison.
2. **Build KML layers** using `migrations_visuals.py`:
   - Layer 1: species-colored LineString corridors following actual terrain (not straight lines), directional arrows at regular intervals, origin+destination habitat Placemarks explaining why the journey happens, terrain context (mountains as obstacles, rivers as guides, coastlines as corridors), animation dots for currently active migrations
   - Layer 2: species icon Placemarks at route midpoints (bird silhouette, whale tail, paw print, butterfly outline), IUCN status colored (green=LC, yellow=NT, orange=VU, red=EN, dark red=CR, black=EX), balloon with scientific name/status/population/distance/diet/threat/remarkable fact, threat overlay polygons (shipping lanes, hunting zones, dam barriers) for endangered species
   - Layer 3: dual route comparison (historical grey route + current colored route), timing shift markers with calendar icons at waypoints ("Historically 15 Mar, now 1 Mar — 14 days earlier"), side-by-side population columns (historical tall vs current short where declining), NOAA temperature anomaly choropleth overlay
   - Layer 4: 15-20 simultaneously shown migration routes colored by species class (bird=sky blue, marine=navy, land mammal=amber, turtle=teal, fish=silver, insect=orange), global 360° slow-rotating camera at high oblique, legend on rightmost screen balloon
3. **Seasonal awareness:** Always check current month. Mar-Apr = northward spring. Aug-Sep = southward autumn. Dec-Jan = southern hemisphere summer. Default to currently active migrations.
4. **Generate natural history panel PNG** — warm dark wood-toned background `#2a1f14`, thin green `#4a8c3f` border. "ANIMAL MIGRATIONS" header with current month+season. Species roster with one-line route summary, IUCN colored dot, activity status. "Migration of the Moment" card: 3-sentence editorial about the most remarkable/urgent migration currently visualized.
5. **TTS narration** — speak like a nature documentary narrator, not a data system. Lead with the remarkable fact before the statistic. Always say IUCN status. Example: "The monarch butterfly is one of the most extraordinary travelers on Earth. Right now, millions are making a 4,500-kilometer journey from Canada to the mountains of central Mexico, guided by the sun and the Earth's magnetic field. Their numbers have fallen 80 percent since the 1990s."
6. **Deploy** via scp to lg1 → sudo cp to master.kml + slave_2.kml + PNG. 3s refresh — no relaunch.

## Rightmost Screen PNG Panel

Warm dark wood background, thin green border, natural history museum aesthetic:

```
┌──────────────────────────────────────────┐
│ ANIMAL MIGRATIONS                        │
│ August 2026 · Late Summer · Southbound   │
├──────────────────────────────────────────┤
│ 🟡 Arctic Tern: Arctic→Antarctic 90K km │
│ 🟠 Monarch: Canada→Mexico 4,500 km      │
│ 🟢 Wildebeest: Serengeti circuit 1,600  │
│ 🟢 Humpback: Alaska→Hawaii 6,000 km     │
├──────────────────────────────────────────┤
│ ★ MIGRATION OF THE MOMENT               │
│ The monarch butterfly cannot complete    │
│ its migration in a single generation.    │
│ It uses a multi-generational relay       │
│ that science still does not fully        │
│ understand. Numbers have fallen 80%.     │
└──────────────────────────────────────────┘
```

Generator: `migrations_panel_png()` via Pillow.

## The One Rule

Animal migration is not data. It is one of the most ancient and astonishing things on this planet. Every visualization should make the viewer feel something, not just know something. Lead with the remarkable fact before the statistic. Always show the IUCN status. Always show the historical comparison when the data exists, because the change is usually more striking than the current snapshot alone.

## Narration Style (TTS)

Speak like a nature documentary narrator. NOT "Migration route loaded for Danaus plexippus." INSTEAD: "The monarch butterfly is guided by the sun, the Earth's magnetic field, and something we still do not fully understand."

For each species, structure the narration as: remarkable fact → route description → distance → current status → what threatens it → why it matters.

## Verification

- Movebank: `curl` to `movebank.org` confirms API reachable
- IUCN: `curl "https://api.iucnredlist.org/api/v4/taxa/species/15967"` returns JSON
- eBird: `curl "https://api.ebird.org/v2/data/obs/geo/recent"` returns observations
- Master KML has 15+ styleUrl references across species classes
- lg2 fetches `slave_2.kml` + PNG every 3s

## Files

- `scripts/migrations_visuals.py` — Migration KML generators (route_kml, species_card_kml, historical_comparison_kml, global_overview_kml, migrations_panel_png)
- `scripts/migrations_run.py` — CLI entry point
- `/home/nara/wm-collector/collectors/migrations_*.py` — Per-layer collectors
- Related: `lg-data-visualization` (framework), `lg-kml-tours` (camera), `geography-educator` (terrain-aware visualizations)

## How to get free API keys

| Source | Registration | Free Tier |
|--------|-------------|-----------|
| Movebank | `movebank.org` → Create account | Unlimited (academic) |
| IUCN | `api.iucnredlist.org` → Request token | 10,000 req/day |
| eBird | `ebird.org` → API key | Unlimited (non-commercial) |
| OBIS | No key needed | Open API |
| NOAA CDO | `ncdc.noaa.gov` → Request token | 1,000 req/day |
| Journey North | No key needed | Open web data |
