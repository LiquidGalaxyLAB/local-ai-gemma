# xdotool Orbit — Single-Command Smooth Rotation

## When to Use

When repeated flytoview commands to `/tmp/query.txt` cause stuttering ("moving, stopping, moving"), use Google Earth's native rotation via `xdotool`. This sends one command to start rotating and one to stop — no gaps, no command stacking, perfectly smooth.

## ⚠️ CRITICAL: Inward vs Outward Orbit

`xdotool ctrl+Left` produces **outward rotation** — the camera rotates in place like turning your head. The viewpoint stays at one position but the direction you're looking rotates. This is NOT what users typically mean by "orbit."

**flytoview with changing `heading`** produces **inward orbit** — the camera moves AROUND the target, always looking at it. Each step changes the heading value, placing the camera at a different position around the target.

| Approach | Camera motion | User perception |
|----------|--------------|----------------|
| `xdotool keydown ctrl+Left` | Rotates in place (outward) | "Like turning your head" |
| `flytoview heading=0 → 360` | Circles around target (inward) | "Going around the spot" |

**When a user asks for "orbit," they want inward (camera going around the spot).** Use xdotool only when explicitly asked, or as a fallback when repeated flytoview commands stutter despite all fixes. If using xdotool, explain the distinction so the user knows the motion will be outward rotation, not a true orbit around the target.

## Prerequisites

- `xdotool` installed on lg1 (present on most LG rigs)
- Earth window must be focused (`xdotool getactivewindow getwindowname` returns "Google Earth Pro")

## How It Works

```python
import subprocess

# Start rotating (hold key)
subprocess.run(["xdotool", "keydown", "--clearmodifiers", "ctrl+Left"],
               env={"DISPLAY": ":0"})

# Wait for desired rotation (55s ≈ full rotation on VM)
time.sleep(55)

# Stop rotating (release key)
subprocess.run(["xdotool", "keyup", "--clearmodifiers", "ctrl+Left"],
               env={"DISPLAY": ":0"})
```

Earth handles the rotation internally — no `/tmp/query.txt` writes during the orbit.

## Key Controls

| Action | xdotool command | Earth effect |
|--------|----------------|--------------|
| Rotate heading left | `keydown ctrl+Left` | Orbital rotation |
| Rotate heading right | `keydown ctrl+Right` | Orbital rotation opposite |
| Stop rotation | `keyup ctrl+Left` (or `keyup ctrl+Right`) | Camera stops |
| Pan north | `keydown Up` | Move view north |
| Pan south | `keydown Down` | Move view south |
| Pan east | `keydown Right` | Move view east |
| Pan west | `keydown Left` | Move view west |

## Multi-Stop Tour with xdotool

Combine flytoview positioning (one-shot) with xdotool rotation (smooth orbit):

```python
# 1. Position camera via /tmp/query.txt (one command)
write_q('flytoview=<gx:duration>5.0</gx:duration>...heading=0...</LookAt>')
time.sleep(7)

# 2. Orbit smoothly via xdotool (no /tmp/query.txt writes during rotation)
xdo_keydown("ctrl+Left")
time.sleep(55)  # Full rotation
xdo_keyup("ctrl+Left")

# 3. Fly to next location
write_q('flytoview=<gx:duration>5.0</gx:duration>...<longitude>79.97</longitude>...')
time.sleep(7)
xdo_keydown("ctrl+Left")
time.sleep(40)
xdo_keyup("ctrl+Left")
```

## Rotation Speed

Rotation speed depends on Earth's mouse-look sensitivity settings. Default on VM:
- ~55 seconds for a full 360° rotation
- Tune by adjusting the `sleep` duration

## Script Pattern

```python
#!/usr/bin/env python3
"""Multi-stop tour with xdotool smooth orbit"""
import time, subprocess

def xdo_keydown(key):
    subprocess.run(["xdotool", "keydown", "--clearmodifiers", key],
                   env={"DISPLAY": ":0"}, timeout=5)

def xdo_keyup(key):
    subprocess.run(["xdotool", "keyup", "--clearmodifiers", key],
                   env={"DISPLAY": ":0"}, timeout=5)

def write_q(txt):
    with open("/tmp/query.txt", "w") as f:
        f.write(txt)

def flyto(lon, lat, rng, tilt, hdg, dur=5.0):
    cmd = ('flytoview=<gx:duration>%.1f</gx:duration><gx:flyToMode>smooth</gx:flyToMode>'
           '<LookAt><longitude>%.4f</longitude><latitude>%.4f</latitude>'
           '<range>%d</range><tilt>%d</tilt><heading>%.1f</heading>'
           '<altitudeMode>relativeToGround</altitudeMode></LookAt>') % (dur, lon, lat, rng, tilt, hdg)
    write_q(cmd)

# Reset
write_q("exittour=true")
time.sleep(1)

# Position at target
flyto(88.1476, 27.7021, 250000, 55, 0, 5.0)
time.sleep(7)

# Smooth orbit via xdotool (single command)
xdo_keydown("ctrl+Left")
time.sleep(55)  # One full rotation
xdo_keyup("ctrl+Left")

# Clean up
write_q("exittour=true")
```

## Why This Beats Repeated flytoview

| Approach | Stutter? | Command count | Gaps? |
|----------|----------|---------------|-------|
| Repeated flytoview (72 steps) | Yes ❌ | 72 writes | 0-500ms gaps between write & daemon read |
| xdotool keydown/keyup | No ✅ | 2 commands | Zero — Earth handles internally |

## Pitfalls

- **DISPLAY must be :0** — Set `env={"DISPLAY": ":0"}` in subprocess calls. Running via `nohup`/`ssh -f` drops the DISPLAY env var; always pass it explicitly.
- **Window focus** — xdotool sends keys to the active window. If another dialog steals focus, the rotation stops. Call `xdotool getactivewindow getwindowname` to verify Earth is focused.
- **Cannot interrupt mid-rotation** — Unlike flytoview commands that can be overwritten, xdotool keydown holds the key. To stop early, send `xdotool keyup ctrl+Left` via another SSH session.
- **Doesn't interfere with NetworkLink refresh** — Since xdotool controls Earth directly (not via /tmp/query.txt), there's no conflict with the 3s master.kml NetworkLink refresh, even if flyToView=1 is active.
- **Combine with static KML** — Deploy placemarks/polygons to master.kml before starting the tour. The xdotool rotation just moves the camera; content stays rendered.
