# Armed Conflicts Collector Pattern

## Architecture

```
Static config (10 zones) + BBC World conflict-filtered RSS
  → build_kml(): generates 188+ features across 10 zones
    → each zone gets unique KML (front line arrow, siege rings, etc.)
    → 1-line text labels at lon+1.8, lat+0.8 with scale 2.2
    → 3D extruded columns at altitude (intensity × 20000m)
  → deploy to Apache master.kml
  → wait 8s for NetworkLink refresh
  → for each zone:
      fly to zone at 600km range, 55 tilt
      generate + deploy right-screen text panel (Pillow PNG)
      play TTS voiceover (2-4 lines about the zone)
      dwell 10-12 seconds
  → final wide overview

## KML Generation Rules

1. **Build all KML as a single string** — no CDATA, no gx namespace, no external icon URLs from arbitrary hosts
2. **Use Google CDN icons only**: `http://maps.google.com/mapfiles/kml/paddle/`
3. **Colors in ABGR format**: `ff0000ff` = red, `ff00ff00` = green, `ffff0000` = blue
4. **Every zone must look distinct** — do NOT reuse the same style for multiple zones
5. **Text labels** use `<IconStyle><scale>0.0</scale></IconStyle>` (hide icon) + `<LabelStyle><scale>2.2</scale><color>ffffffff</color></LabelStyle>`
6. **3D columns** use `<Polygon><extrude>1</extrude>` with coordinates at 0 altitude

## Python Template (string concatenation, no f-strings for Python 3.5 compat)

```python
features = ""
for z in ZONES:
    lat, lon = z["lat"], z["lon"]
    sid = "z" + str(i)
    
    # Style definition
    styles += '<Style id="' + sid + '_s"><PolyStyle><color>' + col + '</color><fill>1</fill><outline>0</outline></PolyStyle>\n'
    
    # Placemark (coordinate string as separate variable to avoid quote mixing)
    cc = str(lon-0.3) + ',' + str(lat-0.3) + ',0 ' + str(lon+0.3) + ',' + str(lat-0.3) + ',0 ' + str(lon+0.1) + ',' + str(lat+0.3) + ',0'
    features += '<Placemark><name></name><styleUrl>#' + sid + '_s</styleUrl><Polygon><extrude>1</extrude><altitudeMode>relativeToGround</altitudeMode><outerBoundaryIs><LinearRing><coordinates>' + cc + '</coordinates></LinearRing></outerBoundaryIs></Polygon></Placemark>\n'

# Key pitfall: ALWAYS use variables for coordinate strings, never inline string concatenation
# with mixed quote types (+ '...' + "..." + '...') — Python will error on unterminated strings.
```

## Text Panel Generation

```python
from PIL import Image, ImageDraw, ImageFont
import textwrap

img = Image.new('RGBA', (500, 500), (12, 14, 24, 240))
draw = ImageDraw.Draw(img)
font_b = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
font_s = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)

draw.text((16, 12), "TITLE", font=font_b, fill=(255, 60, 60))
draw.text((16, 54), zone_name, font=font_s, fill=(255, 200, 100))
for w in textwrap.wrap(description, width=50):
    draw.text((16, 80), w, font=font_s, fill=(200, 200, 220))
img.save("/tmp/right_panel.png")
```

## Canvas for the 3D face of... wait, I need to focus.

## Sequence

1. Generate KML → write to /tmp/ → scp → sudo cp to Apache
2. `time.sleep(8)` — wait for Earth's 3s NetworkLink refresh
3. Deploy initial text panel via scp + sudo cp to right_panel.png
4. Camera flyto via /tmp/query.txt for each zone
5. Update text panel before each new zone
6. TTS plays during the 10-12s dwell
