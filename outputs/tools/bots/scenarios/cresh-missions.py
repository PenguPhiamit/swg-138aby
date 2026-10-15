"""Cresh, missions: take the nearest destroy mission from a general Mos Eisley mission terminal (found with the server's
object search, Bot.locate, inside buildings too), walk to its target with basic gear, attack the lair, and check
that the mission completes and pays into the bank. Missions are also how combat groups find creatures.

Server rules (Agent/local-research/missions/report.md, 15 Oct; Claude rewrote the checks from it):
  * Only general terminals (terminal_mission.iff) give destroy missions; artisan, statue and newbie ones don't.
  * A destroy target is placed 1000-2000 m from where the list was requested, so the old 600 m bound refused every one.
  * The lair spawns only when the mission's owner (Cresh) comes within 128 m of the waypoint. It can land up to about
    256 m away; the server then says "Transmission Received: Mission Target has been located..." and moves the waypoint.
  * A player holds at most 2 missions. The reward (375 x level + up to 15 x level) goes into the BANK.
"""
import math
from pathlib import Path

GROUP = 'Cresh'
PLACES = Path(__file__).resolve().parents[1] / 'places.json'
MAX_ROUTE = 2300  # 2000 m placement plus the lair's offset
LOCATED = 'Mission Target has been located'


def point(m):
    """Where the mission sends us: its waypoint once it has one, else its start. A listed mission's waypoint is an
    empty one (planet "0" at 0, 0); reading it as the target refused all six destroy missions on 15 Oct (Claude)."""
    for key in ('waypoint', 'start'):
        p = (m or {}).get(key) or {}
        if str(p.get('planet', '0')) not in ('0', '') and isinstance(p.get('x'), (int, float)) \
                and isinstance(p.get('y'), (int, float)) and (p['x'] or p['y']):
            return p
    return {}


def run(g):
    cresh, ilsa, kor = g['Cresh'], g['Ilsa'], g['Kor']
    for bot in g.bots:
        g.note(f'{bot.first} gear: ' + str(bot.gear('basic'))[:160])

    here = cresh.status()
    # The server's object search finds terminals anywhere in town, inside buildings too (then with a cell).
    spots = [t for t in cresh.locate('terminal_mission', radius=1500)
             if str(t.get('template', '')).rsplit('/', 1)[-1] == 'terminal_mission.iff']
    if not g.check('a mission terminal in town', spots, spots and {k: spots[0].get(k) for k in ('template', 'distance', 'cell')}):
        g.note('BLOCKED: no general mission terminal (terminal_mission.iff) within 1.5 km of '
               + f"{here.get('x', 0):.0f} {here.get('y', 0):.0f}")
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

    held = [m for m in cresh.missions() if 'datapad' in str(m.get('container_name'))]
    if len(held) >= 2:
        g.note(f'BLOCKED: Cresh already holds {len(held)} missions (the server allows 2); abort them by hand: '
               + ', '.join(str(m.get('title')) for m in held))
        return
    offered = [m for m in cresh.mission_list(terminal['oid']) if 'mission_bag' in str(m.get('container_name'))]
    kinds = sorted({str(m.get('type')) for m in offered})
    g.check('the terminal lists missions', offered, f'{len(offered)} missions: {kinds}')
    here = cresh.status()  # where the list was requested: the server measures from here

    def distance(m):
        target = point(m)
        if target.get('planet', here.get('planet')) != here.get('planet'):
            return math.inf
        if not all(isinstance(target.get(k), (int, float)) for k in ('x', 'y')):
            return math.inf
        return math.hypot(target['x'] - here['x'], target['y'] - here['y'])
    destroy = sorted((m for m in offered if m.get('type') == 'destroy' and distance(m) <= MAX_ROUTE), key=distance)
    if not destroy:
        g.note(f'BLOCKED: no same-planet destroy mission with a known waypoint within {MAX_ROUTE} m '
               f'(offered: {kinds}); no mission accepted.')
        return
    mission = destroy[0]
    bank_before = here.get('bank_credits')
    cresh.accept_mission(mission['oid'], terminal['oid'])
    mine = next((m for m in cresh.missions() if m['oid'] == mission['oid']), {})
    if not g.check('accept the nearest destroy mission', 'datapad' in str(mine.get('container_name')),
            {k: mission.get(k) for k in ('title', 'target', 'difficulty', 'reward')}):
        return
    target = point(mine) or point(mission)
    if not target or not all(isinstance(target.get(k), (int, float)) for k in ('x', 'y')):
        g.note('BLOCKED: accepted mission omitted usable target coordinates.')
        return
    away = math.hypot(target['x'] - here['x'], target['y'] - here['y'])
    if away > MAX_ROUTE or target.get('planet', here.get('planet')) != here.get('planet'):
        g.note('BLOCKED: accepted target changed outside the bounded route; mission retained for inspection.')
        return
    g.note(f"target {target['x']:.0f} {target['y']:.0f} on {target.get('planet')}, about {away:.0f} m away; "
           f"reward {mission.get('reward')}")

    # Cresh (the owner) leads: only the owner entering the 128 m area spawns the lair.
    trips = g.parallel(*[lambda b=b, i=i: b.walk(target['x'] + 3 * i, target['y'] - 12, tries=3) for i, b in enumerate(g.bots)])
    if not g.check('reach the mission area', all(isinstance(t, dict) and t.get('arrived') for t in trips),
            [(b.first, t.get('seconds') if isinstance(t, dict) else str(t)) for b, t in zip(g.bots, trips)]):
        return
    located = cresh.wait_for(lambda e: LOCATED in str(e.get('text', '')), 20)
    g.check('the target is located (waypoint updated)', located, (located or {}).get('text'))
    moved = next((m for m in cresh.missions() if m['oid'] == mission['oid']), {})
    spot = point(moved) or target
    if located and all(isinstance(spot.get(k), (int, float)) for k in ('x', 'y')) \
            and math.hypot(spot['x'] - target['x'], spot['y'] - target['y']) > 20:
        g.note(f"waypoint moved {math.hypot(spot['x'] - target['x'], spot['y'] - target['y']):.0f} m to the lair")
        g.parallel(*[lambda b=b, i=i: b.walk(spot['x'] + 3 * i, spot['y'] - 15, tries=3) for i, b in enumerate(g.bots)])
    lair = cresh.find('lair', radius=80, type='TANO') or cresh.find('', radius=60, type='TANO',
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
    if gone and left is None:
        bank_after = cresh.status().get('bank_credits')
        paid = (bank_after - bank_before) if isinstance(bank_after, int) and isinstance(bank_before, int) else None
        reward = mission.get('reward')
        # Group members within 128 m of the mission's end point share the reward, so Cresh's part can be a third.
        g.check('the reward reaches the bank', paid is not None and paid > 0,
                {'bank_before': bank_before, 'bank_after': bank_after, 'paid': paid, 'reward': reward})
    for bot in g.bots:
        g.note(f'{bot.first} after: {bot.posture()}')
