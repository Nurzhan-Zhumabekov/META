"""Readiness check; --live explicitly sends the two local demo screenshots to Meta."""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from dotenv import set_key
from PIL import Image
from src import config
from src.errors import ComparisonUnavailable
from src.meta_compare import MetaComparer


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--live', action='store_true')
    parser.add_argument('--activate', action='store_true', help='Enable COMPARER=meta only after a successful live response; API restart is required.')
    parser.add_argument('--original', type=Path, default=ROOT / 'outputs/feature-demo/original-profile.png')
    parser.add_argument('--suspect', type=Path, default=ROOT / 'outputs/feature-demo/suspect-profile.png')
    args = parser.parse_args()
    if not config.META_API_KEY:
        print(json.dumps({'ready': False, 'code': 'meta_not_configured', 'detail': 'Add META_API_KEY to the project .env. No request was made.'}))
        return 2
    if not args.live:
        print(json.dumps({'key_configured': True, 'model': config.META_MODEL, 'live_verified': False, 'next': 'Run with --live to test the demo screenshots.'}))
        return 0
    if not args.original.is_file() or not args.suspect.is_file():
        print('Provide --original and --suspect paths to two test screenshots.')
        return 2
    try:
        with Image.open(args.original) as original, Image.open(args.suspect) as suspect:
            result = MetaComparer().analyze(original, suspect, owner_handle='aigerim.k', suspect_handle='aigerim.k_official')
    except ComparisonUnavailable as error:
        print(json.dumps({'ready': False, 'code': error.code, 'detail': str(error)}))
        return 1
    output = ROOT / 'outputs/meta-live-check.json'
    output.write_text(json.dumps(result.analysis, ensure_ascii=False, indent=2), encoding='utf-8')
    if args.activate:
        set_key(str(ROOT / '.env'), 'COMPARER', 'meta')
    print(json.dumps({'live_verified': True, 'model': config.META_MODEL, 'analysis_saved_to': str(output), 'activation_saved': args.activate, 'restart_api': args.activate}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
