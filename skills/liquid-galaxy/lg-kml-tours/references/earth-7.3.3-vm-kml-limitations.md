# Earth 7.3.3 VM KML Limitations

## Environment

- **Google Earth Pro:** 7.3.3.7786 (Linux)
- **OS:** Ubuntu 14.04/16.04
- **Virtualization:** VirtualBox
- **Graphics:** VirtualBox VGA / Gallium
- **Network:** Bridged LAN (no internet access on guest)

## Symptoms

KML is deployed to `/var/www/html/kml/master.kml`, served correctly by Apache
(HTTP 200, correct `Content-Type: application/vnd.google-earth.kml+xml`),
Earth fetches it via NetworkLink every 3s (confirmed in Apache access logs),
but **nothing displays** — no placemarks, no camera movement, no errors.

## Confirmed Working KML (Minimal)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <name>Hong Kong</name>
    <LookAt>
      <longitude>114.1694</longitude>
      <latitude>22.3193</latitude>
      <range>200000</range>
      <tilt>60</tilt>
      <altitudeMode>relativeToGround</altitudeMode>
    </LookAt>
    <Placemark>
      <name>Hong Kong</name>
      <Point>
        <coordinates>114.1694,22.3193,0</coordinates>
      </Point>
    </Placemark>
  </Document>
</kml>
```

## ⚠️ CORRECTION (July 2026): gx:Tour with xmlns:gx DOES work

**Earlier version of this doc claimed adding `xmlns:gx` silently rejected the entire KML. This is INCORRECT.** gx:Tour with `xmlns:gx` has been tested and confirmed working on Earth 7.3.3.7786 (VirtualBox VM, July 2026):

- Deployed KML with `xmlns:gx="http://www.google.com/kml/ext/2.2"` 
- Contains `<gx:Tour>`, `<gx:Playlist>`, `<gx:FlyTo>`, `<gx:Wait>`
- Named "Orbit" — triggered with `echo "playtour=Orbit" > /tmp/query.txt`
- Tour played successfully — smooth orbit on all 3 screens
- Stopped with `echo "exittour=true" > /tmp/query.txt`

**What IS still rejected:** 
- `<gx:altitudeMode>` inside `<LookAt>` — use plain `<altitudeMode>` instead
- `<BalloonStyle><text><![CDATA[...]]></text></BalloonStyle>` — balloon styles with CDATA 
- External icon URLs (when VM has no internet)

**Key insight:** The gx namespace rejection may have been a false positive from other features (CDATA in balloon text, or unresolvable external icons) that happened to appear alongside xmlns:gx in the same KML. When tested in isolation with only Placemark + gx:Tour, xmlns:gx works perfectly.

## Confirmed Non-Working KML (Invisible) — Any Single Feature Breaks It

The following features, added **individually** to the minimal KML above,
cause the entire KML to become invisible:

### 1. gx Namespace in Document-level Elements (NOT gx:Tour)

**⚠️ CORRECTION:** Earlier versions claimed `xmlns:gx` itself breaks KML. This is only true for gx: namespace elements used OUTSIDE of gx:Tour. gx:Tour with gx:FlyTo/gx:Wait inside gx:Playlist works fine. What does NOT work:

```xml
<LookAt>
  <gx:altitudeMode>relativeToGround</gx:altitudeMode>  <!-- ❌ Breaks LookAt -->
</LookAt>
```

Using `<gx:altitudeMode>` inside `<LookAt>` causes Earth to silently ignore the entire LookAt. Always use plain `<altitudeMode>` instead.

**Safe pattern:**
```xml
<LookAt>
  <altitudeMode>relativeToGround</altitudeMode>  <!-- ✅ Works -->
</LookAt>
```

### 2. Style with BalloonStyle CDATA

```xml
<Style id="myIcon">
  <IconStyle>
    <scale>0.8</scale>
    <Icon>
      <href>http://maps.google.com/mapfiles/kml/pal3/icon56.png</href>
    </Icon>
  </IconStyle>
  <LabelStyle><scale>1.2</scale></LabelStyle>
  <BalloonStyle>
    <text><![CDATA[<div>styled</div>]]></text>
  </BalloonStyle>
</Style>
```

Any `<Style>` definition with `<BalloonStyle>` containing CDATA causes
the KML to go invisible. The style itself may be cached, but the entire
KML is discarded.

### 3. External Icon URL in Style

```xml
<Icon>
  <href>http://maps.google.com/mapfiles/kml/pal3/icon56.png</href>
</Icon>
```

When the VM has no internet access, the icon fails to load AND the entire
KML is rejected. Local icon references may work but are untested.

### 4. Rich HTML in `<description>` (CDATA)

```xml
<description><![CDATA[
  <b>Bold text</b><br>
  <i>Italic text</i>
]]></description>
```

While CDATA in `<description>` is standard KML, on this Earth version
it may cause the placemark to not appear at all. Plain text descriptions
work fine.

## Diagnosis Steps

When KML isn't visible:

1. **Check Apache access logs** for Earth requests:
   ```bash
   tail -f /var/log/apache2/access.log | grep 'master.kml'
   ```
   If Earth is NOT fetching, the NetworkLink refresh is broken.
   If Earth IS fetching (HTTP 200), the KML content is the problem.

2. **Simplify progressively:**
   - Strip `xmlns:gx` → no gx namespace
   - Strip all `<Style>` blocks → no styles at all
   - Strip CDATA from descriptions → plain text
   - Strip external icon URLs → just bare Placemark with Point

3. **Deploy and wait** 3-6s for the next NetworkLink refresh cycle.

## Root Cause Hypothesis

Earth 7.3.3 on Linux with VirtualBox VGA graphics may use a simplified
rendering path that silently discards KML features it cannot render or
resolve. The gx namespace suggests features this version doesn't support,
causing the parser to bail on the entire document rather than degrade
gracefully. Similarly, unresolvable external icons (no VM internet) may
cause the renderer to skip the KML entirely.

Physical LG rigs with full internet and newer Earth versions may support
all these features without issue. This limitation is specific to the
offline VirtualBox VM setup.
