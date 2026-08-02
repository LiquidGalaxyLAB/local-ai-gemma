# flyToView=1 Fix for master.kml Auto-Positioning

## Problem

Deploying a new KML to `/var/www/html/kml/master.kml` via the 3s NetworkLink refresh
shows placemarks and polygons but **the camera never moves** to the Document's
`<LookAt>` position. The LookAt only works on Earth's initial launch when
`~/earth/kml/master/myplaces.kml` is first parsed.

## Root Cause

The master KML NetworkLink in `myplaces.kml` had no `<flyToView>` element.
In KML, `flyToView` defaults to `0` (false) when absent. So Earth loads new
KML content on each refresh but never re-processes the Document LookAt.

## Fix

Add `<flyToView>1</flyToView>` to the master KML NetworkLink in
`~/earth/kml/master/myplaces.kml`. This tells Earth to check the loaded KML's
Document LookAt on every refresh and fly there if it changed.

### One-time setup

```bash
# 1. Add flyToView=1 via sed
sshpass -p 'lg' ssh lg@<LG-IP> \
  "sed -i 's|<href>##LG_PHPIFACE##kml/master.kml</href>|<href>##LG_PHPIFACE##kml/master.kml</href>\\n\\t\\t\\t\\t<flyToView>1</flyToView>|' ~/earth/kml/master/myplaces.kml"

# 2. Relaunch Earth once to load the updated myplaces.kml
sshpass -p 'lg' ssh lg@<LG-IP> '/home/lg/bin/lg-relaunch-direct'

# 3. Verify
sshpass -p 'lg' ssh lg@<LG-IP> "grep -A5 'master.kml' ~/earth/kml/master/myplaces.kml"
# Expected output:
# <href>##LG_PHPIFACE##kml/master.kml</href>
# <flyToView>1</flyToView>
# <refreshMode>onInterval</refreshMode><refreshInterval>3</refreshInterval></Link>
```

After this fix, any update to `/var/www/html/kml/master.kml` auto-flies the
camera to the new LookAt position within 3 seconds. No relaunch needed.

## Important Notes

- **One-time fix only.** Once applied and Earth is relaunched, it persists.
- When the KML file hasn't changed, HTTP caching (ETag/304) prevents
  re-processing — no unnecessary camera re-flying.
- This is separate from `flytoview=` via `/tmp/query.txt`. flyToView handles
  NetworkLink refresh; flytoview handles immediate on-demand camera moves.
- **Never edit `~/earth/kml/master/myplaces.kml` directly while Earth is running.**
  It's only read at startup. Always relaunch after modifications.
