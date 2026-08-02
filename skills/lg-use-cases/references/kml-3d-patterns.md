# 3D KML Patterns for LG VM Earth 7.3.3

Tested patterns that work on VirtualBox Google Earth 7.3.3 (no gx namespace, no CDATA).

## 3D Extruded Column (Intensity Visual)

Height = intensity × 20000-30000m. Color by category (ABGR).

```xml
<Style id="col_example">
  <PolyStyle><color>8f0000ff</color><fill>1</fill><outline>0</outline></PolyStyle>
</Style>
<Placemark>
  <name></name>
  <styleUrl>#col_example</styleUrl>
  <Polygon><extrude>1</extrude>
    <altitudeMode>relativeToGround</altitudeMode>
    <outerBoundaryIs><LinearRing>
      <coordinates>lon-0.3,lat-0.3,0 lon+0.3,lat-0.3,0 lon+0.3,lat+0.3,0 lon-0.3,lat+0.3,0 lon-0.3,lat-0.3,0</coordinates>
    </LinearRing></outerBoundaryIs>
  </Polygon>
</Placemark>
```

## Chokepoint Arrow Path

```xml
<Style id="arrow"><LineStyle><color>ffff0000</color><width>5</width></LineStyle></Style>
<Placemark><name></name><styleUrl>#arrow</styleUrl>
  <LineString><extrude>1</extrude><altitudeMode>relativeToGround</altitudeMode>
    <coordinates>lon1,lat1,10000 lon2,lat2,10000</coordinates>
  </LineString>
</Placemark>
```

## Concentric Siege Rings

Generate 4 rings at r=0.12, 0.24, 0.36, 0.48 deg with 20 points each.

## 1-Line Text Labels

Scale 2.2, offset 1.8° lon + 0.8° lat from marker. No icon. White color.

```xml
<Style id="txt"><IconStyle><scale>0.0</scale></IconStyle>
  <LabelStyle><color>ffffffff</color><scale>2.2</scale></LabelStyle></Style>
<Placemark><name>One line max 80 chars</name>
  <styleUrl>#txt</styleUrl>
  <Point><coordinates>lon+1.8,lat+0.8,0</coordinates></Point>
</Placemark>
```

## Color-Coding Convention

| Category | ABGR | Use |
|----------|------|-----|
| Battle/War | `ffff0000` | Active combat |
| Siege/Blockade | `ffff4400` | Urban siege |
| Protest | `ff0088ff` | Civil unrest |
| Displacement | `ffff6600` | Refugee flows |
| Military/Naval | `ff00ff00` | Bases |
| Ports/Trade | `ffff0000` (blue) | Commercial |
| Oil/Energy | `ff882200` | Terminals |
| Crisis | `ffff8822` | Humanitarian |
| Border | `ff44aaff` | LoC tensions |
