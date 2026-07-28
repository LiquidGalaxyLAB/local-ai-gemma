#!/usr/bin/env python3
"""Weather KML generator — 3D temp column, wind arrow, weather icon, right panel."""
import sys, os, json, subprocess, time, urllib.request
from PIL import Image, ImageDraw, ImageFont
import textwrap

LG_IP = "192.168.1.12"
LG_PASS = "lg"
CITY = "Pune"
LAT, LON = 18.5204, 73.8567

def fetch():
    url = "https://wttr.in/" + CITY + "?format=j1"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    d = json.loads(urllib.request.urlopen(req, timeout=15).read())['current_condition'][0]
    return d

def make_panel(d):
    img = Image.new('RGBA', (500, 440), (20, 25, 50, 240))
    draw = ImageDraw.Draw(img)
    try: ft=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',18); fb=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',14); fs=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',11)
    except: ft=fb=fs=ImageFont.load_default()
    for i in range(50): draw.rectangle([(0,i),(500,i)], fill=(0,60,120,max(0,210-i*3)))
    draw.text((16,12), CITY + ' — WEATHER', font=ft, fill=(0,220,255))
    draw.line([(16,42),(484,42)], fill=(0,220,255,60), width=1)
    y, items = 55, [
        ("Conditions", d['weatherDesc'][0]['value'] + " | " + d['temp_C'] + "C feels " + d['FeelsLikeC'] + "C"),
        ("Wind", d['windspeedKmph'] + " km/h " + d['winddir16Point']),
        ("Humidity", d['humidity'] + "% | Cloud: " + d['cloudcover'] + "%"),
        ("Pressure", d['pressure'] + " hPa | Vis: " + d['visibility'] + " km"),
        ("UV Index", d['uvIndex']),
    ]
    for h, b in items:
        draw.text((16,y), h, font=fb, fill=(100,200,255)); y+=22
        draw.line([(16,y),(484,y)], fill=(100,200,255,20), width=1); y+=4
        for wl in textwrap.wrap(b, width=55): draw.text((20,y), wl, font=fs, fill=(200,210,240)); y+=16
        y+=4
    img.save('/tmp/wx_panel.png')

def make_kml(d):
    lat, lon = LAT, LON
    temp = int(d['temp_C'])
    h = temp * 1000
    desc = d['weatherDesc'][0]['value'].lower()
    if 'rain' in desc: icon = 'paddle/red-circle.png'
    elif 'cloud' in desc or 'overcast' in desc: icon = 'paddle/grn-circle.png'
    elif 'sun' in desc or 'clear' in desc: icon = 'paddle/ylw-circle.png'
    else: icon = 'paddle/blu-circle.png'
    
    if temp >= 35: col, fill = 'ff0000ff', '7f0000ff'
    elif temp >= 30: col, fill = 'ff0044ff', '7f0044ff'
    elif temp >= 25: col, fill = 'ff8822ff', '7f8822ff'
    elif temp >= 20: col, fill = 'ff22ff44', '7f22ff44'
    else: col, fill = 'ffff0000', '7fff0000'
    
    cc = (str(round(lon-0.02,4)) + ',' + str(round(lat-0.02,4)) + ',0 ' +
          str(round(lon+0.02,4)) + ',' + str(round(lat-0.02,4)) + ',0 ' +
          str(round(lon+0.02,4)) + ',' + str(round(lat+0.02,4)) + ',0 ' +
          str(round(lon-0.02,4)) + ',' + str(round(lat+0.02,4)) + ',0 ' +
          str(round(lon-0.02,4)) + ',' + str(round(lat-0.02,4)) + ',0')
    
    kml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<kml xmlns="http://www.opengis.net/kml/2.2">\n<Document>\n'
        '<name>' + CITY + ' Weather</name>\n'
        '<LookAt><longitude>' + str(lon) + '</longitude><latitude>' + str(lat) +
        '</latitude><range>30000</range><tilt>60</tilt><heading>0</heading>'
        '<altitudeMode>relativeToGround</altitudeMode></LookAt>\n'
        
        '<Style id="col"><PolyStyle><color>' + fill + '</color><fill>1</fill><outline>1</outline></PolyStyle>'
        '<LineStyle><color>' + col + '</color><width>2</width></LineStyle></Style>\n'
        
        '<Style id="ico"><IconStyle><scale>1.5</scale><color>ffffffff</color>'
        '<Icon><href>http://maps.google.com/mapfiles/kml/' + icon + '</href></Icon>'
        '</IconStyle><LabelStyle><scale>0.0</scale></LabelStyle></Style>\n'
        
        '<Style id="lbl"><IconStyle><scale>0.0</scale></IconStyle>'
        '<LabelStyle><scale>2.0</scale><color>ffffffff</color></LabelStyle></Style>\n'
        
        '<Style id="wind"><LineStyle><color>ffffffff</color><width>3</width></LineStyle></Style>\n'
        
        # 3D temp column
        '<Placemark><name></name><styleUrl>#col</styleUrl>'
        '<Polygon><extrude>1</extrude><altitudeMode>relativeToGround</altitudeMode>'
        '<outerBoundaryIs><LinearRing><coordinates>' + cc + '</coordinates></LinearRing></outerBoundaryIs>'
        '</Polygon></Placemark>\n'
        
        # Weather icon at top
        '<Placemark><name></name><styleUrl>#ico</styleUrl>'
        '<Point><coordinates>' + str(lon) + ',' + str(lat) + ',' + str(h) + '</coordinates></Point>'
        '</Placemark>\n'
        
        # Temperature label
        '<Placemark><name>' + d['temp_C'] + 'C</name><styleUrl>#lbl</styleUrl>'
        '<Point><coordinates>' + str(lon+0.05) + ',' + str(lat+0.02) + ',' + str(h) + '</coordinates></Point>'
        '</Placemark>\n'
        
        # Wind arrow
        '<Placemark><name></name><styleUrl>#wind</styleUrl>'
        '<LineString><extrude>1</extrude><altitudeMode>relativeToGround</altitudeMode>'
        '<coordinates>' + str(lon-0.03) + ',' + str(lat) + ',500 ' + str(lon+0.03) + ',' + str(lat) + ',500'
        '</coordinates></LineString></Placemark>\n'
        
        # City label
        '<Placemark><name>' + CITY + '</name><styleUrl>#lbl</styleUrl>'
        '<Point><coordinates>' + str(lon) + ',' + str(lat) + ',0</coordinates></Point>'
        '</Placemark>\n'
        
        '</Document>\n</kml>\n'
    )
    return kml

def main():
    print("=== Weather: " + CITY + " ===")
    d = fetch()
    print("  " + d['weatherDesc'][0]['value'] + ", " + d['temp_C'] + "C")
    kml = make_kml(d)
    make_panel(d)
    with open('/tmp/wx.kml','w') as f: f.write(kml)
    subprocess.run(['sshpass','-p',LG_PASS,'scp','-o','StrictHostKeyChecking=no','/tmp/wx.kml','lg@'+LG_IP+':/home/lg/wx.kml'],capture_output=True,timeout=15)
    subprocess.run(['sshpass','-p',LG_PASS,'scp','-o','StrictHostKeyChecking=no','/tmp/wx_panel.png','lg@'+LG_IP+':/home/lg/wp.png'],capture_output=True,timeout=15)
    subprocess.run(['sshpass','-p',LG_PASS,'ssh','-o','StrictHostKeyChecking=no','lg@'+LG_IP,
        'echo '+LG_PASS+' | sudo -S cp /home/lg/wx.kml /var/www/html/kml/master.kml 2>/dev/null; echo '+LG_PASS+' | sudo -S cp /home/lg/wp.png /var/www/html/kml/right_panel.png 2>/dev/null'],capture_output=True,timeout=15)
    print("  Deployed. Flying to " + CITY + "...")
    time.sleep(8)
    f2 = '<LookAt><longitude>' + str(LON) + '</longitude><latitude>' + str(LAT) + '</latitude><range>30000</range><tilt>60</tilt><heading>0</heading><altitudeMode>relativeToGround</altitudeMode></LookAt>'
    cmd = 'rm -f /tmp/query.txt && echo "flytoview=' + f2 + '" > /tmp/query.txt'
    subprocess.run(['sshpass','-p',LG_PASS,'ssh','-o','StrictHostKeyChecking=no','lg@'+LG_IP,cmd],capture_output=True,timeout=10)
    print("  Done. Column: " + d['temp_C'] + "km tall")

if __name__ == '__main__':
    main()
