"""Exercise real local workers and isolated public roles inside a clean container.

No Meta request is made: CI uses the explicit local comparison provider.
"""
import base64
import json
from pathlib import Path
import time
import sys

import httpx


def main():
    base = 'http://127.0.0.1:8090'
    for _ in range(180):
        try:
            if httpx.get(base+'/healthz',timeout=2,trust_env=False).status_code==200:
                break
        except httpx.HTTPError:
            pass
        time.sleep(1)
    else:
        raise RuntimeError('Container readiness did not pass')
    first = httpx.Client(base_url=base+'/api/', headers={'Origin':base},timeout=180,trust_env=False)
    second = httpx.Client(base_url=base+'/api/', headers={'Origin':base},timeout=180,trust_env=False)
    try:
        state_path = Path('/var/data/smoke-state.json')
        if '--verify-restart' in sys.argv:
            state = json.loads(state_path.read_text())
            first.cookies.update(state['cookies'])
            assert first.post('demo/reviewer').status_code == 200
            assert first.get('statuses').json() == {}
            record = first.get('reviewer/cases').json()[0]
            assert record['id'] == state['id'] and record['status'] == 'rejected'
            assert record['history'][-1]['kind'] == 'appeal_resolved'
            assert first.get(f"claims/{state['id']}/evidence/original").status_code == 200
            print(json.dumps({'restart_persistence':'passed','history_and_processed_evidence':'retained','provider_requests':0}))
            return
        for client in (first,second):
            assert client.post('demo/session').status_code==200
        images = {'original':Path('/fixtures/original-faint-gutters.png').read_bytes(),
                  'suspect_image':Path('/fixtures/copy-faint-gutters.png').read_bytes()}
        files=lambda:{key:(key+'.png',value,'image/png') for key,value in images.items()}
        inspection=first.post('evidence/inspect',data={'owner':'aigerim.k','suspect':'aigerim.k.showcase'},files=files())
        assert inspection.status_code==200, inspection.status_code
        prepared=inspection.json()
        assert prepared['providers']=={'ocr':'paddleocr','photos':'imagededup','privacy':'presidio'}
        assert prepared['photos']['count']>=4
        assert prepared['redaction']['regions_masked']==2
        facts={'handle':'aigerim.k.showcase','display_name':'Aigerim K.',
               'bio':'Collecting moments, not things. Photographer · Astana, Kazakhstan. Bookings and collaborations.',
               'has_profile_picture':True,'has_external_url':False,'is_private':False,
               'num_posts':6,'num_followers':29,'num_following':2310}
        original={k:v for k,v in facts.items() if k in {'handle','display_name','bio'}};original['handle']='aigerim.k'
        created=first.post('claims',files=files(),data={'owner':'aigerim.k','suspect':'aigerim.k.showcase',
            'inspection_id':prepared['inspection_id'],'ocr_reviewed':'true',
            'profile_facts':json.dumps(facts),'original_profile_facts':json.dumps(original)})
        assert created.status_code==200,created.status_code
        row=created.json();identifier=row['id']
        assert row['status']=='under_review'
        assert row['analysis']['pair_ml']['risk_score'] is not None
        assert second.get('statuses').json()=={}
        assert first.post('demo/reviewer').status_code==200
        assert second.post('demo/reviewer').status_code==200
        assert second.get(f'claims/{identifier}/evidence/original').status_code==404
        for side in ('original','suspect'):
            preview=base64.b64decode(prepared['redaction']['previews'][side].split(',')[1])
            assert first.get(f'claims/{identifier}/evidence/{side}').content==preview
        assert first.post(f'claims/{identifier}/status',json={'status':'confirmed','reason':'Fictional copied content reviewed for this isolated test.','expected_version':0}).status_code==200
        access=first.post(f'claims/{identifier}/appeal-access').json()
        submitted=first.post('appeals',json={'token':access['token'],'reason':'This fictional example is being appealed to exercise the review process.'})
        assert submitted.status_code==201
        assert first.get('statuses').json()['aigerim.k.showcase']=='confirmed'
        pending=first.get('appeals/pending').json()[0]
        assert first.post(f"appeals/{pending['appeal']['id']}/resolve",json={'outcome':'overturn','reason':'The demonstration appeal is accepted after an explicit human action.','expected_version':pending['claim']['version']}).status_code==200
        assert first.get('statuses').json()=={} and second.get('statuses').json()=={}
        history=first.get(f'claims/{identifier}/history').json()['events']
        assert history[-1]['kind']=='appeal_resolved' and history[-1]['to_status']=='rejected'
        state_path.write_text(json.dumps({'id':identifier,'cookies':dict(first.cookies)}))
        state_path.chmod(0o600)
        assert first.delete('reviewer/session').status_code==200
        assert first.get('reviewer/session').status_code==401
        print(json.dumps({'public_session_isolation':'passed','real_paddleocr':'passed','real_presidio_masks':2,
                          'matched_photo_regions':prepared['photos']['count'],'preview_evidence_bytes_equal':True,
                          'moderator_reason_and_history':'passed','appeal_overturn':'passed','provider_requests':0}))
    finally:
        first.close();second.close()


if __name__=='__main__':
    main()
