# Right-Screen Text Panel — ScreenOverlay Pattern

All educational/situational text content goes to the rightmost screen (lg2 on 3-screen rig — physical layout `[lg3][lg1][lg2]`, even slaves on right) as a ScreenOverlay PNG — never as placemark labels on the Earth globe.

## Why
- Earth KML stays clean: only visual elements (points, lines, polygons)
- Text is readable: dark semi-transparent panel with high-contrast text, not subject to Earth's label rendering quirks
- Panel updates independently via 3s slave KML refresh, without touching master.kml

## Generator Tool

Located at `/home/nara/wm-collector/right_panel.py` on the Pi.

```python
from PIL import Image, ImageDraw, ImageFont
import textwrap, os

def make_panel(title, lines, out_path="/tmp/right_panel.png", width=520, height=620):
    """Generate a dark-themed text panel PNG."""
    img = Image.new('RGBA', (width, height), (10, 12, 22, 235))
    draw = ImageDraw.Draw(img)
    
    # Fonts
    ft = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 17)
    fb = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
    fs = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 10)
    
    # Title (yellow), sections (## prefix = light blue header), body (light grey, 52-58 char wrap)
    draw.text((18, 10), title, font=ft, fill=(255, 204, 0))
    # ... iterate over lines, wrap text with textwrap.fill(item, width=55)
    
    img.save(out_path)
```

## KML Structure (slave_2.kml on 3-screen rig — rightmost)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <ScreenOverlay>
      <name>Text Panel</name>
      <Icon><href>http://lg1:81/kml/right_panel.png</href></Icon>
      <overlayXY x="1" y="0.5" xunits="fraction" yunits="fraction"/>
      <screenXY x="0.98" y="0.5" xunits="fraction" yunits="fraction"/>
      <size x="0" y="0" xunits="pixels" yunits="pixels"/>
    </ScreenOverlay>
  </Document>
</kml>
```

## Deployment

```bash
python3 /home/nara/wm-collector/right_panel.py
sshpass -p 'lg' scp /tmp/right_panel.png /tmp/slave_2.kml lg@<LG-IP>:/home/lg/
sshpass -p 'lg' ssh lg@<LG-IP> 'sudo cp /home/lg/right_panel.png /var/www/html/kml/'
sshpass -p 'lg' ssh lg@<LG-IP> 'sudo cp /home/lg/slave_2.kml /var/www/html/kml/slave_2.kml'
```

## Logo Overlay (Left Screen)

Same ScreenOverlay pattern, positioned top-left:
```xml
<overlayXY x="0" y="1" xunits="fraction" yunits="fraction"/>
<screenXY x="0.02" y="0.97" xunits="fraction" yunits="fraction"/>
```

## Prerequisites
- lg3's Solo KML NetworkLink must have `refreshInterval=3` (see lg-ssh-control)
- Earth on lg3 must be launched with `--no_system_check --no_signin` + `LIBGL_ALWAYS_SOFTWARE=1`
