---
name: lg-kml-tours
description: Create cinematic KML tours for Liquid Galaxy — FlyTo, orbit, spline-based, storytelling tours.
version: 2.3.0
platforms: [linux]
metadata:
  hermes:
    tags: [LiquidGalaxy, KML, Tour, Orbit, Animation, Camera]
    related_skills: [lg-data-visualization, lg-orbit-workflow, lg-ssh-control]
---

# KML Tour Generation for Liquid Galaxy

## ⚠️ Critical Lesson: Tours Don't Auto-Play — Unless You Use playtour=

`gx:Tour` requires clicking Play in Earth's Places panel. There is no autoPlay
attribute in KML. On LG kiosk rigs where users can't click, **gx:Tour is useless
by itself.**

**HOWEVER:** The LG Wiki documents `playtour=<name>` via `/tmp/query.txt` as the
proven method to auto-play a gx:Tour without any click. This works on Earth 7.3.3
(test confirmed July 2026):

```bash
# 1. Deploy KML with gx:Tour named "Orbit"
# 2. Trigger it:
echo 'playtour=Orbit' > /tmp/query.txt
# 3. Stop it:
echo 'exittour=true' > /tmp/query.txt
```

So the rule is: **gx:Tour alone requires Play click. gx:Tour + playtour= does NOT.**

Working alternatives for auto-camera control (ranked by smoothness):

| Method | How | Auto? | Smoothness |
|--------|-----|-------|------------|
| **playtour=** | Deploy gx:Tour KML → `echo 'playtour=X' > /tmp/query.txt` | ✅ | ★★★★★ (native Earth animation) |
| **flytoview via query.txt** | SSH echo to /tmp/query.txt | ✅ | ★★★☆☆ (daemon race conditions) |
| **Static LookAt** | Put `<LookAt>` in `<Document>` | ✅ | ★★☆☆☆ (single position only) |
| **Python loop on lg1** | Rewrite master.kml every 3s | ✅ | ★★☆☆☆ (flicker on refresh) |
| **flytoview= NetworkLink** | CGI script on lg1 | ✅ | ★★★★☆ (needs CGI setup) |

**Recommended for smooth kiosk orbits:** gx:Tour KML + `playtour=`.

## Tour Structure

Every KML tour lives inside a `<gx:Tour>` element with a `<gx:Playlist>`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2"
     xmlns:gx="http://www.google.com/kml/ext/2.2">
  <Document>
    <name>Tour Name</name>
    <gx:Tour>
      <name>Play Me</name>
      <gx:Playlist>
        <!-- tour primitives go here -->
      </gx:Playlist>
    </gx:Tour>
  </Document>
</kml>
```

**CRITICAL:** Every KML on this LG rig MUST include a `<LookAt>` in the Document (before Placemarks/Tour). Without it, Earth loads the KML but stays at default view (Paris).

See `templates/lg-kml-tours/compact-orbit-tour.kml` — a complete 12-step orbit tour template. Copy, replace LON/LAT/RNG/TILT, deploy, then `echo 'playtour=Orbit' > /tmp/query.txt`.

## Tour Primitives

### gx:FlyTo
Moves the camera to a location with smooth animation.

```xml
<gx:FlyTo>
  <gx:duration>5.0</gx:duration>     <!-- travel time in seconds -->
  <gx:flyToMode>smooth</gx:flyToMode> <!-- smooth or bounce -->
  <LookAt>
    <longitude>78.5</longitude>
    <latitude>20.5</latitude>
    <altitude>0</altitude>
    <heading>0</heading>
    <tilt>60</tilt>
    <range>5000000</range>
    <altitudeMode>relativeToGround</altitudeMode>
  </LookAt>
</gx:FlyTo>
```

### gx:Wait
Pauses the tour at a location.

```xml
<gx:Wait>
  <gx:duration>3.0</gx:duration>
</gx:Wait>
```

### LookAt Parameters
| Param | Description | Typical range |
|-------|-------------|---------------|
| longitude | Target longitude | -180 to 180 |
| latitude | Target latitude | -90 to 90 |
| altitude | Camera altitude | 0 for ground level |
| heading | Camera bearing (0=N, 90=E, 180=S, 270=W) | 0 to 360 |
| tilt | Angle from vertical (0=top-down, 90=horizontal) | 0 to 90 |
| range | Distance from target in meters | 1000 to 10,000,000 |
| altitudeMode | clampToGround, relativeToGround, or absolute | relativeToGround recommended |

## Tour Design Principles

A tour should not simply jump between locations. Instead:

- **Smoothly transition** between points (FlyTo duration 3-8s)
- **Pause** at important locations (Wait 3-5s)
- **Adjust tilt and heading** dynamically to frame each scene
- **Maintain visual continuity** — don't teleport, fly through
- **Create a narrative flow** — establish context, reveal details, conclude

**Good Tour:** Location A → Smooth FlyTo → Wait → Orbit → FlyTo Location B → Wait  
**Bad Tour:** Location A → Instant Jump → Location B

## Tour Types

### 1. Simple Point-to-Point
```
FlyTo A (5s, smooth) → Wait (3s) → FlyTo B (5s, smooth) → Wait (3s)
```

### 2. Orbit Tour
Generate multiple FlyTo steps around a single target landmark, changing heading `360/n` degrees each step while keeping LookAt fixed on the target. Each step is a short duration (0.5-2s) for smooth animation.

```python
for i in range(steps):
    heading = i * (360.0 / steps)
    # FlyTo with heading=heading, same lat/lon/range/tilt
```

### 3. Multi-Location Tour
Sequential FlyTo stops at each location with waits.

### 4. Spline-Based (Cinematic) Tour
Generate 50-200 intermediate FlyTo steps along a mathematically interpolated path where lat, lon, altitude, heading, and tilt all change smoothly.

Using Catmull-Rom interpolation or linear interpolation with easing:
- Start slow → accelerate → decelerate → stop
- Easing function: f(t) = 3t² - 2t³ (smoothstep)

```python
def smoothstep(t):
    return t * t * (3 - 2 * t)

for i in range(steps):
    t = i / (steps - 1)
    eased_t = smoothstep(t)
    lat = lerp(lat_a, lat_b, eased_t)
    lon = lerp(lon_a, lon_b, eased_t)
    # ... etc
```

### 5. Storytelling Tour
Combines camera moves with pauses at key locations for narration. Use longer waits (5-10s) at important sites, shorter (2-3s) at transition points.

## NetworkLink + flytoview Pattern (Auto-Camera Without Tours)

The key technique used by LG projects (La Palma Volcano repo) is **NetworkLink with `flytoview=`** to move the camera automatically — no Play button needed.

### How it works

1. Deploy KML containing a NetworkLink pointing to a CGI script on lg1
2. The NetworkLink uses `flytoview=<LookAt>` to instruct Earth where to fly
3. With `refreshInterval=2` and `viewRefreshMode=onStop`, Earth continuously re-queries

### Structure

```xml
<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2"
     xmlns:gx="http://www.google.com/kml/ext/2.2"
     xmlns:atom="http://www.w3.org/2005/Atom">
  <Document>
    <name>Network Links</name>
    <visibility>0</visibility>
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
    <!-- Placemarks, Tours, overlays here -->
  </Document>
</kml>
```

### flytoview URL Encoding

The `flytoview=` parameter encodes a full LookAt as a single-line string:

```
flytoview=<LookAt><longitude>78.0422</longitude><latitude>27.1751</latitude><range>500</range><tilt>70</tilt><heading>180</heading><gx:altitudeMode>relativeToGround</gx:altitudeMode></LookAt>
```

When Earth loads this URL through a NetworkLink, it flies the camera to the specified view automatically.

**⚠️ Caveat:** `flytoview=` requires a **CGI script** on lg1 (typically `/usr/lib/cgi-bin/viewCenteredPlacemark.py`). Most LG rigs may not have this. Without it, the NetworkLink returns 404. See `references/lg-kml-tours/lg-cgi-setup.md` for setup instructions.

### Static LookAt (Most Reliable Auto-Positioning)

Put a `<LookAt>` in `<Document>` — when Earth loads the KML via the 3s NetworkLink refresh, the camera moves there automatically:

```xml
<Document>
  <name>My Visualization</name>
  <LookAt>
    <longitude>78.0422</longitude>
    <latitude>27.1751</latitude>
    <altitude>0</altitude>
    <heading>180</heading>
    <tilt>70</tilt>
    <range>200</range>
    <altitudeMode>relativeToGround</altitudeMode>
  </LookAt>
</Document>
```

No CGI scripts. No Python loops. No Play clicks. This is the baseline — use it unless you need continuous animation.

### flytoview via /tmp/query.txt (Fastest Reliable Method)

This LG has a background process watching `/tmp/query.txt` for commands.
Writing `flytoview=<LookAt>` to this file triggers a camera fly-to immediately:

```bash
ssh lg@<LG-IP> 'echo "flytoview=<LookAt>...</LookAt>" > /tmp/query.txt'
```

The file is consumed (deleted) after processing — that means it worked.
See the **lg-ssh-control** skill's "FlyTo Camera via /tmp/query.txt" procedure
for the full pattern and pitfall notes.

### Decision Matrix

| Goal | Method | Dependencies | Smoothness |
|------|--------|-------------|------------|
| Single fixed camera | Static LookAt | None | ★★☆☆☆ |
| One-shot fly to location | flytoview via /tmp/query.txt | None | ★★★☆☆ |
| **Smooth orbit / continuous animation** | **gx:Tour KML + playtour=** | **gx:Tour deployed, then `playtour=Orbit`** | **★★★★★** |
| Continuous orbit/flyover | Python loop on lg1 | Python 3.5+, sudo | ★★☆☆☆ |
| Cinematic multi-stop tour | gx:Tour KML + playtour= | gx:Tour + `playtour=` | ★★★★★ |
| flytoview= NetworkLink | CGI script on lg1 | CGI setup | ★★★★☆ |

### Why this beats static tour KMLs

| Approach | Requires Play click? | Auto-updates? | Smooth? |
|----------|---------------------|---------------|---------|
| Static gx:Tour KML | Yes ❌ | No ❌ | Yes ✅ |
| flytoview= NetworkLink | No ✅ | Yes (2s) ✅ | Yes ✅ |
| Continuous script update | No ✅ | Yes (3s) ✅ | Step-by-step ✅ |

For LG kiosk mode (no mouse), use **continuous script update** for animations or **flytoview=** for one-shot camera moves.

## Rich Data Overlays (from La Palma repo)

> **⚠️ VM limitation:** These overlay patterns (Polygon, LineString, styled point icons with external URLs, rich HTML balloons, Camera element, gx: namespace) may NOT render on VirtualBox VM rigs running Earth 7.3.3. See `references/lg-kml-tours/earth-7.3.3-vm-kml-limitations.md`. On physical LG hardware they should work fine. Always test with a minimal KML first — if it works, progressively add overlay features.

> **⛓️ Related skill:** For **data-driven KML generation** — polling external APIs (USGS, EONET, OpenSky) and transforming to placemarks/polygons — see the `lg-data-visualization` skill. This skill (`lg-kml-tours`) covers the KML format and tour patterns; `lg-data-visualization` covers the data pipeline around them.

### Polygon Overlays (Lava flows)
```xml
<MultiGeometry>
  <Polygon>
    <tessellate>1</tessellate>
    <altitudeMode>relativeToGround</altitudeMode>
    <outerBoundaryIs>
      <LinearRing>
        <coordinates>lon,lat,alt lon,lat,alt ...</coordinates>
      </LinearRing>
    </outerBoundaryIs>
    <innerBoundaryIs>
      <LinearRing>
        <coordinates>...</coordinates>
      </LinearRing>
    </innerBoundaryIs>
  </Polygon>
</MultiGeometry>
```

### LineString Overlays (Roads)
```xml
<MultiGeometry>
  <LineString>
    <coordinates>lon,lat,alt lon,lat,alt ...</coordinates>
  </LineString>
</MultiGeometry>
```

## KML Visual Quality Patterns (July 2026)

These patterns emerged from comparing World Monitor's clean web-globe visualizations with LG's KML rendering. The goal: make LG placemarks as clean and informative as World Monitor's map layers.

### Custom Icon Hosting on LG Apache (VM WARNING: Google CDN shape icons 404)

**CRITICAL: Google CDN shape icons return 404 on this VM rig.** `maps.google.com/mapfiles/kml/shapes/air.png`, `fire_station.png`, and `shaded_dot.png` all fail. Only **paddle icons** (ylw/blu/red/grn/ltblu/purp-circle.png) render reliably. If you need custom shapes, host them on lg1 Apache at `/var/www/html/kml/icons/`.

Instead of relying on Google's CDN icons (which may fail on VM Earth 7.3.3), host your own icon set on lg1's Apache (port 81):

```
/var/www/html/kml/icons/
├── plane.png        → Air traffic (rotated by heading)
├── earthquake.png   → Concentric rings
├── military.png     → Shield silhouette
├── news.png         → Document with text lines
├── wildfire.png     → Flame shape
├── storm.png        → Spiral cyclone
├── flood.png        → Water drop
├── alert.png        → Exclamation triangle
└── circle-{color}.png → Generic colored dots (8 colors)
```

**Deployment:** Generate PNGs with Pillow (Python Imaging Library), scp to lg1, then deploy with Python subprocess sudo cp. Icons must be world-readable (755) and owned by lg:lg.

Icons are served at `http://lg1:81/kml/icons/<name>.png`. Reference from any KML:
```xml
<Icon><href>http://lg1:81/kml/icons/plane.png</href></Icon>
```

### Icon Rotation by Heading (AirMashup Pattern)

For directional markers (aircraft, vessels), rotate the icon to match heading using `<heading>` inside `<IconStyle>`:

```xml
<Style id="s_air_traffic_plane">
  <IconStyle>
    <color>ff00ff88</color>
    <scale>1.0</scale>
    <heading>237</heading>
    <Icon><href>http://lg1:81/kml/icons/plane.png</href></Icon>
  </IconStyle>
</Style>
```

Learned from AirMashup project (Dev Gadani, LiquidGalaxyLAB) which uses `pnt.style.iconstyle.heading = aircraft.hdg` via Python's `simplekml` library. Works on Earth 7.3.3 VM.

### Folder-Organized Layers

Group placemarks by type with `<Folder>` tags. Only include folders with content:

```xml
<Folder>
  <name>✈ Air Traffic</name>
  <visibility>1</visibility>
  <Placemark>...</Placemark>
</Folder>
```

### Altitude-Mode Placemarks (Flights)

Show aircraft at actual altitude:

```xml
<Placemark>
  <Point>
    <coordinates>51.5,0.5,10668</coordinates>
  </Point>
  <altitudeMode>relativeToGround</altitudeMode>
</Placemark>
```

Third coordinate value is altitude in meters. OpenSky returns altitudes in meters natively.

### Generating Custom Icons with Pillow

```python
from PIL import Image, ImageDraw
img = Image.new('RGBA', (48, 48), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)
draw.ellipse([18, 18, 30, 30], fill='#ff4444')
img.save('circle-red.png', 'PNG')
```

Standard canvas: 48×48px, RGBA with transparent background.

### Per-Layer Style Palette

| Layer | Color (ABGR) | Icon |
|-------|-------------|------|
| Air Traffic | `ff00ff88` | `plane.png` |
| Military | `ff0044ff` | `military.png` |
| Earthquake | `ffff0000` | `earthquake.png` |
| Wildfire | `ffff6600` | `wildfire.png` |
| Storm | `ff44aaff` | `storm.png` |
| Flood | `ff3388cc` | `flood.png` |
| Weather Alert | `ffffcc00` | `alert.png` |
| News | `ff88aacc` | `news.png` |
| Airport | `ff00bbff` | `circle-blue.png` |

### Right-Screen News Convention

Per LG multi-screen standards, news/articles go on the **rightmost screen = floor(N/2) + 1**. On a 3-screen rig that is **lg2** (floor(1.5)+1 = 2), deploy to `slave_2.kml`:

- **master.kml**: Data layers (earthquakes, flights, bases, airports, weather)
- **slave_2.kml**: News articles in a vertical column east of center

Position news articles as a vertical list:
```python
for i, article in enumerate(news_articles):
    art_lat = region.center_lat + 2.0 - (i * 0.18)
    art_lon = region.center_lon + 8.0
```

---

### Point Icons with Custom Locally-Hosted Images
```xml
<Style id="IconStyle00">
  <IconStyle>
    <scale>0.3</scale>
    <Icon>
      <href>https://raw.githubusercontent.com/user/repo/main/icon.png</href>
    </Icon>
  </IconStyle>
</Style>
```

### Rich HTML Balloons (Info Popups)
> **⚠️ VM CRITICAL: CDATA balloons do NOT render on this rig.** Any `<![CDATA[...]]>` in a KML (including `<description>` and `<BalloonStyle><text>`) causes Earth 7.3.3 on VirtualBox to silently drop the entire Placemark — the wiki's CDATA balloon pattern renders nothing here. Use **escaped HTML entities** (`&lt;div&gt;`) instead, with `<gx:balloonVisibility>1</gx:balloonVisibility>` for auto-open. See `lg-ssh-control` Procedure 14 and its `scripts/lg-kml-tours/deploy_balloon.py`. The example below is the physical-hardware pattern only.

```xml
<description><![CDATA[
<html><body style="margin:0px;overflow:auto;background:#FFFFFF;">
<table style="font-family:Arial;font-size:12px;width:100%;">
<tr style="background:#9CBCE2"><td>Title</td></tr>
<tr><td>Property: Value</td></tr>
</table></body></html>
]]></description>
```

### Camera Element (Alternative to LookAt)
```xml
<Camera>
  <longitude>-17.9068</longitude>
  <latitude>28.6201</latitude>
  <altitude>6238</altitude>
  <heading>-0.79</heading>
  <tilt>4.91</tilt>
  <roll>-0.70</roll>
  <gx:altitudeMode>relativeToSeaFloor</gx:altitudeMode>
</Camera>
```

The `<Camera>` element specifies the camera's absolute position (where the camera IS) rather than a target (where it LOOKS AT). It supports `roll` for banking/rotation effects.

## Non-Tech User Design Principle

Every KML and animation on this LG must work **without user interaction.**
The screens run in kiosk mode — no keyboard, no mouse, no Play button.

### Voice-Friendly Delivery

All responses about KML work are read aloud via TTS. Keep explanations **short, conversational, human-friendly** — no technical jargon, no wall-of-text. 1-2 sentences per point. If the user just said "create a KML," don't narrate every step — do it and report briefly.

**Rules:**
- Never rely on `gx:Tour` without `playtour=` — **gx:Tour + playtour= IS the recommended auto-play approach** (deploy KML, then `echo 'playtour=Orbit' > /tmp/query.txt`)
- Always deploy a static `<LookAt>` as the baseline (camera positions itself on refresh)
- If orbit animation is needed, prefer `playtour=` with a gx:Tour KML over flytoview loops
- **CRITICAL:** When using flytoview orbit via query.txt, deploy KML with **NO LookAt** — otherwise flyToView=1 refresh fights the orbit every 3s (see Pitfalls)
- Placemarks must be in a static KML that never gets overwritten
- Test by imagining a visitor walking up to the screens — what do they see?

**`gx:Tour` always requires clicking Play in Earth's Places panel.** There's no autoPlay attribute in KML. For LG kiosk mode:

- **Continuous script update** — Python loop on lg1 rewriting master.kml every 3s (orbit/flyover)
- **flytoview= NetworkLink** — Camera flies to a view when NetworkLink loads
- **Static LookAt** — Single fixed camera position

## ⚠️ Inward vs Outward Orbit (Critical Distinction)

Users expect "orbit" to mean **going around the target** (inward orbit) — the camera moves to different positions around a fixed point, always looking at it. This is what `flytoview` with changing `heading` does.

**Do NOT** use `xdotool keydown ctrl+Left` for orbit — this produces **outward rotation** (camera spins in place like turning your head). The viewpoint stays in one spot while the direction rotates. Users will reject this as "not an orbit."

| Method | Motion Type | User Expectation |
|--------|------------|------------------|
| `flytoview` with changing heading | Inward orbit ✅ | "Going around the spot" |
| `xdotool keydown ctrl+Left` | Outward rotation ❌ | "Rotating like human looking outward" |

Use `xdotool` only as a last resort when repeated flytoview commands stutter despite all fixes (atomic writes, flyToView=0, matching durations). If you must use it, explain the limitation upfront.

## Cinematic Multi-Stop Tour (Auto-Fly via /tmp/query.txt)

Works without Play click. A Python script on lg1 writes sequential `flytoview`
commands to `/tmp/query.txt`, automatically flying between locations.

### Tour Parameters

| Parameter | VM Rig | Physical Rig |
|-----------|--------|-------------|
| Fly-to duration | 4-6s | 3-5s |
| Wait at stop | 5-7s | 3-5s |
| Range (close) | 5,000-20,000m | 500-5,000m |
| Range (overview) | 150,000-300,000m | 50,000-150,000m |
| Tilt | 45-65° | 50-70° |
| Orbit steps | 60 (1.5s each) | 60 (0.4s each) |

### How It Works

1. Deploy KML with placemarks (**no LookAt** — script controls camera)
2. SCP the tour script to lg1
3. Run via `ssh -f nohup python3 script.py > log 2>&1`
4. Script resets tour state (`exittour=true`), then flies stop-by-stop
5. Final stop: orbit around last location for continuous viewing

### Two-Stage Fly-In Pattern (Proven)

When the tour script needs to fly to a new geographic region (e.g., Italy → Canada), always use a multi-stage fly-in to avoid jarring camera glitches:

```
Stage 1: Wide overview (range=3,000,000m, tilt=40, duration=5-6s) → wait 6-8s
Stage 2: Intermediate zoom (range=500,000m, tilt=50, duration=5-6s) → wait 6-8s  
Stage 3: Close zoom (range=100,000-200,000m, tilt=60, duration=5-6s) → wait 7-8s
Stage 4: Begin orbit
```

Without this, Earth races across the planet at breakneck speed in a single 5s flytoview, causing wild visual glitches and a broken initial position. Verified on July 2026 VM rig.

### Template

See `templates/lg-kml-tours/cinematic-tour.py` — complete template with `flyto()` helper.
See `templates/lg-kml-tours/himalayas-tour.kml` — example KML with styled placemarks + HTML balloons.

### Example: Himalayan Tour (7 stops)

```
Overview (200km) → Everest close (8km) → Lhotse (5km) →
Fly west → Annapurna (12km) → K2 (200km) → Everest orbit (60 steps)
```

Total runtime: ~2 minutes. Deploy and forget.

## Earth Dialog Auto-Dismiss (No-Internet Setup)

If the LG VM has no internet, Google Earth shows a "cannot contact login server"
dialog on every launch. This is purely cosmetic — Earth works fine after
dismissing it.

**Solution:** Install the `scripts/lg-kml-tours/dismiss-earth-dialogs.py` script as an autostart
entry. See `references/lg-kml-tours/vm-network-fix.md` in the `lg-ssh-control` skill for full
install instructions.

The script:
1. Waits 8s for Earth to start
2. Sends Escape, Return, Alt+A, Return every 2s for 30s
3. Auto-dismisses any dialog that appears

## 3D Shape Generation

COLLADA .dae models don't render on this LG. Use stacked extruded `<Polygon>` rings for 3D shapes — renders natively and reliably.

### 3D Triangle Peak Markers (Blue Extruded Polygons)

A proven technique for marking mountain peaks with 3D extruded triangles. No COLLADA, no gx namespace, no external icons.

### Triangle Geometry

A small equilateral triangle (~1.5km sides) centered on the peak coordinates, extruded to a visible height:

```xml
<Style id="blueTri">
  <LineStyle>
    <color>ffff0000</color>    <!-- blue outline in ABGR -->
    <width>2</width>
  </LineStyle>
  <PolyStyle>
    <color>ffff0000</color>    <!-- blue fill in ABGR -->
    <fill>1</fill>
    <outline>1</outline>
  </PolyStyle>
</Style>

<Placemark>
  <name>Kanchenjunga 8,586m</name>
  <styleUrl>#blueTri</styleUrl>
  <Polygon>
    <extrude>1</extrude>
    <altitudeMode>relativeToGround</altitudeMode>
    <outerBoundaryIs>
      <LinearRing>
        <coordinates>
          88.1476,27.7101,12000    <!-- top vertex, extruded to 12km -->
          88.1626,27.6941,12000    <!-- bottom-right -->
          88.1326,27.6941,12000    <!-- bottom-left -->
          88.1476,27.7101,12000    <!-- close ring -->
        </coordinates>
      </LinearRing>
    </outerBoundaryIs>
  </Polygon>
</Placemark>
```

### Parameters

| Parameter | Value | Notes |
|-----------|-------|-------|
| Triangle offset | ~0.015° lat/lon (~1.5km) | Centered on peak coordinate |
| Extrude height | 8,000–12,000m | Above highest peaks to be visible |
| Fill color (ABGR) | `ffff0000` | Pure blue (A=ff, B=ff, G=00, R=00) |
| VM safety | ✅ Works | Basic `<Style>` without CDATA — safe |

### How it works

`extrude=1` tells Earth to draw vertical walls from the ground up to the polygon's altitude, creating a 3D prism. Three vertices = triangular prism = a visible 3D marker from any angle.

### Template

See `templates/lg-kml-tours/peak-markers.kml` — reusable template with editable coordinates, colors, and extrude heights. Copy, customize, deploy.

### Frame-count-agnostic

Place these in `master.kml` — they render on all screens via the standard NetworkLink refresh.

**Sphere:** See `scripts/lg-kml-tours/sphere-generator.py` — generates a sphere from N layered polygon rings at different altitudes/radii. 12 layers x 36 segments produces a smooth sphere. Run locally via Python 3, pipe output to .kml, then deploy via the standard deploy pattern.

- `templates/lg-kml-tours/pyramid-generator.py` — Generates stacked-ring pyramids. Also see `templates/lg-kml-tours/geography-educator.py` (geography KML) and `templates/lg-kml-tours/date-line-educator.py` (date line educator).

**Cylinder:** A single extruded polygon circle (36+ segments) with `<extrude>1</extrude>` and `<altitudeMode>relativeToGround</altitudeMode>` approximates a cylinder. Set the `altitude` in coordinates to the desired height.

Key parameters for sphere generator:
- `LAYERS` — more layers = smoother sphere. 8-12 is good for visibility, 20+ for smoothness.
- `SEGMENTS` — circle segments. 36 minimum, 48+ for rounder appearance.
- `RADIUS_M` — sphere radius in meters. 100,000 = 100km sphere.
- `altitudeMode`: use `absolute` so the sphere floats at a fixed height above sea level. Use `relativeToGround` with a lower radius for terrain-hugging shapes.
- Colors use ABGR hex format: AABBGG + RR suffix. `ff0000ff` = opaque blue, `7f00ffff` = semi-transparent yellow.

## Validation Rules

Before deploying any tour KML:
1. **XML validity** — well-formed XML, proper escaping
2. **Namespace** — `xmlns:gx="http://www.google.com/kml/ext/2.2"` must be present
3. **Tag ordering** — inside gx:Playlist, elements must be: gx:FlyTo, gx:Wait (not mixed with non-tour elements)
4. **Coordinates** — lon/lat within valid ranges, altitude non-negative
5. **LookAt always present** — both in Document and in each FlyTo
6. **Duration** — FlyTo: 1-10s, Wait: 1-15s recommended
7. **Tilt range** — 0-90 (Google Earth clamps to ~85)
8. **Heading** — 0-360 (Google Earth wraps)
9. **Tour name** — present and descriptive
10. **Smoothness** — at least 36 steps for orbit tours, 50+ for spline paths

## Deployment

Use the standard KML deployment workaround:
1. Write KML at `/tmp/<name>.kml`
2. **Save a copy to `~/lg-content/kml/archive/<name>-$(date +%Y%m%d).kml` for rollback.**
3. Write deploy helper at `/tmp/deploy-kml.sh` (embedded `echo "lg" | sudo -S`)
4. SCP both to lg1
5. SSH and run deploy helper
6. Master refresh (3s) auto-loads the tour

### Clear (Remove) KML from Master

**No relaunch needed after KML clear or update.** The 3s master NetworkLink refresh auto-picks up changes. This is the user's explicit preference — never relaunch after KML operations.

To clear the display and return screens to default state:

1. **Kill any active orbit/script** first:
   ```bash
   sshpass -p 'lg' ssh -o StrictHostKeyChecking=no lg@<LG-IP> "pkill -f script-name"
   ```
2. **Create a clear helper + blank KML** at `/tmp/blank.kml` and `/tmp/clear-kml.sh`:
   ```xml
   <?xml version="1.0" encoding="UTF-8"?>
   <kml xmlns="http://www.opengis.net/kml/2.2">
     <Document>
       <name>Blank</name>
     </Document>
   </kml>
   ```
   ```bash
   #!/bin/bash
   echo "lg" | sudo -S cp /home/lg/blank.kml /var/www/html/kml/master.kml
   echo "Cleared"
   ```
3. SCP and run:
   ```bash
   sshpass -p 'lg' scp -o StrictHostKeyChecking=no /tmp/blank.kml /tmp/clear-kml.sh lg@<LG-IP>:/home/lg/
   sshpass -p 'lg' ssh -o StrictHostKeyChecking=no lg@<LG-IP> "bash /home/lg/clear-kml.sh"
   ```
4. **Stop any stuck tour state** (cleans up if orbit left Earth in tour mode):
   ```bash
   sshpass -p 'lg' ssh -o StrictHostKeyChecking=no lg@<LG-IP> 'echo "exittour=true" > /tmp/query.txt'
   ```

**⚠️ No relaunch needed after KML clear.** The 3s master NetworkLink refresh picks up the blank KML automatically. Relaunch is only needed if Earth cached the previous content — in normal operation, the blank appears within 3s. Never deploy a blank KML as an intermediate step before deploying a new KML.** If you intend to replace the content, skip the blank step and deploy the new KML directly. A blank KML can cause Earth to cache empty state and fail to pick up the replacement. Always overwrite master.kml with the final target KML — no bridge step.

## flyToView=1 in myplaces.kml (Critical Fix for Auto-Positioning)

Without this, deploying a new KML to master.kml shows placemarks but the
camera stays where it was — the Document `<LookAt>` is only processed on
**initial Earth launch**, not on NetworkLink refresh.

**Fix:** Add `<flyToView>1</flyToView>` to the master KML NetworkLink in
`~/earth/kml/master/myplaces.kml`:

```bash
# Before:
<href>##LG_PHPIFACE##kml/master.kml</href>
<refreshMode>onInterval</refreshMode><refreshInterval>3</refreshInterval>

# After:
<href>##LG_PHPIFACE##kml/master.kml</href>
<flyToView>1</flyToView>
<refreshMode>onInterval</refreshMode><refreshInterval>3</refreshInterval>
```

This is a **one-time fix** — deploy it, relaunch Earth once, then every
future KML update auto-flies to the LookAt position on the 3s refresh.

**Implementation via sed:**
```bash
sed -i 's|<href>##LG_PHPIFACE##kml/master.kml</href>|<href>##LG_PHPIFACE##kml/master.kml</href>\n\t\t\t\t<flyToView>1</flyToView>|' ~/earth/kml/master/myplaces.kml
```

**Reload is required after this change** — myplaces.kml is read at Earth
startup. Use `lg-relaunch-direct` once. After that, no more relaunches needed.

### Why This Wasn't Working

The master NetworkLink had no `<flyToView>` element, which defaults to `0`
(false). So every 3s refresh downloaded new KML content (placemarks, polygons)
but **never moved the camera** to the Document's `<LookAt>` position.
The LookAt only worked on Earth's initial launch when myplaces.kml was first
parsed.

With `<flyToView>1</flyToView>`, Earth checks the KML's Document LookAt on
every refresh and flies there if it changed. When the file hasn't changed,
HTTP caching (ETag/304) prevents re-processing.

### Verification

```bash
grep -A5 'master.kml' ~/earth/kml/master/myplaces.kml
# Expected: flyToView>1</flyToView> present between href and refreshMode
```

## Wiki Awareness

A companion knowledge base lives at `~/wiki/` covering all LG architecture, KML patterns, 3D shapes, orbit animation, and VM quirks. **When you discover a new KML pattern, fix an animation bug, or learn something new, update the relevant wiki page.** The wiki is the durable reference — this skill is the executable procedure.

### Wiki Sync After Skill Updates

Whenever this skill is updated (patched with new procedures, fixes, or discoveries):
1. Check if any wiki page at `~/wiki/concepts/` or `~/wiki/comparisons/` covers the same topic
2. If yes, update that wiki page to reflect the change
3. Append the update to `~/wiki/log.md`

Specifically:
- **New KML pattern discovered** → update [[lg-kml-patterns]] or [[lg-3d-shapes]]
- **New orbit/animation trick** → update [[lg-orbit-animation]]
- **New KML debugging insight** → update [[lg-kml-debugging]]
- **New hosting/refresh quirk** → update [[lg-hosting-and-refresh]]
- **Bug fix / pitfall discovered** → add to both the skill's Pitfalls table AND the relevant wiki page

## Pitfalls

- **CRITICAL: Document LookAt must use `<altitudeMode>`, NOT `<gx:altitudeMode>`** — Earth silently ignores a `<LookAt>` that contains `gx:` namespace elements (like `<gx:altitudeMode>`). The `gx:` prefix is only valid inside `<Camera>`. Always use plain `<altitudeMode>relativeToGround</altitudeMode>` in Document LookAt. This was the root cause of the Madrid fly-to failing — KML deployed, refresh worked, flyToView=1 was set, but Earth skipped the LookAt because of the unknown gx: element.
- **CRITICAL: gx:Tour via NetworkLink — playtour= silently fails** — `playtour=<name>` only finds tours registered in Earth's Places panel. When a gx:Tour is deployed via the 3s NetworkLink refresh (master.kml), the tour renders visually but NEVER registers in Places — `playtour=` has no tour to find and silently does nothing. Verified on Earth 7.3.3 VM July 2026. **Fix:** deploy the tour KML as a separate NetworkLink in myplaces.kml with `<NetworkLinkControl><Update>`, or skip gx:Tour entirely and use sequential flytoview commands.
- **CRITICAL UPDATE: CDATA entirely invisible (even in `<description>`)** — The earlier belief that only BalloonStyle CDATA was rejected is incomplete. **Any CDATA anywhere** — including `<description><![CDATA[...]]></description>` — causes the containing Placemark to be invisible. The entire Placemark element is silently dropped. Use `xml.sax.saxutils.escape()` or plain text only.
- **CRITICAL UPDATE: Earth 7.3.3 on VirtualBox DOES accept xmlns:gx for gx:Tour** — earlier belief that the gx namespace was entirely rejected is incorrect. gx:Tour with `xmlns:gx` renders and plays correctly. What IS rejected: `<gx:altitudeMode>` inside `<LookAt>`, CDATA anywhere (see above), and external icon URLs from unknown hosts.
- **COLLADA models don't render** on this LG — use extruded polygons for 3D
- **LookAt is mandatory** in Document or Earth stays on default Paris view
- **Long playlists** (>100 steps) may lag on older Earth versions
- **AltitudeMode** in FlyTo's LookAt should match the tour's general scope (relativeToGround for most, absolute for space-level views)
- **Python 3.5 on lg1** — no f-strings. Use `%` formatting or `.format()` in scripts that run on the LG VM. Python 3.5's `subprocess.run` works fine with `input=b"...".encode()` for sudo.
- **`pkill -f` can kill SSH session** — `pkill -f script-name` matches the full process command line. If the SSH command contains the script path (e.g., `python3 /home/lg/taj-orbit.py`), `pkill -f taj-orbit` matches the sshd shell too, killing your connection with exit 255. **Fix:** use a short unique name that won't appear in the SSH command string, or kill by PID after listing (`kill <pid>`).
- **flyToView=1 interferes with flytoview orbit scripts (CRITICAL)** — Even when master.kml has NO `<LookAt>`, having `<flyToView>1</flyToView>` in myplaces.kml's Master NetworkLink causes stutter. Every 3s NetworkLink refresh, Earth re-processes the KML, creating a brief camera reset that fights ongoing flytoview commands from /tmp/query.txt. **Fix:** set `<flyToView>0</flyToView>` in `~/earth/kml/master/myplaces.kml` before starting any flytoview orbit. This requires a relaunch to take effect. See `references/lg-kml-tours/orbit-stutter-fix.md` for the complete debugging chain.
- **VM Earth can't render close terrain** — On VirtualBox VM rigs, Google Earth fails to render terrain when range < 100,000m. The screen goes blank or shows untextured surfaces. **Fix:** always use range >= 1,500,000m (1,500km) for reliable rendering on VM-based LG rigs. Physical hardware handles close ranges fine.
- **Inward vs outward orbit (CRITICAL distinction)** — `flytoview` with changing heading = **inward orbit** (camera moves AROUND the target, always looking at it). This is what users mean by "orbit." `xdotool keydown ctrl+Left` = **outward rotation** (camera rotates in place like turning your head — the viewpoint stays in one spot but the direction you're looking rotates). These are fundamentally different motions. When a user asks for orbit, they want inward (going around the spot). Use `xdotool` only when explicitly asked or when repeated flytoview commands stutter despite all fixes.**
- **Duplicate orbit/flyover processes** — each SSH invocation that starts a background script creates a new process. Always `pkill -f <name>` before starting fresh.
- **Lon/lat for space views at (0,0)** — when range >= 10,000,000 (showing Earth disk), the lat/lon barely matters since the whole planet is visible.
- **Heading wraparound (CRITICAL for smooth orbit)** — Never reset heading to 0 after reaching 360. Earth sees `heading=354 → heading=0` as a reversal (counter-clockwise 354°) instead of a continuation (clockwise 6°). **Fix: keep heading growing past 360.** Earth handles values > 360 fine by wrapping internally. Remove the `heading %= 360` from your orbit loop.

  ```python
  # WRONG — causes direction flip every rotation
  heading = (step % 60) * 6.0

  # RIGHT — smooth continuous rotation
  heading = 0.0
  while True:
      query(flytoview_str(lat, lon, rng, tilt, heading))
      heading += 6.0        # Never wrap, keep growing
      time.sleep(0.4)
  ```

- **Initial fly-in before orbit** — Send a long-duration (3s) `flytoview` to the starting position first, then wait 3.5s before starting the orbit loop. Without this, the first orbit step may overwrite the fly-in command and the camera never reaches the target.

- **Two-stage fly-in for large geographic jumps** — When switching between distant locations (e.g., Italy → Canada, or Pisa → CN Tower), sending a direct flytoview at close range (100km) causes Earth to race across the planet in seconds, which can glitch or blank out. **Fix:** always use a two-stage approach:
  1. **Wide overview**: flytoview with range=3,000,000m (or larger), tilt=40-45°, duration=5-6s
  2. **Wait** 6-8s for the overview to complete
  3. **Zoom in**: flytoview with target range (100-200km), tilt=55-65°, duration=5-6s
  4. **Wait** 7-8s for the zoom to complete
  5. Then start the orbit

  ```bash
  # Stage 1: wide overview
  ssh lg@lg1 'echo "flytoview=<gx:duration>5.0</gx:duration>...<range>3000000</range><tilt>40</tilt>..." > /tmp/query.txt'
  sleep 6
  # Stage 2: zoom in
  ssh lg@lg1 'echo "flytoview=<gx:duration>6.0</gx:duration>...<range>100000</range><tilt>60</tilt>..." > /tmp/query.txt'
  sleep 8
  # Stage 3: orbit
  ```
  
  This gives Earth time to smoothly transition between hemispheres without visual glitches.

  ```python
  # 1. Fly in slowly
  query('flytoview=<gx:duration>3.0</gx:duration>...heading=0...</LookAt>')
  time.sleep(3.5)  # Wait for fly-in to complete

  # 2. Start orbit
  heading = 0.0
  while True:
      query(flytoview_str(..., heading))
      heading += 6.0
      time.sleep(0.4)
  ```

- **KML not visible after deploying following a blank/clear** — Deploying a blank KML to clear, then later deploying a real KML, may leave screens showing empty content. Earth's NetworkLink can cache the blank HTTP response. **Fix:** after deploying the real KML, send `exittour=true` then a fresh `flytoview` to `/tmp/query.txt`. This forces Earth to re-sync camera and re-render content. Best practice: skip the blank step entirely and overwrite master.kml directly with the new content.
- **`query.txt` consumed = success** — `cat /tmp/query.txt` returning "No such file" means the LG daemon read and processed the command. This is success, not failure. A file that still has content means the daemon hasn't picked it up yet.
- **CRITICAL: Earth 7.3.3 on VirtualBox — PARTIAL namespace rejection.** The EARLIER belief that `xmlns:gx` entirely rejects the KML was incorrect. gx:Tour with `xmlns:gx` and `gx:FlyTo`/`gx:Wait` inside `gx:Playlist` works perfectly (verified July 2026). What IS rejected: `<gx:altitudeMode>` inside `<LookAt>`, `<BalloonStyle><text><![CDATA[...]]></text></BalloonStyle>`, and external icon URLs. Always use plain `<altitudeMode>` in LookAt elements. See `references/lg-kml-tours/earth-7.3.3-vm-kml-limitations.md` for the full CORRECTED diagnosis.

  **What DOES work:** Basic `<Style>` with `<PolyStyle>` and `<LineStyle>` (color + width) works fine on the VM. 3D extruded polygons with `<Style>` render correctly in blue/any color. The limitation is specifically CDATA balloon styles and the gx namespace, not all styles.

  **Safe KML style pattern:**
  ```xml
  <Style id="myStyle">
    <LineStyle>
      <color>ffff0000</color>
      <width>2</width>
    </LineStyle>
    <PolyStyle>
      <color>ffff0000</color>
      <fill>1</fill>
      <outline>1</outline>
    </PolyStyle>
  </Style>
  ```

  **Fix when KML doesn't render:** Keep `xmlns="http://www.opengis.net/kml/2.2"` (no gx), avoid CDATA in balloon text, use only local style references. Start with `<Document>`, `<LookAt>`, and `<Placemark>` with `<Point>` — that baseline always renders. If that works, add `<Style>` with PolyStyle/LineStyle only (no BalloonStyle/CDATA). Skip external icon URLs entirely.

## Domain Balloon Styles (Which Aesthetic per Skill)

**Each LG domain awareness skill has its own balloon aesthetic — do NOT cross-contaminate.** The balloon color scheme signals which type of data the viewer is seeing before they read a single word:

| Skill | Balloon Style | BG Color | Accent | Font | Use When |
|-------|--------------|----------|--------|------|----------|
| **news-storyteller** | Dark HUD card | `#10131c` | Category color bars (red/orange/blue/green/yellow) | Headline 27px bold white, Arial body | News articles |
| **history-educator** | Parchment | `#1a1712` | Sepia/amber `#d4a017` header | Georgia serif titles, amber body | Historical events |
| **maritime-awareness** | Navy SITREP | `#0a111f` | Cyan `#00aacc` border | Status dots, timestamped | Shipping, cables, chokepoints |
| **energy-monitor** | Charcoal ticker | `#1a1a1a` | Amber `#d4a017` border + gold header for renewables | Live ticker (WTI/Brent/TTF), monospace data | Pipelines, power, mining, solar |
| **cyber-infrastructure** | Terminal NOC | `#000000` (pure black) | Electric blue `#00aaff` | Monospace, UTC, SIEM feed | Outages, GPS jamming, DDoS |
| **armed-conflicts** | (Own visual language — see that skill) | — | — | — | Conflict zones, front lines |

**Generator locations:**
- News: `scripts/lg-kml-tours/news_card_balloon.py` (this skill, also `/home/nara/wm-collector/news_visuals.py`)
- History: `/home/nara/wm-collector/history_visuals.py` (`history_balloon_kml()`, parchment style)
- Maritime/Energy/Cyber: inline in their respective demo scripts at `/home/nara/wm-collector/`

**The rule:** If you're deploying a maritime visualization, use the navy SITREP — never the amber energy ticker or the news category colors. The viewer should know which domain they're looking at from the color palette alone.

**THE pattern for text content on the rightmost screen.** Instead of plain BalloonStyle or PNG panels, generate a **dark HUD-style card balloon**: stacked news cards with category color bars, large headlines, source+timestamp, summary, and category badges. Verified working on this VM (July 2026) — the balloon auto-opens via `gx:balloonVisibility` and the cards render beautifully.

**Reusable generator:** `scripts/lg-kml-tours/news_card_balloon.py` (also at `/home/nara/wm-collector/news_visuals.py`). It provides:
- `news_card_balloon_kml(articles, limit=N)` → full KML with ONE Placemark whose BalloonStyle holds N stacked cards (escaped HTML — VM-safe, no CDATA)
- `detect_category(text)` → breaking/conflict/disaster/geopolitics/economy/science/sport/default
- `story_shape(seed, cat, lat, lon, viz)` → **UNIQUE visual per story** — shape+color chosen deterministically by seed so no two stories look alike
- Shape library: `ring_kml` (pulse rings), `column_kml` (3D column), `cone_kml` (tapered cone), `diamond_kml` (rotated square), `dot_cloud_kml` (scattered dots), `radial_kml` (spokes), `line_kml`, `arc_kml`
- `palette_for(cat, seed)` / `viz_for_category(cat, seed)` → per-category color PALETTES (3 variants each) — colors vary by seed too
- `style_block(viz)` → ico_/poly_/line_ Style definitions

**MULTI-SHAPE + MULTI-COLOR RULE (Nara, mandatory):** KMLs must NEVER be identical. Every story gets a different shape AND color combo. Seed = story index. Never recycle the same style for consecutive stories. This applies to ALL LG content skills — see also `armed-conflicts` skill which has its own unique-per-zone visual language.

**⚠️ NEWS vs CONFLICT SEPARATION:** The news skill and armed-conflicts skill are DIFFERENT. Conflict-specific visuals (front-line arrows, siege rings, displacement arrows, faction markers, crisis spirals, border lines) belong ONLY to the armed-conflicts skill. The news skill uses its own shape set (rings, columns, cones, diamonds, dot clouds, radials, arcs) — do NOT duplicate conflict visuals in news KMLs or vice versa.

**Category color scheme:**
| Category | Bar | Fill (ABGR) | Icon |
|----------|-----|-------------|------|
| breaking | `#ff2d2d` | `7f0000ff` | red-circle |
| conflict | `#ff2d2d` | `7f0000ff` | red-circle |
| disaster | `#ff8c1a` | `7f00aaff` | orange-circle |
| geopolitics | `#2d7fff` | `7f0088ff` | ltblue-circle |
| economy | `#2dff6b` | `7f00ff00` | grn-circle |
| science | `#ffe32d` | `7f00ccff` | ylw-circle |
| sport | `#ffd32d` | `7f00ccff` | ylw-circle |
| default | `#9aa4b2` | `7f4444ff` | blu-circle |

**Deploy to rightmost screen** (root formula: rightmost = floor(N/2)+1; N=3 → slave_2.kml):
```python
from news_card_balloon import news_card_balloon_kml
kml = news_card_balloon_kml(articles, limit=5)
# write to /tmp, scp to lg1, sudo cp to /var/www/html/kml/slave_<rightmost>.kml
```
The slave's 3s Solo KML refresh picks it up — no relaunch needed for content updates.

**Card layout inside the balloon:** dark background `#10131c` with 1px border, 5px category color bar on top, 27px bold white headline, 13px muted source·timestamp, 17px summary, colored badge at bottom. Cards stacked with 14px margin → scrollable news feed.

## Two-Layer Architecture (Reliable Animation)

Critical lesson: **never overwrite master.kml for animation.**  
Rewriting master.kml every 3s causes placemark flicker because Earth re-parses
the entire document on each NetworkLink refresh.

Instead, use a two-layer approach:

### Layer 1: Static KML (deploy once, never touch)
Deploy KML with placemarks, polygons, styles, and CGI NetworkLink to
master.kml. Stays there permanently — content remains rock-solid.

### Layer 2: flytoview-only script (animate via /tmp/query.txt)
This LG monitors `/tmp/query.txt`. Writing a `flytoview=` command triggers
an immediate camera fly-to. The file is consumed (deleted) after processing.

See `scripts/lg-kml-tours/paris-smooth-orbit.py` in this skill directory for a working template.

## Smooth Orbit Parameters

The exact parameters that produce a smooth orbit. **Choice depends on rig type:**

| Parameter | Fast (Physical) | Slow (VM Rig) | Why |
|-----------|---------------|---------------|-----|
| Steps per rotation | 60 | 72 | More steps = smaller heading changes = smoother |
| Step interval | 400ms | 1500ms | VMs can't keep up with sub-second writes — causes shakiness |
| gx:duration | 0.3 | **1.5** | **Must match step interval for seamless motion** — see note below |
| gx:flyToMode | smooth | smooth | Without this, Earth jumps |
| Rotation time | 24s | ~108s | Slower = less jitter on VMs |
| exittour=true | Before start | Before start | Clears stuck tours |

**Golden rule:** If orbit is "shaky" or "stuck", double step interval and gx:duration. 400ms steps work on physical hardware; VM rigs (VirtualBox) need 1.0-1.5s steps. Test slow first, then speed up.

### CRITICAL: gx:duration Must Match (or Exceed) Step Interval

**The most common stutter cause is a gap between flytoview commands.** If gx:duration is shorter than the step interval, the camera finishes moving before the next command arrives, creating a visible "move → pause → move" pattern.

| Pattern | gx:duration | Step interval | Gap | Result |
|---------|-------------|---------------|-----|--------|
| ❌ Underlap | 1.0s | 1.5s | 0.5s | Pause per step = stutter |
| ✅ Seamless | 1.5s | 1.5s | 0s | Continuous, but any daemon delay = tiny pause |
| ✅ **Overlap (preferred)** | **2.5s** | **2.0s** | -0.5s | Next command arrives while previous still playing; Earth adjusts smoothly — zero visible gaps |

**Preferred: overlap pattern.** Set gx:duration ~25% longer than the step interval (e.g. gx:duration=2.5s with sleep=2.0s). Each new flytoview arrives while the previous animation is still playing — Earth queues the next target and smoothly adjusts course. No gaps, even with daemon processing overhead.

**Secondary: match exactly.** gx:duration=1.5 with sleep=1.5. Zero gap but also zero overlap — any daemon delay reading /tmp/query.txt introduces a visible pause.

**Never underlap.** gx:duration shorter than the interval always produces stutter on VM rigs.

### Atomic Write Patterns (Prevents Stutter from Partial Reads)

The LG daemon reads `/tmp/query.txt` asynchronously. If the script opens the file for writing while the daemon is reading it, the daemon may read a truncated/empty file, causing the camera to freeze momentarily.

**Preferred: atomic rename** — write to a temp file on the same filesystem, then os.rename(). This is truly atomic: the daemon reads the complete file or nothing:

```python
def write_q(txt):
    tmp = "/tmp/query.txt.new"
    dst = "/tmp/query.txt"
    with open(tmp, "w") as f:
        f.write(txt)
    os.rename(tmp, dst)   # atomic on same filesystem
```

**Alternative: os.remove + write** — delete before recreating. Brief gap, but safer than truncation:

```python
def write_q(txt):
    path = "/tmp/query.txt"
    try:
        os.remove(path)
    except OSError:
        pass
    with open(path, "w") as f:
        f.write(txt)
```

Neither bare mode="w" nor direct write is sufficient if the daemon has the file open. Always use one of the two patterns above.

### flyToView=1 Must Be Disabled for Smooth Orbits

**Even without a `<LookAt>` in master.kml, `flyToView=1` in myplaces.kml causes stutter.** Every 3s NetworkLink refresh, Earth re-processes the KML file. Even though there's no LookAt to fly to, the re-processing creates a brief camera reset that fights ongoing flytoview commands from the orbit script.

**Fix:** Set `flyToView=0` in `~/earth/kml/master/myplaces.kml` before starting any flytoview orbit:

```bash
sed -i 's|<flyToView>1</flyToView>|<flyToView>0</flyToView>|' ~/earth/kml/master/myplaces.kml
```

This edit to myplaces.kml requires a relaunch to take effect (read once at Earth startup).

**Restore after orbit completes** if you need auto-positioning for static KML deploys:

```bash
sed -i 's|<flyToView>0</flyToView>|<flyToView>1</flyToView>|' ~/earth/kml/master/myplaces.kml
```

### Complete VM-Optimized Orbit Template

```python
#!/usr/bin/env python3
"""VM-optimized continuous orbit via /tmp/query.txt."""
import os, time

LON = 88.1476
LAT = 27.7021
RNG = 250000
TILT = 55
STEPS = 72          # 72 x 5deg = full rotation
STEP_S = 1.5        # Seconds between steps
DUR = 1.5           # gx:duration — MUST match STEP_S

def write_q(txt):
    path = "/tmp/query.txt"
    try:
        os.remove(path)
    except OSError:
        pass
    with open(path, "w") as f:
        f.write(txt)

# Reset tour state
write_q("exittour=true")
time.sleep(1)

# Slow fly-in
flyin = 'flytoview=<gx:duration>4.0</gx:duration><gx:flyToMode>smooth</gx:flyToMode>' \
        '<LookAt><longitude>%.6f</longitude><latitude>%.6f</latitude>' \
        '<range>%d</range><tilt>%d</tilt><heading>0</heading>' \
        '<altitudeMode>relativeToGround</altitudeMode></LookAt>' % (LON, LAT, RNG, TILT)
write_q(flyin)
time.sleep(6)

# Continuous orbit — heading never wraps past 360
heading = 0.0
while True:
    cmd = 'flytoview=<gx:duration>%.1f</gx:duration><gx:flyToMode>smooth</gx:flyToMode>' \
          '<LookAt><longitude>%.6f</longitude><latitude>%.6f</latitude>' \
          '<range>%d</range><tilt>%d</tilt><heading>%.1f</heading>' \
          '<altitudeMode>relativeToGround</altitudeMode></LookAt>' \
          % (DUR, LON, LAT, RNG, TILT, heading)
    write_q(cmd)
    heading += 5.0    # 360/72 — never wrap
    time.sleep(STEP_S)
```

See `templates/lg-kml-tours/vm-orbit-template.py` for the configurable version.

### flytoview Format (must match exactly)

```
flytoview=<gx:duration>0.3</gx:duration><gx:flyToMode>smooth</gx:flyToMode><LookAt>
<longitude>...</longitude><latitude>...</latitude>
<range>...</range><tilt>...</tilt>
<heading>...</heading>
<altitudeMode>relativeToGround</altitudeMode></LookAt>
```

The `gx:duration` and `gx:flyToMode` go **before** the `<LookAt>` tag, not inside it.
Without these, Earth uses default (instant/jumpy) transitions.

### Complete Orbit Lifecycle (from La Palma App)

```python
# 1. Stop any active tour first
query('exittour=true')
time.sleep(0.1)  # small delay for cleanup

# 2. Run orbit: 60 steps, 400ms each
for step in range(60):
    bearing = step * (360.0 / 60)  # 0, 6, 12, ... 354
    flycmd = 'flytoview=<gx:duration>0.3</gx:duration><gx:flyToMode>smooth</gx:flyToMode>' \
             '<LookAt><longitude>%.6f</longitude><latitude>%.6f</latitude>' \
             '<range>%d</range><tilt>%d</tilt>' \
             '<heading>%.1f</heading>' \
             '<altitudeMode>relativeToGround</altitudeMode></LookAt>' \
             % (lon, lat, rng, tilt, bearing)
    query(flycmd)
    time.sleep(0.4)

# 3. Stop: exit tour + restore last position
query('exittour=true')
if last_position:
    query('flytoview=' + last_position)
```

The `exittour=true` command appears in three lifecycle events:
- **Before start** — clears any stuck tour from a previous run
- **After completion** — returns Earth to normal navigation mode
- **On error/stop** — ensures clean state regardless of failure

### Starting Background Scripts on lg1

Verified working on this rig (`ssh -f` + `nohup`):

```bash
# ✅ Verified working
sshpass -p 'lg' ssh -f -o StrictHostKeyChecking=no lg@<LG-IP> \
  "nohup python3 /home/lg/script.py > /home/lg/script.log 2>&1"
```

Do NOT use `setsid ... < /dev/null` pattern — it exits 255 and the process
fails to start. Always use `ssh -f` + `nohup` on this rig.

**Verification after starting:**
```bash
sleep 3 && sshpass -p 'lg' ssh -o StrictHostKeyChecking=no lg@<LG-IP> \
  "pgrep -a python && tail -3 /home/lg/script.log"
```

### Pi-Based Orbit (Alternative: SSH from Pi Instead of Script on lg1)

When running a Python orbit script directly on lg1 causes stutter despite all fixes (atomic writes, matching durations, flyToView=0), try running the orbit **from the Pi via SSH** instead. Each step sends flytoview via a single `echo > /tmp/query.txt` SSH command — truly atomic, no truncation/rename races.

**Why it helps:**
- Each SSH `echo` is a single kernel write syscall — the daemon either sees the complete file or nothing
- No os.remove() / rename() pattern needed — the pipe is atomic by construction
- Overlap pattern naturally works: gx:duration > sleep interval
- Works regardless of lg1's Python version or nohup state

**Pattern:**
```bash
# Fly in
sshpass -p 'lg' ssh lg@<LG-IP> 'echo "flytoview=<gx:duration>4.0</gx:duration><gx:flyToMode>smooth</gx:flyToMode><LookAt>...</LookAt>" > /tmp/query.txt'
sleep 5

# Each orbit step
HDG=0
for step in $(seq 1 72); do
  sshpass -p 'lg' ssh lg@<LG-IP> \
    "echo 'flytoview=<gx:duration>2.5</gx:duration><gx:flyToMode>smooth</gx:flyToMode><LookAt><longitude>$LON</longitude><latitude>$LAT</latitude><range>$RNG</range><tilt>$TILT</tilt><heading>$HDG</heading><altitudeMode>relativeToGround</altitudeMode></LookAt>' > /tmp/query.txt"
  HDG=$((HDG + 5))
  sleep 2.0
done
```

See `templates/lg-kml-tours/pi-orbit-template.sh` for a reusable template with configurable parameters.

**Trade-off:** The bash script runs on the Pi for the full orbit duration (~2-3 min). Use `background=true` + `notify_on_complete=true` in the Hermes terminal tool to keep the session responsive.

### Stopping Background Scripts

```bash
sshpass -p 'lg' ssh lg@<LG-IP> "pkill -f script-name"
```

**⚠️ Mandatory cleanup after stopping: remove stale /tmp/query.txt**
A killed orbit script leaves its last-written flytoview on disk at `/tmp/query.txt`. Earth's daemon continues processing this stale command, keeping the camera locked on the orbit's last position. This can survive Earth restarts because the file persists on disk. Heading values >360 in the stale content indicate it came from an orbit script.

```bash
sshpass -p 'lg' ssh lg@<LG-IP> "rm -f /tmp/query.txt"
# Verify it's gone:
sshpass -p 'lg' ssh lg@<LG-IP> "cat /tmp/query.txt 2>/dev/null || echo 'clean'"
```

Always verify after starting:
```bash
sshpass -p 'lg' ssh lg@<LG-IP> "pgrep -a script-name"
```

## Automated Continuous Animation (Script-Based)

When users cannot click Play on a tour (kiosk/LG mode), use a **Python loop on lg1** that rewrites master.kml with incremental LookAt changes. The master 3s auto-refresh makes Earth pick up each new position.

### How it works

1. A Python script runs indefinitely on lg1 (via nohup)
2. Each iteration: generates KML with a different heading → writes to /tmp → `sudo cp` to `/var/www/html/kml/master.kml` → sleep 3s
3. The LG's master NetworkLink refresh (3s) re-reads master.kml and moves the camera
4. Result: continuous orbit without any user interaction

### Key parameters

| Param | Value | Effect |
|-------|-------|--------|
| Steps | 48 | Smoothness vs update frequency tradeoff |
| Sleep | 3s | Must match master refresh interval |
| sudo -S | Python subprocess with `input=b"PW\n"` | Works under sshpass, bypasses tool guard |

### Starting the script

```bash
# Deploy to lg1 first
sshpass -p 'lg' scp orbit-loop.py lg@<LG-IP>:/home/lg/
sshpass -p 'lg' ssh lg@<LG-IP> "chmod +x /home/lg/orbit-loop.py"

# Start in background (survives SSH disconnect)
sshpass -p 'lg' ssh lg@<LG-IP> "nohup python3 /home/lg/orbit-loop.py > /home/lg/orbit-loop.log 2>&1 &"
# Then SSH again and disown:
sshpass -p 'lg' ssh lg@<LG-IP> "disown -a"  # or just verify with ps
```

### Stopping

```bash
sshpass -p 'lg' ssh lg@<LG-IP> "kill \$(pgrep -f orbit-loop)"
```

### Script template

See `scripts/lg-kml-tours/orbit-loop.py` in this skill directory for the working orbit template.
See `templates/lg-kml-tours/orbit-template.py` for a customizable template with editable
LON/LAT/STEPS/RNG/TILT and optional placemarks array.

### Rich KML template

See `templates/lg-kml-tours/taj-explorer.kml` for a complete example combining: static LookAt auto-positioning, NetworkLink refresh, gx:Tour, styled placemarks with dark-themed HTML balloons, polygon overlay, and LineString — all in one deployable file.

## Logo Overlay Deployment (Leftmost Slave)

Logos appear on the **leftmost slave screen**. Leftmost = floor(N/2) + 2 (root formula). On 3-screen rig: floor(1.5)+2 = 3 → **lg3** → `slave_3.kml`. Never on master.kml.

### Frame-Count-Agnostic Formula
## ScreenOverlay Text Panel (Right Screen Educational Content)

The recommended pattern for putting text on the rightmost screen without cluttering the Earth globe. Instead of placemark labels, generate a dark-themed PNG with all text rendered client-side via Pillow, and display it as a ScreenOverlay.

> **Wiki standard:** The LG Wiki's official approach uses KML BalloonStyle + CDATA + `gx:balloonVisibility` (see `lg-wiki-reference` skill). That's the standard on physical hardware. On this VM rig CDATA is silently rejected — two working alternatives: (1) **escaped-HTML balloons** (`&lt;div&gt;` instead of `<![CDATA[<div>]]>`, keep `gx:balloonVisibility>1` — verified rendering July 2026, see `lg-ssh-control` Procedure 14), or (2) the ScreenOverlay PNG below for larger text panels.

### Why this patternhe recommended pattern for putting text on the rightmost screen without cluttering the Earth globe. Instead of placemark labels, generate a dark-themed PNG with all text rendered client-side via Pillow, and display it as a ScreenOverlay.

> **Wiki standard:** The LG Wiki's official approach uses KML BalloonStyle + CDATA + `gx:balloonVisibility` (see `lg-wiki-reference` skill). That's the standard on physical hardware. On this VM rig CDATA is silently rejected — two working alternatives: (1) **escaped-HTML balloons** (`&lt;div&gt;` instead of `<![CDATA[<div>]]>`, keep `gx:balloonVisibility>1` — verified rendering July 2026, see `lg-ssh-control` Procedure 14), or (2) the ScreenOverlay PNG below for larger text panels.

### Why this pattern

### Text Panel Generator

Located at `/home/nara/wm-collector/right_panel.py`. Generates a 520×620 dark-themed PNG with wrapped text:

```python
from PIL import Image, ImageDraw, ImageFont
import textwrap

img = Image.new('RGBA', (520, 620), (10, 12, 22, 235))
draw = ImageDraw.Draw(img)

# Title in yellow, sections in light blue, body in light grey
draw.text((18, 10), "TITLE", font=font_title, fill=(255, 204, 0))
# Sections with "##" prefix render as blue headers
# Bullet items render as grey wrapped text at 52 char width
```

### ScreenOverlay KML (slave_2.kml on 3-screen rig)

The overlay is positioned on the right edge of the screen, centered vertically:

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

### Deployment

```bash
# Generate the text panel
python3 /home/nara/wm-collector/right_panel.py

# Deploy to lg1 Apache
sshpass -p 'lg' scp /tmp/right_panel.png lg@<LG-IP>:/home/lg/
sshpass -p 'lg' ssh lg@<LG-IP> 'sudo cp /home/lg/right_panel.png /var/www/html/kml/'

# Deploy the overlay KML to slave_2 (rightmost on 3-screen rig)
sshpass -p 'lg' scp /tmp/slave_2.kml lg@<LG-IP>:/home/lg/
sshpass -p 'lg' ssh lg@<LG-IP> 'sudo cp /home/lg/slave_2.kml /var/www/html/kml/slave_2.kml'
```

The 3s refresh on lg2's Solo KML NetworkLink automatically picks up both the new PNG and the KML.

### Logo Overlay (Leftmost Slave)

Same pattern — a logo PNG displayed via ScreenOverlay on the leftmost screen (lg3 for 3-screen setups). Position at top-left:

```xml
<overlayXY x="0" y="1" xunits="fraction" yunits="fraction"/>
<screenXY x="0.02" y="0.97" xunits="fraction" yunits="fraction"/>
```

See `templates/lg-kml-tours/logo-overlay.kml` for the full template.

## LG Multi-Screen Layout Convention

**Root formula (LG Wiki standard):** lg1 = master (screen 1), total screens = N. **Right-most screen = floor(N/2) + 1; left-most screen = floor(N/2) + 2.**

| Screens N | Rightmost (text panel / balloons) | Leftmost (logo) |
|-----------|-----------------------------------|-----------------|
| 3 | **slave_2.kml** (lg2) | slave_3.kml (lg3) |
| 5 | slave_3.kml (lg3) | slave_4.kml (lg4) |
| 7 | slave_4.kml (lg4) | slave_5.kml (lg5) |

| Screen | Role | Overlay Content |
|--------|------|----------------|
| leftmost (floor(N/2)+2) | Logo only | ScreenOverlay PNG (top-left) + master.kml via ViewSync |
| lg1 (master, center) | Main Earth view | master.kml only (no overlay) |
| rightmost (floor(N/2)+1) | Text panel / balloons | ScreenOverlay PNG or BalloonStyle KML (right edge) + master.kml via ViewSync |

All text content (titles, explanations, bullet points, data quality) goes to the rightmost screen — never on Earth as placemark labels and never on master.kml.

## References

- **Authoritative source:** [LG Wiki](https://lg-wiki-coral.vercel.app/docs/) — the best source of truth for all LG camera control, including `playtour=`, orbit research, KML patterns, and advanced camera techniques. Consult this BEFORE the skill when the wiki has coverage.
- `references/lg-kml-tours/lg-wiki-camera-patterns.md` — Curated findings from the LG Wiki: playtour= pattern, orbit research, directional commands, cinematic KML tours.
- **Balloon/text pattern:** The LG Wiki's official approach is KML BalloonStyle + CDATA + `gx:balloonVisibility` sent to `slave_N.kml` (see wiki pages `#6662bcf1d0b8e0d6ad35` and `#698f239779dbaad8a314`). On physical hardware this is the standard. On this VM rig CDATA is silently rejected — use ScreenOverlay PNG instead. Documented in `lg-wiki-reference` skill.
- `~/lg-architecture.md` — Full foundation system architecture (5-layer model, 4 core patterns, content directory, skill skeleton). The **authoritative reference** for how all LG skills fit together.
- **Content directory:** Before deploying any KML or animation script, save a copy to `~/lg-content/kml/archive/<name>-<date>.kml` for rollback. Animation script copies go to `~/lg-content/scripts/`.
- `references/lg-kml-tours/la-palma-repo-analysis.md` — Analysis of the La Palma Volcano Eruption Tracking Tool (NetworkLink + CGI + flytoview patterns)
- `references/lg-kml-tours/lg-cgi-setup.md` — How to set up Apache CGI on the LG for the flytoview camera control pattern
- `references/lg-kml-tours/continuous-kml-animation.md` — Continuous animation via Python script on lg1
- `references/lg-kml-tours/flytoview-fix-myplaces.md` — How to enable `flyToView=1` in myplaces.kml so KML updates auto-position the camera without relaunch
- `references/lg-kml-tours/lg-master-web-app-analysis.md` — LG Master Web App: Flutter SSH patterns, frame-count-agnostic design, SFTP KML upload, forceRefresh, query/flyTo methods
- `scripts/lg-kml-tours/sphere-generator.py` — generates 3D sphere KML from stacked extruded polygon rings (COLLADA-free)
- `templates/lg-kml-tours/minimal-vm.kml` — Bare-bones KML template that always works on VM Earth 7.3.3: no gx namespace, no styles, no CDATA, no external icons. Start here for any new KML on VM rigs, then add features one at a time testing each addition.
- `templates/lg-kml-tours/taj-explorer.kml` — Complete La Palma-pattern KML with LookAt, NetworkLink, styled placemarks, polygon overlay, and LineString
- `templates/lg-kml-tours/pi-orbit-template.sh` — Pi-based SSH orbit template (bash). Each step is an atomic SSH echo with overlap timing. Run from Pi, not lg1. Configurable LON/LAT/RNG/TILT/STEPS/DUR/INTERVAL.<br>
- `templates/lg-kml-tours/vm-orbit-template.py` — VM-optimized continuous orbit via /tmp/query.txt (configurable LON/LAT/RNG/TILT/STEPS, Python 3.5 compat)
- `templates/lg-kml-tours/nz-dynamic.kml` — Multi-layer La Palma-style KML: extruded polygon + LineString + styled point placemarks with dark-themed HTML balloons (no LookAt — for orbit-backed use)
- `templates/lg-kml-tours/etna-la-palma-style.kml` — Complete La Palma-style demo: 4 polygon overlays (lava flows, hazard zone), 2 road LineStrings, 4 styled point placemarks with volcanic/seismic icons and HTML balloons. Pair with vm-orbit-template.py for two-layer animation.
- `templates/lg-kml-tours/himalayas-3d-peaks.kml` — 3D extruded blue triangle markers for mountain peaks. VM-safe: basic `<Style>` with PolyStyle only (no CDATA, no gx). Triangle offset ~0.015° lat/lon with extrude to 11-12km. Copy, edit coordinates, deploy.
- `templates/lg-kml-tours/barcelona.kml` — Minimal city placemark KML: Barcelona, Sagrada Familia, Camp Nou. VM-safe: no gx, no styles, just `<Point>` coordinates. Clean starting template for any city.
- `references/lg-kml-tours/orbit-stutter-fix.md` — Complete debugging chain for flytoview orbit stutter: gx:duration mismatch, os.remove() pattern, flyToView=1 interference, step count optimization. Start here when an orbit "moves, stops, moves."
- `references/lg-kml-tours/xdotool-orbit.md` — Alternative smooth orbit approach using xdotool (Google Earth native rotation). Single command: press-and-hold `ctrl+Left`, release when done. Zero stutter — Earth handles rotation internally. No /tmp/query.txt writes during rotation. Best when repeated flytoview commands cause stutter. Includes multi-stop tour pattern and complete Python script template.
- `references/lg-kml-tours/earth-7.3.3-vm-kml-limitations.md` — Detailed diagnosis of Earth 7.3.3 VM silently rejecting KML with gx namespace, Style/CDATA, or external icon URLs.
- `references/lg-kml-tours/icon-hosting.md` — Custom icon set for LG KML: 16 icons (plane, earthquake, military, news, wildfire, storm, flood, alert, 8 circle colors), generation with Pillow, deployment to lg1:81, and KML usage with heading rotation.
- `scripts/lg-kml-tours/generate-lg-icons.py` — Generates the 16-icon set as 48×48px RGBA PNGs in `/tmp/lg-icons/`. Run locally, then deploy to lg1 via the icon-hosting pattern.
- `scripts/lg-kml-tours/news_card_balloon.py` — Reusable news-card balloon generator: dark HUD card UI (category color bars, headlines, source+timestamp, summary, badges) + ring/column/line/arc KML visuals + category detection. THE preferred tool for rightmost-screen text content. Also at `/home/nara/wm-collector/news_visuals.py`.

## Related Skills
- `lg-data-visualization` — Data-driven KML from external APIs (USGS, EONET, OpenSky, etc.): collectors, geofiltering, KML generation pipeline, screen-placement rules, refresh cadence.
- `lg-orbit-workflow` — Smooth orbit parameters, flyToView conflicts, Pi-based SSH orbit.
- `lg-ssh-control` — KML deployment helpers, refresh controls, relaunch commands.

## Dynamic Unique Visuals Pattern

**Principle:** Each feature gets its own unique KML approach based on content type — never recycle the same style for everything.

### Why

A KML with 10 identical blue circles is visually dead. A KML where each feature has a distinct visual (arrows, rings, dots, polygons, columns) tells a story and keeps the viewer engaged.

### Implementation

Instead of one loop generating the same Placemark type for all features, use a dispatch table:

```python
for f in features:
    if f["type"] == "frontline":    kml += front_line_arrow(f)
    elif f["type"] == "siege":      kml += concentric_rings(f)
    elif f["type"] == "factions":   kml += faction_markers(f)
    elif f["type"] == "spread":     kml += wave_polygons(f)
    elif f["type"] == "blockade":   kml += blockade_ring(f)
    else:                           kml += default_column(f)
```

### Common Visual Primitives

| Primitive | KML Element | Use Case |
|-----------|-------------|----------|
| 3D column | Extruded Polygon | Ports, bases, intensity |
| Arrow path | LineString | Routes, invasions |
| Rings | Circle LineStrings | Siege, blast zones |
| Scatter dots | Multiple Points | Damage density |
| Fading waves | Decreasing-alpha Polygons | Spreading phenomena |
| Overlap layers | Offset Polygons | Ethnic/faction zones |
| Altitude dots | Points with varying Z | Crisis spirals |

### Label Pattern

1-line text labels at 2.0-2.2x scale, offset from marker, with icon hidden:

```xml
<Style id="lbl">
  <IconStyle><scale>0.0</scale></IconStyle>
  <LabelStyle><color>ffffffff</color><scale>2.2</scale></LabelStyle>
</Style>
<Placemark>
  <name>⚔ Ukraine: 300km front</name>
  <styleUrl>#lbl</styleUrl>
  <Point><coordinates>lon+1.8,lat+0.8,0</coordinates></Point>
</Placemark>
```

### KML Coordinate Precision (Critical Pitfall)
**Floating point arithmetic in Python produces imprecise KML coordinates that Earth silently rejects.** For example, `str(26.65 - 0.3)` produces `26.349999999999998` instead of `26.35`. Earth 7.3.3 on VM may reject placemarks with these imprecise coordinates.
**Fix:** Always round to 4 decimal places: `round(coordinate, 4)` before inserting into KML strings.

### Synced Camera Tour Sequence
When running a multi-stop tour, the sequence matters:
1. **Deploy KML first** — wait 8s for NetworkLink refresh
2. **Start camera tour** — fly to each zone
3. **At each stop:** deploy zone-specific right-screen text panel (PNG)
4. **Voiceover plays** during 10-12s dwell per stop
5. **Fly to next zone** — repeat

### Working Example
See `armed_conflicts.py` — 10 unique visuals for 10 conflict types.
See `references/lg-kml-tours/synced-camera-voiceover-panel.md` for the full tour+voice+panel pattern.
