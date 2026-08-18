# DEMO-local-ai-with-gemma-by-google — Ubuntu App

Desktop controller for a Liquid Galaxy rig. Drives pre-baked KML
visualizations (17 use-case skills × 36 visualizations) on the multi-screen
Google Earth cluster over SSH.

**v3.0** — app by Nara (Hermes Agent). Features: 360° camera orbit, logo
overlay (554×500 on leftmost screen), right-screen info panels, clear-earth
(preserves logo), relaunch/reboot.

Same protocol + assets as the Android companion app (shared `assets/`).

## Quick start (Ubuntu 26.04 / any modern Ubuntu)

```
./run.sh
```

`run.sh` creates a `.venv` on first run, installs the two dependencies
(PySide6 + paramiko), and launches the app.

Manual alternative:
```
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python main.py
```

## Configure

Open Settings (⚙ button, top-right) and enter:
- Master IP address  (e.g. 192.168.1.18)
- SSH username      (default `lg`)
- SSH password      (default `lg`)
- SSH port          (default `22`)
- Number of screens (used to place panels/logo; default `3`)

Use "Test connection" to verify, then deploy visualizations from the skill
grid. "Clear Earth" resets the rig. Advanced actions (logo / relaunch /
reboot) are in the Settings dialog.

## Requirements

- Python 3.10+ and `python3-venv`
- Network reachability to the rig's master node

## Files

```
main.py           entry point
run.sh            launcher (venv + deps + run)
requirements.txt  PySide6, paramiko
README.md         this file
assets/           skills.json + kml/ (pre-baked KML + glass panels)
app/              application source
```
