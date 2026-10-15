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


def _indoors(row, obj):
    """(z, cell) for a move inside the bot's building cell (positions there are cell-local), else (None, None)."""
    return (obj.get('z', 0.0), row['cell']) if row.get('cell') else (None, None)


def _toward(me, obj, stop):
    """A point `stop` metres short of obj on the line from me."""
    dx, dy = obj['x'] - me['x'], obj['y'] - me['y']
    d = math.hypot(dx, dy) or 1.0
    return obj['x'] - dx / d * stop, obj['y'] - dy / d * stop


class Fighter:
    """One bot's side of a fight, one tick at a time (fight() below, and escort.py). Talks only to its own bot."""

    def __init__(self, bot, role, record):
        self.bot, self.role, self.rec = bot, role, record
        self.turn, self.last_ok, self._rotation = 0, True, None

    def rotation(self):
        if self._rotation is None:
            self._rotation = specials(self.bot.profession('list').get('skills', []), self.role.get('weapon', ''))
            self.rec['rotation'] = len(self._rotation)
        return self._rotation

    def send(self, name, to):
        events = self.bot.slash(name, target=to, wait=.4)
        self.rec['sent'][name] += 1
        refused = [e for e in events if e.get('event') == 'command_failed']
        for e in refused:
            self.rec['refused'][f"{name}: {e.get('reason') or e.get('error')}"] += 1
        return not refused

    def open(self, target):
        for call in self.role.get('opener', []):
            self.send(call, target)

    def strike(self, row, obj):
        """Close to reach if needed, then one attack: a special while the last one landed; the plain attack
        after a refusal (cooldown, action) and every third tick, as a player would weave them."""
        gap = math.hypot(obj['x'] - row['x'], obj['y'] - row['y']) if row.get('x') is not None else 0
        ranged = self.role.get('ranged')
        if gap > (self.role.get('reach', RANGED_REACH) if ranged else MELEE_REACH):
            x, y = _toward(row, obj, self.role.get('stand', RANGED_STAND) if ranged else 1.5)
            self.bot.move(x, y, *_indoors(row, obj), timeout=8)
            self.rec['moves'] += 1
        rotation = self.rotation()
        if rotation and self.last_ok and self.turn % 3 != 2:
            self.last_ok = self.send(rotation[self.turn % len(rotation)], obj['oid'])
        else:
            self.send('attack', obj['oid'])
            self.last_ok = True
        self.turn += 1


class Healer(Fighter):
    def mend(self, row, patients):
        """Heal the lowest of patients (name -> {'health': ratio, 'posture', 'x', 'y', 'oid'}) under HEAL_BELOW.
        True when someone needed it."""
        hurt = sorted(((r['health'], name, r) for name, r in patients.items()
                       if r.get('posture') not in DOWN and r.get('health', 1) < HEAL_BELOW and r.get('oid')),
                      key=lambda t: t[0])
        if not hurt:
            return False
        _, name, patient = hurt[0]
        if row.get('x') is not None and patient.get('x') is not None and                 math.hypot(patient['x'] - row['x'], patient['y'] - row['y']) > HEAL_REACH:
            self.bot.move(patient['x'] + 1.5, patient['y'], *_indoors(row, patient), timeout=8)
            self.rec['moves'] += 1
        if self.send('healDamage', patient['oid']):
            self.rec['heals'] += 1
        return True


def new_record():
    return {'sent': collections.Counter(), 'refused': collections.Counter(), 'moves': 0, 'lowest_health': 1.0,
            'heals': 0, 'end': None}


def self_row(bot, rec=None):
    """The bot's own health ratio, posture and position, from its status."""
    me = bot.status()
    ham, top = me.get('me', {}).get('ham', {}), me.get('me', {}).get('max_ham', {})
    ratio = ham.get('health', 0) / top['health'] if top.get('health') else 1.0
    if rec is not None:
        rec['lowest_health'] = round(min(rec['lowest_health'], ratio), 2)
    return {'health': ratio, 'posture': me.get('me', {}).get('posture'), 'x': me.get('x'), 'y': me.get('y'),
            'oid': me.get('self'), 'cell': me.get('cell') or 0, 'zone': me.get('planet')}


def fight(g, target, roles, seconds=180):
    stop = threading.Event()
    table = {}             # first name -> {'health': ratio, 'posture', 'x', 'y', 'oid'}
    lock = threading.Lock()
    record = {b.first: new_record() for b in g.bots if b.first in roles}
    outcome = {'result': 'timeout', 'seconds': None}
    began = time.time()

    def note_self(bot):
        row = self_row(bot, record[bot.first])
        with lock:
            table[bot.first] = row
        return row

    def drive(bot, role):
        fighter = Fighter(bot, role, record[bot.first])
        fighter.rotation()
        fighter.open(target)
        while not stop.is_set() and time.time() - began < seconds:
            row = note_self(bot)
            if row['posture'] in DOWN:
                break
            obj = _seek(bot, target)
            if obj is None or obj.get('posture') in DOWN:
                outcome['result'] = 'target ' + (obj.get('posture') if obj else 'gone')
                stop.set()
                break
            fighter.strike(row, obj)
            bot.idle(TICK)
        record[bot.first]['end'] = table.get(bot.first, {}).get('posture')

    def heal(bot, role):
        healer = Healer(bot, role, record[bot.first])
        while not stop.is_set() and time.time() - began < seconds:
            row = note_self(bot)
            if row['posture'] in DOWN:
                break
            with lock:
                patients = dict(table)
            if not healer.mend(row, patients) and role.get('weapon'):
                healer.send('attack', target)
            bot.idle(TICK)
        record[bot.first]['end'] = table.get(bot.first, {}).get('posture')

    jobs = [(lambda b=b, r=roles[b.first]: (heal if r.get('healer') else drive)(b, r)) for b in g.bots if b.first in roles]
    g.parallel(*jobs)
    stop.set()
    outcome['seconds'] = round(time.time() - began, 1)
    for rec in record.values():
        rec['sent'], rec['refused'] = dict(rec['sent']), dict(rec['refused'].most_common(6))
    return dict(outcome, crew=record)
