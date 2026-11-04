"""Freeze controlled copy-triage pairs derived from published LinkedIn text.

This is an external-text robustness diagnostic, not real Instagram copy ground truth.
Raw profiles and derived text stay under ignored outputs/.
"""
import argparse
import ast
import csv
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from evals.independent import audit

EXPECTED_CSV = '11ad526b791670fbe479d37a14be8be8801f55c4eabac20f65a92acf1683b533'


def clean(value):
    text = (value or '').strip()
    if text.startswith('[') and len(text) < 100_000:
        try:
            items = ast.literal_eval(text)
            if isinstance(items, list):
                text = ' '.join(str(item) for item in items)
        except (ValueError, SyntaxError):
            pass
    return ' '.join(text.split())


def build(source):
    data = source.read_bytes()
    if hashlib.sha256(data).hexdigest() != EXPECTED_CSV:
        raise ValueError('The published CSV changed; review the new source before use')
    csv.field_size_limit(4_000_000)
    with source.open(encoding='utf-8-sig', newline='') as stream:
        raw = list(csv.DictReader(stream))
    eligible = []
    for index, row in enumerate(raw):
        name, bio = clean(row['Full Name']), clean(row['About'])
        if row['Label'] != '0' or len(bio) < 100 or not name or name.casefold() in {'nan', 'none'}:
            continue
        identifier = hashlib.sha256(f'{EXPECTED_CSV}:{index}'.encode()).hexdigest()[:16]
        eligible.append((identifier, {'handle': 'source_'+identifier, 'display_name': name[:100], 'bio': bio[:500]}))
    eligible.sort()
    if len(eligible) < 75:
        raise ValueError('Expected at least 75 eligible source profiles')
    rows = []
    for split, start in [('train', 0), ('validation', 25), ('test', 50)]:
        cohort = eligible[start:start+25]
        for n, (group, original) in enumerate(cohort):
            other = cohort[(n+1)%len(cohort)][1]
            variants = [
                ('exact_copy', 1, {**original, 'handle': original['handle']+'.copy'}),
                ('changed_name', 1, {**original, 'handle': 'gallery_'+group, 'display_name': other['display_name']}),
                ('different_handle', 1, {**original, 'handle': 'atelier_'+group}),
                ('added_bio_text', 1, {**original, 'handle': 'new_'+group, 'bio': (original['bio'][:440]+' New page. Message this account for commissions.')[:500]}),
                ('ordinary_default_avatar', 0, other.copy()),
                ('same_name_different_bio', 0, {**other, 'handle': 'journal_'+group, 'display_name': original['display_name']}),
                ('disclosed_fan', 0, {**original, 'handle': 'fans_'+group, 'bio': ('Unofficial fan page. Not the original author. '+original['bio'])[:500]}),
                ('disclosed_parody', 0, {**original, 'handle': 'parody_'+group, 'bio': ('PARODY account. Not the real author. '+original['bio'])[:500]}),
            ]
            for kind, label, suspect in variants:
                rows.append({'id': f'{split}-{group}-{kind}', 'group': group, 'split': split,
                             'kind': kind, 'label': label, 'original': original, 'suspect': suspect})
    audit(rows)
    return {'source_url': 'https://github.com/navid-aub/LinkedIn-Dataset',
            'source_csv_article': 'https://doi.org/10.7717/peerj-cs.3182/supp-2',
            'source_csv_sha256': EXPECTED_CSV,
            'license_notice': 'Original dataset guidelines restrict use to research with citation. Raw and derived profiles are not redistributed.',
            'provenance': 'Controlled transformations of externally published legitimate profile text; no source clone pair links were available.',
            'task': 'controlled_copy_triage', 'source_profiles': 75, 'constructed_pairs': len(rows),
            'limitations': ['This is not a human-labelled Instagram impersonation test.',
                            'Handles are constructed, biographies are truncated to 500 characters, and pair labels are controlled.',
                            'Fan and parody negatives test triage context, rather than absence of literal text reuse.',
                            'No model training uses these source texts in this release.'], 'rows': rows}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=ROOT/'outputs/public-data-research/linkedin.csv')
    parser.add_argument('--out', type=Path, default=ROOT/'outputs/independent-eval/external-text-manifest.json')
    args = parser.parse_args()
    if args.out.exists():
        parser.error('Preserve the frozen manifest; choose a new output path')
    manifest = build(args.source)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(manifest, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
    print(json.dumps({'path': str(args.out), **audit(manifest['rows'])}, indent=2))
