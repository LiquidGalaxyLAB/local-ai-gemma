# ScreenOverlay Rendering on Earth 7.3.3 VM

From multiple sessions on this VM rig (July-Aug 2026). Earth 7.3.3 on VirtualBox
has specific rules about what renders on NetworkLink-loaded KMLs (slave_2.kml, slave_3.kml).

## What Does NOT Work on slave KMLs

### gx:balloonVisibility (automatically dropped)
Adding `<gx:balloonVisibility>1</gx:balloonVisibility>` to a BalloonStyle
Placemark in slave_2.kml silently fails. Earth 7.3.3 VM drops the `xmlns:gx`
namespace declaration from NetworkLink-loaded KML, so `gx:` prefixed elements
are unknown and ignored. The balloon content exists but never auto-opens.

### HTML ScreenOverlay (gray box with X)
Using `<ScreenOverlay>` with `<Icon><href>http://lg1:81/kml/panel.html</href></Icon>`
where the target is an HTML file renders as a **gray box with an X**.
Earth silently failed to render the HTML content.

## What DOES Work

### ScreenOverlay with PNG image
Using `<ScreenOverlay>` pointing to a PNG image file. Works reliably.

```xml
<ScreenOverlay>
  <Icon><href>http://lg1:81/kml/markets_panel.png</href></Icon>
  <overlayXY x="0" y="1" xunits="fraction" yunits="fraction"/>
  <screenXY x="0.02" y="0.98" xunits="fraction" yunits="fraction"/>
  <size x="0" y="0" xunits="pixels" yunits="pixels"/>
</ScreenOverlay>
```

The PNG must be served by Apache on lg1:81 (`/var/www/html/kml/`). Use Pillow
to generate dark-themed panels with market data, sector breakdowns, etc.

### BalloonStyle with escaped HTML + gx:balloonVisibility in master.kml
In `master.kml` (loaded by the master NetworkLink which may have xmlns:gx),
gx:balloonVisibility works. Use escaped HTML entities (NOT CDATA) for the
BalloonStyle text content.

### Google CDN paddle pins always render
`http://maps.google.com/mapfiles/kml/paddle/<color>-circle.png` pins render
reliably on VM Earth 7.3.3. Use these for index/placemark markers.
