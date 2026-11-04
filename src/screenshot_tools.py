"""Validated worker client and short-lived screenshot-bound inspection tickets."""
import hashlib
import io
import secrets
import threading
import time
from collections import OrderedDict
from typing import Annotated, Literal

import httpx
from PIL import ImageOps
from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator

from evidence_tools.worker_auth import worker_key
from .errors import ComparisonUnavailable
from .evidence_redaction import redact_pair

Rect = Annotated[list[Annotated[float, Field(ge=0, le=1)]], Field(min_length=4, max_length=4)]


class Strict(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True, allow_inf_nan=False)


class Observation(Strict):
    value: str | int
    confidence: float = Field(ge=0, le=1)
    approximate: bool = False


class Finding(Strict):
    entity_type: Literal['EMAIL_ADDRESS', 'PHONE_NUMBER', 'CREDIT_CARD', 'IBAN_CODE', 'IP_ADDRESS']
    confidence: float = Field(ge=0, le=1)
    box: Rect


class Privacy(Strict):
    provider: Literal['presidio']
    findings: list[Finding] = Field(max_length=512)
    count: int = Field(ge=0, le=512)
    limitations: list[str] = Field(max_length=8)


class Profile(Strict):
    fields: dict[Literal['handle','display_name','bio','num_posts','num_followers','num_following'], Observation]
    warnings: list[str] = Field(max_length=20)
    width: int = Field(ge=1, le=1800)
    height: int = Field(ge=1, le=1800)
    privacy: Privacy
    recognized_lines: int = Field(ge=0, le=512)

    @model_validator(mode='after')
    def check_fields(self):
        for key, observation in self.fields.items():
            if key.startswith('num_'):
                if type(observation.value) is not int or not 0 <= observation.value <= 2_147_483_647:
                    raise ValueError('Invalid OCR count')
            elif type(observation.value) is not str or len(observation.value) > 500:
                raise ValueError('Invalid OCR text')
        if self.privacy.count != len(self.privacy.findings):
            raise ValueError('Inconsistent privacy count')
        return self


class Match(Strict):
    original_index: int = Field(ge=0, le=23)
    suspect_index: int = Field(ge=0, le=23)
    phash_distance: int = Field(ge=0, le=64)
    dhash_distance: int = Field(ge=0, le=64)
    pixel_correlation: float = Field(ge=0, le=1)


class Photos(Strict):
    provider: Literal['imagededup']
    method: str = Field(max_length=100)
    original_boxes: list[Rect] = Field(max_length=24)
    suspect_boxes: list[Rect] = Field(max_length=24)
    matches: list[Match] = Field(max_length=24)
    count: int = Field(ge=0, le=24)
    limitations: list[str] = Field(max_length=8)

    @model_validator(mode='after')
    def check_matches(self):
        if self.count != len(self.matches):
            raise ValueError('Inconsistent match count')
        if any(m.original_index >= len(self.original_boxes) or m.suspect_index >= len(self.suspect_boxes) for m in self.matches):
            raise ValueError('Invalid region index')
        return self


class Providers(Strict):
    ocr: Literal['paddleocr']
    photos: Literal['imagededup']
    privacy: Literal['presidio']


class Inspection(Strict):
    original: Profile
    suspect: Profile
    photos: Photos
    providers: Providers
    elapsed_seconds: float = Field(ge=0, le=600)


_tickets = OrderedDict()
_lock = threading.Lock()


def status():
    if not worker_key():
        return {'ready': False, 'code': 'evidence_tools_unconfigured'}
    try:
        with httpx.Client(trust_env=False, timeout=0.7) as client:
            response = client.get('http://127.0.0.1:8091/health')
            response.raise_for_status()
            return response.json()
    except (httpx.HTTPError, ValueError):
        return {'ready': False, 'code': 'evidence_tools_unavailable'}


def image_key(image):
    normalized = ImageOps.exif_transpose(image).convert('RGB')
    return hashlib.sha256(str(normalized.size).encode() + normalized.tobytes()).hexdigest()


def _image_bytes(image):
    normalized = ImageOps.exif_transpose(image).convert('RGB')
    normalized.thumbnail((1800,1800))
    output = io.BytesIO()
    normalized.save(output, 'PNG')
    return output.getvalue()


def inspect_backend(original, suspect, owner, handle):
    key = worker_key()
    if not key:
        raise ComparisonUnavailable('evidence_tools_unconfigured', 'The screenshot inspection service is not configured. Manual entry is available.', 503)
    try:
        with httpx.Client(trust_env=False, timeout=httpx.Timeout(120, connect=3)) as client:
            response = client.post('http://127.0.0.1:8091/inspect',
                headers={'X-Evidence-Key': key}, data={'owner': owner, 'suspect': handle},
                files={'original': ('original.png',_image_bytes(original),'image/png'),
                       'suspect_image': ('suspect.png',_image_bytes(suspect),'image/png')})
        if response.status_code == 429:
            raise ComparisonUnavailable('evidence_tools_busy', 'Screenshot inspection is busy. Try again in a few seconds.', 429)
        response.raise_for_status()
        return response.json()
    except (httpx.HTTPError, ValueError):
        raise ComparisonUnavailable('evidence_tools_unavailable', 'Local screenshot inspection did not respond. Retry or enter the details manually.', 503) from None


def inspect_images(original, suspect, owner, handle):
    try:
        parsed = Inspection.model_validate(inspect_backend(original, suspect, owner, handle)).model_dump()
    except ValidationError:
        raise ComparisonUnavailable('evidence_tools_invalid_response', 'The inspection result is incomplete or invalid. No fields were applied.', 503) from None
    redacted = redact_pair(original, suspect, parsed)
    identifier = secrets.token_urlsafe(24)
    with _lock:
        now = time.monotonic()
        for key in list(_tickets):
            if _tickets[key][0] < now:
                del _tickets[key]
        _tickets[identifier] = (now + 900, (image_key(original), image_key(suspect)), parsed)
        while len(_tickets) > 32:
            _tickets.popitem(last=False)
    return {**parsed, 'inspection_id': identifier, 'expires_in_seconds': 900,
            'redaction': {**redacted.audit, 'previews': dict(zip(['original','suspect'],redacted.urls))}}


def resolve(identifier, original, suspect):
    with _lock:
        entry = _tickets.get(identifier)
    if not entry or entry[0] < time.monotonic():
        raise ComparisonUnavailable('inspection_expired', 'The inspection has expired. Run the screenshot check again.', 409)
    if entry[1] != (image_key(original), image_key(suspect)):
        raise ComparisonUnavailable('inspection_mismatch', 'The screenshots changed after inspection. Run the check again.', 409)
    data = entry[2]
    # Store observations about tools, not raw OCR text or contact values, in claims.
    def summary(profile):
        return {k:v for k,v in profile.items() if k != 'fields'} | {
            'field_confidence': {name: item['confidence'] for name,item in profile['fields'].items()}}
    return {**data, 'original': summary(data['original']), 'suspect': summary(data['suspect']),
            'ocr_reviewed': True}
