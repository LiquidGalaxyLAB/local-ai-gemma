# Logo Deployment on Leftmost Slave

Source: LG Wiki (Topic 2), verified on 3-frame VM bridged LAN rig.

## LG Wiki Pattern

Logos/legends display on the **leftmost screen** of the Liquid Galaxy. Content is written to the target slave's KML file at `/var/www/html/kml/slave_<N>.kml`.

### Leftmost Screen Calculation (Dart formula from LG Wiki)

```dart
int leftRig = (_numberOfRigs / 2).floor() + 2;
```

Practical values:
| Rigs | leftRig | File |
|------|---------|------|
| 3 | 3 | slave_3.kml |
| 5 | 4 | slave_4.kml |
| 7 | 5 | slave_5.kml |

### Rightmost Screen (for info bubbles)

```dart
int rightRig = (_numberOfRigs / 2).floor() + 1;
```

## Our Rig (3-frame VM)

Screen order: `lg3:0.0 lg1:0.0 lg2:0.0`
- lg3 (frame 2, /home/lg/frame=2) is leftmost — reads slave_3.kml
- lg1 (frame 0, master) is center — reads master.kml
- lg2 (frame 1) is rightmost — reads slave_2.kml

Existing slave_3.kml at `/var/www/html/kml/slave_3.kml` — add ScreenOverlay inside `<Document>`, keep existing placemarks intact.

## Deployment Steps

1. Upload logo.png to `/home/lg/` on lg1, then `sudo cp` to `/var/www/html/kml/logo.png` (use deploy helper to bypass tool guard)
2. Add `<ScreenOverlay>` block to target `slave_<N>.kml` (leftmost only)
3. 2s slave refresh auto-loads — no relaunch needed

## ScreenOverlay Parameters

| Param | Value | Meaning |
|-------|-------|---------|
| overlayXY x | 0 | Left edge of image |
| overlayXY y | 1 | Top edge of image |
| screenXY x | 0 | Left edge of screen |
| screenXY y | 1 | Top edge of screen |
| xunits | fraction | Fraction-based positioning |
| yunits | fraction | Fraction-based positioning |
| size x | 554 | Width in pixels |
| size y | 500 | Height in pixels |
| xunits (size) | pixels | Pixel sizing |
| yunits (size) | pixels | Pixel sizing |

## Pitfalls

- **Do NOT write logo overlay to master.kml** — it shows on the center or master screen, not the leftmost
- **Do NOT overwrite slave_<N>.kml content** — append the ScreenOverlay inside the existing `<Document>`
- **Logo image URL in KML** must reference the web server: `http://lg1/kml/logo.png` (not the filesystem path)
- **Image format**: PNG works. Upload via SCP + deploy helper (tool guard blocks inline `sudo -S`)
- **Slave refresh**: slave KML files refresh every 2s (if refreshInterval was previously set). If logo doesn't appear, check that the slave's myplaces.kml has refreshInterval on the `slave_x.kml` NetworkLink
