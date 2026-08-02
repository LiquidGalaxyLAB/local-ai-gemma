#!/usr/bin/env python3
"""Smooth orbit around any point — writes flytoview with gx:duration + gx:flyToMode.
Deploy to lg1 and run via: setsid python3 script.py < /dev/null > /dev/null 2>&1 &"""
import time

def flytoview_str(lat, lon, rng, tilt, bearing):
    lookat = '<gx:duration>0.3</gx:duration><gx:flyToMode>smooth</gx:flyToMode><LookAt>' \
             '<longitude>%.6f</longitude><latitude>%.6f</latitude>' \
             '<range>%d</range><tilt>%d</tilt>' \
             '<heading>%.1f</heading>' \
             '<altitudeMode>relativeToGround</altitudeMode></LookAt>'
    return 'flytoview=' + (lookat % (lon, lat, rng, tilt, bearing))

def query(cmd):
    with open("/tmp/query.txt", "w") as f:
        f.write(cmd)

# ---------- CONFIGURE HERE ----------
LAT = 48.8584
LON = 2.2945
RNG = 3000
TILT = 60
STEPS = 60
STEP_DEG = 360.0 / STEPS  # 6 degrees
STEP_S = 0.4
# ------------------------------------

# Reset tour state
query('exittour=true')
time.sleep(0.1)

# Initial fly-in (3s slow)
query('flytoview=<gx:duration>3.0</gx:duration><gx:flyToMode>smooth</gx:flyToMode><LookAt><longitude>%.6f</longitude><latitude>%.6f</latitude><range>%d</range><tilt>%d</tilt><heading>0</heading><altitudeMode>relativeToGround</altitudeMode></LookAt>' % (LON, LAT, RNG, TILT))
time.sleep(3.5)

# Orbit — heading never wraps, keeps growing past 360
heading = 0.0
while True:
    query(flytoview_str(LAT, LON, RNG, TILT, heading))
    heading += STEP_DEG
    time.sleep(STEP_S)
