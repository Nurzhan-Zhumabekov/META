from fastapi.testclient import TestClient
from src import config, pipeline
from src.api import app

ORIGIN = {'Origin': 'http://testserver'}


def enable(monkeypatch, tmp_path):
    monkeypatch.setattr(config, 'PUBLIC_DEMO_ENABLED', True)
    monkeypatch.setattr(config, 'DEMO_SESSION_SECRET', 'test-public-demo-signing-secret')
    monkeypatch.setattr(config, 'DEMO_DATA_ROOT', tmp_path / 'sandboxes')


def test_public_demo_cannot_read_local_reports_or_another_visitors_reports(monkeypatch, tmp_path, new_claim, make_image, png):
    private = new_claim(suspect='private_local_record')
    enable(monkeypatch, tmp_path)
    with TestClient(app) as first, TestClient(app) as second:
        assert first.get('/statuses').status_code == 401
        assert first.post('/demo/session', headers=ORIGIN).status_code == 200
        assert second.post('/demo/session', headers=ORIGIN).status_code == 200
        assert private['suspect_handle'] not in first.get('/statuses').json()
        result = first.post('/claims', headers=ORIGIN, data={'owner':'demo.owner','suspect':'demo.copy'}, files={
            'original':('a.png',png(make_image()),'image/png'),'suspect_image':('b.png',png(make_image()),'image/png')})
        assert result.status_code == 200
        identifier = result.json()['id']
        assert first.get('/statuses').json() == {'demo.copy':'under_review'}
        assert second.get('/statuses').json() == {}
        assert first.get('/claims/pending').status_code == 401
        assert first.post('/demo/reviewer', headers=ORIGIN).status_code == 200
        assert second.post('/demo/reviewer', headers=ORIGIN).status_code == 200
        assert first.get('/claims/pending').json()[0]['id'] == identifier
        assert second.get('/claims/pending').json() == []
        assert second.get(f'/claims/{identifier}/evidence/original').status_code == 404
        assert private['id'] not in first.get('/reviewer/cases').text
    assert pipeline.lookup('private_local_record')[0]['id'] == private['id']


def test_public_demo_rejects_cross_origin_role_grants_and_missing_signing_secret(monkeypatch, tmp_path):
    enable(monkeypatch, tmp_path)
    with TestClient(app) as client:
        assert client.post('/demo/session', headers={'Origin':'https://different.example'}).status_code == 403
        monkeypatch.setattr(config, 'DEMO_SESSION_SECRET', '')
        assert client.post('/demo/session', headers=ORIGIN).status_code == 503


def test_public_demo_bootstrap_also_works_through_mounted_web_api(monkeypatch, tmp_path):
    from src.web import app as web
    enable(monkeypatch, tmp_path)
    with TestClient(web) as client:
        assert client.get('/api/demo/session').json()['enabled'] is True
        assert client.post('/api/demo/session', headers=ORIGIN).status_code == 200
        assert client.post('/api/demo/reviewer', headers=ORIGIN).status_code == 200
        assert client.delete('/api/reviewer/session', headers=ORIGIN).status_code == 200
        assert client.get('/api/reviewer/session').status_code == 401


def test_public_demo_caps_new_sessions_per_ip(monkeypatch, tmp_path):
    enable(monkeypatch, tmp_path)
    for _ in range(3):
        with TestClient(app) as client:
            assert client.post('/demo/session', headers=ORIGIN).status_code == 200
    with TestClient(app) as client:
        assert client.post('/demo/session', headers=ORIGIN).status_code == 429


def test_public_upload_body_limit_applies_before_image_parsing(monkeypatch, tmp_path):
    enable(monkeypatch, tmp_path)
    with TestClient(app) as client:
        assert client.post('/demo/session', headers=ORIGIN).status_code == 200
        response = client.post('/claims', content=b'x', headers={**ORIGIN,'Content-Length':str(13*1024*1024)})
        assert response.status_code == 413


def test_cleanup_only_removes_expired_registered_sandboxes(monkeypatch, tmp_path):
    import time
    import sqlite3
    from src import demo_sessions
    enable(monkeypatch, tmp_path)
    identity = 'a' * 32
    demo_sessions.admit(identity, 'test-address')
    root = config.DEMO_DATA_ROOT
    evidence = root / identity / 'evidence'
    evidence.mkdir(parents=True)
    (evidence / 'image.jpg').write_bytes(b'private-demo')
    unrelated = root / 'keep-me'
    unrelated.mkdir()
    with sqlite3.connect(root / 'sessions.sqlite3') as db:
        db.execute('UPDATE sessions SET created=?', (time.time()-demo_sessions.LIFETIME-601,))
    demo_sessions.cleanup()
    assert not (root / identity).exists()
    assert unrelated.is_dir()
