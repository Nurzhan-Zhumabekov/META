import json

import pytest

from src import pipeline, screenshot_tools
from src.errors import ComparisonUnavailable


def result(pii=False):
    privacy = {'provider': 'presidio', 'findings': [{'entity_type': 'EMAIL_ADDRESS', 'confidence': 1., 'box': [0.1,0.2,0.4,0.3]}] if pii else [], 'count': int(pii), 'limitations': []}
    profile = {'fields': {'handle': {'value': 'alice', 'confidence': 0.99}}, 'warnings': [], 'width': 800, 'height': 900, 'privacy': privacy, 'recognized_lines': 10}
    return {'original': profile, 'suspect': profile,
            'photos': {'provider': 'imagededup', 'method': 'PHash+DHash+pixel-correlation', 'original_boxes': [], 'suspect_boxes': [], 'matches': [], 'count': 0, 'limitations': []},
            'providers': {'ocr': 'paddleocr', 'photos': 'imagededup', 'privacy': 'presidio'}, 'elapsed_seconds': 1.}


def test_inspection_ticket_is_bound_to_actual_images(monkeypatch, make_image):
    monkeypatch.setattr(screenshot_tools, 'inspect_backend', lambda *args: result())
    original, suspect = make_image(), make_image('stripes')
    preview = screenshot_tools.inspect_images(original, suspect, 'alice', 'copy')
    assert screenshot_tools.resolve(preview['inspection_id'], original, suspect)['photos']['count'] == 0
    with pytest.raises(ComparisonUnavailable) as error:
        screenshot_tools.resolve(preview['inspection_id'], suspect, original)
    assert error.value.code == 'inspection_mismatch'


def test_expired_ticket_is_not_silently_accepted(make_image):
    with pytest.raises(ComparisonUnavailable) as error:
        screenshot_tools.resolve('not-an-issued-ticket', make_image(), make_image())
    assert error.value.code == 'inspection_expired'


def test_inspection_endpoint_is_same_origin_and_does_not_save_claim(client, make_image, png, monkeypatch):
    monkeypatch.setattr(screenshot_tools, 'inspect_backend', lambda *args: result())
    files={'original':('o.png',png(make_image()),'image/png'),'suspect_image':('s.png',png(make_image()),'image/png')}
    assert client.post('/evidence/inspect', files=files).status_code == 403
    response=client.post('/evidence/inspect', files=files, headers={'Origin':'http://testserver'})
    assert response.status_code == 200
    assert response.headers['cache-control'] == 'private, no-store'
    assert response.json()['providers']['ocr'] == 'paddleocr'
    assert not pipeline.DB.exists()


def test_ocr_review_required_but_no_consent_to_unredacted_pii_and_summary_omits_text(client, make_image, png, monkeypatch):
    monkeypatch.setattr(screenshot_tools, 'inspect_backend', lambda *args: result(pii=True))
    image=make_image()
    preview=screenshot_tools.inspect_images(image,image,'alice','copy')
    data={'owner':'alice','suspect':'copy','inspection_id':preview['inspection_id']}
    files={'original':('o.png',png(image),'image/png'),'suspect_image':('s.png',png(image),'image/png')}
    response=client.post('/claims', data=data, files=files)
    assert response.status_code == 422
    assert not pipeline.DB.exists()
    response=client.post('/claims',data={**data,'ocr_reviewed':'true'},files=files)
    assert response.status_code == 200
    summary=response.json()['analysis']['screenshot_tools']
    assert summary['providers']['privacy']=='presidio'
    assert 'fields' not in summary['original']
    assert response.json()['status']=='under_review'


def test_saved_evidence_has_the_same_orientation_as_ocr_and_meta():
    from PIL import Image
    image=Image.new('RGB',(80,40),'blue')
    image.getexif()[274]=6
    claim=pipeline.submit_claim('alice','copy',image,image)
    with Image.open(pipeline.DB.parent/'evidence'/claim.id/'original.jpg') as saved:
        assert saved.size == (40,80)
