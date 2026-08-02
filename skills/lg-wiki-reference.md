---
name: lg-wiki-reference
description: "Community wiki ops: architecture, commands, KML, troubleshooting."
version: 0.3.0
metadata:
  hermes:
    tags: [LiquidGalaxy, Wiki, Reference, Troubleshooting, Architecture]
---

# LG Wiki Reference

Community-curated knowledge from [LG Wiki](https://lg-wiki-coral.vercel.app/) covering Liquid Galaxy architecture, control commands, KML operations, SSH patterns, and troubleshooting. Covers what the LG wiki says — not a replacement for this rig's specific skills (lg-ssh-control, lg-kml-tours). Use when the user references a common LG problem, wiki page, or community solution.

## When to Use

- User asks about LG architecture, master-slave, how screens sync
- User references something from the "LG Wiki" site
- User asks "what's the standard/logic" for an LG feature
- User asks how to show text, balloons, or data screens on LG
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

## User Preference

When the user asks "what's the standard/logic" or "what does the wiki say" about an LG feature, answer with **the wiki's official answer first** (the documented standard/procedure), then add any VM-specific caveats or rig-specific notes as a separate section. Do not lead with caveats or workarounds — the wiki is the authoritative standard. This applies to: text display, KML balloons, orbit patterns, screen layout conventions, SSH patterns, and any feature the wiki documents.

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

## KML Balloon & Text Display (Wiki Standard)

The wiki has two dedicated pages for text/balloon display. The standard approach uses **KML BalloonStyle with CDATA** sent to the **rightmost slave screen** via SSH echo.

### KML Balloon Definition (wiki)
"An element used to display information or content, typically associated with a specific location on a map, often appearing as a pop-up window when clicked or hovered over."

### Wiki's Balloon KML Pattern
From "How To Send A Simple Balloon Including Some Data On The Right-Most Screen?":

```xml
<Placemark>
  <name>Location</name>
  <Style>
    <BalloonStyle>
      <bgColor>bb000000</bgColor>
      <text><![CDATA[
        <div style="font-family: Arial, sans-serif; color: #000000; padding: 15px;">
          <h2>Location Details</h2>
          <p><b>Place Name:</b> $placeName</p>
          <p><b>Latitude:</b> $latitude</p>
          <p><b>Longitude:</b> $longitude</p>
        </div>
      ]]></text>
    </BalloonStyle>
  </Style>
  <gx:balloonVisibility>1</gx:balloonVisibility>
  <Point>
    <coordinates>$longitude,$latitude,0</coordinates>
  </Point>
</Placemark>
```

Key elements:
- **`<BalloonStyle>`** with `<text>` containing CDATA-wrapped HTML — defines the balloon appearance
- **`<gx:balloonVisibility>1</gx:balloonVisibility>`** — auto-opens the balloon without requiring a click
- **`<bgColor>`** — semi-transparent background (bb000000 = dark)
- Placemark coordinates set the balloon's geographic anchor point

### Deployment (Flutter, from wiki)
The KML is sent to the rightmost slave via a single SSH command:
```dart
echo '$kmlContent' > /var/www/html/kml/slave_$rightMostScreen.kml
```
The wiki's `sendBallonKml()` function calculates the rightmost screen, generates the KML via `generateBalloonKml()`, and writes it to `slave_<N>.kml`.

### VM Caveat (this rig — verified July 2026)
On this VM rig (Earth 7.3.3), **CDATA anywhere in KML silently drops the entire Placemark** — the wiki's CDATA balloon pattern renders nothing. The working variant uses **escaped HTML entities** instead of CDATA in `<BalloonStyle><text>` (e.g. `&lt;div&gt;` instead of `<![CDATA[<div>]]>`), keeping `<gx:balloonVisibility>1</gx:balloonVisibility>` for auto-open. This escaped variant was confirmed visible on this rig. **Preferred implementation: the news-card balloon** (dark HUD cards, category color bars, headlines, source+timestamp, summary, badges) — see `lg-kml-tours` skill, `scripts/news_card_balloon.py`. Coordinates are always **longitude,latitude** order. See `lg-ssh-control` Procedure 14 for the complete working workflow. On physical LG hardware with Google Earth Pro, the wiki's CDATA pattern works as documented.

### Screen Placement (ROOT FORMULA — LG Wiki standard)
Balloons/text go ONLY to the rightmost screen. **Root formula: screen numbering starts at 1 with the master (lg1); total screens = N (lg1..lgN). Right-most screen number = floor(N/2) + 1.** Left-most = floor(N/2) + 2. For N=3: rightmost = 2 → **slave_2.kml** (lg2), leftmost = 3 (lg3). For N=5: rightmost = 3, leftmost = 4. Never deploy balloons to master.kml or non-rightmost slaves.

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

## Installation Guide (from wiki)

### Ubuntu Setup
- **Recommended version:** Ubuntu 16.04
- **User:** `lg`, password `lqgalaxy`
- **Hostname pattern:** `lgX` (X = machine number)
- Do NOT upgrade system versions. Use 4GB+ USB, Rufus for bootable media.

### LG Software Installation
1. `sudo apt update && sudo apt install curl lsb lsb-core`
2. On master: `bash <(curl -s https://raw.githubusercontent.com/LiquidGalaxyLAB/liquid-galaxy/master/install.sh)`
3. Install params: machine ID, total machine count, unique octet, extra drivers (n)
4. Slaves: run same script, provide master IP and master password
5. Reboot after install

### drivers.ini Configuration
**Master:** `ViewSync/send = true; ViewSync/receive = false; ViewSync/hostname = BROADCAST_ADDRESS`
**Slaves:** `ViewSync/send = false; ViewSync/receive = true; ViewSync/hostname = BROADCAST_ADDRESS`

Adjust `yawOffset` for slaves. Run `~/tools/earth-fullscreen.sh && sudo reboot` for full screen.

### Useful Commands
| Command | Purpose |
|---------|---------|
| `lg-poweroff` | Power off all connected PCs |
| `lg-reboot` | Reboot all connected PCs |
| `lg-relaunch` | Restart Earth (display manager) on all PCs |
| `ifconfig` | Check network configuration |

### Relaunch vs Reboot (wiki)
- **lg-relaunch:** Restarts only the display manager (lxdm/lightdm). Earth reloads. Faster, keeps network state.
- **lg-reboot:** Full OS reboot. Slower but clears all cached state.

## Complete LG Wiki Page Index

The new wiki at lg-wiki-coral.vercel.app has 80+ pages organized in a sidebar. All secondary pages use hash-based routing under `/docs/dynamic#<id>`.

### Core Pages (direct routes)
| Page | URL |
|------|-----|
| Architecture (master-slave, UDP, SSH) | `/docs/arc` |
| Rig Installation (Ubuntu + LG setup) | `/docs/rig` |
| Control Commands (refresh, relaunch, reboot) | `/docs/control` |

### SSH & Connection
| Page | Hash ID |
|------|---------|
| Running LG Commands via SSH | `#66602a8b683fa6a7971b` |
| Maintaining SSH Connection on Flutter | `#6660361c747cd874e050` |
| MultiSSH Service for LG | `#67ddaf949fbd881fbd62` |
| Logging SSH Command Outputs | `#666036f0630bd3cf6b03` |
| Why SSH Can't Be Used in Client JS | `#67882466c9690cb6ac4d` |
| Connecting LG to Devices Outside Host | `#666afc8eef9a656c2f09` |
| Port Forwarding for Physical Devices | `#66604422874926988a5b` |
| Targetting Specific Slave Rigs | `#66602964e1c6b1627936` |

### KML Operations
| Page | Hash ID |
|------|---------|
| Brief on KMLs with LG | `#6661b4404ef6ba84d22d` |
| KML and Its Use in LG Tasks | `#6663172dbe88252a2f84` |
| What is KML? | `#666327363d09ba7292c3` |
| How to Pin a Place with KML Balloon | `#6662bcf1d0b8e0d6ad35` |
| KML File Not Display (Troubleshooting) | `#6666b8267ad2bd7e42cb` |
| Troubleshooting KML Parsing Issues | `#666023ca863b8af4ef75` |
| Uploading KML on Specific Monitors | `#666ab534d2d64944dd56` |
| Generating KML Files Using Flutter | `#666ac351bd237116473c` |
| Dynamic KML Overlay Creation | `#67c0c03fca52e5a4c1bc` |
| Generating KML Elements Using Python | `#67ae2b76af1ebce54eb5` |
| KML Debugging & Verification Method | `#69c3f3f25988c25afd36` |
| Red X Missing Asset Troubleshooting | `#69c3fce391833fb3d9b1` |
| Viewing KML After Upload | `#67d853cc2e4b0005ebdb` |
| Creating KML Tour Viz Screen in Flutter | `#67dc92c51466a62bfbfa` |
| Zoom In/Out in KML Viz Using Bloc | `#67dc9820685ad9636bbf` |
| 3D KML Creation and Coloring | `#699322ab13c984496b20` |
| Logos/KMLs Not Appearing (Refresh) | `#699708923cd369eedc1a` |

### Orbits & Camera Control
| Page | Hash ID |
|------|---------|
| Research on Displaying Orbits | `#65f81004d283a185c05a` |
| Orbiting Command | `#66607ec74a9f59b8a5d4` |
| How to Orbit Around a Coordinate | `#6662b72daa4f3ddefe86` |
| Sending Directional/Rotational Commands | `#66603a04e427cf102222` |
| Searching for a Place (Execute Method) | `#66607ac9f192665bb1ef` |
| Flying to Locations (Flutter) | `#66630d02a23eca877bcf` |
| Creating Large Orbits in LG | `#6661723fa39801face6a` |
| Optimizing Navigation & View Control | `#6669c8e7aecc1e046098` |
| Advanced Camera Tour Animations (Spline) | `#68051d743aab017e1d0a` |
| Advanced LG Camera Control | `#69931ce42a94b69d3aae` |
| Automated Cinematic Fly-Through Tours | `#699de4d886465db36eb1` |
| Orbit Motion Play Animation | `#698f27a8a959418ede2e` |

### Earth & Screen Configuration
| Page | Hash ID |
|------|---------|
| How to Stop Earth from Spinning | `#66685280a2df9343fec6` |
| How LG Screens Talk to Each Other | `#66632526200c8a75ae99` |
| Screen Config & View Angle Calculation | `#699ddcbbbb0f112e9288` |
| Stop Earth Spinning on Startup | `#666b02a29bf201f34757` |
| SetRefresh for Slaves (Logos) | `#666875dd62747534303f` |
| Sending Logos/Legends to Leftmost Slave | `#666876afe021b4017409` |
| Duplicate Earth on Slaves / Blank Master | `#699f2fb9794de55907d8` |
| Topic 3: Google Maps in Flutter App | `#66687b67466b30644c8c` |
| Understanding Lg-Relaunch | `#698dc2010d3512f3058a` |
| Significance of Clean KML Button | `#698dc2030bf876210aee` |
| Changing Celestial Bodies (Earth/Moon/Mars) | `#698f1ad11199d4b0d01f` |
| Sending Balloon to Rightmost Screen | `#698f239779dbaad8a314` |
| Behind the Working of Each LG Command | `#67c6dfbcf1d05277993e` |
| MultiSSH Service for LG | `#67ddaf949fbd881fbd62` |
| Screenshot Integration for LG | `#67ddaffa6af5825a1aee` |
| Mapping Joystick to Control Earth | `#699c2fef7bf0a6086c33` |
| Duplicate Earth on Slaves / Blank Master | `#699f2fb9794de55907d8` |
| Rendering Issue of Pyramid Across Screens | `#699f2d0cad6f4b026ec1` |

### Presentations & CMS
| Page | Hash ID |
|------|---------|
| Creating Basic Presentations with LG | `#666aac04696dea20624d` |
| Creating Basic Presentations (duplicate) | `#666aac4d61cc782526bc` |
| LG Content Management System (CMS) | `#666b1108b746b05bdfcc` |
| Tour of Cities Function (Flutter) | `#6669a3b017dc12cf8788` |

### Chromium & Web
| Page | Hash ID |
|------|---------|
| Chromium on LG | `#65f80b09afc0d4373cfd` |
| Opening/Closing Chromium Sessions | `#66608d2167d056f725b0` |
| Installing Npm Apps on LG | `#6661681214a8e72b466c` |
| Fetching/Displaying API Data (JS) | `#677bc50c8ffb527b1014` |
| Configure Flask Server for LG Nodes | `#67882b387205d2959dad` |
| Non-Google Earth/Chromium Apps Setup | `#66681ef96f476c55a938` |
| LG Web App Quick Start | `#666824819c17ef32a8ae` |
| Vote Commands in LG Web App | `#67c68af1b4fb65b706c2` |
| Gemini AI in Web App | `#67f95cb749780f2ffd19` |
| Integrating LG Server into Web App | `#67f961190e9d1513267f` |
| CSS Animations | `#67f96274b7fe44debb44` |

### Virtual Setup & Troubleshooting
| Page | Hash ID |
|------|---------|
| Liquid Galaxy Virtual Setup Problems & Solutions | `#65f875ae948b736b3f02` |
| Common Errors While Setting Up Rig | `#66632aeaaae7c0bc2355` |
| Error in Install Rig | `#6666bbfd7b18723d7968` |
| Key Points for LG Install (Common Errors) | `#66670ec104993aed1e76` |
| Host Key Verification Failed | `#6662ba3c8d4ebcc6b673` |
| Setup of LG in a VM | `#666b083e67426ca872a4` |
| VM Setup (duplicate) | `#666b0c59389bed787193` |
| LG Setup with Flutter App (SSH + KML) | `#666b0979edc8e604a3f6` |
| Troubleshooting Multi-Node Connectivity | `#67c0942a7cf330b7a560` |
| VirtualBox Host-Only Adapter Fix | `#67d85086e54b2f1d7c7a` |
| Emulator Offline Error Fix | `#69a426c3c2adb8321a3c` |
| Ubuntu 16.04 Freezes on Shutdown | `#69a429926deb21350b44` |
| VirtualBox + Windows Hypervisor Conflict | `#69a42ae543460b96d43f` |
| LG Rig Not Connecting to App | `#699f2e0b787dd91c2d63` |
| Port Forwarding Troubleshooting | `#67c6ed37d4c30136e260` |

### Server & Docker
| Page | Hash ID |
|------|---------|
| Server Installation | `#6666d306bb99512564bb` |
| Docker Installation | `#6666dc9eca7bab920790` |
| Docker Installation (duplicate) | `#6666f6640de2bceb3026` |
| Docker Compose Setup | `#6666fc0676a9d8acd973` |
| Test Setup | `#666702a6984438f7ede4` |
| How to Create Your Own Dockerfile | `#67c35d38a117592e6f77` |

### Sending Images
| Page | Hash ID |
|------|---------|
| Sending Images About Real LG Machine | `#66671f389a67ac93c23e` |

### OSC & Networking
| Page | Hash ID |
|------|---------|
| Open Sound Control (OSC) | `#6668617045d704129d63` |
| Introduction to Networks | `#6662cb0e4622b8241db8` |
| NAT Network | `#6660826c186e05eed61b` |
| Virtual Network Modes for LG | `#67c3581042f8212cf677` |
| Understanding Protocols Used by LG | `#69c54c07b4423e6f58f5` |

### LG Internals & Maintenance
| Page | Hash ID |
|------|---------|
| LG Boot Process | `#69a4973d4992a1556726` |
| File Permissions and Ownership | `#69a4985d68d8102011e9` |
| Environment Variables in LG | `#69a49a436d7036c8d2cc` |
| Folder Structure in LG Setup | `#69a48930af556f73d435` |
| Linux Commands Introduction | `#6662d91126cbec211a1f` |
| Linux Resource Usage in LG | `#69bd4f04bb57fd99a915` |
| Understanding LG Maintenance Commands | `#69a48d8ecb47ec41ff14` |
| SFTP Permission Denied Fix | `#69af332cb3cc50c1fc73` |
| Dynamic SSH Ports in Flutter | `#69b14e1a1bfe94b02571` |
| Running/Testing Flutter App Locally | `#69a48b62811b95e41a32` |
| Master Responsibilities | `#69c54adeed54770b99f9` |
| Google Earth Features and Integration | `#69c54b2c86231817b487` |
| Creating Strong Demo Videos | `#69c54b7bcd932eb71aee` |
| Maps API Key (No Billing) | `#66684b9344d38da2f924` |
| Credentials to Connect to LG Rigs | `#66685008a9ec3039d25d` |
| GSoC Task Naming Conventions | `#69c3f27834bdabc4a1d8` |

### 3D, AR/VR, Special Content
| Page | Hash ID |
|------|---------|
| Converting Blender 3D Model to KMZ | `#67c024077f3e92dca5f1` |
| Understanding Celestial Coordinates | `#67c0c28620bee68e9f00` |
| Constellation Visualizations (Sky View) | `#67c6f9c2c1da92a802f0` |
| Robotic Arm Gesture Control for LG | `#67ddb104c26aba2ce10f` |
| Integrating Google ARCore with LG | `#67ae2da659363a399600` |

### Flutter App Development (LG-specific)
| Page | Hash ID |
|------|---------|
| LG App Developer Quick Start | `#66682833e3afa7934c2b` |
| Flutter vs Web Stack for LG | `#67ab22e9689bbf2601f1` |
| Android Studio Emulator Optimization | `#67a218e062fbe144436c` |
| Automated Testing for LG Apps | `#67ab1ea8ac4a433967a4` |
| Free Multi-Language Support | `#67ae2aa86edeab2dfefb` |
| QR Code Scanner in Flutter | `#67c026310c938f03e9aa` |
| Animated Icons with Rive | `#67c0681e74bd9162277f` |
| Rebuilding APKs from Older Flutter | `#67c3609d65ae83cb5a60` |
| Tab Bar for LG Apps | `#67d857cda6b39d441cd5` |
| Hero Animations in Flutter | `#67d87548e8384f23ff14` |
| Accessibility (Semantics) in Flutter | `#67d87f6270ca5875dddd` |
| Google APIs in Flutter Apps | `#67d882cd2739ed1cadd3` |
| TTS Integration in Flutter | `#67dc96b5e5b54e77ea7d` |
| Migration: pub.dev SSH to dartssh2 v3 | `#66670c47f309e962455f` |
| How AI Translates Speech into KML | `#698dbda11f63f491b826` |
| Riverpod AsyncValue (Connection Screen) | `#666b018aee3077d780c8` |
| Cold Boot vs Warm Boot (Emulator) | `#69b993ca6927d8b22009` |
| Bugs on Real Devices vs Emulator | `#69bd50c3b18a62a5ca20` |
| Writing Effective Prompts for APIs | `#67c6e04db164af5c9b7c` |

### Flutter Development (General)
| Page | Hash ID |
|------|---------|
| State Management (GetX) | `#666062ee60fa80fc7afe` |
| Glassmorphic/Neumorphic UI | `#66606b5599f1f246edda` |
| ML Models in Flutter | `#6660747650ed885be600` |
| AI Models in Flutter Apps | `#66631d9739379fb224b1` |
| Neumorphism in Flutter | `#66631efae785d7940beb` |
| Glassmorphism in Flutter | `#666321fedce64678ebf8` |
| Widget Tree | `#6662bfcd848ed8bc9e7f` |
| Lottie/Hero Animations | `#6662c46727b31d61d951` |
| Flask Backend for ML Features | `#66699d50c14ea8c1e05a` |
| Google Maps Package for Flutter | `#6669a7cda8278895837d` |
| CSV Data in Smart City Dashboard | `#6669a94335bf25d5204d` |
| SetRefresh Function (Flutter) | `#666ac54c126525cbae92` |
| CSV Database in Flutter | `#666aca70935cdfd78d9f` |
| Speech Recognition in Flutter | `#666acbc9ec7a7e87b711` |
| Bluetooth in Flutter | `#666ace79c53b141044b5` |
| Dio vs Http (Networking) | `#666aee5390430d290872` |
| Bloc vs GetX (State Management) | `#666af318d514f93004ec` |
| TFLite for AI Model Integration | `#666af78c829b10991e79` |
| Hive Local Database | `#66686366e290e9b41c03` |
| SQFlite Database (Create/Init) | `#666b1539cf85c2292b4c` |
| SQFlite Tables (Create/Modify) | `#666b17dd6bf599d129f7` |
| API Connection in Flutter App | `#666bec84ea2a7a910e00` |
| Speech to Text in Flutter | `#666866ded0d780ad9f0f` |
| UML | `#666955fcb7c6c873061f` |
| WorkLogs | `#666956c1a8467cf6f04b` |
| Software Process | `#666961cd8756bddb2b70` |
| Agile Software Development | `#666974363f98db8527c8` |

### Community & Misc
| Page | Hash ID |
|------|---------|
| Questions & Answers from Discord | `#65f807b5582647a9ff9d` |
| How to Start in the Community | `#6662c86ed289defc03cb` |
| How to Contribute to LG Wiki | `#6666b2242c099ca9f7af` |
| Acknowledgement | `#66686ac7944a361e8857` |

## Verification

Deploy a simple point placemark KML to master.kml and check it appears on the master screen within 3-5 seconds after the 3s NetworkLink refresh cycle.

## References

- `references/lg-wiki-reference/lg-repo-patterns.md` — Code patterns from La Palma Volcano Tracking Tool and LG Master Web App repos (orbit, flytoview, SSH, KML upload, forceRefresh)
- `references/lg-wiki-reference/wiki-search-navigation.md` — How to navigate the wiki SPA: search-based navigation (reliable), direct URL limitations, fallback JS extraction
- `references/lg-wiki-reference/balloon-deployment-attempt.md` — RESOLVED record of the July 2026 balloon deployment: CDATA fails on VM, escaped HTML works, rightmost = slave_2.kml on 3-screen rig
