"""Cresh, starter: Ilsa asks the big game hunter Rhea Tannor about the world bosses at the starport while Cresh
rides the shuttle Mos Eisley <-> Bestine and back (from whichever is nearer), and Kor looks for a mission terminal."""
import json, time
from ticket_pages import newest_ticket_list, answer_coupon

GROUP = 'Cresh'
STARPORT = (3546, -4790)                 # Rhea Tannor stands here
PROBES = [(3528, -4800), (3480, -4840), (3600, -4880), (3470, -4730), (3380, -4800)]


PORTS = {  # same-planet shuttle network; point names as /purchaseTicket wants them
    'Mos Eisley': {'at': (3416.7, -4648.1), 'point': 'Mos_Eisley_Shuttleport'},
    'Bestine': {'at': (-1098.5, -3563.5), 'point': 'Bestine_Shuttleport'},
}


def ride(g, bot, origin, destination):
    """Buy a ticket at origin's shuttleport and ride to destination. True when the bot arrives."""
    port, there = PORTS[origin], PORTS[destination]
    leg = f'{origin} -> {destination}'
    bot.walk(*port['at'], tries=6)
    terminal = bot.find('terminal_travel', radius=60, type='TANO') or bot.find(
        'travel', radius=60, type='TANO', where=lambda o: 'collector' not in o['name'])
    if not g.check(f'{leg}: travel terminal', terminal, terminal and f"{terminal['name']} {terminal['distance']} m"):
        return False
    bot.go(terminal)
    ticket_args = f"tatooine {port['point']} tatooine {there['point']} single"
    tickets, texts = [], []
    previous = {str(i.get('oid')) for i in bot.inventory().get('items', [])}
    for attempt in range(2):  # the answer can take a few seconds when the command queue is busy
        pages_before = bot.sui_pages().get('pages', [])
        bot.slash('purchaseTicket', ticket_args, wait=2)
        if answer_coupon(bot, pages_before):
            texts.append('answered the new-player travel coupon question (used the coupon)')
        for _ in range(5):
            texts += [e.get('text', '') or e.get('reason', '') for e in bot.inbox
                      if e.get('event') in ('system', 'command_failed') and 'World boss' not in str(e.get('text'))]
            tickets = [i for i in bot.inventory().get('items', []) if 'ticket' in str(i.get('name')).lower()
                       and i.get('oid') is not None and str(i['oid']) not in previous]
            if tickets:
                break
            g.sleep(2)
        if tickets:
            break
    if not g.check(f'{leg}: buy a ticket', tickets, '; '.join(dict.fromkeys(texts))[:200]):
        return False
    collector = bot.find('collector', radius=60, type='TANO')
    if not g.check(f'{leg}: ticket collector', collector):
        return False
    bot.go(collector)
    arrived = None
    for attempt in range(6):  # the shuttle lands on a schedule; keep trying for about six minutes
        before = bot.sui_pages().get('pages', [])
        bot.select(collector['oid'], 20, wait=3)
        page = newest_ticket_list(bot.sui_pages().get('pages', []), before)
        if page:
            bot.sui_respond(page['page_id'], 0, ['0'], wait=10)
        spot = bot.status()
        if spot.get('planet') == 'tatooine' and not spot.get('cell') and abs(spot.get('x', 0) - there['at'][0]) < 300 and abs(spot.get('y', 0) - there['at'][1]) < 300:
            arrived = spot
            break
        g.note(f'{leg} boarding try {attempt + 1}: ' + '; '.join(bot.messages())[:160])
        g.sleep(50)
    return g.check(f'{leg}: ride the shuttle', arrived, arrived and f"at {arrived.get('x'):.0f} {arrived.get('y'):.0f}")


def travel(g, cresh):
    """A round trip from the nearest shuttleport, so every round starts and ends at home (a one-way trip used to
    strand Cresh in Bestine, and the next round's long walk back got it killed in the desert)."""
    here = cresh.status()
    origin = min(PORTS, key=lambda k: (PORTS[k]['at'][0] - here.get('x', 0)) ** 2 + (PORTS[k]['at'][1] - here.get('y', 0)) ** 2)
    destination = next(k for k in PORTS if k != origin)
    if ride(g, cresh, origin, destination):
        ride(g, cresh, destination, origin)


def hunter(g, ilsa):
    ilsa.walk(*STARPORT)
    rhea = ilsa.find('Rhea Tannor', radius=64, type='CREO')
    if not g.check('Rhea Tannor is at the starport', rhea, rhea and f"{rhea['distance']} m"):
        return
    ilsa.go(rhea)
    ilsa.talk(rhea['oid'], wait=3)
    options = ilsa.wait_for('"conversation_options"', 5)
    said = [e.get('text', '') for e in ilsa.inbox if e.get('event') == 'npc_says']
    g.check('she talks', options or said, (said[:1], (options or {}).get('options')))
    if options and options.get('options'):
        ilsa.choose(0, wait=3)
        g.note('Rhea, first answer: ' + '; '.join(e.get('text', '') for e in ilsa.inbox if e.get('event') == 'npc_says')[:300])


def missions(g, kor):
    for x, y in PROBES:
        kor.walk(x, y)
        mission = kor.find('terminal_mission', radius=100, type='TANO') or kor.find('mission', radius=100, type='TANO')
        if mission:
            break
    if not g.check('mission terminal in town', mission, mission and f"{mission['name']} near {mission['x']:.0f} {mission['y']:.0f}"):
        return
    kor.go(mission)
    reply = kor.request('mission_list', 10, target=mission['oid'])
    g.check('mission list request accepted', reply.get('ok'), reply)
    g.note('mission list events: ' + str(sorted({e.get('event') for e in kor.idle(3)}))[:200])


def run(g):
    cresh, ilsa, kor = g['Cresh'], g['Ilsa'], g['Kor']
    g.parallel(lambda: travel(g, cresh), lambda: hunter(g, ilsa), lambda: missions(g, kor))
