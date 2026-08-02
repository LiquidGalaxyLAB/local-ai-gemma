# TeleGeography Submarine Cable API

**Source:** `https://www.submarinecablemap.com/api/v3/`
**Auth:** None (public, no API key)
**Status:** Verified working (August 2026)

## Endpoints

### Cables (GeoJSON LineStrings)
```
GET https://www.submarinecablemap.com/api/v3/cable/cable-geo.json
```
Returns `FeatureCollection` with MultiLineString geometry per cable. Each feature:
- `properties.id` — slug name (e.g. `asia-africa-europe-1-aae-1`)
- `properties.name` — human name
- `properties.color` — hex color
- `properties.feature_id` — unique per-path segment
- `geometry.coordinates` — array of `[lon, lat]` arrays per cable path

Size: ~737KB (500+ cables globally).

### Landing Points (GeoJSON Points)
```
GET https://www.submarinecablemap.com/api/v3/landing-point/landing-point-geo.json
```
Returns `FeatureCollection` with Point geometry per landing station. Each feature:
- `properties.id` — slug (e.g. `mumbai-india`)
- `properties.name` — human name
- `geometry.coordinates` — `[lon, lat]`

Size: ~360KB (hundreds of stations globally).

## India Filtering

India-relevant cables: ~57. Filter by coordinate proximity (lat 6-25, lon 68-92) or name keywords (india, sea-me-we, imewe, aae, bbg, tata, i2i, eig, falcon, bay of bengal, mumbai, chennai).

India landing points: ~28. Key: mumbai (12 cables), chennai, kochi, trivandrum, tuticorin, digha, port blair.

## Working Implementation

`/home/nara/wm-collector/cables_india.py` — live TeleGeography data filtered to 25 India cables, generates KML with 7 colored LineString styles + 7 landing station pins, deploys maritime balloon to slave_2.kml, camera at 8M km. Verified on rig.
