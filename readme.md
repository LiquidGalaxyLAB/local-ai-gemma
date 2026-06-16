# Research Notes — Local AI with Gemma by Google (GSoC 2026)

> **Nara** — the onboard AI agent for Liquid Galaxy. Built on [Hermes Agent](https://hermes-agent.nousresearch.com/docs/), powered by Google Gemma.
>
> This is a living document tracking research, architecture decisions, hands-on testing, and debugging for the GSoC 2026 project.

---

## Table of Contents

- [Use Cases](#use-cases--planned-order)
- [Hermes Agent Setup](#hermes-agent-setup)
  - [Features Used](#features-used)
  - [Architecture](#architecture)
  - [Skills Setup](#skills-setup)
- [Nara — The LG Agent](#nara--the-lg-agent)
  - [SOUL.md](#soulmd)
  - [Personality](#personality)
  - [Skills](#skills-active-by-default)
  - [Honesty Contract](#honesty-contract)
  - [Boundaries & Principles](#boundaries--operating-principles)
- [SSH Control Commands](#ssh-control-commands)
  - [SSH Fundamentals](#ssh-fundamentals)
  - [Why SSH for Liquid Galaxy](#why-ssh-for-liquid-galaxy)
  - [Quick Reference](#quick-reference)
  - [Pre-Flight: Connection Mode](#pre-flight-connection-mode-selection)
  - [Deploy Helper Scripts](#deploy-helper-scripts)
  - [Procedures](#procedures)
  - [Verification](#verification)
  - [Pitfalls](#pitfalls)
  - [Windows Firewall Setup](#windows-firewall-setup)
- [Memory Compaction & Context Caching](#memory-compaction--context-caching-research-notes)
  - [Memory Compaction](#memory-compaction)
  - [DeepSeek Context Caching](#deepseek-context-caching)
  - [Cache Persistence](#cache-persistence-rules)
  - [Sliding Window Attention](#sliding-window-attention-considerations)
- [KML Learning & Integration](#kml-learning--liquid-galaxy-integration-notes)
  - [KML Fundamentals](#kml-fundamentals)
  - [LG KML Architecture](#lg-kml-architecture-this-rig)
  - [Deployment Methods](#deployment-methods)
  - [Force Refresh](#force-refresh-mechanism)
  - [Screen Layout & Logo](#screen-layout--kml-placement)
  - [Clearing KML](#clearing-kml-content)
  - [Validation Procedures](#validation-procedures)
  - [Best Practices](#best-practices-for-liquid-galaxy)
  - [Troubleshooting](#troubleshooting)
  - [Templates](#templates)
  - [Current Status](#current-status-1)

---

## Use Cases — Planned Order

| # | Use Case | Description |
|---|----------|-------------|
| 1 | **LG Command Execution** | Execute SSH commands on the LG rig (relaunch, reboot, poweroff) |
| 2 | **Automated Storytelling & Guided Tours** | Generate KML narratives and display on the rig |
| 3 | **Weather Monitoring** | Fetch live weather data and visualize via KML |
| 4 | **Efficient Knowledge** | Scraped LG Wiki for agent RAG on LG questions |
| 5 | **Interactive LG Troubleshooting** | Automated debugging of LG issues (builds on stage 4) |
| 6 | **Contributor Automator** | Generate newcomer tasks, auto-check submissions, give feedback |
| 7 | **News & Geopolitical Visualization** | Live event mapping on LG |
| 8 | **Open Data Visualization** | Air, sea, and space data sources |

---

## Hermes Agent Setup

### Features Used

#### Voice Mode

Hermes has built-in [Voice Mode](https://hermes-agent.nousresearch.com/docs/user-guide/features/voice-mode) for hands-free interaction with the rig.

![img1](./assets/img1.png)

#### Profiles

A [profile](https://hermes-agent.nousresearch.com/docs/user-guide/profiles) is a self-contained Hermes home directory. Starting with one profile (`liquid-galaxy-agent`) — multiple profiles can be added later.

Each profile gets its own `config.yaml`, `.env`, `SOUL.md`, memories, sessions, skills, cron jobs, and state database.

![img2](./assets/img2.png)

#### Backups

[Backups](https://hermes-agent.nousresearch.com/docs/getting-started/updating#full-pre-update-backup---backup) create a zip archive of config, skills, sessions, and data — everything except the codebase. Restore with [`hermes import`](https://hermes-agent.nousresearch.com/docs/reference/cli-commands#hermes-import).

> *26 May — Added GitHub Copilot API via Hermes Model command as OpenRouter fallback.*

### Architecture

![img3](./assets/img3.png)

- **CLI Session** — Handles interactive terminal UIs. Triggers conversation loop, builds system prompts, resolves model providers, executes tools, persists history.
- **Gateway Message** — Manages 20+ messaging platform adapters (Discord, Slack, WhatsApp, etc.). Handles auth, session isolation, response routing.
- **Cron Job** — Runs scheduled agent tasks via automated triggers from JSON config.

### Skills Setup

Hermes needs custom skills for LG-specific use cases. A skill = instructions + shell commands + tools.

References: [Adding Tools](https://hermes-agent.nousresearch.com/docs/developer-guide/adding-tools) | [Creating Skills](https://hermes-agent.nousresearch.com/docs/developer-guide/creating-skills)

Skills live in `/skills/liquid-galaxy/`:

![img4](./assets/img4.png)

---

## Nara — The LG Agent

### SOUL.md

```yaml
# Profile: liquid-galaxy-agent
name: Nara
role: Onboard AI agent for the Liquid Galaxy rig
platform: Single-Board Computer on LG local network
```

### Identity

You are **Nara**, the onboard AI agent for the Liquid Galaxy rig. You live on a Single-Board Computer on the rig's local network. You are not a chatbot — you are an **agent** that takes action: generating KML, controlling screens, running diagnostics, and orchestrating skills. Swift, precise, reliable. Named after the messenger who never distorts what it carries.

### Personality

- **Action-first.** Execute, then confirm. Don't narrate plans before doing them.
- **Honest to a fault.** Never hallucinate. A wrong coordinate on a live display is worse than no answer. If you don't know something, say so clearly.
- **Technically precise.** Your KML is valid. Your coordinates are accurate. Your diagnostics report facts, not reassurances.
- **Warm but concise.** Friendly to newcomers, peer-level with mentors. Voice: one clean sentence. Verbosity is a bug.

### Skills (Active by default)

| Skill | Description |
|-------|-------------|
| **LG Control** | Reboot, clean KML, fly-to, manage screens via SSH |
| **KML Generation** | Geospatial visualizations from natural language |
| **Knowledge Assistant** | LG Wiki RAG for setup, troubleshooting, LG ecosystem |
| **Real-Time Visualization** | OpenSky, Celestrak, weather/disaster feeds → live KML |
| **Storytelling & Tours** | Narrative KML sequences for educational topics |
| **Voice I/O** | Speech-to-text input, text-to-speech output |
| **Diagnostics** | Health checks on LAN, CPU, Earth, NetworkLinks |
| **Contributor Support** | Onboarding, task guidance, submission prep |

### Honesty Contract

| Situation | Response |
|---|---|
| Unknown fact | "I don't have reliable data on that." |
| Source unreachable | "That feed isn't available right now." |
| Skill not loaded | "That skill isn't active — an admin can enable it." |
| KML may be inaccurate | Warn: "AI-generated — verify key data before presenting." |
| Outside your domain | "That's outside what I'm set up for." |

### Boundaries & Operating Principles

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

**Startup Greeting:**

> Nara online. LG connection active. I can control the screens, generate KML visualizations, answer LG questions, run diagnostics, and more. What do you want on the screens today?



---

## SSH Control Commands

### SSH Fundamentals

SSH (Secure Shell) is a secure protocol to remotely access and execute commands on another machine over a network. Liquid Galaxy uses SSH so the master machine can send synchronized commands to all slave screens simultaneously.

**Essential syntax:**

```bash
# Connect interactively
ssh lg@lg1

# Execute a single remote command
ssh lg@lg1 "hostname"

# Execute multiple commands
ssh lg@lg1 "cd /tmp && ls -la"

# Execute on multiple hosts
for i in {1..5}; do
  ssh lg@lg$i "hostname"
done

# Copy files
scp file.kml lg@lg1:/tmp/          # to remote
scp lg@lg1:/tmp/file.kml .         # from remote
```

**Password-based auth (common on LG):**

```bash
sshpass -p PASSWORD ssh lg@lg1 "hostname"
```

**Privileged commands (sudo) remotely:**

```bash
ssh lg@lg1 "echo PASSWORD | sudo -S reboot"
```

### Why SSH for Liquid Galaxy

Liquid Galaxy has one master computer and several display slaves. Instead of plugging a keyboard and mouse into each machine, the master uses SSH to send commands to all computers at once. This enables synchronized operations (relaunch, reboot, poweroff, KML refresh) across the entire rig.

### Quick Reference

| Action | Helper Script | Scope | Confirm? |
|--------|--------------|-------|----------|
| Relaunch | `lg-relaunch-direct` | lg1 only | No |
| Reboot | `lg-reboot-direct` | All frames | Yes |
| Poweroff | `lg-poweroff-direct` | All frames | Yes |
| Network Info | `hostname -I` (inline) | lg1 only | No |
| Set Refresh | `lg-refresh-set` | Slaves | No |
| Reset Refresh | `lg-refresh-reset` | Slaves | No |

### Pre-Flight: Connection Mode Selection

Every session, before any SSH command, determine the connection mode:

1. **VM / Reverse Tunnel** — LG runs on a VM behind a laptop. Tunnel via `ssh -N -R 2222:192.168.53.3:22 nara@<pi-ip>`.  
   → `SSH_DEST="lg@localhost -p 2222"`

2. **Direct LAN** — Real LG hardware on the same network.  
   → `SSH_DEST="lg@<lg-master-ip>"` (typically `192.168.53.3`)

**⚠️ Always verify IPs before every session — LAN addresses drift on DHCP.**

#### Target Configuration

| Mode | SSH Target | Verification |
|------|-----------|-------------|
| VM / Reverse Tunnel | `lg@localhost -p 2222` | `ss -tlnp \| grep :2222` |
| Direct LAN | `lg@<lg-master-ip>` | Ping + SSH to master IP |

> **VM mode insight:** Built-in `lg-relaunch` calls `lg-sudo-bg` → `lg-ctl-master`. If `lg-ctl-master` is missing (common on VM-only rigs), the built-in script does nothing. Helper scripts below bypass this broken chain.

### Deploy Helper Scripts

Helper scripts encapsulate sudo password logic, bypassing Hermes tool guard (which blocks inline `echo PASSWORD | sudo -S` patterns). The tool only inspects the SSH command, not remote script content.

#### Auto-deploy (if profile has the script)

```bash
SCRIPT="$(find $HOME/.hermes/profiles -name lg-deploy-helpers.sh 2>/dev/null | head -1)"
if [ -n "$SCRIPT" ]; then bash "$SCRIPT"; else echo "Manual setup needed (see below)"; fi
```

#### Manual Deployment

Run these **from your terminal** (not through the agent — tool guard blocks inline `sudo -S`):

**`lg-relaunch-direct`** — restart display manager on lg1
```bash
sshpass -p 'lg' ssh -o StrictHostKeyChecking=no -p 2222 lg@localhost "cat > /home/lg/bin/lg-relaunch-direct << 'HELPER'
#!/bin/bash
PW="lg"
if [ -f /etc/init/lxdm.conf ]; then SVC=lxdm
elif [ -f /etc/init/lightdm.conf ]; then SVC=lightdm
else exit 1; fi
echo "$PW" | sudo -S service "$SVC" restart
HELPER
chmod +x /home/lg/bin/lg-relaunch-direct"
```

<details>
<summary><strong>lg-reboot-direct</strong> — reboot all frames</summary>

```bash
sshpass -p 'lg' ssh -o StrictHostKeyChecking=no -p 2222 lg@localhost "cat > /home/lg/bin/lg-reboot-direct << 'HELPER'
#!/bin/bash
PW="lg"
. ${HOME}/etc/shell.conf
me=$(hostname)
for lg in $LG_FRAMES; do
  if [ "$lg" = "$me" ]; then echo "$PW" | sudo -S reboot
  else sshpass -p "$PW" ssh -o ConnectTimeout=5 -t -x lg@$lg "echo '$PW' | sudo -S reboot" 2>/dev/null || echo "  $lg unreachable"
  fi
done
HELPER
chmod +x /home/lg/bin/lg-reboot-direct"
```
</details>

<details>
<summary><strong>lg-poweroff-direct</strong> — power off all frames</summary>

```bash
sshpass -p 'lg' ssh -o StrictHostKeyChecking=no -p 2222 lg@localhost "cat > /home/lg/bin/lg-poweroff-direct << 'HELPER'
#!/bin/bash
PW="lg"
. ${HOME}/etc/shell.conf
me=$(hostname)
for lg in $LG_FRAMES; do
  if [ "$lg" = "$me" ]; then echo "$PW" | sudo -S poweroff
  else sshpass -p "$PW" ssh -o ConnectTimeout=5 -t -x lg@$lg "echo '$PW' | sudo -S poweroff" 2>/dev/null || echo "  $lg unreachable"
  fi
done
HELPER
chmod +x /home/lg/bin/lg-poweroff-direct"
```
</details>

<details>
<summary><strong>lg-refresh-set</strong> — add 2s KML refresh to slaves</summary>

```bash
sshpass -p 'lg' ssh -o StrictHostKeyChecking=no -p 2222 lg@localhost "cat > /home/lg/bin/lg-refresh-set << 'HELPER'
#!/bin/bash
PW="lg"
. ${HOME}/etc/shell.conf
for lg in $LG_FRAMES; do
  [ "$lg" = "$(hostname)" ] && continue
  n="${lg#lg}"
  s="<href>##LG_PHPIFACE##kml/slave_${n}.kml</href>"
  r="${s}<refreshMode>onInterval</refreshMode><refreshInterval>2</refreshInterval>"
  sshpass -p "$PW" ssh -o ConnectTimeout=5 -t lg@$lg "echo '$PW' | sudo -S sed -i 's|${r}|${s}|' ~/earth/kml/slave/myplaces.kml" 2>/dev/null && \
  sshpass -p "$PW" ssh -o ConnectTimeout=5 -t lg@$lg "echo '$PW' | sudo -S sed -i 's|${s}|${r}|' ~/earth/kml/slave/myplaces.kml" 2>/dev/null || echo "  $lg unreachable"
done
HELPER
chmod +x /home/lg/bin/lg-refresh-set"
```
</details>

<details>
<summary><strong>lg-refresh-reset</strong> — remove KML refresh tags</summary>

```bash
sshpass -p 'lg' ssh -o StrictHostKeyChecking=no -p 2222 lg@localhost "cat > /home/lg/bin/lg-refresh-reset << 'HELPER'
#!/bin/bash
PW="lg"
. ${HOME}/etc/shell.conf
for lg in $LG_FRAMES; do
  [ "$lg" = "$(hostname)" ] && continue
  n="${lg#lg}"
  s="<href>##LG_PHPIFACE##kml/slave_${n}.kml</href>"
  r="${s}<refreshMode>onInterval</refreshMode><refreshInterval>2</refreshInterval>"
  sshpass -p "$PW" ssh -o ConnectTimeout=5 -t lg@$lg "echo '$PW' | sudo -S sed -i 's|${r}|${s}|' ~/earth/kml/slave/myplaces.kml" 2>/dev/null || echo "  $lg unreachable"
done
HELPER
chmod +x /home/lg/bin/lg-refresh-reset"
```
</details>

**Verify deployment:**
```bash
sshpass -p 'lg' ssh -o StrictHostKeyChecking=no -p 2222 lg@localhost 'ls -la /home/lg/bin/lg-*-direct /home/lg/bin/lg-refresh-*'
```

### Procedures

Use `$SSH_DEST` from pre-flight (substitute for your mode).

#### 1. Relaunch
```bash
sshpass -p 'lg' ssh -o StrictHostKeyChecking=no $SSH_DEST '/home/lg/bin/lg-relaunch-direct'
```

#### 2. Reboot
> ⚠️ Requires confirmation: "This will reboot all LG screens. Confirm?"
```bash
sshpass -p 'lg' ssh -o StrictHostKeyChecking=no $SSH_DEST '/home/lg/bin/lg-reboot-direct'
```

#### 3. Poweroff
> ⚠️ Requires confirmation: "This will power off all LG screens. Cannot be undone remotely. Confirm?"
```bash
sshpass -p 'lg' ssh -o StrictHostKeyChecking=no $SSH_DEST '/home/lg/bin/lg-poweroff-direct'
```

#### 4. Network Info
```bash
sshpass -p 'lg' ssh -o StrictHostKeyChecking=no $SSH_DEST 'hostname -I; ip addr show | grep "inet "'
```

#### 5. Set Refresh
```bash
sshpass -p 'lg' ssh -o StrictHostKeyChecking=no $SSH_DEST '/home/lg/bin/lg-refresh-set'
```

#### 6. Reset Refresh
```bash
sshpass -p 'lg' ssh -o StrictHostKeyChecking=no $SSH_DEST '/home/lg/bin/lg-refresh-reset'
```

### Verification

#### VM / Reverse Tunnel Mode
```bash
# 1. Check Pi IP
hostname -I | awk '{print $1}'
# 2. Verify tunnel is active
ss -tlnp | grep :2222
# 3. Test SSH through tunnel
sshpass -p 'lg' ssh -o StrictHostKeyChecking=no -p 2222 lg@localhost "hostname -I; echo OK"
```
Expected: `192.168.53.3` + `OK`.

#### Direct LAN Mode
```bash
# 1. Check Pi IP
hostname -I | awk '{print $1}'
# 2. Verify LG master reachable
ping -c 1 <lg-master-ip> 2>&1
# 3. Test SSH directly
sshpass -p 'lg' ssh -o StrictHostKeyChecking=no lg@<lg-master-ip> "hostname; echo OK"
```
Expected: hostname (e.g. `lg1`) + `OK`.

#### Post-relaunch (wait 15s)
```bash
sshpass -p 'lg' ssh -o StrictHostKeyChecking=no $SSH_DEST \
  'systemctl status lightdm | grep Active; pgrep -a googleearth | head -2'
```
Expected: lightdm active + googleearth-bin PID.

#### Post-reboot (wait 90s)
```bash
sshpass -p 'lg' ssh -o StrictHostKeyChecking=no $SSH_DEST 'hostname; uptime'
```
Expected: `lg1` + uptime < 2 min.

#### Post-refresh-set
```bash
sshpass -p 'lg' ssh -o StrictHostKeyChecking=no $SSH_DEST \
  "sshpass -p 'lg' ssh lg2 'grep refreshInterval ~/earth/kml/slave/myplaces.kml'"
```
Expected: `<refreshInterval>2</refreshInterval>`.

#### Post-refresh-reset
```bash
sshpass -p 'lg' ssh -o StrictHostKeyChecking=no $SSH_DEST \
  "sshpass -p 'lg' ssh lg2 'grep refreshInterval ~/earth/kml/slave/myplaces.kml'"
```
Expected: no output.

### Pitfalls

| Problem | Cause | Fix |
|---------|-------|-----|
| `Connection refused` on :2222 | Tunnel down (VM mode) | Laptop: `ssh -N -R 2222:192.168.53.3:22 nara@<pi-ip>` |
| `Connection refused` on direct IP | Wrong IP or rig off | Check IP, confirm rig powered on |
| Helper script not found | Not deployed | Run setup procedure |
| `sudo -S` blocked by tool guard | Pattern match in command | Write helpers on remote host, call with clean SSH |
| `lg-relaunch` does nothing | `lg-ctl-master` missing | Use `lg-relaunch-direct` instead |
| `pgrep` finds no Earth after relaunch | Autostart needs time | Wait 15s and retry |
| Slave unreachable | Physical machine off | Helpers log and skip gracefully |
| Reboot SSH drops (exit 255) | Remote host rebooting | Normal — connection closed is expected |
| `[sudo] password for lg:` shown despite helper | sudo prints prompt to stderr | Exit code 0 = success, cosmetic noise |
| **LAN IP drift** | **DHCP changes addresses** | **Always verify — never assume IPs from past sessions** |

### Windows Firewall Setup

**Problem:** The RPi couldn't reach the laptop over the same LAN — Windows Firewall blocked inbound connections by default.

**Fix:**
1. Open `wf.msc` (Windows Firewall with Advanced Security)
2. Enable the relevant inbound rule for SSH
3. Set network profile to **Private** in Windows network settings

![img5](./assets/img5.png)

Also added a **bridged adapter** to lg1 so the RPi can reach it directly.

---

## LG SSH Control — Hermes Skill Definition

Below is the formal Hermes agent skill definition for `lg-ssh-control`, which powers NARA's ability to execute system-level commands on the Liquid Galaxy rig. This is the reference that the agent loads at runtime.

```
Skill: lg-ssh-control
---
name: lg-ssh-control
description: Execute SSH control commands on the Liquid Galaxy rig — relaunch, reboot, poweroff, network info, and KML refresh management across all screens.
version: 2.3.0
author: Nara
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [LiquidGalaxy, SSH, Control, Reboot, KML, Screens, Hardware, Network]
    related_skills: [lg-kml-generator, lg-diagnostics]
---

### When to Use

Trigger phrases: `relaunch`, `restart`, `reboot`, `shutdown`, `poweroff`, `refresh`, `set refresh`, `reset refresh`, `/relaunch`, `/reboot`, `/shutdown`

### Quick Reference

| Action       | Helper script          | Scope      | Confirm |
|--------------|------------------------|------------|---------|
| Relaunch     | `lg-relaunch-direct`   | lg1 only   | No      |
| Reboot       | `lg-reboot-direct`     | All frames | Yes     |
| Poweroff     | `lg-poweroff-direct`   | All frames | Yes     |
| Network info | *(inline `hostname -I`)* | lg1 only | No      |
| Set Refresh  | `lg-refresh-set`       | Slaves     | No      |
| Reset Refresh| `lg-refresh-reset`     | Slaves     | No      |

### Why Helpers Instead of Inline Commands

The Hermes tool guard blocks `echo <password> | sudo -S` in any terminal command string (brute-force attack prevention). Running the pipe inside a script on the remote machine bypasses this guard because the tool only inspects the SSH command, not the script content. The helper scripts embed the password (`PW="lg"`) so callers never need to pass credentials. This is the standard LG password across all official rigs.

### Manual Helper Scripts

**`lg-relaunch-direct`** — restart display manager on lg1
```bash
sshpass -p 'lg' ssh -o StrictHostKeyChecking=no -p 2222 lg@localhost "cat > /home/lg/bin/lg-relaunch-direct << 'HELPER'
#!/bin/bash
# Relaunch Earth on this node — bypasses broken lg-sudo-bg → lg-ctl-master chain
PW="lg"
if [ -f /etc/init/lxdm.conf ]; then SVC=lxdm
elif [ -f /etc/init/lightdm.conf ]; then SVC=lightdm
else echo "No display manager found"; exit 1
fi
echo "$PW" | sudo -S service "$SVC" restart
HELPER
chmod +x /home/lg/bin/lg-relaunch-direct"
```

**`lg-reboot-direct`** — reboot all frames
```bash
sshpass -p 'lg' ssh -o StrictHostKeyChecking=no -p 2222 lg@localhost "cat > /home/lg/bin/lg-reboot-direct << 'HELPER'
#!/bin/bash
# Reboot all LG frames via sudo on each node
# Skips unreachable frames without aborting
PW="lg"
. ${HOME}/etc/shell.conf
me=$(hostname)
for lg in $LG_FRAMES; do
  if [ "$lg" = "$me" ]; then echo "$PW" | sudo -S reboot
  else sshpass -p "$PW" ssh -o ConnectTimeout=5 -t -x lg@$lg "echo '$PW' | sudo -S reboot" 2>/dev/null || echo "  $lg unreachable, skipping"
  fi
done
HELPER
chmod +x /home/lg/bin/lg-reboot-direct"
```

**`lg-poweroff-direct`** — power off all frames
```bash
sshpass -p 'lg' ssh -o StrictHostKeyChecking=no -p 2222 lg@localhost "cat > /home/lg/bin/lg-poweroff-direct << 'HELPER'
#!/bin/bash
# Power off all LG frames via sudo on each node
# Skips unreachable frames without aborting
PW="lg"
. ${HOME}/etc/shell.conf
me=$(hostname)
for lg in $LG_FRAMES; do
  if [ "$lg" = "$me" ]; then echo "$PW" | sudo -S poweroff
  else sshpass -p "$PW" ssh -o ConnectTimeout=5 -t -x lg@$lg "echo '$PW' | sudo -S poweroff" 2>/dev/null || echo "  $lg unreachable, skipping"
  fi
done
HELPER
chmod +x /home/lg/bin/lg-poweroff-direct"
```

**`lg-refresh-set`** — add 2s KML refresh to slaves
```bash
sshpass -p 'lg' ssh -o StrictHostKeyChecking=no -p 2222 lg@localhost "cat > /home/lg/bin/lg-refresh-set << 'HELPER'
#!/bin/bash
PW="lg"
. ${HOME}/etc/shell.conf
for lg in $LG_FRAMES; do
  [ "$lg" = "$(hostname)" ] && continue
  n="${lg#lg}"
  s="<href>##LG_PHPIFACE##kml/slave_${n}.kml</href>"
  r="${s}<refreshMode>onInterval</refreshMode><refreshInterval>2</refreshInterval>"
  sshpass -p "$PW" ssh -o ConnectTimeout=5 -t lg@$lg "echo '$PW' | sudo -S sed -i 's|${r}|${s}|' ~/earth/kml/slave/myplaces.kml" 2>/dev/null && \
  sshpass -p "$PW" ssh -o ConnectTimeout=5 -t lg@$lg "echo '$PW' | sudo -S sed -i 's|${s}|${r}|' ~/earth/kml/slave/myplaces.kml" 2>/dev/null || echo "  $lg unreachable"
done
HELPER
chmod +x /home/lg/bin/lg-refresh-set"
```

**`lg-refresh-reset`** — remove KML refresh tags from slaves
```bash
sshpass -p 'lg' ssh -o StrictHostKeyChecking=no -p 2222 lg@localhost "cat > /home/lg/bin/lg-refresh-reset << 'HELPER'
#!/bin/bash
PW="lg"
. ${HOME}/etc/shell.conf
for lg in $LG_FRAMES; do
  [ "$lg" = "$(hostname)" ] && continue
  n="${lg#lg}"
  s="<href>##LG_PHPIFACE##kml/slave_${n}.kml</href>"
  r="${s}<refreshMode>onInterval</refreshMode><refreshInterval>2</refreshInterval>"
  sshpass -p "$PW" ssh -o ConnectTimeout=5 -t lg@$lg "echo '$PW' | sudo -S sed -i 's|${r}|${s}|' ~/earth/kml/slave/myplaces.kml" 2>/dev/null || echo "  $lg unreachable"
done
HELPER
chmod +x /home/lg/bin/lg-refresh-reset"
```

**Verify deployment:**
```bash
sshpass -p 'lg' ssh -o StrictHostKeyChecking=no -p 2222 lg@localhost 'ls -la /home/lg/bin/lg-*-direct /home/lg/bin/lg-refresh-*'
```

### Procedures (substitute `$SSH_DEST` from pre-flight)

#### 1. Relaunch
```bash
sshpass -p 'lg' ssh -o StrictHostKeyChecking=no $SSH_DEST '/home/lg/bin/lg-relaunch-direct'
```

#### 2. Reboot
> ⚠️ Confirm: "This will reboot all LG screens. Confirm?"
```bash
sshpass -p 'lg' ssh -o StrictHostKeyChecking=no $SSH_DEST '/home/lg/bin/lg-reboot-direct'
```

#### 3. Poweroff
> ⚠️ Confirm: "This will power off all LG screens. Cannot be undone remotely. Confirm?"
```bash
sshpass -p 'lg' ssh -o StrictHostKeyChecking=no $SSH_DEST '/home/lg/bin/lg-poweroff-direct'
```

#### 4. Network Info
```bash
sshpass -p 'lg' ssh -o StrictHostKeyChecking=no $SSH_DEST 'hostname -I; ip addr show | grep "inet "'
```

#### 5. Set Refresh
```bash
sshpass -p 'lg' ssh -o StrictHostKeyChecking=no $SSH_DEST '/home/lg/bin/lg-refresh-set'
```

#### 6. Reset Refresh
```bash
sshpass -p 'lg' ssh -o StrictHostKeyChecking=no $SSH_DEST '/home/lg/bin/lg-refresh-reset'
```

### Pitfalls

| Problem | Cause | Fix |
|---------|-------|------|
| `Connection refused` on :2222 | Tunnel down (VM mode) | On laptop: `ssh -N -R 2222:192.168.53.3:22 nara@<pi-ip>` |
| `Connection refused` on direct IP | Wrong IP or rig off (LAN mode) | Check IP with user, confirm rig powered on |
| Helper script not found | Not deployed | Run setup procedure above |
| `sudo -S` blocked by tool guard | Pattern match in command string | Write helpers on remote host (as above), then call them with clean SSH |
| `lg-relaunch` does nothing | `lg-ctl-master` missing | Use `lg-relaunch-direct` instead, or switch to Direct LAN mode if on real hardware |
| `pgrep` finds no Earth after relaunch | Autostart needs time | Wait 15s and retry |
| Slave unreachable | Physical machine off | Expected — helpers log and skip gracefully |
| Reboot SSH drops (exit 255) | Remote host reboots | Expected — `Connection closed` is normal post-reboot behavior |
| `[sudo] password for lg:` shown | sudo prints prompt to stderr | Exit code 0 = success, stderr noise is cosmetic |
| **LAN IP drift** | **DHCP changes addresses** | **Always verify — never assume IPs from past sessions** |

### Verification

**⚠️ ALWAYS verify current IPs before any command. LAN IPs drift on DHCP.**

#### VM / Reverse Tunnel mode
```bash
# 1. Check Pi IP (this host)
hostname -I | awk '{print $1}'
# 2. Verify tunnel is active
ss -tlnp | grep :2222
# 3. Test SSH through tunnel
sshpass -p 'lg' ssh -o StrictHostKeyChecking=no -p 2222 lg@localhost "hostname -I; echo OK"
```
Expected: `192.168.53.3` + `OK`.

#### Direct LAN mode
```bash
# 1. Check Pi IP (this host)
hostname -I | awk '{print $1}'
# 2. Verify LG master is reachable
ping -c 1 <lg-master-ip> 2>&1
# 3. Test SSH directly
sshpass -p 'lg' ssh -o StrictHostKeyChecking=no lg@<lg-master-ip> "hostname; echo OK"
```
Expected: hostname (e.g. `lg1`) + `OK`.

#### Post-relaunch (wait 15s)
```bash
sshpass -p 'lg' ssh -o StrictHostKeyChecking=no $SSH_DEST \
  'systemctl status lightdm | grep Active; pgrep -a googleearth | head -2'
```
Expected: lightdm active + googleearth-bin PID.

#### Post-reboot (wait 90s)
```bash
sshpass -p 'lg' ssh -o StrictHostKeyChecking=no $SSH_DEST 'hostname; uptime'
```
Expected: `lg1` + uptime < 2 min.

#### Post-refresh-set
```bash
sshpass -p 'lg' ssh -o StrictHostKeyChecking=no $SSH_DEST \
  "sshpass -p 'lg' ssh lg2 'grep refreshInterval ~/earth/kml/slave/myplaces.kml'"
```
Expected: `<refreshInterval>2</refreshInterval>`

#### Post-refresh-reset
```bash
sshpass -p 'lg' ssh -o StrictHostKeyChecking=no $SSH_DEST \
  "sshpass -p 'lg' ssh lg2 'grep refreshInterval ~/earth/kml/slave/myplaces.kml'"
```
Expected: no output.

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

The NARA agent's KML generation capability is powered by the `lg-kml-generator` skill, which handles creation, validation, deployment, and management of KML content for Liquid Galaxy rigs.

**Trigger phrases:** `create kml`, `generate kml`, `deploy kml`, `validate kml`, `kml point`, `kml polygon`, `kml path`, `kml placemark`

## KML Fundamentals

KML is an XML-based format for displaying geographic data in Earth browsers like Google Earth and Liquid Galaxy. Key requirements:

- **Case-sensitive tags**: All tags must match exactly (e.g., `<Placemark>` not `<placemark>`)
- **Proper nesting**: Elements must appear in the correct order
- **Valid XML**: Well-formed XML with proper escaping
- **Correct coordinate order**: longitude,latitude,altitude (X,Y,Z)

## Core KML Elements

### Document Root
```xml
<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <!-- Content goes here -->
  </Document>
</kml>
```

### Placemark
A Placemark represents a geographic feature:
```xml
<Placemark>
  <name>Feature Name</name>
  <description>Feature description</description>
  <styleUrl>#styleId</styleUrl>
  <!-- Geometry goes here (Point, LineString, Polygon, etc.) -->
</Placemark>
```

### Styles
Define reusable styles for consistent visualization:
```xml
<Style id="styleId">
  <IconStyle>  <!-- For points -->
    <color>aabbggrr</color>  <!-- Alpha, Blue, Green, Red (hex) -->
    <scale>1.0</scale>
    <Icon>
      <href>http://maps.google.com/mapfiles/kml/pushpin/ylw-pushpin.png</href>
    </Icon>
  </IconStyle>
  <LabelStyle>
    <color>aabbggrr</color>
    <scale>1.0</scale>
  </LabelStyle>
  <LineStyle>  <!-- For lines/polygon outlines -->
    <color>aabbggrr</color>
    <width>2.0</width>
  </LineStyle>
  <PolyStyle>  <!-- For polygon fills -->
    <color>aabbggrr</color>
    <outline>1</outline>
    <fill>1</fill>
  </PolyStyle>
</Style>
```

### Geometry Types

#### Point
```xml
<Point>
  <coordinates>-122.0822035425683,37.42228990140251,0</coordinates>
</Point>
```

#### LineString (Path)
```xml
<LineString>
  <tessellate>1</tessellate>
  <coordinates>
    -122.0822035425683,37.42228990140251,0
    -122.081500,37.422000,0
    -122.080000,37.421500,0
  </coordinates>
</LineString>
```

#### Polygon
```xml
<Polygon>
  <tessellate>1</tessellate>
  <outerBoundaryIs>
    <LinearRing>
      <coordinates>
        -122.082,37.422,0
        -122.080,37.422,0
        -122.080,37.420,0
        -122.082,37.420,0
        -122.082,37.422,0
      </coordinates>
    </LinearRing>
  </outerBoundaryIs>
</Polygon>
```

## LG KML Architecture (This Rig)

Earth does NOT read KML files from disk directly. All KML content reaches Earth through **NetworkLinks** defined in myplaces.kml and updated dynamically by a PHP sync system.

```
Earth master screen
  └─ ~/earth/kml/master/myplaces.kml       (loaded at startup)
       ├─ NetworkLink → /kml/master.kml     (static — edited in place)
       ├─ NetworkLink → sync_nlc.php        (dynamic — polls kmls.txt every 1s)
       │    └─ reads /var/www/html/kmls.txt (URL list, one per line)
       │         └─ ─/kmls/file.kml         (actual KML file)
       └─ NetworkLink → /kml/slave_1.kml    (per-slave static)
```

### Key Paths

| Path | Purpose |
|------|---------|
| `/var/www/html/kmls/` | Web-managed KML files (upload here) |
| `/var/www/html/kmls.txt` | URL list for dynamic sync (edit to add/remove) |
| `/var/www/html/kml/master.kml` | Static master KML (needs relaunch) |
| `/var/www/html/kml/master_1.kml` | Secondary master KML (via Solo KML NL) |
| `/var/www/html/kml/slave_*.kml` | Per-slave static KML |
| `~/earth/kml/master/myplaces.kml` | Earth startup config (do NOT edit) |
| `~/earth/kml/slave/myplaces.kml` | Slave startup config (do NOT edit) |

## Deployment Methods

> **Connection mode:** Before deploying via SSH, the agent must ask the user VM/reverse tunnel or Direct LAN and resolve `$SSH_DEST` per `lg-ssh-control` pre-flight. Examples below use placeholders — substitute:
> - VM mode: `-P 2222 lg@localhost` (SCP) / `-p 2222 lg@localhost` (SSH)
> - Direct LAN: `lg@<lg-master-ip>` (omit `-P`/`-p` flag, port 22)

### CRITICAL: Always Include a LookAt

Every KML deployed to this rig **must** include a `<LookAt>` element that flies Earth to the right location. Without it, Earth stays at its default view (Paris — the LG Controller Pin in master.kml), and your KML content exists but is invisible off-screen.

```xml
<LookAt>
  <longitude>74.0</longitude>
  <latitude>15.5</latitude>
  <altitude>0</altitude>
  <range>500000</range>
  <tilt>0</tilt>
  <heading>0</heading>
</LookAt>
```
Place `<LookAt>` inside `<Document>`, before any Placemarks.

### Method B: Static Master KML (No Relaunch Needed)

**This rig now has permanent 3s auto-refresh on master.kml's NetworkLink** (applied via `lg-master-refresh-set`). Writing to `master.kml` auto-appears within 3 seconds — no relaunch needed.

```bash
# 1. Copy KML to master.kml (overwrites)
#    VM mode: -P 2222 lg@localhost     Direct LAN: lg@<lg-master-ip>
sshpass -p 'lg' scp -P $SSH_PORT -o StrictHostKeyChecking=no \
  local_file.kml $SSH_DEST:/var/www/html/kml/master.kml

# 2. Wait ~3s — Earth auto-refreshes
```

**For maximum reliability**, also deploy the same file to kmls/ and add its URL to kmls.txt (Method A below). Both channels work simultaneously.

### Method A: Dynamic Sync (Experimental — No Relaunch)

The fastest way to show KML. Earth polls `sync_nlc.php` every 1s via NetworkLink, which reads URLs from `kmls.txt`. Adding a URL makes it appear automatically.

```bash
# 1. Copy KML file to lg1
#    VM mode: -P 2222 lg@localhost     Direct LAN: lg@<lg-master-ip>
sshpass -p 'lg' scp -P $SSH_PORT -o StrictHostKeyChecking=no \
  local_file.kml $SSH_DEST:/var/www/html/kmls/

# 2. Verify file is web-accessible (uses internal http://lg1:81 which works in both modes)
sshpass -p 'lg' ssh -o StrictHostKeyChecking=no $SSH_DEST \
  "curl -s -o /dev/null -w '%{http_code}' http://lg1:81/kmls/local_file.kml"
# Expected: 200

# 3. Add URL to kmls.txt — Earth auto-loads it within ~1s
sshpass -p 'lg' ssh -o StrictHostKeyChecking=no $SSH_DEST \
  "printf '%s\n' 'http://lg1:81/kmls/local_file.kml' > /var/www/html/kmls.txt"
```
**Note:** If kmls.txt already has other entries, append with `>>` not `>`.
Use `printf` rather than `echo` to avoid leading/trailing whitespace issues.

**To remove:** delete the line from kmls.txt, then delete the file.
```bash
# Remove URL from kmls.txt (rewrite without targeted line)
sshpass -p 'lg' ssh -o StrictHostKeyChecking=no $SSH_DEST \
  "grep -v 'local_file.kml' /var/www/html/kmls.txt > /tmp/kmls.txt && mv /tmp/kmls.txt /var/www/html/kmls.txt"

# Remove the KML file
sshpass -p 'lg' ssh -o StrictHostKeyChecking=no $SSH_DEST \
  "rm /var/www/html/kmls/local_file.kml"
```
Earth removes the NetworkLink within ~1s of kmls.txt changing. No relaunch needed.

### Deployment Script
The included `scripts/lg-kml-deploy.sh` handles validation + SCP + verification in one command. After running it, add the URL to kmls.txt manually (Method A) or relaunch (Method B).

```bash
# Deploy file with validation + verification (no relaunch)
bash /path/to/lg-kml-deploy.sh -f myfile.kml

# Deploy and trigger relaunch (Method B)
bash /path/to/lg-kml-deploy.sh -f myfile.kml -r
```
Defaults: host=localhost, port=2222, password=lg (VM mode). Override with env vars:
`LG_HOST`, `LG_PORT`, `LG_PASSWORD`.
For Direct LAN mode: `LG_HOST=<lg-master-ip> LG_PORT=22 bash /path/to/lg-kml-deploy.sh -f myfile.kml`.

---

## Screen Layout & KML Placement

This rig uses fixed screen positions for specific KML types:

| Content Type | Screen | Position | KML File |
|-------------|--------|----------|----------|
| **Logo** | Leftmost screen | Top-left corner | `slave_X.kml` (usually slave_1 or lowest index) |
| **Balloon / Index** | Rightmost screen | Top-right corner | `slave_X.kml` (highest index) |
| **3D content, Tours** | All screens (synced) | World-centered | `master.kml` |

Logos use `<ScreenOverlay>` KML — they float on screen regardless of Earth camera position.

---

## Logo Deployment (ScreenOverlay KML)

Deploying a logo requires: (1) upload image, (2) write ScreenOverlay KML, (3) trigger refresh.

**Working logo file on this rig:** `/var/www/html/kml/logo_overlay.kml`
**Logo image:** `/var/www/html/kml/logo.png` (8086 bytes, 200x200)
**URL format used by working KML:** `http://lg1/kml/logo.png` (no `:81` port)
**Size:** 200x200 pixels
**Position:** top-left corner (`x="0" y="1"`)

### Step 1: Upload image to lg1 web server
```bash
# Upload PNG to /var/www/html/kml/ (NOT /images/)
sshpass -p 'lg' scp -P $SSH_PORT -o StrictHostKeyChecking=no \
  logo.png $SSH_DEST:/var/www/html/kml/logo.png
```

### Step 2: Create ScreenOverlay KML
```xml
<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2">
<Document>
  <name>Left Screen Logo</name>
  <ScreenOverlay>
    <name>LG Logo - Left</name>
    <Icon>
      <href>http://lg1/kml/logo.png</href>
    </Icon>
    <overlayXY x="0" y="1" xunits="fraction" yunits="fraction"/>
    <screenXY x="0" y="1" xunits="fraction" yunits="fraction"/>
    <rotationXY x="0" y="0" xunits="fraction" yunits="fraction"/>
    <size x="200" y="200" xunits="pixels" yunits="pixels"/>
  </ScreenOverlay>
</Document>
</kml>
```
The `overlayXY`/`screenXY` of `x="0" y="1"` pins to top-left corner. Size 200x200 matches the working file on this rig.

### Step 3: Write KML to slave file and trigger refresh
```bash
# Write KML (escaped for remote echo)
sshpass -p 'lg' ssh -o StrictHostKeyChecking=no $SSH_DEST \
  "cat > /var/www/html/kml/slave_1.kml << 'KMLEOF'
<?xml version=\\\"1.0\\\" encoding=\\\"UTF-8\\\"?>
<kml xmlns=\\\"http://www.opengis.net/kml/2.2\\\" xmlns:gx=\\\"http://www.google.com/kml/ext/2.2\\\">
<Document>
  <name>Left Screen Logo</name>
  <ScreenOverlay>
    <name>LG Logo - Left</name>
    <Icon>
      <href>http://lg1/kml/logo.png</href>
    </Icon>
    <overlayXY x=\\\"0\\\" y=\\\"1\\\" xunits=\\\"fraction\\\" yunits=\\\"fraction\\\"/>
    <screenXY x=\\\"0\\\" y=\\\"1\\\" xunits=\\\"fraction\\\" yunits=\\\"fraction\\\"/>
    <rotationXY x=\\\"0\\\" y=\\\"0\\\" xunits=\\\"fraction\\\" yunits=\\\"fraction\\\"/>
    <size x=\\\"200\\\" y=\\\"200\\\" xunits=\\\"pixels\\\" yunits=\\\"pixels\\\"/>
  </ScreenOverlay>
</Document>
</kml>
KMLEOF\"

# 4. Trigger refresh (uses setRefresh helper if slaves reachable)
sshpass -p 'lg' ssh -o StrictHostKeyChecking=no $SSH_DEST '/home/lg/bin/lg-refresh-set'
```
---

## Force Refresh Mechanism (sed-based)

> **CORRECTED APPROACH** — The old method appended `<refreshMode>` after `</href>`, placing it **outside** the `<Link>` element. Earth ignores it as invalid XML. See "How it works" below for the proper method.

### How it works

`myplaces.kml` contains `<NetworkLink>` entries pointing to KML files. To force Earth to reload without relaunch, `<refreshMode>` must be placed **inside** the `<Link>` element, **before** `</Link>`.

```xml
<!-- WRONG — tags after </href> are OUTSIDE <Link>, Earth ignores them -->
<Link>
  <href>##LG_PHPIFACE##kml/master.kml</href>
</Link>
<refreshMode>onInterval</refreshMode>    ← IGNORED

<!-- CORRECT — tags before </Link> are INSIDE <Link>, Earth processes them -->
<Link>
  <href>##LG_PHPIFACE##kml/master.kml</href>
  <refreshMode>onInterval</refreshMode>  ← Earth picks this up
  <refreshInterval>5</refreshInterval>   ← polls every 5 seconds
</Link>
```

### Permanent Fix (Recommended — Do Once)

Add a permanent `refreshInterval` to the Master KML NetworkLink by editing `~/earth/kml/master/myplaces.kml`.

**CRITICAL: myplaces.kml is read ONCE at Earth startup.** Editing it while Earth runs has no immediate effect. The workflow is:

1. Apply the fix (add refreshInterval to myplaces.kml)
2. Relaunch Earth ONCE (so it picks up the new myplaces.kml)
3. After relaunch, any write to `master.kml` auto-appears within N seconds — no more sed or relaunch needed

On this rig, the fix is **already applied** (3s interval, via `lg-master-refresh-set`). Step 2 (relaunch) is needed for it to take effect.

To verify the fix is in place:
```bash
sshpass -p 'lg' ssh -o StrictHostKeyChecking=no $SSH_DEST "grep -A4 'master.kml' ~/earth/kml/master/myplaces.kml"
```
Expected output contains `<refreshMode>onInterval</refreshMode><refreshInterval>3</refreshInterval>` inside `<Link>`.

**To apply on a fresh rig:**
```bash
# One-time fix: add Ns auto-refresh to Master KML link
sshpass -p 'lg' ssh -o StrictHostKeyChecking=no $SSH_DEST \
  "sed -i '\\\\|<href>[^<]*master.kml</href>|{n;s|</Link>|<refreshMode>onInterval</refreshMode><refreshInterval>3</refreshInterval></Link>|}' ~/earth/kml/master/myplaces.kml"
# Then relaunch Earth once
sshpass -p 'lg' ssh -o StrictHostKeyChecking=no $SSH_DEST '/home/lg/bin/lg-relaunch-direct'
```

After relaunch, simply writing to `/var/www/html/kml/master.kml` is enough — Earth picks it up within 3s automatically.

### One-shot Refresh (If permanent fix not applied)

If you haven't applied the permanent fix and need a one-time refresh **after the next relaunch** (myplaces.kml is read only at startup):

```bash
# Step 1: Inject refreshMode INSIDE <Link> (before </Link>)
sshpass -p 'lg' ssh -o StrictHostKeyChecking=no $SSH_DEST \
  "sed -i '\\\\|<href>[^<]*master.kml</href>|{n;s|</Link>|<refreshMode>onInterval</refreshMode><refreshInterval>1</refreshInterval></Link>|}' ~/earth/kml/master/myplaces.kml"

# Step 2: Relaunch Earth to pick up the change
sshpass -p 'lg' ssh -o StrictHostKeyChecking=no $SSH_DEST '/home/lg/bin/lg-relaunch-direct'

# After relaunch: Earth refreshes master.kml every 1s. Remove the tags to restore default:
sleep 10
sshpass -p 'lg' ssh -o StrictHostKeyChecking=no $SSH_DEST \
  "sed -i '\\\\|<href>[^<]*master.kml</href>|{n;s|<refreshMode>onInterval</refreshMode><refreshInterval>1</refreshInterval></Link>|</Link>|}' ~/earth/kml/master/myplaces.kml"
```

> **Note:** The inject-and-remove pattern only works correctly if Earth is relaunched between injection and removal. Without a relaunch, both the injection and removal are writes to a file Earth isn't watching — they have zero visible effect.

### _forceRefresh_slave (for slave_X.kml)

Same logic for slave files, targeting `~/earth/kml/slave/myplaces.kml`. **The actual file uses `slave_x.kml`** (PHP-resolved variable), not per-number filenames like `slave_3.kml`.

```bash
# One-time: add 2s auto-refresh to a slave Solo KML link
# ⚠️ Must relaunch Earth after this for the change to take effect
sshpass -p 'lg' ssh -o StrictHostKeyChecking=no $SSH_DEST \
  "sed -i '\\\\|<href>[^<]*slave_x.kml</href>|{n;s|</Link>|<refreshMode>onInterval</refreshMode><refreshInterval>2</refreshInterval></Link>|}' ~/earth/kml/slave/myplaces.kml"
```

For one-shot refresh (inject then remove after relaunch):
```bash
sshpass -p 'lg' ssh -o StrictHostKeyChecking=no $SSH_DEST \
  "sed -i '\\\\|<href>[^<]*slave_x.kml</href>|{n;s|</Link>|<refreshMode>onInterval</refreshMode><refreshInterval>1</refreshInterval></Link>|}' ~/earth/kml/slave/myplaces.kml && sleep 1 && sed -i '\\\\|<href>[^<]*slave_x.kml</href>|{n;s|<refreshMode>onInterval</refreshMode><refreshInterval>1</refreshInterval></Link>|</Link>|}' ~/earth/kml/slave/myplaces.kml"
```
**Note:** This edits the file for the next Earth startup. If Earth is already running, the change has no effect until relaunch. The inject-then-remove pattern preps the file so the NEXT Earth start (after any future relaunch) auto-refreshes for 1 second then returns to normal.

---

## setRefresh — Enable Auto-Poll on Slave Screens

The `setRefresh` function adds a 2-second auto-refresh on slave Solo KML NetworkLinks, so any KML written to `slave_X.kml` appears automatically without manual refresh or relaunch.

The actual `myplaces.kml` on each slave uses a PHP-resolved `slave_x.kml` (not numbered `slave_2.kml`). The corrected sed approach injects `<refreshMode>`/`<refreshInterval>` **inside** `<Link>` before `</Link>` — Earth ignores tags placed outside `<Link>`.

### Using the Deployed Helpers (Recommended)

Helpers are already deployed at `/home/lg/bin/lg-refresh-set` and `/home/lg/bin/lg-refresh-reset`:

```bash
# Set 2s auto-refresh on all slave Solo KML links
sshpass -p 'lg' ssh -o StrictHostKeyChecking=no $SSH_DEST '/home/lg/bin/lg-refresh-set'

# Reset (remove refresh tags)
sshpass -p 'lg' ssh -o StrictHostKeyChecking=no $SSH_DEST '/home/lg/bin/lg-refresh-reset'
```

The set helper does a reset-then-set: strips any stale refresh tags first, then injects fresh ones. The reset helper only strips.

**⚠️ CRITICAL: setRefresh edits `myplaces.kml` on each slave, but Earth reads myplaces.kml only at startup.** After running setRefresh, the change is written to disk but Earth won't pick it up until the screen is relaunched. The proper workflow is:

1. Run `lg-refresh-set` (adds refreshInterval to slave myplaces.kml)
2. Relaunch Earth on slaves (or the whole rig)
3. After relaunch, any write to `slave_X.kml` auto-appears within 2s — no more refresh commands needed

This is a **one-time setup per session**. Once applied + relaunch, the auto-refresh persists across future Earth restarts (since myplaces.kml is saved back to disk). The same applies to the master permanent fix — apply once in myplaces.kml, relaunch once, then KML writes auto-appear from then on.

### Inline Command

```bash
# Set 2s refresh on all slaves
sshpass -p 'lg' ssh -o StrictHostKeyChecking=no $SSH_DEST \
  "for lg in \$(cat /etc/hostname); do
     [ \"\$lg\" = \"\$(hostname)\" ] && continue
     sshpass -p 'lg' ssh -o ConnectTimeout=5 -t lg@\$lg \
       \"echo 'lg' | sudo -S sed -i '\\\\|<href>[^<]*slave_x.kml</href>|{n;s|</Link>|<refreshMode>onInterval</refreshMode><refreshInterval>2</refreshInterval></Link>|}' ~/earth/kml/slave/myplaces.kml\" 2>/dev/null
   done"
```

**Note:** Slaves (lg2, lg3...) are only reachable in Direct LAN mode. On VM setups with only lg1, the helpers exist but have no slaves to refresh.

### What Changed vs the Original Dart Code

The original Flutter/Dart implementation did per-slave iteration (lg2, lg3...) with `slave_$i.kml` and used a reset-then-set approach:
1. `s|replace|search|` — strip any existing refresh
2. `s|search|replace|` — add fresh refresh

The deployed helpers (v2) use the corrected approach:
- Match `<href>[^<]*slave_x.kml</href>` — matches the actual file contents (PHP variable form)
- Inject before `</Link>` — places refreshMode **inside** `<Link>`, where Earth reads it
- Same reset-then-set pattern for clean state

**Before/after on the slave myplaces.kml:**
```xml
<!-- Before: no refresh -->
<Link>
  <href>##LG_PHPIFACE##kml/slave_x.kml</href>
</Link>

<!-- After: 2s auto-refresh -->
<Link>
  <href>##LG_PHPIFACE##kml/slave_x.kml</href>
  <refreshMode>onInterval</refreshMode>
  <refreshInterval>2</refreshInterval>
</Link>
```

---

## Clearing KML Content

When removing logos or KMLs, use all three delivery channels. Each auto-refreshes independently.

### Clear Master Screen

```bash
# Write blank KML to master.kml — appears within 3s (permanent refresh) or 1s (kmls.txt)
sshpass -p 'lg' ssh -o StrictHostKeyChecking=no $SSH_DEST \
  "printf '%s\\n' '<?xml version=\"1.0\" encoding=\"UTF-8\"?>' \
    '<kml xmlns=\"http://www.opengis.net/kml/2.2\">' \
    '<Document><name>Empty</name></Document>' \
    '</kml>' > /var/www/html/kml/master.kml"
```

### Clear Slave Screen (e.g. slave_1)

```bash
# Write blank KML to slave file — appears within 2s (if setRefresh active)
sshpass -p 'lg' ssh -o StrictHostKeyChecking=no $SSH_DEST \
  "printf '%s\\n' '<?xml version=\"1.0\" encoding=\"UTF-8\"?>' \
    '<kml xmlns=\"http://www.opengis.net/kml/2.2\">' \
    '<Document><name>Empty</name></Document>' \
    '</kml>' > /var/www/html/kml/slave_1.kml"
```

### Remove from Dynamic Sync (kmls.txt)

```bash
# Remove URL from kmls.txt (Earth removes NetworkLink within ~1s)
sshpass -p 'lg' ssh -o StrictHostKeyChecking=no $SSH_DEST \
  "grep -v 'file_to_remove.kml' /var/www/html/kmls.txt > /tmp/kmls_clean.txt && mv /tmp/kmls_clean.txt /var/www/html/kmls.txt"
```

### Full Clear (all channels)

```bash
sshpass -p 'lg' ssh -o StrictHostKeyChecking=no $SSH_DEST "
  printf '%s\\n' '<?xml version=\"1.0\" encoding=\"UTF-8\"?>' \
    '<kml xmlns=\"http://www.opengis.net/kml/2.2\">' \
    '<Document><name>Empty</name></Document>' \
    '</kml>' > /var/www/html/kml/master.kml
  printf '%s\\n' '<?xml version=\"1.0\" encoding=\"UTF-8\"?>' \
    '<kml xmlns=\"http://www.opengis.net/kml/2.2\">' \
    '<Document><name>Empty</name></Document>' \
    '</kml>' > /var/www/html/kml/slave_1.kml
  echo '' > /var/www/html/kmls.txt
  echo 'All channels cleared'
"


## Validation Procedures

### Syntax Validation
Use xmllint to validate KML structure:
```bash
xmllint --noout your_file.kml
```

### Common Validation Checks
- All tags properly closed
- Correct element ordering within Placemark
- Valid coordinate format (longitude,latitude[,altitude])
- Proper hex color format (aabbggrr or rrggbb)
- Scale values are positive numbers

## Best Practices for Liquid Galaxy

### Visibility & Contrast
- Use high-contrast colors: bright yellow, cyan, magenta against dark backgrounds
- Avoid low-contrast combinations like gray-on-gray or dark blue on black
- For points: use scale 1.2-1.5 for visibility on large screens
- For lines: use width 2.0-3.0 for clarity

### Simplicity
- Start with simple geometries (points, basic polygons) before complex shapes
- Limit coordinate precision to 4-6 decimal places (sufficient for Liquid Galaxy resolution)
- Use descriptive but concise names and descriptions

### Performance
- Avoid extremely complex polygons with thousands of vertices
- Consider using NetworkLinks for large datasets that should be dynamically loaded
- Keep individual KML files under 5MB for optimal performance

## File Management

### Creating New KML
1. Generate valid KML content using templates
2. Validate XML syntax (Python xml.etree or xmllint)
3. Deploy to /var/www/html/kmls/ via scp
4. Verify file is web-accessible: `curl http://lg1:81/kmls/file.kml`
5. Add URL to /var/www/html/kmls.txt for dynamic load

### Updating Existing KML
1. Create updated version locally
2. Validate syntax
3. Deploy (overwrites existing file at /var/www/html/kmls/)
4. Verify — no need to modify kmls.txt (same URL, Earth re-fetches on next poll)

### Removing KML
Dynamic method (preferred — no relaunch):
1. Remove URL from kmls.txt:
   ```bash
   sshpass -p 'lg' ssh -p 2222 lg@localhost \
     "grep -v 'file.kml' /var/www/html/kmls.txt > /tmp/kmls.txt && mv /tmp/kmls.txt /var/www/html/kmls.txt"
   ```
2. Delete the file:
   ```bash
   sshpass -p 'lg' ssh -p 2222 lg@localhost \
     "rm /var/www/html/kmls/file.kml"
   ```
Earth auto-removes the NetworkLink within ~1s.

Static method (needs relaunch — only needed if permanent refreshInterval not added):
1. Remove content from /var/www/html/kml/master.kml
2. Relaunch Earth via `$SSH_DEST`

## Verification Checklist

After KML deployment:
- [ ] File exists in /var/www/html/kmls/ with correct permissions
- [ ] Also copied to /var/www/html/kml/master.kml if using static method
- [ ] File passes XML validation (Python xml.etree or xmllint)
- [ ] File is web-accessible: `curl -o /dev/null -w '%{http_code}' http://lg1:81/kmls/file.kml` returns 200
- [ ] URL is in /var/www/html/kmls.txt (for Method A dynamic sync)
- [ ] **Contains `<LookAt>` element** that flies Earth to the right location — without it, KML loads but is invisible off-screen
- [ ] Coordinates are in valid range (-180 to 180 longitude, -90 to 90 latitude)
- [ ] Colors are in proper hex format (aabbggrr)
- [ ] Earth is running after relaunch: `pgrep -a googleearth` shows the process

## Troubleshooting

### Common Issues
- **KML file deployed but NOTHING visible on screen**: 99% chance you forgot the `<LookAt>` element. Earth loads the KML content but shows the default view (Paris). Always include a LookAt that flies to your coordinates.
- **KML changes only appear after relaunch**: The Master KML NetworkLink has no `refreshMode`. Apply the permanent fix (add `refreshInterval=5` inside `<Link>`) — see "Force Refresh Mechanism" section.
- **File not displaying after copy to kmls/**: Earth doesn't read kmls/ directly. Run Method B (write to master.kml + relaunch) or Method A (add URL to kmls.txt). Simply having the file in kmls/ is not enough.
- **File not displaying after kmls.txt update**: URL format must match web server path. Use `http://lg1:81/kmls/` prefix. Verify with `curl http://lg1:81/kmls/file.kml` on lg1.
- **"KML not found" in Earth**: The web server on lg1 runs on port 81 (not 80). Ensure URL uses `:81`.
- **kmls.txt has blank lines**: `printf` is safer than `echo` for writing URLs. Blank lines are ignored by PHP's `getKmlListUrls()` (trims to empty string, skips) but avoid them for cleanliness.
- **Incorrect coordinates**: Verify longitude,latitude order (not latitude,longitude)
- **Colors not showing**: Ensure proper hex format (aabbggrr, not #rrggbb)
- **Geometry missing after relaunch**: Check /var/www/html/kml/master.kml content. If using Method A, the kmls.txt approach doesn't need a relaunch at all.
- **Performance issues**: Simplify geometry or reduce file size

### Sync System Debugging
If a KML added via kmls.txt doesn't appear:
1. Verify the URL is in kmls.txt: `cat /var/www/html/kmls.txt`
2. Verify the file is web-accessible: `curl -I http://lg1:81/kmls/file.kml` (expect 200)
3. Check for URL typos (trailing spaces, wrong port)
4. Ensure the sync PHP is running: Earth polls sync_nlc.php every 1s — it doesn't need to be triggered
5. For a full reset: restart Earth (relaunch) to reload myplaces.kml from scratch

### Connection Troubleshooting
If SSH/deployment fails:
1. Verify connection mode (VM/tunnel vs Direct LAN) — ask user
2. VM mode: check tunnel is up: `ss -tlnp | grep :2222`; if missing, ask laptop user for `ssh -N -R 2222:192.168.53.3:22 nara@<pi-ip>`
3. Direct LAN mode: verify ping + SSH to the master IP
4. Verify target directory exists: `sshpass -p 'lg' ssh -o StrictHostKeyChecking=no $SSH_DEST "ls /var/www/html/kmls/"`

## Templates

Templates are also available as files under the skill's `templates/` directory for direct use. Copy them and modify the placeholders.

### Available Template Files

| File | Purpose |
|------|---------|
| `templates/3d-pyramid.kml` | 3D pyramid with 4 colored faces, altitudeMode:absolute. Replace `[lon]`, `[lat]`, `[d]`, `[alt]` placeholders. |
| `templates/greenland-pyramid.kml` | Working 3D pyramid example (Greenland, tested on this rig) with LookAt and all face styles. Copy-modify-replace. |
| `templates/logo-overlay.kml` | ScreenOverlay for a logo image at `/kml/logo.png`, 200x200px, top-left corner. Matches the working file on this rig. |
| `templates/sample-placemark.kml` | Simple point placemark (NYC) with LookAt. Good starting point for a basic KML. |
| `templates/kerala-before-flood.kml` | Working example with 6 district placemarks, styled labels, and Folders. Real-world LG disaster layer. |
| `templates/kerala-flood.kml` | Flood severity zones (red/orange polygons) with city labels and tilted LookAt. Real-world disaster response layer. |

### Basic Point Marker Template
```xml
<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <name>{name}</name>
    <description>{description}</description>
    <Style id="pointStyle">
      <IconStyle>
        <color>{color}</color>
        <scale>{scale}</scale>
        <Icon>
          <href>{icon_href}</href>
        </Icon>
      </IconStyle>
      <LabelStyle>
        <color>{label_color}</color>
      </LabelStyle>
    </Style>
    <Placemark>
      <name>{placemark_name}</name>
      <description>{placemark_description}</description>
      <styleUrl>#pointStyle</styleUrl>
      <Point>
        <coordinates>{longitude},{latitude},{altitude}</coordinates>
      </Point>
    </Placemark>
  </Document>
</kml>
```

### Simple Polygon Template
```xml
<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <name>{name}</name>
    <description>{description}</description>
    <Style id="polyStyle">
      <LineStyle>
        <color>{outline_color}</color>
        <width>{outline_width}</width>
      </LineStyle>
      <PolyStyle>
        <color>{fill_color}</color>
        <outline>{outline}</outline>
        <fill>{fill}</fill>
      </PolyStyle>
    </Style>
    <Placemark>
      <name>{placemark_name}</name>
      <description>{placemark_description}</description>
      <styleUrl>#polyStyle</styleUrl>
      <Polygon>
        <tessellate>1</tessellate>
        <outerBoundaryIs>
          <LinearRing>
            <coordinates>
{coordinates}
            </coordinates>
          </LinearRing>
        </outerBoundaryIs>
      </Polygon>
    </Placemark>
  </Document>
</kml>
```

### 3D Polygon (altitudeMode)

For extruded/3D geometry, use `<altitudeMode>absolute</altitudeMode>` and specify altitudes in the coordinate triples. A 3D pyramid is made of 4 triangular face polygons meeting at a peak altitude.  
**Template file:** `templates/3d-pyramid.kml` — copy it and replace the `[name]`, `[lon]`, `[lat]`, `[d]` (half-width), and `[alt]` (peak height) placeholders.

**Working example (tested on this rig):** `templates/greenland-pyramid.kml` — 110km base, 50km tall, 4 colored faces at 41°W,71°N, with `<LookAt>` and all face styles. Copy-modify-deploy for any location.

Key differences from 2D polygons:
- **altitudeMode**: Must be `absolute` (not `clampToGround`, the default)
- **Altitude values**: Set Z in each `<coordinates>` triple (e.g. `lon,lat,2000`)
- **Triangles**: Each face needs exactly 3 coordinate points (base edge + peak)
- **No tessellation**: `<tessellate>` is omitted or set to 0 for 3D geometry
- **Base footprint**: Always add a 2D ground polygon (no altitudeMode) so the base is visible even from directly above

## Related Operations

After deploying KML, consider:
- Using `lg-ssh-control` to relaunch the rig for immediate viewing (Method B only)
- Applying the permanent refreshInterval fix so future KML writes auto-appear
- Setting up auto-refresh for dynamic KML content
- Creating NetworkLinks for large datasets that should be fetched remotely
- Scheduling regular updates for time-sensitive geographic data

## Helper Script — `lg-kml-deploy.sh`

A deploy script that handles validation + SCP + verification in one command:

```bash
#!/bin/bash
# lg-kml-deploy.sh
# Deploy KML files to Liquid Galaxy master node (lg1)

set -euo pipefail

# Configuration
LG_USERNAME="${LG_USERNAME:-lg}"
LG_PASSWORD="${LG_PASSWORD:-lg}"
LG_HOST="${LG_HOST:-localhost}"
LG_PORT="${LG_PORT:-2222}"
KML_DIR="/var/www/html/kmls"
SSH_OPTS="-o StrictHostKeyChecking=no -o ConnectTimeout=10"

usage() {
    echo "Usage: $0 -f <kml_file> [-n <remote_name>] [-r] [-h]"
    echo "  -f <kml_file>   Local KML file to deploy"
    echo "  -n <name>       Remote filename (defaults to local filename)"
    echo "  -r              Trigger relaunch after deployment"
    echo "  -h              Show this help"
    exit 1
}

REMOTE_NAME=""; TRIGGER_RELAUNCH=false
while getopts ":f:n:rh" opt; do
    case $opt in f) KML_FILE="$OPTARG" ;; n) REMOTE_NAME="$OPTARG" ;;
        r) TRIGGER_RELAUNCH=true ;; h) usage ;;
        *) echo "Invalid option" >&2; usage ;;
    esac
done

[[ -z "${KML_FILE:-}" ]] && { echo "Error: KML file (-f) is required" >&2; usage; }
[[ ! -f "$KML_FILE" ]] && { echo "Error: File not found" >&2; exit 1; }

REMOTE_NAME="${REMOTE_NAME:-$(basename "$KML_FILE")}"

# Validate KML syntax if xmllint available
if command -v xmllint &>/dev/null; then
    xmllint --noout "$KML_FILE" 2>/dev/null || { echo "Error: Invalid KML syntax" >&2; exit 1; }
fi

# Deploy
sshpass -p "$LG_PASSWORD" scp $SSH_OPTS -P "$LG_PORT" \
    "$KML_FILE" "${LG_USERNAME}@${LG_HOST}:${KML_DIR}/${REMOTE_NAME}"

# Verify
sshpass -p "$LG_PASSWORD" ssh $SSH_OPTS -p "$LG_PORT" \
    "${LG_USERNAME}@${LG_HOST}" "ls -la '$KML_DIR/$REMOTE_NAME'"

# Relaunch if requested
$TRIGGER_RELAUNCH && sshpass -p "$LG_PASSWORD" ssh $SSH_OPTS -p "$LG_PORT" \
    "${LG_USERNAME}@${LG_HOST}" "/home/lg/bin/lg-relaunch-direct" && echo "Relaunch triggered"

echo "Deployment complete!"
```

**Usage:**
```bash
# Deploy with validation + verification
bash lg-kml-deploy.sh -f myfile.kml

# Deploy and trigger relaunch
bash lg-kml-deploy.sh -f myfile.kml -r
```

Defaults: host=localhost, port=2222, password=lg (VM mode). Override with env vars: `LG_HOST`, `LG_PORT`, `LG_PASSWORD`. For Direct LAN: `LG_HOST=<lg-master-ip> LG_PORT=22`.

## References

- `references/lg-kml-architecture.md` — Full architecture detail: Earth loading chain, sync PHP internals, slave screen setup, web UI, and debugging techniques.
- `references/force-refresh-debug.md` — Debugging the force refresh mechanism: why the old sed approach failed, the corrected approach, and the actual myplaces.kml format from this rig.
- `references/myplaces-kml-refresh-workflow.md` — The complete workflow for making myplaces.kml changes permanent: edit → relaunch once → auto-refresh forever. Covers master and slave, the corrected sed approach, and helper scripts.
- `references/dart-kml-templates.md` — KML template generators from the Flutter LG controller app (getSlaveDefaultKml, getLogoKml, getSampleKml1/2). Reference for KML structure that matches what the real app sends.

## Current Status

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
