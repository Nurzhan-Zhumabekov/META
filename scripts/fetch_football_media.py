"""Fetch attributed Commons football photos without editing source image bytes."""
import html
import json
import re
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import httpx

ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/'web/public/media/football'
HEADERS={'User-Agent':'Codex/0.166 (https://openai.com/codex/; local educational prototype image import)'}
FILES={
    'ronaldo':'Cristiano Ronaldo with Al Nassr, 19 September 2023 - 60 (cropped).jpg',
    'messi':'Lionel-Messi-Argentina-2022-FIFA-World-Cup (cropped).jpg',
    'mbappe':'Kylian Mbappé (46369981091).jpg',
    'haaland':'Erling Haaland 2023 (cropped-v2).jpg',
    'bellingham':'Jude Bellingham England v Panama 27 June 26-160 (cropped).jpg',
    'salah':'Mohamed salah.jpg',
    'neymar':'Neymar Jr. with Al Hilal, 3 October 2023 - 04 (cropped).jpg',
    'vini':'Vinicius Jr 2021.jpg',
}


def main():
    DEST.mkdir(parents=True,exist_ok=True)
    with httpx.Client(headers=HEADERS,timeout=30,follow_redirects=True) as client:
        response=client.get('https://commons.wikimedia.org/w/api.php',params={
            'action':'query','format':'json','titles':'|'.join('File:'+name for name in FILES.values()),
            'prop':'imageinfo','iiprop':'url|extmetadata','iiurlwidth':960})
        response.raise_for_status()
        pages={p['title']:p for p in response.json()['query']['pages'].values()}
        def download(entry):
            slug,name=entry
            info=pages['File:'+name]['imageinfo'][0]
            url=info.get('thumburl',info['url'])
            photo=client.get(url);photo.raise_for_status()
            if not photo.headers.get('content-type','').startswith('image/'):
                raise ValueError('Image expected')
            (DEST/(slug+'.jpg')).write_bytes(photo.content)
            metadata=info['extmetadata']
            clean=lambda key:html.unescape(re.sub('<[^>]+>','',metadata.get(key,{}).get('value','')))
            return {'file':slug+'.jpg','source':info['descriptionurl'],'author':clean('Artist'),
                    'license':clean('LicenseShortName'),'license_url':clean('LicenseUrl'),
                    'changes':'Source bytes unchanged; CSS object-fit crops in the interface.'}
        credits=list(ThreadPoolExecutor(max_workers=3).map(download,FILES.items()))
        extras={
            'pitch':'https://images.unsplash.com/photo-1579952363873-27f3bade9f55?auto=format&fit=crop&w=1100&q=85',
            'stadium':'https://images.unsplash.com/photo-1522778119026-d647f0596c20?auto=format&fit=crop&w=1100&q=85',
            'matchday':'https://images.unsplash.com/photo-1431324155629-1a6deb1dec8d?auto=format&fit=crop&w=1100&q=85',
            'training':'https://images.unsplash.com/photo-1518604666860-9ed391f76460?auto=format&fit=crop&w=1100&q=85',
        }
        for slug,url in extras.items():
            photo=client.get(url);photo.raise_for_status()
            if not photo.headers.get('content-type','').startswith('image/'):
                raise ValueError('Image expected')
            (DEST/(slug+'.jpg')).write_bytes(photo.content)
            credits.append({'file':slug+'.jpg','source':url,'author':'Unsplash contributors',
                            'license':'Unsplash License','license_url':'https://unsplash.com/license',
                            'changes':'Unsplash CDN supplied display size; CSS crop only.'})
    (DEST/'credits.json').write_text(json.dumps(credits,ensure_ascii=False,indent=2),encoding='utf-8')
    rows=''.join('<tr><td>'+html.escape(c['file'])+'</td><td>'+html.escape(c['author'])+'</td><td><a href="'+html.escape(c['source'],quote=True)+'">Source</a></td><td><a href="'+html.escape(c['license_url'],quote=True)+'">'+html.escape(c['license'])+'</a></td></tr>' for c in credits)
    (ROOT/'web/public/photo-credits.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Photo credits</title><style>body{font:15px/1.5 system-ui;max-width:1100px;margin:40px auto;padding:20px}td,th{padding:12px;text-align:left;border-bottom:1px solid #ddd}a{color:#4054d8}table{width:100%;border-collapse:collapse}</style><h1>Photo credits</h1><p>Unofficial local concept. Football accounts are fictional fan profiles; posts and statistics are demo data. Photographs do not imply endorsement. Source bytes are unchanged; display crops use CSS.</p><table><tr><th>File</th><th>Author</th><th>Source</th><th>License</th></tr>'+rows+'</table><p><a href="/">Back to the app</a></p></html>',encoding='utf-8')
    print(json.dumps({'downloaded':len(credits),'directory':str(DEST)}))


if __name__=='__main__':main()
