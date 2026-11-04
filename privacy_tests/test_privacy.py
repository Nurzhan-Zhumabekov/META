from evidence_tools.privacy import analyze


def test_real_presidio_detects_and_masks_contacts():
    result = analyze('Contact studio.demo@example.com or +1 202 555 0147')
    assert {'EMAIL_ADDRESS','PHONE_NUMBER'} <= {r['entity_type'] for r in result['findings']}
    assert 'studio.demo@example.com' not in result['masked_text']
    assert '202 555 0147' not in result['masked_text']
    assert all('value' not in r for r in result['findings'])


def test_account_statistics_are_not_assumed_to_be_phone_numbers():
    result = analyze('128 публикаций, 5 400 подписчиков, 310 подписок')
    assert not result['findings']


def test_short_invalid_phone_is_not_flagged_just_because_of_a_context_word():
    assert not analyze('Phone: 123')['findings']
