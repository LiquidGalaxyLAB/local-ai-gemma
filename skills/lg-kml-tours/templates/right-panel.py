#!/usr/bin/env python3
"""
Right-screen text panel generator template for LG.
Customize the title and lines array for your use case.
"""
from PIL import Image, ImageDraw, ImageFont
import textwrap, os, subprocess

LG_IP = "192.168.1.12"
LG_PASS = "lg"

def make_panel(title, lines, out_path="/tmp/right_panel.png"):
    """Generate a dark-themed text panel PNG."""
    w, h = 520, 620
    img = Image.new('RGBA', (w, h), (10, 12, 22, 235))
    draw = ImageDraw.Draw(img)
    
    try:
        ft = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 17)
        fb = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 13)
        fs = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 11)
    except:
        ft = fb = fs = ImageFont.load_default()
    
    for i in range(45):
        draw.rectangle([(0, i), (w, i)], fill=(30, 40, 80, max(0, 200 - i * 4)))
    
    draw.text((18, 10), title, font=ft, fill=(255, 204, 0))
    draw.line([(18, 38), (w - 18, 38)], fill=(255, 204, 0, 70), width=1)
    
    y = 50
    for item in lines:
        if item.startswith('##'):
            draw.text((18, y), item.replace('##', '').strip(), font=fb, fill=(100, 180, 255))
            y += 22
            draw.line([(18, y), (w - 18, y)], fill=(100, 180, 255, 25), width=1)
            y += 4
        elif item.strip() == '':
            y += 8
        else:
            for wl in textwrap.wrap(item, width=52):
                draw.text((20, y), wl, font=fs, fill=(195, 200, 220))
                y += 13
            y += 2
    
    os.makedirs(os.path.dirname(out_path) or '.', exist_ok=True)
    img.save(out_path)
    return out_path


def deploy_panel():
    """Deploy the panel PNG and slave_3.kml to LG."""
    kml = '''<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
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
    
    subprocess.run(['sshpass', '-p', LG_PASS, 'scp', '-o', 'StrictHostKeyChecking=no',
        '/tmp/right_panel.png', '/tmp/slave_3.kml', f'lg@{LG_IP}:/home/lg/'], capture_output=True)
    subprocess.run(['sshpass', '-p', LG_PASS, 'ssh', '-o', 'StrictHostKeyChecking=no', f'lg@{LG_IP}',
        'python3 -c "import subprocess; subprocess.run([\'sudo\', \'-S\', \'cp\', \'/home/lg/right_panel.png\', '
        '\'/var/www/html/kml/right_panel.png\'], input=b\'lg\\\\n\'); subprocess.run([\'sudo\', \'-S\', '
        '\'cp\', \'/home/lg/slave_3.kml\', \'/var/www/html/kml/slave_3.kml\'], input=b\'lg\\\\n\')"'],
        capture_output=True)
    print("Panel deployed")


if __name__ == '__main__':
    lines = [
        "## SECTION HEADER",
        "• Bullet point with key information",
        "• Another bullet with more detail",
        "",
        "## SECOND SECTION",
        "• Item one",
        "• Item two",
        "",
        "Source: Reference",
    ]
    make_panel("TITLE", lines)
    deploy_panel()
