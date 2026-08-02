#!/bin/bash
# Pi-based orbit — sends flytoview commands via SSH from the Pi to the LG.
# Each step is an atomic SSH echo, avoiding local script write-timing issues.
#
# Why Pi-based instead of running on lg1:
#   • Each SSH "echo > /tmp/query.txt" is one atomic operation — no truncation/rename races
#   • Overlap pattern is built in: gx:duration > step interval
#   • No Python 3.5 f-string issues, no nohup management
#   • Works whether lg1 is physical or VM
#
# Usage:
#   bash pi-orbit-template.sh
#
# Customize the CONFIG section, save to anywhere on the Pi, and run.
# ── CONFIG ──
IP="192.168.1.200"   # LG master IP
PW="lg"              # SSH password
LON="78.0422"        # Target longitude
LAT="27.1751"        # Target latitude
RNG="100000"         # Camera range (meters) for final zoom and orbit
TILT="60"            # Camera tilt (degrees) for final zoom and orbit
STEPS=72             # Steps per full rotation (72 x 5 deg = 360)
DUR="2.5"            # gx:duration — should be ~25% longer than INTERVAL (overlap)
INTERVAL=2           # sleep between steps (seconds)
# ── END CONFIG ──

CONNECT="-o StrictHostKeyChecking=no -o ConnectTimeout=3"

send() {
  sshpass -p "$PW" ssh $CONNECT lg@"$IP" \
    "echo 'flytoview=<gx:duration>$1</gx:duration><gx:flyToMode>smooth</gx:flyToMode><LookAt><longitude>$LON</longitude><latitude>$LAT</latitude><range>$3</range><tilt>$4</tilt><heading>$2</heading><altitudeMode>relativeToGround</altitudeMode></LookAt>' > /tmp/query.txt" 2>/dev/null
}

flyto_ssh() {
  sshpass -p "$PW" ssh $CONNECT lg@"$IP" \
    "echo 'flytoview=<gx:duration>$1</gx:duration><gx:flyToMode>smooth</gx:flyToMode><LookAt><longitude>$2</longitude><latitude>$3</latitude><range>$4</range><tilt>$5</tilt><heading>$6</heading><altitudeMode>relativeToGround</altitudeMode></LookAt>' > /tmp/query.txt" 2>/dev/null
}

echo "=== Pi orbit: $LON, $LAT final_range=$RNG tilt=$TILT ==="

# 1. Reset any stuck tour
sshpass -p "$PW" ssh $CONNECT lg@"$IP" "echo 'exittour=true' > /tmp/query.txt" 2>/dev/null
sleep 1

# 2. Three-stage fly-in (prevents wild camera glitches on large geographic jumps)
echo "Stage 1: overview"
flyto_ssh 5.0 $LON $LAT 3000000 40 0
sleep 6

echo "Stage 2: intermediate"
flyto_ssh 5.0 $LON $LAT 500000 50 0
sleep 6

echo "Stage 3: close zoom"
flyto_ssh 5.0 $LON $LAT $RNG $TILT 0
sleep 7

# 3. Reset state again before orbit
sshpass -p "$PW" ssh $CONNECT lg@"$IP" "echo 'exittour=true' > /tmp/query.txt" 2>/dev/null
sleep 1

# 4. Orbit loop — heading never wraps, keeps growing past 360
echo "Starting orbit ($STEPS steps)"
HDG=0
for step in $(seq 1 $STEPS); do
  send "$DUR" "$HDG" "$RNG" "$TILT"
  HDG=$((HDG + 360 / STEPS))
  sleep "$INTERVAL"
done

# 5. Clean up
sshpass -p "$PW" ssh $CONNECT lg@"$IP" "echo 'exittour=true' > /tmp/query.txt" 2>/dev/null
echo "=== Orbit complete ==="
