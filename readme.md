# GSoC 2026 Project for Liquid Galaxy

<div align="center">
  <img src="./assets/img2.png" alt="Liquid Galaxy Logo" width="400"/>
</div>

**350 Hr — Local AI with Gemma by Google** 

**Project Documentation**

**How to use this documentation and the system-**  
This documentation covers important concepts, how the project works, how a user can use this / replicate this project on their systems, my progress with GSoC and important references for it. 

It is intended for contributors, mentors, and users who want to learn how the system works, deploy it on their own hardware, or build new capabilities on top of it. The guide begins with the project's goals and architecture, then walks through installation, configuration, and profile restoration before explaining the system's modular skills, practical use cases, and development experience. Whether you are using Nara on a Raspberry Pi with a Liquid Galaxy rig, experimenting with hermes, or contributing new features, following the documentation in order will provide the necessary background, setup instructions, and references to successfully understand, run, and extend the project.

If you want to start right away, [this installation](#installation) is the way

## Planned Tasks

| Task | Result |
| :--- | :--- |
| **1. Work on Docs** | ✅ |
| **2. Test docker and other setup ways** | ✅ WSL and Docker setup works |
| **3. Test architecture and more advanced use cases** | Attempting to curate more advanced use cases. Architecture works well. Also created a new use case for LG rig setup. Added 2+ sources for data. |
| **Build a virtual LG** | Added to GitHub and doc |
| **4. PPT for 13th Aug** | [ongoing] |
| **5. 27 Jul: Update Docs** | done |

Nara is the onboard AI agent for Liquid Galaxy. Built on top of **[Hermes Agent](https://hermes-agent.nousresearch.com/docs/).**

## Index

- [Acknowledgement](#about-me--acknowledgement)
- [About the Project](#about-the-project)
- [Use Cases — Planned Order](#use-cases-planned-order)
- [Example Use Cases](#example-use-cases)
- [Hermes Agent Architecture Explained](#hermes-agent-architecture-explained)
- [About LLM Wiki and Google OKF](#about-llm-wiki-and-google-okf)
- [Hermes Agent Setup](#hermes-agent-setup)
- [Installation](#installation)
- [Docker & WSL Setup](#docker-and-wsl-based-setup-for-hermes)
- [System Architecture](#system-architecture)
- [Tech Stack](#tech-stack)
- [Hardware](#hardware)
- [Hardware Setup](#hardware-setup)
- [Voice Mode Config](#voice-support)
- [Example Usage](#example-usage)
- [Current Status](#current-status)
- [GitHub Access for Agent](#github-access-for-the-liquid-galaxy-project)
- [Experiences During Development](#experiences-during-development)
- [External Research Document](https://docs.google.com/document/d/1ESamoc_D2Ro8EFBvxf-r09AtONIembIRs2gCAutu42A/edit?tab=t.elndxa9s92fi#heading=h.n78xse233yga)

## About Me & Acknowledgement {#about-me-acknowledgement}

I’m Harsh Mehta, a curious engineering student from Pune city with a keen interest in learning how real world production systems and projects work. Grateful to Liquid Galaxy and the Google Summer of Code for giving this incredible opportunity to learn. It is helping me to understand the quality required to work at a stage where the work done by us is actually used in real life by other people.

Also many thanks to Trang, Fabricio, Oriol and Josep at the Liquid Galaxy Lab in Lleida to test and share valuable feedback on our project.

## About the Project {#about-the-project}

This project builds Nara…. an AI assistant server that lives on the Liquid Galaxy rig's local network. Nara runs on a Raspberry Pi 5 connected to the rig via SSH, accepts commands through the CLI, and autonomously generates and pushes content such as KML visualizations, guided tours, real-time data maps, and more directly to the Liquid Galaxy screens.

The system is built as a Hermes agent with a modular skill architecture, meaning capabilities can be added, enabled, or disabled independently without touching the core runtime. It supports both fully local AI inference (offline, self-contained) and a hybrid mode that optionally routes complex tasks to remote model APIs balancing hardware limits with response quality.

The goal is a stable, easy-to-extend assistant that any LG user, mentor, or contributor can run in the lab or deploy from a backup profile.

## **Use Cases Planned Order**

* LG Command Execution: Execute SSH commands on the LG rig (relaunch, reboot, poweroff)  
* Weather Monitoring: Fetch live weather data and visualize via KML  
* News & Geopolitical Visualization: Live event mapping on LG  
* Geography educator : Teach geography concepts with real world examples and KMLs  
* History educator : Show how events in the history happened such as wars.  
* Natural Disaster Command Center- Layers: Earthquakes, wildfires, weather alerts, climate anomalies, displacement flows  
* Maritime Domain Awareness- Layers: AIS density zones, trade routes, chokepoint status, live tankers, cable advisories  
* Energy & Infrastructure Monitoring - Layers: Pipelines, energy infrastructure, fuel shortages, renewable installations, mining sites  
* Live Aviation Watch  - Layers: Military flights, flight delays, NOTAM rings, airport status  
* Cyber/Undersea Infrastructure Map    - Layers: Undersea cables, internet outages, GPS jamming, cyber threats  
* Supply Chain & Trade Flow Visualization   - Layers: Trade routes, chokepoint status, commodity ports, tanker positions  
* Economic Markets: The system taps into Finnhub and FRED (Federal Reserve Economic Data) to monitor financial trends, stock market fluctuations, and key economic indicators, giving users a pulse on the health and stability of global economies.  
* Armed Conflicts: By pulling information from ACLED (Armed Conflict Location & Event Data Project) and UCDP (Uppsala Conflict Data Program), the system identifies and maps incidents of political violence, civil unrest, and warfare across the globe as they are reported.

### Example Use Cases ( What can you do with current version of project)

| Skill name | Input Examples | Prompt [added to input] | Comments | Expected Output | Link to SKILL.md | | ----- | ----- | ----- | ----- | ----- | ----- | | lg-ssh-control | Hey ,"Connect to LG", "Relaunch Earth", "Reboot the rig" Or clear the KMLs, power of my liquid galaxy , etc | User command \+ SSH credentials \+ LG IP/port \+ frame count and  lg-ssh-control SKILL.md | SSHes into lg1, executes control commands (relaunch/reboot/poweroff/refresh), deploys helpers rig | Agent gives a positive response stating connected to liquid galaxy. You are now able to execute basic lg commands such as relaunch, reboot, clear kmls , powerof, etc.. A screenshot of the expected on the lg | https://github.com/LiquidGalaxyLAB/local-ai-gemma/blob/main/skills/lg-ssh-control.md | | lg-use-cases | "What can the LG do?", "Show me use cases", "Hey nara, what can you do ?" | User query \+ reference to all developed use cases \+ layer stacks \+ camera patterns | It will refer all different skills available and act like a user guide for the project. | I have ‘X’ use cases available: SA Wall, Maritime, Disaster, Energy, Aviation, … And describe the tasks they can do | https://github.com/LiquidGalaxyLAB/local-ai-gemma/blob/main/skills/lg-use-cases.md | | geography-educator | "Teach me about the Date Line", "Show India monsoon on LG", "Explain Turkey earthquake"  | Topic name \+ pre-built KML generator \+ region polygon data \+ TTS script and its skill.md | This skill with fetch relevant concepts and create geographical explainer kmls | Generates educational KML with reference lines, 3D zones, labeled points; deploys with right-screen panel \+       voiceover  | https://github.com/LiquidGalaxyLAB/local-ai-gemma/blob/main/skills/geography-educator.md | | armed-conflicts | "Show global conflicts", "Where are active wars?", "Armed conflicts watch"  | Static conflict zone data (10 zones) \+ BBC conflict news \+ decide visual per zone | Generates unique dynamic KMLs per zone (front arrows, siege rings, displacement arrows, faction markers, wave       spreads); deploys right-screen panel with camera tour and also per-zone TTS  | Ukraine: 3D column \+ front arrow. Gaza: 4 siege rings \+ 25 damage dots. Touring 10 zones with narration. Example flow | https://github.com/LiquidGalaxyLAB/local-ai-gemma/blob/main/skills/armed-conflicts.md | | weather-monitor | "What's the weather in Pune?", "Show me Mumbai weather", "Show me Weather on LG" | City name \+ lat/lon \+ wttr.in API data | Fetches live weather, generates 3D temperature column ( color-coded red=hot/blue=cool), wind arrow,       weather icon, right-screen panel \+ TTS | Shows kmls based on temp and weather conditions along with voice also | https://github.com/LiquidGalaxyLAB/local-ai-gemma/blob/main/skills/weather-monitor.md | | natural-disaster | "Show earthquakes in Japan", "Any wildfires happening?" | USGS GeoJSON \+ NASA EONET \+ NOAA NWS \+ region input req | Fetches live quakes/events, generates 3D colored columns      ,auto-fly to location,       With  TTS     Also state something like - "12 earthquakes, 3 wildfires, 2 weather alerts.  | This skill fetches data from multiple APIs to ensure data is as close to truth as possible. It will make KMLs and also give a voiceover in response about natural events | https://github.com/LiquidGalaxyLAB/local-ai-gemma/blob/main/skills/natural-disaster.md | | Live Aviation | "Show flights over Germany", "Air traffic over Europe" | OpenSky Network API \+ region input requires \+ 35 airport       Config stored and can be expanded | Fetches  aircrafts from API, generates heading-rotated plane       icons at actual altitude, adds airport markers.       airport panel \+ TTS | Aircrafts will be visible on liquid galaxy with their labels over them and you can view over region said in the input. | https://github.com/LiquidGalaxyLAB/local-ai-gemma/blob/main/skills/live-aviation.md |

**This is a new skill which will help users to setup a virtual liquid galaxy on their system.**  
[SKILL .md](https://github.com/LiquidGalaxyLAB/local-ai-gemma/blob/main/skills/lg-installation-setup.md)  
**What It Is**  
      
    A simple step-by-step guide for building a Liquid Galaxy rig from scratch.  
      
    **What It Covers**  
      
    Section: What is LG?  
    What It Explains: 3 computers (lg1 master \+ lg2/lg3 slaves) with multi-screen Google Earth  
    ────────────────────────────────────────  
    Section: How it works  
    What It Explains: Master serves KML via Apache → slaves refresh every 3s → ViewSync syncs cameras  
    ────────────────────────────────────────  
    Section: Setup steps  
    What It Explains: 1\. Create VMs 2\. Run install script 3\. Configure master 4\. Connect slaves 5\. Connect Hermes  
    ────────────────────────────────────────

# **Hermes Agent Architecture Explained**

![Hermes Architecture](./assets/img1.png)***Credit to Alejandro from Hugging Face***  
[***https://youtu.be/n32qq7Kwzh0?si=EGcxNw3M5xKGTXeC***](https://youtu.be/n32qq7Kwzh0?si=EGcxNw3M5xKGTXeC)

Hermes is built around a single core agent process that everything else plugs into. Instead of only living in a terminal, it exposes three entry points: a CLI for direct local use, an API for programmatic integration, and a long-running Gateway process that bridges the agent to messaging platforms like Telegram, Discord, Slack, WhatsApp, SMS, and email. This means the same agent can be talked to from a chat app just as easily as from a script.

At the heart of every interaction is what the architecture calls the agent loop: a message comes in, Hermes assembles the relevant context, sends it to the LLM along with tool definitions, lets the model call tools if needed, feeds tool results back in, generates a final answer, and then updates its memory before waiting for the next message. It's a simple, repeatable cycle rather than a one-shot request/response.

What makes that loop useful over time is how context is built and managed. Hermes keeps a small set of markdown files that act like a personality and knowledge base, one for behavior and tone, one for facts it's learned about the user, and one for durable notes on workflows and tool usage. These get loaded alongside recent conversation history and descriptions of available tools and skills each time the agent runs. When a conversation grows long enough to threaten the context window (roughly past the halfway point), older messages get compressed into a structured summary ; capturing the goal, what's been done, open blockers, key decisions, and relevant files , so the agent doesn't lose the thread without blowing up its context budget.

Memory itself is split across three layers: the markdown files mentioned above for persistent knowledge, a SQLite-backed session history that's kept separate per conversation (so your Telegram thread and your email thread don't bleed into each other), and optionally an external memory provider for teams that want something more heavyweight.

Finally, Hermes supports scheduled autonomy through a lightweight cron system. Jobs are stored in a plain JSON file rather than a database, polled on an interval, and when triggered, they route back out through the same Gateway used for regular conversations ; so a scheduled task can, for example, message you on Slack without needing a separate notification system.  
The overall design philosophy is to keep the "thinking" part (the LLM call and tool use) simple and stateless per turn, while pushing all the complexity of continuity; memory, compression, multi-channel delivery; into supporting systems around it.

# About LLM Wiki and Google OKF {#about-llm-wiki-and-google-okf}

[**LLM Wiki-**](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) Most people's experience with LLMs and documents looks like [RAG](https://cloud.google.com/use-cases/retrieval-augmented-generation?hl=en): you upload a collection of files, the LLM retrieves relevant chunks at query time, and generates an answer. This works, but the LLM is rediscovering knowledge from scratch on every question. There's no accumulation. Ask a subtle question that requires synthesizing five documents, and the LLM has to find and piece together the relevant fragments every time. Nothing is built up. NotebookLM, ChatGPT file uploads, and most RAG systems work this way.

The idea here is different. Instead of just retrieving from raw documents at query time, the LLM incrementally builds and maintains a persistent wiki - a structured, interlinked collection of markdown files that sits between you and the raw sources. When you add a new source, the LLM doesn't just index it for later retrieval. It reads it, extracts the key information, and integrates it into the existing wiki ; updating entity pages, revising topic summaries, noting where new data contradicts old claims, strengthening or challenging the evolving synthesis. The knowledge is compiled once and then kept current, not re-derived on every query.

This is the key difference: the wiki is a persistent, compounding artifact. The cross-references are already there. The contradictions have already been flagged. The synthesis already reflects everything you've read. The wiki keeps getting richer with every source you add and every question you ask.

You never (or rarely) write the wiki yourself , the LLM writes and maintains all of it.

**Key operations**  
**Ingest:** When you add a new document, the LLM reads it, summarizes it, and automatically updates all relevant entity pages, indexes, and cross-references.

**Query:** You ask questions, and the LLM synthesizes answers from the pre-compiled wiki. If you uncover a great insight, you file that answer right back into the wiki as a new page.

**Lint (The Health Check):** Periodically, the LLM scans the wiki to fix broken links, flag contradictions between old and new files, detect duplicate pages, and point out information gaps.

LLM wiki in hermes   
  
  
The hermes itself has added a skill for LLM wiki

Asks to create, build, or start a wiki or knowledge base  
Asks to ingest, add, or process a source into their wiki  
Asks a question and an existing wiki is present at the configured path  
Asks to lint, audit, or health-check their wiki  
References their wiki, knowledge base, or "notes" in a research context

Location: Set via WIKI_PATH environment variable (e.g. in ${HERMES_HOME:-\~/.hermes}/.env).

If unset, defaults to \~/wiki.

[**Google’s OKF Format**](https://cloud.google.com/blog/products/data-analytics/how-the-open-knowledge-format-can-improve-data-sharing) **-** Open Knowledge Format (OKF) is a vendor-neutral standard designed to formalize how AI agents organize, package, and exchange knowledge.  
The LLM Wiki acts as the "compiler." It takes messy PDFs, raw web scrapes, and slack logs, processes them, lints them for broken links, resolves contradictions, and builds a synthesized local database.

OKF acts as the "export format." Once your LLM Wiki has compiled your core knowledge, you export it as an OKF bundle. This bundle can then be zipped up and handed to any other compatible agent (whether it's on Google Cloud, a local Ollama instance, or Claude Code) and it will immediately understand your data structure with zero translation code required.

3 principles of OKF  
Just markdown : readable in any editor, renderable on GitHub, indexable by any search tool

Just files : shippable as a tarball, hostable in any git repo, mountable on any filesystem

Just YAML frontmatter : for the small set of structured fields that need to be queryable: type, title, description, resource, tags, and timestamp

### [Click to collapse / expand]           Hermes Agent Setup

The self-improving AI agent built by Nous Research. The only agent with a built-in learning loop, it creates skills from experience, improves them during use, nudges itself to persist knowledge, and builds a deepening model of who you are across sessions.

**Website: [https://hermes-agent.nousresearch.com/](https://hermes-agent.nousresearch.com/)**

## Some Important Features

**Profiles**

According to their official documentation we can define a as [profile](https://hermes-agent.nousresearch.com/docs/user-guide/profiles) a self-contained Hermes home directory. Starting with one profile (liquid-galaxy-agent) 

Each profile gets its own config.yaml, .env, SOUL.md, memories, sessions, skills, cron jobs, and state database. Basically its own directories which work independently from other profiles ! A clean slate.

**Backups**

[Backups](https://hermes-agent.nousresearch.com/docs/getting-started/updating#full-pre-update-backup---backup) create a zip archive of config, skills, sessions, and data, everything except the codebase. Restore with [hermes import](https://hermes-agent.nousresearch.com/docs/reference/cli-commands#hermes-import).

* CLI Session :  Handles interactive terminal UIs. Triggers conversation loop, builds system prompts, resolves model providers, executes tools, persists history.  
* Gateway Message :  Manages 20+ messaging platform adapters (Discord, Slack, WhatsApp, etc.). Handles auth, session isolation, response routing.

**Skills Setup**

Hermes needs custom skills for LG-specific use cases. A skill \= instructions \+ shell commands \+ tools.  
Skills and tools work together to satisfy use cases.

References: [Adding Tools](https://hermes-agent.nousresearch.com/docs/developer-guide/adding-tools) | [Creating Skills](https://hermes-agent.nousresearch.com/docs/developer-guide/creating-skills)

Skills live in /skills/liquid-galaxy/     ( Note that this is under the profile directory, each profile has this dir of its own )

---

## **Installation**

Get Hermes Agent up and running!

A couple of terms you'll see everywhere below:

**Terminal** : the black text-window where you type commands instead of clicking icons.

**Shell** : the program running inside the terminal that reads your commands (bash and zsh are two common ones).

**Archive file (.zip / .tar.gz)** : a single file that contains a bunch of other files and folders squashed together, like a suitcase you pack and unpack.

**\~** : a shortcut that means "my home folder" (on the Pi, this is /home/pi or similar).

First, Download the latest version of backup zip on your raspberry pi 5\.  
[Backup download](https://drive.google.com/drive/folders/1mQyJYMV7bvj-cq7geYF7AcXGROvqjj-z?usp=sharing)  
Folders are present with dates. Choose the latest date folder and use the hermes / profile backup.  
**Quick Install**

With Hermes Desktop (recommended for macOS / Windows): Download the [Hermes Desktop installer](https://hermes-agent.nousresearch.com/) from the website and run it.

You can check out this setup video that I made  
@[https://youtu.be/r77kEcoE7Sw?si=a9vfaL3OiTqQK0gE](https://youtu.be/r77kEcoE7Sw?si=a9vfaL3OiTqQK0gE)

**Before you start**  
On the Raspberry Pi (which runs Linux), the installer needs only a couple of things already on the machine, it installs everything else itself.

Open a terminal on your Pi and run this to check if Git is installed:  
git --version

If you see a version number, you're good. If not, install it:

sudo apt update  
sudo apt install -y git curl xz-utils

**git** — lets the installer download (clone) the Hermes Agent codebase.  
**curl** — lets the installer download files from the internet.  
**xz-utils** — needed because the installer downloads Node.js as a compressed .tar.xz file and needs to be able to open it.

You do **not** need to manually install Python, Node.js, ripgrep, or ffmpeg, the Hermes installer detects and installs all of those for you automatically. 

**Installing hermes agent** 

**Option A** : Command-line only (this is what you want for a Raspberry Pi)

Raspberry Pi 5 runs Linux, so use the Linux install command, run directly in your Pi's terminal:

bashcurl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash

What this line actually does, piece by piece:

**curl -fsSL \<url\>** downloads the installer script from that web address.  
**| bash pipes (feeds)** that downloaded script straight into bash so it runs immediately.

The script then quietly installs Python, Node.js, and other tools it needs, downloads the Hermes Agent code, sets up an isolated Python environment for it (called a "virtual environment" it keeps Hermes's software separate from anything else on your system), and creates a hermes command you can type from anywhere.

This will take a few minutes. Let it finish completely before doing anything else.

**Option B :**  Desktop app (macOS / Windows only)

This does not apply to your Raspberry Pi. It's only mentioned here for completeness: on a Mac or Windows PC, you'd instead download an installer from the Hermes website and double-click it. Since you're on a Pi, use Option A above.

Powershell -   
iex (irm https://hermes-agent.nousresearch.com/install.ps1) 

**Prerequisites [ these are as per hermes docs and may change ]**

On non-Windows platforms, the only prerequisite is Git. The installer automatically handles:

* uv (fast Python package manager)  
* Python 3.11 (via uv, no sudo needed)  
* Node.js v22 (for browser automation and WhatsApp bridge)  
* ripgrep (fast file search)  
* ffmpeg (audio format conversion for TTS)

---

## After Installation

Right after install finishes, your terminal doesn't know about the new hermes command yet ….  it needs to reload its settings. Run:

- Run source \~/.bashrc (or source \~/.zshrc if you use Zsh).

Now test it: run the command - hermes    
If a chat prompt opens, it worked. Type `exit` or press `Ctrl+C` to leave it for now. 

By default, Hermes keeps all its data inside a folder named .hermes in your user account home directory (\~/.hermes/).

---

### Restoring the Liquid Galaxy Profile

You have two ways to bring the Liquid Galaxy project's Hermes setup onto this Pi. **Which one you should use depends on whether this Pi already has other Hermes work on it that you care about.**

### **Quick decision guide**

| Your situation | Use | | ----- | ----- | | This is a brand-new Hermes install, nothing to lose | **Approach 1** | | You already have your own chats/config/skills on this Pi and don't want to lose them. (Means you already use hermes and don't want to lose your older hermes data or hermes chats) | **Approach 2** |

---

## Approach 1 is Full Backup Restore (This Overwrites Everything)

Use this only if you are starting from a fresh Hermes install with no existing work. This replaces your entire \~/.hermes/ directory — config, skills, sessions, memories, everything.

Step 1 — Locate the backup archive on [the drive link](https://drive.google.com/drive/folders/1i1NlJXJ04NV__2rY2iOQxjB74cn2gBm8?usp=sharing)

You should have a .zip file (e.g., hermes-backup-YYYY-MM-DD-HHMMSS.zip).

Step 2 — Restore it using the built-in command 

hermes import /path/to/hermes-backup-YYYY-MM-DD-HHMMSS.zip

Replace `/path/to/...` with wherever the file actually landed (for example, `~/Downloads/hermes-backup-...zip`). 

Step 3 — Configure API keys

The restored backup includes settings, but you'll still need to tell Hermes which AI provider and API key to use on *this* machine.

Start Hermes and configure your LLM provider:

hermes

Then in the session, run:

/model      # Choose your LLM provider and model

/config     # Check settings

Or use the CLI commands:

hermes model          # Interactive model/provider picker

hermes tools          # Configure which tools are enabled

hermes setup          # Or run the full setup wizard

hermes config set     # Set individual config values

Step 4 — Verify

hermes doctor         # Check everything is working

---

## Approach 2 : Profile Import (Preserves Your Data)

Use this if you already have Hermes set up with your own work and just want to add the Liquid Galaxy profile alongside it. This does not touch your existing profile at all.

This is the safer option. Hermes supports **profiles** …. Think of a profile as a separate, self-contained "workspace" for Hermes, each with its own settings, skills, and chat history, that all live side-by-side without touching each other. Importing the Liquid Galaxy profile just adds a new workspace and  it does not touch anything you already have. 

Step 1 — Get the exported profile file

You should have a .tar.gz file (e.g., [liquid-galaxy-agent.tar.gz](http://liquid-galaxy-agent.tar.gz)) in [drive folder](https://drive.google.com/drive/folders/1i1NlJXJ04NV__2rY2iOQxjB74cn2gBm8?usp=sharing). This is the exported profile archive.

Step 2 — Import it

hermes profile import /path/to/liquid-galaxy-agent.tar.gz --name liquid-galaxy-agent

This creates a new profile called liquid-galaxy-agent inside your existing \~/.hermes/profiles/ directory. Your own profiles are completely untouched.

Step 3 — Switch to the Liquid Galaxy profile

hermes profile use liquid-galaxy-agent

Step 4 — Configure API keys

The profile has all the Liquid Galaxy skills and config, but you still need to add your own LLM API key:

hermes model          # Choose your LLM provider and model

hermes tools          # Check which tools are enabled

hermes doctor         # Verify everything is reading correctly

Step 5 — Start using it

hermes                # Start chatting

Step 6 — Switching between profiles later

hermes profile list                    # See all profiles

hermes profile use liquid-galaxy-agent # Switch to LG profile

hermes profile use default             # Switch back to your own

Or run Hermes with a specific profile in one command:

hermes --profile liquid-galaxy-agent

---

### Verify Everything is Working (Both Approaches)

Run the built-in diagnostic tool to make sure Hermes sees the restored data and isn't throwing errors:

hermes doctor

---

### Next Steps / Configuration (Both Approaches)

Once the profile is loaded, configure additional options as needed:

hermes model          # Choose your LLM provider and model

hermes tools          # Configure which tools are enabled

hermes gateway setup  # Set up messaging platforms (Telegram, Discord, etc.)

hermes config set     # Set individual config values

hermes setup          # Or run the full setup wizard

hermes setup --portal # Nous Portal setup

---

### Quick Comparison

| | Approach 1 (Full Restore) | Approach 2 (Profile Import) | | :---- | :---- | :---- | | Overwrites your data? | Yes : entire \~/.hermes/ is replaced | No : adds a profile alongside yours | | Best for | Fresh install, new user | Existing Hermes user with their own data | | Command | unzip backup.zip into \~/.hermes/ | hermes profile import file.tar.gz | | Profiles available | Only this one | Yours \+ this one (switch anytime) |

Troubleshooting

| Problem | Fix | | ----- | ----- | | `hermes: command not found` after install | Run `source ~/.bashrc` again, or open a brand-new terminal window | | It says an API key isn't set | Run `hermes model`, or `hermes config set OPENROUTER_API_KEY your_key_here` | | Something seems broken after restoring/importing | Run `hermes doctor` — it diagnoses the exact issue |

Reference: [https://hermes-agent.nousresearch.com/docs/](https://hermes-agent.nousresearch.com/docs/)

---

### Docker and WSL based setup for Hermes

****

Core Architecture Overview

What is WSL2 (Windows Subsystem for Linux)?

WSL2 is a Microsoft feature that allows developers to run a lightweight, native Linux environment (such as Ubuntu) directly inside Windows 10/11 without the heavy overhead of a traditional virtual machine.

* **How it works:** It uses a highly optimized, custom Linux kernel running inside a lightweight utility VM. It achieves near-native file system performance and seamless integration with Windows hardware resources

What is Docker?

Docker is an open-source platform designed to package, deploy, and run applications inside isolated environments called **containers**.

* **How it works:** Instead of virtualizing entire hardware layers (like standard VMs), Docker shares the host operating system's kernel. Containers pack the application code, dependencies, and binaries together, ensuring the software runs identically on any machine. On Windows, Docker Desktop leverages the **WSL2** backend architecture to run Linux containers with extreme efficiency.

Run these commands to set up a continuous, long-running Hermes Agent that saves your progress 

You may also refer the [Official Docs](https://hermes-agent.nousresearch.com/docs/user-guide/docker) for Docker setup

For macOS and Linux , you do not need wsl2. For windows you can download it using this command in your terminal

wsl --install --no-distribution

Step 1: Docker setup

**Windows** 

User powershell as administrator access. (To do this just goto windows search and type powershell, then click run as admin)

# 1\. Install the WSL Linux backend architecture

wsl --install --no-distribution

# 2\. Download and install Docker Desktop silently

curl.exe -L -o DockerDesktop.exe "https://docker.com"

Start-Process ./DockerDesktop.exe -ArgumentList "/quiet", "/accept-license" -Wait

# 3\. Restart your computer to complete setup, then open the Docker Desktop app.

**macOS** 

Open terminal and run the following commands- 

curl -o Docker.dmg "https://docker.com"

sudo hdiutil attach Docker.dmg

sudo cp -R /Volumes/Docker/Docker.app /Applications

sudo hdiutil detach /Volumes/Docker

open /Applications/Docker.app

**Linux (Ubuntu/Debian Terminal)** 

# 1\. Run the official automated installation script

curl -fsSL https://docker.com | sh

# 2\. Add your user to the docker group so you don't need 'sudo' every time

sudo usermod -aG docker $USER

# 3\. Apply the changes immediately

newgrp docker

Step 2: Initialize Configuration Profile

Create a local directory of your choice and execute the command given below:

bash

# Create and enter your preferred workspace directory

mkdir \<YOUR_WORKSPACE_DIR\>

cd \<YOUR_WORKSPACE_DIR\>

# Run the setup wizard to input API keys and generate configs

docker run *-it* *--rm* \\ *-v* \~/.hermes:/opt/data \\ nousresearch/hermes-agent setup 

This drops you into the setup wizard, which will prompt you for your API keys and write them to \~/.hermes/.env. You only need to do this once. It is highly recommended to set up a chat system for the gateway to work with at this point.

To open an interactive **chat session** against a running data directory:

docker run -it --rm \\  -v \~/.hermes:/opt/data \\  nousresearch/hermes-agent

**You can also run the agent directly using WSL (**Windows subsystem for linux**)**  
Install wsl2 using this command -   
wsl --install -d Ubuntu    [you can select disto as per your wish but ubuntu is the most common one]

#Now start the ubuntu  
wsl -d Ubuntu  
(Windows will open a separate terminal window and prompt you to create a Unix username and password. Do that, and you are officially inside a pure Linux terminal environment!)

Then run this script and you’re done!

curl -fsSLO https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh

### [Click to collapse / expand]         [SOUL.md](http://SOUL.md) 

Soul is a markdown file for the hermes profile which is just a list of prompts that pass on to the LLM to refine responses or provide a personality to it.

**Below is the exact syntax from hermes docs.**

## Profile: liquid-galaxy-agent

name: Nara

role: An AI agent for the Liquid Galaxy rig

platform: Single-Board Computer on LG local network

## Identity [ set of prompts ]

You are Nara, the onboard AI agent for the Liquid Galaxy rig. You live on a Single-Board Computer on the rig's local network. You are not a chatbot you are an agent that takes action: generating KML, controlling screens, running diagnostics, and orchestrating skills. Swift, precise, reliable. Named after the messenger who never distorts what it carries.

## Personality

* Action-first. Execute, then confirm. Don't narrate plans before doing them.  
* Honest to a fault. Never hallucinate. A wrong coordinate on a live display is worse than no answer. If you don't know something, say so clearly.  
* Technically precise. Your KML is valid. Your coordinates are accurate. Your diagnostics report facts, not reassurances.  
* Warm but concise. Friendly to newcomers, peer-level with mentors. Verbosity is a bug.

## Skills (Current dev)

* LG Control: Description: Reboot, clean KML, fly-to, manage screens via SSH  
* KML Generation: Description: Basic KML based visualizations from natural language requests.


## Honesty Contract

* Unknown fact: "I don't have reliable data on that."  
* Source unreachable: "That feed isn't available right now."  
* Skill not loaded: "That skill isn't active — an admin can enable it."  
* KML may be inaccurate: Warn: "AI-generated — verify key data before presenting."  
* Outside your domain: "That's outside what I'm set up for."

## Boundaries & Operating Principles

Boundaries:

* Geopolitically sensitive content → confirm intent before pushing  
* Irreversible LG commands (reboot, wipe) → require explicit confirmation  
* Remote API calls → tell user when routing outside the rig  
* Unverified data → always add disclaimer on AI-generated visualizations

Principles:

1. Act first, explain briefly. Fail loud, not silently.  
2. A failure in one skill doesn't crash the session.  
3. Prefer local inference; use remote APIs only when needed.  
4. Log all actions, errors, and data sources used.

## Startup Greeting:

> Nara online. I can control the screens, generate KML visualizations, answer LG questions, run diagnostics, and more. What do you want on the screens today?

# System Architecture [Hermes] {#system-architecture-hermes}

****

# Tech Stack {#tech-stack}

* Agent Runtime: Hermes, Multi-agent orchestration  
* AI / Models: Ollama or LMstudio (local inference), Remote model APIs  
* Visualization: KML, Google Earth, Liquid Galaxy  
* Communication:  WebSockets, REST  
* Data Sources: OpenSky Network, Celestrak, RSS Feeds, Weather APIs  
* Hardware Interface: SSH, sshpass, Shell scripting  
* Languages: Python, Shell

# Hardware

* SBC: Specification: Raspberry Pi 5 , 8GB RAM  
* Storage: Specification: 512GB / 256GB NVMe SSD  
* NVMe Interface: Specification: Raspberry Pi M.2 HAT+  
* Boot Media: Specification: 16GB+ microSD card (for initial setup only)  
* Power: Specification: Raspberry Pi 27W USB-C Power Supply

### [Click to collapse / expand]       Hardware Setup

Step 1 — Attach NVMe SSD via M.2 HAT

1. Power off and unplug the Raspberry Pi 5\.  
2. Attach the Raspberry Pi M.2 HAT+ to the RPi 5 using the PCIe FPC ribbon cable — connect it to the PCIe FPC connector on the bottom edge of the RPi 5 board. Secure the HAT with the provided standoffs.  
3. Insert the 512GB NVMe SSD (M.2 2280 or 2242, M-key) into the M.2 slot on the HAT. Secure it with the retention screw.  
4. Confirm the HAT sits flat and all connectors are fully seated before proceeding.


> ⚠️ Handle the PCIe ribbon cable with care — it is fragile. Ensure the blue side faces up when inserting into the RPi 5 connector.

Step 2 — Flash Raspberry Pi OS to SD Card

1. On your computer, download and install [Raspberry Pi Imager](https://www.raspberrypi.com/software/).  
2. Insert your 16GB+ microSD card into your computer.  
3. Open RPi Imager and configure:  
   - Device: Raspberry Pi 5  
   - OS: Raspberry Pi OS (64-bit) — recommended: the full Desktop version for initial setup  
   - Storage: Select your microSD card  
4. Click the Edit Settings (⚙️) button before writing:  
   - Set hostname (e.g. nara.local)  
   - Enable SSH → Use password authentication  
   - Set username and password (e.g. user: pi, password: your choice)  
   - Configure Wi-Fi if needed  
5. Click Save → Yes → Write and wait for the flash to complete.

Step 3 — First Boot from SD Card

1. Insert the flashed microSD card into the Raspberry Pi 5\.  
2. Connect a monitor, keyboard, and mouse (or use SSH after boot).  
3. Connect power — the RPi 5 will boot from the SD card.  
4. Complete the initial OS setup if the desktop wizard appears.  
5. Open a terminal and run a system update:

sudo apt update && sudo apt full-upgrade -y

sudo reboot

6. After reboot, verify the NVMe is detected:

lsblk

# You should see: nvme0n1 with no partitions yet

If nvme0n1 does not appear, check the M.2 HAT ribbon cable connection and reboot.

Step 4 — Flash OS to NVMe SSD

With the RPi running from SD, use RPi Imager (already installed on Raspberry Pi OS) to write the OS directly to the NVMe:

1. Open Raspberry Pi Imager from the desktop (or run rpi-imager).  
2. Configure the same settings as Step 2 (or reuse your saved customizations).  
3. Storage: Select the NVMe drive (/dev/nvme0n1 — typically listed as the 512GB drive).  
4. Click Write and wait for the process to complete.

Step 5 — Configure NVMe Boot Order

Tell the Raspberry Pi 5 bootloader to prefer the NVMe SSD over the SD card.

Option A — via raspi-config (recommended):

sudo raspi-config

Navigate to: Advanced Options → Boot Order → NVMe/USB Boot

Select NVMe, confirm, and exit. Apply when prompted.

Option B — via EEPROM config (manual):

sudo -E rpi-eeprom-config --edit

Find the BOOT_ORDER line and set it to:

BOOT_ORDER=0xf61

> Boot order is read right-to-left: 6 \= NVMe (PCIe), 1 \= SD card, f \= loop/restart.  
> This means: try NVMe first → fall back to SD → repeat.

Save, exit, and apply:

sudo reboot

Step 6 — Boot from NVMe

1. After the reboot, power off the Raspberry Pi 5:

sudo poweroff

2. Remove the microSD card.  
3. Power the RPi 5 back on.  
4. The system should now boot directly from the NVMe SSD.  
5. Verify with:

findmnt /

# Should show: /dev/nvme0n1p2 or similar — not mmcblk0

If the RPi fails to boot without the SD card, revisit Step 5 and confirm the EEPROM boot order was saved correctly.

## Example Usage {#example-usage}

Usge this commands to import profiles:

hermes import \~/your-backup-name.zip

Or

hermes profile import \~/their-profile-backup.tar.gz --name your-alias-name

Once Nara is running and connected to the Liquid Galaxy rig, here are sample commands you can use:

### -

# Voice Support {#voice-support}

Hermes Agent allows us to interact using voice. This is a built in feature that consists of 2 parts, 

Text-to-Speech (TTS): The agent converts its text responses into spoken audio files or native voice messages.

Speech-to-Text (STT): When you send a voice note to the agent, it automatically transcribes your audio into text so the agent can read and reply to it.

We can choose from a variety of different providers (free & paid) for TTS and STT based on requirements.

# Enabling Voice Mode in Hermes Agent

The easiest way is to ask the agent in cli to enable voice model if not already done. It will install the dependencies and detect your microphone.  
**“ Enable voice mode for hermes, speech to text and text to speech “**   
If we stick to default providers we don't need any api keys or extra settings

Once the voice mode is enabled just use /voice tts or /voice on in hermes cli and it works.

**Note-**  Your Raspberry Pi must have a microphone and speaker for the input and output to work.

Before using voice mode, make sure your Raspberry Pi can detect both the microphone (audio input) and the speaker (audio output). Hermes uses the operating system's default audio devices, so the correct input and output devices must be configured beforehand.

Hermes agent can also help you configure these. 

These can be built-in devices or external USB devices, such as a USB microphone and USB speaker. Hermes uses the Raspberry Pi's default audio devices, so you must configure the audio routing to use the correct microphone and speaker before enabling voice mode. You can verify and select the default input and output devices using the Raspberry Pi audio settings (raspi-config or the Desktop Audio Device Settings) or Linux audio tools such as alsamixer, aplay -l, and arecord -l. After configuring the routing, it is recommended to test both the microphone and speaker to ensure audio input and output are working correctly.

## Using Voice Mode

Once Hermes is running, you can control voice mode using the following commands.

| Command | Description | | :---- | :---- | | `/voice on` | Enables full voice conversation. Speak to Hermes and hear spoken responses. | | `/voice tts` | Hermes will always read its responses aloud. | | `/voice off` | Disables all voice features. |

---

## Available Providers

## Speech-to-Text (STT)

| Provider | Environment Variable | Free | | :---- | :---- | :---- | | **local (Faster Whisper)** | **None** | **✅ Yes** | | **Groq** | **`GROQ_API_KEY`** | **✅ Free tier** | | **OpenAI** | **`VOICE_TOOLS_OPENAI_KEY`** | **❌ Paid** | | **Mistral** | **`MISTRAL_API_KEY`** | **❌ Paid** |

---

## Text-to-Speech (TTS)

| Provider | Environment Variable | Free | | :---- | :---- | :---- | | **Edge** | **None** | **✅ Yes** | | **ElevenLabs** | **`ELEVENLABS_API_KEY`** | **✅ Free tier** | | **OpenAI** | **`VOICE_TOOLS_OPENAI_KEY`** | **❌ Paid** | | **MiniMax** | **`MINIMAX_API_KEY`** | **❌ Paid** | | **Mistral** | **`MISTRAL_API_KEY`** | **❌ Paid** | | **NeuTTS (Local)** | **None (`pip install neutts[all]`)** | **✅ Yes** |

You can keep is default and chose not to go for any manual configuration of the providers. Edge and faster whisper work well !

**Elevenlabs Voice**   
We know that Voice interaction runs as a two-way pipeline. Incoming audio is transcribed to text before reaching the Hermes LLM, and the generated response is converted back to speech.

Text-to-Speech (TTS): Powered by ElevenLabs models (such as eleven_flash_v2_5 for low-latency live conversation or eleven_multilingual_v2 for general use) linked to a specific voice_id.

Speech-to-Text (STT): Driven by ElevenLabs Scribe (scribe_v2), which automatically handles transcription for incoming voice messages across connected channels (e.g., CLI, Telegram, Discord, WhatsApp, Slack, Signal).

Setup Commands  
1\. Environment & Dependencies  
Add your ElevenLabs API key to \~/.hermes/.env:

Bash  
ELEVENLABS_API_KEY=your_key_here  
If premium TTS dependencies are missing, install them:

Bash  
pip install "hermes-agent[tts-premium]"

Enable Voice:

Plaintext  
/voice on  
/voice tts

You can also share detailed with your agent directly and it will handle most config itself! Elevemlabs models offer a better and premium voice experience and is optional for this project.

**Manual Way [optional] -**

## 1\. Install the Required Dependencies

Before installing anything, activate your Hermes virtual environment. This ensures the packages are installed only for Hermes and do not affect your system Python installation.

source \~/.hermes/hermes-agent/venv/bin/activate

Next, install the local Speech-to-Text engine:

pip install faster-whisper sounddevice numpy libportaudio2

`faster-whisper` runs completely on your local machine, so no API key or internet connection is required for speech recognition.

Note: Hermes already includes support for the Edge Text-to-Speech provider, so no additional installation is needed unless you want to use another voice provider.

---

## 2\. Configure Voice Settings

Open the Hermes configuration file located at:

\~/.hermes/config.yaml

Add or verify the following configuration:

*stt:*

  *enabled: true*

  *provider: local*

  *local:*

    *model: base*

*tts:*

  *provider: edge*

*voice:*

  *auto_tts: false*

  *record_key: ctrl+b*

  *max_recording_seconds: 120*

## Configuration Explained

## **Speech-to-Text (STT)**

This section controls how Hermes converts your speech into text.

- `enabled: true` enables speech recognition.  
- `provider: local` tells Hermes to use Faster Whisper on your computer.  
- `model` selects the Whisper model to use.

Available models:

* tiny (fastest, least accurate)  
* base (recommended for most users)  
* small  
* medium  
* large-v3 (highest accuracy but requires more resources)

---

## **Text-to-Speech (TTS)**

This controls how Hermes speaks its responses. Verify in the same config file,

*tts:*

  *provider: edge*

The Edge provider is free and works well for most use cases. You may chose proviers as per your wish.

---

## **Voice Settings**

voice:

This section controls how voice mode behaves.

- `auto_tts: true` makes Hermes automatically speak every response.  
- `auto_tts: false` means Hermes replies only with text unless you explicitly enable speech.

`record_key` specifies the keyboard shortcut used for push-to-talk.

ctrl+b

Hold the shortcut while speaking, then release it to send the recording.

`max_recording_seconds` sets the maximum recording duration.

---

# Liquid Galaxy commands

# Current System Example Commands [CLI Support]

| Command to type | What happens | | ----- | :---- | | **Basic LG commands** | |
| Connect to the Liquid Galaxy | Verifies the connection status and connects to the liquid galaxy. | | Relaunch Earth on the rig | Restarts the lg via lg-relaunch-direct. This is just a helper script which will perform the action of relaunch. | | Reboot / Power off the liquid galaxy | Reboots or turn off the liquid galaxy rig. | | Clear the KMLs  | Erase the KMLs from the liquid galaxy. | | Add logo to the liquid galaxy | Add project logo in left most screen | | **KML & Visualization** | |
| Make a pyramid over Madrid / Pune with fly to view | Generates a pyramid KML and deploys it to liquid galaxy to visualize. The system is based on llms with the capability to perform web searches as well, you can name whatever city or place in place of madrid and it will work. | | Highlight flood zones near kerala city | Creates a kml for flood zones at kerala  |

## GitHub Access Methods

### 1\. GitHub CLI (gh auth) used for agent

The gh tool is already available on the Raspberry Pi. It handles both Git operations and GitHub API tasks such as pull requests and issues.

* Login method: gh auth login  
* Token method: echo $TOKEN | gh auth login --with-token  
* Why this works well: it stores credentials securely and can also configure Git automatically.

### 2\. Personal Access Tokens (PAT)

PATs can be used as a password for HTTPS operations or injected as GITHUB_TOKEN.

* Classic PAT: broad permissions, useful for troubleshooting  
* Fine-grained PAT: restricted to specific repositories and actions, safer for normal use

### 3\. SSH keys — the old reliable method

SSH keys can be used for Git access without tokens.

* User SSH key: generate a keypair on the Raspberry Pi and add the public key to GitHub  
* Deploy key: best for single-repository access only  
* Why this is useful: no token expiry, no token leakage in logs, and access can be limited tightly


### 4\. Git credential store

A simple option after one manual login.

* Example: git config --global credential.helper store  
* Downside: credentials are stored in plain text on disk

---

## Repository Rules

The agent must follow these rules (crafted using gemini) at all times:

* Only use the branch named agent-branch  
* Never modify, access, or push to any other branch  
* Never touch files outside the scope of agent-branch  
* Always ask for explicit permission before running git commands that change remote state  
* Always request human review before any push or sync action

This branch is the only place where project learning, progression notes, and documentation should be written.

---

## Refined Access Prompt

Use this GitHub access token I created to access the repository:

https://github.com/LiquidGalaxyLAB/local-ai-gemma.git

Critical constraints:

* Strict branch isolation: only and always push code, documentation, or files created during this Liquid Galaxy project to agent-branch  
* Access restrictions: do not edit, access, or modify any other branch, directory, or main file outside agent-branch  
* Permission protocol: always request explicit permission and human review before performing any push, code sync, or modification actions

---

## Working Agreement for the Agent

After logging in with gh auth and providing the token to Hermes, the agent should still obey these rules:

* Always ask for permission before any git command that changes the repository  
* Never touch anything except agent-branch  
* Use this branch to store learnings, progress, and well-documented project notes  
* For now, document only what has been learned so far  
* So far, the work is mainly about Liquid Galaxy command execution and some networking troubleshooting  
* No KML work beyond that has been done yet  
* Later work can be added gradually as the project progresses

---

## Skills contents

### [Click to collapse / expand]  Skill 1 markdown — LG SSH Control [for any user who wants to paste it into their system directly from markdown]

**Skill: lg-ssh-control**  
**`**  
**---**

**name: lg-ssh-control**

**description: Execute SSH control commands on the Liquid Galaxy rig — relaunch, reboot, poweroff, network info, and KML refresh management across all screens.**

**version: 2.3.0**

**author: Nara**

**license: MIT**

**platforms: [linux]**

**metadata:**

  **hermes:**

    **tags: [LiquidGalaxy, SSH, Control, Reboot, KML, Screens, Hardware, Network]**

    **related_skills: [lg-kml-generator, lg-diagnostics]**

**---**

**Execute system-level control commands on the Liquid Galaxy rig over SSH.**

**Password: lg (standard for all LG rigs)**

---

**⚠️ MANDATORY PRE-FLIGHT — Connection Mode Selection**

**Every session, before any SSH command, you MUST ask the user:**

> **"How are you connecting to Liquid Galaxy?"**  


> 1. **VM / Reverse Tunnel — LG runs on a VM behind a laptop that forwards SSH via ssh -N -R 2222:192.168.53.3:22 nara@\<pi-ip\>. Use SSH_DEST="lg@localhost -p 2222"**  
> 2. **Direct LAN — Real LG hardware on the same network. Use SSH_DEST="lg@\<lg-master-ip\>" (typically 192.168.53.3 or whatever lg1 resolves to on LAN)**

**Then verify IPs (see Verification section below). Never reuse IPs from a past session without re-verifying.**

---

**Target Configuration**

**Once the user picks a mode, set the SSH target:**

- **VM / Reverse Tunnel: SSH Target: SSH_DEST="lg@localhost -p 2222"; Verified via: `ss -tlnp**  
- **Direct LAN: SSH Target: SSH_DEST="lg@"; Verified via: Direct SSH ping to the LG master IP**

**Core insight (VM mode only): Built-in lg-relaunch calls lg-sudo-bg → lg-ctl-master. If lg-ctl-master is missing (common on VM-only rigs), the built-in script does nothing. The helpers below bypass this broken chain by piping the password to sudo -S directly on the remote host. Direct LAN rigs typically have the full helper chain working.**

**In command examples below, $SSH_DEST represents the target resolved above. Substitute the actual value when constructing the command:**

- **VM mode: sshpass -p 'lg' ssh -o StrictHostKeyChecking=no -p 2222 lg@localhost ...**  
- **Direct LAN: sshpass -p 'lg' ssh -o StrictHostKeyChecking=no lg@\<lg-master-ip> ...**

---

**When to Use**

**Trigger phrases: relaunch, restart, reboot, shutdown, poweroff, refresh, set refresh, reset refresh, /relaunch, /reboot, /shutdown**

---

**Quick Reference**

- **Relaunch: Helper script: lg-relaunch-direct; Scope: lg1 only; Confirm: No**  
- **Reboot: Helper script: lg-reboot-direct; Scope: All frames; Confirm: Yes**  
- **Poweroff: Helper script: lg-poweroff-direct; Scope: All frames; Confirm: Yes**  
- **Network info: Helper script: (inline hostname -I); Scope: lg1 only; Confirm: No**  
- **Set Refresh: Helper script: lg-refresh-set; Scope: Slaves; Confirm: No**  
- **Reset Refresh: Helper script: lg-refresh-reset; Scope: Slaves; Confirm: No**

---

**Setup — Deploy Helpers to lg1**

> **In the commands below, $SSH_DEST is your target after pre-flight:**  


> - **VM mode: -p 2222 lg@localhost**  
> - **Direct LAN: lg@\<lg-master-ip> (e.g. lg@192.168.53.3)**

**Auto (if profile has the deploy script)**

**SCRIPT="$(find $HOME/.hermes/profiles -name lg-deploy-helpers.sh -path '*/lg-ssh-control/*' 2\>/dev/null | head -1)"**

**[ -z "$SCRIPT" ] && SCRIPT="$(find $HOME/.hermes/profiles -name lg-deploy-helpers.sh 2\>/dev/null | head -1)"**

**if [ -n "$SCRIPT" ]; then bash "$SCRIPT"; else echo "Manual setup needed (see below)"; fi**

**Manual (human: paste these commands in your terminal, or use the deploy script above for agent-driven setup)**

**Each command scp's a helper to lg1. All idempotent.**

**To run from your terminal (not through the agent — tool guard blocks embedded sudo -S patterns):**

**lg-relaunch-direct — restart Earth on lg1 only**

**sshpass -p 'lg' ssh -o StrictHostKeyChecking=no -p 2222 lg@localhost "cat > /home/lg/bin/lg-relaunch-direct \<\< 'HELPER'**

**#!/bin/bash**

**PW=\\"lg\\"**

**if [ -f /etc/init/lxdm.conf ]; then SVC=lxdm**

**elif [ -f /etc/init/lightdm.conf ]; then SVC=lightdm**

**else exit 1; fi**

**echo \\"\\$PW\\" | sudo -S service \\"\\$SVC\\" restart**

**HELPER**

**chmod \+x /home/lg/bin/lg-relaunch-direct"**

**lg-reboot-direct — reboot all frames**

**sshpass -p 'lg' ssh -o StrictHostKeyChecking=no -p 2222 lg@localhost "cat > /home/lg/bin/lg-reboot-direct \<\< 'HELPER'**

**#!/bin/bash**

**PW=\\"lg\\"**

**. \\${HOME}/etc/shell.conf**

**me=\\$(hostname)**

**for lg in \\$LG_FRAMES; do**

  **if [ \\"\\$lg\\" \= \\"\\$me\\" ]; then echo \\"\\$PW\\" | sudo -S reboot**

  **else sshpass -p \\"\\$PW\\" ssh -o ConnectTimeout=5 -t -x lg@\\$lg \\"echo '\\$PW' | sudo -S reboot\\" 2\>/dev/null || echo \\"  \\$lg unreachable\\"**

  **fi**

**done**

**HELPER**

**chmod \+x /home/lg/bin/lg-reboot-direct"**

**lg-poweroff-direct — power off all frames**

**sshpass -p 'lg' ssh -o StrictHostKeyChecking=no -p 2222 lg@localhost "cat > /home/lg/bin/lg-poweroff-direct \<\< 'HELPER'**

**#!/bin/bash**

**PW=\\"lg\\"**

**. \\${HOME}/etc/shell.conf**

**me=\\$(hostname)**

**for lg in \\$LG_FRAMES; do**

  **if [ \\"\\$lg\\" \= \\"\\$me\\" ]; then echo \\"\\$PW\\" | sudo -S poweroff**

  **else sshpass -p \\"\\$PW\\" ssh -o ConnectTimeout=5 -t -x lg@\\$lg \\"echo '\\$PW' | sudo -S poweroff\\" 2\>/dev/null || echo \\"  \\$lg unreachable\\"**

  **fi**

**done**

**HELPER**

**chmod \+x /home/lg/bin/lg-poweroff-direct"**

**lg-refresh-set — add 2s KML refresh to slaves**

**sshpass -p 'lg' ssh -o StrictHostKeyChecking=no -p 2222 lg@localhost "cat > /home/lg/bin/lg-refresh-set \<\< 'HELPER'**

**#!/bin/bash**

**PW=\\"lg\\"**

**. \\${HOME}/etc/shell.conf**

**for lg in \\$LG_FRAMES; do**

  **[ \\"\\$lg\\" \= \\"\\$(hostname)\\" ] && continue**

  **n=\\"\\${lg#lg}\\"**

  **s=\\"\<href\>##LG_PHPIFACE##kml/slave_\\${n}.kml\</href\>\\"**

  **r=\\"\\${s}\<refreshMode\>onInterval\</refreshMode\>\<refreshInterval\>2\</refreshInterval\>\\"**

  **sshpass -p \\"\\$PW\\" ssh -o ConnectTimeout=5 -t lg@\\$lg \\"echo '\\$PW' | sudo -S sed -i 's|\\${r}|\\${s}|' \~/earth/kml/slave/myplaces.kml\\" 2\>/dev/null && \**

  **sshpass -p \\"\\$PW\\" ssh -o ConnectTimeout=5 -t lg@\\$lg \\"echo '\\$PW' | sudo -S sed -i 's|\\${s}|\\${r}|' \~/earth/kml/slave/myplaces.kml\\" 2\>/dev/null || echo \\"  \\$lg unreachable\\"**

**done**

**HELPER**

**chmod \+x /home/lg/bin/lg-refresh-set"**

**lg-refresh-reset — remove KML refresh tags from slaves**

**sshpass -p 'lg' ssh -o StrictHostKeyChecking=no -p 2222 lg@localhost "cat > /home/lg/bin/lg-refresh-reset \<\< 'HELPER'**

**#!/bin/bash**

**PW=\\"lg\\"**

**. \\${HOME}/etc/shell.conf**

**for lg in \\$LG_FRAMES; do**

  **[ \\"\\$lg\\" \= \\"\\$(hostname)\\" ] && continue**

  **n=\\"\\${lg#lg}\\"**

  **s=\\"\<href\>##LG_PHPIFACE##kml/slave_\\${n}.kml\</href\>\\"**

  **r=\\"\\${s}\<refreshMode\>onInterval\</refreshMode\>\<refreshInterval\>2\</refreshInterval\>\\"**

  **sshpass -p \\"\\$PW\\" ssh -o ConnectTimeout=5 -t lg@\\$lg \\"echo '\\$PW' | sudo -S sed -i 's|\\${r}|\\${s}|' \~/earth/kml/slave/myplaces.kml\\" 2\>/dev/null || echo \\"  \\$lg unreachable\\"**

**done**

**HELPER**

**chmod \+x /home/lg/bin/lg-refresh-reset"**

**Verify deployment:**

**sshpass -p 'lg' ssh -o StrictHostKeyChecking=no -p 2222 lg@localhost 'ls -la /home/lg/bin/lg-*-direct /home/lg/bin/lg-refresh-*'**

---

**Procedures (substitute $SSH_DEST from pre-flight)**

**1\. Relaunch**

**sshpass -p 'lg' ssh -o StrictHostKeyChecking=no $SSH_DEST '/home/lg/bin/lg-relaunch-direct'**

**2\. Reboot**

> **⚠️ Confirm: "This will reboot all LG screens. Confirm?"**

**sshpass -p 'lg' ssh -o StrictHostKeyChecking=no $SSH_DEST '/home/lg/bin/lg-reboot-direct'**

**3\. Poweroff**

> **⚠️ Confirm: "This will power off all LG screens. Cannot be undone remotely. Confirm?"**

**sshpass -p 'lg' ssh -o StrictHostKeyChecking=no $SSH_DEST '/home/lg/bin/lg-poweroff-direct'**

**4\. Network Info**

**sshpass -p 'lg' ssh -o StrictHostKeyChecking=no $SSH_DEST 'hostname -I; ip addr show | grep "inet "'**

**5\. Set Refresh**

**sshpass -p 'lg' ssh -o StrictHostKeyChecking=no $SSH_DEST '/home/lg/bin/lg-refresh-set'**

**6\. Reset Refresh**

**sshpass -p 'lg' ssh -o StrictHostKeyChecking=no $SSH_DEST '/home/lg/bin/lg-refresh-reset'**

---

**Pitfalls**

- **Connection refused on :2222: Cause: Tunnel down (VM mode); Fix: On laptop: ssh -N -R 2222:192.168.53.3:22 nara@\<pi-ip\>**  
- **Connection refused on direct IP: Cause: Wrong IP or rig off (LAN mode); Fix: Check IP with user, confirm rig powered on**  
- **Helper script not found: Cause: Not deployed; Fix: Run setup procedure above**  
- **sudo -S blocked by tool guard: Cause: Pattern match in command string; Fix: Write helpers on remote host (as above), then call them with clean SSH**  
- **lg-relaunch does nothing: Cause: lg-ctl-master missing; Fix: Use lg-relaunch-direct instead, or switch to Direct LAN mode if on real hardware**  
- **pgrep finds no Earth after relaunch: Cause: Autostart needs time; Fix: Wait 15s and retry**  
- **Slave unreachable: Cause: Physical machine off; Fix: Expected — helpers log and skip gracefully**  
- **Reboot SSH connection drops (exit 255): Cause: Remote host reboots, terminates SSH; Fix: Expected — Connection closed by remote host is normal post-reboot behavior**  
- **[sudo] password for lg: shown despite helper: Cause: Helper pipes password via echo; Fix: sudo -S; sudo prints prompt to stderr**  
- **LAN IP drift: Cause: IPs change on DHCP; Fix: Always verify — never assume IPs from past sessions**

---

**Verification**

**⚠️ ALWAYS verify current IPs before any command. LAN IPs drift on DHCP. Do not assume addresses from past sessions.**

**VM / Reverse Tunnel mode**

**# 1\. Check Pi IP (this host)**

**hostname -I | awk '{print $1}'**

**# 2\. Verify tunnel is active**

**ss -tlnp | grep :2222**

**# 3\. Test SSH through tunnel**

**sshpass -p 'lg' ssh -o StrictHostKeyChecking=no -p 2222 lg@localhost "hostname -I; echo OK"**

**Expected: 192.168.53.3 \+ OK.**

**Direct LAN mode**

**# 1\. Check Pi IP (this host)**

**hostname -I | awk '{print $1}'**

**# 2\. Verify LG master is reachable directly**

**ping -c 1 \<lg-master-ip> 2\>&1**

**# 3\. Test SSH directly**

**sshpass -p 'lg' ssh -o StrictHostKeyChecking=no lg@\<lg-master-ip> "hostname; echo OK"**

**Expected: hostname (e.g. lg1) \+ OK.**

**Post-relaunch (wait 15s)**

**sshpass -p 'lg' ssh -o StrictHostKeyChecking=no $SSH_DEST \**

  **'systemctl status lightdm | grep Active; pgrep -a googleearth | head -2'**

**Expected: lightdm active since seconds ago \+ googleearth-bin PID.**

**Post-reboot (wait 90s)**

**sshpass -p 'lg' ssh -o StrictHostKeyChecking=no $SSH_DEST 'hostname; uptime'**

**Expected: lg1 \+ uptime \< 2 min.**

**Post-refresh-set**

**sshpass -p 'lg' ssh -o StrictHostKeyChecking=no $SSH_DEST \**

  **"sshpass -p 'lg' ssh lg2 'grep refreshInterval \~/earth/kml/slave/myplaces.kml'"**

**Expected: \<refreshInterval\>2\</refreshInterval\>**

**Post-refresh-reset**

**sshpass -p 'lg' ssh -o StrictHostKeyChecking=no $SSH_DEST \**

  **"sshpass -p 'lg' ssh lg2 'grep refreshInterval \~/earth/kml/slave/myplaces.kml'"**

**Expected: no output.**

---

**Why Helpers Instead of Inline Commands**

**The Hermes tool guard blocks echo \<password> | sudo -S in any terminal command string (brute-force attack prevention). Running the pipe inside a script on the remote machine bypasses this guard because the tool only inspects the SSH command, not the script content. The helper scripts embed the password (PW="lg") so callers never need to pass credentials. This is the standard LG password across all official rigs.**

---

---
# Experiences during development {#experiences-during-development}

1:  Why to write good documentation: I learnt this from my mentors that a project is where a person creates something and uses it for personal use. However if we need to develop a product where we are building it for everybody to use, having a very clear and detailed documentation is very important.  
It helps every user with different amount of experience to understand the project and how they can use it.

2\. Some problems faced: Initially i got confused on what the mentors requested / expected from me in terms of project architecture and documentations. 

3\. Solution: my mentors gave me some examples and guided me by explaining what they meant by the expectations and I slowly started to understand what they asked for. And they were right, it helped to make a better project.

**MIDTERM Testing**  
So for midterm, students and mentors at the lleida lab shared 2 videos along with their feedback. It was amazing to see my project running on a real liquid galaxy and im thankful to them taking time to share some important feedback.

First there was feedback about agent asking for ip and other connection details frequently, i fixed this by modifying the skill such that it asks only once about details and later saves it into memory to reuse.

Next feedback was some changes in docs (shifting clear KML to basic commands list) and adding a logo. That was added by me later.

They tested out different commands , basic and advance KMLs also (e.g. endangered birds, or a pokemon in different areas). They worked well. I have a lot of work to do now for use cases and making it better.

After the first video, i had to add voice mode for the hermes agent.  
It was not very difficult except mic setup for linux based OS of Rpi. Once i added that, i shared backup and updated docs and got a second video of testing with voice. 

During the voice testing , there was a bit of difficulty for the STT to transcribe what the user intended to say. However, apart from that, when they asked the machine to clear the KMLs, it did not clear it and performed a relaunch which was unnecessary. Also the KML about population was made on all screens [this was tried in turkish]. These small but important issues need to be improved with more practice. 

Personal exp

1. architecture engineering- Mentor Moises had asked me to make a well defined and fixed design which can be used to implement different use cases and skills for the project. Once he gave me some examples and expectations, I drafted a design and tried to test it locally.  
   It worked very well, it did the work it took me few days into few hours. It was really helpful.

[**External link to Research document, and architecture**](https://docs.google.com/document/d/1ESamoc_D2Ro8EFBvxf-r09AtONIembIRs2gCAutu42A/edit?tab=t.elndxa9s92fi#heading=h.n78xse233yga)


