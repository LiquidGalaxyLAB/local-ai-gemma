# flyToView=1: The Fix for Auto-Positioning on KML Refresh

## The Problem

Deploying a new KML to master.kml showed placemarks and polygons but the
camera never moved to the LookAt position. It stayed wherever it was
(previously flown position, default Paris view, etc.).

## Root Cause

The master NetworkLink in `~/earth/kml/master/myplaces.kml` had no
`<flyToView>` element. In KML, `flyToView` defaults to `0` (false) when
omitted. This means Earth loads KML content on every 3s refresh but
**never re-processes the Document `<LookAt>` as a camera command.**

The LookAt only worked on Earth's initial launch when myplaces.kml was
parsed for the first time.

## The Fix

Add `<flyToView>1</flyToView>` to the master KML NetworkLink:

```bash
sed -i 's|<href>##LG_PHPIFACE##kml/master.kml</href>|<href>##LG_PHPIFACE##kml/master.kml</href>\n\t\t\t\t<flyToView>1</flyToView>|' ~/earth/kml/master/myplaces.kml
```

Before:
```xml
<href>##LG_PHPIFACE##kml/master.kml</href>
<refreshMode>onInterval</refreshMode>
<refreshInterval>3</refreshInterval>
```

After:
```xml
<href>##LG_PHPIFACE##kml/master.kml</href>
<flyToView>1</flyToView>
<refreshMode>onInterval</refreshMode>
<refreshInterval>3</refreshInterval>
```

## Why It's One-Time

- `myplaces.kml` is only read at Earth startup
- But once set, `flyToView=1` applies to every future NetworkLink refresh
- HTTP caching (ETag/Last-Modified) prevents re-flying when the KML hasn't changed
- When master.kml IS updated (new content, new LookAt), ETag changes, Earth re-loads, and `flyToView=1` makes it fly to the new position

So: edit once → relaunch once → all future KML updates auto-fly.

## Verification

```bash
grep -A5 'master.kml' ~/earth/kml/master/myplaces.kml
# Expected:
#   <href>##LG_PHPIFACE##kml/master.kml</href>
#   <flyToView>1</flyToView>
#   <refreshMode>onInterval</refreshMode>
#   <refreshInterval>3</refreshInterval>
```

## Why Every KML Must Still Include a LookAt

With `flyToView=1`, every KML deployed to master.kml needs a Document-level
`<LookAt>` so Earth knows where to fly on refresh. Without it, Earth may
keep the previous camera position or behave unexpectedly.

```xml
<Document>
  <name>My KML</name>
  <LookAt>
    <longitude>...</longitude>
    <latitude>...</latitude>
    <range>...</range>
    <tilt>...</tilt>
    <heading>...</heading>
    <altitudeMode>relativeToGround</altitudeMode>
  </LookAt>
  <!-- Placemarks, etc. -->
</Document>
```

## History

This was discovered during a Paris orbit session (June 22, 2026). The KML
with the Eiffel Tower polygon and placemarks was deployed and confirmed
accessible via HTTP, but the camera stayed at the previous position.
Adding `flyToView=1` and relaunching once fixed all subsequent deployments.
