"""Shared record of how long tests, builds and restarts take (owner request, 13 Oct), for planning future work.

    python tools/timings.py add <kind> <name> <seconds> [note]   kinds: scenario, build, galaxy-start, setup, review, wait
    python tools/timings.py summary                              writes Bot-reports/TIMINGS.md and prints it
    python tools/timings.py backfill                             adds past scenario runs from Bot-reports/*/LOG.md

The data is Bot-reports/timings.csv: when, kind, name, seconds, result, note. squad.py appends every scenario run by
itself; agents add builds, galaxy starts, bot setup and long waits. Works from Windows or WSL Python.
"""
import csv, re, statistics, sys
from datetime import datetime
from pathlib import Path

REPORTS = Path(__file__).resolve().parents[1] / 'Bot-reports'
DATA = REPORTS / 'timings.csv'
FIELDS = ['when', 'kind', 'name', 'seconds', 'result', 'note']


def add(kind, name, seconds, result='', note='', when=None):
    new = not DATA.exists()
    REPORTS.mkdir(parents=True, exist_ok=True)
    with DATA.open('a', newline='', encoding='utf-8') as stream:
        out = csv.writer(stream)
        if new:
            out.writerow(FIELDS)
        out.writerow([when or f'{datetime.now():%Y-%m-%d %H:%M}', kind, name, round(float(seconds)), result, note])


def rows():
    if not DATA.exists():
        return []
    with DATA.open(newline='', encoding='utf-8') as stream:
        return list(csv.DictReader(stream))


def backfill():
    seen = {(r['when'], r['name']) for r in rows()}
    line = re.compile(r'^- (\d{4}-\d\d-\d\d \d\d:\d\d) · `([^`]+)` · (\d+)/(\d+) checks passed · (\d+) s')
    added = 0
    for log in sorted(REPORTS.glob('*/LOG.md')):
        for text in log.read_text(encoding='utf-8').splitlines():
            match = line.match(text)
            if match:
                when, scenario, passed, total, seconds = match.groups()
                name = f'{scenario}:{log.parent.name}'
                if (when, name) not in seen:
                    add('scenario', name, seconds, f'{passed}/{total}', 'from LOG.md', when)
                    seen.add((when, name))
                    added += 1
    print(f'added {added} past scenario runs')


def summary():
    data = rows()
    groups = {}
    for row in data:
        groups.setdefault((row['kind'], row['name']), []).append(row)
    lines = ['# How long things take', '',
             f'From `timings.csv` ({len(data)} entries, newest {data[-1]["when"] if data else "-"}). '
             'Regenerate with `python tools/timings.py summary`.', '',
             '| Kind | What | Runs | Typical (median) | Fastest | Slowest | Last | Last result |', '|---|---|---|---|---|---|---|---|']
    fmt = lambda s: f'{s / 60:.1f} min' if s >= 120 else f'{s:.0f} s'
    for (kind, name), items in sorted(groups.items()):
        secs = [float(r['seconds']) for r in items]
        lines.append(f'| {kind} | {name} | {len(items)} | {fmt(statistics.median(secs))} | {fmt(min(secs))} | {fmt(max(secs))} '
                     f'| {items[-1]["when"]} | {items[-1]["result"]} |')
    waits = [float(r['seconds']) for r in data if r['kind'] in ('build', 'galaxy-start', 'setup', 'wait')]
    if waits:
        lines += ['', f'Time spent waiting on builds, galaxy starts, bot setup and other waits: **{fmt(sum(waits))}** over {len(waits)} entries.']
    text = '\n'.join(lines) + '\n'
    (REPORTS / 'TIMINGS.md').write_text(text, encoding='utf-8')
    sys.stdout.reconfigure(errors='replace')
    print(text)


if __name__ == '__main__':
    args = sys.argv[1:]
    if args[:1] == ['add'] and len(args) >= 4:
        add(args[1], args[2], args[3], note=' '.join(args[4:]))
    elif args[:1] == ['backfill']:
        backfill()
    elif args[:1] == ['summary']:
        summary()
    else:
        print(__doc__)
