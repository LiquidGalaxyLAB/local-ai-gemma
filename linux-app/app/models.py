"""Data models + skills.json loader (mirrors the Android app's skill.dart).

The skills.json format is the SAME single source of truth shared with the
Flutter Android app and the KML bakery (bake_config.py).
"""
import json
import os


class Visualization:
    def __init__(self, data: dict):
        self.id = data["id"]
        self.label = data["label"]
        self.desc = data.get("desc", "")
        self.master_kml = data["masterKml"]          # "assets/kml/<skill>/<viz>.kml"
        self.panel_png = data["panelPng"]            # "assets/kml/<skill>/<viz>_panel.png"
        self.panel_kml = data["panelKml"]            # "assets/kml/<skill>/<viz>_panel.kml"
        self.flyto = data.get("flyto", {})
        self.tour = data.get("tour")
        self.no_orbit = data.get("noOrbit", False)

    @property
    def skill_id(self):
        # masterKml path: assets/kml/<skill>/<viz>.kml
        return self.master_kml.split("/")[2]

    @property
    def kml_filename(self):
        return os.path.basename(self.master_kml)      # e.g. tokyo-heat.kml

    @property
    def panel_png_filename(self):
        return os.path.basename(self.panel_png)

    @property
    def panel_kml_filename(self):
        return os.path.basename(self.panel_kml)


class Skill:
    def __init__(self, data: dict):
        self.id = data["id"]
        self.name = data["name"]
        self.tagline = data.get("tagline", "")
        self.icon = data.get("icon", "public")       # Material icon name (mapped in UI)
        self.visualizations = [Visualization(v) for v in data["visualizations"]]


def load_skills(skills_json_path: str) -> list[Skill]:
    with open(skills_json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return [Skill(s) for s in data.get("skills", [])]
