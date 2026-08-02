# LG Architecture Quick Reference

The full foundation document is at **`~/lg-architecture.md`** — read it for the complete system design.

## Context

`~/lg-architecture.md` defines the standard 5-layer model (End User → Hermes Runtime → Skills → Content/Reference → Deployment) that all LG operations follow. It codifies 4 reusable patterns extracted from everything built so far:

### 4 Core Patterns

| Pattern | Used for | Load skill |
|---------|----------|------------|
| **A: SSH Control** | relaunch, reboot, poweroff, refresh, network info | lg-ssh-control |
| **B: KML Deploy** | static KML, placemarks, polygons, logos, 3D shapes | lg-kml-tours |
| **C: Animation** | smooth orbit, flyover, continuous camera motion | lg-kml-tours |
| **D: Config Fix** | one-time fixes (flyToView, network, Earth sign-in) | lg-ssh-control + references |

### Content Directory

Generated and deployed content lives at `~/lg-content/`:
```
~/lg-content/
├── kml/archive/       # Past KML versions (deploy from here for rollback)
├── data/real-time/    # Fetched live data (API responses)
├── data/static/       # Reference data (coords, shapes)
├── scripts/           # Deployed animation scripts (copies for reference)
├── logs/              # Deployment logs
└── backups/           # LG config backups (myplaces.kml.bak, shell.conf.bak)
```

Before deploying any KML, save a copy to `~/lg-content/kml/archive/<name>-<date>.kml` for rollback.

### Knowledge Capture Levels

| Level | Tool | What | When |
|-------|------|------|------|
| 1 | `memory` | Durable facts (IPs, constraints, env quirks) | Correction or discovery |
| 2 | `skill_manage` | Reusable procedures + fixes | Complex task done, bug fixed |
| 3 | `session_search` | Full conversation history | Recalling past work |

### Skill Loading Order

```
1. lg-ssh-control    ← ALWAYS FIRST (establishes connection, pre-flight)
2. lg-kml-tours      ← For KML creation/deploy/animation
(More skills loaded as needed from skills/)
```

### Standard Skill Skeleton

```
skills/<skill-name>/
├── SKILL.md              # YAML frontmatter + procedures
├── scripts/              # Deployable helpers, generators
├── templates/            # Reusable KML files, config templates
└── references/           # Architecture notes, troubleshooting
```

When adding a new use case: Identify → Create skeleton → Register in lg-ssh-control's triggers → Test → Lock in with memory.
