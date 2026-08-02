#!/usr/bin/env python3
"""
3D Pyramid KML generator for Liquid Galaxy.

Generates a pyramid over any bounding box using stacked extruded polygon rings.
Renders natively in Google Earth 7.3.3 on VirtualBox — no COLLADA, no gx namespace.

Usage:
  python3 pyramid-generator.py              # Uses defaults (India)
  python3 pyramid-generator.py --lon -95.5 --lat 36.5 --width 59 --depth 25 --layers 20 --apex-alt 500000 --name "USA Pyramid" > /tmp/usa.kml

Then deploy via the standard KML deployment pattern.
"""

import math, sys, argparse

def generate_pyramid(min_lon, min_lat, max_lon, max_lat, layers=20,
                     apex_alt=550000, apex_color="7f44aaff", line_color="ffffffff",
                     center_range=3000000, name="3D Pyramid"):
    """
    Generate a KML string with a stacked-ring pyramid covering the bounding box.

    Each ring is a rectangle at a decreasing size with altitude increasing,
    creating a terraced pyramid effect with `<extrude>1</extrude>`.
    """
    center_lon = (min_lon + max_lon) / 2
    center_lat = (min_lat + max_lat) / 2

    lat_scale = 111000.0
    lon_scale = 111000.0 * math.cos(math.radians(center_lat))
    base_w = (max_lon - min_lon) * lon_scale
    base_d = (max_lat - min_lat) * lat_scale

    style = (
        '    <Style id="pyramid">\n'
        '      <LineStyle><color>{}</color><width>1</width></LineStyle>\n'
        '      <PolyStyle><color>{}</color></PolyStyle>\n'
        '    </Style>'
    ).format(line_color, apex_color)

    rings = []
    for i in range(layers):
        t = i / layers
        alt = t * apex_alt
        shrink = 1.0 - t
        w = base_w * shrink / 2
        d = base_d * shrink / 2

        pts = []
        for dx, dy in [(-w, -d), (w, -d), (w, d), (-w, d), (-w, -d)]:
            lon = center_lon + dx / lon_scale
            lat = center_lat + dy / lat_scale
            pts.append("{:.6f},{:.6f},{:.0f}".format(lon, lat, alt))

        rings.append(
            '  <Placemark>\n'
            '    <name>Layer {}</name>\n'
            '    <styleUrl>#pyramid</styleUrl>\n'
            '    <Polygon>\n'
            '      <extrude>1</extrude>\n'
            '      <altitudeMode>relativeToGround</altitudeMode>\n'
            '      <outerBoundaryIs>\n'
            '        <LinearRing>\n'
            '          <coordinates>\n'
            '            {}\n'
            '          </coordinates>\n'
            '        </LinearRing>\n'
            '      </outerBoundaryIs>\n'
            '    </Polygon>\n'
            '  </Placemark>'
            .format(i + 1, ' '.join(pts))
        )

    kml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<kml xmlns="http://www.opengis.net/kml/2.2">\n'
        '  <Document>\n'
        '    <name>{}</name>\n'
        '    <LookAt>\n'
        '      <longitude>{}</longitude>\n'
        '      <latitude>{}</latitude>\n'
        '      <range>{}</range>\n'
        '      <tilt>50</tilt>\n'
        '      <heading>0</heading>\n'
        '      <altitudeMode>relativeToGround</altitudeMode>\n'
        '    </LookAt>\n'
        '{}\n'
        '{}\n'
        '  </Document>\n'
        '</kml>\n'
    ).format(name, center_lon, center_lat, center_range, style, '\n'.join(rings))

    return kml


# Predefined bounding boxes
REGIONS = {
    'india':      {'min_lon': 67.5, 'min_lat': 6.0,  'max_lon': 97.5, 'max_lat': 37.5, 'apex_alt': 550000, 'name': 'India Pyramid', 'center_range': 3000000},
    'usa':        {'min_lon': -125.0, 'min_lat': 24.0, 'max_lon': -66.0, 'max_lat': 49.0, 'apex_alt': 500000, 'name': 'USA Pyramid', 'center_range': 3000000},
    'middle-east':{'min_lon': 35.0, 'min_lat': 12.0, 'max_lon': 60.0, 'max_lat': 40.0, 'apex_alt': 400000, 'name': 'Middle East Pyramid', 'center_range': 2500000},
    'europe':     {'min_lon': -10.0, 'min_lat': 35.0, 'max_lon': 40.0, 'max_lat': 70.0, 'apex_alt': 500000, 'name': 'Europe Pyramid', 'center_range': 3000000},
}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate a 3D pyramid KML for any region')
    parser.add_argument('--region', choices=list(REGIONS.keys()),
                        help='Use predefined region bounding box')
    parser.add_argument('--lon', type=float, help='Center longitude (ignored with --region)')
    parser.add_argument('--lat', type=float, help='Center latitude (ignored with --region)')
    parser.add_argument('--width', type=float, help='East-west span in degrees (ignored with --region)')
    parser.add_argument('--depth', type=float, help='North-south span in degrees (ignored with --region)')
    parser.add_argument('--layers', type=int, default=20, help='Number of stacked rings (default: 20)')
    parser.add_argument('--apex-alt', type=int, default=550000,
                        help='Apex altitude in meters (default: 550000)')
    parser.add_argument('--range', type=int, default=3000000,
                        help='Camera LookAt range in meters (default: 3000000)')
    parser.add_argument('--name', default='3D Pyramid', help='KML Document name')
    parser.add_argument('--list-regions', action='store_true', help='List predefined regions and exit')

    args = parser.parse_args()

    if args.list_regions:
        print('Predefined regions:')
        for name, box in REGIONS.items():
            center_lon = (box['min_lon'] + box['max_lon']) / 2
            center_lat = (box['min_lat'] + box['max_lat']) / 2
            print('  {:<15s} center ({:.1f}, {:.1f})  apex {}m, range {}m'.format(
                name, center_lat, center_lon, box['apex_alt'], box['center_range']))
        sys.exit(0)

    if args.region:
        if args.region not in REGIONS:
            print('Unknown region: {}. Use --list-regions to see available regions.'.format(args.region))
            sys.exit(1)
        r = REGIONS[args.region]
        min_lon, min_lat = r['min_lon'], r['min_lat']
        max_lon, max_lat = r['max_lon'], r['max_lat']
        apex_alt = r['apex_alt']
        name = r['name']
        center_range = r['center_range']
    else:
        if not (args.lon is not None and args.lat is not None and
                args.width and args.depth):
            print('Error: Provide --region OR --lon/--lat/--width/--depth')
            print('Use --list-regions to see predefined regions.')
            sys.exit(1)
        min_lon = args.lon - args.width / 2
        max_lon = args.lon + args.width / 2
        min_lat = args.lat - args.depth / 2
        max_lat = args.lat + args.depth / 2
        apex_alt = args.apex_alt
        name = args.name
        center_range = args.range

    kml = generate_pyramid(
        min_lon, min_lat, max_lon, max_lat,
        layers=args.layers,
        apex_alt=apex_alt,
        name=name,
        center_range=center_range
    )

    sys.stdout.write(kml)
    sys.stdout.write('\n')
    sys.stderr.write('Generated {}m pyramid "{}" with {} layers ({:.0f}km apex)\n'.format(
        center_range, name, args.layers, apex_alt / 1000))
