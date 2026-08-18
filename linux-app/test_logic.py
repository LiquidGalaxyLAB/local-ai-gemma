"""Offline validation: capture the exact SSH commands the service would send,
verifying the LG protocol (flyto, deploy paths, screen formulas, sudo cp)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.lg_service import LgService
from app.models import load_skills

captured = {"exec": [], "uploads": {}}

# monkeypatch _exec and _upload to capture instead of hitting SSH
def fake_exec(self, cmd):
    captured["exec"].append(cmd)
    return "ok"

def fake_upload(self, path, data):
    captured["uploads"][path] = data

LgService._exec = fake_exec
LgService._upload = fake_upload

skills = load_skills(os.path.join(os.path.dirname(
    os.path.abspath(__file__)), "assets", "skills.json"))

svc = LgService()
viz = skills[0].visualizations[0]   # weather-monitor/tokyo-heat

asset_root = os.path.dirname(os.path.abspath(__file__))  # bundle root

# 1. fly_to
svc.fly_to(viz.flyto)
print("FLYTO:", captured["exec"][-1])

# 2. send_visualization (screens=3 -> rightmost=2)
captured["exec"].clear(); captured["uploads"].clear()
svc.send_visualization(viz, screens=3, password="lg", asset_root=asset_root)
print("\n--- deploy exec commands ---")
for c in captured["exec"]:
    print("  ", c[:120])
print("\n--- uploads ---")
for p in captured["uploads"]:
    print(f"  {p}  ({len(captured['uploads'][p])} bytes)")

# 3. clear_earth
captured["exec"].clear()
svc.clear_earth(screens=3, password="lg")
print("\n--- clear exec ---")
for c in captured["exec"]:
    print("  ", c[:140])

# 4. show_logo (screens=3 -> leftmost=3)
captured["exec"].clear()
svc.show_logo(screens=3, password="lg")
print("\n--- logo exec ---")
for c in captured["exec"]:
    print("  ", c[:140])

# 5. screen formula check
for n in (3, 5, 7):
    print(f"\nscreens={n}: rightmost={n//2+1}, leftmost={n//2+2}")

print("\nVALIDATION_DONE")
