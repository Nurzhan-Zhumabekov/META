import httpx
import pytest

from src import config
from src import meta_availability


@pytest.fixture(autouse=True)
def settings(monkeypatch):
    monkeypatch.setattr(config, 'META_API_KEY', 'private-unit-test-key')
    monkeypatch.setattr(config, 'META_API_BASE_URL', 'https://api.meta.ai/v1')
    monkeypatch.setattr(config, 'META_MODEL', 'muse-spark-1.3')
    meta_availability.reset()


@pytest.mark.parametrize('data,available', [
    ([{'id': 'muse-spark-1.3'}], True),
    ([], False),
    ([{'id': 'different-model'}], False),
])
def test_availability_checks_the_actual_catalog_and_caches(monkeypatch, data, available):
    calls = []
    def get(url, **kwargs):
        calls.append(url)
        assert kwargs['headers']['Authorization'] == 'Bearer private-unit-test-key'
        return httpx.Response(200, json={'data': data})
    monkeypatch.setattr(meta_availability.httpx, 'get', get)
    first = meta_availability.model_access()
    assert first['available'] is available
    assert meta_availability.model_access() == first
    assert calls == ['https://api.meta.ai/v1/models']
    assert 'private-unit-test-key' not in str(first)


def test_unreachable_catalog_is_unavailable_without_leaking_errors(monkeypatch):
    def get(*args, **kwargs):
        raise httpx.ConnectError('private-unit-test-key private-network-details')
    monkeypatch.setattr(meta_availability.httpx, 'get', get)
    assert meta_availability.model_access() == {'available': False, 'state': 'unreachable'}


def test_missing_key_never_requests_catalog(monkeypatch):
    monkeypatch.setattr(config, 'META_API_KEY', '')
    monkeypatch.setattr(meta_availability.httpx, 'get', lambda *a, **k: pytest.fail('unexpected network call'))
    assert meta_availability.model_access() == {'available': False, 'state': 'not_configured'}


def test_catalog_cache_does_not_reuse_another_keys_access(monkeypatch):
    calls = []
    def get(url, **kwargs):
        calls.append(kwargs['headers']['Authorization'])
        return httpx.Response(200, json={'data': [{'id': 'muse-spark-1.3'}] if len(calls)==1 else []})
    monkeypatch.setattr(meta_availability.httpx, 'get', get)
    assert meta_availability.model_access()['available'] is True
    monkeypatch.setattr(config, 'META_API_KEY', 'another-unit-key')
    assert meta_availability.model_access()['available'] is False
    assert len(calls) == 2


def test_invalid_endpoint_does_not_transmit_the_key(monkeypatch):
    monkeypatch.setattr(config, 'META_API_BASE_URL', 'http://invalid.example/v1')
    monkeypatch.setattr(meta_availability.httpx, 'get', lambda *a, **k: pytest.fail('unexpected network call'))
    assert meta_availability.model_access() == {'available': False, 'state': 'invalid_configuration'}


def test_api_does_not_advertise_unlisted_meta_as_ready(client, monkeypatch):
    monkeypatch.setattr(config, 'COMPARER', 'meta')
    monkeypatch.setattr(meta_availability, 'model_access', lambda: {'available': False, 'state': 'not_listed'})
    status = client.get('/analysis/status').json()
    assert status['meta_key_configured'] is True
    assert status['ready'] is False
    assert status['meta_model_access']['state'] == 'not_listed'
