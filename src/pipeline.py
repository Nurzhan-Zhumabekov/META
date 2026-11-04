import os
import io
import uuid
from difflib import SequenceMatcher
from pathlib import Path

from PIL import Image, ImageOps

from .clients import get_comparer
from .models import Claim
from .profile_ml import ProfileFacts, ProfileText, score_profile
from .pair_ml import score_pair
from .meta_compare import MetaComparer
from . import storage, demo_sessions
from .evidence_redaction import redact_pair

# Anchored to the project root so the DB is the same file no matter the cwd.
DB = Path(os.getenv('CLAIMS_DB_PATH', str(Path(__file__).resolve().parent.parent / 'outputs' / 'claims.sqlite3')))
if not DB.is_absolute():
    DB = Path(__file__).resolve().parent.parent / DB


def active_db():
    return demo_sessions.database_path() or DB


def _read() -> list[dict]:
    return storage.read(active_db())


def _load() -> list[dict]:
    return _read()


def _save(rows: list[dict]) -> None:
    storage.replace(active_db(), rows)


def append_record(row):
    def append(rows):
        if demo_sessions.workspace.get() and len(rows) >= 3:
            from fastapi import HTTPException
            raise HTTPException(429, 'This demonstration accepts three reports per visitor session.')
        if any(item['id'] == row['id'] for item in rows):
            raise ValueError('Duplicate report ID')
        rows.append(row)
    storage.mutate(active_db(), append)


def submit_claim(owner: str, suspect: str, original: Image.Image, suspect_img: Image.Image, profile: ProfileFacts | None = None, original_profile: ProfileText | None = None, *, evidence_inspection: dict | None = None) -> Claim:
    profile_risk = score_profile(profile) if profile is not None else None
    pair_risk = score_pair(original_profile, profile) if original_profile is not None and profile is not None else None
    comparer = get_comparer()
    kwargs = {'privacy_inspection': evidence_inspection} if isinstance(comparer,MetaComparer) else {}
    images = (original, suspect_img)
    prepared = None
    if evidence_inspection is not None and not isinstance(comparer,MetaComparer):
        prepared = redact_pair(original,suspect_img,evidence_inspection)
        processed = []
        for raw in prepared.raw:
            with Image.open(io.BytesIO(raw)) as image:
                processed.append(image.convert('RGB'))
        images = tuple(processed)
    comparison = comparer.analyze(*images, owner_handle=owner, suspect_handle=suspect, **kwargs)
    if prepared is not None:
        comparison.provider_images = prepared.raw
        comparison.analysis['privacy_redaction'] = prepared.audit
    if profile_risk is not None:
        comparison.analysis['profile_ml'] = profile_risk
    if pair_risk is not None:
        comparison.analysis['pair_ml'] = pair_risk
    if evidence_inspection is not None:
        comparison.analysis['screenshot_tools'] = evidence_inspection
    img_score, reasons = comparison.image_score, comparison.reasons
    name_sim = SequenceMatcher(None, owner.lstrip("@").lower(), suspect.lstrip("@").lower()).ratio()
    reasons = [*reasons, f"Handle similarity: {name_sim:.0%}"]
    score = 0.8 * img_score + 0.2 * name_sim
    claim = Claim(uuid.uuid4().hex[:8], suspect.lstrip("@"), owner.lstrip("@"), score, reasons, "under_review", comparison.analysis)
    evidence_dir = active_db().parent / 'evidence' / claim.id
    evidence_dir.mkdir(parents=True, exist_ok=False)
    written = []
    try:
        for index, (kind, image) in enumerate([('original', original), ('suspect', suspect_img)]):
            path = evidence_dir / f'{kind}.jpg'
            if comparison.provider_images is not None:
                # Byte-identical to the privacy preview and actual Meta payload.
                path.write_bytes(comparison.provider_images[index])
            else:
                normalized = ImageOps.exif_transpose(image).convert('RGB')
                normalized.thumbnail((1280, 1280), Image.Resampling.LANCZOS)
                normalized.save(path, 'JPEG', quality=90)
            written.append(path)
            claim.evidence[kind] = f'/claims/{claim.id}/evidence/{kind}'
        append_record(claim.to_dict())
    except BaseException:
        for path in written:
            path.unlink(missing_ok=True)
        evidence_dir.rmdir()
        raise
    return claim


def lookup(handle: str) -> list[dict]:
    h = handle.lstrip("@")
    return [r for r in _load() if r["suspect_handle"] == h]


def set_status(claim_id: str, status: str) -> bool:
    def update(rows):
        for r in rows:
            if r["id"] == claim_id:
                r["status"] = status
                return True
        return False
    return storage.mutate(active_db(), update)
