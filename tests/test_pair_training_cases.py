from evals.pair_data import dataset


def test_training_includes_reused_biography_with_a_changed_display_name():
    rows = dataset('train', 1)
    changed = [r for r in rows if r['kind'] == 'changed_name']
    assert changed
    assert changed[0]['label'] == 1
    assert changed[0]['original']['display_name'] != changed[0]['suspect']['display_name']
    assert changed[0]['original']['bio'] == changed[0]['suspect']['bio']
