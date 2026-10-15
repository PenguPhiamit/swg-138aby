"""Escort mode: a bot crew that plays alongside a player (Claude, 15 Oct 2026). Owner: "the dungeon crew was meant
to run with me"; "this function can lead into the crew vendor, and future solo features". So it is generic: any group
from groups.json, any player to escort, roles and formation as data, orders by chat.

    summary = escort(g, owner, roles, minutes=120, formation=None)

Every 2 s each bot, in its own thread and talking only to its own bot (a request resets that bot's inbox):
  * finds the player (who.json gives the object id; the bot's own inspect then gives the player's position, building
    cell, target, combat state and health, from the bot's local copy of the world: no server traffic);
  * fights when the player is in combat (the player's target), when ordered to attack, or when something hits the
    player or a crew member (combat messages), with tools/bots/crew_combat.py's rotations; the healer heals the lowest
    of the player and the crew first;
  * otherwise follows: its formation slot around the player, into the player's building cell too.
  * jumps to the player (/agentgear goto) when the player is on another planet, or out of sight and over 300 m away.
Orders, from the player by spatial chat or a tell to any crew member (a leading "crew" is optional):
  follow | stay | attack | passive | heal | status | dismiss | waypoints (the leader mails the waypoint list)
  | buff (the healer enhances the player's health, action, strength, constitution, quickness and stamina)
  | invite (the leader sends the group invite again)
The leader acknowledges in spatial chat. The run ends on "dismiss", after `minutes`, or when the player has been
offline for 5 minutes.
"""
import json
import math
import re
import threading
import time
from pathlib import Path

import crew_combat

WHO = Path('/opt/swg/testgalaxy/Core3/MMOCoreORB/bin/log/who.json')
# Play data (owner, 15 Oct: "so we can start getting actual play data on improving it", about Creature Handler): the
# leader records every combat message it sees near the player (theirs, their pets', the crew's, the enemy's), the
# player's health and target every 10 s, and the orders. Escort mode only; not in git.
PLAY = Path(__file__).resolve().parents[2] / 'Bot-reports' / 'play'
TICK = crew_combat.TICK
SLACK = 4.0            # metres a bot may drift from its slot before it walks back
THREAT_SECONDS = 20    # how long "something hit us" stays a reason to fight
OFFLINE_LIMIT = 300
CATCHUP = 300          # out of sight and this far away (a speeder, a /teleport): jump to the player
GOTO_PAUSE = 25        # seconds a zone change takes before the next jump may be tried
STUCK_TRIES = 2        # follow walks that end where they began (outdoors) before the bot jumps to the player
TRAIL_STEP = 0.75      # metres the player moves indoors before the trail gets a new point
TRAIL_KEEP = 300
SPACING = (2.0, 1.5)   # indoors, bot n stands 2 + 1.5 n metres back along the player's path


def trail_point(trail, back):
    """The point `back` metres behind the newest one, measured along the trail (cell changes count as no distance)."""
    if not trail:
        return None
    gone = 0.0
    for older, newer in zip(reversed(trail[:-1]), reversed(trail[1:])):
        if older['cell'] == newer['cell']:
            gone += math.hypot(newer['x'] - older['x'], newer['y'] - older['y'])
        if gone >= back:
            return older
    return trail[0]


def walk_time(row, x, y):
    """A move's timeout from the distance: about 4 m/s plus a margin. A flat 15 s cut long walks off and called them
    stuck (owner, 15 Oct: "the crews pathing needs work")."""
    if row.get('x') is None:
        return 30
    return min(60, max(8, math.hypot(x - row['x'], y - row['y']) / 4 + 5))
FORMATION = [(3, 2), (-3, 2), (0, -4), (3, -4), (-3, -4), (5, 0), (-5, 0), (0, 5)]   # metres from the player
ORDERS = ('follow', 'stay', 'attack', 'passive', 'heal', 'status', 'dismiss', 'waypoints', 'buff', 'invite')
BUFFS = ('health', 'action', 'strength', 'constitution', 'quickness', 'stamina')   # the support kit's enhance packs


def word(text):
    """The order in a chat line, or None: 'crew, stay!' -> 'stay'."""
    words = re.findall(r'[a-z]+', str(text).lower())
    if words and words[0] == 'crew':
        words = words[1:]
    return words[0] if words and words[0] in ORDERS else None


def who(owner):
    """The player's row in who.json (oid, zone, world position), or None if offline."""
    try:
        clients = json.loads(WHO.read_text(encoding='utf-8', errors='replace')).get('clients', [])
    except (OSError, ValueError):
        return None
    return next((c for c in clients if str(c.get('firstName', '')).lower() == owner.lower()), None)


def health_of(creature):
    ham, top = creature.get('ham', {}), creature.get('max_ham', {})
    return ham.get('health', 0) / top['health'] if top.get('health') else 1.0


class Shared:
    """What the crew agrees on: orders, the player, threats. One lock; every bot thread reads and writes it."""

    def __init__(self, owner):
        self.lock = threading.Lock()
        self.owner = owner
        self.mode, self.assist, self.attack_until, self.heal_now, self.ended = 'follow', True, 0.0, False, False
        self.heard = {}               # (sender, line) -> when it was obeyed
        self.threat = (None, 0.0)      # (attacker oid, when)
        self.table = {}                # crew first name -> self row
        self.player = {}               # the player's row for the healer
        self.trail = []                # where the player stood indoors (cell, x, y, z), oldest first
        self.buffs = []                # enhancements the healer still owes the player ("buff" order)
        self.log = []

    def order(self, text, sender, now):
        verb = word(text)
        key = (sender, str(text))   # several bots hear the same line: once within 3 s
        with self.lock:
            if not verb or now - self.heard.get(key, -1e9) < 3:
                return None
            self.heard[key] = now
            if verb in ('follow', 'stay'):
                self.mode = verb
            elif verb == 'attack':
                self.attack_until, self.assist = now + 60, True
            elif verb == 'passive':
                self.assist, self.attack_until = False, 0.0
            elif verb == 'heal':
                self.heal_now = True
            elif verb == 'buff':
                self.buffs = list(BUFFS)
            elif verb == 'dismiss':
                self.ended = True
            self.log.append((round(now), verb))
            return verb


ACK = {'follow': 'Following.', 'stay': 'Holding here.', 'attack': 'Engaging your target.', 'passive': 'Weapons down.',
       'heal': 'Healing you.', 'dismiss': 'Crew dismissed.', 'waypoints': 'Mailing you the waypoints.',
       'buff': 'Mirren will buff you: stay close.', 'invite': 'Group invite sent: accept it or type /join.'}


def goto(bot, planet, x, y):
    """Jump to a planet and spot (/agentgear goto, test galaxy bot accounts; the way an admin's /teleport works)."""
    bot.slash('agentGear', f'goto {planet} {x:.0f} {y:.0f}', wait=0)
    answer = bot.wait_for(lambda e: str(e.get('text', '')).startswith('[agentgear]'), 8)
    bot.idle(10)  # the zone change
    return answer


def mail(bot, to, subject, waypoints):
    """Mail waypoints (planet, x, y, name) to a player: /agentgear mail, attachments the player can add."""
    body = ' ; '.join(f'{p} {x:.0f} {y:.0f} {n}' for p, x, y, n in waypoints)
    bot.slash('agentGear', f'mail {to} {subject} | {body}', wait=0)
    return bot.wait_for(lambda e: str(e.get('text', '')).startswith('[agentgear]'), 8)


def escort(g, owner, roles, minutes=120, formation=None, waypoints=None):
    shared = Shared(owner)
    slots = dict(zip([b.first for b in g.bots], formation or FORMATION))
    order = {b.first: i for i, b in enumerate(g.bots)}   # single-file order indoors
    crew_oids = set()
    records = {b.first: crew_combat.new_record() for b in g.bots if b.first in roles}
    counts = {b.first: {'fights': 0, 'follows': 0, 'orders': 0, 'unstuck': 0} for b in g.bots if b.first in roles}
    began, last_seen = time.time(), {'t': time.time()}
    jumped = {}            # first name -> time of the last /agentgear goto
    stuck = {}             # first name -> follow walks in a row that went nowhere
    play, flushed = [], {'t': time.time(), 'snap': 0.0}
    play_file = PLAY / f"{time.strftime('%Y%m%d-%H%M')}-{g.name}-escort.jsonl"

    def note_play(row):
        play.append(dict(row, t=round(time.time(), 1)))
        if time.time() - flushed['t'] > 30:
            flush()

    def flush():
        flushed['t'] = time.time()
        if play:
            PLAY.mkdir(parents=True, exist_ok=True)
            with open(play_file, 'a', encoding='utf-8') as f:
                f.write(''.join(json.dumps(r) + '\n' for r in play))
            del play[:]

    def listen(bot, events):
        for e in events:
            if e.get('event') in ('chat', 'tell') and str(e.get('from', '')).lower().startswith(owner.lower()):
                verb = shared.order(e.get('text'), owner, time.time())
                if verb:
                    counts[bot.first]['orders'] += 1
                    note_play({'kind': 'order', 'order': verb, 'heard_by': bot.first})
                    if bot is g.leader:
                        if verb == 'status':
                            with shared.lock:
                                rows = dict(shared.table)
                            bot.say(', '.join(f"{n} {round(r['health'] * 100)}%" for n, r in rows.items()) or 'No reports yet.')
                        elif verb in ACK:
                            bot.say(ACK[verb])
                        if verb == 'invite':  # owner, in game: 'can you have them invite me again'
                            bot.slash('invite', target=(who(owner) or {}).get('oid', 0), wait=0)
                        if verb == 'waypoints':
                            note_play({'kind': 'mail', 'answer': (mail(bot, owner, 'Waypoints', waypoints or []) or {}).get('text')})
            if e.get('event') == 'combat' and bot is g.leader:
                me = shared.player.get('oid')
                note_play({'kind': 'combat', **{k: e.get(k) for k in ('attacker', 'attacker_name', 'defender',
                           'defender_name', 'amount', 'what', 'weapon')},
                           'by_player': e.get('attacker') == me, 'on_player': e.get('defender') == me,
                           'by_crew': e.get('attacker') in crew_oids, 'on_crew': e.get('defender') in crew_oids})
            if e.get('event') == 'combat' and e.get('attacker') not in crew_oids \
                    and (e.get('defender') in crew_oids or e.get('defender') == shared.player.get('oid')):
                with shared.lock:
                    shared.threat = (e.get('attacker'), time.time())

    def player_now(bot, oid):
        """The player as this bot sees it: position (cell-local inside a building), cell, target, combat, health."""
        seen = bot.inspect(oid) if oid else {}
        creature = seen.get('creature') or {}
        if not seen.get('ok') or not creature:
            return None
        return {'oid': oid, 'x': seen.get('x'), 'y': seen.get('y'), 'z': seen.get('z'), 'cell': seen.get('parent') or 0,
                'target': creature.get('target'), 'fighting': 'combat' in (creature.get('states') or []),
                'health': health_of(creature), 'posture': creature.get('posture')}

    def target_for(bot, player):
        """What to hit now, as an object with x, y, oid (from inspect), or None."""
        now = time.time()
        with shared.lock:
            assist, ordered, (threat, when) = shared.assist, shared.attack_until > now, shared.threat
        choices = []
        if player and player.get('target') and (ordered or (assist and player['fighting'])):
            choices.append(player['target'])
        if assist and threat and now - when < THREAT_SECONDS:
            choices.append(threat)
        for oid in choices:
            if oid in crew_oids or oid == (player or {}).get('oid'):
                continue
            seen = bot.inspect(oid)
            creature = seen.get('creature') or {}
            if seen.get('ok') and seen.get('type') == 'CREO' and creature.get('posture') not in crew_combat.DOWN:
                return {'oid': oid, 'x': seen.get('x'), 'y': seen.get('y'), 'z': seen.get('z'),
                        'name': str(seen.get('name', '')).split(':')[-1]}
        return None

    def follow(bot, row, player, zone_row):
        dx, dy = slots.get(bot.first, (0, -3))
        if player and player['x'] is not None and player['cell']:
            # Indoors there is no room for a formation: on 15 Oct the bots walked to slots 3-5 m off the player, which in
            # the Death Watch bunker's chambers were inside the walls (positions up to 2.5 m off the floor mesh). They
            # walk the player's own path instead, single file: every trail point is a spot the player stood on.
            with shared.lock:
                trail = list(shared.trail)
            back = SPACING[0] + SPACING[1] * order.get(bot.first, 0)
            spot = trail_point(trail, back) or {'cell': player['cell'], 'x': player['x'], 'y': player['y'], 'z': player['z']}
            if (row.get('cell') or 0) == spot['cell'] and row.get('x') is not None and                     math.hypot(spot['x'] - row['x'], spot['y'] - row['y']) <= 1.0:
                bot.doing(f'with {owner} (inside, {back:.0f} m back)')
                return
            bot.doing(f'following {owner} inside')
            same = (row.get('cell') or 0) == spot['cell']
            bot.move(spot['x'], spot['y'], spot.get('z') or 0.0, spot['cell'],
                     timeout=walk_time(row, spot['x'], spot['y']) if same else 30)
            counts[bot.first]['follows'] += 1
            return
        if player and player['x'] is not None:
            spot = (player['x'] + dx, player['y'] + dy)
            same_frame = (player['cell'] or 0) == (row.get('cell') or 0)
            far = not same_frame or row.get('x') is None or math.hypot(spot[0] - row['x'], spot[1] - row['y']) > SLACK
            if far:
                bot.doing(f'following {owner}' + (' inside' if player['cell'] else ''))
                if player['cell']:
                    reply = bot.move(spot[0], spot[1], player.get('z') or 0.0, player['cell'], timeout=walk_time(row, *spot) if same_frame else 30)
                else:
                    reply = bot.move(spot[0], spot[1], timeout=walk_time(row, *spot))
                counts[bot.first]['follows'] += 1
                unstick(bot, row, reply, zone_row, outdoors=not player['cell'])
            else:
                stuck[bot.first] = 0
                bot.doing(f'with {owner}')
        elif zone_row:
            # Out of sight: walk toward who.json's world position (outdoors) on the same planet.
            bot.doing(f'catching up with {owner}')
            x, y = float(zone_row.get('worldPositionX', 0)) + dx, float(zone_row.get('worldPositionY', 0)) + dy
            unstick(bot, row, bot.move(x, y, timeout=walk_time(row, x, y)), zone_row, outdoors=True)

    def unstick(bot, row, reply, zone_row, outdoors):
        """Count follow walks that end where they began; after STUCK_TRIES, outdoors, jump next to the player. Outdoor
        walks have no navmesh between towns, so trees and rocks can pin a bot (owner: "pathing needs work")."""
        reply = reply if isinstance(reply, dict) else {}
        moved = row.get('x') is None or not isinstance(reply.get('x'), (int, float)) or             math.hypot(reply['x'] - row['x'], reply['y'] - row['y']) > 1.0
        stuck[bot.first] = 0 if reply.get('arrived') or moved else stuck.get(bot.first, 0) + 1
        if stuck[bot.first] >= STUCK_TRIES and outdoors and zone_row:
            stuck[bot.first] = 0
            dx, dy = slots.get(bot.first, (0, -3))
            bot.doing(f'stuck: jumping to {owner}')
            counts[bot.first]['unstuck'] += 1
            goto(bot, zone_row.get('zone'), float(zone_row.get('worldPositionX', 0)) + dx,
                 float(zone_row.get('worldPositionY', 0)) + dy)

    tries = {'n': 0, 'restocked': False}

    def buff(bot, row, player):
        """One step of the "buff" order: walk to the player, then one doctor enhancement (owner, 15 Oct: buffs in
        dungeons; the test galaxy's MedicalAnywhere makes them work away from hospitals). The doctor's ~20 s
        cooldown refuses the next one for a while; it stays queued."""
        with shared.lock:
            attribute = shared.buffs[0] if shared.buffs else None
        if attribute is None:
            return False
        same = (player['cell'] or 0) == (row.get('cell') or 0)
        if not same or row.get('x') is None or math.hypot(player['x'] - row['x'], player['y'] - row['y']) > 5:
            bot.doing(f'going to {owner} to buff')
            if player['cell']:
                bot.move(player['x'] + 1, player['y'], player.get('z') or 0.0, player['cell'], timeout=20)
            else:
                bot.move(player['x'] + 1.5, player['y'], timeout=walk_time(row, player['x'], player['y']))
            return True
        bot.doing(f'buffing {owner}: {attribute}')
        events = bot.slash('healenhance', attribute, target=player['oid'], wait=1.5)
        said = ' '.join(str(e.get('text', '')) for e in events)
        done = 'You enhance' in said
        if 'healing_response_60' in said and not tries['restocked']:   # no enhance pack left: fetch the support kit
            tries['restocked'] = True
            bot.slash('agentGear', 'support', wait=0)
            bot.wait_for(lambda e: str(e.get('text', '')).startswith('[agentgear]'), 8)
        elif not done and 'must_wait' not in said and 'in Combat' not in said:
            tries['n'] += 1
        note_play({'kind': 'buff', 'attribute': attribute, 'done': done, 'said': said[:200]})
        if done or tries['n'] >= 3:
            tries['n'] = 0
            with shared.lock:
                if shared.buffs and shared.buffs[0] == attribute:
                    shared.buffs.pop(0)
                if not shared.buffs:
                    tries['restocked'] = False
        return True

    def drain(bot):
        """Hear what arrived since the last tick. Must run before this tick's first request, which clears the inbox."""
        bot._read()
        listen(bot, list(bot.inbox))

    def run(bot, role):
        fighter = (crew_combat.Healer if role.get('healer') else crew_combat.Fighter)(bot, role, records[bot.first])
        engaged = None
        while time.time() - began < minutes * 60:
            drain(bot)
            with shared.lock:
                if shared.ended:
                    break
            row = crew_combat.self_row(bot, records[bot.first])
            with shared.lock:
                shared.table[bot.first] = row
            if row['posture'] in crew_combat.DOWN:
                bot.doing(f'down ({row["posture"]})')
                if row['posture'] == 'dead':
                    bot.recover()
                bot.idle(TICK)
                continue
            zone_row = who(owner)
            if zone_row:
                last_seen['t'] = time.time()
            elif time.time() - last_seen['t'] > OFFLINE_LIMIT:
                bot.doing(f'{owner} went offline: stopping')
                break
            player = player_now(bot, zone_row.get('oid') if zone_row else None)
            here = row.get('zone') or bot.now.get('zone')
            if not here:  # never walk blind: on 15 Oct the crew walked toward Endor coordinates on Tatooine
                bot.doing('finding out which planet I am on')
                bot.idle(TICK)
                continue
            dx, dy = slots.get(bot.first, (0, -3))
            far = zone_row and not player and row.get('x') is not None and math.hypot(
                float(zone_row.get('worldPositionX', 0)) - row['x'], float(zone_row.get('worldPositionY', 0)) - row['y']) > CATCHUP
            if zone_row and here and (zone_row.get('zone') != here or far) and time.time() - jumped.get(bot.first, 0) > GOTO_PAUSE:
                jumped[bot.first] = time.time()
                bot.doing(f"jumping to {owner} on {zone_row.get('zone')}")
                goto(bot, zone_row.get('zone'), float(zone_row.get('worldPositionX', 0)) + dx,
                     float(zone_row.get('worldPositionY', 0)) + dy)
                bot.status()  # learn the new planet
                continue
            if player:
                if bot is g.leader and player['cell']:   # the player on live_map.py's floor plan, among the crew
                    bot.now['escorted'] = {'name': owner, 'cell': player['cell'], 'lx': player['x'], 'ly': player['y'],
                                           'lz': player.get('z'), 'at': time.time()}
                with shared.lock:
                    shared.player = dict(player)
                    last = shared.trail[-1] if shared.trail else None
                    if player['cell'] and (last is None or last['cell'] != player['cell'] or
                                           math.hypot(player['x'] - last['x'], player['y'] - last['y']) >= TRAIL_STEP):
                        shared.trail.append({k: player[k] for k in ('cell', 'x', 'y', 'z')})
                        del shared.trail[:-TRAIL_KEEP]
                    elif not player['cell'] and shared.trail:
                        shared.trail.clear()   # outdoors again: the next building starts a new trail
                if bot is g.leader and time.time() - flushed['snap'] >= 10:
                    flushed['snap'] = time.time()
                    note_play({'kind': 'player', 'health': round(player['health'], 3), 'fighting': player['fighting'],
                               'target': player['target'], 'posture': player['posture'], 'indoors': bool(player['cell'])})
            acted = False
            if role.get('healer'):
                with shared.lock:
                    patients = dict(shared.table)
                    heal_now, shared.heal_now = shared.heal_now, False
                if player and (player['cell'] or 0) == (row.get('cell') or 0):
                    patients[owner] = dict(player, health=0.0 if heal_now else player['health'])
                if fighter.mend(row, patients):
                    bot.doing('healing the lowest of the crew')
                    acted = True
                elif player and shared.buffs:
                    acted = buff(bot, row, player)
            if not acted:
                target = target_for(bot, player)
                if target and (row.get('cell') or 0) == (player or {}).get('cell', 0):
                    if engaged != target['oid']:
                        engaged = target['oid']
                        counts[bot.first]['fights'] += 1
                        fighter.open(target['oid'])
                    bot.doing(f"fighting {target['name']} with {owner}")
                    fighter.strike(row, target)
                    acted = True
                else:
                    engaged = None
            if not acted:
                with shared.lock:
                    mode = shared.mode
                if mode == 'stay':
                    bot.doing(f'holding position ({owner} said stay)')
                else:
                    follow(bot, row, player, zone_row)
            bot.idle(TICK)
        bot.doing('dismissed' if shared.ended else 'escort over')
        records[bot.first]['end'] = shared.table.get(bot.first, {}).get('posture')

    for bot in g.bots:
        bot.status()
        if bot.oid:
            crew_oids.add(bot.oid)
    start = who(owner)
    if start and g.leader.oid:
        g.leader.slash('invite', target=start.get('oid'), wait=1)   # the player accepts the group window
        g.leader.say(f'{g.name} crew here. Orders: follow, stay, attack, passive, heal, status, dismiss.')
    g.parallel(*[lambda b=b: run(b, roles[b.first]) for b in g.bots if b.first in roles])
    flush()
    for rec in records.values():
        rec['sent'], rec['refused'] = dict(rec['sent']), dict(rec['refused'].most_common(6))
    return {'play_data': str(play_file), 'minutes': round((time.time() - began) / 60, 1), 'orders': shared.log, 'counts': counts, 'crew': records,
            'owner_seen': start is not None}
