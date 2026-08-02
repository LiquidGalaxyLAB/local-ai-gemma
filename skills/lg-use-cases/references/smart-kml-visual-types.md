# Smart KML — Context-Aware Visual Types for News Stories

When rendering news articles on LG, different story types call for different visual treatments. Generic pins are replaced with meaningful geographic shapes and colors.

## Visual Type Reference

| Article Contains Keywords | Type | Fill ABGR | Stroke ABGR | Visual |
|--------------------------|------|-----------|-------------|--------|
| flood, rain | flood | `7fff0000` | `ffff0000` | Blue semi-transparent polygon |
| cyclone, storm | storm | `7f00aaff` | `ff00aaff` | Orange-brown zone |
| protest, protester, education, reform | protest | `7f0088ff` | `ff0088ff` | Orange highlighted zone |
| sport, gold, boxer, commonwealth | sport | `7f00ccff` | `ff00ccff` | Gold paddle icon |
| army, military | military | `7f00ff00` | `ff00ff00` | Green marker |
| election, vote | vote | `7f00ff00` | `ff00ff00` | Green zone |
| earthquake | quake | `7f0000ff` | `ff0000ff` | Red polygon |
| fire | fire | `7f0044ff` | `ff0044ff` | Red-orange zone |
| crime | crime | `7f0000ff` | `ff0000ff` | Red zone |
| (none matched) | default | — | `ff4444ff` | Blue circle icon |

## ABGR Color Format

Google Earth uses Alpha-Blue-Green-Red byte order:

```
AABB GGRR
├─┘  ├──┘
│    └── Blue × Green × Red
└────── Alpha (ff=opaque, 7f=50%, 00=transparent)
```

Examples:
- `ffff0000` — Opaque blue
- `ff00ff00` — Opaque green
- `ff0000ff` — Opaque red
- `ff00ffff` — Opaque yellow
- `7fff0000` — Semi-transparent blue (50% alpha)

## Selecting a Visual Type

Scan article title + description for keywords. Return the first match:

```python
def detect_visual_type(text):
    text_lower = text.lower()
    for keyword, viz in VISUAL_TYPES.items():
        if keyword in text_lower:
            return viz
    return {"style": "default", "fill": "7f4444ff", "stroke": "ff4444ff"}
```

## Region Polygons

Pre-defined boundary coordinates for regions that should render as extruded polygons (not point icons):

| Region | Coords (lon,lat) |
|--------|------------------|
| Assam | (89.5,27.8),(96.0,27.8),(96.0,24.5),(89.5,24.5) |
| Delhi NCR | (76.8,28.9),(77.4,28.9),(77.4,28.3),(76.8,28.3) |
| Kashmir | (73.5,37.0),(80.0,37.0),(80.0,33.0),(73.5,33.0) |
| Mumbai | (72.5,19.5),(73.5,19.5),(73.5,18.7),(72.5,18.7) |
| Kerala | (74.5,12.5),(77.5,12.5),(77.5,8.0),(74.5,8.0) |
| Gujarat | (68.0,24.5),(74.5,24.5),(74.5,20.5),(68.0,20.5) |

Polygons must be closed (last coord = first coord) and use `(lon, lat)` ordering.

## Style Deduplication

To keep KML compact when multiple articles trigger the same visual type, deduplicate styles:

```python
seen_styles = set()
styles = ""
for article in articles:
    viz = detect_visual_type(article['title'] + ' ' + article['desc'])
    if viz["style"] in seen_styles:
        continue
    seen_styles.add(viz["style"])
    # emit <Style id="poly_{style}"> and <Style id="ico_{style}">
```
