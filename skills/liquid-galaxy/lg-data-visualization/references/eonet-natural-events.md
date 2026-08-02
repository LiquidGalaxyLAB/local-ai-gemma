# NASA EONET Natural Events API → LG KML

## API Endpoint

```
GET https://eonet.gsfc.nasa.gov/api/v3/events?status=open&days=7
```

- Returns all currently-active natural events globally
- No API key required (free, open NASA API)
- Update cadence: ~15-30 minutes (NASA batch process)
- Query params: `status=open` (active events), `days=N` (lookback window)
- Headers: `User-Agent: <app-name>/1.0`, `Accept: application/json`

## Response Format

```json
{
  "events": [{
    "id": "EONET_1234",
    "title": "Wildfire - California",
    "categories": [{"id": "wildfires", "title": "Wildfires"}],
    "sources": [{"id": "GDACS", "url": "https://gdacs.org/..."}],
    "geometry": [
      {
        "date": "2026-07-01T12:00:00Z",
        "type": "Point",
        "coordinates": [-119.5, 37.2]
      }
    ]
  }]
}
```

`coordinates` = `[longitude, latitude]` — GeoJSON order (lon first).

## Category Mapping

| EONET Category | ABGR Color | Emoji | Scale |
|----------------|-----------|-------|-------|
| wildfires | `ffff6600` (orange) | 🔥 | 1.0 |
| severeStorms | `ff00aaff` (cyan) | 🌀 | 1.0 |
| floods | `ff0000ff` (blue) | 🌊 | 0.9 |
| volcanoes | `ffff0000` (red) | 🌋 | 1.2 |
| earthquakes | skip — dedicated collector | — | — |
| landslides | `ff996633` (brown) | ⛰️ | 0.8 |
| drought | `ffff8800` (amber) | ☀️ | 0.7 |
| dustHaze | `ffcccccc` (grey) | 🌫️ | 0.7 |
| snow | `ffffffff` (white) | ❄️ | 0.7 |
| tempExtremes | `ffff0088` (pink) | 🌡️ | 0.8 |
| seaLakeIce | `ff88ffff` (light blue) | 🧊 | 0.7 |
| waterColor | `ff00ff88` (teal) | 🦠 | 0.7 |
| manmade | `ffff00ff` (magenta) | ⚠️ | 0.7 |

## Filtering Rules

- **Wildfires**: drop events older than 48 hours (they pile up)
- **Earthquakes**: skip (handled by USGS collector)
- **Geometry**: use **last** entry (most recent position), skip non-Point types
