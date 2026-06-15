# Research Notes — Local AI with Gemma by Google (GSoC 2026)

This document tracks my findings for the GSoC 2026 project built around [Hermes Agent](https://hermes-agent.nousresearch.com/docs/). It's a living document ... updated as I work through the docs, do hands-on testing, and debug things.

---

## Use Cases — Planned Order

1. **Liquid Galaxy commands execution** — Execute SSH commands on the LG rig (relaunch, reboot, etc.) — *define components*
2. **Automated Storytelling and Guided Tours** — Generate KMLs and display them on the rig
3. **Weather Monitoring** — Fetch weather data and visualize it on LG via KMLs
4. **Efficient Knowledge** — A scraped and parsed version of LG Wiki, updated occasionally, for the agent to reference when answering LG-related questions
5. **Interactive LG Troubleshooting** — Basic automated debugging of LG issues (builds on knowledge from stage 4)
6. **Contributor Automator (Mentor Assistant)** — A skill that generates curated newcomer tasks, auto-checks submissions, and gives feedback
7. **News and Geopolitical Event Visualization**
8. **Data Visualization from open data sources [Air, Sea, Space]**

## Hermes Features Used

**Voice Mode**

Hermes has a built-in [Voice Mode](https://hermes-agent.nousresearch.com/docs/user-guide/features/voice-mode) which we can use for hands-free interaction with the rig.

![img1](./assets/img1.png)

**Profiles**

A [profile](https://hermes-agent.nousresearch.com/docs/user-guide/profiles) is a self-contained Hermes home directory. Starting with one profile for Liquid Galaxy — multiple profiles can be added later if different LG use cases need separate configurations.

Each profile gets its own `config.yaml`, `.env`, `SOUL.md`, memories, sessions, skills, cron jobs, and state database.

![img2](./assets/img2.png)

**Backups**

[Backups](https://hermes-agent.nousresearch.com/docs/getting-started/updating#full-pre-update-backup---backup) create a zip archive of the Hermes config, skills, sessions, and data — everything except the codebase itself. Other users can restore it with [`hermes import`](https://hermes-agent.nousresearch.com/docs/reference/cli-commands#hermes-import).

> *26 May — Added GitHub Copilot API via the Hermes Model command as a fallback to OpenRouter.*

## Hermes Architecture

![img3](./assets/img3.png)
**CLI Session** — Handles interactive terminal UIs. User input triggers the conversation loop, builds system prompts, resolves model providers, executes the necessary tools, and persists history to a local database.

**Gateway Message** — Manages persistent connections across 20+ messaging platform adapters (Discord, Slack, WhatsApp, and others). Handles user authorization, session isolation, and routes responses back to the originating platform.

**Cron Job** — Runs scheduled agent tasks via automated triggers. Loads pending jobs from a JSON config, spins up a fresh agent instance, injects the relevant skills as context, and sends output to the configured target.

## SOUL.md — Nara (Profile: liquid-galaxy-agent)

### Identity

You are **Nara**, the onboard AI agent for the Liquid Galaxy rig. You live on a Single-Board Computer on the rig's local network. You are not a chatbot — you are an **agent** that takes action: generating KML, controlling screens, running diagnostics, and orchestrating skills. Swift, precise, reliable. Named after the messenger who never distorts what it carries.

### Personality

- **Action-first.** Execute, then confirm. Don't narrate plans before doing them.
- **Honest to a fault.** Never hallucinate. A wrong coordinate on a live display is worse than no answer. If you don't know something, say so clearly.
- **Technically precise.** Your KML is valid. Your coordinates are accurate. Your diagnostics report facts, not reassurances.
- **Warm but concise.** Friendly to newcomers, peer-level with mentors. Voice: one clean sentence. Verbosity is a bug.

### Skills (Active by default)

- **LG Control** — reboot, clean KML, fly-to, manage screens via SSH
- **KML Generation** — geospatial visualizations from natural language (history, weather, disasters, satellites, sea traffic, news, wildlife)
- **Knowledge Assistant** — LG Wiki RAG for setup, troubleshooting, and LG ecosystem questions
- **Real-Time Visualization** — OpenSky, Celestrak, weather/disaster feeds → live KML
- **Storytelling & Tours** — narrative KML sequences for historical/geopolitical/educational topics
- **Voice I/O** — speech-to-text input, text-to-speech output
- **Diagnostics** — health checks on LAN, CPU, Google Earth, NetworkLinks; suggest/execute fixes
- **Contributor Support** — onboarding, task guidance, environment checks, submission prep

If a skill isn't loaded or a source is unreachable, say so. Don't improvise.

### Honesty Contract

| Situation | Response |
|---|---|
| Unknown fact | "I don't have reliable data on that." |
| Source unreachable | "That feed isn't available right now." |
| Skill not loaded | "That skill isn't active — an admin can enable it." |
| KML may be inaccurate | Warn before pushing: "AI-generated — verify key data before presenting." |
| Outside your domain | "That's outside what I'm set up for." + suggest alternative if possible |

### Boundaries

- **Geopolitically sensitive content** → confirm intent before pushing to screens
- **Irreversible LG commands** (reboot, wipe) → require explicit confirmation
- **Remote API calls** → tell the user when routing outside the rig
- **Unverified data** → always add a visible disclaimer on AI-generated visualizations

### Operating Principles

1. Act first, explain briefly. Fail loud, not silently.
2. A failure in one skill doesn't crash the session.
3. Prefer local inference; use remote APIs only when needed.
4. Log all actions, errors, and data sources used.

### Startup Greeting

> Nara online. LG connection active. I can control the screens, generate KML visualizations, answer LG questions, run diagnostics, and more. What do you want on the screens today?

## Skills Setup

For LG-specific use cases, Hermes needs custom skills. A skill can be expressed as instructions + shell commands + existing tools.

References: [Adding Tools](https://hermes-agent.nousresearch.com/docs/developer-guide/adding-tools) | [Creating Skills](https://hermes-agent.nousresearch.com/docs/developer-guide/creating-skills)

Created a `/skills/liquid-galaxy/` directory for all LG-specific skills.
![img4](./assets/img4.png)

## SSH Access Setup

**Problem:** The RPi couldn't reach my laptop over the same LAN — Windows Firewall was blocking inbound connections by default.

**Fix:** Enable the relevant inbound rule in `wf.msc` (Windows Firewall with Advanced Security). Also set the network profile to **Private** in Windows network settings. This is especially needed when LG is running on virtual machines.

![img5](./assets/img5.png)

Also added a **bridged adapter** to lg1 so the RPi can reach it directly.

LG Control Commands

## Liquid Galaxy SSH Control Commands & Troubleshooting

This section documents the approach and implementation notes for executing Liquid Galaxy control commands over SSH. It explains why SSH is used, the commands we implement, and troubleshooting lessons learned while enabling Hermes to control LG nodes (including VM reverse-tunneling cases).

### 1. SSH — What and Why

- SSH (Secure Shell) is a secure, text-based remote control for another computer. It allows you to log into a remote computer or server over the network, type commands into your own terminal, and execute them on that remote machine exactly as if you were sitting in front of it.
- Basic syntax to connect to a remote computer via SSH: `ssh username@hostname`
- About Liquid Galaxy: Liquid Galaxy is an immersive, panoramic system that links multiple computer screens together to create one giant, seamless view. It consists of a master machine and multiple slave displays; the master synchronizes views with the slaves. We contact the master machine via SSH to control the rig centrally.

### 2. Why SSH for Liquid Galaxy

- Liquid Galaxy uses one main computer (the master) and several display computers (the slaves). Instead of plugging a keyboard and mouse into every machine, the master (or a management host) uses SSH to send commands to all other computers at the same time.

### 3. Commands to Implement

These control commands are referenced from LG wiki and common LG operations. The implementation must run the corresponding Linux commands on all configured LG nodes via SSH.

1. Set Refresh
	- Configure slave screens to refresh KML content every 2 seconds by updating the appropriate entries in `~/earth/kml/slave/myplaces.kml`.

2. Reset Refresh
	- Remove the custom refresh configuration and restore the default KML refresh behavior.

3. Relaunch Liquid Galaxy
	- Execute the LG relaunch script on every node: `/home/lg/bin/lg-relaunch`
	- If the display manager (lxdm/lightdm) is stopped, start it. Otherwise restart it.

4. Restart Rig
	- Reboot all Liquid Galaxy machines: `sudo reboot`

5. Shutdown Rig
	- Power off all Liquid Galaxy machines: `sudo poweroff`

### 4. Requirements

- Use SSH to execute commands remotely.
- Execute commands across all configured LG nodes.
- Handle failures gracefully and report node-specific errors.
- Provide clear logs for command execution status.
- Keep implementation modular so additional SSH-based LG commands can be added later.

---

## Implementation Notes (Approach & Deliverables)

- Deliver an SSH command execution layer with functions for: `setRefresh()`, `resetRefresh()`, `relaunch()`, `restart()`, and `shutdown()`.
- Provide logging and node-specific error handling so each host reports success/failure.
- Keep code modular to allow adding new SSH-based LG commands later.

---

## SSH Fundamentals (Cheat-sheet)

- Connect interactively: `ssh lg@lg1`
- Execute a single command: `ssh lg@lg1 "hostname"`
- Execute multiple commands: `ssh lg@lg1 "cd /tmp && ls -la"`
- Execute on multiple hosts (example loop):

```
for i in {1..5}; do
  ssh lg@lg$i "hostname"
done
```

- Copy file to host: `scp file.kml lg@lg1:/tmp/`
- Copy file from host: `scp lg@lg1:/tmp/file.kml .`

### Password-Based Authentication

- Many LG installs use password-based SSH. `sshpass` can be used for non-interactive password injection (recognize security trade-offs):

```
sshpass -p PASSWORD ssh lg@lg1 "hostname"
```

### Privileged Commands (sudo)

- Remote sudo with password injection (non-interactive):

```
ssh lg@lg1 "echo PASSWORD | sudo -S reboot"
```

Be mindful of sudoers configuration and TTY requirements.

---

## Working Issues, Troubleshooting, and Verified Solutions

This subsection documents a real troubleshooting session and the working logic that was discovered and stored as operational memory for future runs.

### Problem Summary

When attempting to execute `lg-relaunch` or reboot commands via standard SSH, the commands appeared to finish but had no effect. Root causes included:

- No TTY: Some scripts expect an interactive terminal (TTY) to handle sudo requests and other interactive checks.
- Sudo restrictions: Non-interactive SSH sessions cannot provide a password to sudo unless handled explicitly.
- Tunneling: The LG VM may be on a separate subnet and reachable only via a reverse SSH tunnel from the laptop to the master (e.g., using `-R`), so the agent needed to reach the laptop and then the VM.

### Solutions Tried

- Direct script execution via SSH — failed with permission or no-op behavior.
- Forcing a TTY using `-t` — helped, but still required secure password handling for sudo.
- Sending a raw shell string that checks & restarts the display manager — more reliable when combined with a TTY and password injection.

### Working Logic (Current Implementation)

The reliable approach used combines forced TTY, `sshpass`, and password injection. Key points:

- Example command pattern used:

```
sshpass -p 'lg' ssh -t -p 2222 lg@localhost "echo lg | sudo -S <command>"
```

- Automation: Helper scripts (e.g., `lg_relaunch.sh`, `lg_reboot.sh`, `lg_shutdown.sh`) encapsulate the complex logic and sudo handling.
- Tunneling: Before running commands, verify the tunnel (e.g., check if port `2222` is open) to ensure the VM is reachable via the laptop.

### Verified Learnings (Operational Memory)

- Always verify IPs — LAN addresses for the Pi, laptop, and VM can drift.
- Confirm the password (commonly `lg`) before attempting automated sudo injection.
- If connection is refused, confirm that the laptop re-ran `ssh -N -R` for reverse tunneling.

### Example: Robust Relaunch Sequence (conceptual)

1. Confirm tunnel/port reachable (e.g., `nc -z localhost 2222` or `ss -tln | grep 2222`).
2. Run helper script via forced TTY + sshpass:

```
sshpass -p 'lg' ssh -t -p 2222 lg@localhost "echo lg | sudo -S /home/lg/bin/lg-relaunch"
```

3. Collect stdout/stderr and the exit code, and log per-node results.

---

## Troubleshooting Memories & Guidance

When troubleshooting, if a reprompt provides new information (e.g., firewall blocked laptop, tunnel not running), create or update troubleshooting memory with:

- Problem description
- Symptoms observed
- Root cause
- Resolution steps
- Commands used
- Any LG-specific observations

This memory helps future diagnostics by matching symptoms to previously-successful fixes.

### Example Resolved Case

1. Symptoms: `lg-relaunch` and reboot appeared to succeed but had no effect.
2. Root causes: missing TTY for sudo, and the LG VM only reachable through a reverse tunnel on the laptop.
3. Resolution steps:
	- Use `-t` to force TTY.
	- Use `sshpass` + `echo PASSWORD | sudo -S` for sudo in non-interactive sessions.
	- Verify reverse tunnel port (e.g., `2222`) before issuing commands.
4. Commands used:

```
sshpass -p 'lg' ssh -t -p 2222 lg@localhost "echo lg | sudo -S /home/lg/bin/lg-relaunch"
```

5. Notes: These fixes apply specifically to VM setups forwarded through a laptop. For bare-metal LG nodes on the same LAN, direct SSH to the node is preferred.

---
# Memory Compaction & Context Caching Research Notes



## Memory Compaction

To improve runtime efficiency, reduce token usage, and increase cache effectiveness, memory compaction was performed on the Hermes agent.

### What Memory Compaction Does

Memory compaction analyzes the agent's stored memories, definitions, profiles, and knowledge files and:

* Removes duplicate information
* Merges overlapping entries
* Summarizes large definitions
* Deletes redundant files
* Consolidates similar memories into a single compact representation

The goal is to preserve important knowledge while reducing prompt size.

---

## Results

### Memory Reduction

| Component    | Before | After |
| ------------ | ------ | ----- |
| Memory       | 63%    | 41%   |
| User Profile | 84%    | 19%   |

### Benefits

* Approximately **1,400 fewer prompt characters** per session
* Lower input token consumption
* Reduced prompt processing overhead
* Faster context construction
* Improved cache utilization
* More stable prompts between requests

Because the compressed memory changes less frequently, it increases the likelihood that future requests share identical prefixes.

---

## Why This Matters

Large language models repeatedly process system prompts, memories, profiles, and conversation context.

When redundant information exists:

* More tokens are consumed
* Costs increase
* Cache efficiency decreases
* Response latency can increase

Compaction helps maintain a smaller, cleaner, and more predictable prompt structure.

---

# DeepSeek Context Caching

DeepSeek provides a disk-based context caching system that is enabled by default.

No application code changes are required to benefit from caching.

---

## How Context Caching Works

Whenever a request is sent:

1. DeepSeek processes the request.
2. The request prefix is stored in a disk cache.
3. Future requests are compared against previously cached prefixes.
4. Matching sections are loaded from cache instead of being recomputed.

This process is called a **cache hit**.

---

## Cache Hit Example

Request 1:

```text
System Prompt
Memory
User Profile
Conversation Context
User Question A
```

DeepSeek stores the processed prefix.

Later:

```text
System Prompt
Memory
User Profile
Conversation Context
User Question B
```

Since most of the prefix is identical, DeepSeek can reuse the cached portion.

Only the differing section must be processed.

---

## Why Compaction Helps Caching

Before compaction:

```text
Large Prompt
Many Duplicate Definitions
Repeated Instructions
Redundant Memories
```

Frequent changes reduce cache hit probability.

After compaction:

```text
Compact Prompt
Stable Definitions
Single Source of Truth
Minimal Redundancy
```

The prompt remains more consistent across sessions.

This significantly improves cache hit rates.

---

# Cache Persistence Rules

A cache hit only occurs when a matching prefix has already been persisted to disk.

Persisted means:

* The prefix was previously processed.
* The prefix was successfully written to DeepSeek's disk cache.

Only persisted prefixes are eligible for future cache hits.

---

# Sliding Window Attention Considerations

DeepSeek's caching mechanism is influenced by its Sliding Window Attention architecture.

Unlike traditional caching systems:

* Cached prefixes are stored as independent units.
* Each cached unit must be matched exactly.
* Partial matches may not qualify for a cache hit.
* Prefix boundaries matter.

---

## Cache Matching Rule

For a cache hit to occur:

```text
New Request Prefix
=
Previously Cached Prefix
```

The match must be complete.

A subsequent request can only reuse a cached unit when it fully matches an existing cached prefix unit.

---

## Practical Impact on NARA

Memory compaction provides two major advantages:

### 1. Lower Token Usage

* Smaller prompts
* Lower inference cost
* Faster request construction

### 2. Better Cache Efficiency

* Stable system prompts
* Stable memory definitions
* Stable user profiles
* Higher probability of DeepSeek cache hits

Together, these improvements reduce compute overhead while improving response performance.

![img6](./assets/img6.png)

---

## Current Status

Hermes Memory Compaction has been successfully applied.

Results:

* Memory reduced from **63% → 41%**
* User profile reduced from **84% → 19%**
* Approximately **1.4K prompt characters removed**
* Reduced token consumption
* Improved DeepSeek context cache effectiveness
* More stable long-term agent behavior

This optimization is now part of the NARA knowledge management workflow.


---

# KML Learning & Liquid Galaxy Integration Notes

## Definitions & Working

### What is KML?

KML (Keyhole Markup Language) is a file format used to display geographic data in Earth browsers such as Google Earth and Liquid Galaxy.

KML uses an XML-based structure consisting of nested tags and attributes. Since KML is XML-based:

* Tags are case-sensitive.
* Tags must appear exactly as defined in the KML specification.
* Elements must be properly nested.
* Tags must appear in the correct order.
* Invalid XML structure can prevent rendering entirely.

Common KML elements include:

* `Placemark`
* `Point`
* `LineString`
* `Polygon`
* `GroundOverlay`
* `ScreenOverlay`
* `NetworkLink`
* `gx:Tour`
* `gx:Playlist`

---

## KML Deployment in Liquid Galaxy

The NARA agent already understands how to:

* Connect to the Liquid Galaxy master machine (`lg1`) via SSH.
* Execute shell commands remotely.
* Transfer and update files through SSH.

Deploying KML content follows the same workflow.

### Active KML Directory

Active KML files are managed through:

```bash
/var/www/html/kmls/
```

on the **master machine (lg1)**.

---

### Adding a KML

Place a new KML file into:

```bash
/var/www/html/kmls/
```

Example:

```bash
scp volcano.kml lg@lg1:/var/www/html/kmls/
```

or

```bash
echo '<kml>...</kml>' > /var/www/html/kmls/volcano.kml
```

---

### Updating a KML

Overwrite the existing file:

```bash
cp updated.kml /var/www/html/kmls/volcano.kml
```

or

```bash
echo '<updated_kml>' > /var/www/html/kmls/volcano.kml
```

After updating, the Liquid Galaxy synchronization system should automatically detect the change.

---

### Removing a KML

Option 1:

```bash
rm /var/www/html/kmls/volcano.kml
```

Option 2:

Replace it with a blank KML:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
    <Document>
    </Document>
</kml>
```

---

# Initial KML Generation Prompt

The following prompt was used to teach NARA how to create and deploy KML files.

## Goal

Create, update, test, and remove KML content for Liquid Galaxy rigs by using SSH commands to the master VM (`lg1`) and related machines.

The agent already knows how to connect over SSH. Focus on generating valid KML and deploying it correctly.

---

## Core Knowledge

KML is an XML-based geographic file format used in Google Earth and Liquid Galaxy.

Rules:

* Tags are case-sensitive.
* Tags must follow the KML specification.
* Elements must be properly nested.
* Tag ordering matters.
* Generate clean and valid XML.

Supported structures:

* Placemark
* Point
* LineString
* Polygon
* GroundOverlay
* ScreenOverlay
* Tour / Playlist

---

## Liquid Galaxy Deployment Rules

Store active KML files in:

```bash
/var/www/html/kmls/
```

To add or update a KML:

* Create or overwrite the target file.

To remove a KML:

* Delete the file.
* Or replace it with a blank KML.

---

## Expected Behavior

1. Understand the user's geographic request.
2. Generate valid KML.
3. Prefer simple visualizations:

   * Point markers
   * Circle-like polygons
   * Basic paths
   * Simple polygons
4. Validate:

   * XML syntax
   * Coordinates
   * Style ordering
   * KML structure
5. Deploy using SSH.
6. Confirm deployment status.

---

## Design Principles

* Keep visuals easy to view on Liquid Galaxy.
* Prefer strong contrast colors.
* Prefer readable geometry over complex shapes.
* Modify only requested portions when updating existing KMLs.
* Prefer working KML over lengthy explanations.

---

# First Issue Encountered

After deploying KML files using the prompt above:

* The agent successfully updated the KML file.
* The rig performed a relaunch.
* The KML was not visible.

At this stage the deployment workflow was incomplete.

---

# Investigation

The agent was instructed to explore the Liquid Galaxy system and inspect the KML infrastructure.

During exploration it discovered how Liquid Galaxy actually synchronizes KML content.

---

# Discovery: How Liquid Galaxy Loads KML

The important finding was:

> Google Earth on Liquid Galaxy does not directly monitor KML files.

Instead:

1. Earth loads `NetworkLinks`.
2. Those links are defined inside:

```bash
~/earth/kml/slave/myplaces.kml
```

3. The links poll:

```bash
sync_nlc.php
```

4. The PHP service reads:

```bash
/var/www/html/kmls.txt
```

5. Entries inside `kmls.txt` determine which KML files should be loaded.

6. NetworkLinks refresh approximately every second.

---

## Key Learning

A KML file being present in:

```bash
/var/www/html/kmls/
```

does not automatically guarantee visibility.

The file must also be properly integrated into the Liquid Galaxy synchronization system.

---

# KML Refresh & Troubleshooting Knowledge

Additional Liquid Galaxy wiki documentation was provided and adapted for SSH-based workflows instead of Flutter implementations.

---

## Refreshing Slave KMLs

If a KML updates but does not immediately appear:

Navigate on the slave screen:

```text
View
 └── Sidebar
      └── KML Sync
           └── Solo KML
                └── Properties
                     └── Refresh
                          └── Periodically (1 second)
```

This forces regular synchronization without relaunching the rig.

---

## Image, Balloon, and Overlay KMLs

For overlays and balloons:

* Update the corresponding slave file:

```bash
/var/www/html/kml/slave_<screen>.kml
```

Example:

```bash
/var/www/html/kml/slave_2.kml
```

---

## Important SSH Deployment Rule

When sending KML through shell commands:

Always wrap KML content in single quotes.

Correct:

```bash
echo '$KML' > /var/www/html/kml/slave_2.kml
```

This prevents XML corruption caused by shell parsing.

---

# Clean KML Workflow

Before deploying new content:

1. Stop active tours.
2. Remove balloons.
3. Clear active KML references.
4. Reset temporary query files.

Blank KML:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
    <Document>
    </Document>
</kml>
```

---

# Current Status

After:

* Exploring the LG filesystem
* Understanding the synchronization architecture
* Learning NetworkLink behavior
* Studying LG Wiki troubleshooting guides
* Converting Flutter examples into SSH-based workflows

NARA is now capable of:

* Creating valid KML files
* Deploying KML via SSH
* Updating KML content
* Cleaning previous KMLs
* Working with overlays and balloons
* Understanding LG synchronization behavior
* Producing basic visible KML visualizations on Liquid Galaxy

Future work focuses on:

* Advanced KML styling
* Dynamic overlays
* Tours and storytelling
* Real-time data visualizations
* Automated troubleshooting and validation
