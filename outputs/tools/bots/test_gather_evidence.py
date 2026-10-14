"""Offline evidence checks, without game processes or network access."""
import importlib.util
from pathlib import Path
from types import SimpleNamespace
import unittest

spec = importlib.util.spec_from_file_location('gather', Path(__file__).parent / 'scenarios/besh-gather.py')
gather = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gather)


class GatherEvidence(unittest.TestCase):
    def test_existing_stack_and_new_stack(self):
        before = {'items': [dict(oid=1, units=10)]}
        self.assertEqual(gather.received_units(before, {'items': [dict(oid=1, units=15)]}), 5)
        self.assertEqual(gather.received_units(before, {'items': [dict(oid=1, units=10), dict(oid=2, units=4)]}), 4)
        self.assertEqual(gather.received_units(before, before), 0)

    def test_text_or_item_identity_never_proves_units(self):
        self.assertIsNone(gather.received_units({}, {'items': [dict(oid=1, name='ore')]}))
        self.assertIsNone(gather.received_units({}, {'items': [dict(oid=1, units=True)]}))

    def test_harvest_issues_one_choice_only(self):
        commands = []
        inventories = iter([{'items': []}, {'items': [dict(oid=2, units=12)]}])
        bot = SimpleNamespace(first='test', go=lambda _: {'arrived': True},
                              inventory=lambda: next(inventories),
                              slash=lambda *a, **kw: commands.append((a, kw)) or [])
        checks = []
        group = SimpleNamespace(note=lambda _: None, check=lambda *a: checks.append(a))
        self.assertEqual(gather.harvest(group, bot, dict(oid=9), 'hide'), 12)
        self.assertEqual(len(commands), 1)
        self.assertEqual(commands[0][0], ('harvestcorpse', 'hide'))
        self.assertTrue(checks[0][1])

    def test_unreachable_corpse_sends_no_harvest(self):
        bot = SimpleNamespace(go=lambda _: {'arrived': False})
        notes = []
        self.assertIsNone(gather.harvest(SimpleNamespace(note=notes.append), bot, dict(oid=9)))
        self.assertTrue(notes)


if __name__ == '__main__':
    unittest.main()
