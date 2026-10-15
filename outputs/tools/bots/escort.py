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
Orders, from the player by spatial chat or a tell to any crew member (a leading "crew" is optional):
  follow | stay | attack | passive | heal | status | dismiss
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
FORMATION = [(3, 2), (-3, 2), (0, -4), (3, -4), (-3, -4), (5, 0), (-5, 0), (0, 5)]   # metres from the player
ORDERS = ('follow', 'stay', 'attack', 'passive', 'heal', 'status', 'dismiss')


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
            elif verb == 'dismiss':
                self.ended = True
            self.log.append((round(now), verb))
            return verb


ACK = {'follow': 'Following.', 'stay': 'Holding here.', 'attack': 'Engaging your target.', 'passive': 'Weapons down.',
       'heal': 'Healing you.', 'dismiss': 'Crew dismissed.'}


def escort(g, owner, roles, minutes=120, formation=None):
    shared = Shared(owner)
    slots = dict(zip([b.first for b in g.bots], formation or FORMATION))
    crew_oids = set()
    records = {b.first: crew_combat.new_record() for b in g.bots if b.first in roles}
    counts = {b.first: {'fights': 0, 'follows': 0, 'orders': 0} for b in g.bots if b.first in roles}
    began, last_seen = time.time(), {'t': time.time()}
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
        if player and player['x'] is not None:
            spot = (player['x'] + dx, player['y'] + dy)
            same_frame = (player['cell'] or 0) == (row.get('cell') or 0)
            far = not same_frame or row.get('x') is None or math.hypot(spot[0] - row['x'], spot[1] - row['y']) > SLACK
            if far:
                bot.doing(f'following {owner}' + (' inside' if player['cell'] else ''))
                if player['cell']:
                    bot.move(spot[0], spot[1], player.get('z') or 0.0, player['cell'], timeout=15)
                else:
                    bot.move(spot[0], spot[1], timeout=15)
                counts[bot.first]['follows'] += 1
            else:
                bot.doing(f'with {owner}')
        elif zone_row:
            # Out of sight: walk toward who.json's world position (outdoors) on the same planet.
            bot.doing(f'catching up with {owner}')
            bot.move(float(zone_row.get('worldPositionX', 0)) + dx, float(zone_row.get('worldPositionY', 0)) + dy, timeout=30)

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
            here = bot.now.get('zone')
            if zone_row and here and zone_row.get('zone') != here:
                bot.doing(f"waiting: {owner} is on {zone_row.get('zone')}")
                bot.idle(TICK)
                continue
            if player:
                with shared.lock:
                    shared.player = dict(player)
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
