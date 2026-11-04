import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:social_demo/main.dart';

void main() {
  testWidgets(
    'Reference feed keeps centered branding and floating navigation',
    (tester) async {
      await tester.binding.setSurfaceSize(const Size(390, 849));
      addTearDown(() => tester.binding.setSurfaceSize(null));
      await tester.pumpWidget(const SocialDemoApp());
      await tester.pump();
      expect(find.byKey(const Key('reference-wordmark')), findsOneWidget);
      final wordmark = tester.getRect(
        find.byKey(const Key('reference-wordmark')),
      );
      expect(wordmark.center.dx, closeTo(195, 0.5));
      expect(
        tester.getCenter(find.byTooltip('Create')).dx,
        lessThan(wordmark.left),
      );
      expect(
        tester.getCenter(find.byTooltip('Notifications')).dx,
        greaterThan(wordmark.right),
      );
      expect(find.text('teemirgali'), findsOneWidget);
      expect(find.text('abilzhan_17'), findsOneWidget);
      expect(find.text('aktobe_typical'), findsOneWidget);
      final home = tester.getCenter(find.byTooltip('Home'));
      final reels = tester.getCenter(find.byTooltip('Reels'));
      final messages = tester.getCenter(find.byTooltip('Messages'));
      final search = tester.getCenter(find.byTooltip('Search'));
      expect(home.dx, lessThan(reels.dx));
      expect(reels.dx, lessThan(messages.dx));
      expect(messages.dx, lessThan(search.dx));
      final panel = tester.getRect(
        find.byKey(const Key('floating-navigation')),
      );
      expect(panel.left, greaterThan(0));
      expect(panel.bottom, lessThan(849));
      expect(tester.takeException(), isNull);
    },
  );

  testWidgets('Reference post actions open the impersonation form', (
    tester,
  ) async {
    await tester.binding.setSurfaceSize(const Size(390, 849));
    addTearDown(() => tester.binding.setSurfaceSize(null));
    await tester.pumpWidget(const SocialDemoApp());
    await tester.pump();
    await tester.tap(find.byTooltip('More actions').first);
    await tester.pumpAndSettle();
    await tester.tap(find.text('Report impersonation'));
    await tester.pumpAndSettle();
    expect(find.text('Report @aktobe_typical'), findsOneWidget);
    await tester.tap(find.text('Submit claim'));
    await tester.pump();
    expect(
      find.text('Enter your handle and attach both screenshots.'),
      findsOneWidget,
    );
    expect(tester.takeException(), isNull);
  });

  for (final width in [320.0, 430.0]) {
    testWidgets('Reference feed and profile fit width $width', (tester) async {
      await tester.binding.setSurfaceSize(Size(width, 849));
      addTearDown(() => tester.binding.setSurfaceSize(null));
      await tester.pumpWidget(const SocialDemoApp());
      await tester.pump();
      expect(tester.takeException(), isNull);
      await tester.tap(find.byTooltip('Profile'));
      await tester.pumpAndSettle();
      expect(find.text('Report impersonation'), findsOneWidget);
      expect(tester.takeException(), isNull);
    });
  }

  testWidgets('Reference account gets a live status badge', (tester) async {
    await tester.pumpWidget(const SocialDemoApp());
    await tester.pump();
    statuses.value = {'aktobe_typical': 'under_review'};
    await tester.pump();
    expect(find.text('Report under review'), findsOneWidget);
    statuses.value = {'aktobe_typical': 'confirmed'};
    await tester.pump();
    expect(find.text('Confirmed impersonation'), findsOneWidget);
    statuses.value = {};
    await tester.pump();
    expect(find.text('Confirmed impersonation'), findsNothing);
    expect(tester.takeException(), isNull);
  });
}
