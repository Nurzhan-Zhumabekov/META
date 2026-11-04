"""Copydays photo-region diagnostic in controlled screenshot grids.

Only evaluation: never changes thresholds, models, claims or provider configuration.
"""
import argparse
import hashlib
import json
from pathlib import Path
import random
import re
import shutil
import tarfile

from PIL import Image, ImageDraw, ImageOps
from evidence_tools.photos import compare_photos
from evals.metrics import binary_metrics


def prepare(root):
    for kind in ('original', 'strong'):
        target = root / 'copydays' / kind
        target.mkdir(parents=True, exist_ok=True)
        with tarfile.open(root/f'copydays-{kind}.tar.gz') as archive:
            for member in archive:
                if not member.isfile() or not re.fullmatch(r'[0-9]{6}\.jpg', member.name):
                    continue
                if member.size > 20_000_000:
                    raise ValueError('Unexpected image size')
                path = target/member.name
                if path.exists():
                    try:
                        with Image.open(path) as existing:
                            if max(existing.size) <= 1200:
                                existing.verify()
                                continue
                    except OSError:
                        pass
                with archive.extractfile(member) as source:
                    image = Image.open(source).convert('RGB')
                    image.thumbnail((1200,1200),Image.Resampling.LANCZOS)
                    image.save(path,'JPEG',quality=92)
    originals = {p.stem[:4]: p for p in (root/'copydays/original').glob('*.jpg')}
    strong = {}
    for p in sorted((root/'copydays/strong').glob('*.jpg')):
        if p.stem[:4] in originals:
            strong.setdefault(p.stem[:4], p)
    identifiers = sorted(strong, key=lambda s: hashlib.sha256(('copydays-v1:'+s).encode()).hexdigest())
    if len(identifiers) < 100:
        raise ValueError('Expected 100 distinct Copydays source blocks')
    rows = []
    for split, ids in [('validation', identifiers[:50]), ('test', identifiers[50:100])]:
        for identity in ids:
            rng = random.Random('copydays-grid-v1:'+identity)
            others = rng.sample([i for i in ids if i != identity], 11)
            original = [originals[identity], *[originals[i] for i in others[:5]]]
            for label, kind, suspect in [(1, 'strong_copy', [strong[identity], *[originals[i] for i in others[5:10]]]),
                                         (0, 'distinct_photos', [originals[i] for i in others[5:11]])]:
                rows.append({'id': f'{identity}-{kind}', 'group': identity, 'split': split, 'label': label,
                             'kind': kind, 'original': [str(p.resolve()) for p in original],
                             'suspect': [str(p.resolve()) for p in suspect]})
    return {'source_url': 'https://thoth.inrialpes.fr/~jegou/data.php.html#copydays',
            'download_source': 'https://dl.fbaipublicfiles.com/vissl/datasets/',
            'license_notice': 'INRIA copyright; dataset provided for copy-detection research. No images are redistributed.',
            'task': 'copied_photo_region_detection', 'layout': 'controlled 3x2 screenshot grid',
            'preprocessing': 'Source images resized to at most 1200 pixels and JPEG quality 92 before screenshot-grid rendering.',
            'selection': 'first 100 source blocks ordered by SHA256(copydays-v1:block); first strong query per block',
            'archive_sha256': {k: hashlib.sha256((root/f'copydays-{k}.tar.gz').read_bytes()).hexdigest() for k in ('original','strong')},
            'rows': rows}


def grid(paths):
    image = Image.new('RGB', (800, 950), 'white')
    draw = ImageDraw.Draw(image)
    draw.text((35, 55), 'Fictional demonstration profile', fill='black')
    draw.text((35, 85), 'Copydays photo-region benchmark', fill='black')
    for index, path in enumerate(paths):
        with Image.open(path) as raw:
            tile = ImageOps.fit(raw.convert('RGB'), (240, 240))
        image.paste(tile, (30+(index%3)*243, 330+(index//3)*243))
    return image


def overlap(a, b):
    intersection = max(0, min(a[2],b[2])-max(a[0],b[0]))*max(0,min(a[3],b[3])-max(a[1],b[1]))
    return intersection / max(1e-9,(a[2]-a[0])*(a[3]-a[1])+(b[2]-b[0])*(b[3]-b[1])-intersection)


def run(manifest, split):
    rows = []
    target = [30/800,330/950,270/800,570/950]
    for case in manifest['rows']:
        if case['split'] != split:
            continue
        result = compare_photos(grid(case['original']), grid(case['suspect']))
        correct = any(overlap(result['original_boxes'][m['original_index']],target)>.7 and
                      overlap(result['suspect_boxes'][m['suspect_index']],target)>.7 for m in result['matches'])
        prediction = bool(correct) if case['label'] else bool(result['count'])
        rows.append({'id': case['id'], 'label': case['label'], 'score': float(prediction),
                     'matches': result['count'], 'original_regions': len(result['original_boxes']),
                     'suspect_regions': len(result['suspect_boxes'])})
        if len(rows)%20 == 0:
            print(json.dumps({'evaluated': len(rows), 'split': split}), flush=True)
    return {'source_url': manifest['source_url'], 'task': manifest['task'], 'split': split,
            'layout': manifest['layout'], 'metrics': binary_metrics([r['label'] for r in rows],[r['score'] for r in rows],.5),
            'provider_requests': 0, 'results': rows,
            'limitations': ['Controlled screenshot layout and one strong query per source block.',
                            'Photo matching is not account ownership or impersonation detection.']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path('outputs/public-data-research'))
    parser.add_argument('--manifest', type=Path, default=Path('outputs/independent-eval/copydays-manifest.json'))
    parser.add_argument('--split', choices=['validation', 'test'], default='validation')
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--matcher', choices=['baseline','current'], default='current')
    args = parser.parse_args()
    if args.out.exists():
        parser.error('Use a new report path')
    if args.manifest.exists():
        manifest = json.loads(args.manifest.read_text(encoding='utf-8'))
    else:
        manifest = prepare(args.root)
        args.manifest.parent.mkdir(parents=True, exist_ok=True)
        args.manifest.write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    if args.matcher == 'baseline':
        from evals.photo_baseline import compare_photos
    report = run(manifest,args.split)
    report['manifest_sha256'] = hashlib.sha256(args.manifest.read_bytes()).hexdigest()
    report['matcher_sha256'] = hashlib.sha256(Path('evals/photo_baseline.py' if args.matcher == 'baseline' else 'evidence_tools/photos.py').read_bytes()).hexdigest()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k != 'results'},indent=2))
