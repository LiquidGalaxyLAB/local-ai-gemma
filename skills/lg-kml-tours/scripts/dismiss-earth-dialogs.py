#!/usr/bin/env python3
"""Auto-dismiss Google Earth dialogs (login server, etc.). Python 3.5 compat.

Deploy to lg1 and run:
  DISPLAY=:0 python3 /home/lg/dismiss-earth-dialogs.py

Or install as autostart:
  1. SCP this script to /home/lg/ on lg1
  2. Create /home/lg/.config/autostart/dismiss-earth-dialogs.desktop:
     [Desktop Entry]
     Type=Application
     Name=Dismiss Earth Dialogs
     Exec=sh -c "sleep 10 && DISPLAY=:0 python3 /home/lg/dismiss-earth-dialogs.py"
     Terminal=false
     X-GNOME-Autostart-enabled=true
  3. Relaunch Earth — autostart runs on every session start
"""
import subprocess, time

LOG = "/home/lg/dismiss_earth_dialogs.log"

def log(msg):
    with open(LOG, "a") as f:
        f.write("%s\n" % msg)

def find_window(name_pattern):
    p = subprocess.Popen(["xdotool", "search", "--name", name_pattern],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, _ = p.communicate()
    out = out.decode().strip()
    return out.split("\n") if p.returncode == 0 else []

log("Dismiss script started")
time.sleep(8)

for attempt in range(15):
    windows = find_window("Google Earth Pro")
    for wid in windows[:1]:
        subprocess.run(["xdotool", "windowactivate", wid],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["xdotool", "key", "Escape"],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(0.3)
        subprocess.run(["xdotool", "key", "Return"],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(0.3)
        subprocess.run(["xdotool", "key", "alt+a"],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(0.3)
        subprocess.run(["xdotool", "key", "Return"],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(2)

log("Dismiss script completed")
