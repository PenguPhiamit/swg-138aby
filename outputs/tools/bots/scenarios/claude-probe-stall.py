"""Claude, stall probe (movement-pushback.md, speed check design A): how many walkers does a server stall bounce?

Every bot in the group walks straight 200 m legs at 5.0 m/s in open desert south of Mos Eisley (path=False) for
STALL_PROBE_SECONDS (default 360), counting server corrections that moved it. Meanwhile the stall is made by hand
(botpop_scale.py down, then step 300 ... all: a BotPop login burst). Run several groups at once with --group, but not
Esk (botpop_scale.py drives esk3). Each group also counts the test galaxy's [Movement] lines written while it walked
(every player's, so the groups' counts overlap): bounces, failed speed checks and (design A) forgiven ones."""
import math, os, time
from pathlib import Path

GROUP = 'Besh'
WEST, EAST = 3480, 3680
SPEED = 5.0
SECONDS = float(os.environ.get('STALL_PROBE_SECONDS', 360))
LANES = ['Aurek', 'Besh', 'Cresh', 'Dorn', 'Forn', 'Esk']
CONSOLE = Path('/opt/swg/testgalaxy/console.log')


def leg(bot, x, y):
    start = bot.status()
    reply = bot.request('move', 110, x=x, y=y, speed=SPEED, path=False, timeout=95)
    fixes = [e for e in bot.inbox if e.get('event') == 'position_set_by_server' and e.get('moved', True)]
    end = bot.status()
    walked = math.hypot(end.get('x', 0) - start.get('x', 0), end.get('y', 0) - start.get('y', 0))
    return {'arrived': bool(reply.get('arrived')), 'error': reply.get('error'), 'walked': round(walked, 1),
            'corrections': len(fixes), 'at': time.strftime('%H:%M:%S')}


def lane(bot, y, deadline):
    first = bot.walk(WEST, y)
    legs = []
    while time.time() < deadline:
        legs.append(leg(bot, EAST if len(legs) % 2 == 0 else WEST, y))
    return {'bot': bot.first, 'start': first.get('arrived'), 'legs': legs}


def movement_lines(offset):
    with CONSOLE.open('rb') as f:
        f.seek(offset)
        lines = [l for l in f.read().decode(errors='replace').splitlines() if '[Movement]' in l]
    return {'bounces': sum('bounce:' in l for l in lines),
            'speed check failed': sum('speed check:' in l for l in lines),
            'forgiven': sum('speed check forgiven' in l for l in lines)}, lines


def run(g):
    for bot in g.bots:
        if bot.status().get('planet') != 'tatooine':
            g.note(f'BLOCKED: {bot.first} is not on Tatooine')
            return
    offset = CONSOLE.stat().st_size if CONSOLE.exists() else None
    began = time.strftime('%I:%M:%S %p')
    deadline = time.time() + SECONDS
    base = LANES.index(g.name) * 4 if g.name in LANES else 24
    results = g.parallel(*[lambda b=b, i=i: lane(b, -5090 - 10 * (base + i), deadline) for i, b in enumerate(g.bots)])
    legs = metres = corrections = failed = 0
    for r in results:
        if not isinstance(r, dict):
            g.note(f'ERROR lane: {r}')
            continue
        g.note(f"{r['bot']}: " + '; '.join(f"{l['at']} {l['walked']} m {l['corrections']} fixes"
                                           + ('' if l['arrived'] else f" ({l['error']})") for l in r['legs']))
        for l in r['legs']:
            legs += 1
            metres += l['walked']
            corrections += l['corrections']
            failed += 0 if l['arrived'] else 1
    g.note(f'{g.name}: walked from {began} for {SECONDS:.0f} s: {legs} legs, {metres:.0f} m, {corrections} corrections,'
           f' {failed} legs failed')
    if offset is not None:
        counts, lines = movement_lines(offset)
        g.note(f'server [Movement] lines while walking (all players): {counts}')
        for line in lines[:40]:
            g.note(line[:300])
    g.check('no walk failed', failed == 0, {'legs': legs, 'failed': failed})
