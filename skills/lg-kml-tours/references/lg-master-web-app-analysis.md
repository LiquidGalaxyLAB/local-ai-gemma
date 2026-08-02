# LG-Master-Web-App — Flutter KML & SSH Patterns

Repo: https://github.com/LiquidGalaxyLAB/LG-Master-Web-App

## Core Architecture (lg_service.dart)

Singleton `LgService` extends `ChangeNotifier`. Holds `LgConnectionModel` (ip,
port, username, password, screens). Uses `dartssh2` package for SSH.

### Connection
- `SSHSocket.connect(ip, port)` with timeout
- `SSHClient(socket, username, onPasswordRequest, keepAliveInterval: 10s)`
- Auto-reconnect: max 5 attempts, 3s delay between retries
- Periodic connection check every 5s

### Key Methods

**execute(command, successMessage)** — Core method. Sends SSH command, returns
result. All other methods build on this.

**query(content)** — Writes to `/tmp/query.txt`:
```dart
await execute('echo "$content" > /tmp/query.txt', 'Query sent: $content');
```

**flyTo(kmlViewTag)** — Writes flytoview to query file:
```dart
await query('flytoview=$kmlViewTag');
```

**uploadKml(content, fileName)** — Uses SFTP to write KML to
`/var/www/html/<filename>`. Appends random number to avoid overwrites.
Writes URL to `/var/www/html/kmls.txt`.

**sendLogo()** — Writes ScreenOverlay KML to leftmost slave:
```dart
"echo '$kmlContent' > /var/www/html/kml/slave_$leftMostScreen.kml"
```
Uses `calculateLeftMostScreen(screens)` — frame-count agnostic.

**forceRefresh(screenNumber)** — Temporarily adds 1s refreshInterval to slave
myplaces.kml via `sed`, waits 1s, then removes it. Forces immediate reload.

### Screen Math
- `calculateRightMostScreen(n)` = n==1 ? 1 : floor(n/2) + 1
- `calculateLeftMostScreen(n)` = n==1 ? 1 : floor(n/2) + 2

Both are frame-count agnostic.

### Frame Count Handling
Default screens = 5. Stored in `LgConnectionModel.screens`. All loops use
this variable, not hardcoded values. The app is fully frame-count agnostic.

## KML Upload (kml.dart screen)

Pattern: connectToLG → uploadKml via SFTP → wait 1s → forceRefresh → flyTo
KML files loaded from assets via `rootBundle.loadString()`.

## Node.js Server Integration (nodejs.dart)

External Node.js server on Render. Flask/Express-style HTTP endpoint.
App sends GET requests to check server status.

## Key Takeaways for Hermes LG Tools
1. All LG operations are SSH commands wrapped as `execute()` calls
2. `query()` method targets `/tmp/query.txt` — same pattern we use
3. Force refresh is a temporary sed injection (add→wait→remove)
4. Screen calculations (`leftMostScreen`, `rightMostScreen`) are generic
5. SFTP used for KML uploads instead of echo redirects
6. Frame count stored in config, never hardcoded — loop over `screens`
