import 'package:flutter_test/flutter_test.dart';

import 'package:liquid_galaxy_demo/main.dart';

void main() {
  testWidgets('app boots to home screen', (WidgetTester tester) async {
    await tester.pumpWidget(const LiquidGalaxyDemoApp());
    await tester.pump();
    // Home is now the root screen.
    expect(find.text('Liquid Galaxy — Demo Suite'), findsOneWidget);
  });
}
