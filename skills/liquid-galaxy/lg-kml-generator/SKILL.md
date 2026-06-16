---
name: lg-kml-generator
description: Generate, validate, deploy, and manage KML content for Liquid Galaxy rigs
version: 2.7.0
author: Hermes (on behalf of user)
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [liquid-galaxy, lg, kml, google-earth, xml, geographic]
    related_skills: [lg-ssh-control, liquid-galaxy-control]
---

# LG KML Generator

Create, validate, deploy, and manage KML (Keyhole Markup License) content for Liquid Galaxy rigs. This skill covers proper KML syntax, styling best practices, deployment to the Liquid Galaxy master node, and verification procedures.

## When to Use

Load this skill when the user requests any of:
- Creating new KML files for geographic visualization
- Updating existing KML content on Liquid Galaxy
- Validating KML syntax and structure
- Deploying KML to /var/www/html/kmls/ on lg1
- Removing or replacing KML files on the rig

Trigger phrases: `create kml`, `generate kml`, `deploy kml`, `validate kml`, `kml point`, `kml polygon`, `kml path`, `kml placemark`

## KML Fundamentals

KML is an XML-based format for displaying geographic data in Earth browsers like Google Earth and Liquid Galaxy. Key requirements:

- **Case-sensitive tags**: All tags must match exactly (e.g., `<Placemark>` not `<placemark>`)
- **Proper nesting**: Elements must appear in the correct order
- **Valid XML**: Well-formed XML with proper escaping
- **Correct coordinate order**: longitude,latitude,altitude (X,Y,Z)

## Core KML Elements

### Document Root
```xml
<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <!-- Content goes here -->
  </Document>
</kml>
```

### Placemark
A Placemark represents a geographic feature:
```xml
<Placemark>
  <name>Feature Name</name>
  <description>Feature description</description>
  <styleUrl>#styleId</styleUrl>
  <!-- Geometry goes here (Point, LineString, Polygon, etc.) -->
</Placemark>
```

### Styles
Define reusable styles for consistent visualization:
```xml
<Style id="styleId">
  <IconStyle>  <!-- For points -->
    <color>aabbggrr</color>  <!-- Alpha, Blue, Green, Red (hex) -->
    <scale>1.0</scale>
    <Icon>
      <href>http://maps.google.com/mapfiles/kml/pushpin/ylw-pushpin.png</href>
    </Icon>
  </IconStyle>
  <LabelStyle>
    <color>aabbggrr</color>
    <scale>1.0</scale>
  </LabelStyle>
  <LineStyle>  <!-- For lines/polygon outlines -->
    <color>aabbggrr</color>
    <width>2.0</width>
  </LineStyle>
  <PolyStyle>  <!-- For polygon fills -->
    <color>aabbggrr</color>
    <outline>1</outline>
    <fill>1</fill>
  </PolyStyle>
</Style>
```

### Geometry Types

#### Point
```xml
<Point>
  <coordinates>-122.0822035425683,37.42228990140251,0</coordinates>
</Point>
```

#### LineString (Path)
```xml
<LineString>
  <tessellate>1</tessellate>
  <coordinates>
    -122.0822035425683,37.42228990140251,0
    -122.081500,37.422000,0
    -122.080000,37.421500,0
  </coordinates>
</LineString>
```

#### Polygon
```xml
<Polygon>
  <tessellate>1</tessellate>
  <outerBoundaryIs>
    <LinearRing>
      <coordinates>
        -122.082,37.422,0
        -122.080,37.422,0
        -122.080,37.420,0
        -122.082,37.420,0
        -122.082,37.422,0
      </coordinates>
    </LinearRing>
  </outerBoundaryIs>
</Polygon>
```

## LG KML Architecture (This Rig)

Earth does NOT read KML files from disk directly. All KML content reaches Earth through **NetworkLinks** defined in myplaces.kml and updated dynamically by a PHP sync system.

```
Earth master screen
  └─ ~/earth/kml/master/myplaces.kml       (loaded at startup)
       ├─ NetworkLink → /kml/master.kml     (static — edited in place)
       ├─ NetworkLink → sync_nlc.php        (dynamic — polls kmls.txt every 1s)
       │    └─ reads /var/www/html/kmls.txt (URL list, one per line)
       │         └─ ─/kmls/file.kml         (actual KML file)
       └─ NetworkLink → /kml/slave_1.kml    (per-slave static)
```

### Key Paths

| Path | Purpose |
|------|---------|
| `/var/www/html/kmls/` | Web-managed KML files (upload here) |
| `/var/www/html/kmls.txt` | URL list for dynamic sync (edit to add/remove) |
| `/var/www/html/kml/master.kml` | Static master KML (needs relaunch) |
| `/var/www/html/kml/master_1.kml` | Secondary master KML (via Solo KML NL) |
| `/var/www/html/kml/slave_*.kml` | Per-slave static KML |
| `~/earth/kml/master/myplaces.kml` | Earth startup config (do NOT edit) |
| `~/earth/kml/slave/myplaces.kml` | Slave startup config (do NOT edit) |

## Deployment Methods

> **Connection mode:** Before deploying via SSH, the agent must ask the user VM/reverse tunnel or Direct LAN and resolve `$SSH_DEST` per `lg-ssh-control` pre-flight. Examples below use placeholders — substitute:
> - VM mode: `-P 2222 lg@localhost` (SCP) / `-p 2222 lg@localhost` (SSH)
> - Direct LAN: `lg@<lg-master-ip>` (omit `-P`/`-p` flag, port 22)

### CRITICAL: Always Include a LookAt

Every KML deployed to this rig **must** include a `<LookAt>` element that flies Earth to the right location. Without it, Earth stays at its default view (Paris — the LG Controller Pin in master.kml), and your KML content exists but is invisible off-screen.

```xml
<LookAt>
  <longitude>74.0</longitude>
  <latitude>15.5</latitude>
  <altitude>0</altitude>
  <range>500000</range>
  <tilt>0</tilt>
  <heading>0</heading>
</LookAt>
```
Place `<LookAt>` inside `<Document>`, before any Placemarks.

### Method B: Static Master KML (No Relaunch Needed)

**This rig now has permanent 3s auto-refresh on master.kml's NetworkLink** (applied via `lg-master-refresh-set`). Writing to `master.kml` auto-appears within 3 seconds — no relaunch needed.

```bash
# 1. Copy KML to master.kml (overwrites)
#    VM mode: -P 2222 lg@localhost     Direct LAN: lg@<lg-master-ip>
sshpass -p 'lg' scp -P $SSH_PORT -o StrictHostKeyChecking=no \
  local_file.kml $SSH_DEST:/var/www/html/kml/master.kml

# 2. Wait ~3s — Earth auto-refreshes
```

**For maximum reliability**, also deploy the same file to kmls/ and add its URL to kmls.txt (Method A below). Both channels work simultaneously.

### Method A: Dynamic Sync (Experimental — No Relaunch)

The fastest way to show KML. Earth polls `sync_nlc.php` every 1s via NetworkLink, which reads URLs from `kmls.txt`. Adding a URL makes it appear automatically.

```bash
# 1. Copy KML file to lg1
#    VM mode: -P 2222 lg@localhost     Direct LAN: lg@<lg-master-ip>
sshpass -p 'lg' scp -P $SSH_PORT -o StrictHostKeyChecking=no \
  local_file.kml $SSH_DEST:/var/www/html/kmls/

# 2. Verify file is web-accessible (uses internal http://lg1:81 which works in both modes)
sshpass -p 'lg' ssh -o StrictHostKeyChecking=no $SSH_DEST \
  "curl -s -o /dev/null -w '%{http_code}' http://lg1:81/kmls/local_file.kml"
# Expected: 200

# 3. Add URL to kmls.txt — Earth auto-loads it within ~1s
sshpass -p 'lg' ssh -o StrictHostKeyChecking=no $SSH_DEST \
  "printf '%s\n' 'http://lg1:81/kmls/local_file.kml' > /var/www/html/kmls.txt"
```
**Note:** If kmls.txt already has other entries, append with `>>` not `>`.
Use `printf` rather than `echo` to avoid leading/trailing whitespace issues.

**To remove:** delete the line from kmls.txt, then delete the file.
```bash
# Remove URL from kmls.txt (rewrite without targeted line)
sshpass -p 'lg' ssh -o StrictHostKeyChecking=no $SSH_DEST \
  "grep -v 'local_file.kml' /var/www/html/kmls.txt > /tmp/kmls.txt && mv /tmp/kmls.txt /var/www/html/kmls.txt"

# Remove the KML file
sshpass -p 'lg' ssh -o StrictHostKeyChecking=no $SSH_DEST \
  "rm /var/www/html/kmls/local_file.kml"
```
Earth removes the NetworkLink within ~1s of kmls.txt changing. No relaunch needed.

### Deployment Script
The included `scripts/lg-kml-deploy.sh` handles validation + SCP + verification in one command. After running it, add the URL to kmls.txt manually (Method A) or relaunch (Method B).

```bash
# Deploy file with validation + verification (no relaunch)
bash /path/to/lg-kml-deploy.sh -f myfile.kml

# Deploy and trigger relaunch (Method B)
bash /path/to/lg-kml-deploy.sh -f myfile.kml -r
```
Defaults: host=localhost, port=2222, password=lg (VM mode). Override with env vars:
`LG_HOST`, `LG_PORT`, `LG_PASSWORD`.
For Direct LAN mode: `LG_HOST=<lg-master-ip> LG_PORT=22 bash /path/to/lg-kml-deploy.sh -f myfile.kml`.

---

## Screen Layout & KML Placement

This rig uses fixed screen positions for specific KML types:

| Content Type | Screen | Position | KML File |
|-------------|--------|----------|----------|
| **Logo** | Leftmost screen | Top-left corner | `slave_X.kml` (usually slave_1 or lowest index) |
| **Balloon / Index** | Rightmost screen | Top-right corner | `slave_X.kml` (highest index) |
| **3D content, Tours** | All screens (synced) | World-centered | `master.kml` |

Logos use `<ScreenOverlay>` KML — they float on screen regardless of Earth camera position.

---

## Logo Deployment (ScreenOverlay KML)

Deploying a logo requires: (1) upload image, (2) write ScreenOverlay KML, (3) trigger refresh.

**Working logo file on this rig:** `/var/www/html/kml/logo_overlay.kml`
**Logo image:** `/var/www/html/kml/logo.png` (8086 bytes, 200x200)
**URL format used by working KML:** `http://lg1/kml/logo.png` (no `:81` port)
**Size:** 200x200 pixels
**Position:** top-left corner (`x="0" y="1"`)

### Step 1: Upload image to lg1 web server
```bash
# Upload PNG to /var/www/html/kml/ (NOT /images/)
sshpass -p 'lg' scp -P $SSH_PORT -o StrictHostKeyChecking=no \
  logo.png $SSH_DEST:/var/www/html/kml/logo.png
```

### Step 2: Create ScreenOverlay KML
```xml
<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2">
<Document>
  <name>Left Screen Logo</name>
  <ScreenOverlay>
    <name>LG Logo - Left</name>
    <Icon>
      <href>http://lg1/kml/logo.png</href>
    </Icon>
    <overlayXY x="0" y="1" xunits="fraction" yunits="fraction"/>
    <screenXY x="0" y="1" xunits="fraction" yunits="fraction"/>
    <rotationXY x="0" y="0" xunits="fraction" yunits="fraction"/>
    <size x="200" y="200" xunits="pixels" yunits="pixels"/>
  </ScreenOverlay>
</Document>
</kml>
```
The `overlayXY`/`screenXY` of `x="0" y="1"` pins to top-left corner. Size 200x200 matches the working file on this rig.

### Step 3: Write KML to slave file and trigger refresh
```bash
# Write KML (escaped for remote echo)
sshpass -p 'lg' ssh -o StrictHostKeyChecking=no $SSH_DEST \
  "cat > /var/www/html/kml/slave_1.kml << 'KMLEOF'
<?xml version=\\\"1.0\\\" encoding=\\\"UTF-8\\\"?>
<kml xmlns=\\\"http://www.opengis.net/kml/2.2\\\" xmlns:gx=\\\"http://www.google.com/kml/ext/2.2\\\">
<Document>
  <name>Left Screen Logo</name>
  <ScreenOverlay>
    <name>LG Logo - Left</name>
    <Icon>
      <href>http://lg1/kml/logo.png</href>
    </Icon>
    <overlayXY x=\\\"0\\\" y=\\\"1\\\" xunits=\\\"fraction\\\" yunits=\\\"fraction\\\"/>
    <screenXY x=\\\"0\\\" y=\\\"1\\\" xunits=\\\"fraction\\\" yunits=\\\"fraction\\\"/>
    <rotationXY x=\\\"0\\\" y=\\\"0\\\" xunits=\\\"fraction\\\" yunits=\\\"fraction\\\"/>
    <size x=\\\"200\\\" y=\\\"200\\\" xunits=\\\"pixels\\\" yunits=\\\"pixels\\\"/>
  </ScreenOverlay>
</Document>
</kml>
KMLEOF\"

# 4. Trigger refresh (uses setRefresh helper if slaves reachable)
sshpass -p 'lg' ssh -o StrictHostKeyChecking=no $SSH_DEST '/home/lg/bin/lg-refresh-set'
```
---

## Force Refresh Mechanism (sed-based)

> **CORRECTED APPROACH** — The old method appended `<refreshMode>` after `</href>`, placing it **outside** the `<Link>` element. Earth ignores it as invalid XML. See "How it works" below for the proper method.

### How it works

`myplaces.kml` contains `<NetworkLink>` entries pointing to KML files. To force Earth to reload without relaunch, `<refreshMode>` must be placed **inside** the `<Link>` element, **before** `</Link>`.

```xml
<!-- WRONG — tags after </href> are OUTSIDE <Link>, Earth ignores them -->
<Link>
  <href>##LG_PHPIFACE##kml/master.kml</href>
</Link>
<refreshMode>onInterval</refreshMode>    ← IGNORED

<!-- CORRECT — tags before </Link> are INSIDE <Link>, Earth processes them -->
<Link>
  <href>##LG_PHPIFACE##kml/master.kml</href>
  <refreshMode>onInterval</refreshMode>  ← Earth picks this up
  <refreshInterval>5</refreshInterval>   ← polls every 5 seconds
</Link>
```

### Permanent Fix (Recommended — Do Once)

Add a permanent `refreshInterval` to the Master KML NetworkLink by editing `~/earth/kml/master/myplaces.kml`.

**CRITICAL: myplaces.kml is read ONCE at Earth startup.** Editing it while Earth runs has no immediate effect. The workflow is:

1. Apply the fix (add refreshInterval to myplaces.kml)
2. Relaunch Earth ONCE (so it picks up the new myplaces.kml)
3. After relaunch, any write to `master.kml` auto-appears within N seconds — no more sed or relaunch needed

On this rig, the fix is **already applied** (3s interval, via `lg-master-refresh-set`). Step 2 (relaunch) is needed for it to take effect.

To verify the fix is in place:
```bash
sshpass -p 'lg' ssh -o StrictHostKeyChecking=no $SSH_DEST "grep -A4 'master.kml' ~/earth/kml/master/myplaces.kml"
```
Expected output contains `<refreshMode>onInterval</refreshMode><refreshInterval>3</refreshInterval>` inside `<Link>`.

**To apply on a fresh rig:**
```bash
# One-time fix: add Ns auto-refresh to Master KML link
sshpass -p 'lg' ssh -o StrictHostKeyChecking=no $SSH_DEST \
  "sed -i '\\\\|<href>[^<]*master.kml</href>|{n;s|</Link>|<refreshMode>onInterval</refreshMode><refreshInterval>3</refreshInterval></Link>|}' ~/earth/kml/master/myplaces.kml"
# Then relaunch Earth once
sshpass -p 'lg' ssh -o StrictHostKeyChecking=no $SSH_DEST '/home/lg/bin/lg-relaunch-direct'
```

After relaunch, simply writing to `/var/www/html/kml/master.kml` is enough — Earth picks it up within 3s automatically.

### One-shot Refresh (If permanent fix not applied)

If you haven't applied the permanent fix and need a one-time refresh:

```bash
# Step 1: Inject refreshMode INSIDE <Link> (before </Link>)
sshpass -p 'lg' ssh -o StrictHostKeyChecking=no $SSH_DEST \
  "sed -i '\\|<href>[^<]*master.kml</href>|{n;s|</Link>|<refreshMode>onInterval</refreshMode><refreshInterval>1</refreshInterval></Link>|}' ~/earth/kml/master/myplaces.kml"

sleep 1

# Step 2: Remove the temporary refresh tags
sshpass -p 'lg' ssh -o StrictHostKeyChecking=no $SSH_DEST \
  "sed -i '\\|<href>[^<]*master.kml</href>|{n;s|<refreshMode>onInterval</refreshMode><refreshInterval>1</refreshInterval></Link>|</Link>|}' ~/earth/kml/master/myplaces.kml"
```

### _forceRefresh_slave (for slave_X.kml)

Same logic for slave files, targeting `~/earth/kml/slave/myplaces.kml`. **The actual file uses `slave_x.kml`** (PHP-resolved variable), not per-number filenames like `slave_3.kml`.

```bash
# One-time: add 2s auto-refresh to a slave Solo KML link
sshpass -p 'lg' ssh -o StrictHostKeyChecking=no $SSH_DEST \
  "sed -i '\\\\|<href>[^<]*slave_x.kml</href>|{n;s|</Link>|<refreshMode>onInterval</refreshMode><refreshInterval>2</refreshInterval></Link>|}' ~/earth/kml/slave/myplaces.kml"
```

For one-shot refresh (inject then remove after 1 second):
```bash
sshpass -p 'lg' ssh -o StrictHostKeyChecking=no $SSH_DEST \
  "sed -i '\\\\|<href>[^<]*slave_x.kml</href>|{n;s|</Link>|<refreshMode>onInterval</refreshMode><refreshInterval>1</refreshInterval></Link>|}' ~/earth/kml/slave/myplaces.kml && sleep 1 && sed -i '\\\\|<href>[^<]*slave_x.kml</href>|{n;s|<refreshMode>onInterval</refreshMode><refreshInterval>1</refreshInterval></Link>|</Link>|}' ~/earth/kml/slave/myplaces.kml"
```

---

## setRefresh — Enable Auto-Poll on Slave Screens

The `setRefresh` function adds a 2-second auto-refresh on slave Solo KML NetworkLinks, so any KML written to `slave_X.kml` appears automatically without manual refresh or relaunch.

The actual `myplaces.kml` on each slave uses a PHP-resolved `slave_x.kml` (not numbered `slave_2.kml`). The corrected sed approach injects `<refreshMode>`/`<refreshInterval>` **inside** `<Link>` before `</Link>` — Earth ignores tags placed outside `<Link>`.

### Using the Deployed Helpers (Recommended)

Helpers are already deployed at `/home/lg/bin/lg-refresh-set` and `/home/lg/bin/lg-refresh-reset`:

```bash
# Set 2s auto-refresh on all slave Solo KML links
sshpass -p 'lg' ssh -o StrictHostKeyChecking=no $SSH_DEST '/home/lg/bin/lg-refresh-set'

# Reset (remove refresh tags)
sshpass -p 'lg' ssh -o StrictHostKeyChecking=no $SSH_DEST '/home/lg/bin/lg-refresh-reset'
```

The set helper does a reset-then-set: strips any stale refresh tags first, then injects fresh ones. The reset helper only strips.

**⚠️ CRITICAL: setRefresh edits `myplaces.kml` on each slave, but Earth reads myplaces.kml only at startup.** After running setRefresh, the change is written to disk but Earth won't pick it up until the screen is relaunched. The proper workflow is:

1. Run `lg-refresh-set` (adds refreshInterval to slave myplaces.kml)
2. Relaunch Earth on slaves (or the whole rig)
3. After relaunch, any write to `slave_X.kml` auto-appears within 2s — no more refresh commands needed

This is a **one-time setup per session**. Once applied + relaunch, the auto-refresh persists across future Earth restarts (since myplaces.kml is saved back to disk). The same applies to the master permanent fix — apply once in myplaces.kml, relaunch once, then KML writes auto-appear from then on.

### Inline Command

```bash
# Set 2s refresh on all slaves
sshpass -p 'lg' ssh -o StrictHostKeyChecking=no $SSH_DEST \
  "for lg in \$(cat /etc/hostname); do
     [ \"\$lg\" = \"\$(hostname)\" ] && continue
     sshpass -p 'lg' ssh -o ConnectTimeout=5 -t lg@\$lg \
       \"echo 'lg' | sudo -S sed -i '\\\\|<href>[^<]*slave_x.kml</href>|{n;s|</Link>|<refreshMode>onInterval</refreshMode><refreshInterval>2</refreshInterval></Link>|}' ~/earth/kml/slave/myplaces.kml\" 2>/dev/null
   done"
```

**Note:** Slaves (lg2, lg3...) are only reachable in Direct LAN mode. On VM setups with only lg1, the helpers exist but have no slaves to refresh.

### What Changed vs the Original Dart Code

The original Flutter/Dart implementation did per-slave iteration (lg2, lg3...) with `slave_$i.kml` and used a reset-then-set approach:
1. `s|replace|search|` — strip any existing refresh
2. `s|search|replace|` — add fresh refresh

The deployed helpers (v2) use the corrected approach:
- Match `<href>[^<]*slave_x.kml</href>` — matches the actual file contents (PHP variable form)
- Inject before `</Link>` — places refreshMode **inside** `<Link>`, where Earth reads it
- Same reset-then-set pattern for clean state

**Before/after on the slave myplaces.kml:**
```xml
<!-- Before: no refresh -->
<Link>
  <href>##LG_PHPIFACE##kml/slave_x.kml</href>
</Link>

<!-- After: 2s auto-refresh -->
<Link>
  <href>##LG_PHPIFACE##kml/slave_x.kml</href>
  <refreshMode>onInterval</refreshMode>
  <refreshInterval>2</refreshInterval>
</Link>
```

---

## Clearing KML Content

When removing logos or KMLs, overwrite the file with a blank KML and then refresh:

```bash
# Write blank KML (uses slave_x.kml — the PHP-resolved form used by all slaves)
sshpass -p 'lg' ssh -o StrictHostKeyChecking=no $SSH_DEST \
  "printf '%s\\\\n' '<?xml version=\\\"1.0\\\" encoding=\\\"UTF-8\\\"?>' \
    '<kml xmlns=\\\"http://www.opengis.net/kml/2.2\\\">' \
    '<Document><name>Empty</name></Document>' \
    '</kml>' > /var/www/html/kml/slave_x.kml"

# Refresh to clear (use helper or one-shot sed)
sshpass -p 'lg' ssh -o StrictHostKeyChecking=no $SSH_DEST '/home/lg/bin/lg-refresh-set'
```


## Validation Procedures

### Syntax Validation
Use xmllint to validate KML structure:
```bash
xmllint --noout your_file.kml
```

### Common Validation Checks
- All tags properly closed
- Correct element ordering within Placemark
- Valid coordinate format (longitude,latitude[,altitude])
- Proper hex color format (aabbggrr or rrggbb)
- Scale values are positive numbers

## Best Practices for Liquid Galaxy

### Visibility & Contrast
- Use high-contrast colors: bright yellow, cyan, magenta against dark backgrounds
- Avoid low-contrast combinations like gray-on-gray or dark blue on black
- For points: use scale 1.2-1.5 for visibility on large screens
- For lines: use width 2.0-3.0 for clarity

### Simplicity
- Start with simple geometries (points, basic polygons) before complex shapes
- Limit coordinate precision to 4-6 decimal places (sufficient for Liquid Galaxy resolution)
- Use descriptive but concise names and descriptions

### Performance
- Avoid extremely complex polygons with thousands of vertices
- Consider using NetworkLinks for large datasets that should be dynamically loaded
- Keep individual KML files under 5MB for optimal performance

## File Management

### Creating New KML
1. Generate valid KML content using templates
2. Validate XML syntax (Python xml.etree or xmllint)
3. Deploy to /var/www/html/kmls/ via scp
4. Verify file is web-accessible: `curl http://lg1:81/kmls/file.kml`
5. Add URL to /var/www/html/kmls.txt for dynamic load

### Updating Existing KML
1. Create updated version locally
2. Validate syntax
3. Deploy (overwrites existing file at /var/www/html/kmls/)
4. Verify — no need to modify kmls.txt (same URL, Earth re-fetches on next poll)

### Removing KML
Dynamic method (preferred — no relaunch):
1. Remove URL from kmls.txt:
   ```bash
   sshpass -p 'lg' ssh -p 2222 lg@localhost \
     "grep -v 'file.kml' /var/www/html/kmls.txt > /tmp/kmls.txt && mv /tmp/kmls.txt /var/www/html/kmls.txt"
   ```
2. Delete the file:
   ```bash
   sshpass -p 'lg' ssh -p 2222 lg@localhost \
     "rm /var/www/html/kmls/file.kml"
   ```
Earth auto-removes the NetworkLink within ~1s.

Static method (needs relaunch — only needed if permanent refreshInterval not added):
1. Remove content from /var/www/html/kml/master.kml
2. Relaunch Earth via `$SSH_DEST`

## Verification Checklist

After KML deployment:
- [ ] File exists in /var/www/html/kmls/ with correct permissions
- [ ] Also copied to /var/www/html/kml/master.kml if using static method
- [ ] File passes XML validation (Python xml.etree or xmllint)
- [ ] File is web-accessible: `curl -o /dev/null -w '%{http_code}' http://lg1:81/kmls/file.kml` returns 200
- [ ] URL is in /var/www/html/kmls.txt (for Method A dynamic sync)
- [ ] **Contains `<LookAt>` element** that flies Earth to the right location — without it, KML loads but is invisible off-screen
- [ ] Coordinates are in valid range (-180 to 180 longitude, -90 to 90 latitude)
- [ ] Colors are in proper hex format (aabbggrr)
- [ ] Earth is running after relaunch: `pgrep -a googleearth` shows the process

## Troubleshooting

### Common Issues
- **KML file deployed but NOTHING visible on screen**: 99% chance you forgot the `<LookAt>` element. Earth loads the KML content but shows the default view (Paris). Always include a LookAt that flies to your coordinates.
- **KML changes only appear after relaunch**: The Master KML NetworkLink has no `refreshMode`. Apply the permanent fix (add `refreshInterval=5` inside `<Link>`) — see "Force Refresh Mechanism" section.
- **File not displaying after copy to kmls/**: Earth doesn't read kmls/ directly. Run Method B (write to master.kml + relaunch) or Method A (add URL to kmls.txt). Simply having the file in kmls/ is not enough.
- **File not displaying after kmls.txt update**: URL format must match web server path. Use `http://lg1:81/kmls/` prefix. Verify with `curl http://lg1:81/kmls/file.kml` on lg1.
- **"KML not found" in Earth**: The web server on lg1 runs on port 81 (not 80). Ensure URL uses `:81`.
- **kmls.txt has blank lines**: `printf` is safer than `echo` for writing URLs. Blank lines are ignored by PHP's `getKmlListUrls()` (trims to empty string, skips) but avoid them for cleanliness.
- **Incorrect coordinates**: Verify longitude,latitude order (not latitude,longitude)
- **Colors not showing**: Ensure proper hex format (aabbggrr, not #rrggbb)
- **Geometry missing after relaunch**: Check /var/www/html/kml/master.kml content. If using Method A, the kmls.txt approach doesn't need a relaunch at all.
- **Performance issues**: Simplify geometry or reduce file size

### Sync System Debugging
If a KML added via kmls.txt doesn't appear:
1. Verify the URL is in kmls.txt: `cat /var/www/html/kmls.txt`
2. Verify the file is web-accessible: `curl -I http://lg1:81/kmls/file.kml` (expect 200)
3. Check for URL typos (trailing spaces, wrong port)
4. Ensure the sync PHP is running: Earth polls sync_nlc.php every 1s — it doesn't need to be triggered
5. For a full reset: restart Earth (relaunch) to reload myplaces.kml from scratch

### Connection Troubleshooting
If SSH/deployment fails:
1. Verify connection mode (VM/tunnel vs Direct LAN) — ask user
2. VM mode: check tunnel is up: `ss -tlnp | grep :2222`; if missing, ask laptop user for `ssh -N -R 2222:192.168.53.3:22 nara@<pi-ip>`
3. Direct LAN mode: verify ping + SSH to the master IP
4. Verify target directory exists: `sshpass -p 'lg' ssh -o StrictHostKeyChecking=no $SSH_DEST "ls /var/www/html/kmls/"`

## Templates

Templates are also available as files under the skill's `templates/` directory for direct use. Copy them and modify the placeholders.

### Available Template Files

| File | Purpose |
|------|---------|
| `templates/3d-pyramid.kml` | 3D pyramid with 4 colored faces, altitudeMode:absolute. Replace `[lon]`, `[lat]`, `[d]`, `[alt]` placeholders. |
| `templates/greenland-pyramid.kml` | Working 3D pyramid example (Greenland, tested on this rig) with LookAt and all face styles. Copy-modify-replace. |
| `templates/logo-overlay.kml` | ScreenOverlay for a logo image at `/kml/logo.png`, 200x200px, top-left corner. Matches the working file on this rig. |
| `templates/sample-placemark.kml` | Simple point placemark (NYC) with LookAt. Good starting point for a basic KML. |
| `templates/kerala-before-flood.kml` | Working example with 6 district placemarks, styled labels, and Folders. Real-world LG disaster layer. |

### Basic Point Marker Template
```xml
<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <name>{name}</name>
    <description>{description}</description>
    <Style id="pointStyle">
      <IconStyle>
        <color>{color}</color>
        <scale>{scale}</scale>
        <Icon>
          <href>{icon_href}</href>
        </Icon>
      </IconStyle>
      <LabelStyle>
        <color>{label_color}</color>
      </LabelStyle>
    </Style>
    <Placemark>
      <name>{placemark_name}</name>
      <description>{placemark_description}</description>
      <styleUrl>#pointStyle</styleUrl>
      <Point>
        <coordinates>{longitude},{latitude},{altitude}</coordinates>
      </Point>
    </Placemark>
  </Document>
</kml>
```

### Simple Polygon Template
```xml
<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <name>{name}</name>
    <description>{description}</description>
    <Style id="polyStyle">
      <LineStyle>
        <color>{outline_color}</color>
        <width>{outline_width}</width>
      </LineStyle>
      <PolyStyle>
        <color>{fill_color}</color>
        <outline>{outline}</outline>
        <fill>{fill}</fill>
      </PolyStyle>
    </Style>
    <Placemark>
      <name>{placemark_name}</name>
      <description>{placemark_description}</description>
      <styleUrl>#polyStyle</styleUrl>
      <Polygon>
        <tessellate>1</tessellate>
        <outerBoundaryIs>
          <LinearRing>
            <coordinates>
{coordinates}
            </coordinates>
          </LinearRing>
        </outerBoundaryIs>
      </Polygon>
    </Placemark>
  </Document>
</kml>
```

### 3D Polygon (altitudeMode)

For extruded/3D geometry, use `<altitudeMode>absolute</altitudeMode>` and specify altitudes in the coordinate triples. A 3D pyramid is made of 4 triangular face polygons meeting at a peak altitude.  
**Template file:** `templates/3d-pyramid.kml` — copy it and replace the `[name]`, `[lon]`, `[lat]`, `[d]` (half-width), and `[alt]` (peak height) placeholders.

**Working example (tested on this rig):** `templates/greenland-pyramid.kml` — 110km base, 50km tall, 4 colored faces at 41°W,71°N, with `<LookAt>` and all face styles. Copy-modify-deploy for any location.

Key differences from 2D polygons:
- **altitudeMode**: Must be `absolute` (not `clampToGround`, the default)
- **Altitude values**: Set Z in each `<coordinates>` triple (e.g. `lon,lat,2000`)
- **Triangles**: Each face needs exactly 3 coordinate points (base edge + peak)
- **No tessellation**: `<tessellate>` is omitted or set to 0 for 3D geometry
- **Base footprint**: Always add a 2D ground polygon (no altitudeMode) so the base is visible even from directly above

## Related Operations

After deploying KML, consider:
- Using `lg-ssh-control` to relaunch the rig for immediate viewing (Method B only)
- Applying the permanent refreshInterval fix so future KML writes auto-appear
- Setting up auto-refresh for dynamic KML content
- Creating NetworkLinks for large datasets that should be fetched remotely
- Scheduling regular updates for time-sensitive geographic data

## References

- `references/lg-kml-architecture.md` — Full architecture detail: Earth loading chain, sync PHP internals, slave screen setup, web UI, and debugging techniques.
- `references/force-refresh-debug.md` — Debugging the force refresh mechanism: why the old sed approach failed, the corrected approach, and the actual myplaces.kml format from this rig.
- `references/myplaces-kml-refresh-workflow.md` — The complete workflow for making myplaces.kml changes permanent: edit → relaunch once → auto-refresh forever. Covers master and slave, the corrected sed approach, and helper scripts.
