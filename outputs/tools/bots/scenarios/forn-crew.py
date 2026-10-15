"""Forn, the dungeon crew (owner, 15 Oct: "give me a crew and we can test their combat more and their movement and
mapping"). Round 1, near Mos Eisley, before any dungeon:

  1. Templates and gear. Each bot holds its template's master boxes (squad.py setup trains them from groups.json),
     wears composite armour with stimpacks (boss kit) and takes its role's weapon into its hands.
  2. Buffs. Mirren, the doctor, enhances everyone's health and action inside the hospital (any cell counts).
  3. Fights. Up to three group fights on the sevorrt plateau, one tier tougher each time: an ordinary creature, a
     big variant, then the toughest in sight. tools/bots/crew_combat.py drives them: real special attacks for the
     weapon in hand, ranged fighters at range, Forn's squad calls, Mirren healing whoever is lowest. Each fight
     records time to kill, specials sent and refused, lowest health and who went down.
  4. Clean up: anyone down recovers, then /agentgear afflict restore clears what the fights left.

Movement is in the tracker log (Bot-reports/tracker/), with a label per bot saying what it is doing.
"""
import importlib.util
from pathlib import Path

GROUP = 'Forn'
PLATEAU = (3830, -4520)
SEARCH = [(0, 0), (150, 0), (0, 150), (-150, 150)]
TOUGH = ('greater', 'giant', 'ancient', 'enraged', 'bull', 'matriarch', 'patriarch', 'king', 'queen', 'elder')
TEMPLATE = {
    'Forn': ['outdoors_squadleader_master', 'combat_rifleman_master'],
    'Brask': ['combat_1hsword_master', 'combat_polearm_master', 'science_medic_master'],
    'Ressa': ['combat_unarmed_master', 'combat_1hsword_master', 'science_medic_master'],
    'Dask': ['combat_commando_master', 'combat_rifleman_master'],
    'Mirren': ['science_doctor_master', 'science_combatmedic_master'],
}
KITS = {'Brask': ['lance', 'onehand'], 'Ressa': ['knuckler', 'onehand'], 'Dask': ['heavy'], 'Mirren': ['medicine2', 'support']}
HOLD = {'Brask': 'lance_vibrolance', 'Ressa': 'vibroknuckler', 'Dask': 'heavy_acid_beam', 'Forn': 'rifle_t21', 'Mirren': 'rifle_t21'}
ROLES = {
    'Forn': {'weapon': 'rifle', 'ranged': True, 'opener': ['steadyaim', 'volleyFire']},
    'Brask': {'weapon': 'polearm'},
    'Ressa': {'weapon': 'unarmed'},
    'Dask': {'weapon': 'special heavy (flame/acid/lightning beam)', 'ranged': True, 'stand': 14, 'reach': 30},
    'Mirren': {'weapon': 'rifle', 'ranged': True, 'healer': True},
}

_spec = importlib.util.spec_from_file_location('crew_combat', Path(__file__).resolve().parents[1] / 'crew_combat.py')
crew_combat = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(crew_combat)


def hold(bot, token):
    """Put the first carried item whose name contains token into the hands (transferItemWeapon, as class-check.py)."""
    bot.status()
    item = next((i for i in bot.inventory().get('items', []) if token in str(i.get('name'))), None)
    if item is None:
        return False, 'missing ' + token
    if item.get('parent') == bot.oid:
        return True, 'already in hand'
    bot.slash('transferItemWeapon', f'{bot.oid} 4 0 0 0', target=item['oid'], wait=1)
    now = next((i for i in bot.inventory().get('items', []) if i.get('oid') == item['oid']), {})
    return now.get('parent') == bot.oid, now.get('name')


def ready(g):
    for bot in g.bots:
        skills = bot.profession('list').get('skills', [])
        missing = [box for box in TEMPLATE[bot.first] if box not in skills]
        g.check(f'{bot.first} holds the template', not missing, missing or TEMPLATE[bot.first])
        bot.doing('gearing up')
        g.note(f'{bot.first} boss kit: ' + str(bot.gear('boss'))[:120])
        for kit in KITS.get(bot.first, []):
            bot.slash('agentGear', kit, wait=0)
            bot.wait_for(lambda e: str(e.get('text', '')).startswith('[agentgear]'), 8)
        if bot.first in HOLD:
            ok, what = hold(bot, HOLD[bot.first])
            g.check(f'{bot.first} holds {HOLD[bot.first]}', ok, what)


def buffs(g):
    mirren = g['Mirren']
    hospitals = mirren.locate('hospital', radius=2000)
    rooms = [r for text in ('object/mobile', 'object/tangible') if hospitals
             for r in mirren.locate(text, radius=40, x=hospitals[0]['x'], y=hospitals[0]['y'])
             if r.get('cell') and r.get('local') and r.get('building') == hospitals[0].get('oid')]
    if not rooms:
        g.note('BLOCKED: no hospital cell found; the crew fights unbuffed.')
        return
    room = rooms[0]
    local = room['local']
    for bot in g.bots:
        bot.doing('going to the hospital for buffs')
    trips = g.parallel(*[lambda b=b, i=i: b.walk(local['x'] + 1.0 + i, local['y'] + 1.0, local['z'], room['cell'], tries=3)
                         for i, b in enumerate(g.bots)])
    if not g.check('the crew walks into the hospital', all(isinstance(t, dict) and t.get('arrived') for t in trips),
                   [(b.first, t.get('arrived') if isinstance(t, dict) else str(t)) for b, t in zip(g.bots, trips)]):
        return
    gains = {}
    for bot in g.bots:
        if bot is mirren:
            continue
        for attribute in ('health', 'action'):
            before = bot.status().get('me', {}).get('max_ham', {}).get(attribute)
            mirren.slash('healenhance', attribute, target=bot.oid, wait=1)
            mirren.wait_for(lambda e: 'healing_response_59' in str(e.get('text', '')), 25)
            after = bot.status().get('me', {}).get('max_ham', {}).get(attribute)
            gains[f'{bot.first} {attribute}'] = (after - before) if isinstance(after, int) and isinstance(before, int) else None
    g.check('Mirren buffs the crew', all(v and v > 0 for v in gains.values()), gains)


def prey(g, tier):
    """The creature for this fight: tier 0 an ordinary one, 1 a big variant, 2 the toughest in sight."""
    forn = g['Forn']
    for dx, dy in SEARCH:
        if (dx, dy) != (0, 0):
            g.parallel(*[lambda b=b, i=i: b.walk(PLATEAU[0] + dx + 4 * i, PLATEAU[1] + dy) for i, b in enumerate(g.bots)])
        found = [o for o in forn.look(120, 'CREO', 400)
                 if str(o.get('name', '')).startswith('@mob/creature_names:') and o.get('posture') == 'upright']
        big = [o for o in found if any(w in o['name'] for w in TOUGH)]
        pick = (big or found) if tier else [o for o in found if o not in big]
        if pick:
            return sorted(pick, key=lambda o: o.get('distance', 999))[0]
    return None


def run(g):
    ready(g)
    buffs(g)
    for bot in g.bots:
        bot.doing('walking to the sevorrt plateau')
    trips = g.parallel(*[lambda b=b, i=i: b.walk(PLATEAU[0] + 4 * i, PLATEAU[1]) for i, b in enumerate(g.bots)])
    if not g.check('the crew reaches the plateau', all(isinstance(t, dict) and t.get('arrived') for t in trips),
                   [(b.first, t.get('seconds') if isinstance(t, dict) else str(t)) for b, t in zip(g.bots, trips)]):
        return
    for tier, label in enumerate(('an ordinary creature', 'a big variant', 'the toughest in sight')):
        target = prey(g, tier)
        if not g.check(f'fight {tier + 1}: {label} in range', target, target and f"{target['name']} {target.get('distance')} m"):
            break
        name = target['name'].split(':')[-1]
        for bot in g.bots:
            bot.doing(f'fight {tier + 1}: engaging {name}')
        record = crew_combat.fight(g, target['oid'], ROLES, seconds=180)
        down = [n for n, r in record['crew'].items() if r.get('end') in crew_combat.DOWN]
        g.check(f'fight {tier + 1}: the crew kills the {name}', 'target' in record['result'] and 'gone' not in record['result'],
                {'result': record['result'], 'seconds': record['seconds'], 'down': down})
        for first, rec in record['crew'].items():
            g.note(f"fight {tier + 1} {first}: sent {sum(rec['sent'].values())} ({len(rec['sent'])} kinds, rotation "
                   f"{rec.get('rotation')}), refused {sum(rec['refused'].values())}, lowest health {rec['lowest_health']}, "
                   f"heals {rec['heals']}, moves {rec['moves']}, end {rec['end']}; top refusals {list(rec['refused'])[:3]}")
        g.check(f'fight {tier + 1}: nobody goes down', not down, down)
        for bot in g.bots:
            if bot.posture() in crew_combat.DOWN:
                bot.recover()
            bot.slash('agentGear', 'afflict restore', wait=0)
            bot.wait_for(lambda e: str(e.get('text', '')).startswith('[agentgear]'), 8)
            bot.doing('resting after the fight')
        if down:
            break
    for bot in g.bots:
        g.note(f'{bot.first} after: {bot.posture()}')
        bot.doing('done')
