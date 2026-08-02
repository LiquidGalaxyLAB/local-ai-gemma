# Slave Stale KML Diagnosis

## Problem

KML deployed to `master.kml` appears on the master screen (lg1) within ~3s due to the
master's `<refreshInterval>3</refreshInterval>` on its Master KML NetworkLink. But slave
screens (lg2, lg3) show old/stale content — they loaded `master.kml` once at Earth
startup and never re-read it.

## Root Cause

Each slave's `~/earth/kml/slave/myplaces.kml` has a **Master KML NetworkLink** that
lacks `<refreshMode>` and `<refreshInterval>`:

```xml
<NetworkLink>
    <name>Master KML</name>
    <Link>
        <href>##LG_PHPIFACE##/kml/master.kml</href>
        <!-- NO flyToView, NO refreshMode, NO refreshInterval -->
    </Link>
</NetworkLink>
```

The master's `~/earth/kml/master/myplaces.kml` already has these — applied by
`lg-master-refresh-set`. But that helper only patches the **master's** myplaces.kml,
not each slave's.

## Diagnosis Steps

1. Read master.kml to confirm it's clean:
   ```bash
   sshpass -p 'lg' ssh lg@<LG-IP> "cat /var/www/html/kml/master.kml"
   ```

2. Check slave myplaces.kml for missing refresh:
   ```bash
   sshpass -p 'lg' ssh lg@<LG-IP> "for lg in lg2 lg3; do echo '=== \$lg ==='; sshpass -p 'lg' ssh lg@\$lg 'grep -A2 \"master.kml\" ~/earth/kml/slave/myplaces.kml'; done"
   ```
   If output shows `</Link>` directly after `</href>` (no `flyToView` or `refreshMode`),
   the slaves lack refresh.

3. Check if `lg-slave-master-refresh-set` helper exists:
   ```bash
   sshpass -p 'lg' ssh lg@<LG-IP> "ls /home/lg/bin/lg-slave-master-refresh-set 2>/dev/null || echo 'not deployed'"
   ```

## Fix

### Preferred: Run the deployed helper

If `lg-slave-master-refresh-set` exists on lg1:
```bash
sshpass -p 'lg' ssh lg@<LG-IP> "/home/lg/bin/lg-slave-master-refresh-set"
```

Then relaunch once (myplaces.kml is read only at Earth startup):
```bash
sshpass -p 'lg' ssh lg@<LG-IP> "/home/lg/bin/lg-relaunch-direct"
```

### Manual (one slave at a time)

```bash
# On each slave via master (frame-count-agnostic):
. ${HOME}/etc/shell.conf
me=$(hostname)
PW="lg"
for lg in $LG_FRAMES; do
  [ "$lg" = "$me" ] && continue
  sshpass -p "$PW" ssh -o ConnectTimeout=5 -t lg@$lg \
    "echo '$PW' | sudo -S sed -i '/master.kml<\/href>/{n;s/<\/Link>/<flyToView>1<\/flyToView><refreshMode>onInterval<\/refreshMode><refreshInterval>3<\/refreshInterval><\/Link>/}' ~/earth/kml/slave/myplaces.kml"
  echo "  $lg: master KML refresh set"
done
```

### Deploy the helper (one-time, if missing)

Write the helper to lg1:
```bash
sshpass -p 'lg' ssh lg@<LG-IP> "cat > /home/lg/bin/lg-slave-master-refresh-set << 'HELPER'
#!/bin/bash
PW=\"lg\"
. \${HOME}/etc/shell.conf
me=\$(hostname)
for lg in \$LG_FRAMES; do
  [ \"\$lg\" = \"\$me\" ] && continue
  sshpass -p \"\$PW\" ssh -o ConnectTimeout=5 -t lg@\$lg \"echo '\$PW' | sudo -S sed -i '/master.kml<.href>/{n;s|<.Link>|<flyToView>1</flyToView><refreshMode>onInterval</refreshMode><refreshInterval>3</refreshInterval></Link>|}' ~/earth/kml/slave/myplaces.kml\" 2>/dev/null
  echo \"  \$lg: master KML refresh set\"
done
HELPER
chmod +x /home/lg/bin/lg-slave-master-refresh-set"
```

## Verification

```bash
sshpass -p 'lg' ssh lg@<LG-IP> "for lg in lg2 lg3; do echo '=== \$lg ==='; sshpass -p 'lg' ssh lg@\$lg 'grep -A2 \"master.kml\" ~/earth/kml/slave/myplaces.kml'; done"
```

Expected output per slave:
```
<href>##LG_PHPIFACE##/kml/master.kml</href>
<flyToView>1</flyToView><refreshMode>onInterval</refreshMode><refreshInterval>3</refreshInterval></Link>
```

## After Fix

Future `master.kml` changes propagate to **all screens** within ~3 seconds with no
relaunch needed. The master screen updates via its own refresh (already configured);
slaves now also re-poll every 3 seconds.
