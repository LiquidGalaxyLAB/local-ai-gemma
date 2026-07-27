# Right-Screen Text Panel Generator

Generate a clean dark-themed PNG with bullet-point text for the LG rightmost screen overlay.

## Usage

```python
from PIL import Image, ImageDraw, ImageFont
import textwrap

img = Image.new('RGBA', (500, 600), (12, 14, 24, 240))
draw = ImageDraw.Draw(img)
ft = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 17)
fb = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 13)
fs = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 11)

# Draw header with gradient
for i in range(50):
    draw.rectangle([(0, i), (500, i)], fill=(35, 45, 85, max(0, 210 - i * 3)))
draw.text((18, 12), "TITLE", font=ft, fill=(255, 204, 0))

# Draw body lines with wrapping
for item in lines:
    if item.startswith('##'):
        # Section header - cyan
        draw.text((18, y), item.replace('##',''), font=fb, fill=(100, 190, 255))
    elif item.startswith('**'):
        # Subheader - yellow
        draw.text((20, y), item.replace('**',''), font=fb, fill=(255, 255, 200))
    else:
        # Body - wrapped light grey
        for w in textwrap.wrap(item, width=52):
            draw.text((20, y), w, font=fs, fill=(195, 200, 220))
            y += 14

img.save("/tmp/right_panel.png")
```

## Reusable Script

`/home/nara/wm-collector/right_panel.py` — contains `make_panel(title, lines)` and `deploy_panel(ip, pass)`.

## Deployment

```bash
# 1. Generate panel
python3 -c "from right_panel import make_panel; make_panel('TITLE', lines)"

# 2. SCP to lg1
sshpass -p 'lg' scp /tmp/right_panel.png lg@<LG-IP>:/home/lg/

# 3. Deploy to Apache
sshpass -p 'lg' ssh lg@<LG-IP> 'sudo cp /home/lg/right_panel.png /var/www/html/kml/'

# 4. Deploy slave_3.kml (ScreenOverlay):
cat > /tmp/slave_3.kml << 'KML'
<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <name>Right Screen Panel</name>
    <ScreenOverlay>
      <name>Text Panel</name>
      <Icon><href>http://lg1:81/kml/right_panel.png</href></Icon>
      <overlayXY x="1" y="0.5" xunits="fraction" yunits="fraction"/>
      <screenXY x="0.98" y="0.5" xunits="fraction" yunits="fraction"/>
      <size x="0" y="0" xunits="pixels" yunits="pixels"/>
    </ScreenOverlay>
  </Document>
</kml>
KML
sshpass -p 'lg' scp /tmp/slave_3.kml lg@<LG-IP>:/home/lg/
sshpass -p 'lg' ssh lg@<LG-IP> 'sudo cp /home/lg/slave_3.kml /var/www/html/kml/'
```

## Screen Layout Rule

- Rightmost screen = N (total screens). For 3 screens = lg3 → `slave_3.kml`
- Leftmost screen = floor(N/2)+2. For 3 screens = lg3 (same as rightmost on 3-screen)
- The text panel ScreenOverlay goes in slave_<N>.kml
- The logo ScreenOverlay goes in slave_<leftmost>.kml
- All screens show the same master.kml Earth visualization via ViewSync
