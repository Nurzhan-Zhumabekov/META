"""Signed, expiring visitor sandboxes. Public role-play never grants local admin access."""
import hashlib
import hmac
import re
import secrets
import time
import sqlite3
import shutil
from contextvars import ContextVar

from fastapi import HTTPException

from . import config

COOKIE = 'mirrorcheck_demo'
ROLE_COOKIE = 'mirrorcheck_demo_reviewer'
LIFETIME = 7200
workspace = ContextVar('demo_workspace', default=None)
reviewer = ContextVar('demo_reviewer', default=False)


def signature(text):
    if not config.DEMO_SESSION_SECRET:
        raise HTTPException(503, 'The public demonstration is not configured.')
    return hmac.new(config.DEMO_SESSION_SECRET.encode(), text.encode(), hashlib.sha256).hexdigest()


def decode(value):
    if not config.DEMO_SESSION_SECRET or not value or not re.fullmatch(r'[a-f0-9]{32}\.[0-9]{10}\.[a-f0-9]{64}', value):
        return None
    identity, issued, digest = value.split('.')
    if not 0 <= time.time()-int(issued) < LIFETIME or not hmac.compare_digest(signature(identity+'.'+issued), digest):
        return None
    return identity


def new_cookie():
    value = secrets.token_hex(16)+'.'+str(int(time.time()))
    return value+'.'+signature(value)


def admit(identity, address):
    cleanup()
    config.DEMO_DATA_ROOT.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(config.DEMO_DATA_ROOT / 'sessions.sqlite3', timeout=15)
    try:
        connection.execute('CREATE TABLE IF NOT EXISTS sessions (id TEXT PRIMARY KEY, created REAL, address_hash TEXT)')
        connection.execute('BEGIN IMMEDIATE')
        current = time.time()
        hashed = signature('address:'+address)
        active = connection.execute('SELECT COUNT(*) FROM sessions WHERE created>?', (current-LIFETIME,)).fetchone()[0]
        recent = connection.execute('SELECT COUNT(*) FROM sessions WHERE address_hash=? AND created>?', (hashed,current-3600)).fetchone()[0]
        if active >= 32 or recent >= 3:
            raise HTTPException(429, 'The demonstration is busy. Try again later.')
        connection.execute('INSERT INTO sessions VALUES (?, ?, ?)', (identity,current,hashed))
        connection.commit()
    finally:
        connection.close()


def cleanup():
    """Remove only expired registered demo workspaces, with a ten-minute grace period."""
    root = config.DEMO_DATA_ROOT.resolve()
    registry = root / 'sessions.sqlite3'
    if not registry.is_file():
        return
    with sqlite3.connect(registry, timeout=15) as connection:
        connection.execute('BEGIN IMMEDIATE')
        expired = connection.execute('SELECT id FROM sessions WHERE created<?', (time.time()-LIFETIME-600,)).fetchall()
        for (identity,) in expired:
            if not re.fullmatch(r'[a-f0-9]{32}', identity):
                continue
            target = root / identity
            if target.is_symlink() or target.resolve().parent != root:
                continue
            if target.is_dir():
                shutil.rmtree(target)
            connection.execute('DELETE FROM sessions WHERE id=?', (identity,))


def role_cookie(identity):
    return signature('reviewer:'+identity)


def has_role(value, identity):
    return bool(identity and value and re.fullmatch(r'[a-f0-9]{64}', value)
                and hmac.compare_digest(value, role_cookie(identity)))


def database_path():
    identity = workspace.get()
    return config.DEMO_DATA_ROOT / identity / 'claims.sqlite3' if identity else None
