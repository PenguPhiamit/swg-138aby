"""Gather the O2 reports and the staged files' hashes into ../checks.json. Our own code (Fable, 14 Oct 2026).

    python -I make_checks.py
"""
import hashlib
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
O2 = os.path.normpath(os.path.join(HERE, '..'))


def sha(path):
    with open(path, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()


def main():
    checks = {'staged_files': {}, 'reports': {}}
    for root in ('staged', 'snippets', 'resources'):
        base = os.path.join(O2, root)
        for d, _, files in os.walk(base):
            for fn in files:
                p = os.path.join(d, fn)
                checks['staged_files'][os.path.relpath(p, O2).replace(os.sep, '/')] = {'bytes': os.path.getsize(p), 'sha256': sha(p)}
    for name in ('snapshot-report.json', 'server-report.json', 'resources-report.json'):
        with open(os.path.join(O2, 'out', name), encoding='utf-8') as f:
            checks['reports'][name] = json.load(f)
    for name in ('dev-check.txt', 'apply-check.txt', 'selftest.txt'):
        p = os.path.join(O2, 'work', name)
        if os.path.exists(p):
            with open(p, encoding='utf-8', errors='replace') as f:
                checks['reports'][name] = f.read().splitlines()
    s = checks['reports']['snapshot-report.json']['checks']
    r = checks['reports']['resources-report.json']
    checks['summary'] = {
        'snapshot': {'bytes': s['bytes'], 'nodes': s['nodes'], 'world_level': s['world_level'], 'round_trip': s['round_trip_identical'],
                     'hoth_ws_round_trip': s['hoth_ws_round_trip'], 'ids': s['ids'], 'ids_clash': s['ids_used_by_other_snapshots'],
                     'templates_missing_client': s['templates_missing_in_client'], 'templates_missing_crc': s['templates_missing_in_merged_crc_table']},
        'server': {'new_files': len(checks['reports']['server-report.json']['new_files']), 'patches': len(checks['reports']['server-report.json']['patches'])},
        'resources': {'rows_added': r['added'], 'stock_round_trip': r['stock_round_trip'], 'staged_round_trip': r['staged_round_trip'],
                      'type_count_rule_check': r['type_count_rule_check']},
        'dev_check_problems': [l for l in checks['reports'].get('dev-check.txt', []) if l.startswith(('MISSING', 'LUAC FAILED', 'TAKEN', 'EXISTS'))],
        'apply_check_refused': [l for l in checks['reports'].get('apply-check.txt', []) if 'REFUSED' in l],
        'selftest_passed': any('SELFTEST PASSED' in l for l in checks['reports'].get('selftest.txt', [])),
        'staged_file_count': len(checks['staged_files']),
    }
    with open(os.path.join(O2, 'checks.json'), 'w', encoding='utf-8') as f:
        json.dump(checks, f, indent=1)
    print(json.dumps(checks['summary'], indent=1))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
