"""Esk, Hoth smoke test (Phase 3): fly Tatooine -> Corellia -> Hoth on the shuttles, look around the Scavenger Starport,
walk a short loop on the snow, and fly back to Corellia. Hoth is reached only from Corellia (travel.iff in
local_planets.tre). Coordinates: the landing points in planet_manager.lua; the outpost is MTG's snapshot at 0 -2000."""
import json, time
from ticket_pages import newest_ticket_list, answer_coupon

GROUP = 'Esk'
# planet, point (as /purchaseTicket wants it), landing spot
MOS_EISLEY = ('tatooine', 'Mos_Eisley_Starport', (3599.9, -4780.4))
CORONET = ('corellia', 'Coronet_Starport', (-66.8, -4711.3))
HOTH = ('hoth', 'Scavenger_Starport', (20.3, -1982.2))


def reach(bot, obj):
    """Walk to an object from locate(): indoors by its cell and cell-local position, outdoors by x/y."""
    if obj.get('cell'):
        spot = obj['local']
        return bot.walk(spot['x'], spot['y'], spot['z'], cell=obj['cell'], tries=6)
    return bot.walk(obj['x'], obj['y'], tries=6)


def ride(g, bot, origin, destination):
    """Buy a ticket at origin's starport and ride to destination. True when the bot is on the destination planet.
    Starport travel terminals stand inside the terminal building, so they are found with the server's search
    (locate), which sees into buildings; look/find only see the bot's own surroundings."""
    leg = f'{origin[0]} -> {destination[0]}'
    here = bot.status()
    if here.get('planet') != origin[0] or ((here['x'] - origin[2][0]) ** 2 + (here['y'] - origin[2][1]) ** 2) ** 0.5 > 40:
        bot.walk(*origin[2], tries=8)
    terminals = bot.locate('terminal_travel', 150, *origin[2])
    terminal = terminals[0] if terminals else None
    if not g.check(f'{leg}: travel terminal', terminal, terminal and
                   f"{terminal.get('template', terminal.get('name'))} {terminal['distance']:.0f} m from the pad"
                   + (f" (indoors, cell {terminal['cell']})" if terminal.get('cell') else '')):
        return False
    trip = reach(bot, terminal)
    at = bot.status()
    ref = terminal['local'] if terminal.get('cell') and at.get('cell') == terminal['cell'] else terminal  # status is cell-local indoors
    gap = ((at['x'] - ref['x']) ** 2 + (at['y'] - ref['y']) ** 2) ** 0.5
    if not g.check(f'{leg}: at the terminal (8 m to buy)', gap <= 8, f'{gap:.1f} m; ' + str(trip)[:160]):
        return False
    previous = {str(i.get('oid')) for i in bot.inventory().get('items', [])}
    tickets, texts = [], []
    for attempt in range(3):  # the first purchase after a galaxy start can fail silently (C7 finding)
        pages_before = bot.sui_pages().get('pages', [])
        bot.slash('purchaseTicket', f'{origin[0]} {origin[1]} {destination[0]} {destination[1]} single', wait=2)
        if answer_coupon(bot, pages_before):
            texts.append('answered the new-player travel coupon question (used the coupon)')
        for _ in range(5):
            texts += [e.get('text', '') or e.get('reason', '') for e in bot.inbox if e.get('event') in ('system', 'command_failed')]
            tickets = [i for i in bot.inventory().get('items', []) if 'ticket' in str(i.get('name')).lower() and i.get('oid') is not None
                       and str(i['oid']) not in previous]
            if tickets:
                break
            g.sleep(2)
        if tickets:
            break
    if not g.check(f'{leg}: buy a ticket', tickets, '; '.join(dict.fromkeys(t for t in texts if t))[:200]):
        return False
    collectors = bot.locate('collector', 150, *origin[2])
    collector = collectors[0] if collectors else None
    if not g.check(f'{leg}: ticket collector', collector, collector and f"{collector['distance']:.0f} m from the pad"):
        return False
    reach(bot, collector)
    arrived = None
    for attempt in range(8):  # shuttles land on a schedule
        before = bot.sui_pages().get('pages', [])
        bot.select(collector['oid'], 20, wait=3)
        page = newest_ticket_list(bot.sui_pages().get('pages', []), before)
        if page:
            bot.sui_respond(page['page_id'], 0, ['0'], wait=15)
        spot = bot.status()
        if spot.get('planet') == destination[0]:
            arrived = spot
            break
        g.note(f'{leg} boarding try {attempt + 1}: ' + '; '.join(bot.messages())[:160])
        g.sleep(45)
    return g.check(f'{leg}: ride the shuttle', arrived,
                   arrived and f"on {arrived.get('planet')} at {arrived.get('x'):.0f} {arrived.get('y'):.0f} z {arrived.get('z', 0):.1f}")


def run(g):
    esk = g['Esk']
    start = esk.status().get('planet')  # a run ends in Coronet, so the next one may start there
    if start == 'hoth':  # a halted run can leave Esk on Hoth
        ride(g, esk, HOTH, CORONET)
    if start == 'tatooine' and not ride(g, esk, MOS_EISLEY, CORONET):
        return
    if not g.check('start in Mos Eisley or Coronet', esk.status().get('planet') == 'corellia', start):
        return
    if not ride(g, esk, CORONET, HOTH):
        return
    spot = esk.status()
    g.check('on Hoth', spot.get('planet') == 'hoth', spot.get('planet'))
    # Hoth's snapshot has no terminal, collector or shuttle of its own: they should come from the outpost_starport
    # template's child objects (as on Bellum Gero's Hoth). Without them nobody can leave.
    port = {}
    for word in ('terminal', 'collector', 'transport', 'shuttle'):
        for o in esk.locate(word, 250):
            port[o['oid']] = f"{o.get('template', o.get('name', '?')).split('/')[-1]} {o['distance']:.0f} m"
    g.check('the starport has a travel terminal and a ticket collector',
            any('terminal_travel' in v for v in port.values()) and any('collector' in v for v in port.values()),
            sorted(port.values())[:20])
    ground = esk.request('height', 6, x=spot['x'], y=spot['y'])
    g.note(f"landing: bot z {spot.get('z', 0):.1f}, ground {ground.get('height', ground)}")
    # The pad and the loop read 0.0 (MTG's outpost sits at height 0). Heights further out show whether the server
    # really reads Hoth's terrain (hoth.trn from MTG) or defaults to flat ground.
    probes = {'500 m north': (20, -1482), '2 km east': (2000, -2000), '3 km west': (-3000, -2000),
              'ice caves': (-400, 2600), 'far north': (0, 6000)}
    relief = {k: round(esk.request('height', 6, x=x, y=y).get('z', 0), 1) for k, (x, y) in probes.items()}
    g.check('the terrain has relief (the server reads hoth.trn)', len(set(relief.values())) > 1, relief)
    # The pad is at 0 but the plain around it at ~45 m (14 Oct): a gentle slope or a crater wall? Heights every 50 m
    # out to 600 m in four directions; the steepest 50 m step is the number to watch (players and bots must climb it).
    profile, steepest = {}, (0, '')
    for name, (ux, uy) in (('north', (0, 1)), ('east', (1, 0)), ('south', (0, -1)), ('west', (-1, 0))):
        line = [round(esk.request('height', 6, x=20.3 + ux * d, y=-1982.2 + uy * d).get('z', 0), 1) for d in range(0, 601, 50)]
        profile[name] = line
        for i in range(1, len(line)):
            if abs(line[i] - line[i - 1]) > steepest[0]:
                steepest = (round(abs(line[i] - line[i - 1]), 1), f'{name} {(i - 1) * 50}-{i * 50} m')
    g.note(f'height profile from the pad, every 50 m: {profile}')
    g.check('no cliff around the outpost (no 50 m step rises more than 25 m)', steepest[0] <= 25, steepest)
    near = esk.look(radius=120, limit=80)
    names = sorted({o.get('name', '?') for o in near})
    g.check('the outpost is there (buildings or terminals nearby)', any('terminal' in v.lower() for v in port.values()) or any('terminal' in n.lower() or 'starport' in n.lower()
                                                                       or 'cloning' in n.lower() for n in names), names[:20])
    # a short loop on the snow around the outpost, reading the ground height as we go
    heights, arrivals = [], []
    for dx, dy in ((60, 0), (60, 60), (0, 60), (0, 0)):
        trip = esk.walk(spot['x'] + dx, spot['y'] + dy, tries=4)
        at = esk.status()
        heights.append(round(at.get('z', 0), 1))
        gap = ((at['x'] - spot['x'] - dx)**2 + (at['y'] - spot['y'] - dy)**2)**.5
        arrivals.append(isinstance(trip, dict) and bool(trip.get('arrived'))
                        and at.get('planet') == 'hoth' and not at.get('cell') and gap <= 8)
        if not isinstance(trip, dict) or not trip.get('arrived'):
            g.note(f'walk to +{dx} +{dy}: ' + str(trip)[:160])
    g.check('walk a loop on the snow', len(arrivals) == 4 and all(arrivals), {'arrivals': arrivals, 'heights': heights})
    creatures = [o for o in esk.look(radius=200, type='CREO', limit=80) if o.get('oid') != esk.oid]
    g.note(f'creatures within 200 m: {len(creatures)} ' + ', '.join(sorted({o.get("name", "?") for o in creatures}))[:200])
    ride(g, esk, HOTH, CORONET)
