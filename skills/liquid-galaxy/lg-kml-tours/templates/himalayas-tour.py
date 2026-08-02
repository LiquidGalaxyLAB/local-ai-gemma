#!/usr/bin/env python3
"""R3DKML cinematic tour — multi-stop flyover with orbits via /tmp/query.txt.

This is the "R3DKML" pattern: deploy a static KML to master.kml once, then let
this script control the camera via /tmp/query.txt. No gx:Tour, no Play click needed.

Usage:
  1. SCP this script + himalayas-tour.kml (or any KML with placemarks) to lg1
  2. Deploy the KML via the helper pattern (see lg-ssh-control)
  3. Start: ssh -f nohup python3 himalayas-tour.py > tour.log 2>&1
  4. Stop:  kill $(pgrep -f himalayas-tour)

STUTTER-FREE PATTERN:
  - gx:duration (1.5) equals step interval (1.5) — no gaps
  - os.remove(path) before write — no partial file reads
  - 72 steps at 5deg per step — smooth rotation

Customize LON/LAT/RNG/TILT per stop below for any region.
"""
import os, time

LOG = "/home/lg/tour.log"

def log(msg):
    with open(LOG, "a") as f:
        f.write("%s\n" % msg)

def write_q(txt):
    """Delete before write to prevent daemon from reading partial content."""
    path = "/tmp/query.txt"
    try:
        os.remove(path)
    except OSError:
        pass
    with open(path, "w") as f:
        f.write(txt)

def flyto(lon, lat, rng, tilt, hdg, dur=5.0):
    cmd = ('flytoview=<gx:duration>%.1f</gx:duration><gx:flyToMode>smooth</gx:flyToMode>'
           '<LookAt><longitude>%.4f</longitude><latitude>%.4f</latitude>'
           '<range>%d</range><tilt>%d</tilt><heading>%.1f</heading>'
           '<altitudeMode>relativeToGround</altitudeMode></LookAt>') % (dur, lon, lat, rng, tilt, hdg)
    write_q(cmd)

def stop_at(lon, lat, rng, tilt, hdg, name, fly_dur=5.0, wait=5.0):
    log("Flying to: %s" % name)
    flyto(lon, lat, rng, tilt, hdg, fly_dur)
    time.sleep(wait)

def orbit_at(lon, lat, rng, tilt, steps=72):
    """Smooth orbit — gx:duration matches step interval to prevent stutter."""
    hdg = 0.0
    for step in range(steps):
        flyto(lon, lat, rng, tilt, hdg, 1.5)
        hdg += 5.0  # 360/72
        if step % 12 == 0:
            log("Orbit step %d, heading %.1f" % (step, hdg))
        time.sleep(1.5)

log("=== Tour Started ===")
write_q("exittour=true")
time.sleep(1)

# ════════════════════════════════════════════
# CUSTOMIZE YOUR STOPS HERE
# ════════════════════════════════════════════

# 1. Wide overview
flyto(82.0, 30.0, 2500000, 45, 180, 4.0)
time.sleep(6)

# 2. Stop + orbit at each location
stop_at(88.1476, 27.7021, 250000, 55, 0, "Kanchenjunga", 5.0, 6.0)
orbit_at(88.1476, 27.7021, 250000, 55, 72)

stop_at(79.9707, 30.3758, 200000, 55, 0, "Nanda Devi", 6.0, 6.0)
orbit_at(79.9707, 30.3758, 200000, 55, 36)

stop_at(77.5770, 34.1526, 300000, 50, 0, "Leh, Ladakh", 7.0, 6.0)
orbit_at(77.5770, 34.1526, 300000, 50, 36)

# 3. Final overview
flyto(82.0, 31.0, 3500000, 35, 180, 6.0)
time.sleep(6)

write_q("exittour=true")
log("=== Tour Complete ===")
