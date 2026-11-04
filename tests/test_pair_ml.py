import json

import pytest

from src import config, pipeline
from src.profile_ml import ProfileFacts
from src.pair_ml import PAIR_FEATURES, PairFacts, pair_features, score_pair


def profile(handle='alice.photo', **changes):
    return ProfileFacts(handle=handle, display_name='Alice Studio',
                        bio='Wedding photographer in Astana. Bookings: alice.example',
                        has_profile_picture=True, has_external_url=True, is_private=False,
                        num_posts=128, num_followers=5400, num_following=310, **changes)


@pytest.fixture
def pair_model(tmp_path, monkeypatch):
    path = tmp_path / 'pair-model.json'
    path.write_text(json.dumps({'artifact_version': 1, 'model_id': 'pair-test',
        'features': list(PAIR_FEATURES), 'mean': [0.] * len(PAIR_FEATURES),
        'scale': [1.] * len(PAIR_FEATURES), 'coefficients': [0.1] * len(PAIR_FEATURES),
        'intercept': -1., 'threshold': 0.5}))
    monkeypatch.setattr(config, 'PAIR_ML_MODEL_PATH', path)
    return path


def test_pair_features_compare_profiles_without_using_avatar_or_popularity():
    original = profile()
    suspect = original.model_copy(update={'handle': 'alice.photo_help'})
    vector = pair_features(original, suspect)
    modified = suspect.model_copy(update={'has_profile_picture': False, 'num_followers': 0})
    assert vector == pair_features(original, modified)
    assert vector[PAIR_FEATURES.index('distinctive_bio_reuse')] > 0
    assert vector != pair_features(original, suspect.model_copy(update={'bio': 'Cooking at home', 'display_name': 'Maria'}))


def test_empty_profiles_and_self_pairs_abstain(pair_model):
    blank = profile().model_copy(update={'bio': '', 'display_name': ''})
    empty = score_pair(blank, blank.model_copy(update={'handle': 'another'}))
    same = score_pair(profile(), profile())
    assert empty['assessment'] == same['assessment'] == 'insufficient_evidence'
    assert empty['risk_score'] is None and same['risk_score'] is None


def test_pair_result_is_labelled_synthetic_and_requires_human_review(pair_model):
    result = score_pair(profile(), profile('alice.photo_help'))
    assert result['provider'] == 'pair_ml'
    assert 0 <= result['risk_score'] <= 1
    assert result['human_review_required'] is True
    assert result['training_data'] == 'synthetic'
    assert result['facts_source'] == 'user_provided'


@pytest.mark.parametrize('change', [{'scale': [0.] * 8}, {'intercept': float('nan')}, {'threshold': -1}])
def test_invalid_pair_artifact_fails_explicitly(pair_model, change):
    from src.errors import ComparisonUnavailable
    data = json.loads(pair_model.read_text())
    pair_model.write_text(json.dumps({**data, **change}))
    with pytest.raises(ComparisonUnavailable) as error:
        score_pair(profile(), profile('alice.help'))
    assert error.value.code == 'pair_ml_unavailable'


def test_training_and_holdout_have_no_shared_identity_families():
    from evals.pair_data import dataset
    train, holdout = dataset('train', 3), dataset('holdout', 2)
    assert not ({r['group'] for r in train} & {r['group'] for r in holdout})
    assert not ({r['original']['handle'] for r in train} & {r['original']['handle'] for r in holdout})
    assert all(r['label'] == 0 for r in holdout if r['kind'] == 'no_avatar')


def test_missing_original_never_invents_a_pair_result(client, make_image, png):
    image = png(make_image())
    response = client.post('/claims', data={'owner': 'alice', 'suspect': 'alice.help'},
        files={'original': ('o.png', image, 'image/png'), 'suspect_image': ('s.png', image, 'image/png')})
    assert response.status_code == 200
    assert 'pair_ml' not in response.json()['analysis']


def test_pair_endpoint_rejects_missing_or_malformed_original(client, pair_model):
    assert client.post('/ml/pair-risk', json={'suspect': profile().model_dump()}).status_code == 422
    response = client.post('/ml/pair-risk', json=PairFacts(original=profile(), suspect=profile('alice.help')).model_dump())
    assert response.status_code == 200
    assert response.json()['provider'] == 'pair_ml'


def test_claim_validates_original_handle_before_analysis(client, make_image, png):
    image = png(make_image())
    response = client.post('/claims', data={'owner': 'alice', 'suspect': 'suspect',
        'original_profile_facts': json.dumps(profile().model_dump(include={'handle', 'display_name', 'bio'}))},
        files={'original': ('o.png', image, 'image/png'), 'suspect_image': ('s.png', image, 'image/png')})
    assert response.status_code == 422
    assert not pipeline.DB.exists()


def test_pipeline_adds_pair_score_without_changing_human_status(client, make_image, png, pair_model, monkeypatch):
    monkeypatch.setattr(pipeline, 'score_profile', lambda _: {'risk_score': 0.1})
    image = png(make_image())
    response = client.post('/claims', data={'owner': 'alice.photo', 'suspect': 'alice.photo_help',
        'profile_facts': json.dumps(profile('alice.photo_help').model_dump()),
        'original_profile_facts': json.dumps(profile().model_dump(include={'handle', 'display_name', 'bio'}))},
        files={'original': ('o.png', image, 'image/png'), 'suspect_image': ('s.png', image, 'image/png')})
    assert response.status_code == 200
    result = response.json()
    assert result['analysis']['pair_ml']['provider'] == 'pair_ml'
    assert result['analysis']['profile_ml']['risk_score'] == 0.1
    assert result['status'] == 'under_review'
