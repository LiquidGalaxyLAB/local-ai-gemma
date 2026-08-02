# Multi-VM NAT Rig — Slave Sync Fix

## Problem

On multi-VM NAT rigs (10.0.2.x network), slaves fail to poll master.kml
from lg1. Three layered causes:

1. **Wrong host resolution** — Each VM has both 10.0.2.x (NAT DHCP) and
   10.42.42.x (static internal) IPs. `/etc/hosts` may point `lg1` at the
   wrong address. Slaves resolve `lg1` differently depending on hosts file.

2. **Missing refreshInterval** — The Master KML NetworkLink in slave
   myplaces has no `<refreshInterval>`. Slaves load master.kml once at
   startup and never re-poll.

3. **`##LG_PHPIFACE##` unresolved** — The source myplaces (`~/earth/kml/
   slave/myplaces.kml`) has a literal PHP placeholder. The LG launch system
   resolves it; manual deployments/restarts don't.

## Diagnosis

```bash
# On each slave (via lg1 as gateway)
sshpass -p lg ssh -o StrictHostKeyChecking=no lg@192.168.1.12 \
  "sshpass -p lg ssh lg@10.0.2.22 'getent hosts lg1'"

# Check Apache logs on lg1
python3 -c "
import subprocess
p = subprocess.Popen(['sudo','-S','tail','-30',
  '/var/log/apache2/other_vhosts_access.log'],
  stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
out, err = p.communicate(b'lg\\n')
ips = set()
for l in out.decode().split(chr(10)):
    if 'master.kml' in l:
        print(l.strip())
"
# Only one IP polling = slaves not syncing
```

## Fix Script Pattern (fix-lg2.py)

Use Python `str.replace` — NEVER nested sed through double SSH (mangles XML):

```python
#!/usr/bin/env python3
"""Fix slave myplaces with correct master IP + refreshInterval"""
import os

path = os.path.expanduser('~/.googleearth/myplaces.kml')
t = open(path).read()

# Fix URL
for old, new in [
    ('http://lg1:81//kml/master.kml', 'http://10.0.2.21:81/kml/master.kml'),
    ('http://lg1:81/kml/master.kml',  'http://10.0.2.21:81/kml/master.kml'),
    ('##LG_PHPIFACE##',               'http://10.0.2.21:81'),
]:
    t = t.replace(old, new)

# Insert refreshInterval after master.kml href if missing
idx = t.find('master.kml</href>')
if idx >= 0:
    end = t.find('</Link>', idx)
    if end >= 0 and 'refreshInterval' not in t[idx:end]:
        t = t[:end] + '<refreshMode>onInterval</refreshMode>\n'
        t = t + '\t\t\t\t<refreshInterval>3</refreshInterval>\n\t\t\t\t' + t[end:]

open(path, 'w').write(t)
```

## Deploy + Execute

```bash
# SCP fix script to the slave
sshpass -p lg scp -o StrictHostKeyChecking=no /tmp/fix-lg2.py \
  lg2@10.0.2.22:/home/lg2/fix-lg2.py

# Run as display owner
sshpass -p lg ssh -o StrictHostKeyChecking=no lg2@10.0.2.22 \
  'python3 /home/lg2/fix-lg2.py'

# Restart Earth as display owner
sshpass -p lg ssh -o StrictHostKeyChecking=no lg2@10.0.2.22 \
  'pkill -u lg2 -f googleearth; sleep 2; \
   DISPLAY=:0 XAUTHORITY=/home/lg2/.Xauthority LIBGL_ALWAYS_SOFTWARE=1 \
   nohup /opt/google/earth/pro/googleearth --no_system_check --no_signin \
   > /dev/null 2>&1 &'
```

## Also Fix the Source

Lightdm restart copies source to runtime — fix both:

```python
sp = os.path.expanduser('~/earth/kml/slave/myplaces.kml')
if os.path.exists(sp):
    st = open(sp).read()
    st = st.replace('##LG_PHPIFACE##', 'http://10.0.2.21:81')
    # ... same URL + refreshInterval fixes
    open(sp, 'w').write(st)
```

## Verification

- Apache log shows slave IPs polling master.kml every 3s
- `grep master.kml ~/.googleearth/myplaces.kml` shows correct URL + refreshInterval
- Earth launched with `--no_system_check --no_signin` (check `/proc/<pid>/cmdline`)
- Display owner matches the X session owner (`who | grep :0`)

## Frame Network Reference (This Rig)

| Frame | NAT IP | Display Owner | Hosts lg1= |
|-------|--------|---------------|------------|
| lg1   | 10.0.2.21 | lg1 | self |
| lg2   | 10.0.2.22 | lg2 | 10.42.42.1 |
| lg3   | 10.0.2.23 | lg3 | 10.42.42.1 |
