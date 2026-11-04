from evidence_tools.layout import parse_profile


def line(text, x, y, confidence=0.98):
    return {'text': text, 'box': [x, y, x + max(30, len(text) * 7), y + 18], 'confidence': confidence}


def test_profile_fields_come_from_spatial_ocr_not_expected_handle():
    rows = [line('aigerim.k.copy', 220, 30), line('Aigerim K.', 220, 65),
            line('6 публикаций', 220, 105), line('5 400 подписчиков', 360, 105), line('310 подписок', 530, 105),
            line('Aigerim K.', 220, 145), line('Собираю моменты, а не вещи.', 220, 173),
            line('Фотограф · Astana, Kazakhstan', 220, 196), line('Съёмки и сотрудничество', 220, 219),
            line('Пожаловаться на аккаунт', 220, 250), line('Моменты', 100, 400)]
    result = parse_profile(rows, 800, 900, expected_handle='aigerim.k.copy')
    assert result['fields']['handle']['value'] == 'aigerim.k.copy'
    assert result['fields']['display_name']['value'] == 'Aigerim K.'
    assert result['fields']['num_followers']['value'] == 5400
    assert result['fields']['num_posts']['value'] == 6
    assert result['fields']['bio']['value'] == 'Собираю моменты, а не вещи.\nФотограф · Astana, Kazakhstan\nСъёмки и сотрудничество'


def test_blank_image_does_not_invent_expected_handle_or_missing_counts():
    result = parse_profile([], 800, 900, expected_handle='known.account')
    assert result['fields'] == {}
    assert result['warnings']


def test_uncertain_ocr_and_phone_numbers_are_not_converted_to_profile_counts():
    rows = [line('alice.copy', 220, 30), line('Alice', 220, 70),
            line('Call +1 202 555 0147', 220, 105), line('800 followers', 220, 140, confidence=0.2)]
    result = parse_profile(rows, 800, 900, expected_handle='alice.copy')
    assert 'num_followers' not in result['fields']
    assert 'num_following' not in result['fields']


def test_header_menu_ellipsis_does_not_hide_observed_profile_handle():
    rows = [line('aigerim.k …', 279, 36), line('Aigerim K.', 278, 76),
            line('128 публикаций 5 400 подписчиков 310 подписок', 282, 110),
            line('Собираю моменты, а не вещи.', 280, 145),
            line('Фотограф · Astana, Kazakhstan', 281, 168),
            line('Редактировать профиль', 192, 234)]
    result = parse_profile(rows, 883, 1240, expected_handle='aigerim.k')
    assert result['fields']['handle']['value'] == 'aigerim.k'
    assert result['fields']['display_name']['value'] == 'Aigerim K.'
    assert result['fields']['num_followers']['value'] == 5400
    assert result['fields']['num_posts']['value'] == 128
    assert result['fields']['num_following']['value'] == 310
    assert result['fields']['bio']['value'].startswith('Собираю моменты')


def test_english_profile_controls_do_not_leak_into_extracted_bio():
    rows = [line('alice.copy', 220, 30), line('Alice', 220, 65),
            line('6 posts', 220, 105), line('5,400 followers', 360, 105), line('310 following', 530, 105),
            line('Alice', 220, 145), line('Collecting moments, not things.', 220, 173),
            line('Photographer in Astana', 220, 196), line('Report account', 220, 250),
            line('Send message', 220, 280), line('Moments', 100, 400)]
    result = parse_profile(rows, 800, 900, expected_handle='alice.copy')
    assert result['fields']['bio']['value'] == 'Collecting moments, not things.\nPhotographer in Astana'
    assert result['fields']['num_followers']['value'] == 5400
    assert result['fields']['num_following']['value'] == 310
