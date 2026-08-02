#!/usr/bin/env python3
"""
3D sphere KML generator for Liquid Galaxy.

Generates a sphere from stacked extruded polygon rings.
COLLADA .dae models don't render on this LG's Google Earth —
stacked extruded polygons do, reliably.

Usage (local generation, then deploy):
  python3 /tmp/sphere-generator.py > /tmp/sphere.kml
  # then deploy to LG via SCP + deploy helper pattern

Editable constants at the bottom of the file.
"""

import math, sys

def generate_sphere_kml(lon, lat, radius_m, base_alt, layers, segments,
                         line_color="ff0000ff", fill_color="7f0000ff",
                         name="3D Sphere"):
    """Generate KML string for a 3D sphere made of stacked extruded polygons."""

    rings = []
    for i in range(layers + 1):
        t = i / layers
        angle = t * math.pi  # 0 (bottom) to PI (top)
        r = radius_m * math.sin(angle)
        h = base_alt + radius_m * (1.0 - math.cos(angle))
        rings.append((r, h))

    lines = []
    lines.append('<?xml version="1.0" encoding="UTF-8"?>')
    lines.append('<kml xmlns="http://www.opengis.net/kml/2.2"')
    lines.append('     xmlns:gx="http://www.google.com/kml/ext/2.2">')
    lines.append('  <Document>')
    lines.append(f'    <name>{name}</name>')
    lines.append('    <LookAt>')
    lines.append(f'      <longitude>{lon}</longitude>')
    lines.append(f'      <latitude>{lat}</latitude>')
    lines.append('      <altitude>0</altitude>')
    lines.append('      <heading>0</heading>')
    lines.append('      <tilt>60</tilt>')
    lines.append(f'      <range>{max(radius_m * 5, 500000)}</range>')
    lines.append('      <altitudeMode>relativeToGround</altitudeMode>')
    lines.append('    </LookAt>')
    lines.append('')
    lines.append('    <Style id="sphereStyle">')
    lines.append(f'      <LineStyle><color>{line_color}</color><width>2</width></LineStyle>')
    lines.append(f'      <PolyStyle><color>{fill_color}</color></PolyStyle>')
    lines.append('    </Style>')
    lines.append('')

    lat_scale = 111000.0
    lon_scale = 111000.0 * math.cos(math.radians(lat))

    for i in range(layers):
        r1, h1 = rings[i]
        r2, h2 = rings[i + 1]
        if r1 < 100 and i == 0:
            continue

        pts = []
        for j in range(segments + 1):
            a = (j / segments) * 2 * math.pi
            dx = r2 * math.cos(a) / lon_scale
            dy = r2 * math.sin(a) / lat_scale
            pts.append(f"{lon + dx},{lat + dy},{h2}")
        for j in range(segments, -1, -1):
            a = (j / segments) * 2 * math.pi
            dx = r1 * math.cos(a) / lon_scale
            dy = r1 * math.sin(a) / lat_scale
            pts.append(f"{lon + dx},{lat + dy},{h1}")

        lines.append('    <Placemark>')
        lines.append(f'      <name>{name} Layer {i + 1}</name>')
        lines.append('      <styleUrl>#sphereStyle</styleUrl>')
        lines.append('      <Polygon>')
        lines.append('        <extrude>1</extrude>')
        lines.append('        <altitudeMode>absolute</altitudeMode>')
        lines.append('        <outerBoundaryIs>')
        lines.append('          <LinearRing>')
        lines.append('            <coordinates>')
        lines.append('              ' + ' '.join(pts))
        lines.append('            </coordinates>')
        lines.append('          </LinearRing>')
        lines.append('        </outerBoundaryIs>')
        lines.append('      </Polygon>')
        lines.append('    </Placemark>')
        lines.append('')

    lines.append('  </Document>')
    lines.append('</kml>')
    return '\n'.join(lines)


# Editable constants — change before generating
LON = 138.0          # Japan
LAT = 36.0
RADIUS_M = 100000    # sphere radius in meters
BASE_ALT = 0         # bottom altitude (absolute)
LAYERS = 12          # more layers = smoother sphere
SEGMENTS = 36        # more segments = rounder circles
LINE_COLOR = "ff0000ff"    # ABGR: blue outline
FILL_COLOR = "7f0000ff"    # ABGR: semi-transparent blue fill
NAME = "3D Sphere"

if __name__ == "__main__":
    kml = generate_sphere_kml(LON, LAT, RADIUS_M, BASE_ALT, LAYERS, SEGMENTS,
                               LINE_COLOR, FILL_COLOR, NAME)
    sys.stdout.write(kml)
    sys.stdout.write('\n')
