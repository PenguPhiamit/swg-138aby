"""Profession wrapper checks without accounts, a body process or a galaxy."""
import json
import unittest
from unittest.mock import Mock

from squad import Bot


def system(payload):
    return {'event': 'system', 'text': '[agentgear] ' + json.dumps(payload)}


class Professions(unittest.TestCase):
    def bot(self, *events):
        bot = Bot.__new__(Bot)  # never read credentials or start a process
        bot.slash = Mock()
        bot.wait_for = Mock(side_effect=lambda match, timeout:
                            next((event for event in events if match(event)), None))
        return bot

    def test_grant_returns_partial_failure_and_preserves_box_names(self):
        reply = dict(kit='profession', profession='combat_carbine',
                     granted=['combat_marksman_novice', 'combat_carbine_novice'],
                     failed=['combat_carbine_master'], skills=['combat_carbine_novice'])
        bot = self.bot(system(dict(kit='boss', failed=[])),
                       system(dict(kit='profession', profession='combat_brawler', granted=[])),
                       system(reply))
        self.assertEqual(bot.profession(' Combat_Carbine '), reply)
        bot.slash.assert_called_once_with('agentGear', 'profession combat_carbine', wait=0)

    def test_clear_uses_profession_command_and_keeps_retained_skills(self):
        reply = dict(kit='profession', profession='clear', granted=[], failed=[],
                     surrendered=['combat_brawler_novice'], skills=['social_language_basic_comprehend'])
        bot = self.bot(system(reply))
        self.assertEqual(bot.clear_professions(), reply)
        bot.slash.assert_called_once_with('agentGear', 'profession clear', wait=0)

    def test_list_returns_current_skills(self):
        reply = dict(kit='profession', profession='list', granted=[], failed=[],
                     skills=['combat_brawler_novice'])
        bot = self.bot(system(reply))
        self.assertEqual(bot.profession('list'), reply)
        bot.slash.assert_called_once_with('agentGear', 'profession list', wait=0)

    def test_gate_and_unknown_profession_errors_are_not_success(self):
        for reply in [dict(error='off on this galaxy'),
                      dict(kit='profession', profession='missing',
                           error='unknown or unavailable profession', granted=[], failed=[])]:
            with self.subTest(reply=reply):
                bot = self.bot(system(reply))
                self.assertEqual(bot.profession('missing'), reply)

    def test_timeout_and_unrelated_replies_report_no_answer(self):
        bot = self.bot({'text': 'hello'}, system(dict(kit='survey', failed=[])))
        self.assertIn('no profession answer', bot.profession('combat_brawler')['error'])

    def test_malformed_json_and_nonobject_answers_report_error(self):
        for text in ['[agentgear] {broken', '[agentgear] []', '[agentgear] null']:
            with self.subTest(text=text):
                bot = self.bot({'event': 'system', 'text': text})
                self.assertEqual(bot.profession('combat_brawler'), {'error': 'invalid profession answer'})

    def test_invalid_arguments_never_send_a_command(self):
        bot = self.bot()
        for name in ['', ' ', 'combat_brawler\nclear', 'combat_brawler;clear', None, 42]:
            with self.subTest(name=name), self.assertRaises(ValueError):
                bot.profession(name)
        bot.slash.assert_not_called()


if __name__ == '__main__':
    unittest.main()
