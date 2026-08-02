# WorldMonitor Data Source Catalog (Reference)

> Based on analysis of [koala73/worldmonitor](https://github.com/koala73/worldmonitor) (74k+ stars),
> a real-time global intelligence dashboard with 30+ data service domains.
> Their architecture: Railway cron scripts → fetch APIs → Redis cache → server handlers.
>
> This document catalogs their data sources, free/open alternatives for each,
> and notes which we should add next to the WM-LG pipeline.

---

## Already Implemented (We Have These)

| Domain | Our Source | WorldMonitor Source | Notes |
|--------|-----------|-------------------|-------|
| Earthquakes | USGS GeoJSON | USGS GeoJSON (same endpoint) | Identical |
| Natural Events | NASA EONET | NASA EONET + GDACS + NOAA NHC | We have EONET + GDACS; NHC added in weather_v2 |
| Weather Alerts | NOAA NWS + wttr.in | NOAA NWS + Open-Meteo | wttr.in works where Open-Meteo DNS fails |
| Air Traffic | OpenSky Network | OpenSky + Wingbits | Wingbits is a premium alt |
| Military Bases | Static config (37 bases) | Static config (build-military-bases-final.mjs) | Similar approach |
| News | 8 RSS feeds | 10 RSS feeds (BBC, Guardian, NPR, PBS, ABC, CBS, NBC + Google News) | Comparable |
| Airports | Static config (35 airports) | (via aviation domain) | Fine as static |
| Maritime config | Static (India region focus) | NGA navigational warnings + AISStream | See "Should Add" below |

---

## Should Add Next (High Value, Free, Already Proven by WM)

### 1. Conflict Events — ACLED (Free Tier)

**WM source:** `acleddata.com/api/acled/read`  
**Why:** Real-time political violence and protest data worldwide. No existing
conflict layer in our pipeline.  
**Auth:** Free API key (register at acleddata.com)  
**Response:** GeoJSON with event type, fatalities, actors, location  
**Cadence:** Daily updates  
**Endpoints used by WM:**
```
https://acleddata.com/api/acled/read
  ?key={API_KEY}
  &event_date={YYYY-MM-DD}
  &region=8              # Region filter (1=Africa, 6=MiddleEast, 8=SouthAsia)
  &limit=1000
```
**Secondary for this layer:** UCDP (free, no key) via `ucdp.uu.se` or GDELT
(via HDX HAPI — `hapi.humdata.org/api/v2/coordination-context/conflict-events`)

### 2. Wildfire Hotspots — NASA FIRMS

**WM source:** NASA FIRMS via VIIRS satellite data  
**Why:** Live satellite fire detection at 375m resolution. Much more accurate
than the event-based EONET data.  
**Auth:** Free NASA Earthdata login (api key)  
**Endpoint:**
```
https://firms.modaps.eosdis.nasa.gov/api/area/csv/{API_KEY}
  ?source=VIIRS_SNPP_NRT
  &dayRange=1
  &area=bbox
```
**Response:** CSV with lat/lon, brightness, confidence, satellite  
**Cadence:** Real-time (satellite overpass ~2hr refresh)

### 3. Ship Tracking — AISStream

**WM source:** AISStream websocket relay (`aisstream.io`)  
**Why:** Our ships.py is static config only — no live vessel positions  
**Auth:** Free API key (aisstream.io, free tier ~1000 msg/min)  
**Endpoint:** WebSocket `wss://stream.aisstream.io/v0/stream`  
**Response:** JSON with MMSI, lat/lon, heading, speed, vessel type  
**Cadence:** Real-time (live stream)  
**Alternative for REST:** MarineTraffic (free tier, 10 req/min) or VesselFinder

### 4. Navigational Warnings — NGA MSI

**WM source:** `msi.nga.mil/api/publications/broadcast-warn`  
**Why:** US government maritime hazard warnings — real-time NAVAREA broadcasts  
**Auth:** None (US Gov open data)  
**Response:** JSON with warning text, area polygon, effective dates  
**We already verified:** This endpoint is responsive and well-structured

### 5. Radiation Monitoring — Safecast

**WM source:** `api.safecast.org/measurements.json`  
**Why:** Global crowd-sourced radiation measurements — unique data layer  
**Auth:** None (open data)  
**Endpoint:**
```
https://api.safecast.org/measurements.json
  ?latitude=35&longitude=140&distance=50&limit=100
```
**Response:** JSON with lat/lon, value (cpm), unit, device type  
**Cadence:** Variable (crowd-sourced, ~daily for most regions)

---

## Medium Priority (Good to Have)

| Domain | Best Free Source | WM Equivalent | Effort |
|--------|-----------------|---------------|--------|
| GPS Jamming | `gpsjam.org/data/manifest.csv` (H3 hex CSVs, no auth, no quota — restored by WM from Wingbits) | WM `fetch-gpsjam.mjs` — daily H3 res-4 hex cells, columns `hex,count_good_aircraft,count_bad_aircraft` | Low — single manifest + CSV fetch |
| Humanitarian Displacement | `hapi.humdata.org/api/v2` (HDX) | HDX HAPI | Low — UN OCHA open data |
| Tropical Cyclones | `www.nhc.noaa.gov/CurrentStorms.json` | NOAA NHC | Already tested and working |
| Thermal Escalation | VIIRS thermal satellite (via FIRMS) | WM has dedicated thermal domain | Medium — needs threshold logic |
| Webcams | webcam aggregator APIs | WM has webcam domain | Medium — needs image overlay |
| Cyber Threats | Shodan/Censys (free tiers) | WM has cyber domain via Cloudflare Radar + GreyNoise — already verified | Medium — needs keys |
| Consumer Prices | Numbeo (free tier) | Numbeo + BLS | Low — static snapshots |
| Defense Patents | USPTO / patent databases | WM has defense-patents domain | Low — not geo-relevant |
| Earth Imagery | Mapbox / Sentinel Hub | WM has imagery domain | Low — needs key |
| **Energy Pipelines** | **Global Energy Monitor public GeoJSON (no key)** | **WM `seed-pipelines-gas.mjs`, `seed-pipelines-oil.mjs`** | **Low — static GeoJSON** |
| **Energy Storage / Shortages** | **GIE AGSI+ (`agsi.gie.eu/api`, free token) + IEA (`api.iea.org`, free)** | **WM `seed-gie-gas-storage.mjs`, `seed-iea-oil-stocks.mjs`** | **Medium — free tokens** |
| **Energy Mix** | **Our World in Data (`owid-public.owid.io/data/energy/owid-energy-data.csv`, open CSV)** | **WM `seed-owid-energy-mix.mjs`** | **Low — single CSV** |
| **Commodity Quotes** | **Yahoo Finance (`query1.finance.yahoo.com/v8/finance/chart/CL=F`, no key)** | **WM `seed-commodity-quotes.mjs` — CL=F (WTI), BZ=F (Brent), TTF=F (gas)** | **Low — public endpoint** |
| **Internet Outages** | **Cloudflare Radar (`api.cloudflare.com/client/v4/radar/annotations/outages`, free CF token)** | **WM `seed-internet-outages.mjs`** | **Low — free account** |
| **BGP Routing** | **Cloudflare Radar BGP + RIPE RIS Live (`ris-live.ripe.net`, open)** | **WM `seed-bgp.mjs`** | **Low — open** |

---

## WM Architecture Patterns Worth Adopting

### Seed-Cache Pattern
WM runs seed scripts on Railway (cron) that fetch from external APIs and
write to Redis. Their server handlers read from cache only — never call
external APIs at request time. This:
- Absorbs API rate limits (seed retries with backoff)
- Provides consistent response timing
- Survives upstream API outages (stale cache serves while seed retries)

**Our equivalent:** Pi cron job calling `run.py` — same pattern,
simpler infrastructure.

### Dual-Source Conflict Verification
WM's conflict domain simultaneously sources from:
1. **ACLED** (API key, high-frequency, event-level data)
2. **UCDP** (free, lower frequency, academic-grade)
3. **GDELT** (free, global, noisier)
4. **HDX HAPI** (free, UN humanitarian data)

This mirrors our dual-source approach but with 4 sources instead of 2.

### Classifier Pipeline
WM's news domain has a dedicated classifier (`_classifier.ts`) that
categorizes articles by topic, region, and significance before serving.
Our current approach uses simple keyword → emoji mapping. A classifier
would be a significant upgrade but requires either an LLM call or a
trained model.

---

## Direct API URLs from WM Code (Verified Working)

| Source | URL | Auth | Works on Pi? |
|--------|-----|------|-------------|
| USGS Earthquakes | `earthquake.usgs.gov/.../4.5_week.geojson` | None | ✅ |
| NASA EONET | `eonet.gsfc.nasa.gov/api/v3/events` | None | ✅ |
| GDACS | `gdacs.org/gdacsapi/api/events/geteventlist/MAP` | None | ✅ |
| NOAA NWS | `api.weather.gov/alerts/active` | None | ✅ |
| OpenSky | `opensky-network.org/api/states/all` | None (free tier) | ✅ |
| NOAA NHC | `www.nhc.noaa.gov/CurrentStorms.json` | None | ✅ |
| NGA Navigational Warnings | `msi.nga.mil/api/publications/broadcast-warn?output=json` | None | ✅ |
| Wikipedia API | `en.wikipedia.org/w/api.php?action=parse&page=Portal:Current_events` | None | ✅ |
| wttr.in | `wttr.in/~lat/lon?format=j1` | None | ✅ |
| Safecast | `api.safecast.org/measurements.json` | None | ✅ |
| HDX HAPI | `hapi.humdata.org/api/v2/coordination-context/conflict-events` | None | ✅ |
| GPSJam | `api.gpsjam.org/api/v1/daily` | None | ✅ |
| GPSJam | `gpsjam.org/data/manifest.csv` + `{date}-h3_4.csv` | None | ✅ |
| Cloudflare Radar (outages) | `api.cloudflare.com/client/v4/radar/annotations/outages` | Free CF API token | ✅ |
| Cloudflare Radar (BGP) | `api.cloudflare.com/client/v4/radar/bgp` | Free CF API token | ✅ |
| GreyNoise Community | `api.greynoise.io/v3` | Free tier (50/day) | ✅ |
| Yahoo Finance Commodities | `query1.finance.yahoo.com/v8/finance/chart/CL=F` | None | ✅ |
| GIE AGSI+ (EU gas storage) | `agsi.gie.eu/api` | Free token | ✅ |
| IEA Oil Stocks | `api.iea.org/netimports/latest` | Free account | ✅ |
| Our World in Data Energy | `owid-public.owid.io/data/energy/owid-energy-data.csv` | None | ✅ |
| Open-Meteo | `api.open-meteo.com/v1/forecast` | None | ❌ DNS fails |

**DNS Note:** `open-meteo.com` does NOT resolve on this Pi's network.
All other sources work. If a future user needs Open-Meteo, they'll need
to fix DNS or use a proxy.
