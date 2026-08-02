#!/usr/bin/env python3
"""
Base collector template for LG data-to-KML pipeline.

Usage:
  1. Subclass or copy this file
  2. Set API_URL and BOUNDING_BOX
  3. Implement fetch() and transform_to_kml()
  4. Run directly or via cron

Dependencies: requests (standard library urllib also works if requests not available)

LG deployment pattern:
  - Writes KML to /tmp/master.kml
  - SCPs to lg1:/home/lg/master.kml
  - Runs sudo cp to /var/www/html/kml/master.kml
  - LG's 3s NetworkLink refresh picks it up
"""

import json
import os
import subprocess
import sys
import tempfile
import time
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape as xml_escape

# ─── Configurable ──────────────────────────────────────────────────────────

API_URL = ""                    # e.g., "https://earthquake.usgs.gov/..."
BOUNDING_BOX = [44, 56, 22, 42] # [lat_min, lat_max, lon_min, lon_max]
LG_IP = "192.168.1.200"         # LG master IP
LG_USER = "lg"
LG_PASS = "lg"
REFRESH_RANGE = 3000000         # KML LookAt range in meters (VM: >= 1,500,000)
REFRESH_TILT = 45               # LookAt tilt
CENTER_LON = 30.0               # Default LookAt center
CENTER_LAT = 50.0

# ─── Helpers ───────────────────────────────────────────────────────────────

def in_bbox(lat, lon):
    """Check if coordinate falls within bounding box."""
    return (BOUNDING_BOX[0] <= lat <= BOUNDING_BOX[1] and
            BOUNDING_BOX[2] <= lon <= BOUNDING_BOX[3])

def abgr_color(r, g, b, a=0xff):
    """Convert RGBA to ABGR hex string for Google Earth."""
    return f"{a:02x}{b:02x}{g:02x}{r:02x}"

# ─── KML Generation ────────────────────────────────────────────────────────

def build_kml(placemarks, title="Data Overlay"):
    """Build a complete KML document with LookAt and placemarks."""
    parts = []
    parts.append('<?xml version="1.0" encoding="UTF-8"?>')
    parts.append('<kml xmlns="http://www.opengis.net/kml/2.2">')
    parts.append('  <Document>')
    parts.append(f'    <name>{xml_escape(title)}</name>')
    parts.append('    <LookAt>')
    parts.append(f'      <longitude>{CENTER_LON}</longitude>')
    parts.append(f'      <latitude>{CENTER_LAT}</latitude>')
    parts.append(f'      <range>{REFRESH_RANGE}</range>')
    parts.append(f'      <tilt>{REFRESH_TILT}</tilt>')
    parts.append('      <heading>0</heading>')
    parts.append('      <altitudeMode>relativeToGround</altitudeMode>')
    parts.append('    </LookAt>')
    # Styles section
    parts.append(styles_xml())
    # Placemarks
    for pm in placemarks:
        parts.append(pm)
    parts.append('  </Document>')
    parts.append('</kml>')
    return '\n'.join(parts)

def styles_xml():
    """Return KML styles block. Override to add custom styles."""
    return '''    <Style id="defaultPin">
      <IconStyle>
        <color>ffff0000</color>
        <scale>1.0</scale>
      </IconStyle>
      <LabelStyle>
        <color>ffffffff</color>
        <scale>0.8</scale>
      </LabelStyle>
    </Style>'''

def placemark_xml(name, lon, lat, description="", style_url="#defaultPin"):
    """Generate a single Placemark XML block."""
    lines = [
        '    <Placemark>',
        f'      <name>{xml_escape(name)}</name>',
        f'      <styleUrl>{style_url}</styleUrl>',
        f'      <description>{xml_escape(description)}</description>',
        '      <Point>',
        f'        <coordinates>{lon},{lat},0</coordinates>',
        '      </Point>',
        '    </Placemark>'
    ]
    return '\n'.join(lines)

def polygon_xml(name, coords, style_url, extrude=False):
    """Generate a Polygon Placemark. coords = list of (lon, lat, alt) tuples."""
    coord_str = '\n'.join(f'          {lon},{lat},{alt}' for lon, lat, alt in coords)
    extrude_tag = '      <extrude>1</extrude>\n' if extrude else ''
    lines = [
        '    <Placemark>',
        f'      <name>{xml_escape(name)}</name>',
        f'      <styleUrl>{style_url}</styleUrl>',
        '      <Polygon>',
        extrude_tag,
        '        <altitudeMode>relativeToGround</altitudeMode>',
        '        <outerBoundaryIs>',
        '          <LinearRing>',
        '            <coordinates>',
        coord_str,
        '          </coordinates>',
        '          </LinearRing>',
        '        </outerBoundaryIs>',
        '      </Polygon>',
        '    </Placemark>'
    ]
    return '\n'.join(l for l in lines if l)

def linestring_xml(name, points, style_url):
    """Generate a LineString Placemark. points = list of (lon, lat, alt) tuples."""
    coord_str = '\n'.join(f'          {lon},{lat},{alt}' for lon, lat, alt in points)
    lines = [
        '    <Placemark>',
        f'      <name>{xml_escape(name)}</name>',
        f'      <styleUrl>{style_url}</styleUrl>',
        '      <LineString>',
        '        <tessellate>1</tessellate>',
        '        <altitudeMode>relativeToGround</altitudeMode>',
        '        <coordinates>',
        coord_str,
        '        </coordinates>',
        '      </LineString>',
        '    </Placemark>'
    ]
    return '\n'.join(lines)

# ─── Deploy ─────────────────────────────────────────────────────────────────

def deploy_kml(kml_string, remote_path="/var/www/html/kml/master.kml"):
    """Write KML to local temp, scp to lg1, sudo-cp to web root."""
    local = "/tmp/master.kml"
    with open(local, "w") as f:
        f.write(kml_string)

    # scp to lg1 home
    result = subprocess.run(
        ["sshpass", "-p", LG_PASS, "scp",
         "-o", "StrictHostKeyChecking=no",
         local, f"{LG_USER}@{LG_IP}:/home/lg/master.kml"],
        capture_output=True, text=True, timeout=15
    )
    if result.returncode != 0:
        print(f"SCP failed: {result.stderr}")
        return False

    # sudo cp to web root — use Python subprocess (NOT echo | sudo -S which
    # hangs over sshpass because sshpass consumes SSH's stdin, breaking the
    # pipe to sudo). The `[sudo] password for lg:` on stderr is cosmetic —
    # exit code 0 means success.
    remote_cmd = (
        'python3 -c "import subprocess; '
        "subprocess.run(['sudo', '-S', 'cp', "
        "'/home/lg/master.kml', '{}'], "
        "input=b'lg\\\\n', check=True)\""
    ).format(remote_path)
    result = subprocess.run(
        ["sshpass", "-p", LG_PASS, "ssh",
         "-o", "StrictHostKeyChecking=no",
         f"{LG_USER}@{LG_IP}", remote_cmd],
        capture_output=True, text=True, timeout=15
    )
    if result.returncode != 0:
        print(f"Deploy failed: {result.stderr.strip()}")
        return False

    print(f"Deployed to {remote_path}")
    return True

# ─── Fetch & Transform (Override These) ─────────────────────────────────────

def fetch():
    """Fetch raw data from API. Returns parsed JSON."""
    raise NotImplementedError("Subclass must implement fetch()")

def transform(data):
    """Transform API response into list of placemark XML strings."""
    raise NotImplementedError("Subclass must implement transform()")

# ─── Main ───────────────────────────────────────────────────────────────────

def main():
    print(f"Fetching from {API_URL}...")
    data = fetch()
    print(f"Got {len(data) if isinstance(data, list) else 'parsed'} items")

    placemarks = transform(data)
    print(f"Generated {len(placemarks)} placemarks")

    kml = build_kml(placemarks, title="Earthquake Monitor")
    if deploy_kml(kml):
        print("Done.")
    else:
        print("Deploy failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
