# myplaces.kml Permanent Refresh Workflow

## Key Insight

`myplaces.kml` on both master and slave machines is read **ONCE at Earth startup**. Editing it while Earth runs changes the file on disk but has **zero effect** until Earth is restarted.

## The Correct Workflow

```
1. Edit myplaces.kml → add refreshInterval to NetworkLink
2. Relaunch Earth ONCE (picks up new myplaces.kml)
3. From then on: any write to linked KML auto-appears within N seconds
```

## What to Edit

### Master (`~/earth/kml/master/myplaces.kml`)
Before:
```xml
<Link>
  <href>##LG_PHPIFACE##kml/master.kml</href>
</Link>
```

After (3s auto-refresh):
```xml
<Link>
  <href>##LG_PHPIFACE##kml/master.kml</href>
  <refreshMode>onInterval</refreshMode>
  <refreshInterval>3</refreshInterval>
</Link>
```

### Slave (`~/earth/kml/slave/myplaces.kml`)
The slave file uses `slave_x.kml` (PHP-resolved `x`), NOT numbered filenames like `slave_2.kml`.

Before:
```xml
<Link>
  <href>##LG_PHPIFACE##kml/slave_x.kml</href>
</Link>
```

After (2s auto-refresh):
```xml
<Link>
  <href>##LG_PHPIFACE##kml/slave_x.kml</href>
  <refreshMode>onInterval</refreshMode>
  <refreshInterval>2</refreshInterval>
</Link>
```

## sed Command (Corrected Approach — injects BEFORE `</Link>`, inside `<Link>`)

The refreshMode tags must be inside `<Link>`, before `</Link>`. Tags after `</href>` but before `</Link>` are fine — Earth reads them. Tags after `</Link>` are silently ignored.

```bash
# Master (3s)
sed -i '\|<href>[^<]*master.kml</href>|{n;s|</Link>|<refreshMode>onInterval</refreshMode><refreshInterval>3</refreshInterval></Link>|}' ~/earth/kml/master/myplaces.kml

# Slave (2s)
sed -i '\|<href>[^<]*slave_x.kml</href>|{n;s|</Link>|<refreshMode>onInterval</refreshMode><refreshInterval>2</refreshInterval></Link>|}' ~/earth/kml/slave/myplaces.kml
```

## Verification

After editing and relaunching:
```bash
grep -A4 'master.kml</href>' ~/earth/kml/master/myplaces.kml
# Expected: refreshMode + refreshInterval inside Link, before </Link>
```

## Helpers on This Rig

| Helper | Action | Deployed at |
|--------|--------|-------------|
| `lg-master-refresh-set` | Adds 3s refresh to master myplaces.kml | `/home/lg/bin/lg-master-refresh-set` |
| `lg-refresh-set` | Adds 2s refresh to all slave myplaces.kml | `/home/lg/bin/lg-refresh-set` |
| `lg-refresh-reset` | Removes refresh tags from slave myplaces.kml | `/home/lg/bin/lg-refresh-reset` |

After running any of these: **must relaunch Earth once** for the change to take effect.
