import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../controllers/app_state.dart';
import '../models/skill.dart';
import '../theme.dart';
import 'settings_screen.dart';

/// Skill detail: the 2-3 fixed visualizations as tappable tiles.
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
              onTap: () => state.sendVisualization(skill, viz),
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
  final VoidCallback onTap;
  const _VizTile({
    required this.skill,
    required this.viz,
    required this.busy,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      child: ListTile(
        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        leading: Icon(
          viz.tour != null ? Icons.play_circle_outline : Icons.terrain,
          size: 32,
          color: viz.tour != null ? LgTheme.ok : LgTheme.accent,
        ),
        title: Text(viz.label,
            style: const TextStyle(fontWeight: FontWeight.w600, color: LgTheme.text)),
        subtitle: Text(viz.desc, style: const TextStyle(color: LgTheme.textDim)),
        trailing: busy
            ? const SizedBox(
                width: 20, height: 20, child: CircularProgressIndicator(strokeWidth: 2))
            : const Icon(Icons.play_arrow, color: LgTheme.accentDark),
        onTap: busy ? null : onTap,
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
        color: connected ? LgTheme.ok.withValues(alpha: 0.08) : LgTheme.warn.withValues(alpha: 0.08),
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
                  ? 'Connected — tap a visualization to deploy it.'
                  : 'Not connected — tapping will auto-connect using your saved settings.',
              style: const TextStyle(color: LgTheme.textDim, fontSize: 13),
            ),
          ),
        ],
      ),
    );
  }
}
