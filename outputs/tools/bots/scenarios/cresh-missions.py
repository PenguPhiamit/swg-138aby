"""Cresh, missions at the general terminal: functional-test-plan.md section 11 (Claude, 17 Oct 2026). The helpers and the
server rules they follow are in ../missions.py.

1. Census: the nearest terminal of every mission type within 2 km of Cresh (a TERMINALS note).
2. At the nearest general terminal (terminal_mission.iff), at the same time:
   * Cresh takes the easiest destroy mission; Cresh or Kor (whoever has inventory room) an in-town deliver mission,
     and does the delivery;
   * Ilsa fills her datapad to 6 with destroy missions, and a 7th must be refused;
   * Kor lists at a newbie and a statue terminal if one stands within 2 km (both must refuse).
3. All three walk to the destroy waypoint (Cresh first: only the owner spawns the lair) and destroy the lair.
A mission is done when it leaves Cresh's datapad and his share (reward // group size) reaches his bank.

Fighting strength: on 17 Oct at 2:25 AM the level-1 bots reached a difficulty-6 lair; Kor died and Cresh fell. So every
member gets the Marksman profession on the test galaxy first (/agentgear profession, existing boxes kept), and the
scenario takes the lowest difficulty within reach. Ilsa's extra missions stay until they expire (48 h; the body has no
abort), and a later run only tries the 7th.
"""
import json

import missions as M

GROUP = 'Cresh'


def run(g):
    cresh, ilsa, kor = g['Cresh'], g['Ilsa'], g['Kor']
    for bot in g.bots:
        bot.recover()
        g.note(f'{bot.first} gear: ' + str(bot.gear('basic'))[:120])
        if not any('combat_marksman_master' in str(s) for s in bot.profession('list').get('skills', [])):
            g.note(f'{bot.first} marksman: ' + str(bot.profession('combat_marksman'))[:120])
    divisor = M.group_size(g, cresh)
    found = M.find_terminals(cresh, at=M.search_point(g, cresh))
    g.note('TERMINALS within 3 km (the search returns 30 at most per type): ' + json.dumps(
        {t: {'count': len(v), 'nearest_m': round(v[0].get('distance', 0))} for t, v in sorted(found.items())}))
    general = (found.get('general') or [None])[0]
    if not g.check('a general mission terminal within 3 km', general, general.get('distance') if general else M.whereabouts(cresh)):
        return
    trips = g.parallel(*[lambda b=b, i=i: M.approach(b, general, i) for i, b in enumerate(g.bots)])
    g.check('Cresh reaches the general terminal', M.arrived(trips[0]),
            [(b.first, t.get('arrived') if isinstance(t, dict) else str(t)) for b, t in zip(g.bots, trips)])
    if not M.arrived(trips[0]):
        return

    listed = M.offers(cresh, general, 'general')
    # The shown difficulty includes the group's level, so take the lowest on offer, and reuse a held destroy mission
    # only if it is no harder (17 Oct 10:15 PM: all three died at a held one shown as 14).
    floor = M.lowest_destroy(cresh, listed)
    g.note(f'general/destroy: lowest destroy difficulty on offer within 2.3 km: {floor}')
    destroy, _, _ = M.take(g, cresh, general, 'general',
                           [('destroy', M.easiest(cresh, most=floor if floor is not None else 10))],
                           'general/destroy', divisor, listed)
    # The deliver goes to whoever has room (a pickup into a full inventory leaves the mission stuck); on 17 Oct all
    # three were full, so dorn-missions.py's Rusk takes one too.
    # With mission-full-pickup.patch installed (M.PICKUP_FIX), a full carrier takes it anyway and errand checks the
    # inv_full answer and the kept pickup.
    carrier = max((cresh, kor), key=M.room)
    deliver, d_before, _ = M.take(g, carrier, general, 'general', [('deliver', M.in_town(carrier))],
                                  'general/deliver', divisor, None if carrier is not cresh else listed,
                                  full_ok=M.PICKUP_FIX)

    jobs = [lambda: M.cap(g, ilsa, general) if M.arrived(trips[1]) else M.blocked(g, 'general/cap', 'Ilsa not at the terminal')]
    if deliver:
        jobs.append(lambda: M.errand(g, carrier, deliver, d_before, divisor, 'general/deliver'))
    shut = [(t, found[t][0]) for t in ('newbie', 'statue') if t in found]
    if shut and not (deliver and carrier is kor):
        jobs.append(lambda: [M.disabled(g, kor, spot, t) for t, spot in shut])
    else:
        g.note('no newbie or statue mission terminal within 3 km; nothing to list there')
    g.parallel(*jobs)

    if destroy:
        M.destroy(g, [cresh, ilsa, kor], destroy, M.bank(cresh), divisor, 'general/destroy')
    M.summary(g)
    for bot in g.bots:
        g.note(f'{bot.first} after: {bot.posture()}')
