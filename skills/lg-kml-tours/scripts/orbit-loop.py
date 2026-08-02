#!/usr/bin/env python3
"""
Continuous camera orbit for Liquid Galaxy.

Runs on lg1, updates /var/www/html/kml/master.kml every 3s with an incremental
heading. The LG's 3s master NetworkLink refresh picks up each change, creating
a smooth orbit without any user interaction (no Play button needed).

Customize the constants at the top before deploying.

Requirements: Python 3.5+ on lg1, sudo access (PW="lg")
"""

import math
import time
import subprocess

# ── CONFIGURE THESE ──
TARGET_LON = 78.5
TARGET_LAT = 20.5
STEPS = 48              # Number of positions in one full rotation
ORBIT_RANGE = 400000    # Camera distance from target (meters)
TILT = 55               # Viewing angle (0=top-down, 90=horizontal)
SLEEP_SECS = 3          # Must match master.kml NetworkLink refresh interval
PW = "lg"               # sudo password on the LG VM

# ── Cylinder/Feature polygon (6-segment, lightweight) ──
# Replace this with whatever KML geometry you want visible during the orbit
RADIUS_DEG = 2.0
FEATURE_ALTITUDE = 100000

cyl_coords = []
cos_lat = math.cos(math.radians(TARGET_LAT))
for i in range(7):
    a = 2 * math.pi * i / 6
    dlat = RADIUS_DEG * math.cos(a)
    dlon = RADIUS_DEG * math.sin(a) / cos_lat
    cyl_coords.append("%.6f,%.6f,%d" % (TARGET_LON + dlon, TARGET_LAT + dlat, FEATURE_ALTITUDE))
cyl_str = " ".join(cyl_coords)

# ── Build helper (no f-strings — Python 3.5 compat) ──
def make_kml(lon, lat, heading, tilt, rng):
    lines = []
    lines.append('<?xml version="1.0" encoding="UTF-8"?>')
    lines.append('<kml xmlns="http://www.opengis.net/kml/2.2"')
    lines.append('     xmlns:gx="http://www.google.com/kml/ext/2.2">')
    lines.append('  <Document>')
    lines.append('    <name>Continuous Orbit</name>')
    lines.append('    <LookAt>')
    lines.append('      <longitude>%.6f</longitude>' % lon)
    lines.append('      <latitude>%.6f</latitude>' % lat)
    lines.append('      <altitude>0</altitude>')
    lines.append('      <heading>%.1f</heading>' % heading)
    lines.append('      <tilt>%d</tilt>' % tilt)
    lines.append('      <range>%d</range>' % rng)
    lines.append('      <altitudeMode>relativeToGround</altitudeMode>')
    lines.append('    </LookAt>')
    lines.append('    <Placemark>')
    lines.append('      <name>Feature</name>')
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
    return "\n".join(lines)

# ── Main loop ──
step = 0
print("Orbit loop starting: %d steps, %ds each, %.1fs per rotation" % (
    STEPS, SLEEP_SECS, STEPS * SLEEP_SECS))

while True:
    heading = (step % STEPS) * 360.0 / STEPS
    kml = make_kml(TARGET_LON, TARGET_LAT, heading, TILT, ORBIT_RANGE)

    with open("/tmp/orbit_kml", "w") as f:
        f.write(kml)

    subprocess.run(
        ["sudo", "-S", "cp", "/tmp/orbit_kml", "/var/www/html/kml/master.kml"],
        input=(PW + "\n").encode(),
        check=True,
        timeout=10
    )

    step += 1
    time.sleep(SLEEP_SECS)
