"""Cached, read-only model access check. Never submits images or creates a completion."""
import hashlib
import threading
import time
from urllib.parse import urlparse

import httpx

from . import config

_lock = threading.Lock()
_cached = None


def reset():
    global _cached
    with _lock:
        _cached = None


def model_access():
    global _cached
    if not config.META_API_KEY:
        return {'available': False, 'state': 'not_configured'}
    url = urlparse(config.META_API_BASE_URL)
    if url.scheme != 'https' or not url.hostname or url.username or url.password or url.query or url.fragment:
        return {'available': False, 'state': 'invalid_configuration'}
    identity = (config.META_API_BASE_URL, config.META_MODEL,
                hashlib.sha256(config.META_API_KEY.encode()).digest())
    with _lock:
        if _cached and _cached[0] == identity and time.monotonic() - _cached[1] < 30:
            return dict(_cached[2])
        result = {'available': False, 'state': 'unreachable'}
        try:
            response = httpx.get(config.META_API_BASE_URL.rstrip('/') + '/models',
                headers={'Authorization': 'Bearer ' + config.META_API_KEY},
                timeout=httpx.Timeout(2, connect=1), trust_env=False, follow_redirects=False)
            if response.status_code == 200:
                envelope = response.json()
                catalog = envelope.get('data') if isinstance(envelope, dict) else None
                if isinstance(catalog, list):
                    available = any(isinstance(item, dict) and item.get('id') == config.META_MODEL for item in catalog)
                    result = {'available': available, 'state': 'available' if available else 'not_listed'}
        except (httpx.HTTPError, ValueError):
            pass
        _cached = (identity, time.monotonic(), result)
        return dict(result)
