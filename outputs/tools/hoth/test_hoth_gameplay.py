"""Offline acceptance evidence checks; no game/network access."""
import unittest
from hoth_gameplay_check import unit_gain, named, choose_job, preflight
from types import SimpleNamespace


class Evidence(unittest.TestCase):
    def test_missing_kit_and_tools_block_before_travel(self):
        notes = []
        g = SimpleNamespace(bots=[SimpleNamespace(inventory=lambda: {'items': []})], note=notes.append)
        self.assertFalse(preflight(g))
        self.assertEqual(len(notes), 2)

    def test_tools_can_belong_to_another_member(self):
        leader = SimpleNamespace(inventory=lambda: {'items': [{'name': 'armor_composite'}]})
        artisan = SimpleNamespace(inventory=lambda: {'items': [{'name': 'survey_tool_' + k} for k in
                                  ('mineral', 'chemical', 'gas', 'moisture', 'flora', 'liquid')]})
        self.assertTrue(preflight(SimpleNamespace(bots=[leader, artisan], note=lambda x: None)))

    def test_existing_stack_gain(self):
        self.assertEqual(unit_gain({'items': [{'oid': 1, 'name': 'ore', 'units': 10}]},
                                   {'items': [{'oid': 1, 'name': 'ore', 'units': 14}]}), [('ore', 4)])

    def test_names_only_are_not_unit_proof(self):
        self.assertIsNone(unit_gain({'items': []}, {'items': [{'oid': 1, 'name': 'ore'}]}))

    def test_no_gain_and_new_stack(self):
        a = {'items': [{'oid': 1, 'name': 'ore', 'quantity': 10}]}
        self.assertEqual(unit_gain(a, a), [])
        self.assertEqual(unit_gain(a, {'items': a['items'] + [{'oid': 2, 'name': 'gas', 'quantity': 3}]}), [('gas', 3)])

    def test_raw_labels_rejected(self):
        self.assertFalse(named('@resource_names:steel_hoth'))
        self.assertFalse(named('  '))
        self.assertTrue(named('Hothian Steel'))

    def test_conversation_does_not_assume_option_zero(self):
        self.assertEqual(choose_job(['Not my problem.', "I'll find her."]), 1)
        self.assertIsNone(choose_job(['Reset the job', 'Next job']))


if __name__ == '__main__':
    unittest.main()
