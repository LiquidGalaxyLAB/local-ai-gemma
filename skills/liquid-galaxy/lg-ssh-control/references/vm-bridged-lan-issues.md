# VM Bridged LAN — Issues and Diagnostics

## Detection: Is it a VM?

```bash
sshpass -p 'lg' ssh lg@<ip> 'cat /sys/class/dmi/id/product_name'
# Returns "VirtualBox" (or similar) for VMs, hardware string for physical
```

## Cross-frame Root SSH

On VM setups (bridged LAN or tunnel), root SSH keys are not deployed between
frames. The built-in `lg-sudo-bg` calls `ssh -x root@$lg` which fails silently:

```
lg3:            ← label printed before SSH attempt
                 ← blank line = SSH failed (no stderr captured)
lg1:
                 ← blank = SSH failed (lg1 = self via hostname, still fails)
lg2:
                 ← blank = SSH failed
```

**Always verify first:**
```bash
sshpass -p 'lg' ssh lg@<master-ip> 'sudo -S ssh -o ConnectTimeout=3 \
  -o StrictHostKeyChecking=no -o PasswordAuthentication=no root@lg2 "hostname" 2>&1' <<< 'lg'
# → "Permission denied (publickey,password)" on VM rigs
```

**Fix:** Use `lg-relaunch-direct` (sshpass-based) instead of built-in.

## Earth Stuck on "Google Earth Options" Dialog

After relaunch on VM rigs, Earth often launches but blocks on the initial
setup/license dialog (654x566 window titled "Google Earth Options").

### Detection
```bash
sshpass -p 'lg' ssh lg@<master-ip> \
  'DISPLAY=:0 xdotool search --name "Google Earth Options" getwindowname 2>&1'
```
Returns "Google Earth Options" if blocked, empty if clear.

### Dismissal
```bash
sshpass -p 'lg' ssh lg@<master-ip> \
  'DISPLAY=:0 xdotool search --name "Google Earth Options" windowactivate --sync \
    key --delay 200 alt+a 2>&1'
sleep 1
sshpass -p 'lg' ssh lg@<master-ip> \
  'DISPLAY=:0 xdotool search --name "Google Earth Options" windowactivate --sync \
    key --delay 200 Return 2>&1'
```
Alt+A = "Agree" button accelerator; Return = confirm. Adjust if dialog version
differs (check visible buttons with `xdotool search --name "Google Earth Options"
getwindowgeometry`).

## VirtualBox Display Output Naming

VirtualBox VMs name their virtual display outputs `Virtual1`, `Virtual2`, etc.
The vendor xrandr script at `/etc/X11/Xsession.d/45x11-custom_xrandr` targets
`--output default` which doesn't exist — causing resolution to stay at 800x600.

### Current state
```bash
DISPLAY=:0 xrandr | grep connected
# → Virtual1 connected primary 800x600+0+0
# → Virtual2 disconnected
```

### Quick fix (manual resolution set)
```bash
DISPLAY=:0 xrandr --output Virtual1 --mode 1920x1080
```

### Permanent fix (edit xrandr script)
```bash
sudo sed -i 's/--output default/--output Virtual1/g' \
  /etc/X11/Xsession.d/45x11-custom_xrandr
```
Then relaunch Earth or reboot for the script to re-run at session start.
