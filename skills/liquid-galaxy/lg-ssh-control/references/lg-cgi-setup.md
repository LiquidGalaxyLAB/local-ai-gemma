# Apache CGI Setup for LG flytoview Camera Control

The La Palma Volcano app uses a CGI script at `http://lg1/cgi-bin/viewCenteredPlacemark.py`
to enable auto-camera positioning via `flytoview=` URL parameters.

This LG rig uses Apache on port 81 with `/var/www/html/` as DocumentRoot.

## Setup Steps

### 1. Enable CGI module

```bash
echo "lg" | sudo -S a2enmod cgi
echo "lg" | sudo -S service apache2 restart
```

### 2. Configure CGI in Apache

Add to `/etc/apache2/sites-enabled/000-default.conf` (for port 81 vhost):

```apache
<Directory /usr/lib/cgi-bin>
    AllowOverride None
    Options +ExecCGI
    AddHandler cgi-script .py
    Require all granted
</Directory>
ScriptAlias /cgi-bin/ /usr/lib/cgi-bin/
```

### 3. Deploy CGI script

Place at `/usr/lib/cgi-bin/viewCenteredPlacemark.py`:

```python
#!/usr/bin/env python3
import cgi, sys
form = cgi.FieldStorage()
kml = '<?xml version="1.0" encoding="UTF-8"?>\n<kml xmlns="http://www.opengis.net/kml/2.2"\n     xmlns:gx="http://www.google.com/kml/ext/2.2">\n  <Document/>\n</kml>'
print('Content-Type: application/vnd.google-earth.kml+xml')
print('Content-Length: %d' % len(kml))
print()
print(kml)
```

Owned by www-data, mode 755.

### 4. KML NetworkLink

In your KML, include a NetworkLink pointing to the CGI:

```xml
<NetworkLink>
  <name>Refresh</name>
  <visibility>0</visibility>
  <Link>
    <href>http://lg1:81/cgi-bin/viewCenteredPlacemark.py?</href>
    <refreshInterval>2</refreshInterval>
    <viewRefreshMode>onStop</viewRefreshMode>
    <viewRefreshTime>1</viewRefreshTime>
  </Link>
</NetworkLink>
```

The trailing `?` in the href allows Earth to append BBOX/view parameters.

## Verification

```bash
curl -s http://lg1:81/cgi-bin/viewCenteredPlacemark.py
```

Expected: valid KML with `<Document/>`.

## Notes

- The CGI only needs to return valid KML. The actual placemark content
  lives in the parent KML document, not in the CGI response.
- `viewRefreshMode=onStop` + `viewRefreshTime=1` means Earth queries the
  CGI 1s after the camera stops moving, then every 2s.
- Without the CGI, the NetworkLink returns 404. The KML still loads but
  without the dynamic refresh.
