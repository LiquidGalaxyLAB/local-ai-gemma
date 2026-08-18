import 'dart:convert';
import 'dart:typed_data';

import 'package:dartssh2/dartssh2.dart';
import 'package:flutter/services.dart' show rootBundle;

/// Liquid Galaxy control service.
///
/// Single SSH/SFTP connection owner. All other operations (orbit, overlay,
/// navigation) call through this class — they never open their own
/// connection. Mirrors the geosaurio-lg architecture.
///
/// Conventions (verified against geosaurio-lg + La-Palma tracker):
///   - connect via SSHSocket + SSHClient (username + password)
///   - fly camera via   echo "flytoview=<LookAt>" > /tmp/query.txt
///   - deploy files via SFTP upload, then sudo cp into /var/www/html/kml/
///   - rightmost screen = N ~/ 2 + 1   (balloons / text panels)
///   - leftmost  screen = N ~/ 2 + 2   (logo)
///   - clear via exittour=true + blank KMLs
class LgService {
  SSHClient? _client;

  /// Base URL used by ScreenOverlay <href>s to reference images/KMLs served
  /// by Apache on the master. Defaults to the LG convention; overridable.
  String baseUrl = 'http://lg1:81';

  bool get isConnected => _client != null;

  // ------------------------------------------------------------- connection
  Future<void> connect({
    required String host,
    required int port,
    required String username,
    required String password,
  }) async {
    disconnect();
    final socket = await SSHSocket.connect(host, port,
        timeout: const Duration(seconds: 8));
    final client = SSHClient(
      socket,
      username: username,
      onPasswordRequest: () => password,
      keepAliveInterval: const Duration(seconds: 10),
    );
    _client = client;
  }

  void disconnect() {
    try {
      _client?.close();
    } catch (_) {}
    _client = null;
  }

  Future<String> testConnection() async {
    final out = await _exec('echo LG_OK && hostname && uname -m');
    return out;
  }

  /// Lightweight liveness probe for the live connection status monitor.
  /// Returns true if the rig answers, false otherwise (never throws).
  Future<bool> ping() async {
    final c = _client;
    if (c == null) return false;
    try {
      await c.run('true');
      return true;
    } catch (_) {
      return false;
    }
  }

  // ------------------------------------------------------------- primitives
  Future<String> _exec(String command) async {
    final c = _client;
    if (c == null) throw LgCommandException('Not connected', command);
    final result = await c.runWithResult(command);
    if (result.exitCode != null && result.exitCode != 0) {
      final err = utf8.decode(result.stderr).trim();
      if (err.isNotEmpty) {
        throw LgCommandException(err, command);
      }
    }
    return utf8.decode(result.stdout).trim();
  }

  /// Run a command with retry-with-backoff. Retries transient SSH/SFTP
  /// failures so a single dropped command during a live demo doesn't
  /// silently leave a screen stale.
  Future<String> execWithRetry(
    String command, {
    int maxAttempts = 3,
    Duration baseDelay = const Duration(milliseconds: 400),
  }) async {
    Object? lastError;
    for (var attempt = 1; attempt <= maxAttempts; attempt++) {
      try {
        return await _exec(command);
      } catch (e) {
        lastError = e;
        if (attempt < maxAttempts) {
          await Future.delayed(baseDelay * attempt);
        }
      }
    }
    throw LgCommandException(
        'Failed after $maxAttempts attempts: $lastError', command);
  }

  Future<void> _upload(String remotePath, Uint8List bytes) async {
    final c = _client;
    if (c == null) throw LgCommandException('Not connected', 'sftp open');
    final sftp = await c.sftp();
    try {
      final file = await sftp.open(remotePath,
          mode: SftpFileOpenMode.create |
              SftpFileOpenMode.truncate |
              SftpFileOpenMode.write);
      try {
        await file.write(Stream.value(bytes));
      } finally {
        await file.close();
      }
    } finally {
      await sftp.close();
    }
  }

  /// Upload raw bytes to the Apache kml directory via a temp home file +
  /// sudo-cp (the standard LG pattern; sudo is required because
  /// /var/www/html/kml is root-owned). Returns true on success, false on any
  /// error (does not throw) so callers can surface per-screen failures.
  Future<bool> pushToKml({
    required Uint8List bytes,
    required String remoteTmp,
    required String target, // full path under /var/www/html/
    required String password,
    String? mkdirTarget,
    int attempts = 3,
  }) async {
    try {
      await _upload(remoteTmp, bytes);
    } catch (_) {
      return false;
    }
    final mkdir = mkdirTarget != null
        ? "echo '$password' | sudo -S mkdir -p $mkdirTarget && "
        : "";
    final cp = "$mkdir"
        "echo '$password' | sudo -S cp $remoteTmp $target && "
        "echo '$password' | sudo -S touch $target";
    try {
      await execWithRetry(cp, maxAttempts: attempts);
      return true;
    } catch (_) {
      return false;
    }
  }

  Future<bool> pushTextToKml({
    required String text,
    required String remoteTmp,
    required String target,
    required String password,
    String? mkdirTarget,
  }) {
    return pushToKml(
      bytes: Uint8List.fromList(utf8.encode(text)),
      remoteTmp: remoteTmp,
      target: target,
      password: password,
      mkdirTarget: mkdirTarget,
    );
  }

  Future<bool> pushAssetToKml({
    required String assetPath,
    required String remoteTmp,
    required String target,
    required String password,
    String? mkdirTarget,
  }) async {
    final data = await rootBundle.load(assetPath);
    return pushToKml(
      bytes: data.buffer.asUint8List(),
      remoteTmp: remoteTmp,
      target: target,
      password: password,
      mkdirTarget: mkdirTarget,
    );
  }

  // ------------------------------------------------------------- screen formula
  // Shared, auditable mapping used by EVERY call site (logo, panels, clear).
  // Matches geosaurio-lg + La-Palma exactly.
  //   rightmost = floor(N/2)+1, leftmost = floor(N/2)+2 (1 for N=1)
  static int rightmostScreen(int screens) =>
      screens == 1 ? 1 : (screens ~/ 2) + 1;

  static int leftmostScreen(int screens) =>
      screens == 1 ? 1 : (screens ~/ 2) + 2;

  // ------------------------------------------------------------- camera
  Future<void> flyTo(Map<String, dynamic> flyto,
      {double headingOverride = -1}) async {
    final lon = flyto['lon'];
    final lat = flyto['lat'];
    final range = flyto['range'] ?? 500000;
    final tilt = flyto['tilt'] ?? 45;
    final heading =
        headingOverride >= 0 ? headingOverride : (flyto['heading'] ?? 0);
    final lookAt = '<LookAt><longitude>$lon</longitude><latitude>$lat</latitude>'
        '<range>$range</range><tilt>$tilt</tilt><heading>$heading</heading>'
        '<altitudeMode>relativeToGround</altitudeMode></LookAt>';
    await _exec('echo "flytoview=$lookAt" > /tmp/query.txt');
  }

  /// Send a smooth-timed orbit step (used by OrbitService).
  /// Runs a single, finite camera orbit on the LG master. Keeping the loop on
  /// the rig avoids Flutter-side timer overlap and the old heading wrap-around
  /// reversal. A separate stop command can interrupt it within one frame.
  Future<void> runOrbitLoop({
    required double longitude,
    required double latitude,
    required double range,
    required double tilt,
    required String stopFile,
  }) async {
    final lookAt = '<LookAt><longitude>${longitude.toStringAsFixed(4)}</longitude>'
        '<latitude>${latitude.toStringAsFixed(4)}</latitude><altitude>0</altitude>'
        '<range>${range.toStringAsFixed(0)}</range>'
        '<tilt>${tilt.toStringAsFixed(0)}</tilt><heading>\$heading</heading>'
        '<altitudeMode>relativeToGround</altitudeMode></LookAt>';
    // 24 steps at 15° are deliberately slow enough for a VM rig. The camera
    // stays centred on the current visualization and stops after one rotation.
    final command = 'rm -f $stopFile; '
        'for heading in \$(seq 0 15 345); do '
        '[ -f $stopFile ] && break; '
        'printf %s "flytoview=<gx:duration>2.2</gx:duration>'
        '<gx:flyToMode>smooth</gx:flyToMode>$lookAt" > /tmp/query.txt; '
        'sleep 2; done; rm -f $stopFile';
    await _exec(command);
  }

  Future<void> stopOrbit(String stopFile) async {
    // The sentinel interrupts a running loop; exittour and removal prevent a
    // stale flytoview command from keeping the camera locked afterwards.
    await _exec('touch $stopFile; echo "exittour=true" > /tmp/query.txt');
  }

  // ------------------------------------------------------------- deploy
  /// Sends one pre-baked visualization: opening fly-to, then master KML +
  /// rightmost text panel, then refresh. Returns a per-step result map so the
  /// UI can report exactly what succeeded/failed.
  Future<Map<String, bool>> sendVisualization({
    required String skillId,
    required VisualizationRef viz,
    required int screens,
    required String password,
  }) async {
    final results = <String, bool>{};

    await flyTo(viz.flyto);

    // 1. LG-hosted icon set. The rig has no dependable external icon access;
    // upload the package icons before the KML that refers to them.
    const iconAssets = [
      'circle-red.png', 'circle-green.png', 'circle-blue.png',
      'circle-orange.png', 'circle-yellow.png', 'circle-pink.png',
      'circle-purple.png', 'circle-white.png', 'plane.png', 'ship.png',
      'satellite.png',
    ];
    var iconsOk = true;
    for (final icon in iconAssets) {
      final ok = await pushAssetToKml(
        assetPath: 'assets/kml/icons/$icon',
        remoteTmp: '/home/lg/app_icon_$icon',
        target: '/var/www/html/kml/icons/$icon',
        password: password,
        mkdirTarget: '/var/www/html/kml/icons',
      );
      iconsOk = iconsOk && ok;
    }
    results['icons'] = iconsOk;

    // 2. master Earth KML
    results['master'] = await pushAssetToKml(
      assetPath: viz.masterKml,
      remoteTmp: '/home/lg/app_master.kml',
      target: '/var/www/html/kml/master.kml',
      password: password,
    );

    // 2. rightmost panel PNG + its ScreenOverlay KML
    final rightmost = rightmostScreen(screens);
    final pngDir = '/var/www/html/kml/$skillId';
    final pngHref = '$baseUrl/kml/$skillId/${viz.id}_panel.png';
    results['panelPng'] = await pushAssetToKml(
      assetPath: viz.panelPng,
      remoteTmp: '/home/lg/app_panel.png',
      target: '$pngDir/${viz.id}_panel.png',
      password: password,
      mkdirTarget: pngDir,
    );

    // Build the panel ScreenOverlay KML with the EXACT matching href.
    final panelKml = _panelOverlayKml(viz.label, pngHref);
    results['panelKml'] = await pushTextToKml(
      text: panelKml,
      remoteTmp: '/home/lg/app_panel.kml',
      target: '/var/www/html/kml/slave_$rightmost.kml',
      password: password,
    );

    // 3. force-refresh the rightmost slave so the new panel shows immediately
    results['refresh'] = await forceRefresh(rightmost, password);

    // 4. optional tour playback
    if (viz.tour != null) {
      try {
        await _exec('echo "playtour=${viz.tour}" > /tmp/query.txt');
        results['tour'] = true;
      } catch (_) {
        results['tour'] = false;
      }
    }

    return results;
  }

  String _panelOverlayKml(String name, String href) {
    return '<?xml version="1.0" encoding="UTF-8"?>'
        '<kml xmlns="http://www.opengis.net/kml/2.2">'
        '<Document><name>$name</name>'
        '<ScreenOverlay><name>$name</name><Icon>'
        '<href>$href</href></Icon>'
        '<overlayXY x="0.5" y="0.5" xunits="fraction" yunits="fraction"/>'
        '<screenXY x="0.5" y="0.5" xunits="fraction" yunits="fraction"/>'
        '<rotationXY x="0" y="0" xunits="fraction" yunits="fraction"/>'
        '<size x="640" y="420" xunits="pixels" yunits="pixels"/>'
        '</ScreenOverlay></Document></kml>';
  }

  /// Force a slave to re-read its Solo KML by toggling the refreshInterval on
  /// its myplaces NetworkLink (geosaurio-lg forceRefresh pattern).
  Future<bool> forceRefresh(int screenNumber, String password) async {
    try {
      // Add 2s refresh, then remove it — triggers an immediate re-fetch.
      await execWithRetry(
        "sshpass -p '$password' ssh -o StrictHostKeyChecking=no -t lg$screenNumber "
        "\"echo '$password' | sudo -S sed -i "
        "'s|<href>##LG_PHPIFACE##kml/slave_$screenNumber.kml</href>|"
        "<href>##LG_PHPIFACE##kml/slave_$screenNumber.kml</href>"
        "<refreshMode>onInterval</refreshMode><refreshInterval>2</refreshInterval>|' "
        "~/earth/kml/slave/myplaces.kml\"");
      await execWithRetry(
        "sshpass -p '$password' ssh -o StrictHostKeyChecking=no -t lg$screenNumber "
        "\"echo '$password' | sudo -S sed -i "
        "'s|<href>##LG_PHPIFACE##kml/slave_$screenNumber.kml</href>"
        "<refreshMode>onInterval</refreshMode><refreshInterval>2</refreshInterval>|"
        "<href>##LG_PHPIFACE##kml/slave_$screenNumber.kml</href>|' "
        "~/earth/kml/slave/myplaces.kml\"");
      return true;
    } catch (_) {
      return false;
    }
  }

  // ------------------------------------------------------------- logo
  /// Upload the logo image (final_logo.png, 1178x1124) via SFTP and place a
  /// ScreenOverlay sized exactly 554x500 px on the LEFTmost screen only.
  /// Returns per-step results.
  Future<Map<String, bool>> sendLogo({
    required int screens,
    required String password,
  }) async {
    final results = <String, bool>{};
    final leftmost = leftmostScreen(screens);

    // 1. upload the image (SFTP) — never assume it pre-exists on the rig
    results['logoPng'] = await pushAssetToKml(
      assetPath: 'assets/images/final_logo.png',
      remoteTmp: '/home/lg/final_logo.png',
      target: '/var/www/html/kml/final_logo.png',
      password: password,
    );

    // 2. overlay KML — pixel-exact 554x500, bottom-left anchored
    final href = '$baseUrl/kml/final_logo.png';
    final logoKml = '<?xml version="1.0" encoding="UTF-8"?>'
        '<kml xmlns="http://www.opengis.net/kml/2.2"><Document><name>Logo</name>'
        '<ScreenOverlay><name>Logo</name><Icon>'
        '<href>$href</href></Icon>'
        '<overlayXY x="0" y="1" xunits="fraction" yunits="fraction"/>'
        '<screenXY x="0.02" y="0.98" xunits="fraction" yunits="fraction"/>'
        '<rotationXY x="0" y="0" xunits="fraction" yunits="fraction"/>'
        '<size x="554" y="500" xunits="pixels" yunits="pixels"/>'
        '</ScreenOverlay></Document></kml>';

    results['logoKml'] = await pushTextToKml(
      text: logoKml,
      remoteTmp: '/home/lg/app_logo.kml',
      target: '/var/www/html/kml/slave_$leftmost.kml',
      password: password,
    );

    results['refresh'] = await forceRefresh(leftmost, password);
    return results;
  }

  /// Remove the logo overlay (write a blank KML to the leftmost slave).
  Future<bool> clearLogo({
    required int screens,
    required String password,
  }) async {
    final leftmost = leftmostScreen(screens);
    const blank = '<kml xmlns="http://www.opengis.net/kml/2.2">'
        '<Document><name>Empty Logo</name></Document></kml>';
    final ok = await pushTextToKml(
      text: blank,
      remoteTmp: '/home/lg/app_logo_blank.kml',
      target: '/var/www/html/kml/slave_$leftmost.kml',
      password: password,
    );
    if (ok) {
      await forceRefresh(leftmost, password);
    }
    return ok;
  }

  // ------------------------------------------------------------- utilities
  Future<void> clearEarth(
      {required int screens, required String password}) async {
    await _exec('echo "exittour=true" > /tmp/query.txt');
    const blank = '<kml xmlns="http://www.opengis.net/kml/2.2">'
        '<Document><name>Blank</name></Document></kml>';
    await _upload(
        '/home/lg/app_blank.kml', Uint8List.fromList(utf8.encode(blank)));
    final parts = <String>[
      "echo '$password' | sudo -S cp /home/lg/app_blank.kml /var/www/html/kml/master.kml",
      "echo '$password' | sudo -S touch /var/www/html/kml/master.kml",
    ];
    final clearedSlaves = <int>[];
    final leftmost = leftmostScreen(screens);
    // Preserve the dedicated logo screen. Every other slave gets a valid blank
    // KML (never an empty/deleted file) and an updated timestamp.
    for (var i = 2; i <= screens; i++) {
      if (i == leftmost) continue;
      parts.add("echo '$password' | sudo -S cp /home/lg/app_blank.kml "
          "/var/www/html/kml/slave_$i.kml");
      parts.add("echo '$password' | sudo -S touch /var/www/html/kml/slave_$i.kml");
      clearedSlaves.add(i);
    }
    await _exec(parts.join(' && '));
    for (final screen in clearedSlaves) {
      await forceRefresh(screen, password);
    }
  }

  // ------------------------------------------------------------- advanced
  // VM rigs do not reliably have cross-frame root SSH keys. The LG direct
  // helpers perform remote frames first and master last; run them detached so
  // the UI gets an honest "sent" result before a display restart/reboot closes
  // the SSH transport. They are intentionally not verified afterward.
  Future<void> _runRigHelper(String helper, String logName) async {
    final command = 'helper=""; '
        'for dir in /home/lg/bin /home/*/bin; do '
        'if [ -x "\$dir/$helper" ]; then helper="\$dir/$helper"; break; fi; '
        'done; '
        'if [ -z "\$helper" ]; then '
        'echo "Required LG helper $helper is not installed" >&2; exit 127; fi; '
        'nohup "\$helper" > "/tmp/$logName" 2>&1 < /dev/null & echo SENT';
    final result = await _exec(command);
    if (!result.contains('SENT')) {
      throw LgCommandException('LG helper did not start', command);
    }
  }

  Future<void> rebootRig() =>
      _runRigHelper('lg-reboot-direct', 'lg-demo-reboot.log');

  Future<void> relaunchRig() =>
      _runRigHelper('lg-relaunch-direct', 'lg-demo-relaunch.log');
}

/// Lightweight reference to a visualization's asset paths + fly-to, passed
/// from the UI to the service (keeps the SSH layer independent of models).
class VisualizationRef {
  final String id;
  final String label;
  final String masterKml;
  final String panelPng;
  final String panelKml;
  final Map<String, dynamic> flyto;
  final String? tour;

  const VisualizationRef({
    required this.id,
    required this.label,
    required this.masterKml,
    required this.panelPng,
    required this.panelKml,
    required this.flyto,
    this.tour,
  });
}

class LgCommandException implements Exception {
  final String message;
  final String command;
  LgCommandException(this.message, this.command);
  @override
  String toString() => message;
}
