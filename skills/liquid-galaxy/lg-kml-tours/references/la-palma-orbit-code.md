# La Palma App: Orbit Animation Source Code

Exact Dart code from the La Palma Volcano Eruption Tracking Tool
(https://github.com/LiquidGalaxyLAB/La-Palma-Volcano-Eruption-Tracking-Tool.git)
showing how the LG app achieves smooth orbit animation.

## orbitPlay() — Main Orbit Controller

```dart
bool _orbitPlaying = false;
Timer? _orbitTimer;

Future<bool> orbitPlay(
   double latitude,
   double longitude,
   double zoom,
   double tilt,
   ) async {
 if (_orbitPlaying) {
   return false;
 }
 if (!_isConnected) {
   print('Cannot start orbit: LG not connected');
   return false;
 }
 await query('exittour=true');
 await Future.delayed(const Duration(milliseconds: 100));
 _orbitPlaying = true;
 try {
   const int steps = 60;
   const int stepDuration = 400;  // ms per step
   int currentStep = 1;
   bool isMoving = false;
   _orbitTimer = Timer.periodic(Duration(milliseconds: stepDuration), (
       timer,
     ) async {
     if (!_orbitPlaying || currentStep >= steps) {
       timer.cancel();
       _orbitPlaying = false;
       try {
         await query('exittour=true');
       } catch (e) {
         print('Error executing exittour after orbit completion: $e');
       }
       return;
     }
     if (isMoving) return;
     try {
       isMoving = true;
       double bearing = (currentStep * (360 / steps)) % 360;
       await flyToOrbit('Orbit', latitude, longitude, zoom, tilt, bearing)
         .timeout(const Duration(milliseconds: 100));
       currentStep++;
       isMoving = false;
     } catch (e) {
       print('Error during orbit step $currentStep: $e');
       currentStep++;
       isMoving = false;
     }
   });
   return true;
 } catch (e) {
   _orbitPlaying = false;
   print('Error during orbit: $e');
   return false;
 }
}
```

## flyToOrbit() — Send One Orbit Step

```dart
String? _lastOrbitPosition;

Future<void> flyToOrbit(
   String context,
   double latitude,
   double longitude,
   double zoom,
   double tilt,
   double bearing,
   ) async {
 try {
   final String lookAt = orbitLookAtLinear(
     latitude, longitude, zoom, tilt, bearing,
   );
   await query('flytoview=$lookAt');
   await Future.delayed(const Duration(milliseconds: 50));
 } catch (error) {
   print('Error in flyToOrbit: $error');
 }
}
```

## orbitLookAtLinear() — Build flytoview String

```dart
String orbitLookAtLinear(
   double latitude,
   double longitude,
   double zoom,
   double tilt,
   double bearing,
   ) {
 final lookAt =
     '<gx:duration>0.3</gx:duration><gx:flyToMode>smooth</gx:flyToMode><LookAt>'
     '<longitude>$longitude</longitude><latitude>$latitude</latitude>'
     '<range>$zoom</range><tilt>$tilt</tilt>'
     '<heading>$bearing</heading>'
     '<altitudeMode>relativeToGround</altitudeMode></LookAt>';
 _lastOrbitPosition = lookAt;
 return lookAt;
}
```

## orbitStop() — Stop and Restore Position

```dart
Future<void> orbitStop() async {
 _orbitTimer?.cancel();
 _orbitTimer = null;
 _orbitPlaying = false;
 try {
   await query('exittour=true').timeout(const Duration(milliseconds: 500));
   if (_lastOrbitPosition != null) {
     await query('flytoview=$_lastOrbitPosition')
       .timeout(const Duration(milliseconds: 500));
   }
 } catch (e) {
   print('Error stopping orbit: $e');
 }
}
```

## query() — Write to /tmp/query.txt

The `query()` function writes a command to `/tmp/query.txt` via SSH.
The LG's monitoring daemon reads this file and executes the command.

Commands:
| Value | Effect |
|-------|--------|
| `flytoview=<LookAt>` | Fly camera to position |
| `exittour=true` | Exit any active tour/clean state |
| `playtour=<name>` | Play a named tour |
| *(empty)* | Clear/reset |

## /tmp/query.txt Lifecycle

```
App writes → /tmp/query.txt  →  LG daemon reads →  daemon executes →  daemon deletes file
     ↑                                                                         │
     └──────────────────────  next write (file recreated)  ←────────────────────┘
```

The file being absent (`cat: /tmp/query.txt: No such file or directory`) means
the command was **successfully consumed**. A blank read is success, not failure.
