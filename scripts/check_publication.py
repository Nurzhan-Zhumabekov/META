"""Check the Git index and bundled ZIPs for unintended runtime data and known secrets.

This scoped check supplements review; it is not a comprehensive secret detector.
Only paths and finding types are printed, never matched credential values.
"""

import io
import json
import re
import subprocess
import zipfile
from pathlib import Path

from dotenv import dotenv_values

ROOT = Path(__file__).resolve().parents[1]
PATTERNS = {
    'private_key': rb'-----BEGIN (?:RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----',
    'github_token': rb'(?:ghp_[A-Za-z0-9]{36}|github_pat_[A-Za-z0-9_]{60,})',
    'aws_key': rb'AKIA[A-Z0-9]{16}',
    'slack_token': rb'xox[baprs]-[A-Za-z0-9-]{24,}',
}
BLOCKED_PARTS = {
    '.venv', '.venv-vision', '.venv-privacy', 'node_modules', 'outputs',
    '__pycache__', '.pytest_cache', '.pytest_tmp', '.gradle', '.kotlin',
    '.dart_tool', '.idea', 'ephemeral',
}


def main():
    paths = subprocess.check_output(['git', 'ls-files', '-z'], cwd=ROOT).decode().split('\0')
    paths = [p for p in paths if p]
    if not paths:
        raise SystemExit('The index is empty; stage the intended source first.')
    secrets = [str(v).encode() for k, v in dotenv_values(ROOT / '.env').items()
               if v and any(term in k.upper() for term in ('KEY', 'TOKEN', 'PASSWORD', 'SECRET'))]
    worker = ROOT / 'outputs/evidence-worker.key'
    if worker.exists():
        secrets.append(worker.read_bytes().strip())
    findings = []
    scanned_zip_members = 0
    size = 0

    def inspect(path, data):
        normalized = Path(path)
        if set(normalized.parts) & BLOCKED_PARTS:
            findings.append({'path': path, 'kind': 'runtime_path'})
        if normalized.name.startswith('.env') and normalized.name != '.env.example':
            findings.append({'path': path, 'kind': 'environment_file'})
        if normalized.suffix in {'.key', '.pem', '.p12', '.pfx', '.jks', '.keystore', '.log', '.db'}:
            findings.append({'path': path, 'kind': 'sensitive_file_type'})
        for secret in secrets:
            if secret and secret in data:
                findings.append({'path': path, 'kind': 'known_local_secret'})
        for kind, pattern in PATTERNS.items():
            if re.search(pattern, data):
                findings.append({'path': path, 'kind': kind})

    for path in paths:
        data = subprocess.check_output(['git', 'show', f':{path}'], cwd=ROOT)
        size += len(data)
        inspect(path, data)
        if path.endswith('.zip'):
            with zipfile.ZipFile(io.BytesIO(data)) as archive:
                if archive.testzip() is not None:
                    findings.append({'path': path, 'kind': 'zip_integrity'})
                for member in archive.infolist():
                    if not member.is_dir():
                        inspect(path + '!' + member.filename, archive.read(member))
                        scanned_zip_members += 1
    result = {'scope': 'Git index and ZIP members', 'tracked_files': len(paths),
              'tracked_bytes': size, 'zip_members': scanned_zip_members, 'findings': findings,
              'comprehensive_secret_audit': False}
    print(json.dumps(result, indent=2))
    if findings:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
