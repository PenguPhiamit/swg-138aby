"""Offline tests for ollama_url.py, the remote-server path of idle_research.py and local_agent.py's address handling.

No real Ollama and no other PC: a tiny fake server answers on 127.0.0.1 only, and a guard fails any test that tries to
open a connection to another address. idle_research.py needs fcntl, so its tests run in WSL Debian:

    wsl -d Debian -u swgemu -- python3 /mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/tools/agents/local/test_ollama_url.py
"""
import contextlib
import email.utils
import io
import json
import os
import sys
import tempfile
import threading
import time
import unittest
import urllib.parse
import urllib.request
import warnings
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import ollama_url
import local_agent
try:
    import idle_research as ir
except ImportError:   # no fcntl: Windows
    ir = None

_real_urlopen = urllib.request.urlopen
_guard = None


def only_loopback(url, *args, **kwargs):
    target = url.full_url if hasattr(url, 'full_url') else url
    host = urllib.parse.urlsplit(target).hostname
    if host != '127.0.0.1':
        raise AssertionError(f'a test tried to reach {host}')
    return _real_urlopen(url, *args, **kwargs)


def setUpModule():
    global _guard
    warnings.simplefilter('ignore', ResourceWarning)   # idle_research.main() and local_agent.main() leave files to exit
    _guard = mock.patch('urllib.request.urlopen', only_loopback)
    _guard.start()


def tearDownModule():
    _guard.stop()


def iso(epoch, hours=-7):
    """An expires_at the way Ollama writes it: RFC 3339, 7 fraction digits, the zone's offset."""
    when = datetime.fromtimestamp(epoch, timezone(timedelta(hours=hours)))
    return when.strftime('%Y-%m-%dT%H:%M:%S.0000000') + f'{hours:+03d}:00'


class FakeOllama:
    """/api/tags, /api/ps and /api/chat on 127.0.0.1; its Date header says `clock`."""

    def __init__(self):
        self.models, self.clock, self.requests = [], 1_800_000_000.0, []
        self.chat_reply = {'message': {'role': 'assistant', 'content': 'all done'}}
        fake = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass

            def date_time_string(self, timestamp=None):
                return email.utils.formatdate(fake.clock, usegmt=True)

            def reply(self, body):
                data = json.dumps(body).encode()
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Content-Length', str(len(data)))
                self.end_headers()
                self.wfile.write(data)

            def do_GET(self):
                fake.requests.append(('GET', self.path, None))
                self.reply({'models': fake.models} if self.path == '/api/ps' else {'models': []})

            def do_POST(self):
                body = json.loads(self.rfile.read(int(self.headers.get('Content-Length', 0))) or b'null')
                fake.requests.append(('POST', self.path, body))
                self.reply(fake.chat_reply)

        self.httpd = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        self.base = f'http://127.0.0.1:{self.httpd.server_address[1]}'
        threading.Thread(target=self.httpd.serve_forever, daemon=True).start()

    def loaded(self, name, expires):
        self.models = [{'name': name, 'model': name, 'expires_at': expires}] if name else []

    def stop(self):
        self.httpd.shutdown()
        self.httpd.server_close()


class AddressTests(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.dir.cleanup)
        self.file = Path(self.dir.name) / 'ollama-url.txt'

    def url(self, env=None, file=None):
        if file is not None:
            self.file.write_bytes(file if isinstance(file, bytes) else file.encode())
        return ollama_url.base_url(environ=env or {}, path=self.file)

    def test_default_is_this_pc(self):
        self.assertEqual(self.url(), 'http://127.0.0.1:11434')
        self.assertEqual(ollama_url.DEFAULT, 'http://127.0.0.1:11434')

    def test_file_beats_default_and_variable_beats_file(self):
        self.assertEqual(self.url(file='http://192.168.7.8:11434\n'), 'http://192.168.7.8:11434')
        self.assertEqual(self.url({'OLLAMA_URL': 'http://10.0.0.9:11434'}), 'http://10.0.0.9:11434')

    def test_blank_variable_falls_through_to_the_file(self):
        self.assertEqual(self.url({'OLLAMA_URL': '  '}, file='http://192.168.7.8:11434'), 'http://192.168.7.8:11434')

    def test_file_survives_windows_editors(self):
        for raw in ('# the friend\r\n\r\nhttp://192.168.7.8:11434\r\n'.encode(), b'\xef\xbb\xbfhttp://192.168.7.8:11434',
                    b'\xff\xfe' + 'http://192.168.7.8:11434\r\n'.encode('utf-16-le')):   # PowerShell 5.1 ">"
            self.assertEqual(self.url(file=raw), 'http://192.168.7.8:11434', raw)

    def test_empty_or_comment_only_file_is_the_default(self):
        self.assertEqual(self.url(file='# nothing yet\n\n'), ollama_url.DEFAULT)
        self.assertEqual(self.url(file=''), ollama_url.DEFAULT)

    def test_forms_of_an_address(self):
        n = ollama_url.normalize
        self.assertEqual(n('192.168.7.8'), 'http://192.168.7.8:11434')
        self.assertEqual(n('friend-pc.local:5000'), 'http://friend-pc.local:5000')
        self.assertEqual(n(' http://192.168.7.8:11434/ '), 'http://192.168.7.8:11434')
        self.assertEqual(n('https://ollama.example'), 'https://ollama.example')
        self.assertEqual(n('http://[fe80::1]:11434'), 'http://[fe80::1]:11434')
        self.assertEqual(n('http://host/ollama/'), 'http://host/ollama')

    def test_bad_addresses_fail_loudly_and_name_their_source(self):
        for bad in ('ftp://host', 'http://', 'http://u:p@host:11434', 'http://host:abc', 'http://host/api/chat',
                    'http://host:11434?x=1', '://x'):
            with self.assertRaises(ollama_url.OllamaUrlError, msg=bad):
                ollama_url.normalize(bad)
        with self.assertRaisesRegex(ollama_url.OllamaUrlError, 'OLLAMA_URL variable'):
            self.url({'OLLAMA_URL': 'ftp://host'})
        self.file.write_text('http://host/api/tags')
        with self.assertRaisesRegex(ollama_url.OllamaUrlError, 'ollama-url.txt'):
            self.url()

    def test_local_means_this_pc(self):
        for local in ('http://127.0.0.1:11434', 'http://localhost:11434', 'http://[::1]:11434', 'http://0.0.0.0:11434',
                      'http://127.0.0.2:11434', 'http://[::ffff:127.0.0.1]:11434', 'http://LOCALHOST'):
            self.assertTrue(ollama_url.is_local(local), local)
        for remote in ('http://192.168.7.8:11434', 'http://friend-pc.local:11434', 'http://10.0.0.2', 'http://8.8.8.8',
                       'https://ollama.example', 'http://[fe80::1]:11434'):
            self.assertFalse(ollama_url.is_local(remote), remote)

    def test_api_joins_routes(self):
        self.assertEqual(ollama_url.api('/api/chat', 'http://192.168.7.8:11434'), 'http://192.168.7.8:11434/api/chat')
        self.assertEqual(ollama_url.api('api/ps', 'http://host/ollama/'), 'http://host/ollama/api/ps')

    def test_describe_has_no_scheme_or_path(self):
        self.assertEqual(ollama_url.describe('http://192.168.7.8:11434'), '192.168.7.8:11434')

    def test_the_address_file_is_gitignored(self):
        root = next((p for p in HERE.parents if (p / '.gitignore').exists()), None)
        if root is None:
            self.skipTest('no .gitignore above this folder')
        rule = ollama_url.URL_FILE.relative_to(root).as_posix()
        lines = (root / '.gitignore').read_text(encoding='utf-8').splitlines()
        self.assertIn(rule, [line.strip() for line in lines])


@unittest.skipIf(ir is None, 'idle_research.py needs fcntl (run in WSL)')
class ExpiryTests(unittest.TestCase):
    NOW = 1_800_000_000.0

    def test_go_style_stamps(self):
        want = datetime(2026, 10, 15, 14, 59, 44, 519813, timezone.utc).timestamp()
        for text in ('2026-10-15T07:59:44.5198135-07:00', '2026-10-15T14:59:44.519813Z', '2026-10-15T16:59:44.519813+02:00'):
            self.assertAlmostEqual(ir.parse_expiry(text, self.NOW), want, delta=0.00001, msg=text)
        self.assertAlmostEqual(ir.parse_expiry('2026-10-15T14:59:44Z', self.NOW), int(want), delta=0.00001)

    def test_never_and_junk_have_no_expiry(self):
        for text in (None, '', 'soon', '0001-01-01T00:00:00Z', '2318-04-11T23:47:16.8547758-07:00',
                     '2026-10-15T07:59:44', '2026-13-45T07:59:44Z'):
            self.assertIsNone(ir.parse_expiry(text, self.NOW), text)

    def test_a_long_but_finite_keep_alive_is_fine(self):
        self.assertIsNotNone(ir.parse_expiry(iso(self.NOW + 24 * 3600), self.NOW))


@unittest.skipIf(ir is None, 'idle_research.py needs fcntl (run in WSL)')
class RemoteStepTests(unittest.TestCase):
    T = 1_800_000_000.0

    def look(self, prev, models, at, server=None):
        return ir.remote_step(prev, 'k', models, self.T + at if server is None else server, self.T + at)

    def test_ten_quiet_minutes_across_timer_runs(self):
        rec, why = self.look(None, {'m': self.T + 250}, 0)
        self.assertIn('first look', why[0])
        rec, why = self.look(rec, {}, 300)            # the model timed out by itself: still quiet
        self.assertIn('5 of 10 min', why[0])
        rec, why = self.look(rec, {}, 600)
        self.assertEqual(why, [])

    def test_timer_jitter_of_half_a_minute_is_allowed(self):
        rec, _ = self.look(None, {}, 0)
        rec, _ = self.look(rec, {}, 290)
        self.assertEqual(self.look(rec, {}, 575)[1], [])
        self.assertTrue(self.look(rec, {}, 560)[1])

    def test_a_finished_request_restarts_the_window(self):
        rec, _ = self.look(None, {'m': self.T + 400}, 0)
        rec, _ = self.look(rec, {'m': self.T + 400}, 300)   # same expiry: nobody used it (model not yet timed out)
        rec, why = self.look(rec, {'m': self.T + 600 + 300}, 600)   # expiry moved: someone's request finished
        self.assertIn('used since the last look', why[0])
        self.assertEqual(rec['since'], self.T + 600)
        rec, why = self.look(rec, {}, 900)
        self.assertIn('5 of 10', why[0])
        self.assertEqual(self.look(rec, {}, 1200)[1], [])

    def test_a_new_model_or_an_early_unload_counts_as_use(self):
        rec, _ = self.look(None, {}, 0)
        self.assertIn('used since', self.look(rec, {'m': self.T + 500}, 300)[1][0])
        rec, _ = self.look(None, {'m': self.T + 900}, 0)
        self.assertIn('used since', self.look(rec, {}, 300)[1][0])      # gone at 300 although it expires at 900

    def test_a_model_past_its_expiry_is_mid_request(self):
        rec, why = self.look(None, {'m': self.T - 60}, 0)
        self.assertIn('mid-request', why[0])
        self.assertEqual(rec['since'], self.T)
        self.assertEqual(self.look(None, {'m': self.T - 5}, 0)[1][0][:5], 'first')   # unload lag is not a request

    def test_no_expiry_means_no_signal(self):
        rec, why = self.look(None, {'m': None}, 0)
        self.assertIsNone(rec)
        self.assertIn('no usable expiry', why[0])

    def test_a_long_gap_between_looks_starts_over(self):
        rec, _ = self.look(None, {}, 0)
        rec, why = self.look(rec, {}, 3600)
        self.assertIn('first look', why[0])

    def test_another_server_starts_over(self):
        rec, _ = ir.remote_step(None, 'a', {}, self.T, self.T)
        rec, why = ir.remote_step(rec, 'b', {}, self.T + 300, self.T + 300)
        self.assertIn('first look', why[0])


@unittest.skipIf(ir is None, 'idle_research.py needs fcntl (run in WSL)')
class IdleResearchTests(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.dir.cleanup)
        root = Path(self.dir.name)
        self.root = root
        for name, value in dict(BASE=root, QUEUE=root / 'queue.json', LOG=root / 'LOG.md', STATE=root / 'state.json',
                                STOP=root / 'STOP', OLLAMA_LOG=root / 'server.log').items():
            patcher = mock.patch.object(ir, name, value)
            patcher.start()
            self.addCleanup(patcher.stop)
        self.fake = FakeOllama()
        self.addCleanup(self.fake.stop)
        env = mock.patch.dict(os.environ, {'OLLAMA_URL': self.fake.base})
        env.start()
        self.addCleanup(env.stop)
        # the address file must not leak in from the real folder
        patcher = mock.patch.object(ollama_url, 'URL_FILE', root / 'none.txt')
        patcher.start()
        self.addCleanup(patcher.stop)

    def as_other_pc(self):
        """Treat the fake (which is on 127.0.0.1) as a server on another PC, and fail if a local check runs."""
        for name in ('gpu_busy', 'owner_client', 'last_request'):
            patcher = mock.patch.object(ir, name, side_effect=AssertionError(f'{name} is about this PC'))
            patcher.start()
            self.addCleanup(patcher.stop)
        patcher = mock.patch.object(ollama_url, 'is_local', lambda base: False)
        patcher.start()
        self.addCleanup(patcher.stop)

    def state(self):
        return json.loads((self.root / 'state.json').read_text(encoding='utf-8'))

    # ---- this PC: the checks are the ones the timer has always made ----
    def log_request(self, seconds_ago):
        stamp = time.strftime('%Y/%m/%d - %H:%M:%S', time.localtime(time.time() - seconds_ago))
        with (self.root / 'server.log').open('a') as f:
            f.write(f'[GIN] {stamp} | 200 |  1m2s |  127.0.0.1 | POST     "/api/chat"\n')

    def local_checks(self, gpu=0, client=False):
        for name, value in (('gpu_busy', gpu), ('owner_client', client)):
            patcher = mock.patch.object(ir, name, return_value=value)
            patcher.start()
            self.addCleanup(patcher.stop)

    def test_this_pc_idle_when_the_log_is_quiet(self):
        self.local_checks()
        self.log_request(3600)
        self.assertEqual(ir.blockers(), [])
        self.assertIsNone(ir.remote_base())
        self.assertFalse((self.root / 'state.json').exists())    # nothing is recorded for this PC

    def test_this_pc_busy_when_the_log_is_recent_the_gpu_busy_or_a_client_runs(self):
        self.local_checks(gpu=80, client=True)
        self.log_request(30)
        why = '; '.join(ir.blockers())
        self.assertIn('Ollama was used', why)
        self.assertIn('GPU at 80 %', why)
        self.assertIn("owner's SWG client", why)

    def test_this_pc_not_answering(self):
        self.local_checks()
        self.log_request(3600)
        self.fake.stop()
        self.assertEqual(ir.blockers(), ['Ollama is not answering'])

    def test_this_pc_uses_api_tags(self):
        self.local_checks()
        self.log_request(3600)
        ir.blockers()
        self.assertEqual(self.fake.requests, [('GET', '/api/tags', None)])

    def test_a_bad_address_is_a_blocker_not_a_crash(self):
        with mock.patch.dict(os.environ, {'OLLAMA_URL': 'ftp://nowhere'}):
            self.assertIn('bad Ollama address', ir.blockers()[0])

    # ---- another PC ----
    def test_other_pc_needs_ten_quiet_minutes_over_consecutive_runs(self):
        self.as_other_pc()
        t0 = self.fake.clock
        self.fake.loaded('gpt-oss:20b', iso(t0 + 250))
        self.assertIn('first look', ir.remote_blockers(self.fake.base, True, now=t0)[0])
        self.fake.clock, self.fake.models = t0 + 300, []
        self.assertIn('5 of 10', ir.remote_blockers(self.fake.base, True, now=t0 + 300)[0])
        self.fake.clock = t0 + 600
        self.assertEqual(ir.remote_blockers(self.fake.base, True, now=t0 + 600), [])
        self.assertTrue(all(r[1] == '/api/ps' for r in self.fake.requests))
        self.assertNotIn('127.0.0.1', json.dumps(self.state()))      # the state file holds a hash, not the address

    def test_status_reads_but_never_records(self):
        self.as_other_pc()
        t0 = self.fake.clock
        ir.remote_blockers(self.fake.base, True, now=t0)
        before = self.state()
        self.fake.clock = t0 + 300
        self.assertIn('5 of 10', ir.remote_blockers(self.fake.base, False, now=t0 + 300)[0])
        self.assertEqual(self.state(), before)

    def test_use_by_someone_else_restarts_the_count(self):
        self.as_other_pc()
        t0 = self.fake.clock
        self.fake.loaded('gpt-oss:20b', iso(t0 + 300))
        ir.remote_blockers(self.fake.base, True, now=t0)
        self.fake.clock = t0 + 300
        self.fake.loaded('gpt-oss:20b', iso(t0 + 600))               # a request finished at t0+300
        self.assertIn('used since', ir.remote_blockers(self.fake.base, True, now=t0 + 300)[0])
        self.fake.clock = t0 + 600
        self.assertIn('5 of 10', ir.remote_blockers(self.fake.base, True, now=t0 + 600)[0])

    def test_the_other_pcs_clock_may_be_hours_off(self):
        self.as_other_pc()
        skew = 5 * 3600
        t0 = self.fake.clock = 1_800_000_000.0 + skew                  # its clock; this PC's `now` is 5 h earlier
        self.fake.loaded('gpt-oss:20b', iso(t0 + 250, hours=2))
        self.assertIn('first look', ir.remote_blockers(self.fake.base, True, now=t0 - skew)[0])
        self.fake.models = []
        for later in (300, 600):
            self.fake.clock = t0 + later
            why = ir.remote_blockers(self.fake.base, True, now=t0 - skew + later)
        self.assertEqual(why, [])           # the model timing out on its own clock is not "used", nor "mid-request"

    def test_other_pc_off_is_a_blocker_and_forgets_the_count(self):
        self.as_other_pc()
        t0 = self.fake.clock
        ir.remote_blockers(self.fake.base, True, now=t0)
        self.assertIn('remote', self.state())
        self.fake.stop()
        why = ir.remote_blockers(self.fake.base, True, now=t0 + 300)
        self.assertIn('is not answering', why[0])
        self.assertNotIn('remote', self.state())

    def test_stop_file_still_wins(self):
        self.as_other_pc()
        (self.root / 'STOP').write_text('paused')
        self.assertIn('STOP exists', ir.blockers()[0])

    def test_main_status_names_the_server_only_when_it_is_another_pc(self):
        queue = {'topics': [{'id': 't1', 'status': 'open', 'title': 'x', 'question': 'y', 'sources': []}]}
        ir.save(ir.QUEUE, queue)
        self.local_checks()
        self.log_request(3600)
        out = io.StringIO()
        with mock.patch.object(sys, 'argv', ['idle_research.py', 'status']), contextlib.redirect_stdout(out):
            ir.main()
        self.assertEqual(out.getvalue(), '1 open topic(s); idle: would start t1\n')
        self.as_other_pc()
        out = io.StringIO()
        with mock.patch.object(sys, 'argv', ['idle_research.py', 'status']), contextlib.redirect_stdout(out):
            ir.main()
        self.assertTrue(out.getvalue().startswith(f'[remote Ollama {ollama_url.describe(self.fake.base)}] 1 open'))
        self.assertIn('first look', out.getvalue())

    # ---- running a topic ----
    def stub_agent(self, body):
        path = self.root / 'stub_agent.py'
        path.write_text('import os, sys, pathlib\nws = pathlib.Path(sys.argv[sys.argv.index("--workspace") + 1])\n' + body)
        patcher = mock.patch.object(ir, 'AGENT', path)
        patcher.start()
        self.addCleanup(patcher.stop)

    def topic(self):
        topic = {'id': 't1', 'status': 'running', 'title': 'x', 'question': 'y', 'sources': []}
        ir.save(ir.QUEUE, {'topics': [topic]})
        return topic

    def test_a_run_hands_the_address_on_scrubs_it_and_keeps_the_idle_count(self):
        self.as_other_pc()
        self.stub_agent('print("talking to", os.environ["OLLAMA_URL"])\n(ws / "report.md").write_text("r" * 400)\n')
        ir.save(ir.STATE, {'last_finish': 5, 'last_topic': 'old'})
        self.assertTrue(ir.run(self.topic()))
        output = (self.root / 't1' / 'agent-output.txt').read_text()
        self.assertIn('talking to <ollama-url>', output)
        self.assertNotIn('127.0.0.1', output + (self.root / 'LOG.md').read_text())
        state = self.state()
        self.assertEqual(state['last_topic'], 't1')
        self.assertGreater(state['last_finish'], 5)
        self.assertEqual(ir.load(ir.QUEUE, {})['topics'][0]['status'], 'review')
        # our own use does not count: the next timer run, 5 minutes on, may start the next topic
        self.fake.clock += 300
        self.assertEqual(ir.remote_blockers(self.fake.base, True, now=time.time() + 300), [])

    def test_a_run_on_this_pc_leaves_the_environment_and_the_state_as_before(self):
        self.stub_agent('print("env", os.environ.get("OLLAMA_URL"))\n(ws / "report.md").write_text("r" * 400)\n')
        with mock.patch.dict(os.environ, {'OLLAMA_URL': 'http://127.0.0.1:1'}):
            self.assertTrue(ir.run(self.topic()))
        self.assertIn('env http://127.0.0.1:1', (self.root / 't1' / 'agent-output.txt').read_text())
        self.assertEqual(set(self.state()), {'last_finish', 'last_topic'})

    def test_a_server_that_vanishes_mid_run_leaves_the_topic_open(self):
        self.as_other_pc()
        self.stub_agent('sys.exit(1)\n')
        with mock.patch.object(ir, 'fetch_ps', side_effect=OSError('gone')):
            self.assertFalse(ir.run(self.topic()))
        self.assertEqual(ir.load(ir.QUEUE, {})['topics'][0]['status'], 'open')
        self.assertIn('stopped answering', (self.root / 'LOG.md').read_text())

    def test_a_failed_run_on_a_live_server_is_failed(self):
        self.as_other_pc()
        self.stub_agent('sys.exit(1)\n')
        self.assertFalse(ir.run(self.topic()))
        self.assertEqual(ir.load(ir.QUEUE, {})['topics'][0]['status'], 'failed')


class LocalAgentTests(unittest.TestCase):
    def setUp(self):
        self.fake = FakeOllama()
        self.addCleanup(self.fake.stop)
        self.dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.dir.cleanup)

    def run_main(self, *argv, env=None):
        out = io.StringIO()
        with mock.patch.object(sys, 'argv', ['local_agent.py', '--workspace', self.dir.name, '--task', 'hi', *argv]), \
                mock.patch.dict(os.environ, env or {}), mock.patch.object(ollama_url, 'URL_FILE', Path(self.dir.name) / 'x'), \
                contextlib.redirect_stdout(out):
            return local_agent.main(), out.getvalue()

    def test_chat_posts_to_the_given_server(self):
        reply = local_agent.chat('gpt-oss:20b', [{'role': 'user', 'content': 'hi'}], 4096, self.fake.base)
        self.assertEqual(reply['message']['content'], 'all done')
        method, path, body = self.fake.requests[0]
        self.assertEqual((method, path, body['model'], body['options']['num_ctx']), ('POST', '/api/chat', 'gpt-oss:20b', 4096))

    def test_flag_beats_variable(self):
        code, out = self.run_main('--ollama-url', self.fake.base, env={'OLLAMA_URL': 'http://127.0.0.1:1'})
        self.assertEqual(code, 0)
        self.assertIn('all done', out)
        self.assertEqual(self.fake.requests[0][1], '/api/chat')

    def test_variable_is_used_without_the_flag(self):
        code, out = self.run_main(env={'OLLAMA_URL': self.fake.base})
        self.assertEqual((code, len(self.fake.requests)), (0, 1))

    def test_a_bad_address_stops_before_any_request(self):
        with contextlib.redirect_stderr(io.StringIO()) as err, self.assertRaises(SystemExit):
            self.run_main('--ollama-url', 'ftp://host')
        self.assertIn('bad Ollama address', err.getvalue())
        self.assertEqual(self.fake.requests, [])


if __name__ == '__main__':
    unittest.main()
