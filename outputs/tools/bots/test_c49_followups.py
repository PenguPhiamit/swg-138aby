"""Saved receipts and failed/moving-target approaches; no game or network calls."""
import importlib.util
import json
from pathlib import Path
import unittest
import tempfile

import crew_combat as cc
import escort
import movement_evidence
from test_crew_combat import FakeBot, TARGET

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('doctor_buffs', HERE / 'scenarios/aurek-doctor-buffs.py')
doctor = importlib.util.module_from_spec(spec)
spec.loader.exec_module(doctor)


class Enhancement(unittest.TestCase):
    def test_saved_gate_refreshes_are_verified_without_ham_growth(self):
        path = HERE / 'testdata/doctor-refresh.json'
        report = json.loads(path.read_text(encoding='utf-8'))
        tested = 0
        for c in report['rows']:
            self.assertEqual(doctor.enhancement_result(c['before'], c['after'], c['events'],
                                                       c['patient'], c['attribute']), 'reapplied')
            tested += 1
        self.assertEqual(tested, 4)

    def test_refusal_wrong_recipient_attribute_or_silence_is_not_a_refresh(self):
        good = {'event': 'system', 'text': "You re-apply Patient's Health enhancement."}
        for events in ([], [{'event': 'command_ack'}],
                       [dict(good, text="You re-apply Other's Health enhancement.")],
                       [dict(good, text="You re-apply Patient's Action enhancement.")],
                       [dict(good, event='chat')], [good, {'event': 'command_failed', 'error': 2}]):
            with self.subTest(events=events):
                self.assertEqual(doctor.enhancement_result(1000, 1000, events, 'Patient', 'health'), 'unverified')

    def test_ham_drop_or_bad_telemetry_cannot_be_hidden_by_receipt(self):
        e = [{'event': 'system', 'text': "You re-apply Patient's Health enhancement."}]
        for before, after in [(1000, 900), (None, 1000), (True, True), (float('inf'), float('inf'))]:
            self.assertEqual(doctor.enhancement_result(before, after, e, 'Patient', 'health'), 'unverified')
        self.assertEqual(doctor.enhancement_result(1000, 1200, [], 'Patient', 'health'), 'increased')


class Approaches(unittest.TestCase):
    def make(self):
        bot = FakeBot('TestFighter', 1, [])
        rec = cc.new_record()
        fighter = cc.Fighter(bot, {'weapon': 'polearm', 'opener': ['volleyFire']}, rec)
        fighter.open(TARGET)
        obj = {'oid': TARGET, 'x': 30., 'y': 0., 'z': 0., 'parent': 0}
        return bot, fighter, rec, obj

    def test_blocked_approach_never_sends_attack_or_opener(self):
        bot, fighter, rec, obj = self.make()
        bot.move = lambda *a, **kw: {'ok': False, 'error': 'blocked'}
        self.assertFalse(fighter.strike(cc.self_row(bot), obj))
        self.assertEqual(bot.sent, [])
        self.assertEqual(rec['approach_deferred'], 1)
        self.assertEqual(fighter.turn, 0)

    def test_successful_approach_rechecks_and_then_opens(self):
        bot, fighter, rec, obj = self.make()
        self.assertTrue(fighter.strike(cc.self_row(bot), obj))
        self.assertEqual(bot.sent, [('volleyFire', TARGET), ('attack', TARGET)])

    def test_target_moving_away_or_crossing_cell_defers_attack(self):
        for update in [{'x': 100.}, {'parent': 77}, {'creature': {'posture': 'dead'}}]:
            bot, fighter, rec, obj = self.make()
            old = bot.inspect
            bot.inspect = lambda oid: dict(old(oid), **update)
            self.assertFalse(fighter.strike(cc.self_row(bot), obj))
            self.assertEqual(bot.sent, [])

    def test_3d_distance_and_unknown_frames(self):
        a = {'x': 0., 'y': 0., 'z': 10., 'cell': 4}
        self.assertEqual(cc.attack_distance(a, dict(a, z=15.)), 5.)
        for b in [dict(a, cell=5), dict(a, z=None), dict(a, x=float('nan'))]:
            self.assertIsNone(cc.attack_distance(a, b))
        bot, fighter, rec, obj = self.make()
        self.assertFalse(fighter.strike({'x': 0., 'y': 0.}, obj))
        self.assertEqual(bot.sent, [])


class LocalNames(unittest.TestCase):
    def test_only_observer_id_gets_me_expansion(self):
        bot = FakeBot('TestLeader', 1, [])
        e = {'attacker': 1, 'attacker_name': 'me', 'defender': 2, 'defender_name': 'me'}
        result = escort.combat_names(e, bot)
        self.assertEqual(result['attacker_name'], 'TestLeader')
        self.assertEqual(result['defender_name'], 'me')
        self.assertEqual(e['attacker_name'], 'me')
        self.assertEqual(escort.combat_names(dict(e, attacker_name='Named NPC'), bot)['attacker_name'], 'Named NPC')


class Evidence(unittest.TestCase):
    def test_truncated_reply_and_position_packet_never_become_a_cause(self):
        report = {'events': {'Bot': [{'event': 'position_set_by_server', 'x': 1, 't': 2}]},
                  'steps': [{'bot': 'Bot', 't': 3, 'request': '{"cmd":"move","x":5,"y":6}',
                             'reply': '{"error":"the server keeps putting us back'}]}
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / 'report.json'
            p.write_text(json.dumps(report), encoding='utf-8')
            out = movement_evidence.summarize(p)
        self.assertEqual(out['correction_events'], {'Bot': 1})
        self.assertEqual(out['moves'][0]['outcome'], 'unavailable/truncated reply')
        self.assertTrue(out['reason'].startswith('undetermined'))


if __name__ == '__main__':
    unittest.main()
