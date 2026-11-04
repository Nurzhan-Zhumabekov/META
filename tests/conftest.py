import io

import numpy as np
import pytest
from fastapi.testclient import TestClient
from PIL import Image

from src import config, pipeline
from src.api import app

REAL_DB = pipeline.DB  # captured at import, before any test patches it
TOKEN = "test-secret"


@pytest.fixture(autouse=True)
def isolated_env(tmp_path, monkeypatch):
    """Every test gets its own claims.json and a known config; the real outputs/claims.json stays untouched."""
    before = REAL_DB.read_bytes() if REAL_DB.exists() else None
    monkeypatch.setattr(pipeline, "DB", tmp_path / "claims.json")
    monkeypatch.setattr(config, "COMPARER", "local")
    monkeypatch.setattr(config, "ADMIN_TOKEN", TOKEN)
    monkeypatch.setattr(config, "PAIR_ML_MODEL_PATH", tmp_path / "unconfigured-pair-model.json")
    yield
    after = REAL_DB.read_bytes() if REAL_DB.exists() else None
    assert after == before, "test touched the real outputs/claims.json"


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def admin():
    return {"X-Admin-Token": TOKEN}


@pytest.fixture
def make_image():
    """Small deterministic test images: 'gradient' (red->blue with a white box) or 'stripes' (yellow/blue)."""

    def _make(kind: str = "gradient", size: int = 64) -> Image.Image:
        a = np.zeros((size, size, 3), np.uint8)
        if kind == "gradient":
            x = np.linspace(0, 255, size, dtype=np.uint8)
            a[..., 0] = x[None, :]
            a[..., 1] = 60
            a[..., 2] = 255 - x[None, :]
            a[size // 4 : size // 2, size // 4 : size // 2] = (255, 255, 255)
        elif kind == "stripes":
            for col in range(size):
                a[:, col] = (230, 200, 20) if (col // 8) % 2 == 0 else (20, 40, 200)
        else:
            raise ValueError(kind)
        return Image.fromarray(a)

    return _make


@pytest.fixture
def png():
    def _png(img: Image.Image) -> bytes:
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return buf.getvalue()

    return _png


@pytest.fixture
def new_claim(client, make_image, png):
    """POST /claims with two generated images; returns the created claim dict."""

    def _new(owner: str = "alice", suspect: str = "@alice_fake") -> dict:
        files = {
            "original": ("o.png", png(make_image("gradient")), "image/png"),
            "suspect_image": ("s.png", png(make_image("gradient")), "image/png"),
        }
        r = client.post("/claims", data={"owner": owner, "suspect": suspect}, files=files)
        assert r.status_code == 200, r.text
        return r.json()

    return _new
