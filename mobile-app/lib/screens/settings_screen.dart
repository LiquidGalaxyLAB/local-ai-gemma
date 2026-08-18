import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../controllers/app_state.dart';
import '../theme.dart';

/// Settings / connection screen — LG-conventional fields (master IP, SSH
/// username, password, port, number of rigs), a test-connection action, and an
/// Advanced section for relaunch / reboot. Reached from the home gear icon;
/// the back arrow returns to Home.
class SettingsScreen extends StatefulWidget {
  const SettingsScreen({super.key});

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  final _formKey = GlobalKey<FormState>();
  late final TextEditingController _host;
  late final TextEditingController _user;
  late final TextEditingController _pass;
  late final TextEditingController _port;
  late int _screens;

  @override
  void initState() {
    super.initState();
    final s = context.read<AppState>();
    _host = TextEditingController(text: s.host);
    _user = TextEditingController(text: s.username);
    _pass = TextEditingController(text: s.password);
    _port = TextEditingController(text: s.port);
    _screens = s.screenCount;
  }

  @override
  void dispose() {
    _host.dispose();
    _user.dispose();
    _pass.dispose();
    _port.dispose();
    super.dispose();
  }

  void _save() {
    if (!_formKey.currentState!.validate()) return;
    final s = context.read<AppState>();
    s.host = _host.text.trim();
    s.username = _user.text.trim();
    s.password = _pass.text;
    s.port = _port.text.trim();
    s.screens = '$_screens';
    s.saveSettings();
    ScaffoldMessenger.of(context)
        .showSnackBar(const SnackBar(content: Text('Settings saved')));
  }

  Future<void> _test() async {
    _save();
    if (!mounted) return;
    final ok = await context.read<AppState>().testConnection();
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(SnackBar(
      content: Text(ok ? 'Connected to the rig' : 'Connection failed'),
      backgroundColor: ok ? LgTheme.ok : LgTheme.danger,
    ));
  }

  void _confirm(String title, String body, VoidCallback action) {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: LgTheme.surface,
        title: Text(title, style: const TextStyle(color: LgTheme.text)),
        content: Text(body, style: const TextStyle(color: LgTheme.textDim)),
        actions: [
          TextButton(
              onPressed: () => Navigator.pop(ctx),
              child: const Text('Cancel', style: TextStyle(color: LgTheme.textDim))),
          TextButton(
              onPressed: () {
                Navigator.pop(ctx);
                action();
              },
              child: const Text('Confirm', style: TextStyle(color: LgTheme.danger))),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final state = context.watch<AppState>();
    return Scaffold(
      appBar: AppBar(title: const Text('Settings')),
      body: Form(
        key: _formKey,
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            TextFormField(
              controller: _host,
              decoration: const InputDecoration(
                  labelText: 'Master IP address', hintText: 'e.g. 192.168.1.12'),
              keyboardType: TextInputType.number,
              validator: (v) =>
                  (v == null || v.trim().isEmpty) ? 'Required' : null,
            ),
            const SizedBox(height: 12),
            TextFormField(
              controller: _user,
              decoration: const InputDecoration(labelText: 'SSH username'),
            ),
            const SizedBox(height: 12),
            TextFormField(
              controller: _pass,
              obscureText: true,
              decoration: const InputDecoration(labelText: 'SSH password'),
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                Expanded(
                  child: TextFormField(
                    controller: _port,
                    decoration: const InputDecoration(labelText: 'SSH port'),
                    keyboardType: TextInputType.number,
                    validator: (v) {
                      final p = int.tryParse(v ?? '');
                      return (p == null || p < 1 || p > 65535)
                          ? 'Invalid port'
                          : null;
                    },
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: DropdownButtonFormField<int>(
                    initialValue: _screens,
                    decoration:
                        const InputDecoration(labelText: 'Number of screens'),
                    items: [
                      for (var n = 2; n <= 9; n++)
                        DropdownMenuItem(value: n, child: Text('$n'))
                    ],
                    onChanged: (v) => setState(() => _screens = v ?? 3),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 20),
            Row(
              children: [
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: state.busy ? null : _test,
                    icon: const Icon(Icons.wifi_tethering),
                    label: const Text('Test connection'),
                  ),
                ),
                const SizedBox(width: 12),
                OutlinedButton(
                  onPressed: _save,
                  child: const Text('Save'),
                ),
              ],
            ),
            const SizedBox(height: 24),
            const Divider(),
            const Text('Advanced',
                style: TextStyle(
                    color: LgTheme.textDim, fontWeight: FontWeight.w600)),
            const SizedBox(height: 8),
            ListTile(
              leading:
                  const Icon(Icons.branding_watermark, color: LgTheme.accent),
              title: const Text('Show logo', style: TextStyle(color: LgTheme.text)),
              subtitle: Text('Leftmost screen (${state.leftmostScreen})',
                  style: const TextStyle(color: LgTheme.textDim, fontSize: 12)),
              onTap: state.busy ? null : () => state.showLogo(),
            ),
            ListTile(
              leading: const Icon(Icons.hide_image, color: LgTheme.textDim),
              title: const Text('Clear logo', style: TextStyle(color: LgTheme.text)),
              subtitle: const Text('Remove the logo from the leftmost screen',
                  style: TextStyle(color: LgTheme.textDim, fontSize: 12)),
              onTap: state.busy ? null : () => state.clearLogo(),
            ),
            ListTile(
              leading: const Icon(Icons.refresh, color: LgTheme.warn),
              title:
                  const Text('Relaunch Earth', style: TextStyle(color: LgTheme.text)),
              subtitle: const Text('Restart the display manager on all screens',
                  style: TextStyle(color: LgTheme.textDim, fontSize: 12)),
              onTap: state.busy
                  ? null
                  : () => _confirm(
                      'Relaunch Earth?',
                      'This restarts Earth on all screens.',
                      state.relaunchRig),
            ),
            ListTile(
              leading: const Icon(Icons.restart_alt, color: LgTheme.danger),
              title:
                  const Text('Reboot rig', style: TextStyle(color: LgTheme.text)),
              subtitle: const Text('Reboots every screen — takes a few minutes',
                  style: TextStyle(color: LgTheme.textDim, fontSize: 12)),
              onTap: state.busy
                  ? null
                  : () => _confirm(
                      'Reboot the rig?',
                      'All screens will reboot. This cannot be undone remotely.',
                      state.rebootRig),
            ),
          ],
        ),
      ),
    );
  }
}
