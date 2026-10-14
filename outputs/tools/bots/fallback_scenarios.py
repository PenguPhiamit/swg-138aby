"""Bounded observational probes, shared by fallback scenarios. Test galaxy only."""
import math


def recover_home(g, ride=None):
    """Return every stranded member by ordinary shuttles; unknown planets stay blocked.

    Travel is checkpointed by the body API/run control. No teleport or exploration.
    Re-read position after each leg: a failed ride must never start the next one.
    """
    if ride is None:
        import importlib.util
        from pathlib import Path
        path = Path(__file__).parent / 'scenarios/esk-hoth.py'
        spec = importlib.util.spec_from_file_location('fallback_home_travel', path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        ride = module.ride
    eisley = ('tatooine', 'Mos_Eisley_Starport', (3599.9, -4780.4))
    coronet = ('corellia', 'Coronet_Starport', (-66.8, -4711.3))
    hoth = ('hoth', 'Scavenger_Starport', (20.3, -1982.2))

    def member(bot):
        g.checkpoint()
        planet = bot.status().get('planet')
        if planet == 'tatooine':
            return True
        if planet not in ('hoth', 'corellia'):
            g.note(f'BLOCKED: {bot.first} recovery has no verified home route from {planet!r}')
            return False
        for origin, destination in ((hoth, coronet), (coronet, eisley)):
            if bot.status().get('planet') != origin[0]:
                continue
            g.checkpoint()
            if not ride(g, bot, origin, destination):
                g.note(f'BLOCKED: {bot.first} return-home leg {origin[0]} -> {destination[0]} failed')
                return False
            if bot.status().get('planet') != destination[0]:
                g.note(f'BLOCKED: {bot.first} return-home arrival was not confirmed')
                return False
        return g.check(f'{bot.first}: recovered to Tatooine', bot.status().get('planet') == 'tatooine')

    results = g.parallel(*[lambda bot=bot: member(bot) for bot in g.bots])
    return all(result is True for result in results)


def outdoor(g):
    bot = g.leader
    s = bot.status()
    if s.get('planet') != 'tatooine' or s.get('cell'):
        g.note('BLOCKED: fallback requires outdoor Tatooine; no automatic Hoth exploration')
        return None, s
    if math.hypot(s.get('x', 0) - 3528, s.get('y', 0) + 4804) > 250:
        g.note('BLOCKED: fallback is restricted to mapped Mos Eisley centre')
        return None, s
    return bot, s


def grid(g):
    bot, s = outdoor(g)
    if bot is None:
        return
    x, y = s['x'], s['y']
    for dx, dy in ((8, 0), (8, 8), (0, 8), (0, 0)):
        g.checkpoint()
        trip = bot.move(x + dx, y + dy, timeout=20)
        actual = bot.status()
        if actual.get('planet') != s['planet'] or actual.get('cell'):
            g.note('BLOCKED: scene changed during fallback grid; stopped')
            return
        height = bot.request('height', 6, x=x + dx, y=y + dy)
        arrived = bool(trip.get('arrived')) and math.hypot(actual['x'] - x - dx, actual['y'] - y - dy) <= 2
        g.check(f'grid {dx},{dy}: arrival', arrived, dict(trip=trip, actual=actual, height=height))
        g.note(f'GRID: target={x+dx:.1f},{y+dy:.1f}; z={actual.get("z")}; server_z={height.get("z")}; '
               f'corrections={trip.get("corrections", "not exposed")}; real-client comparison untested')
        if not arrived or actual.get('me', {}).get('posture') in ('dead', 'incapacitated', 13, 14):
            return


def census(g):
    bot = g.leader
    s = bot.status()
    objects = bot.look(radius=100, type='CREO', limit=120)
    counts = {}
    for obj in objects:
        name = str(obj.get('name', '?'))
        counts[name] = counts.get(name, 0) + 1
    g.check('spawn census reply has a scene', bool(s.get('planet')), s.get('planet'))
    g.note(f'CENSUS: planet={s.get("planet")}; at={s.get("x")},{s.get("y")}; names={counts}; '
           'stationary visible-object sample, not total server population; no staff commands')


def reach(g):
    bot, s = outdoor(g)
    if bot is None:
        return
    # Rotate small samples by the group's run log count rather than revisiting only the nearest bank.
    words = ('terminal_bank', 'terminal_bazaar', 'terminal_mission', 'terminal_travel', 'trainer')
    start = int(g.started // 300) % len(words)
    for word in (words[start], words[(start + 1) % len(words)]):
        found = bot.locate(word, 120)
        if not found:
            g.note(f'BLOCKED: no {word} within local reachability sample')
            continue
        obj = found[0]
        point = obj.get('local', obj)
        result = bot.move(point['x'], point['y'], point.get('z'), obj.get('cell'), timeout=30)
        at = bot.status()
        gap = math.hypot(at['x'] - point['x'], at['y'] - point['y'])
        close = at.get('planet') == s['planet'] and (at.get('cell') or 0) == (obj.get('cell') or 0) and gap <= 6
        g.check(f'{word}: reachable', close, dict(result=result, gap=gap, cell=at.get('cell')))
        if not close:
            return
        menu = bot.radial(obj['oid'])
        g.check(f'{word}: radial opens', bool(menu.get('items')), menu)
        # Do not choose a transaction/training option just to prove it is present.
        g.note(f'REACH: {word} radial observed; service transaction not exercised')
        if at.get('cell'):
            back = bot.move(s['x'], s['y'], timeout=30)
            if not back.get('arrived'):
                g.note('BLOCKED: could not return outdoors after reachability probe')
                return


def travel(g):
    bot, s = outdoor(g)
    if bot is None:
        return
    import importlib.util
    from pathlib import Path
    path = Path(__file__).parent / 'scenarios/cresh-travel.py'
    spec = importlib.util.spec_from_file_location('fallback_travel', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.travel(g, bot)


def crafting(g):
    g.check('crafting inventory observable', 'items' in g.leader.inventory())
    g.note('BLOCKED: full crafting session/ingredient/assembly body API unavailable; no crafting success claimed')
