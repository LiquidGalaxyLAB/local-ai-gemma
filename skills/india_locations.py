#!/usr/bin/env python3
"""
India Location Database for News Storytelling
Maps city/region names mentioned in news articles to coordinates.
"""
import re, json, os, math

# Major Indian cities and landmarks with coordinates
LOCATIONS = {
    # National
    "india": (21.0, 78.0, "India"),
    # Metros
    "delhi": (28.6139, 77.2090, "New Delhi"),
    "new delhi": (28.6139, 77.2090, "New Delhi"),
    "mumbai": (19.0760, 72.8777, "Mumbai"),
    "bangalore": (12.9716, 77.5946, "Bengaluru"),
    "bengaluru": (12.9716, 77.5946, "Bengaluru"),
    "hyderabad": (17.3850, 78.4867, "Hyderabad"),
    "chennai": (13.0827, 80.2707, "Chennai"),
    "kolkata": (22.5726, 88.3639, "Kolkata"),
    "ahmedabad": (23.0225, 72.5714, "Ahmedabad"),
    "pune": (18.5204, 73.8567, "Pune"),
    "jaipur": (26.9124, 75.7873, "Jaipur"),
    "lucknow": (26.8467, 80.9462, "Lucknow"),
    "surat": (21.1702, 72.8311, "Surat"),
    # State capitals
    "bhopal": (23.2599, 77.4126, "Bhopal"),
    "patna": (25.5941, 85.1376, "Patna"),
    "bhubaneswar": (20.2961, 85.8245, "Bhubaneswar"),
    "chandigarh": (30.7333, 76.7794, "Chandigarh"),
    "srinagar": (34.0837, 74.7973, "Srinagar"),
    "guwahati": (26.1445, 91.7362, "Guwahati"),
    "dehradun": (30.3165, 78.0322, "Dehradun"),
    "shimla": (31.1048, 77.1734, "Shimla"),
    "gangtok": (27.3314, 88.6138, "Gangtok"),
    "itanagar": (27.0844, 93.6053, "Itanagar"),
    "kohima": (25.6751, 94.1086, "Kohima"),
    "imphal": (24.8170, 93.9368, "Imphal"),
    "agartala": (23.8315, 91.2868, "Agartala"),
    "shillong": (25.5788, 91.8933, "Shillong"),
    "aizawl": (23.7271, 92.7176, "Aizawl"),
    "ranchi": (23.3441, 85.3096, "Ranchi"),
    "raipur": (21.2514, 81.6296, "Raipur"),
    "panaji": (15.4909, 73.8278, "Panaji"),
    "thiruvananthapuram": (8.5241, 76.9366, "Thiruvananthapuram"),
    # Major cities
    "agra": (27.1767, 78.0081, "Agra"),
    "amritsar": (31.6340, 74.8723, "Amritsar"),
    "varanasi": (25.3176, 82.9739, "Varanasi"),
    "nagpur": (21.1458, 79.0882, "Nagpur"),
    "visakhapatnam": (17.6868, 83.2185, "Visakhapatnam"),
    "indore": (22.7196, 75.8577, "Indore"),
    "kochi": (9.9312, 76.2673, "Kochi"),
    "coimbatore": (11.0168, 76.9558, "Coimbatore"),
    "madurai": (9.9252, 78.1198, "Madurai"),
    "jodhpur": (26.2389, 73.0243, "Jodhpur"),
    "udaipur": (24.5854, 73.7125, "Udaipur"),
    "vadodara": (22.3072, 73.1812, "Vadodara"),
    "nashik": (19.9975, 73.7898, "Nashik"),
    "kanpur": (26.4499, 80.3319, "Kanpur"),
    "allahabad": (25.4358, 81.8463, "Prayagraj"),
    "prayagraj": (25.4358, 81.8463, "Prayagraj"),
    "jammu": (32.7266, 74.8570, "Jammu"),
    "leh": (34.1526, 77.5771, "Leh"),
    "darjeeling": (27.0360, 88.2627, "Darjeeling"),
    "goa": (15.4909, 73.8278, "Goa"),
    "manali": (32.2396, 77.1887, "Manali"),
    "rishikesh": (30.0869, 78.2676, "Rishikesh"),
    "haridwar": (29.9457, 78.1642, "Haridwar"),
    "bodh gaya": (24.6951, 84.9916, "Bodh Gaya"),
    "hampi": (15.3350, 76.4603, "Hampi"),
    # Regions / Areas
    "kashmir": (34.0, 76.0, "Kashmir"),
    "ladakh": (34.0, 77.5, "Ladakh"),
    "himachal": (32.0, 77.0, "Himachal Pradesh"),
    "uttarakhand": (30.0, 79.0, "Uttarakhand"),
    "rajasthan": (27.0, 74.0, "Rajasthan"),
    "gujarat": (22.5, 71.0, "Gujarat"),
    "kerala": (10.0, 76.5, "Kerala"),
    "tamil nadu": (11.0, 78.0, "Tamil Nadu"),
    "karnataka": (15.0, 76.0, "Karnataka"),
    "andhra pradesh": (16.0, 80.0, "Andhra Pradesh"),
    "telangana": (17.5, 79.5, "Telangana"),
    "maharashtra": (19.0, 76.0, "Maharashtra"),
    "west bengal": (22.5, 88.0, "West Bengal"),
    "odisha": (20.5, 84.0, "Odisha"),
    "bihar": (25.5, 85.0, "Bihar"),
    "punjab": (31.0, 75.5, "Punjab"),
    "haryana": (29.5, 76.0, "Haryana"),
    "assam": (26.5, 92.5, "Assam"),
    "meghalaya": (25.5, 91.5, "Meghalaya"),
    "arunachal": (27.5, 94.0, "Arunachal Pradesh"),
    "manipur": (24.8, 93.9, "Manipur"),
    "mizoram": (23.5, 92.8, "Mizoram"),
    "nagaland": (25.5, 94.0, "Nagaland"),
    "tripura": (23.8, 91.5, "Tripura"),
    "sikkim": (27.5, 88.5, "Sikkim"),
    # World locations
    "china": (35.0, 105.0, "China"),
    "pakistan": (30.0, 70.0, "Pakistan"),
    "nepal": (28.0, 84.0, "Nepal"),
    "bangladesh": (24.0, 90.0, "Bangladesh"),
    "sri lanka": (7.5, 80.5, "Sri Lanka"),
    "myanmar": (21.0, 96.0, "Myanmar"),
    "afghanistan": (33.0, 65.0, "Afghanistan"),
    "iran": (32.0, 54.0, "Iran"),
    "middle east": (26.0, 50.0, "Middle East"),
    "ukraine": (49.0, 31.0, "Ukraine"),
    "russia": (60.0, 40.0, "Russia"),
    "moscow": (55.8, 37.6, "Moscow"),
    "usa": (38.0, -97.0, "United States"),
    "united states": (38.0, -97.0, "United States"),
    "america": (38.0, -97.0, "America"),
    "washington": (38.9, -77.0, "Washington DC"),
    "new york": (40.7, -74.0, "New York"),
    "london": (51.5, -0.1, "London"),
    "uk": (55.0, -3.0, "United Kingdom"),
    "britain": (55.0, -3.0, "Britain"),
    "france": (46.6, 2.2, "France"),
    "paris": (48.9, 2.3, "Paris"),
    "germany": (51.2, 10.4, "Germany"),
    "berlin": (52.5, 13.4, "Berlin"),
    "europe": (50.0, 10.0, "Europe"),
    "european union": (50.0, 10.0, "European Union"),
    "eu": (50.0, 10.0, "EU"),
    "italy": (41.9, 12.5, "Italy"),
    "rome": (41.9, 12.5, "Rome"),
    "spain": (40.4, -3.7, "Spain"),
    "madrid": (40.4, -3.7, "Madrid"),
    "japan": (36.2, 138.3, "Japan"),
    "tokyo": (35.7, 139.7, "Tokyo"),
    "south korea": (35.9, 127.8, "South Korea"),
    "seoul": (37.6, 127.0, "Seoul"),
    "north korea": (40.3, 127.5, "North Korea"),
    "australia": (-25.0, 134.0, "Australia"),
    "canada": (56.0, -106.0, "Canada"),
    "brazil": (-14.2, -51.9, "Brazil"),
    "south africa": (-30.5, 25.0, "South Africa"),
    "egypt": (26.8, 30.8, "Egypt"),
    "cairo": (30.0, 31.2, "Cairo"),
    "israel": (31.0, 34.8, "Israel"),
    "jerusalem": (31.8, 35.2, "Jerusalem"),
    "gaza": (31.5, 34.5, "Gaza"),
    "turkey": (39.0, 35.0, "Turkey"),
    "ankara": (39.9, 32.9, "Ankara"),
    "istanbul": (41.0, 29.0, "Istanbul"),
    "syria": (34.8, 39.0, "Syria"),
    "iraq": (33.0, 44.0, "Iraq"),
    "baghdad": (33.3, 44.4, "Baghdad"),
    "yemen": (15.5, 48.5, "Yemen"),
    "saudi arabia": (24.0, 45.0, "Saudi Arabia"),
    "riyadh": (24.6, 46.7, "Riyadh"),
    "uae": (23.4, 53.8, "UAE"),
    "dubai": (25.2, 55.3, "Dubai"),
    "qatar": (25.3, 51.2, "Qatar"),
    "kuwait": (29.3, 47.5, "Kuwait"),
    "oman": (21.0, 57.0, "Oman"),
    "ethiopia": (9.0, 40.0, "Ethiopia"),
    "nigeria": (9.0, 8.0, "Nigeria"),
    "kenya": (-1.3, 36.8, "Kenya"),
    "nairobi": (-1.3, 36.8, "Nairobi"),
    "sudan": (15.5, 30.0, "Sudan"),
    "somalia": (5.0, 46.0, "Somalia"),
    "libya": (26.0, 17.0, "Libya"),
    "algeria": (28.0, 3.0, "Algeria"),
    "morocco": (32.0, -6.0, "Morocco"),
    "indonesia": (-5.0, 120.0, "Indonesia"),
    "jakarta": (-6.2, 106.8, "Jakarta"),
    "philippines": (13.0, 122.0, "Philippines"),
    "thailand": (15.0, 101.0, "Thailand"),
    "vietnam": (16.0, 108.0, "Vietnam"),
    "taiwan": (23.5, 121.0, "Taiwan"),
    "hong kong": (22.3, 114.2, "Hong Kong"),
    "singapore": (1.3, 103.8, "Singapore"),
    "malaysia": (4.2, 101.9, "Malaysia"),
    "kazakhstan": (48.0, 67.0, "Kazakhstan"),
    "africa": (0.0, 20.0, "Africa"),
    "latin america": (-15.0, -60.0, "Latin America"),
    "caribbean": (18.0, -73.0, "Caribbean"),
    "pacific": (0.0, 180.0, "Pacific"),
    "antarctic": (-80.0, 0.0, "Antarctic"),
    "arctic": (85.0, 0.0, "Arctic"),
    "nato": (48.0, 5.0, "NATO"),
    "united nations": (40.7, -74.0, "United Nations"),
    "gaza strip": (31.4, 34.5, "Gaza Strip"),
    "west bank": (31.9, 35.2, "West Bank"),
    "lebanon": (33.9, 35.5, "Lebanon"),
    "beirut": (33.9, 35.5, "Beirut"),
    "jordan": (31.0, 36.0, "Jordan"),
    "amman": (31.9, 35.9, "Amman"),
}


def find_locations(text):
    """Find all locations mentioned in text."""
    text_lower = text.lower()
    found = []
    for name, (lat, lon, display) in sorted(LOCATIONS.items(), key=lambda x: -len(x[0])):
        if name in text_lower:
            found.append((display, lat, lon, name))
    # Deduplicate by proximity
    unique = []
    for f in found:
        is_dup = False
        for u in unique:
            d = math.sqrt((f[1]-u[1])**2 + (f[2]-u[2])**2)
            if d < 2.0:
                is_dup = True
                break
        if not is_dup:
            unique.append(f)
    return unique[:8]  # Max 8 locations per tour


# ── Region Polygons (for dynamic KML shapes) ──
# Each region has a boundary polygon + visual type based on news topic
REGION_POLYGONS = {
    "assam": [(89.5,27.8),(96.0,27.8),(96.0,24.5),(89.5,24.5),(89.5,27.8)],
    "delhi": [(76.8,28.9),(77.4,28.9),(77.4,28.3),(76.8,28.3),(76.8,28.9)],
    "kashmir": [(73.5,37.0),(80.0,37.0),(80.0,33.0),(73.5,33.0),(73.5,37.0)],
    "mumbai": [(72.5,19.5),(73.5,19.5),(73.5,18.7),(72.5,18.7),(72.5,19.5)],
    "kerala": [(74.5,12.5),(77.5,12.5),(77.5,8.0),(74.5,8.0),(74.5,12.5)],
    "gujarat": [(68.0,24.5),(74.5,24.5),(74.5,20.5),(68.0,20.5),(68.0,24.5)],
    # World regions
    "ukraine": [(22.0,52.5),(40.0,52.5),(40.0,44.0),(22.0,44.0),(22.0,52.5)],
    "gaza": [(34.2,31.8),(34.6,31.8),(34.6,31.3),(34.2,31.3),(34.2,31.8)],
    "gaza strip": [(34.2,31.8),(34.6,31.8),(34.6,31.3),(34.2,31.3),(34.2,31.8)],
    "israel": [(34.2,33.5),(35.9,33.5),(35.9,29.5),(34.2,29.5),(34.2,33.5)],
    "west bank": [(34.9,32.5),(35.5,32.5),(35.5,31.4),(34.9,31.4),(34.9,32.5)],
}

# ── Visual Type Selection ──
# Maps article keywords to visual styles (ABGR colors)
VISUAL_TYPES = {
    "flood": {"style": "flood", "fill": "7fff0000", "stroke": "ffff0000"},
    "rain": {"style": "flood", "fill": "7fff0000", "stroke": "ffff0000"},
    "cyclone": {"style": "storm", "fill": "7f00aaff", "stroke": "ff00aaff"},
    "storm": {"style": "storm", "fill": "7f00aaff", "stroke": "ff00aaff"},
    "protest": {"style": "protest", "fill": "7f0088ff", "stroke": "ff0088ff"},
    "protesters": {"style": "protest", "fill": "7f0088ff", "stroke": "ff0088ff"},
    "education": {"style": "protest", "fill": "7f0088ff", "stroke": "ff0088ff"},
    "reform": {"style": "protest", "fill": "7f0088ff", "stroke": "ff0088ff"},
    "sport": {"style": "sport", "fill": "7f00ccff", "stroke": "ff00ccff"},
    "gold": {"style": "sport", "fill": "7f00ccff", "stroke": "ff00ccff"},
    "boxer": {"style": "sport", "fill": "7f00ccff", "stroke": "ff00ccff"},
    "commonwealth": {"style": "sport", "fill": "7f00ccff", "stroke": "ff00ccff"},
    "army": {"style": "military", "fill": "7f00ff00", "stroke": "ff00ff00"},
    "military": {"style": "military", "fill": "7f00ff00", "stroke": "ff00ff00"},
    "election": {"style": "vote", "fill": "7f00ff00", "stroke": "ff00ff00"},
    "earthquake": {"style": "quake", "fill": "7f0000ff", "stroke": "ff0000ff"},
    "fire": {"style": "fire", "fill": "7f0044ff", "stroke": "ff0044ff"},
    "crime": {"style": "crime", "fill": "7f0000ff", "stroke": "ff0000ff"},
}


def detect_visual_type(text):
    """Detect visual style based on article text keywords."""
    text_lower = text.lower()
    for keyword, viz in VISUAL_TYPES.items():
        if keyword in text_lower:
            return viz
    return {"style": "default", "fill": "7f4444ff", "stroke": "ff4444ff"}


def get_region_polygon(name):
    """Get polygon boundary coords for a named region if available."""
    key = name.lower().replace(" ", "_")
    if key in REGION_POLYGONS:
        return REGION_POLYGONS[key]
    for rk, rv in REGION_POLYGONS.items():
        if rk in name.lower() or name.lower() in rk:
            return rv
    return None


def polygon_kml(coords, viz, label=""):
    """Generate a 3D extruded KML polygon from coords + visual style."""
    coord_str = ' '.join(str(lon) + ',' + str(lat) + ',50000' for lon, lat in coords)
    return """
  <Placemark>
    <name></name>
    <styleUrl>#poly_""" + viz["style"] + """</styleUrl>
    <Polygon>
      <extrude>1</extrude>
      <altitudeMode>relativeToGround</altitudeMode>
      <outerBoundaryIs>
        <LinearRing>
          <coordinates>""" + coord_str + """</coordinates>
        </LinearRing>
      </outerBoundaryIs>
    </Polygon>
  </Placemark>"""


def icon_kml(lat, lon, viz, label=""):
    """Generate a KML placemark icon string."""
    cname = viz.get("icon", "blu-circle")
    coords = str(lon) + "," + str(lat) + ",0"
    return """
  <Placemark>
    <name></name>
    <styleUrl>#ico_""" + viz["style"] + """</styleUrl>
    <Point><coordinates>""" + coords + """</coordinates></Point>
  </Placemark>"""
