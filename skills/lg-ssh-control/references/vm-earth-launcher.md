# VM Earth Launcher (Permanent Fix)

## Problem
Earth 7.3.3 on VirtualBox crashes with Signal 11 in libxcb/Qt5 rendering stack.
Shows "Unknown graphics card" dialog on startup that blocks NetworkLinks from firing.
Manual `/opt/google/earth/pro/googleearth` launch bypasses the LG system (ViewSync, config copy).

## Permanent Launcher
`/home/lg1/lg-launcher2.sh` — bundles the full LG system launch:
1. Runs `write-drivers-ini.sh` (ViewSync setup)
2. Copies configs from `~/earth/config/master/` to `~/.config/Google/`
3. Copies myplaces from `~/earth/kml/master/` to `~/.googleearth/`
4. Expands `##LG_PHPIFACE##` and `##HOMEDIR##` in configs
5. Starts dialog auto-dismisser in background (auto-clicks OK on error/graphic/crash dialogs)
6. Launches Earth with `--no_system_check --no_signin` flags + `LIBGL_ALWAYS_SOFTWARE=1`

## Manual Earth Startup (when launcher unavailable)
```bash
sshpass -p lg ssh -o StrictHostKeyChecking=no lg@<LG-IP> \
  'sshpass -p lg ssh -f lg1@localhost "export DISPLAY=:0 LIBGL_ALWAYS_SOFTWARE=1 && \
  nohup /opt/google/earth/pro/googleearth --no_system_check --no_signin > /dev/null 2>&1"'
```

Do NOT use `sudo runuser` — it hangs or fails without a PTY.

## Autostart Issue (Current Config)

`/home/lg/.config/autostart/lg.desktop` runs:
```
Exec=bash /home/lg1/launch-lg-earth.sh
```

`/home/lg1/launch-lg-earth.sh` Sources `${HOME}/etc/shell.conf` but runs as user `lg`, whose HOME is `/home/lg/` — the file is at `/home/lg1/etc/shell.conf`. The source is a no-op, `FRAME_NO` silently fails.

**Result:** Earth starts without ViewSync, without config copy, and without `--no_system_check` — the "unknown graphic card" dialog appears and blocks NetworkLinks.

**To fix autostart permanently:**
```bash
# Replace lg.desktop to use the proper launcher
cat > /home/lg/.config/autostart/lg.desktop << 'DESKTOP'
[Desktop Entry]
Name=LG
Exec=sudo -u lg1 bash /home/lg1/lg-launcher2.sh
Type=Application
DESKTOP
```

## query.txt Stale File Pitfall

When a continuous orbit script is killed (e.g. `bash /tmp/india-orbit.sh`), its last flytoview persists in `/tmp/query.txt`. The daemon considers this a "new" file only when written — stale content just sits there. The camera stays at the old coordinates.

**Symptoms:** user moves camera manually, it snaps back to India. Old flytoview still in query.txt with heading incrementing.

**Fix:** Remove the old file before writing a new command:
```bash
rm -f /tmp/query.txt && echo "flytoview=..." > /tmp/query.txt
```

Always check for leftover processes:
```bash
ps aux | grep -E "orbit|flyto|query"
```

## -direct Helper Deployment

The built-in `/home/lg/bin/lg-relaunch` uses root SSH keys to reach lg2/lg3 — fails on VM rigs. Deploy `-direct` helpers (sshpass-based) once:

```bash
# SCP the helpers to lg1, then copy to /home/lg/bin/ and /home/lg1/bin/
sshpass -p 'lg' scp /tmp/lg-relaunch-direct lg@<IP>:/home/lg/
sshpass -p 'lg' ssh lg@<IP> 'sudo cp /home/lg/lg-relaunch-direct /home/lg/bin/ && sudo chmod 755 /home/lg/bin/lg-relaunch-direct'
# Repeat for lg-reboot-direct and lg-poweroff-direct
```

The `-direct` helpers iterate `$LG_FRAMES` from shell.conf, skip self, restart each remote frame via sshpass, then self last.
