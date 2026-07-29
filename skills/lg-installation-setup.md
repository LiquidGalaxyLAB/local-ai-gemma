---
name: lg-installation-setup
description: Step-by-step guide to set up a Liquid Galaxy rig from scratch — create VMs, install Ubuntu, run the official install script, configure screens, and get Google Earth running with Hermes control.
tags: [liquid-galaxy, setup, installation, new-rig]
---

# Liquid Galaxy Setup Guide

## What It Is

A step-by-step guide to build a Liquid Galaxy rig from scratch. Turns a computer (or multiple VMs) into a multi-screen Google Earth display that you can control through Hermes.

## How It Works

A Liquid Galaxy rig has 3 computers (or VMs):
- **lg1 (master)** — center screen, runs Apache server, controls everything
- **lg2 (slave)** — left screen
- **lg3 (slave)** — right screen

They connect over a network and share the same Google Earth view using ViewSync. The master serves KML files (maps, data, markers) through Apache, and all screens refresh every 3 seconds.

## Setup Steps

### 1. Create the VMs (if using VirtualBox)
- Create 3 Ubuntu 16.04 VMs
- Network: 1 NAT + 1 Bridged adapter per VM
- Install `openssh-server`, `sshpass`, `python3`

### 2. Run the official install script
On each VM, run the LG install script. It sets up Apache, Google Earth Pro, ViewSync, and the query.txt daemon.

### 3. Configure the master (lg1)
- Apache serves KML files on port 81
- Set up auto-login for Google Earth
- Add `--no_system_check --no_signin` flags to Earth launch
- Add `QT_XCB_GL_INTEGRATION=none` to prevent crashes

### 4. Connect the slaves
- Each slave loads the same master.kml via NetworkLink
- Set refreshInterval=3 for auto-updates
- Configure ViewSync to sync camera across all screens

### 5. Connect Hermes
- Hermes on a Raspberry Pi connects to lg1 via SSH
- Deploys KMLs, controls camera, runs data pipelines
- All content updates appear within 3 seconds — no relaunch needed

## What You Can Do After Setup

| What | How |
|------|-----|
| Show live data | Run `python3 run.py --region world --layers earthquakes` |
| Fly the camera | Hermes sends flytoview commands via /tmp/query.txt |
| Update content | Deploy new KML to Apache → appears in 3s |
| Add screens | Works with 3, 5, 7+ screens (just change frame count) |

## Files

- LG official install scripts (from Liquid Galaxy GitHub)
- Hermes skills: lg-ssh-control, news-storyteller, weather-monitor, etc.
- `/home/nara/wm-collector/` — Data collection and KML generation pipeline
