# Poweroff Self-First Bug (June 2026)

## History

The `lg-poweroff-direct` and `lg-reboot-direct` helpers on lg1 had a **self-first** bug: the `for lg in $LG_FRAMES` loop started with lg1 (self) and powered it off before reaching lg2. The SSH session dropped immediately, so lg2 never received its poweroff command.

The skill's `scripts/lg-poweroff-direct` (source of truth) already had the correct remote-first logic since v2.9, but:
- `scripts/helpers/lg-poweroff-direct` (internal helpers copy) still had the old self-first version
- The deployed copy at `/home/lg/bin/lg-poweroff-direct` on lg1 was the self-first version from an earlier deployment

## Fix Applied (2026-06-19)

1. **`/home/lg/bin/lg-poweroff-direct` on lg1** — overwritten with remote-first version via scp
2. **`scripts/helpers/lg-poweroff-direct`** — overwritten to match the correct remote-first logic
3. **Skill version** — bumped to 2.11.0
4. **Poweroff procedure** — updated to mandate scp-deployment of the correct helper before every poweroff
5. **Pre-flight** — Pi IP now auto-checked via `hostname -I` rather than asking Nara

## Verification

The fix is confirmed working: when run, `lg-poweroff-direct` now tries all remote frames (lg2, lg3...) and reports unreachable ones, then powers off self last. The SSH connection stays alive until all remote attempts are complete.

## Future Sessions

When running poweroff on a session that starts fresh:
1. Always `sshpass scp scripts/lg-poweroff-direct lg@localhost:/home/lg/bin/lg-poweroff-direct` first
2. `grep -c "continue" /home/lg/bin/lg-poweroff-direct` should return 1 (correct)
3. Then run the helper

This prevents the bug from recurring even if `/home/lg/bin/` has stale copies from backups or prior sessions.
