"""Mission terminals for the squads: functional-test-plan.md section 11 (Claude, 17 Oct 2026).

Every mission terminal type the test galaxy has, and one whole mission of each kind: take it at the terminal, travel to
it, do the work, get paid into the bank, and see the mission leave the datapad. The scenarios:
  cresh-missions.py  general (destroy, deliver), the 6-mission cap, newbie and statue terminals
  besh-missions.py   artisan (crafting, survey)
  dorn-missions.py   entertainer (dancer, musician)
  forn-missions.py   scout (recon, hunting), bounty, imperial, rebel
Each mission ends in one note, RESULT <terminal>/<type>: {...}, with the reward, the share expected, the bank before and
after, whether the mission left the datapad, and the seconds it took. Those lines are what the test plan records.

Server rules (Core3-dev fc3bb3e2; MMI = src/server/zone/managers/mission/MissionManagerImplementation.cpp):
  * Terminal type to missions (MMI:619-833): general destroy and deliver; artisan survey and crafting; entertainer dancer
    and musician; scout recon and hunting; bounty 10 bounty missions; imperial and rebel destroy and deliver, plus
    crafting, recon, dancer and musician (all three factional extras are on). Newbie and statue terminals answer
    @skill_teacher:skill_terminal_disabled (MMI:165). Any player may use the faction terminals.
  * A list needs the player within 6 m of the terminal and 1.4 s since the last list (MMI:170, 194). Bounty terminals
    need combat_bountyhunter_novice (MMI:178).
  * Core3.MissionManager.MaxActiveMissions missions at once, 6 by default on this server (stock 2; the test galaxy's
    config-local does not set it), at most one bounty; the next one gets mission_generic:too_many_missions (MMI:270).
  * Pay (MissionObjectiveImplementation.cpp:184-350): reward / max(group size when accepted, group size now) to each
    group member within 128 m of the mission's end point (the owner alone if none is), into the bank, with
    mission_generic:success_w_amount. So a grouped bot's share is reward // group size.
  * Destroy: the lair spawns when the owner comes within 128 m of the waypoint, up to 256 m away, and the waypoint
    moves to it ("Mission Target has been located"). Deliver and crafting: the waypoint is the target NPC; talking to it
    hands over a datadisk (crafting: the schematic and its components), the waypoint moves to the destination NPC, and
    talking to that one completes it. Crafting: the item to bring is one of five quest items (mission_manager.lua).
    Survey: a sample of the named resource class with density at least the mission's level (50-95), taken over 1024 m
    from where the list was made. Dancer and musician: that performance inside the building, within 32 m of the mission
    spot, for 10 minutes. Recon: the owner enters a 32 m area 1-4 km out. Hunting: the owner kills 15 x difficulty
    creatures of the target's template within 128 m of itself. Bounty (NPC): the probe droid transmits the target's
    signature, then the seeker droid gives its waypoint (mission level 2+, so combat_bountyhunter_investigation_01);
    the target spawns when the hunter comes within 256 m.
  * The body turns a string-id message whose file has a slash into its first two words (AgentControl.cpp
    onStringIdSystemMessage): success_w_amount and too_many_missions both arrive as "@mission:mission_generic". So these
    checks read the bank and the datapad; the message is only "a mission_generic message came".
  * There is no abort in the body (the client sends MissionAbortCallback, not a command), so a mission that is not
    finished stays in the datapad until it expires after 48 h.
"""
import json
import math
import time

TYPES = {  # template file -> missionTerminalType (bin/scripts/object/tangible/terminal/terminal_mission*.lua)
    'terminal_mission.iff': 'general', 'terminal_mission_artisan.iff': 'artisan',
    'terminal_mission_entertainer.iff': 'entertainer', 'terminal_mission_scout.iff': 'scout',
    'terminal_mission_bounty.iff': 'bounty', 'terminal_mission_imperial.iff': 'imperial',
    'terminal_mission_rebel.iff': 'rebel', 'terminal_mission_newbie.iff': 'newbie',
    'terminal_mission_statue.iff': 'statue'}
_FACTION = {'destroy', 'deliver', 'crafting', 'recon', 'dancer', 'musician'}
OFFERS = {'general': {'destroy', 'deliver'}, 'artisan': {'survey', 'crafting'}, 'entertainer': {'dancer', 'musician'},
          'scout': {'recon', 'hunting'}, 'bounty': {'bounty'}, 'imperial': _FACTION, 'rebel': _FACTION}
DISABLED = '@skill_teacher:skill_terminal_disabled'
GENERIC = '@mission:mission_generic'  # how success_w_amount and too_many_missions reach the body (see above)
CARRY = ('deliver', 'crafting', 'survey')  # missions that put something in the inventory
# Held missions a later run may finish instead of taking another. Not deliver or crafting: a held one may be stuck
# (its NPCs gone after a full-inventory pickup); not bounty: one at a time, and its target moves.
REUSE = ('destroy', 'survey', 'recon', 'hunting', 'dancer', 'musician')
LOCATED = 'Mission Target has been located'
CAP = 6
LIST_COOLDOWN = 1.6            # s between list requests (the server's 1.4 s and a margin)
IN_TOWN = 1500                 # a deliver mission's end within this of the bot: same city (MMI:1323-1417)
SURVEY_DISTANCE = 1024         # a survey sample counts only this far from the mission's start
QUEST_ITEMS = ('attunement_grid', 'current_alternator', 'feedback_controller', 'output_governor', 'power_regulator')
DOWN = ('incapacitated', 'dead')


# ---- small readers ----
def kind(template):
    return TYPES.get(str(template or '').rsplit('/', 1)[-1])


def in_bag(m):
    return 'mission_bag' in str((m or {}).get('container_name'))


def in_datapad(m):
    return 'datapad' in str((m or {}).get('container_name'))


def typed(m):
    return str((m or {}).get('type')) not in ('0', '', 'None')


def where(m):
    """Where a mission sends us: its waypoint once it has one, else its start. A listed mission's waypoint is empty
    (planet "0" at 0, 0); reading it as the target refused every destroy mission on 15 Oct."""
    for key in ('waypoint', 'start'):
        p = (m or {}).get(key) or {}
        if str(p.get('planet', '0')) not in ('0', '') and isinstance(p.get('x'), (int, float)) \
                and isinstance(p.get('y'), (int, float)) and (p['x'] or p['y']):
            return p
    return {}


def far(a, b):
    """Metres between two points with x and y; infinity when either is missing or they are on different planets."""
    if not a or not b or not all(isinstance(p.get(k), (int, float)) for p in (a, b) for k in ('x', 'y')):
        return math.inf
    if a.get('planet') and b.get('planet') and a['planet'] != b['planet']:
        return math.inf
    return math.hypot(a['x'] - b['x'], a['y'] - b['y'])


def held(bot):
    return [m for m in bot.missions() if in_datapad(m)]


def mission_now(bot, oid):
    return next((m for m in bot.missions() if m.get('oid') == oid), None)


BANK_RANGE = 8  # m; BankTerminalSuiCallback's transfer check, and the radial's with bank-terminal-range.patch


def bank(bot, back='here'):
    """The bank balance: from status() when the body knows it, else from a bank terminal's window (bank_window, which
    walks to the terminal; back says where to go afterwards)."""
    value = bot.status().get('bank_credits')
    return value if isinstance(value, int) else bank_window(bot, back)


def bank_window(bot, back='here'):
    """The balance from the nearest bank terminal's Deposit/Withdraw window (radial 68, Script.transfer,
    lblStartingTo), closed at once with cancel, so nothing moves. Needed because the body forgets the balance at the
    first character delta it cannot parse (AgentControl.cpp, CREO1 deltas; 17 Oct: unknown for every bot). Stock Core3
    opens the window at any range and while dead (17 Oct about 6 AM: Kor, dead, 2 km from the nearest terminal);
    Documentation-support/bank-terminal-range.patch makes it 8 m and alive. So the bot walks to the terminal first,
    then back: to back when it is a terminal from locate (approached as at_terminal does), or with 'here' to where it
    stood, when that was outdoors (an indoor spot has no world walk target; pass its terminal instead). None if no
    terminal, no arrival or no window."""
    found = sorted(bot.locate('terminal_bank', radius=3000), key=lambda o: o.get('distance', 0))
    if not found:
        return None
    terminal, here = found[0], bot.status()
    walked = (terminal.get('distance') or 0) > BANK_RANGE - 2
    if walked and not arrived(approach(bot, terminal)):
        return None
    bot.select(terminal['oid'], 68, wait=2)
    value = None
    for page in [p for p in bot.sui_pages().get('pages', []) if p.get('script') == 'Script.transfer']:
        for command in page.get('commands', []):
            if command.get('narrow', [])[:1] == ['transaction.lblStartingTo'] and command.get('wide'):
                try:
                    value = int(command['wide'][0])
                except (TypeError, ValueError):
                    pass
        bot.sui_respond(page['page_id'], 1, [], wait=1)  # cancel
    if walked and isinstance(back, dict):
        approach(bot, back)
    elif walked and back == 'here' and not here.get('cell') and isinstance(here.get('x'), (int, float)):
        bot.walk(here['x'], here['y'], tries=tries_for(far(bot.status(), here)))
    return value


INVENTORY_LIMIT = 80  # 17 Oct: ten squad bots stopped at 80 items, mostly spare /agentgear kits
# Documentation-support/mission-full-pickup.patch in the dev server: a full pickup says inv_full and keeps the objective.
# Set True with the build that installs it; then take(full_ok=PICKUP_FIX) lets a full carrier take a delivery, and
# errand checks the new behaviour (full_pickup). Stock Core3 aborts the objective and the mission is stuck.
PICKUP_FIX = False


def room(bot):
    """Free inventory slots. Stock Core3: a deliver pickup into a full inventory aborts the objective but leaves the
    mission in the datapad, stuck (DeliverMissionObjectiveImplementation.cpp updateMissionStatus; Cresh, 17 Oct 5:38 AM)."""
    return INVENTORY_LIMIT - len(loose_items(bot))


def loose_items(bot):
    """The items directly in the inventory (not held, not inside a bag)."""
    stock = bot.inventory().get('items', [])
    box = next((i.get('oid') for i in stock if i.get('name') == '@item_n:inventory'), None)
    return [i for i in stock if box is not None and i.get('parent') == box]


def spare_item(bot):
    """An item the bot can lose to free a slot: a medicine, else one of the most duplicated plain items (a spare kit),
    never a mission item. None if nothing is duplicated."""
    loose = [i for i in loose_items(bot) if i.get('type') == 'TANO' and '@mission' not in str(i.get('name'))]
    medicine = [i for i in loose if '@medicine_name:' in str(i.get('name'))]
    if medicine:
        return medicine[-1]
    names = {}
    for i in loose:
        names[i.get('name')] = names.get(i.get('name'), 0) + 1
    name = max(names, key=names.get) if names else None
    return next(i for i in reversed(loose) if i.get('name') == name) if name and names[name] > 1 else None


def mark(bot):
    """A point in the bot's history; said(bot, text, since) reads what came after it (each command empties the inbox,
    the history keeps the last 400 events)."""
    return round(time.time() - bot.started, 1) - 0.2


def said(bot, text, since):
    return [e.get('text') for e in bot.history if e.get('t', 0) >= since and text in str(e.get('text', ''))]


def success(bot, since):
    """success_w_amount since a mark: the truncated "@mission:mission_generic" exactly (other mission_generic messages
    such as group_too_far arrive whole, as plain text), or the whole key once the body parser is fixed."""
    return [e.get('text') for e in bot.history if e.get('t', 0) >= since
            and (e.get('text') == GENERIC or 'success_w_amount' in str(e.get('text', '')))]


def tries_for(metres):
    """walk() tries for a route: one move is capped at 95 s, about 400 m at the bots' pace (1130 m in 253 s, 17 Oct)."""
    return 3 if metres == math.inf else max(3, int(metres / 350) + 2)


def items(bot, text=None):
    return [i for i in bot.inventory().get('items', []) if text is None or text in str(i.get('name'))]


def agentgear(bot, kit):
    """/agentgear KIT (test galaxy): the server's JSON answer, or {} when none came."""
    bot.slash('agentGear', kit, wait=0)
    answer = bot.wait_for(lambda e: str(e.get('text', '')).startswith('[agentgear]'), 10)
    try:
        return json.loads(answer['text'][len('[agentgear] '):])
    except (TypeError, KeyError, ValueError):
        return {}


def agentskill(bot, *boxes):
    """/agentskill BOX ... (test galaxy): grants the boxes and their prerequisites. The server's answer text."""
    bot.slash('agentSkill', ' '.join(boxes), wait=0)
    answer = bot.wait_for(lambda e: str(e.get('text', '')).startswith('[agentskill]'), 10)
    return (answer or {}).get('text', 'no answer')


def group_size(g, bot):
    """Player members of bot's group among the squad (the server divides the reward by this). It asks every bot, so
    call it before the bots go off in parallel jobs (two jobs must never drive one bot)."""
    me = (bot.status().get('me') or {}).get('group')
    if not me:
        return 1
    count = 0
    for other in g.bots:
        try:
            if (other.status().get('me') or {}).get('group') == me:
                count += 1
        except Exception:
            pass
    return max(count, 1)


def result(g, line, **fields):
    """One RESULT note: what the test plan records for this mission."""
    fields = {k: v for k, v in fields.items() if v is not None}
    g.__dict__.setdefault('mission_results', []).append(dict(fields, line=line))
    g.note(f'RESULT {line}: ' + json.dumps(fields, sort_keys=True))
    return fields


def blocked(g, line, why, **fields):
    g.note(f'BLOCKED: {line}: {why}')
    return result(g, line, blocked=why, **fields)


# ---- terminals ----
def search_point(g, bot):
    """Where to centre the server's object search for bot: None (its own spot) outdoors; indoors an outdoor teammate's
    x and y. The body's find sends its own x and y, which are cell-local inside a building (AgentControl.cpp find:
    selfX, selfY), so 17 Oct 11:56 AM Cresh, just cloned inside the cloning facility at -17, -10, found no terminal
    within 3 km. Read before parallel jobs: it asks the teammates."""
    if not bot.status().get('cell'):
        return None
    for other in g.bots:
        here = other.status()
        if other is not bot and not here.get('cell') and isinstance(here.get('x'), (int, float)):
            return {'x': here['x'], 'y': here['y']}
    return None


def origin(bot):
    """The bot's position in world coordinates for distance rules. Indoors status() gives cell-local x and y, so the
    world position of the terminal it stands at (recorded by take()) stands in. 17 Oct 12:09 PM: Rusk at an indoor
    general terminal found no in-town delivery among six, every distance being measured from cell-local 0, 0."""
    here = bot.status()
    spot = bot.__dict__.get('mission_origin')
    if here.get('cell') and spot:
        return {'planet': here.get('planet'), 'x': spot['x'], 'y': spot['y']}
    return here


def locate_from(bot, text, radius, at=None):
    return bot.locate(text, radius=radius, x=at['x'], y=at['y']) if at else bot.locate(text, radius=radius)


def find_terminals(bot, radius=3000, at=None):
    """{terminal type: [terminals, nearest first]}. The server's search returns the 30 nearest matches and Mos Eisley
    alone has 54 mission terminals, so each type is searched by its own template name. at: see search_point."""
    found = {}
    for template, ttype in TYPES.items():
        hits = [o for o in locate_from(bot, template[:-4], radius, at) if kind(o.get('template')) == ttype]
        if hits:
            found[ttype] = sorted(hits, key=lambda o: o.get('distance', 0))
    return found


def whereabouts(bot):
    """Where the bot stands and whether its body answers: the detail of a failed search."""
    here = bot.status()
    return {k: here.get(k) for k in ('planet', 'x', 'y', 'cell', 'connected', 'error')}


def nearest_terminal(bot, ttype, radius=3000, at=None):
    template = next(t for t, k in TYPES.items() if k == ttype)
    hits = [o for o in locate_from(bot, template[:-4], radius, at) if kind(o.get('template')) == ttype]
    return min(hits, key=lambda o: o.get('distance', 0)) if hits else None


def at_terminal(g, bot, ttype, slot=0, radius=3000, at=None, team=None):
    """Find the nearest terminal of ttype and walk to it; from over 300 m away a guarded walk first, with team (bot
    and its guards) when given (17 Oct 12:36 PM: Dova, 1 km out after a survey, was incapacitated walking back).
    Returns it, or None after a failed check."""
    spot = nearest_terminal(bot, ttype, radius, at)
    if not g.check(f'{ttype}: a terminal within {radius} m of {bot.first}', spot,
                   {k: spot.get(k) for k in ('distance', 'cell', 'building')} if spot else whereabouts(bot)):
        return None
    if (spot.get('distance') or 0) > 300:
        guarded_walk(g, team or [bot], {'x': spot['x'], 'y': spot['y'] - 8}, f'{ttype}: to the terminal')
    trip = approach(bot, spot, slot)
    if not g.check(f'{ttype}: {bot.first} reaches the terminal', arrived(trip),
                   {k: trip.get(k) for k in ('arrived', 'error', 'seconds')} if isinstance(trip, dict) else trip):
        return None
    return spot


def approach(bot, spot, slot=0):
    """Walk to a terminal (inside its building when it has a cell). slot spreads several bots outdoors."""
    if spot.get('cell'):
        local = spot['local']
        return bot.walk(local['x'], local['y'], local['z'], spot['cell'])
    return bot.walk(spot['x'] + 2 * slot, spot['y'] - 2.5, tries=tries_for(far(bot.status(), spot)))


def arrived(trip):
    return isinstance(trip, dict) and bool(trip.get('arrived'))


def offers(bot, terminal, ttype=None, tries=3):
    """The terminal's typed offers. The bag keeps the previous terminal's list until the refresh arrives, so a list
    whose types don't belong to this terminal type is read again."""
    listed = []
    for _ in range(tries):
        listed = [m for m in bot.mission_list(terminal['oid']) if in_bag(m) and typed(m)]
        kinds = {m.get('type') for m in listed}
        if listed and (ttype not in OFFERS or kinds <= OFFERS[ttype]):
            return listed
        bot.idle(LIST_COOLDOWN)
    return listed


def counts(listed):
    return {k: sum(1 for m in listed if m.get('type') == k) for k in sorted({m.get('type') for m in listed})}


def accept(bot, mission, terminal):
    """Accept and confirm: the mission's record in the datapad, or {} if it never arrived there."""
    bot.accept_mission(mission['oid'], terminal['oid'])
    for _ in range(4):
        mine = mission_now(bot, mission['oid'])
        if in_datapad(mine):
            return mine
        bot.idle(1)
    return {}


def take(g, bot, terminal, ttype, choices, label, divisor, listed=None, full_ok=False):
    """List at terminal (unless listed is given), pick with the first (mission type, chooser) that finds one, accept.
    divisor is the bot's group size (group_size, read before any parallel jobs). full_ok lets a full inventory take a
    delivery (with PICKUP_FIX). Returns (mission, bank before, divisor), or (None, None, None) after a BLOCKED result."""
    if isinstance(terminal.get('x'), (int, float)):
        bot.__dict__['mission_origin'] = {'x': terminal['x'], 'y': terminal['y']}  # world coordinates (locate)
    for mtype, choose in choices:  # finish a mission an earlier run left (there is no abort; the cap is 6)
        old = choose([m for m in held(bot) if m.get('type') == mtype]) if mtype in REUSE else None
        if old:
            g.note(f'{label}: {bot.first} finishes a held {mtype} mission from an earlier run: '
                   + json.dumps({k: old.get(k) for k in ('title', 'target', 'difficulty', 'reward')}))
            return old, bank(bot, terminal), divisor
    if len(held(bot)) >= CAP:
        blocked(g, label, f'{bot.first} already holds {CAP} missions')
        return None, None, None
    listed = offers(bot, terminal, ttype) if listed is None else listed
    wanted = [t for t, _ in choices]
    g.check(f'{label}: the {ttype} terminal offers ' + ' or '.join(wanted),
            any(m.get('type') in wanted for m in listed), counts(listed))
    pick = None
    for mtype, choose in choices:
        pick = choose([m for m in listed if m.get('type') == mtype])
        if pick:
            break
    if pick is None:
        blocked(g, label, f'no {" or ".join(wanted)} mission fits', offers=counts(listed))
        return None, None, None
    if pick.get('type') in CARRY and room(bot) < 3 and not full_ok:
        blocked(g, label, f'{bot.first}\'s inventory is full ({INVENTORY_LIMIT - room(bot)} of {INVENTORY_LIMIT}); '
                          f'not taken, since a full pickup leaves the mission stuck')
        return None, None, None
    before = bank(bot, terminal)  # back to the terminal: the accept needs 6 m (MMI:170)
    taken = accept(bot, pick, terminal)
    if not g.check(f'{label}: accepted into the datapad', taken,
                   {k: pick.get(k) for k in ('type', 'title', 'target', 'difficulty', 'reward')}):
        return None, None, None
    return dict(pick, **taken), before, divisor


def wait_removed(bot, oid, seconds, every=3):
    """Poll until the mission leaves the datapad; True when it did."""
    deadline = time.time() + seconds
    while True:
        if not in_datapad(mission_now(bot, oid)):
            return True
        if time.time() >= deadline:
            return False
        bot.idle(every)


def paid(g, bot, mission, before, divisor, label, since, seconds=30, began=None, **extra):
    """The end of every mission: it leaves the datapad and the share reaches the bank. Records both checks and the
    RESULT; returns its fields."""
    removed = wait_removed(bot, mission['oid'], seconds)
    after = bank(bot)
    reward = mission.get('reward')
    expected = reward // max(divisor or 1, 1) if isinstance(reward, int) else None
    gained = after - before if isinstance(after, int) and isinstance(before, int) else None
    message = success(bot, since)
    far_away = said(bot, 'group_too_far', since)
    if far_away:
        extra['group_too_far'] = True
    g.check(f'{label}: the mission leaves the datapad', removed, {'success message': bool(message),
                                                                   'group_too_far': bool(far_away)})
    # A teammate's mission that ends within 128 m in the same window pays this bot a share too (17 Oct 12:09 PM:
    # Rusk's musician share 52 plus Dorn's dancer share 44, same building): then more than one success message came.
    others = gained - expected if gained is not None and expected is not None and gained > expected         and len(message) > 1 else 0
    if others:
        extra['other_shares'] = others
    g.check(f'{label}: the share reaches the bank', removed and gained is not None and gained - others == expected,
            {'reward': reward, 'divisor': divisor, 'expected': expected, 'paid': gained, 'other_shares': others,
             'success_messages': len(message), 'bank_before': before, 'bank_after': after})
    return result(g, label, type=mission.get('type'), title=mission.get('title'), reward=reward, divisor=divisor,
                  expected=expected, paid=gained, bank_before=before, bank_after=after, removed=removed,
                  message=bool(message), seconds=round(time.time() - began, 1) if began else None, **extra)


def unfinished(g, label, mission, why, began, **extra):
    """A mission that was taken but not finished: a RESULT without pay (it stays in the datapad up to 48 h)."""
    g.note(f'{label}: not finished: {why}')
    return result(g, label, type=mission.get('type'), title=mission.get('title'), reward=mission.get('reward'),
                  removed=False, unfinished=why, seconds=round(time.time() - began, 1), **extra)


# ---- people: deliver and crafting ----
def npc_at(bot, point, exclude=(), radius=8):
    """The creature nearest a waypoint (mission NPCs stand on their spawn point)."""
    best = None
    for o in bot.look(radius=40, type='CREO', limit=300):
        if o.get('oid') in exclude or not all(isinstance(o.get(k), (int, float)) for k in ('x', 'y')):
            continue
        d = math.hypot(o['x'] - point['x'], o['y'] - point['y'])
        if d <= radius and (best is None or d < best[0]):
            best = (d, o)
    return best and best[1]


def visit(g, bot, point, label, exclude=()):
    """Walk to a mission NPC and talk to it. Returns the NPC, or None after a failed check."""
    trip = bot.walk(point['x'] + 1.5, point['y'], tries=tries_for(far(bot.status(), point)))
    if not g.check(f'{label}: reach the NPC', arrived(trip),
                   {k: trip.get(k) for k in ('arrived', 'error', 'seconds')} if isinstance(trip, dict) else trip):
        return None
    npc = npc_at(bot, point, exclude)
    if not g.check(f'{label}: an NPC stands at the waypoint', npc, npc and npc.get('name')):
        return None
    events = bot.talk(npc['oid'], wait=4)
    words = [str(e.get('text') or '') for e in events if e.get('event') in ('npc_says', 'conversation', 'system')]
    g.note(f"{label}: {npc.get('name')}: " + ' / '.join(w[:80] for w in words if w)[:300])
    return npc


def full_pickup(g, bot, mission, first, since, label, squad):
    """A pickup that handed nothing to a full inventory. With mission-full-pickup.patch the server says inv_full and
    keeps the objective (the waypoint stays on the pickup NPC), so after spare items are destroyed a second talk hands
    the item over. Stock Core3 says nothing, despawns both NPCs and leaves the mission stuck in the datapad (17 Oct
    5:38 AM: Cresh at 80 of 80). True when the second talk reached the NPC."""
    kept = mission_now(bot, mission['oid'])
    spot = where(kept or {})
    told = said(bot, 'inv_full', since)
    g.check(f'{label}: a full inventory is told and keeps the pickup', told and in_datapad(kept) and far(spot, first) <= 5,
            {'inv_full': bool(told), 'held': in_datapad(kept), 'waypoint': spot, 'pickup': first, 'room': room(bot)})
    lost = []
    for _ in range(3):  # three slots, as take() wants: a crafting pickup hands over a part per draft slot
        spare = room(bot) < 3 and spare_item(bot)
        if not spare:
            break
        bot.slash('serverDestroyObject', '', target=spare['oid'], wait=1)
        lost.append(spare.get('name'))
    if not g.check(f'{label}: spare items free room', room(bot) > 0, {'room': room(bot), 'destroyed': lost}):
        return False
    g.note(f"{label}: {bot.first} destroyed {lost} for room; talks to the pickup NPC again")
    return visit(g, bot, first, f'{label} pickup again', squad) is not None


def errand(g, bot, mission, before, divisor, label, between=None):
    """Deliver and crafting: pick up from the target NPC, run between(items gained) if given (the crafting step;
    False stops), hand over to the destination NPC, get paid."""
    began, since = time.time(), mark(bot)
    squad = {b.oid for b in g.bots}
    first = where(mission)
    stock = {i['oid'] for i in items(bot)}
    if not visit(g, bot, first, f'{label} pickup', squad):
        return unfinished(g, label, mission, 'pickup failed', began)
    bot.idle(2)
    gained = [i for i in items(bot) if i['oid'] not in stock]
    if not gained and room(bot) < 3:
        if not full_pickup(g, bot, mission, first, since, label, squad):
            return unfinished(g, label, mission, 'full inventory at the pickup', began)
        bot.idle(2)
        gained = [i for i in items(bot) if i['oid'] not in stock]
    g.check(f'{label}: the pickup hands something over', gained, [i.get('name') for i in gained][:6])
    moved = where(mission_now(bot, mission['oid']) or {})
    if not g.check(f'{label}: the waypoint moves to the destination', moved and far(moved, first) > 5,
                   {'from': first, 'to': moved}):
        return unfinished(g, label, mission, 'waypoint did not move', began)
    if between is not None and between(gained) is False:
        return unfinished(g, label, mission, 'crafting failed', began)
    if not visit(g, bot, moved, f'{label} hand-over', squad):
        return unfinished(g, label, mission, 'hand-over failed', began)
    return paid(g, bot, mission, before, divisor, label, since, began=began, route=round(far(first, moved)))


# ---- destroy ----
def creatures_near(bot, radius, squad):
    return [o for o in bot.look(radius=radius, type='CREO', limit=300)
            if o.get('oid') not in squad and str(o.get('name', '')).startswith('@')
            and o.get('posture') not in DOWN and (o.get('health_pct') or 100) > 0]


def guarded_walk(g, team, point, label, leg=250, minutes=15):
    """Walk the team to point in legs; after each leg fight whatever stands next to anyone, and wait for the downed to
    get up. 17 Oct 6:25 AM: three Marksmen walking 1.7 km north of Mos Eisley to a destroy waypoint were each
    incapacitated by creatures on the way, because a walk never fights back. team[0] leads; a dead member drops out.
    Returns {'arrived', 'seconds', 'fights', 'downed'}."""
    squad = {b.oid for b in g.bots}
    began, fights, downed = time.time(), 0, set()
    deadline = began + minutes * 60
    team = list(team)
    stalls, last = 0, None
    while time.time() < deadline:
        status = team[0].status()
        if (status.get('me') or {}).get('posture') == 'dead':
            break
        here = origin(team[0])  # world coordinates, also indoors (the terminal's position)
        spot = (round(status.get('x') or 0), round(status.get('y') or 0), status.get('cell'))
        stalls = stalls + 1 if spot == last else 0
        last = spot
        if stalls >= 3:  # three legs without moving (17 Oct 12:22 PM: Dask retried a 3.3 km leg for 25 minutes)
            break
        left = far(here, point)
        if left <= 20:
            return {'arrived': True, 'seconds': round(time.time() - began, 1), 'fights': fights, 'downed': sorted(downed)}
        share = min(1.0, leg / left) if left != math.inf else 1.0
        step = {'x': here['x'] + (point['x'] - here['x']) * share, 'y': here['y'] + (point['y'] - here['y']) * share}
        if status.get('cell') and not team[0].__dict__.get('mission_origin'):
            step = dict(point)  # no world position known: head for the point; the body routes out of the building
        g.parallel(*[lambda b=b, i=i: b.walk(step['x'] + 3 * i, step['y'], tries=2) for i, b in enumerate(team)])
        for _ in range(4):  # clear what is next to us before the next leg
            standing = [b for b in team if b.posture() not in DOWN]
            near = [o for b in standing for o in creatures_near(b, 20, squad)]
            if not standing or not near:
                break
            target = min(near, key=lambda o: o.get('distance', 99))
            fights += 1
            g.parallel(*[lambda b=b: b.fight(target['oid'], 40) for b in standing])
        wait_until = time.time() + 120  # incapacitation lasts about a minute
        while time.time() < wait_until:
            postures = {b.first: b.posture() for b in team}
            downed |= {n for n, p in postures.items() if p in DOWN}
            team = [b for b in team if postures[b.first] != 'dead'] or team[:1]
            if not any(p == 'incapacitated' for n, p in postures.items() if n in {b.first for b in team}):
                break
            team[0].idle(5)
    g.note(f'{label}: guarded walk stopped {far(team[0].status(), point):.0f} m short after {fights} fights; '
           f'downed {sorted(downed)}')
    return {'arrived': False, 'seconds': round(time.time() - began, 1), 'fights': fights, 'downed': sorted(downed)}


def lair_standing(bot, lair):
    return any(o.get('oid') == lair['oid'] for o in bot.look(radius=150, type='TANO', limit=400))


def destroy_lair(g, team, lair, minutes=6):
    """Fight until the lair is gone: each standing bot first kills what is next to it (lairs send waves), then hits
    the lair, in 30 s rounds. Returns True when the lair is gone."""
    squad = {b.oid for b in g.bots}
    deadline = time.time() + minutes * 60

    def round_for(bot):
        near = creatures_near(bot, 15, squad)
        target = min(near, key=lambda o: o.get('distance', 99)) if near else lair
        return bot.fight(target['oid'], 30)

    while time.time() < deadline:
        if not lair_standing(team[0], lair):
            return True
        up = [b for b in team if b.posture() not in DOWN]
        if not up:
            return False
        g.parallel(*[lambda b=b: round_for(b) for b in up])
    return not lair_standing(team[0], lair)


def destroy(g, team, mission, before, divisor, label):
    """Walk the team to the waypoint (the owner, team[0], first: only the owner spawns the lair), destroy the lair.
    Every member's bank is read before and after: the server pays the members within 128 m of the mission's END point,
    which stays at the first waypoint when the lair spawns elsewhere (DestroyMissionObjectiveImplementation.cpp:175
    moves only the start and the waypoint). 17 Oct 5:38 AM: Ilsa, dead at the first waypoint, was paid; Cresh and Kor
    at the lair were not (group_too_far)."""
    owner, began, since = team[0], time.time(), mark(team[0])
    banks = {b.first: bank(b) for b in team[1:]}
    target = where(mission)
    trip = guarded_walk(g, team, {'x': target['x'], 'y': target['y'] - 12}, label)
    if not g.check(f'{label}: reach the mission area', trip['arrived'], trip):
        return unfinished(g, label, mission, 'mission area not reached', began, walk=trip)
    located = said(owner, LOCATED, since) or owner.wait_for(lambda e: LOCATED in str(e.get('text', '')), 20)
    g.check(f'{label}: the target is located', located)
    spot = where(mission_now(owner, mission['oid']) or {}) or target
    if far(spot, target) > 20:
        g.parallel(*[lambda b=b, i=i: b.walk(spot['x'] + 3 * i, spot['y'] - 15, tries=3) for i, b in enumerate(team)])
    lair = owner.find('lair', radius=100, type='TANO') or owner.find(
        '', radius=80, type='TANO', where=lambda o: '@lair_n:' in str(o.get('name')))
    if not g.check(f'{label}: find the lair', lair, lair and f"{lair['name']} {lair['distance']} m"):
        return unfinished(g, label, mission, 'lair not found', began)
    gone = destroy_lair(g, team, lair)
    g.check(f'{label}: the lair is destroyed', gone, [(b.first, b.posture()) for b in team])
    if not gone:
        return unfinished(g, label, mission, 'lair not destroyed', began, lair=lair.get('name'))
    lair_spot = {'x': lair.get('x'), 'y': lair.get('y')}
    end = mission.get('end') or target  # pay is judged from here; it stays at the first spot the generator picked
    done = paid(g, owner, mission, before, divisor, label, since, began=began, lair=lair.get('name'),
                lair_from_end_point=round(far(lair_spot, end)) if far(lair_spot, end) != math.inf else None)
    shares = {}
    for b in team[1:]:
        after = bank(b, None)  # the lair is done: a member who walked to a bank stays in town
        shares[b.first] = after - banks[b.first] if isinstance(after, int) and isinstance(banks[b.first], int) else None
    shares[owner.first] = done.get('paid')
    g.note(f'{label}: shares paid {shares} (each member within 128 m of the end point gets reward // {divisor})')
    done['shares'] = shares
    # The group-pay check (Documentation-support/mission-group-pay.md): everyone standing who fought at the lair
    # should get a share. Unpatched, pay is judged from the mission's end point only (the generator's first spot), so
    # this fails whenever the lair is over 128 m from it; with the patch, the owner's surroundings count too.
    fighters = [b.first for b in team if b.posture() != 'dead']
    unpaid = [n for n in fighters if not shares.get(n)]
    moved = done.get('lair_from_end_point')
    g.check(f'{label}: everyone who fought at the lair is paid', not unpaid,
            {'unpaid': unpaid, 'lair_from_end_point_m': moved, 'shares': shares})
    return done


# ---- crafting the quest item ----
def template_crc(path):
    """The client's object-template CRC (CRC-32, polynomial 0x04C11DB7, not reflected), as in besh-crafting.py."""
    crc = 0xFFFFFFFF
    for byte in path.encode():
        crc ^= byte << 24
        for _ in range(8):
            crc = ((crc << 1) ^ 0x04C11DB7) & 0xFFFFFFFF if crc & 0x80000000 else (crc << 1) & 0xFFFFFFFF
    return crc ^ 0xFFFFFFFF


QUEST_SCHEMATICS = {template_crc(f'object/draft_schematic/item/quest_item/shared_{n}.iff'): n for n in QUEST_ITEMS}


def craft_result(bot, step, timeout=8):
    return bot.wait_for(lambda e: e.get('event') == 'craft_result' and e.get('step') == step, timeout)


def craft_quest_item(g, bot, label, components):
    """One crafting session at the generic tool for the mission's quest item, with the components the NPC gave.
    Returns the new item or None. The session steps are besh-crafting.py's (17 Oct, 21 of 21)."""
    tool = (items(bot, 'generic_tool') or [None])[0]
    if tool is None:
        agentgear(bot, 'crafting')
        tool = (items(bot, 'generic_tool') or [None])[0]
    if not g.check(f'{label}: a generic crafting tool', tool, tool and tool.get('name')):
        return None
    bot.slash('cancelcraftingsession', wait=1)  # a session left open by an earlier run
    before = {i['oid'] for i in items(bot)}
    bot.slash('requestcraftingsession', target=tool['oid'], wait=0)
    listed = bot.wait_for('"craft_schematics"', 10) or {}
    pick = next((s for s in listed.get('schematics', []) if s.get('crc') in QUEST_SCHEMATICS), None)
    if not g.check(f'{label}: the mission schematic is on the tool', pick,
                   pick and QUEST_SCHEMATICS[pick['crc']] or f"{len(listed.get('schematics', []))} schematics, none a quest item"):
        bot.slash('cancelcraftingsession', wait=1)
        return None
    name = QUEST_SCHEMATICS[pick['crc']]
    old = {i['oid'] for i in items(bot) if i.get('type') == 'MSCO'}
    bot.slash('selectdraftschematic', str(pick['index']), wait=2)
    made = [i for i in items(bot) if i.get('type') == 'MSCO' and i['oid'] not in old]
    if not made:
        g.check(f'{label}: a manufacture schematic is made', False)
        bot.slash('cancelcraftingsession', wait=1)
        return None
    bot.slash('synchronizeduilisten', '0', target=made[-1]['oid'], wait=0)
    slots = bot.wait_for('"craft_slots"', 10) or {}
    if not g.check(f'{label}: the schematic opens with its slots', slots.get('slot_count'),
                   [(s.get('name'), s.get('resource'), s.get('quantity')) for s in slots.get('slots', [])]):
        bot.slash('cancelcraftingsession', wait=1)
        return None
    spare, filled = [c['oid'] for c in components], 0
    for slot in range(slots['slot_count']):
        for oid in list(spare):  # the server says which part fits: code 0 is IngredientSlot::OK
            bot.request('craft_add', 5, target=oid, slot=slot)
            answer = craft_result(bot, 'ingredient', 5)
            if answer and answer.get('code') == 0:
                filled += 1
                spare.remove(oid)
                break
    if not g.check(f'{label}: every slot filled with the NPC\'s parts', filled == slots['slot_count'],
                   f"{filled} of {slots['slot_count']}"):
        bot.slash('cancelcraftingsession', wait=1)
        return None
    bot.slash('nextcraftingstage', '1', wait=0)
    assembly = craft_result(bot, 'assembly', 10)
    g.check(f'{label}: assembly succeeds', assembly and assembly.get('code') != 8, assembly)  # 8: critical failure
    bot.slash('nextcraftingstage', '2', wait=2)  # no station, no experimentation: customization, then finish
    bot.slash('createprototype', '3 1', wait=0)
    done = bot.wait_for(lambda e: 'prototype_transferred' in str(e.get('text', '')), 40)
    bot.idle(2)
    new = [i for i in items(bot) if i['oid'] not in before and i.get('type') != 'MSCO']
    item = next((i for i in new if name in str(i.get('name'))), new[0] if new else None)
    g.check(f'{label}: the {name} is made', done and item, item and item.get('name'))
    return item


def crafting(g, bot, mission, before, divisor, label):
    def make(gained):
        return craft_quest_item(g, bot, label, gained) is not None
    return errand(g, bot, mission, before, divisor, label, between=make)


# ---- survey ----
SURVEY_TOOLS = ('mineral', 'liquid')  # the mission's two classes: mineral and chemical (liquid is the chemical tool)
# A survey mission names a resource CLASS, the third from the end of the spawn's class list (second for chemicals;
# ResourceSpawnImplementation::getSurveyMissionSpawnFamilyName), while the survey list shows each spawn's TYPE, its
# last class. 17 Oct 6:35 AM: "non-ferrous_metal" against aluminum_agrinium, copper_diatium and others. Each class
# here maps to the type prefixes under it (SWG's resource tree); a class not listed falls back to its own words.
FAMILY_TYPES = {
    'ferrous_metal': ('iron_', 'steel_'), 'non-ferrous_metal': ('aluminum_', 'copper_'),
    'metal': ('iron_', 'steel_', 'aluminum_', 'copper_'),
    'igneous_ore': ('ore_extrusive', 'ore_intrusive'), 'sedimentary_ore': ('ore_carbonate', 'ore_siliclastic'),
    'ore': ('ore_',), 'gemstone': ('armophous_', 'crystalline_'), 'amorphous_gemstone': ('armophous_',),
    'crystalline_gemstone': ('crystalline_',), 'radioactive': ('radioactive_',),
    'fuel_petrochem_solid': ('petrochem_fuel_solid',), 'petrochem_fuel_solid': ('petrochem_fuel_solid',),
    'fuel_petrochem_liquid': ('petrochem_fuel_liquid',), 'petrochem_fuel_liquid': ('petrochem_fuel_liquid',),
    'petrochem_inert': ('petrochem_inert',), 'inert_petrochem': ('petrochem_inert',), 'fiberplast': ('fiberplast',)}


def in_family(rtype, family):
    rtype = str(rtype or '').lower()
    prefixes = FAMILY_TYPES.get(family)
    if prefixes:
        return rtype.startswith(prefixes)
    words = [w for w in family.replace('-', '_').split('_') if len(w) >= 4]
    return bool(words) and any(w in rtype for w in words)


def survey_list(bot, tool):
    """Use a survey tool; the survey_resources event, answering the first-use range pop-up (besh-gather.py)."""
    bot.select(tool['oid'], 20, wait=0)
    found = bot.wait_for('"survey_resources"', 4)
    if not found:
        pages = [p for p in bot.sui_pages().get('pages', []) if 'dataList' in json.dumps(p)]
        if pages:
            bot.sui_respond(pages[-1]['page_id'], 0, ['0'], wait=2)
            bot.select(tool['oid'], 20, wait=0)
            found = bot.wait_for('"survey_resources"', 10)
    return found or {}


def survey(g, bot, mission, before, divisor, label, guard=None, spots=4):
    """Walk out past 1024 m from the mission's start, survey the named class, sample where the density reaches the
    mission's level. guard (another bot) walks along."""
    began, since = time.time(), mark(bot)
    family = str(mission.get('target') or '').lower().replace(' ', '_')
    level = mission.get('difficulty') or 50
    start = mission.get('start') or where(mission)
    if not family or not start:
        return unfinished(g, label, mission, 'no resource class or start on the mission', began)
    if not any(items(bot, f'survey_tool_{k}') for k in SURVEY_TOOLS):
        agentgear(bot, 'survey')
    tools = [t for k in SURVEY_TOOLS for t in items(bot, f'survey_tool_{k}')]
    if not g.check(f'{label}: survey tools', tools, [t.get('name') for t in tools]):
        return unfinished(g, label, mission, 'no survey tool', began)
    best = {}
    for n in range(spots):
        bearing = math.radians(45 + 90 * n)
        spot = {'x': start['x'] + 1150 * math.cos(bearing), 'y': start['y'] + 1150 * math.sin(bearing)}
        walkers = [bot] + ([guard] if guard else [])
        guarded_walk(g, walkers, spot, f'{label} spot {n + 1}')
        here = bot.status()
        if far(here, start) <= SURVEY_DISTANCE:
            g.note(f'{label}: spot {n + 1} not reached ({far(here, start):.0f} m from the start); next bearing')
            continue
        for tool in tools:
            listed = survey_list(bot, tool)
            names = [r['name'] for r in listed.get('resources', []) if in_family(r.get('type'), family)]
            if not names and n == 0:  # the class is the resource's third class from the end; types are the last one
                g.note(f"{label}: {tool.get('name')} lists no {family}; types: "
                       + ', '.join(sorted({str(r.get('type')) for r in listed.get('resources', [])}))[:300])
            for name in names[:3]:
                bot.slash('requestSurvey', name, wait=0)
                top = dict((bot.wait_for('"survey_results"', 12) or {}).get('best') or {})
                # The body reports the density as a fraction (17 Oct 12:28 PM: 0.811 for Vesoide, 81%), the mission
                # its level in percent (50-95).
                if isinstance(top.get('percent'), (int, float)) and top['percent'] <= 1.0:
                    top['percent'] = round(top['percent'] * 100, 1)
                if (top.get('percent') or 0) > (best.get('percent') or 0):
                    best = dict(top, name=name)
                bot.idle(4)  # survey cooldown
            if names:
                break
        g.note(f"{label}: spot {n + 1} at {far(here, start):.0f} m: best {best.get('name')} {best.get('percent')}%"
               f" (needs {level}% of {family})")
        if (best.get('percent') or 0) >= level:
            break
    if (best.get('percent') or 0) < level:
        return unfinished(g, label, mission, f"no {family} at {level}% found (best {best.get('percent')}%)", began)
    point = {'x': best['x'], 'y': best['y']}
    if far(point, start) > SURVEY_DISTANCE:
        bot.walk(point['x'], point['y'], tries=3)
    for _ in range(4):
        bot.slash('requestCoreSample', best['name'], wait=0)
        bot.wait_for(lambda e: 'sample' in str(e.get('text', '')).lower(), 40)
        if wait_removed(bot, mission['oid'], 20):
            break
    bot.slash('stand', wait=1)
    return paid(g, bot, mission, before, divisor, label, since, began=began,
                resource=best.get('name'), density=best.get('percent'), level=level)


# ---- entertainer ----
INDOOR_HINTS = ('furniture', 'terminal', 'mobile')  # 'mobile': NPCs standing inside (object/mobile/...)


def go_inside(g, bot, point, label):
    """Into the building at point: walk to it, then to an object the server's search finds inside it (those come with
    a cell and cell-local coordinates). Returns that object or None."""
    bot.walk(point['x'], point['y'] - 14, tries=tries_for(far(bot.status(), point)))
    for text in INDOOR_HINTS:
        inside = sorted((o for o in bot.locate(text, radius=40, x=point['x'], y=point['y']) if o.get('cell')),
                        key=lambda o: far(o, point))
        for o in inside[:3]:
            local = o['local']
            trip = bot.walk(local['x'] + 0.8, local['y'], local['z'], o['cell'])
            if arrived(trip) and bot.status().get('cell'):
                return o
    return None


def hold(bot, thing):
    """Put thing into the hands, as class-check.py's equip does: weapons and instruments share the hold slot and the
    server's own swap fails for an instrument (15 Oct), so whatever is held goes back to the inventory first
    (transferItemMisc, containment -1), then transferItemWeapon into slot 4. True when its parent is the bot."""
    stock = bot.inventory().get('items', [])
    if any(i.get('oid') == thing['oid'] and i.get('parent') == bot.oid for i in stock):
        return True
    box = next((i for i in stock if i.get('name') == '@item_n:inventory' and i.get('parent') == bot.oid), None)
    for i in stock:
        if box and i.get('parent') == bot.oid and 'unknown_weapon' not in str(i.get('name')) \
                and (i.get('type') == 'WEAO' or str(i.get('name')).startswith('@obj_n:obj_')):
            bot.slash('transferItemMisc', f"{box['oid']} -1 0 0 0", target=i['oid'], wait=1)
    bot.slash('transferItemWeapon', f'{bot.oid} 4 0 0 0', target=thing['oid'], wait=1)
    return any(i.get('oid') == thing['oid'] and i.get('parent') == bot.oid for i in bot.inventory().get('items', []))


def perform(g, bot, mission, before, divisor, label, minutes=12):
    """Dancer or musician: inside the mission's building, perform until the mission completes (10 minutes)."""
    began, since = time.time(), mark(bot)
    music = mission.get('type') == 'musician'
    room = go_inside(g, bot, where(mission), label)
    if not g.check(f'{label}: inside the performance building', room, room and room.get('building')):
        return unfinished(g, label, mission, 'could not get inside the building', began)
    if music:
        horn = (items(bot, 'slitherhorn') or [None])[0]
        if horn is None:
            agentgear(bot, 'instruments')
            horn = (items(bot, 'slitherhorn') or [None])[0]
        if not g.check(f'{label}: a slitherhorn in hand', horn and hold(bot, horn), horn and horn.get('name')):
            return unfinished(g, label, mission, 'no instrument in hand', began)
    start = mark(bot)
    bot.slash('startmusic' if music else 'startdance', 'starwars1' if music else 'basic', wait=4)
    begun = said(bot, 'music_start_self' if music else 'dance_start_self', start)
    if not g.check(f'{label}: the performance starts', begun, said(bot, '@', start)[-3:]):
        return unfinished(g, label, mission, 'performance did not start', began)
    done = wait_removed(bot, mission['oid'], minutes * 60, every=15)
    bot.slash('stopmusic' if music else 'stopdance', wait=2)
    if not done:
        return unfinished(g, label, mission, f'not complete after {minutes} minutes of performing', began)
    return paid(g, bot, mission, before, divisor, label, since, began=began, building=room.get('building'))


# ---- scout ----
def recon(g, bot, mission, before, divisor, label, team=()):
    """Walk into the recon area; team walks along and fights (17 Oct: Mirren and Dask, walking alone, were downed)."""
    began, since = time.time(), mark(bot)
    spot = where(mission)
    trip = guarded_walk(g, [bot, *team], spot, label, minutes=30)
    if trip['arrived']:
        bot.walk(spot['x'], spot['y'], tries=1)  # into the 32 m area's middle
    if not g.check(f'{label}: reach the recon area', trip['arrived'] or far(bot.status(), spot) < 30, trip):
        return unfinished(g, label, mission, 'recon area not reached', began, walk=trip)
    return paid(g, bot, mission, before, divisor, label, since, seconds=60, began=began,
                distance=round(far(mission.get('start'), spot)) if mission.get('start') else None)


def creature_key(m):
    return str((m or {}).get('target') or '').split(':')[-1]


def hunt(g, bot, mission, before, divisor, label, minutes=20):
    """Kill the mission's creature until the count is done; the owner fights alone (the server counts its kills)."""
    began, since = time.time(), mark(bot)
    key = creature_key(mission)
    need = 15 * max(int(mission.get('difficulty') or 1), 1)
    kills, tried = 0, set()
    deadline = time.time() + minutes * 60
    while time.time() < deadline and in_datapad(mission_now(bot, mission['oid'])):
        prey = [o for o in bot.locate(key, radius=1500) if o.get('oid') not in tried
                and (o.get('key') == key or str(o.get('name', '')).endswith(':' + key))]
        if not prey:
            g.note(f'{label}: no more {key} within 1500 m after {kills} kills')
            break
        target = min(prey, key=lambda o: o.get('distance', 0))
        tried.add(target['oid'])
        bot.walk(target['x'] - 8, target['y'], tries=tries_for(target.get('distance', 400)))
        live = next((o for o in bot.look(radius=60, type='CREO', limit=300) if o.get('oid') == target['oid']
                     and o.get('posture') not in DOWN), None)
        if not live:
            continue
        bot.fight(live['oid'], 60)
        # Each kill the server counts sends mission_generic:hunting_kills_remaining, which the body turns into
        # "@mission:mission_generic" like success_w_amount (17 Oct 6:35 AM: 13 such messages for Forn's rills).
        kills = len(success(bot, since))
        if bot.posture() in DOWN:
            g.note(f'{label}: {bot.first} went down after {kills} kills')
            break
    kills = len(success(bot, since))
    g.check(f'{label}: kills', kills, f'{kills} counted by the server (kill messages; the last one may be the pay) of {need}')
    if in_datapad(mission_now(bot, mission['oid'])):
        return unfinished(g, label, mission, f'{kills} of {need} {key} killed', began, kills=kills, needed=need)
    return paid(g, bot, mission, before, divisor, label, since, began=began, kills=kills, needed=need)


# ---- bounty ----
BOUNTY_BOXES = ('combat_bountyhunter_novice',)  # mission level 1: the informant gives the waypoint, no droids


def bounty_level(bot):
    """The level of the bounty missions this bot is offered (MMI randomizeGenericBountyMission)."""
    skills = ' '.join(str(s) for s in bot.profession('list').get('skills', []))
    return 3 if 'combat_bountyhunter_investigation_03' in skills else 2 if 'combat_bountyhunter_investigation_01' in skills else 1


def npc_bounty(bot, limit):
    """NPC bounties (a player bounty has no end point) whose target starts within limit m, nearest first."""
    def choose(listed):
        here = origin(bot)
        ok = [m for m in listed if far(here, m.get('end')) <= limit]
        return min(ok, key=lambda m: far(here, m.get('end'))) if ok else None
    return choose


def bounty(g, bot, terminal, label, divisor, limit=4000, lists=30):
    """An NPC bounty. The informant of the mission's level comes first (InformantMissionScreenHandler: the objective
    leaves INITSTATUS; a level-1 informant also gives the target's waypoint). At level 2 and 3 the probe droid then
    transmits the signature and the seeker droid gives the waypoint (both refuse before the informant:
    bounty_no_signature, 17 Oct 6:35 AM). Then walk there, and kill the target when it spawns (within 256 m)."""
    began = time.time()
    g.note(f"{label}: {bot.first} skills: " + agentskill(bot, *BOUNTY_BOXES)[:160])
    level = bounty_level(bot)
    # A level-1 target starts at a random spawn point anywhere on the planet (getRandomBountyTargetPosition), and every
    # list request draws new offers (populateMissionList): list again until one starts within limit.
    choose, listed = npc_bounty(bot, limit), []
    for n in range(lists):
        listed = offers(bot, terminal, 'bounty')
        if choose([m for m in listed if m.get('type') == 'bounty']):
            break
        bot.idle(LIST_COOLDOWN)
    g.note(f'{label}: {n + 1} lists for an NPC target within {limit} m')
    mission, before, divisor = take(g, bot, terminal, 'bounty', [('bounty', choose)], label, divisor, listed)
    if mission is None:
        return None
    since = mark(bot)
    old = where(mission_now(bot, mission['oid']) or {})
    squad = {b.oid for b in g.bots}
    # Every informant is a "spynet_operative" (mobile/mission/informant_npc.lua); only its conversation names the
    # level. Mos Eisley's three outdoor ones are level 1, its one indoors level 3 (screenplays/cities).
    helpers = sorted((o for o in locate_from(bot, 'spynet_operative', 3000, origin(bot) if bot.status().get('cell') else None)
                      if not o.get('cell') or level > 1), key=lambda o: o.get('distance', 0))
    if not g.check(f'{label}: an outdoor level-{level} informant within 3 km', helpers,
                   helpers and {k: helpers[0].get(k) for k in ('name', 'distance')}):
        return unfinished(g, label, mission, f'no level-{level} informant', began, level=level)
    informant = helpers[0]
    bot.walk(informant['x'] + 1.5, informant['y'], tries=tries_for(informant.get('distance', 400)))
    person = npc_at(bot, informant, squad, radius=6) or informant
    bot.talk(person['oid'], wait=4)
    told = said(bot, '@', since)[-4:]
    g.note(f'{label}: informant {person.get("name")}: {told}')
    if level >= 2:
        if not (items(bot, 'probot') and items(bot, 'seeker')):
            agentgear(bot, 'bounty')
        probot, seeker = (items(bot, 'probot') or [None])[0], (items(bot, 'seeker') or [None])[0]
        if not g.check(f'{label}: probe and seeker droids', probot and seeker):
            return unfinished(g, label, mission, 'no droids', began, level=level)
        town = guarded_walk(g, [bot], {'x': bot.status()['x'], 'y': bot.status()['y'] + 600}, label)  # out of town
        bot.select(probot['oid'], 138, wait=3)  # call the probe droid (refused inside a city)
        deadline, landed = time.time() + 90, None
        while time.time() < deadline and not landed:
            landed = next((o for o in bot.look(radius=40, type='CREO', limit=200)
                           if 'probe' in str(o.get('name', '')).lower()), None)
            if not landed:
                bot.idle(5)
        if not g.check(f'{label}: the probe droid lands', landed, said(bot, '@', since)[-3:]):
            return unfinished(g, label, mission, 'probe droid did not land', began, level=level, walk=town)
        bot.select(landed['oid'], 184, wait=5)  # transmit the biological signature
        bot.select(seeker['oid'], 137, wait=3)  # find the target
    deadline, spot = time.time() + 120, {}
    while time.time() < deadline:
        spot = where(mission_now(bot, mission['oid']) or {})
        if spot and far(spot, old) > 5:
            break
        bot.idle(5)
    if not g.check(f"{label}: the target's waypoint arrives", spot and far(spot, old) > 5,
                   {'waypoint': spot, 'messages': said(bot, '@', since)[-4:]}):
        return unfinished(g, label, mission, 'no target waypoint', began, level=level)
    away = far(bot.status(), spot)
    if away > limit:
        return unfinished(g, label, mission, f'target {away:.0f} m away (limit {limit})', began)
    trip = guarded_walk(g, [bot], {'x': spot['x'], 'y': spot['y'] - 20}, label, minutes=25)
    squad = {b.oid for b in g.bots}
    target = None
    deadline = time.time() + 60
    while time.time() < deadline and not target:  # it spawns within 256 m of the hunter, checked every 10 s
        name = str(mission.get('target') or '')
        near = [o for o in bot.look(radius=200, type='CREO', limit=300) if o.get('oid') not in squad]
        target = next((o for o in near if name and name in str(o.get('name'))), None)
        if not target:
            bot.idle(5)
    if not g.check(f'{label}: the target is there', target, target and target.get('name') or trip):
        return unfinished(g, label, mission, 'target not found at the waypoint', began)
    for _ in range(4):
        fought = bot.fight(target['oid'], 60)
        if 'target' in str(fought.get('result')) or bot.posture() in DOWN:
            break
    return paid(g, bot, mission, before, divisor, label, since, began=began, target=target.get('name'))


# ---- the 6-mission cap ----
def cap(g, bot, terminal):
    """Top up to CAP held missions with destroy missions (an active area each; deliver missions would hold two NPC
    spawn points each for 48 h), then a 7th must be refused: it stays in the bag and the datapad stays at CAP. The
    extra missions stay until they expire: the body has no abort."""
    label = 'general/cap'
    listed = offers(bot, terminal, 'general')
    spare = [m for m in listed if m.get('type') == 'destroy'] + [m for m in listed if m.get('type') == 'deliver']
    for m in spare[:max(CAP - len(held(bot)), 0)]:
        accept(bot, m, terminal)
    have = held(bot)
    if not g.check(f'{label}: {bot.first} holds {CAP} missions', len(have) == CAP, f'{len(have)} held'):
        return result(g, label, held=len(have), refused=None)
    left = [m for m in bot.missions() if in_bag(m) and m.get('type') in ('destroy', 'deliver')]
    if not left:
        bot.idle(LIST_COOLDOWN)
        left = [m for m in offers(bot, terminal, 'general') if m.get('type') in ('destroy', 'deliver')]
    if not left:
        return blocked(g, label, 'no 7th mission on the list', held=len(have))
    since = mark(bot)
    seventh = left[0]
    bot.accept_mission(seventh['oid'], terminal['oid'])
    bot.idle(2)
    now = mission_now(bot, seventh['oid'])
    count = len(held(bot))
    message = [t for t in said(bot, '', since) if t == GENERIC or 'too_many_missions' in str(t)]
    refused = not in_datapad(now) and count == CAP
    g.check(f'{label}: the 7th mission is refused', refused,
            {'seventh_in': (now or {}).get('container_name'), 'held': count})
    g.check(f'{label}: a refusal message comes', message, message[-1:] or 'none')
    return result(g, label, held=count, refused=refused, message=message[-1] if message else None,
                  note='too_many_missions arrives as "@mission:mission_generic" (body string-id parser)')


def disabled(g, bot, terminal, ttype):
    """Newbie and statue terminals: the list is refused with @skill_teacher:skill_terminal_disabled."""
    label = f'{ttype}/list'
    trip = approach(bot, terminal)
    if not g.check(f'{label}: reach the {ttype} terminal', arrived(trip), trip):
        return blocked(g, label, 'terminal not reached')
    since = mark(bot)
    bot.mission_list(terminal['oid'])
    refused = said(bot, DISABLED, since)
    g.check(f'{label}: refused with {DISABLED}', refused, refused[-1:] or said(bot, '@', since)[-3:])
    return result(g, label, refused=bool(refused), message=refused[-1] if refused else None)


# ---- choosing ----
def nearest(bot, fits=lambda m: True, limit=math.inf):
    def choose(listed):
        here = origin(bot)
        ok = [m for m in listed if fits(m) and far(here, where(m)) <= limit]
        return min(ok, key=lambda m: far(here, where(m))) if ok else None
    return choose


def in_town(bot):
    """Deliver and crafting missions whose start and end are both in this city, shortest route first."""
    def choose(listed):
        here = origin(bot)
        ok = [m for m in listed if far(here, where(m)) <= 400 and far(here, m.get('end')) <= IN_TOWN]
        return min(ok, key=lambda m: far(here, where(m)) + far(where(m), m.get('end'))) if ok else None
    return choose


def easiest(bot, limit=2300):
    """The lowest-difficulty destroy mission within limit m (1000-2000 m placement plus the lair's offset), avoiding
    boss lairs on a tie."""
    def choose(listed):
        here = origin(bot)
        ok = [m for m in listed if far(here, where(m)) <= limit]
        return min(ok, key=lambda m: (m.get('difficulty') or 99, 'boss' in str(m.get('target')),
                                      far(here, where(m)))) if ok else None
    return choose


def hunting_choice(bot, radius=1500):
    """An easy hunting mission (15 kills) whose creature the server's search finds most of nearby."""
    def choose(listed):
        easy = [m for m in listed if (m.get('difficulty') or 9) == 1] or listed
        scored = []
        for m in easy:
            key = creature_key(m)
            found = [o for o in bot.locate(key, radius=radius)
                     if o.get('key') == key or str(o.get('name', '')).endswith(':' + key)] if len(key) >= 3 else []
            scored.append((len(found), m))
        scored = [s for s in scored if s[0]]
        return max(scored, key=lambda s: s[0])[1] if scored else None
    return choose


def faction(g, bot, terminal, ttype, divisor, team=()):
    """An imperial or rebel terminal: an in-town deliver mission, else the nearest recon (both need no fight)."""
    mission, before, divisor = take(g, bot, terminal, ttype, [('deliver', in_town(bot)),
                                                              ('recon', nearest(bot, limit=4500))],
                                    f'{ttype}/mission', divisor)
    if mission is None:
        return None
    label = f"{ttype}/{mission.get('type')}"
    if mission.get('type') == 'deliver':
        return errand(g, bot, mission, before, divisor, label)
    return recon(g, bot, mission, before, divisor, label, team)


def lowest(listed):
    """The lowest-difficulty offer (survey: 50% is the easiest level)."""
    return min(listed, key=lambda m: m.get('difficulty') or 99) if listed else None


def summary(g):
    """One note with every RESULT of this group's run, for the test plan."""
    keys = ('line', 'reward', 'divisor', 'paid', 'removed', 'seconds', 'blocked', 'unfinished', 'refused')
    g.note('RESULTS ' + json.dumps([{k: r[k] for k in keys if k in r} for r in g.__dict__.get('mission_results', [])]))
