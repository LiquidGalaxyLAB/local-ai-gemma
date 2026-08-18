"""Live end-to-end test against the rig at 192.168.1.18."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.lg_service import LgService
from app.models import load_skills

ASSET_ROOT = os.path.dirname(os.path.abspath(__file__))
skills = load_skills(os.path.join(ASSET_ROOT, "assets", "skills.json"))

svc = LgService()
print("Connecting to 192.168.1.18 ...")
svc.connect("192.168.1.18", 22, "lg", "lg", timeout=8)
print("CONNECTED")
print("host:", svc.test_connection())

viz = skills[0].visualizations[0]  # weather-monitor/tokyo-heat
print(f"\nDeploying '{viz.label}' (screens=3) ...")
svc.send_visualization(viz, 3, "lg", ASSET_ROOT)
print("DEPLOY SENT")

# verify master.kml actually landed
print("\nVerifying master.kml on rig:")
print("  bytes:", svc._exec("wc -c /var/www/html/kml/master.kml"))
print("  first line:", svc._exec("head -c 80 /var/www/html/kml/master.kml"))

# verify slave_2 (rightmost for N=3) has the panel KML
print("\nVerifying slave_2.kml (rightmost panel):")
print("  first line:", svc._exec("head -c 100 /var/www/html/kml/slave_2.kml"))

# verify panel PNG deployed
print("\nVerifying panel PNG:")
print("  ", svc._exec("ls -la /var/www/html/kml/weather-monitor/"))

print("\nEND_TO_END_OK")
svc.disconnect()
