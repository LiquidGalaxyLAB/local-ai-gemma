#!/usr/bin/env python3
"""Smooth orbit for VM-based LG rigs. Slower steps, Python 3.5 compatible.
Deploy to lg1 then start via: ssh -f nohup python3 script.py > log 2>&1

Customize CONFIG section, then run:
  sshpass -p 'lg' scp vm-smooth-orbit.py lg@<IP>:/home/lg/
  sshpass -p 'lg' ssh -f -o StrictHostKeyChecking=no lg@<IP> \\
    "nohup python3 /home/lg/vm-smooth-orbit.py > /home/lg/orbit.log 2>&1"
"""
import time

# ── CONFIG ──
LAT = 27.1751    # Target latitude
LON = 78.0422    # Target longitude
RNG = 3000       # Camera distance (meters)
TILT = 65        # Viewing angle (0=top-down, 90=horizon)
STEPS = 72       # Steps per full rotation (72 = 5 deg per step)
STEP_S = 1.5     # Seconds between steps (VM-safe: 1.0-1.5s)
DUR = 1.0        # gx:duration per step (match ~2/3 of STEP_S)
# ── END CONFIG ──

STEP_DEG = 360.0 / STEPS
LOG = "/home/lg/orbit.log"

def log(msg):
    with open(LOG, "a") as f:
        f.write("%s\n" % msg)

def write_q(txt):
    with open("/tmp/query.txt", "w") as f:
        f.write(txt)

log("Orbit starting: %.4f,%.4f rng=%d tilt=%d %d steps %.1fs each" % (
    LON, LAT, RNG, TILT, STEPS, STEP_S))

# Reset tour state
write_q("exittour=true")
time.sleep(0.5)

# Slow fly-in
flyin = 'flytoview=<gx:duration>4.0</gx:duration><gx:flyToMode>smooth</gx:flyToMode>' \
        '<LookAt><longitude>%.6f</longitude><latitude>%.6f</latitude>' \
        '<range>%d</range><tilt>%d</tilt><heading>0</heading>' \
        '<altitudeMode>relativeToGround</altitudeMode></LookAt>' % (LON, LAT, RNG, TILT)
write_q(flyin)
log("Fly-in sent")
time.sleep(5)

# Orbit — heading keeps growing past 360 (no wrap)
heading = 0.0
step = 0
while True:
    cmd = 'flytoview=<gx:duration>%.1f</gx:duration><gx:flyToMode>smooth</gx:flyToMode>' \
          '<LookAt><longitude>%.6f</longitude><latitude>%.6f</latitude>' \
          '<range>%d</range><tilt>%d</tilt><heading>%.1f</heading>' \
          '<altitudeMode>relativeToGround</altitudeMode></LookAt>' % (DUR, LON, LAT, RNG, TILT, heading)
    write_q(cmd)
    step += 1
    if step % 24 == 0:
        log("Step %d, heading %.1f" % (step, heading))
    heading += STEP_DEG
    time.sleep(STEP_S)
