# Orbit Stutter Debugging Chain

## Symptom
Camera "moves, stops, moves, stops" during flytoview-based orbit on a VM Liquid Galaxy. The animation is not continuous — stutters at regular intervals or between steps.

## Root Causes (in order of discovery)

### 1. gx:duration Mismatch with Step Interval
**Problem:** `gx:duration=1.0` with `step_interval=1.5` creates a 0.5s gap between every step. The camera flies for 1.0s, sits idle for 0.5s, flies again. This looks like stutter.

**Fix:** Set `gx:duration` equal to the step interval. `gx:duration=1.5` with `sleep(1.5)` = seamless continuous motion.

### 2. Concurrent File Read During Write
**Problem:** The LG daemon reads `/tmp/query.txt` asynchronously. When the Python script uses `open(path, "w")`, the file is truncated (0 bytes) before new content is written. If the daemon reads during this window, it gets an empty command and freezes.

**Fix:** Delete the file before writing (`os.remove(path)`) so the daemon either gets the complete old file or finds it missing — never a partial/truncated one.

```python
def write_q(txt):
    path = "/tmp/query.txt"
    try:
        os.remove(path)
    except OSError:
        pass
    with open(path, "w") as f:
        f.write(txt)
```

### 3. flyToView=1 NetworkLink Refresh Fights Orbit
**Problem:** `~/earth/kml/master/myplaces.kml` has `<flyToView>1</flyToView>` on the Master NetworkLink. Every 3s, the NetworkLink refreshes and Earth re-processes the KML. Even when master.kml has NO `<LookAt>`, the re-processing creates a brief camera state reset that interferes with concurrent flytoview commands from /tmp/query.txt.

**Fix:** Set `<flyToView>0</flyToView>` in myplaces.kml before running any flytoview orbit. This requires a relaunch.

```bash
# Disable (before orbit)
sed -i 's|<flyToView>1</flyToView>|<flyToView>0</flyToView>|' ~/earth/kml/master/myplaces.kml

# Enable (after orbit, for static KML auto-positioning)
sed -i 's|<flyToView>0</flyToView>|<flyToView>1</flyToView>|' ~/earth/kml/master/myplaces.kml
```

### 4. Too Few Steps with Large Heading Jumps
**Problem:** 20 steps at 18° per step creates a jerky orbit. Each step is a big camera jump.

**Fix:** 72 steps at 5° per step. More steps = smaller heading changes = visibly smoother. VMs can handle 72 steps at 1.5s intervals (108s per full rotation).
### 5. Transition Between Multi-Stop FlyTo and Orbit

**Problem:** In multi-stop tours, transitioning from a long `stop_at()` flytoview (5-7s duration) to `orbit_at()` (1.5s steps) causes a timing disruption. The first orbit step may arrive while the previous fly-in is still executing.

**Fix:** Wait for the fly-in to complete before starting the orbit. Use `time.sleep(fly_duration + 1)` for safety margin. Or simplify to a single continuous orbit when stutter is an issue.

### 6. Too-Aggressive Fly-In (Single-Stage Zoom)

**Problem:** When switching between distant locations (e.g., Italy → Canada, or Pisa → CN Tower), sending a direct flytoview at close range (100km) causes Earth to race across the planet in seconds, resulting in visual glitches and wild camera movements.

**Fix:** Use a two-stage (or three-stage) fly-in:

1. **Wide overview**: range=3,000,000m, tilt=40-45°, duration=5-6s, wait 6-8s
2. **Intermediate zoom**: range=500,000m, tilt=50°, duration=5-6s, wait 6-8s
3. **Close zoom**: range=100,000-200,000m, tilt=55-65°, duration=5-6s, wait 7-8s

This gives Earth time to smoothly transition between hemispheres. Verified working on VM rig July 2026.

```bash
# Stage 1: wide overview of target region
ssh lg@lg1 'echo "flytoview=<gx:duration>5.0</gx:duration>...<range>3000000</range><tilt>40</tilt>..." > /tmp/query.txt'
sleep 6
# Stage 2: intermediate zoom
ssh lg@lg1 'echo "flytoview=<gx:duration>5.0</gx:duration>...<range>500000</range><tilt>50</tilt>..." > /tmp/query.txt'
sleep 6
# Stage 3: close zoom to target
ssh lg@lg1 'echo "flytoview=<gx:duration>5.0</gx:duration>...<range>100000</range><tilt>60</tilt>..." > /tmp/query.txt'
sleep 7
# Stage 4: begin orbit
```

## Verified Good Configuration (VM Rig)
- 72 steps per rotation
- 5° heading increment per step
- 1.5s step interval
- 1.5s gx:duration
- `os.remove(path)` before each write
- `flyToView=0` in myplaces.kml
- Continuous `while True` loop (never wrap heading)
- Python 3.5 compatible (% formatting, no f-strings)

## Remaining Known Limitation

Even with ALL the above fixes applied, flytoview-based orbit can still stutter on some VM rigs. The suspected root cause is the **daemon polling interval** — the background process monitoring `/tmp/query.txt` may poll at an interval (e.g., 500ms) that doesn't align with the script's write timing, creating variable gaps between command processing.

**If stutter persists after all fixes, the remaining options are:**
1. **xdotool approach** — Use `xdotool keydown ctrl+Left` for native Earth rotation (single command, no gaps). See `references/xdotool-orbit.md`. **Warning:** this produces outward rotation (camera rotates in place) not inward orbit (camera around target).
2. **SSH echo pattern** — Run the orbit loop from the Pi (not on lg1), sending each flytoview as a separate `sshpass ssh 'echo "flytoview=..." > /tmp/query.txt'` command. Each SSH command is an atomic write with no local race condition.
3. **gx:duration overlap** — Set gx:duration slightly longer than step interval (e.g., gx:duration=2.5 with step interval=2.0). The next command arrives while the previous is still playing, creating overlap. Earth smoothly adjusts course mid-flight.

## Testing Protocol
1. Kill existing orbit: `kill $(pgrep -f script-name)`
2. Send `exittour=true` to /tmp/query.txt
3. Disable flyToView=1 in myplaces.kml + relaunch once
4. Start orbit script via `ssh -f nohup python3 script.py > log 2>&1`
5. Wait 15s, then observe on screens for 30s
6. Check log for step progression

## Session History
This debugging chain was worked through in a July 2026 session where a Himalayan R3DKML tour stuttered repeatedly. Each fix was applied and tested incrementally:
1. Step count increased (20→36→72)
2. gx:duration matched to step interval (1.2→1.5)
3. os.remove() added to write_q()
4. flyToView=1 discovered and disabled
5. Final config: 72 steps, 1.5s interval, 1.5s duration, flyToView=0, os.remove
