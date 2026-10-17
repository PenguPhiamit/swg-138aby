"""Claude, movement probe 2 (test plan section 4): corrections on server-planned path walks.

claude-probe-movement.py found no corrections on straight walks (path=False) at any speed. The failing scenarios walk
/agentpath routes, so this repeats their failing trips with path walking and records, for every move, the planned
route's first point against where the bot stood, the route's longest step, and each correction.
- Dova: from the square straight into the cloning facility's cell, 268 m (failed on 17 Oct at 3:26 AM).
- Besh: square to the plateau (Tovan failed the same trip on 15 Oct) and back.
- Pell and Varo: long outdoor routes east of town (Cresh's mission area) and back."""
import math

GROUP = 'Besh'
SQUARE = (3528, -4800)
PLATEAU = (3830, -4530)
EAST = (4150, -4900)
CLONING = dict(x=-0.5, y=2.5, z=-0.05, cell=1106502)  # Mos Eisley cloning facility (building 1106500), inside


def route(bot, x, y, z=None, cell=None):
    here = bot.status()
    plan = bot.path(x, y, z, cell, 30)
    points = plan.get('points') or []
    info = {'ok': plan.get('ok'), 'error': plan.get('error'), 'points': len(points)}
    if points:
        p0 = points[0]
        info['first_point_off'] = round(math.hypot(p0[0] - here.get('x', 0), p0[1] - here.get('y', 0)), 2) \
            if (p0[3] or 0) == (here.get('cell') or 0) else f"cell {p0[3]} vs {here.get('cell')}"
        steps = [(math.hypot(b[0] - a[0], b[1] - a[1]), a[3] != b[3]) for a, b in zip(points, points[1:])]
        if steps:
            longest = max(steps)
            info['longest_step'] = round(longest[0], 1)
            info['doorway_steps'] = [round(s, 1) for s, door in steps if door]
    return info


def trip(bot, label, x, y, z=None, cell=None):
    plan = route(bot, x, y, z, cell)
    fixes, began, reply = [], bot.status(), {}
    for _ in range(3):  # walk(): a single move stops at 95 s; keep the corrections of every try
        reply = bot.move(x, y, z, cell, 95)
        fixes += [e for e in bot.inbox if e.get('event') == 'position_set_by_server']
        if reply.get('arrived') or 'timeout' not in str(reply.get('error', '')):
            break
    return {'bot': bot.first, 'trip': label, 'plan': plan, 'arrived': bool(reply.get('arrived')),
            'error': reply.get('error'), 'seconds': reply.get('seconds'), 'legs': reply.get('legs'),
            'body_corrections': reply.get('corrections'),
            'corrections': [(round(e['x'], 1), round(e['y'], 1), round(e.get('z', 0), 1), e.get('cell'), e.get('moved'))
                            for e in fixes]}


def posture_walk(bot, command, dx):
    """Kneel or sit, then walk 20 m: the body stands up first (17 Oct) instead of being put back every step."""
    bot.slash(command, wait=2.0)
    before = (bot.status().get('me') or {}).get('posture')
    here = bot.status()
    reply = bot.move(here['x'] + dx, here['y'], None, None, 60)
    fixes = [e for e in bot.inbox if e.get('event') == 'position_set_by_server']
    return {'bot': bot.first, 'trip': f'/{command} ({before}) then 20 m', 'plan': {}, 'arrived': bool(reply.get('arrived')),
            'error': reply.get('error'), 'seconds': reply.get('seconds'), 'legs': reply.get('legs'),
            'body_corrections': reply.get('corrections'),
            'corrections': [(round(e['x'], 1), round(e['y'], 1), round(e.get('z', 0), 1), e.get('cell'), e.get('moved'))
                            for e in fixes]}


def run(g):
    besh, dova, pell, varo = g['Besh'], g['Dova'], g['Pell'], g['Varo']
    for bot in g.bots:
        if bot.status().get('planet') != 'tatooine':
            g.note(f'BLOCKED: {bot.first} is not on Tatooine')
            return
    g.parallel(*[lambda b=b, i=i: b.walk(SQUARE[0] + 3 * i, SQUARE[1]) for i, b in enumerate(g.bots)])
    jobs = [
        lambda: [trip(dova, 'square to cloning cell', **CLONING), trip(dova, 'cloning cell to square', *SQUARE)],
        lambda: [posture_walk(besh, 'kneel', 20), posture_walk(besh, 'sit', -20),
                 trip(besh, 'square to plateau', *PLATEAU), trip(besh, 'plateau to square', SQUARE[0] + 3, SQUARE[1])],
        lambda: [trip(pell, 'square to east', *EAST), trip(pell, 'east to square', SQUARE[0] + 6, SQUARE[1])],
        lambda: [trip(varo, 'square to east', EAST[0], EAST[1] - 10), trip(varo, 'east to square', SQUARE[0] + 9, SQUARE[1])],
    ]
    results = g.parallel(*jobs)
    total = failed = fixes = 0
    for trips in results:
        if not isinstance(trips, list):
            g.note(f'ERROR: {trips}')
            continue
        for t in trips:
            total += 1
            failed += 0 if t['arrived'] else 1
            fixes += sum(1 for c in t['corrections'] if c[4] is None or c[4] > 0.05)  # moved 0: the server's resync echo
            g.note(f"{t['bot']} {t['trip']}: {'arrived' if t['arrived'] else t['error']} in {t['seconds']} s, "
                   f"legs {t['legs']}, plan {t['plan']}, body counted {t['body_corrections']}, events {t['corrections']}")
    g.note(f'{total} trips, {failed} failed, {fixes} corrections')
    g.check('every path trip arrives', failed == 0, f'{failed} of {total} failed')
    g.check('no corrections on path trips', fixes == 0, f'{fixes} corrections')
