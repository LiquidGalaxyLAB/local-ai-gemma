# Auto-Dismissing Google Earth Pro Login Dialogs on Offline VM Rigs

## Problem

On LG VM rigs without internet access (or with misconfigured networking), Google Earth Pro 7.3.x shows: *"Google Earth can't contact the login server to activate your account."* on every launch. This dialog blocks the screen until manually dismissed — breaking kiosk mode.

## Root Cause

Earth contacts Google auth endpoints at startup (`www.googleapis.com`, `google.com/earth/associate`, etc.). When these are unreachable, Earth shows the warning. Blocking them in `/etc/hosts` (127.0.0.1) makes failure fast but does NOT suppress the dialog — the dialog still appears.

## Fix: Auto-Dismiss with xdotool

Create a Python script that runs after Earth launches, detects the dialog, and dismisses it automatically.

### Script (`/home/lg/dismiss-dialogs.py`)

```python
#!/usr/bin/env python3
"""Auto-dismiss Google Earth dialogs at startup."""
import subprocess, time, os

def run(cmd):
    subprocess.run(cmd, shell=True)

def find_dialog(name_pattern):
    p = subprocess.Popen(["xdotool", "search", "--name", name_pattern],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, _ = p.communicate()
    out = out.decode().strip()
    return out.split("\n") if p.returncode == 0 else []

# Wait for Earth to start
time.sleep(8)

# Try dismissing dialogs — multiple attempts over ~30s
for attempt in range(15):
    dialogs = find_dialog("Google Earth Pro")
    for wid in dialogs[:1]:
        run("xdotool windowactivate %s 2>/dev/null" % wid)
        run("xdotool key Escape 2>/dev/null")
        time.sleep(0.3)
        run("xdotool key Return 2>/dev/null")
        time.sleep(0.3)
        run("xdotool key alt+a 2>/dev/null")
        time.sleep(0.3)
        run("xdotool key Return 2>/dev/null")
    time.sleep(2)
```

**Python 3.5 caveat:** Do NOT use `capture_output=True` in `subprocess.run` — not available on Python 3.5. Use `Popen` with `stdout=subprocess.PIPE` instead.

### Autostart Entry

Create `/home/lg/.config/autostart/dismiss-earth-dialogs.desktop`:

```
[Desktop Entry]
Type=Application
Name=Dismiss Earth Dialogs
Exec=sh -c "sleep 10 && DISPLAY=:0 python3 /home/lg/dismiss-dialogs.py"
Terminal=false
X-GNOME-Autostart-enabled=true
```

This runs the dismiss script ~10s after the user session starts (Earth is launched by `lg.desktop` in the same autostart directory).

### Deployment

```bash
# On the Pi/Hermes host:
cat > /tmp/dismiss-dialogs.py << 'SCRIPT'
... script content ...
SCRIPT

sshpass -p 'lg' scp /tmp/dismiss-dialogs.py lg@<lg-ip>:/home/lg/
sshpass -p 'lg' scp /tmp/dismiss-earth-dialogs.desktop lg@<lg-ip>:/home/lg/
sshpass -p 'lg' ssh lg@<lg-ip> "sudo cp /home/lg/dismiss-earth-dialogs.desktop /home/lg/.config/autostart/"
```

## Verification

Relaunch Earth. After ~15s, the login dialog should be auto-dismissed. Check: `cat /home/lg/dismiss.log` should show "dismiss script completed".

## Limitation

This only dismisses the dialog after it appears — it may flash on screen for a few seconds. To truly prevent it, fix the VM's internet connectivity (see VM bridged LAN network fix).
