"""Offline tests for missions.py and the four mission scenarios (Claude, 17 Oct 2026). A fake galaxy plays the server
rules the scenarios rely on (terminals and their offers, the 6-mission cap, deliver and crafting NPCs, a lair, survey,
performance, recon, hunting and bounty completion, the bank share), on a fake clock, without a client."""
import importlib.util
import math
import sys
import types
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))  # missions.py, also under python -I (squad.py runs scenarios from this folder)
import missions as M  # noqa: E402
QUEST_CRC = next(iter(M.QUEST_SCHEMATICS))


class Clock:
    def __init__(self):
        self.now = 1000.0

    def time(self):
        return self.now


class Galaxy:
    """Just enough of the server for the mission helpers."""
    def __init__(self, clock):
        self.clock, self.next_oid, self.objects, self.terminals, self.bots = clock, 5000, {}, [], []
        self.allow_seventh = False   # a server that forgets the cap
        self.disabled_message = True
        self.lair_hits = 3

    def oid(self):
        self.next_oid += 1
        return self.next_oid

    def terminal(self, ttype, x, y):
        template = next(t for t, k in M.TYPES.items() if k == ttype)
        spot = {'oid': self.oid(), 'template': 'object/tangible/terminal/' + template, 'x': x, 'y': y}
        self.terminals.append(spot)
        return spot

    def creature(self, key, x, y):
        oid = self.oid()
        self.objects[oid] = {'oid': oid, 'type': 'CREO', 'name': f'@mob/creature_names:{key}', 'key': key,
                             'template': f'object/mobile/{key}.iff', 'x': x, 'y': y}

    def offers_for(self, bot, ttype):
        here = {'planet': 'tatooine', 'x': bot.x, 'y': bot.y + bot.oid % 97}  # every bot's spawn points differ
        at = lambda dx: dict(here, x=bot.x + dx)
        made = []
        if ttype in ('general', 'imperial', 'rebel'):
            made += [dict(type='destroy', difficulty=6 - i % 3, reward=900 + 10 * i, target='@lair_n:x',
                          start=at(1200 + 50 * i), end=at(1200 + 50 * i)) for i in range(6)]
            made += [dict(type='deliver', difficulty=5, reward=60 + i, start=at(50 + 10 * i), end=at(300 + 400 * i))
                     for i in range(6)]
        if ttype in ('scout', 'imperial', 'rebel'):
            made += [dict(type='recon', difficulty=1, reward=300 + i, start=at(1100 + 100 * i)) for i in range(6)]
        if ttype == 'scout':
            made += [dict(type='hunting', difficulty=1 + i % 2, reward=600 + i, target='@mob/creature_names:worrt',
                          start=at(0)) for i in range(6)]
        if ttype == 'artisan':
            made += [dict(type='survey', difficulty=50 + 5 * i, reward=400 + i, target='iron', start=at(0))
                     for i in range(6)]
            made += [dict(type='crafting', difficulty=5, reward=70 + i, start=at(40 + 10 * i), end=at(500))
                     for i in range(6)]
        if ttype == 'entertainer':
            made += [dict(type=k, difficulty=5, reward=150 + i, start=at(100 + 10 * i))
                     for k in ('dancer', 'musician') for i in range(6)]
        if ttype == 'bounty':
            made += [dict(type='bounty', difficulty=37, reward=3000 + i, target='Grevo Tusk', end=at(2000 + 100 * i))
                     for i in range(10)]
        return made

    # what the server does after an accept, a walk, a talk, a fight, a wait
    def accepted(self, bot, record):
        if record['type'] in ('deliver', 'crafting', 'destroy'):
            record['waypoint'] = dict(record['start'])
        if record['type'] in ('deliver', 'crafting'):
            for key, role in (('start', 'target'), ('end', 'destination')):
                oid = self.oid()
                self.objects[oid] = {'oid': oid, 'type': 'CREO', 'name': f'Npc {role}', 'x': record[key]['x'],
                                     'y': record[key]['y'], 'role': role, 'mission': record['oid']}

    def complete(self, bot, record):
        del bot.records[record['oid']]
        bot.bank_credits += record['reward'] // len(self.bots)
        bot.hear('@mission:mission_generic')

    def talk(self, bot, target):
        npc = self.objects[target]
        if npc.get('key') == 'spynet_operative':
            for record in bot.records.values():
                if record['type'] == 'bounty' and 'datapad' in record['container_name']:
                    record['waypoint'] = dict(record['end'])
            return
        record = bot.records.get(npc.get('mission'))
        if record is None:
            return
        if npc['role'] == 'target' and not record.get('picked'):
            record['picked'] = True
            if record['type'] == 'crafting':
                bot.items += [{'oid': self.oid(), 'name': f'@craft_item:part_{n}', 'type': 'TANO', 'part': True}
                              for n in range(2)]
            else:
                bot.items.append({'oid': self.oid(), 'name': '@mission/mission_deliver_neutral_easy:m1l', 'type': 'TANO'})
            record['waypoint'] = dict(record['end'])
        elif npc['role'] == 'destination' and record.get('picked'):
            made = [i for i in bot.items if 'attunement_grid' in i['name']]
            if record['type'] == 'deliver' or made:
                if made:
                    bot.items.remove(made[0])
                self.complete(bot, record)

    def arrive(self, bot):
        for record in list(bot.records.values()):
            if 'datapad' not in record['container_name']:
                continue
            spot = record.get('waypoint') or record.get('start') or {}
            near = math.hypot(spot.get('x', 1e9) - bot.x, spot.get('y', 1e9) - bot.y)
            if record['type'] == 'destroy' and not record.get('lair') and near < 128:
                oid = self.oid()
                record['lair'] = oid
                record['waypoint'] = dict(spot, x=spot['x'] + 40)
                self.objects[oid] = {'oid': oid, 'type': 'TANO', 'name': '@lair_n:tatooine_kreetle_neutral_small',
                                     'x': spot['x'] + 40, 'y': spot['y'], 'mission': record['oid']}
                bot.hear('Transmission Received: ' + M.LOCATED + '.  Mission waypoint has been updated')
            if record['type'] == 'recon' and near < 32:
                self.complete(bot, record)
            if record['type'] == 'bounty' and record.get('waypoint') and near < 256 and not record.get('spawned'):
                oid = self.oid()
                record['spawned'] = oid
                self.objects[oid] = {'oid': oid, 'type': 'CREO', 'name': record['target'], 'x': spot['x'],
                                     'y': spot['y'], 'mission': record['oid']}

    def progress(self, bot):
        if bot.performing and bot.cell:
            kind, since = bot.performing
            for record in list(bot.records.values()):
                if record['type'] == kind and 'datapad' in record['container_name'] \
                        and self.clock.now - since >= 600:
                    self.complete(bot, record)

    def hit(self, bot, target):
        thing = self.objects.get(target)
        if thing is None:
            return {'result': 'target dead'}
        if thing['type'] == 'TANO':  # the lair
            self.lair_hits -= 1
            if self.lair_hits > 0:
                return {'result': 'timeout'}
        del self.objects[target]
        mission = thing.get('mission')
        owner = next((b for b in self.bots if mission in b.records), None)
        if owner:
            self.complete(owner, owner.records[mission])
        for record in [r for r in bot.records.values() if 'datapad' in r['container_name']]:
            if record['type'] == 'hunting' and thing.get('key') == 'worrt':
                record['kills'] = record.get('kills', 0) + 1
                if record['kills'] >= 15 * record['difficulty']:
                    self.complete(bot, record)
                else:
                    bot.hear('@mission:mission_generic')  # hunting_kills_remaining, truncated like success
        return {'result': 'target dead'}


class Bot:
    def __init__(self, first, galaxy, x=0.0, y=0.0, group=7):
        self.first, self.galaxy, self.x, self.y, self.group_id = first, galaxy, x, y, group
        self.oid = galaxy.oid()
        self.started = galaxy.clock.now
        self.history, self.pending, self.items, self.records = [], [], [], {}
        self.bank_credits, self.cell, self.posture_now, self.performing = 1000, 0, 'upright', None
        self.slashes, self.pages, self.bank_known = [], [], True

    def hear(self, text):
        self.history.append({'event': 'system', 'text': text, 't': round(self.galaxy.clock.now - self.started, 1)})

    def tick(self, seconds):
        self.galaxy.clock.now += seconds

    def status(self):
        self.tick(0.5)  # a body request's round trip
        reply = {'planet': 'tatooine', 'x': self.x, 'y': self.y, 'cell': self.cell, 'bank_credits': self.bank_credits,
                 'me': {'group': self.group_id, 'posture': self.posture_now}, 'self': self.oid}
        if not self.bank_known:
            del reply['bank_credits']
        return reply

    def posture(self):
        return self.posture_now

    def recover(self):
        return self.posture_now, self.posture_now

    def locate(self, text, radius=800, x=None, y=None):
        cx, cy = (self.x, self.y) if x is None else (x, y)
        found = [dict(t, distance=math.hypot(t['x'] - cx, t['y'] - cy)) for t in self.galaxy.terminals
                 if text in t['template']]
        found += [dict(o, distance=math.hypot(o['x'] - cx, o['y'] - cy)) for o in self.galaxy.objects.values()
                  if o.get('key') == text]
        if text == 'furniture' and x is not None:  # every building in this galaxy has a chair inside
            found.append({'oid': self.galaxy.oid(), 'template': 'object/tangible/furniture/chair.iff', 'x': x + 2,
                          'y': y, 'cell': 77, 'building': 88, 'local': {'x': 1.0, 'y': 2.0, 'z': 0.5}, 'distance': 2})
        return [o for o in found if o['distance'] <= radius][:30]

    def walk(self, x, y, z=None, cell=None, tries=3):
        if cell:
            self.cell = cell
        else:
            self.tick(math.hypot(x - self.x, y - self.y) / 4.5)
            self.x, self.y, self.cell = x, y, 0
        self.galaxy.arrive(self)
        return {'arrived': True, 'x': x, 'y': y, 'seconds': 1}

    def missions(self):
        return [dict(r) for r in self.records.values()]

    def mission_list(self, terminal, wait=4.0):
        self.tick(wait)
        ttype = M.kind(next(t for t in self.galaxy.terminals if t['oid'] == terminal)['template'])
        if ttype in ('newbie', 'statue'):
            if self.galaxy.disabled_message:
                self.hear(M.DISABLED)
            return self.missions()
        for oid in [o for o, r in self.records.items() if 'mission_bag' in r['container_name']]:
            del self.records[oid]
        for offer in self.galaxy.offers_for(self, ttype):
            oid = self.galaxy.oid()
            self.records[oid] = dict(offer, oid=oid, container_name='@item_n:mission_bag')
        return self.missions()

    def accept_mission(self, mission, terminal, wait=3.0):
        held = [r for r in self.records.values() if 'datapad' in r['container_name']]
        if len(held) >= M.CAP and not self.galaxy.allow_seventh:
            self.hear('@mission:mission_generic')
            return []
        record = self.records[mission]
        record['container_name'] = '@item_n:datapad'
        self.galaxy.accepted(self, record)
        return []

    def idle(self, seconds):
        self.tick(seconds)
        self.galaxy.progress(self)
        return []

    def wait_for(self, match, timeout=10):
        test = match if callable(match) else (lambda e, m=match.lower(): m in str(e).lower().replace("'", '"'))
        for event in list(self.pending):
            if test(event):
                self.pending.remove(event)
                return event
        self.tick(min(timeout, 1))
        return None

    def look(self, radius=64, type='', limit=60):
        return [dict(o, distance=math.hypot(o['x'] - self.x, o['y'] - self.y)) for o in self.galaxy.objects.values()
                if (not type or o['type'] == type) and math.hypot(o['x'] - self.x, o['y'] - self.y) <= radius]

    def find(self, name, radius=96, type='', where=None):
        for o in self.look(radius, type, 400):
            if name.lower() in str(o.get('name', '')).lower() and (where is None or where(o)):
                return o
        return None

    def talk(self, target, wait=3.0):
        self.galaxy.talk(self, target)
        return [{'event': 'npc_says', 'text': 'hello'}]

    def inventory(self):
        return {'items': list(self.items)}

    def fight(self, target, timeout=60):
        self.tick(30)
        return self.galaxy.hit(self, target)

    def gear(self, kit='basic'):
        return {'skipped': 'fake'}

    def profession(self, name):
        return {'skills': ['combat_marksman_master', 'crafting_artisan_novice', 'social_entertainer_novice']}

    def sui_pages(self):
        return {'pages': list(self.pages)}

    def sui_respond(self, page_id, event=0, args=None, wait=2.0):
        self.slashes.append(('sui_respond', page_id, event))
        self.pages = [p for p in self.pages if p['page_id'] != page_id]
        return []

    def select(self, target, radial_id, wait=2.0):
        item = next((i for i in self.items if i['oid'] == target), None)
        name = (item or self.galaxy.objects.get(target) or {}).get('name', '')
        if radial_id == 68 and any(t['oid'] == target and 'terminal_bank' in t['template'] for t in self.galaxy.terminals):
            self.pages.append({'page_id': 900, 'script': 'Script.transfer', 'commands': [
                {'kind': 3, 'narrow': ['transaction.lblStartingFrom', 'Text'], 'wide': ['10000']},
                {'kind': 3, 'narrow': ['transaction.lblStartingTo', 'Text'], 'wide': [str(self.bank_credits)]}]})
        if 'survey_tool' in name:
            self.pending.append({'event': 'survey_resources', 'resources': [{'name': 'Ferrox', 'type': 'iron_smelted'}]})
        elif 'probot' in name and radial_id == 138:
            oid = self.galaxy.oid()
            self.galaxy.objects[oid] = {'oid': oid, 'type': 'CREO', 'name': 'an arakyd probe droid', 'x': self.x + 3,
                                        'y': self.y}
        elif 'seeker' in name and radial_id == 137:
            for record in self.records.values():
                if record['type'] == 'bounty':
                    record['waypoint'] = dict(record['end'])
        self.tick(wait)
        return []

    def request(self, cmd, within=30, **args):
        if cmd == 'craft_add':
            fits = any(i['oid'] == args['target'] and i.get('part') for i in self.items)
            self.pending.append({'event': 'craft_result', 'step': 'ingredient', 'code': 0 if fits else 3})
        return {'ok': True}

    def slash(self, name, args='', target=0, wait=2.0):
        self.slashes.append((name, args))
        self.tick(wait)
        if name == 'agentGear':
            new = {'crafting': 'generic_tool', 'survey': 'survey_tool_mineral', 'instruments': 'slitherhorn',
                   'bounty': None}.get(args)
            if args == 'bounty':
                self.items += [{'oid': self.galaxy.oid(), 'name': '@item_n:mission_bounty_droid_probot', 'type': 'TANO'},
                               {'oid': self.galaxy.oid(), 'name': '@item_n:mission_bounty_droid_seeker', 'type': 'TANO'}]
            elif new:
                self.items.append({'oid': self.galaxy.oid(), 'name': f'@item_n:{new}', 'type': 'TANO'})
            self.pending.append({'event': 'system', 'text': '[agentgear] {"given": true}'})
        elif name == 'agentSkill':
            self.pending.append({'event': 'system', 'text': f'[agentskill] granted {args}'})
        elif name == 'requestcraftingsession':
            self.pending.append({'event': 'craft_schematics', 'schematics': [
                {'index': 0, 'crc': 12345, 'tab': 1}, {'index': 1, 'crc': QUEST_CRC, 'tab': 1}]})
        elif name == 'selectdraftschematic':
            self.items.append({'oid': self.galaxy.oid(), 'name': '@schematic', 'type': 'MSCO'})
        elif name == 'synchronizeduilisten':
            self.pending.append({'event': 'craft_slots', 'slot_count': 2, 'slots': [{'name': 'a'}, {'name': 'b'}]})
        elif name == 'nextcraftingstage' and args == '1':
            self.pending.append({'event': 'craft_result', 'step': 'assembly', 'code': 1})
        elif name == 'createprototype':
            self.items = [i for i in self.items if not i.get('part') and i['type'] != 'MSCO']
            self.items.append({'oid': self.galaxy.oid(), 'name': '@item_n:attunement_grid', 'type': 'TANO'})
            self.pending.append({'event': 'system', 'text': '@system_msg:prototype_transferred'})
        elif name in ('startdance', 'startmusic'):
            kind = 'dancer' if name == 'startdance' else 'musician'
            if kind == 'dancer' or any('slitherhorn' in i['name'] and i.get('held') for i in self.items):
                self.performing = (kind, self.galaxy.clock.now)
                self.hear(f'@performance:{"dance" if kind == "dancer" else "music"}_start_self')
        elif name == 'transferItemMisc':
            box = next(i for i in self.items if i['name'] == '@item_n:inventory')
            for i in self.items:
                if i['oid'] == target:
                    i['held'], i['parent'] = False, box['oid']
        elif name == 'transferItemWeapon':
            for i in self.items:
                if i['oid'] == target:
                    i['held'], i['parent'] = True, self.oid
        elif name in ('stopdance', 'stopmusic'):
            self.performing = None
        elif name == 'requestSurvey':
            self.pending.append({'event': 'survey_results', 'best': {'x': self.x + 10, 'y': self.y, 'percent': 0.7}})
        elif name == 'requestCoreSample':
            for record in [r for r in self.records.values() if 'datapad' in r['container_name']]:
                if record['type'] == 'survey' and math.hypot(record['start']['x'] - self.x,
                                                              record['start']['y'] - self.y) > 1024:
                    self.galaxy.complete(self, record)
        return []


class Group:
    def __init__(self, name, bots):
        self.name, self.bots, self.checks, self.notes = name, bots, [], []

    def __getitem__(self, first):
        return next(b for b in self.bots if b.first == first)

    def check(self, label, ok, detail=''):
        self.checks.append((label, bool(ok), detail))
        return bool(ok)

    def note(self, text):
        self.notes.append(text)

    def parallel(self, *jobs):
        return [job() for job in jobs]

    def passed(self, label):
        return [ok for l, ok, _ in self.checks if l == label]

    def failed(self):
        return [(l, d) for l, ok, d in self.checks if not ok]

    def results(self):
        return sorted(n.split(':')[0][len('RESULT '):] for n in self.notes if n.startswith('RESULT '))


def load(name):
    spec = importlib.util.spec_from_file_location(name.replace('-', '_'), HERE / 'scenarios' / f'{name}.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Base(unittest.TestCase):
    def setUp(self):
        self.clock = Clock()
        self.saved = M.time
        M.time = types.SimpleNamespace(time=self.clock.time)
        self.galaxy = Galaxy(self.clock)

    def tearDown(self):
        M.time = self.saved

    def crew(self, *names, x=3500.0, y=-4800.0):
        bots = [Bot(n, self.galaxy, x + i, y) for i, n in enumerate(names)]
        self.galaxy.bots = bots
        return Group('Test', bots), bots

    def take(self, g, bot, ttype, mtype, choose, divisor):
        terminal = self.galaxy.terminal(ttype, bot.x, bot.y)
        return M.take(g, bot, terminal, ttype, [(mtype, choose)], f'{ttype}/{mtype}', divisor)


class Readers(Base):
    def test_where_skips_the_empty_waypoint_of_a_listed_mission(self):
        m = {'waypoint': {'planet': '0', 'x': 0, 'y': 0}, 'start': {'planet': 'tatooine', 'x': 5, 'y': 6}}
        self.assertEqual(M.where(m)['x'], 5)

    def test_kind_reads_every_terminal_template(self):
        self.assertEqual(M.kind('object/tangible/terminal/terminal_mission.iff'), 'general')
        self.assertEqual(M.kind('object/tangible/terminal/terminal_mission_imperial.iff'), 'imperial')
        self.assertIsNone(M.kind('object/tangible/terminal/terminal_bazaar.iff'))
        self.assertEqual(len(M.TYPES), 9)

    def test_quest_schematic_crc_matches_the_crafting_check(self):
        crafting = load('besh-crafting')
        path = 'object/draft_schematic/item/quest_item/shared_attunement_grid.iff'
        self.assertEqual(M.template_crc(path), crafting.template_crc(path))
        self.assertEqual(sorted(M.QUEST_SCHEMATICS.values()), sorted(M.QUEST_ITEMS))

    def test_an_indoor_bot_searches_from_an_outdoor_teammate(self):
        g, bots = self.crew('Cresh', 'Ilsa', 'Kor')
        bots[0].cell, bots[0].x, bots[0].y = 1105883, -16.7, -10.5  # cell-local, inside the cloning facility
        at = M.search_point(g, bots[0])
        self.assertEqual((at['x'], at['y']), (bots[1].x, bots[1].y))
        self.galaxy.terminal('general', bots[1].x + 40, bots[1].y)
        self.assertEqual(M.find_terminals(bots[0]), {})  # from -17, -10 nothing is in reach
        self.assertIn('general', M.find_terminals(bots[0], at=at))
        bots[0].cell = 0
        self.assertIsNone(M.search_point(g, bots[0]))

    def test_an_indoor_terminal_measures_from_its_world_position(self):
        g, (bot,) = self.crew('Rusk')
        terminal = self.galaxy.terminal('general', bot.x, bot.y)
        bot.mission_list(terminal['oid'])  # offers around the terminal, in world coordinates
        bot.cell, bot.x, bot.y = 1082874, 2.0, -3.0  # then the body reports cell-local x and y
        mission, _, _ = M.take(g, bot, terminal, 'general', [('deliver', M.in_town(bot))], 'general/deliver', 3,
                               listed=[m for m in bot.missions() if M.in_bag(m)])
        self.assertEqual(mission and mission['type'], 'deliver')

    def test_a_teammates_share_in_the_same_window_still_passes(self):
        g, bots = self.crew('Dorn', 'Nima', 'Rusk')
        rusk = bots[2]
        mission = {'oid': 9, 'type': 'musician', 'reward': 157}
        since = M.mark(rusk)
        rusk.hear('@mission:mission_generic')  # Dorn's dancer share
        rusk.hear('@mission:mission_generic')  # his own
        rusk.bank_credits += 96
        done = M.paid(g, rusk, mission, rusk.bank_credits - 96, 3, 'entertainer/musician', since)
        self.assertEqual((done['paid'], done['expected'], done['other_shares']), (96, 52, 44))
        self.assertEqual(g.failed(), [])

    def test_choosers(self):
        g, (bot,) = self.crew('Cresh')
        here = {'planet': 'tatooine', 'x': bot.x, 'y': bot.y}
        town = dict(type='deliver', start=dict(here, x=bot.x + 100), end=dict(here, x=bot.x + 600))
        away = dict(type='deliver', start=dict(here, x=bot.x + 50), end=dict(here, x=bot.x + 4000))
        self.assertIs(M.in_town(bot)([away, town]), town)
        boss = dict(type='destroy', difficulty=3, target='@lair_n:a_boss', start=dict(here, x=bot.x + 1100))
        easy = dict(type='destroy', difficulty=3, target='@lair_n:rat', start=dict(here, x=bot.x + 1900))
        hard = dict(type='destroy', difficulty=2, target='@lair_n:x', start=dict(here, x=bot.x + 2400))
        self.assertIs(M.easiest(bot)([boss, easy, hard]), easy)  # hard is beyond 2300 m
        npc = dict(type='bounty', end=dict(here, x=bot.x + 3000))
        player = dict(type='bounty', end={'planet': '', 'x': 0, 'y': 0})
        self.assertIs(M.npc_bounty(bot, 4000)([player, npc]), npc)
        self.assertEqual(M.lowest([dict(difficulty=60), dict(difficulty=50)])['difficulty'], 50)


class Taking(Base):
    def test_take_accepts_into_the_datapad(self):
        g, (bot,) = self.crew('Cresh')
        mission, before, divisor = self.take(g, bot, 'general', 'deliver', M.in_town(bot), 3)
        self.assertEqual(mission['type'], 'deliver')
        self.assertEqual((before, divisor), (1000, 3))
        self.assertTrue(M.in_datapad(mission))

    def test_take_is_blocked_at_the_cap(self):
        g, (bot,) = self.crew('Ilsa')
        terminal = self.galaxy.terminal('general', bot.x, bot.y)
        for m in [m for m in bot.mission_list(terminal['oid']) if M.in_bag(m)][:M.CAP]:
            bot.accept_mission(m['oid'], terminal['oid'])
        mission, _, _ = M.take(g, bot, terminal, 'general', [('deliver', M.in_town(bot))], 'general/deliver', 1)
        self.assertIsNone(mission)  # a delivery is never reused, and there is no room for another
        self.assertTrue(any('BLOCKED' in n and 'already holds 6' in n for n in g.notes))

    def test_a_held_destroy_mission_is_finished_before_a_new_one_is_taken(self):
        g, (bot,) = self.crew('Cresh')
        first, _, _ = self.take(g, bot, 'general', 'destroy', M.easiest(bot), 3)
        again, _, _ = self.take(g, bot, 'general', 'destroy', M.easiest(bot), 3)
        self.assertEqual(again['oid'], first['oid'])
        self.assertEqual(len(M.held(bot)), 1)
        self.assertTrue(any('finishes a held destroy mission' in n for n in g.notes))

    def test_a_held_delivery_is_never_reused(self):
        g, (bot,) = self.crew('Cresh')
        first, _, _ = self.take(g, bot, 'general', 'deliver', M.in_town(bot), 3)
        again, _, _ = self.take(g, bot, 'general', 'deliver', M.in_town(bot), 3)
        self.assertNotEqual(again['oid'], first['oid'])

    def test_offers_reads_again_when_the_bag_still_holds_another_terminals_list(self):
        g, (bot,) = self.crew('Brask')
        general = self.galaxy.terminal('general', bot.x, bot.y)
        scout = self.galaxy.terminal('scout', bot.x, bot.y)
        bot.mission_list(general['oid'])
        real, calls = bot.mission_list, []

        def lagging(oid, wait=4.0):  # the first scout list still shows the general terminal's types
            calls.append(oid)
            return bot.missions() if len(calls) == 1 else real(oid, wait)
        bot.mission_list = lagging
        listed = M.offers(bot, scout, 'scout')
        self.assertEqual({m['type'] for m in listed}, {'recon', 'hunting'})
        self.assertEqual(len(calls), 2)


class Missions(Base):
    def test_deliver_errand_is_paid_its_share(self):
        g, bots = self.crew('Cresh', 'Ilsa', 'Kor')
        mission, before, divisor = self.take(g, bots[0], 'general', 'deliver', M.in_town(bots[0]), 3)
        done = M.errand(g, bots[0], mission, before, divisor, 'general/deliver')
        self.assertTrue(done['removed'])
        self.assertEqual(done['paid'], mission['reward'] // 3)
        self.assertEqual(g.failed(), [])
        self.assertEqual(g.results(), ['general/deliver'])

    def test_a_wrong_payment_fails_the_bank_check(self):
        g, bots = self.crew('Cresh', 'Ilsa', 'Kor')
        mission, before, _ = self.take(g, bots[0], 'general', 'deliver', M.in_town(bots[0]), 1)
        done = M.errand(g, bots[0], mission, before, 1, 'general/deliver')  # the fake pays a third
        self.assertEqual(g.passed('general/deliver: the share reaches the bank'), [False])
        self.assertEqual(done['expected'], mission['reward'])

    def test_destroy_spawns_moves_and_completes(self):
        g, bots = self.crew('Cresh', 'Ilsa', 'Kor')
        mission, _, divisor = self.take(g, bots[0], 'general', 'destroy', M.easiest(bots[0]), 3)
        self.assertEqual(mission['difficulty'], 4)  # the lowest difficulty within reach
        done = M.destroy(g, bots, mission, M.bank(bots[0]), divisor, 'general/destroy')
        self.assertTrue(done['removed'])
        self.assertEqual(g.failed(), [])
        self.assertEqual(done['shares'], {'Ilsa': 0, 'Kor': 0, 'Cresh': mission['reward'] // 3})  # the fake pays the owner

    def test_guarded_walk_fights_what_waits_on_the_route(self):
        g, bots = self.crew('Cresh', 'Ilsa', 'Kor')
        start = bots[0].x
        self.galaxy.creature('kreetle', start + 500, bots[0].y + 5)  # on the second leg's end
        bots[1].posture_now = 'incapacitated'
        real_idle = bots[0].idle

        def idle(seconds):  # Ilsa gets up after a while
            bots[1].posture_now = 'upright'
            return real_idle(seconds)
        bots[0].idle = idle
        trip = M.guarded_walk(g, bots, {'x': start + 900, 'y': bots[0].y}, 'test')
        self.assertTrue(trip['arrived'])
        self.assertEqual(trip['fights'], 1)
        self.assertEqual(trip['downed'], ['Ilsa'])
        self.assertFalse([o for o in self.galaxy.objects.values() if o.get('key') == 'kreetle'])

    def test_guarded_walk_gives_up_when_the_bot_does_not_move(self):
        g, (dask,) = self.crew('Dask')
        dask.walk = lambda x, y, z=None, cell=None, tries=3: {'ok': False, 'error': 'destination more than 2 km away'}
        started = self.clock.now
        trip = M.guarded_walk(g, [dask], {'x': dask.x + 3300, 'y': dask.y}, 'imperial/recon')
        self.assertFalse(trip['arrived'])
        self.assertLess(self.clock.now - started, 60)  # three stalled legs, not 15 minutes
        self.assertTrue(any('stopped' in n for n in g.notes))

    def test_crafting_errand_crafts_the_quest_item(self):
        g, bots = self.crew('Besh', 'Dova', 'Pell', 'Varo')
        dova = bots[1]
        mission, before, divisor = self.take(g, dova, 'artisan', 'crafting', M.in_town(dova), 4)
        done = M.crafting(g, dova, mission, before, divisor, 'artisan/crafting')
        self.assertEqual(g.failed(), [])
        self.assertEqual(done['paid'], mission['reward'] // 4)
        self.assertIn(('createprototype', '3 1'), dova.slashes)

    def test_crafting_without_the_schematic_is_unfinished(self):
        g, bots = self.crew('Besh', 'Dova', 'Pell', 'Varo')
        dova = bots[1]
        mission, before, divisor = self.take(g, dova, 'artisan', 'crafting', M.in_town(dova), 4)
        saved, M.QUEST_SCHEMATICS = M.QUEST_SCHEMATICS, {1: 'none'}
        try:
            done = M.crafting(g, dova, mission, before, divisor, 'artisan/crafting')
        finally:
            M.QUEST_SCHEMATICS = saved
        self.assertEqual(done['unfinished'], 'crafting failed')
        self.assertEqual(g.passed('artisan/crafting: the mission schematic is on the tool'), [False])

    def test_survey_walks_past_1024_m_and_samples(self):
        g, bots = self.crew('Besh', 'Dova', 'Pell', 'Varo')
        dova, varo = bots[1], bots[3]
        mission, before, divisor = self.take(g, dova, 'artisan', 'survey', M.lowest, 4)
        self.assertEqual(mission['difficulty'], 50)
        done = M.survey(g, dova, mission, before, divisor, 'artisan/survey', guard=varo)
        self.assertEqual(g.failed(), [])
        self.assertTrue(done['removed'])
        self.assertEqual(done['density'], 70.0)  # the body's 0.7 read as 70%
        self.assertGreater(math.hypot(dova.x - mission['start']['x'], dova.y - mission['start']['y']), 1024)

    def test_dancer_and_musician_perform_inside_for_ten_minutes(self):
        g, bots = self.crew('Dorn', 'Nima', 'Rusk')
        for bot, kind in ((bots[0], 'dancer'), (bots[1], 'musician')):
            mission, before, divisor = self.take(g, bot, 'entertainer', kind, M.nearest(bot), 3)
            started = self.clock.now
            done = M.perform(g, bot, mission, before, divisor, f'entertainer/{kind}')
            self.assertTrue(done['removed'], kind)
            self.assertGreaterEqual(self.clock.now - started, 600)
        self.assertEqual(g.failed(), [])

    def test_the_held_weapon_goes_away_before_the_instrument(self):
        g, (nima,) = self.crew('Nima')
        box = {'oid': 1, 'name': '@item_n:inventory', 'type': 'TANO', 'parent': nima.oid}
        pistol = {'oid': 2, 'name': '@weapon_name:pistol_cdef', 'type': 'WEAO', 'parent': nima.oid}
        horn = {'oid': 3, 'name': '@obj_n:obj_slitherhorn', 'type': 'TANO', 'parent': 1}
        nima.items += [box, pistol, horn]
        self.assertTrue(M.hold(nima, horn))
        self.assertEqual(nima.slashes[:2], [('transferItemMisc', '1 -1 0 0 0'), ('transferItemWeapon', f'{nima.oid} 4 0 0 0')])
        self.assertEqual(pistol['parent'], 1)

    def test_the_bank_comes_from_the_terminal_window_when_the_body_lost_it(self):
        g, (bot,) = self.crew('Kor')
        bank = {'oid': 77, 'template': 'object/tangible/terminal/terminal_bank.iff', 'x': bot.x + 2000, 'y': bot.y}
        self.galaxy.terminals.append(bank)
        bot.bank_known, bot.bank_credits = False, 100000
        self.assertEqual(M.bank(bot), 100000)
        self.assertIn(('sui_respond', 900, 1), bot.slashes)  # cancelled: nothing moves
        self.assertEqual(bot.pages, [])

    def test_a_full_inventory_takes_no_delivery(self):
        g, (bot,) = self.crew('Cresh')
        bot.items = [{'oid': 1, 'name': '@item_n:inventory', 'type': 'TANO', 'parent': bot.oid}] + [
            {'oid': 10 + i, 'name': '@medicine_name:stimpack_sm_s1_a', 'type': 'TANO', 'parent': 1} for i in range(80)]
        self.assertEqual(M.room(bot), 0)
        mission, _, _ = self.take(g, bot, 'general', 'deliver', M.in_town(bot), 3)
        self.assertIsNone(mission)
        self.assertFalse(M.held(bot))
        self.assertTrue(any('inventory is full (80 of 80)' in n for n in g.notes))

    def test_only_the_truncated_success_counts(self):
        g, (bot,) = self.crew('Cresh')
        since = M.mark(bot)
        bot.hear('@mission/mission_generic:group_too_far')
        bot.hear('@mission/mission_generic:group_success')
        self.assertEqual(M.success(bot, since), [])
        bot.hear('@mission:mission_generic')
        self.assertEqual(M.success(bot, since), ['@mission:mission_generic'])

    def test_recon_is_paid_on_entering_the_area(self):
        g, bots = self.crew('Forn', 'Brask', 'Dask', 'Ressa', 'Mirren')
        mission, before, divisor = self.take(g, bots[1], 'scout', 'recon', M.nearest(bots[1], limit=3000), 5)
        done = M.recon(g, bots[1], mission, before, divisor, 'scout/recon')
        self.assertEqual(done['paid'], mission['reward'] // 5)
        self.assertEqual(mission['reward'], 300)  # the nearest recon

    def test_hunting_counts_kills_until_done(self):
        g, bots = self.crew('Forn', 'Brask', 'Dask', 'Ressa', 'Mirren')
        for i in range(20):
            self.galaxy.creature('worrt', bots[0].x + 200 + 5 * i, bots[0].y)
        mission, before, divisor = self.take(g, bots[0], 'scout', 'hunting', M.hunting_choice(bots[0]), 5)
        self.assertEqual(mission['difficulty'], 1)
        done = M.hunt(g, bots[0], mission, before, divisor, 'scout/hunting')
        self.assertEqual(done['kills'], 15)
        self.assertTrue(done['removed'])

    def test_hunting_without_prey_is_unfinished(self):
        g, (bot,) = self.crew('Forn')
        mission = {'oid': 1, 'type': 'hunting', 'target': '@mob/creature_names:zz', 'difficulty': 1, 'reward': 600}
        bot.records[1] = dict(mission, container_name='@item_n:datapad')
        done = M.hunt(g, bot, mission, 1000, 5, 'scout/hunting', minutes=1)
        self.assertFalse(done['removed'])
        self.assertIn('0 of 15', done['unfinished'])

    def test_level_one_bounty_goes_through_the_informant(self):
        g, bots = self.crew('Forn', 'Brask', 'Dask', 'Ressa', 'Mirren')
        ressa = bots[3]
        terminal = self.galaxy.terminal('bounty', ressa.x, ressa.y)
        self.galaxy.creature('spynet_operative', ressa.x - 50, ressa.y)
        done = M.bounty(g, ressa, terminal, 'bounty/bounty', 5)
        self.assertEqual(g.failed(), [])
        self.assertEqual(done['paid'], 3000 // 5)
        self.assertIn(('agentSkill', 'combat_bountyhunter_novice'), ressa.slashes)
        self.assertFalse([n for n, *_ in ressa.slashes if n == 'agentGear'])  # no droids at level 1

    def test_bounty_without_an_informant_is_unfinished(self):
        g, bots = self.crew('Forn', 'Brask', 'Dask', 'Ressa', 'Mirren')
        terminal = self.galaxy.terminal('bounty', bots[3].x, bots[3].y)
        done = M.bounty(g, bots[3], terminal, 'bounty/bounty', 5)
        self.assertEqual(done['unfinished'], 'no level-1 informant')

    def test_survey_classes_match_the_listed_types(self):
        self.assertTrue(M.in_family('aluminum_agrinium', 'non-ferrous_metal'))
        self.assertTrue(M.in_family('copper_diatium', 'non-ferrous_metal'))
        self.assertFalse(M.in_family('iron_axidite', 'non-ferrous_metal'))
        self.assertTrue(M.in_family('steel_kiirium', 'ferrous_metal'))
        self.assertTrue(M.in_family('ore_siliclastic_crism', 'sedimentary_ore'))
        self.assertTrue(M.in_family('iron_plumbum', 'iron'))  # not in the table: its own word

    def test_faction_terminal_prefers_an_in_town_delivery(self):
        g, bots = self.crew('Forn', 'Brask', 'Dask', 'Ressa', 'Mirren')
        terminal = self.galaxy.terminal('imperial', bots[3].x, bots[3].y)
        done = M.faction(g, bots[3], terminal, 'imperial', 5)
        self.assertEqual(done['type'], 'deliver')
        self.assertEqual(g.results(), ['imperial/deliver'])


class Cap(Base):
    def test_the_seventh_is_refused(self):
        g, (ilsa,) = self.crew('Ilsa')
        done = M.cap(g, ilsa, self.galaxy.terminal('general', ilsa.x, ilsa.y))
        self.assertTrue(done['refused'])
        self.assertEqual(done['held'], 6)
        self.assertEqual(g.failed(), [])

    def test_a_server_that_takes_a_seventh_fails(self):
        g, (ilsa,) = self.crew('Ilsa')
        self.galaxy.allow_seventh = True
        done = M.cap(g, ilsa, self.galaxy.terminal('general', ilsa.x, ilsa.y))
        self.assertFalse(done['refused'])
        self.assertEqual(g.passed('general/cap: the 7th mission is refused'), [False])

    def test_a_later_run_only_tries_the_seventh(self):
        g, (ilsa,) = self.crew('Ilsa')
        terminal = self.galaxy.terminal('general', ilsa.x, ilsa.y)
        M.cap(g, ilsa, terminal)
        self.assertTrue(M.cap(g, ilsa, terminal)['refused'])
        self.assertEqual(len(M.held(ilsa)), 6)

    def test_disabled_terminals(self):
        g, (kor,) = self.crew('Kor')
        newbie = self.galaxy.terminal('newbie', kor.x + 30, kor.y)
        self.assertTrue(M.disabled(g, kor, newbie, 'newbie')['refused'])
        self.galaxy.disabled_message = False
        self.assertFalse(M.disabled(g, kor, newbie, 'newbie')['refused'])


class Scenarios(Base):
    def test_cresh_missions(self):
        g, bots = self.crew('Cresh', 'Ilsa', 'Kor')
        self.galaxy.terminal('general', bots[0].x + 20, bots[0].y)
        self.galaxy.terminal('statue', bots[0].x + 60, bots[0].y)
        load('cresh-missions').run(g)
        self.assertEqual(g.failed(), [])
        self.assertEqual(g.results(), ['general/cap', 'general/deliver', 'general/destroy', 'statue/list'])
        self.assertTrue(any(n.startswith('TERMINALS') for n in g.notes))
        self.assertTrue(any(n.startswith('RESULTS ') for n in g.notes))

    def test_besh_missions(self):
        g, bots = self.crew('Besh', 'Dova', 'Pell', 'Varo')
        self.galaxy.terminal('artisan', bots[1].x + 20, bots[1].y)
        load('besh-missions').run(g)
        self.assertEqual(g.failed(), [])
        self.assertEqual(g.results(), ['artisan/crafting', 'artisan/survey'])

    def test_dorn_missions(self):
        g, bots = self.crew('Dorn', 'Nima', 'Rusk')
        self.galaxy.terminal('entertainer', bots[0].x + 20, bots[0].y)
        self.galaxy.terminal('general', bots[0].x + 60, bots[0].y)
        load('dorn-missions').run(g)
        self.assertEqual(g.failed(), [])
        self.assertEqual(g.results(), ['entertainer/dancer', 'entertainer/musician', 'general/deliver'])

    def test_forn_missions(self):
        g, bots = self.crew('Forn', 'Brask', 'Dask', 'Ressa', 'Mirren')
        for ttype in ('scout', 'bounty', 'imperial', 'rebel'):
            self.galaxy.terminal(ttype, bots[0].x + 20, bots[0].y)
        for i in range(20):
            self.galaxy.creature('worrt', bots[0].x + 200 + 5 * i, bots[0].y)
        self.galaxy.creature('spynet_operative', bots[0].x - 50, bots[0].y)
        load('forn-missions').run(g)
        self.assertEqual(g.failed(), [])
        self.assertEqual(g.results(), ['bounty/bounty', 'imperial/deliver', 'rebel/deliver', 'scout/hunting',
                                       'scout/recon'])


if __name__ == '__main__':
    unittest.main()
