# Post-Install Checklist (When Install.sh Has Run But LG Isn't Working)

From a real session where the install.sh ran successfully on all 3 VMs but Earth didn't auto-launch and LG commands didn't work. Check these in order.

## 1. Check /home/lg Symlink

If the Ubuntu user is NOT `lg` (e.g. `lg1`, `lg2`, `lg3`), the install script's files land in `/home/lg{N}` but `shell.conf` hardcodes `/home/lg/personavars.txt` and `/home/lg/frame`.

**Fix:**
```bash
sudo rm -f /home/lg
sudo ln -sf /home/lg{N} /home/lg
```

Also fix shell.conf to use explicit paths:
```bash
sudo sed -i 's|/home/lg/personavars.txt|/home/lg{N}/personavars.txt|g' /home/lg{N}/etc/shell.conf
sudo sed -i 's|/home/lg/frame|/home/lg{N}/frame|g' /home/lg{N}/etc/shell.conf
```

## 2. Check Frame Number (personality.sh)

The install script's `personality.sh` sets the frame number. Master should be frame 0, slaves should be ±1, ±2, etc.

```bash
cat ~/frame
```

If master shows `1` instead of `0`, re-run personality:
```bash
sudo ~/bin/personality.sh 1 42   # machine_id=1, octet=42
cat ~/frame   # should now be 0
```

On slaves: `sudo ~/bin/personality.sh 2 42` (or 3 for lg3).

## 3. Check ViewSync in drivers.ini

The `write-drivers-ini.sh` script generates drivers.ini from the frame number. Run it:
```bash
cd ~ && bash ~/earth/scripts/write-drivers-ini.sh
```

Expected output for master:
```
MASTER: true
SLAVE: false
VSYNCHOST: 10.42.42.255
VSYNCPORT: 45678
YAW: 0
```

Expected output for slaves:
```
MASTER: false
SLAVE: true
VSYNCHOST: 10.42.42.255
YAW: -36.5   (lg2) or 36.5 (lg3)
```

Verify the config in the file:
```bash
grep -A6 "ViewSync" /opt/google/earth/pro/drivers.ini
```

Master should have `ViewSync/send = true`, slaves `ViewSync/receive = true`.

## 4. Launch Earth Directly (Bypass launch-earth.sh Hang)

`launch-earth.sh` uses `lg-run` which SSHs to all frames. On VM setups where cross-frame root SSH fails, this hangs forever.

**Fix — launch Earth directly:**
```bash
export DISPLAY=:0
rm -f ~/.googleearth/instance-running-lock
/opt/google/earth/pro/googleearth &
```

**Alternative — create a direct-launch autostart wrapper:**
```bash
cat > ~/.config/autostart/lg.desktop << EOF
[Desktop Entry]
Name=LG
Exec=bash /home/lg{N}/launch-earth-direct.sh
Type=Application
EOF

cat > ~/launch-earth-direct.sh << 'EOF'
#!/bin/bash
export DISPLAY=:0
rm -f $HOME/.googleearth/instance-running-lock
/opt/google/earth/pro/googleearth &
EOF
chmod +x ~/launch-earth-direct.sh
```

## 5. Apache LockFile Fix

On Ubuntu 16.04 (Apache 2.4), the LG install script adds a `LockFile` directive that was removed from Apache 2.4. Apache fails to start.

**Fix:**
```bash
sudo sed -i '/LockFile/d' /etc/apache2/apache2.conf
sudo service apache2 restart
```

## 6. Inter-VM Connectivity

After install, the script creates a 10.42.42.x network on an eth0 alias. Verify all 3 VMs can reach each other:
```bash
ping -c 1 10.42.42.2   # lg1 → lg2
ping -c 1 10.42.42.3   # lg1 → lg3
```

If slaves aren't reachable, the `hosts` file may need updating:
```bash
grep 10.42.42 /etc/hosts
```
Expected:
```
10.42.42.1  lg1
10.42.42.2  lg2
10.42.42.3  lg3
```
