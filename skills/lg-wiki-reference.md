---
name: lg-wiki-reference
description: "Community wiki ops: architecture, commands, KML, troubleshooting."
version: 0.1.0
metadata:
  hermes:
    tags: [LiquidGalaxy, Wiki, Reference, Troubleshooting, Architecture]
---

# LG Wiki Reference

Community-curated knowledge from [LG Wiki](https://lg-wiki-coral.vercel.app/) covering Liquid Galaxy architecture, control commands, KML operations, SSH patterns, and troubleshooting. Covers what the LG wiki says — not a replacement for this rig's specific skills (lg-ssh-control, lg-kml-tours). Use when the user references a common LG problem, wiki page, or community solution.

## When to Use

- User asks about LG architecture, master-slave, how screens sync
- User references something from the "LG Wiki" site
- User asks how control commands work (set refresh, relaunch, reboot, shutdown)
- KML not displaying on screens / "kml not visible"
- Google Earth keeps spinning on startup
- User wants to know why SSH is used vs UDP
- Troubleshooting KML parsing issues, red X errors
- Debugging "KML file not display" problems
- Questions about SetRefresh mechanism for logos
- User asks about running LG commands via SSH
- Questions about protocols (SSH, UDP ViewSync)

## Prerequisites

The wiki is publicly accessible at https://lg-wiki-coral.vercel.app/. No credentials needed.

## Architecture

**Master-Slave Design:** The master initiates commands and manages the system. Slaves operate under the master's control, each driving one display with a fixed angular offset.

**Master responsibilities:**
- Processes user input (SpaceNavigator, touchscreen)
- Calculates trajectories and manages app state (Street View, day/night)
- Handles search queries (looks up coordinates)
- Broadcasts camera state to slaves via UDP (60 Hz)
- Does NOT render pixels (stays lightweight)

**Slave responsibilities:**
- Listen for UDP camera state from master
- Apply fixed angular offset (-80°, -40°, 0°, +40°, +80° for 5-screen)
- Render their unique view slice

**Protocol division:**
- **SSH** (control, from app to master): infrequent, stateful, needs delivery guarantees. File transfer + command execution + auth. Your Flutter app only talks SSH.
- **UDP** (sync, master to all slaves): continuous 60 Hz broadcast, connectionless, loss-tolerant. Packet loss is fine — next update arrives 16ms later. ViewSync is pre-configured in Google Earth on each machine.

## Control Commands

### Set Refresh
Adds `<refreshMode>onInterval</refreshMode><refreshInterval>2</refreshInterval>` to slave `<Link>` elements in `~/earth/kml/slave/myplaces.kml`. Targets `##LG_PHPIFACE##kml/slave_$i.kml` pattern.

### Reset Refresh
Removes the refresh tags from slave myplaces.kml, restoring defaults.

### Relaunch
Restarts the display manager on each frame. Checks for `lxdm` or `lightdm`, then runs `sudo service <svc> restart`.

### Restart
Reboots each frame via `sudo reboot`.

### Shutdown
Powers off each frame via `sudo poweroff`.

## KML Troubleshooting

### KML Not Displaying (Common Causes)

1. **NetworkLink refresh not set** — Slave screens need refreshInterval to detect KML changes. Without it, you must relaunch to see updates. Fix: SetRefresh or manually add refresh tags in slave myplaces.kml.

2. **LookAt missing in Document** — Without a `<LookAt>`, Earth loads at default view (Paris). Content exists but is off-screen. Always include a LookAt.

3. **flyToView=1 not set** — Without `<flyToView>1</flyToView>` in the master NetworkLink, KML updates via refresh show placemarks but never move the camera.

4. **Placemarks in wrong layer** — Placemarks saved to "My Places" instead of deployed via NetworkLink won't trigger ViewSync, so slaves stay blank.

### Debugging KML (Wiki Method)

1. Open Google Earth Pro on master, File, Open (Ctrl+O), select `.kml`
2. Check if it renders under Temporary Places
3. Save to My Places, verify it appears
4. Do NOT use My Places for final deployment — it bypasses NetworkLink and breaks ViewSync. Debug only, then fix the network script.

### Red "X" Missing Asset

Google Earth parsed the `<href>` but cannot find the image.

**Fix A (dynamic app):** Use your machine actual LAN IPv4 address, not `localhost`:
- Wrong: `<href>http://localhost:81/football.png</href>`
- Right: `<href>http://192.168.1.5:81/football.png</href>`

**Fix B (static assets):** Package KML + images into a `.kmz` file. Use clean relative paths in KML (`images/football.png`), then zip KML+images folder into `.kmz`.

### SetRefresh Mechanism (Logos)

If logos/KMLs appear after relaunch but not during live operation, the slave NetworkLink is not polling. SetRefresh adds the refresh tag so slaves auto-poll the KML file every 2 seconds. Without this, slaves read the file once at Earth startup and never update.

Run SetRefresh once, then relaunch Earth. After that, any KML write to `/var/www/html/kml/slave_$i.kml` appears within 2 seconds on that slave.

## Stopping Earth from Spinning

Google Earth may auto-rotate when it starts. To stop it:

1. Open Earth, Tools, Options
2. Reduce Fly To Speed to 0
3. Click Restore Defaults, OK
4. Must be repeated after every relaunch

## Running LG Commands via SSH

From a Flutter app, control commands are executed via SSH using `sshpass`:

```
sshpass -p <password> ssh -t lg$i "echo <password> | sudo -S <command>"
```

- Relaunch: `service lxdm restart` or `service lightdm restart`
- Reboot: `sudo reboot`
- Poweroff: `sudo poweroff`
- Set Refresh: `sed` on `~/earth/kml/slave/myplaces.kml` to inject refresh tags inside `<Link>`
- KML deploy: `echo '<kml>...</kml>' > /var/www/html/kml/slave_$i.kml`

## Common Virtual Setup Issues

| Symptom | Likely Cause | Fix |
|---------|-------------|------|
| Earth launches on master but not slaves | Network error during LG install or wrong Ubuntu version | Re-run setup on problem slave. Use Ubuntu 16.04 only |
| Earth does not start on master | Install/network error | Re-run LG setup with stable internet |
| Unable to locate package | Upgraded Ubuntu past 16.04 | Use Ubuntu 16.04, no upgrades |
| CPU stuck / Kernel panic | Wrong VM core count | Use 2 processor cores per VM |
| Host key verification failed | Improper slave naming | Check `/etc/hostname` and `/etc/hosts` on each VM |
| No route to host on relaunch | Slaves not on same network | Verify NAT network, all VMs on same NAT network |
| Connection timeout | ISP blocked port 22 or wrong network mode | Use NAT Network (not NAT), try different internet |
| Earth keeps spinning | Fly To Speed default | Tools, Options, reduce speed, restore defaults |
| KML works via Open but not via app | SetRefresh not configured | Run SetRefresh, relaunch once, then auto-updates work |
| Red X in place of images | Wrong image path in KML | Use LAN IP or KMZ packaging |
| APK not connecting to network | Missing permission | Add `ACCESS_NETWORK_STATE` to AndroidManifest.xml |

## Verification

Deploy a simple point placemark KML to master.kml and check it appears on the master screen within 3-5 seconds after the 3s NetworkLink refresh cycle.

## References

- `references/lg-repo-patterns.md` — Code patterns from La Palma Volcano Tracking Tool and LG Master Web App repos (orbit, flytoview, SSH, KML upload, forceRefresh)
