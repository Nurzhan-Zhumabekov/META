"""Read-only demo preflight. Never submits a claim or calls a paid model."""
import argparse
import json
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.demo_readiness import readiness_checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-url', default='http://127.0.0.1:8090')
    parser.add_argument('--require-meta', action='store_true')
    args = parser.parse_args()
    base = args.base_url.rstrip('/')
    checks = []
    try:
        with urlopen(base + '/api/analysis/status', timeout=5) as response:
            status = json.load(response)
        if not isinstance(status, dict):
            raise ValueError('Expected a status object')
        checks.extend(readiness_checks(status, require_meta=args.require_meta))
    except (HTTPError, URLError, TimeoutError, ValueError):
        checks.append({'name': 'API status', 'passed': False, 'detail': 'Status unavailable or invalid'})
    for path in ['/', '/profile/aruzhan.jpg', '/messages/aruzhan.jpg']:
        try:
            with urlopen(base + path, timeout=5) as response:
                passed = response.status == 200 and 'text/html' in response.headers.get('Content-Type', '')
            detail = 'HTML route available' if passed else 'Expected an HTML application route'
        except (HTTPError, URLError, TimeoutError):
            passed, detail = False, 'Route unavailable; restart the server after updating the source'
        checks.append({'name': path, 'passed': passed, 'detail': detail})
    ready = all(check['passed'] for check in checks)
    print(json.dumps({'ready': ready, 'mode': 'real-meta' if args.require_meta else 'configured-provider',
                      'checks': checks, 'paid_model_requests': 0, 'claims_written': 0}, indent=2))
    return 0 if ready else 1


if __name__ == '__main__':
    raise SystemExit(main())
