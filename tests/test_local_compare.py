from src.local_compare import LocalComparer


def test_identical_images_score_high(make_image):
    score, reasons = LocalComparer().compare(make_image("gradient"), make_image("gradient"))
    assert score > 0.95
    assert "Profile images are near-identical" in reasons


def test_different_images_score_lower(make_image):
    comparer = LocalComparer()
    same, _ = comparer.compare(make_image("gradient"), make_image("gradient"))
    diff, reasons = comparer.compare(make_image("gradient"), make_image("stripes"))
    assert diff < same
    assert diff < 0.5
    assert "Profile images are near-identical" not in reasons
