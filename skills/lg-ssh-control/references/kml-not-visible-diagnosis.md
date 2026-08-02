# KML Not Visible — Diagnostic Procedure

**When:** Deployed KML to master.kml (HTTP 200 confirmed) but no content appears on LG screens.

**Root causes (most common first):**
1. Earth launched manually, not through the LG system — ViewSync not running, myplaces.kml is stale
2. Earth 7.3.3 crash (Signal 11 in libxcb/Qt5) — Earth appears running but NetworkLink never fires
3. Earth user mismatch — SSH user edits `/home/lg/` files but Earth runs as `lg1` (reads `/home/lg1/`)
4. Master KML NetworkLink has no `refreshInterval` — Earth fetches once at startup, never re-polls
5. Double-slash in URL (`http://lg1:81//kml/`) — URL resolution may fail silently

---

## Step 1: Verify Earth is Running *as the Right User*

```bash
# Check Earth processes
pgrep -a googleearth
ps -o uid,pid,user,cmd -p <PID>
```

Earth should run as **lg1** (UID 1000 on this rig), not lg. If UID differs, the myplaces path is wrong.

**Check Earth's actual environment:**
```bash
cat /proc/<PID>/environ | tr "\0" "\n" | grep -E 'HOME|USER|DISPLAY'
```

Expected: `HOME=/home/lg1`, `USER=lg1`, `DISPLAY=:0`

---

## Step 2: Check Apache Logs for Earth HTTP Requests

The master KML NetworkLink in myplaces causes Earth to fetch `http://lg1:81/kml/master.kml` every N seconds. If Earth is running correctly, Apache logs will show periodic requests with User-Agent `GoogleEarth/7.3.3.*`.

```bash
# Check the virtual host log (LG Apache uses other_vhosts_access.log)
sudo grep "GoogleEarth" /var/log/apache2/other_vhosts_access.log | grep "master.kml" | tail -5
```

**No Earth requests in log = Earth not making NetworkLink calls.** This means:
- Earth may have crashed (Signal 11 in libxcb — see Step 4)
- Earth was started without the LG system (see Step 3)
- The NetworkLink in the runtime myplaces is missing or broken (see Step 5)

**Earth requests present but KML still not visible:**
- Check HTTP response size (should match deployed KML size, not ~500 bytes)
- Check if Earth has a stale cache — restart Earth

---

## Step 3: Determine How Earth Was Launched

**Earth launched through the LG system (correct):**
- Earth was started by `run-earth-bin.sh` via `launch-earth.sh`
- The script runs `write-drivers-ini.sh` (configures ViewSync), copies configs from `~/earth/config/` to `~/.config/Google/`, and copies myplaces.kml from `~/earth/kml/` to `~/.googleearth/`
- Configs have `##LG_PHPIFACE##` expanded to `http://lg1:81/`
- ViewSync process should be active

**Earth launched manually (incorrect — KML won't work):**
- Earth was started as `/opt/google/earth/pro/googleearth` directly
- Runtime `~/.googleearth/myplaces.kml` is stale — may lack refreshInterval
- ViewSync is NOT running
- Configs are not freshly copied from source

**Fix:**
```bash
# Kill existing Earth
sudo kill <PID>

# Run the single-VM LG launch script (avoids SSH hangs to lg2/lg3)
sudo /sbin/runuser -l lg1 -c 'bash /home/lg1/launch-lg1.sh'
```

**Running GUI commands as lg1 (when SSHed as lg):**
The `lg` user cannot access the X display of `lg1` directly. Use `sudo /sbin/runuser -l lg1 -c '...'` to run commands in lg1's session:
```bash
# Check Earth window
sudo /sbin/runuser -l lg1 -c 'DISPLAY=:0 xdotool getactivewindow getwindowname'

# List Earth's visible windows
sudo /sbin/runuser -l lg1 -c 'DISPLAY=:0 xdotool search --onlyvisible --name "Google Earth" getwindowgeometry'
```

If `sudo` needs `-S` (no TTY), use Python subprocess:
```python
import subprocess
r = subprocess.run(['sudo', '-S', '/sbin/runuser', '-l', 'lg1', '-c', 'DISPLAY=:0 xdotool search --name "Google Earth" getwindowname'], input=b'lg\\n', stdout=subprocess.PIPE)
print(r.stdout.decode())
```

If `launch-lg1.sh` doesn't exist, create it (see `references/single-vm-launch.md`).

---

## Step 4: Detect Earth Crash (Signal 11 in libxcb)

Earth 7.3.3 on VirtualBox VMs commonly crashes with Signal 11 (segfault) in the xcb/Qt5 graphics stack. The Earth window shows "Google Earth Pro" but the 3D renderer is broken and NetworkLinks never fire.

**Check for crash logs:**
```bash
ls -la ~/.googleearth/crashlogs/
cat ~/.googleearth/crashlogs/crashlog-*.txt | head -20
```

**Crash signature:** `Crash Signal 11` with stacktrace showing `libxcb.so.1` and `libQt5XcbQpa.so`.

**Also check for blocking dialog (graphic card / sign-in / crash):**
Earth may appear to be running but is actually showing a blocking dialog that prevents NetworkLinks from firing. Check the active window geometry — a tiny window (e.g. 491x138 pixels instead of 800x600+) means a dialog is on top:
```bash
sudo /sbin/runuser -l lg1 -c 'DISPLAY=:0 xdotool getactivewindow getwindowgeometry'
```

List all visible windows to identify the dialog name:
```bash
sudo /sbin/runuser -l lg1 -c \
  'DISPLAY=:0 xdotool search --name "" getwindowname 2>/dev/null | sort -u'
```

Known blocking dialogs on VirtualBox VM rigs:
- **"Unknown graphics card"** — Google Earth Pro's GPU check fails on VirtualBox without 3D acceleration. Fix: `--no_system_check` flag.
- **"Cannot contact login server"** — Offline VM, Earth Pro tries to sign in. Fix: `--no_signin` flag.
- **"Google Earth Crash Detected"** — After a Signal 11 crash. Fix: kill `repair_tool` process, then restart.

**Workarounds (try in order):**
1. **Suppress system check + sign-in:** `export LIBGL_ALWAYS_SOFTWARE=1` AND launch with `--no_system_check --no_signin` flags. This is the most reliable fix for VM rigs.
   ```bash
   /opt/google/earth/pro/googleearth --no_signin --no_system_check
   ```
2. **Software rendering:** `export LIBGL_ALWAYS_SOFTWARE=1` before launching Earth (set permanently in lg1's `.profile`)
3. **Reinstall xcb libraries:** `sudo apt-get install --reinstall libxcb1 libxcb-xfixes0 libxcb-shm0 libxcb-icccm4 libxcb-image0 libxcb-keysyms1 libxcb-randr0 libxcb-render-util0 libxcb-render0 libxcb-shape0 libxcb-sync1 libxcb-util1 libxcb-xinerama0 libxcb-xkb1 libxcb-xv0`
4. **Install VirtualBox Guest Additions** — the permanent fix (fixes display driver and xcb compatibility)
5. **Repair tool:** Run `/opt/google/earth/pro/repair_tool` to reset Earth's configuration

**Dialog auto-dismisser (kiosk mode):** Run a background loop that auto-clicks any blocking dialog:
```bash
nohup bash -c '
while true; do
  sleep 2
  xdotool search --name "Google Earth" key --window 0 Return 2>/dev/null
  xdotool search --name "graphic" key --window 0 Return 2>/dev/null
  xdotool search --name "error" key --window 0 Return 2>/dev/null
  xdotool search --name "Sign In" key --window 0 Escape 2>/dev/null
done
' > /dev/null 2>&1 &
```
The launcher at `/home/lg1/lg-launcher2.sh` includes this dismisser.

---

## Step 5: Verify Runtime myplaces.kml

Earth loads myplaces from `~/.googleearth/myplaces.kml`, NOT from `~/earth/kml/master/myplaces.kml`. The LG system copies from source to runtime at startup — manually started Earth uses whatever is in runtime.

**Check runtime myplaces:**
```bash
sudo grep -A4 "master.kml" /home/lg1/.googleearth/myplaces.kml
```

**Expected output:**
```xml
<href>http://lg1:81/kml/master.kml</href>
<flyToView>1</flyToView>
<refreshMode>onInterval</refreshMode>
<refreshInterval>3</refreshInterval>
```

**If missing refreshInterval or flyToView:**
```bash
# Copy fixed version from source to runtime
sudo cp /home/lg1/earth/kml/master/myplaces.kml /home/lg1/.googleearth/myplaces.kml
sudo chown lg1:lg1 /home/lg1/.googleearth/myplaces.kml
# Then restart Earth
```

**If source also lacks refreshInterval:**
```bash
# Add to source
sudo sed -i 's|<href>http://lg1:81/kml/master.kml</href>|<href>http://lg1:81/kml/master.kml</href>\n\t\t\t\t<flyToView>1</flyToView>\n\t\t\t\t<refreshMode>onInterval</refreshMode>\n\t\t\t\t<refreshInterval>3</refreshInterval>|' /home/lg1/earth/kml/master/myplaces.kml
```

---

## Step 6: Verify Apache Serves KML Correctly

```bash
# Check file on disk
ls -la /var/www/html/kml/master.kml
# Check HTTP response
curl -s -o /dev/null -w "%{http_code}" http://lg1:81/kml/master.kml
curl -s http://lg1:81/kml/master.kml | head -5
```

Expected: HTTP 200, file size matches deployed KML, valid XML.

**Check Apache is on the right port:**
```bash
ss -tlnp | grep apache
```

LG Apache listens on **port 81** only (not 80). The myplaces URL must include `:81`.

---

## Diagnostic Decision Tree

```
KML not visible?
├─ Check Earth PID exists → NO  → Start Earth
│                                └─ Through LG system (run-earth-bin.sh)
│                                   NOT bare googleearth
│
├─ Earth running → Check Apache logs for Earth requests
│  ├─ NO Earth requests → Is Earth crashed? (Step 4)
│  │  ├─ Crash detected → Software rendering workaround
│  │  └─ No crash → Check runtime myplaces (Step 5)
│  │     ├─ Missing refreshInterval → Fix myplaces → Restart Earth
│  │     └─ myplaces correct → Earth launched manually (Step 3)
│  │
│  └─ Earth requests present → Check HTTP response
│     ├─ HTTP 200, correct size → Earth rendering issue (VM limitation)
│     └─ Wrong size/404 → Fix Apache deployment
│
└─ Earth running as wrong user (lg vs lg1)
   └─ Fix: edit lg1's myplaces, restart Earth as lg1
```
