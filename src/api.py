import io
import re
import threading
from typing import Literal

from fastapi import Body, Depends, FastAPI, File, Form, Header, HTTPException, UploadFile, Request, Response
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
from . import moderation
from . import demo_sessions
from . import screenshot_tools
from . import meta_availability
from .reviewer_auth import COOKIE, SESSION_SECONDS, check_origin, new_session, require_reviewer, revoke_session, token_valid

app = FastAPI(title="Fake Account Report API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8090", "http://localhost:8090"],
    allow_methods=["*"],
    allow_headers=["*"],
)

MAX_BYTES = 5 * 1024 * 1024
_public_analysis_slots = threading.BoundedSemaphore(2)


@app.middleware('http')
async def isolate_public_demo(request: Request, call_next):
    if not config.PUBLIC_DEMO_ENABLED:
        return await call_next(request)
    identity = demo_sessions.decode(request.cookies.get(demo_sessions.COOKIE))
    allowed = {'/analysis/status', '/demo/session'}
    route_path = request.url.path.removeprefix(request.scope.get('root_path', ''))
    if not identity and route_path not in allowed:
        return JSONResponse({'detail': 'Start an isolated demonstration session.'}, status_code=401)
    if request.method not in {'GET', 'HEAD', 'OPTIONS'}:
        try:
            check_origin(request)
        except HTTPException as error:
            return JSONResponse({'detail': error.detail}, status_code=error.status_code)
    scope = demo_sessions.workspace.set(identity)
    role = demo_sessions.reviewer.set(demo_sessions.has_role(request.cookies.get(demo_sessions.ROLE_COOKIE), identity))
    limited = request.method == 'POST' and route_path in {'/claims', '/evidence/inspect'}
    acquired = False
    try:
        if limited:
            try:
                length = int(request.headers.get('content-length', '0'))
            except ValueError:
                return JSONResponse({'detail': 'Invalid upload length.'}, status_code=400)
            if not 0 < length <= 12*1024*1024:
                return JSONResponse({'detail': 'Upload exceeds the 12 MB request limit or has no declared length.'}, status_code=413)
            acquired = _public_analysis_slots.acquire(blocking=False)
            if not acquired:
                return JSONResponse({'detail': 'Analysis is busy. Try again shortly.'}, status_code=429)
            if route_path == '/claims' and len(all_claims()) >= 3:
                return JSONResponse({'detail': 'This session has reached its three-report limit.'}, status_code=429)
        response = await call_next(request)
        response.headers['Cache-Control'] = 'private, no-store'
        return response
    finally:
        if acquired:
            _public_analysis_slots.release()
        demo_sessions.workspace.reset(scope)
        demo_sessions.reviewer.reset(role)


@app.get('/demo/session')
def demo_session():
    return {'enabled': config.PUBLIC_DEMO_ENABLED, 'active': bool(demo_sessions.workspace.get()),
            'moderator': demo_sessions.reviewer.get(), 'expires_after_seconds': demo_sessions.LIFETIME}


@app.post('/demo/session')
def start_demo(request: Request, response: Response):
    if not config.PUBLIC_DEMO_ENABLED:
        raise HTTPException(404, 'Public demonstration mode is disabled.')
    check_origin(request)
    if demo_sessions.workspace.get():
        return {'enabled': True, 'active': True, 'expires_after_seconds': demo_sessions.LIFETIME}
    value = demo_sessions.new_cookie()
    demo_sessions.admit(value.split('.')[0], request.client.host if request.client else 'unknown')
    response.set_cookie(demo_sessions.COOKIE, value, max_age=demo_sessions.LIFETIME,
                        httponly=True, secure=request.url.scheme == 'https', samesite='strict', path='/')
    response.delete_cookie(demo_sessions.ROLE_COOKIE, path='/')
    return {'enabled': True, 'active': True, 'expires_after_seconds': demo_sessions.LIFETIME}


@app.post('/demo/reviewer')
def enter_demo_reviewer(request: Request, response: Response):
    if not config.PUBLIC_DEMO_ENABLED or not demo_sessions.workspace.get():
        raise HTTPException(401, 'Start an isolated demonstration session first.')
    check_origin(request)
    response.set_cookie(demo_sessions.ROLE_COOKIE, demo_sessions.role_cookie(demo_sessions.workspace.get()),
                        max_age=demo_sessions.LIFETIME, httponly=True, secure=request.url.scheme == 'https',
                        samesite='strict', path='/')
    return {'authenticated': True, 'scope': 'this_demo_session_only'}


@app.exception_handler(ComparisonUnavailable)
async def comparison_error(request, error: ComparisonUnavailable):
    return JSONResponse(status_code=error.status_code, content={"detail": str(error), "code": error.code})


@app.get("/analysis/status")
def analysis_status():
    meta_access = meta_availability.model_access() if config.COMPARER == 'meta' else None
    return {
        "provider": config.COMPARER,
        "public_demo": config.PUBLIC_DEMO_ENABLED,
        "model": config.META_MODEL if config.COMPARER == "meta" else None,
        "ready": meta_access['available'] if meta_access is not None else config.COMPARER in {"local", "mock"},
        "meta_key_configured": bool(config.META_API_KEY),
        "meta_model_access": meta_access,
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
    response.delete_cookie(demo_sessions.ROLE_COOKIE, path='/')
    return {'authenticated': False}


@app.get('/claims/{claim_id}/evidence/{kind}', dependencies=[Depends(require_admin)])
def claim_evidence(claim_id: str, kind: Literal['original', 'suspect']):
    if not re.fullmatch(r'[a-f0-9]{8}', claim_id) or not any(row['id'] == claim_id for row in all_claims()):
        raise HTTPException(404, 'Evidence not found')
    path = pipeline.active_db().parent / 'evidence' / claim_id / f'{kind}.jpg'
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
    return [moderation.reviewer_claim(r) for r in all_claims() if r["status"] == "under_review"]


@app.get("/claims")
def get_claims(handle: str):
    return [moderation.public_claim(row) for row in lookup(handle)]


class DecisionBody(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    status: Literal['confirmed', 'rejected']
    reason: str = Field(min_length=10, max_length=2000)
    expected_version: int = Field(ge=0)


@app.post("/claims/{claim_id}/status", dependencies=[Depends(require_admin)])
def update_status(claim_id: str, status: str | None = None, payload: DecisionBody | None = Body(default=None)):
    if payload is None and status not in {'confirmed', 'rejected'}:
        raise HTTPException(400, "Invalid status")
    if payload is None:
        moderation.find(all_claims(), claim_id)
        raise HTTPException(422, 'A reason and current report version are required.')
    moderation.decide(claim_id, payload.status, payload.reason, payload.expected_version)
    return {"ok": True}


@app.get('/claims/{claim_id}/history', dependencies=[Depends(require_admin)])
def history(claim_id: str, response: Response):
    row = moderation.find(all_claims(), claim_id)
    response.headers['Cache-Control'] = 'private, no-store'
    return {'events': row.get('history', []), 'version': row.get('version', 0),
            'legacy_decision_without_reason': row['status'] in {'confirmed', 'rejected'} and not row.get('history')}


@app.get('/reviewer/cases', dependencies=[Depends(require_admin)])
def reviewed_cases(response: Response):
    response.headers['Cache-Control'] = 'private, no-store'
    return [moderation.reviewer_claim(row) for row in all_claims()]


@app.post('/claims/{claim_id}/appeal-access', dependencies=[Depends(require_admin)])
def appeal_access(claim_id: str, response: Response):
    response.headers['Cache-Control'] = 'private, no-store'
    return moderation.issue_access(claim_id)


class AppealAccess(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    token: str = Field(min_length=1, max_length=128)


class AppealSubmission(AppealAccess):
    reason: str = Field(min_length=10, max_length=2000)


class AppealResolution(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    outcome: Literal['uphold', 'overturn']
    reason: str = Field(min_length=10, max_length=2000)
    expected_version: int = Field(ge=0)


@app.post('/appeals/access')
def open_appeal(payload: AppealAccess, response: Response):
    response.headers['Cache-Control'] = 'private, no-store'
    return moderation.appeal_detail(payload.token)


@app.post('/appeals', status_code=201)
def appeal(payload: AppealSubmission, response: Response):
    response.headers['Cache-Control'] = 'private, no-store'
    return moderation.submit_appeal(payload.token, payload.reason)


@app.get('/appeals/pending', dependencies=[Depends(require_admin)])
def appeal_queue(response: Response):
    response.headers['Cache-Control'] = 'private, no-store'
    return moderation.pending_appeals()


@app.post('/appeals/{appeal_id}/resolve', dependencies=[Depends(require_admin)])
def resolve_appeal(appeal_id: str, payload: AppealResolution):
    moderation.resolve(appeal_id, payload.outcome, payload.reason, payload.expected_version)
    return {'ok': True}
