"""Dependency-free binary metrics shared by isolated evaluation environments."""
import math


def wilson(success, total):
    if not total:
        return None
    z = 1.959963984540054
    p = success / total
    denominator = 1 + z*z/total
    centre = (p + z*z/(2*total)) / denominator
    half = z * math.sqrt(p*(1-p)/total + z*z/(4*total*total)) / denominator
    return [max(0., centre-half), min(1., centre+half)]


def binary_metrics(labels, scores, threshold):
    if len(labels) != len(scores) or not labels:
        raise ValueError('Expected non-empty aligned labels and scores')
    if any(s is not None and (type(s) not in {int, float} or not math.isfinite(s) or not 0 <= s <= 1) for s in scores):
        raise ValueError('Invalid score')
    predictions = [s is not None and s >= threshold for s in scores]
    tp = sum(y == 1 and p for y, p in zip(labels, predictions))
    fp = sum(y == 0 and p for y, p in zip(labels, predictions))
    tn = sum(y == 0 and not p for y, p in zip(labels, predictions))
    fn = sum(y == 1 and not p for y, p in zip(labels, predictions))
    return {'status': 'measured', 'n': len(labels), 'threshold': threshold,
            'positives': sum(labels), 'confusion_tn_fp_fn_tp': [tn, fp, fn, tp],
            'precision': tp/(tp+fp) if tp+fp else None, 'recall': tp/(tp+fn) if tp+fn else None,
            'f1': 2*tp/(2*tp+fp+fn) if 2*tp+fp+fn else None,
            'false_positive_rate': fp/(fp+tn) if fp+tn else None,
            'coverage': sum(s is not None for s in scores)/len(scores),
            'abstentions': sum(s is None for s in scores),
            'precision_interval_95': wilson(tp, tp+fp), 'recall_interval_95': wilson(tp, tp+fn),
            'false_positive_interval_95': wilson(fp, fp+tn),
            'abstention_policy': 'Unscored pairs count as not flagged; positive abstentions count as false negatives.'}
