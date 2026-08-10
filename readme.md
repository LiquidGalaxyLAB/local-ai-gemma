1|# Local AI with Gemma by Google (Nara)
2|
3|<div align="center">
4|  <img src="./assets/img2.png" alt="Liquid Galaxy logo" width="280" />
5|  <br />
6|  <strong>350 Hr — Local AI with Gemma by Google</strong>
7|  <br />
8|  <em>GSoC 2026 · Liquid Galaxy Lab · Project Documentation</em>
9|</div>
10|
11|---
12|
13|**Nara** is the onboard AI assistant for Liquid Galaxy. Built on the [Hermes Agent](https://hermes-agent.nousresearch.com/docs/) framework, it runs on a local machine (Raspberry Pi recommended), controls the LG rig over SSH, and generates KML visualizations, guided tours, and live data layers — fully local or hybrid cloud inference.
14|
15|| | |
16|| :--- | :--- |
17|| **Project** | Nara — onboard AI for Liquid Galaxy |
18|| **Framework** | [Hermes Agent](https://hermes-agent.nousresearch.com/) (Nous Research) |
19|| **Contributors** | Harsh Mehta (mentee) |
20|| **Mentors** | Andreu Ibanez, Moises Martinez |
21|| **Backup / profiles** | [Google Drive folder](https://drive.google.com/drive/folders/1mQyJYMV7bvj-cq7geYF7AcXGROvqjj-z) |
22|
23|### How to use this documentation
24|
25|This documentation covers important concepts, how the project works, how a user can replicate it, GSoC progress, and key references. It is intended for contributors, mentors, and users who want to learn how the system works, deploy it on their own hardware, or build new capabilities on top of it.
26|
27|The guide starts with goals and architecture, then walks through installation, configuration, and profile restoration before covering modular skills, practical use cases, and development experience. Whether you are using Nara on a Raspberry Pi with a Liquid Galaxy rig, experimenting with Hermes, or contributing new features, following the documentation in order provides the background, setup steps, and references you need.
28|
29|**Want to start right away?** Jump to [Installation](#installation).
30|
31|---
32|
33|## Table of Contents
34|
35|1. [About Me & Acknowledgements](#about-me--acknowledgements)
36|2. [About the Project](#about-the-project)
37|3. [Skill Architecture Design](#skill-architecture-design)
38|4. [Planned Tasks](#planned-tasks)
39|5. [What Nara Can Do](#what-nara-can-do)
40|6. [Example Use Cases (What can you do with current version of project)](#example-use-cases-what-can-you-do-with-current-version-of-project)
41|7. [Quick Start](#quick-start)
42|8. [Hermes Agent Setup](#hermes-agent-setup)
43|9. [Installation](#installation)
44|10. [Restoring the Liquid Galaxy Profile](#restoring-the-liquid-galaxy-profile)
45|11. [Docker & WSL Setup](#docker--wsl-setup)
46|12. [SOUL.md (Nara personality)](#soulmd-nara-personality)
47|13. [Hermes Agent Architecture](#hermes-agent-architecture)
48|14. [LLM Wiki & Google OKF](#llm-wiki--google-okf)
49|15. [System Architecture](#system-architecture)
50|16. [Tech Stack](#tech-stack)
51|17. [Hardware](#hardware)
52|18. [Hardware Setup](#hardware-setup)
53|19. [Example Usage](#example-usage)
54|20. [Voice Support](#voice-support)
55|21. [GitHub Access for the Agent](#github-access-for-the-agent)
56|22. [Current Status](#current-status)
57|23. [Experiences During Development](#experiences-during-development)
58|24. [References](#references)
59|
60|---
61|
62|## About Me & Acknowledgements
63|
64|I'm **Harsh Mehta**, a curious engineering student from Pune with a keen interest in how real-world production systems work. Grateful to Liquid Galaxy and Google Summer of Code for this opportunity to learn and to ship work that others can actually use in the lab.
65|
66|Many thanks to **Trang, Fabricio, Oriol, and Josep** at the Liquid Galaxy Lab in Lleida for testing and sharing valuable feedback on the project.
67|
68|---
69|
70|## About the Project
71|
72|This project builds **Nara** — an AI assistant server that lives on the Liquid Galaxy rig's local network. Nara runs on a Raspberry Pi 5 connected to the rig via SSH, accepts commands through the CLI (and optionally messaging gateways), and autonomously generates and pushes content such as KML visualizations, guided tours, real-time data maps, and more directly to the Liquid Galaxy screens.
73|
74|The system is built as a Hermes agent with a **modular skill architecture**, meaning capabilities can be added, enabled, or disabled independently without touching the core runtime. It supports both fully local AI inference (offline, self-contained) and a hybrid mode that optionally routes complex tasks to remote model APIs — balancing hardware limits with response quality.
75|
76|The goal is a stable, easy-to-extend assistant that any LG user, mentor, or contributor can run in the lab or deploy from a backup profile.
77|
78|---
79|
80|## Skill Architecture Design
81|
82|The project follows a standardized, modular skill architecture to make Liquid Galaxy capabilities easy to develop, maintain, and extend. Rather than embedding logic directly into the agent, each capability is implemented as an independent skill with a single responsibility, allowing new features to be added without modifying the core runtime.
83|
84|The architecture is organized into **six logical layers**:
85|
86|| Layer | Role |
87|| :--- | :--- |
88|| **User Layer** | Accepts requests from the CLI, Web UI, voice interface, Telegram, or scheduled jobs |
89|| **Hermes Runtime** | Acts as the central orchestrator, selecting the appropriate skills, managing conversations, and maintaining long-term memory |
90|| **Skill Layer** | Contains independent, reusable skills such as LG SSH Control and KML Generation, with support for future plug-in skills |
91|| **Knowledge Layer** | Stores shared templates, scripts, documentation, references, troubleshooting guides, and best practices that can be reused across multiple skills instead of duplicating information in prompts |
92|| **Learning Layer** | Captures reusable workflows, successful procedures, and troubleshooting knowledge to continuously improve the agent over time |
93|| **Deployment Layer** | Provides a common deployment mechanism for all skills, enabling KML uploads, SSH command execution, visualization updates, and Liquid Galaxy administration through the master node |
94|
95|### Skill consistency
96|
97|To ensure consistency, every skill follows the same directory structure and documentation format, including metadata, trigger conditions, procedures, verification steps, references, templates, scripts, and examples. Skills remain self-contained, while shared utilities are placed in common directories for reuse.
98|
99|In this repository that maps to:
100|
101|```text
102|skills/
103|├── <skill-name>.md              # Skill doc (metadata, procedures, examples)
104|├── references/<skill-name>/     # Shared troubleshooting & architecture notes
105|├── scripts/<skill-name>/        # Deployable helpers / generators
106|└── templates/<skill-name>/      # Reusable KML / config templates
107|```
108|
109|Full catalog: [SKILLS.md](SKILLS.md).
110|
111|### Workflow for new functionality
112|
113|A standard workflow is followed when introducing new functionality:
114|
115|1. **Determine** whether the request extends an existing skill or requires a new one.  
116|2. **Create** the skill using the standard template.  
117|3. **Register** the skill so Hermes can discover it automatically.  
118|4. **Validate** the complete workflow through real execution on the Liquid Galaxy rig.  
119|5. **Preserve** reusable knowledge through Hermes' learning system and update the associated documentation.
120|
121|### Learning strategy
122|
123|The learning strategy distinguishes between three types of knowledge:
124|
125|| Type | Where it lives | Purpose |
126|| :--- | :--- | :--- |
127|| **Durable facts** | Persistent memory | Stable facts stored for reuse (IPs, rig constraints, preferences) |
128|| **Procedural knowledge** | Reusable skills and workflows | How to perform tasks correctly across sessions |
129|| **Session history** | Conversational / SQLite history | Context and debugging within a conversation |
130|
131|This standardized architecture makes the project scalable, encourages community contributions, minimizes duplicated logic, and enables new Liquid Galaxy use cases to be added with minimal changes to the existing system.
132|
133|---
134|
135|## Planned Tasks
136|
137|| # | Task | Result |
138|| :-: | :--- | :--- |
139|| 1 | Work on docs | ✅ Done |
140|| 2 | Test Docker and WSL-based setups | ✅ WSL and Docker setup works |
141|| 3 | Test architecture & advanced use cases (not only single-API demos) | Architecture works well; virtual LG setup use case; ≥2 data sources |
142|| 4 | Build a virtual LG | Added to GitHub and docs |
143|| 5 | PPT for 13 Aug | 🔄 Ongoing |
144|| 6 | 27 Jul — update docs | ✅ Done |
145|
146|Full skill catalog: **[SKILLS.md](SKILLS.md)** · every skill is a flat file under [`skills/<name>.md`](skills/).
147|
148|---
149|
150|## What Nara Can Do
151|
152|- Control the Liquid Galaxy rig over SSH (relaunch, reboot, shutdown, clear KMLs)
153|- Generate and deploy KMLs for placemarks, overlays, tours, and camera paths
154|- Visualize live or historic data layers (weather, aviation, disasters, maritime, energy)
155|- Provide educator-focused flows (geography, history) with narrated tours
156|- Backup & restore a complete Hermes profile for quick deployment
157|
158|### Use cases — planned order
159|
160|- **LG command execution** — SSH control (relaunch, reboot, poweroff)
161|- **Weather monitoring** — fetch live weather and visualize via KML
162|- **News & geopolitical visualization** — live event mapping on LG
163|- **Geography educator** — teach geography concepts with real-world examples and KMLs
164|- **History educator** — show how historical events (e.g. wars) unfolded
165|- **Natural disaster command center** — earthquakes, wildfires, weather alerts, climate anomalies, displacement flows
166|- **Maritime domain awareness** — AIS density, trade routes, chokepoints, live tankers, cable advisories
167|- **Energy & infrastructure** — pipelines, energy infrastructure, fuel shortages, renewables, mining
168|- **Live aviation watch** — military flights, delays, NOTAM rings, airport status
169|- **Cyber / undersea infrastructure** — undersea cables, internet outages, GPS jamming, cyber threats
170|- **Supply chain & trade flows** — trade routes, chokepoints, commodity ports, tanker positions
171|- **Economic markets** — Finnhub and FRED for financial trends, equities, and indicators
172|- **Armed conflicts** — ACLED and UCDP for political violence and warfare mapping
173|
174|---
175|
176|## Example Use Cases (What can you do with current version of project)
177|
178|| Skill name | Input Examples | Prompt [added to input] | Comments | Expected Output | Link to SKILL.md |
179|| ----- | ----- | ----- | ----- | ----- | ----- |
| lg-ssh-control✅ | Hey Nara, connect to the LG rig" "The rig froze mid-tour, can you reboot the rig ?" "Clear every KML that's currently loaded and power the whole rig down, we're done with the lab work for today" | User command + SSH credentials + LG IP/port + frame count and lg-ssh-control SKILL.md | SSHes into `lg1`, executes control commands (relaunch/reboot/poweroff/refresh), deploys helpers rig | Agent confirms connection and reports actions (relaunch, reboot, clear KMLs, poweroff); master screen shows updated state | https://github.com/LiquidGalaxyLAB/local-ai-gemma/blob/main/skills/lg-ssh-control.md |
| lg-use-cases✅ | Hey Nara, I'm a new student and I've never used this rig before, what exactly can this assistant do for me? "Can you walk me through every use case you support so I know what to demo to visitors this weekend?" "Give me a quick tour of your capabilities, I want to know which skills work offline and which need internet" | User query + reference to all developed use cases + layer stacks + camera patterns | Acts as a guided user manual referencing available skills, offline vs online modes, and demo camera patterns | Lists available use cases (SA Wall, Maritime, Disaster, Energy, Aviation, etc.) and explains their behaviours and dependencies | https://github.com/LiquidGalaxyLAB/local-ai-gemma/blob/main/skills/lg-use-cases.md |
| geography-educator✅ | "Teach me about the International Date Line and show it on the rig"; "Show the India monsoon patterns on LG"; "Explain the Turkey earthquake and visualize the fault lines" | Topic name + pre-built KML generator + region polygon data + TTS script and skill.md | Fetches concepts, builds polygons and explanatory overlays, and prepares a TTS narration | Generates educational KML with reference lines, 3D zones, labeled points; deploys with right-screen panel and voiceover | https://github.com/LiquidGalaxyLAB/local-ai-gemma/blob/main/skills/geography-educator.md |
| armed-conflicts✅ | "Show me all the global conflicts you're tracking right now"; "Where are the active wars today, and how severe are they?"; "Put the armed conflicts watch on the rig and give me a guided tour with narration" | Static conflict zone data (10 zones) + news feeds + visual rules per zone | Produces dynamic KMLs per zone (front arrows, siege rings, displacement arrows, faction markers, wave spreads); camera tours + per-zone TTS | Example visuals: Ukraine (3D column + front arrow), Gaza (4 siege rings + damage dots). Tours across 10 zones with narration | https://github.com/LiquidGalaxyLAB/local-ai-gemma/blob/main/skills/armed-conflicts.md |
| weather-monitor✅ | "What's the weather like in Pune right now?"; "Show Mumbai's temperature and wind in 3D"; "Will it be a good day to visit Madrid tomorrow?" | City name + lat/lon + wttr.in (or similar) API data | Fetches live weather, builds 3D temp columns, wind arrows and icons, presents a right-screen summary with TTS | KMLs reflect temperature (red=hot, blue=cool), wind vectors, and a spoken summary | https://github.com/LiquidGalaxyLAB/local-ai-gemma/blob/main/skills/weather-monitor.md |
| natural-disaster✅ | "Show me earthquakes in Japan right now"; "Any wildfires in Spain I should know about?" | USGS GeoJSON + NASA EONET + NOAA NWS + region input | Fetches live events, generates 3D colored columns, auto-fly camera, and TTS summary | Spoken summary and KMLs: e.g. "12 earthquakes, 3 wildfires, 2 weather alerts" with map overlays | https://github.com/LiquidGalaxyLAB/local-ai-gemma/blob/main/skills/natural-disaster.md |
| Live Aviation✅ | "Show me all flights currently over Germany"; "What does air traffic over Europe look like now?" | OpenSky Network API + region input + airport config (35 airports default) | Fetches aircraft, plots heading-rotated icons at altitude, adds airport markers and a dashboard | Live aircraft markers with labels and an airport activity panel + TTS | https://github.com/LiquidGalaxyLAB/local-ai-gemma/blob/main/skills/live-aviation.md |
| history-educator✅ | "Tell me about WWII"; "Teach me about the Roman Empire"; "Visualize a Mongol conquest"; "What happened during the partition of India?" | Region / event / time period + web search for references | Builds phased visual narratives with territory polygons, advance arrows, battle markers, and narration | KML timelines with camera flythroughs and a parchment-style right-screen balloon with TTS | https://github.com/LiquidGalaxyLAB/local-ai-gemma/blob/main/skills/history-educator.md |
| maritime-awareness✅ | "Show undersea cables coming to India"; "Show live tankers in the Red Sea"; "Visualize trade routes near Europe" | AISStream.io, NGA MSI, Telegeography, and other sources | Extracts region, fetches live/reference data, builds multi-layer colored KMLs and a maritime balloon | Colored route/cable lines, vessel markers, and contextual balloon info on the rightmost screen | https://github.com/LiquidGalaxyLAB/local-ai-gemma/blob/main/skills/maritime-awareness.md |
| energy-monitor✅ | "Where are major oil fields near Russia?"; "Any fuel shortages right now?"; "Show renewable installations in the Middle East"; "Where are the biggest solar farms?" | EIA, GIE AGSI, IEA, World Bank, Yahoo Finance and others | Fetches energy datasets, composes multi-layer KMLs, presents an energy dashboard balloon | Pipelines, solar polygons, 3D columns for resources, and shortage polygons; auto-refresh without relaunch | https://github.com/LiquidGalaxyLAB/local-ai-gemma/blob/main/skills/energy-monitor.md |
| cyber-infrastructure✅ | "Is there GPS jamming anywhere?"; "Are there any BGP hijacks today?"; "Show DDoS attacks or internet disruptions" | Cloudflare Radar, gpsjam.org, OpenBGP streams and other feeds | Aggregates feeds into visual KML layers for jamming zones, hijack arcs, and IXP markers | Visuals: red extruded shutdowns, GPS jamming zones, BGP arcs between AS endpoints; dark-themed right-panel balloon | https://github.com/LiquidGalaxyLAB/local-ai-gemma/blob/main/skills/cyber-infrastructure.md |
| economic-markets✅ | "What's the S&P doing today in India?"; "How is inflation looking globally?"; "Which economies are in recession?" | Finnhub, FRED, Yahoo Finance, Alpha Vantage, World Bank open data | Fetches market & macro data and generates interactive KML heatmaps and indicator overlays | Region-colored market columns, trend balloons, and a summary panel with economic indicators | https://github.com/LiquidGalaxyLAB/local-ai-gemma/blob/main/skills/economic-markets.md |
| animal-migrations✅ | "Show monarch butterfly migration"; "Track the wildebeest migration"; "Where do humpback whales travel?" | Movebank, IUCN, NOAA CDO + seasonal checks | Fetches species tracks, checks seasonal activity, builds multi-layer KMLs with directional LineStrings | Species-colored migration corridors with arrows and seasonal context on the right balloon | https://github.com/LiquidGalaxyLAB/local-ai-gemma/blob/main/skills/animal-migrations.md |
| coral-reef-monitor✅ | "Show coral bleaching on the rig"; "State of the Great Barrier Reef"; "Global reef health near NA" | NOAA Coral Reef Watch, ReefBase, AIMS and other reef datasets | Builds reef polygon outlines and bleaching-alert layers with severity coloring | Multi-layer reef KMLs showing alert levels (teal → orange → crimson) and DHW heatmaps | https://github.com/LiquidGalaxyLAB/local-ai-gemma/blob/main/skills/coral-reef-monitor.md |
| country-instability-index🆕 | "show me the country instability index on the rig", "which countries are most unstable right now", "cross-stream correlation view on the LG" | GDELT Doc API (free, no key) + composites signals from armed-conflicts, economic-markets, cyber-infrastructure, and natural-disaster skills | Meta-skill: 30+ tracked countries rendered as extruded 3D columns (height = composite stress score), camera slow-laps the instability landscape. Cross-stream correlation from World Monitor, rebuilt for a flying camera. | Hexagonal prism columns rising 0-50km on calm-to-crisis gradient, top-5 pulse rings, per-country component breakdown on right-screen intelligence dossier panel (navy + gold). | https://github.com/LiquidGalaxyLAB/local-ai-gemma/blob/main/skills/country-instability-index.md |
| prediction-markets-geo🆕 | "what are prediction markets saying right now", "show me Polymarket on the globe", "where is the world's money betting on conflict" | Polymarket CLOB API (free, no key) — tags filtered for geopolitics, elections, conflict, sanctions, rate cuts | Geo-forecast rings: implied probability mapped as pulsing concentric circles at country centroids. Amber = high uncertainty, white = consensus. Camera flies between high-stakes markets. | Amber pulsing rings at 40-60% probability markets, white slow-pulse at consensus markets, probability bars on right-screen trading terminal panel (charcoal + amber). | https://github.com/LiquidGalaxyLAB/local-ai-gemma/blob/main/skills/prediction-markets-geo.md |
| global-progress-dashboard🆕 | "show me positive global trends on the rig", "what's getting better in the world", "classroom demo — show something positive" | Our World in Data API (free, no key) + WHO GHO (free) + IUCN (free token) — extreme poverty, child mortality, renewables, life expectancy, disease eradication | The counterweight to every crisis skill: maps positive trends with warm sunrise-gradient visuals. Designed for classrooms and public demos. 5 metrics where global trends are unambiguously positive. | Green falling columns (poverty declining), gold rising columns (renewables), amber-to-green choropleth (child mortality), green victory rings (disease eradication), sunrise-gradient right-screen panel. | https://github.com/LiquidGalaxyLAB/local-ai-gemma/blob/main/skills/global-progress-dashboard.md |
| deforestation-monitor🆕 | "show me deforestation on the rig", "where are forests being lost right now", "Amazon deforestation watch on the LG" | NASA FIRMS (free, no key) + GFW Open Data Portal (free CSV) + RESOLVE Ecoregions (free GeoJSON) + WDPA Protected Areas (free token) | 4-layer forest watch: live fire alerts, tree cover loss choropleth, biodiversity hotspot polygons, protected area green borders. Camera flies deforestation fronts — Amazon arc, Congo Basin, Indonesia, West Africa. | Red fire dots at forest edges, green-to-red country choropleth, magenta biodiversity hotspot polygons (new color in Nara's palette), green protected area ramparts, restoration halos for reforesting countries. | https://github.com/LiquidGalaxyLAB/local-ai-gemma/blob/main/skills/deforestation-monitor.md |
| satellite-orbital-tracker🆕 | "show me the ISS on the rig", "satellite tracker on the LG", "Starlink constellation view", "where is Hubble right now" | CelesTrak TLE data (free, no key — 27,000+ objects) + SGP4 propagation (pip sgp4, pure Python) — verified 16,093 active satellites + 10,761 Starlink + stations + debris | Orbital objects at actual altitude on a multi-screen 3D globe — the killer app no browser dashboard can touch. ISS at 423km, Starlink at 550km, GPS ring at 20,200km. Camera rises through orbital shells. | White star markers + vertical altitude tether lines, dotted orbit trails, cyan satellite dots, gold GPS MEO ring, mission-control right-screen panel (pure black + cyan). | https://github.com/LiquidGalaxyLAB/local-ai-gemma/blob/main/skills/satellite-orbital-tracker.md |
216|
217|**Liquid Galaxy setup helper**
218|
219|This special skill helps users build a virtual Liquid Galaxy rig on their system.
220|
**Liquid Galaxy setup helper**

This special skill helps users build a virtual Liquid Galaxy rig on their system.

Each domain has its own specialized skill and visual style. These include news storytelling, history education, armed conflicts, maritime awareness, energy monitoring, cyber infrastructure, economic markets, aviation watch, wildlife migrations, coral reef monitoring, and orbital tracking. Every skill is designed to present information in a way that best fits its topic while sharing the same underlying framework.

The skills are also connected intelligently. Instead of duplicating data or features, they reuse information from one another whenever possible. The country-instability-index functions as a meta-skill, compositing signals from armed-conflicts, economic-markets, cyber-infrastructure, and natural-disaster into one cross-stream correlation view. The global-progress-dashboard serves as a deliberate counterweight — showing positive global trends using warm, optimistic visuals suitable for classrooms and public demos. The prediction-markets-geo skill adds a geo-forecast layer showing what the world's aggregate money believes will happen next. The deforestation-monitor and satellite-orbital-tracker open entirely new domains: ecosystem-scale environmental change and orbital space. All visualizations follow the same deployment process, update automatically on the Liquid Galaxy rig without restarting it, and use a consistent layout for dashboards and screen placement.

**Nara currently has 19 skills built and working** — 14 original + 5 new (country-instability-index, prediction-markets-geo, global-progress-dashboard, deforestation-monitor, satellite-orbital-tracker).

**This is a new skill which will help users to setup a virtual liquid galaxy on their system.**
231|[SKILL.md](https://github.com/LiquidGalaxyLAB/local-ai-gemma/blob/main/skills/lg-installation-setup.md)
232|
233|What It Is
234|
235|It is a step-by-step guide and automated helper for creating a multi-screen Liquid Galaxy virtual machine rig (example: three Ubuntu VMs). The skill explains VM networking, frame assignment, SSH setup, and basic repairs.
236|
237|Example prompts
238|
239|"Help me set up a 3-screen Liquid Galaxy rig using VirtualBox on Ubuntu 16.04."
240|
241|"I just created three blank VMs (lg1, lg2, lg3) for Liquid Galaxy. How do I configure the network adapters and SSH access?"
242|
243|How the skills relate
244|
245|The system is layered so features reuse core capabilities instead of duplicating work. For example, `lg-ssh-control` handles rig communication, `lg-kml-tours` provides visualization primitives, and `lg-data-visualization` normalizes live data feeds for other skills to consume. Visual styles and deployment conventions are shared across skills.
246|
247|Full catalog of all skills in the repo: [SKILLS.md](SKILLS.md).
248|
249|---
250|
251|## Quick Start
252|
253|1. Install Hermes Agent ([Installation](#installation)).
254|2. Ensure SSH connectivity between the Pi (or host) and the Liquid Galaxy master node.
255|3. Import or restore the `liquid-galaxy-agent` Hermes profile ([backup folder](https://drive.google.com/drive/folders/1mQyJYMV7bvj-cq7geYF7AcXGROvqjj-z)).
256|4. Enable skills (`lg-ssh-control`, weather, geography, etc.) and configure API keys with `hermes model`.
257|
258|---
259|
260|## Hermes Agent Setup
261|
262|The self-improving AI agent built by Nous Research. It has a built-in learning loop: it creates skills from experience, improves them during use, persists knowledge, and builds a model of who you are across sessions.
263|
264|**Website:** [https://hermes-agent.nousresearch.com/](https://hermes-agent.nousresearch.com/)
265|
266|### Profiles
267|
268|A [profile](https://hermes-agent.nousresearch.com/docs/user-guide/profiles) is a self-contained Hermes home directory. This project starts with one profile: **`liquid-galaxy-agent`**.
269|
270|Each profile gets its own `config.yaml`, `.env`, `SOUL.md`, memories, sessions, skills, cron jobs, and state database — independent directories, a clean slate.
271|
272|### Backups
273|
274|[Backups](https://hermes-agent.nousresearch.com/docs/getting-started/updating#full-pre-update-backup---backup) create a zip archive of config, skills, sessions, and data (everything except the codebase). Restore with [`hermes import`](https://hermes-agent.nousresearch.com/docs/reference/cli-commands#hermes-import).
275|
276|| Mode | Role |
277|| :--- | :--- |
278|| **CLI session** | Interactive terminal UI — conversation loop, system prompts, model providers, tools, history |
279|| **Gateway message** | 20+ messaging adapters (Discord, Slack, WhatsApp, etc.) — auth, session isolation, routing |
280|
281|### Skills setup
282|
283|Hermes needs custom skills for LG-specific use cases. A skill = instructions + shell commands + tools. Skills and tools work together to satisfy use cases.
284|
285|- [Adding Tools](https://hermes-agent.nousresearch.com/docs/developer-guide/adding-tools)
286|- [Creating Skills](https://hermes-agent.nousresearch.com/docs/developer-guide/creating-skills)
287|
288|Skills live under the profile directory, e.g. `~/.hermes/profiles/<profile>/skills/` (each profile has its own skills tree).
289|
290|In **this repo**, every skill is a **flat markdown file**:
291|
292|| Path | Role |
293|| :--- | :--- |
294|| [`skills/<name>.md`](skills/) | Skill document (YAML frontmatter + procedures) |
295|| [`skills/references/<name>/`](skills/references/) | Optional architecture notes & troubleshooting |
296|| [`skills/scripts/<name>/`](skills/scripts/) | Optional deployable helpers / generators |
297|| [`skills/templates/<name>/`](skills/templates/) | Optional KML / config templates |
298|
299|GitHub example: [skills/live-aviation.md](https://github.com/LiquidGalaxyLAB/local-ai-gemma/blob/main/skills/live-aviation.md) · catalog: [SKILLS.md](SKILLS.md).
300|
301|---
302|
303|## Installation
304|
305|### Terms you'll see
306|
307|| Term | Meaning |
308|| :--- | :--- |
309|| **Terminal** | Text window where you type commands |
310|| **Shell** | Program that reads commands (`bash`, `zsh`, PowerShell) |
311|| **Archive** | `.zip` / `.tar.gz` packing many files into one |
312|| **`~`** | Shortcut for your home folder (e.g. `/home/pi`) |
313|
314|### Download the backup first
315|
316|Download the latest backup from the shared Drive folder:
317|
318|**[Backup download (Google Drive)](https://drive.google.com/drive/folders/1mQyJYMV7bvj-cq7geYF7AcXGROvqjj-z)**
319|
320|Folders are dated — pick the **latest date** and use the Hermes / profile backup inside.
321|
322|### Prerequisites (Raspberry Pi / Linux)
323|
324|```bash
325|git --version
326|```
327|
328|If Git is missing:
329|
330|```bash
331|sudo apt update
332|sudo apt install -y git curl xz-utils
333|```
334|
335|| Package | Why |
336|| :--- | :--- |
337|| **git** | Lets the installer clone the Hermes codebase |
338|| **curl** | Downloads installer assets |
339|| **xz-utils** | Unpacks Node.js `.tar.xz` archives |
340|
341|You do **not** need to manually install Python, Node.js, ripgrep, or ffmpeg — the Hermes installer detects and installs those.
342|
343|On non-Windows platforms, the only hard prerequisite is Git. The installer handles:
344|
345|- uv (fast Python package manager)
346|- Python 3.11 (via uv, no sudo needed)
347|- Node.js v22 (browser automation / WhatsApp bridge)
348|- ripgrep (fast file search)
349|- ffmpeg (audio for TTS)
350|
351|### Option A — Command-line install (recommended for Raspberry Pi)
352|
353|```bash
354|curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
355|```
356|
357|What this does: downloads the installer, installs tooling, creates an isolated Python virtual environment, and exposes a global `hermes` command. Let it finish completely before continuing.
358|
359|### Option B — Desktop app (macOS / Windows)
360|
361|Download the [Hermes Desktop installer](https://hermes-agent.nousresearch.com/) from the website.
362|
363|**PowerShell (Windows):**
364|
365|```powershell
366|iex (irm https://hermes-agent.nousresearch.com/install.ps1)
367|```
368|
369|Setup walkthrough video: [YouTube](https://youtu.be/r77kEcoE7Sw?si=a9vfaL3OiTqQK0gE)
370|
371|### After install
372|
373|Reload your shell, then test:
374|
375|```bash
376|source ~/.bashrc   # or source ~/.zshrc
377|hermes
378|```
379|
380|If a chat prompt opens, install succeeded. Type `exit` or press `Ctrl+C` to leave. By default, Hermes stores data under `~/.hermes/`.
381|
382|---
383|
384|## Restoring the Liquid Galaxy Profile
385|
386|Two safe approaches — pick based on whether this machine already has Hermes work you care about.
387|
388|| Your situation | Use |
389|| :--- | :--- |
390|| Brand-new Hermes install, nothing to lose | **Approach 1 — Full restore** |
391|| Existing chats/config/skills you want to keep | **Approach 2 — Profile import** (recommended) |
392|
393|### Approach 1 — Full backup restore (overwrites `~/.hermes`)
394|
395|Use only on a **fresh** install. This replaces your entire `~/.hermes/` directory — config, skills, sessions, memories, everything.
396|
397|1. Download the `.zip` from the [Drive folder](https://drive.google.com/drive/folders/1mQyJYMV7bvj-cq7geYF7AcXGROvqjj-z) (e.g. `hermes-backup-YYYY-MM-DD-HHMMSS.zip`).
398|2. Restore:
399|
400|```bash
401|hermes import /path/to/hermes-backup-YYYY-MM-DD-HHMMSS.zip
402|```
403|
404|3. Configure model and tools:
405|
406|```bash
407|hermes model          # Interactive model/provider picker
408|hermes tools          # Configure which tools are enabled
409|hermes setup          # Or run the full setup wizard
410|hermes doctor         # Check everything is working
411|```
412|
413|You can also start Hermes and use in-session commands: `/model`, `/config`.
414|
415|### Approach 2 — Profile import (preserves existing data)
416|
417|Safer option: adds `liquid-galaxy-agent` **alongside** other profiles without touching yours.
418|
419|1. Download `liquid-galaxy-agent.tar.gz` from the [Drive folder](https://drive.google.com/drive/folders/1mQyJYMV7bvj-cq7geYF7AcXGROvqjj-z).
420|2. Import and switch:
421|
422|```bash
423|hermes profile import /path/to/liquid-galaxy-agent.tar.gz --name liquid-galaxy-agent
424|hermes profile use liquid-galaxy-agent
425|hermes model
426|hermes tools
427|hermes doctor
428|```
429|
430|3. Start chatting:
431|
432|```bash
433|hermes
434|# or one-shot:
435|hermes --profile liquid-galaxy-agent
436|```
437|
438|4. Switch profiles later:
439|
440|```bash
441|hermes profile list
442|hermes profile use liquid-galaxy-agent
443|hermes profile use default
444|```
445|
446|### Quick comparison
447|
448|| | Approach 1 (Full restore) | Approach 2 (Profile import) |
449|| :--- | :--- | :--- |
450|| Overwrites your data? | Yes — entire `~/.hermes/` | No — adds a profile |
451|| Best for | Fresh install | Existing Hermes users |
452|| Command | `hermes import backup.zip` | `hermes profile import file.tar.gz` |
453|| Profiles available | Only this one | Yours + this one |
454|
455|### Next steps / configuration (both approaches)
456|
457|```bash
458|hermes model          # Choose LLM provider and model
459|hermes tools          # Configure enabled tools
460|hermes gateway setup  # Messaging platforms (Telegram, Discord, etc.)
461|hermes config set     # Set individual config values
462|hermes setup          # Full setup wizard
463|hermes setup --portal # Nous Portal setup
464|hermes doctor         # Diagnostics
465|```
466|
467|### Troubleshooting
468|
469|| Problem | Fix |
470|| :--- | :--- |
471|| `hermes: command not found` | Run `source ~/.bashrc` or open a new terminal |
472|| API key not set | `hermes model` or `hermes config set OPENROUTER_API_KEY your_key` |
473|| Something broken after restore | Run `hermes doctor` |
474|
475|Official docs: [hermes-agent.nousresearch.com/docs](https://hermes-agent.nousresearch.com/docs/)
476|
477|---
478|
479|## Docker & WSL Setup
480|
481|<div align="center">
482|  <img src="./assets/hermes-docker.png" alt="Hermes Agent running in Docker Desktop" width="720" />
483|  <br />
484|  <em>Hermes Agent running under Docker Desktop</em>
485|</div>
486|
487|<br />
488|
489|You can also follow the [official Docker guide](https://hermes-agent.nousresearch.com/docs/user-guide/docker).
490|
491|### What is WSL2?
492|
493|**Windows Subsystem for Linux (WSL2)** runs a lightweight Linux environment (e.g. Ubuntu) inside Windows 10/11 without a full traditional VM — near-native filesystem performance and good hardware integration. It uses a custom Linux kernel inside a lightweight utility VM.
494|
495|### What is Docker?
496|
497|**Docker** packages apps into isolated **containers** that share the host kernel (code, dependencies, and binaries together). On Windows, Docker Desktop uses the **WSL2** backend for efficient Linux containers.
498|
499|### Install Docker
500|
501|**Windows (PowerShell as Administrator):**
502|
503|```powershell
504|# 1. Install the WSL Linux backend
505|wsl --install --no-distribution
506|
507|# 2. Download and install Docker Desktop
508|curl.exe -L -o DockerDesktop.exe "https://docker.com"
509|Start-Process ./DockerDesktop.exe -ArgumentList "/quiet", "/accept-license" -Wait
510|
511|# 3. Restart, then open Docker Desktop
512|```
513|
514|**macOS:**
515|
516|```bash
517|curl -o Docker.dmg "https://docker.com"
518|sudo hdiutil attach Docker.dmg
519|sudo cp -R /Volumes/Docker/Docker.app /Applications
520|sudo hdiutil detach /Volumes/Docker
521|open /Applications/Docker.app
522|```
523|
524|**Linux (Ubuntu/Debian):**
525|
526|```bash
527|curl -fsSL https://docker.com | sh
528|sudo usermod -aG docker $USER
529|newgrp docker
530|```
531|
532|> **Note:** On macOS and Linux you do not need WSL2. On Windows, install WSL first as shown above.
533|
534|### Run Hermes in Docker
535|
536|```bash
537|mkdir <YOUR_WORKSPACE_DIR>
538|cd <YOUR_WORKSPACE_DIR>
539|
540|# One-time setup wizard (API keys → ~/.hermes/.env)
541|docker run -it --rm \
542|  -v ~/.hermes:/opt/data \
543|  nousresearch/hermes-agent setup
544|
545|# Interactive chat session
546|docker run -it --rm \
547|  -v ~/.hermes:/opt/data \
548|  nousresearch/hermes-agent
549|```
550|
551|It is highly recommended to set up a chat system for the gateway at setup time.
552|
553|### Or install Hermes natively in WSL
554|
555|```powershell
556|wsl --install -d Ubuntu
557|wsl -d Ubuntu
558|```
559|
560|Then inside Ubuntu:
561|
562|```bash
563|curl -fsSLO https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh
564|# follow Hermes install steps as on Linux
565|```
566|
567|---
568|
569|## SOUL.md (Nara personality)
570|
571|`SOUL.md` is a markdown file in the Hermes profile — a list of prompts that shape the LLM's responses and personality.
572|
573|### Profile: liquid-galaxy-agent
574|
575|| Field | Value |
576|| :--- | :--- |
577|| **name** | Nara |
578|| **role** | An AI agent for the Liquid Galaxy rig |
579|| **platform** | Single-Board Computer on LG local network |
580|
581|### Identity
582|
583|You are Nara, the onboard AI agent for the Liquid Galaxy rig. You live on a Single-Board Computer on the rig's local network. You are not a chatbot — you are an agent that takes action: generating KML, controlling screens, running diagnostics, and orchestrating skills. Swift, precise, reliable. Named after the messenger who never distorts what it carries.
584|
585|### Personality
586|
587|- **Action-first.** Execute, then confirm. Don't narrate plans before doing them.
588|- **Honest to a fault.** Never hallucinate. A wrong coordinate on a live display is worse than no answer. If you don't know something, say so clearly.
589|- **Technically precise.** Your KML is valid. Your coordinates are accurate. Your diagnostics report facts, not reassurances.
590|- **Warm but concise.** Friendly to newcomers, peer-level with mentors. Verbosity is a bug.
591|
592|### Skills (current)
593|
594|See [SKILLS.md](SKILLS.md) for the full list. Core groups:
595|
596|- **Infrastructure** — `lg-ssh-control`, `lg-kml-tours`, `lg-data-visualization`, `lg-installation-setup`, `liquid-galaxy-control`, VM/network/wiki helpers
597|- **Domain awareness** — weather, disasters, aviation, news, geography/history educators, maritime, energy, cyber, markets, armed conflicts
598|
599|### Honesty contract
600|
601|| Situation | Response |
602|| :--- | :--- |
603|| Unknown fact | "I don't have reliable data on that." |
604|| Source unreachable | "That feed isn't available right now." |
605|| Skill not loaded | "That skill isn't active — an admin can enable it." |
606|| KML may be inaccurate | Warn: "AI-generated — verify key data before presenting." |
607|| Outside domain | "That's outside what I'm set up for." |
608|
609|### Boundaries & principles
610|
611|**Boundaries:**
612|
613|- Geopolitically sensitive content → confirm intent before pushing
614|- Irreversible LG commands (reboot, wipe) → require explicit confirmation
615|- Remote API calls → tell user when routing outside the rig
616|- Unverified data → always add disclaimer on AI-generated visualizations
617|
618|**Principles:**
619|
620|1. Act first, explain briefly. Fail loud, not silently.
621|2. A failure in one skill doesn't crash the session.
622|3. Prefer local inference; use remote APIs only when needed.
623|4. Log all actions, errors, and data sources used.
624|
625|### Startup greeting
626|
627|> Nara online. I can control the screens, generate KML visualizations, answer LG questions, run diagnostics, and more. What do you want on the screens today?
628|
629|---
630|
631|## Hermes Agent Architecture
632|
633|<div align="center">
634|  <img src="./assets/hermes-architecture.png" alt="Hermes Agent Architecture diagram" width="900" />
635|  <br />
636|  <em>Hermes Agent Architecture — credit to Alejandro (Hugging Face). <a href="https://youtu.be/n32qq7Kwzh0?si=EGcxNw3M5xKGTXeC">Video walkthrough</a></em>
637|</div>
638|
639|<br />
640|
641|Hermes is built around a single core agent process that everything else plugs into. Instead of only living in a terminal, it exposes three **entry points**: a CLI for direct local use, an API for programmatic integration, and a long-running Gateway that bridges the agent to messaging platforms like Telegram, Discord, Slack, WhatsApp, SMS, and email. The same agent can be talked to from a chat app just as easily as from a script.
642|
643|| Entry point | Role |
644|| :--- | :--- |
645|| **CLI** | Direct local terminal use |
646|| **API** | Programmatic / external integration |
647|| **Gateway** | Long-running bridge to Telegram, Discord, Slack, WhatsApp, SMS, email, etc. |
648|
649|### The agent loop
650|
651|1. User sends a message  
652|2. Hermes builds context (memory files + history + tools/skills)  
653|3. Context + history go to the LLM  
654|4. LLM may call tools  
655|5. Tool results return to the LLM  
656|6. LLM produces a final response  
657|7. Hermes updates memory  
658|
659|It's a simple, repeatable cycle rather than a one-shot request/response.
660|
661|### Context & memory
662|
663|Hermes keeps markdown files as a lightweight personality and knowledge base. These load alongside recent conversation history and tool/skill descriptions each turn. When a conversation grows past ~50% of the context window, older turns are compressed into a structured summary (goal, completed actions, blockers, decisions, relevant files) so the agent doesn't lose the thread.
664|
665|| File | Purpose |
666|| :--- | :--- |
667|| `soul.md` | Behavior / tone (system prompt style) |
668|| `user.md` | Learned facts about the user |
669|| `memory.md` | Durable notes on workflows and tool usage |
670|
671|Memory layers:
672|
673|1. **Markdown memory files** — persistent knowledge  
674|2. **SQLite session history** — isolated per conversation / channel (Telegram vs email don't bleed)  
675|3. **External providers** (optional) — e.g. mem0, SuperMemory  
676|
677|### Cron jobs
678|
679|Scheduled tasks live in a plain `jobs.json` (not SQLite), are polled on an interval, and route out through the same Gateway — so a scheduled job can message you on Slack without a separate notification system.
680|
681|**Design philosophy:** keep the "thinking" part (LLM call and tool use) simple and stateless per turn; push continuity — memory, compression, multi-channel delivery — into supporting systems around it.
682|
683|---
684|
685|## LLM Wiki & Google OKF
686|
687|<div align="center">
688|  <img src="./assets/llw-wiki-arch.png" alt="LLM Wiki three-layer architecture" width="720" />
689|  <br />
690|  <em>LLM Wiki — three-layer architecture (raw sources → entities/concepts → compiled knowledge)</em>
691|</div>
692|
693|<br />
694|
695|Most people's experience with LLMs and documents looks like [RAG](https://cloud.google.com/use-cases/retrieval-augmented-generation?hl=en): upload files, retrieve chunks at query time, generate an answer. That works, but the LLM rediscovers knowledge from scratch on every question — nothing accumulates.
696|
697|An **[LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)** is different. Instead of only retrieving from raw documents at query time, the LLM incrementally builds and maintains a persistent wiki — a structured, interlinked collection of markdown files between you and the raw sources. When you add a source, the LLM reads it, extracts key information, and integrates it: updating entity pages, revising topic summaries, noting contradictions. Knowledge is **compiled once** and kept current.
698|
699|| Operation | What happens |
700|| :--- | :--- |
701|| **Ingest** | New source is read, summarized, and merged into entity/topic pages |
702|| **Query** | Answers are synthesized from the pre-compiled wiki; great insights can be filed back as pages |
703|| **Lint** | Health check: broken links, contradictions, duplicates, gaps |
704|
705|In Hermes, set the wiki path via `WIKI_PATH` in `${HERMES_HOME:-~/.hermes}/.env` (defaults to `~/wiki`). Hermes includes a skill that triggers on create / ingest / query / lint style requests.
706|
707|### Google Open Knowledge Format (OKF)
708|
709|[OKF](https://cloud.google.com/blog/products/data-analytics/how-the-open-knowledge-format-can-improve-data-sharing) is a vendor-neutral standard for how agents package and exchange knowledge:
710|
711|| Role | What it does |
712|| :--- | :--- |
713|| **LLM Wiki** | The "compiler" — messy PDFs, scrapes, and logs → synthesized local knowledge |
714|| **OKF** | The "export format" — zip a bundle for any compatible agent with zero translation code |
715|
716|| Principle | Meaning |
717|| :--- | :--- |
718|| **Just markdown** | Readable in any editor, renderable on GitHub |
719|| **Just files** | Shippable as a tarball, hostable in git |
720|| **Just YAML frontmatter** | Structured fields: type, title, tags, timestamps |
721|
722|---
723|
724|## System Architecture
725|
726|<div align="center">
727|  <img src="./assets/img3.png" alt="Hermes entry points and AIAgent core components" width="720" />
728|  <br />
729|  <em>Entry points → AIAgent core → session storage and tool backends</em>
730|</div>
731|
732|<br />
733|
734|High-level layout for this project:
735|
736|| Layer | Components |
737|| :--- | :--- |
738|| **Hermes core** | CLI, API, Gateway entry points |
739|| **Skills** | Modular instructions + tool wrappers (SSH, KML, data fetchers) |
740|| **Memory** | Markdown wiki + SQLite session store |
741|| **Models** | Local (Ollama / LM Studio) or remote APIs |
742|
743|---
744|
745|## Tech Stack
746|
747|| Area | Technologies |
748|| :--- | :--- |
749|| Agent runtime | Hermes, multi-agent orchestration |
750|| AI / models | Ollama or LM Studio (local), remote model APIs |
751|| Visualization | KML, Google Earth, Liquid Galaxy |
752|| Communication | WebSockets, REST |
753|| Data sources | OpenSky Network, Celestrak, RSS, weather APIs |
754|| Hardware interface | SSH, sshpass, shell scripting |
755|| Languages | Python, Shell |
756|
757|---
758|
759|## Hardware
760|
761|<div align="center">
762|  <img src="./assets/img1.png" alt="Raspberry Pi 5 with M.2 HAT+ and NVMe SSD" width="520" />
763|  <br />
764|  <em>Recommended agent host: Raspberry Pi 5 with M.2 HAT+ and NVMe SSD</em>
765|</div>
766|
767|<br />
768|
769|| Component | Specification |
770|| :--- | :--- |
771|| **SBC** | Raspberry Pi 5, 8GB RAM |
772|| **Storage** | 256GB / 512GB NVMe SSD |
773|| **NVMe interface** | Raspberry Pi M.2 HAT+ (M-key) |
774|| **Boot media** | 16GB+ microSD (initial setup only) |
775|| **Power** | Raspberry Pi 27W USB-C supply |
776|| **Network** | Local LAN with SSH from agent → LG master |
777|
778|---
779|
780|## Hardware Setup
781|
782|### Step 1 — Attach NVMe SSD via M.2 HAT
783|
784|1. Power off and unplug the Raspberry Pi 5.
785|2. Attach the Raspberry Pi M.2 HAT+ to the RPi 5 using the PCIe FPC ribbon cable — connect it to the PCIe FPC connector on the bottom edge of the RPi 5 board. Secure the HAT with the provided standoffs.
786|3. Insert the 512GB NVMe SSD (M.2 2280 or 2242, M-key) into the M.2 slot on the HAT. Secure it with the retention screw.
787|4. Confirm the HAT sits flat and all connectors are fully seated before proceeding.
788|
789|> ⚠️ Handle the PCIe ribbon cable with care — it is fragile. Ensure the blue side faces up when inserting into the RPi 5 connector.
790|
791|### Step 2 — Flash Raspberry Pi OS to SD card
792|
793|1. On your computer, download and install [Raspberry Pi Imager](https://www.raspberrypi.com/software/).
794|2. Insert your 16GB+ microSD card into your computer.
795|3. Open RPi Imager and configure:
796|   - **Device:** Raspberry Pi 5
797|   - **OS:** Raspberry Pi OS (64-bit) — full Desktop version recommended for initial setup
798|   - **Storage:** Select your microSD card
799|4. Click Edit Settings (⚙️) before writing:
800|   - Set hostname (e.g. `nara.local`)
801|   - Enable SSH → password authentication
802|   - Set username and password
803|   - Configure Wi-Fi if needed
804|5. Click Save → Yes → Write and wait for the flash to complete.
805|
806|### Step 3 — First boot from SD card
807|
808|1. Insert the flashed microSD card into the Raspberry Pi 5.
809|2. Connect a monitor, keyboard, and mouse (or use SSH after boot).
810|3. Connect power — the RPi 5 will boot from the SD card.
811|4. Complete the initial OS setup if the desktop wizard appears.
812|5. Open a terminal and run a system update:
813|
814|```bash
815|sudo apt update && sudo apt full-upgrade -y
816|sudo reboot
817|```
818|
819|6. After reboot, verify the NVMe is detected:
820|
821|```bash
822|lsblk
823|# You should see: nvme0n1 with no partitions yet
824|```
825|
826|If `nvme0n1` does not appear, check the M.2 HAT ribbon cable connection and reboot.
827|
828|### Step 4 — Flash OS to NVMe SSD
829|
830|With the RPi running from SD, use RPi Imager (already on Raspberry Pi OS) to write the OS to the NVMe:
831|
832|1. Open Raspberry Pi Imager from the desktop (or run `rpi-imager`).
833|2. Configure the same settings as Step 2 (or reuse saved customizations).
834|3. **Storage:** Select the NVMe drive (`/dev/nvme0n1` — typically listed as the 512GB drive).
835|4. Click Write and wait for completion.
836|
837|### Step 5 — Configure NVMe boot order
838|
839|Tell the Raspberry Pi 5 bootloader to prefer the NVMe SSD over the SD card.
840|
841|**Option A — via raspi-config (recommended):**
842|
843|```bash
844|sudo raspi-config
845|```
846|
847|Navigate to: **Advanced Options → Boot Order → NVMe/USB Boot** → select NVMe → confirm and exit.
848|
849|**Option B — via EEPROM config (manual):**
850|
851|```bash
852|sudo -E rpi-eeprom-config --edit
853|```
854|
855|Set:
856|
857|```text
858|BOOT_ORDER=0xf61
859|```
860|
861|> Boot order is read right-to-left: `6` = NVMe (PCIe), `1` = SD card, `f` = loop/restart.  
862|> Meaning: try NVMe first → fall back to SD → repeat.
863|
864|```bash
865|sudo reboot
866|```
867|
868|### Step 6 — Boot from NVMe
869|
870|```bash
871|sudo poweroff
872|```
873|
874|1. Remove the microSD card.
875|2. Power the RPi 5 back on.
876|3. The system should boot directly from the NVMe SSD.
877|4. Verify:
878|
879|```bash
880|findmnt /
881|# Should show: /dev/nvme0n1p2 or similar — not mmcblk0
882|```
883|
884|If the RPi fails to boot without the SD card, revisit Step 5 and confirm the EEPROM boot order was saved correctly.
885|
886|---
887|
888|## Example Usage
889|
890|Import / restore reminders:
891|
892|```bash
893|hermes import ~/your-backup-name.zip
894|# or
895|hermes profile import ~/liquid-galaxy-agent.tar.gz --name liquid-galaxy-agent
896|```
897|
898|Once Nara is running and connected to the rig:
899|
900|### Basic LG commands
901|
902|| Command | What happens |
903|| :--- | :--- |
904|| Connect to the Liquid Galaxy | Verifies connection / connects to the rig |
905|| Relaunch Earth on the rig | Restarts Earth via `lg-relaunch-direct` helper |
906|| Reboot / power off the Liquid Galaxy | Reboots or shuts down the rig |
907|| Clear the KMLs | Removes deployed KMLs |
908|| Add logo to the Liquid Galaxy | Project logo on the leftmost screen |
909|
910|### KML & visualization
911|
912|| Command | What happens |
913|| :--- | :--- |
914|| Make a pyramid over Madrid / Pune with fly-to | Generates & deploys a pyramid KML (any city works; agent can web-search coords) |
915|| Highlight flood zones near Kerala | Creates and shows flood-zone KML |
916|| "What's the weather in Pune?" | Weather columns + icons on LG |
917|| "Show flights over Germany" | Live aviation layer from OpenSky |
918|| "Show earthquakes in Japan" | Disaster layers + auto-fly + TTS |
919|
920|---
921|
922|## Voice Support
923|
924|Hermes supports two-way voice:
925|
926|| Mode | Role |
927|| :--- | :--- |
928|| **TTS (Text-to-Speech)** | Agent converts responses into spoken audio or native voice messages |
929|| **STT (Speech-to-Text)** | Voice notes / mic input transcribed to text for the agent |
930|
931|You can choose free or paid providers for TTS and STT based on requirements.
932|
933|### Enabling voice mode
934|
935|Easiest path: ask the agent in the CLI:
936|
937|> "Enable voice mode for hermes, speech to text and text to speech"
938|
939|It will install dependencies and detect your microphone. Defaults need no API keys.
940|
941|```text
942|/voice on      # full voice conversation
943|/voice tts     # always read responses aloud
944|/voice off     # disable voice features
945|```
946|
947|**Note:** Your Raspberry Pi must have a microphone and speaker (built-in or USB). Hermes uses the OS default audio devices — configure routing first via Desktop audio settings, `raspi-config`, or `alsamixer` / `aplay -l` / `arecord -l`. Hermes can also help you configure these.
948|
949|### Providers
950|
951|**Speech-to-Text (STT)**
952|
953|| Provider | Environment variable | Free? |
954|| :--- | :--- | :---: |
955|| Local (Faster Whisper) | — | ✅ |
956|| Groq | `GROQ_API_KEY` | ✅ Free tier |
957|| OpenAI | `VOICE_TOOLS_OPENAI_KEY` | ❌ |
958|| Mistral | `MISTRAL_API_KEY` | ❌ |
959|
960|**Text-to-Speech (TTS)**
961|
962|| Provider | Environment variable | Free? |
963|| :--- | :--- | :---: |
964|| Edge | — | ✅ |
965|| ElevenLabs | `ELEVENLABS_API_KEY` | ✅ Free tier |
966|| OpenAI | `VOICE_TOOLS_OPENAI_KEY` | ❌ |
967|| MiniMax | `MINIMAX_API_KEY` | ❌ |
968|| Mistral | `MISTRAL_API_KEY` | ❌ |
969|| NeuTTS (local) | — (`pip install neutts[all]`) | ✅ |
970|
971|Edge + Faster Whisper work well as defaults.
972|
973|### ElevenLabs (optional premium)
974|
975|Voice is a two-way pipeline: STT → Hermes LLM → TTS.
976|
977|- **TTS:** e.g. `eleven_flash_v2_5` (low latency) or `eleven_multilingual_v2`, with a `voice_id`
978|- **STT:** ElevenLabs Scribe (`scribe_v2`) across CLI / Telegram / Discord / WhatsApp / Slack / Signal
979|
980|```bash
981|# Add to ~/.hermes/.env
982|ELEVENLABS_API_KEY=your_key_here
983|
984|# If premium TTS deps are missing
985|pip install "hermes-agent[tts-premium]"
986|```
987|
988|Then: `/voice on` and `/voice tts`. You can also describe your preferred setup to the agent and let it configure most of it.
989|
990|### Manual local setup (optional)
991|
992|```bash
993|source ~/.hermes/hermes-agent/venv/bin/activate
994|pip install faster-whisper sounddevice numpy libportaudio2
995|```
996|
997|`faster-whisper` runs fully local — no API key required for STT. Edge TTS is already supported by Hermes.
998|
999|Configure `~/.hermes/config.yaml`:
1000|
1001|```yaml
1002|stt:
1003|  enabled: true
1004|  provider: local
1005|  local:
1006|    model: base
1007|
1008|tts:
1009|  provider: edge
1010|
1011|voice:
1012|  auto_tts: false
1013|  record_key: ctrl+b
1014|  max_recording_seconds: 120
1015|```
1016|
1017|| Setting | Meaning |
1018|| :--- | :--- |
1019|| `stt.provider: local` | Faster Whisper on-device |
1020|| `stt.local.model` | `tiny` / `base` (recommended) / `small` / `medium` / `large-v3` |
1021|| `tts.provider: edge` | Free cloud TTS |
1022|| `voice.auto_tts` | `true` = always speak; `false` = text unless `/voice` enabled |
1023|| `voice.record_key` | Push-to-talk shortcut (hold to speak, release to send) |
1024|
1025|---
1026|
1027|## GitHub Access for the Agent
1028|
1029|Methods useful when the agent (or you) needs GitHub access from the Pi:
1030|
1031|### 1. GitHub CLI (`gh auth`)
1032|
1033|The `gh` tool handles Git operations and GitHub API tasks (PRs, issues).
1034|
1035|```bash
1036|gh auth login
1037|# or token:
1038|echo $TOKEN | gh auth login --with-token
1039|```
1040|
1041|Stores credentials securely and can configure Git automatically.
1042|
1043|### 2. Personal Access Tokens (PAT)
1044|
1045|PATs work as HTTPS passwords or as `GITHUB_TOKEN`.
1046|
1047|- **Classic PAT** — broad permissions; useful for troubleshooting  
1048|- **Fine-grained PAT** — restricted to specific repos/actions; safer for normal use  
1049|
1050|### 3. SSH keys
1051|
1052|- User SSH key on the Pi → add public key to GitHub  
1053|- Deploy key — single-repository access only  
1054|- No token expiry; access can be limited tightly  
1055|
1056|### 4. Git credential store
1057|
1058|```bash
1059|git config --global credential.helper store
1060|```
1061|
1062|Simple after one manual login — credentials stored in plain text on disk.
1063|
1064|### Repository rules (for the agent)
1065|
1066|When the agent is given GitHub access for this project:
1067|
1068|- Prefer the branch named **`agent-branch`** for agent-written learning/progress notes  
1069|- Do not modify or push to other branches without explicit human approval  
1070|- Always ask for permission before git commands that change remote state  
1071|- Always request human review before any push or sync  
1072|
1073|Repo: https://github.com/LiquidGalaxyLAB/local-ai-gemma.git
1074|
1075|---
1076|
1077|## Current Status
1078|
1079|**Nara can currently:**
1080|
1081|- Establish SSH to the Liquid Galaxy and run admin commands (relaunch Earth, reboot, poweroff)
1082|- Generate valid KML, deploy to the master (static `master.kml` and dynamic flows via `kmls.txt`), update or clear layers
1083|- Run domain skills for weather, disasters, aviation, news, educators, maritime, energy, cyber, markets, and conflicts
1084|- Guide virtual LG installation and VM/network setup
1085|
1086|| Area | Status |
1087|| :--- | :--- |
1088|| Documentation | High coverage (this README + [SKILLS.md](SKILLS.md) + GSoC 350h project notes) |
1089|| Skills | **23** flat skill files under [`skills/`](skills/) — see [example use cases](#example-use-cases-what-can-you-do-with-current-version-of-project) |
1090|| Testing | WSL and Docker validated; virtual LG use case documented |
1091|| Midterm lab testing | Lleida lab feedback applied (connection memory, logo, voice mode) |
1092|| Presentation | PPT in progress (13 Aug target) |
1093|
1094|---
1095|
1096|## Experiences During Development
1097|
1098|1. **Why good documentation matters**  
1099|   Mentors emphasized that personal projects and products for everyone are different. Clear, detailed documentation lets users with different experience levels understand and use the project.
1100|
1101|2. **Problems faced**  
1102|   Early on, expectations around architecture and documentation were unclear.
1103|
1104|3. **Solution**  
1105|   Mentors shared examples and guided what “good” looked like. That framing improved the project design and the docs.
1106|
1107|### Midterm testing
1108|
1109|Students and mentors at the Lleida lab shared two videos plus feedback. Seeing the project run on a real Liquid Galaxy was a highlight.
1110|
1111|| Feedback | Response |
1112|| :--- | :--- |
1113|| Agent asked for IP / connection details too often | Skill updated to ask once and save to memory for reuse |
1114|| Docs: move clear-KML into basic commands; add logo | Docs and logo updated |
1115|| Basic + advanced KMLs (e.g. endangered birds, themed overlays) | Worked well on the rig |
1116|| Voice mode needed after first video | Added; mic setup on Raspberry Pi OS was the main friction |
1117|| STT sometimes misheard intent; clear-KML once relaunched instead; multi-screen population KML issues | Tracking for skill hardening |
1118|
1119|### Architecture engineering
1120|
1121|Mentor Moises asked for a well-defined, fixed design that can host different use cases and skills. After examples and expectations, a design was drafted and tested locally — work that previously took days often dropped to hours.
1122|
1123|**Research / architecture doc:**  
1124|[External research document and architecture](https://docs.google.com/document/d/1ESamoc_D2Ro8EFBvxf-r09AtONIembIRs2gCAutu42A/edit?tab=t.elndxa9s92fi#heading=h.n78xse233yga)
1125|
1126|---
1127|
1128|## References
1129|
1130|| Resource | Link |
1131|| :--- | :--- |
1132|| Hermes Agent docs | https://hermes-agent.nousresearch.com/docs/ |
1133|| Hermes website | https://hermes-agent.nousresearch.com/ |
1134|| Project backups / profiles | https://drive.google.com/drive/folders/1mQyJYMV7bvj-cq7geYF7AcXGROvqjj-z |
1135|| LLM Wiki (Karpathy gist) | https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f |
1136|| Google OKF | https://cloud.google.com/blog/products/data-analytics/how-the-open-knowledge-format-can-improve-data-sharing |
1137|| Architecture video | https://youtu.be/n32qq7Kwzh0 |
1138|| Setup walkthrough | https://youtu.be/r77kEcoE7Sw |
1139|| Research & architecture doc | [Google Doc](https://docs.google.com/document/d/1ESamoc_D2Ro8EFBvxf-r09AtONIembIRs2gCAutu42A/edit?tab=t.elndxa9s92fi#heading=h.n78xse233yga) |
1140|| GitHub repo / skills | https://github.com/LiquidGalaxyLAB/local-ai-gemma |
1141|
1142|---
1143|
1144|*Google Summer of Code 2026 · Liquid Galaxy Lab · Local AI with Gemma by Google*
1145|