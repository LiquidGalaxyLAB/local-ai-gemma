# Local AI with Gemma by Google (Nara)

<div align="center">
  <img src="./assets/img2.png" alt="Liquid Galaxy logo" width="280" />
  <br />
  <strong>350 Hr — Local AI with Gemma by Google</strong>
  <br />
  <em>GSoC 2026 · Liquid Galaxy Lab · Project Documentation</em>
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

### How to use this documentation

This documentation covers important concepts, how the project works, how a user can replicate it, GSoC progress, and key references. It is intended for contributors, mentors, and users who want to learn how the system works, deploy it on their own hardware, or build new capabilities on top of it.

The guide starts with goals and architecture, then walks through installation, configuration, and profile restoration before covering modular skills, practical use cases, and development experience. Whether you are using Nara on a Raspberry Pi with a Liquid Galaxy rig, experimenting with Hermes, or contributing new features, following the documentation in order provides the background, setup steps, and references you need.

**Want to start right away?** Jump to [Installation](#installation).

---

## Table of Contents

1. [About Me & Acknowledgements](#about-me--acknowledgements)
2. [About the Project](#about-the-project)
3. [Planned Tasks](#planned-tasks)
4. [What Nara Can Do](#what-nara-can-do)
5. [Use Cases (Current Skills)](#use-cases-current-skills)
6. [Quick Start](#quick-start)
7. [Hermes Agent Setup](#hermes-agent-setup)
8. [Installation](#installation)
9. [Restoring the Liquid Galaxy Profile](#restoring-the-liquid-galaxy-profile)
10. [Docker & WSL Setup](#docker--wsl-setup)
11. [SOUL.md (Nara personality)](#soulmd-nara-personality)
12. [Hermes Agent Architecture](#hermes-agent-architecture)
13. [LLM Wiki & Google OKF](#llm-wiki--google-okf)
14. [System Architecture](#system-architecture)
15. [Tech Stack](#tech-stack)
16. [Hardware](#hardware)
17. [Hardware Setup](#hardware-setup)
18. [Example Usage](#example-usage)
19. [Voice Support](#voice-support)
20. [GitHub Access for the Agent](#github-access-for-the-agent)
21. [Current Status](#current-status)
22. [Experiences During Development](#experiences-during-development)
23. [References](#references)

---

## About Me & Acknowledgements

I'm **Harsh Mehta**, a curious engineering student from Pune with a keen interest in how real-world production systems work. Grateful to Liquid Galaxy and Google Summer of Code for this opportunity to learn and to ship work that others can actually use in the lab.

Many thanks to **Trang, Fabricio, Oriol, and Josep** at the Liquid Galaxy Lab in Lleida for testing and sharing valuable feedback on the project.

---

## About the Project

This project builds **Nara** — an AI assistant server that lives on the Liquid Galaxy rig's local network. Nara runs on a Raspberry Pi 5 connected to the rig via SSH, accepts commands through the CLI (and optionally messaging gateways), and autonomously generates and pushes content such as KML visualizations, guided tours, real-time data maps, and more directly to the Liquid Galaxy screens.

The system is built as a Hermes agent with a **modular skill architecture**, meaning capabilities can be added, enabled, or disabled independently without touching the core runtime. It supports both fully local AI inference (offline, self-contained) and a hybrid mode that optionally routes complex tasks to remote model APIs — balancing hardware limits with response quality.

The goal is a stable, easy-to-extend assistant that any LG user, mentor, or contributor can run in the lab or deploy from a backup profile.

---

## Planned Tasks

| # | Task | Result |
| :-: | :--- | :--- |
| 1 | Work on docs | ✅ Done |
| 2 | Test Docker and WSL-based setups | ✅ WSL and Docker setup works |
| 3 | Verify architecture & advanced use cases | Architecture works well; virtual LG use case added; ≥2 data sources |
| 4 | Build virtual LG (VM-based) | Added to GitHub and docs |
| 5 | Presentation (PPT) — 13 Aug | 🔄 In progress |
| 6 | Update docs (27 Jul) | ✅ Done |

---

## What Nara Can Do

- Control the Liquid Galaxy rig over SSH (relaunch, reboot, shutdown, clear KMLs)
- Generate and deploy KMLs for placemarks, overlays, tours, and camera paths
- Visualize live or historic data layers (weather, aviation, disasters, maritime, energy)
- Provide educator-focused flows (geography, history) with narrated tours
- Backup & restore a complete Hermes profile for quick deployment

### Use cases — planned order

- **LG command execution** — SSH control (relaunch, reboot, poweroff)
- **Weather monitoring** — live weather → KML
- **News & geopolitical visualization** — live event mapping on LG
- **Geography educator** — teach concepts with real-world examples and KMLs
- **History educator** — show how historical events (e.g. wars) unfolded
- **Natural disaster command center** — earthquakes, wildfires, weather alerts, climate anomalies, displacement flows
- **Maritime domain awareness** — AIS density, trade routes, chokepoints, tankers, cable advisories
- **Energy & infrastructure** — pipelines, fuel shortages, renewables, mining
- **Live aviation watch** — military flights, delays, NOTAM rings, airport status
- **Cyber / undersea infrastructure** — undersea cables, outages, GPS jamming, cyber threats
- **Supply chain & trade flows** — commodity ports, tanker positions, chokepoints
- **Economic markets** — Finnhub and FRED (Federal Reserve Economic Data) for financial trends and indicators
- **Armed conflicts** — ACLED and UCDP for political violence and warfare mapping

---

## Use Cases (Current Skills)

| Skill | Example input | Prompt / context | Expected output | Skill doc |
| :--- | :--- | :--- | :--- | :--- |
| **lg-ssh-control** | "Connect to LG", "Relaunch Earth", "Clear the KMLs" | User command + SSH credentials + LG IP/port + frame count + skill.md | SSH control (relaunch / reboot / poweroff / clear KMLs); deploys helpers on rig | [lg-ssh-control.md](skills/lg-ssh-control.md) |
| **lg-use-cases** | "What can you do?", "Show me use cases" | User query + all developed use cases + layer stacks | Lists available skills and guided help | [lg-use-cases.md](skills/lg-use-cases.md) |
| **geography-educator** | "Teach me about the Date Line", "Show India monsoon on LG" | Topic + KML generator + region data + TTS | Educational KML (lines, 3D zones, labels) + panel + voiceover | [geography-educator.md](skills/geography-educator.md) |
| **armed-conflicts** | "Show global conflicts", "Where are active wars?" | Zone data + news + visual per zone | Dynamic KMLs (fronts, siege rings, displacement) + tour + TTS | [armed-conflicts.md](skills/armed-conflicts.md) |
| **weather-monitor** | "What's the weather in Pune?", "Show Mumbai weather" | City + lat/lon + wttr.in API | 3D temperature columns, wind arrows, icons + panel + TTS | [weather-monitor.md](skills/weather-monitor.md) |
| **natural-disaster** | "Show earthquakes in Japan", "Any wildfires?" | USGS + NASA EONET + NOAA NWS + region | Multi-API KML, auto-fly + TTS summary | [natural-disaster.md](skills/natural-disaster.md) |
| **live-aviation** | "Show flights over Germany", "Air traffic over Europe" | OpenSky API + region + airport config | Heading-rotated plane icons at altitude + airport markers + TTS | [live-aviation.md](skills/live-aviation.md) |
| **news-storyteller** | "Show world news", "What's happening globally?" | Multi-feed news + 3D KMLs + camera animation | News story layers with camera tour | [news-storyteller.md](skills/news-storyteller.md) |
| **lg-installation-setup** | "Set up a virtual Liquid Galaxy" | VM install guide skill | Step-by-step virtual LG rig setup | [lg-installation-setup.md](skills/lg-installation-setup.md) |

### Virtual Liquid Galaxy skill

A dedicated skill walks users through building a **virtual LG** on their own machine:

| Section | What it covers |
| :--- | :--- |
| What is LG? | 3 computers (lg1 master + lg2/lg3 slaves) with multi-screen Google Earth |
| How it works | Master serves KML via Apache → slaves refresh every ~3s → ViewSync syncs cameras |
| Setup steps | Create VMs → run install script → configure master → connect slaves → connect Hermes |

Full skill: [skills/lg-installation-setup.md](skills/lg-installation-setup.md)

---

## Quick Start

1. Install Hermes Agent ([Installation](#installation)).
2. Ensure SSH connectivity between the Pi (or host) and the Liquid Galaxy master node.
3. Import or restore the `liquid-galaxy-agent` Hermes profile ([backup folder](https://drive.google.com/drive/folders/1mQyJYMV7bvj-cq7geYF7AcXGROvqjj-z)).
4. Enable skills (`lg-ssh-control`, weather, geography, etc.) and configure API keys with `hermes model`.

---

## Hermes Agent Setup

The self-improving AI agent built by Nous Research. It has a built-in learning loop: it creates skills from experience, improves them during use, persists knowledge, and builds a model of who you are across sessions.

**Website:** [https://hermes-agent.nousresearch.com/](https://hermes-agent.nousresearch.com/)

### Profiles

A [profile](https://hermes-agent.nousresearch.com/docs/user-guide/profiles) is a self-contained Hermes home directory. This project starts with one profile: **`liquid-galaxy-agent`**.

Each profile gets its own `config.yaml`, `.env`, `SOUL.md`, memories, sessions, skills, cron jobs, and state database — independent directories, a clean slate.

### Backups

[Backups](https://hermes-agent.nousresearch.com/docs/getting-started/updating#full-pre-update-backup---backup) create a zip archive of config, skills, sessions, and data (everything except the codebase). Restore with [`hermes import`](https://hermes-agent.nousresearch.com/docs/reference/cli-commands#hermes-import).

| Mode | Role |
| :--- | :--- |
| **CLI session** | Interactive terminal UI — conversation loop, system prompts, model providers, tools, history |
| **Gateway message** | 20+ messaging adapters (Discord, Slack, WhatsApp, etc.) — auth, session isolation, routing |

### Skills setup

Hermes needs custom skills for LG-specific use cases. A skill = instructions + shell commands + tools. Skills and tools work together to satisfy use cases.

- [Adding Tools](https://hermes-agent.nousresearch.com/docs/developer-guide/adding-tools)
- [Creating Skills](https://hermes-agent.nousresearch.com/docs/developer-guide/creating-skills)

Skills live under the profile directory, e.g. `~/.hermes/profiles/<profile>/skills/` (each profile has its own skills tree). Project skill sources for this repo are under [`skills/`](skills/).

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

| Package | Why |
| :--- | :--- |
| **git** | Lets the installer clone the Hermes codebase |
| **curl** | Downloads installer assets |
| **xz-utils** | Unpacks Node.js `.tar.xz` archives |

You do **not** need to manually install Python, Node.js, ripgrep, or ffmpeg — the Hermes installer detects and installs those.

On non-Windows platforms, the only hard prerequisite is Git. The installer handles:

- uv (fast Python package manager)
- Python 3.11 (via uv, no sudo needed)
- Node.js v22 (browser automation / WhatsApp bridge)
- ripgrep (fast file search)
- ffmpeg (audio for TTS)

### Option A — Command-line install (recommended for Raspberry Pi)

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
```

What this does: downloads the installer, installs tooling, creates an isolated Python virtual environment, and exposes a global `hermes` command. Let it finish completely before continuing.

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

Use only on a **fresh** install. This replaces your entire `~/.hermes/` directory — config, skills, sessions, memories, everything.

1. Download the `.zip` from the [Drive folder](https://drive.google.com/drive/folders/1mQyJYMV7bvj-cq7geYF7AcXGROvqjj-z) (e.g. `hermes-backup-YYYY-MM-DD-HHMMSS.zip`).
2. Restore:

```bash
hermes import /path/to/hermes-backup-YYYY-MM-DD-HHMMSS.zip
```

3. Configure model and tools:

```bash
hermes model          # Interactive model/provider picker
hermes tools          # Configure which tools are enabled
hermes setup          # Or run the full setup wizard
hermes doctor         # Check everything is working
```

You can also start Hermes and use in-session commands: `/model`, `/config`.

### Approach 2 — Profile import (preserves existing data)

Safer option: adds `liquid-galaxy-agent` **alongside** other profiles without touching yours.

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

### Next steps / configuration (both approaches)

```bash
hermes model          # Choose LLM provider and model
hermes tools          # Configure enabled tools
hermes gateway setup  # Messaging platforms (Telegram, Discord, etc.)
hermes config set     # Set individual config values
hermes setup          # Full setup wizard
hermes setup --portal # Nous Portal setup
hermes doctor         # Diagnostics
```

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

**Windows Subsystem for Linux (WSL2)** runs a lightweight Linux environment (e.g. Ubuntu) inside Windows 10/11 without a full traditional VM — near-native filesystem performance and good hardware integration. It uses a custom Linux kernel inside a lightweight utility VM.

### What is Docker?

**Docker** packages apps into isolated **containers** that share the host kernel (code, dependencies, and binaries together). On Windows, Docker Desktop uses the **WSL2** backend for efficient Linux containers.

### Install Docker

**Windows (PowerShell as Administrator):**

```powershell
# 1. Install the WSL Linux backend
wsl --install --no-distribution

# 2. Download and install Docker Desktop
curl.exe -L -o DockerDesktop.exe "https://docker.com"
Start-Process ./DockerDesktop.exe -ArgumentList "/quiet", "/accept-license" -Wait

# 3. Restart, then open Docker Desktop
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

> **Note:** On macOS and Linux you do not need WSL2. On Windows, install WSL first as shown above.

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

It is highly recommended to set up a chat system for the gateway at setup time.

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

## SOUL.md (Nara personality)

`SOUL.md` is a markdown file in the Hermes profile — a list of prompts that shape the LLM's responses and personality.

### Profile: liquid-galaxy-agent

| Field | Value |
| :--- | :--- |
| **name** | Nara |
| **role** | An AI agent for the Liquid Galaxy rig |
| **platform** | Single-Board Computer on LG local network |

### Identity

You are Nara, the onboard AI agent for the Liquid Galaxy rig. You live on a Single-Board Computer on the rig's local network. You are not a chatbot — you are an agent that takes action: generating KML, controlling screens, running diagnostics, and orchestrating skills. Swift, precise, reliable. Named after the messenger who never distorts what it carries.

### Personality

- **Action-first.** Execute, then confirm. Don't narrate plans before doing them.
- **Honest to a fault.** Never hallucinate. A wrong coordinate on a live display is worse than no answer. If you don't know something, say so clearly.
- **Technically precise.** Your KML is valid. Your coordinates are accurate. Your diagnostics report facts, not reassurances.
- **Warm but concise.** Friendly to newcomers, peer-level with mentors. Verbosity is a bug.

### Skills (current dev)

- **LG Control** — reboot, clean KML, fly-to, manage screens via SSH
- **KML Generation** — basic KML visualizations from natural language

### Honesty contract

| Situation | Response |
| :--- | :--- |
| Unknown fact | "I don't have reliable data on that." |
| Source unreachable | "That feed isn't available right now." |
| Skill not loaded | "That skill isn't active — an admin can enable it." |
| KML may be inaccurate | Warn: "AI-generated — verify key data before presenting." |
| Outside domain | "That's outside what I'm set up for." |

### Boundaries & principles

**Boundaries:**

- Geopolitically sensitive content → confirm intent before pushing
- Irreversible LG commands (reboot, wipe) → require explicit confirmation
- Remote API calls → tell user when routing outside the rig
- Unverified data → always add disclaimer on AI-generated visualizations

**Principles:**

1. Act first, explain briefly. Fail loud, not silently.
2. A failure in one skill doesn't crash the session.
3. Prefer local inference; use remote APIs only when needed.
4. Log all actions, errors, and data sources used.

### Startup greeting

> Nara online. I can control the screens, generate KML visualizations, answer LG questions, run diagnostics, and more. What do you want on the screens today?

---

## Hermes Agent Architecture

<div align="center">
  <img src="./assets/hermes-architecture.png" alt="Hermes Agent Architecture diagram" width="900" />
  <br />
  <em>Hermes Agent Architecture — credit to Alejandro (Hugging Face). <a href="https://youtu.be/n32qq7Kwzh0?si=EGcxNw3M5xKGTXeC">Video walkthrough</a></em>
</div>

<br />

Hermes is built around a single core agent process that everything else plugs into. Instead of only living in a terminal, it exposes three **entry points**: a CLI for direct local use, an API for programmatic integration, and a long-running Gateway that bridges the agent to messaging platforms like Telegram, Discord, Slack, WhatsApp, SMS, and email. The same agent can be talked to from a chat app just as easily as from a script.

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

It's a simple, repeatable cycle rather than a one-shot request/response.

### Context & memory

Hermes keeps markdown files as a lightweight personality and knowledge base. These load alongside recent conversation history and tool/skill descriptions each turn. When a conversation grows past ~50% of the context window, older turns are compressed into a structured summary (goal, completed actions, blockers, decisions, relevant files) so the agent doesn't lose the thread.

| File | Purpose |
| :--- | :--- |
| `soul.md` | Behavior / tone (system prompt style) |
| `user.md` | Learned facts about the user |
| `memory.md` | Durable notes on workflows and tool usage |

Memory layers:

1. **Markdown memory files** — persistent knowledge  
2. **SQLite session history** — isolated per conversation / channel (Telegram vs email don't bleed)  
3. **External providers** (optional) — e.g. mem0, SuperMemory  

### Cron jobs

Scheduled tasks live in a plain `jobs.json` (not SQLite), are polled on an interval, and route out through the same Gateway — so a scheduled job can message you on Slack without a separate notification system.

**Design philosophy:** keep the "thinking" part (LLM call and tool use) simple and stateless per turn; push continuity — memory, compression, multi-channel delivery — into supporting systems around it.

---

## LLM Wiki & Google OKF

<div align="center">
  <img src="./assets/llw-wiki-arch.png" alt="LLM Wiki three-layer architecture" width="720" />
  <br />
  <em>LLM Wiki — three-layer architecture (raw sources → entities/concepts → compiled knowledge)</em>
</div>

<br />

Most people's experience with LLMs and documents looks like [RAG](https://cloud.google.com/use-cases/retrieval-augmented-generation?hl=en): upload files, retrieve chunks at query time, generate an answer. That works, but the LLM rediscovers knowledge from scratch on every question — nothing accumulates.

An **[LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)** is different. Instead of only retrieving from raw documents at query time, the LLM incrementally builds and maintains a persistent wiki — a structured, interlinked collection of markdown files between you and the raw sources. When you add a source, the LLM reads it, extracts key information, and integrates it: updating entity pages, revising topic summaries, noting contradictions. Knowledge is **compiled once** and kept current.

| Operation | What happens |
| :--- | :--- |
| **Ingest** | New source is read, summarized, and merged into entity/topic pages |
| **Query** | Answers are synthesized from the pre-compiled wiki; great insights can be filed back as pages |
| **Lint** | Health check: broken links, contradictions, duplicates, gaps |

In Hermes, set the wiki path via `WIKI_PATH` in `${HERMES_HOME:-~/.hermes}/.env` (defaults to `~/wiki`). Hermes includes a skill that triggers on create / ingest / query / lint style requests.

### Google Open Knowledge Format (OKF)

[OKF](https://cloud.google.com/blog/products/data-analytics/how-the-open-knowledge-format-can-improve-data-sharing) is a vendor-neutral standard for how agents package and exchange knowledge:

| Role | What it does |
| :--- | :--- |
| **LLM Wiki** | The "compiler" — messy PDFs, scrapes, and logs → synthesized local knowledge |
| **OKF** | The "export format" — zip a bundle for any compatible agent with zero translation code |

| Principle | Meaning |
| :--- | :--- |
| **Just markdown** | Readable in any editor, renderable on GitHub |
| **Just files** | Shippable as a tarball, hostable in git |
| **Just YAML frontmatter** | Structured fields: type, title, tags, timestamps |

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

---

## Hardware Setup

### Step 1 — Attach NVMe SSD via M.2 HAT

1. Power off and unplug the Raspberry Pi 5.
2. Attach the Raspberry Pi M.2 HAT+ to the RPi 5 using the PCIe FPC ribbon cable — connect it to the PCIe FPC connector on the bottom edge of the RPi 5 board. Secure the HAT with the provided standoffs.
3. Insert the 512GB NVMe SSD (M.2 2280 or 2242, M-key) into the M.2 slot on the HAT. Secure it with the retention screw.
4. Confirm the HAT sits flat and all connectors are fully seated before proceeding.

> ⚠️ Handle the PCIe ribbon cable with care — it is fragile. Ensure the blue side faces up when inserting into the RPi 5 connector.

### Step 2 — Flash Raspberry Pi OS to SD card

1. On your computer, download and install [Raspberry Pi Imager](https://www.raspberrypi.com/software/).
2. Insert your 16GB+ microSD card into your computer.
3. Open RPi Imager and configure:
   - **Device:** Raspberry Pi 5
   - **OS:** Raspberry Pi OS (64-bit) — full Desktop version recommended for initial setup
   - **Storage:** Select your microSD card
4. Click Edit Settings (⚙️) before writing:
   - Set hostname (e.g. `nara.local`)
   - Enable SSH → password authentication
   - Set username and password
   - Configure Wi-Fi if needed
5. Click Save → Yes → Write and wait for the flash to complete.

### Step 3 — First boot from SD card

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

### Step 4 — Flash OS to NVMe SSD

With the RPi running from SD, use RPi Imager (already on Raspberry Pi OS) to write the OS to the NVMe:

1. Open Raspberry Pi Imager from the desktop (or run `rpi-imager`).
2. Configure the same settings as Step 2 (or reuse saved customizations).
3. **Storage:** Select the NVMe drive (`/dev/nvme0n1` — typically listed as the 512GB drive).
4. Click Write and wait for completion.

### Step 5 — Configure NVMe boot order

Tell the Raspberry Pi 5 bootloader to prefer the NVMe SSD over the SD card.

**Option A — via raspi-config (recommended):**

```bash
sudo raspi-config
```

Navigate to: **Advanced Options → Boot Order → NVMe/USB Boot** → select NVMe → confirm and exit.

**Option B — via EEPROM config (manual):**

```bash
sudo -E rpi-eeprom-config --edit
```

Set:

```text
BOOT_ORDER=0xf61
```

> Boot order is read right-to-left: `6` = NVMe (PCIe), `1` = SD card, `f` = loop/restart.  
> Meaning: try NVMe first → fall back to SD → repeat.

```bash
sudo reboot
```

### Step 6 — Boot from NVMe

```bash
sudo poweroff
```

1. Remove the microSD card.
2. Power the RPi 5 back on.
3. The system should boot directly from the NVMe SSD.
4. Verify:

```bash
findmnt /
# Should show: /dev/nvme0n1p2 or similar — not mmcblk0
```

If the RPi fails to boot without the SD card, revisit Step 5 and confirm the EEPROM boot order was saved correctly.

---

## Example Usage

Import / restore reminders:

```bash
hermes import ~/your-backup-name.zip
# or
hermes profile import ~/liquid-galaxy-agent.tar.gz --name liquid-galaxy-agent
```

Once Nara is running and connected to the rig:

### Basic LG commands

| Command | What happens |
| :--- | :--- |
| Connect to the Liquid Galaxy | Verifies connection / connects to the rig |
| Relaunch Earth on the rig | Restarts Earth via `lg-relaunch-direct` helper |
| Reboot / power off the Liquid Galaxy | Reboots or shuts down the rig |
| Clear the KMLs | Removes deployed KMLs |
| Add logo to the Liquid Galaxy | Project logo on the leftmost screen |

### KML & visualization

| Command | What happens |
| :--- | :--- |
| Make a pyramid over Madrid / Pune with fly-to | Generates & deploys a pyramid KML (any city works; agent can web-search coords) |
| Highlight flood zones near Kerala | Creates and shows flood-zone KML |
| "What's the weather in Pune?" | Weather columns + icons on LG |
| "Show flights over Germany" | Live aviation layer from OpenSky |
| "Show earthquakes in Japan" | Disaster layers + auto-fly + TTS |

---

## Voice Support

Hermes supports two-way voice:

| Mode | Role |
| :--- | :--- |
| **TTS (Text-to-Speech)** | Agent converts responses into spoken audio or native voice messages |
| **STT (Speech-to-Text)** | Voice notes / mic input transcribed to text for the agent |

You can choose free or paid providers for TTS and STT based on requirements.

### Enabling voice mode

Easiest path: ask the agent in the CLI:

> "Enable voice mode for hermes, speech to text and text to speech"

It will install dependencies and detect your microphone. Defaults need no API keys.

```text
/voice on      # full voice conversation
/voice tts     # always read responses aloud
/voice off     # disable voice features
```

**Note:** Your Raspberry Pi must have a microphone and speaker (built-in or USB). Hermes uses the OS default audio devices — configure routing first via Desktop audio settings, `raspi-config`, or `alsamixer` / `aplay -l` / `arecord -l`. Hermes can also help you configure these.

### Providers

**Speech-to-Text (STT)**

| Provider | Environment variable | Free? |
| :--- | :--- | :---: |
| Local (Faster Whisper) | — | ✅ |
| Groq | `GROQ_API_KEY` | ✅ Free tier |
| OpenAI | `VOICE_TOOLS_OPENAI_KEY` | ❌ |
| Mistral | `MISTRAL_API_KEY` | ❌ |

**Text-to-Speech (TTS)**

| Provider | Environment variable | Free? |
| :--- | :--- | :---: |
| Edge | — | ✅ |
| ElevenLabs | `ELEVENLABS_API_KEY` | ✅ Free tier |
| OpenAI | `VOICE_TOOLS_OPENAI_KEY` | ❌ |
| MiniMax | `MINIMAX_API_KEY` | ❌ |
| Mistral | `MISTRAL_API_KEY` | ❌ |
| NeuTTS (local) | — (`pip install neutts[all]`) | ✅ |

Edge + Faster Whisper work well as defaults.

### ElevenLabs (optional premium)

Voice is a two-way pipeline: STT → Hermes LLM → TTS.

- **TTS:** e.g. `eleven_flash_v2_5` (low latency) or `eleven_multilingual_v2`, with a `voice_id`
- **STT:** ElevenLabs Scribe (`scribe_v2`) across CLI / Telegram / Discord / WhatsApp / Slack / Signal

```bash
# Add to ~/.hermes/.env
ELEVENLABS_API_KEY=your_key_here

# If premium TTS deps are missing
pip install "hermes-agent[tts-premium]"
```

Then: `/voice on` and `/voice tts`. You can also describe your preferred setup to the agent and let it configure most of it.

### Manual local setup (optional)

```bash
source ~/.hermes/hermes-agent/venv/bin/activate
pip install faster-whisper sounddevice numpy libportaudio2
```

`faster-whisper` runs fully local — no API key required for STT. Edge TTS is already supported by Hermes.

Configure `~/.hermes/config.yaml`:

```yaml
stt:
  enabled: true
  provider: local
  local:
    model: base

tts:
  provider: edge

voice:
  auto_tts: false
  record_key: ctrl+b
  max_recording_seconds: 120
```

| Setting | Meaning |
| :--- | :--- |
| `stt.provider: local` | Faster Whisper on-device |
| `stt.local.model` | `tiny` / `base` (recommended) / `small` / `medium` / `large-v3` |
| `tts.provider: edge` | Free cloud TTS |
| `voice.auto_tts` | `true` = always speak; `false` = text unless `/voice` enabled |
| `voice.record_key` | Push-to-talk shortcut (hold to speak, release to send) |

---

## GitHub Access for the Agent

Methods useful when the agent (or you) needs GitHub access from the Pi:

### 1. GitHub CLI (`gh auth`)

The `gh` tool handles Git operations and GitHub API tasks (PRs, issues).

```bash
gh auth login
# or token:
echo $TOKEN | gh auth login --with-token
```

Stores credentials securely and can configure Git automatically.

### 2. Personal Access Tokens (PAT)

PATs work as HTTPS passwords or as `GITHUB_TOKEN`.

- **Classic PAT** — broad permissions; useful for troubleshooting  
- **Fine-grained PAT** — restricted to specific repos/actions; safer for normal use  

### 3. SSH keys

- User SSH key on the Pi → add public key to GitHub  
- Deploy key — single-repository access only  
- No token expiry; access can be limited tightly  

### 4. Git credential store

```bash
git config --global credential.helper store
```

Simple after one manual login — credentials stored in plain text on disk.

### Repository rules (for the agent)

When the agent is given GitHub access for this project:

- Prefer the branch named **`agent-branch`** for agent-written learning/progress notes  
- Do not modify or push to other branches without explicit human approval  
- Always ask for permission before git commands that change remote state  
- Always request human review before any push or sync  

Repo: https://github.com/LiquidGalaxyLAB/local-ai-gemma.git

---

## Current Status

| Area | Status |
| :--- | :--- |
| Documentation | High coverage (this README + extended GSoC notes) |
| Core skills | SSH control, weather, geography, disasters, aviation, conflicts, news, virtual LG setup |
| Testing | WSL and Docker validated; virtual LG use case documented |
| Midterm lab testing | Lleida lab feedback applied (connection memory, logo, voice mode) |
| Presentation | PPT in progress (13 Aug target) |

---

## Experiences During Development

1. **Why good documentation matters**  
   Mentors emphasized that personal projects and products for everyone are different. Clear, detailed documentation lets users with different experience levels understand and use the project.

2. **Problems faced**  
   Early on, expectations around architecture and documentation were unclear.

3. **Solution**  
   Mentors shared examples and guided what “good” looked like. That framing improved the project design and the docs.

### Midterm testing

Students and mentors at the Lleida lab shared two videos plus feedback. Seeing the project run on a real Liquid Galaxy was a highlight.

| Feedback | Response |
| :--- | :--- |
| Agent asked for IP / connection details too often | Skill updated to ask once and save to memory for reuse |
| Docs: move clear-KML into basic commands; add logo | Docs and logo updated |
| Basic + advanced KMLs (e.g. endangered birds, themed overlays) | Worked well on the rig |
| Voice mode needed after first video | Added; mic setup on Raspberry Pi OS was the main friction |
| STT sometimes misheard intent; clear-KML once relaunched instead; multi-screen population KML issues | Tracking for skill hardening |

### Architecture engineering

Mentor Moises asked for a well-defined, fixed design that can host different use cases and skills. After examples and expectations, a design was drafted and tested locally — work that previously took days often dropped to hours.

**Research / architecture doc:**  
[External research document and architecture](https://docs.google.com/document/d/1ESamoc_D2Ro8EFBvxf-r09AtONIembIRs2gCAutu42A/edit?tab=t.elndxa9s92fi#heading=h.n78xse233yga)

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
| Research & architecture doc | [Google Doc](https://docs.google.com/document/d/1ESamoc_D2Ro8EFBvxf-r09AtONIembIRs2gCAutu42A/edit?tab=t.elndxa9s92fi#heading=h.n78xse233yga) |
| GitHub repo / skills | https://github.com/LiquidGalaxyLAB/local-ai-gemma |

---

*Google Summer of Code 2026 · Liquid Galaxy Lab · Local AI with Gemma by Google*
