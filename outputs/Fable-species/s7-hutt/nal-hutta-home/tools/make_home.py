"""PL-04: lay out Nal Hutta as the Hutt home and check every placement (Claude, 17 Oct 2026). Our own code and layout.

    C:/Users/Pengw/miniconda3/python.exe -I make_home.py

Writes ../home.json (every placement with its checks) and the generated Lua data file
../server/MMOCoreORB/bin/scripts/screenplays/sandbox/hutta_home_places.lua. Exits 1 if a check fails.

Bilbousa (Darklight's snapshot) is laid out along one processional avenue: the starport at the north end (yaw 180, its
front on y 1711), the bank's round plaza (-767, 1562), the bazaar of ten merchant tents (x -808 and -730, y 1429-1509)
and the palace gate (y 1413) at the south end. Four Jabba-palace towers already stand round it; each tower's entrance
is marked by one of Darklight's green lamps on its town-side face (checked below), so those are the four first kajidic
seats. Two new towers on the flat 80 m shelf (north and west, found by find_sites.py) make six.

Snapshot statics (client and server, local_planets.tre) are the buildings and props; people, terminals and the trade
yard are server-side (spawnMobile / spawnSceneObject, the Hoth batch C and Ossus PL-02 pattern), so they need no client
change. Kajidic names are the S7 README's own (section 5.5), not Legends clans.
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from hutta_common import (HOME, TOWN_CENTRE, Terrain, existing_footprints, jsave, obb, poly_overlap,  # noqa: E402
                          circle_poly_overlap, tinfo, rot)

FIRST_ID = 7170001          # new snapshot ids; checked against every snapshot the client loads (build step)
TOWER = 'object/building/tatooine/shared_tower_jabbas_palace.iff'
BANNER = 'object/static/structure/general/shared_all_banner_generic_s01.iff'
AMBER = 'object/static/structure/general/shared_streetlamp_medium_style_02_on.iff'   # Darklight's lamp, warm light
FOUNTAIN = 'object/static/structure/corellia/shared_corl_fountain_circle_s01.iff'
CAMP = 'object/building/poi/tatooine_hutt_businessmen_camp_large1.iff'

# kajidic seats: name, tower (existing snapshot id or None), centre, the face the entrance is on (compass heading
# outward from the tower), the existing lamp that marks that entrance (None for new towers)
SEATS = [
    ('Kessoth', 390000058, (-652.0, 1680.0), 180, 390000225),
    ('Vollaka', 390000059, (-984.0, 1562.0), 90, 390000221),     # inside Nym's stronghold; its gate lamps at x -937
    ('Dromuul', 390000091, (-889.0, 1812.0), 180, 390000278),
    ('Narissik', 390000092, (-540.0, 1501.0), 270, 390000270),
    ('Tashuga', None, (-750.0, 1920.0), 180, None),              # north shelf, behind the starport
    ('Bessolo', None, (-1050.0, 1690.0), 90, None),              # west shelf, facing the hotel street
]
HALF = 38.0                  # the tower's footprint half-width (client EXBX of thm_tato_jabbas_palace_tower)
GATE_X = {390000059: -937.0}  # Vollaka's entrance is the stronghold's gate, not the tower face
# Nym's stronghold's client box (x -998..-877) is loose: Darklight's own gate lamps (-937) stand inside it, so the
# Vollaka props at the gate may overlap that box; they are still checked against every prop and against each other
ALLOW_BOX = {'Vollaka': {390000035}}

# server-side people and things: kind, key, x, y, heading, note
PEOPLE = [
    # the bazaar: the two kajidic vendors stand in front of a tent each, facing the avenue
    ('npc', 'hutta_kessoth_outfitter', -798.5, 1489.0, 90, 'Kessoth outfitter, in front of the tent at -808 1489'),
    ('npc', 'hutta_vollaka_broker', -739.5, 1469.0, 270, 'Vollaka broker, in front of the tent at -730 1469'),
    # the starport end of the avenue
    ('npc', 'hutta_council_herald', -766.0, 1700.0, 0, 'the council herald, facing arrivals from the starport'),
    ('terminal', 'kajidic_contracts', -782.0, 1692.0, 90, 'mission terminal, west side of the avenue'),
    ('terminal', 'kajidic_contracts', -749.0, 1692.0, 270, 'mission terminal, east side of the avenue'),
    ('npc', 'patron_nikto', -790.0, 1700.0, 135, 'a cargo runner'),
    ('npc', 'patron_nikto', -744.0, 1702.0, 225, 'a cargo runner'),
    # the cantina door (the cantina faces south; Darklight's lamp 238 stands at its door, -641 1539)
    ('terminal', 'smuggling_runs', -662.0, 1533.0, 180, 'mission terminal, west of the cantina door'),
    ('terminal', 'smuggling_runs', -628.0, 1533.0, 180, 'mission terminal, east of the cantina door'),
    ('npc', 'trainer_smuggler', -650.0, 1531.0, 180, 'the stock smuggler trainer, at the cantina door'),
    # the bazaar crowd
    ('npc', 'patron_nikto', -770.0, 1497.0, 200, 'a bazaar idler'),
    ('npc', 'patron_nikto', -760.0, 1445.0, 20, 'a bazaar idler'),
    ('npc', 'patron_nikto', -785.0, 1462.0, 110, 'a bazaar idler'),
]

# deliver-mission NPC points (MissionManager, spawn type 2 = neutral), 3 m off Darklight's street lamps
NPC_POINTS_FROM_LAMPS = [390000216, 390000217, 390000218, 390000219, 390000229, 390000246, 390000260, 390000263]

TRADE_YARD = (-440.0, 1530.0)   # flat east shelf (find_sites.py: 1.7 m relief over r 38)


def heading_vec(h):
    r = math.radians(h)
    return math.sin(r), math.cos(r)


def lateral(h):
    """unit vector 90 degrees clockwise of the heading (to the right when facing out)"""
    return heading_vec(h + 90)


def main():
    t = Terrain()
    fps = existing_footprints()
    byid = {f[0]: f for f in fps}
    problems = []
    statics, people, guards = [], [], []
    nid = FIRST_ID

    def add_static(template, x, y, yaw, why, allow=()):
        nonlocal nid
        z = round(t.h(x, y), 2)
        statics.append({'id': nid, 'template': template, 'x': round(x, 2), 'y': round(y, 2), 'z': z, 'yaw': yaw, 'why': why,
                        'allowed_box_overlaps': sorted(allow)})
        nid += 1

    seats = []
    for name, tower, (cx, cy), face, lamp in SEATS:
        if tower is not None:
            f = byid[tower]
            assert f[1] == TOWER and abs(f[2] - cx) < 0.1 and abs(f[3] - cy) < 0.1, (name, f[:4])
        if lamp is not None:
            lf = byid[lamp]
            assert 'streetlamp' in lf[1], lamp
        else:
            add_static(TOWER, cx, cy, 0, '%s seat: new tower' % name)
        ox, oy = heading_vec(face)
        lx, ly = lateral(face)
        if tower in GATE_X:
            fx, fy = GATE_X[tower] + 3.0, cy
        else:
            fx, fy = cx + ox * (HALF + 3.0), cy + oy * (HALF + 3.0)
        seats.append({'kajidic': name, 'tower_id': tower, 'centre': [cx, cy], 'entrance_face': face, 'entrance': [round(fx, 1), round(fy, 1)],
                      'marked_by_lamp': lamp})
        for side in (-1, 1):
            guards.append({'kind': 'npc', 'key': 'gamorrean_guard', 'x': round(fx + side * 6 * lx, 2), 'y': round(fy + side * 6 * ly, 2), 'heading': face,
                           'note': 'a %s guard' % name, 'seat': name})
            allow = ALLOW_BOX.get(name, set())
            add_static(BANNER, fx + side * 10 * lx + ox, fy + side * 10 * ly + oy, face, '%s seat: banner' % name, allow)
            add_static(AMBER, fx + side * 14 * lx + ox, fy + side * 14 * ly + oy, face, '%s seat: amber lamp' % name, allow)

    # the council palace's water garden: a round fountain at the head of the bazaar, two amber lamps beside it
    add_static(FOUNTAIN, -767.0, 1515.0, 0, 'council palace approach: fountain')
    add_static(AMBER, -776.0, 1520.0, 0, 'council palace approach: amber lamp')
    add_static(AMBER, -758.0, 1520.0, 0, 'council palace approach: amber lamp')

    for kind, key, x, y, h, note in PEOPLE:
        people.append({'kind': kind, 'key': key, 'x': x, 'y': y, 'heading': h, 'note': note})
    people += guards
    points = []
    for lid in NPC_POINTS_FROM_LAMPS:
        f = byid[lid]
        ox, oy = heading_vec(f[4] + 90)
        points.append({'from_lamp': lid, 'x': round(f[2] + 3 * ox, 1), 'y': round(f[3] + 3 * oy, 1), 'heading': round((f[4] + 90) % 360)})

    # ---- checks
    solid_small = [f for f in fps if any(k in f[1] for k in ('lamp', 'banner', 'tent', 'brazier', 'fountain', 'antenna'))]
    new_polys = [(s['id'], s['template'], obb(s['template'], s['x'], s['y'], s['yaw'])) for s in statics]
    report = {'statics': [], 'people': [], 'npc_points': [], 'trade_yard': None}
    for s, (_, tpl, poly) in zip(statics, new_polys):
        info = tinfo(tpl)
        hits = [f[0] for f in fps if poly_overlap(poly, f[5]) and f[0] not in s['allowed_box_overlaps']]
        if tpl == TOWER:
            lo, hi = t.disc(s['x'], s['y'], HALF, step=HALF / 4)
        else:
            lo, hi = t.disc(s['x'], s['y'], 2.0, step=1.0)
        others = [o[0] for o in new_polys if o[0] != s['id'] and poly_overlap(poly, o[2])]
        ok = not hits and not others and lo >= 79.0 and hi - lo <= 2.5 and info['in_stock_table'] and info['client_file'] and not info['missing_appearances']
        row = dict(s, ground=[round(lo, 2), round(hi, 2)], overlaps_existing=hits, overlaps_new=others, stock_template=info['in_stock_table'], ok=ok)
        report['statics'].append(row)
        if not ok:
            problems.append('static %d %s: %s' % (s['id'], s['why'], {k: row[k] for k in ('ground', 'overlaps_existing', 'overlaps_new', 'stock_template')}))
    for p in people + points:
        g = t.h(p['x'], p['y'])
        near = [f[0] for f in solid_small if circle_poly_overlap(p['x'], p['y'], 0.8, f[5])]
        near += [o[0] for o in new_polys if circle_poly_overlap(p['x'], p['y'], 0.8, o[2])]
        inside = [f[0] for f in fps if f[0] not in near and circle_poly_overlap(p['x'], p['y'], 0.1, f[5])]
        ok = g >= 79.0 and not near
        row = dict(p, ground=round(g, 2), touches_props=near, inside_building_box=inside, ok=ok)
        report['people' if p in people else 'npc_points'].append(row)
        if not ok:
            problems.append('placement %s at %s,%s: ground %.2f, props %s' % (p.get('key', 'npc point'), p['x'], p['y'], g, near))
    lo, hi = t.disc(TRADE_YARD[0], TRADE_YARD[1], 25.0, step=5.0)
    hits = [f[0] for f in fps if circle_poly_overlap(TRADE_YARD[0], TRADE_YARD[1], 25.0, f[5])]
    hits += [o[0] for o in new_polys if circle_poly_overlap(TRADE_YARD[0], TRADE_YARD[1], 25.0, o[2])]
    report['trade_yard'] = {'template': CAMP, 'x': TRADE_YARD[0], 'y': TRADE_YARD[1], 'ground': [round(lo, 2), round(hi, 2)], 'overlaps': hits,
                            'ok': lo >= 79.0 and hi - lo <= 3.0 and not hits}
    if not report['trade_yard']['ok']:
        problems.append('trade yard: %s' % report['trade_yard'])
    dist = [round(math.hypot(s['x'] - TOWN_CENTRE[0], s['y'] - TOWN_CENTRE[1])) for s in statics]
    home = {'schema': 'hutta-home-1', 'units': 'x east, y north, z up (m); yaw/heading = compass degrees (0 north, 90 east)',
            'first_id': FIRST_ID, 'last_id': nid - 1, 'seats': seats, 'statics': report['statics'], 'people': report['people'],
            'npc_points': report['npc_points'], 'trade_yard': report['trade_yard'], 'farthest_static_from_town_centre_m': max(dist),
            'problems': problems}
    jsave(os.path.join(HOME, 'home.json'), home)
    write_lua(home)
    print('statics %d (ids %d-%d), people %d, npc points %d, farthest static %d m from the town centre' % (
        len(statics), FIRST_ID, nid - 1, len(people), len(points), max(dist)))
    for p in problems:
        print('PROBLEM', p)
    return 1 if problems else 0


def write_lua(home):
    path = os.path.join(HOME, 'server', 'MMOCoreORB', 'bin', 'scripts', 'screenplays', 'sandbox', 'hutta_home_places.lua')
    os.makedirs(os.path.dirname(path), exist_ok=True)
    L = ['-- Nal Hutta as the Hutt home (PL-04): placements in Bilbousa. Generated by',
         '-- outputs/Fable-species/s7-hutt/nal-hutta-home/tools/make_home.py from home.json; edit there, not here.',
         '-- x, y, heading (compass degrees: 0 north, 90 east); z comes from getWorldFloor when spawned.',
         '',
         'HuttaHomePlaces = {']
    L.append('\t-- kind, template or terminal role, x, y, heading, label')
    L.append('\tpeople = {')
    for p in home['people']:
        label = p['note'] if p['key'] in ('gamorrean_guard', 'patron_nikto') else ''
        L.append('\t\t{ "%s", "%s", %.2f, %.2f, %d, "%s" },' % (p['kind'], p['key'], p['x'], p['y'], p['heading'], label))
    L.append('\t},')
    ty = home['trade_yard']
    L.append('\t-- the Hutt businessmen camp from Tatooine (stock POI; its tents and crates are its child objects)')
    L.append('\ttradeYard = { "%s", %.1f, %.1f, 0 },' % (ty['template'].replace('/shared_', '/'), ty['x'], ty['y']))
    L.append('}')
    L.append('')
    with open(path, 'w', newline='\n') as f:
        f.write('\n'.join(L))


if __name__ == '__main__':
    sys.exit(main())
