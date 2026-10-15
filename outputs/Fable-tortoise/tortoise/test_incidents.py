"""Offline tests for incidents.py on synthetic reports written to a temporary folder (never Bot-reports).
Run: python test_incidents.py   (prints PASS <n> checks or the first FAIL and exits 1). Ours, AGPL-3.0."""
import contextlib
import io
import json
import os
import sys
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import incidents as inc

checks = 0


def check(cond, what):
    global checks
    checks += 1
    if not cond:
        print(f'FAIL {checks}: {what}')
        sys.exit(1)


T0 = datetime(2026, 10, 14, 10, 0, 0)


def write(root, group, minutes, scenario, state='finished', checks=(), notes=(), error=None, seconds=60):
    """One report in the squad's shape: <stamp>-<scenario stem>.json under <root>/<group>/."""
    started = T0 + timedelta(minutes=minutes)
    rows = [{'label': label, 'ok': ok, 'detail': detail, 't': 1.0 + i} for i, (label, ok, detail) in enumerate(checks)]
    data = {'group': group, 'scenario': scenario, 'started': started.strftime(inc.STAMP), 'state': state,
            'seconds': seconds, 'passed': sum(r['ok'] for r in rows), 'total': len(rows), 'error': error,
            'checks': rows, 'notes': list(notes), 'steps': [], 'events': {}}
    folder = Path(root) / group
    folder.mkdir(parents=True, exist_ok=True)
    name = f'{started:%Y%m%d-%H%M%S}-{Path(scenario).stem}.json'
    (folder / name).write_text(json.dumps(data, indent=1), encoding='utf-8')
    return f'{group}/{name}'


def main():
    tmp = tempfile.mkdtemp(prefix='fable-tortoise-', dir=os.environ.get('FABLE_SCRATCH') or None)
    root = Path(tmp) / 'Bot-reports'
    ok, bad = ('camp placed', True, ''), ('camp placed', False, '@camp:error_lair_too_close')

    # 1. One failed run is not an incident yet: it is listed under seen_once.
    write(root, 'Aurek', 0, 'aurek-camp.py', 'failed', [bad])
    runs, unreadable = inc.load_runs(root, groups=('Aurek',))
    res = inc.build(runs)
    check(res['incidents'] == [] and res['seen_once_total'] == 1 and res['seen_once'][0]['key'] == 'camp placed', '1 seen once')
    check(res['seen_once'][0]['class'] == 'defect-candidate', '1 class')

    # 2. The same failure in two consecutive runs opens a watch incident; a third makes it persistent.
    write(root, 'Aurek', 25, 'aurek-camp.py', 'failed', [bad])
    runs, _ = inc.load_runs(root, groups=('Aurek',))
    res = inc.build(runs)
    check(len(res['incidents']) == 1 and res['incidents'][0]['severity'] == 'watch' and res['incidents'][0]['runs_seen'] == 2, '2 watch')
    write(root, 'Aurek', 50, 'aurek-camp.py', 'failed', [bad])
    runs, _ = inc.load_runs(root, groups=('Aurek',))
    res = inc.build(runs)
    row = res['incidents'][0]
    check(row['severity'] == 'persistent' and row['runs_seen'] == 3 and row['state'] == 'open', '3 persistent')
    check(row['first_seen'] == '2026-10-14 10:00:00' and row['last_seen'] == '2026-10-14 10:50:00' and row['age_s'] == 3000, '3 times')
    check(len(row['evidence']) == 3 and row['evidence'][-1]['report'].startswith('Aurek/20261014-105000'), '3 evidence')

    # 4. A run that errored cannot vouch for a check it never reached; a run where the check passed resolves it.
    write(root, 'Aurek', 75, 'aurek-camp.py', 'error', [], error='TypeError: bad thing (scenario line 9: x)')
    runs, _ = inc.load_runs(root, groups=('Aurek',))
    res = inc.build(runs)
    check(len(res['incidents']) == 1 and res['incidents'][0]['kind'] == 'FAIL' and res['incidents'][0]['state'] == 'open', '4 error run keeps FAIL open')
    check(res['incidents'][0]['runs_seen'] == 3 and res['incidents'][0]['runs_between'] == 1, '4 runs_between counts the non-vouching run')
    check(res['seen_once_total'] == 1 and res['seen_once'][0]['kind'] == 'ERROR' and res['seen_once'][0]['class'] == 'harness'
          and res['seen_once'][0]['state'] == 'open', '4 the error itself is open, seen once, class harness')
    by = write(root, 'Aurek', 100, 'aurek-camp.py', 'finished', [ok])
    runs, _ = inc.load_runs(root, groups=('Aurek',))
    res = inc.build(runs)
    check(res['incidents'] == [] and len(res['resolved']) == 1, '4 resolved')
    check(res['resolved'][0]['resolved_by'] == by and res['resolved'][0]['resolved_at'] == '2026-10-14 11:40:00', '4 resolved by')
    check(res['seen_once_total'] == 1 and res['seen_once'][0]['kind'] == 'ERROR' and res['seen_once'][0]['state'] == 'resolved', '4 error seen once, resolved by the clean run')

    # 5. BLOCKED notes: class blocked, digits normalised, bot-down wording recognised; stopped runs ignored.
    write(root, 'Besh', 0, 'besh-harvest.py', 'blocked', [], ['BLOCKED: prey level unknown or above 12; need a spawn'])
    write(root, 'Besh', 25, 'besh-harvest.py', 'blocked', [], ['BLOCKED: prey level unknown or above 15; need a spawn',
                                                              'BLOCKED: Pell not logged in'])
    write(root, 'Besh', 30, 'besh-harvest.py', 'stopped', [], [], error='RunStopped: owner requested halt')
    runs, _ = inc.load_runs(root, groups=('Besh',))
    res = inc.build(runs)
    check(len(res['incidents']) == 1 and res['incidents'][0]['class'] == 'blocked', '5 blocked incident')
    check(res['incidents'][0]['key'] == 'prey level unknown or above #; need a spawn', f'5 key {res["incidents"][0]["key"]}')
    check(res['seen_once'][0]['class'] == 'bot-down', '5 bot-down note')
    check(len(res['ignored_stopped']) == 1 and res['incidents'][0]['runs_seen'] == 2, '5 stopped run ignored')

    # 6. A note repeated inside one run counts once.
    write(root, 'Cresh', 0, 'cresh-x.py', 'blocked', [], ['BLOCKED: twice', 'BLOCKED: twice'])
    runs, _ = inc.load_runs(root, groups=('Cresh',))
    res = inc.build(runs)
    check(res['incidents'] == [] and res['seen_once_total'] == 1, '6 repeated note counts once')

    # 7. Another scenario's run never closes an episode; the same scenario's clean run does.
    write(root, 'Cresh', 25, 'cresh-y.py', 'finished', [('other', True, '')])
    write(root, 'Cresh', 50, 'cresh-x.py', 'blocked', [], ['BLOCKED: twice'])
    runs, _ = inc.load_runs(root, groups=('Cresh',))
    res = inc.build(runs)
    check(len(res['incidents']) == 1 and res['incidents'][0]['runs_seen'] == 2 and res['incidents'][0]['runs_between'] == 0, '7 other scenario neutral')
    write(root, 'Cresh', 75, 'cresh-x.py', 'finished', [('fine', True, '')])
    runs, _ = inc.load_runs(root, groups=('Cresh',))
    res = inc.build(runs)
    check(res['incidents'] == [] and res['resolved'][0]['key'] == 'twice', '7 clean run resolves')

    # 8. Epochs: a restart closes open episodes; the follow-up episode links back; bot-down inside the blackout is suppressed.
    write(root, 'Dorn', 0, 'dorn-social.py', 'failed', [('leash', False, '12 m')])
    write(root, 'Dorn', 25, 'dorn-social.py', 'failed', [('leash', False, '13 m')])
    restart = T0 + timedelta(minutes=40)
    write(root, 'Dorn', 42, 'dorn-social.py', 'failed', [('leash', False, '14 m')], ['BLOCKED: Nima not logged in'])
    write(root, 'Dorn', 70, 'dorn-social.py', 'failed', [('leash', False, '15 m')], ['BLOCKED: Nima not logged in'])
    runs, _ = inc.load_runs(root, groups=('Dorn',))
    res = inc.build(runs, epochs=[restart])
    check(len(res['resolved']) == 1 and res['resolved'][0]['resolved_by'] == 'server restart (epoch 1)', '8 restart closes')
    check(res['resolved'][0]['resolved_at'] == '2026-10-14 10:40:00', '8 closed at the epoch time')
    check(len(res['incidents']) == 1 and res['incidents'][0]['continues'] == res['resolved'][0]['id'], '8 continues link')
    check(res['incidents'][0]['epoch'] == 1 and res['incidents'][0]['runs_seen'] == 2, '8 new episode in epoch 1')
    check(res['suppressed_total'] == 1 and res['suppressed'][0]['report'].startswith('Dorn/20261014-104200'), '8 blackout suppressed')
    check(res['seen_once_total'] == 1 and res['seen_once'][0]['class'] == 'bot-down', '8 after the blackout it opens')
    res2 = inc.build(runs)  # without epochs: one leash episode of four runs, and the bot-down note is an incident too
    runs_seen = {r['class']: r['runs_seen'] for r in res2['incidents']}
    check(runs_seen == {'defect-candidate': 4, 'bot-down': 2} and res2['suppressed_total'] == 0, f'8 no epochs {runs_seen}')

    # 8b. Seen gone after the restart, then back: a new episode without a `continues` link.
    write(root, 'Grek', 0, 'grek.py', 'failed', [('gate', False, 'a')])
    write(root, 'Grek', 25, 'grek.py', 'failed', [('gate', False, 'b')])
    write(root, 'Grek', 50, 'grek.py', 'finished', [('gate', True, '')])
    write(root, 'Grek', 75, 'grek.py', 'failed', [('gate', False, 'c')])
    write(root, 'Grek', 100, 'grek.py', 'failed', [('gate', False, 'd')])
    runs, _ = inc.load_runs(root, groups=('Grek',))
    res = inc.build(runs, epochs=[restart])
    check(len(res['incidents']) == 1 and res['incidents'][0]['continues'] is None and res['incidents'][0]['id'].endswith('-2'), '8b no link after a clean run')
    check(res['resolved'][0]['resolved_by'] == 'server restart (epoch 1)' and res['resolved'][0]['runs_seen'] == 2, '8b first closed by restart')
    write(root, 'Grek', 0, 'grek2.py', 'failed', [('gate', False, 'a')])
    write(root, 'Grek', 25, 'grek2.py', 'failed', [('gate', False, 'b')])
    write(root, 'Grek', 50, 'grek2.py', 'error', [], error='KeyError: x')  # cannot vouch: the link survives
    write(root, 'Grek', 75, 'grek2.py', 'failed', [('gate', False, 'c')])
    write(root, 'Grek', 100, 'grek2.py', 'failed', [('gate', False, 'd')])
    runs, _ = inc.load_runs(root, groups=('Grek',))
    res = inc.build(runs, epochs=[restart])
    linked = [r for r in res['incidents'] if r['scenario'] == 'grek2.py' and r['kind'] == 'FAIL'][0]
    check(linked['continues'] is not None and linked['continues'].endswith('-1'), '8b error run keeps the link')

    # 9. Evidence is bounded to the newest N.
    runs, _ = inc.load_runs(root, groups=('Dorn',))
    res3 = inc.build(runs, evidence=2)
    leash = [r for r in res3['incidents'] if r['kind'] == 'FAIL'][0]
    check(len(leash['evidence']) == 2 and leash['evidence'][-1]['detail'] == '15 m' and leash['evidence'][0]['detail'] == '14 m', '9 bounded evidence')

    # 10. Malformed and non-timestamped files: counted or ignored, never fatal.
    (root / 'Esk').mkdir(exist_ok=True)
    (root / 'Esk' / '20261014-120000-broken.json').write_text('{not json', encoding='utf-8')
    (root / 'Esk' / '20261014-120100-badchecks.json').write_text(json.dumps({'group': 'Esk', 'scenario': 'x', 'checks': [{'label': 'a'}]}), encoding='utf-8')
    (root / 'Esk' / 'manifest.json').write_text('{}', encoding='utf-8')
    runs, unreadable = inc.load_runs(root, groups=('Esk',))
    check(runs == [] and len(unreadable) == 2, f'10 unreadable {unreadable}')

    # 11. Determinism: two builds of the same reports agree exactly; ids are content-derived.
    runs, _ = inc.load_runs(root)
    a, b = inc.build(runs, epochs=[restart]), inc.build(runs, epochs=[restart])
    check(json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True), '11 deterministic')
    check(all(r['id'].startswith(r['group'][:2] + '-' + r['kind'][0]) for r in a['incidents'] + a['resolved']), '11 id layout')

    # 12. Baseline and compare: a pass-rate drop and a slower median are flagged; label mismatch warns.
    base_root = Path(tmp) / 'base'
    for i in range(4):
        write(base_root, 'Esk', i * 25, 'esk-routes.py', 'finished', [('a', True, ''), ('b', True, '')], seconds=100)
    now_root = Path(tmp) / 'now'
    for i in range(4):
        write(now_root, 'Esk', i * 25, 'esk-routes.py', 'failed', [('a', True, ''), ('b', False, 'x')], seconds=170)
    write(now_root, 'Esk', 200, 'esk-new.py', 'finished', [('c', True, '')])
    write(now_root, 'Esk', 210, 'esk-routes.py', 'stopped', [], error='RunStopped: run time budget reached')
    saved = inc.baseline(inc.load_runs(base_root, groups=('Esk',))[0], 'archive 248092a2')
    check(saved['rows']['Esk|esk-routes.py']['pass_rate'] == 1.0 and saved['rows']['Esk|esk-routes.py']['median_seconds'] == 100.0, '12 baseline rows')
    current = inc.baseline(inc.load_runs(now_root, groups=('Esk',))[0], 'archive 248092a2')
    check(current['rows']['Esk|esk-routes.py']['runs'] == 4 and current['runs'] == 5, '12 stopped run excluded from the baseline')
    cmp = inc.compare(current, saved)
    flags = {r['key']: r['flags'] for r in cmp['rows']}
    check(cmp['warnings'] == [] and cmp['flagged'] == 2, f'12 flagged {cmp["flagged"]}')
    check(flags['Esk|esk-routes.py'] == ['pass rate down 1.00 -> 0.50', 'median time up 100 s -> 170 s'], f'12 flags {flags}')
    check(flags['Esk|esk-new.py'] == ['new scenario'], '12 new scenario')
    cmp2 = inc.compare(inc.baseline(inc.load_runs(now_root, groups=('Esk',))[0], 'other build'), saved)
    check(len(cmp2['warnings']) == 1 and 'different labels' in cmp2['warnings'][0], '12 label warning')

    # 13. The command line writes only under --out and reads a window.
    out = Path(tmp) / 'out'
    quiet = contextlib.redirect_stdout(io.StringIO())
    with quiet:
        inc.main(['incidents', '--reports', str(root), '--out', str(out), '--epoch', restart.strftime(inc.STAMP), '--since', '2026-10-14 10:30'])
    written = json.loads((out / 'incidents.json').read_text(encoding='utf-8'))
    check((out / 'incidents.md').exists() and written['epochs'] == ['2026-10-14 10:40:00'], '13 cli output')
    check(all(r['first_seen'] >= '2026-10-14 10:30:00' for r in written['incidents'] + written['resolved']), '13 since window')
    check(sorted(p.name for p in root.rglob('*')) == sorted(p.name for p in root.rglob('*')) and not (root / 'incidents.json').exists(), '13 reports untouched')
    with contextlib.redirect_stdout(io.StringIO()):
        inc.main(['baseline', '--reports', str(base_root), '--save', str(out / 'baseline.json'), '--label', 'archive 248092a2'])
        inc.main(['compare', '--reports', str(now_root), '--baseline', str(out / 'baseline.json'), '--out', str(out), '--label', 'archive 248092a2'])
    check((out / 'compare.md').read_text(encoding='utf-8').count('pass rate down') == 1, '13 compare written')

    print(f'PASS test_incidents ({checks} checks)')


if __name__ == '__main__':
    main()
