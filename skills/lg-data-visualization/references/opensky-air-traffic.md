# OpenSky Network — Air Traffic Data Source

**URL:** `https://opensky-network.org/api/states/all`

**Auth:** Anonymous (limited) or basic auth (free account, higher limits)

**Rate limits:**
- Anonymous: ~10 states globally, no bbox filter
- Basic auth (free account): Full bbox query, 4000 requests/day
- To get more data, set `OPENSKY_USER` and `OPENSKY_PASS` env vars

**Request format (with auth):**
```
GET /api/states/all?lamin=LAT_MIN&lamax=LAT_MAX&lomin=LON_MIN&lomax=LON_MAX
```

**Response format (per state array):**
```
[0] icao24          — ICAO 24-bit address (hex)
[1] callsign         — Flight callsign (may be empty)
[2] origin_country   — Country of registration
[5] longitude
[6] latitude
[7] baro_altitude    — Barometric altitude (meters)
[8] on_ground        — Boolean
[9] velocity         — m/s
[10] true_track      — Heading in degrees
```

**ICAO hex range matching (military detection):**
Certain ICAO hex prefixes correspond to known air forces:
| Prefix | Operator |
|--------|----------|
| `ADF7`, `AE01`-`AE07` | USAF |
| `4000`, `43C0` | RAF (UK) |
| `3AA0`, `3B70` | French Air Force |
| `3EA0`, `3F40` | German Air Force |
| `738A` | Israeli Air Force |
| `4D00` | NATO |
| `7102`, `7103` | RSAF (Saudi) |
| `8968` | UAEAF |

**Implementation notes (from `collectors/air_traffic.py`):**
- Use bbox query for region-filtered results
- Skip on-ground aircraft with no callsign (likely grounded planes)
- Cap at 100 results to avoid KML bloat
- Military flights get blue icons, civilian get teal
- Callsign is primary label; fallback to truncated ICAO24

**Pitfalls:**
- Anonymous tier returns very limited data — bbox parameter is ignored without auth
- Free account registration at opensky-network.org is free and instant
- Rate limit: 4000 requests/day on free tier (more than enough for 5-min polling)
- ICAO hex prefixes are not exhaustive — military detection is best-effort
