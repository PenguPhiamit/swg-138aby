"""Aurek, starter: walk to the sevorrt plateau north-east of Mos Eisley, fight one creature as a group,
check the kill, XP and everyone's health afterwards, then try a medic heal."""
GROUP = 'Aurek'
PLATEAU = (3830, -4520)
TOUGH = ('greater', 'giant', 'ancient', 'enraged', 'bull', 'matriarch', 'patriarch', 'king', 'queen', 'elder')
SEARCH = [(150, 0), (150, 150), (0, 150), (-150, 150)]  # more of the plateau and the desert past it
EASY = ('kreetle', 'rockmite', 'mound_mite', 'worrt', 'rill', 'scurrier', 'womprat', 'sevorrt')  # weakest first


def run(g):
    aurek, jesh, tamsin = g['Aurek'], g['Jesh'], g['Tamsin']
    for bot in g.bots:  # Aurek is the world-boss group: composite armor, T21/battleaxe, stimpacks
        g.note(f'{bot.first} gear: ' + str(bot.gear('boss'))[:160])

    trips = g.parallel(*[lambda b=b, i=i: b.walk(PLATEAU[0] + 4 * i, PLATEAU[1]) for i, b in enumerate(g.bots)])
    g.check('all three reach the plateau', all(isinstance(t, dict) and t.get('arrived') for t in trips),
            [(b.first, t.get('seconds') if isinstance(t, dict) else str(t)) for b, t in zip(g.bots, trips)])

    def wild(o):  # an ordinary creature, not an NPC, droid, player or a big variant
        name = str(o.get('name', ''))
        return (name.startswith('@mob/creature_names:') and o.get('posture') == 'upright'
                and not any(word in name for word in TOUGH))

    found = []
    for dx, dy in [(0, 0)] + SEARCH:  # creatures spawn around players over time; look in a few places
        if (dx, dy):
            g.parallel(*[lambda b=b, i=i: b.walk(PLATEAU[0] + dx + 4 * i, PLATEAU[1] + dy) for i, b in enumerate(g.bots)])
        found = [o for o in aurek.look(100, 'CREO', 400) if wild(o)]
        if found:
            break
    found.sort(key=lambda o: next((i for i, w in enumerate(EASY) if w in o['name']), len(EASY)))
    g.note('creatures in range: ' + ', '.join(sorted({o['name'].split(':')[-1] for o in found})))
    prey = found[0] if found else None
    if not g.check('a creature in range', prey, prey and f"{prey['name']} at {prey['distance']} m"):
        return

    fights = g.parallel(*[lambda b=b: b.fight(prey['oid'], 90) for b in g.bots])
    results = [f.get('result') if isinstance(f, dict) else str(f) for f in fights]
    g.check('the creature goes down', any('target' in str(r) for r in results), results)

    xp = [m for b in g.bots for m in b.messages() if 'xp' in m.lower() or 'experience' in m.lower()]
    g.check('combat XP message', xp, xp[:3])

    for bot in g.bots:
        me = bot.status().get('me', {})
        g.note(f"{bot.first}: {me.get('posture')} H{me.get('ham', {}).get('health')}/{me.get('max_ham', {}).get('health')}")

    events = tamsin.slash('healdamage', target=aurek.oid, wait=3)
    g.note('Tamsin /healDamage on Aurek: ' + '; '.join(e.get('text', e.get('event', '')) for e in events
                                                        if e.get('event') in ('system', 'command_failed'))[:300])
