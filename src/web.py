"""Same-origin native web app and API. Build web/ before starting this module."""
import re
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse

from .api import app as api

WEB_DIST = Path(__file__).resolve().parent.parent / 'web' / 'dist'
app = FastAPI(title='Instagram feature concept', docs_url=None, redoc_url=None)
app.mount('/api', api)


@app.get('/healthz')
def health():
    from . import config, screenshot_tools
    from .profile_ml import model_status
    from .pair_ml import pair_model_status
    ready = (model_status().get('ready', False) and pair_model_status().get('ready', False)
             and screenshot_tools.status().get('ready', False)
             and (config.COMPARER != 'meta' or bool(config.META_API_KEY))
             and (not config.PUBLIC_DEMO_ENABLED or bool(config.DEMO_SESSION_SECRET)))
    return JSONResponse({'ready': bool(ready), 'human_review_required': True}, status_code=200 if ready else 503)


@app.get('/{path:path}')
def web_page(path: str):
    target = (WEB_DIST / path).resolve()
    if not target.is_relative_to(WEB_DIST.resolve()):
        raise HTTPException(404)
    if target.is_file():
        cache = 'no-store' if target.suffix.lower() == '.html' else 'public, max-age=3600'
        return FileResponse(target, headers={'Cache-Control': cache})
    profile_route = re.fullmatch(r'(?:profile|messages)/@?[A-Za-z0-9_.]{1,30}', path) is not None
    if not profile_route and Path(path).suffix.lower() in {'.js', '.css', '.png', '.jpg', '.jpeg', '.webp', '.svg', '.ico', '.woff', '.woff2', '.map'}:
        raise HTTPException(404)
    index = WEB_DIST / 'index.html'
    if not index.is_file():
        return JSONResponse({'detail': 'Web build missing. Run npm ci and npm run build in web/.'}, status_code=503)
    return FileResponse(index, headers={'Cache-Control': 'no-store'})
