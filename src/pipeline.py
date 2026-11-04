import json
import os
import tempfile
import threading
import uuid
from difflib import SequenceMatcher
from pathlib import Path

from PIL import Image, ImageOps

from .clients import get_comparer
from .models import Claim
from .profile_ml import ProfileFacts, ProfileText, score_profile
from .pair_ml import score_pair
from .meta_compare import MetaComparer

# Anchored to the project root so the DB is the same file no matter the cwd.
DB = Path(__file__).resolve().parent.parent / "outputs" / "claims.json"
# Guards load-modify-save within this process; separate processes (API + Gradio) are not covered.
_lock = threading.Lock()


def _read() -> list[dict]:
    return json.loads(DB.read_text("utf-8")) if DB.exists() else []


def _load() -> list[dict]:
    # Locked so a read never overlaps os.replace (which fails on Windows if the file is open).
    with _lock:
        return _read()


def _save(rows: list[dict]) -> None:
    """Write to a temp file in the same directory, then atomically swap it in."""
    DB.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=DB.parent, prefix=DB.name, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(rows, f, ensure_ascii=False, indent=2)
        os.replace(tmp, DB)
    except BaseException:
        os.unlink(tmp)
        raise


def submit_claim(owner: str, suspect: str, original: Image.Image, suspect_img: Image.Image, profile: ProfileFacts | None = None, original_profile: ProfileText | None = None, *, evidence_inspection: dict | None = None) -> Claim:
    profile_risk = score_profile(profile) if profile is not None else None
    pair_risk = score_pair(original_profile, profile) if original_profile is not None and profile is not None else None
    comparer = get_comparer()
    kwargs = {'privacy_inspection': evidence_inspection} if isinstance(comparer,MetaComparer) else {}
    comparison = comparer.analyze(original, suspect_img, owner_handle=owner, suspect_handle=suspect, **kwargs)
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
    evidence_dir = DB.parent / 'evidence' / claim.id
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
        with _lock:
            _save(_read() + [claim.to_dict()])
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
    with _lock:
        rows = _read()
        for r in rows:
            if r["id"] == claim_id:
                r["status"] = status
                _save(rows)
                return True
    return False
