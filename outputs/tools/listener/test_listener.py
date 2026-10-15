"""Offline tests for listener.py: no keyboard is read, no window is inspected (a fake stands in for Windows), nothing
leaves this PC. The one real Windows call is asking which program is in front, which reads no key.

    python -I test_listener.py
"""
import contextlib
import io
import json
import os
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import listener as L

T0 = 1_800_000_000.0


def key(t, k, held, **extra):
    """A down at t and an up at t + held."""
    return [dict(t=t, kind='down', k=k, **extra), dict(t=t + held, kind='up', k=k)]


def feed_all(red, events):
    out = []
    for ev in sorted(events, key=lambda e: (e['t'], e['kind'] == 'down')):
        out += red.feed(ev)
    return out


def names(events):
    return [e['k'] for e in events if 'k' in e]


class RedactorTests(unittest.TestCase):
    def setUp(self):
        self.red = L.Redactor()

    def test_a_held_key_is_one_press_with_its_duration_written_after_the_hold_back(self):
        self.assertEqual(feed_all(self.red, key(T0, 'W', 1.0)), [])          # letters wait 7 s to be told from typing
        self.assertEqual(self.red.tick(T0 + 3), [])
        self.assertEqual(self.red.tick(T0 + 10), [{'t': T0, 'k': 'W', 'ms': 1000}])
        self.assertEqual(feed_all(self.red, key(T0 + 20, 'Space', 0.2)), [{'t': T0 + 20, 'k': 'Space', 'ms': 200}])

    def test_hotbar_digits_and_function_keys_are_kept_even_when_fast(self):
        events = [e for i, k in enumerate('123456') for e in key(T0 + i * 0.3, k, 0.1)]
        self.assertEqual(names(feed_all(self.red, events)), list('123456'))
        self.assertEqual(self.red.tick(T0 + 30), [])

    def test_fast_strafing_looks_like_typing_unless_the_owner_exempts_those_keys(self):
        events = [e for i, k in enumerate('WASDWASD') for e in key(T0 + i * 0.2, k, 0.1)]
        self.assertEqual(names(feed_all(self.red, events)), [])           # default: counted, never written
        exempt = L.Redactor(['W', 'A', 'S', 'D'])
        self.assertEqual(names(feed_all(exempt, events)), list('WASDWASD'))

    def test_chat_text_is_counted_not_kept(self):
        events = key(T0, 'Enter', 0.05) + [e for i, k in enumerate('HELLO') for e in key(T0 + 1 + i * 0.2, k, 0.05)]
        events += key(T0 + 3, 'Enter', 0.05)
        out = feed_all(self.red, events)
        self.assertEqual(names(out), ['Enter', 'Enter'])
        typed = [e for e in out if 'typed' in e]
        self.assertEqual((len(typed), typed[0]['typed'], typed[0]['end']), (1, 5, 'sent'))
        for letter in 'HELO':
            self.assertNotIn(f'"{letter}"', json.dumps(out))

    def test_a_slash_command_is_counted_not_kept(self):
        events = key(T0, 'Slash', 0.05) + [e for i, k in enumerate('FOLLOW') for e in key(T0 + 0.5 + i * 0.2, k, 0.05)]
        events += key(T0 + 3, 'Enter', 0.05)
        out = feed_all(self.red, events)
        self.assertEqual(names(out), ['Enter'])
        self.assertEqual([e['typed'] for e in out if 'typed' in e], [7])

    def test_escape_cancels_typing(self):
        out = feed_all(self.red, key(T0, 'Enter', 0.05) + key(T0 + 1, 'X', 0.05) + key(T0 + 2, 'Esc', 0.05))
        self.assertEqual([e['end'] for e in out if 'typed' in e], ['cancelled'])
        self.assertNotIn('"X"', json.dumps(out))

    def test_typing_that_is_never_closed_ends_by_itself(self):
        feed_all(self.red, key(T0, 'Enter', 0.05) + key(T0 + 1, 'A', 0.05))
        self.assertEqual(self.red.tick(T0 + 10), [])
        out = self.red.tick(T0 + 25)
        self.assertEqual([(e['typed'], e['end']) for e in out], [(1, 'idle')])
        # and the keys after that are logged again
        self.assertEqual(names(feed_all(self.red, key(T0 + 30, 'F1', 0.1))), ['F1'])

    def test_a_typing_like_run_outside_chat_is_counted_not_kept(self):
        events = [e for i, k in enumerate('PASSWORD') for e in key(T0 + i * 0.3, k, 0.08)]
        out = feed_all(self.red, events) + self.red.tick(T0 + 4)
        self.assertEqual(names(out), [])                              # nothing before the run was long enough to log
        out = self.red.tick(T0 + 30)
        self.assertEqual([(e['typed'], e['end']) for e in out], [(8, 'idle')])
        self.assertEqual(self.red.pending, [])
        self.assertNotIn('"P"', json.dumps(out))

    def test_a_short_run_of_letters_is_a_normal_press_after_the_hold(self):
        events = [e for i, k in enumerate('RFXZC') for e in key(T0 + i * 0.3, k, 0.08)]
        self.assertEqual(feed_all(self.red, events), [])              # held back, not yet written
        self.assertEqual(names(self.red.tick(T0 + 20)), list('RFXZC'))

    def test_slow_typing_is_the_residual_risk_and_is_logged(self):
        events = [e for i, k in enumerate('PASSWORD') for e in key(T0 + i * 2.0, k, 0.08)]
        feed_all(self.red, events)
        self.assertEqual(len(names(self.red.tick(T0 + 60))), 8)       # documented limit: the gate is what protects here

    def test_the_gate_closing_keeps_no_text(self):
        feed_all(self.red, [dict(t=T0, kind='down', k='W')])
        feed_all(self.red, key(T0 + 1, 'Enter', 0.05) + key(T0 + 1.5, 'Q', 0.05)[:1])
        out = self.red.flush(T0 + 3)
        self.assertIn('W', names(out))
        self.assertEqual([(e['typed'], e['end']) for e in out if 'typed' in e], [(1, 'closed')])
        self.assertEqual((self.red.holds, self.red.pending, self.red.typing), ({}, [], None))

    def test_letters_held_back_when_the_gate_closes_become_a_count(self):
        feed_all(self.red, [e for i, k in enumerate('RFXZ') for e in key(T0 + i * 0.3, k, 0.08)])
        out = self.red.flush(T0 + 2)
        self.assertEqual(names(out), [])
        self.assertEqual([e['typed'] for e in out], [4])

    def test_mouse_buttons_keep_their_position_even_while_typing(self):
        out = feed_all(self.red, key(T0, 'Enter', 0.05) + key(T0 + 1, 'MouseLeft', 0.1, x=40, y=60))
        click = [e for e in out if e.get('k') == 'MouseLeft'][0]
        self.assertEqual((click['x'], click['y'], click['ms']), (40, 60, 100))


class GateTests(unittest.TestCase):
    ONLINE = (True, {'zone': 'tatooine', 'x': 1, 'y': 2}, 'online')

    def test_open_only_when_everything_holds(self):
        self.assertEqual(L.gate(False, 'swgemu.exe', ['swgemu.exe'], self.ONLINE)[0], True)
        self.assertEqual(L.gate(False, 'SWGEmu.EXE', ['swgemu.exe'], self.ONLINE)[0], True)
        self.assertEqual(L.gate(True, 'swgemu.exe', ['swgemu.exe'], self.ONLINE), (False, 'paused'))
        self.assertEqual(L.gate(False, 'notepad.exe', ['swgemu.exe'], self.ONLINE), (False, 'client not in front'))
        self.assertEqual(L.gate(False, '', ['swgemu.exe'], self.ONLINE)[0], False)
        self.assertEqual(L.gate(False, 'swgemu.exe', ['swgemu.exe'], None), (False, 'player list not checked'))
        self.assertEqual(L.gate(False, 'swgemu.exe', ['swgemu.exe'], (False, None, 'no owner character online')),
                         (False, 'no owner character online'))


class WhoTests(unittest.TestCase):
    def who(self, clients, age=5, fail=0):
        calls = {'n': 0}

        def reader(path):
            calls['n'] += 1
            if calls['n'] <= fail:
                raise FileNotFoundError(path)
            return {'clients': clients}, T0 - age
        return reader

    def test_an_owner_character_online_opens_it_and_gives_the_position(self):
        clients = [{'firstName': 'Botty', 'zone': 'naboo'},
                   {'firstName': 'alpha', 'zone': 'tatooine', 'worldPositionX': 10.0, 'worldPositionY': -20.0}]
        ok, info, why = L.read_who(['p'], ['Alpha'], T0, 400, self.who(clients))
        self.assertEqual((ok, info, why), (True, {'zone': 'tatooine', 'x': 10.0, 'y': -20.0}, 'online'))

    def test_logged_out_stale_or_missing_closes_it(self):
        out = [{'firstName': 'Alpha', 'isOnline': False}]
        self.assertEqual(L.read_who(['p'], ['Alpha'], T0, 400, self.who(out))[0::2], (False, 'no owner character online'))
        self.assertEqual(L.read_who(['p'], ['Alpha'], T0, 400, self.who([{'firstName': 'Alpha'}], age=900))[0::2],
                         (False, 'player list is stale'))
        self.assertEqual(L.read_who(['p'], [], T0, 400, self.who([]))[0::2], (False, 'no characters configured (run setup)'))
        with mock.patch.object(L.time, 'sleep'):
            self.assertEqual(L.read_who(['p'], ['Alpha'], T0, 400, self.who([], fail=99))[0::2],
                             (False, 'player list not readable'))

    def test_a_file_that_is_briefly_missing_while_core3_swaps_it_is_retried(self):
        with mock.patch.object(L.time, 'sleep'):
            ok = L.read_who(['p'], ['Alpha'], T0, 400, self.who([{'firstName': 'Alpha'}], fail=2))[0]
        self.assertTrue(ok)

    def test_the_other_galaxy_is_tried_too(self):
        reader = mock.Mock(side_effect=[({'clients': []}, T0), ({'clients': [{'firstName': 'Alpha'}]}, T0)])
        self.assertTrue(L.read_who(['test', 'live'], ['Alpha'], T0, 400, reader)[0])


class FakePlatform:
    def __init__(self):
        self.fg, self.down, self.key_calls = 'notepad.exe', set(), 0

    def fg_exe(self):
        return self.fg

    def key_down(self, vk):
        self.key_calls += 1
        return vk in self.down

    def cursor_in_window(self):
        return 100, 200


class RecorderTests(unittest.TestCase):
    CFG = dict(L.DEFAULTS, characters=['Alpha'], who_files=['p'])

    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.dir.cleanup)
        self.folder = Path(self.dir.name)
        self.plat = FakePlatform()
        self.clients = [{'firstName': 'Alpha', 'zone': 'tatooine', 'worldPositionX': 1.0, 'worldPositionY': 2.0}]
        self.rec = L.Recorder(self.CFG, self.plat, L.EventLog(self.folder), self.folder, lambda p: ({'clients': self.clients}, time.time()))
        self.t = time.time()

    def go(self, seconds, step=0.25):
        end = self.t + seconds
        while self.t < end:
            self.rec.step(self.t)
            self.t += step

    def events(self):
        return self.rec.log.read(0)

    def test_nothing_is_read_while_another_program_is_in_front(self):
        self.plat.down = {0x57, 0x31}
        self.go(5)
        self.assertEqual((self.plat.key_calls, self.events()), (0, []))

    def test_nothing_is_read_while_no_owner_character_is_online(self):
        self.plat.fg = 'swgemu.exe'
        self.clients = [{'firstName': 'Alpha', 'isOnline': False}]
        self.go(5)
        self.assertEqual((self.plat.key_calls, [e for e in self.events() if 'k' in e]), (0, []))
        self.assertIn('no owner character online', self.rec.why)

    def test_nothing_is_read_while_paused_and_it_resumes(self):
        self.plat.fg = 'swgemu.exe'
        (self.folder / 'PAUSE').write_text('x')
        self.go(3)
        self.assertEqual(self.plat.key_calls, 0)
        (self.folder / 'PAUSE').unlink()
        self.go(1)
        self.assertGreater(self.plat.key_calls, 0)

    def test_while_open_a_press_and_the_position_are_recorded(self):
        self.plat.fg = 'swgemu.exe'
        self.go(1)
        self.plat.down = {0x57}
        self.go(1)
        self.plat.down = set()
        self.go(1)
        self.assertEqual([e for e in self.events() if e.get('k') == 'W'], [])      # letters wait 7 s
        self.go(8)
        out = self.events()
        self.assertEqual([e['gate'] for e in out if 'gate' in e], ['open'])
        press = [e for e in out if e.get('k') == 'W']
        self.assertEqual(len(press), 1)
        self.assertTrue(900 <= press[0]['ms'] <= 1500, press)
        self.assertEqual([e['pos'] for e in out if 'pos' in e], [{'zone': 'tatooine', 'x': 1.0, 'y': 2.0}])

    def test_a_mouse_click_has_a_position_inside_the_window(self):
        self.plat.fg = 'swgemu.exe'
        self.go(1)
        self.plat.down = {1}
        self.go(0.5)
        self.plat.down = set()
        self.go(0.5)
        click = [e for e in self.events() if e.get('k') == 'MouseLeft'][0]
        self.assertEqual((click['x'], click['y']), (100, 200))

    def test_keys_already_held_when_it_opens_are_not_reported(self):
        self.plat.down = {0x57}
        self.go(1)                                   # other program in front
        self.plat.fg = 'swgemu.exe'
        self.go(2)
        self.assertEqual([e for e in self.events() if 'k' in e], [])

    def test_alt_tab_during_chat_keeps_no_text_and_closes_the_gate(self):
        self.plat.fg = 'swgemu.exe'
        self.go(1)
        for vk in (0x0D, 0x48, 0x49, 0x21 + 0x20):      # Enter, H, I, then a letter-ish code
            self.plat.down = {vk}
            self.go(0.3)
            self.plat.down = set()
            self.go(0.3)
        self.plat.fg = 'chrome.exe'
        self.go(1)
        text = json.dumps(self.events())
        self.assertIn('"gate": "closed"', text)
        self.assertNotIn('"k":"H"', text)
        self.assertNotIn('"k":"I"', text)
        self.assertEqual(len([e for e in self.events() if 'typed' in e]), 1)

    def test_a_whole_chat_message_leaves_only_a_count(self):
        self.plat.fg = 'swgemu.exe'
        self.go(1)
        for vk in [0x0D] + [ord(c) for c in 'SECRETPW'] + [0x0D]:
            self.plat.down = {vk}
            self.go(0.15, step=0.05)
            self.plat.down = set()
            self.go(0.15, step=0.05)
        self.go(10)
        written = '\n'.join(p.read_text() for p in self.folder.glob('events-*.jsonl'))
        for letter in 'SECRTPW':
            self.assertNotIn(f'"k":"{letter}"', written)
        self.assertEqual([e['typed'] for e in self.events() if 'typed' in e], [8])

    def test_state_file_and_stop_file(self):
        self.go(3)
        state = json.loads((self.folder / 'state.json').read_text())
        self.assertEqual((state['open'], state['pid']), (False, os.getpid()))
        (self.folder / 'STOP').write_text('x')
        self.assertTrue(self.rec.stopping())

    def test_closing_while_open_writes_the_closed_marker(self):
        self.plat.fg = 'swgemu.exe'
        self.go(1)
        self.rec.close(self.t)
        self.assertEqual([e['gate'] for e in self.events() if 'gate' in e], ['open', 'closed'])


class LogAndCommandTests(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.dir.cleanup)
        self.log = L.EventLog(self.dir.name, keep_hours=48)

    def test_files_are_per_hour_old_ones_are_pruned_and_a_torn_line_is_skipped(self):
        self.log.write({'t': T0, 'k': 'W', 'ms': 5})
        self.log.write({'t': T0 + 7200, 'k': 'S', 'ms': 5})
        self.assertEqual(len(list(Path(self.dir.name).glob('events-*.jsonl'))), 2)
        with next(Path(self.dir.name).glob('events-*.jsonl')).open('a') as f:
            f.write('{"t": 1, "k"')
        self.assertEqual([e['k'] for e in self.log.read(0)], ['W', 'S'])
        old, new = sorted(Path(self.dir.name).glob('events-*.jsonl'))
        os.utime(old, (T0 - 3 * 86400, T0 - 3 * 86400))
        os.utime(new, (T0, T0))
        self.log.prune(T0)
        self.assertEqual(len(list(Path(self.dir.name).glob('events-*.jsonl'))), 1)

    def test_summary_counts_without_text(self):
        events = [{'t': T0, 'gate': 'open'}] + [{'t': T0 + i, 'k': 'W', 'ms': 500} for i in range(3)] + [
            {'t': T0 + 5, 'k': 'MouseLeft', 'ms': 80, 'x': 1, 'y': 2}, {'t': T0 + 6, 'typed': 12, 'ms': 4000, 'end': 'sent'},
            {'t': T0 + 7, 'pos': {'zone': 'tatooine', 'x': 1.0, 'y': 2.0}}, {'t': T0 + 8, 'mark': 'boss fight'}]
        text = '\n'.join(L.summarize(events, 10))
        for want in ('W x3', 'mouse: left x1', 'typing: 1 time(s), 12 characters (text not kept)', 'tatooine', 'boss fight'):
            self.assertIn(want, text)
        self.assertIn('nothing recorded', '\n'.join(L.summarize([], 10)))
        self.assertIn('text not kept', L.fmt(events[5]))

    def test_pid_alive_never_ends_a_process(self):
        self.assertTrue(L.pid_alive(os.getpid()))
        self.assertFalse(L.pid_alive(None))
        self.assertFalse(L.pid_alive(2_000_000_000))

    def test_setup_leaves_out_bots_and_prints_no_names(self):
        root = Path(self.dir.name)
        (root / 'list.txt').write_text('Test Galaxy,Alpha Tester (Test Galaxy),0,2\nTest Galaxy,Beta Tester (Test Galaxy),0,2\n'
                                       'Test Galaxy,Kael Tester (Test Galaxy),0,2\n', encoding='utf-8')
        (root / 'groups.json').write_text(json.dumps({'groups': {'g': {'members': [{'name': 'Beta Bot'}]}}}))
        out = io.StringIO()
        with mock.patch.object(L, 'CHARACTER_LIST', root / 'list.txt'), mock.patch.object(L, 'GROUPS', root / 'groups.json'), \
                mock.patch.object(L, 'CONFIG', root / 'cfg.json'), contextlib.redirect_stdout(out):
            L.cmd_setup()
        self.assertEqual(json.loads((root / 'cfg.json').read_text())['characters'], ['Alpha'])
        for name in ('Alpha', 'Beta', 'Kael'):
            self.assertNotIn(name, out.getvalue())
        self.assertIn('1 character(s)', out.getvalue())

    def test_forget_and_mark_through_the_commands(self):
        with mock.patch.object(L, 'DATA', Path(self.dir.name)), contextlib.redirect_stdout(io.StringIO()) as out:
            L.main(['mark', 'hello'])
            self.assertEqual(len(list(Path(self.dir.name).glob('events-*.jsonl'))), 1)
            L.main(['tail', '5'])
            self.assertIn('note: hello', out.getvalue())
            L.main(['forget'])
        self.assertEqual(list(Path(self.dir.name).glob('events-*.jsonl')), [])


@unittest.skipUnless(os.name == 'nt', 'Windows only')
class WindowsSmokeTests(unittest.TestCase):
    def test_which_program_is_in_front_reads_no_key(self):
        platform = L.WindowsInput()
        self.assertIsInstance(platform.fg_exe(), str)


if __name__ == '__main__':
    unittest.main()
