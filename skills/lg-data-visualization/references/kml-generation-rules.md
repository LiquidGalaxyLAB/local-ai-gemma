# KML Generation Rules for Data Visualization

Tested constraints on this LG VM rig (Ubuntu 16.04, Earth Pro 7.1/7.3.3 in VirtualBox). Physical hardware may be more permissive — test each feature incrementally.

## Mandatory (always include)

- **LookAt in Document** — without it, Earth loads at Paris default view and the camera never moves to your data. Must use plain `<altitudeMode>`, NOT `<gx:altitudeMode>`.
- **Valid KML wrapper** — `<?xml version="1.0" encoding="UTF-8"?><kml xmlns="http://www.opengis.net/kml/2.2"><Document>...</Document></kml>`
- **Range ≥ 1,500,000m** for country-level views on VM (below this, Earth fails to render terrain)
- **ABGR hex color** — Alpha Blue Green Red byte order. `ffff0000` = opaque red, `ff00ff00` = green, `ff0000ff` = blue

## VM Limitations (do not use)

| Feature | Status | Alternative |
|---------|--------|-------------|
| `<gx:altitudeMode>` inside LookAt | ❌ Rejected silently | Use `<altitudeMode>relativeToGround</altitudeMode>` |
| CDATA in `<BalloonStyle><text>` | ❌ Rejected | Text-only or skip balloons |
| External icon URLs (from internet) | ❌ Rejected | Use `http://lg1:81/...` for local assets |
| COLLADA/KMZ models | ❌ Rejected | Extruded polygons for 3D |
| `gx:namespace` used anywhere except gx:Tour | ❌ Partial rejection | Keep namespace clean: only `xmlns` for basic KML |

## What DOES work on VM

- `<LookAt>` with plain `<altitudeMode>` ✅
- `<Placemark>` with `<Point>` ✅
- `<Style>` with `<IconStyle>`, `<LabelStyle>`, `<LineStyle>`, `<PolyStyle>` ✅
- **Google Maps icon URLs** (`http://maps.google.com/mapfiles/kml/shapes/*.png`) ✅ — Earth bundles these icons locally, no internet needed
- `<Polygon>` with `<extrude>1</extrude>` (3D prisms) ✅
- `<LineString>` with `<tessellate>1</tessellate>` ✅
- `<ScreenOverlay>` (logos, branding) ✅ — but must point to `http://lg1:81/...` URL
- `gx:Tour` with `xmlns:gx` + `gx:FlyTo`/`gx:Wait` inside `gx:Playlist` ✅ (confirmed working July 2026)

## Screen-Specific Placement

News articles, balloon info, and index text go on the **right screen only** (rightmost = floor(N/2)+1; lg2 for N=3). This avoids cluttering the center+left screens that show the primary geographic data. The right screen serves as the "info panel."

Implementation: Either:
1. A second `<NetworkLink>` in master.kml that targets a `news.kml` overlay, or
2. A separate `<ScreenOverlay>` on the right screen only

See `screen-placement.md` for the full layout reference.

## Color Conventions for Data Layers

| Data Type | ABGR Color | Meaning |
|-----------|------------|---------|
| Earthquake M5+ | `ffff0000` | Red — high severity |
| Earthquake M4-5 | `ff00ffff` | Yellow — moderate |
| Earthquake M<4 | `ff00ff00` | Green — low |
| Wildfire | `ffff6600` | Orange |
| Conflict event | `ffff0000` | Red |
| Military activity | `ffff0000` | Red |
| Natural disaster | `ffffff00` | Cyan |
| Weather alert | `ffffffff` | White |
| Pipeline | `ffff00ff` | Magenta (purple-ish) |
| Undersea cable | `ff00ffff` | Yellow (ABGR: 00ffff) |
| Ship/AIS | `ffff0000` | Bright blue (ABGR has B at pos 2, G at pos 3) |

Note: `ff0000ff` in ABGR = Blue (alpha=ff, blue=ff, green=00, red=00). When in doubt, write the hex as `AABBGGRR` and remember Google Earth flips the last two bytes vs RGBA.
