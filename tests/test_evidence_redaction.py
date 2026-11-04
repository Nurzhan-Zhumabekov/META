import base64
import hashlib
import io
import json

import httpx
import pytest
from PIL import Image

from src import config, pipeline, screenshot_tools
from src.errors import ComparisonUnavailable
from src.meta_compare import MetaComparer, reset_meta_state


def inspection_result():
    findings = [
        {'entity_type': 'EMAIL_ADDRESS', 'confidence': 1., 'box': [.2,.2,.8,.3]},
        {'entity_type': 'PHONE_NUMBER', 'confidence': .75, 'box': [.2,.4,.8,.5]},
    ]
    profile = {'fields': {'handle': {'value': 'alice', 'confidence': .99}},
               'warnings': [], 'width': 800, 'height': 900,
               'privacy': {'provider': 'presidio', 'findings': findings, 'count': 2, 'limitations': []},
               'recognized_lines': 3}
    return {'original': profile, 'suspect': profile,
            'photos': {'provider':'imagededup', 'method':'PHash+DHash+pixel-correlation',
                       'original_boxes':[], 'suspect_boxes':[], 'matches':[], 'count':0, 'limitations':[]},
            'providers':{'ocr':'paddleocr','photos':'imagededup','privacy':'presidio'}, 'elapsed_seconds':1.}


def response():
    return httpx.Response(200, json={'choices':[{'finish_reason':'stop','message':{'content':json.dumps({
        'similarity_score':.8,'summary':'Visible reuse; contact lines are hidden.',
        'evidence':['Same public display name.'],'differences':[],
        'limitations':['Masked contact text cannot be compared.'],'recommendation':'needs_review'})}}], 'usage':{}})


def test_preview_is_burned_in_and_exactly_matches_provider_and_saved_evidence(monkeypatch):
    monkeypatch.setattr(config, 'COMPARER', 'meta')
    monkeypatch.setattr(config, 'META_API_KEY', 'unit-test-only')
    monkeypatch.setattr(screenshot_tools, 'inspect_backend', lambda *args: inspection_result())
    reset_meta_state()
    image=Image.new('RGB',(800,900),'white')
    image.getexif()[270]='private original metadata'
    preview=screenshot_tools.inspect_images(image,image,'alice','copy')
    urls=preview['redaction']['previews']
    calls=[]
    def handler(request):
        calls.append(json.loads(request.content))
        return response()
    monkeypatch.setattr(pipeline, 'get_comparer', lambda: MetaComparer(client=httpx.Client(transport=httpx.MockTransport(handler))))
    # Legacy callers without inspection_id must also run local redaction.
    claim=pipeline.submit_claim('alice','copy',image,image)
    sent=[p['image_url']['url'] for p in calls[0]['messages'][1]['content'] if p['type']=='image_url']
    assert sent == [urls['original'],urls['suspect']]
    audit=claim.analysis['privacy_redaction']
    assert audit['applied'] is True and audit['regions_masked']==4
    for side,url in zip(['original','suspect'],sent):
        raw=base64.b64decode(url.split(',',1)[1])
        assert hashlib.sha256(raw).hexdigest()==audit['images'][side]['sha256']
        assert (pipeline.DB.parent/'evidence'/claim.id/f'{side}.jpg').read_bytes()==raw
        with Image.open(io.BytesIO(raw)) as masked:
            assert max(masked.getpixel((400,225)))<25
            assert max(masked.getpixel((400,405)))<25
            assert min(masked.getpixel((400,700)))>240
            assert not masked.getexif()
    assert image.getpixel((400,225))==(255,255,255), 'Do not mutate the uploaded source image'


def test_privacy_failure_prevents_provider_request_and_claim_creation(monkeypatch,make_image):
    monkeypatch.setattr(config,'COMPARER','meta')
    monkeypatch.setattr(config,'META_API_KEY','unit-test-only')
    calls=[]
    def unavailable(*args):
        raise ComparisonUnavailable('evidence_tools_unavailable','Local privacy check unavailable',503)
    monkeypatch.setattr(screenshot_tools,'inspect_backend',unavailable)
    monkeypatch.setattr(pipeline,'get_comparer',lambda:MetaComparer(client=httpx.Client(transport=httpx.MockTransport(lambda request:calls.append(request)))))
    with pytest.raises(ComparisonUnavailable):
        pipeline.submit_claim('alice','copy',make_image(),make_image())
    assert calls==[]
    assert not pipeline.DB.exists()
    assert not (pipeline.DB.parent/'evidence').exists()


@pytest.mark.parametrize('box',[[.8,.2,.1,.3],[.1,.5,.4,.2],[0.,0.,float('nan'),.2]])
def test_invalid_redaction_coordinates_fail_closed(monkeypatch,make_image,box):
    result=inspection_result()
    result['original']['privacy']['findings'][0]['box']=box
    monkeypatch.setattr(screenshot_tools,'inspect_backend',lambda *args:result)
    with pytest.raises(ComparisonUnavailable):
        screenshot_tools.inspect_images(make_image(),make_image(),'alice','copy')


def test_masks_follow_exif_display_orientation_and_metadata_is_removed():
    from src.evidence_redaction import redact_pair
    source=Image.new('RGB',(80,40),'white')
    source.getexif()[274]=6
    masked=redact_pair(source,source,inspection_result())
    with Image.open(io.BytesIO(masked.raw[0])) as image:
        assert image.size==(40,80)
        assert max(image.getpixel((20,20)))<30
        assert min(image.getpixel((20,65)))>230
        assert not image.getexif()
