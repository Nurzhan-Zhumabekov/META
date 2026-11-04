from copy import deepcopy

import pytest

from src.demo_readiness import readiness_checks


def healthy_status():
    return {
        'provider': 'meta', 'ready': True, 'meta_key_configured': True,
        'human_review_required': True, 'privacy_redaction_required': True,
        'profile_ml': {'ready': True, 'enabled': True}, 'pair_ml': {'ready': True},
        'evidence_tools': {'ready': True, 'ocr': {'provider': 'paddleocr'},
                           'photo_comparison': {'provider': 'imagededup'},
                           'privacy': {'ready': True, 'provider': 'presidio'}},
    }


def test_complete_demo_status_passes_without_modifying_it():
    status = healthy_status()
    before = deepcopy(status)
    assert all(check['passed'] for check in readiness_checks(status, require_meta=True))
    assert status == before


@pytest.mark.parametrize('section,field', [
    (None, 'ready'), (None, 'meta_key_configured'), (None, 'human_review_required'),
    (None, 'privacy_redaction_required'), ('profile_ml', 'ready'),
    ('profile_ml', 'enabled'), ('pair_ml', 'ready'), ('evidence_tools', 'ready'),
])
def test_a_successful_http_response_does_not_hide_unavailable_dependencies(section, field):
    status = healthy_status()
    (status[section] if section else status)[field] = False
    assert any(not check['passed'] for check in readiness_checks(status, require_meta=True))


def test_privacy_provider_and_live_meta_cannot_be_replaced_by_a_ready_mock():
    status = healthy_status()
    status['provider'] = 'mock'
    status['evidence_tools']['privacy'] = {'ready': True, 'provider': 'mock'}
    failures = [check['name'] for check in readiness_checks(status, require_meta=True) if not check['passed']]
    assert 'Live Meta provider' in failures
    assert 'Presidio privacy inspection' in failures


def test_missing_status_fields_fail_closed_and_local_mode_is_explicit():
    assert any(not check['passed'] for check in readiness_checks({}, require_meta=True))
    status = healthy_status()
    status.update(provider='local', meta_key_configured=False, privacy_redaction_required=False)
    checks = readiness_checks(status, require_meta=False)
    assert all(check['passed'] for check in checks)
    assert any(check['detail'] == 'local' for check in checks)
