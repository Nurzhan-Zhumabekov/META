import pytest

from src import config

# (method, path) of the two reviewer endpoints; the status call uses a valid status value.
PROTECTED = [
    ("GET", "/claims/pending"),
    ("POST", "/claims/abc12345/status?status=confirmed"),
]


@pytest.mark.parametrize("method,path", PROTECTED)
def test_no_token_is_401(client, method, path):
    assert client.request(method, path).status_code == 401


@pytest.mark.parametrize("method,path", PROTECTED)
def test_wrong_token_is_401(client, method, path):
    r = client.request(method, path, headers={"X-Admin-Token": "nope"})
    assert r.status_code == 401


@pytest.mark.parametrize("method,path", PROTECTED)
def test_non_ascii_token_is_401_not_500(client, method, path):
    r = client.request(method, path, headers={"X-Admin-Token": "café".encode("latin-1")})
    assert r.status_code == 401


@pytest.mark.parametrize("token", [None, "", "test-secret"])
@pytest.mark.parametrize("method,path", PROTECTED)
def test_unset_admin_token_fails_closed_with_503(client, monkeypatch, method, path, token):
    monkeypatch.setattr(config, "ADMIN_TOKEN", "")
    headers = {} if token is None else {"X-Admin-Token": token}
    assert client.request(method, path, headers=headers).status_code == 503


def test_correct_token_lists_pending(client, admin, new_claim):
    claim = new_claim()
    r = client.get("/claims/pending", headers=admin)
    assert r.status_code == 200
    assert [c["id"] for c in r.json()] == [claim["id"]]


def test_correct_token_updates_status(client, admin, new_claim):
    claim = new_claim()
    r = client.post(f"/claims/{claim['id']}/status", json={"status": "confirmed", "reason": "The reviewed evidence supports confirmation.", "expected_version": 0}, headers=admin)
    assert r.status_code == 200
    assert r.json() == {"ok": True}


def test_public_endpoints_need_no_token(client, new_claim):
    # new_claim POSTs /claims without a token
    new_claim(suspect="someone")
    assert client.get("/statuses").status_code == 200
    assert client.get("/claims", params={"handle": "someone"}).status_code == 200
