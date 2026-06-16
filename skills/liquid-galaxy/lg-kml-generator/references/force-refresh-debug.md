# Force Refresh Debugging — myplaces.kml Structure

## The Bug

The old sed-based force refresh appended `<refreshMode>` after `</href>`:

```
sed -i 's|<href>[^<]*master.kml</href>|&<refreshMode>onInterval</refreshMode>|
```

This produces:
```xml
<Link>
  <href>##LG_PHPIFACE##kml/master.kml</href><refreshMode>onInterval</refreshMode>
</Link>
```

While the tags technically sit between `<Link>` and `</Link>`, Google Earth on this rig does NOT process them when appended inline after `</href>`. The refresh never fires, and the only way to see new KML is relaunch.

## The Fix

Inject refreshMode as a separate line INSIDE `<Link>`, before `</Link>`:

```bash
sed -i '\|<href>[^<]*master.kml</href>|{n;s|</Link>|<refreshMode>onInterval</refreshMode><refreshInterval>5</refreshInterval></Link>|}' ~/earth/kml/master/myplaces.kml
```

This produces:
```xml
<Link>
  <href>##LG_PHPIFACE##kml/master.kml</href>
  <refreshMode>onInterval</refreshMode>
  <refreshInterval>5</refreshInterval>
</Link>
```

This is processed correctly by Earth, and KML changes auto-appear within the interval.

## Slave myplaces.kml Format (from this rig)

Each slave (lg2..lgN) loads `~/earth/kml/slave/myplaces.kml`. All slaves share the same template — it uses `slave_x.kml` where `x` is a PHP variable that resolves per-machine:

```xml
<NetworkLink>
  <name>Solo KML</name>
  <Link>
    <href>##LG_PHPIFACE##kml/slave_x.kml</href>
  </Link>
</NetworkLink>
```

Key differences from master myplaces.kml:
- Solo KML uses `slave_x.kml` (not `slave_2.kml` / `slave_3.kml`) — the `x` is PHP-substituted
- Solo KML Update uses `sync_nlc_x.php` (reads `kmls_x.txt` per-slave)
- The master href has a slash after `##LG_PHPIFACE##` (`/kml/master.kml`); the slave does NOT (`kml/slave_x.kml`) — both are correct for this rig's PHP routing

**Implication for refresh helpers:** per-slave refresh helpers iterating `slave_$i.kml` will NOT match. Must target `slave_x.kml` to work on this rig.

## Permanent Fix (Recommended)

Run the one-time fix on the rig so ALL future KML writes auto-appear. See lg-kml-generator skill's "Force Refresh Mechanism" section.

## Actual myplaces.kml Format (from this rig)

Earth master screen loads `~/earth/kml/master/myplaces.kml` at startup. The critical NetworkLink for master.kml:

```xml
<NetworkLink>
  <name>Master KML</name>
  <Link>
    <href>##LG_PHPIFACE##kml/master.kml</href>
  </Link>
</NetworkLink>
```

Note: The href uses `##LG_PHPIFACE##` prefix (not a file:// or http:// path directly). This is a Liquid Galaxy PHP interface placeholder that gets resolved at the server level.

The KML Update NetworkLink (sync_nlc.php) already has the CORRECT pattern with refreshMode properly inside `<Link>`:

```xml
<NetworkLink>
  <name>KML Update</name>
  <Link>
    <href>##LG_PHPIFACE##/sync_nlc.php</href>
    <refreshMode>onInterval</refreshMode>
    <refreshInterval>1</refreshInterval>
  </Link>
</NetworkLink>
```

## Also Affected

- `lg-refresh-set` and `lg-refresh-reset` helpers (v2.3.x and earlier) used the same broken `s="${href}"` / `r="${href}<refreshMode>..</refreshMode>"` pattern. Fixed in lg-ssh-control v2.4.0 — deploy the updated helpers to apply the fix on the rig.
