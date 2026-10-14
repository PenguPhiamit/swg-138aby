"""Gather the three reports and the staged files' hashes into checks.json. Our own code (Fable, 14 Oct 2026).

    python -I make_checks.py
"""
import hashlib
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..'))
STAGED = os.path.join(ROOT, 'staged', 'client')


def sha(path):
    with open(path, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()


def main():
    checks = {'staged_files': {}, 'reports': {}}
    for base, _, files in os.walk(STAGED):
        for fn in files:
            p = os.path.join(base, fn)
            rel = os.path.relpath(p, STAGED).replace(os.sep, '/')
            checks['staged_files'][rel] = {'bytes': os.path.getsize(p), 'sha256': sha(p)}
    for name in ('ossus-report.json', 'tables-report.json', 'env-report.json', 'ossus-sites.json'):
        with open(os.path.join(ROOT, 'out', name), encoding='utf-8') as f:
            checks['reports'][name] = json.load(f)
    t = checks['reports']['ossus-report.json']
    checks['summary'] = {
        'terrain_verdict': t['verdict'], 'terrain_bytes': t['bytes'], 'round_trip': t['round_trip_identical'],
        'core3_notes_unexpected': t['core3_order_notes_unexpected'], 'structure_pairs_not_in_stock': t['structure_pairs_not_in_stock'],
        'references_missing': t['references_missing'], 'height_survey': t['height_survey'],
        'tables': {k: all(v is True for kk, v in r.items() if kk.endswith(('round_trip', 'unchanged', 'kept', 'agrees', 'ascending', 'names')))
                   for k, r in checks['reports']['tables-report.json']['files'].items()},
        'env_families_match_terrain': checks['reports']['env-report.json']['files']['datatables/environment/ossus.iff']['families_match_terrain'],
        'env_referenced_files_exist': checks['reports']['env-report.json']['files']['datatables/environment/ossus.iff']['referenced_files_exist'],
        'staged_file_count': len(checks['staged_files']),
    }
    with open(os.path.join(ROOT, 'checks.json'), 'w', encoding='utf-8') as f:
        json.dump(checks, f, indent=1)
    print(json.dumps(checks['summary'], indent=1))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
