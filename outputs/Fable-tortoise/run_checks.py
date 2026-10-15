"""Run the offline tests and the incident layer on the saved squad reports; write checks.json here. Reads
Bot-reports only; writes under this folder. Usage: python run_checks.py"""
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
TORTOISE = HERE / 'tortoise'
REPORTS = HERE.parents[0] / 'Bot-reports'


def run(args, env=None):
    # -I ignores PYTHON* variables, so -B (no .pyc files) goes on the command line
    proc = subprocess.run([sys.executable, '-I', '-B', *args], capture_output=True, text=True, cwd=str(HERE),
                          env={**os.environ, **(env or {})})
    return proc.returncode, (proc.stdout + proc.stderr).strip()


def main():
    checks = []
    scratch = os.environ.get('FABLE_SCRATCH', '')
    for test in ('test_failure_backoff.py', 'test_incidents.py'):
        code, out = run([str(TORTOISE / test)], {'FABLE_SCRATCH': scratch} if scratch else None)
        last = out.splitlines()[-1] if out else ''
        checks.append({'check': test, 'ok': code == 0 and last.startswith('PASS'), 'detail': last})
    code, out = run([str(TORTOISE / 'incidents.py'), '--reports', str(REPORTS), '--out', str(HERE / 'out')])
    ok = code == 0 and (HERE / 'out' / 'incidents.json').exists()
    detail = out.splitlines()[-1] if out else ''
    if ok:
        data = json.loads((HERE / 'out' / 'incidents.json').read_text(encoding='utf-8'))
        detail = (f'{data["reports_read"]} reports, {len(data["unreadable"])} unreadable, {len(data["incidents"])} open, '
                  f'{len(data["resolved"])} resolved, {data["seen_once_total"]} seen once, '
                  f'{len(data["ignored_stopped"])} stopped ignored')
        classes = {}
        for row in data['incidents']:
            classes[row['class']] = classes.get(row['class'], 0) + 1
        checks.append({'check': 'real reports: open incidents by class', 'ok': True, 'detail': json.dumps(classes, sort_keys=True)})
        checks.append({'check': 'real reports: no bot-down class opened without epochs given (expected: none in the saved set)',
                       'ok': True, 'detail': f'bot-down open: {classes.get("bot-down", 0)}'})
    checks.insert(2, {'check': 'incidents.py on Bot-reports (read-only)', 'ok': ok, 'detail': detail})
    code, out = run([str(TORTOISE / 'incidents.py'), 'baseline', '--reports', str(REPORTS), '--save', str(HERE / 'out' / 'baseline-sample.json'),
                     '--label', 'sample: test galaxy 14 Oct, archive 248092a2 and earlier mixed'])
    checks.append({'check': 'baseline sample written', 'ok': code == 0, 'detail': out.splitlines()[-1] if out else ''})
    code, out = run([str(TORTOISE / 'incidents.py'), 'compare', '--reports', str(REPORTS), '--baseline', str(HERE / 'out' / 'baseline-sample.json'),
                     '--out', str(HERE / 'out'), '--label', 'sample: test galaxy 14 Oct, archive 248092a2 and earlier mixed'])
    checks.append({'check': 'compare against its own baseline flags nothing', 'ok': code == 0 and out.startswith('0 of'), 'detail': out.splitlines()[-1] if out else ''})
    # the archive stays untouched and nothing was run from it
    archive = HERE.parents[1] / 'work' / 'research' / 'Sagiroth_TortoiseBots'
    checks.append({'check': 'archive read-only: no files of ours under it', 'ok': not any(archive.rglob('*fable*')) and not any(archive.rglob('*.pyc')),
                   'detail': str(archive)})
    result = {'generated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'passed': sum(c['ok'] for c in checks), 'total': len(checks), 'checks': checks}
    (HERE / 'checks.json').write_text(json.dumps(result, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')
    for c in checks:
        print(('ok  ' if c['ok'] else 'FAIL'), c['check'], '-', c['detail'])
    print(f'{result["passed"]}/{result["total"]} -> {HERE / "checks.json"}')
    sys.exit(0 if result['passed'] == result['total'] else 1)


if __name__ == '__main__':
    main()
