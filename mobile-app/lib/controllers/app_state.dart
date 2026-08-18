import 'dart:async';

import 'package:flutter/foundation.dart';
import 'package:flutter/services.dart' show rootBundle;
import 'package:shared_preferences/shared_preferences.dart';

import '../models/skill.dart';
import '../services/lg_service.dart';

/// Application state: persisted settings, the skill catalog, and the live LG
/// connection. Exposed via Provider.
///
/// Maintains a live connection status by periodically probing the rig with a
/// lightweight SSH command; the `connected` flag updates in near-real-time.
class AppState extends ChangeNotifier {
  final LgService lg = LgService();

  // persisted settings (LG-conventional keys)
  String host = '';
  String username = 'lg';
  String password = 'lg';
  String port = '22';
  String screens = '3';

  List<Skill> skills = [];
  bool skillsLoaded = false;
  bool busy = false;
  bool connected = false;
  String? lastMessage;
  bool lastMessageIsError = false;

  // live connection monitoring
  Timer? _statusTimer;
  bool _probeInFlight = false;

  Future<void> init() async {
    await _loadSettings();
    await _loadSkills();
    _startStatusMonitor();
  }

  // ------------------------------------------------------------- live status
  void _startStatusMonitor() {
    _statusTimer?.cancel();
    _statusTimer = Timer.periodic(const Duration(seconds: 5), (_) {
      _probeConnection();
    });
  }

  /// Lightweight liveness probe — only runs when we believe we're connected,
  /// and only when the settings are present. Flips `connected` off if the rig
  /// stops answering, so the UI always reflects the true state.
  Future<void> _probeConnection() async {
    if (_probeInFlight || busy) return;
    if (host.trim().isEmpty) return;
    _probeInFlight = true;
    try {
      if (connected) {
        // verify the existing connection is still alive
        final ok = await lg.ping();
        if (!ok) {
          connected = false;
          notifyListeners();
        }
      }
      // if not connected, don't auto-reconnect from the timer (avoid surprise
      // SSH churn); the user reconnects via Settings/Test or an action.
    } catch (_) {
      if (connected) {
        connected = false;
        notifyListeners();
      }
    } finally {
      _probeInFlight = false;
    }
  }

  // ------------------------------------------------------------- settings
  Future<void> _loadSettings() async {
    final p = await SharedPreferences.getInstance();
    host = p.getString('ip') ?? '';
    username = p.getString('username') ?? 'lg';
    password = p.getString('pass') ?? 'lg';
    port = p.getString('port') ?? '22';
    screens = p.getString('number_of_rigs') ?? '3';
    notifyListeners();
  }

  Future<void> saveSettings() async {
    final p = await SharedPreferences.getInstance();
    await p.setString('ip', host);
    await p.setString('username', username);
    await p.setString('pass', password);
    await p.setString('port', port);
    await p.setString('number_of_rigs', screens);
    notifyListeners();
  }

  bool get hasSettings => host.trim().isNotEmpty;

  int get screenCount => int.tryParse(screens) ?? 3;

  int get rightmostScreen => LgService.rightmostScreen(screenCount);

  int get leftmostScreen => LgService.leftmostScreen(screenCount);

  // ------------------------------------------------------------- skills
  Future<void> _loadSkills() async {
    try {
      final data = await rootBundle.loadString('assets/skills.json');
      skills = await loadSkills(data);
      skillsLoaded = true;
      notifyListeners();
    } catch (e) {
      lastMessage = 'Could not load skill catalog: $e';
      lastMessageIsError = true;
      notifyListeners();
    }
  }

  Future<void> reloadSkills() async {
    skillsLoaded = false;
    notifyListeners();
    await _loadSkills();
  }

  // ------------------------------------------------------------- actions
  void _setBusy(bool b) {
    busy = b;
    notifyListeners();
  }

  void _report(String msg, {bool error = false}) {
    lastMessage = msg;
    lastMessageIsError = error;
    notifyListeners();
  }

  Future<bool> testConnection() async {
    if (!_validateSettings()) return false;
    _setBusy(true);
    try {
      await lg.connect(
        host: host.trim(),
        port: int.parse(port.trim()),
        username: username.trim(),
        password: password,
      );
      final out = await lg.testConnection();
      connected = true;
      _report('Connected: $out');
      // Auto-show the logo on the leftmost screen after connecting (matches
      // geosaurio-lg, which sends the logo as part of connection init).
      try {
        await lg.sendLogo(screens: screenCount, password: password);
      } catch (_) {
        // non-fatal — connection succeeded even if the logo push hiccuped
      }
      return true;
    } catch (e) {
      connected = false;
      _report('Connection failed: ${_friendly(e)}', error: true);
      return false;
    } finally {
      _setBusy(false);
    }
  }

  Future<void> disconnect() async {
    connected = false;
    notifyListeners();
    lg.disconnect();
  }

  Future<void> sendVisualization(Skill skill, Visualization viz) async {
    if (!connected) await _reconnect();
    if (!connected) return;
    _setBusy(true);
    try {
      final results = await lg.sendVisualization(
        skillId: skill.id,
        viz: VisualizationRef(
          id: viz.id,
          label: viz.label,
          masterKml: viz.masterKml,
          panelPng: viz.panelPng,
          panelKml: viz.panelKml,
          flyto: viz.flyto,
          tour: viz.tour,
        ),
        screens: screenCount,
        password: password,
      );
      final failed = results.entries.where((e) => !e.value).map((e) => e.key);
      if (failed.isEmpty) {
        _report('"${viz.label}" is live on the rig');
      } else {
        _report('"${viz.label}" partially failed: ${failed.join(', ')}',
            error: true);
      }
    } catch (e) {
      connected = false;
      _report('Deploy failed: ${_friendly(e)}', error: true);
    } finally {
      _setBusy(false);
    }
  }

  Future<void> clearEarth() async {
    if (!connected) await _reconnect();
    if (!connected) return;
    _setBusy(true);
    try {
      await lg.clearEarth(screens: screenCount, password: password);
      _report('Earth cleared');
    } catch (e) {
      _report('Clear failed: ${_friendly(e)}', error: true);
    } finally {
      _setBusy(false);
    }
  }

  Future<void> showLogo() async {
    if (!connected) await _reconnect();
    if (!connected) return;
    _setBusy(true);
    try {
      final r = await lg.sendLogo(screens: screenCount, password: password);
      final failed = r.entries.where((e) => !e.value).map((e) => e.key);
      _report(failed.isEmpty
          ? 'Logo shown on leftmost screen'
          : 'Logo partially failed: ${failed.join(', ')}',
          error: failed.isNotEmpty);
    } catch (e) {
      _report('Logo failed: ${_friendly(e)}', error: true);
    } finally {
      _setBusy(false);
    }
  }

  Future<void> clearLogo() async {
    if (!connected) await _reconnect();
    if (!connected) return;
    _setBusy(true);
    try {
      await lg.clearLogo(screens: screenCount, password: password);
      _report('Logo removed');
    } catch (e) {
      _report('Clear logo failed: ${_friendly(e)}', error: true);
    } finally {
      _setBusy(false);
    }
  }

  Future<void> relaunchRig() async {
    if (!connected) await _reconnect();
    if (!connected) return;
    _setBusy(true);
    try {
      await lg.relaunchRig(screens: screenCount, password: password);
      _report('Relaunch command sent');
    } catch (e) {
      _report('Relaunch failed: ${_friendly(e)}', error: true);
    } finally {
      _setBusy(false);
    }
  }

  Future<void> rebootRig() async {
    if (!connected) await _reconnect();
    if (!connected) return;
    _setBusy(true);
    try {
      await lg.rebootRig(screens: screenCount, password: password);
      connected = false;
      _report('Reboot command sent — rig is restarting');
    } catch (e) {
      _report('Reboot failed: ${_friendly(e)}', error: true);
    } finally {
      _setBusy(false);
    }
  }

  Future<void> _reconnect() async {
    await testConnection();
  }

  bool _validateSettings() {
    if (host.trim().isEmpty) {
      _report('Enter the rig master IP in Settings first', error: true);
      return false;
    }
    final p = int.tryParse(port.trim());
    if (p == null || p < 1 || p > 65535) {
      _report('SSH port must be a number 1-65535', error: true);
      return false;
    }
    return true;
  }

  String _friendly(Object e) {
    final s = e.toString();
    if (s.contains('SocketException') || s.contains('Connection refused')) {
      return 'cannot reach the rig at $host:$port';
    }
    if (s.contains('authentication') ||
        s.contains('Auth') ||
        s.contains('password')) {
      return 'login failed — check username/password';
    }
    return s.length > 120 ? s.substring(0, 120) : s;
  }

  @override
  void dispose() {
    _statusTimer?.cancel();
    lg.disconnect();
    super.dispose();
  }
}
