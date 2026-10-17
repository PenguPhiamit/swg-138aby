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


def isolate(case, root):
    """No settings from the real environment or from the real folder's ollama-*.txt files."""
    patcher = mock.patch.dict(os.environ)
    patcher.start()
    case.addCleanup(patcher.stop)
    for name in ('OLLAMA_URL', 'OLLAMA_MODEL', 'OLLAMA_CTX'):
        os.environ.pop(name, None)
    for name in ('URL_FILE', 'MODEL_FILE', 'CTX_FILE'):
        patcher = mock.patch.object(ollama_url, name, Path(root) / f'no-{name}.txt')
        patcher.start()
        case.addCleanup(patcher.stop)


def iso(epoch, hours=-7):
    """An expires_at the way Ollama writes it: RFC 3339, 7 fraction digits, the zone's offset."""
    when = datetime.fromtimestamp(epoch, timezone(timedelta(hours=hours)))
    return when.strftime('%Y-%m-%dT%H:%M:%S.0000000') + f'{hours:+03d}:00'


class FakeOllama:
    """/api/tags, /api/ps and /api/chat on 127.0.0.1; its Date header says `clock`."""

    def __init__(self):
        self.models, self.clock, self.requests = [], 1_800_000_000.0, []
        self.tags = ['gpt-oss:20b']   # what the server has pulled (/api/tags)
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
                self.reply({'models': fake.models} if self.path == '/api/ps'
                           else {'models': [{'name': n, 'model': n} for n in fake.tags]})

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
        lines = [line.strip() for line in (root / '.gitignore').read_text(encoding='utf-8').splitlines()]
        for path in (ollama_url.URL_FILE, ollama_url.MODEL_FILE, ollama_url.CTX_FILE):
            self.assertIn(path.relative_to(root).as_posix(), lines)

    # ---- model and context size: the same order as the address ----
    def setting(self, getter, env=None, file=None):
        if file is not None:
            self.file.write_bytes(file if isinstance(file, bytes) else file.encode())
        return getter(environ=env or {}, path=self.file)

    def test_model_and_ctx_defaults_are_as_before(self):
        self.assertEqual(self.setting(ollama_url.model), 'gpt-oss:20b')
        self.assertEqual(self.setting(ollama_url.ctx), 65536)

    def test_model_and_ctx_come_from_variable_then_file_then_default(self):
        self.assertEqual(self.setting(ollama_url.model, file='# small\r\nqwen3:8b\r\n'), 'qwen3:8b')
        self.assertEqual(self.setting(ollama_url.model, {'OLLAMA_MODEL': 'gpt-oss:20b'}), 'gpt-oss:20b')
        self.assertEqual(self.setting(ollama_url.model, {'OLLAMA_MODEL': ' '}), 'qwen3:8b')
        self.assertEqual(self.setting(ollama_url.ctx, file=b'\xff\xfe' + '32768\r\n'.encode('utf-16-le')), 32768)
        self.assertEqual(self.setting(ollama_url.ctx, {'OLLAMA_CTX': '16384'}), 16384)
        self.assertEqual(self.setting(ollama_url.ctx, {'OLLAMA_CTX': ''}), 32768)

    def test_model_names(self):
        for name in ('qwen3:8b', 'gpt-oss:20b', 'llama3.1', 'hf.co/user/repo:Q4_K_M', 'registry.example/lib/m:1b@x'):
            self.assertEqual(ollama_url.parse_model(f' {name} '), name)
        for bad in ('', 'qwen3 8b', '-m', 'qwen3:8b;rm', 'a\tb', '"qwen3:8b"'):
            with self.assertRaises(ollama_url.OllamaSettingError, msg=bad):
                ollama_url.parse_model(bad)

    def test_context_sizes(self):
        self.assertEqual(ollama_url.parse_ctx(' 32768 '), 32768)
        for bad in ('', 'lots', '32k', '3.5', '-1', '0', '1024', '99999999'):
            with self.assertRaises(ollama_url.OllamaSettingError, msg=bad):
                ollama_url.parse_ctx(bad)

    def test_a_bad_model_or_ctx_fails_loudly_and_names_its_source(self):
        with self.assertRaisesRegex(ollama_url.OllamaSettingError, 'OLLAMA_CTX variable'):
            self.setting(ollama_url.ctx, {'OLLAMA_CTX': 'lots'})
        model_file = Path(self.dir.name) / 'ollama-model.txt'
        model_file.write_text('qwen3 8b')
        with self.assertRaisesRegex(ollama_url.OllamaSettingError, 'ollama-model.txt'):
            ollama_url.model(environ={}, path=model_file)
        self.assertNotIsInstance(ollama_url.OllamaSettingError('x'), ollama_url.OllamaUrlError)
        self.assertIsInstance(ollama_url.OllamaUrlError('x'), ollama_url.OllamaSettingError)

    def test_model_missing_reads_the_tags_answer(self):
        tags = json.dumps({'models': [{'name': 'qwen3:8b'}, {'model': 'gpt-oss:20b'}, {'name': 'tiny:latest'}]})
        self.assertIsNone(ollama_url.model_missing(tags, 'qwen3:8b'))
        self.assertIsNone(ollama_url.model_missing(tags, 'gpt-oss:20b'))
        self.assertIsNone(ollama_url.model_missing(tags, 'tiny'))          # "tiny" means tiny:latest
        self.assertIn('qwen3:8B is not on the server', ollama_url.model_missing(tags, 'qwen3:8B'))
        self.assertIn('ollama pull llama3', ollama_url.model_missing(tags, 'llama3'))
        self.assertIsNotNone(ollama_url.model_missing('{"models": []}', 'qwen3:8b'))
        for unreadable in (b'', b'<html>', b'[1]', b'null', b'{"models": 5}'):
            self.assertIsNone(ollama_url.model_missing(unreadable, 'qwen3:8b'), unreadable)


class ServerListTests(unittest.TestCase):
    """17 Oct: ollama-url.txt may list several servers (the friend's PC, then this PC), each with its model and size."""
    S = ollama_url.Server

    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.dir.cleanup)
        isolate(self, self.dir.name)

    def servers(self, text, env=None):
        ollama_url.URL_FILE.write_text(text, encoding='utf-8')
        return ollama_url.servers(environ=env or {})

    def test_one_line_files_mean_what_they_did(self):
        self.assertEqual(self.servers('http://192.168.7.8:11434\n'), [self.S('http://192.168.7.8:11434', 'gpt-oss:20b', 65536)])
        ollama_url.MODEL_FILE.write_text('qwen3:8b')
        ollama_url.CTX_FILE.write_text('16384')
        self.assertEqual(self.servers('192.168.7.8'), [self.S('http://192.168.7.8:11434', 'qwen3:8b', 16384)])
        ollama_url.URL_FILE.unlink()
        self.assertEqual(ollama_url.servers(environ={}), [self.S(ollama_url.DEFAULT, 'qwen3:8b', 16384)])

    def test_each_line_may_name_its_model_and_context(self):
        listed = self.servers('# the friend first\nhttp://192.168.7.8:11434  qwen3.6:35b-a3b  65536   # friend\n'
                              '127.0.0.1 16384 qwen3:8b\n\nlocalhost:5000\n')
        self.assertEqual(listed, [self.S('http://192.168.7.8:11434', 'qwen3.6:35b-a3b', 65536),
                                  self.S('http://127.0.0.1:11434', 'qwen3:8b', 16384),
                                  self.S('http://localhost:5000', 'gpt-oss:20b', 65536)])
        self.assertEqual(ollama_url.base_url(environ={}), 'http://192.168.7.8:11434')

    def test_variables_beat_every_line_and_OLLAMA_URL_means_one_server(self):
        text = 'http://192.168.7.8:11434 qwen3.6:35b-a3b 65536\n127.0.0.1 qwen3:8b 16384\n'
        listed = self.servers(text, {'OLLAMA_MODEL': 'tiny:1b', 'OLLAMA_CTX': '4096'})
        self.assertEqual({(s.model, s.ctx) for s in listed}, {('tiny:1b', 4096)})
        self.assertEqual(self.servers(text, {'OLLAMA_URL': '10.0.0.9'}), [self.S('http://10.0.0.9:11434', 'gpt-oss:20b', 65536)])

    def test_a_bad_line_fails_loudly_and_names_it(self):
        for text, kind, words in (('192.168.7.8\nftp://x\n', ollama_url.OllamaUrlError, 'line 2'),
                                  ('192.168.7.8 qwen3 8b\n', ollama_url.OllamaSettingError, 'two model names'),
                                  ('192.168.7.8 32768 16384\n', ollama_url.OllamaSettingError, 'two context sizes'),
                                  ('192.168.7.8 1024\n', ollama_url.OllamaSettingError, 'outside'),
                                  ('192.168.7.8 a:1 4096 x\n', ollama_url.OllamaSettingError, 'more than')):
            with self.assertRaisesRegex(kind, words, msg=text):
                self.servers(text)

    def test_pick_takes_the_first_that_answers_and_never_probes_the_fallback(self):
        self.servers('http://192.168.7.8:11434 big:1\n192.168.7.9 mid:1\n127.0.0.1 small:1\n')
        asked = []

        def probe(up):
            def answers(base):
                asked.append(base)
                return base in up
            return answers
        self.assertEqual(ollama_url.pick(environ={}, probe=probe({'http://192.168.7.8:11434'})),
                         (self.S('http://192.168.7.8:11434', 'big:1', 65536), []))
        self.assertEqual(ollama_url.pick(environ={}, probe=probe({'http://192.168.7.9:11434'}))[1], ['192.168.7.8:11434'])
        asked.clear()
        server, skipped = ollama_url.pick(environ={}, probe=probe(set()))
        self.assertEqual((server.model, skipped), ('small:1', ['192.168.7.8:11434', '192.168.7.9:11434']))
        self.assertNotIn('http://127.0.0.1:11434', asked)

    def test_a_single_server_is_never_probed(self):
        never = mock.Mock(side_effect=AssertionError('probed'))
        self.servers('http://192.168.7.8:11434\n')
        self.assertEqual(ollama_url.pick(environ={}, probe=never)[1], [])
        self.assertEqual(ollama_url.pick(environ={'OLLAMA_URL': '10.0.0.9'}, probe=never)[0].base, 'http://10.0.0.9:11434')

    def test_answers_asks_api_tags_briefly(self):
        fake = FakeOllama()
        self.addCleanup(fake.stop)
        self.assertTrue(ollama_url.answers(fake.base))
        self.assertEqual(fake.requests, [('GET', '/api/tags', None)])
        fake.stop()
        self.assertFalse(ollama_url.answers(fake.base))
        self.assertLessEqual(ollama_url.PROBE_S, 15)   # one timer run waits this long at most for an off PC


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
        isolate(self, root)    # nothing from the real environment or the real folder's ollama-*.txt files
        os.environ['OLLAMA_URL'] = self.fake.base
        patcher = mock.patch.object(ir.memguard, 'commit_headroom_gb', return_value=None)   # never this PC's memory
        patcher.start()
        self.addCleanup(patcher.stop)

    def as_other_pc(self):
        """Treat the fake (which is on 127.0.0.1) as a server on another PC, and fail if a local check runs."""
        for name in ('gpu_busy', 'owner_client', 'last_request'):
            patcher = mock.patch.object(ir, name, side_effect=AssertionError(f'{name} is about this PC'))
            patcher.start()
            self.addCleanup(patcher.stop)
        patcher = mock.patch.object(ir.memguard, 'commit_headroom_gb',
                                    side_effect=AssertionError('commit_headroom_gb is about this PC'))
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

    def local_checks(self, gpu=0, client=False, headroom=None):
        for target, name, value in ((ir, 'gpu_busy', gpu), (ir, 'owner_client', client),
                                    (ir.memguard, 'commit_headroom_gb', headroom)):   # None: can't be read
            patcher = mock.patch.object(target, name, return_value=value)
            patcher.start()
            self.addCleanup(patcher.stop)

    def test_this_pc_low_memory_is_a_blocker(self):
        self.local_checks(headroom=5.5)
        self.log_request(3600)
        self.assertEqual(ir.blockers(), ['Windows commit headroom 5.5 GB (needs 8 GB)'])

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

    def test_a_bad_model_or_ctx_is_a_blocker_not_a_crash(self):
        for name, value in (('OLLAMA_CTX', 'lots'), ('OLLAMA_MODEL', 'not a model')):
            with mock.patch.dict(os.environ, {name: value}):
                why = ir.blockers()
                self.assertEqual((len(why), why[0].startswith(f'bad Ollama setting ({name} variable')), (1, True), why)
        self.assertEqual(self.fake.requests, [])

    def test_a_model_the_server_does_not_have_is_a_blocker(self):
        self.local_checks()
        self.log_request(3600)
        self.fake.tags = ['qwen3:8b']
        self.assertEqual(ir.blockers(), ['model gpt-oss:20b is not on the server (ollama pull gpt-oss:20b)'])
        with mock.patch.dict(os.environ, {'OLLAMA_MODEL': 'qwen3:8b'}):
            self.assertEqual(ir.blockers(), [])

    def test_the_settings_do_not_change_what_this_pc_sends(self):
        self.local_checks()
        self.log_request(3600)
        self.fake.tags = ['qwen3:8b']
        with mock.patch.dict(os.environ, {'OLLAMA_MODEL': 'qwen3:8b', 'OLLAMA_CTX': '32768'}):
            self.assertEqual(ir.blockers(), [])
        self.assertEqual(self.fake.requests, [('GET', '/api/tags', None)])

    def test_source_budget_follows_the_context_size(self):
        self.assertEqual(ir.source_cap(65536), ir.SOURCE_CAP)       # unchanged at the old default
        self.assertEqual(ir.source_cap(32768), ir.SOURCE_CAP // 2)
        self.assertEqual(ir.source_cap(2048), 10_000)
        src = self.root / 'src'
        (self.root / 'big.txt').write_text('\n'.join('x' * 70 for _ in range(500)))     # about 40,000 characters numbered
        topic = {'sources': ['h:big.txt', 'h:big.txt:1-100']}
        with mock.patch.object(ir, 'H', self.root):
            copied, skipped = ir.copy_sources(topic, src, ir.source_cap(65536))
            self.assertEqual((len(copied), skipped), (2, []))
            copied, skipped = ir.copy_sources(topic, src, 45_000)
            self.assertEqual((len(copied), len(skipped)), (1, 1))
            self.assertIn('over the 45000-character budget', skipped[0])

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

    def test_a_rerun_keeps_the_last_report_as_report_previous(self):
        (self.root / 't1').mkdir()
        (self.root / 't1' / 'report.md').write_text('the 15 Oct report')
        self.stub_agent('(ws / "report.md").write_text("r" * 400)\n')
        self.assertTrue(ir.run(self.topic()))
        self.assertEqual((self.root / 't1' / 'report.previous.md').read_text(), 'the 15 Oct report')
        self.assertEqual((self.root / 't1' / 'report.md').read_text(), 'r' * 400)

    def test_a_failed_run_on_a_live_server_is_failed(self):
        self.as_other_pc()
        self.stub_agent('sys.exit(1)\n')
        self.assertFalse(ir.run(self.topic()))
        self.assertEqual(ir.load(ir.QUEUE, {})['topics'][0]['status'], 'failed')

    def test_a_run_passes_model_and_ctx_to_the_agent(self):
        self.stub_agent('print("args", " ".join(sys.argv[1:]))\n(ws / "report.md").write_text("r" * 400)\n')
        self.assertTrue(ir.run(self.topic()))
        self.assertIn('--model gpt-oss:20b --ctx 65536', (self.root / 't1' / 'agent-output.txt').read_text())
        with mock.patch.dict(os.environ, {'OLLAMA_MODEL': 'qwen3:8b', 'OLLAMA_CTX': '32768'}):
            self.assertTrue(ir.run(self.topic()))
        self.assertIn('--model qwen3:8b --ctx 32768', (self.root / 't1' / 'agent-output.txt').read_text())

    # ---- the whole check against a server on another PC, model list included ----
    def test_other_pc_through_blockers_asks_ps_and_tags(self):
        self.as_other_pc()
        self.assertIn('first look', ir.blockers(record=True)[0])
        self.assertEqual(sorted(r[1] for r in self.fake.requests), ['/api/ps', '/api/tags'])

    def test_other_pc_without_the_model_says_so(self):
        self.as_other_pc()
        self.fake.tags = ['qwen3:8b']
        why = ir.blockers()
        self.assertEqual(len(why), 2, why)
        self.assertIn('is not on the server', why[1])
        with mock.patch.dict(os.environ, {'OLLAMA_MODEL': 'qwen3:8b'}):
            self.assertEqual(len(ir.blockers()), 1)

    def test_other_pc_that_is_off_says_so_once(self):
        self.as_other_pc()
        self.fake.stop()
        why = ir.blockers(record=True)
        self.assertEqual(len(why), 1, why)
        self.assertIn('is not answering', why[0])

    # ---- several servers, held topics and a topic's own model (17 Oct) ----
    DEAD = 'http://127.0.0.1:9'   # nothing listens there: the friend's PC, switched off

    def servers(self, text):
        os.environ.pop('OLLAMA_URL')
        ollama_url.URL_FILE.write_text(text, encoding='utf-8')

    def main(self, command='status'):
        out = io.StringIO()
        with mock.patch.object(sys, 'argv', ['idle_research.py', command]), contextlib.redirect_stdout(out):
            code = ir.main()
        return code, out.getvalue()

    def open_topics(self, *topics):
        ir.save(ir.QUEUE, {'topics': [dict({'status': 'open', 'title': 'x', 'question': 'y', 'sources': []}, **t)
                                      for t in topics]})

    def test_falls_back_to_this_pc_when_the_other_pc_is_off(self):
        self.servers(f'{self.DEAD} big:1 65536\n{self.fake.base} small:1 16384\n')
        self.fake.tags = ['small:1']
        self.local_checks()
        self.log_request(3600)
        self.open_topics({'id': 't1'})
        self.assertEqual(self.main()[1], '[127.0.0.1:9 not answering, so this PC] 1 open topic(s); idle: would start t1\n')

    def test_a_run_uses_the_server_it_was_decided_on(self):
        self.servers(f'{self.DEAD} big:1 65536\n{self.fake.base} small:1 16384\n')
        self.stub_agent('print("args", " ".join(sys.argv[1:]), "url", os.environ["OLLAMA_URL"])\n'
                        '(ws / "report.md").write_text("r" * 400)\n')
        self.assertTrue(ir.run(self.topic()))
        output = (self.root / 't1' / 'agent-output.txt').read_text()
        self.assertIn('--model small:1 --ctx 16384', output)
        self.assertIn(f'url {self.fake.base}', output)

    def test_local_only_topics_wait_while_the_server_is_another_pc(self):
        self.open_topics({'id': 'names', 'local_only': True}, {'id': 't2'})
        self.as_other_pc()
        with mock.patch.object(ir, 'blockers', return_value=[]):
            self.assertEqual(self.main()[1], f'[remote Ollama {ollama_url.describe(self.fake.base)}] 2 open topic(s), '
                                             '1 held (names: local_only, waits for this PC); idle: would start t2\n')
        self.open_topics({'id': 'names', 'local_only': True})
        with mock.patch.object(ir, 'blockers', return_value=[]):
            self.assertIn('not starting: every open topic is held', self.main()[1])

    def test_local_only_topics_run_on_this_pc(self):
        self.assertIsNone(ir.hold_reason({'local_only': True}, ollama_url.Server('http://127.0.0.1:11434', 'm', 4096), None))

    def test_a_topic_may_name_its_model(self):
        self.local_checks()
        self.log_request(3600)
        self.fake.tags = ['gpt-oss:20b', 'gemma4:12b']
        self.open_topics({'id': 'chat', 'model': 'nothere:1'}, {'id': 'lines', 'model': 'gemma4:12b'})
        self.stub_agent('print("args", " ".join(sys.argv[1:]))\n(ws / "report.md").write_text("r" * 400)\n')
        code, out = self.main('check')
        self.assertEqual(code, 0, out)
        self.assertIn('2 open topic(s), 1 held (chat: needs nothere:1, not on this server); idle: would start lines', out)
        self.assertIn('--model gemma4:12b --ctx 65536', (self.root / 'lines' / 'agent-output.txt').read_text())
        self.assertEqual({t['id']: t['status'] for t in ir.load(ir.QUEUE, {})['topics']}, {'chat': 'open', 'lines': 'review'})

    def test_a_topic_may_name_its_context_size(self):
        self.local_checks()
        self.log_request(3600)
        self.fake.tags = ['gpt-oss:20b', 'hf.co/u/rp-GGUF:IQ4_XS']
        self.open_topics({'id': 'bad', 'ctx': 'lots'}, {'id': 'rp', 'model': 'hf.co/u/rp-GGUF:IQ4_XS', 'ctx': 8192})
        self.stub_agent('print("args", " ".join(sys.argv[1:]))\n(ws / "report.md").write_text("r" * 400)\n')
        code, out = self.main('check')
        self.assertIn('1 held (bad: bad ctx (', out)
        self.assertIn('--model hf.co/u/rp-GGUF:IQ4_XS --ctx 8192', (self.root / 'rp' / 'agent-output.txt').read_text())

    # ---- chaining topics on another PC (owner, 17 Oct) ----
    def statuses(self):
        return {t['id']: t['status'] for t in ir.load(ir.QUEUE, {})['topics']}

    def check_now(self):
        out = io.StringIO()
        with mock.patch.object(sys, 'argv', ['idle_research.py', 'check', '--now']), contextlib.redirect_stdout(out):
            return ir.main(), out.getvalue()

    def test_topics_follow_each_other_on_another_pc(self):
        self.as_other_pc()
        self.open_topics({'id': 'a'}, {'id': 'b'}, {'id': 'c'})
        self.stub_agent('(ws / "report.md").write_text("r" * 400)\n')
        code, out = self.check_now()
        self.assertEqual((code, self.statuses()), (0, {'a': 'review', 'b': 'review', 'c': 'review'}), out)
        self.assertEqual(out.count('idle: would start'), 3)
        self.assertIn("queue finished on the friend's PC: paused", out)   # and then it pauses itself (below)
        self.assertIn('STOP exists', out.splitlines()[-1])

    def test_the_runner_pauses_itself_when_the_friends_queue_finishes(self):
        self.as_other_pc()
        self.fake.tags = ['gpt-oss:20b']
        self.open_topics({'id': 'a'}, {'id': 'rp', 'model': 'nothere:1'})
        self.stub_agent('(ws / "report.md").write_text("r" * 400)\n')
        self.check_now()
        self.assertEqual(self.statuses(), {'a': 'review', 'rp': 'open'})
        stop = (self.root / 'STOP').read_text()
        self.assertIn("the queue finished on the friend's PC", stop)
        self.assertIn('- rp: needs nothere:1, not on this server', stop)
        self.assertIn('queue finished on the friend\'s PC: paused (Agent/local-research/STOP); 1 still waiting: rp',
                      (self.root / 'LOG.md').read_text())
        self.open_topics({'id': 'later'})
        self.assertIn('STOP exists', self.check_now()[1])                      # nothing starts until it is deleted
        self.assertEqual(self.statuses(), {'later': 'open'})

    def test_no_pause_while_something_can_still_run(self):
        self.as_other_pc()
        self.open_topics({'id': 'a'}, {'id': 'b'})
        self.stub_agent('(ws / "report.md").write_text("r" * 400)\n')
        with mock.patch.object(ir, 'SERVICE_S', ir.CHAIN_MIN_S - 1):   # the chain ends after a, with b still open
            self.check_now()
        self.assertFalse((self.root / 'STOP').exists())

    def test_a_check_that_finds_the_friends_queue_already_done_pauses_too(self):
        # the chain that ran the last topic may have been started by older code; the next check still pauses
        self.as_other_pc()
        self.open_topics({'id': 'a', 'status': 'review'})
        self.assertIn('STOP exists', self.main('check')[1])
        self.assertTrue((self.root / 'STOP').exists())
        self.assertFalse((self.root / 'STOP').unlink() or self.main('status')[1].count('paused'))   # status only reads
        self.assertFalse((self.root / 'STOP').exists())

    def test_this_pc_never_pauses_itself(self):
        self.local_checks()
        self.log_request(3600)
        self.open_topics({'id': 'a'})
        self.stub_agent('(ws / "report.md").write_text("r" * 400)\n')
        self.main('check')
        self.assertEqual(self.statuses(), {'a': 'review'})
        self.assertFalse((self.root / 'STOP').exists())

    def test_this_pc_still_runs_one_topic_per_check(self):
        self.local_checks()
        self.log_request(3600)
        self.open_topics({'id': 'a'}, {'id': 'b'})
        self.stub_agent('(ws / "report.md").write_text("r" * 400)\n')
        self.assertEqual(self.main('check')[0], 0)
        self.assertEqual(self.statuses(), {'a': 'review', 'b': 'open'})

    def test_no_chaining_with_too_little_service_time_left(self):
        self.as_other_pc()
        self.open_topics({'id': 'a'}, {'id': 'b'})
        self.stub_agent('(ws / "report.md").write_text("r" * 400)\n')
        with mock.patch.object(ir, 'SERVICE_S', ir.CHAIN_MIN_S - 1):   # under half an hour left after the first
            self.check_now()
        self.assertEqual(self.statuses(), {'a': 'review', 'b': 'open'})

    def test_a_chained_topic_that_runs_out_of_time_goes_back_to_open(self):
        self.as_other_pc()
        self.open_topics({'id': 'a'}, {'id': 'b'})
        self.stub_agent('import time\ntime.sleep(10)\n')
        with mock.patch.object(ir, 'SERVICE_S', 2), mock.patch.object(ir, 'CHAIN_MIN_S', 0):
            self.check_now()
        self.assertEqual(self.statuses(), {'a': 'open', 'b': 'open'})
        self.assertIn('reached its time limit, topic left open', (self.root / 'LOG.md').read_text())

    def test_chaining_stops_after_three_failures_in_a_row(self):
        self.as_other_pc()
        self.open_topics(*({'id': f't{n}'} for n in range(5)))
        self.stub_agent('sys.exit(1)\n')
        code, out = self.check_now()
        self.assertEqual(code, 1)
        self.assertEqual(list(self.statuses().values()), ['failed', 'failed', 'failed', 'open', 'open'])

    def test_a_chunk_job_gets_the_servers_model_and_at_most_16k(self):
        self.servers(f'{self.fake.base} big:1 65536\n')
        stub = self.root / 'stub_step.py'
        stub.write_text('import os, sys\nprint("args", " ".join(sys.argv[1:]), "url", os.environ.get("OLLAMA_URL"))\n')
        topic = {'id': 'm1', 'status': 'running', 'kind': 'map', 'job': 'bot-gaps'}
        ir.save(ir.QUEUE, {'topics': [topic]})
        with mock.patch.object(ir, 'JOBS', stub), mock.patch.object(ir, 'MAP', stub):
            self.assertTrue(ir.run(topic))
        output = (self.root / 'm1' / 'map-output.txt').read_text()
        self.assertIn('--model big:1 --ctx 16384', output)
        self.assertIn(f'url {self.fake.base}', output)


class LocalAgentTests(unittest.TestCase):
    def setUp(self):
        self.fake = FakeOllama()
        self.addCleanup(self.fake.stop)
        self.dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.dir.cleanup)
        isolate(self, self.dir.name)
        headroom = mock.patch.object(local_agent.memguard, 'commit_headroom_gb', return_value=None)  # not this PC's
        headroom.start()
        self.addCleanup(headroom.stop)

    def run_main(self, *argv, env=None):
        out = io.StringIO()
        with mock.patch.object(sys, 'argv', ['local_agent.py', '--workspace', self.dir.name, '--task', 'hi', *argv]), \
                mock.patch.dict(os.environ, env or {}), contextlib.redirect_stdout(out):
            return local_agent.main(), out.getvalue()

    def sent(self):
        return self.fake.requests[0][2]

    def test_model_and_ctx_default_to_what_they_were(self):
        self.run_main(env={'OLLAMA_URL': self.fake.base})
        self.assertEqual((self.sent()['model'], self.sent()['options']['num_ctx']), ('gpt-oss:20b', 65536))

    def test_model_and_ctx_from_variables_and_flags(self):
        self.run_main(env={'OLLAMA_URL': self.fake.base, 'OLLAMA_MODEL': 'qwen3:8b', 'OLLAMA_CTX': '32768'})
        self.assertEqual((self.sent()['model'], self.sent()['options']['num_ctx']), ('qwen3:8b', 32768))
        self.fake.requests.clear()
        self.run_main('--model', 'tiny:1b', '--ctx', '4096',
                      env={'OLLAMA_URL': self.fake.base, 'OLLAMA_MODEL': 'qwen3:8b', 'OLLAMA_CTX': '32768'})
        self.assertEqual((self.sent()['model'], self.sent()['options']['num_ctx']), ('tiny:1b', 4096))

    def test_a_bad_model_or_ctx_stops_before_any_request(self):
        for argv, env in ((('--ctx', '100'), {}), (('--model', 'a b'), {}), ((), {'OLLAMA_CTX': 'lots'}),
                          ((), {'OLLAMA_MODEL': '-x'})):
            with contextlib.redirect_stderr(io.StringIO()) as err, self.assertRaises(SystemExit):
                self.run_main(*argv, env={'OLLAMA_URL': self.fake.base, **env})
            self.assertIn('bad Ollama setting', err.getvalue())
        self.assertEqual(self.fake.requests, [])

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
        # one chat, then (Ollama on this PC) the unload that empties the prompt cache (memguard.py)
        self.assertEqual((code, len(self.fake.requests)), (0, 2))
        self.assertEqual((self.fake.requests[1][2]['keep_alive'], self.fake.requests[1][2]['messages']), (0, []))

    def test_low_memory_stops_before_a_chat(self):
        with mock.patch.object(local_agent.memguard, 'commit_headroom_gb', return_value=2.0), \
                mock.patch.object(local_agent.time, 'sleep'):
            code, out = self.run_main(env={'OLLAMA_URL': self.fake.base})
        self.assertEqual(code, 3)
        self.assertIn('commit headroom 2.0 GB', out)
        self.assertTrue(all(r[2]['messages'] == [] for r in self.fake.requests))   # unloads only, no chat

    def test_a_bad_address_stops_before_any_request(self):
        with contextlib.redirect_stderr(io.StringIO()) as err, self.assertRaises(SystemExit):
            self.run_main('--ollama-url', 'ftp://host')
        self.assertIn('bad Ollama address', err.getvalue())
        self.assertEqual(self.fake.requests, [])

    def test_without_a_flag_it_uses_the_first_server_that_answers(self):
        ollama_url.URL_FILE.write_text(f'http://127.0.0.1:9 big:1\n{self.fake.base} small:1 4096\n')
        code, out = self.run_main()
        self.assertEqual(code, 0)
        self.assertIn('127.0.0.1:9 not answering', out)
        self.assertEqual((self.sent()['model'], self.sent()['options']['num_ctx']), ('small:1', 4096))

    def test_another_pc_is_unloaded_every_five_steps_and_at_the_end(self):
        # 17 Oct: its prompt cache grows in that PC's RAM; its memory can't be read from here, so no headroom check
        self.fake.chat_reply = {'message': {'role': 'assistant', 'content': '',
                                            'tool_calls': [{'function': {'name': 'list_dir', 'arguments': {'path': '.'}}}]}}
        with mock.patch.object(local_agent.ollama_url, 'is_local', return_value=False), \
                mock.patch.object(local_agent.memguard, 'commit_headroom_gb', side_effect=AssertionError('this PC')):
            code, out = self.run_main('--max-steps', '11', env={'OLLAMA_URL': self.fake.base})
        unloads = [r for r in self.fake.requests if r[2]['messages'] == []]
        self.assertEqual((code, len(unloads)), (1, 3))   # before steps 6 and 11, and once at the end


if __name__ == '__main__':
    unittest.main()
