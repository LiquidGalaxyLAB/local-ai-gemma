import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../controllers/app_state.dart';
import '../models/skill.dart';
import '../theme.dart';
import 'settings_screen.dart';
import 'skill_detail_screen.dart';

/// Home: the main screen. Grid of skill cards, a settings gear, a connection
/// indicator, and an always-visible Clear Earth action. When the rig isn't
/// configured yet, a prominent banner guides the user to Settings.
class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  IconData _iconFor(String name) {
    const map = <String, IconData>{
      'wb_sunny': Icons.wb_sunny,
      'flight': Icons.flight,
      'directions_boat': Icons.directions_boat,
      'bolt': Icons.bolt,
      'security': Icons.security,
      'gps_fixed': Icons.gps_fixed,
      'show_chart': Icons.show_chart,
      'pets': Icons.pets,
      'waves': Icons.waves,
      'forest': Icons.forest,
      'assessment': Icons.assessment,
      'donut_large': Icons.donut_large,
      'satellite': Icons.satellite_alt,
      'trending_up': Icons.trending_up,
      'newspaper': Icons.newspaper,
      'public': Icons.public,
      'history_edu': Icons.history_edu,
    };
    return map[name] ?? Icons.public;
  }

  @override
  Widget build(BuildContext context) {
    final state = context.watch<AppState>();
    return Scaffold(
      appBar: AppBar(
        title: const Text('demo app by Nara (Hermes Agent)'),
        leading: _ConnectionStatus(connected: state.connected),
        actions: [
          IconButton(
            tooltip: 'Settings',
            icon: const Icon(Icons.settings),
            onPressed: () => Navigator.of(context).push(
                MaterialPageRoute(builder: (_) => const SettingsScreen())),
          ),
        ],
      ),
      body: Column(
        children: [
          if (!state.hasSettings)
            _NotConfiguredBanner(onConfigure: () => _openSettings(context)),
          Expanded(
            child: _buildBody(context, state),
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: state.busy ? null : state.clearEarth,
        backgroundColor: LgTheme.danger,
        foregroundColor: Colors.white,
        icon: const Icon(Icons.cleaning_services),
        label: const Text('Clear Earth'),
      ),
    );
  }

  void _openSettings(BuildContext context) {
    Navigator.of(context).push(
        MaterialPageRoute(builder: (_) => const SettingsScreen()));
  }

  Widget _buildBody(BuildContext context, AppState state) {
    if (!state.skillsLoaded) {
      return const Center(
          child: CircularProgressIndicator(color: LgTheme.accent));
    }
    if (state.skills.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.error_outline, color: LgTheme.warn, size: 40),
            const SizedBox(height: 12),
            const Text('Could not load the skill catalog.',
                style: TextStyle(color: LgTheme.textDim)),
            const SizedBox(height: 12),
            TextButton.icon(
              onPressed: () => context.read<AppState>().reloadSkills(),
              icon: const Icon(Icons.refresh),
              label: const Text('Retry'),
            ),
          ],
        ),
      );
    }
    return GridView.builder(
      padding: const EdgeInsets.all(16),
      gridDelegate: const SliverGridDelegateWithMaxCrossAxisExtent(
        maxCrossAxisExtent: 240,
        mainAxisSpacing: 12,
        crossAxisSpacing: 12,
        childAspectRatio: 0.9,
      ),
      itemCount: state.skills.length,
      itemBuilder: (context, i) =>
          _SkillCard(skill: state.skills[i], icon: _iconFor(state.skills[i].icon)),
    );
  }
}

class _NotConfiguredBanner extends StatelessWidget {
  final VoidCallback onConfigure;
  const _NotConfiguredBanner({required this.onConfigure});

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.fromLTRB(16, 12, 16, 0),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: LgTheme.warn.withValues(alpha: 0.10),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: LgTheme.warn.withValues(alpha: 0.4)),
      ),
      child: Row(
        children: [
          const Icon(Icons.info_outline, color: LgTheme.warn),
          const SizedBox(width: 10),
          const Expanded(
            child: Text(
              'Not connected yet — configure the rig to start.',
              style: TextStyle(color: LgTheme.text, fontSize: 13),
            ),
          ),
          TextButton(
            onPressed: onConfigure,
            child: const Text('Configure'),
          ),
        ],
      ),
    );
  }
}

class _ConnectionStatus extends StatelessWidget {
  final bool connected;
  const _ConnectionStatus({required this.connected});

  @override
  Widget build(BuildContext context) {
    final color = connected ? LgTheme.ok : LgTheme.warn;
    final label = connected ? 'Connected' : 'Offline';
    return Center(
      child: Container(
        margin: const EdgeInsets.only(left: 12),
        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
        decoration: BoxDecoration(
          color: color.withValues(alpha: 0.15),
          borderRadius: BorderRadius.circular(20),
          border: Border.all(color: color.withValues(alpha: 0.5)),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              width: 8,
              height: 8,
              decoration: BoxDecoration(shape: BoxShape.circle, color: color),
            ),
            const SizedBox(width: 6),
            Text(label,
                style: TextStyle(
                    color: color, fontSize: 12, fontWeight: FontWeight.w700)),
          ],
        ),
      ),
    );
  }
}

class _SkillCard extends StatelessWidget {
  final Skill skill;
  final IconData icon;
  const _SkillCard({required this.skill, required this.icon});

  @override
  Widget build(BuildContext context) {
    return Card(
      clipBehavior: Clip.antiAlias,
      child: InkWell(
        onTap: () => Navigator.of(context).push(MaterialPageRoute(
            builder: (_) => SkillDetailScreen(skill: skill))),
        child: Padding(
          padding: const EdgeInsets.all(14),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Icon(icon, size: 34, color: LgTheme.accent),
              const Spacer(),
              Text(skill.name,
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                  style: const TextStyle(
                      fontWeight: FontWeight.w700, color: LgTheme.text)),
              const SizedBox(height: 4),
              Text(skill.tagline,
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                  style: const TextStyle(
                      fontSize: 12, color: LgTheme.textDim)),
              const SizedBox(height: 4),
              Text('${skill.visualizations.length} visualizations',
                  style: const TextStyle(
                      fontSize: 11, color: LgTheme.accentDark)),
            ],
          ),
        ),
      ),
    );
  }
}
