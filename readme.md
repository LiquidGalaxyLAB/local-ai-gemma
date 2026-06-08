# Local AI with Gemma by Google

<p align="center">
  <img src="https://summerofcode.withgoogle.com/assets/media/gsoc-generic-badge.svg" alt="GSoC 2026" height="30"/>
  &nbsp;
  <img src="https://img.shields.io/badge/Organization-Liquid%20Galaxy-blue" alt="Liquid Galaxy"/>
  &nbsp;
  <img src="https://img.shields.io/badge/Hardware-Raspberry%20Pi%205-red" alt="Raspberry Pi 5"/>
  &nbsp;
  <img src="https://img.shields.io/badge/Agent-Nara%20%7C%20Hermes-purple" alt="Nara Agent"/>
  &nbsp;
  <img src="https://img.shields.io/badge/Status-In%20Development-yellow" alt="Status"/>
</p>

> **A GSoC 2026 Project** · Liquid Galaxy · Mentors: Andreu Ibanez, Moisés Martínez · Mentee: Harsh Mehta

---

## Table of Contents

- [About the Project](#about-the-project)
- [Meet Nara](#meet-nara)
- [Features](#features)
- [System Architecture](#system-architecture)
- [Tech Stack](#tech-stack)
- [Hardware](#hardware)
- [Hardware Setup](#hardware-setup)
  - [Step 1 — Attach NVMe SSD via M.2 HAT](#step-1--attach-nvme-ssd-via-m2-hat)
  - [Step 2 — Flash Raspberry Pi OS to SD Card](#step-2--flash-raspberry-pi-os-to-sd-card)
  - [Step 3 — First Boot from SD Card](#step-3--first-boot-from-sd-card)
  - [Step 4 — Flash OS to NVMe SSD](#step-4--flash-os-to-nvme-ssd)
  - [Step 5 — Configure NVMe Boot Order](#step-5--configure-nvme-boot-order)
  - [Step 6 — Boot from NVMe](#step-6--boot-from-nvme)
- [Hermes Setup](#hermes-setup)
- [Skill System](#skill-system)
- [Contributing](#contributing)
- [Acknowledgements](#acknowledgements)
- [License](#license)

---

## About the Project

This project builds **Nara** — an AI assistant server that lives on the Liquid Galaxy rig's local network. Nara runs on a Raspberry Pi 5 connected to the rig via SSH, accepts commands through Telegram or voice, and autonomously generates and pushes content — KML visualizations, guided tours, real-time data maps, and more — directly to the Liquid Galaxy screens.

The system is built as a **Hermes agent** with a modular skill architecture, meaning capabilities can be added, enabled, or disabled independently without touching the core runtime. It supports both fully local AI inference (offline, self-contained) and a hybrid mode that optionally routes complex tasks to remote model APIs — balancing hardware limits with response quality.

The goal is a stable, easy-to-extend assistant that any LG user, mentor, or contributor can run in the lab or deploy from a backup profile.

---

## Meet Nara

**Nara** is the agent profile built on the [Hermes](https://github.com/hrsh7th/hermes) agent framework, tailored specifically for the Liquid Galaxy ecosystem. It has a defined personality, a curated skill set, and a strict honesty contract — she will never hallucinate data or push unverified content to the screens.

Nara's profile is portable. It can be exported as a backup and restored on any compatible Hermes + Raspberry Pi 5 setup, making it easy to share across LG labs and deployments worldwide.
<!-- 
**What Nara can do out of the box:**
- Control the Liquid Galaxy rig (reboot, relaunch, shutdown, clean KML)
- Generate KML visualizations from natural language prompts
- Answer questions about LG using a built-in RAG knowledge assistant
- Visualize real-time data from open sources (aircraft, satellites, weather, sea traffic)
- Tell geospatial stories and run guided tours
- Respond by voice or Telegram
- Run system health diagnostics and suggest fixes
- Assist contributors with onboarding and task management

---

## Features

### Core
- **Agentic AI Runtime** — Hermes-based multi-agent orchestration on a local SBC
- **Skill Manager** — Add, enable, disable, and update skills independently
- **Telegram Bot** — Private-mode bot for remote command and media control
- **Voice Interface** — Full speech-to-text input and text-to-speech response pipeline
- **Model Layer** — Local inference via Ollama + optional remote API fallback via Model Router

### Content & Visualization
- **KML Generator** — AI-generated KML from natural language: history, science, news, sports, nature
- **Real-Time Data** — Live feeds from OpenSky (aircraft), Celestrak (satellites), weather & disaster APIs
- **Storytelling & Tours** — Narrative KML sequences for historical and educational content
- **News & Geopolitical Maps** — Visualize current events geographically on the rig
- **Weather Dashboard** — Temperature, AQI, forecast overlays via open weather APIs

### Operations
- **LG Health Monitor** — Automated checks on LAN, CPU, Google Earth, NetworkLinks
- **LG Wiki Knowledge Base** — Scraped, chunked, and vector-indexed LG Wiki for fast Q&A
- **Contributor Assistant** — Curated task generation, submission validation, and mentor notifications
- **Personality Layer** — Configurable agent tone and response style

---

## System Architecture

```
USER (Voice / Telegram)
        │
        ▼
┌─────────────────────────────────────────────┐
│         NARA — Hermes Agent Runtime         │
│  ┌────────────┐  ┌──────────────────────┐   │
│  │ Main Agent │→ │    Skill Manager     │   │
│  └────────────┘  │  KMLGenerator        │   │
│                  │  LGController        │   │
│                  │  KnowledgeSkill      │   │
│                  │  TTS / Voice         │   │
│                  │  ModifySkill         │   │
│                  └──────────────────────┘   │
│  ┌─────────────────────────────────────┐    │
│  │           Model Router              │    │
│  │  Local (Ollama) ↔ Remote Model APIs │    │
│  └─────────────────────────────────────┘    │
│  ┌─────────────────────────────────────┐    │
│  │  Storage: Metadata DB, File Store,  │    │
│  │  Vector DB, Markdown Workflows      │    │
│  └─────────────────────────────────────┘    │
└────────────────────┬────────────────────────┘
                     │ SSH
                     ▼
           ┌──────────────────┐
           │  Liquid Galaxy   │
           │       Rig        │
           │  lg1 ... lgN     │
           └──────────────────┘
```

---

## Tech Stack

| Layer | Technologies |
|---|---|
| Agent Runtime | Hermes, Multi-agent orchestration |
| AI / Models | Ollama (local inference), Remote model APIs |
| Knowledge | RAG, Vector Database, LG Wiki scrape |
| Visualization | KML, Google Earth, Liquid Galaxy |
| Communication | Telegram Bot API, WebSockets, REST |
| Voice | Speech-to-Text, Text-to-Speech pipelines |
| Data Sources | OpenSky Network, Celestrak, RSS Feeds, Weather APIs |
| Hardware Interface | SSH, sshpass, Shell scripting |
| Storage | Metadata DB, File Store, NVMe SSD |
| Languages | Python, Shell |

---
-->
## Hardware

| Component | Specification |
|---|---|
| SBC | Raspberry Pi 5 — 8GB RAM |
| Storage | 512GB NVMe SSD |
| NVMe Interface | Raspberry Pi M.2 HAT+ |
| Boot Media | 16GB+ microSD card (for initial setup only) |
| Power | Raspberry Pi 27W USB-C Power Supply |


> The Raspberry Pi 5 runs as the **Nara Agent Server**, connected to the Liquid Galaxy rig over the local LAN via SSH.

![Hardware setup](/assets/img1.png)
---

## Hardware Setup

### Step 1 — Attach NVMe SSD via M.2 HAT

1. Power off and unplug the Raspberry Pi 5.
2. Attach the **Raspberry Pi M.2 HAT+** to the RPi 5 using the PCIe FPC ribbon cable — connect it to the **PCIe FPC connector** on the bottom edge of the RPi 5 board. Secure the HAT with the provided standoffs.
3. Insert the **512GB NVMe SSD** (M.2 2280 or 2242, M-key) into the M.2 slot on the HAT. Secure it with the retention screw.
4. Confirm the HAT sits flat and all connectors are fully seated before proceeding.

> ⚠️ Handle the PCIe ribbon cable with care — it is fragile. Ensure the blue side faces up when inserting into the RPi 5 connector.

---

### Step 2 — Flash Raspberry Pi OS to SD Card

1. On your computer, download and install **[Raspberry Pi Imager](https://www.raspberrypi.com/software/)**.
2. Insert your **16GB+ microSD card** into your computer.
3. Open RPi Imager and configure:
   - **Device:** Raspberry Pi 5
   - **OS:** Raspberry Pi OS (64-bit) — recommended: the full Desktop version for initial setup
   - **Storage:** Select your microSD card
4. Click the **Edit Settings (⚙️)** button before writing:
   - Set hostname (e.g. `nara.local`)
   - Enable SSH → Use password authentication
   - Set username and password (e.g. user: `pi`, password: your choice)
   - Configure Wi-Fi if needed
5. Click **Save → Yes → Write** and wait for the flash to complete.

---

### Step 3 — First Boot from SD Card

1. Insert the flashed microSD card into the Raspberry Pi 5.
2. Connect a monitor, keyboard, and mouse (or use SSH after boot).
3. Connect power — the RPi 5 will boot from the SD card.
4. Complete the initial OS setup if the desktop wizard appears.
5. Open a terminal and run a system update:

```bash
sudo apt update && sudo apt full-upgrade -y
sudo reboot
```

6. After reboot, verify the NVMe is detected:

```bash
lsblk
# You should see: nvme0n1 with no partitions yet
```

If `nvme0n1` does not appear, check the M.2 HAT ribbon cable connection and reboot.

---

### Step 4 — Flash OS to NVMe SSD

With the RPi running from SD, use **RPi Imager** (already installed on Raspberry Pi OS) to write the OS directly to the NVMe:

1. Open **Raspberry Pi Imager** from the desktop (or run `rpi-imager`).
2. Configure the same settings as Step 2 (or reuse your saved customizations).
3. **Storage:** Select the NVMe drive (`/dev/nvme0n1` — typically listed as the 512GB drive).
4. Click **Write** and wait for the process to complete.



---

### Step 5 — Configure NVMe Boot Order

Tell the Raspberry Pi 5 bootloader to prefer the NVMe SSD over the SD card.

**Option A — via raspi-config (recommended):**

```bash
sudo raspi-config
```

Navigate to: `Advanced Options` → `Boot Order` → `NVMe/USB Boot`

Select **NVMe**, confirm, and exit. Apply when prompted.

**Option B — via EEPROM config (manual):**

```bash
# Open the EEPROM config editor
sudo -E rpi-eeprom-config --edit
```

Find the `BOOT_ORDER` line and set it to:

```
BOOT_ORDER=0xf61
```

> Boot order is read right-to-left: `6` = NVMe (PCIe), `1` = SD card, `f` = loop/restart.  
> This means: try NVMe first → fall back to SD → repeat.

Save, exit, and apply:

```bash
sudo reboot
```

---

### Step 6 — Boot from NVMe

1. After the reboot, **power off** the Raspberry Pi 5:

```bash
sudo poweroff
```

2. **Remove the microSD card.**
3. Power the RPi 5 back on.
4. The system should now boot directly from the NVMe SSD.
5. Verify with:

```bash
findmnt / 
# Should show: /dev/nvme0n1p2 or similar — not mmcblk0
```

If the RPi fails to boot without the SD card, revisit Step 5 and confirm the EEPROM boot order was saved correctly.

---
<!--
## Hermes Setup

>  **Coming soon.** This section will cover installing the Hermes agent runtime, loading the Nara profile, configuring skills, and connecting to the Liquid Galaxy rig.

Steps will include:
- [ ] Installing Hermes on Raspberry Pi OS
- [ ] Loading the Nara agent profile from backup
- [ ] Configuring `config.yaml` (LG IP, SSH credentials, screen count)
- [ ] Setting up the Telegram bot (private mode)
- [ ] Configuring the Voice HAT and audio pipeline
- [ ] Running Ollama and loading local models
- [ ] Verifying LG SSH connection and running the first command
- [ ] Enabling and testing skills

---

## Skill System

Skills are modular capability units loaded by Nara's skill manager. Each skill is a self-contained `.md` file following the Hermes `SKILL.md` format.

| Skill | Description |
|---|---|
| `lg-ssh-control` | Relaunch, reboot, poweroff, network info, KML refresh |
| `lg-kml-generator` | Generate and push KML from natural language *(coming soon)* |
| `lg-knowledge` | LG Wiki RAG Q&A *(coming soon)* |
| `lg-diagnostics` | Health checks and recovery *(coming soon)* |
| `lg-storytelling` | Narrative KML tours *(coming soon)* |
| `lg-realtime-data` | Live feeds from OpenSky, Celestrak, weather *(coming soon)* |
| `lg-contributor` | Onboarding assistant for GSoC contributors *(coming soon)* |

---
-->
## Contributing

This is a GSoC 2026 project. Contributions, feedback, and testing are welcome.
---

## License

MIT License — see [LICENSE](LICENSE) for details.

---
