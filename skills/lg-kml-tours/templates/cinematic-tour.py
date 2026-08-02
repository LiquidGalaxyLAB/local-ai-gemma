#!/usr/bin/env python3
"""
Cinematic multi-stop tour template for Liquid Galaxy.
Flies between locations via /tmp/query.txt — no Play click needed.
"""
import os, time

LOG = "/home/lg/tour.log"

def log(msg):
    with open(LOG, "a") as f:
        f.write("%s\n" % msg)

def write_q(txt):
    path = "/tmp/query.txt"
    try:
        os.remove(path)
    except OSError:
        pass
    with open(path, "w") as f:
        f.write(txt)

def flyto(lon, lat, rng, tilt, hdg, dur=4.0):
    cmd = 'flytoview=<gx:duration>%.1f</gx:duration><gx:flyToMode>smooth</gx:flyToMode><LookAt><longitude>%.6f</longitude><latitude>%.6f</latitude><range>%d</range><tilt>%d</tilt><heading>%.1f</heading><altitudeMode>relativeToGround</altitudeMode></LookAt>' % (dur, lon, lat, rng, tilt, hdg)
    write_q(cmd)

def wait(s):
    time.sleep(s)

log("Tour starting")

# Reset any stuck camera state
write_q("exittour=true")
wait(0.5)

# === EDIT YOUR TOUR STOPS BELOW ===
# Format: flyto(lon, lat, range(m), tilt(deg), heading(deg), duration(s))
# Use larger range for wide views, smaller for close-ups
# Duration: 4-6s for smooth transitions between stops

# Stop 1: Wide overview
log("1/N - Overview")
flyto(86.9, 27.9, 200000, 50, 0, 5.0)
wait(6)

# Stop 2: Close-up
log("2/N - Close-up")
flyto(86.925, 27.988, 8000, 65, 180, 5.0)
wait(6)

# Add more stops here...

# Final stop: Orbit around last location
log("N/N - Final orbit")
flyto(86.925, 27.988, 20000, 55, 0, 4.0)
wait(5)

heading = 0.0
for step in range(60):
    cmd = 'flytoview=<gx:duration>1.0</gx:duration><gx:flyToMode>smooth</gx:flyToMode><LookAt><longitude>%.6f</longitude><latitude>%.6f</latitude><range>%d</range><tilt>%d</tilt><heading>%.1f</heading><altitudeMode>relativeToGround</altitudeMode></LookAt>' % (86.925, 27.988, 20000, 55, heading)
    write_q(cmd)
    heading += 6.0
    time.sleep(1.5)

log("Tour complete")
