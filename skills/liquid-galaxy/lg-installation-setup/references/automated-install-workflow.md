# Automated Install Workflow (3-Phase, Master + Slaves)

Captured from a July 2026 session installing LG on a 3-VM VirtualBox cluster with NAT-only slaves and a multi-adapter master.

## When to Use Scripted Install

The official `install.sh` is **interactive** (7+ `read -p` prompts). When the agent has SSH access, use these scripts to automate the entire install. There are two separate workflows:

- **Master (lg1):** Full installer script (replaces interactive install.sh)
- **Slaves (lg2, lg3):** 3-phase install through the master as a NAT jumpbox

---

## Part 1: Master Install Script (lg1)

This script is scp'd to lg1 and run as a bash script. It:
1. Sets all variables directly (no interactive prompts)
2. Uses HTTPS repos (bypasses VirtualBox NAT HTTP blocking)
3. Installs Google Earth via host-side .deb download + scp
4. Preserves the 3-adapter network config after install
5. Fixes Apache LockFile and personality.sh issues

```bash
#!/bin/bash
# Automated LG installation for master (lg1)
MASTER=true
MASTER_IP="192.168.53.3"
MASTER_USER=$USER
MASTER_HOME=$HOME
MASTER_PASSWORD="lg"
LOCAL_USER=$USER
MACHINE_ID="1"
MACHINE_NAME="lg1"
TOTAL_MACHINES="3"
INSTALL_DRIVERS=false
OCTET="42"
GIT_URL="https://github.com/LiquidGalaxyLAB/liquid-galaxy"
EARTH_DEB="https://dl.google.com/dl/earth/client/current/google-earth-stable_current_amd64.deb"
EARTH_FOLDER="/opt/google/earth/pro/"

export DEBIAN_FRONTEND=noninteractive

# Pre-cache sudo
echo "lg" | sudo -S -v

# Clone repo
cd /home/lg1
git clone $GIT_URL 2>&1
USER_PATH=$(pwd)/liquid-galaxy

# Install packages with HTTPS repos
echo "lg" | sudo -S bash -c 'cat > /etc/apt/sources.list << EOF
deb https://archive.ubuntu.com/ubuntu/ xenial main restricted universe multiverse
deb https://archive.ubuntu.com/ubuntu/ xenial-updates main restricted universe multiverse
deb https://archive.ubuntu.com/ubuntu/ xenial-security main restricted universe multiverse
deb https://archive.ubuntu.com/ubuntu/ xenial-backports main restricted universe multiverse
EOF'
echo "lg" | sudo -S apt-get clean
echo "lg" | sudo -S apt-get update -o Acquire::https::Timeout=30
echo "lg" | sudo -S apt-get install -yq python3 python3-pip tcpdump git chromium-browser nautilus openssh-server sshpass squid3 squid-cgi apache2 xdotool unclutter lsb-core lsb

# Install Google Earth (assumes .deb was pre-downloaded and scp'd)
echo "lg" | sudo -S dpkg -i /home/lg1/google-earth.deb
echo "lg" | sudo -S apt-get install -f -y

# Copy LG files
echo "lg" | sudo -S cp -r $USER_PATH/earth/ $HOME/
echo "lg" | sudo -S ln -sf $EARTH_FOLDER $HOME/earth/builds/latest
echo "lg" | sudo -S cp -r $USER_PATH/gnu_linux/home/lg/. $HOME/
echo "lg" | sudo -S cp -r $USER_PATH/gnu_linux/etc/ $USER_PATH/gnu_linux/patches/ $USER_PATH/gnu_linux/sbin/ /
echo "lg" | sudo -S chown -R $LOCAL_USER:$LOCAL_USER $HOME/
echo "lg" | sudo -S chmod +0666 /dev/uinput

# SSH keys (master)
$HOME/tools/clean-ssh.sh

# Prepare SSH files for slaves
mkdir -p ssh-files/etc
echo "lg" | sudo -S cp -r /etc/ssh ssh-files/etc/
mkdir -p ssh-files/root/ ssh-files/user/
echo "lg" | sudo -S cp -r /root/.ssh ssh-files/root/ 2>/dev/null
echo "lg" | sudo -S cp -r $HOME/.ssh ssh-files/user/
zip -FSr "ssh-files.zip" ssh-files
mv ssh-files.zip $HOME/ssh-files.zip 2>/dev/null
rm -rf ssh-files/

# Screens config
$HOME/bin/personality.sh $MACHINE_ID $OCTET

# Preserve custom network config
echo "lg" | sudo -S bash -c 'cat > /etc/network/interfaces << EOF
auto lo
iface lo inet loopback
auto enp0s3
iface enp0s3 inet dhcp
auto enp0s8
iface enp0s8 inet static
  address 192.168.53.3
  netmask 255.255.255.0
auto enp0s9
iface enp0s9 inet static
  address 192.168.1.7
  netmask 255.255.255.0
  gateway 192.168.1.1
EOF'

# Fix /etc/hosts
echo "lg" | sudo -S sed -i '/10.42./d' /etc/hosts
echo "lg" | sudo -S bash -c 'cat >> /etc/hosts << EOF
192.168.53.3  lg1
192.168.53.2  lg2
192.168.53.1  lg3
EOF'

# Apache + PHP web interface
echo "lg" | sudo -S apt-get install -yq php php-cgi libapache2-mod-php
echo "lg" | sudo -S sed -i '/LockFile/d' /etc/apache2/apache2.conf
echo "lg" | sudo -S rm -f /var/www/html/index.html
echo "lg" | sudo -S cp -r $USER_PATH/php-interface/. /var/www/html/
echo "lg" | sudo -S chown -R $LOCAL_USER:$LOCAL_USER /var/www/html/
echo "lg" | sudo -S service apache2 restart

# Autostart Earth on boot
mkdir -p $HOME/.config/autostart/
echo -e "[Desktop Entry]\nName=LG\nExec=bash \"$HOME\"/earth/scripts/launch-earth.sh\nType=Application" > $HOME/.config/autostart/lg.desktop

# Cleanup
echo "lg" | sudo -S rm -rf /home/lg1/liquid-galaxy
```

### Handling Google Earth .deb Download

If the VM can't reach dl.google.com (common through VirtualBox NAT), download on the host and scp:

```bash
# On host/Pi:
wget "https://dl.google.com/dl/earth/client/current/google-earth-stable_current_amd64.deb" -O /tmp/google-earth.deb
scp /tmp/google-earth.deb lg1@<lg1-ip>:/home/lg1/google-earth.deb

# Verify on VM — should be 56057072 bytes
```

---

## Part 2: Slave Install Through NAT Jumpbox (lg2, lg3)

When slaves only have a NAT adapter (10.0.2.x), use lg1 as a jumpbox. Three phased scripts are uploaded to lg1, then deployed to each slave.

### Phase 1: Fix Repos, DNS, Hostname

```bash
#!/bin/bash
# slave-step1.sh — scp to lg1, then to slave, then execute
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
echo lg\${ID} > /etc/hostname && hostname lg\${ID}
sed -i 's/lg\${ID}-VirtualBox/lg\${ID}/g' /etc/hosts
echo 127.0.1.1 lg\${ID} >> /etc/hosts
"
```

Deploy to each slave through lg1:
```bash
sshpass -p 'lg' ssh lg1@<lg1-ip> '
  sshpass -p "lg" scp /home/lg1/slave-step1.sh lg2@10.0.2.12:/home/lg2/
  sshpass -p "lg" ssh lg2@10.0.2.12 "bash /home/lg2/slave-step1.sh 2"
'
```

### Phase 2: Install Packages, Clone Repo

```bash
#!/bin/bash
# slave-step2.sh
ID=\$1
export DEBIAN_FRONTEND=noninteractive
echo "lg" | sudo -S apt-get update -o Acquire::https::Timeout=30 2>&1 | tail -3
echo "lg" | sudo -S apt-get install -yq python3 python3-pip tcpdump git chromium-browser nautilus openssh-server sshpass squid3 squid-cgi apache2 xdotool unclutter lsb-core lsb 2>&1 | tail -5
cd /home/lg\${ID}
[ -d liquid-galaxy ] && rm -rf liquid-galaxy
git clone https://github.com/LiquidGalaxyLAB/liquid-galaxy 2>&1 | tail -2
```

### Phase 3: LG Configuration

```bash
#!/bin/bash
# slave-step3.sh
ID=\$1; MASTER_IP="10.0.2.11"; OCTET=42; HOME="/home/lg\${ID}"

# SSH keys from master
sshpass -p "lg" scp lg1@\${MASTER_IP}:~/ssh-files.zip \${HOME}/
cd \${HOME}; unzip -o ssh-files.zip 2>/dev/null
sudo cp -r \${HOME}/ssh-files/etc/ssh /etc/ 2>/dev/null
sudo cp -r \${HOME}/ssh-files/root/.ssh /root/ 2>/dev/null
sudo cp -r \${HOME}/ssh-files/user/.ssh \${HOME}/ 2>/dev/null
rm -rf \${HOME}/ssh-files*

# LG files from cloned repo
sudo cp -r \${HOME}/liquid-galaxy/earth/ \${HOME}/earth/
sudo ln -sf /opt/google/earth/pro \${HOME}/earth/builds/latest
sudo cp -r \${HOME}/liquid-galaxy/gnu_linux/home/lg/. \${HOME}/
sudo cp -r \${HOME}/liquid-galaxy/gnu_linux/etc/ \${HOME}/liquid-galaxy/gnu_linux/patches/ \${HOME}/liquid-galaxy/gnu_linux/sbin/ /
sudo chown -R lg\${ID}:lg\${ID} \${HOME}/

# Slave KML
sudo sed -i "s/slave_x/slave_\${ID}/g" \${HOME}/earth/kml/slave/myplaces.kml
sudo sed -i "s/sync_nlc_x/sync_nlc_\${ID}/g" \${HOME}/earth/kml/slave/myplaces.kml

# Frame, personality
echo \${ID} > \${HOME}/frame; echo 1 > \${HOME}/screen
sudo \${HOME}/bin/personality.sh \${ID} \${OCTET}

# /home/lg symlink fix
sudo rm -f /home/lg; sudo ln -sf /home/lg\${ID} /home/lg
sudo sed -i 's|/home/lg/personavars.txt|/home/lg'\${ID}'/personavars.txt|g' \${HOME}/etc/shell.conf
sudo sed -i 's|/home/lg/frame|/home/lg'\${ID}'/frame|g' \${HOME}/etc/shell.conf

# NAT network hosts
sudo sed -i '/10.42./d' /etc/hosts
sudo bash -c 'cat >> /etc/hosts << EOF
10.0.2.11  lg1
10.0.2.12  lg2
10.0.2.13  lg3
EOF'

# Autostart
mkdir -p \${HOME}/.config/autostart/
echo -e "[Desktop Entry]\\nName=LG\\nExec=bash \${HOME}/earth/scripts/launch-earth.sh\\nType=Application" > \${HOME}/.config/autostart/lg.desktop
rm -rf \${HOME}/liquid-galaxy 2>/dev/null
```

---

## Known Post-Install Fixes

| Issue | Symptom | Fix |
|-------|---------|-----|
| Apache2 fails | `Invalid command 'LockFile'` | `sudo sed -i '/LockFile/d' /etc/apache2/apache2.conf && sudo service apache2 restart` |
| personality.sh writes to /home/lg/ | `No such file or directory: /home/lg/screen` | `echo 1 > ~/screen; echo 1 > ~/frame` |
| Earth won't start — /home/lg missing | launch-earth.sh silently exits | `sudo ln -sf /home/lg{N} /home/lg` + fix shell.conf paths |
| apt-get hangs at 0% | apt-get update never completes | Switch repos to HTTPS |
| Google Earth download stalls | 0-byte .deb after minutes | Host download + scp (56 MB) |
| sudo: unable to resolve host | Hostname not in /etc/hosts | Add `127.0.1.1 lg{N}` |
