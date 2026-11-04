import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:social_demo/main.dart';

void main() {
  testWidgets(
    'Meta analysis identifies the provider and preserves limitations',
    (tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: AnalysisSummary(
              analysis: {
                'provider': 'meta',
                'model': 'muse-spark-1.3',
                'summary': 'Visible reuse of profile text.',
                'evidence': ['Same bio'],
                'differences': ['Different handle'],
                'limitations': ['Ownership not established'],
              },
            ),
          ),
        ),
      );
      expect(find.text('Meta AI · muse-spark-1.3'), findsOneWidget);
      expect(find.text('• Same bio'), findsOneWidget);
      expect(find.text('• Different handle'), findsOneWidget);
      expect(find.text('• Ownership not established'), findsOneWidget);
      expect(
        find.textContaining('reviewer makes the final decision'),
        findsOneWidget,
      );
    },
  );

  testWidgets('Local results are never presented as Meta AI', (tester) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: Scaffold(
          body: AnalysisSummary(
            analysis: {'provider': 'local', 'summary': 'Local comparison'},
          ),
        ),
      ),
    );
    expect(find.text('Screenshot comparison · local'), findsOneWidget);
    expect(find.textContaining('Meta AI'), findsNothing);
  });
}
