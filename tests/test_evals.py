import json

import numpy as np
import pytest

from evals import run


def case(case_id):
    return next(c for c in run.load_cases() if c['id'] == case_id)


def test_suite_preserves_fifteen_original_ids_and_expectations():
    cases = run.load_cases()
    assert len(cases) == len({c['id'] for c in cases}) == 15
    assert case('copied_bio_avatar')['expected'] == ['needs_review']
    assert case('blank_both')['expected'] == ['insufficient_evidence']


@pytest.mark.parametrize('case_id', ['same_avatar_only', 'default_avatars'])
def test_avatar_reuse_does_not_accidentally_duplicate_the_entire_post_grid(case_id):
    original, suspect = run.images(case(case_id))
    assert np.array_equal(np.array(original.crop((16, 65, 105, 154))), np.array(suspect.crop((16, 65, 105, 154))))
    assert not np.array_equal(np.array(original.crop((0, 360, 390, 620))), np.array(suspect.crop((0, 360, 390, 620))))


def test_explicit_ml_facts_match_the_candidate_account():
    for sample in run.load_cases():
        facts = run.profile_for(sample)
        assert facts.handle == sample['suspect']
        assert facts.num_posts >= 0 and facts.num_followers >= 0
        assert facts.has_profile_picture is (sample['kind'] != 'default_avatar')


def test_grader_does_not_treat_ml_risk_as_an_impersonation_verdict():
    sample = case('unrelated_names')
    row = {'analysis': {'provider': 'meta', 'recommendation': 'unlikely_impersonation'},
           'profile_ml': {'risk_score': 0.99, 'human_review_required': True, 'facts_source': 'user_provided'},
           'status': 'under_review'}
    checks = run.grade(sample, row)
    assert all(checks.values())
    row['status'] = 'confirmed'
    assert run.grade(sample, row)['human_review'] is False


def test_ml_is_still_recorded_when_meta_fails(tmp_path, monkeypatch):
    from src import pipeline
    from src.errors import ComparisonUnavailable
    monkeypatch.setattr(pipeline, 'submit_claim', lambda *args, **kwargs: (_ for _ in ()).throw(ComparisonUnavailable('meta_timeout', 'Timed out', 504)))
    monkeypatch.setattr(run, 'score_profile', lambda _: {'risk_score': 0.25, 'human_review_required': True, 'facts_source': 'user_provided'})
    row = run.evaluate_case(case('unrelated_names'), tmp_path)
    assert row['profile_ml']['risk_score'] == 0.25
    assert row['error'] == 'meta_timeout'
    assert row['checks']['meta_recommendation'] is False
