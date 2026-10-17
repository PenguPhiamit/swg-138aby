"""Forn's crew, missions at the scout, bounty, imperial and rebel terminals: functional-test-plan.md section 11 (Claude,
17 Oct 2026). Helpers and server rules: ../missions.py.

All at once, each bot on its own mission:
  * Forn: an easy hunting mission at the scout terminal (15 kills of the creature found most often nearby, alone,
    since the server counts the owner's kills);
  * then Forn: the nearest recon mission at the scout terminal (walk into the area 1-4 km out; Mirren, the crew's
    Doctor, died walking there alone on 17 Oct);
  * Ressa: an NPC bounty at the bounty terminal. She gets Novice Bounty Hunter only on the test galaxy (level-1
    missions: a Mos Eisley informant gives the target's waypoint, no droids), then walks there and kills the target.
    Dask got Investigation I on 17 Oct, which makes his missions level 2 (informants in Mos Espa and Wayfar, droids);
  * Dask at the imperial terminal and Brask at the rebel one: an in-town deliver mission, else the nearest recon (Mos
    Eisley offers no faction deliver missions, 17 Oct).
Each is done when it leaves the owner's datapad and the share (reward // group size, 5 here) reaches the bank.
"""
import missions as M

GROUP = 'Forn'


def run(g):
    forn, brask, dask, ressa, mirren = g['Forn'], g['Brask'], g['Dask'], g['Ressa'], g['Mirren']
    for bot in g.bots:
        bot.recover()
    divisor = M.group_size(g, forn)
    points = {b.first: M.search_point(g, b) for b in g.bots}  # before the parallel jobs: it asks teammates

    def scout(bot, slot, mtype):
        terminal = M.at_terminal(g, bot, 'scout', slot, at=points[bot.first])
        if not terminal:
            return None
        choose = M.hunting_choice(bot) if mtype == 'hunting' else M.nearest(bot, limit=4500)
        mission, before, _ = M.take(g, bot, terminal, 'scout', [(mtype, choose)], f'scout/{mtype}', divisor)
        if mission is None:
            return None
        if mtype == 'hunting':
            M.hunt(g, bot, mission, before, divisor, 'scout/hunting')
            return scout(bot, slot, 'recon') if bot.posture() not in M.DOWN else None  # then a recon, armed
        return M.recon(g, bot, mission, before, divisor, 'scout/recon')

    def hunter(bot):  # M.bounty grants the bounty hunter boxes before it lists (the terminal needs the novice box)
        terminal = M.at_terminal(g, bot, 'bounty', at=points[bot.first])
        return terminal and M.bounty(g, bot, terminal, 'bounty/bounty', divisor)

    def side(bot, ttype):
        terminal = M.at_terminal(g, bot, ttype, at=points[bot.first])
        return terminal and M.faction(g, bot, terminal, ttype, divisor)

    # Mirren (Doctor) died walking alone to a recon area on 17 Oct 12:28 PM, so Forn does the recon after his hunt.
    g.parallel(lambda: scout(forn, 0, 'hunting'), lambda: hunter(ressa),
               lambda: side(dask, 'imperial'), lambda: side(brask, 'rebel'))
    M.summary(g)
    for bot in g.bots:
        g.note(f'{bot.first} after: {bot.posture()}')
