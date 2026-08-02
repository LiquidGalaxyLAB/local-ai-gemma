# Google Maps KML Icon Palette (Symbol Icons)

Earth bundles the Google Maps icon set. Use `http://maps.google.com/mapfiles/kml/` URLs — they resolve from Earth's local cache, no internet needed.

## Shape Icons (`.../shapes/`)

| Icon | URL | Best for |
|------|-----|----------|
| earthquake.png | `.../shapes/earthquake.png` | Seismic events |
| fire_station.png | `.../shapes/fire_station.png` | Wildfires, fire incidents |
| volcano.png | `.../shapes/volcano.png` | Volcanic activity |
| rainy.png | `.../shapes/rainy.png` | Storms, precipitation |
| h2o.png | `.../shapes/h2o.png` | Floods, water events |
| mountains.png | `.../shapes/mountains.png` | Landslides, terrain |
| military.png | `.../shapes/military.png` | Bases, defense sites |
| target.png | `.../shapes/target.png` | Conflict zones, attacks |
| caution.png | `.../shapes/caution.png` | Warnings, alerts |
| airports.png | `.../shapes/airports.png` | Airports, aviation |
| sailing.png | `.../shapes/sailing.png` | Ships, maritime |
| electronics.png | `.../shapes/electronics.png` | Cyber, infrastructure |
| alert.png | `.../shapes/alert.png` | Outages, disruptions |
| nuclear.png | `.../shapes/nuclear.png` | Radiation, nuclear sites |
| astronomy.png | `.../shapes/astronomy.png` | Satellites, space |
| park.png | `.../shapes/park.png` | Conservation, wildlife |
| info-i.png | `.../shapes/info-i.png` | Info points, news |
| oil.png | `.../shapes/oil.png` | Pipelines, oil/gas |

## Paddle Icons (`.../paddle/`)

Colored paddles with letters/numbers. Use for generic markers that need a specific color:

| Icon | URL |
|------|-----|
| Red | `.../paddle/red-blank.png` |
| Green | `.../paddle/grn-blank.png` |
| Yellow | `.../paddle/ylw-blank.png` |
| Blue | `.../paddle/blu-blank.png` |
| Orange | `.../paddle/org-blank.png` |
| Purple | `.../paddle/purple-blank.png` |
| White | `.../paddle/wht-blank.png` |
| Letters | `.../paddle/red-<letter>.png` (e.g. `red-A.png`) |
| Numbers | `.../paddle/red-<N>.png` (e.g. `red-1.png`) |

## Full icon set list

Google maintains the complete catalog at `http://maps.google.com/mapfiles/kml/pal4/` (for the classic 64-icon palette) and `http://maps.google.com/mapfiles/ms/micons/` (for the marker icon set used in My Maps).

## Usage in KML

```xml
<Style id="s_earthquake">
  <IconStyle>
    <color>ffff0000</color>
    <scale>1.0</scale>
    <Icon>
      <href>http://maps.google.com/mapfiles/kml/shapes/earthquake.png</href>
    </Icon>
  </IconStyle>
  <LabelStyle>
    <color>ffffffff</color>
    <scale>0.8</scale>
  </LabelStyle>
</Style>
```

## VM Compatibility

✅ Works on Earth 7.3.3 in VirtualBox — tested July 2026.
The icons are bundled with Earth Pro and resolve locally. No internet connection needed on the LG VM.
