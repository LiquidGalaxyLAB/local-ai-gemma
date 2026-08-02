# Balloon Deployment to Rightmost Screen — RESOLVED (July 31, 2026)

**Outcome: SUCCESS with the escaped-HTML variant, on the CORRECT rightmost screen (slave_2.kml).**

## Final Working Recipe

1. Balloon KML = single Placemark with `<BalloonStyle><text>` using **escaped HTML entities** (`&lt;div&gt;...`), NOT CDATA — CDATA silently drops the whole Placemark on this VM's Earth 7.3.3.
2. Add `<gx:balloonVisibility>1</gx:balloonVisibility>` for auto-open.
3. Coordinates in **longitude,latitude** order.
4. Deploy to `/var/www/html/kml/slave_2.kml` — the RIGHTMOST screen (root formula rightmost = floor(N/2)+1 → lg2 for N=3).

## Why slave_3.kml Failed (the original wrong target)

The first attempt targeted `slave_3.kml` believing it was the rightmost screen. It is NOT — lg3 is the LEFTMOST screen (odd slave, left of lg1). The balloon deployed there was invisible on the rightmost screen because nothing was ever written to `slave_2.kml`.

## Additional Root Causes Found (why even the correct file wasn't showing)

1. **lg2's Earth was not polling slave_2.kml at all** — runtime `~/.googleearth/myplaces.kml` had the literal `##LG_PHPIFACE##` placeholder (unresolved) instead of `http://lg1:81/`, so the Solo KML NetworkLink pointed at an unresolvable URL. Fix: `sed -i 's|##LG_PHPIFACE##|http://lg1:81/|g' ~/.googleearth/myplaces.kml` then restart Earth once (config fix).
2. **No refreshInterval on the Solo KML NetworkLink** — added `<refreshMode>onInterval</refreshMode><refreshInterval>3</refreshInterval>` via a Python edit (nested sed through double-SSH mangles tabs and can inject stray chars breaking XML).
3. **Earth launched headless on slaves** — must SSH as the display-owning user (`lgN@lgN`, not `lg@lgN`) with `XAUTHORITY=$HOME/.Xauthority DISPLAY=:0`.
4. **Apache logs live at `/var/log/apache2/other_vhosts_access.log`** (vhost log), not access.log — use it to verify Earth is polling (e.g. `10.42.42.2 - GET /kml/slave_2.kml 200`).

## Verified Working State

- `10.42.42.2` (lg2) → `GET /kml/slave_2.kml` → HTTP 200 every 3s (confirmed in Apache vhost log)
- Balloon rendered on both screens initially because old balloon KML was still in `slave_3.kml` (left screen); cleared with blank KML so balloon exists ONLY on `slave_2.kml`.

## Wiki Pattern Reference

From wiki page "How To Send A Simple Balloon Including Some Data On The Right-Most Screen?" (hash `#698f239779dbaad8a314`): the wiki's `sendBallonKml()` calculates rightmost screen, generates KML, SSH echoes to `slave_<rightmost>.kml`. Works on physical hardware; the CDATA→escaped-HTML substitution is the VM-specific adaptation.
