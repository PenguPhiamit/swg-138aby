"""Group combat with real rotations, for the dungeon crew (Claude, 15 Oct 2026; owner: "give me a crew and we can
test their combat more and their movement and mapping").

The bot body's own fight reflex (AgentControl::fight) walks into melee range and sends only the default attack every
2 s, so riflemen punch and nobody uses a special. Here every fighter cycles through the special attacks it holds for
the weapon in its hands (Claude-class-check/commands.json, read from the server's command tables), ranged fighters
keep their distance, the squad leader opens with its group calls, and the healer heals whoever is lowest.

    record = fight(g, target_oid, roles, seconds=180)
    roles: first name -> {'weapon': WEAPON key ('rifle', 'polearm', '1h melee', 'unarmed', 'special heavy ...'),
                          'ranged': bool, 'stand'/'reach': metres for a ranged fighter (default 22/45),
                          'healer': bool, 'opener': [group calls sent once at the start]}

One thread per bot, and each thread only ever talks to its own bot: a request resets that bot's inbox, so the healer
reads its teammates' health from the table the fighters fill each tick, never from their bots.
"""
import collections
import json
import math
import threading
import time
from pathlib import Path

COMMANDS = Path(__file__).resolve().parents[2] / 'Claude-class-check' / 'commands.json'
TICK = 2.0             # the body's own fight reflex attacks every 2 s
MELEE_REACH = 4.0      # m; the reflex closes to 1.5 m and attacks inside 3.5 m
RANGED_STAND = 22.0    # where a ranged fighter stops when it has to close in
RANGED_REACH = 45.0
HEAL_BELOW = .7        # the healer acts on anyone under 70% health
HEAL_REACH = 5.0
DOWN = ('incapacitated', 'dead')


def specials(skills, weapon):
    """Attacks the bot holds for this weapon class, in the order the tables list them."""
    held = set(skills)
    rows = json.loads(COMMANDS.read_text(encoding='utf-8'))['commands']
    return [r['slash'] for r in rows
            if r.get('test_kind') == 'attack' and r.get('slash') and 'weapon:' + weapon in r.get('setup_tags', [])
            and any(g.get('box') in held for g in r.get('granted_by', []))]


def _seek(bot, target):
    obj = next((o for o in bot.look(80, 'CREO', 400) if o.get('oid') == target), None)
    return obj


def _toward(me, obj, stop):
    """A point `stop` metres short of obj on the line from me."""
    dx, dy = obj['x'] - me['x'], obj['y'] - me['y']
    d = math.hypot(dx, dy) or 1.0
    return obj['x'] - dx / d * stop, obj['y'] - dy / d * stop


def fight(g, target, roles, seconds=180):
    stop = threading.Event()
    table = {}             # first name -> {'health': ratio, 'posture', 'x', 'y', 'oid'}
    lock = threading.Lock()
    record = {b.first: {'sent': collections.Counter(), 'refused': collections.Counter(), 'moves': 0,
                        'lowest_health': 1.0, 'heals': 0, 'end': None} for b in g.bots if b.first in roles}
    outcome = {'result': 'timeout', 'seconds': None}
    began = time.time()

    def note_self(bot):
        me = bot.status()
        ham, top = me.get('me', {}).get('ham', {}), me.get('me', {}).get('max_ham', {})
        ratio = ham.get('health', 0) / top['health'] if top.get('health') else 1.0
        row = {'health': ratio, 'posture': me.get('me', {}).get('posture'), 'x': me.get('x'), 'y': me.get('y'),
               'oid': me.get('self')}
        with lock:
            table[bot.first] = row
        rec = record[bot.first]
        rec['lowest_health'] = round(min(rec['lowest_health'], ratio), 2)
        return me, row

    def send(bot, name, to):
        events = bot.slash(name, target=to, wait=.4)
        record[bot.first]['sent'][name] += 1
        refused = [e for e in events if e.get('event') == 'command_failed']
        for e in refused:
            record[bot.first]['refused'][f"{name}: {e.get('reason') or e.get('error')}"] += 1
        return not refused

    def drive(bot, role):
        rotation = specials(bot.profession('list').get('skills', []), role['weapon'])
        record[bot.first]['rotation'] = len(rotation)
        for call in role.get('opener', []):
            send(bot, call, target)
        turn, last_ok = 0, True
        while not stop.is_set() and time.time() - began < seconds:
            me, row = note_self(bot)
            if row['posture'] in DOWN:
                break
            obj = _seek(bot, target)
            if obj is None or obj.get('posture') in DOWN:
                outcome['result'] = 'target ' + (obj.get('posture') if obj else 'gone')
                stop.set()
                break
            gap = math.hypot(obj['x'] - row['x'], obj['y'] - row['y']) if row['x'] is not None else 0
            reach = role.get('reach', RANGED_REACH) if role.get('ranged') else MELEE_REACH
            if gap > reach:
                x, y = _toward(row, obj, role.get('stand', RANGED_STAND) if role.get('ranged') else 1.5)
                bot.move(x, y, timeout=8)
                record[bot.first]['moves'] += 1
            # A special while the last one landed; the plain attack after a refusal (cooldown, action) and every
            # third tick, as a player would weave them.
            if rotation and last_ok and turn % 3 != 2:
                last_ok = send(bot, rotation[turn % len(rotation)], target)
            else:
                send(bot, 'attack', target)
                last_ok = True
            turn += 1
            bot.idle(TICK)
        record[bot.first]['end'] = table.get(bot.first, {}).get('posture')

    def heal(bot, role):
        while not stop.is_set() and time.time() - began < seconds:
            me, row = note_self(bot)
            if row['posture'] in DOWN:
                break
            with lock:
                hurt = sorted(((r['health'], name, r) for name, r in table.items()
                               if r['posture'] not in DOWN and r['health'] < HEAL_BELOW), key=lambda t: t[0])
            if hurt:
                _, name, patient = hurt[0]
                if row['x'] is not None and patient['x'] is not None and \
                        math.hypot(patient['x'] - row['x'], patient['y'] - row['y']) > HEAL_REACH:
                    bot.move(patient['x'] + 1.5, patient['y'], timeout=8)
                    record[bot.first]['moves'] += 1
                if send(bot, 'healDamage', patient['oid']):
                    record[bot.first]['heals'] += 1
            elif role.get('weapon'):
                send(bot, 'attack', target)
            bot.idle(TICK)
        record[bot.first]['end'] = table.get(bot.first, {}).get('posture')

    jobs = [(lambda b=b, r=roles[b.first]: (heal if r.get('healer') else drive)(b, r)) for b in g.bots if b.first in roles]
    g.parallel(*jobs)
    stop.set()
    outcome['seconds'] = round(time.time() - began, 1)
    for rec in record.values():
        rec['sent'], rec['refused'] = dict(rec['sent']), dict(rec['refused'].most_common(6))
    return dict(outcome, crew=record)
