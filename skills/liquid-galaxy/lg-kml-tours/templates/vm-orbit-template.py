#!/usr/bin/env python3
"""
VM-optimized continuous orbit for Liquid Galaxy via /tmp/query.txt.

Customize the CONFIG section below, deploy to lg1, then start:
  sshpass -p 'lg' ssh -f lg@<LG-IP> "nohup python3 /home/lg/script.py > /home/lg/script.log 2>&1"

Stop:
  sshpass -p 'lg' ssh lg@<LG-IP> "kill $(pgrep -f script-name)"

Python 3.5 compatible (no f-strings).
"""
import os, time

# ── CONFIG ──
LAT = 37.0
LON = 138.0
RNG = 1500000       # 1,500km minimum for VM rigs (< 100km = blank terrain)
TILT = 50
STEPS = 72          # 72 steps x 5 deg each = 360 deg
STEP_DEG = 360.0 / STEPS
STEP_S = 1.5        # seconds between steps (VM: 1.5-2s, physical: 0.4s)
GX_DURATION = 1.5   # gx:duration — MUST match STEP_S for seamless motion. If < STEP_S, creates stutter gaps.
LOG = "/home/lg/orbit.log"
# ── END CONFIG ──

def log(msg):
    with open(LOG, "a") as f:
        f.write("%s\n" % msg)

def write_q(txt):
    """Write flytoview command to /tmp/query.txt. Atomic rename prevents partial reads."""
    tmp = "/tmp/query.txt.new"
    dst = "/tmp/query.txt"
    with open(tmp, "w") as f:
        f.write(txt)
    os.rename(tmp, dst)

log("Orbit starting: %.4f,%.4f range=%d tilt=%d" % (LON, LAT, RNG, TILT))

# Reset any stuck tour
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

# Orbit loop — heading never wraps, keeps growing past 360
log("Starting orbit loop")
heading = 0.0
step = 0
while True:
    cmd = 'flytoview=<gx:duration>%.1f</gx:duration><gx:flyToMode>smooth</gx:flyToMode>' \
          '<LookAt><longitude>%.6f</longitude><latitude>%.6f</latitude>' \
          '<range>%d</range><tilt>%d</tilt><heading>%.1f</heading>' \
          '<altitudeMode>relativeToGround</altitudeMode></LookAt>' \
          % (GX_DURATION, LON, LAT, RNG, TILT, heading)
    write_q(cmd)
    step += 1
    if step % 10 == 0:
        log("Step %d, heading %.1f" % (step, heading))
    heading += STEP_DEG
    time.sleep(STEP_S)
