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

    // KISS orbit: rotate around the visualization's focus. Clamp the range into
    // a local-orbit band so far-away views (continental history maps, whole-Earth
    // satellite shells) don't turn into a stuttering planet-scale spin, and so
    // close views never dip below Google Earth's VM render floor (~100 km).
    final rawRange = _number(flyto['range']) ?? 500000;
    final range = rawRange.clamp(150000.0, 2500000.0).toDouble();
    final tilt = _number(flyto['tilt']) ?? 45;

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
