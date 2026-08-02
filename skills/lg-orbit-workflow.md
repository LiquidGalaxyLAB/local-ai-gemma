---
name: lg-orbit-workflow
description: Smooth LG orbit via Pi-based SSH commands with overlap timing. Fixes stutter from flyToView=1 conflicts and /tmp/query.txt write races.
---

# LG Smooth Orbit Workflow

**Problem:** Repeated flytoview commands to `/tmp/query.txt` stutter (go-stop-go) due to daemon polling delays, write races, or flyToView=1 refresh fights.

**Solution:** Pi-based SSH `echo` commands with overlapping timing (2.5s duration, 2.0s interval) and flyToView=0.

## Pre-flight

1. **Check flyToView** — if myplaces.kml has flyToView=1, disable it:
   ```bash
   sshpass -p 'lg' ssh lg@<IP> "sed -i 's|<flyToView>1</flyToView>|<flyToView>0</flyToView>|' ~/earth/kml/master/myplaces.kml"
   ```
   Then **relaunch Earth once** for the change to take effect.

2. **Verify Earth window** focus for xdotool (if using):
   ```bash
   sshpass -p 'lg' ssh lg@<IP> "DISPLAY=:0 xdotool getactivewindow getwindowname"
   ```

## Orbit Script Template (Pi-based)

Save as `orbit.sh` on the Pi:

```bash
#!/bin/bash
IP="<lg-ip>"
PW="lg"
LON="<longitude>"
LAT="<latitude>"
RNG="100000"   # VM-safe: 100km+
TILT="60"

send() {
  sshpass -p "$PW" ssh -o StrictHostKeyChecking=no -o ConnectTimeout=3 lg@"$IP" \
    "echo 'flytoview=<gx:duration>\$1</gx:duration><gx:flyToMode>smooth</gx:flyToMode><LookAt><longitude>$LON</longitude><latitude>$LAT</latitude><range>\$3</range><tilt>\$4</tilt><heading>\$2</heading><altitudeMode>relativeToGround</altitudeMode></LookAt>' > /tmp/query.txt" 2>/dev/null
}
```

## Fly-in Sequence

**Always do a wide overview before zooming close** — prevents long-distance camera jumps:

```bash
# Step 1: Wide overview (3000km range)
send 5.0 0 3000000 40
sleep 6

# Step 2: Zoom in
send 6.0 0 100000 60
sleep 8

# Step 3: Clear state
sshpass -p "$PW" ssh lg@"$IP" "echo 'exittour=true' > /tmp/query.txt"
sleep 1
```

## Orbit Loop

**Overlap timing is key:** gx:duration > step interval so next command arrives while previous animation is still playing:

```bash
HDG=0
for step in $(seq 1 72); do
  send 2.5 $HDG 100000 60    # duration=2.5s
  HDG=$((HDG + 5))
  sleep 2.0                   # interval=2.0s — shorter than duration
done
```

- 72 steps × 5° = full 360° rotation
- 2.5s duration > 2.0s interval = overlap, no gaps
- Heading grows past 360 (Earth handles wrap)

## Deploy KML

```bash
# SCP KML + deploy helper, then run helper on lg1
sshpass -p 'lg' scp /tmp/spot.kml /tmp/deploy-spot.sh lg@<IP>:/home/lg/
sshpass -p 'lg' ssh lg@<IP> "bash /home/lg/deploy-spot.sh"
```

## Pitfalls

| Symptom | Cause | Fix |
|---------|-------|-----|
| Camera jumps wildly on fly-in | No overview step before close zoom | Add 3000km overview first |
| Orbit stutters (go-stop-go) | flyToView=1 fighting commands | Set flyToView=0 + relaunch |
| Left-right bouncing | Heading wrapping oddly | Check heading grows past 360, no modulo |
| Blank screen at close range | VM terrain fails <100km | Keep range >= 100,000m |
| No Python 3.5 f-strings | lg1 runs Ubuntu 14.04 | Use % formatting |
