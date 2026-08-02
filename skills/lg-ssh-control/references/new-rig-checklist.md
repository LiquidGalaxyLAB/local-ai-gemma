# New Rig First-Time Checklist

When deploying the WM-LG pipeline to a NEW Liquid Galaxy rig (restoring
the backup on a different system), follow this checklist in order.

## 1. Collect Credentials

Ask the user for all 5 at once:
- IP address of master computer
- SSH port (22 default, 2222 for tunnel)
- SSH username (usually `lg`, but can be `lg1` if Ubuntu installer set hostname-as-username)
- SSH password (standard is `lg`)
- Number of screens

Save to memory.

## 2. Detect Earth User (CRITICAL)

Earth may NOT run as the user you SSH in as. Earth's actual user determines
which `myplaces.kml` it reads.

```bash
# After SSHing to master, check which user owns Earth's process:
sshpass -p 'lg' ssh lg@<IP> "ps aux | grep googleearth-bin | head -1 | awk '{print \$1}'"
# Returns: lg1 (or lg, or lg2, etc.)
```

Earth owns myplaces at: `/home/<earth_user>/earth/kml/master/myplaces.kml`

**Common pitfall:** You SSH as `lg` and edit `/home/lg/earth/.../myplaces.kml`,
but Earth runs as `lg1` and reads from `/home/lg1/earth/.../myplaces.kml`.
The wrong file gets patched and KML never appears.

If Earth user differs from SSH user, all sed/Python edits must target
`/home/<earth_user>/earth/kml/...` using `sudo` since the SSH user can't
write to another user's home directory.

## 3. Verify myplaces.kml Path

```bash
# Find ALL myplaces.kml files on the system:
find /home -name "myplaces.kml" -path "*/master/*" 2>/dev/null
# Expected: /home/lg/earth/kml/master/myplaces.kml (if lg user)
#           /home/lg1/earth/kml/master/myplaces.kml (if lg1 user)
```

Confirm which one Earth actually reads by checking the Earth user's home.

## 4. Check Apache Port

```bash
grep Listen /etc/apache2/ports.conf
# LG standard: Apache on port 81 only (not 80)
# ##LG_PHPIFACE## resolves to http://lg1:81/
```

If port differs from 81, update `##LG_PHPIFACE##` accordingly.

## 5. Verify KML Serving

```bash
curl -s -o /dev/null -w '%{http_code}' http://lg1:81/kml/master.kml
# Expected: 200
```

If 404, check DocumentRoot and that `/var/www/html/kml/` exists.

## 6. Check query.txt Daemon

```bash
cat /tmp/query.txt 2>/dev/null
# If file doesn't exist: daemon may not be running (OK, just means flytoview won't work via query.txt)
# If file exists with old content: daemon is NOT consuming it — flytoview won't work
# If file is consumed (returns "No such file"): daemon IS running — flytoview works
```

This rig may launch Earth through a custom script (e.g. `launch-lg-earth.sh`)
instead of the full LG system stack. Custom launch scripts typically lack
the query.txt monitoring daemon.

## 7. Check Apache Access for KML Fetches

```bash
python3 -c "
import subprocess
r = subprocess.Popen(['sudo','-S','tail','-80','/var/log/apache2/access.log'],
    stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
out, _ = r.communicate(b'lg\n')
lines = out.decode(errors='replace').strip().split(chr(10))
kml_lines = [l for l in lines if 'kml' in l.lower()]
print('KML requests:', len(kml_lines))
"
```

Zero KML requests means Earth's NetworkLink is not fetching from Apache
(possible causes: wrong myplaces.kml path, Earth hasn't been restarted
after myplaces edits, NetworkLink improperly configured).

## 8. Check Slave Reachability

Most VM rigs have slaves on an internal 10.x network. Check from master:

```bash
ping -c 1 lg2    # Should work, internal network
ping -c 1 lg3    # Should work, internal network
```

Check IPs in `/etc/hosts` on master.

If reachable, apply slave master refresh and restart on all frames.
If NOT reachable (single-VM rig or NAT-only network), only master screen
gets the KML data.

## 9. Gateway SSH to Slaves

When Pi cannot reach slaves (10.42.42.x internal), tunnel through master:

```bash
# Check status
sshpass -p 'lg' ssh lg@<LG-IP> 'sshpass -p lg ssh lg@10.42.42.2 "pgrep googleearth-bin"'

# Edit myplaces (with sudo for correct user)
sshpass -p 'lg' ssh lg@<LG-IP> \
  'sshpass -p lg ssh lg@10.42.42.2 '\''python3 -c "..."'\'
```

## 10. Apply Slave Master Refresh (All Frames)

Each frame's myplaces.kml needs refreshInterval on its Master KML NetworkLink.
Reachable or not, every frame that runs Earth needs this:

```
<refreshMode>onInterval</refreshMode>
<refreshInterval>3</refreshInterval>
```

## 11. One-Time Restart

After editing myplaces.kml on any frame, restart Earth once. After that,
all future KML updates appear within 3s — no restart needed ever again.

```bash
python3 -c "import subprocess,os; svc='lxdm' if os.path.exists('/etc/init/lxdm.conf') else 'lightdm'; subprocess.run(['sudo','-S','service',svc,'restart'], input=b'lg\n', check=True)"
```

## 12. Verify KML Display

Deploy a simple test KML to master.kml, wait 6s (2 refresh cycles), check.

```bash
# Deploy test
sshpass -p 'lg' ssh lg@<IP> 'python3 -c "import subprocess; subprocess.run([\"sudo\",\"-S\",\"cp\",\"/tmp/test.kml\",\"/var/www/html/kml/master.kml\"], input=b\"lg\n\", check=True)"'

# Verify served
curl -s http://lg1:81/kml/master.kml | head -3
# Expected: <?xml version="1.0" encoding="UTF-8"?>
```

## Common Pitfalls Encountered

| Symptom | Root Cause |
|---------|-----------|
| KML file served at port 81 but invisible on ALL screens | Earth user mismatch — patched wrong myplaces.kml (Step 2) |
| KML visible on master but NOT on slaves | Slaves lack refreshInterval on master NetworkLink (Step 10) |
| Apache returns 200 but access log has zero Earth requests | myplaces.kml has wrong NetworkLink href or Earth hasn't been restarted (Step 11) |
| query.txt content persists, not consumed | No query.txt daemon on this rig (Step 6) — use KML LookAt + flyToView=1 as fallback |
| `echo 'lg' \| sudo -S` hangs inside SSH | sshpass consumes stdin; use Python subprocess with `input=` instead |
