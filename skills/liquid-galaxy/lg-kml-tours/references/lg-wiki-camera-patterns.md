# LG Wiki Camera Patterns

Curated findings from the LG Wiki (https://lg-wiki-coral.vercel.app/docs/) — the authoritative source for LG camera control.

## playtour= Pattern (Recommended for Smooth Orbits)

From LG Wiki Q&A #15: `echo "playtour=Orbit" > /tmp/query.txt` triggers a gx:Tour
named "Orbit" to auto-play. No Play click needed.

**Confirmed working on Earth 7.3.3 (July 2026).**

### Sequence
1. Deploy KML with `<gx:Tour><name>Orbit</name>` to master.kml
2. `echo 'flytoview=<LookAt>...target...</LookAt>' > /tmp/query.txt` — position camera
3. sleep 3
4. `echo 'playtour=Orbit' > /tmp/query.txt` — start tour
5. `echo 'exittour=true' > /tmp/query.txt` — stop tour

### Why It's Better
- Earth's native animation engine handles interpolation (no daemon race conditions)
- No sshpass latency per step
- No file-write atomicity issues

## Orbit Research (from LG Wiki)
- Max camera altitude: ~63,000km natively
- Max orbit altitude displayable: ~36,000km (Graveyard orbit)
- Lower orbits (GPS, LEO) display fine within altitude limits
- Use absolute altitudeMode for space-level views

## Directional/Rotational Commands
The "Sending Directional And Rotational Commands" article covers sending
navigation commands via SSH. Key commands:
- `flytoview=<LookAt>` — fly camera to position
- `playtour=<name>` — play named tour
- `exittour=true` — stop tour
