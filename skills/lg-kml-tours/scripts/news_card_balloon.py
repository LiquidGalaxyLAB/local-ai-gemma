#!/usr/bin/env python3
"""
News Visuals for Liquid Galaxy — richer KML generation.

Implements the "news balloon card" UI (dark HUD-style card with category
color bar, headline, source+timestamp, summary, category badge) and
story-type-specific Earth visuals (rings, columns, polygons, front lines).

VM constraints (Earth 7.3.3 on VirtualBox):
- NO CDATA anywhere (silently drops the Placemark) — use escaped HTML
- NO gx: namespace in NetworkLink-loaded KML
- Round all coordinates to 4 decimals

DESIGN RULE (Nara): KMLs must NEVER be identical. Every story gets a
DIFFERENT shape + color combo, chosen deterministically from the story
index (seed). Multi-shape + multi-color, never recycled styles.

NOTE: This is the NEWS visual language. Conflict visuals (front-line
arrows, siege rings, displacement arrows, crisis spirals) belong to the
armed-conflicts skill — do not duplicate them here.
"""
import math

# ── Category system ──────────────────────────────────────────────
# Each category has a PALETTE of (bar, fill, stroke, icon) — colors vary
# per story so consecutive stories never look the same.
CATEGORIES = {
    "breaking": {
        "badge": "BREAKING", "label": "Breaking",
        "palette": [
            {"bar": "#ff2d2d", "fill": "7f0000ff", "stroke": "ff0000ff", "icon": "red-circle"},
            {"bar": "#ff5555", "fill": "7f2222ff", "stroke": "ff2222ff", "icon": "red-diamond"},
            {"bar": "#b31212", "fill": "7f1111cc", "stroke": "ff1111cc", "icon": "red-circle"},
        ]},
    "conflict": {
        "badge": "CONFLICT", "label": "Conflict",
        "palette": [
            {"bar": "#ff2d2d", "fill": "7f0000ff", "stroke": "ff0000ff", "icon": "red-circle"},
            {"bar": "#d64040", "fill": "7f1010cc", "stroke": "ff1010cc", "icon": "red-diamond"},
            {"bar": "#8f1d1d", "fill": "7f2020aa", "stroke": "ff2020aa", "icon": "red-circle"},
        ]},
    "disaster": {
        "badge": "DISASTER", "label": "Disaster",
        "palette": [
            {"bar": "#ff8c1a", "fill": "7f00aaff", "stroke": "ff00aaff", "icon": "orange-circle"},
            {"bar": "#ffa040", "fill": "7f1060dd", "stroke": "ff1060dd", "icon": "orange-diamond"},
            {"bar": "#e06000", "fill": "7f0088cc", "stroke": "ff0088cc", "icon": "orange-circle"},
            {"bar": "#ffb36b", "fill": "7f2080bb", "stroke": "ff2080bb", "icon": "ylw-circle"},
        ]},
    "geopolitics": {
        "badge": "WORLD", "label": "World",
        "palette": [
            {"bar": "#2d7fff", "fill": "7f0088ff", "stroke": "ff0088ff", "icon": "ltblue-circle"},
            {"bar": "#5a9aff", "fill": "7f1068dd", "stroke": "ff1068dd", "icon": "ltblu-diamond"},
            {"bar": "#1e5fd0", "fill": "7f0044cc", "stroke": "ff0044cc", "icon": "ltblue-circle"},
        ]},
    "economy": {
        "badge": "ECONOMY", "label": "Economy",
        "palette": [
            {"bar": "#2dff6b", "fill": "7f00ff00", "stroke": "ff00ff00", "icon": "grn-circle"},
            {"bar": "#67e88f", "fill": "7f20cc33", "stroke": "ff20cc33", "icon": "grn-diamond"},
            {"bar": "#16b94a", "fill": "7f00aa22", "stroke": "ff00aa22", "icon": "grn-circle"},
        ]},
    "science": {
        "badge": "SCIENCE", "label": "Science",
        "palette": [
            {"bar": "#ffe32d", "fill": "7f00ccff", "stroke": "ff00ccff", "icon": "ylw-circle"},
            {"bar": "#c9a9ff", "fill": "7f66aa99", "stroke": "ff66aa99", "icon": "wht-diamond"},
            {"bar": "#9d7bd8", "fill": "7f4488cc", "stroke": "ff4488cc", "icon": "ylw-circle"},
        ]},
    "sport": {
        "badge": "SPORT", "label": "Sport",
        "palette": [
            {"bar": "#ffd32d", "fill": "7f00ccff", "stroke": "ff00ccff", "icon": "ylw-circle"},
            {"bar": "#ffb800", "fill": "7f1088dd", "stroke": "ff1088dd", "icon": "ylw-diamond"},
            {"bar": "#ffea6b", "fill": "7f20aabb", "stroke": "ff20aabb", "icon": "ylw-circle"},
        ]},
    "default": {
        "badge": "NEWS", "label": "News",
        "palette": [
            {"bar": "#9aa4b2", "fill": "7f4444ff", "stroke": "ff4444ff", "icon": "blu-circle"},
            {"bar": "#b8c2d0", "fill": "7f5566cc", "stroke": "ff5566cc", "icon": "blu-diamond"},
            {"bar": "#7a8494", "fill": "7f3344aa", "stroke": "ff3344aa", "icon": "blu-circle"},
        ]},
}

CATEGORY_KEYWORDS = [
    ("breaking", ["breaking", "urgent", "just in", "explosion", "attack", "shooting", "strike"]),
    ("conflict", ["war", "conflict", "missile", "invasion", "military", "troops", "offensive", "ceasefire", "front line", "battle", "drone"]),
    ("disaster", ["flood", "earthquake", "wildfire", "fire", "cyclone", "storm", "landslide", "tsunami", "drought", "evacuat", "heatwave"]),
    ("economy",  ["economy", "market", "stock", "trade", "tariff", "inflation", "bank", "finance", "gdp", "oil price", "debt", "recession", "rally", "rate"]),
    ("science",  ["space", "launch", "nasa", "isro", "climate", "science", "research", "discover", "mars", "moon", "orbit", "gene", "vaccine", "ai"]),
    ("sport",    ["sport", "cricket", "football", "olympics", "world cup", "championship", "medal", "tennis", "boxer", "race"]),
    ("geopolitics", ["election", "vote", "president", "minister", "summit", "diplomat", "sanction", "treaty", "parliament", "referendum", "court"]),
]


def detect_category(text):
    """Return category key for a headline+description string."""
    t = text.lower()
    for cat, kws in CATEGORY_KEYWORDS:
        for kw in kws:
            if kw in t:
                return cat
    return "default"


def palette_for(cat, seed=0):
    """Pick a color variant from the category palette, varying by seed."""
    cat = cat if cat in CATEGORIES else "default"
    pal = CATEGORIES[cat]["palette"]
    return pal[seed % len(pal)]


def viz_for_category(cat, seed=0):
    """Return a viz dict (fill/stroke/icon/style) for a category+seed."""
    c = palette_for(cat, seed)
    style = cat if cat in ("breaking", "conflict", "disaster", "economy",
                           "science", "sport", "geopolitics") else "default"
    # ensure unique style id per seed so styles never collide
    return {"style": "%s_%d" % (style, seed % 3),
            "fill": c["fill"], "stroke": c["stroke"], "icon": c["icon"]}


# ── HTML escaping (VM-safe replacement for CDATA) ────────────────
def esc(s):
    """Escape text for embedding in KML BalloonStyle (no CDATA on VM)."""
    return (s.replace("&", "&amp;").replace("<", "&lt;")
             .replace(">", "&gt;").replace('"', "&quot;"))


# ── News Balloon Card UI (rightmost screen) ──────────────────────
def news_card_balloon_kml(articles, limit=6):
    """
    Build a KML with ONE Placemark whose BalloonStyle holds stacked
    news cards (dark HUD theme, category color bars). Escaped HTML —
    works on VM Earth. Auto-opens via gx:balloonVisibility.
    """
    cards = []
    for i, a in enumerate(articles[:limit]):
        cat = detect_category(a.get("title", "") + " " + a.get("desc", ""))
        c = palette_for(cat, i)
        title = esc(a.get("title", "")[:90])
        src = esc(a.get("source", "News"))
        ts = esc(a.get("date", ""))
        desc = esc(a.get("desc", ""))[:220]
        cards.append(f"""
        <div style="background:#10131c;border-radius:10px;overflow:hidden;margin-bottom:14px;border:1px solid #232838;">
          <div style="background:{c['bar']};height:5px;"></div>
          <div style="padding:14px 16px;">
            <div style="font-family:Arial,sans-serif;font-size:27px;color:#ffffff;font-weight:bold;line-height:1.25;">{i+1}. {title}</div>
            <div style="font-family:Arial,sans-serif;font-size:13px;color:#8a93a8;margin-top:6px;">{src} &middot; {ts}</div>
            <div style="font-family:Arial,sans-serif;font-size:17px;color:#d5dae6;margin-top:10px;line-height:1.4;">{desc}</div>
            <div style="display:inline-block;margin-top:10px;background:{c['bar']};color:#000;font-family:Arial,sans-serif;font-size:12px;font-weight:bold;padding:3px 10px;border-radius:9px;">{CATEGORIES[cat]['badge']}</div>
          </div>
        </div>""")

    body = "".join(cards)
    escaped_body = esc(body)

    return f'''<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2">
 <Document>
  <name>News Feed</name>
  <Placemark>
    <name>News</name>
    <Style>
      <BalloonStyle>
        <bgColor>bb000000</bgColor>
        <text>{escaped_body}</text>
      </BalloonStyle>
    </Style>
    <gx:balloonVisibility>1</gx:balloonVisibility>
    <Point>
      <coordinates>0,0,0</coordinates>
    </Point>
  </Placemark>
 </Document>
</kml>'''


# ── Story-type Earth visuals (master.kml) ────────────────────────
# DESIGN: each story gets a DIFFERENT shape + color (seeded by story
# index). Shapes: rings, columns, cones, diamonds, dot clouds, arcs,
# radials. Conflict shapes (front lines, siege rings) stay in the
# armed-conflicts skill.

def ring_kml(lat, lon, viz, label="", rings=3, radius_deg=0.8, alt=20000):
    """Concentric rings (breaking/incident pulse approximation)."""
    out = []
    for r in range(1, rings + 1):
        coords = []
        steps = 48
        rad = radius_deg * r / rings
        for s in range(steps + 1):
            th = 2 * math.pi * s / steps
            coords.append(f"{round(lon + rad * math.cos(th), 4)},{round(lat + rad * math.sin(th), 4)},{alt}")
        ring = "\n        ".join(coords)
        out.append(f"""
  <Placemark>
    <name></name>
    <styleUrl>#poly_{viz['style']}</styleUrl>
    <Polygon>
      <extrude>1</extrude>
      <altitudeMode>relativeToGround</altitudeMode>
      <outerBoundaryIs>
        <LinearRing>
          <coordinates>
        {ring}
          </coordinates>
        </LinearRing>
      </outerBoundaryIs>
    </Polygon>
  </Placemark>""")
    return "\n".join(out)


def column_kml(lat, lon, viz, height_m=300000, label="", radius_deg=0.35):
    """3D extruded column (economy magnitude, disaster epicenter)."""
    coords = []
    steps = 36
    for s in range(steps + 1):
        th = 2 * math.pi * s / steps
        coords.append(f"{round(lon + radius_deg * math.cos(th), 4)},{round(lat + radius_deg * math.sin(th), 4)},{height_m}")
    ring = "\n        ".join(coords)
    return f"""
  <Placemark>
    <name></name>
    <styleUrl>#poly_{viz['style']}</styleUrl>
    <Polygon>
      <extrude>1</extrude>
      <altitudeMode>relativeToGround</altitudeMode>
      <outerBoundaryIs>
        <LinearRing>
          <coordinates>
        {ring}
          </coordinates>
        </LinearRing>
      </outerBoundaryIs>
    </Polygon>
  </Placemark>"""


def cone_kml(lat, lon, viz, height_m=300000, label="", radius_deg=0.6):
    """3D tapered cone (taller = stronger signal). Stacked rings shrinking
    toward the top — reads as a cone/pyramid from any angle."""
    layers = 5
    out = []
    for li in range(layers):
        frac = 1.0 - (li / layers) * 0.6   # shrink radius upward
        alt = height_m * (li + 1) / layers
        coords = []
        steps = 30
        rad = radius_deg * frac
        for s in range(steps + 1):
            th = 2 * math.pi * s / steps
            coords.append(f"{round(lon + rad * math.cos(th), 4)},{round(lat + rad * math.sin(th), 4)},{int(alt)}")
        ring = "\n        ".join(coords)
        out.append(f"""
  <Placemark>
    <name></name>
    <styleUrl>#poly_{viz['style']}</styleUrl>
    <Polygon>
      <extrude>1</extrude>
      <altitudeMode>relativeToGround</altitudeMode>
      <outerBoundaryIs>
        <LinearRing>
          <coordinates>
        {ring}
          </coordinates>
        </LinearRing>
      </outerBoundaryIs>
    </Polygon>
  </Placemark>""")
    return "\n".join(out)


def diamond_kml(lat, lon, viz, label="", size_deg=0.5, height_m=200000):
    """3D diamond / rotated square marker (alternate pin shape)."""
    # rotated square at altitude = diamond from top-down
    off = size_deg
    coords = [
        f"{round(lon,4)},{round(lat + off,4)},{height_m}",
        f"{round(lon + off,4)},{round(lat,4)},{height_m}",
        f"{round(lon,4)},{round(lat - off,4)},{height_m}",
        f"{round(lon - off,4)},{round(lat,4)},{height_m}",
        f"{round(lon,4)},{round(lat + off,4)},{height_m}",
    ]
    ring = "\n        ".join(coords)
    return f"""
  <Placemark>
    <name></name>
    <styleUrl>#poly_{viz['style']}</styleUrl>
    <Polygon>
      <extrude>1</extrude>
      <altitudeMode>relativeToGround</altitudeMode>
      <outerBoundaryIs>
        <LinearRing>
          <coordinates>
        {ring}
          </coordinates>
        </LinearRing>
      </outerBoundaryIs>
    </Polygon>
  </Placemark>"""


def dot_cloud_kml(lat, lon, viz, label="", count=18, radius_deg=1.0):
    """Scattered 3D dots (disruption spread / event footprint)."""
    import random
    rnd = random.Random(round(lat * 1000) + round(lon * 1000))
    out = []
    for _ in range(count):
        th = rnd.uniform(0, 2 * math.pi)
        r = rnd.uniform(0.15, radius_deg)
        dlat = lat + r * math.sin(th)
        dlon = lon + r * math.cos(th)
        alt = rnd.randint(15000, 80000)
        out.append(f"""
  <Placemark>
    <name></name>
    <styleUrl>#ico_{viz['style']}</styleUrl>
    <Point><coordinates>{round(dlon,4)},{round(dlat,4)},{alt}</coordinates></Point>
  </Placemark>""")
    return "\n".join(out)


def radial_kml(lat, lon, viz, label="", rays=8, radius_deg=1.2, alt=60000):
    """Radiating spokes from a point (broadcast / reach / alert)."""
    out = []
    for r in range(rays):
        th = 2 * math.pi * r / rays
        x2 = lon + radius_deg * math.cos(th)
        y2 = lat + radius_deg * math.sin(th)
        cstr = f"{round(lon,4)},{round(lat,4)},{alt} {round(x2,4)},{round(y2,4)},{alt}"
        out.append(f"""
  <Placemark>
    <name></name>
    <styleUrl>#line_{viz['style']}</styleUrl>
    <LineString>
      <tessellate>1</tessellate>
      <altitudeMode>relativeToGround</altitudeMode>
      <coordinates>{cstr}</coordinates>
    </LineString>
  </Placemark>""")
    return "\n".join(out)


def line_kml(coords, viz, label="", width=3):
    """LineString (trade corridors, routes)."""
    cstr = " ".join(f"{round(lon,4)},{round(lat,4)},100000" for lon, lat in coords)
    return f"""
  <Placemark>
    <name></name>
    <styleUrl>#line_{viz['style']}</styleUrl>
    <LineString>
      <tessellate>1</tessellate>
      <altitudeMode>relativeToGround</altitudeMode>
      <coordinates>{cstr}</coordinates>
    </LineString>
  </Placemark>"""


def arc_kml(start, end, viz, label="", height=2000000):
    """Curved arc (launch trajectory / orbital path / flight route)."""
    coords = []
    steps = 40
    lat1, lon1 = start
    lat2, lon2 = end
    for s in range(steps + 1):
        t = s / steps
        lat = lat1 + (lat2 - lat1) * t
        lon = lon1 + (lon2 - lon1) * t
        bulge = math.sin(math.pi * t) * 0.35
        alt = height + int(bulge * height)
        coords.append(f"{round(lon,4)},{round(lat,4)},{alt}")
    cstr = " ".join(coords)
    return f"""
  <Placemark>
    <name></name>
    <styleUrl>#line_{viz['style']}</styleUrl>
    <LineString>
      <tessellate>1</tessellate>
      <altitudeMode>absolute</altitudeMode>
      <coordinates>{cstr}</coordinates>
    </LineString>
  </Placemark>"""


# Shape dispatch — every story gets a different shape by seed
def story_shape(seed, cat, lat, lon, viz, label=""):
    """Return KML for a story location, shape chosen by (seed, cat)."""
    # shape groups: 0=rings, 1=column, 2=cone, 3=diamond, 4=dotcloud, 5=radial
    if cat == "breaking":
        shapes = [ring_kml, radial_kml, ring_kml, diamond_kml]
    elif cat == "disaster":
        shapes = [column_kml, ring_kml, cone_kml, dot_cloud_kml]
    elif cat == "economy":
        shapes = [column_kml, cone_kml, column_kml, radial_kml]
    elif cat == "science":
        shapes = [radial_kml, ring_kml, dot_cloud_kml, diamond_kml]
    elif cat == "sport":
        shapes = [diamond_kml, ring_kml, diamond_kml, column_kml]
    elif cat == "geopolitics":
        shapes = [cone_kml, diamond_kml, column_kml, ring_kml]
    else:
        shapes = [diamond_kml, column_kml, ring_kml, dot_cloud_kml]
    fn = shapes[seed % len(shapes)]
    if fn is ring_kml:
        return ring_kml(lat, lon, viz, label, rings=2 + (seed % 3), radius_deg=0.6 + 0.3 * (seed % 3))
    if fn is column_kml:
        return column_kml(lat, lon, viz, height_m=180000 + 90000 * (seed % 3), label=label)
    if fn is cone_kml:
        return cone_kml(lat, lon, viz, height_m=220000 + 80000 * (seed % 3), label=label)
    if fn is diamond_kml:
        return diamond_kml(lat, lon, viz, label, size_deg=0.4 + 0.15 * (seed % 3))
    if fn is dot_cloud_kml:
        return dot_cloud_kml(lat, lon, viz, label, count=12 + 6 * (seed % 3))
    if fn is radial_kml:
        return radial_kml(lat, lon, viz, label, rays=6 + 2 * (seed % 3))
    return icon_kml(lat, lon, viz, label)


def icon_kml(lat, lon, viz, label=""):
    """Generate a KML placemark icon string."""
    cname = viz.get("icon", "blu-circle")
    coords = str(lon) + "," + str(lat) + ",0"
    return f"""
  <Placemark>
    <name></name>
    <styleUrl>#ico_{viz['style']}</styleUrl>
    <Point><coordinates>{coords}</coordinates></Point>
  </Placemark>"""


def style_block(viz):
    """Generate Style definitions for a visual type (point + poly + line)."""
    s = viz["style"]
    icon = viz.get("icon", "blu-circle")
    return f"""
    <Style id="ico_{s}">
      <IconStyle><scale>0.9</scale><color>{viz['stroke']}</color>
        <Icon><href>http://maps.google.com/mapfiles/kml/paddle/{icon}.png</href></Icon>
      </IconStyle>
      <LabelStyle><scale>0</scale></LabelStyle>
    </Style>
    <Style id="poly_{s}">
      <PolyStyle><color>{viz['fill']}</color><fill>1</fill><outline>1</outline></PolyStyle>
      <LineStyle><color>{viz['stroke']}</color><width>2</width></LineStyle>
    </Style>
    <Style id="line_{s}">
      <LineStyle><color>{viz['stroke']}</color><width>3</width></LineStyle>
    </Style>"""
