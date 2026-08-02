# KML CDATA & Icon URL Rules (VM Earth 7.3.3)

## CDATA Rejection

Google Earth Pro 7.3.3 on VirtualBox silently rejects **any** CDATA in KML,
not just BalloonStyle. Even `<description><![CDATA[...]]></description>`
causes the entire containing Placemark to be invisible.

**Fix:** Use plain text only. In Python:
```python
from xml.sax.saxutils import escape
desc = escape(raw_text)
```

## Icon URLs

| Type | Works? | Example |
|------|--------|---------|
| Google CDN | ✅ Yes | `http://maps.google.com/mapfiles/kml/paddle/blu-circle.png` |
| Google CDN shapes | ✅ Yes | `http://maps.google.com/mapfiles/kml/shapes/air.png` |
| Local lg1:81 PNGs | ❌ 404 unless icons deployed separately | `http://lg1:81/kml/icons/plane.png` |

**Rule:** Default to Google CDN icons. Local icons require separate deploy via
`generate_icons.py` + `scp` to Apache. Verify with `curl -o /dev/null -w "%{http_code}"`
before relying on local icons.

## Empty Name Tags

Placemarks with `<name>Text</name>` put text on the globe via ViewSync, cluttering all screens. Per LG Wiki convention, all text goes to the right-screen ScreenOverlay PNG only.

**Fix:** Use empty `<name></name>` instead of omitting the tag:
```xml
<Placemark>
  <name></name>    <!-- NOT <name>Label</name> and NOT omitting the tag -->
  <Point><coordinates>78.0,21.0,0</coordinates></Point>
</Placemark>
```

Earth renders the empty name as nothing visible on the globe. The tag must be present (not omitted) to avoid rendering artifacts on some VM builds.

## KML Content Rules (VM-specific)

| Rule | Detail |
|------|--------|
| No gx: namespace | Causes entire KML to be invisible |
| No CDATA anywhere | Even in `<description>`, not just BalloonStyle |
| Use Google CDN icons | Not local lg1:81 PNGs unless verified |
| Simple `<Point>` works | Coordinates only, no styles |
| Styled `<Placemark>` with `<IconStyle>` | Works with Google CDN `<Icon><href>` |
