import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import 'controllers/app_state.dart';
import 'screens/home_screen.dart';
import 'theme.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const LiquidGalaxyDemoApp());
}

class LiquidGalaxyDemoApp extends StatelessWidget {
  const LiquidGalaxyDemoApp({super.key});

  @override
  Widget build(BuildContext context) {
    return ChangeNotifierProvider(
      create: (_) => AppState()..init(),
      child: MaterialApp(
        title: 'Liquid Galaxy Demo Suite',
        debugShowCheckedModeBanner: false,
        theme: LgTheme.dark(),
        // Home is the root screen. Settings is reached via the gear icon.
        home: const HomeScreen(),
      ),
    );
  }
}
