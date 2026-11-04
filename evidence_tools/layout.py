"""Conservative spatial parsing of OCR observations, never of account fixtures."""
import math
import re

COUNT_LABELS = {
    'num_posts': r'публикац\w*|posts?|жарияланым\w*',
    'num_followers': r'подписчик\w*|followers?|жазылушы\w*',
    'num_following': r'подписок|подписки|following|жазылым\w*',
}
STOP = re.compile(r'^(?:пожаловаться|подписаться|подписки$|отправить сообщение|редактировать профиль|сохран[её]нное|моменты$|в пути$|за кадром$|аккаунт на проверке|подтверждена имперсонация|follow$|message$|edit profile|report$|highlights$)', re.I)
UI = re.compile(r'^(?:instagram|главная|поиск|сообщения|создать|уведомления|ещ[её]|reels|интересное|публикации с отметками)$', re.I)
ENGLISH_CONTROLS = re.compile(r'^(?:report account|send message|following|saved|moments|on the road|behind the scenes|account under review|impersonation confirmed|view profile|edit profile)$', re.I)


def is_control(text):
    return bool(STOP.search(text) or ENGLISH_CONTROLS.fullmatch(text.strip()))


def _count(value):
    text = value.lower().replace('\u00a0', '').replace(' ', '')
    approximate = bool(re.search(r'[kкmм]', text))
    multiplier = 1_000_000 if text.endswith(('m', 'м')) else 1000 if text.endswith(('k', 'к')) else 1
    text = re.sub(r'[kкmм]$', '', text)
    if multiplier == 1:
        text = text.replace(',', '').replace('.', '')
    else:
        text = text.replace(',', '.')
    try:
        number = int(float(text) * multiplier)
    except ValueError:
        return None, False
    return (number, approximate) if 0 <= number <= 2_147_483_647 else (None, False)


def parse_profile(observations, width, height, *, expected_handle=''):
    rows = [r for r in observations if isinstance(r.get('text'), str) and
            type(r.get('confidence')) in {float, int} and math.isfinite(r['confidence']) and
            r['confidence'] >= 0.65 and len(r.get('box', [])) == 4]
    rows.sort(key=lambda r: (r['box'][1], r['box'][0]))
    fields, warnings = {}, []
    expected = expected_handle.lstrip('@').casefold()
    def observed_handle_text(row):
        # A neighbouring account-menu icon can join the header's OCR line.
        # Remove only a separate trailing ellipsis, never infer missing letters.
        return re.sub(r'\s+(?:…|\.{3})$', '', row['text'].strip()).lstrip('@')
    handles = []
    for row in rows:
        text = observed_handle_text(row)
        if re.fullmatch(r'[A-Za-z0-9_.]{1,30}', text) and not UI.fullmatch(text):
            if text.casefold() == expected or ('.' in text or '_' in text):
                handles.append(row)
    exact = [r for r in handles if observed_handle_text(r).casefold() == expected]
    handle = (exact or handles or [None])[0]
    if handle is None:
        return {'fields': {}, 'warnings': ['The profile username could not be read reliably. Enter the details manually.']}
    observed_handle = observed_handle_text(handle)
    fields['handle'] = {'value': observed_handle, 'confidence': handle['confidence']}
    if expected and observed_handle.casefold() != expected:
        warnings.append('The recognized username differs from the selected account. Check the screenshot.')
    content_left = 65 if width >= 700 else 0
    content = [r for r in rows if r['box'][1] > handle['box'][1] + 8 and r['box'][0] >= content_left]
    stat_rows = []
    for field, label in COUNT_LABELS.items():
        for row in content:
            match = re.search(r'([0-9][0-9\s.,]*[kKmMкКмМ]?)\s*(?:' + label + r')\b', row['text'], re.I)
            if match:
                value, approximate = _count(match[1])
            elif re.fullmatch(label, row['text'].strip(), re.I):
                nearby = [r for r in content if r['box'][3] <= row['box'][3] and row['box'][1] - r['box'][3] <= 35
                          and abs(r['box'][0] - row['box'][0]) < 80 and re.fullmatch(r'[0-9][0-9\s.,]*[kKmMкКмМ]?', r['text'].strip())]
                value, approximate = _count(nearby[-1]['text']) if nearby else (None, False)
            else:
                continue
            if value is not None:
                fields[field] = {'value': value, 'confidence': min(row['confidence'], 0.7) if approximate else row['confidence'], 'approximate': approximate}
                stat_rows.append(row)
                if approximate:
                    warnings.append('Abbreviated counts are approximate. Check the exact number.')
                break
    stat_bottom = max((r['box'][3] for r in stat_rows), default=handle['box'][3])
    def is_count_row(row):
        return any(re.search(label, row['text'], re.I) for label in COUNT_LABELS.values())
    names = [r for r in content if r['box'][1] < max(stat_bottom + 70, handle['box'][3] + 120)
             and not is_count_row(r) and not is_control(r['text']) and not UI.fullmatch(r['text'])
             and re.search(r'[^\W\d_]', r['text']) and len(r['text']) <= 100
             and r['text'].strip().lstrip('@').casefold() != observed_handle.casefold()]
    if names:
        name = names[0]
        fields['display_name'] = {'value': name['text'].strip(), 'confidence': name['confidence']}
        duplicates = [r for r in names if r['text'].strip() == name['text'].strip()]
        bio_start = max(stat_bottom, duplicates[-1]['box'][3])
    else:
        bio_start = stat_bottom
    stops = [r['box'][1] for r in content if r['box'][1] >= bio_start and is_control(r['text'])]
    bio_end = min(stops, default=min(height, bio_start + 220))
    bio = [r for r in content if bio_start < r['box'][1] < bio_end and not is_count_row(r)
           and not UI.fullmatch(r['text']) and not is_control(r['text'])]
    if bio:
        value = '\n'.join(r['text'].strip() for r in bio)[:500]
        fields['bio'] = {'value': value, 'confidence': min(r['confidence'] for r in bio)}
    for field in ['display_name', 'bio', *COUNT_LABELS]:
        if field not in fields:
            warnings.append(f'Could not reliably read {field}. Check or enter it manually.')
    return {'fields': fields, 'warnings': list(dict.fromkeys(warnings))}
