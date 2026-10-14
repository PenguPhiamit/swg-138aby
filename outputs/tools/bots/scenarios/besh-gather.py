"""Besh, gatherers with a guard. Each gathering type is one routine (a "macro") that any scenario can reuse:

  guard_sweep(g, guard, spot)     Varo clears ordinary creatures within 40 m before anyone kneels; returns the kills
  harvest(g, bot, corpse)         meat, hide and bone from a fresh kill (scout)
  survey_and_sample(g, bot, kind) any survey tool the bot carries: mineral, liquid, and chemical/flora/gas/
                                  moisture/wind/solar once crafted; surveys, then takes a core sample of the best
  forage(g, bot)                  scout foraging
  relog_keeps(g, bot)             log out and back in; is every item (resource containers too) still there?

Missing skills show up as BLOCKED notes ("missing ability"): train the skill, then run again.
"""
import json

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
        if 'target' in str(result.get('result')):
            kills.append(prey)
        if guard.posture() != 'upright':
            g.note(f'{guard.first} went down; gatherers carry on unguarded')
            break
    g.check(f'{guard.first} guards the field', guard.posture() == 'upright', f'{len(kills)} kills')
    return kills


def harvest(g, bot, corpse):
    bot.go(corpse)
    got = {}
    for what in ('meat', 'hide', 'bone'):
        events = bot.slash('harvestcorpse', what, target=corpse['oid'], wait=3)
        if missing_ability(events):
            g.note(f'BLOCKED: {bot.first} lacks the harvesting ability (train it at a scout trainer)')
            return got
        got[what] = '; '.join(e.get('text', '') for e in events if e.get('event') == 'system')[:120]
    g.check(f'{bot.first} harvests {corpse["name"].split(":")[-1]}', any('harvest' in v.lower() for v in got.values()), got)
    return got


def survey_and_sample(g, bot, kind):
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
    names = [r['name'] for r in (found or {}).get('resources', [])]
    if not g.check(f'{bot.first} {kind} survey lists resources', names, names[:6]):
        return None
    best = (None, 0)
    for name in names[:5]:
        bot.slash('requestSurvey', name, wait=0)
        top = ((bot.wait_for('"survey_results"', 12) or {}).get('best') or {}).get('percent', 0)
        if top > best[1]:
            best = (name, top)
        bot.idle(4)  # survey cooldown
    if not g.check(f'{bot.first} {kind} survey finds a concentration', best[0], best):
        return None
    before = len(bot.inventory().get('items', []))
    bot.slash('requestCoreSample', best[0], wait=0)
    located = bot.wait_for(lambda e: 'sample' in str(e.get('text', '')).lower(), 40)
    bot.idle(15)
    after = len(bot.inventory().get('items', []))
    texts = '; '.join(bot.messages())[:200]
    g.check(f'{bot.first} {kind} core sample of {best[0]}', after > before or 'located' in str(located),
            f'inventory {before} -> {after}; {texts}')
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
    jobs.append(lambda: [harvest(g, pell, k) for k in kills] if kills else forage(g, pell))
    g.parallel(*jobs)
    if kills:
        forage(g, pell)

    for bot in (besh, dova):  # any other survey tools they picked up (crafted or looted)
        kinds = {str(i.get('name')).split('survey_tool_')[-1] for i in bot.inventory().get('items', [])
                 if 'survey_tool_' in str(i.get('name'))} - {'mineral', 'liquid'}
        for kind in sorted(kinds):
            survey_and_sample(g, bot, kind)

    relog_keeps(g, besh)
