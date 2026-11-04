"""Train a small pairwise text-reuse model on explicitly synthetic pairs."""
import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import numpy as np
import sklearn
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GridSearchCV, StratifiedGroupKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from evals.pair_data import dataset
from scripts.train_profile_ml import metrics
from src.pair_ml import PAIR_FEATURES, pair_features
from src.profile_ml import ProfileFacts


def vectors(rows):
    return np.array([pair_features(ProfileFacts(**r['original']), ProfileFacts(**r['suspect'])) for r in rows])


def measurements(rows, probabilities, threshold=0.7):
    y = np.array([r['label'] for r in rows])
    result = metrics(y, probabilities)
    # metrics() historically uses .5; retain it separately and report the actual
    # predeclared conservative operating threshold without tuning on holdout.
    pred = probabilities >= threshold
    negatives, positives = y == 0, y == 1
    result.update(operating_threshold=threshold,
                  operating_accuracy=float(np.mean(pred == y)),
                  false_positives=int(np.sum(pred & negatives)),
                  false_negatives=int(np.sum(~pred & positives)),
                  recall_at_operating_threshold=float(np.mean(pred[positives])),
                  false_positive_rate=float(np.mean(pred[negatives])))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, default=ROOT / 'outputs/ml')
    args = parser.parse_args()
    out = args.output_dir
    out.mkdir(parents=True, exist_ok=True)
    splits = {name: dataset(name, n) for name, n in [('train', 240), ('validation', 60), ('holdout', 60)]}
    hashes = {}
    for name, rows in splits.items():
        blob = json.dumps(rows, ensure_ascii=False, indent=2).encode('utf-8')
        (out / f'pair-{name}.json').write_bytes(blob)
        hashes[name] = hashlib.sha256(blob).hexdigest()
    train = splits['train']
    x = vectors(train)
    y = np.array([r['label'] for r in train])
    fitted = GridSearchCV(Pipeline([('scaler', StandardScaler()),
        ('classifier', LogisticRegression(max_iter=3000, solver='lbfgs'))]),
        {'classifier__C': [0.01, 0.1, 1, 10]}, scoring='roc_auc',
        cv=StratifiedGroupKFold(5, shuffle=True, random_state=143), n_jobs=1, error_score='raise')
    fitted.fit(x, y, groups=[r['group'] for r in train])
    best = fitted.best_estimator_
    scaler, classifier = best.named_steps['scaler'], best.named_steps['classifier']
    model = {'artifact_version': 1, 'model_id': 'pair-text-logreg-v2-synthetic',
             'features': list(PAIR_FEATURES), 'mean': scaler.mean_.tolist(), 'scale': scaler.scale_.tolist(),
             'coefficients': classifier.coef_[0].tolist(), 'intercept': float(classifier.intercept_[0]),
             'threshold': 0.7, 'training_data': 'synthetic', 'split_sha256': hashes}
    export_error = 0.0
    reports = {}
    train_keys = {tuple(row) for row in x}
    for name, rows in splits.items():
        inputs = vectors(rows)
        probabilities = best.predict_proba(inputs)[:, 1]
        logits = (inputs - scaler.mean_) / scaler.scale_ @ classifier.coef_[0] + classifier.intercept_[0]
        exported = 1 / (1 + np.exp(-np.clip(logits, -700, 700)))
        export_error = max(export_error, float(np.max(np.abs(probabilities - exported))))
        reports[name] = measurements(rows, probabilities)
        reports[name]['identity_groups'] = len({r['group'] for r in rows})
        reports[name]['feature_vectors_also_in_train'] = sum(tuple(row) in train_keys for row in inputs) if name != 'train' else None
        reports[name]['by_kind'] = {kind: {'n': sum(r['kind'] == kind for r in rows),
            'flagged': sum(float(p) >= 0.7 for r, p in zip(rows, probabilities) if r['kind'] == kind)} for kind in sorted({r['kind'] for r in rows})}
    if export_error > 1e-10:
        raise ValueError('Exported inference mismatch')
    assert not ({r['group'] for r in train} & {r['group'] for r in splits['holdout']})
    report = {'training_data': 'synthetic', 'sklearn': sklearn.__version__, 'selected_C': fitted.best_params_['classifier__C'],
              'train_cv_auc': float(fitted.best_score_), 'split_sha256': hashes,
              'generator_sha256': hashlib.sha256((ROOT / 'evals/pair_data.py').read_bytes()).hexdigest(),
              'threshold_selected_on_holdout': False, 'original_15_used_for_training': False,
              'identity_overlap': 0, 'max_export_abs_error': export_error, 'splits': reports,
              'limitations': ['Synthetic labels and a shared procedural generator do not establish real-world performance.',
                              'Text feature vectors can recur across distinct fictional identities; overlaps are disclosed.',
                              'Model only measures textual reuse of explicit user-supplied facts. Human review is required.']}
    (out / 'pair_risk_model.json').write_text(json.dumps(model, indent=2), encoding='utf-8')
    (out / 'pair-training-report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
