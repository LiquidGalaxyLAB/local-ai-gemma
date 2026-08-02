# Smart KML Visual Types

Reusable visual pattern for context-aware KML generation. Each data type maps to
a specific KML style (3D extruded column, region polygon, glow rings, paddle icons).
Used by: news-storyteller, armed-conflicts, natural-disasters.

## Visual Type System

| Topic Keywords | Style | Visual Element | ABGR Fill | Use Case |
|---------------|-------|---------------|-----------|----------|
| flood, rain | flood | 🔵 Blue 3D extruded block (50km) | `7fff0000` | Weather, disasters |
| cyclone, storm | storm | 🟤 Orange-brown zone | `7f00aaff` | Weather |
| protest, education, reform | protest | 🟠 Orange semi-transparent zone | `7f0088ff` | News, conflicts |
| sport, gold, boxer, commonwealth | sport | 🟡 Gold paddle icons | `7f00ccff` | Sports news |
| military, army | military | 🟢 Green markers | `7f00ff00` | Conflicts, bases |
| earthquake | quake | 🔴 Red zone | `7f0000ff` | Disasters |
| fire | fire | 🔴 Red-orange zone | `7f0044ff` | Wildfires |
| crime | crime | 🔴 Red markers | `7f0000ff` | Conflicts, news |
| battle | battle | 🔴 Red 3D column + volcano glow | `7f0000ff` | Armed conflicts |
| (default) | default | 🔵 Blue circle icon | — | General |

## 3D Extruded Column (Advanced)

```xml
<Placemark>
  <name></name>
  <styleUrl>#col_battle</styleUrl>
  <Polygon>
    <extrude>1</extrude>
    <altitudeMode>relativeToGround</altitudeMode>
    <outerBoundaryIs>
      <LinearRing>
        <coordinates>lon-1.5,lat-1.5,0 ... lon+1.5,lat+1.5,height</coordinates>
      </LinearRing>
    </outerBoundaryIs>
  </Polygon>
</Placemark>
```

Height = intensity × 20,000m (20km to 100km).

## Glow Rings (Concentric)

Three overlapping icons at decreasing scale for pulsing effect:

```xml
<Style id="glow1"><IconStyle><scale>3.0</scale><color>40ff0000</color>...</Style>
<Style id="glow2"><IconStyle><scale>2.0</scale><color>70ff0000</color>...</Style>
<Style id="glow3"><IconStyle><scale>1.2</scale><color>ffff0000</color>...</Style>
```

Place all three at the same coordinate for a glowing concentric effect.

## Region Polygon (Extruded)

```xml
<Placemark>
  <name></name>
  <styleUrl>#poly_battle</styleUrl>
  <Polygon>
    <extrude>1</extrude>
    <altitudeMode>relativeToGround</altitudeMode>
    <outerBoundaryIs>
      <LinearRing>
        <coordinates>lon1,lat1,0 lon2,lat2,0 ... lonN,latN,0</coordinates>
      </LinearRing>
    </outerBoundaryIs>
  </Polygon>
</Placemark>
```

PolyStyle color with alpha (e.g. `7f0000ff` = semi-transparent red).
LineStyle stroke (e.g. `ff0000ff` = opaque red, 3px width).

## Color Format (ABGR)

Google Earth uses Alpha-Blue-Green-Red byte order:
- `ffff0000` = opaque blue
- `ff00ff00` = opaque green  
- `ff0000ff` = opaque red
- `ff00ffff` = opaque yellow
- `ff0088ff` = opaque orange (B=00, G=88, R=ff)
- `7f` prefix = 50% alpha (semi-transparent)

## KML Rule Checklist

- [ ] No gx: namespace
- [ ] No CDATA in descriptions — use `html.escape()` only
- [ ] No local icon URLs — use Google CDN: `http://maps.google.com/mapfiles/kml/`
- [ ] Empty `<name></name>` on all placemarks (text goes to right screen)
- [ ] Include `<LookAt>` in Document for initial camera position
- [ ] All styles defined before any Placemark elements
