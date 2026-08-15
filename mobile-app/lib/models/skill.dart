import 'dart:convert';

/// A single pre-baked visualization within a skill.
class Visualization {
  final String id;
  final String label;
  final String desc;
  final String masterKml;
  final String panelPng;
  final String panelKml;
  final Map<String, dynamic> flyto;
  final String? tour;

  const Visualization({
    required this.id,
    required this.label,
    required this.desc,
    required this.masterKml,
    required this.panelPng,
    required this.panelKml,
    required this.flyto,
    this.tour,
  });

  factory Visualization.fromJson(Map<String, dynamic> j) => Visualization(
        id: j['id'] as String,
        label: j['label'] as String,
        desc: (j['desc'] ?? '') as String,
        masterKml: j['masterKml'] as String,
        panelPng: j['panelPng'] as String,
        panelKml: j['panelKml'] as String,
        flyto: (j['flyto'] as Map).cast<String, dynamic>(),
        tour: j['tour'] as String?,
      );
}

/// A use-case skill holding 2-3 fixed visualizations.
class Skill {
  final String id;
  final String name;
  final String tagline;
  final String icon; // Material icon name
  final List<Visualization> visualizations;

  const Skill({
    required this.id,
    required this.name,
    required this.tagline,
    required this.icon,
    required this.visualizations,
  });

  factory Skill.fromJson(Map<String, dynamic> j) => Skill(
        id: j['id'] as String,
        name: j['name'] as String,
        tagline: (j['tagline'] ?? '') as String,
        icon: (j['icon'] ?? 'public') as String,
        visualizations: (j['visualizations'] as List)
            .map((v) => Visualization.fromJson(v as Map<String, dynamic>))
            .toList(),
      );
}

/// Loads the bundled skills.json (single source of truth shared with the
/// KML bakery) into typed models.
Future<List<Skill>> loadSkills(String assetData) async {
  final decoded = json.decode(assetData) as Map<String, dynamic>;
  final list = (decoded['skills'] as List)
      .map((s) => Skill.fromJson(s as Map<String, dynamic>))
      .toList();
  return list;
}
