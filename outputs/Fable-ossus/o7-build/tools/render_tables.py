"""Render the README tables from poi-placements.json and template-resolution.json and inject them between the markers
<!-- NAME --> ... <!-- /NAME --> in ../README.md. Our own code (Claude, 16 Oct 2026).

    python -I render_tables.py            # rewrite the README's generated blocks
"""
import collections
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from o7_common import O7, jload  # noqa: E402


def n(v):
    return '{:,}'.format(int(round(v)))


def creatures(p):
    rows = p['creatures_within_300m']
    if rows:
        return '; '.join('%s L%s x%d (%s m)' % (r['name'], r['levels'], r['sightings'], n(r['nearest_m'])) for r in rows)
    nf = p['nearest_creature']
    return 'none (nearest %s L%s, %s m)' % (nf['name'], nf['level'], n(nf['distance_m'])) if nf else 'none seen'


def poi_table():
    d = jload(os.path.join(O7, 'poi-placements.json'))
    out = ['| # | Place | Centre x / y | Ground z | Nearest census ground sample | Creatures within 300 m (census) | Lair props within 300 m | From Knossa | Flags |',
           '|---|---|---|---|---|---|---|---|---|']
    for k, p in d['pois'].items():
        s = p['census_nearest_sample']
        lp = p['lair_props_within_300m']
        flags = '; '.join(f.replace('inside a no-build circle: ', 'in no-build: ').replace('STEEP: ', '**steep** ') for f in p['flags']
                          if not f.startswith('no census creature')) or 'none'
        n3 = p['census_nearest_3_ground_samples'][0]
        out.append('| %s | %s | %s / %s | %.1f | %s m: z %d (terrain there %.1f) | %s | %s | %s m | %s |' % (
            p['poi'], p['name'], n(p['centre'][0]), n(p['centre'][1]), p['ground_z_terrain'], n(n3['distance_m']), n3['census_z'], n3['terrain_z_at_sample'], creatures(p),
            ('%d (nearest %s m)' % (lp['count'], n(lp['nearest_m']))) if lp['count'] else 'none', n(p['distance_from_knossa_m']), flags))
    return '\n'.join(out)


def notes_block():
    d = jload(os.path.join(O7, 'poi-placements.json'))
    out = []
    for k, p in d['pois'].items():
        o6 = p['o6_point']
        move = '' if not o6 or p['moved_from_o6_m'] in (None, 0) else ' Moved %s m from o6\'s (%s, %s).' % (n(p['moved_from_o6_m']), n(o6[0]), n(o6[1]))
        out.append('- **%s %s** (%d objects).%s %s' % (p['poi'], p['name'], p['objects'], move, p['notes']))
    return '\n'.join(out)


def contents_block():
    s = jload(os.path.join(O7, 'statics.json'))
    p = jload(os.path.join(O7, 'poi-placements.json'))
    by = collections.OrderedDict()
    for o in s['objects']:
        role = re.sub(r' \d+ of \d+$', '', o['role'])
        role = re.sub(r'^(crater) \d+ ', r'\1 ', role)
        by.setdefault(o['poi'], collections.Counter())[role] += 1
    out = []
    for k, c in by.items():
        out.append('- **%d %s** (%d): %s' % (k, p['pois'][str(k)]['name'], sum(c.values()), ', '.join('%s x%d' % (r, v) if v > 1 else r for r, v in c.items())))
    return '\n'.join(out)


def group_paths(paths):
    by = collections.OrderedDict()
    for t in paths:
        d, f = t.rsplit('/', 1)
        by.setdefault(d, []).append(f)
    parts = []
    for d, fs in by.items():
        names = [re.sub(r'^shared_', '', f)[:-4] for f in fs]
        parts.append('`%s/shared_{%s}.iff`' % (d, ', '.join(names)) if len(names) > 1 else '`%s/%s`' % (d, fs[0]))
    return '; '.join(parts)


def resolution_block():
    d = jload(os.path.join(O7, 'template-resolution.json'))
    out = []
    for it in d['items']:
        chosen = [c['template'] for c in it['chosen']]
        what = group_paths(chosen) if chosen else ''
        if it['shaders']:
            what = ', '.join('`%s`' % s['shader'] for s in it['shaders'])
        out.append('- **%s**\n  - Status: %s.\n  - Chosen: %s\n  - Why: %s' % (
            it['o6'], it['status'], what or '(no template; terrain affectors)', it['why']))
    return '\n'.join(out)


def inject(text, name, body):
    pat = re.compile(r'(<!-- %s -->)(.*?)(<!-- /%s -->)' % (name, name), re.S)
    if not pat.search(text):
        raise SystemExit('marker %s missing in README.md' % name)
    return pat.sub(lambda m: m.group(1) + '\n' + body + '\n' + m.group(3), text)


def main():
    path = os.path.join(O7, 'README.md')
    text = open(path, encoding='utf-8').read()
    text = inject(text, 'POI_TABLE', poi_table())
    text = inject(text, 'POI_NOTES', notes_block())
    text = inject(text, 'POI_CONTENTS', contents_block())
    text = inject(text, 'RESOLUTION', resolution_block())
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(text)
    print('README.md updated,', len(text), 'characters')


if __name__ == '__main__':
    main()
