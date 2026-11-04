"""Frozen, account-disjoint profile-pair evaluation. No network or claim writes."""
import argparse
import hashlib
import json
from pathlib import Path

from evals.metrics import binary_metrics
from src.pair_ml import score_pair
from src.profile_ml import ProfileText


def fingerprint(row):
    data = {k: row[k] for k in ('original', 'suspect')}
    return hashlib.sha256(json.dumps(data, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def audit(rows):
    if not rows:
        raise ValueError('Dataset is empty')
    identifiers, pairs, accounts, groups = set(), set(), {}, {}
    counts = {}
    for row in rows:
        identifier, group, split = row['id'], row['group'], row['split']
        if split not in {'train', 'validation', 'test'} or type(row['label']) is not int or row['label'] not in {0, 1}:
            raise ValueError('Expected a declared split and binary labels')
        digest = fingerprint(row)
        if identifier in identifiers or digest in pairs:
            raise ValueError('Dataset contains duplicate pairs or IDs')
        identifiers.add(identifier); pairs.add(digest)
        if group in groups and groups[group] != split:
            raise ValueError('Identity group overlap between splits')
        groups[group] = split
        for kind in ('original', 'suspect'):
            profile = ProfileText.model_validate({key: row[kind][key] for key in ('handle', 'display_name', 'bio')})
            handle = profile.handle.lstrip('@').casefold()
            if handle in accounts and accounts[handle] != split:
                raise ValueError('account overlap between splits')
            accounts[handle] = split
        counts[split] = counts.get(split, 0) + 1
    return {'pairs': len(rows), 'groups': len(groups), 'accounts': len(accounts), 'split_counts': counts,
            'cross_split_account_overlap': 0, 'duplicate_pairs': 0,
            'manifest_sha256': hashlib.sha256(json.dumps(rows, sort_keys=True, ensure_ascii=False).encode()).hexdigest()}


def evaluate(rows, meta_results=None, *, split='test'):
    quality = audit(rows)
    test = [r for r in rows if r['split'] == split]
    if not test:
        raise ValueError('A frozen test split is required')
    predictions = []
    threshold = None
    for row in test:
        original, suspect = [ProfileText.model_validate({key: row[kind][key] for key in ('handle', 'display_name', 'bio')}) for kind in ('original', 'suspect')]
        result = score_pair(original, suspect)
        if threshold is not None and threshold != result['threshold']:
            raise ValueError('Model threshold changed during evaluation')
        threshold = result['threshold']
        meta = (meta_results or {}).get(row['id'])
        if meta is not None and meta.get('input_sha256') != fingerprint(row):
            raise ValueError('Meta input hash does not match the frozen pair')
        predictions.append({'id': row['id'], 'kind': row.get('kind', 'unspecified'), 'label': row['label'],
                            'input_sha256': fingerprint(row), 'text_score': result['risk_score'],
                            'meta_score': meta.get('score') if meta else None,
                            'model': result['model'], 'model_sha256': result['model_sha256']})
    labels = [r['label'] for r in predictions]
    measured_meta = [r for r in predictions if (meta_results or {}).get(r['id']) is not None]
    not_run = {'status': 'not_run', 'reason': 'No input-hash-bound Meta results supplied.'}
    meta_report = binary_metrics([r['label'] for r in measured_meta], [r['meta_score'] for r in measured_meta], .8) if measured_meta else not_run
    hybrid = binary_metrics([r['label'] for r in measured_meta],
                            [float(r['text_score'] >= threshold and r['meta_score'] >= .8) if r['text_score'] is not None and r['meta_score'] is not None else None for r in measured_meta], .5) if measured_meta else not_run
    return {'audit': quality, 'evaluated_split': split, 'threshold_tuned_on_test': False,
            'text_ml': binary_metrics(labels, [r['text_score'] for r in predictions], threshold),
            'meta_visual': meta_report, 'hybrid_both_required': hybrid,
            'meta_result_coverage': len(measured_meta)/len(test), 'provider_requests': 0,
            'by_kind': {kind: binary_metrics([r['label'] for r in predictions if r['kind'] == kind],
                [r['text_score'] for r in predictions if r['kind'] == kind], threshold) for kind in sorted({r['kind'] for r in predictions})},
            'predictions': predictions,
            'limitations': ['Labels must describe the declared task; scores do not establish ownership.',
                            'Hybrid is a predeclared triage experiment, not an automatic moderation decision.',
                            'Dataset construction and source provenance require separate review.']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', required=True, type=Path)
    parser.add_argument('--meta-results', type=Path)
    parser.add_argument('--out', required=True, type=Path)
    parser.add_argument('--split', choices=['validation', 'test'], default='test')
    args = parser.parse_args()
    if args.out.exists():
        parser.error('Use a new output path to preserve previous results')
    data = json.loads(args.manifest.read_text(encoding='utf-8'))
    for key in ('source_url', 'license_notice', 'provenance', 'task'):
        if not data.get(key):
            parser.error(f'Dataset metadata missing: {key}')
    report = evaluate(data['rows'], json.loads(args.meta_results.read_text(encoding='utf-8')) if args.meta_results else None, split=args.split)
    report['dataset'] = {k: v for k, v in data.items() if k != 'rows'}
    report['source_manifest_sha256'] = hashlib.sha256(args.manifest.read_bytes()).hexdigest()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k not in {'predictions', 'by_kind'}}, indent=2))


if __name__ == '__main__':
    main()
