#!/usr/bin/env python3
"""
History Educator balloon + KML generator for Liquid Galaxy.

Parchment-meets-modern-briefing style: dark background, sepia/amber header
bar (NOT the news category colors). Each phase is a card showing:
  - Phase name (large bold)
  - Year / date range
  - 2-3 sentence description of what is unfolding NOW
  - "Key Figures" line
  - "Stakes" line (what happens if this goes the other way)

VM constraints (Earth 7.3.3 on VirtualBox):
- NO CDATA anywhere (silently drops the Placemark) — escaped HTML only
- NO gx: namespace in NetworkLink-loaded KML
- Round all coordinates to 4 decimals
- Rightmost screen = floor(N/2)+1 (N=3 → slave_2.kml)
"""
import math


def esc(s):
    """Escape text for BalloonStyle (no CDATA on VM)."""
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
             .replace(">", "&gt;").replace('"', "&quot;"))


# ── Parchment-style phase card balloon ───────────────────────────
def history_balloon_kml(phases, title="History", limit=None):
    """
    Build ONE Placemark whose BalloonStyle holds phase cards.
    phases: list of dicts:
      {name, year, desc, key_figures, stakes}
    Amber/sepia accent (#d4a017 header), dark parchment body (#1a1712).
    """
    cards = []
    for p in phases[:limit] if limit else phases:
        name = esc(p.get("name", "Phase"))
        year = esc(p.get("year", ""))
        desc = esc(p.get("desc", ""))
        kf = esc(p.get("key_figures", ""))
        stakes = esc(p.get("stakes", ""))
        cards.append(f"""
        <div style="background:#1a1712;border-radius:10px;overflow:hidden;margin-bottom:14px;border:1px solid #3a3222;">
          <div style="background:linear-gradient(90deg,#d4a017,#8a6d1a);height:6px;"></div>
          <div style="padding:14px 16px;">
            <div style="font-family:Georgia,serif;font-size:26px;color:#f0e2b0;font-weight:bold;line-height:1.25;">{name}</div>
            <div style="font-family:Arial,sans-serif;font-size:15px;color:#c8a84e;margin-top:5px;letter-spacing:1px;">{year}</div>
            <div style="font-family:Arial,sans-serif;font-size:17px;color:#e2d7b8;margin-top:10px;line-height:1.45;">{desc}</div>
            <div style="font-family:Arial,sans-serif;font-size:14px;color:#b89a5a;margin-top:10px;"><b>Key Figures:</b> {kf}</div>
            <div style="font-family:Arial,sans-serif;font-size:14px;color:#a08040;margin-top:6px;border-top:1px solid #3a3222;padding-top:8px;"><b>Stakes:</b> {stakes}</div>
          </div>
        </div>""")

    body = esc("".join(cards))
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2">
 <Document>
  <name>{esc(title)}</name>
  <Placemark>
    <name>History</name>
    <Style>
      <BalloonStyle>
        <bgColor>bb000000</bgColor>
        <text>{body}</text>
      </BalloonStyle>
    </Style>
    <gx:balloonVisibility>1</gx:balloonVisibility>
    <Point>
      <coordinates>0,0,0</coordinates>
    </Point>
  </Placemark>
 </Document>
</kml>'''


# ── Historical layer helpers (master.kml) ────────────────────────
def territory_polygon_kml(coords, fill, stroke, style_id, label=""):
    """Semi-transparent filled polygon for control lines / empire extent."""
    cstr = " ".join(f"{round(lon,4)},{round(lat,4)},20000" for lon, lat in coords)
    return f"""
  <Placemark>
    <name></name>
    <styleUrl>#{style_id}</styleUrl>
    <Polygon>
      <extrude>1</extrude>
      <altitudeMode>relativeToGround</altitudeMode>
      <outerBoundaryIs>
        <LinearRing>
          <coordinates>{cstr}</coordinates>
        </LinearRing>
      </outerBoundaryIs>
    </Polygon>
  </Placemark>"""


def advance_arrow_kml(points, style_id, alt=50000):
    """LineString arrow path for advances / routes / migrations."""
    cstr = " ".join(f"{round(lon,4)},{round(lat,4)},{alt}" for lon, lat in points)
    return f"""
  <Placemark>
    <name></name>
    <styleUrl>#{style_id}</styleUrl>
    <LineString>
      <tessellate>1</tessellate>
      <altitudeMode>relativeToGround</altitudeMode>
      <coordinates>{cstr}</coordinates>
    </LineString>
  </Placemark>"""


def battle_marker_kml(lat, lon, style_id, scale=1.0):
    """Extruded column at battle site; scale reflects battle size."""
    h = int(150000 * scale)
    coords = []
    steps = 30
    rad = 0.3 * scale
    for s in range(steps + 1):
        th = 2 * math.pi * s / steps
        coords.append(f"{round(lon + rad*math.cos(th),4)},{round(lat + rad*math.sin(th),4)},{h}")
    ring = "\n        ".join(coords)
    return f"""
  <Placemark>
    <name></name>
    <styleUrl>#{style_id}</styleUrl>
    <Polygon>
      <extrude>1</extrude>
      <altitudeMode>relativeToGround</altitudeMode>
      <outerBoundaryIs>
        <LinearRing>
          <coordinates>{ring}</coordinates>
        </LinearRing>
      </outerBoundaryIs>
    </Polygon>
  </Placemark>"""


def siege_ring_kml(lat, lon, style_id, rings=4, radius_deg=0.7):
    """Concentric siege perimeter rings tightening over time."""
    out = []
    for r in range(rings, 0, -1):
        rad = radius_deg * r / rings
        coords = []
        steps = 40
        for s in range(steps + 1):
            th = 2 * math.pi * s / steps
            coords.append(f"{round(lon + rad*math.cos(th),4)},{round(lat + rad*math.sin(th),4)},15000")
        ring = "\n        ".join(coords)
        out.append(f"""
  <Placemark>
    <name></name>
    <styleUrl>#{style_id}</styleUrl>
    <LineString>
      <tessellate>1</tessellate>
      <altitudeMode>relativeToGround</altitudeMode>
      <coordinates>{ring}</coordinates>
    </LineString>
  </Placemark>""")
    return "\n".join(out)


def capital_pin_kml(lat, lon, style_id, label=""):
    """Placemark pin at a capital / key city (2.0x label)."""
    return f"""
  <Placemark>
    <name>{esc(label)}</name>
    <styleUrl>#{style_id}</styleUrl>
    <Point><coordinates>{round(lon,4)},{round(lat,4)},0</coordinates></Point>
  </Placemark>"""


def style_defs():
    """Standard history styles: amber/gold empire, red/blue faction,
    dashed trade route, siege ring, battle column, capital pin."""
    return """
    <Style id="hist_empire">
      <PolyStyle><color>7f00aacc</color><fill>1</fill><outline>1</outline></PolyStyle>
      <LineStyle><color>ff00aacc</color><width>2</width></LineStyle>
    </Style>
    <Style id="hist_empire_lost">
      <PolyStyle><color>7f4444ff</color><fill>1</fill><outline>1</outline></PolyStyle>
      <LineStyle><color>ff4444ff</color><width>2</width></LineStyle>
    </Style>
    <Style id="hist_faction_a">
      <PolyStyle><color>7f0000ff</color><fill>1</fill><outline>1</outline></PolyStyle>
      <LineStyle><color>ff0000ff</color><width>2</width></LineStyle>
    </Style>
    <Style id="hist_faction_b">
      <PolyStyle><color>7f00ff00</color><fill>1</fill><outline>1</outline></PolyStyle>
      <LineStyle><color>ff00ff00</color><width>2</width></LineStyle>
    </Style>
    <Style id="hist_advance">
      <LineStyle><color>ffff0000</color><width>4</width></LineStyle>
    </Style>
    <Style id="hist_advance_b">
      <LineStyle><color>ff00ffff</color><width>3</width></LineStyle>
    </Style>
    <Style id="hist_route">
      <LineStyle><color>ff44ccff</color><width>3</width></LineStyle>
    </Style>
    <Style id="hist_siege">
      <LineStyle><color>ffffaa00</color><width>2</width></LineStyle>
    </Style>
    <Style id="hist_battle">
      <PolyStyle><color>7f0000ff</color><fill>1</fill><outline>1</outline></PolyStyle>
      <LineStyle><color>ff0000ff</color><width>2</width></LineStyle>
    </Style>
    <Style id="hist_pin">
      <IconStyle><scale>1.0</scale><color>ffffcc00</color>
        <Icon><href>http://maps.google.com/mapfiles/kml/paddle/ylw-circle.png</href></Icon>
      </IconStyle>
      <LabelStyle><color>ffffe88a</color><scale>2.0</scale></LabelStyle>
    </Style>
    <Style id="hist_pin_red">
      <IconStyle><scale>1.0</scale><color>ffff4444</color>
        <Icon><href>http://maps.google.com/mapfiles/kml/paddle/red-circle.png</href></Icon>
      </IconStyle>
      <LabelStyle><color>ffffe88a</color><scale>2.0</scale></LabelStyle>
    </Style>
    <Style id="hist_pin_blue">
      <IconStyle><scale>1.0</scale><color>ff44ccff</color>
        <Icon><href>http://maps.google.com/mapfiles/kml/paddle/blu-circle.png</href></Icon>
      </IconStyle>
      <LabelStyle><color>ffffe88a</color><scale>2.0</scale></LabelStyle>
    </Style>
    """


def master_kml_document(layers, lookat):
    """Assemble master.kml with styles + layers + LookAt."""
    lon = lookat.get("lon", 0); lat = lookat.get("lat", 0)
    rng = lookat.get("range", 4000000); tilt = lookat.get("tilt", 45)
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <name>History Educator</name>
    <LookAt><longitude>{lon}</longitude><latitude>{lat}</latitude>
    <range>{rng}</range><tilt>{tilt}</tilt><heading>0</heading>
    <altitudeMode>relativeToGround</altitudeMode></LookAt>
{style_defs()}
{layers}
  </Document>
</kml>"""
