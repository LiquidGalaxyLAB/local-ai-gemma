# GDACS Disaster Events API

**Endpoint:** `https://www.gdacs.org/gdacsapi/api/events/geteventlist/MAP`
**Auth:** None (free, no API key)
**Rate limit:** Unknown, be conservative (cache 10-30 min)
**Response format:** JSON (GeoJSON-like with `features` array)
**Update cadence:** ~10-30 minutes per event type

## Event Types

| Code | Kind (KML icon) | Description |
|------|-----------------|-------------|
| `EQ` | `earthquake` | Earthquake (magnitude-based) |
| `TC` | `severeStorms` | Tropical Cyclone |
| `FL` | `floods` | Flood |
| `VO` | `volcano` | Volcano |
| `WF` | `wildfire` | Wildfire |
| `DR` | `drought` | Drought |

## Alert Levels

| Level | Color (ABGR) | Scale |
|-------|-------------|-------|
| Red | `ff0000ff` | 1.3 |
| Orange | `ff0066ff` | 1.0 |
| Green | `ff00ff00` | 0.7 |

## Response Fields (per event in `features[].properties`)

| Field | Type | Notes |
|-------|------|-------|
| `eventtype` / `eventType` | string | One of: `EQ`, `TC`, `FL`, `VO`, `WF` |
| `eventid` | string | GDACS internal ID |
| `name` / `title` | string | Human-readable event name |
| `lat` / `latitude` | float | Latitude |
| `lon` / `longitude` | float | Longitude |
| `alertlevel` | string | `Red`, `Orange`, or `Green` |
| `country` | string | Affected country |
| `magnitude` | float | For EQ: Richter; for TC: wind speed |
| `description` | string | Brief description |

## Pitfalls

- Response structure varies slightly — GDACS uses both `features` array format and top-level array
- Field naming is inconsistent: `eventtype` vs `eventType`, `lat` vs `latitude`
- Some events have null `magnitude`
- Cache aggressively — GDACS data refreshes on 10-30 min cycles
- Filter out earthquakes if using the USGS collector (GDACS earthquake data is less detailed)
