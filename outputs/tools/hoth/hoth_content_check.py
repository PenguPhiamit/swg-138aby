"""Hoth content check (14 Oct, after the 09:27 test restart): does tonight's Hoth content exist in the game world?
Esk flies Tatooine -> Corellia -> Hoth (esk-hoth.py's ride), asks the server's object search (/agentpath find, zone-wide
around a point, into buildings too) for each piece, talks to the quest giver, and flies back to Corellia. One bot; the
rest of the Esk crew stays home. Ending in Coronet is deliberate: the next overnight round finds Esk off Tatooine, so
ChatGPT's C20 return-home fallback runs for real.

    wsl -d Debian -u swgemu -- python3 .../tools/bots/squad.py run .../tools/hoth/hoth_content_check.py --group Esk --no-fallback

Pieces (dev): ice caves c5f1ae06, area spawners 69eb77fe, camps de1b679a + 5eb140ce, missions and quest chain 92d99dba.
"""
import importlib.util
from pathlib import Path

GROUP = 'Esk'
_spec = importlib.util.spec_from_file_location(
    'esk_hoth', Path(__file__).resolve().parents[1] / 'bots' / 'scenarios' / 'esk-hoth.py')
esk_hoth = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(esk_hoth)

CAVES = {'cave_04_ice_s01': (-385, 2436), 'the other three ice caves': (-400, 2600)}
CAMPS = {  # site: (x, y, an NPC template that stands there)
    'Imperial forward camp': (2600, -3900, 'hoth_snowtrooper'),
    'Rebel forward camp': (-2800, 1200, 'hoth_rebel_snow'),
    "scavengers' camp": (-1400, -3300, 'hoth_scavenger'),
    "raiders' camp": (-1200, -3600, 'hoth_scavenger_raider'),
    'contested ground': (2400, 200, 'hoth_snow'),
    'salvage detail': (-100, -1960, 'hoth_imperial_salvage_tech'),
}
ZONES = {  # batch A area spawners: centre and radius
    'tauntaun plains west': (-3000, -1500, 1800), 'tauntaun plains east': (3000, -1200, 1500),
    'mynock fields south': (-2000, -4800, 1200), 'wampa flanks west': (-1800, 3200, 900),
    'wampa flanks south-east': (1200, 1500, 700), 'imperial zone east': (2500, -3500, 1200),
    'rebel zone north-west': (-2500, 1000, 1200), 'scavenger zone south-west': (-1500, -3200, 900),
}


def run(g):
    esk = g['Esk']
    start = esk.status().get('planet')
    if start == 'tatooine' and not esk_hoth.ride(g, esk, esk_hoth.MOS_EISLEY, esk_hoth.CORONET):
        return
    if start != 'hoth' and not esk_hoth.ride(g, esk, esk_hoth.CORONET, esk_hoth.HOTH):
        return
    if not g.check('on Hoth', esk.status().get('planet') == 'hoth', esk.status().get('planet')):
        return

    for name, (x, y) in CAVES.items():
        wampas = esk.locate('wampa', 300, x=x, y=y)
        inside = [o for o in wampas if o.get('cell')]
        g.check(f'wampas in {name}', len(inside) > 0, f'{len(inside)} inside cells, {len(wampas)} found')

    # The server's search matches template paths, name keys and displayed names, not Core3 mobile names
    # (09:43: "hoth_snowtrooper" found nothing). Count any creature (object/mobile/...) and the camp props.
    for name, (x, y, template) in CAMPS.items():
        npcs = esk.locate('object/mobile/', 40, x=x, y=y)
        props = esk.locate('object/static/structure/', 40, x=x, y=y)
        g.check(f'{name}: props at the camp', len(props) > 0, f'{len(props)} props')
        g.check(f'{name}: NPCs at the camp', len(npcs) > 0,
                f'{len(npcs)}: ' + ', '.join(sorted({o.get("name", "?") for o in npcs}))[:150] + f' (expected {template})')

    lairs = {}
    for name, (x, y, r) in ZONES.items():
        lairs[name] = len(esk.locate('lair', r, x=x, y=y))
    # A note, not a check: spawn areas fill around players, and Esk stands at the outpost, outside every zone.
    g.note(f'lairs found per batch A zone (search capped at 30; zones fill only near players): {lairs}')

    terminals = esk.locate('terminal_mission', 40, x=48, y=-1999)
    g.check('two mission terminals east of the starport', len(terminals) >= 2,
            [(round(t['x']), round(t['y'])) for t in terminals])

    vell = esk.locate('quartermaster', 30, x=44, y=-2010) or esk.locate('Vell', 30, x=44, y=-2010)
    if g.check('Quartermaster Vell stands at the outpost', bool(vell), vell[:1] if vell else None):
        walked = esk.walk(vell[0]['x'] + 2, vell[0]['y'])
        g.note(f'walked to Vell: {walked.get("arrived")}, {walked.get("seconds")} s')
        events = esk.talk(vell[0]['oid'], wait=4)
        texts = [str(e.get('text', '')) for e in events if e.get('text')]
        options = esk.status().get('conversation_options', [])
        g.check('Vell talks (quest conversation)', bool(texts or options), dict(texts=texts[:3], options=options[:4]))

    esk_hoth.ride(g, esk, esk_hoth.HOTH, esk_hoth.CORONET)
