from contextlib import asynccontextmanager
from importlib.metadata import version
import io
import threading
import time

import httpx
from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from PIL import Image, ImageOps, UnidentifiedImageError

from .layout import parse_profile
from .photos import compare_photos
from .vision import ocr_engine, read_text
from .worker_auth import require_key, worker_key

state = {'ready': False}
busy = threading.BoundedSemaphore(1)


def warm():
    try:
        ocr_engine()
        state.update(ready=True)
    except Exception as error:
        state.update(error=type(error).__name__)


@asynccontextmanager
async def lifespan(app):
    threading.Thread(target=warm, daemon=True).start()
    yield


app = FastAPI(lifespan=lifespan, docs_url=None, redoc_url=None)


def privacy_health():
    try:
        with httpx.Client(trust_env=False, timeout=1) as client:
            response = client.get('http://127.0.0.1:8092/health')
            response.raise_for_status()
            return response.json()
    except (httpx.HTTPError, ValueError):
        return {'ready': False}


@app.get('/health')
def health():
    privacy = privacy_health()
    return {**state, 'ready': state['ready'] and privacy.get('ready', False),
            'ocr': {'provider': 'paddleocr', 'version': version('paddleocr'),
                    'recognizer': 'cyrillic_PP-OCRv5_mobile_rec', 'device': 'cpu'},
            'photo_comparison': {'provider': 'imagededup', 'version': version('imagededup')},
            'privacy': privacy}


async def decode(upload):
    data = await upload.read(5 * 1024 * 1024 + 1)
    if len(data) > 5 * 1024 * 1024:
        raise HTTPException(413, 'Screenshot exceeds 5 MB')
    try:
        image = Image.open(io.BytesIO(data))
        if image.width * image.height > 16_000_000:
            raise HTTPException(413, 'Screenshot exceeds 16 megapixels')
        image = ImageOps.exif_transpose(image).convert('RGB')
        image.thumbnail((1800, 1800), Image.Resampling.LANCZOS)
        return image
    except (OSError, UnidentifiedImageError, Image.DecompressionBombError):
        raise HTTPException(400, 'Invalid screenshot') from None


def privacy_for(lines, image):
    text = '\n'.join(row['text'] for row in lines)
    if len(text) > 20000:
        raise HTTPException(422, 'Too much screenshot text to inspect safely')
    with httpx.Client(trust_env=False, timeout=30) as client:
        response = client.post('http://127.0.0.1:8092/analyze', json={'text': text},
                               headers={'X-Evidence-Key': worker_key()})
        if response.status_code != 200:
            raise HTTPException(503, 'Presidio privacy inspection is unavailable')
        privacy = response.json()
    offset = 0
    results = []
    for line in lines:
        for finding in privacy['findings']:
            if finding['start'] < offset + len(line['text']) and finding['end'] > offset:
                x,y,x2,y2 = line['box']
                results.append({'entity_type': finding['entity_type'], 'confidence': finding['confidence'],
                                'box': [x/image.width, y/image.height, x2/image.width, y2/image.height]})
        offset += len(line['text']) + 1
    return {'provider': 'presidio', 'findings': results, 'count': len(results),
            'limitations': privacy['limitations']}


def inspect_pair(original, suspect, owner, handle):
    if not busy.acquire(blocking=False):
        raise HTTPException(429, 'Another screenshot inspection is running. Try again shortly.')
    started = time.monotonic()
    try:
        profiles = []
        for image, hint in [(original, owner), (suspect, handle)]:
            lines = read_text(image)
            parsed = parse_profile(lines, *image.size, expected_handle=hint)
            profiles.append({**parsed, 'width': image.width, 'height': image.height,
                             'privacy': privacy_for(lines, image), 'recognized_lines': len(lines)})
        return {'original': profiles[0], 'suspect': profiles[1], 'photos': compare_photos(original, suspect),
                'providers': {'ocr': 'paddleocr', 'photos': 'imagededup', 'privacy': 'presidio'},
                'elapsed_seconds': round(time.monotonic() - started, 3)}
    finally:
        busy.release()


@app.post('/inspect', dependencies=[Depends(require_key)])
async def inspect(original: UploadFile = File(...), suspect_image: UploadFile = File(...),
                  owner: str = Form('', max_length=31), suspect: str = Form('', max_length=31)):
    if not state['ready']:
        raise HTTPException(503, 'PaddleOCR is initializing or unavailable')
    from starlette.concurrency import run_in_threadpool
    return await run_in_threadpool(inspect_pair, await decode(original), await decode(suspect_image), owner, suspect)
