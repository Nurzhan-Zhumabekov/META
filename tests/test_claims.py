from src import pipeline

MAX_BYTES = 5 * 1024 * 1024


def _post_claim(client, original: bytes, suspect_image: bytes):
    files = {
        "original": ("o.png", original, "image/png"),
        "suspect_image": ("s.png", suspect_image, "image/png"),
    }
    return client.post("/claims", data={"owner": "@alice", "suspect": "@alice_fake"}, files=files)


def test_create_claim(client, make_image, png):
    r = _post_claim(client, png(make_image("gradient")), png(make_image("stripes")))
    assert r.status_code == 200
    claim = r.json()
    assert claim["suspect_handle"] == "alice_fake"  # '@' stripped
    assert claim["owner_handle"] == "alice"
    assert claim["status"] == "under_review"
    assert 0.0 <= claim["score"] <= 1.0
    assert any("Handle similarity" in reason for reason in claim["reasons"])

    # persisted and retrievable by suspect handle (with or without '@')
    for handle in ("alice_fake", "@alice_fake"):
        assert client.get("/claims", params={"handle": handle}).json() == [claim]
    assert pipeline.DB.exists()


def test_invalid_image_is_400(client, make_image, png):
    r = _post_claim(client, b"definitely not an image", png(make_image()))
    assert r.status_code == 400
    r = _post_claim(client, png(make_image()), b"")
    assert r.status_code == 400
    assert not pipeline.DB.exists()  # nothing saved


def test_oversize_image_is_413(client, make_image, png):
    r = _post_claim(client, b"\0" * (MAX_BYTES + 1), png(make_image()))
    assert r.status_code == 413
    assert not pipeline.DB.exists()


def test_status_update_unknown_id_is_404(client, admin):
    r = client.post("/claims/doesnotexist/status", params={"status": "confirmed"}, headers=admin)
    assert r.status_code == 404


def test_status_update_invalid_status_is_400(client, admin, new_claim):
    claim = new_claim()
    r = client.post(f"/claims/{claim['id']}/status", params={"status": "banana"}, headers=admin)
    assert r.status_code == 400
    # claim left untouched
    assert client.get("/claims", params={"handle": claim["suspect_handle"]}).json()[0]["status"] == "under_review"


def test_status_update_changes_status(client, admin, new_claim):
    claim = new_claim()
    response = client.post(f"/claims/{claim['id']}/status", json={"status": "rejected", "reason": "The report does not establish impersonation.", "expected_version": 0}, headers=admin)
    assert response.status_code == 200
    assert client.get("/claims", params={"handle": claim["suspect_handle"]}).json()[0]["status"] == "rejected"
    assert client.get("/claims/pending", headers=admin).json() == []


def test_statuses_confirmed_beats_under_review_and_rejected_is_hidden(client, admin, new_claim):
    def decide(claim, status):
        r = client.post(f"/claims/{claim['id']}/status", json={"status": status, "reason": "A moderator reviewed the supplied evidence.", "expected_version": 0}, headers=admin)
        assert r.status_code == 200

    # same suspect: confirmed must win no matter the order of the claims
    a1 = new_claim(suspect="fake_a")  # stays under_review
    a2 = new_claim(suspect="fake_a")
    decide(a2, "confirmed")
    new_claim(suspect="fake_a")  # later under_review claim must not downgrade it
    # suspect that is only under review
    new_claim(suspect="fake_b")
    # suspect whose only claim was rejected
    c1 = new_claim(suspect="fake_c")
    decide(c1, "rejected")
    # suspect with a rejected and an under_review claim: under_review shows
    d1 = new_claim(suspect="fake_d")
    decide(d1, "rejected")
    new_claim(suspect="fake_d")

    assert a1["status"] == "under_review"
    assert client.get("/statuses").json() == {
        "fake_a": "confirmed",
        "fake_b": "under_review",
        "fake_d": "under_review",
    }
