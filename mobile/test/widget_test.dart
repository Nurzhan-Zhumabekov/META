import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:social_demo/main.dart';

void main() {
  testWidgets('Instagram navigation opens profile and impersonation report', (
    tester,
  ) async {
    await tester.pumpWidget(const SocialDemoApp());
    await tester.pump();
    expect(find.bySemanticsLabel('Instagram'), findsOneWidget);
    expect(find.byTooltip('Profile'), findsOneWidget);
    await tester.tap(find.byTooltip('Profile'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Report impersonation'));
    await tester.pumpAndSettle();
    expect(find.text('Report @aigerim.k'), findsOneWidget);
    expect(find.text('Your original handle'), findsOneWidget);
    await tester.tap(find.text('Submit claim'));
    await tester.pump();
    expect(
      find.text('Enter your handle and attach both screenshots.'),
      findsOneWidget,
    );
  });
  testWidgets('Account badges reflect API statuses', (tester) async {
    statuses.value = {'aigerim.k_official': 'confirmed'};
    await tester.pumpWidget(
      const MaterialApp(home: Scaffold(body: FlagBadge('confirmed_fake'))),
    );
    expect(find.text('Confirmed impersonation'), findsOneWidget);
    statuses.value = {};
  });
}
