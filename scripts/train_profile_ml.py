"""Train an independent profile baseline; never executes the upstream notebook.

Run from project root with requirements-ml.txt installed. --download retrieves only
the two pinned CSVs into ignored outputs/ml/data, not third-party executable code.
"""
import argparse
import csv
import hashlib
import json
import math
import platform
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import httpx
import numpy as np
import sklearn
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, average_precision_score, brier_score_loss, confusion_matrix, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import GridSearchCV, StratifiedGroupKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer, StandardScaler

from src.profile_ml import FEATURES, LOG_FEATURES, NO_AVATAR_FEATURES

UPSTREAM = 'Ajaysagayam/Detection_of_Fake_Accounts_in_Social_Media'
COMMIT = 'f8dc984326eded77363e7466060cc7ee6d5d32b6'


def load_dataset(path):
    rows = list(csv.DictReader(Path(path).open(encoding='utf-8-sig', newline='')))
    features, labels = [], []
    for row in rows:
        vector = []
        for name in FEATURES:
            value = row[name]
            if name in {'profile_pic', 'extern_url', 'private'}:
                if value not in {'Yes', 'No'}:
                    raise ValueError(f'Invalid category in {name}')
                value = float(value == 'Yes')
            else:
                value = float(value)
            if not math.isfinite(value) or value < 0:
                raise ValueError(f'Invalid numeric value in {name}')
            if name.startswith('ratio_') and value > 1:
                raise ValueError('Ratio outside 0..1')
            vector.append(value)
        label = int(row['fake'])
        if label not in {0, 1}:
            raise ValueError('Expected binary labels')
        features.append(vector)
        labels.append(label)
    x, y = np.array(features, dtype=float), np.array(labels, dtype=int)
    if len(set(labels)) != 2:
        raise ValueError('Both classes are required')
    return x, y


def transform(x, features=FEATURES):
    result = np.asarray(x, dtype=float).copy()
    for index, name in enumerate(features):
        if name in LOG_FEATURES:
            result[:, index] = np.log1p(result[:, index])
    return result


def row_key(row):
    return tuple(float(v) for v in row)


def metrics(y, p):
    pred = p >= 0.5
    return {
        'n': len(y), 'positives': int(sum(y)), 'threshold': 0.5,
        'roc_auc': float(roc_auc_score(y, p)), 'average_precision': float(average_precision_score(y, p)),
        'accuracy': float(accuracy_score(y, pred)), 'precision': float(precision_score(y, pred, zero_division=0)),
        'recall': float(recall_score(y, pred)), 'f1': float(f1_score(y, pred)),
        'brier': float(brier_score_loss(y, p)), 'confusion_matrix_tn_fp_fn_tp': confusion_matrix(y, pred, labels=[0, 1]).tolist(),
    }


def auc_interval(y, p):
    rng = np.random.default_rng(42)
    values = []
    for _ in range(1000):
        idx = rng.integers(0, len(y), len(y))
        if len(np.unique(y[idx])) == 2:
            values.append(roc_auc_score(y[idx], p[idx]))
    return [float(v) for v in np.quantile(values, [0.025, 0.975])]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data-dir', type=Path, default=ROOT.parent / '_research/fake-accounts-upstream')
    parser.add_argument('--download', action='store_true')
    parser.add_argument('--include-avatar', action='store_true', help='Reproduce legacy v1; v2 excludes avatar.')
    parser.add_argument('--output-dir', type=Path, default=ROOT / 'outputs/ml')
    args = parser.parse_args()
    out = args.output_dir
    out.mkdir(parents=True, exist_ok=True)
    data_dir = args.data_dir
    if args.download:
        data_dir = out / 'data'
        data_dir.mkdir(exist_ok=True)
        for name in ['social_media_train.csv', 'social_media_test.csv']:
            response = httpx.get(f'https://raw.githubusercontent.com/{UPSTREAM}/{COMMIT}/{name}', timeout=30, follow_redirects=False)
            response.raise_for_status()
            (data_dir / name).write_bytes(response.content)
    full_x, y = load_dataset(data_dir / 'social_media_train.csv')
    full_xt, yt = load_dataset(data_dir / 'social_media_test.csv')
    features = FEATURES if args.include_avatar else NO_AVATAR_FEATURES
    indices = [FEATURES.index(f) for f in features]
    x, xt = full_x[:, indices], full_xt[:, indices]
    groups = [hashlib.sha256(json.dumps(row.tolist()).encode()).hexdigest() for row in x]
    cv = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=42)
    pipeline = Pipeline([
        ('transform', FunctionTransformer(transform, kw_args={'features': features})), ('scaler', StandardScaler()),
        ('classifier', LogisticRegression(solver='lbfgs', max_iter=5000, tol=1e-7)),
    ])
    search = GridSearchCV(pipeline, {'classifier__C': [0.001, 0.01, 0.1, 1, 10, 100, 1000]}, scoring='roc_auc', cv=cv, n_jobs=1, error_score='raise')
    search.fit(x, y, groups=groups)
    fitted = search.best_estimator_
    p = fitted.predict_proba(xt)[:, 1]
    # Report the original split, then a conservative unique non-overlapping holdout.
    # Exclude overlaps in BOTH the original and reduced feature spaces. Keep the
    # original 9-feature holdout membership for directly comparable metrics too.
    train_keys = {row_key(row) for row in full_x}
    reduced_train_keys = {row_key(row) for row in x}
    seen, clean_indices = set(), []
    comparable_indices, comparable_seen = [], set()
    for i, row in enumerate(full_xt):
        key = row_key(row)
        if key not in train_keys and key not in comparable_seen:
            comparable_indices.append(i)
            comparable_seen.add(key)
        reduced_key = row_key(xt[i])
        if key not in train_keys and reduced_key not in reduced_train_keys and reduced_key not in seen:
            clean_indices.append(i)
            seen.add(reduced_key)
    clean = np.asarray(clean_indices)
    if len(np.unique(yt[clean])) != 2:
        raise ValueError('Clean holdout must contain both classes')
    test_metrics = metrics(yt[clean], p[clean])
    test_metrics['roc_auc_bootstrap_95ci'] = auc_interval(yt[clean], p[clean])
    scaler = fitted.named_steps['scaler']
    classifier = fitted.named_steps['classifier']
    provenance = {
        'source': f'https://github.com/{UPSTREAM}', 'commit': COMMIT,
        'dataset_attribution': 'Bardiya Bakhshandeh, Instagram fake/spammer genuine accounts, March 2019; likely source CC BY 3.0, mirrored transformations not fully documented',
        'csv_sha256': {n: hashlib.sha256((data_dir / n).read_bytes()).hexdigest() for n in ['social_media_train.csv', 'social_media_test.csv']},
        'upstream_code_copied': False,
    }
    model = {
        'artifact_version': 1 if args.include_avatar else 2,
        'model_id': 'profile-logreg-v1' if args.include_avatar else 'profile-logreg-v2-no-avatar', 'features': list(features),
        'mean': scaler.mean_.tolist(), 'scale': scaler.scale_.tolist(),
        'coefficients': classifier.coef_[0].tolist(), 'intercept': float(classifier.intercept_[0]),
        'threshold': 0.5,
        'training_bounds': {name: [float(x[:, i].min()), float(x[:, i].max())] for i, name in enumerate(features)},
        'provenance': provenance, 'metrics': test_metrics,
    }
    combined = np.vstack([x, xt])
    logits = (transform(combined, features) - scaler.mean_) / scaler.scale_ @ classifier.coef_[0] + classifier.intercept_[0]
    exported = 1 / (1 + np.exp(-np.clip(logits, -700, 700)))
    max_error = float(np.max(np.abs(exported - fitted.predict_proba(combined)[:, 1])))
    if max_error > 1e-10:
        raise ValueError('Exported model disagrees with sklearn')
    report = {
        'provenance': provenance,
        'versions': {'python': platform.python_version(), 'sklearn': sklearn.__version__, 'numpy': np.__version__},
        'features': list(features), 'ignored_features': [f for f in FEATURES if f not in features], 'log1p_features': sorted(LOG_FEATURES),
        'train_rows': len(y), 'test_rows': len(yt), 'train_class_counts': np.bincount(y).tolist(),
        'test_class_counts': np.bincount(yt).tolist(), 'selected_C': search.best_params_['classifier__C'],
        'train_cv_auc': float(search.best_score_), 'original_test': metrics(yt, p), 'clean_test': test_metrics,
        'same_v1_holdout': metrics(yt[comparable_indices], p[comparable_indices]),
        'selected_feature_train_test_overlaps': sum(row_key(row) in reduced_train_keys for row in xt),
        'test_rows_removed_for_overlap_or_duplicates': len(yt) - len(clean),
        'max_export_abs_error': max_error, 'upstream_notebook_executed': False,
        'test_used_for_selection': False,
        'limitations': [
            'Small, manually labeled, balanced 2019 fake/spam dataset; not an impersonation dataset.',
            'Unknown account identities prevent person-level leakage checks.',
            'Model scores are not calibrated for present-day Instagram prevalence.',
            'Bio length is measured in characters; two ambiguous upstream fields were excluded.',
        ],
    }
    (out / 'profile_risk_model.json').write_text(json.dumps(model, indent=2), encoding='utf-8')
    (out / 'training-report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps({'model': model['model_id'], 'train_rows': len(y), 'clean_holdout': test_metrics, 'selected_C': report['selected_C'], 'export_error': max_error}, indent=2))


if __name__ == '__main__':
    main()
