# Dual-Source API Reference

## EMSC Earthquakes (earthquakes_v2.py)

**Base URL:** `https://www.seismicportal.eu/fdsnws/event/1/query`

**Auth:** None  
**Rate limit:** Generous (200+ results per query)  
**Endpoint pattern:**
```
https://www.seismicportal.eu/fdsnws/event/1/query
  ?format=json          # REQUIRED — NOT 'geojson' (returns 400)
  &minmag=2.5           # Minimum magnitude
  &limit=200            # Max results
```

**Response shape (FDSN JSON):**
```json
{
  "features": [
    {
      "geometry": {
        "type": "Point",
        "coordinates": [lon, lat, depth]
      },
      "properties": {
        "mag": 3.6,
        "time": "2026-07-22T17:20:52.315Z",  // ISO string, NOT Unix ms
        "flynn_region": "NEVADA",             // Place name field
        "depth": 9.4,
        "source_catalog": "EMSC-RTS",
        "evtype": "ke"
      }
    }
  ]
}
```

**Gotchas:**
- `format=json` works; `format=geojson` returns HTTP 400
- `time` is an ISO 8601 string, NOT a Unix epoch millisecond (USGS format)
- Place name is in `flynn_region`, NOT `place` (USGS) or `fly_from_place`
- Coordinates come from standard GeoJSON `geometry.coordinates` (same as USGS)
- EMSC has better European/Mediterranean coverage than USGS but weaker
  global coverage — expect fewer Middle East/Africa events at same magnitude
- FDSN spec uses `minmagnitude` as standard param but seismicportal accepts `minmag`

---

## wttr.in Weather (weather_v2.py)

**Base URL:** `https://wttr.in/~{lat}{N/S}/{lon}{E/W}?format=j1`

**Auth:** None  
**Rate limit:** Very generous (public service)  
**Endpoint pattern:**
```
https://wttr.in/~26.0N/48.0E?format=j1   # Positive latitude = N north
https://wttr.in/~33.0S/71.0W?format=j1   # Negative = S south (pass absolute)
```

**Response shape:**
```json
{
  "current_condition": [
    {
      "weatherCode": 113,       // WMO weather code
      "temp_C": "32",
      "FeelsLikeC": "35",
      "humidity": "45",
      "windspeedKmph": "15",
      "weatherDesc": [{"value": "Sunny"}]
    }
  ],
  "nearest_area": [
    {
      "areaName": [{"value": "Riyadh"}],
      "country": [{"value": "Saudi Arabia"}]
    }
  ]
}
```

**WMO Weather Code → Alert Mapping (in code):**
| Code | Condition | Severity |
|------|-----------|----------|
| 0-3 | Clear to cloudy | none (skip) |
| 45, 48 | Fog | minor |
| 51, 53, 55, 56, 57 | Drizzle | minor |
| 61, 63, 65, 66, 67 | Rain | moderate |
| 71, 73, 75, 77 | Snow | moderate |
| 80, 81, 82 | Rain showers | moderate |
| 85, 86 | Snow showers | moderate |
| 95 | Thunderstorm | severe |
| 96, 99 | Thunderstorm + hail | extreme |

**Gotchas:**
- NOT a weather alert API — it reports current conditions, not active warnings
- Used as a rough cross-check against NOAA NWS (which is US-only)
- Coordinates use `~26.0N/48.0E` format; for negative lon use `~26.0N/48.0W`
- Rate limit is generous but avoid sub-minute polling
- Returns JSON only with `format=j1`; default is ANSI-colored terminal output
- Some locations may have `nearest_area[0]` empty — handle gracefully
- The `weatherCode` field is the WMO code at query time, not forecast

---

## Wikipedia Current Events (disasters_v2.py)

**Base URL:** `https://en.wikipedia.org/w/api.php`

**Auth:** None  
**Rate limit:** Standard Wikimedia API (generous, but be a good citizen)  
**Endpoint:**
```
https://en.wikipedia.org/w/api.php
  ?action=parse
  &page=Portal:Current_events
  &prop=text
  &format=json
```

**Approach:** Parses the HTML of Wikipedia's current events portal for
disaster-related news items. This is a text-scraping approach, not a
structured API.

**How it works:**
1. Fetch the raw HTML via Wikimedia's `action=parse` API
2. Extract `<li>` list items from the HTML
3. Classify each item using regex keyword matching:
   - Earthquake: `\b(magnitude|earthquake|quake|seismic|aftershock|mag[\s.]?\d)\b`
   - Flood: `\b(flood|flooding|flash flood|torrential rain|heavy rainfall)\b`
   - Wildfire: `\b(wildfire|bushfire|forest fire|blaze)\b`
   - Storm: `\b(hurricane|typhoon|cyclone|tornado|storm|tropical storm)\b`
   - Volcano: `\b(volcano|volcanic|eruption|lava|ash)\b`
4. Extract approximate lat/lon from known place names (80+ city/country mappings)
5. Check if location falls within region bounding box

**Location lookup** uses a static dict of 80+ countries/regions → (lat, lon)
centroid coordinates, including Middle East, Asia, Africa, Americas, Europe,
Oceania.

**Gotchas:**
- Wikipedia HTML may change structure — the `<li>` extraction is fragile
- Location extraction is approximate (country centroid, not exact event location)
- Requires internet access to `en.wikipedia.org` (API endpoint, not scraping)
- Categorization is keyword-based, not NLP — may misclassify
- Some events have no location → skipped (no map point)
- Max 30 items returned to avoid KML bloat
- The portal updates continuously but Wikipedia editors may lag real-time by
  hours for minor events
- Independent from all API-based disaster sources: these are human-written
  news summaries, not automated sensor data
