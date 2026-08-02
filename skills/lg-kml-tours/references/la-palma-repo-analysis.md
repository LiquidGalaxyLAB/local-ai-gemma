# La Palma Volcano Eruption Tracking Tool — KML Analysis

Repo: https://github.com/LiquidGalaxyLAB/La-Palma-Volcano-Eruption-Tracking-Tool
Analyzed: 2026-06-22

## Architecture

This is a Flutter Android app that builds KML programmatically and deploys
to Liquid Galaxy via SSH. Key KML classes in `lib/codingapp/kml/`:

| File | Purpose |
|------|---------|
| `kml.dart` | Base KML wrapper — wraps content inside NetworkLink + Document |
| `kmlgenerator.dart` | Saves KML string to device Downloads folder |
| `kml/customkml.dart` | Maritime zones, eruptive vents, land use overlays |
| `kml/flyto.dart` | Generates `flytoview=<LookAt>` URL parameter |
| `kml/LookAt.dart` | LookAt data class with linear string encoding |
| `kml/orbit.dart` | 36-step orbit generator (heading += 10 per step) |
| `kml/lavabuilder.dart` | Polygon-based lava flow overlay with date filtering |
| `kml/tremorbuilder.dart` | Earthquake/tremor data (15K+ lines of coordinates) |
| `kml/buildingsbuilder.dart` | Building damage point data with styled icons |
| `kml/roadsbuilder.dart` | Road damage line data with colored LineStyles |

## Critical KML Structure (kml.dart)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2"
     xmlns:gx="http://www.google.com/kml/ext/2.2"
     xmlns:atom="http://www.w3.org/2005/Atom">
  <Document>
    <name>Network Links</name>
    <visibility>0</visibility>
    <open>0</open>
    <NetworkLink>
      <name>View Centered Placemark</name>
      <visibility>0</visibility>
      <refreshVisibility>0</refreshVisibility>
      <flyToView>0</flyToView>
      <Link>
        <href>http://lg1/cgi-bin/viewCenteredPlacemark.py</href>
        <refreshInterval>2</refreshInterval>
        <viewRefreshMode>onStop</viewRefreshMode>
        <viewRefreshTime>1</viewRefreshTime>
      </Link>
    </NetworkLink>
    <name>$projectName</name>
    $content  <!-- Placemarks, overlays, tours -->
  </Document>
</kml>
```

**NOTE:** Two `<name>` elements in the same `<Document>` (bug or intentional).
The NetworkLink is hidden (visibility=0) and serves as a dynamic refresh layer.

## Orbit Pattern (orbit.dart)

- 36 FlyTo steps (heading += 10 per step = 360° rotation)
- 1.2s duration per step
- 60° tilt, 40,000m range
- Uses `gx:fovy` (field of view) and `altitude` with `gx:altitudeMode=absolute`
- Standalone `<gx:Tour>` element (separate from the NetworkLink content)

## flytoview= Pattern (flyto.dart)

- Encodes LookAt as single-line XML string
- Used as URL parameter: `flytoview=<LookAt>...</LookAt>`
- When loaded via NetworkLink, Earth flies camera to that view
- Requires CGI script on lg1 to parse and respond

## Rich Data Overlay Techniques

### Polygon with Holes (Lava)
- `<MultiGeometry>` with outer + inner boundaries
- `<tessellate>1</tessellate>` for ground following
- Full date-range filtering (Sep 24 → Dec 18, 2021)

### LineString (Roads)
- `<MultiGeometry><LineString>` for road segments
- Color-coded LineStyle per damage grade

### Point Icons (Buildings)
- Custom icons from GitHub raw URLs
- `<scale>0.3</scale>` for small building markers
- CDATA HTML descriptions with styled tables

### Camera Element
- Used instead of LookAt in some placemarks
- Supports `roll` parameter
- `<gx:altitudeMode>relativeToSeaFloor</gx:altitudeMode>` for volcanic terrain

## SSH Deployment (lg_tasks.dart)

Uses `dart:io` + `ssh2` package to:
- Connect to LG (IP/port/user/password from SharedPreferences)
- Write KML files to remote LG paths
- Execute lg-relaunch, lg-reboot, lg-shutdown
- Clean visualization, set/reset refresh
- Deploy logos

## Key Takeaways for LG KML

1. **NetworkLink + CGI** is the core pattern they use, not static KML files
2. **flytoview=** encodes camera position into URL
3. **Orbit uses 36 steps** at 1.2s each
4. **Rich overlays** use MultiGeometry, CDATA, and GitHub-hosted icons
5. **Date-range filtering** via nested if/else blocks in Dart
6. The app is a **Flutter type-safe builder** — KML generated programmatically, not hand-written
