# Console-First Install: Lessons from a Real Session

## Core Lesson

The official `install.sh` from the LG repo is designed to run from a desktop VM terminal. Attempting to automate it over SSH (piped inputs, wrapper scripts, patched variables) costs hours and produces the same result as running it from the console in 15 minutes.

**Rule:** When a user asks "install LG on these VMs", give them the **exact commands to paste into the VM console**. Do NOT write SSH automation for the install phase.

## What Went Wrong (Agent-Driven SSH)

| Problem | Cause | Fix |
|---------|-------|-----|
| `sudo -v` hangs | Script reads from TTY; piped `printf` feeds are consumed by sudo prompt, starving subsequent `read` prompts | Can't fix cleanly — use console |
| HTTP downloads stall | VirtualBox NAT blocks port 80. `dl.google.com` HTTP → 0% forever | HTTPS helps for Earth .deb, but install.sh hardcodes HTTP |
| `sudo` cache doesn't propagate | `echo \| sudo -S -v` caches for that process only; child processes get "no tty" | NOPASSWD sudo fixes it, but reboot still fails |
| `reboot` fails over SSH | `reboot` needs logind/init daemon TTY access even with NOPASSWD | Must run manually from console |
| git clone is slow (93MB) | Through VirtualBox NAT, GitHub HTTPS clone is 3-5+ min | Clone on host, tarball only needed subdirs (944K) |
| earth/ directory missing | Script's `cp -r` sometimes fails silently when $USER_PATH is wrong | Must verify post-install and re-copy |
| Apache fails to start | Install.sh adds deprecated `LockFile` directive to Apache 2.4 | `sudo sed -i '/LockFile/d' /etc/apache2/apache2.conf` |

## User Preference Signal

The user said **"we dont need to deal with ggl earth shit. I NEED LIQUID GALAXY!!"** and **"remove old slop and install liquid galaxy"**.

Translation: stop building custom install scripts and just run the official one. The official `bash <(curl -s ...)` command is what the user expects. Custom automation is perceived as "slop."

## Optimal Workflow (For Future Sessions)  

```
1. User says "install LG on 3 VMs"  
2. Say: "Great — I need you to run one command in each VM console."  
3. Paste the exact commands with the expected answers  
4. After install, verify remotely via SSH  
5. Fix Apache LockFile, /home/lg symlink, and /etc/hosts  
6. Done  
```  

## Post-Install: Earth Grey Screen / Not Starting  

After reboot, Earth often isn't running even though the install completed. Three recurring causes:  

### 1. Stale Instance Lock  

```bash
# Check: file points to a PID that no longer exists  
ls -la ~/.googleearth/instance-running-lock
# Fix:
rm -f ~/.googleearth/instance-running-lock
rm -f /tmp/query.txt
```

### 2. Resolution at 800x600 (VirtualBox "Virtual1" Display)  

The `earth-fullscreen.sh` script modifies `45x11-custom_xrandr` which targets display output named `default`. VirtualBox VMs name their display `Virtual1`.  

```bash
# Fix resolution:
xrandr --output Virtual1 --mode 1920x1080
# Also patch the script so it works after future full-screen toggles:
sudo sed -i 's/output default/output Virtual1/g' ~/tools/45x11-custom_xrandr
```

### 3. launch-earth.sh Hangs on SSH to Slaves  

The `launch-earth.sh` script calls `lg-run killall` which SSHes to all frames. If slaves are unreachable (rebooting or SSH not running), the script blocks indefinitely.  

```bash
# Kill the stuck launch, then start Earth directly:
pkill -f launch-earth
pkill -f run-earth-bin
export DISPLAY=:0
/opt/google/earth/pro/googleearth &
```

## ⚠️ SSH Key Sync Bug (Non-Standard Usernames)  

When slaves have non-standard usernames (`lg2`/`lg3` instead of `lg`), the install.sh sets `MASTER_HOME=$HOME` which on a slave resolves to `/home/lg3` — not `/home/lg1`. This causes `scp $MASTER_IP:$MASTER_HOME/ssh-files.zip` to fail.  

**Symptom:** Slave output shows "Permission denied, please try again" during SSH key sync phase, followed by "unzip: cannot find ssh-files.zip".  

**Fix — regenerate and push keys manually after install:**  

```bash
# On master (lg1):
cd ~ && mkdir -p ssh-files/etc ssh-files/root ssh-files/user
sudo cp -r /etc/ssh ssh-files/etc/
sudo cp -r /root/.ssh ssh-files/root/
sudo cp -r ~/.ssh ssh-files/user/
zip -FSr ssh-files.zip ssh-files
sudo chown lg1:lg1 ssh-files.zip
rm -rf ssh-files

# On each slave (via master as jumpbox):
sshpass -p "lg" scp lg1@10.0.2.11:~/ssh-files.zip ~/
unzip -o ssh-files.zip
sudo cp -r ssh-files/etc/ssh /etc/
sudo cp -r ssh-files/root/.ssh /root/
sudo cp -r ssh-files/user/.ssh ~/
sudo chmod 0600 ~/.ssh/lg-id_rsa
sudo chown -R lgN:lgN ~/.ssh
rm -rf ssh-files*
```

## What SHOULD be Automated Over SSH  

Only the **post-install fixups**:  

- Apache LockFile fix  
- /home/lg symlink (if username isn't `lg`)  
- shell.conf path fix (if username isn't `lg`)  
- /etc/hosts for internal IPs  
- KML refresh setup  
- Deploy helper scripts (lg-relaunch-direct, etc.)  
