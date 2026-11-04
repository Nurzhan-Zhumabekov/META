"""Compare ML versions on frozen inputs; replay Meta results without API calls."""
import argparse
from copy import deepcopy
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from evals.fixtures import profile_for
from evals.run import load_cases
from src import config, pipeline
from src.models import ComparisonResult
from src.profile_ml import score_profile


def compare(baseline, candidate_dir, out):
    from PIL import Image
    previous = json.loads(baseline.read_text(encoding='utf-8'))
    output_dir = out.parent
    if out.exists() or (output_dir / 'claims.json').exists():
        raise ValueError('Use a fresh comparison directory.')
    output_dir.mkdir(parents=True, exist_ok=True)
    old_db, old_comparer = pipeline.DB, pipeline.get_comparer
    before = old_db.read_bytes() if old_db.exists() else None
    old_ml, old_pair = config.ML_MODEL_PATH, config.PAIR_ML_MODEL_PATH
    config.ML_MODEL_PATH = candidate_dir / 'profile_risk_model.json'
    config.PAIR_ML_MODEL_PATH = candidate_dir / 'pair_risk_model.json'
    pipeline.DB = output_dir / 'claims.json'
    records = {r['id']: r for r in previous['results']}
    rows = []
    try:
        for case in load_cases():
            recorded = records[case['id']]
            class RecordedComparer:
                def analyze(self, *args, **kwargs):
                    analysis = deepcopy(recorded['analysis'])
                    analysis.pop('profile_ml', None)
                    analysis.pop('pair_ml', None)
                    analysis['evaluation_meta_replayed'] = True
                    return ComparisonResult(analysis['similarity_score'], [analysis['summary']], analysis)
            pipeline.get_comparer = RecordedComparer
            original_facts, suspect_facts = profile_for(case, original=True), profile_for(case)
            case_dir = baseline.parent / 'cases' / case['id']
            for kind, expected in recorded['input_sha256'].items():
                if hashlib.sha256((case_dir / f'{kind}.png').read_bytes()).hexdigest() != expected:
                    raise ValueError('Frozen evidence changed')
            with Image.open(case_dir / 'original.png') as original, Image.open(case_dir / 'suspect.png') as suspect:
                claim = pipeline.submit_claim(case['owner'], case['suspect'], original, suspect, suspect_facts, original_facts)
            v2, pair = claim.analysis['profile_ml'], claim.analysis['pair_ml']
            toggled = score_profile(suspect_facts.model_copy(update={'has_profile_picture': not suspect_facts.has_profile_picture}))
            assert v2['risk_score'] == toggled['risk_score']
            assert claim.status == 'under_review'
            rows.append({'id': case['id'], 'description': case['description'],
                'v1_profile_risk': recorded['profile_ml']['risk_score'], 'v2_profile_ml': v2, 'pair_ml': pair,
                'explicit_original': original_facts.model_dump(include={'handle', 'display_name', 'bio'}),
                'explicit_suspect': suspect_facts.model_dump(), 'avatar_invariant': True,
                'meta_recorded_recommendation': recorded['analysis']['recommendation'],
                'meta_image_evidence_insufficient': case['kind'] in {'blank', 'blank_original', 'blank_suspect', 'blur'},
                'status': claim.status, 'claim_id': claim.id})
    finally:
        pipeline.DB, pipeline.get_comparer = old_db, old_comparer
        config.ML_MODEL_PATH, config.PAIR_ML_MODEL_PATH = old_ml, old_pair
        if before != (old_db.read_bytes() if old_db.exists() else None):
            raise RuntimeError('Real complaints database changed during comparison.')
    result = {'cases': len(rows), 'meta_network_calls': 0, 'meta_source': str(baseline),
              'meta_results_replayed': True, 'real_db_unchanged': True,
              'avatar_invariant_cases': sum(r['avatar_invariant'] for r in rows),
              'scope': 'Existing synthetic development suite, not a new independent accuracy estimate.',
              'blank_image_note': 'Pair ML uses explicit text, even when the images are blank; this does not override insufficient image evidence.',
              'results': rows}
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline', type=Path, default=ROOT / 'outputs/evals/baseline-20261103/results.json')
    parser.add_argument('--models', type=Path, default=ROOT / 'outputs/ml/v2')
    parser.add_argument('--output', type=Path, default=ROOT / 'outputs/evals/ml-v2-20261103/results.json')
    args = parser.parse_args()
    result = compare(args.baseline, args.models, args.output)
    print(json.dumps({k: v for k, v in result.items() if k != 'results'}, indent=2))


if __name__ == '__main__':
    main()
