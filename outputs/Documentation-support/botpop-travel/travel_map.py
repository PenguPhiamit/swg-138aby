"""Pass/fail map of the shuttle routes from a BotPop run (botpop-travel.patch).

Reads the run's botpop-launch.jsonl (travel_try, travel_done and travel_fail rows) and prints, per route
(departure point -> arrival point), how many trips started, arrived and failed, with each failure's step and
reason, then the failures by step. Read-only.

    python3 travel_map.py <path to bin/log/botpop-launch.jsonl> [--since <epoch ms>] [--md out.md]
"""
import argparse
import collections
import json
import sys


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('log')
    parser.add_argument('--since', type=int, default=0, help='only rows at or after this time (ms)')
    parser.add_argument('--md', help='also write the tables to this Markdown file')
    args = parser.parse_args()

    routes = collections.OrderedDict()
    steps = collections.Counter()
    open_tries = 0

    with open(args.log, encoding='utf-8', errors='replace') as log:
        for line in log:
            if '"travel_' not in line:
                continue
            try:
                row = json.loads(line)
            except ValueError:
                continue
            event = row.get('e')
            if event not in ('travel_try', 'travel_done', 'travel_fail') or row.get('t', 0) < args.since:
                continue
            key = (f"{row.get('from_planet', '?')}: {row.get('from_point') or '(none)'}",
                   f"{row.get('to_planet', '?')}: {row.get('to_point') or '(none)'}")
            r = routes.setdefault(key, {'try': 0, 'done': 0, 'fail': collections.Counter(), 'secs': []})
            if event == 'travel_try':
                r['try'] += 1
                open_tries += 1
            elif event == 'travel_done':
                r['done'] += 1
                r['secs'].append(row.get('secs', 0))
                open_tries -= 1
            else:
                why = f"{row.get('step', '?')}: {row.get('why', '?')}"
                r['fail'][why] += 1
                steps[row.get('step', '?')] += 1
                open_tries -= 1

    lines = ['| From | To | Tries | Arrived | Failed | Median trip (s) | Failures (step: reason x n) |',
             '|---|---|---:|---:|---:|---:|---|']
    for (start, end), r in sorted(routes.items(), key=lambda item: (-sum(item[1]['fail'].values()), item[0])):
        secs = sorted(r['secs'])
        median = secs[len(secs) // 2] if secs else ''
        fails = '; '.join(f'{why} x{n}' for why, n in r['fail'].most_common())
        status = 'PASS' if r['done'] and not r['fail'] else 'FAIL' if not r['done'] else 'MIXED'
        lines.append(f"| {start} | {end} | {r['try']} | {r['done']} | {sum(r['fail'].values())} | {median} | "
                     f"{status}{' - ' + fails if fails else ''} |")

    total_try = sum(r['try'] for r in routes.values())
    total_done = sum(r['done'] for r in routes.values())
    lines += ['', f'Routes {len(routes)}, tries {total_try}, arrived {total_done}, failed {sum(steps.values())}, '
              f'still under way at the end of the log {max(0, open_tries)}.', '',
              '| Step | Failures |', '|---|---:|']
    lines += [f'| {step} | {n} |' for step, n in steps.most_common()]

    text = '\n'.join(lines)
    print(text)
    if args.md:
        with open(args.md, 'w', encoding='utf-8') as out:
            out.write('# Shuttle routes from the BotPop run\n\n' + text + '\n')
    return 0


if __name__ == '__main__':
    sys.exit(main())
