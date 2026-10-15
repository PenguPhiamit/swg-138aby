"""Besh, gatherers with a guard. Each gathering type is one routine (a "macro") that any scenario can reuse:

  guard_sweep(g, guard, spot)     Varo clears ordinary creatures within 40 m before anyone kneels; returns the kills
  harvest(g, bot, corpse, kind)   one harvest choice per fresh kill (scout)
  survey_and_sample(g, bot, kind) any survey tool the bot carries: mineral, liquid, and chemical/flora/gas/
                                  moisture/wind/solar once crafted; surveys, then takes a core sample of the best
  forage(g, bot)                  scout foraging
  relog_keeps(g, bot)             log out and back in; is every item (resource containers too) still there?

Missing skills show up as BLOCKED notes ("missing ability"): train the skill, then run again.

Server rules (Agent/local-research/survey-sample/report.md, 15 Oct): the organic survey tool has toolType 0 on this
server and can never list anything (flora needs the lumber tool), so it is skipped. A tool lists only spawns of its
class that are in shift on this planet: an empty list for gas, moisture, wind or solar is server state, not a fault.
"liquid" is the chemical tool. A survey costs about 100 mind, and running low gives survey_mind (no results).
"""
import json


def resource_units(reply):
    return {str(i['oid']): i['units'] for i in reply.get('items', [])
            if i.get('oid') is not None and type(i.get('units')) is int and i['units'] >= 0}


def received_units(before, after):
    old, new = resource_units(before), resource_units(after)
    if not new:
        return None
    return sum(max(0, quantity - old.get(oid, 0)) for oid, quantity in new.items())


def check_receipt(g, label, before, after):
    gain = received_units(before, after)
    if gain is None:
        g.note('BLOCKED: ' + label + ': numeric resource units unavailable')
    else:
        g.check(label, gain > 0, {'units_received': gain})
    return gain

GROUP = 'Besh'
FIELD = (3760, -4600)  # open ground below the plateau, outside Mos Eisley
TOUGH = ('greater', 'giant', 'ancient', 'enraged', 'bull', 'matriarch', 'patriarch', 'king', 'queen', 'elder')


def missing_ability(events):
    return any(e.get('event') == 'command_failed' and e.get('error') == 2 for e in events)


def guard_sweep(g, guard, spot, radius=40, most=2):
    def wild(o):
        name = str(o.get('name', ''))
        dx, dy = o['x'] - spot[0], o['y'] - spot[1]
        return (name.startswith('@mob/creature_names:') and o.get('posture') == 'upright'
                and not any(w in name for w in TOUGH) and (dx * dx + dy * dy) ** 0.5 <= radius)

    kills = []
    for _ in range(most):
        prey = next((o for o in guard.look(radius + 30, 'CREO', 400) if wild(o)), None)
        if prey is None:
            break
        result = guard.fight(prey['oid'], 90)
        g.note(f"{guard.first} vs {prey['name'].split(':')[-1]}: {result.get('result')}")
        if result.get('result') == 'target dead':
            kills.append(prey)
        if guard.posture() != 'upright':
            g.note(f'{guard.first} went down; gatherers carry on unguarded')
            break
    g.check(f'{guard.first} guards the field', guard.posture() == 'upright', f'{len(kills)} kills')
    return kills


def harvest(g, bot, corpse, kind='meat'):
    if kind not in ('meat', 'hide', 'bone'):
        raise ValueError('unknown harvest kind')
    if not bot.go(corpse).get('arrived'):
        g.note('BLOCKED: cannot reach fresh corpse for harvesting')
        return None
    before = bot.inventory()
    events = bot.slash('harvestcorpse', kind, target=corpse['oid'], wait=3)
    if missing_ability(events):
        g.note(f'BLOCKED: {bot.first} lacks the harvesting ability (train it at a scout trainer)')
        return None
    return check_receipt(g, f'{bot.first} harvests {kind}', before, bot.inventory())


ALWAYS_SPAWNED = ('mineral', 'liquid')  # ore and chemical spawns are always in shift; other classes come and go
SURVEY_MIND = 110                          # a survey costs 100 - focus/15 mind


def mind(bot):
    return ((bot.status().get('me') or {}).get('ham') or {}).get('mind')


def survey_and_sample(g, bot, kind):
    if kind == 'organic':
        g.note(f'{bot.first}: organic survey tool skipped (toolType 0 on this server; it lists nothing)')
        return None
    tool = next((i for i in bot.inventory().get('items', []) if f'survey_tool_{kind}' in str(i.get('name'))), None)
    if tool is None:
        return None
    bot.select(tool['oid'], 20, wait=0)
    found = bot.wait_for('"survey_resources"', 4)
    if not found:  # the first use asks for a survey range (a list pop-up; skip the helper droid's quest box)
        pages = [p for p in bot.sui_pages().get('pages', []) if 'dataList' in json.dumps(p)]
        if pages:
            bot.sui_respond(pages[-1]['page_id'], 0, ['0'], wait=2)
            bot.select(tool['oid'], 20, wait=0)
            found = bot.wait_for('"survey_resources"', 10)
    if not found:
        g.note(f'BLOCKED: {bot.first} {kind} survey: no resource list arrived (range pop-up not answered?)')
        return None
    names = [r['name'] for r in found.get('resources', [])]
    if not names and kind not in ALWAYS_SPAWNED:
        g.note(f'{bot.first} {kind} survey: empty list, no {kind} spawn in shift on this planet now (server state)')
        return None
    if not g.check(f'{bot.first} {kind} survey lists resources', names, names[:6]):
        return None
    best, tired = (None, 0), False
    for name in names[:5]:
        left = mind(bot)
        if isinstance(left, int) and left < SURVEY_MIND:
            g.note(f'{bot.first} {kind}: mind {left} too low for another survey; stopped after the ones done')
            tired = True
            break
        bot.slash('requestSurvey', name, wait=0)
        top = ((bot.wait_for('"survey_results"', 12) or {}).get('best') or {}).get('percent', 0)
        if top > best[1]:
            best = (name, top)
        bot.idle(4)  # survey cooldown
    if best[0] is None and tired:
        g.note(f'BLOCKED: {bot.first} {kind}: out of mind before any survey found a concentration')
        return None
    if not g.check(f'{bot.first} {kind} survey finds a concentration', best[0], best):
        return None
    before = bot.inventory()
    bot.slash('requestCoreSample', best[0], wait=0)
    located = bot.wait_for(lambda e: 'sample' in str(e.get('text', '')).lower(), 40)
    bot.idle(15)
    after = bot.inventory()
    check_receipt(g, f'{bot.first} {kind} core sample of {best[0]}', before, after)
    bot.slash('stand', wait=1)
    return best[0]


def forage(g, bot):
    bot.idle(3)  # standing still
    events = bot.slash('forage', wait=12)
    if missing_ability(events):
        g.note(f'BLOCKED: {bot.first} lacks the forage ability (train it at a scout trainer)')
        return
    texts = [e.get('text', '') for e in events if e.get('event') == 'system']
    g.check(f'{bot.first} forages', texts, texts[:3])


def relog_keeps(g, bot):
    """Log out and back in; every inventory item (by object id) should still be there."""
    def items():
        return {i['oid']: str(i.get('name')) for i in bot.inventory().get('items', [])}

    before = items()
    bot.stop()
    result = bot.start()
    after = items() if result == 'ready' else {}
    lost = [before[o] for o in before if o not in after]
    g.check(f'{bot.first} keeps all {len(before)} items through a relog', result == 'ready' and not lost,
            f'{result}; lost {lost[:5]}')


def run(g):
    besh, dova, pell, varo = g['Besh'], g['Dova'], g['Pell'], g['Varo']
    g.note('Varo gear: ' + str(varo.gear('basic'))[:160])
    g.parallel(*[lambda b=b, i=i: b.walk(FIELD[0] + 5 * i, FIELD[1]) for i, b in enumerate(g.bots)])

    kills = guard_sweep(g, varo, FIELD)
    jobs = [lambda: survey_and_sample(g, besh, 'mineral'), lambda: survey_and_sample(g, dova, 'liquid')]
    jobs.append(lambda: [harvest(g, pell, k, ('meat', 'hide', 'bone')[i % 3])
                         for i, k in enumerate(kills)] if kills else forage(g, pell))
    if len(kills) < 3:
        g.note('BLOCKED: full meat/hide/bone coverage needs three separate fresh corpses')
    g.parallel(*jobs)
    if kills:
        forage(g, pell)

    for bot in (besh, dova):  # any other survey tools they picked up (crafted or looted)
        kinds = {str(i.get('name')).split('survey_tool_')[-1] for i in bot.inventory().get('items', [])
                 if 'survey_tool_' in str(i.get('name'))} - {'mineral', 'liquid'}
        for kind in sorted(kinds):
            survey_and_sample(g, bot, kind)

    relog_keeps(g, besh)
