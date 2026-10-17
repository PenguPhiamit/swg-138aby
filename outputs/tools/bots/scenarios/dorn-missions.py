"""Dorn, missions at the entertainer terminal: functional-test-plan.md section 11 (Claude, 17 Oct 2026). Helpers and
server rules: ../missions.py.

Dorn (Entertainer) takes the nearest dancer mission and Nima (Medic, given Novice Entertainer on the test galaxy for
this) the nearest musician mission. Each goes into the mission's building and performs there (Dorn /startdance basic,
Nima /startmusic starwars1 on a slitherhorn) until the mission completes after 10 minutes, both at the same time. Each
is done when it leaves the performer's datapad and the share (reward // group size) reaches the bank.
"""
import missions as M

GROUP = 'Dorn'


def run(g):
    dorn, nima = g['Dorn'], g['Nima']
    for bot in (dorn, nima):
        bot.recover()
    if not any('social_entertainer_novice' in str(s) for s in nima.profession('list').get('skills', [])):
        g.note('Nima: ' + M.agentskill(nima, 'social_entertainer_novice')[:160])
    divisor = M.group_size(g, dorn)
    spot = M.nearest_terminal(dorn, 'entertainer')
    if not g.check('entertainer: a terminal within 2500 m', spot, spot and spot.get('distance')):
        return
    trips = g.parallel(lambda: M.approach(dorn, spot, 0), lambda: M.approach(nima, spot, 1))

    def job(bot, trip, mtype):
        if not g.check(f'entertainer/{mtype}: {bot.first} reaches the terminal', M.arrived(trip), trip):
            return None
        mission, before, _ = M.take(g, bot, spot, 'entertainer', [(mtype, M.nearest(bot))],
                                    f'entertainer/{mtype}', divisor)
        return mission and M.perform(g, bot, mission, before, divisor, f'entertainer/{mtype}')

    g.parallel(lambda: job(dorn, trips[0], 'dancer'), lambda: job(nima, trips[1], 'musician'))
    M.summary(g)
