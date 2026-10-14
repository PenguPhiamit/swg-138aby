"""Gather hashes of the staged files and tables plus the S3 logs into ../checks.json. Our own code (Fable, 14 Oct 2026).

    python -I make_checks.py
"""
import hashlib
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..'))


def sha(path):
    with open(path, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()


def main():
    checks = {'files': {}, 'logs': {}}
    for base in ('s3/staged', 's3/snippets', 's3/tables', 's3/patches.tsv', 's3/new-files.txt', 'provenance.json'):
        p = os.path.join(ROOT, base)
        if os.path.isfile(p):
            checks['files'][base] = {'bytes': os.path.getsize(p), 'sha256': sha(p)}
        else:
            for d, _, files in os.walk(p):
                for fn in files:
                    q = os.path.join(d, fn)
                    checks['files'][os.path.relpath(q, ROOT).replace(os.sep, '/')] = {'bytes': os.path.getsize(q), 'sha256': sha(q)}
    for name in ('selftest.txt', 'apply-check.txt', 'dev-check.txt'):
        p = os.path.join(ROOT, 's3', 'work', name)
        if os.path.exists(p):
            with open(p, encoding='utf-8', errors='replace') as f:
                checks['logs'][name] = f.read().splitlines()
    with open(os.path.join(ROOT, 's3', 'tables', 'chiss-rows.json'), encoding='utf-8') as f:
        rows = json.load(f)
    checks['summary'] = {
        'selftest_passed': any('SELFTEST PASSED' in l for l in checks['logs'].get('selftest.txt', [])),
        'apply_check_refused': [l for l in checks['logs'].get('apply-check.txt', []) if 'REFUSED' in l],
        'dev_check_problems': [l for l in checks['logs'].get('dev-check.txt', []) if l.startswith(('LUAC FAILED', 'TAKEN', 'MISSING'))],
        'chiss_rows_per_table': {k.split('/')[-1]: len(v['rows']) for k, v in rows['dtii_rows'].items()},
        'chiss_iff_fragments': sum(len(v['chiss_fragments']) for v in rows['iff_fragments'].values()),
        'tables_with_schema_drift': [k.split('/')[-1] for k, v in rows['dtii_rows'].items() if v['types_package'] != v['types_stock']],
        'staged_file_count': len(checks['files']),
    }
    with open(os.path.join(ROOT, 'checks.json'), 'w', encoding='utf-8') as f:
        json.dump(checks, f, indent=1)
    print(json.dumps(checks['summary'], indent=1))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
