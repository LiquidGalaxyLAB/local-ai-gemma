# VM LG System Launch Fix (Post-Reinstall Troubleshooting)

After a fresh install of LG on VirtualBox VMs with non-standard usernames (lg1/lg2/lg3 instead of lg), Earth won't auto-launch and `lg-run` fails. This reference captures the full remediation order.

## Root Cause Chain

```
install.sh → username lg1/lg2/lg3 (not lg)
  → /home/lg doesn't exist
  → personality.sh fails silently (no frame/screen files)
  → shell.conf can't source personavars.txt
  → launch-earth.sh exits early (FRAME_NO unset)
  → Autostart does nothing → grey desktop on all VMs
```

On top of that:
- `lg-run` SSHs as `lg@hostname` but user is `lg1`/`lg2`/`lg3` → `Permission denied`
- `run-earth-bin.sh` calls `lg-sudo killall` → `ssh root@slave` → hangs asking for root password
- `~/earth/scripts/run-earth-bin.sh` expands `~` on the local machine (lg1) before SSH sends it → slaves get wrong path

## Fix Order (Do These Steps on lg1)

### Step 1: Create /home/lg Symlink

```bash
sudo rm -f /home/lg
sudo ln -sf /home/lg{N} /home/lg    # N = 1, 2, or 3
```

Also create frame/screen files manually:
```bash
echo 0 > /home/lg1/frame    # 0 = master
echo 1 > /home/lg1/screen
```

**Frame numbering for 3-screen setups:** lg1=0 (master), lg2=1 (slave, yaw -36.5), lg3=2 (slave, yaw +36.5). Do NOT use hostname suffix (e.g. lg3 → 3) — the `write-drivers-ini.sh` wraps frames > LG_FRAMES_MAX/2 around, so frame 3 wraps to 0 (=master again, wrong for a slave).

### Step 2: Run write-drivers-ini.sh

```bash
cd /home/lg1 && bash ~/earth/scripts/write-drivers-ini.sh
```

Expected master output:
```
MASTER: true, SLAVE: false, YAW: 0
ViewSync/send = true, ViewSync/receive = false
```

Expected slave output:
```
MASTER: false, SLAVE: true, YAW: -36.5 (lg2) or +36.5 (lg3)
ViewSync/send = false, ViewSync/receive = true
```

### Step 3: Clear Stale SSH Host Keys (Post-Reinstall)

After reinstall, VMs have new SSH host keys. Stale keys in `/etc/ssh/ssh_known_hosts` cause:
```
Host key verification failed
Password authentication is disabled to avoid man-in-the-middle attacks
```

Fix on the master (lg1):
```bash
ssh-keygen -f /etc/ssh/ssh_known_hosts -R 10.42.42.2
ssh-keygen -f /etc/ssh/ssh_known_hosts -R 10.42.42.3
ssh-keygen -f ~/.ssh/known_hosts -R 10.42.42.2
ssh-keygen -f ~/.ssh/known_hosts -R 10.42.42.3
```

### Step 4: Set Up User-Level SSH Keys

`lg-run`/`lg-run-bg` use plain `ssh` (not `sshpass`), so passwordless keys are required:

```bash
[ ! -f ~/.ssh/id_rsa ] && ssh-keygen -t rsa -N "" -f ~/.ssh/id_rsa
ssh-copy-id lg1@lg1

for host in lg2 lg3; do
  sshpass -p "lg" ssh-copy-id -o StrictHostKeyChecking=no $host@$host
done

# Self-keys on slaves
for host in lg2 lg3; do
  ssh -o StrictHostKeyChecking=no $host@$host "
    [ ! -f ~/.ssh/id_rsa ] && ssh-keygen -t rsa -N '' -f ~/.ssh/id_rsa
    cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys
    chmod 600 ~/.ssh/authorized_keys
  "
done
```

### Step 5: Patch lg-run/lg-run-bg for Non-Standard Usernames

`lg-run` SSHs as `lg@$lg` but users are `lg1`/`lg2`/`lg3`. Patch to map hostname→username:

```bash
cat > /home/lg1/bin/lg-run << 'SCRIPT'
#!/bin/bash
. ${HOME}/etc/shell.conf
while [ $# -gt 0 ]; do
  case $1 in
    --hosts|-h) shift; LG_FRAMES="$1" ;;
    *) CMD="$CMD $1" ;;
  esac
  shift
done
[ -z "${LG_FRAMES}" ] && echo "LG_FRAMES is empty" && exit 1
lg-ctl-master
for lg in $LG_FRAMES; do
  echo; echo $lg:
  case "$lg" in
    lg1) USER="lg1" ;; lg2) USER="lg2" ;; lg3) USER="lg3" ;;
    *)   USER="lg" ;;
  esac
  ssh -o StrictHostKeyChecking=no -tt -x $USER@$lg "$CMD"
done
exit 0
SCRIPT
chmod +x /home/lg1/bin/lg-run
```

Same patch for `lg-run-bg` (add `-f` flag to SSH).

### Step 6: Fix launch-earth.sh Path Resolution

In `launch-earth.sh`, the `lg-run-bg` call uses `~/earth/scripts/run-earth-bin.sh` which expands the tilde on lg1 before sending over SSH. Slaves receive `/home/lg1/...` which doesn't exist on them.

Fix — use single quotes to preserve the tilde:
```bash
# Change this:
lg-run-bg ${SCRIPDIR}/run-earth-bin.sh
# To this:
lg-run-bg 'bash ~/earth/scripts/run-earth-bin.sh'
```

### Step 7: Patch run-earth-bin.sh to Skip lg-sudo

The master's `while true` loop calls `lg-sudo killall googleearth-bin` which SSHs as `root@slave` — no root SSH keys on VMs.

```bash
sed -i 's/lg-sudo killall googleearth-bin/: # lg-sudo disabled for VM/' ~/earth/scripts/run-earth-bin.sh
```

**⚠️ Do NOT leave an empty `then` block.** Ubuntu 16.04 bash rejects `if ... ; then # comment; fi` (comment doesn't count as a statement). Always keep `:` (no-op).

### Step 8: Patch Autostart (Until SSH Works Cross-Frame)

Create a direct-launch autostart that works independently:

```bash
cat > /home/lg1/.config/autostart/lg.desktop << 'EOF'
[Desktop Entry]
Name=LG
Exec=bash /home/lg1/launch-lg1-earth.sh
Type=Application
EOF

cat > /home/lg1/launch-lg1-earth.sh << 'EOF'
#!/bin/bash
. ${HOME}/etc/shell.conf
FRAME_NO=$(cat ${HOME}/frame 2>/dev/null)
export DISPLAY=:0
sleep 3
rm -f ${HOME}/.googleearth/instance-running-lock
if [[ "${FRAME_NO}" = "0" ]]; then
    /home/lg1/earth/scripts/launch-earth.sh
else
    /opt/google/earth/pro/googleearth &
fi
EOF
chmod +x /home/lg1/launch-lg1-earth.sh
```

### Step 9: Launch the LG System

```bash
export DISPLAY=:0
. /home/lg1/etc/shell.conf
bash /home/lg1/earth/scripts/launch-earth.sh
```

Wait 15s, then verify:
```bash
for host in lg1 lg2 lg3; do
  U="lg$host"
  PID=$(ssh -o StrictHostKeyChecking=no $U@$host "pgrep googleearth-bin" 2>/dev/null)
  echo "$host: PID=${PID:-NOT RUNNING}"
done
```

## Frame Number Reference (3-Screen Setup)

| Host | Frame | Yaw | Role | ViewSync |
|------|-------|-----|------|----------|
| lg1  | 0     | 0°   | Master (center) | send=true |
| lg2  | 1     | -36.5° | Slave (right) | receive=true |
| lg3  | 2     | +36.5° | Slave (left) | receive=true |

Frame 3 (if set) wraps to 0 in `write-drivers-ini.sh` because `3 > 3/2` → `FRAME_NO = 3-3 = 0` → treated as master. This is the standard LG behavior but breaks when hostname-based frame numbers are used.

## Earth Running ≠ LG Running

Bare Earth launch bypasses:
- ViewSync configuration (drivers.ini)
- myplaces.kml NetworkLink setup
- Tile cache management
- Crash-recovery while loop
- /tmp/query.txt monitor
- KML serving through Apache
