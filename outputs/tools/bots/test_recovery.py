"""Recovery-route regressions without network/game access."""
import unittest
import importlib.util
from pathlib import Path
from types import SimpleNamespace
from fallback_scenarios import recover_home


class Recovery(unittest.TestCase):
    def group(self, *planets):
        bots = []
        for i, planet in enumerate(planets):
            bot = SimpleNamespace(first=f'bot{i}', planet=planet)
            bot.status = lambda bot=bot: {'planet': bot.planet}
            bots.append(bot)
        g = SimpleNamespace(bots=bots, notes=[], checks=[])
        g.checkpoint = lambda: None
        g.parallel = lambda *jobs: [job() for job in jobs]
        g.note = g.notes.append
        def check(label, ok, detail=''):
            g.checks.append((label, bool(ok)))
            return bool(ok)
        g.check = check
        return g

    def test_mixed_crew_each_gets_own_route(self):
        g = self.group('tatooine', 'hoth', 'corellia')
        legs = []
        def ride(g, bot, origin, destination):
            legs.append((bot.first, origin[0], destination[0]))
            bot.planet = destination[0]
            return True
        self.assertTrue(recover_home(g, ride))
        self.assertEqual(legs, [('bot1', 'hoth', 'corellia'), ('bot1', 'corellia', 'tatooine'),
                                ('bot2', 'corellia', 'tatooine')])
        self.assertTrue(all(b.planet == 'tatooine' for b in g.bots))

    def test_failed_leg_does_not_continue(self):
        g = self.group('hoth')
        legs = []
        def ride(g, bot, origin, destination):
            legs.append(origin[0])
            return False
        self.assertFalse(recover_home(g, ride))
        self.assertEqual(legs, ['hoth'])

    def test_success_reply_without_scene_change_is_rejected(self):
        g = self.group('hoth')
        self.assertFalse(recover_home(g, lambda *args: True))
        self.assertIn('arrival was not confirmed', g.notes[-1])

    def test_unknown_planet_never_travels(self):
        g = self.group('naboo')
        def ride(*args):
            self.fail('unknown route must not be attempted')
        self.assertFalse(recover_home(g, ride))
        self.assertIn('no verified home route', g.notes[0])

    def test_already_home_never_travels(self):
        g = self.group('tatooine')
        self.assertTrue(recover_home(g, lambda *args: self.fail('already home')))

    def test_dorn_failed_walk_records_failure_and_turns_leash_off(self):
        spec = importlib.util.spec_from_file_location('dorn_social_test', Path(__file__).parent / 'scenarios/dorn-social.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        commands, checks = [], []
        bot = SimpleNamespace(started=0, gear=lambda *a: {}, status=lambda: {'x': 1, 'y': 2},
                              say=lambda *a: None, tell=lambda *a: {},
                              wait_for=lambda *a: {'text': 'with me'}, walk=lambda *a: {'ok': False, 'error': 'disconnected'})
        bot.slash = lambda *a, **k: commands.append(a) or [{'text': 'Leashed to Dorn'}]
        class Group:
            bots = []
            def __getitem__(self, name):
                return bot
            def note(self, text):
                pass
            def parallel(self, *jobs):
                return []
            def check(self, label, ok, detail=''):
                checks.append((label, bool(ok)))
                return bool(ok)
        module.run(Group())  # previously raised KeyError('x') here
        self.assertIn(('leader leash test walk arrived', False), checks)
        self.assertEqual(commands[-1], ('leash', 'off'))


if __name__ == '__main__':
    unittest.main()
