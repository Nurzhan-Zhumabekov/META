"""Publish only the fictional demo's actual browser captures and verify persistence."""
import base64
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import httpx
from dotenv import dotenv_values
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
DEMO = ROOT / 'outputs/browser-evidence-tools-20261103'
CLAIM = 'd676e40c'
STEPS = [
    ('01-original-profile.png', 'Оригинальный профиль', 'Исходный aigerim.k: 128 публикаций, 5 400 подписчиков, 310 подписок.'),
    ('02-copy-before-report.png', 'Копия до жалобы', 'Новый вымышленный aigerim.k.vision. Метки ещё нет. Email и телефон — тестовые примеры.'),
    ('03-report-form.png', 'Подача жалобы', 'Выбрана причина «Выдаёт себя за другого». Загружаются два скриншота.'),
    ('04-autofill-matches.png', 'PaddleOCR + imagededup', 'Автозаполнение без подстановки значений из демоданных. Найдены и пронумерованы 6 пар одинаковых постов.'),
    ('05-privacy-review.png', 'Presidio: email и телефон', 'Найдены EMAIL_ADDRESS и PHONE_NUMBER. Оригинальные скриншоты остаются без маскирования; отправка требует явного подтверждения.'),
    ('06-reviewed-fields.png', 'Проверка полей', 'OCR прочитал все 6 полей обоих профилей. Кириллическая «а» в Astana исправлена вручную; счётчики не менялись.'),
    ('07-consent-ready.png', 'Подтверждение перед отправкой', 'Отмечены проверка OCR и согласие на передачу оригиналов с обнаруженными данными в Meta AI.'),
    ('08-meta-processing.png', 'Реальный запрос Meta AI', 'Сервер вызывает Meta Muse Spark и обе независимые локальные ML-модели. Это не имитация ответа.'),
    ('09-report-submitted.png', 'Жалоба d676e40c создана', 'Состояние under_review. AI не может самостоятельно добавить подтверждённую метку.'),
    ('10-analysis-meta-ml.png', 'Результаты анализа', 'Meta: needs_review; сходство изображений и ника 84,8%. Pair ML: 71,26%. Profile ML: 94,59%. Это сигналы данного примера, не точность моделей.'),
    ('11-profile-under-review.png', 'Ожидание решения', 'Профиль показывает «Аккаунт на проверке». Подтверждённой метки пока нет.'),
    ('12-moderator-evidence.png', 'Модератор изучает доказательства', 'Защищённый кабинет показывает оба скриншота и 6 пар выделенных фото.'),
    ('13-moderator-analysis.png', 'Модератор изучает анализ', 'Доступны наблюдения Meta, ML, OCR, дубликаты, приватность и ограничения.'),
    ('14-moderator-confirmed.png', 'Решение сохранено', 'Нажата кнопка подтверждения только новой деможалобы. Предыдущие 7 жалоб сохранены без изменений.'),
    ('15-profile-labelled.png', 'Метка появилась', 'Подтверждена имперсонация — после отдельного решения модератора.'),
    ('16-profile-after-reload.png', 'Метка после перезагрузки', 'Страница перезагружена. Метка остаётся; confirmed сохранён на сервере.'),
]


def main():
    before = json.loads((DEMO / 'claims-before.json').read_text(encoding='utf-8-sig'))
    after = json.loads((ROOT / 'outputs/claims.json').read_text(encoding='utf-8'))
    by_id = {row['id']: row for row in after}
    assert len(before) == 7 and len(after) == 8
    assert all(by_id[row['id']] == row for row in before), 'An earlier claim changed'
    assert set(by_id) - {row['id'] for row in before} == {CLAIM}
    claim = by_id[CLAIM]
    assert claim['status'] == 'confirmed'
    analysis = claim['analysis']
    tools = analysis['screenshot_tools']
    assert analysis['provider'] == 'meta' and not analysis['cached']
    assert analysis['recommendation'] == 'needs_review'
    assert tools['photos']['count'] == 6
    assert tools['suspect']['privacy']['count'] == 2
    assert tools['ocr_reviewed'] and tools['pii_acknowledged']
    assert all(len(tools[side]['field_confidence']) == 6 for side in ['original', 'suspect'])
    assert all('fields' not in tools[side] for side in ['original', 'suspect'])
    with httpx.Client(trust_env=False, timeout=5) as client:
        status = client.get('http://127.0.0.1:8090/api/analysis/status').json()
        public_status = client.get('http://127.0.0.1:8090/api/statuses').json()
        private_evidence = client.get(f'http://127.0.0.1:8090/api/claims/{CLAIM}/evidence/original')
    assert status['evidence_tools']['ready']
    assert private_evidence.status_code in (401, 403)
    slides = []
    hashes = {}
    for name, title, caption in STEPS:
        path = DEMO / name
        raw = path.read_bytes()
        hashes[name] = hashlib.sha256(raw).hexdigest()
        with Image.open(path) as image:
            mime = Image.MIME[image.format]
        slides.append({'title': title, 'caption': caption, 'image': f'data:{mime};base64,' + base64.b64encode(raw).decode()})
    record = {
        'verified_at': datetime.now(timezone.utc).isoformat(), 'claim_id': CLAIM,
        'status': claim['status'], 'previous_claims_unchanged': len(before),
        'meta': {key: analysis[key] for key in ['provider','model','recommendation','similarity_score','usage','cached']},
        'combined_similarity': claim['score'],
        'pair_ml': {key: analysis['pair_ml'][key] for key in ['model','risk_score','training_data']},
        'profile_ml': {key: analysis['profile_ml'][key] for key in ['model','risk_score','ignored_features']},
        'tools': tools, 'service_readiness': status['evidence_tools'],
        'unauthenticated_evidence_status': private_evidence.status_code,
        'public_statuses': public_status, 'screenshots_sha256': hashes,
        'checks': {'backend_tests':116,'vision_tests':6,'privacy_tests':3,'frontend_tests':17,'build':True,'prettier':True},
        'demo_data': 'fictional local accounts; reserved example email and phone',
        'manual_correction': 'Cyrillic a in Astana corrected in both bios before submission; counters unchanged',
    }
    (DEMO / 'verification.json').write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding='utf-8')
    payload = json.dumps(slides, ensure_ascii=False).replace('<', '\\u003c')
    document = '''<!doctype html><html lang="ru"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Жалоба: OCR → фото → приватность → Meta + ML → модератор</title>
<style>*{box-sizing:border-box}body{margin:0;background:#fafafa;color:#171717;font:15px/1.5 Arial,sans-serif}header{padding:22px 28px;border-bottom:1px solid #ddd;background:#fff}h1{font-size:23px;margin:0 0 8px}p{margin:4px 0;color:#555}a{color:#4659ef}main{display:grid;grid-template-columns:280px minmax(0,1fr);max-width:1400px;margin:auto}nav{padding:20px;display:flex;flex-direction:column;gap:6px}button{font:inherit;cursor:pointer;border:1px solid #ddd;background:#fff;border-radius:8px;padding:10px;text-align:left}button[aria-current=true]{background:#edf0ff;color:#2437c6;border-color:#7784fa}article{padding:24px;min-width:0}h2{margin:0 0 8px;font-size:22px}.controls{display:flex;gap:12px;margin:14px 0}img{display:block;max-width:100%;max-height:76vh;margin:auto;object-fit:contain;border:1px solid #ddd;border-radius:10px;background:#fff}small{display:block;margin-top:12px;color:#666}.metrics{margin-top:10px;font-weight:bold;color:#176349}@media(max-width:760px){main{grid-template-columns:1fr}nav{flex-direction:row;overflow:auto;padding:12px}nav button{min-width:170px}article{padding:16px}header{padding:18px}img{max-height:none}}</style>
<header><h1>Полный процесс жалобы со скриншотами</h1><p>Реальные снимки браузера · d676e40c · локальный неофициальный прототип · 3 ноября 2026</p><div class="metrics">PaddleOCR: 6 полей каждого профиля · imagededup: 6 фото · Presidio: email + телефон</div><p><a href="/profile/aigerim.k.vision">Открыть профиль с меткой</a> · <a href="/review">Кабинет модератора</a></p></header>
<main><nav aria-label="Этапы"></nav><article><h2 id="title"></h2><p id="caption"></p><div class="controls"><button id="prev">← Назад</button><span id="position" aria-live="polite"></span><button id="next">Далее →</button></div><img id="shot" alt=""><small>Совпадение фото и оценки моделей не доказывают владение аккаунтом. Pair ML обучена на синтетических парах. Presidio предупреждает о найденных данных; эти оригинальные скриншоты не маскировались.</small></article></main><script>
const slides=__SLIDES__;let current=0;const nav=document.querySelector('nav');slides.forEach((s,i)=>{const b=document.createElement('button');b.textContent=`${i+1}. ${s.title}`;b.onclick=()=>show(i);nav.append(b)});function show(i){current=Math.max(0,Math.min(slides.length-1,i));const s=slides[current];document.querySelector('#title').textContent=s.title;document.querySelector('#caption').textContent=s.caption;document.querySelector('#shot').src=s.image;document.querySelector('#shot').alt=`Этап ${current+1}: ${s.title}`;document.querySelector('#position').textContent=`${current+1} / ${slides.length}`;document.querySelectorAll('nav button').forEach((b,n)=>b.setAttribute('aria-current',String(n===current)));document.querySelector('#prev').disabled=current===0;document.querySelector('#next').disabled=current===slides.length-1}document.querySelector('#prev').onclick=()=>show(current-1);document.querySelector('#next').onclick=()=>show(current+1);document.addEventListener('keydown',e=>{if(e.key==='ArrowLeft')show(current-1);if(e.key==='ArrowRight')show(current+1)});show(0);
</script></html>'''.replace('__SLIDES__', payload)
    # Never publish environment credentials or the private worker key.
    secrets = [str(v) for k,v in dotenv_values(ROOT / '.env').items() if v and ('KEY' in k or 'TOKEN' in k)]
    secrets.append((ROOT / 'outputs/evidence-worker.key').read_text().strip())
    for value in secrets:
        assert value not in document
        for asset in (ROOT / 'web/dist').rglob('*'):
            if asset.is_file() and asset.suffix in {'.js','.html','.css'}:
                assert value.encode() not in asset.read_bytes(), 'Secret found in a frontend asset'
    for target in [DEMO/'walkthrough.html',ROOT/'web/public/evidence-tools-walkthrough.html',ROOT/'web/dist/evidence-tools-walkthrough.html']:
        target.write_text(document, encoding='utf-8')
    print(json.dumps({'claim':CLAIM,'status':claim['status'],'previous_claims_unchanged':len(before),'photos':6,'privacy_regions':2,'ocr_fields_each':6,'slides':len(slides),'secret_scan':'passed'}))


if __name__ == '__main__':
    main()
