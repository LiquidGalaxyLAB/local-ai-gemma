# Liquid Galaxy Demo Suite — Android App

A Flutter Android controller for a Liquid Galaxy rig. Drive pre-baked KML
visualizations on the multi-screen Google Earth cluster over SSH.

Built against the conventions of the LiquidGalaxyLAB org's Flutter apps
(Super Liquid Galaxy Controller, La Palma Volcano tracker):
`dartssh2` SSH, `flytoview` via `/tmp/query.txt`, SFTP KML push to
`/var/www/html/kml/`, and the LG screen formula
`rightmost = N ~/ 2 + 1` (panels), `leftmost = N ~/ 2 + 2` (logo).

## Contents

- `lib/` — app source
  - `main.dart` — entry point (Provider + MaterialApp)
  - `theme.dart` — LG "mission control" dark palette
  - `models/skill.dart` — Skill / Visualization models + skills.json loader
  - `services/lg_service.dart` — SSH + KML deploy + fly-to + admin actions
  - `controllers/app_state.dart` — settings persistence + action dispatch
  - `screens/` — splash, home (skill grid), skill detail, settings
- `assets/skills.json` — single source of truth: 17 skills × 36 visualizations
  (KML asset paths, fly-to coords, tour flags)
- `assets/kml/` — pre-baked KML + right-screen panel PNGs

## Configure (Settings screen)

Fields (all persisted via SharedPreferences, surviving restarts):

| Field | Meaning | Default |
|-------|---------|---------|
| Master IP address | LG master node (lg1) IP | — |
| SSH username | LG rig user | `lg` |
| SSH password | LG rig password | `lg` |
| SSH port | SSH port | `22` |
| Number of screens | Used to compute rightmost/leftmost screens | `3` |

"Test connection" opens an SSH session and reports success/failure.

Advanced (bottom of Settings): Show logo (leftmost screen), Relaunch Earth
(restart display manager on all screens), Reboot rig (with confirm dialog).

## Run

On any machine with Flutter 3.24+ and the Android SDK:

```
flutter pub get
flutter build apk --release
# APK at build/app/outputs/flutter-apk/app-release.apk
```

Or debug-run on a connected tablet:

```
flutter run
```

## How a visualization deploys (in order)

1. Fly-to opening shot → `echo "flytoview=<LookAt>" > /tmp/query.txt`
2. Master KML → SFTP upload + `sudo cp` to `/var/www/html/kml/master.kml`
3. Rightmost panel PNG + ScreenOverlay KML → `slave_<rightmost>.kml`
4. Optional `playtour=<name>` for tour playback

## Known limitations

- Built on ARM64 (Raspberry Pi) under box64 x86_64 emulation; the APK itself
  is a standard Android ARM64 artifact, independent of the build host.
- Release APK is signed with the Liquid Galaxy Demo Suite release certificate.
- Requires network reachability to the rig's master node from the tablet.
- No live data at demo time: all KML is pre-baked (by design — reliability
  over flexibility).
- Tour playback is only triggered when a visualization defines a `tour`
  (most are static overlays the presenter narrates manually).
