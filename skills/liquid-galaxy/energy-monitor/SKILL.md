---
name: energy-monitor
description: "Live energy infrastructure layers on Liquid Galaxy."
version: 1.0.0
platforms: [linux]
metadata:
  hermes:
    tags: [energy, pipelines, infrastructure, mining, renewables, kml, liquid-galaxy]
    related_skills: [maritime-awareness, lg-data-visualization, lg-kml-tours, armed-conflicts]
---

# Energy & Infrastructure Monitor

Turns the LG rig into an energy command center. Covers pipelines, power plants, fuel shortages, solar/wind installations, and mining sites across 5 toggleable layers. Camera defaults to high oblique over the region — energy is physical: pipelines follow terrain, mines cluster around geology, renewables track latitude and wind belts.

**5 layers, each toggleable:** (1) Pipelines, (2) Energy Infrastructure, (3) Fuel Shortages, (4) Renewables, (5) Mining Sites.

**Key dependency stance:** Python + `wm-collector` framework. Free open APIs (EIA, GIE AGSI, Our World in Data, World Bank, Yahoo Finance). VM-safe KML (escaped HTML, no CDATA, rounded coords). Rightmost screen = floor(N/2)+1.

## When to Use

Trigger phrases:
- "show me global pipelines" / "where are the major oil fields"
- "show energy infrastructure on the rig" / "are there any fuel shortages right now"
- "show me renewable energy installations" / "where are the biggest solar farms"
- "show mining sites in Africa" / "full energy picture on the rig"
- "energy watch" / "show me LNG terminals"
- "where are the major power plants" / "show offshore oil rigs"
- "which regions have fuel shortages today" / "where are the biggest wind farms"

**Extract 3 anchors:** layer(s) wanted / region / live vs reference.

## Data Sources (from World Monitor source code — verified free)

| Source | URL | Auth | WM File |
|--------|-----|------|---------|
| EIA Open Data (oil/gas/inventory) | `eia.gov/opendata/` | Free API key (`EIA_API_KEY`) | `scripts/seed-energy-spine.mjs` |
| GIE AGSI+ (European gas storage) | `agsi.gie.eu/api` | Free token (`AGSI_API_KEY`) | `scripts/seed-gie-gas-storage.mjs` |
| IEA Oil Stocks | `api.iea.org/netimports/` | Free with account | `scripts/seed-iea-oil-stocks.mjs` |
| JODI (oil + gas monthly stats) | JODI database | Free | `scripts/seed-jodi-oil.mjs`, `seed-jodi-gas.mjs` |
| Our World in Data (energy mix) | `owid-public.owid.io/data/energy/owid-energy-data.csv` | None (open CSV) | `scripts/seed-owid-energy-mix.mjs` |
| World Bank (power reliability) | `api.worldbank.org/v2` | None (open) | `scripts/seed-power-reliability.mjs` |
| Yahoo Finance (crude/gas quotes) | `query1.finance.yahoo.com/v8/finance/chart/` | None (public) | `scripts/seed-commodity-quotes.mjs` |
| Global Energy Monitor (pipelines) | Public GeoJSON | None (open) | `scripts/seed-pipelines-gas.mjs`, `seed-pipelines-oil.mjs` |
| WRI Global Power Plant DB | Public dataset | None (open) | `scripts/seed-energy-capacity.mjs` |
| IRENA / Global Solar & Wind Atlas | Public stats | None (open) | Referenced in WM docs |

**Commodity tickers used (Yahoo Finance):** `CL=F` (WTI crude), `BZ=F` (Brent crude), `TTF=F` (TTF natural gas), `MTF=F` (coal). Free, no key needed.

## How to Run

```bash
cd /home/nara/wm-collector
python3 energy_run.py --layer=pipelines --region=europe
python3 energy_run.py --layer=renewables --region=global
python3 energy_run.py --layer=all              # Full stack
python3 energy_run.py --layer=shortages
python3 energy_run.py --layer=mining --region=africa
```

Uses `sshpass` SCP + Python subprocess sudo-cp to lg1. No relaunch — 3s NetworkLink refresh.

## Quick Reference

| Layer | Data Source | Update Cadence | Key Files |
|-------|------------|----------------|-----------|
| Pipelines | Global Energy Monitor GeoJSON | Static (reference) | `collectors/pipelines.py` |
| Infrastructure | WRI Global Power Plant DB | Quarterly | `collectors/energy_infra.py` |
| Fuel Shortages | EIA + IEA + news feeds | Daily | `collectors/energy_shortages.py` |
| Renewables | OWID + IRENA + Solar/Wind Atlas | Monthly | `collectors/energy_renewables.py` |
| Mining Sites | USGS mineral data | Quarterly | `collectors/energy_mining.py` |

## Procedure

1. **Extract layer + region from user request.** If "energy watch" → full 5-layer stack. If "solar farms in India" → Layer 4, India region. If "what pipelines cross Ukraine" → Layer 1, Ukraine region.
2. **Build KML layers** using `energy_visuals.py` generators:
   - Layer 1: pipeline LineStrings colored by commodity (black=oil, orange=gas, cyan=LNG, yellow=refined, purple=hydrogen), thickness ∝ capacity, solid=operational/dashed=sanctioned, compressor+terminal Placemarks
   - Layer 2: facility Placemarks typed by category (atom=nuclear, smokestack=coal, flame=gas, tower=refinery, tanker=LNG, rig=offshore, tower=substation), 3D extruded columns ∝ capacity, color-coded by fuel, green/amber/red by status
   - Layer 3: shortage Polygon overlays (amber=spot shortage, orange=rationing, red=acute crisis), relief-route LineStrings, per-zone balloon with type/duration/cause/price-premium
   - Layer 4: solar Polygon fills (gold), offshore wind zones (teal), wind turbine clusters, hydro dam icons with reservoir level %, renewable choropleth background (green ≥80%, grey <20%)
   - Layer 5: mine Placemarks typed by commodity (diamond=coal, radioactive=uranium, battery=lithium, etc.), supply-chain LineStrings mine→processor→market, Atacama lithium triangle special overlay
3. **Generate energy SITREP balloon** — dark charcoal `#1a1a1a`, thin amber `#d4a017` border, "ENERGY & INFRASTRUCTURE MONITOR" header with live WTI/Brent/TTF ticker, 5 status lines with colored dots.
4. **Deploy** via scp to lg1 → sudo cp to master.kml + slave_2.kml. 3s refresh — **no relaunch**.
5. **Camera:** Global altitude for full stack (10s) → top 3 shortage zones → largest renewable site → most significant mine → pull back. Total tour 90-120s.

## Pipeline Layer — Key Geopolitical Overlays

For these politically critical pipelines, generate a special highlight overlay + balloon text:
- **Nord Stream 1+2:** Baltic Sea, Russia→Germany. Destroyed/sanctioned — show as dashed grey ghost lines with note "sabotaged Sept 2022"
- **Druzhba:** Russia→Eastern Europe. Operational but threatened. Solid line with alternating amber dash
- **TurkStream:** Russia→Turkey→Southern Europe. Blue gas line
- **East African Crude Oil Pipeline:** Uganda→Tanzania. Under construction, dashed yellow
- **BTC:** Baku-Tbilisi-Ceyhan. Caspian→Mediterranean, operational, solid black
- **Trans-Saharan:** Nigeria→Algeria→Europe. Proposed, dotted grey

## Rightmost Screen Balloon — Energy SITREP

Dark charcoal `#1a1a1a`, thin amber `#d4a017` border. Header: "ENERGY & INFRASTRUCTURE MONITOR" with live ticker (WTI $85.40 · Brent $88.20 · TTF €38.50). Five status lines:

```
🟢 Pipelines: 847,000 km tracked, 3 active disruptions
🟠 Infrastructure: 847 GW offline for maintenance/outage globally
🟠 Fuel Shortages: 14 active events — 4 critical, 10 elevated
🟢 Renewables: 142 GW new capacity under construction
🟠 Mining: Cobalt supply tightening — DRC production down 8% QoQ
```

Generator: `energy_sitrep_kml(status_dict)` in `energy_visuals.py`. Escaped HTML.

## The One Rule

Every energy asset has a physical explanation — pipelines follow valleys, solar farms cluster on sun belts, mines sit where geology put the ore, refineries hug coastlines near deep-water ports. Honor this in every visualization. The geography is the explanation, not the backdrop.

## Verification

- Apache vhost log: lg2 fetches `slave_2.kml` every 3s (HTTP 200)
- Master KML has 20+ styleUrl references across active layers
- `curl -sI http://lg1:81/kml/master.kml` returns 200
- Camera positioned over the energy corridor/region via `/tmp/query.txt`

## Files

- `scripts/energy_visuals.py` — Energy KML generators
- `scripts/energy_run.py` — CLI entry point
- `/home/nara/wm-collector/energy_pipelines_europe.py` — **Verified demo (Aug 2026)**: 7 Russia→Europe pipelines (Nord Stream ghost-grey SABOTAGED, Yamal-Europe sanctioned grey, TurkStream/Blue Stream/Druzhba/Soyuz/Brotherhood operational), 9 compressor stations green/amber/red by status, energy SITREP balloon. Asset status encoding pattern: operational=solid, sanctioned=dashed grey, suspended/sabotaged=ghost grey.
- `/home/nara/wm-collector/energy_solar_me.py` — **Verified demo (Aug 2026)**: 8 Middle East mega solar farms (MBR 5GW, Al Dhafra 2GW, Benban 1.65GW, Sudair 1.5GW, NEOM 3GW planned), 3D capacity columns (height ∝ MW), desert sun belt underlay, gold-header renewable SITREP balloon. 12GW active + 6GW pipeline. 30 KML features, 8 style types.
- `/home/nara/wm-collector/energy_mining_india.py` — **Verified demo (Aug 2026)**: 17 Indian mines across 9 commodities (coal, iron ore, copper, uranium, gold, lithium, rare earths, bauxite, zinc+lead, manganese), 3D columns ∝ production, 2 mineral belts, 5 supply-chain LineStrings mine→processor→port, dark charcoal mining SITREP balloon. 82 Placemark features, 17 style types.
- `/home/nara/wm-collector/collectors/energy_*.py` — Collectors per layer
- **Deployment pattern shared across all demos:** write KML to `/tmp/`, `bash /home/lg/clear-touch.sh` for blank+ETag change, scp to lg1, sudo cp to master.kml + slave_2.kml, fly camera via `/tmp/query.txt`. No relaunch. Same pattern as maritime-awareness, history-educator, and news-storyteller.
- Related: `maritime-awareness` (separate skill), `lg-data-visualization` (framework), `lg-kml-tours` (camera), `armed-conflicts` (separate visual language)

## How to get free API keys

| Source | Registration | Free Tier |
|--------|-------------|-----------|
| EIA | `eia.gov/opendata/` register | 5,000 req/day |
| GIE AGSI+ | `agsi.gie.eu` token request | Unlimited for EU gas |
| IEA | `iea.org` account | 5,000 req/month |
| Yahoo Finance | No key needed | Public chart API |
| Our World in Data | No key needed | Open CSV |
| World Bank | No key needed | Open API |
| Global Energy Monitor | No key needed | Public GeoJSON |
