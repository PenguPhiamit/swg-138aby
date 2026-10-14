"""Cresh, missions: take the nearest destroy mission within 600 m from a Mos Eisley mission terminal (found with the server's
object search, Bot.locate, inside buildings too), walk to its target with basic gear, attack the lair, and check
that the mission completes. Missions are also how combat groups find creatures."""
import math
from pathlib import Path

GROUP = 'Cresh'
PLACES = Path(__file__).resolve().parents[1] / 'places.json'


def run(g):
    cresh, ilsa, kor = g['Cresh'], g['Ilsa'], g['Kor']
    for bot in g.bots:
        g.note(f'{bot.first} gear: ' + str(bot.gear('basic'))[:160])

    here = cresh.status()
    # The server's object search finds terminals anywhere in town, inside buildings too (then with a cell).
    spots = [t for t in cresh.locate('terminal_mission', radius=1500)
             if not any(k in t.get('template', '') for k in ('bounty', 'entertainer', 'imperial', 'rebel', 'scout', 'newbie'))]
    if not g.check('a mission terminal in town', spots, spots and {k: spots[0].get(k) for k in ('template', 'distance', 'cell')}):
        g.note('BLOCKED: no general mission terminal within 1.5 km of ' + f"{here.get('x', 0):.0f} {here.get('y', 0):.0f}")
        return
    spot = spots[0]
    if spot.get('cell'):  # inside a building: walk to it in its cell
        local = spot['local']
        trips = g.parallel(*[lambda b=b: b.walk(local['x'], local['y'], local['z'], spot['cell']) for b in g.bots])
    else:
        trips = g.parallel(*[lambda b=b, i=i: b.walk(spot['x'] + 2 * i, spot['y'] - 3) for i, b in enumerate(g.bots)])
    if not g.check('reach the mission terminal', all(isinstance(t, dict) and t.get('arrived') for t in trips), trips):
        return
    terminal = {'oid': spot['oid'], 'x': spot.get('local', spot)['x'], 'y': spot.get('local', spot)['y']}

    offered = [m for m in cresh.mission_list(terminal['oid']) if 'mission_bag' in str(m.get('container_name'))]
    kinds = sorted({str(m.get('type')) for m in offered})
    g.check('the terminal lists missions', offered, f'{len(offered)} missions: {kinds}')
    here = cresh.status()  # distance from terminal, not the old staging position
    def distance(m):
        target = m.get('waypoint') or m.get('start') or {}
        if target.get('planet', here.get('planet')) != here.get('planet'):
            return math.inf
        if not all(isinstance(target.get(k), (int, float)) for k in ('x', 'y')):
            return math.inf
        return math.hypot(target['x'] - here['x'], target['y'] - here['y'])
    destroy = sorted((m for m in offered if m.get('type') == 'destroy' and distance(m) <= 600), key=distance)
    if not destroy:
        g.note('BLOCKED: no same-planet destroy mission with a known waypoint within 600 m; no mission accepted.')
        return
    mission = destroy[0]
    cresh.accept_mission(mission['oid'], terminal['oid'])
    mine = next((m for m in cresh.missions() if m['oid'] == mission['oid']), {})
    if not g.check('accept the nearest destroy mission', 'datapad' in str(mine.get('container_name')),
            {k: mission.get(k) for k in ('title', 'target', 'difficulty', 'reward')}):
        return
    target = mine.get('waypoint') or mine.get('start') or mission.get('waypoint') or mission.get('start')
    if not target or not all(isinstance(target.get(k), (int, float)) for k in ('x', 'y')):
        g.note('BLOCKED: accepted mission omitted usable target coordinates.')
        return
    distance = math.hypot(target['x'] - here['x'], target['y'] - here['y'])
    if distance > 600 or target.get('planet', here.get('planet')) != here.get('planet'):
        g.note('BLOCKED: accepted target changed outside the bounded route; mission retained for inspection.')
        return
    g.note(f"target {target['x']:.0f} {target['y']:.0f} on {target.get('planet')}, about {distance:.0f} m away")

    trips = g.parallel(*[lambda b=b, i=i: b.walk(target['x'] + 3 * i, target['y'] - 12, tries=3) for i, b in enumerate(g.bots)])
    if not g.check('reach the mission area', all(isinstance(t, dict) and t.get('arrived') for t in trips),
            [(b.first, t.get('seconds') if isinstance(t, dict) else str(t)) for b, t in zip(g.bots, trips)]):
        return
    lair = cresh.find('lair', radius=80, type='TANO') or cresh.find('', radius=40, type='TANO',
                                                                      where=lambda o: '@lair_n:' in str(o.get('name')))
    if not g.check('find the lair', lair, lair and f"{lair['name']} {lair['distance']} m"):
        return
    g.parallel(lambda: kor.fight(lair['oid'], 150), lambda: cresh.fight(lair['oid'], 150))
    gone = not any(o['oid'] == lair['oid'] for o in cresh.look(radius=100, type='TANO', limit=400))
    done = cresh.wait_for(lambda e: 'mission' in str(e.get('text', '')).lower(), 10)
    left = next((m for m in cresh.missions() if m['oid'] == mission['oid']), None)
    g.check('the lair is destroyed', gone)
    g.check('the mission completes', gone and left is None,
            {'mission_removed': left is None, 'message': (done or {}).get('text')})
    g.note('Payout remains unverified until body exposes reliable credits before/after.')
    for bot in g.bots:
        g.note(f'{bot.first} after: {bot.posture()}')
