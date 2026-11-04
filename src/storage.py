"""Transactional demo storage; JSON remains a supported legacy/test format."""
import json
import os
import sqlite3
import tempfile
import threading
from pathlib import Path

_json_lock = threading.RLock()


def _json_read(path):
    return json.loads(path.read_text(encoding='utf-8')) if path.exists() else []


def _json_write(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(dir=path.parent, prefix=path.name, suffix='.tmp')
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as stream:
            json.dump(rows, stream, ensure_ascii=False, indent=2)
        os.replace(temporary, path)
    except BaseException:
        Path(temporary).unlink(missing_ok=True)
        raise


def _connect(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path, timeout=30, isolation_level=None)
    try:
        connection.execute('PRAGMA busy_timeout=30000')
        connection.execute('PRAGMA journal_mode=WAL')
        connection.execute('BEGIN IMMEDIATE')
        connection.execute('CREATE TABLE IF NOT EXISTS metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL)')
        connection.execute('CREATE TABLE IF NOT EXISTS claims (id TEXT PRIMARY KEY, payload TEXT NOT NULL)')
        if not connection.execute("SELECT 1 FROM metadata WHERE key='legacy_imported'").fetchone():
            legacy = path.with_name('claims.json')
            for row in _json_read(legacy):
                connection.execute('INSERT OR IGNORE INTO claims VALUES (?, ?)',
                                   (row['id'], json.dumps(row, ensure_ascii=False)))
            connection.execute("INSERT INTO metadata VALUES ('legacy_imported', '1')")
        connection.commit()
        return connection
    except BaseException:
        connection.close()
        raise


def _rows(connection):
    return [json.loads(row[0]) for row in connection.execute('SELECT payload FROM claims ORDER BY rowid')]


def read(path):
    path = Path(path)
    if path.suffix == '.json':
        with _json_lock:
            return _json_read(path)
    connection = _connect(path)
    try:
        return _rows(connection)
    finally:
        connection.close()


def mutate(path, operation):
    """Read, validate and commit one operation under a cross-process write lock."""
    path = Path(path)
    if path.suffix == '.json':
        with _json_lock:
            rows = _json_read(path)
            result = operation(rows)
            _json_write(path, rows)
            return result
    connection = _connect(path)
    try:
        connection.execute('BEGIN IMMEDIATE')
        rows = _rows(connection)
        result = operation(rows)
        current_ids = {row['id'] for row in rows}
        previous_ids = {r[0] for r in connection.execute('SELECT id FROM claims')}
        for identifier in previous_ids - current_ids:
            connection.execute('DELETE FROM claims WHERE id=?', (identifier,))
        for row in rows:
            connection.execute('INSERT INTO claims VALUES (?, ?) ON CONFLICT(id) DO UPDATE SET payload=excluded.payload',
                               (row['id'], json.dumps(row, ensure_ascii=False)))
        connection.commit()
        return result
    except BaseException:
        connection.rollback()
        raise
    finally:
        connection.close()


def replace(path, rows):
    def update(existing):
        existing[:] = rows
    mutate(path, update)
