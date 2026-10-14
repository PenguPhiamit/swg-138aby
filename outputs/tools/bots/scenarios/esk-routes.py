"""Esk, starter: three navmesh routes walked at the same time (into the cantina, to the starport, up to the
plateau), then all three back to the town square."""
GROUP = 'Esk'
CANTINA = dict(x=16.58, y=-14.21, z=-4.29, cell=1105883)  # Mos Eisley cantina, inside
STARPORT = (3546, -4790)
PLATEAU = (3830, -4530)  # about 175 m higher than town
SQUARE = (3528, -4800)


def run(g):
    esk, lira, tovan = g['Esk'], g['Lira'], g['Tovan']
    for bot in g.bots:
        spot = bot.status()
        if spot.get('planet') != 'tatooine':
            g.note(f'BLOCKED: {bot.first} is on {spot.get("planet")}; Mos Eisley routes require Tatooine. No movement issued.')
            return
    g.note('Tovan gear: ' + str(tovan.gear('basic'))[:160])
    trips = g.parallel(lambda: esk.walk(**CANTINA), lambda: lira.walk(*STARPORT), lambda: tovan.walk(*PLATEAU))
    for bot, label, trip in zip(g.bots, ('cantina (indoors)', 'starport', 'plateau'), trips):
        ok = isinstance(trip, dict) and trip.get('arrived')
        detail = trip if not isinstance(trip, dict) else {k: trip.get(k) for k in ('seconds', 'legs', 'points', 'cell', 'z', 'error')}
        g.check(f'{bot.first} reaches the {label}', ok, detail)

    inside = esk.look(radius=40, type='CREO')
    g.note(f'cantina: Esk sees {len(inside)} creatures inside, e.g. ' + ', '.join(o['name'] for o in inside[:4]))
    top = tovan.status()
    g.check('Tovan is up on the plateau (z > 150)', top.get('z', 0) > 150, f"z {top.get('z')}")

    back = g.parallel(*[lambda b=b, i=i: b.walk(SQUARE[0] + 3 * i, SQUARE[1]) for i, b in enumerate(g.bots)])
    g.check('all three back in the square', all(isinstance(t, dict) and t.get('arrived') for t in back),
            [(b.first, t.get('seconds') if isinstance(t, dict) else str(t)) for b, t in zip(g.bots, back)])
