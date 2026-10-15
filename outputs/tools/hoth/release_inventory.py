"""Read-only C24 dev/sandbox and archive-tool history; writes local gate evidence."""
import json
from datetime import datetime
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'outputs/Documentation-support'
REVIEWS = {
    '98ad1d1d': 'C24b: R2-F1 resolved in source; multi-zone fixed-point fixtures pass; repeated-start runtime untested',
    '3a0b154f': 'C24b: scaling/rounding/caps/default/top-up reviewed; offline fixtures pass; resource gameplay untested',
    'eccb53e1': 'C24: R2-F1 P2; corrected in 98ad1d1d, re-reviewed C24b',
    'c046e633': 'C24: C22-F1 source race addressed; cancellation stress test pending',
    '54a33063': 'C24: C22-F2 source finding resolved; real-client appearance pending',
    '1c4c24fb': 'C24 source review; gameplay pending',
    '23014f39': 'C19 addendum + C22, source finding resolved',
    '90f60a81': 'C22: enclosing fight incomplete',
    'c5f1ae06': 'C22: source/geometry checks, client checks pending',
    '69eb77fe': 'C22: rancor appearance finding; follow-up fix separately gated',
    'de1b679a': 'C22: heading finding; follow-up fix separately gated',
    '34d4772a': 'C19: original counter race; fixed separately',
    'b7f03b0e': 'C19: offline loot checks, no drop acceptance',
    '2f205cd2': 'C19: data/inheritance reviewed; resource gameplay pending',
    'bea94e7a': 'C19: floor counterexample resolved in source',
    '578861d9': 'C19: feasibility trainer, client acceptance pending',
    '0c44d431': 'C18 reduced sample only', '5c7ae017': 'C18 reduced sample only',
    '5b2a858f': 'C4e: Hoth travel evidence, review findings retained',
    '421adb15': 'C4e: review findings retained', '9ac7cdcd': 'C4e: reviewed',
    '5aadc8b9': 'C4d: remaining findings; later fixes separate',
    '09a56205': 'C4b/C4c: changes requested', '220e0f39': 'C4b/C4c: changes requested',
    'f25c90f9': 'C4b/C4c: changes requested', 'f0b192e9': 'C19/C22: self-input failure resolved',
    '2009167b': 'C24: map integration reviewed; owner confirmed 18 markers',
    'c2573e31': 'C24: format switch reviewed; isolated format checks pass',
}


def main():
    prefix = ['wsl', '-d', 'Debian', '-u', 'swgemu', '--', 'git', '-C', '/opt/swg/Core3-dev']
    dev_head = subprocess.check_output(prefix + ['rev-parse', 'dev'], text=True).strip()
    sandbox = subprocess.check_output(prefix + ['rev-parse', 'sandbox'], text=True).strip()
    dev = subprocess.check_output(prefix + ['log', '--format=oneline', f'{sandbox}..{dev_head}'], encoding='utf-8')
    h_head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    h = subprocess.check_output(['git', 'log', '--format=oneline', h_head, '--', 'outputs/tools/hoth/hoth_client_build.py',
        'outputs/tools/hoth/client_load_order.py', 'outputs/tools/swgfmt', 'outputs/Fable-builder/tools',
        'outputs/Fable-hoth-mapnames/tools/hoth_names.py'], cwd=ROOT, encoding='utf-8')
    rows = []
    for repo, lines in [('dev', dev), ('h archive tools', h)]:
        for line in lines.splitlines():
            sha, title = line.split(' ', 1)
            rows.append(dict(repo=repo, commit=sha, purpose=title,
                             review=REVIEWS.get(sha[:8], 'No independent per-commit approval recorded in this inventory'),
                             gameplay='C23 pending; source review is not gameplay acceptance'))
    captured = datetime.now().astimezone().isoformat(timespec='seconds')
    evidence = dict(captured_at=captured, dev_head=dev_head, sandbox_head=sandbox, h_head=h_head,
                    scope='Conservative superset: every unpromoted dev commit, including shared bot/client helpers; unrelated features need not be promoted with Hoth. Refreshing history does not renew reviews or establish runtime acceptance.', rows=rows)
    (OUT / 'hoth-release-commits.json').write_text(json.dumps(evidence, indent=2) + '\n', encoding='utf-8', newline='\r\n')
    table = '# C24 commit inventory\n\nCaptured ' + captured + '; pinned dev `' + dev_head + '`, sandbox `' + sandbox + '`, h history `' + h_head + '`.\n\n' + evidence['scope'] + '\n\n'
    table += '| Repo | Commit | Purpose | Independent review | Gameplay |\n|---|---|---|---|---|\n'
    table += ''.join(f"| {r['repo']} | `{r['commit'][:8]}` | {r['purpose'].replace('|', '/')} | {r['review']} | {r['gameplay']} |\n" for r in rows)
    (OUT / 'hoth-release-commits.md').write_text(table, encoding='utf-8', newline='\r\n')
    print(f'{len(rows)} commit rows recorded; dev={dev_head[:8]}, sandbox={sandbox[:8]}')


if __name__ == '__main__':
    main()
