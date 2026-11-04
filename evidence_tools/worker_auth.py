import secrets
from pathlib import Path

from fastapi import Header, HTTPException

KEY_FILE = Path(__file__).resolve().parents[1] / 'outputs/evidence-worker.key'


def worker_key():
    try:
        return KEY_FILE.read_text(encoding='utf-8').strip()
    except OSError:
        return ''


def require_key(x_evidence_key: str | None = Header(default=None)):
    expected = worker_key()
    if not expected:
        raise HTTPException(503, 'Worker access is not configured')
    if not x_evidence_key or not secrets.compare_digest(x_evidence_key, expected):
        raise HTTPException(401, 'Worker authorization required')
