# LG KML Architecture — Discovered 2026-06-15

## Two Data Paths to Earth

### 1. Dynamic Sync (via kmls.txt) — PREFERRED

```
User/Agent
  │  scp file.kml ──→ /var/www/html/kmls/file.kml
  │  append URL  ──→ /var/www/html/kmls.txt
  │                    (URL: http://lg1:81/kmls/file.kml)
  ▼
sync_nlc.php (polls kmls.txt every 1s via filemtime)
  │  detects new URL
  │  generates NetworkLinkControl <Update><Create> KML
  ▼
Earth master screen receives NetworkLinkControl via its polling connection
  │  creates NetworkLink to http://lg1:81/kmls/file.kml
  │  loads and renders the KML
```

Key files on the rig:
- `/var/www/html/kmls/` — stores uploaded KML files (served via Apache on :81)
- `/var/www/html/kmls.txt` — one URL per line, read by sync PHP
- `/var/www/html/sync_nlc.php` — PHP endpoint polled by Earth every 1s
- `/var/www/html/sync_nlc_base.php` — core sync logic (NetworkLink generation)

The sync PHP (`sync_nlc_base.php`) works by:
1. Reading kmls.txt via `getKmlListUrls()`
2. Comparing with the client's `?client_kmls=` cookie parameter (MD5 list)
3. Generating `NetworkLinkControl` with `<Create>` (add) and `<Delete>` (remove) elements
4. Targeting Document `id="master"` (or `"master_1"` for slave sync)
5. Keeping the connection alive for 10s, polling filemtime each second
6. When kmls.txt changes (filemtime > client timestamp), it sends the update

### 2. Static Master KML (via master.kml) — Needs Relaunch

```
User/Agent
  │  scp file.kml ──→ /var/www/html/kml/master.kml
  ▼
Relaunch Earth (service lightdm restart)
  │  Earth restarts, reads ~/earth/kml/master/myplaces.kml
  │  myplaces.kml has NetworkLink to http://lg1:81/kml/master.kml
  ▼
Earth loads master.kml content at startup
```

## Earth Startup Config (myplaces.kml)

File: `~/earth/kml/master/myplaces.kml` (do NOT edit directly)

Contains a `<Folder name="KML Sync">` with these NetworkLinks:

| NetworkLink | Target | Refresh |
|---|---|---|
| Master KML | `/kml/master.kml` | Once (startup) |
| KML Update | `sync_nlc.php` | onInterval, 1s |
| View Placemark | `cgi-bin/viewCenteredPlacemark.py?` | onStop (view change) |
| Solo KML | `kml/master_1.kml` | Once (startup) |
| Solo KML Update | `sync_nlc_1.php` | onInterval, 1s |

## Slave Screens

Each slave (lg2..lgN) has its own `~/earth/kml/slave/myplaces.kml` with:
- `sync_nlc_x.php` (where x = slave number) — reads `kmls_x.txt`
- Static per-slave KML at `/var/www/html/kml/slave_x.kml`

Adding a URL to `kmls.txt` (no suffix) targets the MASTER screen only.
Adding a URL to `kmls_1.txt` targets slave lg2's Solo KML NetworkLink.

## Web Interface (index.php)

The web UI at `http://lg1:81/` provides:
- Layer toggles (planet-based KML groups from `/var/www/kml/earth/`, `/var/www/kml/moon/`, etc.)
- KML management via touchscreen sync API (`sync_touchscreen.php` with `touch_action=add|delete`)
- kmls.txt management through the web UI

## URLs & Web Server

- Apache runs on port 81 (not 80)
- `http://lg1:81/kmls/` maps to `/var/www/html/kmls/`
- `http://lg1:81/kml/` maps to `/var/www/html/kml/`
- The PHP `$KML_SERVER_BASE` is `http://lg1:81/kml/`
- The PHP `$KML_SYS_PATH` is `/var/www/kml/` (planet layers)

## Debugging Sync

To see what the sync PHP returns (simulate Earth's poll):
```bash
sshpass -p 'lg' ssh -p 2222 lg@localhost \
  "curl -s 'http://localhost:81/sync_nlc.php?t=0&client_kmls='"
```
This forces a fresh poll with no cached KMLs. The response is the NetworkLinkControl KML.
