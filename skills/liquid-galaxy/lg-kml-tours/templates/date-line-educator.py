#!/usr/bin/env python3
"""
International Date Line visual educator for Liquid Galaxy.
Generates KML with 180 meridian, actual date line (zigzag), day labels, explanations, and cities.

Deploy:
  python3 date-line-educator.py
  scp /tmp/dateline.kml lg@<LG-IP>:/home/lg/dateline.kml
  sshpass -p 'lg' ssh lg@<LG-IP> 'sudo cp /home/lg/dateline.kml /var/www/html/kml/master.kml'
  # flytoview to 180E, 20N, 15000000m range
"""

STYLES = """
    <Style id="line180"><LineStyle><color>ff00ffff</color><width>3</width></LineStyle></Style>
    <Style id="dateline"><LineStyle><color>ffff4444</color><width>4</width></LineStyle></Style>
    <Style id="east"><IconStyle><scale>0.0</scale></IconStyle><LabelStyle><color>ff44ff44</color><scale>2.2</scale></LabelStyle></Style>
    <Style id="west"><IconStyle><scale>0.0</scale></IconStyle><LabelStyle><color>ffff4444</color><scale>2.2</scale></LabelStyle></Style>
    <Style id="explain"><IconStyle><scale>0.0</scale></IconStyle><LabelStyle><color>ffffcc00</color><scale>1.6</scale></LabelStyle></Style>
    <Style id="explain_sm"><IconStyle><scale>0.0</scale></IconStyle><LabelStyle><color>ffffffff</color><scale>1.2</scale></LabelStyle></Style>
    <Style id="cap"><IconStyle><scale>0.6</scale><color>ffff4444</color><Icon><href>http://maps.google.com/mapfiles/kml/paddle/red-circle.png</href></Icon></IconStyle><LabelStyle><color>ffffffff</color><scale>1.3</scale></LabelStyle></Style>
    <Style id="arrow"><IconStyle><scale>0.0</scale></IconStyle><LabelStyle><color>ff88ff88</color><scale>1.8</scale></LabelStyle></Style>
"""

# 180 deg meridian (straight cyan line)
meridian_pts = ' '.join('180,{0},0'.format(lat) for lat in range(-90, 91, 10))

# Date line zigzag
dateline_coords = [
    (62,180),(60,-175),(55,-175),(52,180),(50,180),(40,180),(30,180),(20,180),
    (15,180),(10,180),(5,180),(0,180),(-5,180),(-10,180),(-15,180),
    (-18,-175),(-20,-175),(-22,180),(-25,180),(-30,180),(-35,180),(-40,180),
    (-45,180),(-50,180),(-55,180),(-60,180),(-65,180),(-70,180),(-75,180),(-80,180),
]

# Day labels
labels = """  <Placemark><name>Sunrise TOMORROW (West Side)</name><styleUrl>#west</styleUrl><Point><coordinates>175,35,0</coordinates></Point></Placemark>
  <Placemark><name>Go West arrow +1 Day</name><styleUrl>#explain</styleUrl><Point><coordinates>175,28,0</coordinates></Point></Placemark>
  <Placemark><name>Yesterday (East Side)</name><styleUrl>#east</styleUrl><Point><coordinates>-175,35,0</coordinates></Point></Placemark>
  <Placemark><name>Go East arrow -1 Day</name><styleUrl>#explain</styleUrl><Point><coordinates>-175,28,0</coordinates></Point></Placemark>"""

# Assemble and write
kml = """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <name>International Date Line</name>
    <LookAt><longitude>180</longitude><latitude>20</latitude><range>15000000</range><tilt>0</tilt><heading>0</heading><altitudeMode>relativeToGround</altitudeMode></LookAt>
    <open>1</open>""" + STYLES + """
    <Folder><name>Reference Lines</name>
      <Placemark><name>180 deg Meridian</name><styleUrl>#line180</styleUrl><LineString><coordinates>""" + meridian_pts + """</coordinates></LineString></Placemark>
      <Placemark><name>International Date Line</name><styleUrl>#dateline</styleUrl><LineString><coordinates>""" + ' '.join('{1},{0},0'.format(*c) for c in dateline_coords) + """</coordinates></LineString></Placemark>
    </Folder>
    <Folder><name>Day Labels</name>""" + labels + """
      <Placemark><name>arrow West plus 1 day</name><styleUrl>#arrow</styleUrl><Point><coordinates>165,0,0</coordinates></Point></Placemark>
      <Placemark><name>arrow East minus 1 day</name><styleUrl>#arrow</styleUrl><Point><coordinates>-165,0,0</coordinates></Point></Placemark>
    </Folder>
    <Folder><name>Explanations</name>
      <Placemark><name>The International Date Line</name><styleUrl>#explain</styleUrl><Point><coordinates>-170,15,0</coordinates></Point></Placemark>
      <Placemark><name>Not a straight line - zigzags around countries</name><styleUrl>#explain_sm</styleUrl><Point><coordinates>-170,10,0</coordinates></Point></Placemark>
      <Placemark><name>Kiribati shifted it east in 1995</name><styleUrl>#explain_sm</styleUrl><Point><coordinates>-175,-5,0</coordinates></Point></Placemark>
      <Placemark><name>Fiji and Tonga keep it west</name><styleUrl>#explain_sm</styleUrl><Point><coordinates>-175,-20,0</coordinates></Point></Placemark>
      <Placemark><name>Aleutians bend it west for USA</name><styleUrl>#explain_sm</styleUrl><Point><coordinates>-175,55,0</coordinates></Point></Placemark>
    </Folder>
    <Folder><name>Key Cities</name>
      <Placemark><name>Auckland NZ</name><styleUrl>#cap</styleUrl><Point><coordinates>174.8,-36.8,0</coordinates></Point></Placemark>
      <Placemark><name>Suva Fiji</name><styleUrl>#cap</styleUrl><Point><coordinates>178.4,-18.1,0</coordinates></Point></Placemark>
      <Placemark><name>Nuku'alofa Tonga</name><styleUrl>#cap</styleUrl><Point><coordinates>-175.2,-21.1,0</coordinates></Point></Placemark>
      <Placemark><name>Kiritimati Kiribati</name><styleUrl>#cap</styleUrl><Point><coordinates>-157.4,1.9,0</coordinates></Point></Placemark>
      <Placemark><name>Honolulu Hawaii</name><styleUrl>#cap</styleUrl><Point><coordinates>-157.8,21.3,0</coordinates></Point></Placemark>
      <Placemark><name>Petropavlovsk Russia</name><styleUrl>#cap</styleUrl><Point><coordinates>158.7,53.0,0</coordinates></Point></Placemark>
      <Placemark><name>Tokyo Japan</name><styleUrl>#cap</styleUrl><Point><coordinates>139.8,35.7,0</coordinates></Point></Placemark>
      <Placemark><name>Sydney Australia</name><styleUrl>#cap</styleUrl><Point><coordinates>151.2,-33.9,0</coordinates></Point></Placemark>
    </Folder>
  </Document>
</kml>"""

with open('/tmp/dateline.kml', 'w') as f:
    f.write(kml)
print('Date line KML: ' + str(len(kml)) + ' bytes')
