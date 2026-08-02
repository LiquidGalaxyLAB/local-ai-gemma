# USGS Earthquake API → LG KML

## API Endpoint

```
GET https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/4.5_week.geojson
```

- Returns all M4.5+ earthquakes globally in the last 7 days as GeoJSON
- No API key required
- Update cadence: ~5-10 minutes
- Headers: `User-Agent: <app-name>/1.0`, `Accept: application/json`

## Response Format (GeoJSON FeatureCollection)

```json
{
  "type": "FeatureCollection",
  "metadata": { "generated": 1234567890, "count": 42 },
  "features": [{
    "type": "Feature",
    "id": "us6000tazy",
    "properties": {
      "mag": 4.5,
      "place": "7 km NNW of Ābdānān, Iran",
      "time": 1720451234567,
      "updated": 1720452000000,
      "url": "https://earthquake.usgs.gov/earthquakes/eventpage/us6000tazy",
      "detail": "...",
      "magType": "mb",
      "type": "earthquake"
    },
    "geometry": {
      "type": "Point",
      "coordinates": [47.3941, 33.0578, 10.0]
    }
  }]
}
```

`coordinates` = `[longitude, latitude, depth_km]`

## Region Filter (Bounding Box)

Apply before generating KML to keep the dataset manageable:

```python
def in_bbox(lat, lon, bbox):
    """bbox: [lat_min, lat_max, lon_min, lon_max]"""
    return bbox[0] <= lat <= bbox[1] and bbox[2] <= lon <= bbox[3]
```

**Middle East example:** `[12.0, 40.0, 35.0, 60.0]`

## KML Generation

### Magnitude Color Scale

| Range | Color (ABGR) | Style Name | Scale | Meaning |
|-------|-------------|-----------|-------|---------|
| M4.0–4.5 | `ff00ff00` (green) | `s_green` | 0.6 | Minor |
| M4.5–5.0 | `ff00ffff` (yellow) | `s_yellow` | 0.8 | Light |
| M5.0–5.5 | `ff0066ff` (orange) | `s_orange` | 1.0 | Moderate |
| M5.5–6.0 | `ff0000ff` (red) | `s_red` | 1.3 | Strong |
| M6.0+ | `ff000099` (dark red) | `s_darkred` | 1.6 | Major |

### Placemark Template

```xml
<Placemark>
  <name>M{mag:.1f} — {place}</name>
  <description><![CDATA[
    Magnitude: {mag:.1f}<br/>
    Depth: {depth:.0f} km<br/>
    Location: {place}<br/>
    Time: {time_str}<br/>
    USGS: <a href='{url}'>{id}</a>
  ]]></description>
  <styleUrl>#{style_id}</styleUrl>
  <Point>
    <coordinates>{lon},{lat},0</coordinates>
  </Point>
</Placemark>
```

### Style Template

```xml
<Style id="s_yellow">
  <IconStyle>
    <color>ff00ffff</color>
    <scale>0.8</scale>
  </IconStyle>
  <LabelStyle>
    <color>ffffffff</color>
    <scale>0.9</scale>
  </LabelStyle>
</Style>
```

### Required Document Elements

```xml
<Document>
  <name>WM Middle East Monitor</name>
  <LookAt>
    <longitude>48.0</longitude>
    <latitude>26.0</latitude>
    <altitude>0</latitude>
    <heading>0</heading>
    <tilt>50</tilt>
    <range>3000000</range>
    <altitudeMode>relativeToGround</altitudeMode>
  </LookAt>
  <!-- Styles then Placemarks -->
</Document>
```

## Deploy Command (Working)

```bash
# SCP
sshpass -p 'lg' scp -o StrictHostKeyChecking=no /tmp/wm-eq.kml lg@<LG-IP>:/home/lg/wm-eq.kml

# Deploy via Python subprocess (NOT echo | sudo -S which hangs over sshpass)
sshpass -p 'lg' ssh -o StrictHostKeyChecking=no lg@<LG-IP> \
  'python3 -c "import subprocess; subprocess.run([\"sudo\", \"-S\", \"cp\", \"/home/lg/wm-eq.kml\", \"/var/www/html/kml/master.kml\"], input=b\"lg\\n\", check=True)"'
```

## Collector Script Location

On this Pi: `/home/nara/wm-collector/collector.py`

Run: `cd /home/nara/wm-collector && python3 collector.py`

## Cadence

Recommended cron: every 30 minutes. USGS updates every 5-10 min but daily data is sufficient for LG display.
