"""Claude, movement probe (test plan section 4): do server corrections depend on walking speed?

Each Besh-group bot walks straight 200 m legs in open desert south of Mos Eisley (no /agentpath, path=False) at
5.0, 4.6 and 4.2 m/s, in a different order per bot, and counts position_set_by_server events per leg. The body
gives up after 3 corrections in one move, so a leg that fails reports how far it got first."""
import math

GROUP = 'Besh'
WEST, EAST = 3480, 3680
SPEEDS = (5.0, 4.6, 4.2)


def leg(bot, x, y, speed):
    start = bot.status()
    reply = bot.request('move', 110, x=x, y=y, speed=speed, path=False, timeout=95)
    fixes = [e for e in bot.inbox if e.get('event') == 'position_set_by_server']
    end = bot.status()
    walked = math.hypot(end.get('x', 0) - start.get('x', 0), end.get('y', 0) - start.get('y', 0))
    return {'speed': speed, 'arrived': bool(reply.get('arrived')), 'error': reply.get('error'),
            'seconds': reply.get('seconds'), 'walked': round(walked, 1), 'corrections': len(fixes),
            'fixes': [(round(e['x'], 1), round(e['y'], 1)) for e in fixes]}


def lane(bot, i):
    y = -5090 - 10 * i
    out = [bot.walk(WEST, y)]
    order = SPEEDS[i % 3:] + SPEEDS[:i % 3]
    legs = []
    for n, speed in enumerate(order * 2):
        legs.append(leg(bot, EAST if n % 2 == 0 else WEST, y, speed))
    return {'bot': bot.first, 'start': {k: out[0].get(k) for k in ('arrived', 'error', 'seconds')}, 'legs': legs}


def run(g):
    for bot in g.bots:
        if bot.status().get('planet') != 'tatooine':
            g.note(f'BLOCKED: {bot.first} is not on Tatooine')
            return
    results = g.parallel(*[lambda b=b, i=i: lane(b, i) for i, b in enumerate(g.bots)])
    per_speed = {s: {'legs': 0, 'metres': 0.0, 'corrections': 0, 'failed': 0} for s in SPEEDS}
    for r in results:
        if not isinstance(r, dict):
            g.note(f'ERROR lane: {r}')
            continue
        g.note(f"{r['bot']}: " + '; '.join(f"{l['speed']} m/s {l['walked']} m {l['corrections']} fixes"
                                           + ('' if l['arrived'] else f" ({l['error']})") for l in r['legs']))
        for l in r['legs']:
            s = per_speed[l['speed']]
            s['legs'] += 1
            s['metres'] += l['walked']
            s['corrections'] += l['corrections']
            s['failed'] += 0 if l['arrived'] else 1
    for speed, s in per_speed.items():
        rate = s['corrections'] / s['metres'] * 100 if s['metres'] else None
        g.note(f"speed {speed}: {s['legs']} legs, {s['metres']:.0f} m, {s['corrections']} corrections"
               f" ({rate if rate is None else round(rate, 2)} per 100 m), {s['failed']} legs failed")
    slow = per_speed[SPEEDS[-1]]
    g.check(f'no corrections at {SPEEDS[-1]} m/s', slow['corrections'] == 0, slow)
    g.check(f'no failed legs at {SPEEDS[0]} m/s', per_speed[SPEEDS[0]]['failed'] == 0, per_speed[SPEEDS[0]])
