# Slave Installation Through NAT Jumpbox

Captured from a July 2026 session where lg2 and lg3 had **only NAT adapters**
(10.0.2.12, 10.0.2.13) and were reachable only through lg1 (master) as a
SSH jumpbox. The official `install.sh` could NOT be run interactively on slaves
because they had no console access from the agent — the entire installation was
driven from lg1 via nested `sshpass` commands.

## Prerequisites

- lg1 (master) is fully installed with LG (Google Earth, Apache, SSH keys, etc.)
- sshpass installed on lg1 (`apt-get install -y sshpass`)
- Slaves have at least:
  - Ubuntu 16.04 installed
  - SSH server running (see EOL repo fix in SKILL.md before apt-get)
  - HTTPS repos configured (same as master — see SKILL.md Critical Pre-Flight)
  - A user account (may be `lg2`/`lg3` not `lg` — adjust accordingly)
  - DNS configured (`echo nameserver 8.8.8.8 > /etc/resolv.conf`)

## Overview: What the Slave Install Does

Unlike the master (which needs Google Earth, Apache, PHP, and KML serving),
slaves only need:
1. LG files (earth/, bin/, etc/) — copied from the cloned repo
2. SSH keys from master — so the master can control slaves
3. Slave-specific KML myplaces.kml — replaces `slave_x` with `slave_N`
4. Personality configuration — frame ID, screen count
5. Autostart — Earth launches on boot
6. /etc/hosts — maps lg1/lg2/lg3 to the NAT IPs (10.0.2.x)

## Step-by-Step Slave Install (3-Phase Scripted Approach)

**⚠️ Prerequisite: Add NOPASSWD sudo on the slave first.** Without it, every sudo call inside the script will silently fail when run over SSH:

```bash
echo "lg2 ALL=(ALL) NOPASSWD: ALL" | sudo tee /etc/sudoers.d/lg2-nopasswd
sudo chmod 0440 /etc/sudoers.d/lg2-nopasswd
```

### Phase 1: Repos, DNS, Hostname

Create and deploy `slave-step1.sh`:

```bash
#!/bin/bash
# Step 1: Fix repos, DNS, hostname
ID=$1
echo "lg" | sudo -S bash -c "
cat > /etc/apt/sources.list << EOF
deb https://archive.ubuntu.com/ubuntu/ xenial main restricted universe multiverse
deb https://archive.ubuntu.com/ubuntu/ xenial-updates main restricted universe multiverse
deb https://archive.ubuntu.com/ubuntu/ xenial-security main restricted universe multiverse
deb https://archive.ubuntu.com/ubuntu/ xenial-backports main restricted universe multiverse
EOF
echo nameserver 8.8.8.8 > /etc/resolv.conf
echo nameserver 1.1.1.1 >> /etc/resolv.conf
echo lg\${ID} > /etc/hostname
hostname lg\${ID}
sed -i 's/lg\${ID}-VirtualBox/lg\${ID}/g' /etc/hosts
echo 127.0.1.1 lg\${ID} >> /etc/hosts
"
echo "Step 1 done: hostname lg${ID}, repos fixed"
```

Deploy and run from lg1:
```bash
sshpass -p 'lg' scp slave-step1.sh lg1@<lg1-ip>:/home/lg1/
sshpass -p 'lg' ssh lg1@<lg1-ip> \
  'sshpass -p "lg" scp /home/lg1/slave-step1.sh lg2@10.0.2.12:/home/lg2/ && \
   sshpass -p "lg" ssh lg2@10.0.2.12 "bash /home/lg2/slave-step1.sh 2"'
```

### Phase 2: Packages + LG Repo Clone

Create `slave-step2.sh`:

```bash
#!/bin/bash
# Slave Step 2: Install packages, clone LG repo
ID=$1
export DEBIAN_FRONTEND=noninteractive

echo "lg" | sudo -S apt-get update -o Acquire::https::Timeout=30 2>&1 | tail -3
echo "lg" | sudo -S apt-get install -yq python3 python3-pip tcpdump git \
    chromium-browser nautilus openssh-server sshpass squid3 squid-cgi \
    apache2 xdotool unclutter lsb-core lsb 2>&1 | tail -5

cd /home/lg${ID}
git clone https://github.com/LiquidGalaxyLAB/liquid-galaxy 2>&1 | tail -2
echo "Step 2 done: packages installed, repo cloned"
```

Deploy and run the same way (scp to lg1 → scp to slave → remote bash).

### Phase 3: LG Configuration

Create `slave-step3.sh`:

```bash
#!/bin/bash
ID=$1
MASTER_IP="10.0.2.11"
OCTET=42
HOME="/home/lg${ID}"

export DEBIAN_FRONTEND=noninteractive

# Get SSH keys from master
sshpass -p "lg" scp -o StrictHostKeyChecking=no lg1@${MASTER_IP}:~/ssh-files.zip ${HOME}/
cd ${HOME}
unzip -o ssh-files.zip -d ${HOME}/ 2>/dev/null
echo "lg" | sudo -S cp -r ${HOME}/ssh-files/etc/ssh /etc/ 2>/dev/null
echo "lg" | sudo -S cp -r ${HOME}/ssh-files/root/.ssh /root/ 2>/dev/null
echo "lg" | sudo -S cp -r ${HOME}/ssh-files/user/.ssh ${HOME}/ 2>/dev/null
rm -rf ${HOME}/ssh-files* 2>/dev/null

# Copy Earth and LG files
echo "lg" | sudo -S cp -r ${HOME}/liquid-galaxy/earth/ ${HOME}/earth/
echo "lg" | sudo -S ln -sf /opt/google/earth/pro ${HOME}/earth/builds/latest 2>/dev/null
echo "lg" | sudo -S cp -r ${HOME}/liquid-galaxy/gnu_linux/home/lg/. ${HOME}/
cd ${HOME}/dotfiles 2>/dev/null
for f in *; do [ -f "$f" ] && mv "$f" ".$f" 2>/dev/null; done
cd - > /dev/null
echo "lg" | sudo -S cp -r ${HOME}/liquid-galaxy/gnu_linux/etc/ \
    ${HOME}/liquid-galaxy/gnu_linux/patches/ ${HOME}/liquid-galaxy/gnu_linux/sbin/ /
echo "lg" | sudo -S chmod 0440 /etc/sudoers.d/42-lg 2>/dev/null
echo "lg" | sudo -S chown -R lg${ID}:lg${ID} ${HOME}/
echo "lg" | sudo -S chmod +0666 /dev/uinput

# Slave KML
echo "lg" | sudo -S sed -i "s/slave_x/slave_${ID}/g" ${HOME}/earth/kml/slave/myplaces.kml
echo "lg" | sudo -S sed -i "s/sync_nlc_x/sync_nlc_${ID}/g" ${HOME}/earth/kml/slave/myplaces.kml

# Frame ID and personality
echo ${ID} > ${HOME}/frame
echo 1 > ${HOME}/screen
echo "lg" | sudo -S ${HOME}/bin/personality.sh ${ID} ${OCTET} 2>&1 | tail -3

# Hosts for NAT network
echo "lg" | sudo -S sed -i '/10.42./d' /etc/hosts
echo "lg" | sudo -S bash -c 'cat >> /etc/hosts << EOF
10.0.2.11  lg1
10.0.2.12  lg2
10.0.2.13  lg3
EOF'

# Autostart
mkdir -p ${HOME}/.config/autostart/
echo -e "[Desktop Entry]\nName=LG\nExec=bash ${HOME}/earth/scripts/launch-earth.sh\nType=Application" \
  > ${HOME}/.config/autostart/lg.desktop
```

## Pitfalls

| Problem | Cause | Fix |
|---------|-------|------|
| `sudo: unable to resolve host lg` | Hostname change isn't reflected in `/etc/hosts` yet | Run the hosts fix from Phase 1 or add `127.0.1.1 lg<N>` to `/etc/hosts` after hostname change |
| Var `$ID` not expanding in nested SSH | Quoting depth: `${ID}` in a double-quoted heredoc inside a nested sshpass command doesn't survive | Use single-quoted heredocs with proper escaping, or write the script file on the destination and pass ID as `$1` |
| personality.sh writes to `/home/lg/` not `/home/lgN/` | Script hardcodes `/home/lg/` paths | Create `~/frame` and `~/screen` manually before running personality |
| Slave Earth won't auto-start | Autostart .desktop file user mismatch (e.g. file owned by root) | `chown -R lgN:lgN ~/.config/autostart/` |
| **SSH key sync fails on non-standard usernames** | `MASTER_HOME=$HOME` resolves to `/home/lg3` on slave, not `/home/lg1` where `ssh-files.zip` lives | Regen zip on master (`cd ~ && zip -r ssh-files.zip .ssh/`), scp manually to `/home/lgN/`, then `unzip` and `cp -r` (see `console-first-install.md` for exact commands) |
