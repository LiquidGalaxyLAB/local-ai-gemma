#!/usr/bin/env python3
"""
Right-screen text panel generator for Liquid Galaxy.
Generates a dark-themed PNG with wrapped text for the right screen overlay.
"""
from PIL import Image, ImageDraw, ImageFont
import textwrap, os, subprocess, sys

def make_panel(title, lines, out_path="/tmp/right_panel.png", width=520, height=620):
    """Generate a clean dark-text panel PNG."""
    img = Image.new('RGBA', (width, height), (10, 12, 22, 235))
    draw = ImageDraw.Draw(img)
    
    try:
        ft = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 17)
        fb = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
        fs = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 10)
    except:
        ft = fb = fs = ImageFont.load_default()
    
    for i in range(45):
        draw.rectangle([(0, i), (width, i)], fill=(30, 40, 80, max(0, 200 - i * 4)))
    
    draw.text((18, 10), title, font=ft, fill=(255, 204, 0))
    draw.line([(18, 38), (width - 18, 38)], fill=(255, 204, 0, 70), width=1)
    
    y = 50
    for item in lines:
        if item.startswith('##'):
            t = item.replace('##', '').strip()
            draw.text((18, y), t, font=fb, fill=(100, 180, 255))
            y += 22
            draw.line([(18, y), (width - 18, y)], fill=(100, 180, 255, 30), width=1)
            y += 4
        elif item.startswith('**'):
            t = item.replace('**', '').strip()
            draw.text((20, y), t, font=fb, fill=(255, 255, 200))
            y += 18
        elif item.strip() == '':
            y += 6
        else:
            for w in textwrap.wrap(item, width=58):
                draw.text((20, y), w, font=fs, fill=(190, 195, 215))
                y += 12
            y += 3
    
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    img.save(out_path)
    return out_path, width, height


def deploy_panel(lg_ip="192.168.1.12", lg_pass="lg"):
    """Deploy the panel PNG and slave_3.kml to LG."""
    # Generate slave_3.kml
    kml = '''<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <name>Right Screen Panel</name>
    <ScreenOverlay>
      <name>Text Panel</name>
      <Icon><href>http://lg1:81/kml/right_panel.png</href></Icon>
      <overlayXY x="1" y="0.5" xunits="fraction" yunits="fraction"/>
      <screenXY x="0.98" y="0.5" xunits="fraction" yunits="fraction"/>
      <size x="0" y="0" xunits="pixels" yunits="pixels"/>
    </ScreenOverlay>
  </Document>
</kml>'''
    with open('/tmp/slave_3.kml', 'w') as f:
        f.write(kml)
    
    subprocess.run(['sshpass', '-p', lg_pass, 'scp', '-o', 'StrictHostKeyChecking=no',
        '/tmp/right_panel.png', '/tmp/slave_3.kml',
        f'lg@{lg_ip}:/home/lg/'], capture_output=True, timeout=30)
    
    subprocess.run(['sshpass', '-p', lg_pass, 'ssh', '-o', 'StrictHostKeyChecking=no',
        f'lg@{lg_ip}',
        'python3 -c "import subprocess; subprocess.run([\'sudo\', \'-S\', \'cp\', \'/home/lg/right_panel.png\', \'/var/www/html/kml/right_panel.png\'], input=b\'lg\\\\n\'); subprocess.run([\'sudo\', \'-S\', \'cp\', \'/home/lg/slave_3.kml\', \'/var/www/html/kml/slave_3.kml\'], input=b\'lg\\\\n\')"'],
        capture_output=True, timeout=30)
    
    print("Panel deployed to right screen")


if __name__ == '__main__':
    # Example: Turkey earthquake
    lines = [
        "## THE EARTHQUAKE",
        "**Magnitude:** M7.8 — February 6, 2023",
        "**Location:** 18km depth near Gaziantep, Turkey",
        "**Duration:** 75 seconds of rupture",
        "**Casualties:** 50,000+ killed, 120,000+ injured",
        "",
        "## WHY IT HAPPENED",
        "**Tectonics:** Arabian Plate pushes north 25mm/yr",
        "**Fault:** East Anatolian Fault — strike-slip",
        "**Rupture:** 300km long across 3 plate boundaries",
        "**Aftershock:** M7.5 struck 9 hours later",
        "",
        "## AFFECTED AREA",
        "11 provinces in Turkey — 13 million people",
        "Northern Syria — Aleppo, Idlib regions",
        "300km fault rupture from Hatay to Malatya",
        "",
        "Source: USGS Earthquake Hazards Program",
    ]
    make_panel("Turkiye Earthquake M7.8", lines)
    deploy_panel()
