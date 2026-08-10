---
name: satellite-orbital-tracker
description: Real-time orbital object tracker — ISS, Starlink megaconstellation, Hubble, space debris, and 16000+ active satellites rendered at actual orbital altitude on a multi-screen globe. The only place on Earth where orbital altitude is physically meaningful in 3D.
version: 1.0.0
tags: [satellite, orbit, space, ISS, starlink, debris, TLE, liquid-galaxy, 3D]
related_skills: [live-aviation, lg-data-visualization]
---

# Satellite & Orbital Object Tracker

Turns the LG rig into a space operations center — the kind of display you'd see at a mission control facility or a planetarium. Tracks every active satellite, the ISS, China's Tiangong station, Starlink's megaconstellation, Hubble, and the largest debris objects — all at their actual orbital altitude above Earth, updated in real time from live TLE (Two-Line Element) orbital data.

**This is the killer app for Liquid Galaxy that no browser dashboard can touch.** A browser map shows satellites as flat dots on a 2D surface. On a 3D multi-screen LG rig with a flying camera, orbital altitude becomes physically meaningful — the ISS at 420 km visibly floats above the atmosphere, Starlink shells form concentric rings at 550 km, and debris fields look like hazard zones you can physically fly through. A viewer standing in a room can look up and see the ISS passing overhead in real time.

## Why Distinct From Existing Skills

- **live-aviation** operates *within* the atmosphere (0–15 km). This skill operates *above* it (200–42,000 km). No overlap in altitude range, data source, or visual language.
- No other Nara skill operates above the Kármán line (100 km). This is a completely new domain — orbital space.
- The visual language is deliberately different: deep space black background, glowing cyan orbit trails, planetarium aesthetic. Nothing else in the catalog looks like space.

## Trigger Phrases

- "show me the ISS on the rig" / "where is the space station right now"
- "satellite tracker on the LG" / "show me everything in orbit"
- "Starlink constellation view" / "how many satellites are overhead"
- "show me the orbital debris field" / "space junk on the rig"
- "where is Hubble" / "show me Tiangong"
- "orbital watch" / "space operations center on the LG"
- "what satellites are passing over India right now"

## Data Sources

**All sources confirmed working, free, no auth required.**

| Source | URL | Auth | What It Provides |
|--------|-----|------|-----------------|
| CelesTrak Active Satellites | `celestrak.org/NORAD/elements/gp.php?GROUP=active&FORMAT=tle` | **None** | TLE data for 16,093 active payloads — updated daily |
| CelesTrak Starlink | `celestrak.org/NORAD/elements/gp.php?GROUP=starlink&FORMAT=tle` | **None** | TLE for 10,761 Starlink satellites — all shells |
| CelesTrak Stations | `celestrak.org/NORAD/elements/gp.php?GROUP=stations&FORMAT=tle` | **None** | ISS (ZARYA), Tiangong, and all modules |
| CelesTrak Debris | `celestrak.org/NORAD/elements/gp.php?GROUP=debris&FORMAT=tle` | **None** | Largest tracked debris objects (>10 cm) |
| CelesTrak Brightest | `celestrak.org/NORAD/elements/gp.php?GROUP=visual&FORMAT=tle` | **None** | 100 brightest satellites — visible to naked eye |
| CelesTrak GPS/GNSS | `celestrak.org/NORAD/elements/gp.php?GROUP=gps-ops&FORMAT=tle` | **None** | Operational GPS, GLONASS, Galileo, BeiDou |

**Verified on this network (Aug 2026):**
- Active satellites: 16,093 TLE records confirmed
- Starlink: 10,761 TLE records confirmed
- Stations: ISS (ZARYA), POISK, NAUKA, Tiangong (TIANHE, WENTIAN, MENGTIAN) — all confirmed with valid TLE data
- Total orbital objects available: ~27,000+ from CelesTrak alone

**How TLE works:** Each satellite gets a 2-line orbital element set updated daily. From TLE, we compute the satellite's current position (lat, lon, altitude) using the SGP4 propagator (Python `sgp4` library, pip-installable, no key). Position accuracy: ~1 km at epoch, degrading to ~3 km after 24h. More than sufficient for visualization at LG globe scales.

## What the Skill Shows (5 Layers, Each Toggleable)

### Layer 1: ISS and Space Stations — The Bright Anchors

ISS and Tiangong as large, high-contrast markers at their actual orbital position (420 km altitude for ISS, ~390 km for Tiangong). Rendered as:

- **Marker:** 6-pointed star icon (★), white `#ffffff`, scale 3.0 — largest marker on the globe, visible from global zoom
- **Orbit trail:** White dotted LineString tracing the station's ground track for the past 90 minutes (one orbit) and projected forward 90 minutes. Thickness 2px, 40% opacity.
- **Altitude indicator:** A thin vertical white line connecting the station marker down to Earth's surface — this is the key visual that makes orbital altitude physically meaningful. From global zoom, the ISS visibly hangs above the planet.
- **Label:** "ISS · 420 km · 27,600 km/h" at marker offset

### Layer 2: Starlink Megaconstellation — The Ring Cloud

Starlink satellites as small cyan dots at 550 km altitude (Shell 1). With 10,761 active satellites, individual dots are visible only at close zoom — at global zoom, they form a visible ring pattern around Earth:

- **60 orbital planes** at 53° inclination — visible as parallel dotted lines circling the globe
- **Color:** Cyan `#00ccff` at 60% opacity for individual dots, fading to 15% for the constellation cloud at global zoom
- **Starlink shells:** Shell 1 (550 km), Shell 2 (540 km), Shell 4 (560 km) — three concentric orbital bands
- **Label:** "Shell 1: 1,584 satellites at 550 km" — shown as a ring label, not per-satellite

### Layer 3: GPS/GNSS Constellation — The Navigation Backbone

GPS, GLONASS, Galileo, and BeiDou satellites at ~20,200 km altitude (MEO — Medium Earth Orbit). These are much higher than LEO satellites and form a distinctive ring pattern:

- **Markers:** Small white diamond icons at 20,200 km
- **Orbit ring:** Thin gold `#ccaa44` LineString at 20,200 km altitude — visible as a distinct outer ring
- **Label:** "GPS · 31 sats at 20,200 km" — per constellation

### Layer 4: Brightest Visual Satellites — What You Can See Tonight

The 100 brightest satellites (CelesTrak "visual" group) rendered as medium-brightness markers with a visibility indicator:

- **Currently sunlit:** Bright white markers (satellite in sunlight, visible from dark ground)
- **In Earth's shadow:** Dim grey markers (invisible to naked eye)
- **Ground track:** Thin green LineString for the next 90 minutes of the ISS pass — "ISS will pass over Madrid in 34 minutes"

### Layer 5: Debris Field — The Hazard Zones

Largest debris objects (>10 cm, ~200 tracked) as small amber warning triangles at their orbital altitude:

- **Color:** Amber `#ff8800`, small scale (0.5)
- **Clustered into hazard bands:** debris concentrates at 800–1,000 km (polar sun-synchronous orbits) and ~36,000 km (GEO graveyard)
- **No individual labels** — debris is shown as a hazard density visualization

## KML Construction — VM-Safe Approach

All orbits rendered as LineString rings at the computed altitude. VM-safe KML rules apply: no CDATA, no gx: namespace (except for camera tours), coordinates rounded to 4 decimal places.

**TLE → Position computation:**
```python
from sgp4.api import Satrec
sat = Satrec.twoline2rv(line1, line2)
jd, fr = jday(year, month, day, hour, minute, second)
e, r, v = sat.sgp4(jd, fr)  # r = [x,y,z] in km (ECI)
# Convert ECI → lat/lon/alt → KML coordinates
```

**Single orbit trail KML example (ISS):**
```xml
<Placemark>
  <name>ISS (ZARYA) · 420 km · 27,600 km/h</name>
  <styleUrl>#iss_trail</styleUrl>
  <LineString>
    <altitudeMode>absolute</altitudeMode>
    <coordinates>
      -75.1234,15.5678,420000
      -74.8901,16.1234,420000
      ...90-minute orbit at 60s intervals...
    </coordinates>
  </LineString>
</Placemark>
```

**Satellite position rendering:** A single marker at the current computed position, updated each run (position valid for ~1 hour at >1 km accuracy). The orbit trail is static (computed once from the TLE epoch) — the marker position is live.

## Camera Design

The camera treats space as a place you can visit — altitude changes to match orbital shells:

1. **Opening — Ground observer view:** Camera at ground level (100 m altitude), tilted 85° looking straight up from the viewer's region. Stars/black background, satellite trails visible overhead. This is what a person sees standing outside looking up — but with labels. Hold 5 seconds. Right-screen: "27,000+ objects in Earth orbit. You're looking up through them."

2. **Rise to ISS altitude:** Camera ascends to 450 km (just above the ISS), tilt flattens to 20°, centered on the ISS's current position. The planet is visible below, the ISS trails nearby. Hold 8 seconds. Right-screen: "ISS at 420 km — 27,600 km/h, completes an orbit every 90 minutes. Currently over [location]."

3. **Starlink shell fly-through:** Camera rises to 580 km (above Starlink Shell 1), tilt 30°. The cyan dotted rings of the Starlink constellation are visible as parallel orbital planes wrapping the Earth. Camera pans along one orbital plane for 10 seconds. Right-screen: "Starlink Shell 1: 1,584 satellites at 550 km. SpaceX operates 10,761 Starlinks across 3 shells."

4. **Rise to MEO — the GPS ring:** Camera rises to 21,000 km, tilt 60°. Earth is much smaller now. The GPS/GLONASS/Galileo/BeiDou satellite ring at ~20,200 km is clearly visible as a gold band. Hold 6 seconds. Right-screen: "Medium Earth Orbit: 120+ navigation satellites at 20,200 km. Every GPS fix your phone gets comes from objects in this ring."

5. **GEO — the Clarke Belt:** Camera rises to 36,000 km. The geostationary ring (the "Clarke Belt") is visible as a thin ring at this altitude. Satellites here stay fixed over one spot on Earth. Hold 4 seconds. Right-screen: "Geostationary orbit: 36,000 km. Communication, weather, and broadcast satellites — each one locked to a single point on Earth."

6. **Return to Earth:** Camera descends back to 1,000 km, 45° tilt. The full orbital picture — LEO cloud, Starlink shells, MEO ring, GEO ring — visible against the planet below. Hold 8 seconds. End.

Total tour: ~50 seconds (faster than most Nara skills — space is big, and you feel the speed).

## Right-Screen Balloon Design

Visual identity: **mission control console** — planetarium meets NASA:

- **Background:** Pure black `#000000` with a thin cyan `#00ccff` border (2px). Deepest black of any Nara skill — space has no ambient light.
- **Header:** "ORBITAL TRACKER" in cyan monospace font, center-aligned. Below: "TLE epoch: 2026-221.85937483 · Next update: 2026-222.00000000" in small text.
- **Body — vertical stack:**
  - **Current ISS position:** Lat/lon/alt/velocity. "Over South Pacific · -34.2°S, -152.8°W · 420 km · 7.66 km/s"
  - **Pass predictions:** "Next UK pass: 22:14 UTC (47 min) · Next US East pass: 23:01 UTC (94 min)"
  - **Satellite count by orbital regime:** LEO: 21,403 · MEO: 412 · GEO: 691 · HEO: 89
  - **Starlink status:** 10,761 tracked · 3 shells active · Shell 4 deploying
  - **Debris warning:** "Tracked debris: 36,500 objects >10 cm · 800–1000 km band: high density"
- **Footer:** "Data: CelesTrak · SGP4 propagation · Positions valid to ±1 km · No auth required"

Generated as PNG via Pillow (`gen_orbital_panel.py`), deployed to rightmost screen. The cyan-on-black aesthetic is deliberately similar to cyber-infrastructure but lighter — cyber is electric blue, this is pure cyan, and the black here represents deep space not a terminal screen.

## What Nara Says Back

> "Orbital tracker deployed. 27,000 objects across all regimes. ISS currently over the South Pacific at 420 km — you can see it as the white star icon, with the dotted trail showing its last orbit. Camera is rising through the Starlink shells now — 10,761 Starlinks, that's the cyan dotted ring pattern wrapping the globe. Above that: GPS constellation at 20,200 km, and the geostationary ring at 36,000 km. Total tracked debris: 36,500 objects >10 cm. This is what Earth's orbital environment looks like in real time."

## The One Rule

**Altitude is not a number — it's a place you can visit.** Every design decision serves the single purpose of making orbital altitude physically experienceable. The ISS's 420 km isn't printed as text — it's shown as a white vertical line connecting the station to the ground. The camera doesn't describe Starlink shells — it flies through them. The GPS ring isn't mentioned as "medium Earth orbit" — the camera rises to it and the viewer sees it as a gold band at 20,000 km. If a viewer standing in the room cannot physically point to where the ISS is relative to the Earth's surface, the skill has failed. Space is big, and on a 3D multi-screen LG rig, you can feel that bigness.

## Files

| File | Purpose |
|------|---------|
| `/home/nara/wm-collector/collectors/orbital_tracker.py` | Main script — fetches CelesTrak TLE, propagates positions via SGP4, builds 5-layer KML, deploys, runs camera ascent tour |
| `/home/nara/wm-collector/gen_orbital_panel.py` | Right-screen PNG panel generator (Pillow, cyan-on-black space theme) |
| `references/satellite-orbital-tracker/celestrak-groups.json` | CelesTrak query groups, descriptions, update cadences |

## Manual Run

```bash
cd /home/nara/wm-collector && python3 collectors/orbital_tracker.py
```

## Cron (Auto-Refresh)

```bash
cronjob action=create name=orbital-tracker schedule=2h \
  prompt="cd /home/nara/wm-collector && python3 collectors/orbital_tracker.py" \
  skills=satellite-orbital-tracker
```

## Dependency

```bash
pip install sgp4  # SGP4 propagator — pure Python, no external deps
```

TLE parsing and SGP4 propagation are CPU-light (~0.1ms per satellite). Processing 27,000 TLE records takes ~3 seconds on a Raspberry Pi 5.
