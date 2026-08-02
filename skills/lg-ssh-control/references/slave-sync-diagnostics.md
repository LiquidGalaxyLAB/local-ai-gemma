# Slave Sync Diagnostic Chain

From session 2026-08-02, where lg2/lg3 were not polling master.kml despite
Earth running with correct flags. This reference catalogs ALL root causes
discovered across multiple sessions, in diagnostic order.

## Diagnostic Chain (run in order on each slave)

1. **Is Earth running?** `pgrep googleearth-bin` — if not, launch with proper flags
2. **Has correct flags?** `cat /proc/PID/cmdline | tr '\000' ' '` — must contain `--no_system_check --no_signin`
3. **Which user owns the display?** `who | grep :0` — Earth must launch as display owner or with `XAUTHORITY=/home/<user>/.Xauthority`
4. **Is Master KML NetworkLink present?** `grep master.kml ~/.googleearth/myplaces.kml`
5. **Is `##LG_PHPIFACE##` resolved?** Look for `http://lg1:81` not `##LG_PHPIFACE##`
6. **Is URL correct?** Check for double-slash (`http://lg1:81//kml/`) or missing slash (`http://lg1:81kml/`)
7. **Does it have refreshInterval?** `grep refreshInterval ~/.googleearth/myplaces.kml`
8. **Is the right KML assigned?** Slave should load `slave_2.kml` (rightmost) or `slave_3.kml` (leftmost) per root formula
9. **Can slave reach Apache?** `curl -sI http://lg1:81/kml/master.kml` — must return 200
10. **Is /etc/hosts correct?** `grep lg1 /etc/hosts` — must resolve to the correct internal IP
11. **Apache logs:** `sudo tail -f /var/log/apache2/other_vhosts_access.log | grep master.kml` — watch for real-time polls from each slave IP

## Common Fix Patterns

### Fix runtime myplaces (Python — no sed escape issues)
```python
p = os.path.expanduser('~/.googleearth/myplaces.kml')
t = open(p).read()
t = t.replace('##LG_PHPIFACE##', 'http://lg1:81')
t = t.replace('http://lg1:81//kml/', 'http://lg1:81/kml/')
t = t.replace('http://lg1:81kml/', 'http://lg1:81/kml/')
if 'master.kml</href>' in t and 'refreshInterval' not in t:
    # Insert refreshInterval after href, before closing </Link>
    idx = t.find('master.kml</href>')
    end = t.find('</Link>', idx)
    t = t[:end] + '<refreshMode>onInterval</refreshMode>\n\t\t\t\t<refreshInterval>3</refreshInterval>\n\t\t\t\t' + t[end:]
open(p, 'w').write(t)
```

### Fix source myplaces (survives lightdm restart)
```python
sp = os.path.expanduser('~/earth/kml/slave/myplaces.kml')
# Apply same fix as above to sp
```

### Fix wrong slave KML
```python
t = t.replace('slave_3.kml', 'slave_2.kml')  # or vice versa
```

### Fix hosts
```bash
sudo sed -i 's/10.0.2.21  lg1/10.42.42.1  lg1/' /etc/hosts
# Or whichever IP matches the working slave
```

### Remove stale instance lock
```bash
rm -f ~/.googleearth/instance-running-lock
```

### Launch Earth as correct user
For multi-VM NAT rig where display is owned by e.g. `lg2`:
```bash
DISPLAY=:0 XAUTHORITY=/home/lg2/.Xauthority LIBGL_ALWAYS_SOFTWARE=1 \
  nohup /opt/google/earth/pro/googleearth --no_system_check --no_signin > /dev/null 2>&1 &
```
