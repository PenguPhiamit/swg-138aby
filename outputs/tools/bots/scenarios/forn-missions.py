"""Forn's crew, missions at the scout, bounty, imperial and rebel terminals: functional-test-plan.md section 11 (Claude,
17 Oct 2026). Helpers and server rules: ../missions.py.

All at once, each bot on its own mission:
  * Forn: an easy hunting mission at the scout terminal (15 kills of the creature found most often nearby, alone,
    since the server counts the owner's kills);
  * Mirren: the nearest recon mission at the scout terminal (walk into the area 1-4 km out; her inventory was full
    on 17 Oct, and a recon puts nothing in it);
  * Dask: an NPC bounty at the bounty terminal. He gets Novice Bounty Hunter and Investigation I on the test galaxy
    (level-2 missions, so the droids work) and the droid kit: probe droid, seeker droid, walk, kill;
  * Ressa at the imperial terminal and Brask at the rebel one: an in-town deliver mission, else the nearest recon.
Each is done when it leaves the owner's datapad and the share (reward // group size, 5 here) reaches the bank.
"""
import missions as M

GROUP = 'Forn'


def run(g):
    forn, brask, dask, ressa, mirren = g['Forn'], g['Brask'], g['Dask'], g['Ressa'], g['Mirren']
    for bot in g.bots:
        bot.recover()
    divisor = M.group_size(g, forn)

    def scout(bot, slot, mtype):
        terminal = M.at_terminal(g, bot, 'scout', slot)
        if not terminal:
            return None
        choose = M.hunting_choice(bot) if mtype == 'hunting' else M.nearest(bot, limit=3000)
        mission, before, _ = M.take(g, bot, terminal, 'scout', [(mtype, choose)], f'scout/{mtype}', divisor)
        if mission is None:
            return None
        if mtype == 'hunting':
            return M.hunt(g, bot, mission, before, divisor, 'scout/hunting')
        return M.recon(g, bot, mission, before, divisor, 'scout/recon')

    def hunter(bot):  # M.bounty grants the bounty hunter boxes before it lists (the terminal needs the novice box)
        terminal = M.at_terminal(g, bot, 'bounty')
        return terminal and M.bounty(g, bot, terminal, 'bounty/bounty', divisor)

    def side(bot, ttype):
        terminal = M.at_terminal(g, bot, ttype)
        return terminal and M.faction(g, bot, terminal, ttype, divisor)

    g.parallel(lambda: scout(forn, 0, 'hunting'), lambda: scout(mirren, 1, 'recon'), lambda: hunter(dask),
               lambda: side(ressa, 'imperial'), lambda: side(brask, 'rebel'))
    M.summary(g)
    for bot in g.bots:
        g.note(f'{bot.first} after: {bot.posture()}')
