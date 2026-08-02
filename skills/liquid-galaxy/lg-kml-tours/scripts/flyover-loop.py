#!/usr/bin/env python3
"""Continuous global flyover - updates master.kml every 3s. Runs on lg1.

Deploy:
  scp flyover-loop.py lg@<LG-IP>:/home/lg/
  ssh lg@<LG-IP> "nohup python3 /home/lg/flyover-loop.py > /home/lg/flyover-loop.log 2>&1 &"

Stop:
  ssh lg@<LG-IP> "pkill -f flyover-loop"
"""
import math, time, subprocess

PW = "lg"

# Key waypoints: (lon, lat, heading, tilt, range_m)
STEPS = [
  (-60.0, 0.0, 0.0, 0.0, 20000000),
  (-60.0, -10.0, 270.0, 45.0, 5000000),
  (-70.0, -10.0, 270.0, 55.0, 1000000),
  (-60.0, -5.0, 180.0, 50.0, 3000000),
  (-80.0, 30.0, 270.0, 55.0, 500000),
  (-105.0, 35.0, 315.0, 60.0, 200000),
  (-75.0, 40.0, 90.0, 55.0, 500000),
  (-74.0, 40.7, 90.0, 65.0, 5000),
  (-60.0, 45.0, 45.0, 50.0, 3000000),
  (0.0, 50.0, 90.0, 55.0, 200000),
  (2.3, 48.9, 180.0, 65.0, 2000),
  (12.5, 41.9, 135.0, 60.0, 100000),
  (12.5, 41.9, 180.0, 70.0, 1000),
  (20.0, 35.0, 90.0, 55.0, 2000000),
  (31.1, 29.9, 180.0, 55.0, 200000),
  (31.1, 29.9, 180.0, 70.0, 2000),
  (35.0, 25.0, 45.0, 50.0, 3000000),
  (50.0, 25.0, 45.0, 55.0, 500000),
  (60.0, 25.0, 90.0, 55.0, 1000000),
  (70.0, 22.0, 135.0, 55.0, 1000000),
  (78.5, 20.5, 45.0, 55.0, 400000),
  (90.0, 22.0, 90.0, 55.0, 1000000),
  (100.0, 20.0, 90.0, 55.0, 1000000),
  (105.0, 15.0, 90.0, 55.0, 1000000),
  (116.0, 40.0, 270.0, 60.0, 50000),
  (140.0, 35.0, 90.0, 55.0, 2000000),
  (180.0, 0.0, 0.0, 0.0, 20000000),
]

def smoothstep(t):
    return t * t * (3.0 - 2.0 * t)

def lerp(a, b, t):
    return a + (b - a) * t

# Generate interpolated path
FULL = []
for w in range(len(STEPS) - 1):
    w0 = STEPS[w]
    w1 = STEPS[w + 1]
    for i in range(8):
        t = float(i) / 8.0
        e = smoothstep(t)
        lon = lerp(w0[0], w1[0], e)
        lat = lerp(w0[1], w1[1], e)
        h = lerp(w0[2], w1[2], e)
        tilt = lerp(w0[3], w1[3], e)
        rng = int(lerp(w0[4], w1[4], e))
        FULL.append((lon, lat, h, tilt, rng))

# Cylinder polygon (from previous session)
cyl_lat = 20.5
cyl_lon = 78.5
cos_lat = math.cos(math.radians(cyl_lat))
cyl_parts = []
for i in range(7):
    a = 2.0 * math.pi * float(i) / 6.0
    dlat = 2.0 * math.cos(a)
    dlon = 2.0 * math.sin(a) / cos_lat
    cyl_parts.append("%.6f,%.6f,100000" % (cyl_lon + dlon, cyl_lat + dlat))
cyl_str = " ".join(cyl_parts)

step = 0
while True:
    idx = step % len(FULL)
    lon, lat, heading, tilt, rng = FULL[idx]

    lines = []
    lines.append('<?xml version="1.0" encoding="UTF-8"?>')
    lines.append('<kml xmlns="http://www.opengis.net/kml/2.2">')
    lines.append('  <Document>')
    lines.append('    <name>Global Flyover</name>')
    lines.append('    <LookAt>')
    lines.append('      <longitude>%.6f</longitude>' % lon)
    lines.append('      <latitude>%.6f</latitude>' % lat)
    lines.append('      <altitude>0</altitude>')
    lines.append('      <heading>%.1f</heading>' % heading)
    lines.append('      <tilt>%.0f</tilt>' % tilt)
    lines.append('      <range>%d</range>' % rng)
    lines.append('      <altitudeMode>relativeToGround</altitudeMode>')
    lines.append('    </LookAt>')
    lines.append('    <Placemark>')
    lines.append('      <name>India Cylinder</name>')
    lines.append('      <visibility>1</visibility>')
    lines.append('      <Style>')
    lines.append('        <PolyStyle><color>7fff8800</color><outline>1</outline></PolyStyle>')
    lines.append('        <LineStyle><color>ffff8800</color><width>2</width></LineStyle>')
    lines.append('      </Style>')
    lines.append('      <Polygon>')
    lines.append('        <extrude>1</extrude>')
    lines.append('        <altitudeMode>relativeToGround</altitudeMode>')
    lines.append('        <outerBoundaryIs>')
    lines.append('          <LinearRing>')
    lines.append('            <coordinates>%s</coordinates>' % cyl_str)
    lines.append('          </LinearRing>')
    lines.append('        </outerBoundaryIs>')
    lines.append('      </Polygon>')
    lines.append('    </Placemark>')
    lines.append('  </Document>')
    lines.append('</kml>')

    kml = "\n".join(lines)

    with open("/tmp/flyover_kml", "w") as f:
        f.write(kml)

    subprocess.run(["sudo", "-S", "cp", "/tmp/flyover_kml", "/var/www/html/kml/master.kml"],
                   input=(PW + "\n").encode(), check=True)

    step += 1
    time.sleep(3)
