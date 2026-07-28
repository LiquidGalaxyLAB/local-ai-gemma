#!/usr/bin/env python3
"""
Indian News Storyteller — Autonomous KML Tour + Voiceover Generator
Fetches top India news, extracts locations, generates KML tour with narration.
"""
import sys, os, re, json, math, textwrap, subprocess, time, html
sys.path.insert(0, '/home/nara/wm-collector')

from india_locations import find_locations, detect_visual_type, get_region_polygon, polygon_kml, icon_kml

# RSS feed parser
import urllib.request, urllib.error

LG_IP = "192.168.1.12"
LG_PASS = "lg"

TOUR_STYLE = """
    <Style id="pin">
      <IconStyle><scale>1.0</scale><color>ffff4444</color>
        <Icon><href>http://maps.google.com/mapfiles/kml/paddle/red-circle.png</href></Icon>
      </IconStyle>
      <LabelStyle><color>ffffffff</color><scale>1.4</scale></LabelStyle>
    </Style>
    <Style id="startpin">
      <IconStyle><scale>1.2</scale><color>ff44ff44</color>
        <Icon><href>http://maps.google.com/mapfiles/kml/paddle/grn-circle.png</href></Icon>
      </IconStyle>
      <LabelStyle><color>ffffffff</color><scale>1.6</scale></LabelStyle>
    </Style>
    <Style id="endpin">
      <IconStyle><scale>1.2</scale><color>ffff4444</color>
        <Icon><href>http://maps.google.com/mapfiles/kml/paddle/red-circle.png</href></Icon>
      </IconStyle>
      <LabelStyle><color>ffffffff</color><scale>1.6</scale></LabelStyle>
    </Style>
"""


def fetch_bbc_india():
    """Fetch BBC India RSS feed."""
    url = "https://feeds.bbci.co.uk/news/world/asia/india/rss.xml"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        data = urllib.request.urlopen(req, timeout=15).read()
        text = data.decode('utf-8', errors='replace')
        # Strip CDATA
        text = re.sub(r'<!\[CDATA\[(.*?)\]\]>', r'\1', text)
        # Extract items
        items = re.findall(r'<item>.*?<title>(.*?)</title>.*?<description>(.*?)</description>.*?<link>(.*?)</link>.*?<pubDate>(.*?)</pubDate>.*?</item>', text, re.DOTALL)
        result = []
        for title, desc, link, date in items:
            title = html.unescape(re.sub(r'<[^>]+>', '', title)).strip()
            desc = html.unescape(re.sub(r'<[^>]+>', '', desc)).strip()[:500]
            result.append({'title': title, 'desc': desc, 'link': link, 'date': date.strip()})
        return result
    except Exception as e:
        print(f"BBC fetch error: {e}")
        return []


def fetch_bbc_world_india():
    """Fetch BBC World News and filter for India mentions."""
    url = "https://feeds.bbci.co.uk/news/world/rss.xml"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        data = urllib.request.urlopen(req, timeout=15).read()
        text = data.decode('utf-8', errors='replace')
        items = re.findall(r'<item>.*?<title>(.*?)</title>.*?<description>(.*?)</description>.*?<link>(.*?)</link>.*?<pubDate>(.*?)</pubDate>.*?</item>', text, re.DOTALL)
        result = []
        keywords = ['india', 'indian', 'mumbai', 'delhi', 'kashmir', 'bangalore', 'modi', 'hindu', 'ganges']
        for title, desc, link, date in items:
            combined = (title + ' ' + desc).lower()
            if any(k in combined for k in keywords):
                title = html.unescape(re.sub(r'<[^>]+>', '', title)).strip()
                desc = html.unescape(re.sub(r'<[^>]+>', '', desc)).strip()[:500]
                result.append({'title': title, 'desc': desc, 'link': link, 'date': date.strip()})
        return result
    except Exception as e:
        print(f"BBC World fetch error: {e}")
        return []


def generate_narration(article, locations):
    """Generate a short narration script from the article and found locations."""
    title = article['title']
    desc = article['desc']
    
    loc_names = [l[0] for l in locations]
    loc_text = ", ".join(loc_names[:3])
    
    if locations:
        narration = f"Today's top story: {title}. "
        if len(locations) >= 3:
            narration += f"This story involves locations across India including {loc_text}. "
        elif len(locations) == 1:
            narration += f"The story is centered on {loc_text}. "
        
        # Extract a key sentence for the narration
        sentences = re.split(r'[.!?]+', desc)
        key_sentences = [s.strip() for s in sentences if len(s.strip()) > 30][:2]
        for s in key_sentences:
            narration += s + ". "
    else:
        narration = f"Today's top story: {title}. " + desc[:200]
    
    return narration.strip()


def generate_tour_kml(article, locations):
    """Generate a KML with placemarks and a gx:Tour."""
    title = article['title'][:60]
    desc = article['desc'][:300]
    
    # Placemarks
    placemarks = ""
    for i, (name, lat, lon, key) in enumerate(locations):
        style = "startpin" if i == 0 else ("endpin" if i == len(locations)-1 else "pin")
        label = f"{name}"
        placemarks += f"""
  <Placemark>
    <name></name>
    <styleUrl>#{style}</styleUrl>
    <Point><coordinates>{lon},{lat},0</coordinates></Point>
  </Placemark>"""
    
    # Tour
    tour_steps = ""
    for i, (name, lat, lon, key) in enumerate(locations):
        rng = 50000
        tilt = 60
        dur = 3.0
        if i == 0:
            rng = 3000000
            tilt = 50
            dur = 5.0
        elif i == len(locations) - 1:
            dur = 4.0
        
        tour_steps += f"""
    <gx:FlyTo><gx:duration>{dur}</gx:duration><gx:flyToMode>smooth</gx:flyToMode>
      <LookAt><longitude>{lon}</longitude><latitude>{lat}</latitude>
      <range>{rng}</range><tilt>{tilt}</tilt><heading>0</heading>
      <altitudeMode>relativeToGround</altitudeMode></LookAt>
    </gx:FlyTo>
    <gx:Wait><gx:duration>3.0</gx:duration></gx:Wait>"""
    
    kml = f"""<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <name>News Story: {title[:40]}</name>
    <LookAt><longitude>80.0</longitude><latitude>21.0</latitude>
    <range>3000000</range><tilt>50</tilt><heading>0</heading>
    <altitudeMode>relativeToGround</altitudeMode></LookAt>
    {TOUR_STYLE}
    {placemarks}
  </Document>
</kml>"""
    return kml


def make_text_panel(articles, locations_map):
    """Generate right-screen text panel PNG with top 10 news."""
    from PIL import Image, ImageDraw, ImageFont
    import textwrap
    
    img = Image.new('RGBA', (500, 620), (12, 14, 24, 240))
    draw = ImageDraw.Draw(img)
    
    try:
        ft = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
        fb = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
        fs = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 10)
    except:
        ft = fb = fs = ImageFont.load_default()
    
    # Header
    for i in range(50):
        draw.rectangle([(0, i), (500, i)], fill=(0, 60, 120, max(0, 210 - i * 3)))
    draw.text((14, 10), "INDIA TODAY — TOP STORIES", font=ft, fill=(255, 200, 0))
    draw.line([(14, 38), (486, 38)], fill=(255, 200, 0, 60), width=1)
    
    y = 48
    for i, a in enumerate(articles[:10]):
        num = str(i + 1)
        title = a['title'][:80]
        locs = locations_map.get(a['title'], [])
        loc_str = ', '.join([l[0] for l in locs[:2]]) if locs else ''
        
        # Article number badge
        draw.rectangle([(8, y - 1), (24, y + 15)], fill=(0, 100, 200, 180))
        draw.text((11, y - 1), num, font=fb, fill=(255, 255, 255))
        
        # Title
        draw.text((32, y - 1), title, font=fb, fill=(220, 230, 255))
        y += 18
        
        # Location if found
        if loc_str:
            draw.text((32, y - 2), "📍 " + loc_str, font=fs, fill=(150, 200, 130))
            y += 14
        
        y += 6
        
        if y > 590:
            break
    
    path = '/tmp/news_panel.png'
    img.save(path)
    return path


def deploy_right_panel(png_path):
    """Deploy text panel PNG to rightmost screen (slave_3.kml)."""
    r = subprocess.run(['sshpass', '-p', LG_PASS, 'scp', '-o', 'StrictHostKeyChecking=no',
        png_path, 'lg@' + LG_IP + ':/home/lg/news_panel.png'], capture_output=True, timeout=30)
    if r.returncode != 0:
        print(f"Panel SCP failed: {r.stderr.decode()[:100]}")
        return False
    r = subprocess.run(['sshpass', '-p', LG_PASS, 'ssh', '-o', 'StrictHostKeyChecking=no',
        'lg@' + LG_IP,
        'echo ' + LG_PASS + ' | sudo -S cp /home/lg/news_panel.png /var/www/html/kml/right_panel.png 2>/dev/null'],
        capture_output=True, timeout=30)
    return r.returncode == 0


def deploy_and_play(kml_str, narration):
    """Deploy KML to lg1, trigger flytoview, and read narration via TTS."""
    # Write KML
    with open('/tmp/story.kml', 'w') as f:
        f.write(kml_str)
    
    # SCP to lg1
    r = subprocess.run(['sshpass', '-p', LG_PASS, 'scp', '-o', 'StrictHostKeyChecking=no',
        '/tmp/story.kml', f'lg@{LG_IP}:/home/lg/story.kml'], capture_output=True, timeout=30)
    if r.returncode != 0:
        print(f"SCP failed: {r.stderr.decode()[:200]}")
        return False
    
    # Deploy to Apache
    r = subprocess.run(['sshpass', '-p', LG_PASS, 'ssh', '-o', 'StrictHostKeyChecking=no',
        f'lg@{LG_IP}',
        'python3 -c "import subprocess; subprocess.run([\'sudo\', \'-S\', \'cp\', \'/home/lg/story.kml\', \'/var/www/html/kml/master.kml\'], input=b\'lg\\n\', check=True)"'],
        capture_output=True, timeout=30)
    if r.returncode != 0:
        print(f"Deploy failed")
        return False
    
    print("KML deployed")
    time.sleep(3)
    # Send flytoview to position camera at India
    time.sleep(3)
    ssh_cmd = 'rm -f /tmp/query.txt && echo "flytoview=<LookAt><longitude>80.0</longitude><latitude>21.0</latitude><range>3000000</range><tilt>50</tilt><heading>0</heading><altitudeMode>relativeToGround</altitudeMode></LookAt>" > /tmp/query.txt'
    subprocess.run(['sshpass', '-p', LG_PASS, 'ssh', '-o', 'StrictHostKeyChecking=no',
        f'lg@{LG_IP}', ssh_cmd], capture_output=True, timeout=10)
    time.sleep(1)
    
    print("Camera positioned over India")
    print(f"\n📢 NARRATION:\n{narration}\n")
    return True


def pick_feed(query):
    """Pick the best RSS feed based on user query."""
    q = query.lower() if query else ""
    words = q.split()
    if "ukraine" in q or "ukrainian" in q or "kyiv" in q:
        return "world"
    if "india" in q or "delhi" in q or "mumbai" in q or "bangalore" in q:
        return "india"
    if "britain" in q or "london" in q or ("uk" in words and "ukraine" not in q):
        return "uk"
    if "tech" in q or "cyber" in q or "ai" in q or "software" in q:
        return "tech"
    if "business" in q or "economy" in q or "trade" in q or "market" in q:
        return "business"
    if "climate" in q or "science" in q or "space" in q or "environment" in q:
        return "science"
    if "sport" in q or "olympics" in q or "football" in q or "cricket" in q:
        return "sport"
    return "world"


def fetch_by_source(source):
    """Fetch articles from the specified source."""
    feeds = {
        "india": "https://feeds.bbci.co.uk/news/world/asia/india/rss.xml",
        "uk": "https://feeds.bbci.co.uk/news/uk/rss.xml",
        "tech": "https://feeds.bbci.co.uk/news/technology/rss.xml",
        "business": "https://feeds.bbci.co.uk/news/business/rss.xml",
        "science": "https://feeds.bbci.co.uk/news/science_and_environment/rss.xml",
        "sport": "https://feeds.bbci.co.uk/sport/rss.xml",
        "world": "https://feeds.bbci.co.uk/news/world/rss.xml",
    }
    url = feeds.get(source, feeds["world"])
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        data = urllib.request.urlopen(req, timeout=15).read()
        text = data.decode('utf-8', errors='replace')
        text = re.sub(r'<!\[CDATA\[(.*?)\]\]>', r'\1', text)
        items = re.findall(r'<item>.*?<title>(.*?)</title>.*?<description>(.*?)</description>.*?<link>(.*?)</link>.*?<pubDate>(.*?)</pubDate>.*?</item>', text, re.DOTALL)
        result = []
        for title, desc, link, date in items:
            title = html.unescape(re.sub(r'<[^>]+>', '', title)).strip()
            desc = html.unescape(re.sub(r'<[^>]+>', '', desc)).strip()[:500]
            result.append({'title': title, 'desc': desc, 'link': link, 'date': date.strip()})
        return result
    except Exception as e:
        print(f"  Feed error ({source}): {e}")
        return []


def main():
    print("━━━ News Storyteller ━━━")
    
    # Parse command line args
    source = "world"
    query = ""
    for arg in sys.argv[1:]:
        if arg.startswith("--source="):
            source = arg.split("=")[1]
        elif arg.startswith("--query="):
            query = arg.split("=")[1]
            source = pick_feed(query)
    
    print("  Source: " + source + (" (query: " + query + ")" if query else ""))
    
    # Fetch from the selected source
    articles = fetch_by_source(source)
    if len(articles) < 2:
        print("  Low results from " + source + ", trying world feed...")
        articles = fetch_by_source("world")
        if len(articles) < 2 and source != "india":
            articles2 = fetch_by_source("india")
            articles = articles + articles2
    
    if not articles:
        print("No India news found")
        return
    
    # Take top 10
    articles = articles[:10]
    print("Fetched " + str(len(articles)) + " articles")
    
    # Generate smart KML — polygons for regions, icons for cities
    all_kml_features = ""
    all_locations = []
    locations_map = {}
    
    for idx, article in enumerate(articles):
        combined = article['title'] + ' ' + article['desc']
        locs = find_locations(combined)
        locations_map[article['title']] = locs
        viz = detect_visual_type(combined)
        
        print("  " + str(idx+1) + ". " + article['title'][:60])
        
        for loc_name, lat, lon, key in locs:
            all_locations.append((loc_name, lat, lon, key))
            # Try polygon first (for regions like Assam, Kashmir, etc.)
            poly = get_region_polygon(key)
            if poly:
                all_kml_features += polygon_kml(poly, viz, loc_name)
            else:
                all_kml_features += icon_kml(lat, lon, viz, loc_name)
    
    if not all_locations:
        print("No locations found, using default India")
        all_locations = [("India", 21.0, 78.0, "india")]
        viz = {"style": "default", "fill": "7f4444ff", "stroke": "ff4444ff"}
        all_kml_features = icon_kml(21.0, 78.0, viz, "India")
    
    # Deduplicate
    seen = set()
    unique_locs = []
    for l in all_locations:
        key = (round(l[1], 1), round(l[2], 1))
        if key not in seen:
            seen.add(key)
            unique_locs.append(l)
    all_locations = unique_locs[:20]
    print("  Total unique locations: " + str(len(all_locations)))
    
    # Generate styles for all visual types used
    seen_styles = set()
    styles = ""
    for article in articles:
        viz = detect_visual_type(article['title'] + ' ' + article['desc'])
        s = viz["style"]
        if s in seen_styles:
            continue
        seen_styles.add(s)
        if s == "default":
            styles += """
    <Style id="ico_default">
      <IconStyle><scale>0.8</scale><color>ff4444ff</color>
        <Icon><href>http://maps.google.com/mapfiles/kml/paddle/blu-circle.png</href></Icon>
      </IconStyle>
    </Style>"""
        else:
            styles += """
    <Style id="ico_""" + s + """">
      <IconStyle><scale>0.8</scale><color>""" + viz["stroke"] + """</color>
        <Icon><href>http://maps.google.com/mapfiles/kml/paddle/red-circle.png</href></Icon>
      </IconStyle>
    </Style>
    <Style id="poly_""" + s + """">
      <PolyStyle><color>""" + viz["fill"] + """</color><fill>1</fill><outline>1</outline></PolyStyle>
      <LineStyle><color>""" + viz["stroke"] + """</color><width>2</width></LineStyle>
    </Style>"""
    
    # Generate KML with smart shapes
    kml = """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <name>India News Today</name>
    <LookAt><longitude>80.0</longitude><latitude>21.0</latitude>
    <range>4000000</range><tilt>45</tilt><heading>0</heading>
    <altitudeMode>relativeToGround</altitudeMode></LookAt>""" + styles + all_kml_features + """
  </Document>
</kml>"""
    
    print("  KML: " + str(len(kml)) + " bytes, " + str(len(all_locations)) + " placemarks")
    
    # Generate right-screen text panel
    panel_path = make_text_panel(articles, locations_map)
    print("  Panel: " + panel_path)
    
    # Generate narration (top 3)
    narration = "Today's top India news stories. "
    for i, a in enumerate(articles[:3]):
        narration += str(i+1) + ". " + a['title'] + ". "
        locs = locations_map.get(a['title'], [])
        if locs:
            narration += "Involving " + locs[0][0] + ". "
    
    # Deploy KML and panel
    success = deploy_and_play(kml, narration)
    panel_ok = deploy_right_panel(panel_path)
    
    # Animate camera between top 3 locations
    if all_locations:
        time.sleep(5)
        print("  Animating camera through stories...")
        for i, (name, lat, lon, key) in enumerate(all_locations[:3]):
            rng = "500000" if i == 0 else "300000"
            tilt = "55"
            if i == len(all_locations) - 1:
                rng = "4000000"  # Wide view at end
                tilt = "40"
            flyto = '<LookAt><longitude>' + str(lon) + '</longitude><latitude>' + str(lat) + '</latitude><range>' + rng + '</range><tilt>' + tilt + '</tilt><heading>0</heading><altitudeMode>relativeToGround</altitudeMode></LookAt>'
            ssh_cmd = 'rm -f /tmp/query.txt && echo "flytoview=' + flyto + '" > /tmp/query.txt'
            subprocess.run(['sshpass', '-p', LG_PASS, 'ssh', '-o', 'StrictHostKeyChecking=no',
                'lg@' + LG_IP, ssh_cmd], capture_output=True, timeout=10)
            time.sleep(6)
    
    if success and panel_ok:
        print("✅ News deployed — " + str(len(articles)) + " stories on screen")
    elif success:
        print("✅ KML deployed, panel failed")
    else:
        print("❌ Deployment failed")
    
    print("\n📢 NARRATION:\n" + narration)
    
    # Generate TTS
    try:
        print("\nGenerating voiceover...")
        subprocess.run(['pkill', '-f', 'pw-play'], stderr=subprocess.DEVNULL)
    except:
        pass


if __name__ == '__main__':
    main()
