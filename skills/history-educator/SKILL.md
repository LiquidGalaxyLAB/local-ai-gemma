---
name: history-educator
description: "Create phased history KML tours on Liquid Galaxy."
version: 2.0.0
platforms: [linux]
metadata:
  hermes:
    tags: [history, kml, liquid-galaxy, education, timeline]
    related_skills: [armed-conflicts, news-storyteller, lg-kml-tours]
---

# History Educator

Turns any historical event with a geographic dimension into a **self-running visual lecture** on the Liquid Galaxy rig. The rig becomes a time machine: territory changing hands, armies moving, empires expanding and collapsing, trade routes forming — animated across the multi-screen panorama with TTS narration alongside. Not a static map — a sequence of phases the viewer experiences.

**Key dependency stance:** pure Python (stdlib + `news_card_balloon`/`history_visuals` helpers). KML is VM-safe (escaped HTML, no CDATA, no gx in NetworkLink KML, coords rounded to 4 decimals). Rightmost screen = `floor(N/2)+1` (N=3 → slave_2.kml).

## When to Use

Trigger phrases:
- "show me how World War 2 started" / "teach me about the Roman Empire"
- "visualize the Mongol conquests" / "what happened during the partition of India"
- "show the Cold War on the rig" / "walk me through the Battle of Stalingrad"
- "how did the Ottoman Empire fall" / "show me the spread of the Black Death"
- "teach me about the transatlantic slave trade routes"
- "visualize how Alexander the Great conquered Persia"
- Any historical event/war/empire/migration/battle with a geography

**Extract 3 anchors from the user input:** event name, approximate time period, geographic region. Those are enough to build phases, choose KML types, and write narration.

## Universal Structure (Every Event)

1. **Establish the world BEFORE the event** — zoom out, show the region, label key players. NEVER start at the climax.
2. **Show the event unfolding in 3-6 named phases.** Each phase has its own KML layers that build on/replace previous ones. Phase names are human and dramatic — "The Invasion Begins", "The Empire Fractures", "The Last Stand" — never "Phase 1".
3. **Show the world AFTER and why it matters** — final territorial outcome, wide view, net change visible across all screens.

**gx:Tour** is the primary sequencing tool: camera movements, balloon updates, and layer changes progress the story. Use `playtour=` on this rig (see lg-kml-tours) OR sequential flytoview via `/tmp/query.txt` — the rig's proven camera driver.

## Rightmost Screen Balloon (Parchment Style)

The history balloon is **parchment meets modern briefing card** — NOT the news category colors:

- Dark background (`#1a1712`), **sepia/amber header bar** (`#d4a017` gradient), Georgia serif phase titles in warm parchment text (`#f0e2b0`)
- ONE Placemark, balloon auto-opens via `gx:balloonVisibility>1`
- Each phase card shows:
  1. **Phase name** (large bold)
  2. **Year / date range**
  3. **2-3 sentence description** of what is unfolding NOW in the tour
  4. **"Key Figures"** line — people driving events
  5. **"Stakes"** line — what happens if this goes the other way (teaches contingency: history was NOT inevitable)

**Generator:** `scripts/history_visuals.py` → `history_balloon_kml(phases, title)`.
Phases are a list of dicts: `{name, year, desc, key_figures, stakes}`. Escaped HTML (VM-safe). Deploy to `/var/www/html/kml/slave_<rightmost>.kml`.

## KML Types per Scenario

### Wars & Military Campaigns (richest)
1. **Territory polygons** — pre-war control, each faction semi-transparent in its color
2. **Advance arrows** (LineStrings) — direction/thrust per campaign phase, sequenced so camera follows movement
3. **Battle columns** — extruded cylinders at battle sites, size ∝ scale of battle
4. **Siege rings** — concentric polygons tightening around besieged city
5. **Post-war polygon layer** — final territorial outcome; fly back wide to show net change start→finish

### Empires Rising & Falling
- Time-lapse polygon layers: expansion adds territory (gold/imperial purple `hist_empire`), decline shrinks it; contrasting color for lost/contested (`hist_empire_lost`)
- Capital pins labeled with ruler + year (`capital_pin_kml`, 2.0x label scale)
- Dashed trade-route LineStrings between ports/overland routes (`hist_route`)
- **Payoff moment:** camera pulls back at peak expansion so the whole empire fits across all screens

### Revolutions & Political Upheaval
- Pre-revolution power polygons (kingdoms, colonies, occupied zones) → dissolve phase by phase into new entities
- Flashpoint city icons with balloon text explaining triggers
- gx:Tour hops city→city in chronological order — viewer watches the movement spread
- Final redrawn borders as clean polygon layer

### Ancient Civilizations
- Ground overlay image tiles (semi-transparent) over the region — territory, cities, roads, aqueducts, trade networks
- **Soft-edged polygons** (spheres of influence, not modern borders) — avoid hard outlines
- Every major city labeled with balloon text on what it was known for
- **Slow cinematic camera** — long gliding arcs, not snappy cuts

### Battles (single engagement)
- Zoom to street/valley level if terrain matters (Thermopylae, Waterloo, Stalingrad)
- Starting troop positions: polygons per side, contrasting colors
- Animate phases: initial positions → first engagement → flanking/breakthrough → retreat/rout → final positions
- Thin LineString arrows for unit movements; markers at commander positions and key terrain (the hill, the bridge, the river crossing)
- Balloon updates each phase with the decision/event that drove the action
- End: pull back to show strategic consequence in the wider war

### Migrations & Diaspora
- **Flow arrows** — thick LineStrings with direction, width/color intensity ∝ volume of people
- Placemark stops along the route (pauses, settlements, obstacles)
- Origin region polygon at start; destination region polygons at end (communities formed)
- Forced migrations/deportations: darker muted palette

### Cold War / Ideological Conflicts
- **Choropleth world map** — NATO blue, Warsaw Pact red, Non-Aligned grey
- Animate realignments phase by phase by swapping country colors
- **Missile-range arcs** — semi-transparent LineString arcs between superpower territory and targets (dramatic across panorama)
- Flashpoint pins (Korea, Cuba, Vietnam, Berlin) pulsing, balloon text on tour arrival

## Narration Structure (TTS)

1. **Hook** — one dramatic opening sentence ("In the summer of 1941, three million soldiers crossed a border that would never be the same again.")
2. **Phases** — plain language narration per phase as camera moves
3. **Legacy** — closing line connecting the event to today ("The borders drawn at Versailles in 1919 still shape the conflicts you see on this map right now.")

Rules: 20-30 seconds per phase (syncs with camera). Never read coordinates or technical details aloud — those belong in the balloon panel only.

## Procedure

1. **Extract anchors** from user request: event, time period, region.
2. **Build the phase structure** — 3-6 named phases (context → unfolding → aftermath/legacy).
3. **Generate master.kml layers** per scenario type using `history_visuals.py` helpers (territory polygons, advance arrows, battle markers, siege rings, pins) — each phase's layers distinct (multi-shape + multi-color, never recycled).
4. **Generate the parchment balloon** — `history_balloon_kml(phases, title)` → rightmost screen `slave_<rightmost>.kml`.
5. **Deploy** via the standard helper pattern (write local → scp to lg1 → sudo cp): master.kml for layers, slave_2.kml for balloon. 3s refresh picks up — **no relaunch for content**.
6. **Camera + voiceover together:** deploy KML → 8s wait → fly to region wide view → for each phase: flytoview to the phase focus, update balloon if phase-specific, play TTS phase narration, dwell 10-12s.
7. **End:** fly wide to show the net outcome + play legacy narration.

## Verification

After deploy: `grep -c "styleUrl" /var/www/html/kml/master.kml` shows layers present; Apache vhost log (`/var/log/apache2/other_vhosts_access.log`) shows lg2 fetching `slave_2.kml` + the balloon file every 3s. The parchment balloon renders on the rightmost screen with phase cards.

## Files

- `scripts/history_visuals.py` — parchment balloon + KML layer generators (history_balloon_kml, territory_polygon_kml, advance_arrow_kml, battle_marker_kml, siege_ring_kml, capital_pin_kml, style_defs, master_kml_document)
- `/home/nara/wm-collector/history_visuals.py` — same module (working copy)
- `/home/nara/wm-collector/history_demo_takshashila.py` — **Verified demo (Jul 2026)**: Takshashila University (6 phases, ancient civilizations), Gandhara territory, 3 trade routes, 12 student-origin dots, battle + siege rings, parchment balloon. Deployed and verified on rig.
- `/home/nara/wm-collector/history_demo_mongol.py` — **Verified demo (Aug 2026)**: Mongol Invasions (6 phases, empires rising), peak-extent polygon, 8 advance arrows, 5 battle columns, 6 pins, 7 siege rings, parchment balloon. 22.9KB KML, 27 style elements.
- Related: `lg-kml-tours` skill, `armed-conflicts` (separate visual language), `news-storyteller` (different balloon style)
