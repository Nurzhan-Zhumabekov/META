import pytest
from fastapi.testclient import TestClient

from src import pipeline

ORIGIN = {'Origin': 'http://testserver'}


def login(client, token='test-secret'):
    return client.post('/reviewer/session', json={'token': token}, headers=ORIGIN)


def test_reviewer_cookie_is_private_and_not_a_frontend_secret(client, new_claim):
    claim = new_claim()
    assert client.get('/reviewer/session').status_code == 401
    response = login(client)
    assert response.status_code == 200
    cookie = response.headers['set-cookie'].lower()
    assert 'httponly' in cookie and 'samesite=strict' in cookie
    assert 'test-secret' not in response.text
    assert client.get('/claims/pending').status_code == 200
    response = client.post(f"/claims/{claim['id']}/status", headers=ORIGIN,
                           json={"status": "confirmed", "reason": "The processed evidence supports this decision.", "expected_version": 0})
    assert response.status_code == 200
    assert client.get('/statuses').json()['alice_fake'] == 'confirmed'


def test_reviewer_login_rejects_invalid_key_and_cross_origin(client):
    assert login(client, 'incorrect').status_code == 401
    assert client.post('/reviewer/session', json={'token': 'test-secret'}, headers={'Origin': 'https://other.example'}).status_code == 403


def test_cookie_mutations_require_same_origin_and_logout_revokes_access(client, new_claim):
    claim = new_claim()
    assert login(client).status_code == 200
    assert client.post(f"/claims/{claim['id']}/status?status=confirmed", headers={'Origin': 'https://other.example'}).status_code == 403
    assert client.delete('/reviewer/session', headers=ORIGIN).status_code == 200
    assert client.get('/claims/pending').status_code == 401


def test_evidence_is_saved_only_for_valid_claim_and_requires_reviewer(client, new_claim, admin):
    claim = new_claim()
    assert claim['created_at']
    assert set(claim['evidence']) == {'original', 'suspect'}
    url = claim['evidence']['original']
    assert client.get(url).status_code == 401
    response = client.get(url, headers=admin)
    assert response.status_code == 200
    assert response.headers['content-type'] == 'image/jpeg'
    assert response.content.startswith(b'\xff\xd8')
    assert 'no-store' in response.headers['cache-control']
    assert (pipeline.DB.parent / 'evidence' / claim['id'] / 'original.jpg').exists()
    assert client.get(f"/claims/{claim['id']}/evidence/invalid", headers=admin).status_code in {404, 422}


def test_web_mount_keeps_api_errors_json_and_serves_built_pages(tmp_path, monkeypatch):
    from src import web
    dist = tmp_path / 'dist'
    dist.mkdir()
    (dist / 'index.html').write_text('<html>Web application</html>')
    (dist / 'demo-guide.html').write_text('<html>MirrorCheck landing</html>')
    (dist / 'app.js').write_text('/* built asset */')
    monkeypatch.setattr(web, 'WEB_DIST', dist)
    with TestClient(web.app) as client:
        assert client.get('/').status_code == 200
        assert 'Web application' in client.get('/profile/aigerim.k').text
        assert client.get('/api/analysis/status').json()['provider'] == 'local'
        assert client.get('/api/unknown').status_code == 404
        assert client.get('/missing.js').status_code == 404
        landing = client.get('/demo-guide.html')
        assert 'MirrorCheck landing' in landing.text
        assert landing.headers['cache-control'] == 'no-store'
        assert client.get('/app.js').headers['cache-control'] == 'public, max-age=3600'


@pytest.mark.parametrize('route', ['/profile/aruzhan.jpg', '/messages/aruzhan.jpg'])
def test_profile_handles_with_media_suffixes_are_client_routes(tmp_path, monkeypatch, route):
    from src import web
    dist = tmp_path / 'dist'
    dist.mkdir()
    (dist / 'index.html').write_text('<html>Web application</html>')
    monkeypatch.setattr(web, 'WEB_DIST', dist)
    with TestClient(web.app) as client:
        response = client.get(route)
        assert response.status_code == 200
        assert 'Web application' in response.text
        assert response.headers['cache-control'] == 'no-store'
        assert client.get('/media/missing.jpg').status_code == 404
        assert client.get('/assets/missing.js').status_code == 404
        assert client.get('/profile/%2e%2e/%2e%2e/missing.jpg').status_code == 404
