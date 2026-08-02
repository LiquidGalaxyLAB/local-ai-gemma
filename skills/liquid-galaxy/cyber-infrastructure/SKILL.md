---
name: cyber-infrastructure
description: "Live internet outage and cyber threat layers on Liquid Galaxy."
version: 1.0.0
platforms: [linux]
metadata:
  hermes:
    tags: [cyber, internet, outages, gps, jamming, bgp, ddos, kml, liquid-galaxy]
    related_skills: [maritime-awareness, lg-data-visualization, lg-kml-tours, armed-conflicts]
---

# Cyber & Undersea Infrastructure Monitor

Turns the LG rig into a cyber operations center — the kind of display you would see in a national CERT or NOC. Covers internet outages, GPS jamming, cyber threats (DDoS/ransomware/BGP), and BGP routing anomalies across 3 live layers. Camera defaults high-global → descends into specific threat regions. Dark aesthetic: deep blacks, electric blues, sharp neon accents — network topology map, not geographic reference.

**3 layers, each toggleable:** (1) Internet Outages, (2) GPS Jamming, (3) Cyber Threats.

**Note: Undersea cables belong to the `maritime-awareness` skill** (Layer 5: Cable Advisories). This skill references that layer but does not duplicate it. For cable queries, load maritime-awareness.

**Key dependency stance:** Python + `wm-collector` framework. Free open APIs (Cloudflare Radar, GPSJam.org, Shodan/GreyNoise free tiers). VM-safe KML (escaped HTML, no CDATA, coords rounded to 4 decimals). Rightmost screen = floor(N/2)+1.

## When to Use

Trigger phrases:
- "show me internet outages right now" / "is there GPS jamming happening anywhere"
- "show me active cyber threats on the rig" / "are there any BGP hijacks today"
- "show me the global internet infrastructure" / "cyber watch on the rig"
- "full cyber picture" / "where is GPS being jammed"
- "show me DDoS attacks happening now" / "which countries are under cyberattack right now"
- "show internet disruptions by country" / "show me the digital choke points"

**Extract 3 anchors:** layer(s) wanted / region / live vs reference.

**Undersea cable queries → load `maritime-awareness` instead** (cable network is already fully covered there).

## Data Sources (from World Monitor source code — verified free)

| Source | URL | Auth | WM File |
|--------|-----|------|---------|
| Cloudflare Radar (outages) | `api.cloudflare.com/client/v4/radar/annotations/outages` | Free CF account (`CLOUDFLARE_API_TOKEN`) | `scripts/seed-internet-outages.mjs` |
| GPSJam.org (GNSS interference) | `gpsjam.org/data/manifest.csv` + `{date}-h3_4.csv` | **None** (free, no key, no quota) | `scripts/fetch-gpsjam.mjs` |
| Cloudflare Radar (BGP) | `api.cloudflare.com/client/v4/radar/bgp` | Same CF token | `scripts/seed-bgp.mjs` |
| GreyNoise (scan traffic) | `api.greynoise.io/v3` | Free community tier | `scripts/seed-cyber.mjs` |
| PeeringDB (IXP data) | `peeringdb.com/api` | None (open) | Referenced in WM docs |
| RIPE RIS (BGP routing) | `ris-live.ripe.net` | None (open) | Referenced in WM docs |

**World Monitor tracks 31 data sources including cyber/GPS/outages** — all verified working by the 77k-star project. Data source health monitor at `docs/DATA_SOURCES.md`.

## How to Run

```bash
cd /home/nara/wm-collector
python3 cyber_run.py --layer=outages --region=global
python3 cyber_run.py --layer=gps-jamming
python3 cyber_run.py --layer=cyber-threats
python3 cyber_run.py --layer=all              # Full cyber stack
python3 cyber_run.py --layer=all --region=eastern-mediterranean
```

Uses `sshpass` SCP + Python subprocess sudo-cp to lg1. No relaunch — 3s NetworkLink refresh.

## Quick Reference

| Layer | Data Source | Update Cadence | Key Endpoint |
|-------|------------|----------------|--------------|
| Internet Outages | Cloudflare Radar | 5-15 min | `api.cloudflare.com/client/v4/radar/annotations/outages` |
| GPS Jamming | GPSJam.org | Daily (new data each day) | `gpsjam.org/data/manifest.csv` + H3 hex CSVs |
| Cyber Threats | GreyNoise + BGP streams | 5-15 min | `api.greynoise.io/v3` (free tier) |

## Procedure

1. **Extract layer + region from user request.** If "cyber watch" → full 3-layer stack. If "show internet outages in Iran" → Layer 1, Iran region. If "GPS jamming Eastern Med" → Layer 2, Eastern Mediterranean.
2. **Build KML layers** using `cyber_visuals.py` generators:
   - Layer 1: outage Polygon overlays (deep red for shutdowns, amber for cable-caused, blue for provider failures), BGP hijack LineString arcs (blue=correct route, red=hijacked route), provider outage pulsing circles scaled by impact radius
   - Layer 2: GPS jamming H3 hex grid polygons (pale yellow→orange→red by intensity), persistent zone highlights (Eastern Med, Baltic, Black Sea, Korean Peninsula), aircraft-track anomaly markers as yellow triangle icons
   - Layer 3: DDoS burst arcs (thin electric red lines converging on target), ransomware Placemarks with slow-pulse icons, scanning heatmap (pale blue→cyan→white per country), threat-actor context balloons, global attack flow map (top 20 source→target arcs)
3. **Generate cyber SITREP balloon** — pure black `#000000`, thin electric blue `#00aaff` border, monospace font, "CYBER & INFRASTRUCTURE WATCH" header with UTC timestamp, 4 status lines (Internet/GPS/Cyber/Cables), SIEM-style scrolling event feed (last 20 events cycling timestamp+type+location+severity).
4. **Deploy** via scp to lg1 → sudo cp to master.kml + slave_2.kml. 3s refresh — **no relaunch**.
5. **Camera:** Global altitude for full stack (10s — cable web + outage zones + jamming + attack arcs visible simultaneously) → top 3 most severe events (8-10s each) → 3+ layers → pull back global. Total tour 90-120s.

## The Rightmost Screen Balloon — Cyber SITREP

Pure black, electric blue border, monospace font (terminal/NOC aesthetic), UTC timestamp:

```
┌──────────────────────────────────────────┐
│ CYBER & INFRASTRUCTURE WATCH  ⏱ 18:45Z  │
├──────────────────────────────────────────┤
│ 🟢 Internet: 23 active outages —        │
│    3 shutdowns, 8 provider, 12 cable    │
│ 🟡 GPS: E Med SEVERE, Baltic MODERATE,  │
│    Black Sea ELEVATED — 3 active zones  │
│ 🟠 Cyber: 847 DDoS/hr — top targets:    │
│    Ukraine gov, Taiwan fin, Poland grid │
│ 🟢 Cables: 2 active cuts — Red Sea ETA  │
│    18d, SE Asia ETA 6d (see maritime)   │
├──────────────────────────────────────────┤
│ 18:42 DDoS · Ukraine · Finance · HIGH   │
│ 18:38 BGP · SE Asia · Route leak · MED  │
│ 18:35 Ransom · US · Healthcare · CRIT   │
│ 18:31 Scan · DE · Recon · LOW           │
└──────────────────────────────────────────┘
```

Generator: `cyber_sitrep_kml(status_dict)` in `cyber_visuals.py`. Escaped HTML, pure black bg `#000000`, monospace, all fields word-wrapped.

## GPS Jamming — Persistent Zones

Four permanent highlight zones (special balloon treatment):

| Zone | Center | Status | Aircraft Affected | Likely Source |
|------|--------|--------|-------------------|---------------|
| Eastern Mediterranean | 35N, 33E | SEVERE | ~1,500 flights/day | Syria/Russia EW |
| Baltic Sea | 57N, 20E | MODERATE | ~800 flights/day | Kaliningrad |
| Black Sea | 44N, 33E | ELEVATED | ~500 flights/day (spoofing) | Crimea |
| Korean Peninsula | 38N, 127E | INTERMITTENT | ~300 flights/day | DPRK border |

GPSJam data format: H3 res-4 hex cells, columns `hex,count_good_aircraft,count_bad_aircraft`. Metric: `pct = bad/total`. Low <2%, Medium 2-10%, High >10%. Daily updates, no auth, no quota.

## Outage Classification (Before KML Generation)

| Type | Polygon Color | Example | Balloon Fields |
|------|--------------|---------|----------------|
| National Shutdown | Deep Red `#cc0000` | Government-ordered blackout | Country, % loss, population, start/duration, cause, precedent |
| Provider Outage | Amber `#ff8800` | AWS us-east-1 down | Provider, services, affected area, ETA |
| Cable-Cut Outage | Cyan `#00aacc` | Red Sea cable cut | Cable name, repair ETA, countries affected, alt routing |
| BGP Hijack | Red/Blue arcs | Route leak → wrong AS | Origin/destination/hijacker AS, duration, accidental vs deliberate |

## The One Rule

Resist Hollywood hacker aesthetics. Every arc must represent a real traffic flow between real geographic endpoints. Every polygon must cover the real affected GPS grid cell. Every icon must sit at real facility coordinates. No random glowing arcs, no spinning globes, no meaningless cascading numbers. The real data creates the drama — GPSJamming in the Eastern Med affecting 1,500 flights daily is dramatic enough without embellishment. Let geography anchor the invisible.

## Verification

- Apache vhost log: lg2 fetches `slave_2.kml` (200) every 3s
- Master KML has 15+ styleUrl references across active layers
- `curl -sI http://lg1:81/kml/master.kml` returns 200
- Camera at high global → descends to threat zones via `/tmp/query.txt`

## Files

- `scripts/cyber_visuals.py` — Cyber KML generators (outage_kml, gpsjam_kml, ddos_arc_kml, ransomware_kml, bgp_hijack_kml, scan_heatmap_kml, cyber_sitrep_kml)
- `scripts/cyber_run.py` — CLI entry point
- `/home/nara/wm-collector/cyber_ukraine_russia.py` — **Verified demo (Aug 2026)**: Russia-Ukraine internet blockages — 7 outage zones (3 persistent shutdowns, 1 active, 2 regional, 1 allied), 6 IXP nodes, 2 BGP arcs, pure-black+electric-blue monospace cyber SITREP balloon. Outage classification by type+status.
- `/home/nara/wm-collector/collectors/cyber_*.py` — Collectors per layer
- Related: `maritime-awareness` (cables — do NOT duplicate), `lg-data-visualization` (framework), `lg-kml-tours` (camera)

## How to get free API keys

| Source | Registration | Free Tier |
|--------|-------------|-----------|
| Cloudflare Radar | `dash.cloudflare.com` → API tokens → Radar:Read | Unlimited for outages/BGP |
| GPSJam.org | No key needed | Unlimited, daily CSV |
| GreyNoise | `greynoise.io` → Community | 50 req/day |
| PeeringDB | No key needed | Open API |
| RIPE RIS Live | No key needed | Open BGP stream |
| IPinfo | `ipinfo.io` → free | 50k req/month |
