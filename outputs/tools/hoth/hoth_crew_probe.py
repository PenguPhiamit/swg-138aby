"""Hoth with a crew: Esk's group geared and trained like the world-boss crew (owner, 14 Oct: "give esk a crew similar
to the world boss crew"). Claude's server test.

    squad.py setup Esk     (applies the training in groups.json: Esk and Tovan fighters, Lira Doctor)
    squad.py run /mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/tools/hoth/hoth_crew_probe.py

All three revive if needed, take the boss kit (composite armor; T21 rifle / battleaxe; stimpacks for the medic), fly
to Hoth, walk the probe's stops south of the outpost together and fight whatever comes within reach, as a group.
Lira heals the most hurt after each fight. If anyone goes down the crew falls back to the pad, revives and flies home.
Bellum's Hoth creatures are level 62-115; these are trained, not levelled, so losses are expected and recorded.
"""
import importlib.util
from pathlib import Path

GROUP = 'Esk'
_spec = importlib.util.spec_from_file_location('hoth_probe', Path(__file__).resolve().parent / 'hoth_creature_probe.py')
probe = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(probe)
rides = probe.rides
STOPS = [(20, -2240), (60, -2300), (-40, -2300), (20, -2240)]
OFFSETS = {'Esk': (0, 0), 'Tovan': (4, 3), 'Lira': (-4, 6)}  # Lira a little behind the fighters
REACH = 30  # m: a creature this close is taken as a threat


def hp(bot):
    me = bot.status().get('me', {})
    return me.get('posture'), me.get('ham', {}).get('health', 0), me.get('max_ham', {}).get('health', 1)


def to_hoth(g, bot):
    planet = bot.status().get('planet')
    if planet == 'hoth':
        return True
    if planet == 'tatooine' and not rides.ride(g, bot, rides.MOS_EISLEY, rides.CORONET):
        return False
    return rides.ride(g, bot, rides.CORONET, rides.HOTH)


def run(g):
    crew = [g['Esk'], g['Tovan'], g['Lira']]
    lira = g['Lira']
    for bot in crew:
        probe.newest_ticket_list(bot)
        before, after = bot.recover()
        g.note(f'{bot.first}: {before} -> {after}; gear ' + str(bot.gear('boss'))[:120])
    arrived = g.parallel(*[lambda b=b: to_hoth(g, b) for b in crew])
    if not g.check('the whole crew is on Hoth', all(arrived), dict(zip([b.first for b in crew], arrived))):
        return
    seen, fights, downed = {}, [], []
    for x, y in STOPS:
        g.parallel(*[lambda b=b: b.walk(x + OFFSETS[b.first][0], y + OFFSETS[b.first][1], tries=4) for b in crew])
        for _ in range(3):
            near = []
            for o in crew[0].look(radius=256, type='CREO', limit=120):
                name = str(o.get('name', '?'))
                if any(k in name.lower() for k in probe.HOTH_NAMES):
                    seen.setdefault(name, set()).add(o.get('oid'))
                    if o.get('distance', 999) <= REACH and o.get('posture') not in ('dead', 'incapacitated'):
                        near.append(o)
            if near:
                target = min(near, key=lambda o: o.get('distance', 999))
                results = g.parallel(*[lambda b=b: b.fight(target['oid'], 60) for b in crew if b is not lira])
                fights.append((target.get('name'), [str(r)[:60] for r in results]))
                hurt = sorted((b for b in crew if hp(b)[0] == 'upright'), key=lambda b: hp(b)[1] / max(hp(b)[2], 1))
                if hurt and hp(lira)[0] == 'upright':
                    lira.slash('healdamage', target=hurt[0].oid, wait=3)
            downed = [b.first for b in crew if hp(b)[0] in ('incapacitated', 'dead')]
            if downed:
                break
            g.sleep(10)
        g.note(f'stop {x} {y}: seen { {n: len(v) for n, v in seen.items()} }; fights {len(fights)}; '
               + ', '.join(f'{b.first} {hp(b)[0]} {hp(b)[1]}/{hp(b)[2]}' for b in crew))
        if downed:
            g.note(f'down: {downed}; falling back to the pad')
            break
    for name, result in fights:
        g.note(f'fight vs {name}: {result}')
    g.check('Bellum Hoth creatures seen near the crew', bool(seen), {n: len(v) for n, v in seen.items()})
    g.check('crew survived the walk', not downed, downed or 'all upright')
    for bot in crew:
        bot.recover(wait=120)
    g.parallel(*[lambda b=b: b.walk(*probe.PAD, tries=6) for b in crew])
    for bot in crew:
        if probe.alive(bot)[0]:
            rides.ride(g, bot, rides.HOTH, rides.CORONET)
