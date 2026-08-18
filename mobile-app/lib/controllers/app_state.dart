import 'package:flutter/foundation.dart';
import 'package:flutter/services.dart' show rootBundle;
import 'package:shared_preferences/shared_preferences.dart';

import '../models/skill.dart';
import '../services/lg_service.dart';
import '../services/orbit_service.dart';

/// Application state: persisted settings, the skill catalog, the live LG
/// connection, and the orbit controller. Exposed via Provider.
class AppState extends ChangeNotifier {
  final LgService lg = LgService();
  late final OrbitService orbit = OrbitService(lg);

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
  bool orbiting = false;
  String? lastMessage;
  bool lastMessageIsError = false;

  Future<void> init() async {
    await _loadSettings();
    await _loadSkills();
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

  Future<void> resendLogo() async {
    // Convenience: clear then re-send, for live demo recovery.
    await showLogo();
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

  // ------------------------------------------------------------- orbit
  Future<void> startOrbit(Map<String, dynamic> flyto) async {
    if (!connected) await _reconnect();
    if (!connected) return;
    try {
      final ok = await orbit.start(flyto);
      orbiting = ok;
      if (ok) {
        _report('Orbit started');
      } else {
        _report('Orbit could not start (already orbiting?)', error: true);
      }
    } catch (e) {
      _report('Orbit error: ${_friendly(e)}', error: true);
    }
    notifyListeners();
  }

  Future<void> stopOrbit() async {
    await orbit.stop();
    orbiting = false;
    _report('Orbit stopped');
    notifyListeners();
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
    orbit.dispose();
    lg.disconnect();
    super.dispose();
  }
}
