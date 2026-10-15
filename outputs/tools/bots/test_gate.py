"""Offline tests for gate.py's verdict logic (no server, no bots): python3 -I tools/bots/test_gate.py"""
import sys, tempfile, unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gate  # noqa: E402


class Classify(unittest.TestCase):
    def test_statuses(self):
        self.assertEqual(gate.classify('', True), 'NEW')
        self.assertEqual(gate.classify('', False), 'NEW')
        self.assertEqual(gate.classify('PPP', True), 'PASS')
        self.assertEqual(gate.classify('PPP', False), 'REGRESSION')
        self.assertEqual(gate.classify('PFP', False), 'FLAKY')
        self.assertEqual(gate.classify('PPF', True), 'FIXED')
        self.assertEqual(gate.classify('PPF', False), 'FAILING')


class Verdict(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        gate.GATE_DIR, gate.GATE_MD = root / 'gate', root / 'GATE.md'
        gate.GATE_DIR.mkdir()

    def tearDown(self):
        self.tmp.cleanup()

    def result(self, **extra):
        base = {'stamp': '20261015-000000', 'problems': [], 'warnings': [], 'bots': '18/18',
                'health': {'dev': 'abc', 'archive': 'def', 'galaxy': {'error_lines': 0}}}
        base.update(extra)
        return base

    def test_regression_fails(self):
        rows = [{'key': 'Dorn|d.py|a', 'ok': False, 'status': 'REGRESSION', 'detail': 'x'},
                {'key': 'Dorn|d.py|b', 'ok': True, 'status': 'PASS', 'detail': ''}]
        self.assertEqual(gate.finish(self.result(), rows), 1)
        self.assertTrue(gate.GATE_MD.read_text(encoding='utf-8').startswith('# Gate: FAIL'))

    def test_known_failures_and_warnings_pass(self):
        rows = [{'key': 'Dorn|d.py|a', 'ok': False, 'status': 'FAILING', 'detail': 'x'},
                {'key': 'Esk|e.py|b', 'ok': False, 'status': 'FLAKY', 'detail': ''},
                {'key': 'Esk|e.py|c', 'ok': None, 'status': 'MISSING', 'detail': ''}]
        result = self.result(warnings=['Aurek a.py: no checks ran (blocked)'])
        self.assertEqual(gate.finish(result, rows), 0)
        text = gate.GATE_MD.read_text(encoding='utf-8')
        self.assertTrue(text.startswith('# Gate: PASS'))
        self.assertIn('- WARN Aurek a.py: no checks ran', text)
        self.assertIn('## Still failing: 1', text)

    def test_problem_fails_and_skip_is_skipped(self):
        self.assertEqual(gate.finish(self.result(problems=['bots online 17/18 after setup']), []), 1)
        self.assertEqual(gate.finish(self.result(problems=['busy'], skipped=True), []), 1)
        self.assertTrue(gate.GATE_MD.read_text(encoding='utf-8').startswith('# Gate: SKIPPED'))


if __name__ == '__main__':
    unittest.main()
