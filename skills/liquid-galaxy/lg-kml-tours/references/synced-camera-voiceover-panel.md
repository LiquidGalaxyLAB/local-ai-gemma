# Synced Camera + Voiceover + Right-Panel Tour Pattern

Deploy KML → wait for refresh → slow camera tour where each stop updates the right-screen text panel and plays zone-specific TTS narration. Used by armed-conflicts, news-storyteller, and geography-educator.

## Sequence

1. **Generate KML** with all features + big text labels (2.0x+ scale, offset from markers)
2. **Deploy KML** to master.kml on Apache
3. **Wait 8s** for NetworkLink refresh (3s × 2 cycles + safety margin)
4. **Fly to global overview** (range=20M, tilt=0) → wait 5s
5. **For each stop:**
   a. **Fly to** location (range=600km, tilt=55°) → wait 2s for camera to settle
   b. **Deploy right-screen text panel** with zone-specific info (Pillow PNG → scp → sudo cp)
   c. **TTS voiceover** plays describing this zone (2-4 lines)
   d. **Dwell** 10-12s for user to read panel + hear voice
6. **Final fly** to global overview

## Right-Screen Text Panel (Per-Stop)

Generate dynamically per stop using Pillow:
- Dark bg `#0c0e18` with blue gradient header
- Zone name in orange/yellow
- Description in light grey (wrapped)
- Intensity bar (5 blocks, color-coded)
- Coordinates, affected population
- Status indicator (red/green dot + label)

```python
def make_panel(zone):
    img = Image.new('RGBA', (500, 500), (12, 14, 24, 240))
    draw = ImageDraw.Draw(img)
    # Title, zone name, description, intensity bar, status
    img.save('/tmp/right_panel.png')
```

Deploy via scp → sudo cp before each stop's dwell period.

## Voiceover Script

Format per zone: "[Zone name]. [Key fact 1]. [Key fact 2]."
Keep to 2-4 lines, spoken in ~8-10s. Generated via Hermes TTS tool (Edge provider).

## Dwell Timing

| Phase | Duration | Purpose |
|-------|----------|---------|
| Fly to zone | 1-2s | Camera animation |
| Deploy panel | 1-2s | SCP + sudo cp |
| Voiceover + read | 10-12s | User consumes content |
| **Total per stop** | **~12-15s** | |

## VM Earth Camera Ranges

| View | Range | Tilt | Use |
|------|-------|------|-----|
| Global overview | 15-20M km | 0° | See all features |
| Regional hotspot | 600-800km | 55° | Zone-specific view |
| Close-up | 50-200km | 60° | Detail inspection |
