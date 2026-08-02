# La Palma Volcano & LG Master Web App — Code Patterns

Extracted from https://github.com/LiquidGalaxyLAB/La-Palma-Volcano-Eruption-Tracking-Tool
and https://github.com/LiquidGalaxyLAB/LG-Master-Web-App

## La Palma Repo Patterns

**KML wrapper (kml.dart):** Wraps content inside a NetworkLink + Document:
- `<NetworkLink>` pointing to `http://lg1/cgi-bin/viewCenteredPlacemark.py` with 2s refresh
- Two `<name>` elements in same Document (intentional)
- Hidden NetworkLink (visibility=0) for dynamic refresh

**flytoview (flyto.dart):** Encodes LookAt as single-line XML string:
```
flytoview=<LookAt><longitude>...</longitude>...</LookAt>
```

**Orbit (orbit.dart):** 36-step gx:Tour, 1.2s duration, 10deg heading increments, 60 tilt, 40km range. Uses `gx:fovy` and `gx:altitudeMode=absolute`.

**Rich data:** MultiGeometry polygons (lava), LineStrings (roads), styled icons from GitHub URLs, CDATA HTML balloons. Date-range filtering in Dart builders.

## LG-Master-Web-App Patterns

**SSH Connection (lg_service.dart):** Uses `dartssh2` package. Singleton service pattern. Connection model stores ip/port/username/password/screens. Frame-count agnostic (uses configurable `screens` count).

**query() method** — writes to `/tmp/query.txt`:
```dart
await execute('echo "$content" > /tmp/query.txt', 'Query sent');
```

**flyTo()** — calls query with `flytoview=$kmlViewTag`.

**forceRefresh()** — adds/removes refresh tags on slave myplaces.kml via sed over SSH.

**uploadKml()** — SFTP upload to `/var/www/html/`, randomizes filename with timestamp.

**sendLogo()** — writes ScreenOverlay KML to `/var/www/html/kml/slave_$leftMostScreen.kml`.

**LG control methods:** shutdown (screens→1 loop, slaves first then lg1), relaunch, reboot — all frame-count agnostic.

**Node.js server:** Optional external server on Render for AI/image processing, contacted via HTTP GET.

## Key Takeaways

1. Both repos are Flutter apps that talk SSH from mobile/desktop to LG — not agent-to-LG
2. Frame-count agnostic: loop from `screens` down to 1, never hardcode
3. The `query.txt` + `flytoview=` pattern is universal across both repos and our rig
4. La Palma uses CGI NetworkLink (needs Apache CGI on lg1) — this rig doesn't have it
5. LG-Master-Web-App defaults: user=lg, pass=lqgalaxy (not lg!), screens=5
