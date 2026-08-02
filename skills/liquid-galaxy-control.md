---
name: liquid-galaxy-control
description: Control Liquid Galaxy rig (relaunch, reboot, shutdown) via SSH.
---

**DEPRECATED** — Superseded by `lg-ssh-control` (more comprehensive: dual-mode connection support for VM/tunnel and Direct LAN, multi-frame reboot/poweroff, KML refresh, helper deploy/verify scripts). Use `lg-ssh-control` for all new work. This skill is kept for backward compatibility and will be consolidated by the curator.

## Pitfalls (critical)

- **lg-ctl-master missing** — See `lg-ssh-control` for the `lg-relaunch-direct` workaround.
- **Tool guard blocks `sudo -S`** — See `lg-ssh-control` for the helper script workaround.
- **IPs drift on LAN** — Always verify current IPs before any command. Do not rely on hardcoded addresses from past sessions.
- **Connection mode varies** — `lg-ssh-control` v2.3+ asks VM/tunnel vs Direct LAN at session start. Do not assume `localhost:2222`.

## Quick Reference (use lg-ssh-control instead)

| Action | lg-ssh-control helper |
|--------|----------------------|
| Relaunch | `lg-relaunch-direct` via `$SSH_DEST` (resolved by connection mode pre-flight) |
| Reboot | `lg-reboot-direct` via `$SSH_DEST` |
| Poweroff | `lg-poweroff-direct` via `$SSH_DEST` |
| Set Refresh | `lg-refresh-set` via `$SSH_DEST` |
| Reset Refresh | `lg-refresh-reset` via `$SSH_DEST` |

**Verification:** See [`lg-ssh-control.md`](lg-ssh-control.md) — the Verification section covers both VM/tunnel and Direct LAN modes.

