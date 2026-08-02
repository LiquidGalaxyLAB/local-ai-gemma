---
name: maritime-awareness
description: "Live maritime intelligence layers on Liquid Galaxy."
version: 1.0.0
platforms: [linux]
metadata:
  hermes:
    tags: [maritime, ships, ais, kml, liquid-galaxy, chokepoints, cables, trade-routes]
    related_skills: [lg-data-visualization, lg-kml-tours, lg-ssh-control]
---

# Maritime Domain Awareness

Turns the LG rig into a maritime operations centre. When the user asks about shipping, sea traffic, ocean trade, maritime incidents, chokepoints, or undersea cables, this skill assembles live multi-layer intelligence across all screens. Camera sits at high oblique over the relevant ocean basin — the curvature of Earth and scale of global traffic become immediately felt.

**5 layers, each toggleable:** (1) AIS Density, (2) Trade Routes, (3) Chokepoint Status, (4) Live Tankers, (5) Cable Advisories.

**Key dependency stance:** Python + the `wm-collector` framework (`/home/nara/wm-collector/`). Free open APIs (AISStream, NGA, NOAA). VM-safe KML (escaped HTML, no CDATA, rounded coords). Rightmost screen = floor(N/2)+1.

## When to Use

Trigger phrases:
- "show me global shipping traffic" / "what's happening at the Strait of Hormuz"
- "show live tankers in the Red Sea" / "are there any cable advisories"
- "show AIS density right now" / "visualize global trade routes on the rig"
- "maritime watch" / "what chokepoints are under stress today"
- "show me the busiest shipping lanes" / "is Suez Canal traffic normal"
- "show undersea cable threats" / "full maritime picture on the rig"

**When triggered, extract 3 things:** which layer(s) they want (or full stack), geographic region (global / ocean basin / named chokepoint), live data vs reference/static.

## Prerequisites

- **Pi with `wm-collector` framework** — `run.py` at `/home/nara/wm-collector/run.py`
- **AISStream.io free API key** — register at aisstream.io, free tier ~1000 msg/min. Set as env var `AISSTREAM_KEY`
- **NGA navigational warnings** — no auth (US Gov open data), `msi.nga.mil/api/publications/broadcast-warn?output=json`
- **TeleGeography cable GeoJSON** — publicly downloadable from `github.com/telegeography/...`
- **MarineTraffic / AISHub** — optional secondary v2 source for AIS (free tier: 10 req/min)
- **SSH** to lg1 at 192.168.1.12 (lg/lg), standard deploy pattern

## How to Run

```bash
cd /home/nara/wm-collector
python3 maritime_run.py --layer=ais-density --region=global
python3 maritime_run.py --layer=chokepoints
python3 maritime_run.py --layer=all              # Full stack
python3 maritime_run.py --layer=tankers --region=persian-gulf
python3 maritime_run.py --layer=cables --show-advisories
```

Uses `sshpass` SCP + Python subprocess sudo-cp to lg1. No relaunch — 3s NetworkLink refresh picks up everything.

## Quick Reference

| Layer | Data Source | Update Cadence | Key Endpoint |
|-------|------------|----------------|--------------|
| AIS Density | AISStream.io (websocket) | Live stream | `wss://stream.aisstream.io/v0/stream` |
| Trade Routes | Static GeoJSON (15 lanes) | Static | Bundled reference file |
| Chokepoint Status | NGA MSI + maritime RSS feeds | 30 min | `msi.nga.mil/api/publications/broadcast-warn` |
| Live Tankers | AISStream (filtered type 80-89) | Live stream | same as AIS Density |
| Cable Advisories | TeleGeography + NGA cuts | Daily | TeleGeography cable GeoJSON |

### 9 Tracked Chokepoints

| Chokepoint | Coordinates | Trade Volume |
|-----------|------------|--------------|
| Strait of Hormuz | 26.5N, 56.5E | ~21M barrels/day oil |
| Strait of Malacca | 1.5N, 104.5E | 25% world trade |
| Suez Canal | 30.0N, 32.5E | 12% global trade |
| Bab-el-Mandeb | 12.5N, 43.5E | ~6M barrels/day oil |
| English Channel | 51.0N, 1.5E | ~500 ships/day |
| Danish Straits | 56.0N, 11.0E | Russian oil to Europe |
| Turkish Straits | 41.0N, 29.0E | Caspian oil export |
| Strait of Gibraltar | 36.0N, -5.3W | Atlantic-Med gateway |
| Panama Canal | 9.0N, -79.5W | 6% world trade |

Status colors: green (normal), amber (elevated tension/partial disruption), red (active incident/closure). Extruded overlay polygon glows above the passage.

## Procedure

1. **Extract layer + region from user request.** If they ask about a specific chokepoint ("Hormuz") → Layer 3 only, fly direct, zoom close. If "maritime watch" or "full picture" → all 5 layers stacked.
2. **Build KML layers** using `maritime_visuals.py` generators:
   - Layer 1: hex-grid density polygons with 3D extrusion (short→tall, blue→white by vessel count)
   - Layer 2: 15 trade-route LineStrings with directional arrows, port placemarks with throughput data
   - Layer 3: 9 chokepoint status polygons (green/amber/red), each with a balloon showing status + trade volume + alternative route
   - Layer 4: tanker Placemarks with rotated ship icons, DWT-scaled, loaded/ballast color-coded, 6hr track trails
   - Layer 5: cable LineStrings (dim blue=healthy, red=damaged, amber=elevated risk), landing-station pins, incident rings
3. **Generate the maritime situation report balloon** — dark navy background, cyan border, "MARITIME DOMAIN AWARENESS" header with timestamp, 5 status lines with colored dots.
4. **Deploy** via scp to lg1 → sudo cp to master.kml + slave_2.kml. 3s refresh — **no relaunch**.
5. **Camera:** Global altitude for full stack (8s) → circuit of top 3 stressed chokepoints (5-6s each) → busiest tanker region → active cable incidents → pull back for final wide shot. Total tour 90-120s.
6. **TTS voiceover** narrates the situation report — numbers read from the AIS/tanker/chokepoint status.

## Rightmost Screen Balloon — Maritime SITREP

Dark navy `#0a111f` background, thin cyan `#00aaff` border. Header: "MARITIME DOMAIN AWARENESS" bold white, live timestamp. Five status lines with colored dots:

```
🟢 AIS: 87,000 vessels tracked globally (18:45 UTC)
🟠 Chokepoints: Bab-el-Mandeb AMBER — Houthi advisory active
🟢 Tankers: 6,200 tracked, 14 AIS-dark events in last 24h
🟠 Cables: 2 active advisories — Red Sea cut ongoing
🟢 Trade Routes: Suez volume down 18% vs 30-day average
```

Generator: `maritime_sitrep_kml(status_dict)` in `maritime_visuals.py`. Escaped HTML.

## The One Rule

Every piece of maritime data has a geographic home — never present it as text-only. Even "is Suez traffic normal?" should fly the camera to the Canal, show the chokepoint overlay in its current status color, and let the balloon explain the numbers. The ocean is the medium.

## Verification

- Apache vhost log: lg2 fetches `slave_2.kml` every 3s (HTTP 200)
- Master KML has 25+ styleUrl references across all active layers
- `curl -sI http://lg1:81/kml/master.kml` returns 200
- Camera positioned over the correct ocean basin via `/tmp/query.txt`

## Files

- `scripts/maritime_visuals.py` — Maritime KML generators (ais_density_kml, trade_routes_kml, chokepoints_kml, tanker_kml, cables_kml, maritime_sitrep_kml, style_defs)
- `scripts/maritime_run.py` — CLI entry point (parse layer/region, collect data, build KML, deploy, camera tour)
- `/home/nara/wm-collector/collectors/ships.py` — Existing static maritime config (naval bases, ports, chokepoints)
- `/home/nara/wm-collector/collectors/maritime_live.py` — New collector: AISStream websocket + NGA MSI + TeleGeography cables
- `/home/nara/wm-collector/cables_india.py` — **Verified demo (Aug 2026)**: fetches live TeleGeography cable API (`submarinecablemap.com/api/v3`), filters 25 major international cables to India, generates KML with 7 colored LineString styles + 7 landing station pins (Mumbai, Chennai, Kochi, Trivandrum, Tuticorin, Digha, Port Blair), deploys dark navy SITREP balloon to slave_2.kml. Confirmed working.
- `/home/nara/wm-collector/maritime_europe.py` — **Verified demo (Aug 2026)**: 10 trade routes (cargo-colored: cyan/black/orange), 5 oil tanker flow corridors, 5 European chokepoints (green/amber status diamonds), 7 major ports. Maritime SITREP balloon.
- `references/telegeography-cable-api.md` — TeleGeography API v3 endpoints, response format, India filtering patterns
- Related: `lg-data-visualization` (collector framework, KML rules, dual-source), `lg-kml-tours` (camera control), `armed-conflicts` (separate visual language)

## Data Sources (from World Monitor source code — verified)

| Source | URL | Auth | WM File | Status |
|--------|-----|------|---------|--------|
| AISStream (live vessels) | `wss://stream.aisstream.io/v0/stream` | Free API key (`AISSTREAM_API_KEY`) | `scripts/ais-relay.cjs` | Verified ✓ |
| NGA Maritime Warnings | `https://msi.nga.mil/api/publications/broadcast-warn?output=json&status=A` | None (US Gov) | `server/worldmonitor/maritime/v1/list-navigational-warnings.ts` | Verified ✓ |
| Submarine Cables | TeleGeography public dataset + seed scripts | None (public GeoJSON) | `scripts/seed-submarine-cables.mjs` | Verified ✓ |
| CorridorRisk (chokepoint scoring) | CorridorRisk API | Optional API key (`CORRIDORRISK_API_KEY`) | `server/worldmonitor/supply-chain/v1/_corridorrisk-upstream.ts` | Optional |
| Chokepoint Baselines | Static JSON seeded from PortWatch/IMF | None (pre-seeded) | `scripts/seed-chokepoint-baselines.mjs`, `scripts/seed-portwatch-chokepoints-ref.mjs` | Verified ✓ |
| Chokepoint Flows/History | IMF PortWatch + static snapshots | None (public) | `scripts/seed-chokepoint-flows.mjs`, `docs/snapshots/chokepoint-transit-2026-07.json` | Verified ✓ |

**AISStream relay pattern (from WM):** World Monitor runs a Node.js relay server (`scripts/ais-relay.cjs`) that connects to AISStream's WebSocket, buffers vessel positions in-memory (5-min snapshot cache), and exposes them via HTTP. Our equivalent: a Python collector that calls AISStream, builds density grids, and writes KML. No relay needed — we produce KML directly from the collector.

**How to get free API keys:**
- AISStream: register at `aisstream.io` → free tier ~1000 msg/min
- NGA MSI: no key needed (US Government open data)
- TeleGeography cables: download public GeoJSON from their GitHub
- PortWatch/IMF: register at `portal.api.imf.org` → free tier
