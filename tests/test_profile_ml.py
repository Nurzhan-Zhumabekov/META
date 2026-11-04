import json
import math

import pytest
from pydantic import ValidationError

from src import config, pipeline
from src.errors import ComparisonUnavailable
from src.profile_ml import FEATURES, ProfileFacts, feature_vector, score_profile


def facts(**changes):
    return {
        'handle': 'alice_fake', 'display_name': 'Alice', 'bio': 'Photos',
        'has_profile_picture': True, 'has_external_url': False, 'is_private': False,
        'num_posts': 6, 'num_followers': 40, 'num_following': 2100,
        **changes,
    }


@pytest.fixture
def model_path(tmp_path, monkeypatch):
    path = tmp_path / 'model.json'
    path.write_text(json.dumps({
        'artifact_version': 1, 'model_id': 'test-logreg',
        'features': list(FEATURES), 'mean': [0.0] * len(FEATURES),
        'scale': [1.0] * len(FEATURES), 'coefficients': [0.0] * len(FEATURES),
        'intercept': 0.0, 'threshold': 0.5,
        'training_bounds': {f: [0, 100000000] for f in FEATURES},
        'provenance': {'source': 'test fixture'}, 'metrics': {},
    }))
    monkeypatch.setattr(config, 'ML_MODEL_PATH', path)
    monkeypatch.setattr(config, 'ML_ENABLED', True)
    return path


def test_features_use_profile_metadata_not_screenshots():
    vector = feature_vector(ProfileFacts(**facts(handle='alice1', display_name='Alice2', bio='abc')))
    assert vector[0] == 1
    assert vector[1] == pytest.approx(1 / 6)
    assert vector[2] == pytest.approx(1 / 6)
    assert vector[3] == pytest.approx(math.log1p(3))
    assert vector[4:6] == [0, 0]
    assert vector[-3:] == pytest.approx([math.log1p(6), math.log1p(40), math.log1p(2100)])


@pytest.mark.parametrize('changes', [
    {'num_followers': -1}, {'num_posts': '6'}, {'num_posts': True},
    {'is_private': None}, {'has_profile_picture': 'Yes'},
    {'handle': 'invalid handle'}, {'num_following': float('nan')},
    {'fake': 1},
])
def test_profile_facts_are_explicit_and_validated(changes):
    with pytest.raises(ValidationError):
        ProfileFacts(**facts(**changes))


def test_inference_uses_safe_json_weights(model_path):
    result = score_profile(ProfileFacts(**facts()))
    assert result['risk_score'] == 0.5
    assert result['provider'] == 'profile_ml'
    assert result['model'] == 'test-logreg'
    assert result['human_review_required'] is True
    assert 'impersonation' in result['limitations'][0]


def test_missing_model_is_explicit(monkeypatch, tmp_path):
    monkeypatch.setattr(config, 'ML_MODEL_PATH', tmp_path / 'absent.json')
    with pytest.raises(ComparisonUnavailable) as error:
        score_profile(ProfileFacts(**facts()))
    assert error.value.code == 'ml_model_unavailable'


def test_corrupt_model_rejected(model_path):
    data = json.loads(model_path.read_text())
    data['scale'][0] = 0
    model_path.write_text(json.dumps(data))
    with pytest.raises(ComparisonUnavailable):
        score_profile(ProfileFacts(**facts()))


def test_v2_profile_risk_is_invariant_to_a_default_avatar(model_path):
    data = json.loads(model_path.read_text())
    features = [f for f in FEATURES if f != 'profile_pic']
    data.update(artifact_version=2, model_id='profile-logreg-v2-no-avatar', features=features,
                mean=[0.0] * 8, scale=[1.0] * 8, coefficients=[0.1] * 8)
    model_path.write_text(json.dumps(data))
    with_avatar = score_profile(ProfileFacts(**facts(has_profile_picture=True)))
    without_avatar = score_profile(ProfileFacts(**facts(has_profile_picture=False)))
    assert with_avatar['risk_score'] == without_avatar['risk_score']
    assert 'profile_pic' in without_avatar['ignored_features']
    assert all(f['feature'] != 'profile_pic' for f in without_avatar['factors'])


def test_out_of_training_range_is_flagged(model_path):
    data = json.loads(model_path.read_text())
    data['training_bounds']['num_followers'] = [0, 10]
    model_path.write_text(json.dumps(data))
    result = score_profile(ProfileFacts(**facts()))
    assert 'num_followers' in result['out_of_range_features']


def test_profile_risk_endpoint_needs_no_meta_key(client, model_path):
    response = client.post('/ml/profile-risk', json=facts())
    assert response.status_code == 200
    assert response.json()['risk_score'] == 0.5


def test_claim_keeps_ml_risk_separate_and_under_review(client, make_image, png, model_path):
    image = png(make_image())
    response = client.post('/claims', data={
        'owner': 'alice', 'suspect': 'alice_fake', 'profile_facts': json.dumps(facts()),
    }, files={'original': ('o.png', image, 'image/png'), 'suspect_image': ('s.png', image, 'image/png')})
    assert response.status_code == 200
    result = response.json()
    assert result['analysis']['provider'] == 'local'
    assert result['analysis']['profile_ml']['risk_score'] == 0.5
    assert result['score'] > 0.8
    assert result['status'] == 'under_review'
    assert client.get('/claims', params={'handle': 'alice_fake'}).json()[0]['analysis'] == result['analysis']


@pytest.mark.parametrize('profile', ['{bad json', json.dumps(facts(handle='someone_else'))])
def test_bad_or_mismatched_facts_do_not_save_claim(client, make_image, png, model_path, profile):
    image = png(make_image())
    response = client.post('/claims', data={'owner': 'alice', 'suspect': 'alice_fake', 'profile_facts': profile},
        files={'original': ('o.png', image, 'image/png'), 'suspect_image': ('s.png', image, 'image/png')})
    assert response.status_code == 422
    assert not pipeline.DB.exists()


def test_ml_status_exposes_model_metadata(client, model_path):
    status = client.get('/analysis/status').json()
    assert status['profile_ml']['ready'] is True
    assert status['profile_ml']['model'] == 'test-logreg'


def test_meta_and_ml_outputs_coexist_without_score_blending(client, make_image, png, model_path, monkeypatch):
    from src.models import ComparisonResult

    class MetaResult:
        def analyze(self, *args, **kwargs):
            return ComparisonResult(0.2, ['Visible screenshot differences'], {'provider': 'meta', 'model': 'muse-spark-1.3'})

    monkeypatch.setattr(pipeline, 'get_comparer', lambda: MetaResult())
    image = png(make_image())
    response = client.post('/claims', data={
        'owner': 'alice_fake', 'suspect': 'alice_fake', 'profile_facts': json.dumps(facts()),
    }, files={'original': ('o.png', image, 'image/png'), 'suspect_image': ('s.png', image, 'image/png')})
    assert response.status_code == 200
    result = response.json()
    assert result['score'] == pytest.approx(0.8 * 0.2 + 0.2 * 1.0)
    assert result['analysis']['provider'] == 'meta'
    assert result['analysis']['profile_ml']['risk_score'] == 0.5
    assert result['status'] == 'under_review'
