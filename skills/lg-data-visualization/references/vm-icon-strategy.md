# Icon Strategy for Earth 7.3.3 on VirtualBox

Empirically tested July 2026: **Google CDN icons work; local icons fail.**

## The Problem
Earth 7.3.3 on VirtualBox silently drops placemarks that reference external PNG icons, even when:
- The PNG is served from `http://lg1:81/kml/icons/icon.png` (HTTP 200 confirmed)
- The `<Icon><href>` URL is manually verified with `curl`
- The file has correct permissions (644)

## Verified Working Icons (Google CDN)
These always render:

| Shape | URL |
|-------|-----|
| Airplane | `http://maps.google.com/mapfiles/kml/shapes/air.png` |
| Earthquake | `http://maps.google.com/mapfiles/kml/shapes/earthquake.png` |
| Volcano | `http://maps.google.com/mapfiles/kml/shapes/volcano.png` |
| Military | `http://maps.google.com/mapfiles/kml/shapes/military.png` |
| Caution | `http://maps.google.com/mapfiles/kml/shapes/caution.png` |
| Info-i | `http://maps.google.com/mapfiles/kml/shapes/info-i.png` |
| Airports | `http://maps.google.com/mapfiles/kml/shapes/airports.png` |
| Fire station | `http://maps.google.com/mapfiles/kml/shapes/fire_station.png` |
| Red circle | `http://maps.google.com/mapfiles/kml/paddle/red-circle.png` |
| Blue circle | `http://maps.google.com/mapfiles/kml/paddle/blu-circle.png` |
| Green circle | `http://maps.google.com/mapfiles/kml/paddle/grn-circle.png` |
| Yellow circle | `http://maps.google.com/mapfiles/kml/paddle/ylw-circle.png` |
| Orange circle | `http://maps.google.com/mapfiles/kml/paddle/orange-circle.png` |
| White circle | `http://maps.google.com/mapfiles/kml/paddle/wht-circle.png` |
| Light blue circle | `http://maps.google.com/mapfiles/kml/paddle/ltblu-circle.png` |
| Purple circle | `http://maps.google.com/mapfiles/kml/paddle/purple-circle.png` |

## CDATA Blocks (also fail on VM)
Any `<description><![CDATA[...]]></description>` causes Earth 7.3.3 VM to silently drop the entire placemark. Use plain escaped text instead:

```xml
<!-- DON'T: -->
<description><![CDATA[Callsign: ABC123<br/>Altitude: 35,000 ft]]></description>

<!-- DO: -->
<description>Callsign: ABC123 | Altitude: 35,000 ft</description>
```

## How the generator was patched (July 2026)
The `kml/generator.py` was changed:
1. `SHAPE_ICONS` now points to `http://maps.google.com/mapfiles/kml/...` instead of `http://lg1:81/kml/icons/...`
2. `CIRCLE_ICONS` now uses Google CDN paddle URLs instead of local circle-{color}.png
3. CDATA in descriptions was replaced with `escape(plain_text)` — `<![CDATA[` is never emitted
4. The `xmlns:gx` namespace is never added (only plain `xmlns="http://www.opengis.net/kml/2.2"`)
