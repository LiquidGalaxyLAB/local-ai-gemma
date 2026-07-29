# Local AI with Gemma by Google (Nara)

<div align="center">
  <img src="./assets/img2.png" alt="Liquid Galaxy logo" width="280" />
  <br />
  <strong>350 Hr — Local AI with Gemma by Google</strong>
  <br />
  <em>GSoC 2026 · Liquid Galaxy Lab</em>
</div>

---

**Nara** is the onboard AI assistant for Liquid Galaxy. Built on the [Hermes Agent](https://hermes-agent.nousresearch.com/docs/) framework, it runs on a local machine (Raspberry Pi recommended), controls the LG rig over SSH, and generates KML visualizations, guided tours, and live data layers — fully local or hybrid cloud inference.

| | |
| :--- | :--- |
| **Project** | Nara — onboard AI for Liquid Galaxy |
| **Framework** | [Hermes Agent](https://hermes-agent.nousresearch.com/) (Nous Research) |
| **Contributors** | Harsh Mehta (mentee) |
| **Mentors** | Andreu Ibanez, Moises Martinez |
| **Backup / profiles** | [Google Drive folder](https://drive.google.com/drive/folders/1mQyJYMV7bvj-cq7geYF7AcXGROvqjj-z) |

---

## Table of Contents

1. [About Me & Acknowledgements](#about-me--acknowledgements)
2. [About the Project](#about-the-project)
3. [Planned Tasks](#planned-tasks)
4. [What Nara Can Do](#what-nara-can-do)
5. [Use Cases (Current Skills)](#use-cases-current-skills)
6. [Quick Start](#quick-start)
7. [Installation](#installation)
8. [Restoring the Liquid Galaxy Profile](#restoring-the-liquid-galaxy-profile)
9. [Docker & WSL Setup](#docker--wsl-setup)
10. [Hermes Agent Architecture](#hermes-agent-architecture)
11. [LLM Wiki & Google OKF](#llm-wiki--google-okf)
12. [System Architecture](#system-architecture)
13. [Tech Stack](#tech-stack)
14. [Hardware](#hardware)
15. [Example Usage](#example-usage)
16. [Voice Support](#voice-support)
17. [Current Status](#current-status)
18. [References](#references)

---

## About Me & Acknowledgements

I'm **Harsh Mehta**, an engineering student from Pune with a keen interest in how real-world production systems work. Grateful to Liquid Galaxy and Google Summer of Code for this opportunity to ship work that others can actually use in the lab.

Many thanks to **Trang, Fabricio, Oriol, and Josep** at the Liquid Galaxy Lab in Lleida for testing and sharing valuable feedback on the project.

---

## About the Project

Nara lives on the Liquid Galaxy rig's local network. It runs on a Raspberry Pi 5 connected to the rig via SSH, accepts commands through the CLI (and optionally messaging gateways), and autonomously generates and pushes content — KML visualizations, guided tours, real-time data maps, and more — directly to the Liquid Galaxy screens.

The system is a Hermes agent with a **modular skill architecture**: capabilities can be added, enabled, or disabled independently without touching the core runtime. It supports both fully local AI inference (offline, self-contained) and a hybrid mode that optionally routes complex tasks to remote model APIs.

The goal is a stable, easy-to-extend assistant that any LG user, mentor, or contributor can run in the lab or deploy from a backup profile.

---

## Planned Tasks

| # | Task | Result |
| :-: | :--- | :--- |
| 1 | Work on docs | ✅ Done |
| 2 | Test Docker and WSL-based setups | ✅ WSL and Docker tested |
| 3 | Verify architecture & advanced use cases | Architecture validated; virtual LG use case added; ≥2 data sources |
| 4 | Build virtual LG (VM-based) | Docs and scripts added to the repo |
| 5 | Presentation (PPT) — 13 Aug | 🔄 In progress |
| 6 | Update docs (27 Jul) | ✅ Done |

---

## What Nara Can Do

- Control the Liquid Galaxy rig over SSH (relaunch, reboot, shutdown, clear KMLs)
- Generate and deploy KMLs for placemarks, overlays, tours, and camera paths
- Visualize live or historic data layers (weather, aviation, disasters, maritime, energy)
- Provide educator-focused flows (geography, history) with narrated tours
- Backup & restore a complete Hermes profile for quick deployment

### Planned use-case roadmap

- **LG command execution** — SSH control (relaunch, reboot, poweroff)
- **Weather monitoring** — live weather → KML
- **News & geopolitical visualization** — live event mapping
- **Geography / history educator** — concepts and historical events with KML + TTS
- **Natural disaster command center** — earthquakes, wildfires, weather alerts
- **Maritime domain awareness** — AIS, trade routes, chokepoints
- **Energy & infrastructure** — pipelines, renewables, mining
- **Live aviation watch** — flights, airports, NOTAMs
- **Cyber / undersea infrastructure** — cables, outages, GPS jamming
- **Supply chain & trade flows** — commodity ports, tanker positions
- **Economic markets** — Finnhub, FRED indicators
- **Armed conflicts** — ACLED, UCDP mapping

---

## Use Cases (Current Skills)

| Skill | Example input | Expected output | Skill doc |
| :--- | :--- | :--- | :--- |
| **lg-ssh-control** | "Connect to LG", "Relaunch Earth" | SSH control commands (relaunch / reboot / clear KMLs) | [lg-ssh-control.md](https://github.com/LiquidGalaxyLAB/local-ai-gemma/blob/main/skills/lg-ssh-control.md) |
| **lg-use-cases** | "What can you do?", "Show me use cases" | Lists available skills and guided help | [lg-use-cases.md](https://github.com/LiquidGalaxyLAB/local-ai-gemma/blob/main/skills/lg-use-cases.md) |
| **geography-educator** | "Teach me about the Date Line" | Educational KMLs + optional TTS narration | [geography-educator.md](https://github.com/LiquidGalaxyLAB/local-ai-gemma/blob/main/skills/geography-educator.md) |
| **armed-conflicts** | "Show global conflicts" | Dynamic conflict-zone KMLs, camera tour, TTS | [armed-conflicts.md](https://github.com/LiquidGalaxyLAB/local-ai-gemma/blob/main/skills/armed-conflicts.md) |
| **weather-monitor** | "What's the weather in Pune?" | 3D columns, icons, panel + voice on LG | [weather-monitor.md](https://github.com/LiquidGalaxyLAB/local-ai-gemma/blob/main/skills/weather-monitor.md) |
| **natural-disaster** | "Show earthquakes in Japan" | Multi-API KML, auto-fly + TTS summary | [natural-disaster.md](https://github.com/LiquidGalaxyLAB/local-ai-gemma/blob/main/skills/natural-disaster.md) |
| **live-aviation** | "Show flights over Germany" | Aircraft positions from OpenSky on LG | [live-aviation.md](https://github.com/LiquidGalaxyLAB/local-ai-gemma/blob/main/skills/live-aviation.md) |
| **lg-installation-setup** | "Set up a virtual Liquid Galaxy" | Step-by-step VM-based LG rig setup | [lg-installation-setup.md](https://github.com/LiquidGalaxyLAB/local-ai-gemma/blob/main/skills/lg-installation-setup.md) |

### Virtual Liquid Galaxy skill

A dedicated skill walks users through building a **virtual LG** on their own machine:

| Section | What it covers |
| :--- | :--- |
| What is LG? | 3 computers (lg1 master + lg2/lg3 slaves) with multi-screen Google Earth |
| How it works | Master serves KML via Apache → slaves refresh every ~3s → ViewSync syncs cameras |
| Setup steps | Create VMs → run install script → configure master → connect slaves → connect Hermes |

Full skill: [lg-installation-setup.md](https://github.com/LiquidGalaxyLAB/local-ai-gemma/blob/main/skills/lg-installation-setup.md)

---

## Quick Start

1. Install Hermes Agent ([Installation](#installation)).
2. Ensure SSH connectivity between the Pi (or host) and the Liquid Galaxy master node.
3. Import or restore the `liquid-galaxy-agent` Hermes profile ([backup folder](https://drive.google.com/drive/folders/1mQyJYMV7bvj-cq7geYF7AcXGROvqjj-z)).
4. Enable skills (`lg-ssh-control`, `kml-generator`, `weather-monitor`, etc.) and configure API keys with `hermes model`.

---

## Installation

### Terms you'll see

| Term | Meaning |
| :--- | :--- |
| **Terminal** | Text window where you type commands |
| **Shell** | Program that reads commands (`bash`, `zsh`, PowerShell) |
| **Archive** | `.zip` / `.tar.gz` packing many files into one |
| **`~`** | Shortcut for your home folder (e.g. `/home/pi`) |

### Download the backup first

Download the latest backup from the shared Drive folder:

**[Backup download (Google Drive)](https://drive.google.com/drive/folders/1mQyJYMV7bvj-cq7geYF7AcXGROvqjj-z)**

Folders are dated — pick the **latest date** and use the Hermes / profile backup inside.

### Prerequisites (Raspberry Pi / Linux)

```bash
git --version
```

If Git is missing:

```bash
sudo apt update
sudo apt install -y git curl xz-utils
```

You do **not** need to manually install Python, Node.js, ripgrep, or ffmpeg — the Hermes installer handles those.

### Option A — Command-line install (recommended for Raspberry Pi)

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
```

### Option B — Desktop app (macOS / Windows)

Download the [Hermes Desktop installer](https://hermes-agent.nousresearch.com/) from the website.

**PowerShell (Windows):**

```powershell
iex (irm https://hermes-agent.nousresearch.com/install.ps1)
```

Setup walkthrough video: [YouTube](https://youtu.be/r77kEcoE7Sw?si=a9vfaL3OiTqQK0gE)

### After install

Reload your shell, then test:

```bash
source ~/.bashrc   # or source ~/.zshrc
hermes
```

If a chat prompt opens, install succeeded. Type `exit` or press `Ctrl+C` to leave. By default, Hermes stores data under `~/.hermes/`.

---

## Restoring the Liquid Galaxy Profile

Two safe approaches — pick based on whether this machine already has Hermes work you care about.

| Your situation | Use |
| :--- | :--- |
| Brand-new Hermes install, nothing to lose | **Approach 1 — Full restore** |
| Existing chats/config/skills you want to keep | **Approach 2 — Profile import** (recommended) |

### Approach 1 — Full backup restore (overwrites `~/.hermes`)

Use only on a **fresh** install.

1. Download the `.zip` from the [Drive folder](https://drive.google.com/drive/folders/1mQyJYMV7bvj-cq7geYF7AcXGROvqjj-z) (e.g. `hermes-backup-YYYY-MM-DD-HHMMSS.zip`).
2. Restore:

```bash
hermes import /path/to/hermes-backup-YYYY-MM-DD-HHMMSS.zip
```

3. Configure model and tools:

```bash
hermes model
hermes tools
hermes doctor
```

### Approach 2 — Profile import (preserves existing data)

Safer option: adds `liquid-galaxy-agent` **alongside** other profiles.

1. Download `liquid-galaxy-agent.tar.gz` from the [Drive folder](https://drive.google.com/drive/folders/1mQyJYMV7bvj-cq7geYF7AcXGROvqjj-z).
2. Import and switch:

```bash
hermes profile import /path/to/liquid-galaxy-agent.tar.gz --name liquid-galaxy-agent
hermes profile use liquid-galaxy-agent
hermes model
hermes tools
hermes doctor
```

3. Start chatting:

```bash
hermes
# or one-shot:
hermes --profile liquid-galaxy-agent
```

4. Switch profiles later:

```bash
hermes profile list
hermes profile use liquid-galaxy-agent
hermes profile use default
```

### Quick comparison

| | Approach 1 (Full restore) | Approach 2 (Profile import) |
| :--- | :--- | :--- |
| Overwrites your data? | Yes — entire `~/.hermes/` | No — adds a profile |
| Best for | Fresh install | Existing Hermes users |
| Command | `hermes import backup.zip` | `hermes profile import file.tar.gz` |
| Profiles available | Only this one | Yours + this one |

### Troubleshooting

| Problem | Fix |
| :--- | :--- |
| `hermes: command not found` | Run `source ~/.bashrc` or open a new terminal |
| API key not set | `hermes model` or `hermes config set OPENROUTER_API_KEY your_key` |
| Something broken after restore | Run `hermes doctor` |

Official docs: [hermes-agent.nousresearch.com/docs](https://hermes-agent.nousresearch.com/docs/)

---

## Docker & WSL Setup

<div align="center">
  <img src="./assets/hermes-docker.png" alt="Hermes Agent running in Docker Desktop" width="720" />
  <br />
  <em>Hermes Agent running under Docker Desktop</em>
</div>

<br />

You can also follow the [official Docker guide](https://hermes-agent.nousresearch.com/docs/user-guide/docker).

### What is WSL2?

**Windows Subsystem for Linux (WSL2)** runs a lightweight Linux environment (e.g. Ubuntu) inside Windows 10/11 without a full traditional VM — near-native filesystem performance and good hardware integration.

### What is Docker?

**Docker** packages apps into isolated **containers** that share the host kernel. On Windows, Docker Desktop uses the **WSL2** backend for efficient Linux containers.

### Install Docker

**Windows (PowerShell as Administrator):**

```powershell
wsl --install --no-distribution
curl.exe -L -o DockerDesktop.exe "https://docker.com"
Start-Process ./DockerDesktop.exe -ArgumentList "/quiet", "/accept-license" -Wait
# Restart, then open Docker Desktop
```

**macOS:**

```bash
curl -o Docker.dmg "https://docker.com"
sudo hdiutil attach Docker.dmg
sudo cp -R /Volumes/Docker/Docker.app /Applications
sudo hdiutil detach /Volumes/Docker
open /Applications/Docker.app
```

**Linux (Ubuntu/Debian):**

```bash
curl -fsSL https://docker.com | sh
sudo usermod -aG docker $USER
newgrp docker
```

### Run Hermes in Docker

```bash
mkdir <YOUR_WORKSPACE_DIR>
cd <YOUR_WORKSPACE_DIR>

# One-time setup wizard (API keys → ~/.hermes/.env)
docker run -it --rm \
  -v ~/.hermes:/opt/data \
  nousresearch/hermes-agent setup

# Interactive chat session
docker run -it --rm \
  -v ~/.hermes:/opt/data \
  nousresearch/hermes-agent
```

### Or install Hermes natively in WSL

```powershell
wsl --install -d Ubuntu
wsl -d Ubuntu
```

Then inside Ubuntu:

```bash
curl -fsSLO https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh
# follow Hermes install steps as on Linux
```

---

## Hermes Agent Architecture

<div align="center">
  <img src="./assets/hermes-architecture.png" alt="Hermes Agent Architecture diagram" width="900" />
  <br />
  <em>Hermes Agent Architecture — credit to Alejandro (Hugging Face). <a href="https://youtu.be/n32qq7Kwzh0?si=EGcxNw3M5xKGTXeC">Video walkthrough</a></em>
</div>

<br />

Hermes is built around a single core agent process. Three **entry points** feed it:

| Entry point | Role |
| :--- | :--- |
| **CLI** | Direct local terminal use |
| **API** | Programmatic / external integration |
| **Gateway** | Long-running bridge to Telegram, Discord, Slack, WhatsApp, SMS, email, etc. |

### The agent loop

1. User sends a message  
2. Hermes builds context (memory files + history + tools/skills)  
3. Context + history go to the LLM  
4. LLM may call tools  
5. Tool results return to the LLM  
6. LLM produces a final response  
7. Hermes updates memory  

### Context & memory

Hermes keeps markdown files as a lightweight personality and knowledge base:

| File | Purpose |
| :--- | :--- |
| `soul.md` | Behavior / tone (system prompt style) |
| `user.md` | Learned facts about the user |
| `memory.md` | Durable notes on workflows and tool usage |

When a conversation grows past ~50% of the context window, older turns are compressed into a structured summary (goal, completed actions, blockers, decisions, relevant files).

Memory layers:

1. **Markdown memory files** — persistent knowledge  
2. **SQLite session history** — isolated per conversation / channel  
3. **External providers** (optional) — e.g. mem0, SuperMemory  

### Cron jobs

Scheduled tasks live in a plain `jobs.json`, are polled on an interval, and route out through the same Gateway — so a scheduled job can message you on Slack without a separate notification system.

---

## LLM Wiki & Google OKF

<div align="center">
  <img src="./assets/llw-wiki-arch.png" alt="LLM Wiki three-layer architecture" width="720" />
  <br />
  <em>LLM Wiki — three-layer architecture (raw sources → entities/concepts → compiled knowledge)</em>
</div>

<br />

Most RAG systems re-discover knowledge from scratch every query. An **[LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)** is different: the LLM incrementally builds and maintains a persistent, interlinked set of markdown files. Knowledge is **compiled once** and kept current — not re-derived on every question.

| Operation | What happens |
| :--- | :--- |
| **Ingest** | New source is read, summarized, and merged into entity/topic pages |
| **Query** | Answers are synthesized from the pre-compiled wiki |
| **Lint** | Health check: broken links, contradictions, duplicates, gaps |

In Hermes, set the wiki path via `WIKI_PATH` in `${HERMES_HOME:-~/.hermes}/.env` (defaults to `~/wiki`). Hermes includes a skill that triggers on create/ingest/query/lint style requests.

### Google Open Knowledge Format (OKF)

[OKF](https://cloud.google.com/blog/products/data-analytics/how-the-open-knowledge-format-can-improve-data-sharing) is a vendor-neutral standard for how agents package and exchange knowledge:

| Principle | Meaning |
| :--- | :--- |
| **Just markdown** | Readable in any editor, renderable on GitHub |
| **Just files** | Shippable as a tarball, hostable in git |
| **Just YAML frontmatter** | Structured fields: type, title, tags, timestamps |

Think of the LLM Wiki as the **compiler** and OKF as the **export format** — zip a bundle and hand it to any compatible agent with zero translation code.

---

## System Architecture

<div align="center">
  <img src="./assets/img3.png" alt="Hermes entry points and AIAgent core components" width="720" />
  <br />
  <em>Entry points → AIAgent core → session storage and tool backends</em>
</div>

<br />

High-level layout for this project:

| Layer | Components |
| :--- | :--- |
| **Hermes core** | CLI, API, Gateway entry points |
| **Skills** | Modular instructions + tool wrappers (SSH, KML, data fetchers) |
| **Memory** | Markdown wiki + SQLite session store |
| **Models** | Local (Ollama / LM Studio) or remote APIs |

---

## Tech Stack

| Area | Technologies |
| :--- | :--- |
| Agent runtime | Hermes, multi-agent orchestration |
| AI / models | Ollama or LM Studio (local), remote model APIs |
| Visualization | KML, Google Earth, Liquid Galaxy |
| Communication | WebSockets, REST |
| Data sources | OpenSky Network, Celestrak, RSS, weather APIs |
| Hardware interface | SSH, sshpass, shell scripting |
| Languages | Python, Shell |

---

## Hardware

<div align="center">
  <img src="./assets/img1.png" alt="Raspberry Pi 5 with M.2 HAT+ and NVMe SSD" width="520" />
  <br />
  <em>Recommended agent host: Raspberry Pi 5 with M.2 HAT+ and NVMe SSD</em>
</div>

<br />

| Component | Specification |
| :--- | :--- |
| **SBC** | Raspberry Pi 5, 8GB RAM |
| **Storage** | 256GB / 512GB NVMe SSD |
| **NVMe interface** | Raspberry Pi M.2 HAT+ (M-key) |
| **Boot media** | 16GB+ microSD (initial setup only) |
| **Power** | Raspberry Pi 27W USB-C supply |
| **Network** | Local LAN with SSH from agent → LG master |

### Hardware setup (summary)

1. **Attach NVMe** via M.2 HAT+ (power off first; handle the PCIe ribbon carefully).  
2. **Flash Raspberry Pi OS** (64-bit) to microSD with [Raspberry Pi Imager](https://www.raspberrypi.com/software/) — enable SSH, set hostname/user.  
3. **First boot** from SD → `sudo apt update && sudo apt full-upgrade -y` → verify NVMe with `lsblk`.  
4. **Write OS to NVMe** with Imager, then set boot order to **NVMe first** (`raspi-config` → Advanced → Boot Order, or `BOOT_ORDER=0xf61`).  
5. Power off, remove SD, boot from NVMe — confirm with `findmnt /`.

---

## Example Usage

Once Nara is running and connected to the rig:

| Command | What happens |
| :--- | :--- |
| Connect to the Liquid Galaxy | Verifies connection / connects to the rig |
| Relaunch Earth on the rig | Restarts Earth via helper script |
| Reboot / power off the Liquid Galaxy | Reboots or shuts down the rig |
| Clear the KMLs | Removes deployed KMLs |
| Add logo to the Liquid Galaxy | Project logo on the leftmost screen |
| Make a pyramid over Madrid / Pune | Generates & deploys a KML with fly-to |
| Highlight flood zones near Kerala | Creates and shows flood-zone KML |
| "What's the weather in Pune?" | Weather columns + icons on LG |
| "Show flights over Germany" | Live aviation layer from OpenSky |

Import / restore reminders:

```bash
hermes import ~/your-backup-name.zip
# or
hermes profile import ~/liquid-galaxy-agent.tar.gz --name liquid-galaxy-agent
```

---

## Voice Support

Hermes supports two-way voice:

| Mode | Role |
| :--- | :--- |
| **TTS** | Agent speaks responses |
| **STT** | Voice notes / mic input transcribed to text |

Easiest path: ask the agent in the CLI to enable voice mode (it can install dependencies and detect devices). Defaults need no API keys.

```text
/voice on      # full voice conversation
/voice tts     # always read responses aloud
/voice off     # disable voice features
```

The Pi needs a working mic and speaker (built-in or USB). Configure defaults via Desktop audio settings, `raspi-config`, or `alsamixer` / `aplay -l` / `arecord -l`.

### Providers (optional)

**Speech-to-Text**

| Provider | Env var | Free? |
| :--- | :--- | :---: |
| Local (Faster Whisper) | — | ✅ |
| Groq | `GROQ_API_KEY` | ✅ Free tier |
| OpenAI | `VOICE_TOOLS_OPENAI_KEY` | ❌ |
| Mistral | `MISTRAL_API_KEY` | ❌ |

**Text-to-Speech**

| Provider | Env var | Free? |
| :--- | :--- | :---: |
| Edge | — | ✅ |
| ElevenLabs | `ELEVENLABS_API_KEY` | ✅ Free tier |
| OpenAI | `VOICE_TOOLS_OPENAI_KEY` | ❌ |
| MiniMax | `MINIMAX_API_KEY` | ❌ |
| Mistral | `MISTRAL_API_KEY` | ❌ |
| NeuTTS (local) | — (`pip install neutts[all]`) | ✅ |

Edge + Faster Whisper work well as defaults. Premium voices (e.g. ElevenLabs) are optional.

---

## Current Status

| Area | Status |
| :--- | :--- |
| Documentation | High coverage (this README + extended GSoC notes) |
| Core skills | `lg-ssh-control`, KML generator, weather, geography, disasters, aviation, conflicts |
| Testing | WSL and Docker validated; virtual LG use case documented |
| Presentation | PPT in progress (13 Aug target) |

---

## References

| Resource | Link |
| :--- | :--- |
| Hermes Agent docs | https://hermes-agent.nousresearch.com/docs/ |
| Hermes website | https://hermes-agent.nousresearch.com/ |
| Project backups / profiles | https://drive.google.com/drive/folders/1mQyJYMV7bvj-cq7geYF7AcXGROvqjj-z |
| LLM Wiki (Karpathy gist) | https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f |
| Google OKF | https://cloud.google.com/blog/products/data-analytics/how-the-open-knowledge-format-can-improve-data-sharing |
| Architecture video | https://youtu.be/n32qq7Kwzh0 |
| Setup walkthrough | https://youtu.be/r77kEcoE7Sw |
| GitHub skills | https://github.com/LiquidGalaxyLAB/local-ai-gemma |

---

*Google Summer of Code 2026 · Liquid Galaxy Lab · Local AI with Gemma by Google*
