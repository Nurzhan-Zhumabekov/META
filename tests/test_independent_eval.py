import pytest

from evals.independent import audit, binary_metrics, evaluate


def pair(identifier, group, label=1, split='test'):
    return {'id': identifier, 'group': group, 'split': split, 'label': label, 'kind': 'copy' if label else 'ordinary',
            'original': {'handle': group, 'display_name': 'A maker', 'bio': 'Handmade ceramic commissions in Astana.'},
            'suspect': {'handle': group + '_copy', 'display_name': 'A maker', 'bio': 'Handmade ceramic commissions in Astana.'}}


def test_audit_rejects_shared_accounts_even_under_different_group_names():
    train = pair('train', 'maker', split='train')
    test = pair('test', 'different')
    test['suspect'] = train['original']
    with pytest.raises(ValueError, match='account overlap'):
        audit([train, test])


def test_audit_rejects_duplicate_pairs_and_conflicting_labels():
    first = pair('one', 'maker')
    duplicate = {**first, 'id': 'two', 'label': 0}
    with pytest.raises(ValueError, match='duplicate'):
        audit([first, duplicate])


def test_metrics_count_abstentions_and_report_false_positive_rate():
    result = binary_metrics([1, 1, 0, 0], [.9, None, .8, .1], .7)
    assert result['confusion_tn_fp_fn_tp'] == [1, 1, 1, 1]
    assert result['coverage'] == .75
    assert result['recall'] == .5 and result['false_positive_rate'] == .5
    assert result['precision_interval_95'] is not None


def test_missing_meta_is_not_presented_as_measured_hybrid_accuracy(monkeypatch):
    monkeypatch.setattr('evals.independent.score_pair', lambda a,b: {'risk_score': .8, 'threshold': .7, 'model':'test-model','model_sha256':'test-hash'})
    report = evaluate([pair('one', 'maker'), pair('two', 'runner', 0)])
    assert report['text_ml']['n'] == 2
    assert report['meta_visual']['status'] == 'not_run'
    assert report['hybrid_both_required']['status'] == 'not_run'
    assert report['provider_requests'] == 0


def test_replayed_meta_must_match_exact_frozen_pair(monkeypatch):
    monkeypatch.setattr('evals.independent.score_pair', lambda a,b: {'risk_score': .8, 'threshold': .7, 'model':'test-model','model_sha256':'test-hash'})
    with pytest.raises(ValueError, match='input hash'):
        evaluate([pair('one', 'maker')], {'one': {'input_sha256':'wrong','score': .9}})
