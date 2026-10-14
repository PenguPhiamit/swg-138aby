"""Gather the S4 reports, logs and file hashes into ../checks.json. Our own code (Fable, 14 Oct 2026).

    python -I make_checks.py
"""
import hashlib
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
S4 = os.path.normpath(os.path.join(HERE, '..'))


def sha(path):
    with open(path, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()


def main():
    checks = {'files': {}, 'reports': {}, 'logs': {}}
    for base in ('staged', 'cpp', 'snippets', 'patches.tsv', 'new-files.txt', 'apply.sh'):
        p = os.path.join(S4, base)
        if os.path.isfile(p):
            checks['files'][base] = {'bytes': os.path.getsize(p), 'sha256': sha(p)}
        elif os.path.isdir(p):
            for d, _, files in os.walk(p):
                for fn in files:
                    q = os.path.join(d, fn)
                    checks['files'][os.path.relpath(q, S4).replace(os.sep, '/')] = {'bytes': os.path.getsize(q), 'sha256': sha(q)}
    for name in ('stage-chiss-report.json', 'stage-gotal-nautolan-test-report.json', 'verify-staged-report.json', 'acst-diff.json'):
        p = os.path.join(S4, 'out', name)
        if os.path.exists(p):
            with open(p, encoding='utf-8') as f:
                checks['reports'][name] = json.load(f)
    for name in ('git-apply-check.txt', 'selftest.txt', 'apply-check.txt', 'hunks.txt'):
        p = os.path.join(S4, 'work', name)
        if os.path.exists(p):
            with open(p, encoding='utf-8', errors='replace') as f:
                checks['logs'][name] = f.read().splitlines()
    ga = checks['logs'].get('git-apply-check.txt', [])
    v = checks['reports'].get('verify-staged-report.json', {})
    checks['summary'] = {
        'stage_chiss': checks['reports'].get('stage-chiss-report.json', {}).get('summary'),
        'stage_gotal_nautolan_test': checks['reports'].get('stage-gotal-nautolan-test-report.json', {}).get('summary'),
        'verify_staged_verdict': v.get('_verdict'),
        'acst_species_appearances': checks['reports'].get('acst-diff.json', {}).get('species_appearances'),
        'git_apply_check_ok': any('git apply --check: OK' in l for l in ga),
        'patch_applied_equals_edited_copies': all('applied == new' in l for l in ga if 'applied' in l and 'new' in l) and sum(1 for l in ga if l.startswith('applied == new')) == 8,
        'originals_match_dev': sum(1 for l in ga if l.startswith('same as dev')) == 8 and not any(l.startswith('DEV CHANGED') for l in ga),
        'lua_selftest_passed': any('SELFTEST PASSED' in l for l in checks['logs'].get('selftest.txt', [])),
        'lua_apply_check_refused': [l for l in checks['logs'].get('apply-check.txt', []) if 'REFUSED' in l],
    }
    with open(os.path.join(S4, 'checks.json'), 'w', encoding='utf-8') as f:
        json.dump(checks, f, indent=1)
    print(json.dumps(checks['summary'], indent=1))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
