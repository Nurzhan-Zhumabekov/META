"""Profile metadata risk, independent of screenshot similarity and identity decisions."""
import hashlib
import json
import math
from functools import lru_cache
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from . import config
from .errors import ComparisonUnavailable

FEATURES = (
    'profile_pic', 'ratio_numlen_username', 'ratio_numlen_fullname', 'len_desc',
    'extern_url', 'private', 'num_posts', 'num_followers', 'num_following',
)
LOG_FEATURES = {'len_desc', 'num_posts', 'num_followers', 'num_following'}
NO_AVATAR_FEATURES = tuple(f for f in FEATURES if f != 'profile_pic')
LABELS = {
    'profile_pic': 'Profile picture', 'ratio_numlen_username': 'Digits in username',
    'ratio_numlen_fullname': 'Digits in display name', 'len_desc': 'Bio length',
    'extern_url': 'External link', 'private': 'Account visibility',
    'num_posts': 'Post count', 'num_followers': 'Follower count', 'num_following': 'Following count',
}
LIMITATIONS = [
    'This model estimates fake/spam-like profile patterns, not impersonation or identity.',
    'Training data are small, balanced and old; the score is not a calibrated real-world probability.',
    'Profile facts are user-supplied and not verified against Instagram. A human reviewer must decide.',
]


class ProfileText(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    handle: str = Field(min_length=1, max_length=31, pattern=r'^@?[A-Za-z0-9_.]{1,30}$')
    display_name: str = Field(max_length=100)
    bio: str = Field(max_length=500)


class ProfileFacts(ProfileText):
    has_profile_picture: bool
    has_external_url: bool
    is_private: bool
    num_posts: int = Field(ge=0, le=2_147_483_647)
    num_followers: int = Field(ge=0, le=2_147_483_647)
    num_following: int = Field(ge=0, le=2_147_483_647)


def raw_features(profile: ProfileFacts) -> list[float]:
    handle = profile.handle.lstrip('@')
    ratio = lambda s: sum(c.isdigit() for c in s) / len(s) if s else 0.0
    return [
        float(profile.has_profile_picture), ratio(handle), ratio(profile.display_name), float(len(profile.bio)),
        float(profile.has_external_url), float(profile.is_private),
        float(profile.num_posts), float(profile.num_followers), float(profile.num_following),
    ]


def feature_vector(profile: ProfileFacts) -> list[float]:
    return [math.log1p(v) if name in LOG_FEATURES else v for name, v in zip(FEATURES, raw_features(profile))]


@lru_cache(maxsize=4)
def _load_model(path: str, mtime: int, size: int) -> dict:
    try:
        raw = Path(path).read_bytes()
        if len(raw) > 2_000_000:
            raise ValueError('Model too large')
        model = json.loads(raw)
        expected = FEATURES if model['artifact_version'] == 1 else NO_AVATAR_FEATURES if model['artifact_version'] == 2 else ()
        if not expected or model['features'] != list(expected):
            raise ValueError('Unsupported artifact')
        for name in ['mean', 'scale', 'coefficients']:
            values = model[name]
            if len(values) != len(expected) or not all(type(v) in {int, float} and math.isfinite(v) for v in values):
                raise ValueError('Invalid weights')
        if not all(v > 0 for v in model['scale']) or not math.isfinite(model['intercept']):
            raise ValueError('Invalid scaling')
        model['sha256'] = hashlib.sha256(raw).hexdigest()
        return model
    except (OSError, ValueError, TypeError, KeyError):
        raise ComparisonUnavailable('ml_model_unavailable', 'Profile ML model is missing or invalid. Run scripts/train_profile_ml.py first.', 503) from None


def load_model() -> dict:
    if not config.ML_ENABLED:
        raise ComparisonUnavailable('ml_disabled', 'Profile ML analysis is disabled on the server.', 503)
    try:
        p = Path(config.ML_MODEL_PATH)
        stat = p.stat()
    except OSError:
        raise ComparisonUnavailable('ml_model_unavailable', 'Profile ML model is not trained yet. Run scripts/train_profile_ml.py first.', 503) from None
    return _load_model(str(p.resolve()), stat.st_mtime_ns, stat.st_size)


def model_status() -> dict:
    try:
        model = load_model()
    except ComparisonUnavailable as error:
        return {'ready': False, 'enabled': config.ML_ENABLED, 'code': error.code}
    return {
        'ready': True, 'enabled': True, 'model': model['model_id'],
        'features': len(model['features']), 'metrics': model.get('metrics', {}),
        'ignored_features': [f for f in FEATURES if f not in model['features']],
        'human_review_required': True,
    }


def score_profile(profile: ProfileFacts) -> dict:
    model = load_model()
    selected = model['features']
    all_raw, all_transformed = raw_features(profile), feature_vector(profile)
    raw = [all_raw[FEATURES.index(f)] for f in selected]
    transformed = [all_transformed[FEATURES.index(f)] for f in selected]
    contributions = [c * (v - m) / s for c, v, m, s in zip(model['coefficients'], transformed, model['mean'], model['scale'])]
    logit = float(model['intercept']) + sum(contributions)
    score = 1 / (1 + math.exp(-min(max(logit, -700), 700)))
    bounds = model.get('training_bounds', {})
    out_of_range = [f for f, v in zip(selected, raw) if f in bounds and not bounds[f][0] <= v <= bounds[f][1]]
    ranked = sorted(zip(selected, raw, contributions), key=lambda row: abs(row[2]), reverse=True)[:4]
    return {
        'provider': 'profile_ml', 'model': model['model_id'], 'model_sha256': model['sha256'],
        'risk_score': score, 'risk_band': 'high' if score >= 0.7 else 'medium' if score >= 0.3 else 'low',
        'factors': [{'feature': f, 'label': LABELS[f], 'value': value, 'contribution': contribution,
                    'direction': 'raises' if contribution > 0 else 'lowers' if contribution < 0 else 'neutral'}
                   for f, value, contribution in ranked],
        'out_of_range_features': out_of_range, 'limitations': LIMITATIONS,
        'ignored_features': [f for f in FEATURES if f not in selected],
        'human_review_required': True, 'facts_source': 'user_provided',
    }
