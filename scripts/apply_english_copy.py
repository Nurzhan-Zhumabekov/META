"""One-time local English copy migration; original copy is retained in outputs."""
from pathlib import Path
import hashlib
import json
import re
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'outputs' / 'english-ui'


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    translations = {}
    for source in OUT.glob('*-copy.tsv'):
        for line in source.read_text(encoding='utf-8').splitlines():
            if '\t' in line:
                original, english = line.split('\t', 1)
                if original in translations and translations[original] != english:
                    raise ValueError('Conflicting translation: ' + original)
                translations[original] = english
    baseline = OUT / 'baseline-hashes.json'
    if not baseline.exists():
        protected = [ROOT / 'outputs' / 'claims.json']
        protected += [p for p in (ROOT / 'outputs' / 'evidence').rglob('*') if p.is_file()]
        baseline.write_text(json.dumps({p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in protected}, indent=2), encoding='utf-8')
    targets = [p for p in (ROOT / 'web' / 'src').rglob('*') if p.suffix in {'.ts', '.tsx'}]
    targets.append(ROOT / 'web' / 'index.html')
    changed = []
    for path in targets:
        text = path.read_text(encoding='utf-8')
        updated = text
        for original, english in sorted(translations.items(), key=lambda item: -len(item[0])):
            updated = updated.replace(original, english)
        if updated != text:
            backup = OUT / 'original-source' / path.relative_to(ROOT)
            backup.parent.mkdir(parents=True, exist_ok=True)
            if not backup.exists():
                shutil.copyfile(path, backup)
            path.write_text(updated, encoding='utf-8')
            changed.append(path.relative_to(ROOT).as_posix())
    print(json.dumps({'changed': changed, 'translations': len(translations)}, ensure_ascii=False))
    for path in targets:
        for number, line in enumerate(path.read_text(encoding='utf-8').splitlines(), 1):
            if re.search(r'[\u0400-\u04ff]', line):
                print(f'{path.relative_to(ROOT)}:{number}:{line.strip()}')


if __name__ == '__main__':
    main()
