# Earth 7.3.3 XCB Crash Fix (VirtualBox)

After a `lg-relaunch-direct` (lightdm restart), Earth 7.3.3 on VirtualBox
crashes immediately with Signal 6 (SIGABRT) at 0.006s uptime. The crash is
in Qt5's XCB platform plugin — the OpenGL integration via XCB segfaults.

## Symptom

```
Crash Signal 6
Up Time 0.009821
Stacktrace: _ZN14QXcbConnectionC2E... (Qt5 XCB constructor)
```

Earth window may briefly flash then disappear. Zero HTTP requests to Apache
after restart. Multiple crashlogs in `~/.googleearth/crashlogs/`.

## Root Cause

After lightdm restarts the X server, the Qt5 XCB platform plugin's GL
integration (`libqxcbglx.so`) fails because the VirtualBox video driver's
OpenGL context can't be re-established. This is a VirtualBox + Earth 7.3.3
specific issue — real LG hardware with proper GPUs doesn't have this problem.

## Fix

Set `QT_XCB_GL_INTEGRATION=none` in Earth's environment. This tells Qt5's
XCB platform plugin to skip OpenGL integration entirely:

```bash
QT_XCB_GL_INTEGRATION=none DISPLAY=:0 LIBGL_ALWAYS_SOFTWARE=1 \
  /opt/google/earth/pro/googleearth --no_system_check --no_signin
```

## X Authority Cookie Mismatch

After lightdm restart, the X server regenerates its authority cookie. Earth's
`.Xauthority` file may have a stale cookie, causing:

```
Invalid MIT-MAGIC-COOKIE-1 key
```

**Fix — sync the cookie:**
```python
import subprocess
subprocess.run(['sudo', '-S', 'xauth', '-f', '/var/run/lightdm/root/:0',
    'extract', '/tmp/xc', 'lg1/unix:0'], input=b'lg\n')
subprocess.run(['sudo', '-S', 'chmod', '644', '/tmp/xc'], input=b'lg\n')
subprocess.run(['xauth', 'merge', '/tmp/xc'])
```

## Permanent Autostart Fix

The `lg.desktop` autostart file must include all three env vars:

```
[Desktop Entry]
Name=LG
Exec=env DISPLAY=:0 LIBGL_ALWAYS_SOFTWARE=1 QT_XCB_GL_INTEGRATION=none \
  /opt/google/earth/pro/googleearth --no_system_check --no_signin
Type=Application
```

## Verification

After restart with the fix:
1. Check Apache logs: `grep GoogleEarth /var/log/apache2/other_vhosts_access.log`
   → should show `GET /kml/master.kml` and `GET /sync_nlc_1.php` every 3s
2. Check Earth PIDs: `pgrep -c googleearth` → should be 2+ (bash wrapper + binary)

## Related

- `lg-vm-quirks.md` wiki page — VM-specific X11 issues
- `lg-kml-debugging.md` — "Earth Window Shows But Zero HTTP Requests"
- `/home/lg1/launch-lg-earth.sh` — Launch script updated with X authority sync
