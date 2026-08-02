#!/usr/bin/env python3
"""
Geography Educator — generates educational KML for LG.
Teaches: equator, tropics, prime meridian, continents, mountain ranges, rivers, volcanoes, capitals.
No CDATA, no gx namespace, Google CDN icons.

Usage:
  python3 geography-educator.py
  scp /tmp/geography.kml lg@<LG-IP>:/home/lg/
  ssh lg@<LG-IP> 'sudo cp /home/lg/geography.kml /var/www/html/kml/master.kml'
  # flytoview to 0,20, 20000000m range
"""

def make_line(name, style, coords):
    pts = ' '.join('{1},{0},0'.format(*c) for c in coords)
    return '  <Placemark><name>{0}</name><styleUrl>#{1}</styleUrl><LineString><coordinates>{2}</coordinates></LineString></Placemark>'.format(name, style, pts)

def make_poly(name, verts):
    pts = ' '.join('{1},{0},0'.format(*c) for c in verts)
    return '  <Placemark><name>{0}</name><styleUrl>#mtn</styleUrl><Polygon><extrude>1</extrude><altitudeMode>relativeToGround</altitudeMode><outerBoundaryIs><LinearRing><coordinates>{1}</coordinates></LinearRing></outerBoundaryIs></Polygon></Placemark>'.format(name, pts)

kml = '''<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <name>Geography Educator</name>
    <LookAt><longitude>0</longitude><latitude>20</latitude><range>20000000</range><tilt>0</tilt><heading>0</heading><altitudeMode>relativeToGround</altitudeMode></LookAt>
    <open>1</open>
    <Style id="equator"><LineStyle><color>ff00ffff</color><width>3</width></LineStyle></Style>
    <Style id="tropic"><LineStyle><color>ffffcc00</color><width>2</width></LineStyle></Style>
    <Style id="meridian"><LineStyle><color>ffff6622</color><width>2</width></LineStyle></Style>
    <Style id="mtn"><LineStyle><color>ffffffff</color><width>1</width></LineStyle><PolyStyle><color>7f44aaff</color></PolyStyle></Style>
    <Style id="river"><LineStyle><color>aa4444ff</color><width>3</width></LineStyle></Style>
    <Style id="cap"><IconStyle><scale>0.8</scale><color>ffff4444</color><Icon><href>http://maps.google.com/mapfiles/kml/paddle/red-circle.png</href></Icon></IconStyle><LabelStyle><color>ffffffff</color><scale>1.4</scale></LabelStyle></Style>
    <Style id="continent"><IconStyle><scale>0.0</scale></IconStyle><LabelStyle><color>ffffcc00</color><scale>2.0</scale></LabelStyle></Style>
    <Style id="volcano"><IconStyle><scale>0.7</scale><color>ffff6600</color><Icon><href>http://maps.google.com/mapfiles/kml/shapes/volcano.png</href></Icon></IconStyle><LabelStyle><color>ffffffff</color><scale>1.2</scale></LabelStyle></Style>

    <Folder><name>Grid and Reference Lines</name>
''' + make_line("Equator 0 deg Latitude", "equator", [(0,-180),(0,180)]) + '''
''' + make_line("Tropic of Cancer 23.5N", "tropic", [(23.5,-180),(23.5,180)]) + '''
''' + make_line("Tropic of Capricorn 23.5S", "tropic", [(-23.5,-180),(-23.5,180)]) + '''
''' + make_line("Prime Meridian 0 deg Longitude", "meridian", [(-90,0),(90,0)]) + '''
    </Folder>
    <Folder><name>Continents</name>
      <Placemark><name>Africa</name><styleUrl>#continent</styleUrl><Point><coordinates>20,0,0</coordinates></Point></Placemark>
      <Placemark><name>Europe</name><styleUrl>#continent</styleUrl><Point><coordinates>10,50,0</coordinates></Point></Placemark>
      <Placemark><name>Asia</name><styleUrl>#continent</styleUrl><Point><coordinates>90,40,0</coordinates></Point></Placemark>
      <Placemark><name>North America</name><styleUrl>#continent</styleUrl><Point><coordinates>-100,45,0</coordinates></Point></Placemark>
      <Placemark><name>South America</name><styleUrl>#continent</styleUrl><Point><coordinates>-60,-15,0</coordinates></Point></Placemark>
      <Placemark><name>Australia</name><styleUrl>#continent</styleUrl><Point><coordinates>135,-25,0</coordinates></Point></Placemark>
      <Placemark><name>Antarctica</name><styleUrl>#continent</styleUrl><Point><coordinates>60,-82,0</coordinates></Point></Placemark>
    </Folder>
    <Folder><name>Mountain Ranges</name>
''' + make_poly("Himalayas", [(27,72),(28,72),(29,80),(29,88),(28,92),(27,92),(26,88),(26,80)]) + '''
''' + make_poly("Andes", [(-55,-72),(-50,-73),(-30,-71),(-10,-75),(5,-78),(10,-73),(10,-70),(5,-77),(-10,-73),(-30,-69),(-50,-71),(-55,-70)]) + '''
''' + make_poly("Rockies", [(60,-140),(65,-145),(60,-120),(50,-115),(40,-110),(35,-106),(30,-104),(30,-110),(35,-112),(40,-115),(50,-120),(60,-130)]) + '''
''' + make_poly("Alps", [(43,3),(44,4),(45,6),(46,8),(47,10),(48,12),(47,14),(46,14),(45,12),(44,10),(43,7),(43,5)]) + '''
    </Folder>
    <Folder><name>Major Rivers</name>
''' + make_line("Nile", "river", [(32,30),(32,28),(33,26),(33,24),(32,22),(32,20),(31,18),(31,16),(32,14),(32,12),(33,10)]) + '''
''' + make_line("Amazon", "river", [(-1,-50),(-2,-52),(-2,-54),(-3,-56),(-3,-58),(-4,-60),(-4,-62),(-3,-64),(-3,-66),(-4,-68),(-4,-70),(-5,-72)]) + '''
''' + make_line("Mississippi", "river", [(29,-89),(30,-90),(31,-91),(32,-92),(33,-91),(34,-90),(35,-89),(36,-89),(37,-89),(38,-90),(39,-91),(40,-93),(41,-94),(42,-94),(43,-94),(44,-94),(45,-94),(46,-94),(47,-94),(48,-94)]) + '''
''' + make_line("Ganges", "river", [(25,88),(25,87),(26,86),(26,85),(25,84),(25,83),(25,82),(24,81),(24,80),(23,79)]) + '''
    </Folder>
    <Folder><name>Volcanoes</name>
''' + '\n'.join('      <Placemark><name>Volcano {0}</name><styleUrl>#volcano</styleUrl><Point><coordinates>{2},{1},0</coordinates></Point></Placemark>'.format(n,lat,lon) for n,lat,lon in [
    ("Mount Fuji",35.36,138.73),("Krakatoa",-6.10,105.40),("Kilimanjaro",-3.07,37.35),
    ("Mount Etna",37.75,14.99),("St. Helens",46.20,-122.18),("Mauna Loa",19.48,-155.61),
    ("Vesuvius",40.82,14.43),("Eyjafjallajokull",63.63,-19.62)]) + '''
    </Folder>
    <Folder><name>World Capitals</name>
''' + '\n'.join('      <Placemark><name>Capital {0}</name><styleUrl>#cap</styleUrl><Point><coordinates>{2},{1},0</coordinates></Point></Placemark>'.format(n,lat,lon) for n,lat,lon in [
    ("Washington DC",38.9,-77.0),("London",51.5,-0.1),("Paris",48.9,2.3),
    ("Beijing",39.9,116.4),("New Delhi",28.6,77.2),("Moscow",55.8,37.6),
    ("Tokyo",35.7,139.7),("Cairo",30.0,31.2),("Canberra",-35.3,149.1)]) + '''
    </Folder>
  </Document>
</kml>'''

with open('/tmp/geography.kml', 'w') as f:
    f.write(kml)
print('Geography KML: ' + str(len(kml)) + ' bytes')
