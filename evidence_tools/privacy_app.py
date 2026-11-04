from contextlib import asynccontextmanager
from importlib.metadata import version
import threading

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict, Field

from .privacy import analyze, engine
from .worker_auth import require_key

state = {'ready': False}


def warm():
    try:
        engine()
        state.update(ready=True)
    except Exception as error:
        state.update(error=type(error).__name__)


@asynccontextmanager
async def lifespan(app):
    threading.Thread(target=warm, daemon=True).start()
    yield


app = FastAPI(lifespan=lifespan, docs_url=None, redoc_url=None)


class Text(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    text: str = Field(max_length=20000)


@app.get('/health')
def health():
    return {**state, 'provider': 'presidio', 'version': version('presidio-analyzer'),
            'scope': 'contacts_and_financial_identifiers'}


@app.post('/analyze', dependencies=[Depends(require_key)])
def inspect_text(payload: Text):
    if not state['ready']:
        raise HTTPException(503, 'Privacy analyzer is initializing or unavailable')
    return analyze(payload.text)
