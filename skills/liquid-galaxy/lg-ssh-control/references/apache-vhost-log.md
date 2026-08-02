# Apache Access Log — Correct Path on LG

**The LG Apache access log lives at:**
```
/var/log/apache2/other_vhosts_access.log
```

**NOT at `/var/log/apache2/access.log`** — that file does not exist or is empty on this rig.

## Why

Apache on Ubuntu 14.04/16.04 LG installs uses the vhost-combined log format with `CustomLog /var/log/apache2/other_vhosts_access.log vhost_combined` in `/etc/apache2/apache2.conf`. All virtual host requests (including `lg1:81/kml/*`) go to this file.

## How to check

```bash
# Read last 10 KML requests
sshpass -p 'lg' ssh lg@<LG-IP> \
  'echo "lg" | sudo -S grep "kml/" /var/log/apache2/other_vhosts_access.log | tail -10'

# Check if slave_2.kml is being polled
sshpass -p 'lg' ssh lg@<LG-IP> \
  'echo "lg" | sudo -S grep "slave_2.kml" /var/log/apache2/other_vhosts_access.log | tail -5'
```

## Sample output (healthy)

```
10.42.42.1:80 10.42.42.2 - - [01/Aug/2026:18:47:47 +0530] "GET /kml/slave_2.kml HTTP/1.1" 200 10210 "-" "GoogleEarth/7.3.3.7786(X11;Linux (4.15.0.0);en;kml:2.2;client:Pro;type:default)"
```

The IP `10.42.42.2` is lg2, `10.42.42.3` is lg3, `10.42.42.1` is lg1 (self-request). HTTP 304 = not modified (ETag match), HTTP 200 = fresh content served.

## Diagnosis checklist

- **No requests at all** → Earth not polling. Check `pgrep -c googleearth-bin`, verify runtime myplaces has resolved `##LG_PHPIFACE##` to `http://lg1:81/`, verify refreshInterval tags present.
- **HTTP 304 every time** → File hasn't changed. Run `sudo touch master.kml` or `sudo touch slave_2.kml` to force new ETag.
- **HTTP 200 but content invisible** → KML has CDATA (dropped on VM Earth), or uses rejected gx namespace, or has floating point precision issues.
