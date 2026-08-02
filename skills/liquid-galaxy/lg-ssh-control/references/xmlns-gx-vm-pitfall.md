# xmlns:gx Namespace on NetworkLink-Loaded KML (VM Earth 7.3.3)

## The Rule

**NEVER add `xmlns:gx="http://www.google.com/kml/ext/2.2"` to any KML file that Google Earth fetches via NetworkLink.** This includes `master.kml`, `slave_2.kml`, `slave_3.kml`, and any other KML served from Apache and loaded by Earth's 3s refresh.

On Earth 7.3.3 running on VirtualBox, the gx namespace in a NetworkLink-loaded KML causes **all Placemarks to be silently dropped**. The file is fetched (HTTP 200 visible in Apache logs), but no content renders. No error, no warning — just invisible.

## What Works

- **`xmlns:gx` works in master.kml loaded directly at Earth startup** (via myplaces.kml NetworkLink that's parsed on launch). gx:Tour with gx:FlyTo/gx:Wait inside gx:Playlist renders fine.
- **Plain `xmlns="http://www.opengis.net/kml/2.2"` always works** — no gx namespace, no problem.
- **`gx:balloonVisibility` works ONLY when the gx namespace IS declared.** Since the namespace breaks NetworkLink KML, `gx:balloonVisibility` CANNOT be used in slave KMLs. See below for the workaround.

## Balloon Workaround for Slave Screens

Since `gx:balloonVisibility` requires the namespace that silently kills the KML:

1. Use `<BalloonStyle><bgColor>bb000000</bgColor><text>ESCAPED_HTML_HERE</text></BalloonStyle>` in a `<Style>`
2. Include the same escaped HTML in a `<description>` element on the Placemark
3. The balloon will auto-open when the placemark has focus
4. Point at `(0,0,0)` so it doesn't clutter the Earth surface

```xml
<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
 <Document>
  <name>Balloon</name>
  <Placemark>
    <name>Info</name>
    <description>&lt;div&gt;...escaped HTML...&lt;/div&gt;</description>
    <Style>
      <BalloonStyle>
        <bgColor>bb000000</bgColor>
        <text>&lt;div&gt;...escaped HTML...&lt;/div&gt;</text>
      </BalloonStyle>
    </Style>
    <Point><coordinates>0,0,0</coordinates></Point>
  </Placemark>
 </Document>
</kml>
```

## Verification

If you deploy a slave KML and Apache shows HTTP 200 but nothing renders:
1. Check for `xmlns:gx` in the KML file → remove it
2. Check for CDATA (`<![CDATA[`) anywhere → replace with escaped HTML
3. Deploy with just the plain KML namespace

## References

- Discovered and verified Aug 2026 on this rig (Earth 7.3.3, VirtualBox)
- Related: `kml-cdata-and-icons.md` (CDATA rejection), `earth-7.3.3-vm-kml-limitations.md` (full VM KML constraints)
