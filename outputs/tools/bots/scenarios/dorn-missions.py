"""Dorn, missions at the entertainer terminal, and a delivery: functional-test-plan.md section 11 (Claude, 17 Oct 2026).
Helpers and server rules: ../missions.py.

At the nearest entertainer terminal Dorn (Entertainer) takes the nearest dancer mission and Rusk (Brawler, given Novice
Entertainer on the test galaxy for this) the nearest musician mission. Dorn goes into the mission's building and
dances (/startdance basic) until the mission completes after 10 minutes. Rusk first does an in-town deliver mission
from the nearest general terminal (on 17 Oct Cresh's group all had full inventories, and a pickup into a full
inventory leaves the mission stuck), then plays (/startmusic starwars1 on a slitherhorn) in his mission's building.
Each is done when it leaves the datapad and the share (reward // group size) reaches the bank.
"""
import missions as M

GROUP = 'Dorn'


def run(g):
    dorn, rusk = g['Dorn'], g['Rusk']
    for bot in (dorn, rusk):
        bot.recover()
    if not any('social_entertainer_novice' in str(s) for s in rusk.profession('list').get('skills', [])):
        g.note('Rusk: ' + M.agentskill(rusk, 'social_entertainer_novice')[:160])
    divisor = M.group_size(g, dorn)
    spot = M.nearest_terminal(dorn, 'entertainer')
    if not g.check('entertainer: a terminal within 3000 m', spot, spot and spot.get('distance')):
        return
    trips = g.parallel(lambda: M.approach(dorn, spot, 0), lambda: M.approach(rusk, spot, 1))

    def take(bot, trip, mtype):
        if not g.check(f'entertainer/{mtype}: {bot.first} reaches the terminal', M.arrived(trip), trip):
            return None, None
        mission, before, _ = M.take(g, bot, spot, 'entertainer', [(mtype, M.nearest(bot))],
                                    f'entertainer/{mtype}', divisor)
        return mission, before

    def dancer():
        mission, before = take(dorn, trips[0], 'dancer')
        return mission and M.perform(g, dorn, mission, before, divisor, 'entertainer/dancer')

    def musician():
        mission, before = take(rusk, trips[1], 'musician')
        general = M.at_terminal(g, rusk, 'general')
        if general:
            parcel, p_before, _ = M.take(g, rusk, general, 'general', [('deliver', M.in_town(rusk))],
                                         'general/deliver', divisor)
            if parcel:
                M.errand(g, rusk, parcel, p_before, divisor, 'general/deliver')
        return mission and M.perform(g, rusk, mission, M.bank(rusk), divisor, 'entertainer/musician')

    g.parallel(dancer, musician)
    M.summary(g)
