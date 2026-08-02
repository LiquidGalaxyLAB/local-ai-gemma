# Earth 7.3.3 Crash Recovery After Lightdm Restart

## The Double-Crash Problem

After `lg-relaunch-direct` (restarts lightdm on all frames), Earth 7.3.3 on VirtualBox can fail in two ways:

### Crash 1: Signal 6 — Qt5 XCB GL Integration (NEW)
- **Symptom:** Crashlog shows `_ZN14QXcbConnectionC2E...` (Qt5 XCB constructor), uptime <0.01s
- **Cause:** Qt5 tries to initialize OpenGL integration through XCB, which fails on VirtualBox's software renderer after a fresh X session
- **Fix:** `QT_XCB_GL_INTEGRATION=none` in environment

### Crash 2: Signal 11 — libxcb / Graphics Stack
- **Symptom:** Crashlog shows `libxcb.so.1` + `libQt5XcbQpa.so`, uptime ~58s
- **Cause:** Earth tries GPU acceleration, segfaults in VirtualBox's graphics stack
- **Fix:** `LIBGL_ALWAYS_SOFTWARE=1` + `--no_system_check --no_signin`

## X Authority Issue

After lightdm restart, the X server generates a **new** MIT-MAGIC-COOKIE-1 in `/var/run/lightdm/root/:0`. The user's `~/.Xauthority` still has the **old** cookie. Earth crashes because Qt5 can't authenticate to the X server.

### Recovery Procedure

```python
import subprocess, time

# 1. Restart lightdm (if Earth is completely dead)
subprocess.run(['sudo', '-S', 'service', 'lightdm', 'restart'], input=b'lg\n', timeout=10)
time.sleep(45)

# 2. Verify X is running
r = subprocess.run(['pgrep', '-c', 'Xorg'], stdout=subprocess.PIPE)
print(f'Xorg PIDs: {r.stdout.decode().strip()}')

# 3. Start Earth with root X authority (always matches the running X server)
r = subprocess.run(['sudo', '-S', 'sh', '-c',
    'XAUTHORITY=/var/run/lightdm/root/:0 DISPLAY=:0 '
    'LIBGL_ALWAYS_SOFTWARE=1 QT_XCB_GL_INTEGRATION=none '
    'nohup /opt/google/earth/pro/googleearth --no_system_check --no_signin '
    '> /home/lg/earth-start.log 2>&1 & echo LAUNCHED'],
    input=b'lg\n', stdout=subprocess.PIPE, timeout=10)
print(r.stdout.decode().strip())

# 4. Verify after 25s
time.sleep(25)
r = subprocess.run(['pgrep', '-c', 'googleearth'], stdout=subprocess.PIPE)
print(f'Earth PIDs: {r.stdout.decode().strip()}')
# Expected: 2
```

### Alternative: Sync X Authority for Normal User
```bash
# Extract cookie from root authority and merge into user's file
sudo xauth -f /var/run/lightdm/root/:0 extract /tmp/xc lg1/unix:0
sudo chmod 644 /tmp/xc
xauth merge /tmp/xc
```

## Permanent Autostart Fix

The autostart file at `/home/lg/.config/autostart/lg.desktop` must include ALL three env vars:

```
[Desktop Entry]
Name=LG
Exec=env DISPLAY=:0 LIBGL_ALWAYS_SOFTWARE=1 QT_XCB_GL_INTEGRATION=none /opt/google/earth/pro/googleearth --no_system_check --no_signin
Type=Application
```

## Slave VMs

The same fix applies to lg2 and lg3. The autostart files go to the **logged-in user's** home directory (e.g. `/home/lg3/.config/autostart/` for lg3). Earth must run as the display session owner — use `sshpass -p lg ssh -f <user>@localhost "..."` to start it under the correct user, or use the `-direct` helper (`lg-relaunch-direct`) which restarts lightdm — the autostart then picks up the correct user.

### Starting Earth as Display User via SSH
```bash
# From the slave VM itself:
sshpass -p lg ssh -f -o StrictHostKeyChecking=no <display_user>@localhost \
  "XAUTHORITY=/home/<display_user>/.Xauthority DISPLAY=:0 \
   LIBGL_ALWAYS_SOFTWARE=1 QT_XCB_GL_INTEGRATION=none \
   nohup /opt/google/earth/pro/googleearth --no_system_check --no_signin"
```

## Verification
1. Check Apache logs for Earth User-Agent: `grep GoogleEarth /var/log/apache2/other_vhosts_access.log`
2. Check Earth PIDs: `pgrep -c googleearth` (expect 2)
3. Check crash logs: `ls ~/.googleearth/crashlogs/` (should be empty after successful start)
