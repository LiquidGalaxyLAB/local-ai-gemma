# Post-Install Troubleshooting: Earth Not Launching (Grey Screen)

After the official install.sh runs and reboots, Earth may fail to start, leaving a grey/empty desktop on the VM display. This reference covers the three most common causes on VirtualBox rigs.

## Cause 1: Stale Instance Lock

Google Earth writes an `instance-running-lock` file to `~/.googleearth/` when it starts. If the VM was rebooted while Earth was running, this file persists pointing to a now-dead PID — Earth refuses to launch thinking another instance is still alive.

**Fix:**
```bash
rm -f ~/.googleearth/instance-running-lock
```

**Verify:**
```bash
ls -la ~/.googleearth/instance-running-lock
# Expected: "No such file or directory"
```

## Cause 2: launch-earth.sh Hangs on Slave SSH

The standard autostart file points to `launch-earth.sh`, which calls `lg-run killall` to kill any existing Earth on all frames before starting a new one. `lg-run` uses SSH to connect to every frame listed in `$LG_FRAMES`. If a slave isn't running SSH (fresh install, still booting, or unreachable), the `lg-run killall` command **hangs indefinitely**, and Earth never launches on the master.

**Symptoms:**
- `pgrep googleearth` returns nothing on the master
- `ps aux | grep launch-earth` shows the script stuck
- `ps aux | grep lg-run` shows an SSH connection attempt to a slave
- Re-running `launch-earth.sh` manually also hangs

**Fix A — Launch Earth Directly (Bypass launch-earth.sh):**

Create a custom autostart that launches the Earth binary directly:

```bash
cat > ~/.config/autostart/lg.desktop << 'EOF'
[Desktop Entry]
Name=LG
Exec=bash /home/lg1/launch-lg1-earth.sh
Type=Application
EOF

cat > ~/launch-lg1-earth.sh << 'EOF'
#!/bin/bash
export DISPLAY=:0
rm -f /home/lg1/.googleearth/instance-running-lock
/opt/google/earth/pro/googleearth &
EOF
chmod +x ~/launch-lg1-earth.sh
```

Then reboot or run the script manually:
```bash
export DISPLAY=:0
bash ~/launch-lg1-earth.sh
```

**Fix B — One-Time Manual Start (No Autostart Change):**

```bash
export DISPLAY=:0
rm -f ~/.googleearth/instance-running-lock
/opt/google/earth/pro/googleearth &
sleep 8
pgrep googleearth && echo "Earth running" || echo "Still not starting"
```

**Pitfall — Don't use `launch-earth.sh` directly over SSH:**
Even `ssh -f` or `nohup` won't save you — the script blocks until the slave SSH times out. Always use the direct binary approach for SSH-triggered starts.

## Cause 3: VirtualBox Display Name (Low Resolution / Black Frame)

The LG full-screen script (`45x11-custom_xrandr`) targets `--output default`, but VirtualBox VMs name their display output `Virtual1`. The xrandr command silently fails, leaving a 800x600 resolution. Google Earth can render at 800x600, but the UI is nearly unusable and content may appear as a grey or black frame.

**Fix A — Persistent Resolution Hook (LightDM):**

```bash
# Create fix script
sudo bash -c 'cat > /usr/local/bin/fix-resolution.sh << "EOF"
#!/bin/bash
sleep 2
xrandr --output Virtual1 --mode 1920x1200 2>/dev/null
EOF'
sudo chmod +x /usr/local/bin/fix-resolution.sh

# Hook into LightDM
sudo mkdir -p /etc/lightdm/lightdm.conf.d
echo -e "[Seat:*]\ndisplay-setup-script=/usr/local/bin/fix-resolution.sh" | \
  sudo tee /etc/lightdm/lightdm.conf.d/50-resolution.conf
```

This runs automatically on every LightDM login, so the fix persists across reboots.

**Fix B — Immediate (Current Session):**
```bash
export DISPLAY=:0
xrandr --output Virtual1 --mode 1920x1200
```

**Fix C — Patch the LG Script (Permanent for LG's own scripts):**
```bash
sudo sed -i 's/output default/output Virtual1/g' /home/lg1/tools/45x11-custom_xrandr
```

## Verification Checklist

After applying the above fixes:

```bash
export DISPLAY=:0
echo "--- Display ---"
xdpyinfo | grep dimensions
echo "--- Earth ---"
pgrep googleearth && echo "PID: $(pgrep googleearth-bin)" || echo "NOT RUNNING"
echo "--- Lock ---"
ls ~/.googleearth/instance-running-lock 2>/dev/null || echo "No lock (good)"
```

Expected output:
```
  dimensions:    1920x1200 pixels (or similar high resolution)
Earth RUNNING
No lock (good)
```

## Fixing the Autostart for Future Reboots

The cleanest autostart configuration that survives reboots and avoids the launch-earth.sh hang:

```bash
# Remove the old launch-earth.sh autostart
rm -f ~/.config/autostart/lg.desktop

# Create direct-launch autostart
cat > ~/.config/autostart/lg.desktop << 'EOF'
[Desktop Entry]
Name=LG
Exec=bash /home/lg1/launch-lg1-earth.sh
Type=Application
EOF

# Create the launch script
cat > ~/launch-lg1-earth.sh << 'EOF'
#!/bin/bash
export DISPLAY=:0
sleep 3
rm -f /home/lg1/.googleearth/instance-running-lock
/opt/google/earth/pro/googleearth &
EOF
chmod +x ~/launch-lg1-earth.sh
```

The `sleep 3` gives the desktop environment time to settle before Earth starts.
