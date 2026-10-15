"""Offline tests for escort.py (Claude, 15 Oct 2026): orders, and one short escort with fake bots."""
import json
import tempfile
import threading
import time
import unittest
from pathlib import Path

import escort

OWNER, PREY = 7, 500


class Bot:
    def __init__(self, first, oid, view):
        self.first, self.oid, self.view = first, oid, view
        self.inbox, self.sent, self.moves, self.said, self.labels = [], [], [], [], []
        self.arriving = []   # events the server sends during the next idle
        self.now = {'zone': 'tatooine'}
        self.planet = 'tatooine'

    def _read(self):
        pass

    def status(self):
        self.inbox = []
        return {'me': {'ham': {'health': 1000}, 'max_ham': {'health': 1000}, 'posture': 'upright'},
                'x': 100.0, 'y': 90.0, 'self': self.oid, 'cell': 0, 'planet': self.planet}

    def inspect(self, oid):
        return self.view.get(oid, {'ok': False})

    def slash(self, name, args='', target=0, wait=0):
        self.sent.append((name, target))
        return []

    def wait_for(self, match, timeout=10):
        return None

    def move(self, x, y, z=None, cell=None, timeout=90):
        self.moves.append((round(x), round(y)))
        return dict(self.move_reply) if hasattr(self, 'move_reply') else {}

    def idle(self, seconds):
        time.sleep(.005)
        self.inbox += self.arriving
        self.arriving = []
        return list(self.inbox)

    def say(self, text):
        self.said.append(text)

    def profession(self, name):
        return {'skills': ['combat_rifleman_novice']}

    def doing(self, text):
        self.labels.append(text)

    def recover(self):
        pass


class Group:
    name = 'Forn'

    def __init__(self, bots):
        self.bots = bots

    @property
    def leader(self):
        return self.bots[0]

    def parallel(self, *jobs):
        threads = [threading.Thread(target=job) for job in jobs]
        for t in threads:
            t.start()
        for t in threads:
            t.join()


class Orders(unittest.TestCase):
    def test_words(self):
        self.assertEqual(escort.word('crew, stay!'), 'stay')
        self.assertEqual(escort.word('Follow'), 'follow')
        self.assertIsNone(escort.word('stay here please crew'.replace('stay', 'wait')))
        self.assertIsNone(escort.word('hello crew'))

    def test_a_line_heard_by_five_bots_counts_once(self):
        shared = escort.Shared('[name removed]')
        now = time.time()
        self.assertEqual(shared.order('crew stay', '[name removed]', now), 'stay')
        self.assertIsNone(shared.order('crew stay', '[name removed]', now + .5))
        self.assertEqual(shared.mode, 'stay')
        shared.order('passive', '[name removed]', now + 10)
        self.assertFalse(shared.assist)
        shared.order('dismiss', '[name removed]', now + 20)
        self.assertTrue(shared.ended)


class Escort(unittest.TestCase):
    def test_fight_the_players_target_heal_the_player_answer_status(self):
        view = {OWNER: {'ok': True, 'x': 100.0, 'y': 100.0, 'z': 0.0, 'parent': 0,
                        'creature': {'posture': 'upright', 'states': ['combat'], 'ham': {'health': 400},
                                     'max_ham': {'health': 1000}, 'target': PREY}},
                PREY: {'ok': True, 'type': 'CREO', 'name': '@mob/creature_names:kreetle', 'x': 110.0, 'y': 100.0,
                       'z': 0.0, 'creature': {'posture': 'upright'}}}
        forn, mirren = Bot('Forn', 1, view), Bot('Mirren', 2, view)
        forn.arriving = [{'event': 'chat', 'from': '[name removed] Q', 'text': 'crew status'},
                      {'event': 'combat', 'attacker': PREY, 'defender': OWNER, 'amount': 120, 'attacker_name': 'a kreetle'}]
        roles = {'Forn': {'weapon': 'rifle', 'ranged': True}, 'Mirren': {'weapon': 'rifle', 'ranged': True, 'healer': True}}
        with tempfile.TemporaryDirectory() as tmp:
            escort.PLAY, real_who = Path(tmp), escort.who
            escort.who = lambda owner: {'oid': OWNER, 'zone': 'tatooine', 'worldPositionX': 100, 'worldPositionY': 100}
            try:
                summary = escort.escort(Group([forn, mirren]), '[name removed]', roles, minutes=.005)
            finally:
                escort.who = real_who
            rows = [json.loads(line) for line in Path(summary['play_data']).read_text().splitlines()]
        self.assertTrue(summary['owner_seen'])
        self.assertIn(('invite', OWNER), forn.sent)
        self.assertTrue(any(target == PREY and name != 'invite' for name, target in forn.sent))   # Forn fights the kreetle
        self.assertIn(('healDamage', OWNER), mirren.sent)                                     # Mirren heals the player
        self.assertTrue(any('%' in line or 'No reports' in line for line in forn.said))      # the status answer
        self.assertIn('status', [verb for _, verb in summary['orders']])
        self.assertTrue(any(r['kind'] == 'combat' and r['on_player'] for r in rows))
        self.assertTrue(any(r['kind'] == 'player' and r['fighting'] for r in rows))


    def test_a_bot_whose_walks_go_nowhere_jumps_to_the_player(self):
        view = {OWNER: {'ok': True, 'x': 100.0, 'y': 140.0, 'z': 0.0, 'parent': 0,
                        'creature': {'posture': 'upright', 'states': [], 'ham': {'health': 1000},
                                     'max_ham': {'health': 1000}}}}
        brask = Bot('Brask', 3, view)
        brask.move_reply = {'arrived': False, 'x': 100.0, 'y': 90.0}   # where it already stands: pinned
        with tempfile.TemporaryDirectory() as tmp:
            escort.PLAY, real_who = Path(tmp), escort.who
            escort.who = lambda owner: {'oid': OWNER, 'zone': 'tatooine', 'worldPositionX': 100, 'worldPositionY': 140}
            try:
                summary = escort.escort(Group([brask]), '[name removed]', {'Brask': {'weapon': 'polearm'}}, minutes=.004)
            finally:
                escort.who = real_who
        self.assertTrue(summary['counts']['Brask']['unstuck'] >= 1)
        self.assertIn('stuck: jumping to [name removed]', brask.labels)


    def test_indoors_the_crew_walks_where_the_player_stood(self):
        view = {OWNER: {'ok': True, 'x': 4.0, 'y': -2.0, 'z': -10.0, 'parent': 5996315,
                        'creature': {'posture': 'upright', 'states': [], 'ham': {'health': 1000},
                                     'max_ham': {'health': 1000}}}}
        brask = Bot('Brask', 3, view)
        brask.planet = 'endor'
        brask.cells = []
        real_move = brask.move

        def move(x, y, z=None, cell=None, timeout=90):
            brask.cells.append(cell)
            return real_move(x, y, z, cell, timeout)

        brask.move = move
        with tempfile.TemporaryDirectory() as tmp:
            escort.PLAY, real_who = Path(tmp), escort.who
            escort.who = lambda owner: {'oid': OWNER, 'zone': 'endor', 'worldPositionX': -4660, 'worldPositionY': 4320}
            try:
                escort.escort(Group([brask]), '[name removed]', {'Brask': {'weapon': 'polearm'}}, minutes=.003)
            finally:
                escort.who = real_who
        self.assertTrue(brask.moves)
        self.assertEqual(set(brask.moves), {(4, -2)})          # the player's own spot, no formation offset
        self.assertEqual(set(brask.cells), {5996315})

    def test_the_buff_order_walks_the_healer_through_the_enhancements(self):
        view = {OWNER: {'ok': True, 'x': 100.0, 'y': 90.0, 'z': 0.0, 'parent': 0,
                        'creature': {'posture': 'upright', 'states': [], 'ham': {'health': 1000},
                                     'max_ham': {'health': 1000}}}}
        mirren = Bot('Mirren', 2, view)
        mirren.arriving = [{'event': 'tell', 'from': '[name removed]', 'text': 'crew buff'}]
        real_slash = mirren.slash

        def slash(name, args='', target=0, wait=0):
            real_slash(name, target=target)
            return [{'event': 'system', 'text': f"You enhance [name removed]'s {args.title()} by 200."}] if name == 'healenhance' else []

        mirren.slash = slash
        with tempfile.TemporaryDirectory() as tmp:
            escort.PLAY, real_who = Path(tmp), escort.who
            escort.who = lambda owner: {'oid': OWNER, 'zone': 'tatooine', 'worldPositionX': 100, 'worldPositionY': 90}
            try:
                escort.escort(Group([mirren]), '[name removed]', {'Mirren': {'weapon': 'rifle', 'ranged': True, 'healer': True}}, minutes=.004)
            finally:
                escort.who = real_who
        self.assertEqual([t for name, t in mirren.sent if name == 'healenhance'], [OWNER] * len(escort.BUFFS))


class Trail(unittest.TestCase):
    def test_a_point_some_metres_back_along_the_path(self):
        trail = [{'cell': 1, 'x': 0.0, 'y': 0.0}, {'cell': 1, 'x': 2.0, 'y': 0.0}, {'cell': 1, 'x': 4.0, 'y': 0.0},
                 {'cell': 2, 'x': 4.0, 'y': 3.0}, {'cell': 2, 'x': 4.0, 'y': 5.0}]
        self.assertEqual(escort.trail_point(trail, 1.5)['y'], 3.0)    # 2 m back, within the newest cell
        self.assertEqual(escort.trail_point(trail, 3.0)['x'], 2.0)    # the cell change counts as no distance
        self.assertEqual(escort.trail_point(trail, 99)['x'], 0.0)
        self.assertIsNone(escort.trail_point([], 2))


if __name__ == '__main__':
    unittest.main()
