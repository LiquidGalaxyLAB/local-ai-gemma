# VM Earth Startup Pitfall

## The Problem

On VM-based LG rigs (single VM with lg2/lg3 unreachable), the autostart `lg.desktop` runs `launch-earth.sh` which:

1. Calls `lg-run killall run-earth-bin.sh googleearth-bin` — this SSHes to **all** frames
2. SSH to lg2/lg3 hangs forever (no such host on single-VM setups)
3. Earth never starts on lg1 because the script is blocked waiting

## Symptoms

```
$ ps aux | grep -E 'ssh.*lg@lg|lg-run|launch-earth'
lg  6043  bash /home/lg/earth/scripts/launch-earth.sh
lg  6055  /bin/bash /home/lg/bin/lg-run killall run-earth-bin.sh googleearth-bin
lg  6626  ssh -tt -x lg@lg2  killall run-earth-bin.sh googleearth-bin
```

- `googleearth-bin` PID absent
- `launch-earth.sh` stuck in process list
- `ssh -tt -x lg@lg2` stuck forever

## The Fix

```bash
# 1. Kill the stuck SSH to unreachable slaves (get PIDs from ps aux)
sshpass -p 'lg' ssh lg@192.168.1.200 "kill 6043 6055 6626"

# 2. Remove stale lock file
sshpass -p 'lg' ssh lg@192.168.1.200 "rm -f /home/lg/.googleearth/instance-running-lock"

# 3. Start Earth directly (bypasses launch-earth.sh)
sshpass -p 'lg' ssh -f lg@192.168.1.200 \
  "export DISPLAY=:0 && nohup /opt/google/earth/pro/googleearth > /home/lg/earth-start.log 2>&1"

# 4. Wait 20-30s for Earth to load
sleep 25

# 5. Check it's running
sshpass -p 'lg' ssh lg@192.168.1.200 "pgrep -a googleearth-bin"

# 6. If stuck on "Google Earth Options" dialog, dismiss it:
sshpass -p 'lg' ssh lg@192.168.1.200 \
  "DISPLAY=:0 xdotool search --name 'Google Earth Options' key alt+a"
sshpass -p 'lg' ssh lg@192.168.1.200 \
  "DISPLAY=:0 xdotool search --name 'Google Earth Options' key Return"
```

## After Power Cycle

The autostart `lg.desktop` will try `launch-earth.sh` again on next boot, which will hang again. You must use the manual start pattern every time after boot/power-cycle until this is fixed in the launch script.

**Permanent fix (not yet applied):** Rewrite `launch-earth.sh` to skip `lg-run killall` on unreachable frames, or replace the autostart entry to start Earth directly.
