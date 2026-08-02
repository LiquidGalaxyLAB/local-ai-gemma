#!/usr/bin/env python3
"""Generate a dark-themed right-screen text panel PNG for LG overlay."""
from PIL import Image, ImageDraw, ImageFont
import textwrap, os

def make_panel(title, lines, output_path="/tmp/right_panel.png", width=500, height=600):
    img = Image.new('RGBA', (width, height), (12, 14, 24, 240))
    draw = ImageDraw.Draw(img)
    try:
        ft = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 17)
        fb = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 13)
        fs = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 11)
    except:
        ft = fb = fs = ImageFont.load_default()
    for i in range(50):
        draw.rectangle([(0, i), (width, i)], fill=(35, 45, 85, max(0, 210 - i * 3)))
    draw.text((18, 12), title, font=ft, fill=(255, 204, 0))
    draw.line([(18, 40), (width - 18, 40)], fill=(255, 204, 0, 60), width=1)
    y = 55
    for line in lines:
        if line.startswith("##"):
            t = line.replace("##", "").strip()
            draw.text((18, y), t, font=fb, fill=(100, 190, 255))
            y += 22
            draw.line([(18, y), (width - 18, y)], fill=(100, 190, 255, 25), width=1)
            y += 4
        elif line.strip():
            for w in textwrap.wrap(line, width=52):
                draw.text((20, y), w, font=fs, fill=(195, 200, 220))
                y += 14
            y += 2
        else:
            y += 8
    img.save(output_path)
    return output_path

def deploy_panel(pi_ip, lg_ip, pw, output_path, title, lines):
    """Generate and deploy a text panel to the rightmost LG screen (slave_N.kml)."""
    make_panel(title, lines, output_path)
    import subprocess
    subprocess.run(['sshpass', '-p', pw, 'scp', '-o', 'StrictHostKeyChecking=no',
        output_path, lg_ip + ':/home/lg/right_panel.png'], capture_output=True, timeout=15)
    subprocess.run(['sshpass', '-p', pw, 'ssh', '-o', 'StrictHostKeyChecking=no', lg_ip,
        "python3 -c \"import subprocess; subprocess.run(['sudo', '-S', 'cp', '/home/lg/right_panel.png', '/var/www/html/kml/right_panel.png'], input=b'" + pw + "\\n')\""],
        capture_output=True, timeout=15)
    return output_path
