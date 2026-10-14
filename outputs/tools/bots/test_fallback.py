"""Offline switching and ticket-page regressions; no game/account access."""
import tempfile
import unittest
import contextlib
import io
import json
from types import SimpleNamespace
from unittest.mock import patch
from pathlib import Path
from fallback import Chooser
from ticket_pages import newest_ticket_list


class Switching(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.main, self.a, self.b = [Path(self.tmp.name) / n for n in ('main.py', 'a.py', 'b.py')]
        for path in (self.main, self.a, self.b):
            path.write_text('# v1')
        self.c = Chooser()
        self.select()

    def select(self):
        return self.c.select('Esk', self.main, [self.a, self.b])[0]

    def outcome(self, ok=True, notes=(), error=None, state='finished'):
        return self.c.observe('Esk', dict(checks=[dict(label='arrival', ok=ok)], notes=notes, error=error, state=state))

    def test_two_passes_and_main_retry(self):
        self.assertIsNone(self.outcome())
        self.assertEqual(self.outcome()['next'], 'a.py')
        self.assertEqual(self.select(), self.a)
        self.outcome(ok=False)
        self.assertEqual(self.outcome(ok=False)['next'], 'b.py')
        self.assertEqual(self.outcome()['next'], 'main.py')

    def test_repeat_failure_and_change_reset(self):
        self.outcome(False)
        self.assertEqual(self.outcome(False)['next'], 'a.py')
        self.main.write_text('# revised main')
        self.assertEqual(self.select(), self.main)
        self.assertIsNone(self.outcome(False))

    def test_blocked_is_not_pass(self):
        self.outcome(notes=['BLOCKED: API missing'])
        self.assertEqual(self.outcome(notes=['BLOCKED: API missing'])['next'], 'a.py')

    def test_halt_does_not_switch(self):
        self.outcome(False)
        self.assertIsNone(self.outcome(False, state='stopped'))
        self.assertEqual(self.select(), self.main)

    def test_nonconsecutive_failure_does_not_switch(self):
        self.outcome(False)
        self.outcome(True)
        self.assertIsNone(self.outcome(False))

    def test_repeated_round_timeout_switches(self):
        self.outcome(False, error='RunStopped: run time budget reached', state='stopped')
        self.assertEqual(self.outcome(False, error='RunStopped: run time budget reached', state='stopped')['next'], 'a.py')

    def test_empty_scenario_is_blocked(self):
        self.c.observe('Esk', {})
        self.assertEqual(self.c.observe('Esk', {})['next'], 'a.py')

    def test_state_survives_new_chooser(self):
        self.outcome(False)
        self.c = Chooser(self.c.state)
        self.select()
        self.assertEqual(self.outcome(False)['next'], 'a.py')

    def test_missing_fallback_returns_main(self):
        self.outcome(); self.outcome()
        self.a.unlink()
        self.assertEqual(self.select(), self.main)


class Tickets(unittest.TestCase):
    def test_ignores_confirmation_and_stale_list(self):
        old = dict(page_id=100, callback='msgSelected', text='ticket')
        new = dict(page_id=101, callback='msgSelected', text='ticket')
        confirm = dict(page_id=102, text='ticket purchase complete')
        self.assertEqual(newest_ticket_list([confirm, new, old], [old]), new)
        self.assertIsNone(newest_ticket_list([confirm, old], [old]))

    def test_reused_page_id_with_new_content(self):
        old = dict(page_id=10, callback='msgSelected', text='old')
        new = dict(page_id=10, callback='msgSelected', text='new')
        self.assertEqual(newest_ticket_list([new], [old]), new)


class RunnerIntegration(unittest.TestCase):
    def test_actual_runner_rotates_and_records_without_game_io(self):
        import squad
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            here, reports = root / 'tools', root / 'reports'
            scenarios = here / 'scenarios'
            scenarios.mkdir(parents=True)
            main, a, b = [scenarios / n for n in ('main.py', 'a.py', 'b.py')]
            for path in (main, a, b):
                path.write_text("GROUP = 'Esk'\n")
            (here / 'fallback-plan.json').write_text(json.dumps({'Esk': ['a.py', 'b.py']}))
            executed = []

            def fake_job(path, name, spec, results, deadline, assignment):
                executed.append(path.name)
                target = reports / name
                target.mkdir(parents=True, exist_ok=True)
                report = target / f'{len(executed)}.json'
                checks = [dict(label='arrival', ok=True, detail='fixture')]
                report.write_text(json.dumps(dict(checks=checks, notes=[], error=None,
                                      state='finished', passed=1, total=1, assignment=assignment)))
                results[(path.name, name)] = (SimpleNamespace(checks=checks, notes=[]), None, 0, report)

            spec = {'groups': {'Esk': {'focus': 'fixture', 'members': []}}}
            with patch.object(squad, 'HERE', here), patch.object(squad, 'REPORTS', reports), \
                 patch.object(squad, 'OUTPUTS', root), patch.object(squad, 'load_spec', return_value=spec), \
                 patch.object(squad, 'run_job', side_effect=fake_job), \
                 contextlib.redirect_stdout(io.StringIO()):
                squad.cmd_run([str(main), '--rounds', '5'])
            self.assertEqual(executed, ['main.py', 'main.py', 'a.py', 'a.py', 'b.py'])
            state = json.loads((reports / 'runs/fallback-state.json').read_text())
            self.assertEqual(Path(state['Esk']['active']).name, 'main.py')
            self.assertIn('scheduled main retry', (reports / 'Esk/LOG.md').read_text())
            self.assertEqual(len((reports / 'fallback-coverage.md').read_text().splitlines()), 5)


class ProbeSafety(unittest.TestCase):
    def test_esk_main_routes_refuse_wrong_planet(self):
        import importlib.util
        from unittest.mock import MagicMock, Mock
        path = Path(__file__).parent / 'scenarios/esk-routes.py'
        spec = importlib.util.spec_from_file_location('test_esk_routes', path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        bots = [Mock(first=n) for n in ('Esk', 'Lira', 'Tovan')]
        for bot in bots:
            bot.status.return_value = dict(planet='hoth')
        group = MagicMock(bots=bots)
        group.__getitem__.side_effect = dict(zip(('Esk', 'Lira', 'Tovan'), bots)).__getitem__
        module.run(group)
        group.parallel.assert_not_called()
        for bot in bots:
            bot.walk.assert_not_called()
            bot.gear.assert_not_called()

    def test_hoth_grid_reach_and_travel_never_move(self):
        import fallback_scenarios as probes
        from unittest.mock import Mock
        bot = Mock()
        bot.status.return_value = dict(planet='hoth', cell=0, x=20, y=-2224)
        group = Mock(leader=bot)
        for probe in (probes.grid, probes.reach, probes.travel):
            probe(group)
        bot.move.assert_not_called()
        bot.walk.assert_not_called()
        bot.locate.assert_not_called()
        self.assertEqual(group.note.call_count, 3)

    def test_failed_grid_stops_after_first_move(self):
        import fallback_scenarios as probes
        from unittest.mock import Mock
        bot = Mock()
        bot.status.return_value = dict(planet='tatooine', cell=0, x=3528, y=-4804)
        bot.move.return_value = dict(ok=False, error='blocked')
        bot.request.return_value = dict(z=5)
        group = Mock(leader=bot)
        probes.grid(group)
        self.assertEqual(bot.move.call_count, 1)
        self.assertFalse(group.check.call_args.args[1])


if __name__ == '__main__':
    unittest.main()
