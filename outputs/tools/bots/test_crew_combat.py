"""Offline tests for crew_combat.py (Claude, 15 Oct 2026): the fight loop with fake bots."""
import threading
import time
import unittest

import crew_combat as cc

TARGET = 99


class FakeBot:
    def __init__(self, first, oid, skills, health=1000, ticks_to_kill=3):
        self.first, self.oid, self.skills, self.health = first, oid, skills, health
        self.looks, self.ticks_to_kill, self.sent, self.moves = 0, ticks_to_kill, [], []
        self.x, self.y = 0.0, 0.0

    def profession(self, name):
        return {'skills': self.skills}

    def status(self):
        return {'me': {'ham': {'health': self.health}, 'max_ham': {'health': 1000}, 'posture': 'upright'},
                'x': self.x, 'y': self.y, 'z': 0.0, 'self': self.oid}

    def look(self, radius, type, limit):
        self.looks += 1
        return [{'oid': TARGET, 'x': 30.0, 'y': 0.0, 'z': 0.0, 'posture': 'dead' if self.looks > self.ticks_to_kill else 'upright'}]

    def inspect(self, oid):
        return {'ok': True, 'oid': oid, 'x': 30.0, 'y': 0.0, 'z': 0.0, 'parent': 0,
                'creature': {'posture': 'upright'}}

    def slash(self, name, args='', target=0, wait=0):
        self.sent.append((name, target))
        if name == 'polearmLegHit2':
            return [{'event': 'command_failed', 'reason': 'cooldown'}]
        return []

    def move(self, x, y, z=None, cell=None, timeout=90):
        self.moves.append((round(x), round(y)))
        self.x, self.y = x, y
        return {'arrived': True, 'x': x, 'y': y}

    def idle(self, seconds):
        time.sleep(.01)  # the real tick is 2 s; this only lets the threads interleave
        return []


class FakeGroup:
    def __init__(self, bots):
        self.bots = bots

    def parallel(self, *jobs):
        threads = [threading.Thread(target=job) for job in jobs]
        for t in threads:
            t.start()
        for t in threads:
            t.join()


class Fight(unittest.TestCase):
    def test_melee_closes_in_ranged_keeps_range_healer_heals_the_lowest(self):
        brask = FakeBot('Brask', 1, ['combat_polearm_novice', 'combat_polearm_speed_01'], health=500, ticks_to_kill=8)
        forn = FakeBot('Forn', 2, ['combat_rifleman_novice'], ticks_to_kill=8)
        mirren = FakeBot('Mirren', 3, [])
        roles = {'Brask': {'weapon': 'polearm'}, 'Forn': {'weapon': 'rifle', 'ranged': True, 'opener': ['steadyaim']},
                 'Mirren': {'weapon': 'rifle', 'ranged': True, 'healer': True}}
        record = cc.fight(FakeGroup([brask, forn, mirren]), TARGET, roles, seconds=60)
        self.assertEqual(record['result'], 'target dead')
        # Brask walks to 1.5 m short of the target, Forn stays outside melee (30 m is inside his 45 m reach).
        self.assertIn((28, 0), brask.moves)
        self.assertEqual(forn.moves, [])
        self.assertEqual(forn.sent[0], ('steadyaim', TARGET))
        # Brask is at 50%: Mirren heals him.
        self.assertIn(('healDamage', 1), mirren.sent)
        # Brask's polearm specials come from the server tables; the refused one is counted.
        self.assertTrue(any(name.startswith('polearm') for name, _ in brask.sent))
        self.assertIn('polearmLegHit2: cooldown', record['crew']['Brask']['refused'])
        self.assertEqual(record['crew']['Brask']['lowest_health'], .5)


if __name__ == '__main__':
    unittest.main()
