"""Offline regressions; never connects to a galaxy."""
import tempfile
import threading
import time
import unittest
from pathlib import Path
from run_control import RunControl, RunStopped, read_activity


class ControlTests(unittest.TestCase):
    def test_stop_during_wait(self):
        with tempfile.TemporaryDirectory() as folder:
            control = RunControl(folder, 'Esk', 'fixture')
            timer = threading.Timer(.05, lambda: (Path(folder) / 'STOP').touch())
            timer.start()
            began = time.monotonic()
            with self.assertRaises(RunStopped):
                control.sleep(10)
            timer.join()
            self.assertLess(time.monotonic() - began, 1)
            self.assertEqual(read_activity(folder)[0]['state'], 'stopped')

    def test_deadline_and_stale_records(self):
        with tempfile.TemporaryDirectory() as folder:
            control = RunControl(folder, 'Esk', 'fixture', time.monotonic() - 1)
            with self.assertRaisesRegex(RunStopped, 'budget'):
                control.checkpoint()
            self.assertTrue(read_activity(folder, stale_after=-1)[0]['stale'])

    def test_parallel_publication(self):
        with tempfile.TemporaryDirectory() as folder:
            control = RunControl(folder, 'Esk', 'fixture')
            errors = []
            def publish():
                try:
                    for _ in range(20):
                        control.publish('running')
                except Exception as exc:
                    errors.append(exc)
            workers = [threading.Thread(target=publish) for _ in range(4)]
            for worker in workers:
                worker.start()
            for worker in workers:
                worker.join()
            self.assertEqual(errors, [])
            self.assertEqual(read_activity(folder)[0]['state'], 'running')


if __name__ == '__main__':
    unittest.main()
