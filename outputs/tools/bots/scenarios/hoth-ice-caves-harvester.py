"""Job list item 9 (Claude, 18 Oct 2026; owner 10:11 AM: harvesters in the Hoth ice caves; 11:20 AM: generators too):
may harvester and power generator deeds go in the ice caves no-build circle while everything else stays refused?
Needs dev `e56154bb` (the HARVESTERAREA flag and `/agentgear structures`).

One Esk bot takes the structures kit (an ore harvester, a wind generator and an item factory deed), jumps to Hoth and
places, east of the owner's spot by Goke (-224, 2441) and inside the 450 m ice caves circle:
1. the harvester at -194, 2441: expect placed;
2. the generator at -164, 2441: expect placed;
3. the factory at -124, 2441: expect "Building is not permitted here";
then a second harvester deed inside the Echo Base circle (-5113, 5097, 750 m): expect refused.
The placed harvester and generator stay on the test galaxy at the spots in the log; the owner's own spot is left free."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import escort  # noqa: E402

GROUP = 'Esk'
FOCUS = ('Item 9: harvesters and generators may be placed in the Hoth ice caves circle; a factory, and anything at '
         'Echo Base, may not')

KINDS = ('harvester', 'generator', 'factory')
SPOTS = {'harvester': (-194, 2441), 'generator': (-164, 2441), 'factory': (-124, 2441)}
ECHO_SPOT = (-4700, 5300)
NOT_PERMITTED = 'not_permitted'


def kit(bot):
    bot.slash('agentGear', 'structures', wait=0)
    answer = bot.wait_for(lambda e: str(e.get('text', '')).startswith('[agentgear]'), 8)
    items = bot.inventory().get('items', [])
    have = {k: next((i for i in items if k in (str(i.get('name')) + str(i.get('template'))).lower()), None) for k in KINDS}
    return answer, have


def place(bot, deed, x, y):
    """/placestructure <deed> x y angle; returns the system messages of the next 20 s and whether the deed is gone."""
    bot.slash('placestructure', f'{deed["oid"]} {x} {y} 0', wait=0)
    events = bot.idle(20)
    texts = [str(e.get('text', '')) for e in events if e.get('event') == 'system']
    gone = all(i.get('oid') != deed['oid'] for i in bot.inventory().get('items', []))
    return texts, gone


def run(g):
    bot = g.bots[0]
    answer, have = kit(bot)
    g.note(f'structures kit: {answer and answer.get("text")}')
    if not g.check('the bot holds harvester, generator and factory deeds', all(have.values()), str(have)[:300]):
        return

    escort.goto(bot, 'hoth', *SPOTS['harvester'])
    st = bot.status()
    g.note(f'at {st.get("planet")} {st.get("x")}, {st.get("y")}')
    for kind in KINDS:
        texts, gone = place(bot, have[kind], *SPOTS[kind])
        g.note(f'{kind} at {SPOTS[kind]}: {texts[:6]}')
        refused = any(NOT_PERMITTED in t for t in texts)
        if kind == 'factory':
            g.check('ice caves: the factory deed is refused with "not permitted"', refused and not gone, f'deed gone {gone}')
        else:
            g.check(f'ice caves: the {kind} deed is accepted (no "not permitted", deed used)', gone and not refused,
                    f'deed gone {gone}')
    site = [o for o in bot.look(128, '', 200) if any(w in str(o.get('name', '')).lower()
                                                      for w in ('harvester', 'generator', 'construction', 'mining'))]
    g.note('structures near the spots: ' + '; '.join(f'{o.get("name")} {o.get("oid")} {o.get("x")},{o.get("y")}'
                                                     for o in site[:8]))

    _, again = kit(bot)   # a fresh harvester deed: Echo Base must refuse even a harvester
    probe = again['harvester']
    if not g.check('a second harvester deed for the Echo Base check', probe is not None):
        return
    escort.goto(bot, 'hoth', *ECHO_SPOT)
    texts, gone = place(bot, probe, *ECHO_SPOT)
    g.note(f'harvester at Echo Base {ECHO_SPOT}: {texts[:6]}')
    g.check('Echo Base circle: the harvester deed is refused with "not permitted"',
            not gone and any(NOT_PERMITTED in t for t in texts), f'deed gone {gone}')
