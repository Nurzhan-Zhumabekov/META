"""Learned text-reuse signal for explicit profile pairs, independent of Meta.

Training data are synthetic. No image OCR, identity inference or automatic verdict.
"""
import hashlib
import json
import math
import re
import unicodedata
from difflib import SequenceMatcher
from functools import lru_cache
from pathlib import Path

from pydantic import BaseModel, ConfigDict

from . import config
from .errors import ComparisonUnavailable
from .profile_ml import ProfileText

PAIR_FEATURES = ('name_similarity', 'handle_similarity', 'owner_handle_contained',
                 'bio_similarity', 'distinctive_bio_reuse', 'contact_reuse',
                 'name_bio_interaction', 'disclosure')
LABELS = ('Name match', 'Username similarity', 'Original username contained in the other username',
          'Bio similarity', 'Distinctive bio word reuse', 'Reused contact detail or domain',
          'Combined name and bio match', 'Fan page or parody disclosure')
GENERIC = set('a an the and or in at of for to my your is i me we our with official original '
              'photo photos photographer photography travel life lifestyle love welcome blog blogger '
              'personal account page daily studio link bio bookings book follow music art '
              'и в на я мы для по мой моя фото фотограф фотография путешествия блог '
              'личный аккаунт страница жизнь добро пожаловать'.split())
DISCLOSURE = re.compile(r'\b(?:unofficial|fan(?:page|s)?|parody|satire|fanclub|фан(?:атская|страница)?|пародия|неофициальн\w*)\b', re.I)
CONTACT = re.compile(r'(?:[\w.+-]+@[\w.-]+\.[a-z]{2,}|(?:https?://)?(?:[a-z0-9-]+\.)+[a-z]{2,}(?:/[\w/-]*)?)', re.I)
LIMITATIONS = [
    'Trained on synthetic pairs; performance on real accounts has not been established.',
    'This score describes text reuse, not the probability of impersonation or account ownership.',
    'Both profiles were described by the user and were not verified against Instagram; this text model does not read screenshots.',
    'The avatar and follower/following counts are not used. A moderator makes the decision.',
]


class PairFacts(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    original: ProfileText
    suspect: ProfileText


def normalize(text):
    return ' '.join(re.findall(r'\w+', unicodedata.normalize('NFKC', text).casefold()))


def _similarity(a, b):
    return SequenceMatcher(None, a, b, autojunk=False).ratio() if a and b else 0.0


def pair_features(original, suspect):
    name_a, name_b = normalize(original.display_name), normalize(suspect.display_name)
    handle_a, handle_b = normalize(original.handle.lstrip('@')), normalize(suspect.handle.lstrip('@'))
    bio_a, bio_b = normalize(original.bio), normalize(suspect.bio)
    distinctive_a, distinctive_b = set(bio_a.split()) - GENERIC, set(bio_b.split()) - GENERIC
    shared = distinctive_a & distinctive_b
    # A single common word is not distinctive reuse; added suffix text cannot
    # erase reuse of the original bio (including a prompt injection in the bio).
    reuse = len(shared) / len(distinctive_a) if len(shared) >= 2 and distinctive_a else 0.0
    contacts_a = {c.lower().removeprefix('https://').removeprefix('http://') for c in CONTACT.findall(original.bio)}
    contacts_b = {c.lower().removeprefix('https://').removeprefix('http://') for c in CONTACT.findall(suspect.bio)}
    name_similarity = _similarity(name_a, name_b)
    return [name_similarity, _similarity(handle_a, handle_b),
            float(len(handle_a) >= 5 and handle_a in handle_b and handle_a != handle_b),
            _similarity(bio_a, bio_b), reuse, float(bool(contacts_a & contacts_b)),
            name_similarity * reuse, float(bool(DISCLOSURE.search(unicodedata.normalize('NFKC', suspect.bio))))]


@lru_cache(maxsize=4)
def _load(path, mtime, size):
    try:
        raw = Path(path).read_bytes()
        if len(raw) > 2_000_000:
            raise ValueError('Oversized model')
        model = json.loads(raw)
        if model['artifact_version'] != 1 or model['features'] != list(PAIR_FEATURES):
            raise ValueError('Unsupported model')
        for key in ['mean', 'scale', 'coefficients']:
            if len(model[key]) != len(PAIR_FEATURES) or not all(type(v) in {int, float} and math.isfinite(v) for v in model[key]):
                raise ValueError('Invalid weights')
        if not all(v > 0 for v in model['scale']) or type(model['intercept']) not in {int, float} or not math.isfinite(model['intercept']):
            raise ValueError('Invalid scaling')
        if type(model['threshold']) not in {int, float} or not 0 < model['threshold'] < 1:
            raise ValueError('Invalid threshold')
        if not isinstance(model['model_id'], str) or len(model['model_id']) > 100:
            raise ValueError('Invalid model ID')
        model['sha256'] = hashlib.sha256(raw).hexdigest()
        return model
    except (OSError, ValueError, TypeError, KeyError):
        raise ComparisonUnavailable('pair_ml_unavailable', 'Pair ML model is missing or invalid. Run scripts/train_pair_ml.py.', 503) from None


def load_pair_model():
    if not config.ML_ENABLED:
        raise ComparisonUnavailable('ml_disabled', 'ML is disabled.', 503)
    try:
        path = Path(config.PAIR_ML_MODEL_PATH)
        stat = path.stat()
    except OSError:
        raise ComparisonUnavailable('pair_ml_unavailable', 'Pair ML is not trained yet. Run scripts/train_pair_ml.py.', 503) from None
    return _load(str(path.resolve()), stat.st_mtime_ns, stat.st_size)


def pair_model_status():
    try:
        model = load_pair_model()
        return {'ready': True, 'model': model['model_id'], 'training_data': 'synthetic', 'human_review_required': True}
    except ComparisonUnavailable as error:
        return {'ready': False, 'code': error.code}


def score_pair(original: ProfileText, suspect: ProfileText):
    model = load_pair_model()
    base = {'provider': 'pair_ml', 'model': model['model_id'], 'model_sha256': model['sha256'],
            'training_data': 'synthetic', 'facts_source': 'user_provided', 'human_review_required': True,
            'limitations': LIMITATIONS, 'threshold': model['threshold']}
    vector = pair_features(original, suspect)
    if original.handle.lstrip('@').casefold() == suspect.handle.lstrip('@').casefold() or not normalize(original.bio) or not normalize(suspect.bio):
        return {**base, 'risk_score': None, 'assessment': 'insufficient_evidence', 'factors': [],
                'reason': 'Two different profiles with non-empty bios are required for comparison.'}
    contributions = [c * (v - m) / s for c, v, m, s in zip(model['coefficients'], vector, model['mean'], model['scale'])]
    score = 1 / (1 + math.exp(-min(max(model['intercept'] + sum(contributions), -700), 700)))
    factors = [{'feature': f, 'label': label, 'value': v, 'contribution': contribution,
                'direction': 'raises' if contribution > 0 else 'lowers' if contribution < 0 else 'neutral'}
               for f, label, v, contribution in zip(PAIR_FEATURES, LABELS, vector, contributions)]
    return {**base, 'risk_score': score, 'assessment': 'needs_review' if score >= model['threshold'] else 'low_copy_signal',
            'factors': sorted(factors, key=lambda f: abs(f['contribution']), reverse=True)}
