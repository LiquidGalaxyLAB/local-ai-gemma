import 'dart:convert';
import 'dart:typed_data';

import 'package:dartssh2/dartssh2.dart';
import 'package:flutter/services.dart' show rootBundle;

/// Liquid Galaxy control service.
///
/// Wraps dartssh2 and mirrors the conventions used across LiquidGalaxyLAB
/// Flutter apps (Super Liquid Galaxy Controller, La Palma Volcano Tracker):
///   - connect via SSHSocket + SSHClient (username + password)
///   - fly camera via   echo "flytoview=<LookAt>" > /tmp/query.txt
///   - deploy KML via SFTP upload + sudo cp into /var/www/html/kml/
///   - rightmost screen = N ~/ 2 + 1   (balloons / text panels)
///   - leftmost  screen = N ~/ 2 + 2   (logo)
///   - clear via exittour=true + blank KMLs
class LgService {
  SSHClient? _client;

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
    );
    _client = client;
  }

  Future<void> disconnect() async {
    try {
      _client?.close();
    } catch (_) {}
    _client = null;
  }

  Future<String> testConnection() async {
    final out = await _exec('echo LG_OK && hostname && uname -m');
    return out;
  }

  // ------------------------------------------------------------- primitives
  Future<String> _exec(String command) async {
    final c = _client;
    if (c == null) throw StateError('Not connected');
    final result = await c.runWithResult(command);
    if (result.exitCode != null && result.exitCode != 0) {
      final err = utf8.decode(result.stderr).trim();
      if (err.isNotEmpty) {
        throw LgCommandException(err, command);
      }
    }
    return utf8.decode(result.stdout).trim();
  }

  Future<void> _upload(String remotePath, Uint8List bytes) async {
    final c = _client;
    if (c == null) throw StateError('Not connected');
    final sftp = await c.sftp();
    final file = await sftp.open(remotePath,
        mode: SftpFileOpenMode.create |
            SftpFileOpenMode.truncate |
            SftpFileOpenMode.write);
    await file.write(Stream.value(bytes));
    await file.close();
  }

  /// Deploy a local asset (KML text) to a remote path, then sudo-copy into
  /// the Apache kml directory. Uses the LG password for sudo (same as SSH).
  Future<void> _deployAsset({
    required String assetPath,
    required String remoteTmp,
    required String target,
    required String password,
    bool isBinary = false,
    String? mkdirTarget,
  }) async {
    final bytes = isBinary
        ? (await rootBundle.load(assetPath)).buffer.asUint8List()
        : Uint8List.fromList(
            utf8.encode(await rootBundle.loadString(assetPath)));
    await _upload(remoteTmp, bytes);
    final mkdir = mkdirTarget != null
        ? "echo '$password' | sudo -S mkdir -p $mkdirTarget && "
        : "";
    final cp =
        "echo '$password' | sudo -S cp $remoteTmp $target && echo '$password' | sudo -S touch $target";
    await _exec("$mkdir$cp");
  }

  // ------------------------------------------------------------- camera
  Future<void> flyTo(Map<String, dynamic> flyto) async {
    final lon = flyto['lon'];
    final lat = flyto['lat'];
    final range = flyto['range'] ?? 500000;
    final tilt = flyto['tilt'] ?? 45;
    final heading = flyto['heading'] ?? 0;
    final lookAt = '<LookAt><longitude>$lon</longitude><latitude>$lat</latitude>'
        '<range>$range</range><tilt>$tilt</tilt><heading>$heading</heading>'
        '<altitudeMode>relativeToGround</altitudeMode></LookAt>';
    await _exec('echo "flytoview=$lookAt" > /tmp/query.txt');
  }

  // ------------------------------------------------------------- deploy
  /// Sends one pre-baked visualization: opening fly-to, then master KML +
  /// rightmost text panel, then refresh.
  Future<void> sendVisualization({
    required String skillId,
    required VisualizationRef viz,
    required int screens,
    required String password,
  }) async {
    await flyTo(viz.flyto);

    // 1. master Earth KML
    await _deployAsset(
      assetPath: viz.masterKml,
      remoteTmp: '/home/lg/app_master.kml',
      target: '/var/www/html/kml/master.kml',
      password: password,
    );

    // 2. rightmost panel PNG + its ScreenOverlay KML
    final rightmost = screens ~/ 2 + 1;
    final pngDir = '/var/www/html/kml/$skillId';
    await _deployAsset(
      assetPath: viz.panelPng,
      remoteTmp: '/home/lg/app_panel.png',
      target: '$pngDir/${viz.id}_panel.png',
      password: password,
      isBinary: true,
      mkdirTarget: pngDir,
    );
    await _deployAsset(
      assetPath: viz.panelKml,
      remoteTmp: '/home/lg/app_panel.kml',
      target: '/var/www/html/kml/slave_$rightmost.kml',
      password: password,
    );

    // 3. optional tour playback
    if (viz.tour != null) {
      await _exec('echo "playtour=${viz.tour}" > /tmp/query.txt');
    }
  }

  // ------------------------------------------------------------- utilities
  Future<void> clearEarth({required int screens, required String password}) async {
    await _exec('echo "exittour=true" > /tmp/query.txt');
    const blank = '<kml xmlns="http://www.opengis.net/kml/2.2">'
        '<Document><name>Blank</name></Document></kml>';
    await _upload('/home/lg/app_blank.kml',
        Uint8List.fromList(utf8.encode(blank)));
    final parts = <String>[
      "echo '$password' | sudo -S cp /home/lg/app_blank.kml /var/www/html/kml/master.kml",
    ];
    for (var i = 1; i <= screens; i++) {
      parts.add("echo '$password' | sudo -S cp /home/lg/app_blank.kml "
          "/var/www/html/kml/slave_$i.kml");
    }
    await _exec(parts.join(' && '));
  }

  Future<void> showLogo({required int screens, required String password}) async {
    final leftmost = screens ~/ 2 + 2;
    const logo = '<?xml version="1.0" encoding="UTF-8"?>'
        '<kml xmlns="http://www.opengis.net/kml/2.2"><Document><name>Logo</name>'
        '<ScreenOverlay><name>Logo</name><Icon>'
        '<href>http://lg1:81/kml/logo_overlay.png</href></Icon>'
        '<overlayXY x="0.5" y="0.5" xunits="fraction" yunits="fraction"/>'
        '<screenXY x="0.5" y="0.5" xunits="fraction" yunits="fraction"/>'
        '<size x="320" y="90" xunits="pixels" yunits="pixels"/>'
        '</ScreenOverlay></Document></kml>';
    await _upload('/home/lg/app_logo.kml',
        Uint8List.fromList(utf8.encode(logo)));
    await _exec("echo '$password' | sudo -S cp /home/lg/app_logo.kml "
        "/var/www/html/kml/slave_$leftmost.kml");
  }

  // ------------------------------------------------------------- advanced
  Future<void> rebootRig({required int screens, required String password}) async {
    for (var i = screens; i >= 1; i--) {
      await _exec("sshpass -p '$password' ssh -o StrictHostKeyChecking=no "
          "-t lg$i \"echo '$password' | sudo -S reboot\"");
    }
  }

  Future<void> relaunchRig({required int screens, required String password}) async {
    for (var i = screens; i >= 1; i--) {
      await _exec("sshpass -p '$password' ssh -o StrictHostKeyChecking=no "
          "-t lg$i \"echo '$password' | sudo -S service lightdm restart\"");
    }
  }
}

/// Lightweight reference to a visualization's asset paths + fly-to, passed
/// from the UI to the service (keeps the SSH layer independent of models).
class VisualizationRef {
  final String id;
  final String masterKml;
  final String panelPng;
  final String panelKml;
  final Map<String, dynamic> flyto;
  final String? tour;

  const VisualizationRef({
    required this.id,
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
