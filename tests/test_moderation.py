import hashlib
import json
from concurrent.futures import ThreadPoolExecutor

from src import pipeline


def decision(client, admin, claim, status='confirmed', reason='The visible evidence supports this decision.'):
    return client.post(f"/claims/{claim['id']}/status", headers=admin,
                       json={'status': status, 'reason': reason, 'expected_version': claim.get('version', 0)})


def test_new_decision_requires_a_reason_and_has_private_history(client, admin, new_claim):
    claim = new_claim()
    assert client.post(f"/claims/{claim['id']}/status?status=confirmed", headers=admin).status_code == 422
    assert decision(client, admin, claim).status_code == 200
    assert client.get(f"/claims/{claim['id']}/history").status_code == 401
    history = client.get(f"/claims/{claim['id']}/history", headers=admin).json()
    event = history['events'][-1]
    assert event['kind'] == 'moderator_decision'
    assert event['reason'] == 'The visible evidence supports this decision.'
    assert event['from_status'] == 'under_review' and event['to_status'] == 'confirmed'
    assert event['at'] and event['actor']
    public = client.get('/claims', params={'handle': claim['suspect_handle']}).json()[0]
    assert 'history' not in public and 'appeal_access' not in public


def test_stale_decision_cannot_overwrite_newer_review(client, admin, new_claim):
    claim = new_claim()
    assert decision(client, admin, claim).status_code == 200
    assert decision(client, admin, claim, status='rejected').status_code == 409
    assert pipeline.lookup(claim['suspect_handle'])[0]['status'] == 'confirmed'


def test_appeal_access_is_moderator_issued_and_secret_is_hashed(client, admin, new_claim):
    claim = new_claim()
    assert client.post(f"/claims/{claim['id']}/appeal-access").status_code == 401
    assert client.post(f"/claims/{claim['id']}/appeal-access", headers=admin).status_code == 409
    assert decision(client, admin, claim).status_code == 200
    access = client.post(f"/claims/{claim['id']}/appeal-access", headers=admin).json()
    assert access['token'] and access['expires_at']
    stored = pipeline.lookup(claim['suspect_handle'])[0]
    assert access['token'] not in json.dumps(stored)
    assert stored['appeal_access']['token_sha256'] == hashlib.sha256(access['token'].encode()).hexdigest()
    public = client.get('/claims', params={'handle': claim['suspect_handle']}).json()[0]
    assert 'appeal_access' not in public
    assert client.post('/appeals/access', json={'token': 'invalid'}).status_code == 401


def test_appeal_is_scoped_pending_then_overturned_by_explicit_moderator(client, admin, new_claim):
    claim = new_claim()
    other = new_claim(suspect='another_fake')
    assert decision(client, admin, claim).status_code == 200
    access = client.post(f"/claims/{claim['id']}/appeal-access", headers=admin).json()
    detail = client.post('/appeals/access', json={'token': access['token']})
    assert detail.status_code == 200 and detail.json()['claim']['id'] == claim['id']
    assert other['id'] not in detail.text
    payload = {'token': access['token'], 'reason': 'These are shared stock photographs. Please reconsider the label.'}
    submitted = client.post('/appeals', json=payload)
    assert submitted.status_code == 201
    appeal = submitted.json()
    assert client.post('/appeals', json=payload).status_code == 409
    assert client.get('/statuses').json()[claim['suspect_handle']] == 'confirmed'
    assert client.get('/appeals/pending').status_code == 401
    queued = client.get('/appeals/pending', headers=admin).json()
    assert queued[0]['appeal']['id'] == appeal['id']
    resolution = {'outcome': 'overturn', 'reason': 'Shared stock photographs do not establish impersonation.',
                  'expected_version': queued[0]['claim']['version']}
    assert client.post(f"/appeals/{appeal['id']}/resolve", json=resolution).status_code == 401
    assert client.post(f"/appeals/{appeal['id']}/resolve", json=resolution, headers=admin).status_code == 200
    assert claim['suspect_handle'] not in client.get('/statuses').json()
    assert client.post(f"/appeals/{appeal['id']}/resolve", json=resolution, headers=admin).status_code == 409
    history = client.get(f"/claims/{claim['id']}/history", headers=admin).json()['events']
    assert [e['kind'] for e in history][-2:] == ['appeal_submitted', 'appeal_resolved']
    assert history[-1]['to_status'] == 'rejected'


def test_sqlite_import_is_idempotent_and_concurrent_appends_are_not_lost(tmp_path, monkeypatch):
    legacy = [{'id': 'abc12345', 'suspect_handle': 'legacy', 'status': 'confirmed', 'analysis': {}}]
    source = tmp_path / 'claims.json'
    source.write_text(json.dumps(legacy), encoding='utf-8')
    before = source.read_bytes()
    monkeypatch.setattr(pipeline, 'DB', tmp_path / 'claims.sqlite3')
    assert pipeline._load() == legacy
    assert pipeline._load() == legacy
    def add(i):
        pipeline.append_record({'id': f'{i:08x}', 'suspect_handle': f'demo_{i}', 'status': 'under_review'})
    with ThreadPoolExecutor(max_workers=6) as pool:
        list(pool.map(add, range(30)))
    assert len(pipeline._load()) == 31
    assert source.read_bytes() == before
