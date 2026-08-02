#!/usr/bin/env python3
"""Customizable orbit template — fill in LAT, LON, RNG, TILT, then deploy to lg1."""
import time

LAT = 48.8584    # Target latitude
LON = 2.2945     # Target longitude
RNG = 3000       # Orbit range in meters
TILT = 60        # Camera tilt (0=top-down, 90=horizontal)
STEPS = 60       # Steps per full rotation (60 = smooth)
STEP_DEG = 360.0 / STEPS   # Degrees per step (6.0)
STEP_S = 0.4     # Seconds between steps (400ms)

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

# 1. Reset any active tour
query('exittour=true')
time.sleep(0.1)

# 2. Initial fly-in (3s slow, then wait for it to complete)
query('flytoview=<gx:duration>3.0</gx:duration><gx:flyToMode>smooth</gx:flyToMode><LookAt><longitude>%.6f</longitude><latitude>%.6f</latitude><range>%d</range><tilt>%d</tilt><heading>0</heading><altitudeMode>relativeToGround</altitudeMode></LookAt>' % (LON, LAT, RNG, TILT))

# 3. Wait for fly-in before orbiting
time.sleep(3.5)

# 4. Orbit — heading NEVER wraps back to 0
heading = 0.0
while True:
    query(flytoview_str(LAT, LON, RNG, TILT, heading))
    heading += STEP_DEG
    time.sleep(STEP_S)
