import 'package:flutter_tts/flutter_tts.dart';

/// Minimal on-device narration.
///
/// Uses the free FlutterTts plugin (Android's built-in text-to-speech engine,
/// no network, no API keys). We speak one or two short lines so a viewer hears
/// what the rightmost panel is showing. Failure is silent — narration must
/// never break the deploy path.
class SpeechService {
  final FlutterTts _tts = FlutterTts();

  Future<void> speak(String text) async {
    try {
      await _tts.stop();
      await _tts.setSpeechRate(0.48);
      await _tts.setVolume(1.0);
      await _tts.speak(text);
    } catch (_) {
      // TTS is optional; ignore any engine/init failure.
    }
  }

  Future<void> stop() async {
    try {
      await _tts.stop();
    } catch (_) {}
  }
}
