#!/usr/bin/env python3
"""
Auto-dismiss Google Earth Pro dialogs at startup.
Runs in background, sends keyboard events to dismiss the
"cannot contact login server" dialog (or any Earth modal).
Deploy to autostart so it runs after every logout/relaunch.

Python 3.5 compatible — no f-strings, no capture_output.
"""
import subprocess
import time
import os

def find_dialog(name_pattern):
    p = subprocess.Popen(
        ["xdotool", "search", "--name", name_pattern],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, _ = p.communicate()
    out = out.decode().strip()
    return out.split("\n") if p.returncode == 0 else []

# Wait for Earth to start and show dialog
time.sleep(8)

for attempt in range(15):
    dialogs = find_dialog("Google Earth Pro")
    for wid in dialogs[:1]:  # main window
        subprocess.run(
            "xdotool windowactivate %s 2>/dev/null" % wid, shell=True)
        subprocess.run("xdotool key Escape 2>/dev/null", shell=True)
        time.sleep(0.3)
        subprocess.run("xdotool key Return 2>/dev/null", shell=True)
        time.sleep(0.3)
        subprocess.run("xdotool key alt+a 2>/dev/null", shell=True)
        time.sleep(0.3)
        subprocess.run("xdotool key Return 2>/dev/null", shell=True)
    time.sleep(2)

with open(os.path.expanduser("~/dismiss-done.log"), "w") as f:
    f.write("dismiss script completed\n")
