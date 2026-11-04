import io
import re
from typing import Literal

from fastapi import Depends, FastAPI, File, Form, Header, HTTPException, UploadFile, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from starlette.concurrency import run_in_threadpool
from PIL import Image, UnidentifiedImageError
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from . import config
from .errors import ComparisonUnavailable
from .pipeline import _load as all_claims
from .pipeline import lookup, set_status, submit_claim
from .profile_ml import ProfileFacts, ProfileText, model_status, score_profile
from .pair_ml import PairFacts, pair_model_status, score_pair
from . import pipeline
from . import screenshot_tools
from .reviewer_auth import COOKIE, SESSION_SECONDS, check_origin, new_session, require_reviewer, revoke_session, token_valid

app = FastAPI(title="Fake Account Report API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8090", "http://localhost:8090"],
    allow_methods=["*"],
    allow_headers=["*"],
)

MAX_BYTES = 5 * 1024 * 1024


@app.exception_handler(ComparisonUnavailable)
async def comparison_error(request, error: ComparisonUnavailable):
    return JSONResponse(status_code=error.status_code, content={"detail": str(error), "code": error.code})


@app.get("/analysis/status")
def analysis_status():
    return {
        "provider": config.COMPARER,
        "model": config.META_MODEL if config.COMPARER == "meta" else None,
        "ready": bool(config.META_API_KEY) if config.COMPARER == "meta" else config.COMPARER in {"local", "mock"},
        "meta_key_configured": bool(config.META_API_KEY),
        "human_review_required": True,
        "profile_ml": model_status(),
        "pair_ml": pair_model_status(),
        "evidence_tools": screenshot_tools.status(),
        "privacy_redaction_required": config.COMPARER == 'meta',
    }


@app.post('/ml/profile-risk')
def profile_risk(profile: ProfileFacts):
    return score_profile(profile)


@app.post('/ml/pair-risk')
def pair_risk(pair: PairFacts):
    return score_pair(pair.original, pair.suspect)


def require_admin(request: Request, x_admin_token: str | None = Header(default=None)) -> None:
    require_reviewer(request, x_admin_token)


class ReviewerLogin(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    token: str = Field(min_length=1, max_length=512)


@app.post('/reviewer/session')
def reviewer_login(payload: ReviewerLogin, request: Request, response: Response):
    check_origin(request)
    if not config.ADMIN_TOKEN:
        raise HTTPException(503, 'Reviewer access is not configured')
    if not token_valid(payload.token):
        raise HTTPException(401, 'Invalid reviewer code')
    response.set_cookie(COOKIE, new_session(), max_age=SESSION_SECONDS, httponly=True,
                        secure=request.url.scheme == 'https', samesite='strict', path='/')
    response.headers['Cache-Control'] = 'no-store'
    return {'authenticated': True}


@app.get('/reviewer/session', dependencies=[Depends(require_admin)])
def reviewer_session():
    return {'authenticated': True}


@app.delete('/reviewer/session', dependencies=[Depends(require_admin)])
def reviewer_logout(request: Request, response: Response):
    revoke_session(request.cookies.get(COOKIE))
    response.delete_cookie(COOKIE, path='/')
    return {'authenticated': False}


@app.get('/claims/{claim_id}/evidence/{kind}', dependencies=[Depends(require_admin)])
def claim_evidence(claim_id: str, kind: Literal['original', 'suspect']):
    if not re.fullmatch(r'[a-f0-9]{8}', claim_id) or not any(row['id'] == claim_id for row in all_claims()):
        raise HTTPException(404, 'Evidence not found')
    path = pipeline.DB.parent / 'evidence' / claim_id / f'{kind}.jpg'
    if not path.is_file():
        raise HTTPException(404, 'Evidence not saved for this earlier report')
    return FileResponse(path, media_type='image/jpeg', headers={'Cache-Control': 'private, no-store', 'X-Content-Type-Options': 'nosniff'})


async def _read_image(f: UploadFile) -> Image.Image:
    data = await f.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise HTTPException(413, "Image too large (max 5 MB)")
    try:
        image = Image.open(io.BytesIO(data))
        if image.width * image.height > 16_000_000:
            raise HTTPException(413, "Image dimensions are too large (max 16 megapixels)")
        image.load()
        return image
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError):
        raise HTTPException(400, "Not a valid image")


@app.post('/evidence/inspect')
async def inspect_evidence(request: Request, response: Response,
    original: UploadFile = File(...), suspect_image: UploadFile = File(...),
    owner: str = Form('', max_length=31), suspect: str = Form('', max_length=31)):
    check_origin(request)
    result = await run_in_threadpool(screenshot_tools.inspect_images,
        await _read_image(original), await _read_image(suspect_image), owner, suspect)
    response.headers['Cache-Control'] = 'private, no-store'
    return result


@app.post("/claims")
async def create_claim(
    owner: str = Form(...),
    suspect: str = Form(...),
    original: UploadFile = File(...),
    suspect_image: UploadFile = File(...),
    profile_facts: str | None = Form(default=None, max_length=5000),
    original_profile_facts: str | None = Form(default=None, max_length=5000),
    inspection_id: str | None = Form(default=None, max_length=128),
    ocr_reviewed: bool = Form(default=False),
    pii_acknowledged: bool = Form(default=False),
):
    profile = None
    if profile_facts is not None:
        try:
            profile = ProfileFacts.model_validate_json(profile_facts)
        except ValidationError:
            raise HTTPException(422, 'Profile facts must be valid JSON with explicit counts, text and boolean fields.') from None
        if profile.handle.lstrip('@').lower() != suspect.lstrip('@').lower():
            raise HTTPException(422, 'Profile facts must describe the suspect account.')
    original_profile = None
    if original_profile_facts is not None:
        try:
            original_profile = ProfileText.model_validate_json(original_profile_facts)
        except ValidationError:
            raise HTTPException(422, 'Original profile facts must be valid JSON.') from None
        if original_profile.handle.lstrip('@').lower() != owner.lstrip('@').lower():
            raise HTTPException(422, 'Original profile facts must describe the claimed owner.')
        if profile is None:
            raise HTTPException(422, 'Pair comparison requires explicit facts for both profiles.')
    original_image, candidate_image = await _read_image(original), await _read_image(suspect_image)
    inspection = None
    if inspection_id:
        if not ocr_reviewed:
            raise HTTPException(422, 'Review the recognized data before submitting.')
        inspection = screenshot_tools.resolve(inspection_id, original_image, candidate_image)
        # Legacy pii_acknowledged is accepted but cannot bypass redaction.
    kwargs = {'evidence_inspection': inspection} if inspection else {}
    claim = await run_in_threadpool(submit_claim, owner, suspect, original_image, candidate_image, profile, original_profile, **kwargs)
    return claim.to_dict()


@app.get("/statuses")
def get_statuses():
    """suspect handle -> strongest status ('confirmed' beats 'under_review'); rejected claims are hidden."""
    rank = {"under_review": 1, "confirmed": 2}
    out: dict[str, str] = {}
    for r in all_claims():
        s = r["status"]
        if s in rank and rank[s] > rank.get(out.get(r["suspect_handle"], ""), 0):
            out[r["suspect_handle"]] = s
    return out


@app.get("/claims/pending", dependencies=[Depends(require_admin)])
def get_pending():
    return [r for r in all_claims() if r["status"] == "under_review"]


@app.get("/claims")
def get_claims(handle: str):
    return lookup(handle)


@app.post("/claims/{claim_id}/status", dependencies=[Depends(require_admin)])
def update_status(claim_id: str, status: str):
    if status not in {"under_review", "confirmed", "rejected"}:
        raise HTTPException(400, "Invalid status")
    if not set_status(claim_id, status):
        raise HTTPException(404, "Claim not found")
    return {"ok": True}
