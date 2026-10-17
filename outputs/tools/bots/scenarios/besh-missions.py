"""Besh, missions at the artisan terminal: functional-test-plan.md section 11 (Claude, 17 Oct 2026). Helpers and server
rules: ../missions.py.

Dova (a novice Artisan; she made the crafting check's survey device on 17 Oct, while Besh's inventory was full) takes an
in-town crafting mission and the easiest survey mission at the nearest artisan terminal. Crafting: the target NPC hands
over the quest item's schematic and parts, she crafts it at the generic tool and brings it to the destination NPC.
Survey: she walks over 1024 m out with Varo as guard, surveys the named resource class and samples where the density
reaches the mission's level. Each is done when it leaves her datapad and her share (reward // group size) reaches her
bank.
"""
import missions as M

GROUP = 'Besh'


def run(g):
    dova, varo = g['Dova'], g['Varo']
    for bot in (dova, varo):
        bot.recover()
    if not any('crafting_artisan_novice' in str(s) for s in dova.profession('list').get('skills', [])):
        g.note('Dova profession: ' + str(dova.profession('crafting_artisan'))[:160])
    g.note('Varo gear: ' + str(varo.gear('basic'))[:120])
    divisor = M.group_size(g, dova)
    terminal = M.at_terminal(g, dova, 'artisan', at=M.search_point(g, dova))  # Varo joins her for the survey walk
    if not terminal:
        return
    listed = M.offers(dova, terminal, 'artisan')
    craft, c_before, _ = M.take(g, dova, terminal, 'artisan', [('crafting', M.in_town(dova))],
                                'artisan/crafting', divisor, listed)
    survey, _, _ = M.take(g, dova, terminal, 'artisan', [('survey', M.lowest)], 'artisan/survey', divisor, listed)
    if craft:
        M.crafting(g, dova, craft, c_before, divisor, 'artisan/crafting')
    if survey:
        M.survey(g, dova, survey, M.bank(dova), divisor, 'artisan/survey', guard=varo)
    M.summary(g)
