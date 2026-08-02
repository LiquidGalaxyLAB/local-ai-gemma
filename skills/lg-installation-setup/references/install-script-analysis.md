# install.sh Walkthrough

Analysis of the official LG install script at:
https://raw.githubusercontent.com/LiquidGalaxyLAB/liquid-galaxy/master/install.sh

## Configuration Prompts

The script asks for these inputs **interactively via `read -p`**. The agent cannot answer these over SSH — the user must run the script from the VM console.

| Prompt | Master (lg1) | Slave (lg2/lg3) |
|--------|-------------|-----------------|
| Machine id | 1 | 2 or 3 |
| Master machine IP | (auto-detected — see IP detection note below) | User enters master's LAN-reachable IP |
| Master local user password | (not asked) | `lg` (or whatever master's lg password is) |
| Total machines count | 3 | 3 |
| Unique number (octet) | 42 | 42 |
| Install extra drivers? (y/n) | n (unless nVidia GPU) | n |

> **Master IP auto-detection pitfall (multi-adapter VMs):** The script discovers the master IP via `ifconfig | grep --after-context=1 $NETWORK_INTERFACE` where `$NETWORK_INTERFACE` is the interface with the default route (from `route -n`). On a multi-adapter VM (NAT + host-only + bridged), the default route is the **NAT** adapter, so the script shows 10.0.2.15 — which is NOT reachable from the LAN.
>
> **What to do:** Note the shown IP but ignore it. After install, run `hostname -I` to find the bridged IP (e.g. 192.168.1.23). This is the IP that agents and slaves should use.
>
> **When installing slaves,** enter the **bridged** IP (not the NAT IP) of lg1 as the master IP. If you enter 10.0.2.15, the slave won't be able to reach the master.

## Script Phases

### Phase 1: Prerequisites
- Checks Ubuntu OS (`/etc/os-release` must contain "Ubuntu")
- Refuses to run as root
- Clones git repo (`LiquidGalaxyLAB/liquid-galaxy`) if not present
- Upgrades system packages

### Phase 2: Package Installation
Installs: python3, python3-pip, tcpdump, git, chromium-browser, nautilus, openssh-server, sshpass, squid3, squid-cgi, apache2, xdotool, unclutter, lsb-core, lsb, libc6-dev-i386, gcc

If `INSTALL_DRIVERS=true`: libfontconfig1:i386, libx11-6:i386, libxrender1:i386, libxext6:i386, libglu1-mesa:i386, libglib2.0-0:i386, libsm6:i386, nvidia-361

**Pitfall:** `libc6-dev-i386` and `gcc` are for 32-bit compatibility — not strictly needed for 64-bit Earth but the script installs them regardless. On a minimal Ubuntu install, `lsb-core` pulls in many dependencies (~200MB).

### Phase 3: Google Earth Installation
```bash
wget -q $EARTH_DEB   # http://dl.google.com/dl/earth/client/current/google-earth-stable_current_amd64.deb
sudo dpkg -i google-earth*.deb
rm google-earth*.deb
```

**Pitfall:** If the Google download URL fails or times out, the script continues silently. Verify Earth installed: `dpkg -l | grep earth`.

The EARTH_DEB URL is determined by `getconf LONG_BIT`:
- 32-bit: `google-earth-stable_current_i386.deb` 
- 64-bit: `google-earth-stable_current_amd64.deb`

There is NO ARM64 variant — this is the fundamental blocker for ARM LG.

### Phase 4: OS Configuration
- LightDM autologin for `lg` user
- Disables screen blanking, screensaver, lock screen, idle dim
- Hides Unity launcher (auto-hide)
- Sets Chromium as default browser
- Removes update-notifier packages

**Pitfall:** The gsettings calls assume a GNOME/Unity desktop. On Ubuntu 16.04 this works. On other desktops (Xubuntu/Lubuntu) or newer Ubuntu versions, gsettings may fail silently.

### Phase 5: LG Configuration
- Copies `earth/` config files to `$HOME`
- Symlinks Earth build directory: `$HOME/earth/builds/latest → /opt/google/earth/pro/`
- Patches Earth's startup script to set `LC_NUMERIC=en_US.UTF-8`
- Slave-specific: replaces `slave_x` with `slave_<MACHINE_ID>` in myplaces.kml
- Copies dotfiles, sudoers config, AppArmor config
- Chowns everything to `lg` user
- Makes `/dev/uinput` world-writable (0666)

### Phase 6: SSH Configuration
- **Master:** runs `~/tools/clean-ssh.sh` to generate SSH keys, creates `ssh-files.zip`
- **Slave:** SCPs `ssh-files.zip` from master using sshpass, unzips it
- Sets up passwordless SSH between frames

**Pitfall:** The SSH key distribution assumes the master is directly reachable from each slave. On VirtualBox with NAT Network, this works. With other network topologies, it may fail.

## Post-Installation

After reboot:
1. Earth auto-launches via LightDM autostart mechanism
2. Earth default view is centered on Paris (48.8566, 2.3522)
3. First launch may show the "Google Earth Options" dialog — auto-dismiss via xdotool if needed

## Common Failures at Each Phase

| Phase | Failure | Symptom | Fix |
|-------|---------|---------|-----|
| Phase 1 | apt mirror down | `apt-get update` hangs | Switch mirror, retry |
| Phase 2 | libc6-dev-i386 conflicts | Package installation fails | Skip libc6-dev-i386, install rest manually |
| Phase 3 | Earth download fails | No Earth installed after script | Manually download and dpkg -i |
| Phase 3 | dpkg dependency error | Earth deb fails | `sudo apt-get install -f` then retry |
| Phase 5 | SSH setup timeout (slave) | Slave can't find master | Verify master IP, password, network connectivity |
| Post | Earth not auto-starting | `pgrep googleearth` returns nothing | Check `~/.config/autostart/lg-earth.desktop` exists |
| Post | Earth stuck on dialog | Earth starts but shows setup dialog | xdotool search/key auto-dismiss (see lg-ssh-control references) |
