# NOAA NWS Weather Alerts API

**Endpoint:** `https://api.weather.gov/alerts/active?status=actual&message_type=alert`
**Auth:** None (free, no API key)
**Rate limit:** 30 req/s (per their terms)
**Response format:** GeoJSON FeatureCollection
**Update cadence:** ~2-5 minutes

## Query Parameters

| Param | Values | Notes |
|-------|--------|-------|
| `status` | `actual`, `exercise`, `test`, `draft` | Use `actual` for live alerts |
| `message_type` | `alert`, `update`, `cancel` | Use `alert` for new alerts only |
| `event` | `Tornado Warning`, `Flood Watch`, etc. | Filter by event type |
| `point` | `lat,lon` | Alerts near a point |
| `region` | `AL`,`AK`,...,`WY` | State-based filter |

## Response Structure (GeoJSON)

```json
{
  "features": [{
    "properties": {
      "id": "urn:oid:2.49.0.1.840.0...",
      "event": "Severe Thunderstorm Warning",
      "headline": "...",
      "severity": "Severe",
      "urgency": "Immediate",
      "areaDesc": "County Name",
      "instruction": "Move to safe shelter...",
      "messageType": "Alert"
    },
    "geometry": {
      "type": "Polygon",
      "coordinates": [[[lon,lat],...]]
    }
  }]
}
```

## Severity Levels

| Severity | Color (ABGR) | Sort priority |
|----------|-------------|---------------|
| Extreme | `ff0000ff` | 1 |
| Severe | `ff0055ff` | 2 |
| Moderate | `ff00aaff` | 3 |
| Minor | `ff00ff88` | 4 |
| Unknown | `ffaaaaaa` | 5 |

## Pitfalls

- Geometry can be `Point`, `Polygon`, or `MultiPolygon` — handle all three
- `headline` can be up to 500 chars; truncate for KML descriptions
- Some alerts have no `instruction` field
- Rate limit is generous but respect it — cache results for 5 min
