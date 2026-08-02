#!/usr/bin/env python3
"""Generate 48x48px custom KML icons for LG visualization.
Output: /tmp/lg-icons/*.png — then deploy to lg1:81/kml/icons/
"""

import os
from PIL import Image, ImageDraw

OUT = '/tmp/lg-icons'
os.makedirs(OUT, exist_ok=True)
S = 48
H = S // 2

def save(name, draw_fn):
    img = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    draw_fn(ImageDraw.Draw(img))
    img.save(os.path.join(OUT, name), 'PNG')
    print(f"  {name}")

# ── Airplane ──────────────────────────────────────────
def plane(draw):
    draw.polygon([(24,2),(28,20),(44,22),(44,26),(28,28),(24,46),(20,46),
                  (16,28),(4,26),(4,22),(20,20),(20,2)], fill='#88bbff', outline='#fff', width=2)
save('plane.png', plane)

# ── Earthquake (concentric rings) ─────────────────────
def earthquake(draw):
    for r, w in [(14,3),(10,2),(6,2)]:
        draw.ellipse([H-r,H-r,H+r,H+r], outline='#ff4444', width=w)
    draw.ellipse([H-3,H-3,H+3,H+3], fill='#ff4444')
save('earthquake.png', earthquake)

# ── Military (shield) ─────────────────────────────────
def military(draw):
    draw.polygon([(8,8),(40,8),(40,28),(24,44),(8,28)], fill='#4466aa', outline='#fff', width=2)
save('military.png', military)

# ── News (document with lines) ────────────────────────
def news(draw):
    draw.rectangle([8,6,40,42], fill='#334455', outline='#fff', width=2)
    for y in [16,24,32]:
        draw.line([(14,y),(36,y)], fill='#88aacc', width=3)
save('news.png', news)

# ── Wildfire (flame) ──────────────────────────────────
def wildfire(draw):
    draw.polygon([(24,4),(34,20),(44,28),(36,38),(38,46),(24,40),
                  (10,46),(12,38),(4,28),(14,20)], fill='#ff6600', outline='#fc0', width=2)
save('wildfire.png', wildfire)

# ── Storm (spiral cyclone) ────────────────────────────
def storm(draw):
    import math
    for r in [20,14,8]:
        draw.ellipse([H-r,H-r,H+r,H+r], outline='#44aaff', width=2)
    for i in range(0,360,45):
        rad, x, y = math.radians(i), H+int(18*math.cos(math.radians(i))), H+int(18*math.sin(math.radians(i)))
        draw.line([(H,H),(x,y)], fill='#44aaff', width=2)
save('storm.png', storm)

# ── Flood (water drop) ────────────────────────────────
def flood(draw):
    draw.ellipse([6,14,42,40], fill='#3388cc', outline='#66bbff', width=2)
    draw.polygon([(10,16),(18,6),(26,16),(34,6),(42,16)], fill='#66bbff')
save('flood.png', flood)

# ── Alert (exclamation triangle) ──────────────────────
def alert(draw):
    draw.polygon([(24,4),(44,44),(4,44)], fill='#fc0', outline='#fff', width=2)
    draw.line([(24,14),(24,32)], fill='#c30', width=4)
    draw.ellipse([21,36,27,42], fill='#c30')
save('alert.png', alert)

# ── Colored circles (8 colors) ────────────────────────
for name, color in {'red':'#ff3333','blue':'#3388ff','green':'#33cc33',
                     'yellow':'#ffcc00','orange':'#ff6600','white':'#cccccc',
                     'cyan':'#33cccc','purple':'#9933ff'}.items():
    def circle(c=color):
        def d(draw): draw.ellipse([2,2,S-2,S-2], fill=c, outline='#fff', width=2)
        return d
    save(f'circle-{name}.png', circle())

print(f"\nDone: {len(os.listdir(OUT))} icons in {OUT}")
