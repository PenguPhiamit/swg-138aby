"""Owner-approved C23 SETUP exception, 14 Oct 2026; never an acceptance test.

Existing Esk crew on test galaxy only. No accounts/admin/teleports/world edits.
Run with squad.py --group Esk, exclusive driver claim and outside active rounds.
"""
import json

GROUP = 'Esk'
PREP = {'Esk': ('boss', ['combat_rifleman_master', 'outdoors_scout_novice']),
        'Tovan': ('boss', ['combat_2hsword_master', 'outdoors_scout_novice']),
        'Lira': ('support', ['science_doctor_master', 'crafting_artisan_survey_04'])}


def answer(bot, command, args, prefix):
    bot.slash(command, args, wait=0)
    event = bot.wait_for(lambda e: str(e.get('text', '')).startswith(prefix), 10)
    if not event:
        return {'error': 'no helper reply'}
    try:
        return json.loads(event['text'][len(prefix):])
    except (ValueError, TypeError, KeyError):
        return {'error': 'malformed helper reply'}


def run(g):
    g.note('SETUP ONLY: owner-approved 2026-10-14 exception; not normal gameplay acceptance')
    for name, (kit, skills) in PREP.items():
        bot = g[name]
        status = bot.status()
        if not g.check(name + ': safe starting state', status.get('planet') == 'tatooine'
                       and status.get('me', {}).get('posture') == 'upright', status.get('planet')):
            return
    for name, (kit, skills) in PREP.items():
        bot = g[name]
        reply = answer(bot, 'agentSkill', ' '.join(skills), '[agentskill] ')
        trained = set(reply.get('granted', [])) >= set(skills) and not any(
            reply.get(k) for k in ('failed', 'unknown', 'error'))
        if not g.check(name + ': requested skills granted', trained, reply):
            g.note('BLOCKED: stop setup after skill helper failure; no extra grants attempted')
            return
        reply = answer(bot, 'agentGear', kit, '[agentgear] ')
        g.check(name + ': ' + kit + ' kit helper reports success',
                not reply.get('error') and not reply.get('failed'), reply)
        inventory = bot.inventory()
        g.check(name + ': inventory readable after setup', inventory.get('ok'),
                {'items': len(inventory.get('items', []))})
    tools = {name: [i for i in g[name].inventory().get('items', [])
                    if 'survey_tool_' in str(i.get('name'))] for name in PREP}
    g.note('SURVEY TOOL AUDIT: ' + str(tools))
    g.note('Preparation receipts do not prove combat survival, active doctor support, crafting or survey acceptance.')
