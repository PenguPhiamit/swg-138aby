"""PL-06: lay out Bilbousa's townsfolk and the swamp sites, check them, and write life.json and the generated Lua
(server/MMOCoreORB/bin/scripts/screenplays/sandbox/hutta_life_places.lua).

Town: patrol routes are found on a 2 m grid of free ground (A* round Darklight's buildings, PL-04's statics and people,
footprints padded 1.2 m), then thinned to corners whose straight legs stay clear. Stationary townsfolk stand on free
cells near the town's meeting points, at least 3 m apart and 2.5 m from anything. Swamp: each site centre comes from
find_swamp_sites.py; every spawn offset is checked for dry ground (>= 76.5 m, the water is 75 m) and given its height.
    C:/Users/Pengw/miniconda3/python.exe -I make_life.py
"""
import heapq, json, math, os, random, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from life_common import LIFE, occupied, blocked, segment_clear, TOWN_CENTRE  # noqa: E402
sys.path.insert(0, os.path.join(LIFE, '..', 'nal-hutta-home', 'tools'))
from hutta_common import Terrain  # noqa: E402

GRID, PAD, Z_TOWN = 2.0, 1.2, 80.0
OUT_LUA = os.path.join(LIFE, 'server', 'MMOCoreORB', 'bin', 'scripts', 'screenplays', 'sandbox', 'hutta_life_places.lua')

# meeting points (x, y): open ground PL-04 already uses or that the town map shows free
ANCHORS = {
    'starport': (-766, 1696), 'avenue_north': (-766, 1640), 'bank_west': (-830, 1560), 'bank_east': (-716, 1560),
    'bazaar_north': (-768, 1515), 'bazaar': (-768, 1470), 'palace_gate': (-766, 1436), 'cantina': (-646, 1527),
    'kessoth': (-652, 1632), 'narissik': (-588, 1501), 'vollaka': (-926, 1562), 'dromuul': (-889, 1764),
    'bessolo': (-1000, 1690), 'tashuga': (-750, 1872), 'east_street': (-700, 1640),
}
# patrol name -> anchors visited in a loop (the route between each pair is found by A*)
PATROLS = {
    'avenue': ['starport', 'avenue_north', 'bank_west', 'bazaar', 'palace_gate', 'bazaar', 'bank_east', 'avenue_north'],
    'cantina_run': ['cantina', 'bank_east', 'east_street', 'kessoth', 'east_street', 'bank_east'],
    'west_seats': ['vollaka', 'bank_west', 'avenue_north', 'dromuul', 'bessolo', 'vollaka'],
    'east_seats': ['narissik', 'cantina', 'kessoth', 'east_street', 'starport', 'bank_east', 'narissik'],
    'bazaar_loop': ['bazaar_north', 'bazaar', 'palace_gate', 'bazaar'],
}
# who walks each route: (route, template or "patrolNpc", start anchor index, mood)
WALKERS = [('avenue', 'patrolNpc', 0, ''), ('avenue', 'patrolNpc', 4, ''), ('cantina_run', 'patrolNpc', 0, ''),
           ('cantina_run', 'hutta_weequay_watch', 3, ''), ('west_seats', 'hutta_weequay_watch', 0, ''),
           ('west_seats', 'patrolNpc', 3, ''), ('east_seats', 'patrolNpc', 0, ''), ('east_seats', 'hutta_weequay_watch', 5, ''),
           ('bazaar_loop', 'patrolNpc', 0, ''), ('bazaar_loop', 'patrolNpc', 2, '')]
# stationary townsfolk per anchor (the screenplay draws a commoner or an NPC per spot, as the stock cities do)
STATIONARY = {'starport': 3, 'avenue_north': 2, 'bank_west': 3, 'bank_east': 2, 'bazaar': 4, 'bazaar_north': 2,
              'palace_gate': 2, 'cantina': 3, 'east_street': 2, 'narissik': 1}
# named people who stand still and talk: (key, anchor, mood)
TALKERS = [('hutta_rodian_trader', 'bazaar', 'conversation'), ('hutta_old_weequay', 'bank_west', 'bored'),
           ('hutta_twilek_attendant', 'palace_gate', 'calm'), ('hutta_swamp_beggar', 'bazaar_north', 'sad'),
           ('hutta_nikto_dockhand', 'starport', 'npc_standing_drinking')]
# Hutt retinues: a lounging Hutt noble, two Gamorrean guards, a Twi'lek attendant
RETINUES = [('hutta_hutt_noble_kessoth', 'east_street'), ('hutta_hutt_noble_dromuul', 'bank_west')]
# the quest giver stands by the Kessoth seat's door
QUEST_GIVER = ('hutta_kessoth_majordomo', 'kessoth')

# swamp sites (centre from sites.json: sector, band) and their contents as offsets from the centre
SITES = {
    'swamp_rat_camp': {'from': ('SW', 'near'), 'building': 'object/building/poi/naboo_swamp_rat_gang_camp_medium.iff',
                       'name': 'a smugglers\' camp'},
    'freighter_wreck': {'from': ('E', 'near'), 'name': 'a burned freighter'},
    'spice_den': {'from': ('NW', 'mid'), 'building': 'object/building/poi/tatooine_spicefiend_medium.iff', 'name': 'a spice den'},
    'old_ruins': {'from': ('SE', 'mid'), 'building': 'object/building/poi/naboo_ruins_medium_1.iff', 'name': 'old ruins'},
    'hit_squad_camp': {'from': ('SW', 'mid'), 'building': 'object/building/poi/tatooine_hutt_assassin_camp_medium1.iff',
                       'name': 'a rival kajidic\'s camp'},
}


def grid_free(polys, x0, x1, y0, y1):
    free = set()
    y = y0
    while y <= y1:
        x = x0
        while x <= x1:
            if not blocked(polys, x, y, r=0.9):
                free.add((round(x), round(y)))
            x += GRID
        y += GRID
    return free


def snap(free, p):
    return min(free, key=lambda c: (c[0] - p[0]) ** 2 + (c[1] - p[1]) ** 2)


def astar(free, a, b):
    a, b = snap(free, a), snap(free, b)
    openq = [(0, a)]
    came, g = {a: None}, {a: 0}
    while openq:
        _, cur = heapq.heappop(openq)
        if cur == b:
            break
        for dx in (-GRID, 0, GRID):
            for dy in (-GRID, 0, GRID):
                if not dx and not dy:
                    continue
                n = (round(cur[0] + dx), round(cur[1] + dy))
                if n not in free:
                    continue
                cost = g[cur] + math.hypot(dx, dy)
                if cost < g.get(n, 1e9):
                    g[n] = cost
                    came[n] = cur
                    heapq.heappush(openq, (cost + math.hypot(b[0] - n[0], b[1] - n[1]), n))
    if b not in came:
        raise SystemExit('no path %s -> %s' % (a, b))
    path, c = [], b
    while c:
        path.append(c)
        c = came[c]
    return path[::-1]


def thin(polys, path):
    """Keep only the corners: from each kept point, jump to the farthest later point whose straight leg is clear."""
    out, i = [path[0]], 0
    while i < len(path) - 1:
        k = i + 1
        for m in range(len(path) - 1, i + 1, -1):
            if not segment_clear(polys, path[i], path[m], step=0.75):
                k = m
                break
        out.append(path[k])
        i = k
    return out


def main():
    polys = occupied(pad=PAD)
    free = grid_free(polys, -1060, -500, 1420, 1900)
    print('free cells', len(free))
    report = {'problems': []}

    routes = {}
    for name, stops in PATROLS.items():
        pts = []
        for a, b in zip(stops, stops[1:] + stops[:1]):
            leg = thin(polys, astar(free, ANCHORS[a], ANCHORS[b]))
            pts.extend(leg[:-1])
        # delay (True) at each anchor stop, plain corners otherwise
        anchors = {snap(free, ANCHORS[s]) for s in stops}
        routes[name] = [[p[0], Z_TOWN, p[1], 0, p in anchors] for p in pts]
        for p, q in zip(pts, pts[1:] + pts[:1]):
            hit = segment_clear(polys, p, q, step=0.75)
            if hit:
                report['problems'].append('route %s leg %s-%s touches %s' % (name, p, q, hit))
    walkers = []
    for route, tpl, start, mood in WALKERS:
        p = routes[route][min(start * 3, len(routes[route]) - 1)]
        walkers.append([route, tpl, p[0], Z_TOWN, p[2], 0, 0, mood, False])

    rnd = random.Random(1017)
    taken = []

    def spot(anchor, near=14.0):
        cx, cy = ANCHORS[anchor]
        cands = [c for c in free if math.hypot(c[0] - cx, c[1] - cy) <= near and not blocked(polys, c[0], c[1], r=2.5)
                 and all(math.hypot(c[0] - t[0], c[1] - t[1]) >= 3.0 for t in taken)
                 and not any(math.hypot(c[0] - w[0], c[1] - w[1]) < 2.0 for r in routes.values() for w in [(q[0], q[2]) for q in r])]
        if not cands and near < 30:
            return spot(anchor, near + 8)
        if not cands:
            report['problems'].append('no free spot near ' + anchor)
            return None
        c = rnd.choice(sorted(cands))
        taken.append(c)
        return c

    stationary = []
    for anchor, n in STATIONARY.items():
        for _ in range(n):
            c = spot(anchor)
            if c:
                stationary.append([300, c[0], Z_TOWN, c[1], rnd.choice([0, 45, 90, 135, 180, 225, 270, 315]), 0,
                                   rnd.choice(['conversation', '', 'bored', 'calm', 'npc_standing_drinking'])])
    talkers = []
    for key, anchor, mood in TALKERS:
        c = spot(anchor)
        if c:
            talkers.append([key, c[0], c[1], rnd.choice([0, 90, 180, 270]), mood])
    retinues = []
    for key, anchor in RETINUES:
        c = spot(anchor, near=18.0)
        if c:
            retinues.append([key, c[0], c[1], 180])
    giver = spot(QUEST_GIVER[1], near=10.0)

    # swamp sites
    sites_found = {(s['sector'], s['band']): s for s in json.load(open(os.path.join(LIFE, 'sites.json')))}
    t = Terrain()
    sites = {}
    ring = [(0, 0)] + [(round(r * math.sin(math.radians(a)), 1), round(r * math.cos(math.radians(a)), 1))
                       for r, n in ((9, 5), (15, 7)) for a in range(0, 360, 360 // n)]
    for key, s in SITES.items():
        f = sites_found[s['from']]
        x, y = f['x'], f['y']
        pts = []
        for dx, dy in ring:
            h = t.h(x + dx, y + dy)
            if h >= 76.5:
                pts.append([dx, dy, round(h, 2)])
        if len(pts) < 8:
            report['problems'].append('site %s: only %d dry points' % (key, len(pts)))
        sites[key] = {'x': x, 'y': y, 'z': round(t.h(x, y), 2), 'relief': f['relief'], 'dist': f['dist'],
                      'name': s['name'], 'building': s.get('building', ''), 'points': pts}

    life = {'schema': 'hutta-life-1', 'anchors': ANCHORS, 'routes': routes, 'walkers': walkers, 'stationary': stationary,
            'talkers': talkers, 'retinues': retinues, 'quest_giver': [QUEST_GIVER[0], giver[0], giver[1], 180] if giver else None,
            'sites': sites, 'problems': report['problems']}
    json.dump(life, open(os.path.join(LIFE, 'life.json'), 'w'), indent=1)
    write_lua(life)
    print('routes', {k: len(v) for k, v in routes.items()}, 'stationary', len(stationary), 'talkers', len(talkers),
          'retinues', len(retinues), 'sites', {k: (v['x'], v['y'], v['z'], len(v['points'])) for k, v in sites.items()})
    print('problems:', report['problems'] or 'none')
    return 1 if report['problems'] else 0


def lua_list(rows, indent='\t\t'):
    def val(v):
        if isinstance(v, bool):
            return 'true' if v else 'false'
        if isinstance(v, str):
            return '"%s"' % v
        if isinstance(v, float):
            return '%.2f' % v
        return str(v)
    return '\n'.join(indent + '{ ' + ', '.join(val(v) for v in r) + ' },' for r in rows)


def write_lua(life):
    os.makedirs(os.path.dirname(OUT_LUA), exist_ok=True)
    out = ['-- Nal Hutta life (PL-06): Bilbousa\'s townsfolk and the swamp sites. Generated by',
           '-- outputs/Fable-species/s7-hutt/nal-hutta-life/tools/make_life.py from life.json; edit there, not here.',
           '-- Town x, y on the 80 m shelf; headings in compass degrees. Site points are offsets from the site centre with',
           '-- their ground height (all dry, above the 75 m water).', '', 'HuttaLifePlaces = {']
    out.append('\t-- patrol routes: { x, z, y, cell, wait here }')
    out.append('\tpatrolPoints = {')
    for name, pts in life['routes'].items():
        out.append('\t\t%s = {' % name)
        out.append(lua_list(pts, '\t\t\t'))
        out.append('\t\t},')
    out.append('\t},')
    out.append('\t-- { route, template, x, z, y, heading, cell, mood, combat }')
    out.append('\tpatrolMobiles = {\n' + lua_list(life['walkers']) + '\n\t},')
    out.append('\t-- { respawn, x, z, y, heading, cell, mood }')
    out.append('\tstationaryMobiles = {\n' + lua_list(life['stationary']) + '\n\t},')
    out.append('\t-- { template, x, y, heading, mood }')
    out.append('\ttalkers = {\n' + lua_list(life['talkers']) + '\n\t},')
    out.append('\t-- { Hutt template, x, y, heading }: the guards and the attendant stand round the Hutt')
    out.append('\tretinues = {\n' + lua_list(life['retinues']) + '\n\t},')
    g = life['quest_giver']
    out.append('\tquestGiver = { "%s", %.2f, %.2f, %d },' % (g[0], g[1], g[2], g[3]))
    out.append('\t-- swamp sites: centre, the POI building (if any) and dry spawn points { dx, dy, z }')
    out.append('\tsites = {')
    for key, s in life['sites'].items():
        out.append('\t\t%s = { x = %.1f, y = %.1f, z = %.2f, building = "%s", points = {' % (key, s['x'], s['y'], s['z'], s['building']))
        out.append(lua_list(s['points'], '\t\t\t'))
        out.append('\t\t} },')
    out.append('\t},')
    out.append('}')
    open(OUT_LUA, 'w', newline='\n').write('\n'.join(out) + '\n')


if __name__ == '__main__':
    sys.exit(main())
