# Screen Placement Reference for LG Data Visualization

## 3-Screen Rig Layout

```
lg2 (left, slave)     lg1 (center, master)     lg3 (right, slave)
yawOffset: -55°       yawOffset: 0°            yawOffset: +55°
```

## What Goes Where

| Screen | Role | Content | Notes |
|--------|------|---------|-------|
| lg1 (center) | Master | Data placemarks, camera control | Keyboard + mouse available |
| lg2 (left) | Slave, data only | Data placemarks | No UI, pure map view |
| lg3 (right) | Slave, data + info | Data placemarks + news balloons/index | Right screen = info panel |

## Placement Rules (by content type)

### Data Placemarks (all layers)
→ **master.kml** — renders on all screens via ViewSync
- Earthquakes, military activity, natural events, etc.
- Same placemarks everywhere, each screen shows a different angle

### Logo / Branding
→ **Leftmost slave only** (lg3 for 3-screen, lg4 for 5-screen)
- Formula from LG Wiki: `leftRig = floor(N/2) + 2`
  - N=3 → lg3 (floor=1 + 2 = 3)
  - N=5 → lg4 (floor=2 + 2 = 4)
  - N=7 → lg5 (floor=3 + 2 = 5)
- Use `<ScreenOverlay>` in the slave's KML file
- Position: top-left of screen: `x="0" y="1"`

### News Balloons / Article Index / Rich Info
→ **Right screen only** (lg2 for 3-screen)
- Heavy HTML balloons with article text should not clutter all screens
- Use a separate KML file deployed to the right slave's KML path
- Or add a `<ScreenOverlay>` positioned on the right screen
- The right screen acts as the "situational awareness info panel"

### Control Overlays / UI
→ **Master (lg1) only**
- Camera controls, layer toggles, search — only on center screen
- These make no sense on slaves (no input)

## KML Deployment Strategy for Multi-Screen

**Option A: Single master.kml (simplest)**
- All placemarks in `master.kml` → all screens see them
- News balloons: place their placemarks at the edge of the view (e.g., far right of the boundng box) so they only appear on the right screen's viewing angle
- Simplest to manage but less precise

**Option B: Separate per-screen KMLs (precise)**
- Placemarks in `master.kml` → all screens
- News overlay in `slave_x.kml` → right screen only (PHP-resolves to the correct screen)
- Logo in leftmost `slave_N.kml`
- More work but gives per-screen control

## Frame-Count Agnostic Design

All helpers and scripts should reference `$LG_FRAMES` from `shell.conf` rather than hardcoding 3. The screen placement formula `floor(N/2)+2` works for any N (3, 5, 7+).
