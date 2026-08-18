import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../controllers/app_state.dart';
import '../models/skill.dart';
import '../theme.dart';
import 'settings_screen.dart';

/// Skill detail: the 2-3 fixed visualizations as tappable tiles, each with a
/// Deploy action and a generic Orbit action (available for every visualization).
class SkillDetailScreen extends StatelessWidget {
  final Skill skill;
  const SkillDetailScreen({super.key, required this.skill});

  @override
  Widget build(BuildContext context) {
    final state = context.watch<AppState>();
    return Scaffold(
      appBar: AppBar(
        title: Text(skill.name),
        actions: [
          IconButton(
            tooltip: 'Settings',
            icon: const Icon(Icons.settings),
            onPressed: () => Navigator.of(context).push(MaterialPageRoute(
                builder: (_) => const SettingsScreen())),
          ),
        ],
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          Text(skill.tagline,
              style: const TextStyle(color: LgTheme.textDim, fontSize: 15)),
          const SizedBox(height: 16),
          for (final viz in skill.visualizations)
            _VizTile(
              skill: skill,
              viz: viz,
              busy: state.busy,
              orbiting: state.orbiting,
              onDeploy: () => state.sendVisualization(skill, viz),
              onOrbit: () =>
                  state.startOrbit(viz.flyto),
            ),
          if (state.orbiting)
            Padding(
              padding: const EdgeInsets.only(top: 12),
              child: ElevatedButton.icon(
                onPressed: state.stopOrbit,
                icon: const Icon(Icons.stop_circle_outlined),
                label: const Text('Stop orbit'),
              ),
            ),
          const SizedBox(height: 16),
          _ConnectionHint(connected: state.connected),
        ],
      ),
    );
  }
}

class _VizTile extends StatelessWidget {
  final Skill skill;
  final Visualization viz;
  final bool busy;
  final bool orbiting;
  final VoidCallback onDeploy;
  final VoidCallback onOrbit;
  const _VizTile({
    required this.skill,
    required this.viz,
    required this.busy,
    required this.orbiting,
    required this.onDeploy,
    required this.onOrbit,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(
                  viz.tour != null ? Icons.play_circle_outline : Icons.terrain,
                  size: 32,
                  color: viz.tour != null ? LgTheme.ok : LgTheme.accent,
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(viz.label,
                          style: const TextStyle(
                              fontWeight: FontWeight.w600, color: LgTheme.text)),
                      Text(viz.desc,
                          style: const TextStyle(color: LgTheme.textDim, fontSize: 13)),
                    ],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                Expanded(
                  child: FilledButton.icon(
                    onPressed: busy ? null : onDeploy,
                    icon: const Icon(Icons.play_arrow),
                    label: const Text('Deploy'),
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: busy ? null : onOrbit,
                    icon: Icon(orbiting ? Icons.rotate_left : Icons.donut_large),
                    label: Text(orbiting ? 'Orbiting…' : 'Orbit'),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

class _ConnectionHint extends StatelessWidget {
  final bool connected;
  const _ConnectionHint({required this.connected});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: connected
            ? LgTheme.ok.withValues(alpha: 0.08)
            : LgTheme.warn.withValues(alpha: 0.08),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        children: [
          Icon(connected ? Icons.check_circle : Icons.info_outline,
              color: connected ? LgTheme.ok : LgTheme.warn),
          const SizedBox(width: 10),
          Expanded(
            child: Text(
              connected
                  ? 'Connected — deploy a visualization or start an orbit.'
                  : 'Not connected — tapping will auto-connect using your saved settings.',
              style: const TextStyle(color: LgTheme.textDim, fontSize: 13),
            ),
          ),
        ],
      ),
    );
  }
}
