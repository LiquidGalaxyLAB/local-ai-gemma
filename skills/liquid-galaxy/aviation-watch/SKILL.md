---
name: aviation-watch
description: "Live air traffic and military flights on Liquid Galaxy."
version: 1.0.0
platforms: [linux]
metadata:
  hermes:
    tags: [aviation, flights, military, ads-b, opensky, notam, kml, liquid-galaxy]
    related_skills: [lg-data-visualization, lg-kml-tours, lg-ssh-control, cyber-infrastructure]
---

# Live Aviation Watch

Turns the LG rig into an air traffic operations center. Covers live civilian traffic, military flights, NOTAMs/airspace restrictions, flight delays, and airport status across 4 layers. Aircraft exist in a vertical stack — altitude is the third dimension, and the rig's 3D rendering makes it visible. Aesthetic: radar scope meets glass cockpit — dark background, green/amber operational colors, red for military.

**4 layers, each toggleable:** (1) Military Flights, (2) Flight Delays, (3) NOTAM Rings, (4) Airport Status.

**Key dependency stance:** Python + `wm-collector` framework. Free APIs (OpenSky, ADS-B Exchange, FAA NOTAM). VM-safe KML. Rightmost screen = floor(N/2)+1.

## When to Use

Trigger phrases:
- "show me live air traffic over Europe" / "are there any military flights I should know about"
- "show me flight delays right now" / "what NOTAMs are active over the Middle East"
- "show me airport status globally" / "aviation watch on the rig"
- "full airspace picture" / "show me military activity over the Baltic"
- "which airports have ground stops right now" / "show me restricted airspace"
- "any interesting military movements today" / "show me air traffic over the US"
- "which flights are delayed the most today" / "show me active NOTAMs near conflict zones"
- "show me the busiest airports right now" / "is there any airspace closure"

**Extract 3 anchors:** layer(s) / region / live vs reference.

## Data Sources (from World Monitor source code — verified free)

| Source | URL | Auth | WM File |
|--------|-----|------|---------|
| OpenSky Network (civilian ADS-B) | `opensky-network.org/api/states/all` | Free (anonymous tier) | `api/opensky.js` |
| ADS-B Exchange (unfiltered incl. military) | `adsbexchange.com` | Free tier | Referenced in WM docs |
| AviationStack (flight status, delays) | `aviationstack.com` | Free key (`AVIATIONSTACK_API`) | `scripts/seed-aviation-stack.mjs` |
| Wingbits (aircraft enrichment) | Wingbits API | Free contact required | `.env.example` (`WINGBITS_API_KEY`) |
| FAA NOTAM API | `notams.aim.faa.gov` | None (US Gov) | `scripts/seed-notam.mjs` |
| ICAO NOTAM | `applications.icao.int` | Free key (`ICAO_API_KEY`) | `.env.example` |
| MIRTA (military installations) | `geospatial-usace.opendata.arcgis.com` | None (US Gov) | `scripts/fetch-mirta-bases.mjs` |
| OurAirports (airport geometry) | `ourairports.com/data/airports.csv` | None (open CSV) | Referenced in WM docs |

## How to Run

```bash
cd /home/nara/wm-collector
python3 aviation_run.py --layer=military --region=baltic
python3 aviation_run.py --layer=delays --region=global
python3 aviation_run.py --layer=notams --region=middle-east
python3 aviation_run.py --layer=airports --region=europe
python3 aviation_run.py --layer=all              # Full aviation stack
```

## Quick Reference

| Layer | Data Source | Update Cadence | Key Endpoint |
|-------|------------|----------------|--------------|
| Military Flights | ADS-B Exchange + OpenSky filter | 10 sec (live) | `adsbexchange.com` API |
| Flight Delays | AviationStack + FlightAware | 5 min | `aviationstack.com` |
| NOTAM Rings | FAA + ICAO + EUROCONTROL | 30 min | `notams.aim.faa.gov` |
| Airport Status | ATIS + Eurocontrol + OurAirports | 10 min | `ourairports.com` + METAR |

## Procedure

1. **Extract layer + region from user request.** If "aviation watch" → full 4-layer stack. If "military over Baltic" → Layer 1, Baltic region. If "ground stops globally" → Layer 4, global.
2. **Build KML layers** using `aviation_visuals.py`:
   - Layer 1: military aircraft Placemarks with rotated heading icons, branch-colored (dark blue=USAF, red=Russian, navy=USN), 30-min track trails as dotted lines, reconnaissance/ISR range rings, ghost markers for transponder-off aircraft, balloon with callsign/type/origin/context
   - Layer 2: airport delay columns (height=departures, color=avg delay), disrupted-flight LineString arcs (red=delayed 90m+, dashed=broken arcs for cancelled), propagation-risk amber arcs for next 3hr
   - Layer 3: NOTAM cylinder polygons (solid=security TFR, orange=hazard, blue=VIP, yellow=disaster), extruded to actual ceiling altitude; navigation hazard outline rings; military activation filled polygons; GPS NOTAM hatched overlays; conflict-zone special treatment with deep red + warning border + historical context
   - Layer 4: airport runway icons scaled by passenger volume, colored by status (green=normal, yellow=GDP, orange=ground stop, red=partial closure, black+X=full closure), extruded pulsing cylinder for disrupted hubs, runway layout diagrams at high zoom, conflict-zone advisory overlays
3. **Generate ATC radar-scope PNG panel** — pure black `#000000`, green text, amber caution, red emergencies. "AVIATION WATCH" header with UTC Zulu timestamp. 4 status lines (TRAFFIC/MILITARY/DELAYS/AIRSPACE). Flight-strip feed: top 10 significant events + emergency squawk alerts (7700/7600/7500).
4. **Deploy** via scp to lg1 → sudo cp to master.kml + slave_2.kml + PNG. 3s refresh — **no relaunch**.
5. **Camera:** Global altitude for full stack (10s — density heatmap + NOTAM rings + airport status) → top 3 military tracks → busiest airport disruption → pull back. Total tour 90-120s.

## Military Aircraft — Known Callsign Patterns

| Callsign Pattern | Country | Operator | Typical Mission |
|-----------------|---------|----------|----------------|
| RCH#### | USA | USAF | Strategic airlift (C-17, C-5) |
| TOPCAT# | USA | USAF | Aerial refueling (KC-135, KC-46) |
| FORTE## | UK | RAF | Various — Typhoon, F-35 |
| COBRA## | USA | USAF | ISR / reconnaissance |
| IVAN## | Russia | RuAF | Various military |
| SU#### | Russia | RuAF | Sukhoi fighters |
| PLF### | Poland | Polish AF | Military transport |

## Rightmost Screen — ATC Radar Scope

Pure black, green text, amber caution, red emergencies:

```
┌──────────────────────────────────────────┐
│ AVIATION WATCH  ⏱ 18:45Z                │
├──────────────────────────────────────────┤
│ TRAFFIC: 94,200 airborne — Atlantic 847  │
│ MILITARY: 23 tracked — 4 ISR, 8 tanker  │
│ DELAYS: 14 GDP airports — ATL 45m avg   │
│ AIRSPACE: 847 NOTAMs — 3 conflict zones │
├──────────────────────────────────────────┤
│ 🔴 18:42 UAL123 squawk 7700 EMERGENCY    │
│ 🔵 18:38 RCH456 KC-135 Baltic orbit      │
│ 🟠 18:35 ATL ground stop — TSTM WX      │
│ 🟡 18:31 GPS NOTAM Eastern Med           │
└──────────────────────────────────────────┘
```

Generator: `aviation_sitrep_png()` via Pillow. ScreenOverlay PNG (always visible).

## The One Rule

Every aircraft in the sky is the outcome of a regulatory permission, a fuel calculation, a crew schedule, and a political decision. A military aircraft 50km from a conflict border is not just a dot — show its altitude, its track history, its sensor range, and its operational context. Make the viewer understand the sky as managed, contested, congested infrastructure.

## Verification

- OpenSky: `curl "https://opensky-network.org/api/states/all"` returns JSON with states array
- ADS-B Exchange: `curl` returns unfiltered aircraft including military hex codes
- Master KML has 15+ styleUrl references across layers
- lg2 fetches `slave_2.kml` + PNG every 3s

## VM Earth 7.3.3 Icon & Rendering Rules (verified Aug 2026)

**Icons — what renders and what doesn't:**
- `maps.google.com/mapfiles/kml/paddle/ylw-circle.png` ✓ always renders
- `maps.google.com/mapfiles/kml/paddle/blu-circle.png` ✓ always renders
- `maps.google.com/mapfiles/kml/paddle/red-circle.png` ✓ always renders
- `maps.google.com/mapfiles/kml/paddle/grn-circle.png` ✓ always renders
- `maps.google.com/mapfiles/kml/paddle/ltblu-circle.png` ✓ always renders
- `maps.google.com/mapfiles/kml/shapes/air.png` ✗ **returns 404 — do NOT use for aircraft**
- `maps.google.com/mapfiles/kml/shapes/fire_station.png` ✗ **returns 404**
- `maps.google.com/mapfiles/kml/shapes/shaded_dot.png` ✗ **returns 404**

**Shared styles required:** Define heading-bucket `<Style>` elements in `<Document>`, reference via `<styleUrl>#hdg_90`. Inline `<Style>` blocks inside `<Placemark>` are unreliable on the VM. Group aircraft by heading bucket (every 10°) to minimize KML size — the Canada demo used 36 buckets for 571 aircraft.

**`<heading>` rotation inside `<IconStyle>` works** with paddle icons — aircraft icons point in their actual flight direction.

**Rightmost screen:** Use the proven ScreenOverlay → PNG pattern (Pillow-generated, dark theme). `gx:balloonVisibility` and HTML ScreenOverlays do NOT work on this VM. PNG is the only reliable always-visible pattern.

**Deploy pattern:** SCP KML + PNG to lg1, `subprocess.run(['sudo','-S','cp',...], input=b'lg\n')` to `/var/www/html/kml/`, then `sudo touch` to force ETag change → 3s refresh.

## Files

- `scripts/aviation_visuals.py` — KML generators (military_aircraft_kml, delay_network_kml, notam_cylinder_kml, airport_status_kml, radar_panel_png)
- `scripts/aviation_run.py` — CLI entry point
- `/home/nara/wm-collector/collectors/air_traffic.py` — Existing OpenSky collector
- `/home/nara/wm-collector/collectors/airports.py` — Existing static airport config (35 airports)
- Related: `lg-data-visualization` (framework), `cyber-infrastructure` (GPS jamming cross-reference)

## How to get free API keys

| Source | Registration | Free Tier |
|--------|-------------|-----------|
| OpenSky | `opensky-network.org` → create account | 400 req/day anonymous, 4000/day registered |
| ADS-B Exchange | `adsbexchange.com` → RapidAPI | 2000 req/month |
| AviationStack | `aviationstack.com` | 500 req/month |
| FAA NOTAM | No key needed | US Gov open data |
| OurAirports | No key needed | Open CSV download |
