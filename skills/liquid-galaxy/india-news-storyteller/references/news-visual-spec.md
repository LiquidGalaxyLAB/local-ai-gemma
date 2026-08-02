# News Visual Spec — User's Standard (Nara, July 2026)

User's requirements for news visualization on Liquid Galaxy. Implemented
subset lives in `/home/nara/wm-collector/news_visuals.py`; the full spec
below is the target — extend toward it when adding new story types.

## The News Balloon UI (rightmost screen) — IMPLEMENTED

Not a plain text dump — a **styled HTML card that looks like a news panel**:

- Dark-themed card with a **colored top bar** whose color changes by category:
  red = breaking/conflict, orange = disasters, blue = geopolitical,
  green = economy, yellow = science/space.
- **Bold headline** at top in large white text (26-28px), source tag +
  timestamp in small muted text just below, then a 2-3 sentence summary
  paragraph, then a **category badge** at the bottom.
- Dark semi-transparent background (`bb000000`) — heads-up display overlay,
  never a light card (Earth is already dark; a light card looks jarring).
- Fonts LARGE (headline 26-28px, body 16-18px) — LG screens viewed from a
  distance.
- Multiple news items → **stack as separate cards inside the same balloon**
  (scrollable news feed panel), never multiple balloon files.

VM constraint: implemented with escaped HTML entities, NOT CDATA (Earth 7.3.3
drops any Placemark containing CDATA). Auto-open via `gx:balloonVisibility`.

## KML types by story type

### Breaking news / incident at a specific location — PARTIAL
Placemark at exact event coords with a **pulsing red circle icon**. Pair with
a gx:Tour that flies over the location, zooms to street level briefly, pulls
back to regional view. Balloon shows headline+summary while camera is
mid-flight.
Implemented: concentric pulse rings (`ring_kml`) + center icon. Tour overlay
not yet wired (gx:Tour auto-play via NetworkLink needs the myplaces
registration trick — see lg-kml-tours skill).

### Geopolitical / country-level news — PLANNED
Polygon outlining the entire country/region using border coords, filled with
semi-transparent color by sentiment (red=conflict/sanctions, blue=diplomacy,
green=agreements/deals). **Extrude slightly** for a glowing border effect at
angle. Fly camera to bird's-eye view so the whole territory spans the
panorama.
Needs: country border coordinate data (REGION_POLYGONS currently has ~10
regions only).

### Conflict / war news — PLANNED
Richest visual type, layered KMLs:
1. Country polygon fill (overall conflict zone)
2. LineString paths along active front lines with arrow styling
3. Extruded cylinders at flashpoint cities sized by reported activity
4. Displacement flow arrows (thin lines with direction) for refugee/troop
   movement corridors
Each layer = separate KML file so layers toggle independently.
`line_kml()` exists; arrowheads + layer separation + cylinder-by-intensity
are TODO.

### Economic / market news — PARTIAL
Extruded 3D columns (Polygon + relativeToGround) at financial capitals /
commodity hubs. Column height = magnitude (big drop → tall red, rally → tall
green). Trade news: LineStrings connecting countries, thickness = trade
volume.
Implemented: `column_kml()` (height param). Trade-volume lines TODO.

### Natural disaster news — PARTIAL
Single-event focused KML (not a global sweep): fly directly to region, 3D
column at epicenter/origin, radius circle (Polygon circle) for affected area,
label surrounding cities with distance markers for scale.
Implemented: `column_kml` + `ring_kml` at epicenter. City distance labels
TODO.

### Election / political news — PLANNED
Choropleth: fill each admin region (state/province/constituency) with the
leading party/outcome color — ground overlay or multiple Polygons. Extruded
columns over capital cities showing vote margin (tall = decisive, short =
close). Camera pulls back to see the whole-country pattern.
Needs: region polygon data + party-color mapping.

### Space / science news — PLANNED
Launch/orbital events: LineString **arc** from launch site to target orbit
path, Placemark icon at launch site, trajectory waypoints. Astronomical
events: ground overlay image (eclipse path, comet trajectory map). Camera
tilts up slightly toward the sky.
`arc_kml()` exists (bulged arc between two points); waypoints + overlay
images TODO.

### Multi-story news feed (no single location) — IMPLEMENTED (basic)
One Placemark per story at each story's geographic center, all loaded
together — pins across the globe simultaneously. Category-colored icon per
pin. gx:Tour hops between them in recency order (fly, pause 4s, fly...) while
the rightmost-screen balloon updates to the current story. Self-running
global briefing tour.
Current: icons + camera fly-through of top 3 via `/tmp/query.txt`; per-stop
balloon update TODO (balloon currently shows all cards at once — acceptable
per the stacked-cards standard).

## Category color reference (implemented)

| Category | Bar hex | Badge | Earth visual |
|----------|---------|-------|--------------|
| breaking | #ff2d2d | BREAKING | pulse rings + icon |
| conflict | #ff2d2d | CONFLICT | pulse rings + icon |
| disaster | #ff8c1a | DISASTER | 3D column + radius rings |
| geopolitics | #2d7fff | WORLD | icon |
| economy | #2dff6b | ECONOMY | icon (column TODO) |
| science | #ffe32d | SCIENCE | icon (arc TODO) |
| sport | #ffd32d | SPORT | icon |
| default | #9aa4b2 | NEWS | icon |
