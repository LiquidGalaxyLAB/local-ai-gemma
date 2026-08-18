import 'dart:async';

import 'lg_service.dart';

/// A controlled, rig-side camera orbit.
///
/// The loop runs on the LG master, not on a Flutter timer. That avoids the
/// overlapping SSH commands and heading reset that made the old orbit shaky.
/// A small stop-sentinel file lets any new visualization or Clear Earth end it
/// immediately.
class OrbitService {
  OrbitService(this._lg);

  static const _stopFile = '/tmp/lg_demo_orbit_stop';
  final LgService _lg;
  bool _running = false;

  bool get isRunning => _running;

  Future<bool> start(Map<String, dynamic> flyto) async {
    if (_running || !_lg.isConnected) return false;

    final lon = _number(flyto['lon']);
    final lat = _number(flyto['lat']);
    if (lon == null || lat == null) return false;

    // VirtualBox-based LG rigs need a wider range than a physical rig. Keep the
    // current scene readable while preventing the close-terrain blank screen.
    final requestedRange = _number(flyto['range']) ?? 1500000;
    final range = (requestedRange < 1500000 ? 1500000.0 : requestedRange).toDouble();
    final tilt = ((_number(flyto['tilt']) ?? 55).clamp(35, 70)).toDouble();

    _running = true;
    try {
      await _lg.runOrbitLoop(
        longitude: lon,
        latitude: lat,
        range: range,
        tilt: tilt,
        stopFile: _stopFile,
      );
      return true;
    } finally {
      _running = false;
    }
  }

  Future<void> stop() async {
    if (!_lg.isConnected) {
      _running = false;
      return;
    }
    try {
      await _lg.stopOrbit(_stopFile);
    } finally {
      _running = false;
    }
  }

  double? _number(Object? value) {
    if (value is num) return value.toDouble();
    return double.tryParse('$value');
  }
}
