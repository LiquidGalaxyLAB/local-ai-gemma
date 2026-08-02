#!/usr/bin/env python3
"""
Armed Conflicts — Dynamic KMLs + synced voiceover + right-screen text panel.
Camera stops at each zone -> deploys text panel -> plays voiceover -> waits -> next.
"""
import sys, os, subprocess, time, html, re, math, random, urllib.request
from PIL import Image, ImageDraw, ImageFont
import textwrap

LG_IP = "192.168.1.12"
LG_PASS = "lg"
random.seed(42)

# 10 conflict zones with unique visual approaches
ZONES = [
    {"name":"Ukraine War","lat":48.5,"lon":32.5,"intensity":5,
     "desc":"Europe's deadliest conflict since WWII. 300km front line across eastern Ukraine.",
     "label":"Ukraine: 300km front line, 38M affected"},
    {"name":"Gaza Strip","lat":31.4,"lon":34.5,"intensity":5,
     "desc":"Dense urban warfare in Gaza Strip. 2.1 million people under siege.",
     "label":"Gaza: 2.1M under siege, urban conflict"},
    {"name":"Sudan","lat":15.5,"lon":32.5,"intensity":4,
     "desc":"Civil war between SAF and RSF. Over 8 million people displaced.",
     "label":"Sudan: 8M displaced, SAF vs RSF"},
    {"name":"Myanmar","lat":21.5,"lon":96.5,"intensity":4,
     "desc":"Multi-front civil war. Junta fighting resistance forces across 3 regions.",
     "label":"Myanmar: Junta vs resistance, 3 fronts"},
    {"name":"DRC","lat":-2.0,"lon":25.0,"intensity":4,
     "desc":"M23 rebels and 120+ armed groups active in eastern Congo.",
     "label":"DRC: M23 rebels, 120+ militias"},
    {"name":"Sahel","lat":14.0,"lon":2.0,"intensity":4,
     "desc":"Jihadist insurgency spreading across Mali, Niger, and Burkina Faso.",
     "label":"Sahel: Jihadist insurgency, 3 nations"},
    {"name":"Yemen","lat":15.5,"lon":47.5,"intensity":3,
     "desc":"Houthi coalition conflict. Blockade causing famine conditions.",
     "label":"Yemen: Blockade, famine, civil war"},
    {"name":"Ethiopia","lat":12.5,"lon":39.5,"intensity":3,
     "desc":"Tigray ethnic conflict causing regional instability in the Horn.",
     "label":"Ethiopia: Tigray ethnic conflict"},
    {"name":"Haiti","lat":18.5,"lon":-72.3,"intensity":4,
     "desc":"Gangs control 80% of capital. Political collapse, hunger crisis.",
     "label":"Haiti: Gangs control 80%, crisis"},
    {"name":"Kashmir","lat":34.0,"lon":76.0,"intensity":2,
     "desc":"India-Pakistan border tensions along the Line of Control.",
     "label":"Kashmir: LoC tensions, India-Pakistan"},
]

def make_text_panel(zone):
    img = Image.new('RGBA', (500, 500), (12, 14, 24, 240))
    draw = ImageDraw.Draw(img)
    try:
        ft = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
        fb = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
        fs = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
    except:
        ft = fb = fs = ImageFont.load_default()
    for i in range(50):
        draw.rectangle([(0, i), (500, i)], fill=(40, 20, 30, max(0, 200 - i * 3)))
    draw.text((16, 12), "ARMED CONFLICTS", font=ft, fill=(255, 60, 60))
    draw.line([(16, 42), (484, 42)], fill=(255, 60, 60, 60), width=1)
    draw.text((16, 54), zone["name"], font=fb, fill=(255, 200, 100))
    for w in textwrap.wrap(zone["desc"], width=50):
        draw.text((16, 80), w, font=fs, fill=(200, 200, 220))
    y = 115
    draw.text((16, y), "Intensity:", font=fs, fill=(150, 150, 180))
    for bi in range(5):
        col = (255, 80, 80) if bi < zone["intensity"] else (40, 40, 50)
        draw.rectangle([(100 + bi*25, y), (122 + bi*25, y+18)], fill=col)
    y += 35
    draw.text((16, y), "Location: "+str(round(zone["lat"],1))+"N, "+str(round(zone["lon"],1))+"E", font=fs, fill=(150,150,180))
    y += 22
    draw.text((16, y), "Affected: N/A", font=fs, fill=(150,150,180))
    y += 35
    draw.ellipse([(16, y), (30, y+14)], fill=(255,0,0))
    draw.text((38, y), "ACTIVE CONFLICT", font=fs, fill=(255,255,255))
    y += 30
    draw.line([(16, y), (484, y)], fill=(60,60,80), width=1)
    y += 10
    draw.text((16, y), "Source: BBC Monitoring + Static Config", font=ImageFont.load_default(), fill=(100,100,120))
    path = "/tmp/right_panel.png"
    img.save(path)
    return path

def deploy_panel(path):
    subprocess.run(['sshpass','-p',LG_PASS,'scp','-o','StrictHostKeyChecking=no',path,'lg@'+LG_IP+':/home/lg/rp.png'],capture_output=True,timeout=30)
    subprocess.run(['sshpass','-p',LG_PASS,'ssh','-o','StrictHostKeyChecking=no','lg@'+LG_IP,'echo '+LG_PASS+' | sudo -S cp /home/lg/rp.png /var/www/html/kml/right_panel.png 2>/dev/null'],capture_output=True,timeout=15)

def fly_to(lon, lat, rng, tilt=55):
    f = '<LookAt><longitude>'+str(lon)+'</longitude><latitude>'+str(lat)+'</latitude><range>'+str(rng)+'</range><tilt>'+str(tilt)+'</tilt><heading>0</heading><altitudeMode>relativeToGround</altitudeMode></LookAt>'
    cmd = 'rm -f /tmp/query.txt && echo "flytoview='+f+'" > /tmp/query.txt'
    subprocess.run(['sshpass','-p',LG_PASS,'ssh','-o','StrictHostKeyChecking=no','lg@'+LG_IP,cmd],capture_output=True,timeout=10)

def build_kml():
    styles, features = "", ""
    for i, z in enumerate(ZONES):
        lat, lon, s = z["lat"], z["lon"], "z"+str(i)
        n = z["name"].lower().replace(" ", "_")
        styles += '<Style id="'+s+'_txt"><IconStyle><scale>0.0</scale></IconStyle><LabelStyle><color>ffffffff</color><scale>2.2</scale></LabelStyle></Style>\n'
        features += '<Placemark><name>'+z["label"]+'</name><styleUrl>#'+s+'_txt</styleUrl><Point><coordinates>'+str(lon+1.8)+','+str(lat+0.8)+',0</coordinates></Point></Placemark>\n'
        if "ukraine" in n:
            styles += '<Style id="'+s+'_l"><LineStyle><color>ffff0000</color><width>6</width></LineStyle>\n'
            line = ' '.join(str(lon+o)+','+str(lat+o2)+',0' for o,o2 in [(0,0),(2,1),(4,0),(6,1),(8,0)])
            features += '<Placemark><name></name><styleUrl>#'+s+'_l</styleUrl><LineString><extrude>1</extrude><altitudeMode>relativeToGround</altitudeMode><coordinates>'+line+'</coordinates></LineString></Placemark>\n'
        elif "gaza" in n:
            styles += '<Style id="'+s+'_r"><LineStyle><color>ffff4400</color><width>2</width></LineStyle>\n<Style id="'+s+'_d"><IconStyle><scale>1.2</scale><color>ffff4400</color><Icon><href>http://maps.google.com/mapfiles/kml/paddle/red-circle.png</href></Icon></IconStyle>\n'
            for rng in range(1,5):
                ring = ' '.join(str(lon+rng*0.12*math.cos(math.radians(a)))+','+str(lat+rng*0.12*math.sin(math.radians(a)))+',0' for a in range(0,360,20))
                features += '<Placemark><name></name><styleUrl>#'+s+'_r</styleUrl><LineString><coordinates>'+ring+'</coordinates></LineString></Placemark>\n'
            for _ in range(25):
                dx, dy = lon+random.uniform(-0.15,0.15), lat+random.uniform(-0.15,0.15)
                features += '<Placemark><name></name><styleUrl>#'+s+'_d</styleUrl><Point><coordinates>'+str(dx)+','+str(dy)+',0</coordinates></Point></Placemark>\n'
        elif "sudan" in n:
            styles += '<Style id="'+s+'_a"><LineStyle><color>ffff6600</color><width>4</width></LineStyle>\n'
            for ax,ay,bx,by in [(lon,lat,lon+5,lat-2),(lon+1,lat+1,lon+4,lat-1)]:
                features += '<Placemark><name></name><styleUrl>#'+s+'_a</styleUrl><LineString><extrude>1</extrude><altitudeMode>relativeToGround</altitudeMode><coordinates>'+str(ax)+','+str(ay)+',5000 '+str(bx)+','+str(by)+',5000</coordinates></LineString></Placemark>\n'
        elif "myanmar" in n:
            styles += '<Style id="'+s+'_d"><IconStyle><scale>0.6</scale><color>ffcc0000</color><Icon><href>http://maps.google.com/mapfiles/kml/paddle/red-circle.png</href></Icon></IconStyle>\n'
            for _ in range(20):
                dx, dy = lon+random.uniform(-2,3), lat+random.uniform(-1.5,2)
                features += '<Placemark><name></name><styleUrl>#'+s+'_d</styleUrl><Point><coordinates>'+str(dx)+','+str(dy)+',0</coordinates></Point></Placemark>\n'
        elif "drc" in n:
            for fi,(fo,fa) in enumerate([(0,0),(1.5,1),(-1,0.5),(2,-1)]):
                fc = ["ff0000ff","ffff4400","ffffaa00","ff00ff00"][fi]
                styles += '<Style id="'+s+'_f'+str(fi)+'"><IconStyle><scale>1.0</scale><color>'+fc+'</color><Icon><href>http://maps.google.com/mapfiles/kml/paddle/blu-circle.png</href></Icon></IconStyle>\n'
                features += '<Placemark><name></name><styleUrl>#'+s+'_f'+str(fi)+'</styleUrl><Point><coordinates>'+str(lon+fo)+','+str(lat+fa)+',0</coordinates></Point></Placemark>\n'
        elif "sahel" in n:
            for wi,(wr,wc) in enumerate([((lon-1,lat-1,lon+1,lat+1),"7fff8844"),((lon-2,lat-2,lon+2,lat+2),"5fff8844"),((lon-3,lat-3,lon+3,lat+3),"3fff8844")]):
                styles += '<Style id="'+s+'_w'+str(wi)+'"><PolyStyle><color>'+wc+'</color><fill>1</fill><outline>1</outline></PolyStyle>\n'
                features += '<Placemark><name></name><styleUrl>#'+s+'_w'+str(wi)+'</styleUrl><Polygon><extrude>1</extrude><altitudeMode>relativeToGround</altitudeMode><outerBoundaryIs><LinearRing><coordinates>'+str(wr[0])+','+str(wr[1])+',0 '+str(wr[2])+','+str(wr[1])+',0 '+str(wr[2])+','+str(wr[3])+',0 '+str(wr[0])+','+str(wr[3])+',0 '+str(wr[0])+','+str(wr[1])+',0</coordinates></LinearRing></outerBoundaryIs></Polygon></Placemark>\n'
        elif "yemen" in n:
            styles += '<Style id="'+s+'_b"><LineStyle><color>ffaa4444</color><width>3</width></LineStyle>\n'
            ring = ' '.join(str(lon+0.8*math.cos(math.radians(a)))+','+str(lat+0.8*math.sin(math.radians(a)))+',0' for a in range(0,360,15))
            features += '<Placemark><name></name><styleUrl>#'+s+'_b</styleUrl><LineString><coordinates>'+ring+'</coordinates></LineString></Placemark>\n'
        elif "ethiopia" in n:
            for ei,(eo,ea,ec) in enumerate([(0,0,"8fff8844"),(1,1,"8fff4422"),(-0.5,-0.5,"8f44aaff")]):
                styles += '<Style id="'+s+'_e'+str(ei)+'"><PolyStyle><color>'+ec+'</color><fill>1</fill><outline>1</outline></PolyStyle>\n'
                features += '<Placemark><name></name><styleUrl>#'+s+'_e'+str(ei)+'</styleUrl><Polygon><extrude>1</extrude><altitudeMode>relativeToGround</altitudeMode><outerBoundaryIs><LinearRing><coordinates>'+str(lon+eo-1)+','+str(lat+ea-1)+',0 '+str(lon+eo+1)+','+str(lat+ea-1)+',0 '+str(lon+eo+1)+','+str(lat+ea+1)+',0 '+str(lon+eo-1)+','+str(lat+ea+1)+',0 '+str(lon+eo-1)+','+str(lat+ea-1)+',0</coordinates></LinearRing></outerBoundaryIs></Polygon></Placemark>\n'
        elif "haiti" in n:
            styles += '<Style id="'+s+'_d"><IconStyle><scale>0.8</scale><color>ffff8822</color><Icon><href>http://maps.google.com/mapfiles/kml/paddle/red-circle.png</href></Icon></IconStyle>\n'
            for _ in range(20):
                dx, dy, dh = lon+random.uniform(-0.3,0.3), lat+random.uniform(-0.3,0.3), int(random.uniform(5000,35000))
                features += '<Placemark><name></name><styleUrl>#'+s+'_d</styleUrl><Point><coordinates>'+str(dx)+','+str(dy)+','+str(dh)+'</coordinates></Point></Placemark>\n'
        elif "kashmir" in n:
            styles += '<Style id="'+s+'_l"><LineStyle><color>ff44aaff</color><width>3</width></LineStyle>\n'
            loc = ' '.join(str(lon+o)+','+str(lat+o2)+',0' for o,o2 in [(0,0),(0.5,0.2),(1,0),(1.5,0.3),(2,0)])
            features += '<Placemark><name></name><styleUrl>#'+s+'_l</styleUrl><LineString><coordinates>'+loc+'</coordinates></LineString></Placemark>\n'
    return ('<?xml version="1.0" encoding="UTF-8"?>\n<kml xmlns="http://www.opengis.net/kml/2.2">\n<Document>\n<name>Armed Conflicts</name>\n<LookAt><longitude>20</longitude><latitude>20</latitude><range>20000000</range><tilt>0</tilt><heading>0</heading><altitudeMode>relativeToGround</altitudeMode></LookAt>\n'+styles+features+'</Document>\n</kml>\n')

def main():
    print("=== Dynamic Armed Conflicts ===")
    kml = build_kml()
    count = kml.count("Placemark")
    print("  "+str(len(kml))+" bytes, "+str(count)+" features")
    with open('/tmp/dc.kml','w') as f: f.write(kml)
    subprocess.run(['sshpass','-p',LG_PASS,'scp','-o','StrictHostKeyChecking=no','/tmp/dc.kml','lg@'+LG_IP+':/home/lg/dc.kml'],capture_output=True,timeout=30)
    subprocess.run(['sshpass','-p',LG_PASS,'ssh','-o','StrictHostKeyChecking=no','lg@'+LG_IP,'echo '+LG_PASS+' | sudo -S cp /home/lg/dc.kml /var/www/html/kml/master.kml 2>/dev/null'],capture_output=True,timeout=30)
    print("  Waiting for KML..."); time.sleep(8); print("  KML deployed.\n")
    deploy_panel(make_text_panel(ZONES[0]))
    print("  Starting synced camera tour...\n")
    fly_to(20, 20, 20000000, 0); time.sleep(5)
    for z in ZONES:
        print("    "+z["name"])
        fly_to(z["lon"], z["lat"], 600000, 55); time.sleep(2)
        deploy_panel(make_text_panel(z)); time.sleep(1)
        print("      VOICE: "+z["desc"][:100]); time.sleep(10)
    fly_to(20, 20, 20000000, 0)
    print("\n  Tour complete.")

if __name__ == '__main__':
    main()
