"""Death, cloning and insurance: functional-test-plan.md section 9, gap 7 (Claude, 17 Oct 2026).

Dova, at the nearest cloning facility (Mos Eisley from the crafting check):
  1. binds there: the cloning terminal's radial 20, the confirm window, 1,000 credits (CloningStoreSuiCallback);
  2. insures one item: /insure near an insurance terminal, the first row of the list, 100 credits
     (InsuranceMenuSuiCallback), "@base_player:prose_insure_success";
  3. dies: three incapacitations in a row (/agentgear afflict incap; the third kills, as in combat);
  4. clones at the bound facility: the clone window's "@base_player:revive_bind" row (it is offered only when the
     bind was stored), then back on the same planet within 60 m of the bound facility's terminal;
  5. reads the decay report (PlayerManager sendPlayerToCloner): the insured item lost 1% and others 5%, and the item
     is still in the inventory.
Then /agentgear afflict restore clears the clone wounds so later scenarios start clean.
Not covered: the wounds and battle fatigue values themselves (the body does not track wounds), and binding at a
facility other than the closest (Mos Eisley has one).
"""
import json
import math
import re

GROUP = 'Besh'
ROW = re.compile(r'^List\.dataList\.(\d+)$')


def rows(page):
    """A list window's rows by index: the 'List.dataList.N' 'Text' settings of a SuiCreatePageMessage."""
    found = {}
    for command in page.get('commands', []):
        narrow, wide = command.get('narrow') or [], command.get('wide') or []
        for value in narrow:
            match = ROW.match(str(value))
            if match and 'Text' in narrow and wide:
                found[int(match.group(1))] = wide[0]
    return [found[i] for i in sorted(found)]


def page_with(bot, text, timeout=10):
    """The newest SUI page whose JSON contains text, waiting up to timeout seconds."""
    def newest():
        pages = [p for p in bot.sui_pages().get('pages', []) if text in json.dumps(p)]
        return pages[-1] if pages else None
    page = newest()
    if page is None and bot.wait_for(lambda e: e.get('event') == 'sui_page' and text in json.dumps(e), timeout):
        page = newest()
    return page


def credits(bot):
    s = bot.status()
    return (s.get('bank_credits') or 0) + (s.get('cash_credits') or 0)


ANCHOR = (3500, -4800)  # Mos Eisley: the search centre while the bot stands in a cell (status x/y are then cell-local)


def search(bot, text, radius, center=None):
    """The server's object search around center, or around the bot outdoors (indoors: around ANCHOR)."""
    if center is None and bot.status().get('cell'):
        center = ANCHOR
    return bot.locate(text, radius, *center) if center else bot.locate(text, radius)


def cells_of(bot, obj):
    """The cells of obj's building that hold terminals (the server search reports each object's cell)."""
    found = search(bot, 'terminal', 60, (obj['x'], obj['y']))
    return {o['cell'] for o in found if o.get('building') == obj.get('building') and o.get('cell')} | {obj.get('cell')}


def walk_to(bot, obj):
    """Next to an object; indoors with the cell-local position the server search gives (locate's 'local')."""
    local = obj.get('local')
    if obj.get('cell') and local:
        # Two legs: a long walk straight to a cell failed with "the server keeps putting us back" (17 Oct, 268 m from
        # Mos Eisley's weapon station); outdoors to the building's edge first, then in, works.
        if (bot.status().get('cell') or 0) != obj['cell']:
            bot.walk(obj['x'], obj['y'])
        return bot.walk(local['x'] - 1.5, local['y'], local['z'], obj['cell'], tries=4)
    return bot.walk(obj['x'] + 1.5, obj['y'])


def bind(g, bot, terminal):
    before = credits(bot)
    bot.select(terminal['oid'], 20, wait=1)
    already = any('already stored here' in str(e.get('text', '')) for e in bot.idle(1))
    if already:
        g.note(f'{bot.first}: clone data was already stored here (no charge this run)')
        return True
    page = page_with(bot, 'clone_confirm')
    if not g.check(f'{bot.first}: the cloning terminal asks to store clone data', page, page and page.get('page_id')):
        return False
    bot.sui_respond(page['page_id'], 0, [], wait=3)
    paid = before - credits(bot)
    coupon = 'coupon' in json.dumps(page)
    return g.check(f'{bot.first}: clone data stored ({"new-player coupon" if coupon else "1,000 credits"})',
                   coupon or paid == 1000, f'paid {paid}')


def insure(g, bot):
    before = credits(bot)
    events = bot.slash('insure', wait=2)
    page = page_with(bot, 'mnu_insure')
    if not g.check(f'{bot.first}: /insure opens the insurance list', page,
                   page or [e.get('text') for e in events if e.get('event') == 'system'][:3]):
        return None
    listed = rows(page)
    if not g.check(f'{bot.first}: the list has insurable items', listed, listed[:5]):
        return None
    bot.sui_respond(page['page_id'], 0, ['false', '0'], wait=3)
    said = [e.get('text') for e in bot.idle(1) if 'insure' in str(e.get('text', ''))]
    paid = before - credits(bot)
    g.check(f'{bot.first}: insures {listed[0]} for 100 credits', paid == 100 and any('success' in t for t in said),
            f'paid {paid}; {said[:2]}')
    return listed[0]


def die(g, bot):
    for _ in range(5):
        if bot.posture() == 'dead':
            break
        for _ in range(30):  # stand up from the last incapacitation first
            if bot.posture() != 'incapacitated':
                break
            bot.idle(3)
        bot.slash('agentGear', 'afflict incap', wait=3)
    return g.check(f'{bot.first} dies after incapacitations in a row', bot.posture() == 'dead', bot.posture())


def clone_at_bind(g, bot, terminal, other, planet):
    page = page_with(bot, 'revive_title', 30)
    if not g.check(f'{bot.first}: the clone window opens', page, page and page.get('page_id')):
        return False
    options = rows(page)
    if not g.check(f'{bot.first}: the clone window offers the bound facility', '@base_player:revive_bind' in options, options):
        return False
    bot.sui_respond(page['page_id'], 0, [str(options.index('@base_player:revive_bind')), '@base_player:revive_title'], wait=8)
    for _ in range(10):
        if bot.posture() != 'dead':
            break
        bot.idle(3)
    here = bot.status()
    bound = cells_of(bot, terminal)
    if here.get('cell'):  # inside: one of the bound building's cells
        there, detail = here['cell'] in bound, f"cell {here['cell']}, bound building's cells {sorted(bound)}"
    else:  # outside (the cloner's spawn point can be outdoors): nearer the bound building than the other one
        to = lambda o: math.hypot(here['x'] - o['x'], here['y'] - o['y']) if o else 1e9
        there = to(terminal) <= 60 and to(terminal) < to(other)
        detail = f"outdoors at {here['x']:.0f}, {here['y']:.0f}: {to(terminal):.0f} m from the bound cloner" + (
            f", {to(other):.0f} m from the other" if other else '')
    g.check(f'{bot.first} clones at the bound facility', bot.posture() != 'dead' and here.get('planet') == planet and there,
            f"{here.get('planet')}, posture {bot.posture()}, {detail}")
    return True


def decay_report(g, bot, insured, kept):
    page = page_with(bot, 'DECAY REPORT', 20)
    if not g.check(f'{bot.first}: the decay report arrives', page, page and page.get('page_id')):
        return
    lines = [r for r in rows(page) if '(@' in r]
    percent = {}
    for line in lines:
        match = re.match(r'\s*-\s*(.+?)\s*\(@(\d+)%\)', line)
        if match:
            percent.setdefault(match.group(1), []).append(int(match.group(2)))
    mine = percent.get(insured, [])
    g.check(f'{bot.first}: the insured {insured} decays least', bool(mine) and max(mine) >= max(max(v) for v in percent.values()),
            {k: v for k, v in list(percent.items())[:6]})
    bot.sui_respond(page['page_id'], 0, [], wait=1)
    # The inventory gives item keys (@wearables_name:...), the windows display names, so compare object ids: every
    # item carried before the death is still there after cloning, the insured one included.
    now = {i['oid'] for i in bot.inventory().get('items', [])}
    lost = [name for oid, name in kept.items() if oid not in now]
    g.check(f'{bot.first} keeps every item through death and cloning ({insured} included)', not lost,
            f'{len(kept)} items before; lost {lost[:5]}')


def run(g):
    bot = g['Dova']
    bot.recover()
    planet = bot.status().get('planet')
    # Bind at one facility and die at another, so "closest" and "bound" differ (Mos Eisley has two cloners).
    cloners = search(bot, 'terminal_cloning', 1500)
    terminal = cloners[0] if cloners else None
    other = next((t for t in cloners if terminal and t.get('building') != terminal.get('building')), None)
    if not g.check(f'{bot.first}: a cloning terminal within 1.5 km', terminal, terminal and
                   {k: terminal.get(k) for k in ('building', 'x', 'y', 'distance')}):
        return
    if not walk_to(bot, terminal).get('arrived'):
        g.note('BLOCKED: could not reach the cloning terminal')
        return
    if credits(bot) < 1100:
        g.note(f'BLOCKED: {bot.first} has {credits(bot)} credits; binding and insurance need 1,100')
        return
    if not bind(g, bot, terminal):
        return
    insurer = next(iter(search(bot, 'terminal_insurance', 60, (terminal['x'], terminal['y']))), None)
    if insurer is None or not walk_to(bot, insurer).get('arrived'):
        g.note(f'BLOCKED: no reachable insurance terminal near the cloner ({insurer and insurer.get("template")})')
        return
    insured = insure(g, bot)
    if insured is None:
        return
    if other is not None and walk_to(bot, other).get('arrived'):
        g.note(f"{bot.first} dies at the other cloner (building {other.get('building')}), so the closest is not the bound one")
    else:
        g.note(f'{bot.first} dies at the bound cloner (no second cloner reached): closest and bound are the same building')
    kept = {i['oid']: str(i.get('name')) for i in bot.inventory().get('items', []) if i.get('type') != 'MSCO'}
    if not die(g, bot):
        return
    if clone_at_bind(g, bot, terminal, other, planet):
        decay_report(g, bot, insured, kept)
    bot.slash('agentGear', 'afflict restore', wait=2)
