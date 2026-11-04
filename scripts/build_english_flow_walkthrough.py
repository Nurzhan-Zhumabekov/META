"""Publish the actual fictional English browser run and verify its persistence."""
import base64
import hashlib
import html
import json
from datetime import datetime, timezone
from pathlib import Path

import httpx
from dotenv import dotenv_values
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
DEMO = ROOT / 'outputs/browser-english-flow-20261104'
HANDLE = 'aigerim.k.archive'
STEPS = [
    ('01-original-profile.png', 'Original profile', 'The original fictional profile: aigerim.k, 128 posts, 5,400 followers and 310 following.'),
    ('02-copy-before-report.png', 'Copy before the report', 'The new fictional copy reuses the name, bio and six post images. No review or impersonation label is present yet.'),
    ('03-report-reason.png', 'Report the account', 'Choose Report account, then Pretending to be someone else.'),
    ('04-ocr-processing.png', 'Inspect screenshots locally', 'Upload both actual browser screenshots. PaddleOCR reads fields, imagededup compares image regions and Presidio checks identifiers.'),
    ('05-ocr-redaction-preview.png', 'Review the masked preview', 'Presidio masks the example email and phone before Meta AI. The previews are the actual JPEG files prepared for the provider.'),
    ('06-reviewed-ml-fields.png', 'Review the ML inputs', 'Correct OCR errors against the screenshots, review the counts and enable both profile ML and the two-profile text comparison.'),
    ('07-meta-processing.png', 'Real Meta AI analysis', 'Submit the report. Only the processed screenshots go to Meta AI; the local models evaluate the reviewed profile fields separately.'),
    ('08-report-receipt.png', 'Report received', 'The report is Under review. AI results alone do not add an impersonation label.'),
    ('09-meta-and-ml-results.png', 'Meta AI and ML results', 'The actual English Meta response and independent ML signals are shown. These scores are not proof of identity or account ownership.'),
    ('10-profile-under-review.png', 'Profile under review', 'The profile shows Account under review while waiting for an explicit moderator decision.'),
    ('11-moderator-evidence.png', 'Moderator checks the evidence', 'The authenticated moderator reviews the same processed images, the provider observations and the local ML results.'),
    ('12-moderator-decision.png', 'Human decision', 'After examining the evidence, the moderator chooses Confirm impersonation for this fictional demo account.'),
    ('13-decision-saved.png', 'Decision saved', 'The server saves the moderator decision. Other reports remain unchanged.'),
    ('14-profile-labelled.png', 'Profile warning appears', 'The profile now shows Impersonation confirmed after the separate moderator action.'),
    ('15-label-after-reload.png', 'Warning persists after reload', 'Reloading the profile retains the warning because the confirmed decision is stored on the server.'),
]


def image_url(path):
    raw = path.read_bytes()
    with Image.open(path) as image:
        mime = Image.MIME[image.format]
    return f'data:{mime};base64,' + base64.b64encode(raw).decode()


def main():
    before = json.loads((DEMO / 'claims-before.json').read_text(encoding='utf-8'))
    after = json.loads((ROOT / 'outputs/claims.json').read_text(encoding='utf-8'))
    previous = {row['id']: row for row in before}
    fresh = [row for row in after if row['id'] not in previous]
    assert len(before) == 9 and len(after) == 10 and len(fresh) == 1
    assert all(next(row for row in after if row['id'] == old_id) == old for old_id, old in previous.items())
    claim = fresh[0]
    assert claim['suspect_handle'] == HANDLE and claim['status'] == 'confirmed'
    analysis = claim['analysis']
    assert analysis['provider'] == 'meta' and analysis['cached'] is False
    assert analysis['prompt_version'] == 'impersonation-evidence-v2-en'
    assert analysis['pair_ml']['risk_score'] is not None and analysis['profile_ml']['risk_score'] is not None
    assert analysis['screenshot_tools']['ocr_reviewed']
    audit = analysis['privacy_redaction']
    assert audit['applied'] and audit['regions_masked'] >= 2
    for side in ['original', 'suspect']:
        preview = (DEMO / f'preview-{side}.jpg').read_bytes()
        saved = (ROOT / 'outputs/evidence' / claim['id'] / f'{side}.jpg').read_bytes()
        assert preview == saved
        assert hashlib.sha256(saved).hexdigest() == audit['images'][side]['sha256']
        with Image.open(DEMO / f'preview-{side}.jpg') as image:
            assert not image.getexif()
    with httpx.Client(trust_env=False, timeout=6) as client:
        assert client.get('http://127.0.0.1:8090/api/statuses').json()[HANDLE] == 'confirmed'
        evidence_status = client.get(f"http://127.0.0.1:8090/api/claims/{claim['id']}/evidence/suspect").status_code
        assert evidence_status == 401
    record = {
        'verified_at': datetime.now(timezone.utc).isoformat(), 'claim_id': claim['id'],
        'handle': HANDLE, 'status': claim['status'], 'previous_claims_unchanged': len(before),
        'meta': {k: analysis[k] for k in ['provider', 'model', 'recommendation', 'prompt_version', 'cached', 'usage']},
        'combined_similarity': claim['score'], 'profile_ml': analysis['profile_ml']['risk_score'],
        'pair_ml': analysis['pair_ml']['risk_score'], 'matched_regions': analysis['screenshot_tools']['photos']['count'],
        'redaction': audit, 'preview_equals_stored_provider_bytes': True,
        'unauthenticated_evidence_status': evidence_status,
        'manual_review': 'Corrected the reported display name and bio, and restored the omitted first original-bio line from the visible screenshots.',
        'demo_data': 'Fictional local accounts and reserved example contact details.',
    }
    rescanned = DEMO / 'redaction-recheck.json'
    if rescanned.exists():
        record['local_redaction_rescan'] = json.loads(rescanned.read_text(encoding='utf-8'))
    slides = [{'title': title, 'caption': caption, 'image': image_url(DEMO / name)} for name, title, caption in STEPS]
    metrics = {
        'Meta recommendation': analysis['recommendation'],
        'Combined similarity': f"{claim['score']:.1%}",
        'Pair ML · text reuse': f"{analysis['pair_ml']['risk_score']:.1%}",
        'Profile ML · spam patterns': f"{analysis['profile_ml']['risk_score']:.1%}",
        'Matched image regions': str(record['matched_regions']),
        'Personal data regions masked': str(audit['regions_masked']),
    }
    pills = ''.join(f'<span><small>{html.escape(label)}</small><b>{html.escape(value)}</b></span>' for label, value in metrics.items())
    payload = json.dumps(slides, ensure_ascii=True).replace('<', '\\u003c')
    document = '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>English demo · Report → Meta AI + ML → Moderator → Profile label</title>
<style>*{box-sizing:border-box}body{margin:0;background:#fafafa;color:#14171a;font:14px/1.5 system-ui,sans-serif}header{padding:22px 28px;border-bottom:1px solid #e3e5e7;background:white}h1{font-size:25px;margin:0 0 8px}p{margin:6px 0;color:#60666c}a{color:#4458e9}.metrics{display:flex;flex-wrap:wrap;gap:8px;margin:16px 0}.metrics>span{background:#f3f5f8;padding:9px 13px;border-radius:8px}.metrics small,.metrics b{display:block}.metrics small{color:#697078;font-size:11px}.layout{display:grid;grid-template-columns:270px minmax(0,1fr);max-width:1500px;margin:auto}nav{padding:20px;display:flex;flex-direction:column;gap:6px}button{font:inherit;cursor:pointer;border:1px solid #ddd;background:white;border-radius:9px;padding:9px 12px;text-align:left}nav button[aria-current=true]{background:#edf0ff;color:#2e42bd;border-color:#8d9bed}article{padding:22px;min-width:0}h2{font-size:22px;margin:0 0 8px}.controls{display:flex;align-items:center;gap:12px;margin:14px 0}.viewer{background:white;border:1px solid #ddd;border-radius:12px;max-height:72vh;overflow:auto}.viewer img{display:block;max-width:100%;height:auto;margin:auto}.footnote{font-size:12px;margin-top:14px}button:disabled{opacity:.4;cursor:default}@media(max-width:760px){header{padding:18px}h1{font-size:21px}.layout{grid-template-columns:1fr}nav{flex-direction:row;overflow:auto;padding:12px}nav button{min-width:180px}article{padding:16px}.viewer{max-height:none}}</style>
<header><h1>Report → Meta AI + ML → Moderator → Profile label</h1><p>Actual browser captures · English interface · Fictional local demonstration · Claim __CLAIM__</p><div class="metrics">__METRICS__</div><p><a href="/profile/aigerim.k.archive">Open the labelled profile</a> · <a href="/review">Report review center</a> · <a href="/">Back to Instagram concept</a></p></header>
<div class="layout"><nav aria-label="Walkthrough steps"></nav><article><h2 id="title"></h2><p id="caption"></p><div class="controls"><button id="previous">← Previous</button><span id="position" aria-live="polite"></span><button id="next">Next →</button></div><div class="viewer"><img id="shot" alt=""></div><p class="footnote">These are real captures from the local demo, not a modification of Instagram. Meta and ML scores do not prove ownership. Pair ML uses synthetic training data. Matching regions may cover a group of posts. Original report records remain unchanged; this one was confirmed by a separate moderator action.</p></article></div>
<script>const slides=__SLIDES__;let current=0;const nav=document.querySelector('nav');slides.forEach((s,i)=>{const b=document.createElement('button');b.textContent=(i+1)+'. '+s.title;b.onclick=()=>show(i);nav.append(b)});function show(i){current=Math.max(0,Math.min(slides.length-1,i));const s=slides[current];document.querySelector('#title').textContent=s.title;document.querySelector('#caption').textContent=s.caption;document.querySelector('#shot').src=s.image;document.querySelector('#shot').alt='Step '+(current+1)+': '+s.title;document.querySelector('#position').textContent=(current+1)+' / '+slides.length;document.querySelectorAll('nav button').forEach((b,n)=>b.setAttribute('aria-current',String(n===current)));document.querySelector('#previous').disabled=current===0;document.querySelector('#next').disabled=current===slides.length-1;document.querySelector('.viewer').scrollTop=0}document.querySelector('#previous').onclick=()=>show(current-1);document.querySelector('#next').onclick=()=>show(current+1);document.addEventListener('keydown',e=>{if(e.key==='ArrowLeft')show(current-1);if(e.key==='ArrowRight')show(current+1)});show(0);</script></html>'''
    document = document.replace('__CLAIM__', html.escape(claim['id'])).replace('__METRICS__', pills).replace('__SLIDES__', payload)
    secrets = [str(v) for k, v in dotenv_values(ROOT / '.env').items() if v and ('KEY' in k or 'TOKEN' in k)]
    secrets.append((ROOT / 'outputs/evidence-worker.key').read_text().strip())
    for secret in secrets:
        assert secret not in document
    record['secret_scan'] = 'passed'
    (DEMO / 'verification.json').write_text(json.dumps(record, ensure_ascii=True, indent=2), encoding='utf-8')
    for path in [DEMO / 'walkthrough.html', ROOT / 'web/public/english-report-walkthrough.html', ROOT / 'web/dist/english-report-walkthrough.html']:
        path.write_text(document, encoding='utf-8')
    print(json.dumps({key: record[key] for key in ['claim_id', 'status', 'previous_claims_unchanged', 'meta', 'combined_similarity', 'profile_ml', 'pair_ml', 'matched_regions']}))


if __name__ == '__main__':
    main()
