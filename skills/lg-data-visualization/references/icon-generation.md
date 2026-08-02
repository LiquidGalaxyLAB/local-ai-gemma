# Custom Icon Generation for LG KML

Generate 48x48 PNG icons via Python Pillow for display on LG screens. Hosted on lg1:81/kml/icons/.

## Why Custom Icons

- No CDN dependency — works offline
- Heading rotation support for air traffic
- Smaller than Google's paddles — less visual clutter
- Themed per data type (earthquake rings, shield for military, plane silhouette)

## Generation Pattern

```python
from PIL import Image, ImageDraw
import math

S = 48  # Icon size
H = S // 2

img = Image.new('RGBA', (S, S), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)

# Draw geometric shape (example: concentric rings for earthquake)
for r, w in [(14, 3), (10, 2), (6, 2)]:
    draw.ellipse([H-r, H-r, H+r, H+r], outline='#ff4444', width=w)
draw.ellipse([H-3, H-3, H+3, H+3], fill='#ff4444')

img.save('/tmp/lg-icons/earthquake.png', 'PNG')
```

## Icon Catalog

| Name | Shape | Color Schema | Used By |
|------|-------|-------------|---------|
| plane.png | Top-down fuselage with wings | Blue (#88bbff) + white outline | `air_traffic`, rotated by heading |
| earthquake.png | 3 concentric rings + center dot | Red (#ff4444) | `earthquakes` |
| military.png | Shield polygon | Blue (#4466aa) + white outline | `military_base` |
| news.png | Document with text lines | Dark blue (#334455) + white outline | `news`, info panels |
| wildfire.png | Flame shape (4-point star) | Orange (#ff6600) + yellow outline | `wildfire` |
| storm.png | 3 circles + 8 radial spokes | Light blue (#44aaff) | `severeStorms` |
| flood.png | Water drop + ellipse | Blue (#3388cc) + light blue | `floods` |
| alert.png | Exclamation in triangle | Yellow (#ffcc00) + red detail | `weather_alert` |
| circle-{color}.png | Filled circle with white ring | Per color (see below) | Generic fallback |

## Circle Color Variants

8 circle icons for generic use:
- `circle-red.png` (#ff3333) — High priority, conflicts
- `circle-blue.png` (#3388ff) — Aviation, maritime
- `circle-green.png` (#33cc33) — Normal, safe
- `circle-yellow.png` (#ffcc00) — Warnings, alerts
- `circle-orange.png` (#ff6600) — Moderate priority
- `circle-white.png` (#cccccc) — Neutral, info
- `circle-cyan.png` (#33cccc) — Special categories
- `circle-purple.png` (#9933ff) — Premium, VIP

All circles: filled disk (46px diameter) + white outline ring (2px width).

## Deployment

```bash
# Generate all icons
python3 generate_icons.py  # -> /tmp/lg-icons/*.png (16 files)

# Create dir on lg1
sshpass -p 'lg' ssh lg@<IP> 'sudo mkdir -p /var/www/html/kml/icons'

# SCP
for f in /tmp/lg-icons/*.png; do
  sshpass -p 'lg' scp "$f" lg@<IP>:/home/lg/icons-$(basename $f)
done

# Deploy via Python subprocess on lg1 (sudo cp — not echo|sudo which hangs)
# Write deploy script to lg1:
cat > /tmp/deploy-icons.py << 'PYEOF'
import subprocess, glob, os
for f in glob.glob('/home/lg/icons-*.png'):
    name = os.path.basename(f).replace('icons-', '')
    subprocess.run(['sudo', '-S', 'cp', f, '/var/www/html/kml/icons/' + name], input=b'lg\n', check=True)
    os.remove(f)
subprocess.run(['sudo', '-S', 'chown', '-R', 'lg:lg', '/var/www/html/kml/icons/'], input=b'lg\n', check=True)
subprocess.run(['sudo', '-S', 'chmod', '-R', '755', '/var/www/html/kml/icons/'], input=b'lg\n', check=True)
print('Done')
PYEOF

sshpass -p 'lg' scp /tmp/deploy-icons.py lg@<IP>:/home/lg/deploy-icons.py
sshpass -p 'lg' ssh lg@<IP> python3 /home/lg/deploy-icons.py
```

**Important:** Python 3.5 on lg1 does NOT support f-strings. The deploy script must use `.format()` or `+` concatenation. Do not write `f'/var/www/html/kml/icons/{name}'` in scripts executed ON lg1.

## Verification

```bash
curl -I http://lg1:81/kml/icons/plane.png
# Expected: HTTP/1.1 200 OK
```

## KML Style Reference

```xml
<Style id="s_air_traffic_plane">
  <IconStyle>
    <color>ff00ff88</color>
    <scale>1.2</scale>
    <heading>237</heading>  <!-- rotation by flight direction -->
    <Icon><href>http://lg1:81/kml/icons/plane.png</href></Icon>
  </IconStyle>
  <LabelStyle>
    <color>ffffffff</color>
    <scale>1.4</scale>
  </LabelStyle>
</Style>
```
