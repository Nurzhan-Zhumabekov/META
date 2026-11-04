from evals.report import render_report


def test_report_is_standalone_and_escapes_untrusted_model_text(tmp_path):
    run = {'total': 1, 'passed': 1, 'meta_passed': 1, 'ml_contract_passed': 1,
           'human_review_passed': 1, 'results': [
               {'id': 'sample', 'description': '<script>alert(1)</script>', 'passed': True,
                'checks': {}, 'expected': ['needs_review'], 'status': 'under_review',
                'analysis': {'recommendation': 'needs_review', 'summary': '</details><script>bad()</script>'},
                'profile_ml': {'risk_score': 0.25}, 'latency_seconds': 1.2}]}
    html = render_report([('Baseline', run, tmp_path)])
    assert '<script>alert(1)</script>' not in html
    assert '&lt;script&gt;alert(1)&lt;/script&gt;' in html
    assert '25.0%' in html and 'needs_review' in html
    assert 'under_review' in html
    assert '<link rel="stylesheet"' not in html
    assert '<script src=' not in html


def test_report_does_not_describe_ml_contract_pass_as_accuracy(tmp_path):
    run = {'total': 15, 'passed': 15, 'meta_passed': 15, 'ml_contract_passed': 15,
           'human_review_passed': 15, 'results': []}
    html = render_report([('Baseline', run, tmp_path)])
    assert '15 / 15' in html
    assert 'не точность' in html
    assert 'ML' in html
