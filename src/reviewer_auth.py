"""Local web reviewer sessions. Secrets are never sent to the frontend build."""
import secrets
import threading
import time

from fastapi import HTTPException, Request

from . import config
from . import demo_sessions

COOKIE = 'reviewer_session'
SESSION_SECONDS = 3600
_sessions: dict[str, tuple[float, str]] = {}
_lock = threading.Lock()


def check_origin(request: Request) -> None:
    expected = f'{request.url.scheme}://{request.headers.get("host", "")}'
    if request.headers.get('origin') != expected:
        raise HTTPException(403, 'Reviewer actions require the same origin.')


def token_valid(token: str | None) -> bool:
    return bool(token and config.ADMIN_TOKEN and secrets.compare_digest(token.encode(), config.ADMIN_TOKEN.encode()))


def new_session() -> str:
    value = secrets.token_urlsafe(32)
    with _lock:
        now = time.monotonic()
        expired = [key for key, (until, _) in _sessions.items() if until <= now]
        for key in expired:
            _sessions.pop(key, None)
        if len(_sessions) >= 256:
            _sessions.pop(next(iter(_sessions)))
        _sessions[value] = (now + SESSION_SECONDS, config.ADMIN_TOKEN)
    return value


def revoke_session(value: str | None) -> None:
    with _lock:
        _sessions.pop(value, None)


def require_reviewer(request: Request, header: str | None) -> None:
    if config.PUBLIC_DEMO_ENABLED:
        if not demo_sessions.workspace.get() or not demo_sessions.reviewer.get():
            raise HTTPException(401, 'Enter the moderator sandbox to review this session.')
        if request.method not in {'GET', 'HEAD', 'OPTIONS'}:
            check_origin(request)
        return
    if not config.ADMIN_TOKEN:
        raise HTTPException(503, 'Reviewer endpoints are disabled: ADMIN_TOKEN is not configured')
    if header is not None:
        if not token_valid(header):
            raise HTTPException(401, 'Invalid or missing X-Admin-Token')
        return
    cookie = request.cookies.get(COOKIE)
    with _lock:
        session = _sessions.get(cookie)
    if not session or session[0] <= time.monotonic() or not token_valid(session[1]):
        raise HTTPException(401, 'Reviewer sign-in required')
    if request.method not in {'GET', 'HEAD', 'OPTIONS'}:
        check_origin(request)
