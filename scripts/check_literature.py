"""Check the portable literature catalog and PDF bytes; requires only Python 3."""
from pathlib import Path
import hashlib
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]


def check(root=ROOT):
    records = json.loads((root / 'literature/catalog.json').read_text(encoding='utf-8'))
    bibliography = (root / 'paper/manuscript/references.bib').read_text(encoding='utf-8')
    bibkeys = set(re.findall(r'@\w+\s*\{\s*([^,\s]+)', bibliography))
    seen_keys, seen_paths, seen_hashes = set(), set(), set()
    errors, missing = [], []
    for record in records:
        key = record['citekey']
        if key in seen_keys or key not in bibkeys:
            errors.append('Duplicate or unknown citation key: ' + key)
        seen_keys.add(key)
        pdf = record['pdf']
        if not pdf:
            if record['file_status'] != 'missing':
                errors.append('Inconsistent missing status: ' + key)
            missing.append(key)
            continue
        if record['file_status'] != 'present':
            errors.append('Inconsistent present status: ' + key)
        path = (root / pdf['path']).resolve()
        if not path.is_relative_to((root / 'literature/pdfs').resolve()):
            errors.append('PDF is outside literature/pdfs: ' + key)
            continue
        if path in seen_paths:
            errors.append('Duplicate PDF path: ' + key)
        seen_paths.add(path)
        if not path.is_file():
            errors.append('Missing file: ' + pdf['path'])
            continue
        content = path.read_bytes()
        digest = hashlib.sha256(content).hexdigest()
        if not content.startswith(b'%PDF-'):
            errors.append('Not a real PDF (possibly an LFS pointer): ' + key)
        if len(content) != pdf['bytes'] or digest != pdf['sha256']:
            errors.append('PDF size/hash mismatch: ' + key)
        if digest in seen_hashes:
            errors.append('Duplicate PDF content: ' + key)
        seen_hashes.add(digest)
    actual = {p.resolve() for p in (root / 'literature/pdfs').glob('*.pdf')}
    for path in actual - seen_paths:
        errors.append('PDF not indexed: ' + path.name)
    if seen_keys != bibkeys:
        errors.append('Catalog and canonical bibliography have different citation keys')
    # The migration log is archival. Verify its PDF entries against the current
    # catalog; manuscripts may legitimately be edited after this reorganization.
    migrations = json.loads((root / 'docs/migration-2026-09-23.json').read_text(encoding='utf-8'))
    original_pdfs = {m['to']:m['sha256'] for m in migrations if m['to'].endswith('.pdf')}
    for record in records:
        pdf = record['pdf']
        if pdf and pdf['path'] in original_pdfs and original_pdfs[pdf['path']] != pdf['sha256']:
            errors.append('PDF differs from migration baseline: ' + record['citekey'])
    return {'records':len(records), 'pdfs':len(actual), 'missing_pdf_keys':missing, 'errors':errors}


if __name__ == '__main__':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    result = check()
    print(json.dumps(result,ensure_ascii=False,indent=2))
    sys.exit(bool(result['errors']))
