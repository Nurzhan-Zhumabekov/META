import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:social_demo/main.dart';

void main() {
  testWidgets('ML card keeps risk separate from similarity and human verdict', (
    tester,
  ) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: Scaffold(
          body: AnalysisSummary(
            analysis: {
              'provider': 'local',
              'profile_ml': {
                'model': 'profile-logreg-v1',
                'risk_score': 0.72,
                'risk_band': 'high',
                'factors': [
                  {
                    'label': 'Following count',
                    'value': 2100,
                    'direction': 'raises',
                  },
                ],
                'out_of_range_features': [],
              },
            },
          ),
        ),
      ),
    );
    expect(find.text('Profile ML · logistic regression'), findsOneWidget);
    expect(find.text('ML risk score: 72%'), findsOneWidget);
    expect(find.textContaining('does not prove impersonation'), findsOneWidget);
    expect(find.textContaining('Meta AI ·'), findsNothing);
  });

  testWidgets('ML fields are editable facts, not inferred from screenshot', (
    tester,
  ) async {
    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: SingleChildScrollView(
            child: ProfileFactsFields(account: accounts[1]),
          ),
        ),
      ),
    );
    expect(find.text('Posts'), findsOneWidget);
    expect(find.text('Followers'), findsOneWidget);
    expect(find.text('Following'), findsOneWidget);
    expect(find.textContaining('Review these demo values'), findsOneWidget);
    final state = tester.state<ProfileFactsFieldsState>(
      find.byType(ProfileFactsFields),
    );
    expect(state.facts()['num_posts'], 6);
    expect(state.facts()['num_followers'], 40);
    expect(state.facts()['handle'], 'aigerim.k_official');
  });
}
