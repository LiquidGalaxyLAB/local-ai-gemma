# KML Deploy Sequence

Standard sequence for deploying content to LG with voiceover and camera animation.
Used by: news-storyteller, armed-conflicts, geography-educator, and all use cases.

## The Sequence

1. **Generate KML** — Build the KML with visual elements only (no text labels). Use `<name></name>` for all placemarks. Text goes to right-screen panel only.

2. **Deploy KML to Apache** (via scp + sudo cp) — overwrite master.kml

3. **WAIT 6-8 seconds** — Let the 3s NetworkLink refresh cycle pick up the new KML. Without this wait, Earth shows stale content while your camera commands start flying to wrong positions.

4. **Deploy right-screen text panel** (optional) — scp the PNG, sudo cp to right_panel.png. Right screen (slave_2.kml on 3-screen rig) refreshes independently.

5. **START TTS voiceover + camera animation TOGETHER** — Voiceover in background, camera flytoview in foreground. They play simultaneously so the audio narration matches the camera movement.

## Camera Animation Pattern

```python
# Slow flythrough with dwell times
def camera_tour(zones):
    # Start with wide overview
    fly_to(20, 20, 20000000, 0)
    time.sleep(5)
    
    # Fly to each location slowly
    for z in zones:
        fly_to(z["lon"], z["lat"], 800000, 55)
        time.sleep(8)  # 8s dwell per location
```

**Timing rules:**
- Wide overview: 15,000-20,000km range, 5s dwell
- Regional close-up: 800,000-1,000,000km range, 8s dwell
- Tight close-up: 200,000-500,000km range, 10s dwell
- Transitions via `/tmp/query.txt` are instant (no animation)
- Total tour time = sum(dwell times) — plan for 2-3 minutes max

## Right-Screen Text Rule (CRITICAL)

- ALL text content goes to right-screen ScreenOverlay PNG
- Placemarks in master.kml MUST use `<name></name>` (empty)
- Description text: use `html.escape()` only, NEVER `<![CDATA[`
- Rightmost screen formula: N (total screen count)

## Voiceover + Camera Sync

Generate TTS narration first, then start playback in background while camera runs:

```python
# 1. Prepare narration script
narration = "Global update. Location 1. Detail. Location 2. Detail..."

# 2. Start TTS in background (via subprocess or hermes TTS tool)

# 3. Start camera tour (blocks, runs while TTS plays)
camera_tour(zones)
```
