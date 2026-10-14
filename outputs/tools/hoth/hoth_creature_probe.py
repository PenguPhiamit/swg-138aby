"""Hoth creatures slice: does the world spawner put Bellum's Hoth creatures around a player? (Claude's server test.)

    squad.py run /mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/tools/hoth/hoth_creature_probe.py

Observation only: Esk flies Coronet -> Hoth (reusing esk-hoth.py's ride(); that scenario is ChatGPT's and is not
changed), walks out of the outpost's no-spawn circle (200 m) on the gentle south side, looks around at a few stops,
and flies back. No attacks. A level 1 bot among level 62-115 creatures can die; that is recorded, not hidden.
The creature names are Bellum's customName values ("a wampa", "a Hoth tauntaun", ...), so any of them seen near the
outpost proves the ported templates, lairs and world-spawner region work together.
"""
import importlib.util
import json
from pathlib import Path

GROUP = 'Esk'
_spec = importlib.util.spec_from_file_location('esk_hoth_rides', Path(__file__).resolve().parents[1] / 'bots/scenarios/esk-hoth.py')
rides = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(rides)

PAD = (20.3, -1982.2)
# South of the pad the ground rises gently (8.7 m at 250 m, 16 m at 300 m; hoth-port-log.md, 14 Oct 02:20).
STOPS = [(20, -2240), (20, -2330), (120, -2330), (-80, -2330), (20, -2240)]
HOTH_NAMES = ('wampa', 'tauntaun', 'mynock', 'probe droid', 'snowtrooper', 'snow soldier', 'snow sergeant',
              'scavenger', 'salvage technician')


def alive(bot):
    s = bot.status()
    s['posture'] = s.get('me', {}).get('posture')  # status keeps posture under "me" (14 Oct: read from the top level, so a dead Esk walked on)
    return s['posture'] not in ('dead', 'incapacitated') and s.get('planet') == 'hoth', s


def newest_ticket_list(bot):
    """ride() answers the last SUI page that mentions 'ticket', but the bot keeps every page it was sent, so that can be
    an old ticket list or the terminal's 'purchase complete' box (14 Oct: ten stale lists after a few tries). Show it
    only the newest collector list (pages with the msgSelected callback). Local to this probe; esk-hoth.py unchanged."""
    original = bot.sui_pages

    def pages():
        reply = original()
        lists = sorted((p for p in reply.get('pages', []) if 'msgSelected' in json.dumps(p)), key=lambda p: p.get('page_id', 0))
        return {**reply, 'pages': lists[-1:]}
    bot.sui_pages = pages


def run(g):
    esk = g['Esk']
    newest_ticket_list(esk)
    start = esk.status().get('planet')
    if start == 'tatooine' and not rides.ride(g, esk, rides.MOS_EISLEY, rides.CORONET):
        return
    if start == 'hoth':
        rides.ride(g, esk, rides.HOTH, rides.CORONET)
    if not g.check('start at Coronet', esk.status().get('planet') == 'corellia', esk.status().get('planet')):
        return
    if not rides.ride(g, esk, rides.CORONET, rides.HOTH):
        return
    seen = {}
    for x, y in STOPS:
        trip = esk.walk(x, y, tries=4)
        ok, s = alive(esk)
        if not ok:
            g.note(f'Esk is {s.get("posture")} on {s.get("planet")} at {s.get("x", 0):.0f} {s.get("y", 0):.0f}; stopping the walk')
            break
        for wait in range(3):  # the spawner reacts to a moving player; give it a little time at each stop
            for o in esk.look(radius=256, type='CREO', limit=120):
                name = str(o.get('name', '?'))
                if o.get('oid') != esk.oid and any(k in name.lower() for k in HOTH_NAMES):
                    seen.setdefault(name, set()).add(o.get('oid'))
            g.sleep(15)
        g.note(f'stop {x:.0f} {y:.0f} ({((x - PAD[0]) ** 2 + (y - PAD[1]) ** 2) ** 0.5:.0f} m from the pad): '
               f'{ {n: len(v) for n, v in seen.items()} }; walk {str(trip)[:80]}')
    counts = {n: len(v) for n, v in sorted(seen.items())}
    g.check('Bellum Hoth creatures spawn outside the outpost (world spawner)', bool(counts), counts)
    ok, s = alive(esk)
    if ok:
        esk.walk(*PAD, tries=6)
        rides.ride(g, esk, rides.HOTH, rides.CORONET)
    else:
        g.note('Esk did not survive the walk; left on Hoth for the next run to clone/recover')
