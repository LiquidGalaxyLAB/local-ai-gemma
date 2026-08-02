# KML Icon Deployment on Earth 7.3.3 VM

## Key Finding (July 2026)

Earth 7.3.3 on VirtualBox makes ZERO HTTP requests for custom icon PNGs hosted on the local Apache server at `http://lg1:81/kml/icons/*.png`. Despite the icons being accessible (HTTP 200), Earth never fetches them. Apache access logs confirm 0 PNG requests from the GoogleEarth user-agent.

Google CDN icons (`http://maps.google.com/mapfiles/kml/...`) DO work reliably because Earth 7.3.3 uses a different code path for built-in icon URLs.

## Recommendation

Use Google Maps CDN icons instead of self-hosted icons:

```python
# ❌ Local icons — Earth never requests them
ICON_URL = 'http://lg1:81/kml/icons/plane.png'

# ✅ Google CDN — works every time
ICON_URL = 'http://maps.google.com/mapfiles/kml/shapes/air.png'
```

## Icon URL Reference

| Purpose | Google CDN URL |
|---------|---------------|
| Air traffic | `http://maps.google.com/mapfiles/kml/shapes/air.png` |
| Airports | `http://maps.google.com/mapfiles/kml/shapes/airports.png` |
| Earthquake | `http://maps.google.com/mapfiles/kml/shapes/earthquake.png` |
| Volcano | `http://maps.google.com/mapfiles/kml/shapes/volcano.png` |
| Fire/Wildfire | `http://maps.google.com/mapfiles/kml/shapes/fire_station.png` |
| Caution/Warning | `http://maps.google.com/mapfiles/kml/shapes/caution.png` |
| Info | `http://maps.google.com/mapfiles/kml/shapes/info-i.png` |
| Military | `http://maps.google.com/mapfiles/kml/shapes/military.png` |
| Red circle | `http://maps.google.com/mapfiles/kml/paddle/red-circle.png` |
| Blue circle | `http://maps.google.com/mapfiles/kml/paddle/blu-circle.png` |
| Green circle | `http://maps.google.com/mapfiles/kml/paddle/grn-circle.png` |
| Yellow circle | `http://maps.google.com/mapfiles/kml/paddle/ylw-circle.png` |
| Orange circle | `http://maps.google.com/mapfiles/kml/paddle/orange-circle.png` |
| White circle | `http://maps.google.com/mapfiles/kml/paddle/wht-circle.png` |
| Light blue circle | `http://maps.google.com/mapfiles/kml/paddle/ltblu-circle.png` |
| Purple circle | `http://maps.google.com/mapfiles/kml/paddle/purple-circle.png` |

## Icon Heading Rotation

Directional icons (aircraft) can be rotated using `<heading>` in IconStyle. This works on Earth 7.3.3 VM.
