"""Mynock den, option 2: an outdoor den in the mynock fields (no client change). Our own code and layout (Fable,
14 Oct 2026); the 23 spawns are the same creature templates, counts and respawn times as option 1 (Bellum Gero's
cave den, AGPL-3.0, credited there), placed on the open snow around a ring of stock ice stalagmites and columns.
Ground heights come from the Core3 height port validated on Hoth (../../Fable-hoth-batchA/tools/hoth_survey.py).

    python -I stage_den_outdoor.py     # writes ../staged/.../screenplays/poi/hoth_mynock_den_outdoor.lua, ../new-files.txt,
                                       #   ../patches.tsv, ../checks.json
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..'))
OUTPUTS = os.path.normpath(os.path.join(ROOT, '..', '..'))
sys.path.insert(0, os.path.join(OUTPUTS, 'Fable-hoth-batchA', 'tools'))
sys.path.insert(0, os.path.join(OUTPUTS, 'Fable-planet-test', 'tools'))
import hoth_survey  # noqa: E402

STAGED = os.path.join(ROOT, 'staged', 'MMOCoreORB', 'bin', 'scripts')
SITE = (-2000.0, -4800.0)      # the batch B den site in hoth_mynock_fields_south (ground 44.8 m, 100 m steps under 14 m)
PROP = 'object/static/structure/general/'
STALAGMITES = ['cave_stalagmite_ice_style_%02d.iff' % n for n in (1, 2, 3, 4, 5, 6, 7, 8, 9)]
COLUMNS = ['cave_column_ice_style_%02d.iff' % n for n in (1, 2, 3)]

# the same creatures, counts and respawns as option 1: 15 ice mynocks, 7 greater ice mynocks, 1 broodmother
MOBILES = (['hoth_ice_mynock'] * 15, ['hoth_greater_ice_mynock'] * 7, ['hoth_mynock_broodmother'])
RESPAWN = {'hoth_ice_mynock': 420, 'hoth_greater_ice_mynock': 420, 'hoth_mynock_broodmother': 1800}


def ring(n, radius, phase=0.0):
    return [(radius * math.sin(math.radians(phase + 360.0 * k / n)), radius * math.cos(math.radians(phase + 360.0 * k / n))) for k in range(n)]


def main():
    ev = hoth_survey.evaluator()
    cx, cy = SITE
    g = lambda x, y: round(ev.height(x, y), 1)  # noqa: E731
    props, mobs = [], []
    # the den: three ice columns at the centre, stalagmites in two rings (18 m and 34 m)
    for i, (dx, dy) in enumerate(ring(3, 7.0, 30.0)):
        props.append((PROP + COLUMNS[i], round(cx + dx, 1), round(cy + dy, 1), (i * 120) % 360))
    for i, (dx, dy) in enumerate(ring(9, 18.0, 10.0)):
        props.append((PROP + STALAGMITES[i], round(cx + dx, 1), round(cy + dy, 1), (i * 40) % 360))
    for i, (dx, dy) in enumerate(ring(6, 34.0, 25.0)):
        props.append((PROP + STALAGMITES[(i * 2) % 9], round(cx + dx, 1), round(cy + dy, 1), (i * 60) % 360))
    # the broodmother among the columns, greater mynocks at 12 m, ice mynocks in two rings at 26 m and 44 m
    mobs.append(('hoth_mynock_broodmother', cx, cy + 2.0, 180))
    for i, (dx, dy) in enumerate(ring(7, 12.0, 0.0)):
        mobs.append(('hoth_greater_ice_mynock', round(cx + dx, 1), round(cy + dy, 1), int((math.degrees(math.atan2(dx, dy)) + 180) % 360) - 180))
    for i, (dx, dy) in enumerate(ring(8, 26.0, 22.5)):
        mobs.append(('hoth_ice_mynock', round(cx + dx, 1), round(cy + dy, 1), int((math.degrees(math.atan2(dx, dy)) + 180) % 360) - 180))
    for i, (dx, dy) in enumerate(ring(7, 44.0, 0.0)):
        mobs.append(('hoth_ice_mynock', round(cx + dx, 1), round(cy + dy, 1), int((math.degrees(math.atan2(dx, dy)) + 180) % 360) - 180))
    assert sorted(m[0] for m in mobs) == sorted(sum(MOBILES, []))
    lines = [
        '-- Mynock den, option 2: an outdoor den in the mynock fields (hoth_mynock_fields_south), no client change.',
        '-- The same creatures, counts and respawn times as option 1 (Bellum Gero\'s cave den, AGPL-3.0; outputs/Fable-hoth-batchB),',
        '-- laid out by us on the open snow around stock ice stalagmites and columns. Heights from the Core3 height port.',
        '-- Fable batch B (den-outdoor), 14 Oct 2026. Do not load together with poi/hoth_mynock_den.lua (option 1).',
        '', 'HothMynockDenOutdoorScreenPlay = ScreenPlay:new {', '\tnumberOfActs = 1,', '', '\tscreenplayName = "HothMynockDenOutdoorScreenPlay"', '}',
        '', 'registerScreenPlay("HothMynockDenOutdoorScreenPlay", true)', '',
        'function HothMynockDenOutdoorScreenPlay:start()', '\tif (isZoneEnabled("hoth")) then', '\t\tself:spawnSceneObjects()', '\t\tself:spawnMobiles()', '\tend', 'end', '',
        'function HothMynockDenOutdoorScreenPlay:spawnSceneObjects()', '\t-- 7-argument spawnSceneObject: heading in radians']
    placed = []
    for t, x, y, h in props:
        z = g(x, y)
        lines.append('\tspawnSceneObject("hoth", "%s", %s, %s, %s, 0, math.rad(%d))' % (t, x, z, y, h))
        placed.append({'kind': 'prop', 'template': t, 'x': x, 'z': z, 'y': y, 'heading_deg': h})
    lines += ['end', '', 'function HothMynockDenOutdoorScreenPlay:spawnMobiles()']
    for t, x, y, h in mobs:
        z = g(x, y)
        lines.append('\tspawnMobile("hoth", "%s", %d, %s, %s, %s, %d, 0)' % (t, RESPAWN[t], x, z, y, h))
        placed.append({'kind': 'mobile', 'template': t, 'respawn': RESPAWN[t], 'x': x, 'z': z, 'y': y, 'heading_deg': h})
    lines += ['end', '']
    rel = 'screenplays/poi/hoth_mynock_den_outdoor.lua'
    path = os.path.join(STAGED, rel.replace('/', os.sep))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(lines))
    with open(os.path.join(ROOT, 'new-files.txt'), 'w', encoding='utf-8', newline='\n') as f:
        f.write('# new files under MMOCoreORB/bin/scripts\n' + rel + '\n')
    with open(os.path.join(ROOT, 'patches.tsv'), 'w', encoding='utf-8', newline='\n') as f:
        f.write('# <file>\t<mode>\t<anchor>\t<new line>\n')
        f.write('screenplays/screenplays.lua\tafter\tincludeFile("poi/hoth_camps.lua") -- Sandbox: Hoth camps (Fable batch B)\t'
                'includeFile("poi/hoth_mynock_den_outdoor.lua") -- Sandbox: Hoth mynock den, outdoor option (Fable batch B)\n')
    zs = [p['z'] for p in placed]
    checks = {'site': SITE, 'ground_at_centre': g(cx, cy), 'placed': placed, 'height_range': [min(zs), max(zs)],
              'steepest_10m_step_across_site': round(max(abs(ev.height(cx + d + 10, cy) - ev.height(cx + d, cy)) for d in range(-60, 60, 10)), 2),
              'props': len(props), 'mobiles': len(mobs), 'counts': {k: sum(1 for m in mobs if m[0] == k) for k in RESPAWN},
              'server_templates_to_check': sorted(set(t.replace('.iff', '.lua') for t, *_ in props)),
              'creature_templates': sorted(RESPAWN), 'file': rel}
    with open(os.path.join(ROOT, 'checks.json'), 'w', encoding='utf-8') as f:
        json.dump(checks, f, indent=1)
    print({k: v for k, v in checks.items() if k not in ('placed', 'server_templates_to_check')})
    return 0


if __name__ == '__main__':
    sys.exit(main())
