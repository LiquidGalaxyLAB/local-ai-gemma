# Right-Screen Text Panel — ScreenOverlay PNG Generator

All text content (titles, explanations, bullet points, data quality) goes to the right-screen text panel PNG — never as placemark labels on the Earth globe.

## Screen Formula (ROOT — LG Wiki standard)
- **Rightmost screen** = floor(N/2) + 1 → `slave_<rightmost>.kml`
- **Leftmost screen** = floor(N/2) + 2 → `slave_<leftmost>.kml`
- For 3 screens: rightmost = 2 (lg2), leftmost = 3 (lg3)

## Python Generator (`/home/nara/wm-collector/right_panel.py`)

```python
from PIL import Image, ImageDraw, ImageFont
import textwrap, os

img = Image.new('RGBA', (500, 600), (12, 14, 24, 240))
draw = ImageDraw.Draw(img)

# Fonts
ft = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 17)
fb = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 13)
fs = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 11)

# Header gradient
for i in range(50):
    draw.rectangle([(0, i), (500, i)], fill=(35, 45, 85, max(0, 210 - i*3)))

draw.text((18, 12), "TITLE", font=ft, fill=(255, 204, 0))
draw.line([(18, 40), (482, 40)], fill=(255, 204, 0, 60), width=1)

# Content: sections (##TITLE), bullets (• text), sources
y = 55
for item in lines:
    if item.startswith("##"):
        t = item.replace("##", "").strip()
        draw.text((18, y), t, font=fb, fill=(100, 190, 255))
        y += 22
        draw.line([(18, y), (482, y)], fill=(100, 190, 255, 25), width=1)
        y += 4
    elif item.strip():
        for w in textwrap.wrap(item, width=52):
            draw.text((20, y), w, font=fs, fill=(195, 200, 220))
            y += 14
        y += 2
    else:
        y += 8

img.save("/tmp/right_panel.png")
```

## ScreenOverlay KML (slave_2.kml on 3-screen rig)
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
# Deploy PNG and KML
sshpass -p 'lg' scp /tmp/right_panel.png /tmp/slave_2.kml lg@<LG-IP>:/home/lg/
sshpass -p 'lg' ssh lg@<LG-IP> 'sudo cp /home/lg/right_panel.png /var/www/html/kml/'
sshpass -p 'lg' ssh lg@<LG-IP> 'sudo cp /home/lg/slave_2.kml /var/www/html/kml/'
```

## Key Rules
- NEVER put text as placemark labels on master.kml — use ScreenOverlay
- All text/balloons go to rightmost screen only (slave_<rightmost>.kml — slave_2 on 3-screen rig)
- Solid dark background (RGBA 12,14,24,240) — clean readable panel
- Bullet points only, no paragraphs
- Panel updates independently via 3s slave KML refresh
