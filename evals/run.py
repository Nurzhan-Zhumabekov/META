"""Live Meta + independent ML on the 15 fixed synthetic cases; never the real DB."""
import argparse
import hashlib
import json
import math
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src import config, pipeline
from src.errors import ComparisonUnavailable
from src.meta_compare import PROMPT_VERSION, SYSTEM_PROMPT
from src.profile_ml import load_model, score_profile
from evals.fixtures import images, profile_for


def load_cases():
    return json.loads(Path(__file__).with_name('cases.json').read_text(encoding='utf-8'))


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def grade(case, row):
    analysis = row.get('analysis') or {}
    ml = row.get('profile_ml') or {}
    risk = ml.get('risk_score')
    return {
        'meta_recommendation': analysis.get('provider') == 'meta' and analysis.get('recommendation') in case['expected'],
        'ml_contract': type(risk) in {float, int} and math.isfinite(risk) and 0 <= risk <= 1 and ml.get('human_review_required') is True and ml.get('facts_source') == 'user_provided',
        'human_review': row.get('status') == 'under_review',
    }


def evaluate_case(case, run_dir):
    started = time.monotonic()
    case_dir = Path(run_dir) / 'cases' / case['id']
    case_dir.mkdir(parents=True, exist_ok=True)
    original, suspect = images(case)
    original.save(case_dir / 'original.png')
    suspect.save(case_dir / 'suspect.png')
    facts = profile_for(case)
    row = {
        'id': case['id'], 'description': case['description'], 'kind': case['kind'],
        'expected': case['expected'], 'facts': facts.model_dump(),
        'input_sha256': {name: digest(case_dir / f'{name}.png') for name in ['original', 'suspect']},
    }
    try:
        row['profile_ml'] = score_profile(facts)
    except ComparisonUnavailable as error:
        row['ml_error'] = error.code
    try:
        # Actual application pipeline, with DB redirected by main into this run.
        # Human decisions are NEVER called by the runner.
        claim = pipeline.submit_claim(case['owner'], case['suspect'], original, suspect,
                                      facts if 'profile_ml' in row else None)
        row.update(status=claim.status, score=claim.score, analysis=claim.analysis, claim_id=claim.id)
    except ComparisonUnavailable as error:
        row['error'] = error.code
    except Exception as error:
        row['error'] = f'internal_{type(error).__name__}'
    row['checks'] = grade(case, row)
    row['passed'] = all(row['checks'].values())
    row['latency_seconds'] = round(time.monotonic() - started, 3)
    (case_dir / 'result.json').write_text(json.dumps(row, ensure_ascii=False, indent=2), encoding='utf-8')
    return row


def summarize(rows, metadata, complete):
    usages = [r.get('analysis', {}).get('usage', {}) for r in rows if not r.get('analysis', {}).get('cached')]
    tokens = {name: sum(u.get(name, 0) for u in usages) for name in ['prompt_tokens', 'completion_tokens', 'total_tokens']}
    latencies = sorted(r['latency_seconds'] for r in rows)
    return {
        **metadata, 'complete': complete, 'passed': sum(r['passed'] for r in rows), 'total': len(rows),
        'meta_passed': sum(r['checks']['meta_recommendation'] for r in rows),
        'ml_contract_passed': sum(r['checks']['ml_contract'] for r in rows),
        'human_review_passed': sum(r['checks']['human_review'] for r in rows),
        'tokens': tokens, 'latency_mean_seconds': round(sum(latencies) / len(latencies), 3) if latencies else None,
        'estimated_successful_response_cost_usd': round((tokens['prompt_tokens'] * 1.25 + tokens['completion_tokens'] * 4.25) / 1_000_000, 6),
        'cost_basis': 'Uncached Standard input $1.25/M and output $4.25/M; upper estimate for successful responses, excludes unknown failed-attempt usage.',
        'pricing_source': 'https://dev.meta.ai/docs/pricing-rate-limits',
        'scope': 'Synthetic development cases, not independent Instagram accuracy. ML contract checks are not impersonation accuracy.',
        'results': rows,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--live', action='store_true')
    parser.add_argument('--limit', type=int, default=15)
    parser.add_argument('--run-dir', type=Path)
    parser.add_argument('--case', action='append', dest='case_ids')
    args = parser.parse_args(argv)
    cases = load_cases()
    if args.case_ids:
        unknown = set(args.case_ids) - {c['id'] for c in cases}
        if unknown:
            parser.error('Unknown case IDs: ' + ', '.join(sorted(unknown)))
        cases = [c for c in cases if c['id'] in args.case_ids]
    cases = cases[:max(1, min(args.limit, 15))]
    if not args.live:
        print(json.dumps({'mode': 'list_only', 'cases': len(cases), 'ids': [c['id'] for c in cases], 'network_calls': 0}))
        return 0
    if not config.META_API_KEY:
        print(json.dumps({'live_verified': False, 'blocked': 'META_API_KEY is missing', 'network_calls': 0}))
        return 2
    if config.COMPARER != 'meta':
        parser.error('COMPARER must be meta for a live evaluation; no silent local fallback.')
    model = load_model()
    run_dir = (args.run_dir or ROOT / 'outputs/evals' / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')).resolve()
    real_db = pipeline.DB
    if run_dir == real_db.parent.resolve() or (run_dir / 'claims.json').resolve() == real_db.resolve():
        parser.error('Choose an isolated run directory, not the real complaints directory.')
    run_dir.mkdir(parents=True, exist_ok=True)
    result_file = run_dir / 'results.json'
    if result_file.exists():
        parser.error('Run directory already contains results. Use a new directory to preserve the previous run.')
    before = real_db.read_bytes() if real_db.exists() else None
    metadata = {
        'created_at': datetime.now(timezone.utc).isoformat(), 'model': config.META_MODEL,
        'prompt_version': PROMPT_VERSION, 'prompt_sha256': hashlib.sha256(SYSTEM_PROMPT.encode()).hexdigest(),
        'cases_sha256': digest(Path(__file__).with_name('cases.json')),
        'fixture_source_sha256': digest(Path(__file__).with_name('fixtures.py')),
        'runner_source_sha256': digest(__file__), 'ml_model': model['model_id'], 'ml_model_sha256': model['sha256'],
        'requested_cases': len(cases),
    }
    rows = []
    pipeline.DB = run_dir / 'claims.json'
    try:
        for case in cases:
            row = evaluate_case(case, run_dir)
            rows.append(row)
            summary = summarize(rows, metadata, False)
            result_file.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
            a, ml = row.get('analysis', {}), row.get('profile_ml', {})
            print(json.dumps({'id': row['id'], 'passed': row['passed'], 'recommendation': a.get('recommendation'),
                              'ml_risk': ml.get('risk_score'), 'error': row.get('error'),
                              'seconds': row['latency_seconds']}), flush=True)
    finally:
        pipeline.DB = real_db
        after = real_db.read_bytes() if real_db.exists() else None
        if before != after:
            raise RuntimeError('Real complaints database changed during evaluation; inspect concurrent writers.')
    summary = summarize(rows, metadata, True)
    summary['real_db_unchanged'] = True
    result_file.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({k: v for k, v in summary.items() if k not in {'results', 'scope', 'cost_basis'}}), flush=True)
    return 0 if summary['passed'] == len(cases) else 1


if __name__ == '__main__':
    raise SystemExit(main())
