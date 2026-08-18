import 'dart:async';

import 'package:flutter/foundation.dart';

import 'lg_service.dart';

/// Reusable 360° camera orbit, modeled on geosaurio-lg's LgOrbitService.
///
/// Drives the rig by repeatedly sending `flytoview=` LookAt KML with an
/// incrementing heading over SSH, on a Timer. Never blocks the UI thread,
/// and is cleanly cancelable. Guards against overlapping orbits via a
/// `_isOrbiting` flag + an in-flight `_isMoving` flag.
///
/// IMPORTANT: before orbiting, it first flies to the target with a smooth
/// transition so the camera never jumps abruptly from its current position.
class OrbitService {
  final LgService _lg;

  OrbitService(this._lg);

  bool _isOrbiting = false;
  bool _isMoving = false;
  Timer? _timer;
  int _step = 0;

  // configurable (not hardcoded per visualization)
  int steps = 60; // ticks per full 360°
  int stepDurationMs = 400;
  double tilt = 72;
  double rangeFactor = 1.0; // multiplier applied to the flyto range

  bool get isOrbiting => _isOrbiting;

  /// Start orbiting around the given camera target.
  ///
  /// [flyto] is the visualization's opening camera position (center lat/lon,
  /// range, tilt). The camera first flies smoothly to that target, then begins
  /// rotating its heading. This avoids the abrupt jump when the camera is
  /// somewhere else entirely.
  Future<bool> start(Map<String, dynamic> flyto) async {
    if (_isOrbiting) {
      debugPrint('OrbitService: already orbiting, ignoring start');
      return false;
    }
    if (!_lg.isConnected) {
      debugPrint('OrbitService: not connected');
      return false;
    }

    final lat = (flyto['lat'] as num).toDouble();
    final lon = (flyto['lon'] as num).toDouble();
    final baseRange = ((flyto['range'] as num?)?.toDouble() ?? 500000) * rangeFactor;
    final baseTilt = (flyto['tilt'] as num?)?.toDouble() ?? tilt;
    final startHeading = (flyto['heading'] as num?)?.toDouble() ?? 0;

    // 1. Fly smoothly to the target first (no jump).
    try {
      await _lg.flyToSmooth(
        {'lon': lon, 'lat': lat, 'range': baseRange, 'tilt': baseTilt},
        startHeading,
      );
      // let the smooth fly settle before the timer starts stepping
      await Future.delayed(const Duration(milliseconds: 350));
    } catch (e) {
      debugPrint('OrbitService: initial fly-to failed $e');
    }

    _step = 0;
    _isOrbiting = true;
    _isMoving = false;
    debugPrint('OrbitService: START lat=$lat lon=$lon range=$baseRange tilt=$baseTilt');

    _timer?.cancel();
    _timer = Timer.periodic(Duration(milliseconds: stepDurationMs), (timer) async {
      if (!_isOrbiting) {
        timer.cancel();
        return;
      }
      if (_isMoving) {
        // skip this tick — a movement is still in flight
        return;
      }
      _isMoving = true;
      try {
        final heading = (startHeading + _step * (360.0 / steps)) % 360.0;
        await _lg.flyToSmooth(
          {'lon': lon, 'lat': lat, 'range': baseRange, 'tilt': baseTilt},
          heading,
        );
        _step++;
        if (_step >= steps) _step = 0;
      } catch (e) {
        debugPrint('OrbitService: step error $e');
      } finally {
        _isMoving = false;
      }
    });

    return true;
  }

  /// Stop the orbit, leaving the camera in its current position. No further
  /// commands are queued.
  Future<void> stop() async {
    _timer?.cancel();
    _timer = null;
    _isOrbiting = false;
    _isMoving = false;
    _step = 0;
    debugPrint('OrbitService: STOP');
  }

  void dispose() {
    stop();
  }
}
