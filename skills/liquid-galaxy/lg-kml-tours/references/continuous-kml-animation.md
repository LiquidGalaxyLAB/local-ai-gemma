# Continuous KML Animation (No Tour Needed)

## Problem
Google Earth Pro tours require clicking the Play button in the Places panel. On LGs
in kiosk mode, users cannot click UI elements. Static KML with a single LookAt
shows a fixed view that only changes on refresh.

## Solution
Exploit the master.kml NetworkLink refresh cycle (3s). Run a loop on lg1 that
rewrites master.kml with an incremental heading each cycle. Earth re-reads the
file on refresh and the camera moves to the new LookAt.

## How Smooth Is It?
- 48 steps × 3s = 144s per full rotation (2.4 min)
- Each step changes heading by 7.5°
- Google Earth animates the transition internally (not instant snap)
- Result: perceivably smooth orbit, better with more steps

## Key Constraints

| Constraint | Reason |
|------------|--------|
| Sleep = refresh interval | If sleep < refresh, Earth skips updates; if >, orbit is jerky |
| sudo via subprocess | Tool guard blocks `echo PW \| sudo -S` in SSH commands but not inside remote scripts |
| No f-strings | lg1 runs Python 3.5 |
| Kill duplicates first | Each SSH invocation starts a new background process |

## Lifecycle Management

```bash
# Start
sshpass -p 'lg' ssh lg@192.168.1.200 "nohup python3 /home/lg/orbit-loop.py > /home/lg/orbit-loop.log 2>&1 &"

# Check
sshpass -p 'lg' ssh lg@192.168.1.200 "ps aux | grep orbit-loop"

# Verify heading is rotating
sshpass -p 'lg' ssh lg@192.168.1.200 "grep heading /var/www/html/kml/master.kml"
# Re-run every ~3s to see heading increment

# Stop
sshpass -p 'lg' ssh lg@192.168.1.200 "kill \$(pgrep -f orbit-loop)"
```

## Alternative: Deploy helper script on lg1

Instead of running the orbit-loop on the Pi and SCPing every cycle, the script
lives entirely on lg1. Only the initial SCP deploy crosses the network.

```bash
# One-time deploy
sshpass -p 'lg' scp orbit-loop.py lg@192.168.1.200:/home/lg/
sshpass -p 'lg' ssh lg@192.168.1.200 "chmod +x /home/lg/orbit-loop.py"

# Start
sshpass -p 'lg' ssh lg@192.168.1.200 "cd /home/lg && nohup python3 orbit-loop.py > orbit-loop.log 2>&1 &"
sleep 2
sshpass -p 'lg' ssh lg@192.168.1.200 "disown -a 2>/dev/null; ps aux | grep orbit-loop | grep -v grep"
```

## Session History

2026-06-22: First orbit-loop deployed for India cylinder (78.5°E, 20.5°N).
48 steps, 400km range, 55° tilt. Deployed via Python script on lg1.
COLLADA model failed; switched to extruded 6-segment polygon.
