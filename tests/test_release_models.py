"""A clean source checkout must install safe models without overwriting local training."""

import json
from pathlib import Path

import pytest

from scripts.install_demo_models import install_models


def release_sources(root: Path):
    source = root / 'models'
    source.mkdir()
    project = Path(__file__).resolve().parents[1]
    for name in ('profile_risk_model.json', 'pair_risk_model.json'):
        (source / name).write_bytes((project / 'models' / name).read_bytes())
    return source


def test_fresh_checkout_installs_both_valid_model_artifacts(tmp_path):
    source = release_sources(tmp_path)
    installed = install_models(tmp_path)
    assert len(installed) == 2
    models = [json.loads(path.read_text(encoding='utf-8')) for path in installed]
    assert {model['model_id'] for model in models} == {
        'profile-logreg-v2-no-avatar', 'pair-text-logreg-v2-synthetic',
    }
    assert all(path.read_bytes() == (source / path.name).read_bytes() for path in installed)


def test_existing_local_training_is_preserved_and_install_is_idempotent(tmp_path):
    release_sources(tmp_path)
    target = tmp_path / 'outputs/ml'
    target.mkdir(parents=True)
    custom = b'{"model_id":"custom-local-training"}\n'
    (target / 'profile_risk_model.json').write_bytes(custom)
    assert len(install_models(tmp_path)) == 1
    assert (target / 'profile_risk_model.json').read_bytes() == custom
    assert install_models(tmp_path) == []


def test_invalid_release_has_no_partial_install(tmp_path):
    source = release_sources(tmp_path)
    (source / 'pair_risk_model.json').write_text('not json', encoding='utf-8')
    with pytest.raises(ValueError):
        install_models(tmp_path)
    assert not (tmp_path / 'outputs/ml').exists()
