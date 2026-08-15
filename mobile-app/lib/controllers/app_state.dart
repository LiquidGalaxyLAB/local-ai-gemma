import 'package:flutter/foundation.dart';
import 'package:flutter/services.dart' show rootBundle;
import 'package:shared_preferences/shared_preferences.dart';

import '../models/skill.dart';
import '../services/lg_service.dart';

/// Application state: persisted settings, the skill catalog, and the live
/// LG connection. Exposed to the widget tree via Provider.
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

  int get rightmostScreen => screenCount ~/ 2 + 1;

  int get leftmostScreen => screenCount ~/ 2 + 2;

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
      await lg.sendVisualization(
        skillId: skill.id,
        viz: VisualizationRef(
          id: viz.id,
          masterKml: viz.masterKml,
          panelPng: viz.panelPng,
          panelKml: viz.panelKml,
          flyto: viz.flyto,
          tour: viz.tour,
        ),
        screens: screenCount,
        password: password,
      );
      _report('"${viz.label}" is live on the rig');
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
      await lg.showLogo(screens: screenCount, password: password);
      _report('Logo shown on leftmost screen');
    } catch (e) {
      _report('Logo failed: ${_friendly(e)}', error: true);
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
}
