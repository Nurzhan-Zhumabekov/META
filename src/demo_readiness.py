"""Read-only checks for the complete demo, separate from provider connectivity."""


def readiness_checks(status: dict, *, require_meta: bool = True) -> list[dict]:
    profile = status.get('profile_ml') or {}
    pair = status.get('pair_ml') or {}
    evidence = status.get('evidence_tools') or {}
    privacy = evidence.get('privacy') or {}
    ocr = evidence.get('ocr') or {}
    photos = evidence.get('photo_comparison') or {}
    provider = status.get('provider', 'unknown')
    checks = []

    def check(name, passed, detail):
        checks.append({'name': name, 'passed': bool(passed), 'detail': detail})

    check('Analysis available', status.get('ready') is True, provider)
    if require_meta:
        check('Live Meta provider', provider == 'meta' and status.get('meta_key_configured') is True,
              'Meta configured; no paid provider request is made by this check')
        check('Mandatory contact redaction', status.get('privacy_redaction_required') is True,
              'Redaction must remain enabled before Meta requests')
    check('Human moderation', status.get('human_review_required') is True,
          'No automatic impersonation decisions')
    check('Profile ML', profile.get('ready') is True and profile.get('enabled') is True,
          'Independent spam-pattern signal')
    check('Pair ML', pair.get('ready') is True, 'Independent text-reuse signal')
    check('Evidence workers', evidence.get('ready') is True, 'Local screenshot processing')
    check('PaddleOCR', ocr.get('provider') == 'paddleocr', 'Profile field extraction')
    check('imagededup', photos.get('provider') == 'imagededup', 'Conservative photo-region comparison')
    check('Presidio privacy inspection', privacy.get('ready') is True and privacy.get('provider') == 'presidio',
          'Local privacy inspection')
    return checks
