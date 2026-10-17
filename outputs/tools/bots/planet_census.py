"""Per-planet data for content design, from a BotPop run's event log (botpop-launch.jsonl or a .jsonl.<HHMM>.old).

ossus_census.py generalised to every planet that had explorers or hunters. Per planet: creatures by template with
level range and the 1 km squares they were met in; lairs by template; static objects with no name; coverage.
Writes Bot-reports/planet-data/<planet>.md and <planet>.csv, and README.md (an index). Read-only; stdlib only.

    python3 planet_census.py RUN.jsonl [--name run13] [--out Bot-reports/planet-data]

Sources: explorers' "seen" rows (kind, name, level, x, y), hunters' kill / death / incap / aggro / giveup rows (the
creature's name and level, at the bot's position), "lair" and "lair_check" rows (mission lairs), and every bot's
"snap" rows for coverage. Positions from combat rows are the bot's, within a few tens of metres of the creature.
"""
import argparse
import collections
import csv
import json
import os
import time

HERE = os.path.dirname(os.path.abspath(__file__))
OUTPUTS = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(OUTPUTS, 'Bot-reports', 'planet-data')
KM = 1000
HALF_KM = 8  # planets run from -8,192 to 8,192 m: 16 x 16 squares of 1 km (the edge squares are a few metres wider)
STOCK = ['corellia', 'dantooine', 'dathomir', 'endor', 'lok', 'naboo', 'rori', 'talus', 'tatooine', 'yavin4']
UNNAMED = {'', 'unknown_object', '?', None}

# event -> (name field, level field, kind, source label)
CREATURE_ROWS = {'kill': ('target', 'tlvl', 'killed'), 'death': ('killer', 'klvl', 'killed a bot'),
                 'incap': ('by', 'blvl', 'incapacitated a bot'), 'aggro': ('by', 'blvl', 'attacked first'),
                 'giveup': ('target', 'tlvl', 'given up on')}


def square(x, y):
    clamp = lambda v: max(-HALF_KM, min(HALF_KM - 1, int(v // KM)))
    return clamp(x), clamp(y)


def sq_text(s):
    return f'{s[0]},{s[1]}'


class Thing:
    __slots__ = ('kind', 'name', 'lvls', 'squares', 'sources', 'spots')

    def __init__(self, kind, name):
        self.kind, self.name = kind, name
        self.lvls, self.squares, self.sources, self.spots = [], collections.Counter(), collections.Counter(), set()

    def add(self, source, x, y, lvl=None, z=None):
        if lvl:
            self.lvls.append(lvl)
        self.squares[square(x, y)] += 1
        self.sources[source] += 1
        if len(self.spots) < 200:
            self.spots.add((int(round(x / 10) * 10), int(round(y / 10) * 10), int(z) if z is not None else None))

    def lvl_text(self):
        if not self.lvls:
            return '?'
        lo, hi = min(self.lvls), max(self.lvls)
        return str(lo) if lo == hi else f'{lo}-{hi}'


class Planet:
    def __init__(self, name):
        self.name = name
        self.things = {}
        self.explorers, self.hunters, self.bots = set(), set(), set()
        self.covered = collections.Counter()      # 1 km square -> snapshots
        self.explored = set()                     # squares an explorer stood in
        self.first = self.last = None
        self.seen_dedup = set()

    def thing(self, kind, name):
        key = (kind, name)
        if key not in self.things:
            self.things[key] = Thing(kind, name)
        return self.things[key]


def read(path):
    planets = {}
    with open(path, 'rb') as f:
        for line in f:
            try:
                r = json.loads(line)
            except ValueError:
                continue
            p = r.get('planet')
            e = r.get('e')
            if not p or 'x' not in r or 'y' not in r:
                continue
            pl = planets.get(p) or planets.setdefault(p, Planet(p))
            t = r.get('t')
            if t:
                pl.first = t if pl.first is None else min(pl.first, t)
                pl.last = t if pl.last is None else max(pl.last, t)
            x, y = r['x'], r['y']
            if e == 'snap':
                pl.bots.add(r.get('bot'))
                pl.covered[square(x, y)] += 1
                if r.get('role') == 'explorer':
                    pl.explorers.add(r.get('bot'))
                    pl.explored.add(square(x, y))
            elif e == 'seen':
                kind, name = r.get('kind', '?'), r.get('name')
                if kind in ('static', 'building') and name in UNNAMED:
                    kind, name = 'unnamed', 'unknown_object'
                # each name once per 256 m square, as ossus_census counts sightings
                key = (kind, name, int(x // 256), int(y // 256))
                if key in pl.seen_dedup:
                    continue
                pl.seen_dedup.add(key)
                pl.thing(kind, name).add('seen by explorers', x, y, r.get('lvl'), r.get('z'))
            elif e in CREATURE_ROWS:
                field, lfield, label = CREATURE_ROWS[e]
                name = r.get(field)
                if not name:
                    continue
                if e == 'kill':
                    pl.hunters.add(r.get('bot'))
                pl.thing('creature', name).add(label, x, y, r.get(lfield))
            elif e == 'lair' and r.get('lair'):
                pl.thing('lair', r['lair']).add('mission lair found', x, y)
            elif e == 'lair_check' and r.get('lair'):
                pl.thing('lair', r['lair']).add('mission lair fought', x, y)
    return planets


def where(thing, top=5):
    return '; '.join(f'{sq_text(s)} ({c})' for s, c in thing.squares.most_common(top))


def write_planet(pl, out_dir, run, source):
    total = (2 * HALF_KM) ** 2
    seen = set(pl.covered) | {s for th in pl.things.values() for s in th.squares}
    kinds = collections.Counter(k for k, _ in pl.things)
    md = [f'# {pl.name.capitalize()}: planet data ({run})\n',
          f"From `{source}`, {fmt_day(pl.first)} {clock(pl.first)} to {clock(pl.last)}. Written by `tools/bots/planet_census.py`; "
          f"every row with its squares is in `{pl.name}.csv`.\n",
          f'- Bots here: {len(pl.bots):,} ({len(pl.explorers):,} explorers, {len(pl.hunters):,} that killed something).',
          f'- Coverage: {len(seen)} of {total} squares of 1 km had a bot or a sighting in them ({100 * len(seen) / total:.0f}%); '
          f'explorers stood in {len(pl.explored)}.',
          f"- Templates: {kinds['creature']} creatures, {kinds['lair']} lairs, {kinds['building']} buildings, {kinds['static']} named statics, "
          f"{str(sum(pl.things[('unnamed', 'unknown_object')].sources.values())) + ' sightings of unnamed statics' if ('unnamed', 'unknown_object') in pl.things else 'no unnamed statics'}.",
          ]
    if not pl.explorers:
        md.append(f'- **No explorers here**, so buildings, statics and creatures nobody fought are missing. '
                  f'To send some: `botpop explore 50 {pl.name}` in the test galaxy console (the galaxy owner runs it).')
    md.append('\nSquares are `x,y` in km from the planet centre, south-west corner: `3,-5` is x 3,000 to 3,999 m, y -5,000 to -4,001 m. '
              'Counts in brackets are events in that square (sightings, kills, deaths and so on).\n')

    def section(title, kind, cols, cells, limit=None):
        items = sorted((th for (k, _), th in pl.things.items() if k == kind), key=lambda th: -sum(th.sources.values()))
        if not items:
            return
        md.append(f'## {title}\n')
        md.append('| ' + ' | '.join(cols) + ' |')
        md.append('|' + '---|' * len(cols))
        for th in items[:limit]:
            md.append('| ' + ' | '.join(str(c) for c in cells(th)) + ' |')
        if limit and len(items) > limit:
            md.append(f'\n{len(items) - limit} more in the CSV.')
        md.append('')

    src = lambda th, s: th.sources.get(s, 0) or ''
    section('Creatures', 'creature', ['template', 'level', 'killed', 'killed a bot', 'attacked first', 'seen (256 m squares)', '1 km squares', 'most met in'],
            lambda th: [th.name, th.lvl_text(), src(th, 'killed'), src(th, 'killed a bot'), src(th, 'attacked first'),
                        src(th, 'seen by explorers'), len(th.squares), where(th)])
    section('Lairs', 'lair', ['template', 'level', 'mission finds', 'fought (checks)', 'seen (256 m squares)', '1 km squares', 'most met in'],
            lambda th: [th.name, th.lvl_text(), src(th, 'mission lair found'), src(th, 'mission lair fought'), src(th, 'seen by explorers'),
                        len(th.squares), where(th)])
    section('Buildings', 'building', ['template', 'seen (256 m squares)', 'where'], lambda th: [th.name, sum(th.sources.values()), where(th, 4)])
    section('Static objects', 'static', ['template', 'seen (256 m squares)', 'where'], lambda th: [th.name, sum(th.sources.values()), where(th, 4)], 60)
    if ('unnamed', 'unknown_object') in pl.things:
        th = pl.thing('unnamed', 'unknown_object')
        md.append('## Static objects with no name\n')
        md.append(f"{sum(th.sources.values())} sightings in {len(th.squares)} squares of 1 km: objects the server holds with no name "
                  "(no template string the explorers could read). Worth a look for missing content or leftover markers. Spots (x/y/z, to 10 m), first 40:\n")
        md.append(', '.join(f'{x}/{y}/{z if z is not None else "?"}' for x, y, z in sorted(th.spots)[:40]) + '.\n')

    with open(os.path.join(out_dir, pl.name + '.md'), 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(md) + '\n')
    with open(os.path.join(out_dir, pl.name + '.csv'), 'w', encoding='utf-8', newline='') as f:
        w = csv.writer(f, lineterminator='\n')
        w.writerow(['planet', 'kind', 'template', 'level_min', 'level_max', 'square_x_km', 'square_y_km', 'events', 'sources'])
        for (kind, name), th in sorted(pl.things.items()):
            lo, hi = (min(th.lvls), max(th.lvls)) if th.lvls else ('', '')
            for s, c in sorted(th.squares.items()):
                w.writerow([pl.name, kind, name, lo, hi, s[0], s[1], c, ';'.join(f'{k}={v}' for k, v in sorted(th.sources.items()))])
    return len(seen), kinds


def clock(ms):
    return time.strftime('%I:%M %p', time.localtime(ms / 1000)).lstrip('0') if ms else '?'


def fmt_day(ms):
    return time.strftime('%d %b', time.localtime(ms / 1000)) if ms else '?'


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('events')
    ap.add_argument('--name', default='latest run')
    ap.add_argument('--out', default=OUT)
    a = ap.parse_args(argv)
    planets = read(a.events)
    keep = {p: pl for p, pl in planets.items() if pl.explorers or pl.hunters}
    os.makedirs(a.out, exist_ok=True)
    source = os.path.basename(a.events)
    index = [f'# Planet data ({a.name})\n',
             f'Per-planet creatures, lairs, statics and coverage from `{source}`, for designing new content. '
             f'Written by `tools/bots/planet_census.py`; one page and one CSV per planet that had explorers or hunters.\n',
             '| planet | bots | explorers | hunters | 1 km squares covered | creatures | lairs | buildings | statics | unnamed statics |',
             '|---|---|---|---|---|---|---|---|---|---|']
    for p in sorted(keep):
        pl = keep[p]
        covered, kinds = write_planet(pl, a.out, a.name, source)
        unnamed = sum(pl.things[('unnamed', 'unknown_object')].sources.values()) if ('unnamed', 'unknown_object') in pl.things else 0
        index.append(f'| [{p}]({p}.md) | {len(pl.bots):,} | {len(pl.explorers):,} | {len(pl.hunters):,} | {covered} of {(2 * HALF_KM) ** 2} | '
                     f"{kinds['creature']} | {kinds['lair']} | {kinds['building']} | {kinds['static']} | {unnamed} |")
        print(f"{p}: {len(pl.bots)} bots, {len(pl.explorers)} explorers, {covered} squares, {len(pl.things)} templates")
    missing_explorers = sorted(p for p in keep if not keep[p].explorers)
    absent = sorted(set(STOCK) - set(keep))
    index.append('')
    if missing_explorers:
        index.append(f"No explorers on {', '.join(missing_explorers)}: those pages list only what hunters fought, with no buildings or statics.")
    if absent:
        index.append(f"No data at all for {', '.join(absent)}.")
    index.append('\nTo get explorers onto a planet, the galaxy owner types `botpop explore N <planet>` in the test galaxy console '
                 '(for example `botpop explore 50 dantooine`). Hunters go where the launch cities are.')
    with open(os.path.join(a.out, 'README.md'), 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(index) + '\n')


if __name__ == '__main__':
    main()
