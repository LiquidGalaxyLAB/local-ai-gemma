# Pre-Built Geography KML Generators

These one-shot Python scripts generate educational KMLs with clean Earth visuals + right-screen text panels. Run from the Pi. No wm-collector dependency — just Python stdlib + Pillow.

## International Date Line

Shows the red zigzag date line vs cyan 180° meridian, "Tomorrow" west / "Yesterday" east, city dots for affected territories.

```
python3 /tmp/gen_date_line.py
# → /tmp/dateline.kml (5491 bytes)
```

**Generated styles:** `line180` (cyan), `dateline` (red zigzag), city, explanation, tomorrow/yesterday labels.

**Camera:** Pacific Ocean at 15,000km, 0° tilt

**Deploy:**
```
sshpass -p 'lg' scp /tmp/dateline.kml lg@<IP>:/home/lg/
sshpass -p 'lg' ssh lg@<IP> 'sudo cp /home/lg/dateline.kml /var/www/html/kml/master.kml'
sshpass -p 'lg' ssh lg@<IP> 'rm -f /tmp/query.txt && echo "flytoview=..." > /tmp/query.txt'
```

## India Monsoon Rainfall

Blue wind arrows (monsoon paths), brown Western Ghats ridge, orange rain shadow zone, wettest/driest location labels.

```
python3 /tmp/gen_monsoon.py
# → /tmp/monsoon.kml (8234 bytes)
```

**Camera:** India at 3,000km, 45° tilt

## Turkey-Syria Earthquake M7.8

Red earthquake icon (M7.8 epicenter), orange East Anatolian Fault line (300km rupture), cyan plate boundary, red rupture zone, aftershock dots (12), affected city dots (8).

```
python3 /tmp/gen_eq_visual.py
# → /tmp/eq_visual.kml (4223 bytes, 50 placemarks)
```

**Camera:** Turkey at 600km, 55° tilt

**Troubleshooting:** If placemarks don't render, verify no `xmlns:gx` or CDATA in the KML. Check `QT_XCB_GL_INTEGRATION=none` is set in Earth's environment.

## Ports of India

9 major ports with capacity data, 4 naval bases, 3 strategic chokepoints + educational labels.

Generated via wm-collector + port info merge:
```
cd /home/nara/wm-collector
python3 run.py --region india --layers ships --single-source --data-only
# then merge port info labels via port_edu.py
```

**Camera:** India at 2,500km, 50° tilt

## Right-Screen Text Panels

All geography educators deploy companion text panels via `/home/nara/wm-collector/right_panel.py`. The PNG goes to `http://lg1:81/kml/right_panel.png` and is loaded by `slave_2.kml` (rightmost = floor(N/2)+1; for N=3 → lg2):

```python
from right_panel import make_panel
lines = ["## HEADER", "", "• Content line 1", "• Content line 2"]
make_panel("HEADER", lines, "/tmp/right_panel.png")
# then scp → sudo cp to Apache
```

## Key KML Rules for These Generators

- No `xmlns:gx` namespace — use standard `xmlns="http://www.opengis.net/kml/2.2"`
- No CDATA in any element — use plain text or `escape()` only
- Placemark `<name>` is empty — text goes to right panel
- Google CDN icons: `http://maps.google.com/mapfiles/kml/paddle/*.png`
- ABGR color format: `ff0000ff` = red, `ffff0000` = blue, `ff00ff00` = green
- LookAt must be in Document for camera to auto-position (with flyToView=1)
