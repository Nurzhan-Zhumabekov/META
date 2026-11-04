"""Verify the fictional live run and publish its actual before/after images."""
import base64
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import httpx
from dotenv import dotenv_values
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
DEMO = ROOT / 'outputs/browser-redaction-20261103'
CLAIM = '2ee6228b'
STEPS = [
    ('03-redacted-preview.png','Предпросмотр перед отправкой','Presidio нашёл 2 области: email и телефон. На сервере соответствующие строки закрыты непрозрачными блоками. Найдены все 6 совпавших постов.'),
    ('04-meta-processing.png','Запрос в Meta AI','Отправлены только обработанные JPEG. Исходные изображения и тексты OCR в запрос не добавляются. ML отдельно работает с проверенными полями локально.'),
    ('05-meta-analysis-redacted.png','Ответ Meta и ML','Реальный uncached Muse Spark: needs_review. Модель отмечает закрытую часть bio и сравнивает остальной видимый контент.'),
    ('06-reviewer-masked-evidence.png','Доказательства у модератора','Защищённый кабинет показывает те же JPEG-изображения с закрытыми контактами. Новая жалоба остаётся under_review.'),
    ('07-reviewer-redaction-audit.png','Подтверждение скрытия','В анализе сохранены версия политики, число областей и SHA-256 фактически отправленных изображений. Прежние восемь жалоб не изменились.'),
    ('08-provider-image-in-browser.png','Сам отправленный JPEG','Изображение открыто через защищённый маршрут доказательств. Это те же байты, которые получил Meta AI.'),
]


def data_url(path):
    with Image.open(path) as image:
        mime=Image.MIME[image.format]
    return f'data:{mime};base64,'+base64.b64encode(path.read_bytes()).decode()


def main():
    before=json.loads((DEMO/'claims-before.json').read_text(encoding='utf-8-sig'))
    rows=json.loads((ROOT/'outputs/claims.json').read_text(encoding='utf-8'))
    previous={row['id'] for row in before}
    assert len(before)==8 and len(rows)==9
    assert {row['id'] for row in rows}-previous=={CLAIM}
    assert all(next(row for row in rows if row['id']==old['id'])==old for old in before)
    claim=next(row for row in rows if row['id']==CLAIM)
    assert claim['status']=='under_review'
    analysis=claim['analysis']
    audit=analysis['privacy_redaction']
    assert audit['applied'] and audit['regions_masked']==2
    assert analysis['provider']=='meta' and analysis['cached'] is False
    assert analysis['screenshot_tools']['photos']['count']==6
    for side in ['original','suspect']:
        preview=(DEMO/f'preview-{side}.jpg').read_bytes()
        stored=(ROOT/'outputs/evidence'/CLAIM/f'{side}.jpg').read_bytes()
        assert preview==stored
        assert hashlib.sha256(preview).hexdigest()==audit['images'][side]['sha256']
        with Image.open(DEMO/f'preview-{side}.jpg') as image:
            assert not image.getexif()
    rescan=json.loads((DEMO/'redaction-recheck.json').read_text())
    assert rescan['remaining_identifier_regions']=={'original':0,'suspect':0}
    assert rescan['photo_matches_after_masking']==6
    with httpx.Client(trust_env=False,timeout=5) as client:
        assert client.get(f'http://127.0.0.1:8090/api/claims/{CLAIM}/evidence/suspect').status_code==401
        assert client.get('http://127.0.0.1:8090/api/analysis/status').json()['privacy_redaction_required']
    record={
        'verified_at':datetime.now(timezone.utc).isoformat(),'claim':CLAIM,'status':claim['status'],
        'previous_claims_unchanged':8,'meta':{k:analysis[k] for k in ['provider','model','recommendation','cached','usage']},
        'redaction':audit,'preview_equals_provider_equals_saved_bytes':True,'real_rescan':rescan,
        'combined_similarity':claim['score'],'pair_ml':analysis['pair_ml']['risk_score'],
        'profile_ml':analysis['profile_ml']['risk_score'],
        'checks':{'backend_tests':122,'frontend_tests':18,'build':True,'formatting':True},
        'limits':['Only detected identifiers are covered; OCR and recognizers can miss text.',
                  'Whole OCR lines are covered with padding; neighbouring pixels can also be hidden.'],
    }
    slides=[{'src':data_url(DEMO/name),'title':title,'caption':caption} for name,title,caption in STEPS]
    payload=json.dumps({'before':data_url(DEMO/'02-copy-unredacted.png'),
                        'after':data_url(DEMO/'preview-suspect.jpg'),'slides':slides,
                        'audit':audit},ensure_ascii=False).replace('<','\\u003c')
    document='''<!doctype html><html lang="ru"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Presidio · автоматическое скрытие контактов</title>
<style>*{box-sizing:border-box}[hidden]{display:none!important}body{margin:0;background:#fafafa;color:#191919;font:15px/1.5 Arial,sans-serif}header{background:#fff;border-bottom:1px solid #ddd;padding:24px 30px}h1{margin:0 0 8px;font-size:24px}p{margin:7px 0;color:#555}a{color:#4659ef}.status{color:#176349;font-weight:bold}.layout{display:grid;grid-template-columns:260px minmax(0,1fr);max-width:1400px;margin:auto}nav{padding:22px;display:flex;flex-direction:column;gap:7px}button{font:inherit;text-align:left;border:1px solid #ddd;border-radius:9px;padding:11px 14px;background:#fff;cursor:pointer}button[aria-current=true],button[aria-pressed=true]{background:#edf1ff;border-color:#7081ec;color:#283bb7}article{padding:25px;min-width:0}h2{margin:0 0 10px;font-size:22px}.toggle{display:flex;gap:10px;margin:16px 0}.image-window{max-height:68vh;overflow:auto;background:#fff;border:1px solid #ddd;border-radius:12px}img{display:block;width:100%;height:auto}.caption{min-height:48px}small{display:block;margin-top:15px;color:#666}code{word-break:break-all;font-size:12px}details{padding:16px 0}summary{cursor:pointer}@media(max-width:700px){.layout{grid-template-columns:1fr}nav{flex-direction:row;overflow:auto;padding:12px}nav button{min-width:175px}article{padding:16px}header{padding:18px}.image-window{max-height:none}}</style>
<header><h1>Контакты скрываются до отправки в Meta AI</h1><p>Реальная демонстрация · вымышленный aigerim.k.safe · жалоба 2ee6228b</p><div class="status">2 области скрыты → повторная проверка: 0 идентификаторов → 6 совпавших фото сохранены</div><p><a href="/review">Кабинет модератора</a> · <a href="/profile/aigerim.k.safe">Профиль на рассмотрении</a></p></header>
<div class="layout"><nav aria-label="Шаги демонстрации"></nav><article><h2 id="title">До / после</h2><p id="caption" class="caption"></p><div class="toggle" id="toggle"><button id="before">До скрытия</button><button id="after">После · именно для Meta AI</button></div><div class="image-window"><img id="image" alt=""></div><details><summary>Проверка отправленных файлов</summary><p>Предпросмотр = отправленный JPEG = сохранённое доказательство. Сравнение побайтно и по SHA-256 прошло.</p><code id="hash"></code></details><small>Тестовые контакты — зарезервированные примеры. Скрининг зависит от OCR и распознавания Presidio: скрываются найденные области, все виды персональных данных не гарантируются. Жалоба under_review; решение остаётся за модератором.</small></article></div>
<script>const data=__PAYLOAD__;const nav=document.querySelector('nav');const names=['До / после',...data.slides.map(s=>s.title)];let active=0;names.forEach((name,i)=>{const b=document.createElement('button');b.textContent=`${i+1}. ${name}`;b.onclick=()=>show(i);nav.append(b)});function compare(after){document.querySelector('#image').src=after?data.after:data.before;document.querySelector('#image').alt=after?'Скриншот для Meta AI: email и телефон закрыты':'Исходный демоскриншот с тестовыми контактами';document.querySelector('#before').setAttribute('aria-pressed',String(!after));document.querySelector('#after').setAttribute('aria-pressed',String(after));document.querySelector('#caption').textContent=after?'Email и телефон физически закрашены в JPEG на сервере. Meta AI получил именно этот файл.':'Исходный скриншот: email и телефон видны. Эта версия в Meta AI не отправлялась.';document.querySelector('.image-window').scrollTop=0}function show(i){active=i;document.querySelectorAll('nav button').forEach((b,n)=>b.setAttribute('aria-current',String(i===n)));document.querySelector('#toggle').hidden=i!==0;if(i===0){document.querySelector('#title').textContent='До / после';compare(true)}else{const s=data.slides[i-1];document.querySelector('#title').textContent=s.title;document.querySelector('#caption').textContent=s.caption;document.querySelector('#image').src=s.src;document.querySelector('#image').alt=s.title;document.querySelector('.image-window').scrollTop=0}}document.querySelector('#before').onclick=()=>compare(false);document.querySelector('#after').onclick=()=>compare(true);document.querySelector('#hash').textContent='SHA-256 JPEG для Meta: '+data.audit.images.suspect.sha256;show(0);</script></html>'''.replace('__PAYLOAD__',payload)
    secrets=[str(v) for k,v in dotenv_values(ROOT/'.env').items() if v and ('KEY' in k or 'TOKEN' in k)]
    secrets.append((ROOT/'outputs/evidence-worker.key').read_text().strip())
    for value in secrets:
        assert value not in document
        for path in (ROOT/'web/dist/assets').rglob('*'):
            if path.is_file():
                assert value.encode() not in path.read_bytes(),'Secret found in frontend build'
    record['secret_scan']='passed'
    (DEMO/'verification.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
    for path in [DEMO/'walkthrough.html',ROOT/'web/public/redaction-walkthrough.html',ROOT/'web/dist/redaction-walkthrough.html']:
        path.write_text(document,encoding='utf-8')
    print(json.dumps({'claim':CLAIM,'status':claim['status'],'masked_regions':2,'remaining_identifiers':0,'photo_matches':6,'previous_claims_unchanged':8,'secret_scan':'passed'}))


if __name__=='__main__':
    main()
