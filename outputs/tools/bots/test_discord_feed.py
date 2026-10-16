"""C46 offline checks. Run with the owner's Windows Python; never starts a service.

  C:/Users/Pengw/miniconda3/python.exe -m unittest discover -s outputs/tools/bots -p test_discord_feed.py -v
"""
from datetime import datetime
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

from PIL import Image

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))
import discord_feed as f
import live_map as m
from public_map_data import public_filter, public_link
from watchdog_probe import probe


def fixture():
    return json.loads((HERE / 'testdata/discord-map.json').read_text(encoding='utf-8'))


class PrivacyAndRendering(unittest.TestCase):
    def test_default_preview_never_reads_webhook_or_sends(self):
        with tempfile.TemporaryDirectory() as temp, \
             patch.object(f, 'HOME', Path(temp)), \
             patch.object(f, 'read_data', return_value=fixture()), \
             patch.object(f, 'watchdog_probe', return_value=None), \
             patch.object(f, 'digest_payload', return_value=None), \
             patch.object(f, 'read_webhook', side_effect=AssertionError()), \
             patch.object(f, 'private_file', side_effect=AssertionError()), \
             patch.object(f, 'discord_request', side_effect=AssertionError()):
            self.assertEqual(f.main(['--once']), 0)
            self.assertTrue((Path(temp) / 'preview-state.json').exists())
            self.assertFalse((Path(temp) / 'state.json').exists())
            self.assertTrue(list((Path(temp) / 'preview').glob('*.png')))

    def test_filter_removes_all_source_names_and_private_fields(self):
        result = public_filter(fixture())
        text = json.dumps(result)
        for private in ('PRIVATE', '192.0.2.1', '/private', 'account', 'activity', 'issues', 'target'):
            self.assertNotIn(private, text)
        self.assertEqual(set(result), {'bots', 'stats', 'roles', 'cities'})
        self.assertEqual(len(result['bots']), 3)
        self.assertEqual(result['bots'][0]['label'], 'Bot 1')

    def test_unknown_free_text_and_nonfinite_coordinates(self):
        d = fixture()
        d['pop'][0][2] = 'PRIVATE ROLE'
        d['pop'][0][6] = 'PRIVATE STATE'
        d['pop'][0][4] = float('nan')
        d['pop'][1][3] = 'PRIVATE PLANET'
        result = public_filter(d)
        self.assertEqual(len(result['bots']), 2)
        self.assertEqual(result['bots'][0]['role'], 'other')
        self.assertIsNone(result['bots'][0]['x'])
        json.dumps(result, allow_nan=False)

    def test_payload_shape_and_validated_link(self):
        result = f.card_payload(public_filter(fixture()), 'https://some-demo.trycloudflare.com')
        self.assertEqual(result['allowed_mentions']['parse'], [])
        self.assertEqual(result['attachments'], [{'id': 0, 'filename': 'bot-map.png'}])
        self.assertEqual(result['embeds'][0]['image']['url'], 'attachment://bot-map.png')
        self.assertEqual(result['embeds'][0]['url'], 'https://some-demo.trycloudflare.com')
        self.assertEqual(len(result['embeds'][0]['fields']), 9)
        self.assertNotIn('PRIVATE', json.dumps(result))
        for link in ('http://some-demo.trycloudflare.com', 'https://discord.com',
                     'https://x.trycloudflare.com/PRIVATE', 'https://x.trycloudflare.com?token=secret',
                     'https://x.trycloudflare.com.evil.test', 'https://a@x.trycloudflare.com'):
            self.assertEqual(public_link(link), '')
            self.assertNotIn('url', f.card_payload(public_filter(fixture()), link)['embeds'][0])

    def test_saved_json_renders_png_panels_and_previews(self):
        data = public_filter(fixture())
        png = f.render_map(data)
        im = Image.open(io.BytesIO(png))
        self.assertEqual(im.size, (1000, 648))
        self.assertEqual(im.format, 'PNG')
        self.assertGreater(len(im.getcolors(im.width * im.height)), 10)
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp)
            f.preview(path, f.card_payload(data), png, [f.text_payload('Galaxy is down')], datetime(2026, 10, 16, 6))
            self.assertEqual(len(list(path.glob('*.json'))), 2)
            self.assertEqual(len(list(path.glob('*.png'))), 1)

    def test_private_routes_rejected_without_opening_a_socket(self):
        for route in ('/server.json', '/feed.json', '/bot.json?name=PRIVATE', '/floor', '/navmaps.json',
                      '/navmap/test.json', '/mapimg/tatooine.png', '/data.json?anything=1', '/data.json.extra'):
            handler = object.__new__(m.PublicHandler)
            handler.path = route
            handler.send_error = lambda status: self.assertEqual(status, 404)
            with patch.object(m, 'public_snapshot', side_effect=AssertionError('must not read data')):
                handler.do_GET()

    def test_public_snapshot_does_not_call_private_snapshot(self):
        with patch.object(m, 'pop_rows', return_value=fixture()['pop']), \
             patch.object(m, 'feed_status', return_value=fixture()['feed']), \
             patch.object(m, 'snapshot', side_effect=AssertionError()), \
             patch.object(m, 'present', side_effect=AssertionError()), \
             patch.dict(m.pop, {'server': fixture()['pop_server'], 'ended': False}):
            self.assertEqual(len(m.public_snapshot()['bots']), 3)

    def test_public_start_skips_roster_and_logger(self):
        with patch.object(sys, 'argv', ['live_map.py', '--public']), \
             patch.object(m, 'load_roster', side_effect=AssertionError()), \
             patch.object(m, 'seed_history', side_effect=AssertionError()), \
             patch.object(m.threading, 'Thread', side_effect=AssertionError()), \
             patch.object(m, 'ThreadingHTTPServer') as server:
            m.main()
            server.assert_called_once_with(('127.0.0.1', 8766), m.PublicHandler)


class EventsAndDigest(unittest.TestCase):
    def test_freshness_and_explicit_stop(self):
        with patch.object(m.time, 'time', return_value=1000), \
             patch.object(m, 'WHO') as who, \
             patch.dict(m.pop, {'server': {'t': 990000, 'online': 1700}, 'ended': False}):
            who.stat.side_effect = OSError()
            self.assertTrue(m.feed_status()['server_up'])
            self.assertTrue(m.feed_status()['run_active'])
            m.pop['server']['t'] = 700000
            self.assertFalse(m.feed_status()['server_up'])
            self.assertFalse(m.feed_status()['run_active'])
            m.pop['server']['t'] = 990000
            m.pop['ended'] = True
            self.assertFalse(m.feed_status()['run_active'])

    def test_pop_counter_reset_missions_and_stop(self):
        events = [{'e': 'spawn', 't': 1000, 'bot': 1, 'name': 'PRIVATE'},
                  {'e': 'mission_done', 't': 2000, 'bot': 1},
                  {'e': 'stop', 't': 3000}]
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'events.jsonl'
            path.write_text(''.join(json.dumps(e)+'\n' for e in events))
            with patch.object(m, 'POP_LOG', path), patch.dict(m.pop, {'inode': None, 'offset': 0,
                    'bots': {}, 'server': {}, 'pos_mtime': 0, 'missions_done': 0, 'run_id': None, 'ended': False}):
                m.pop_read()
                self.assertEqual(m.pop['missions_done'], 1)
                self.assertTrue(m.pop['ended'])
                self.assertEqual(m.pop['bots'], {})
                with path.open('a') as out:
                    out.write(json.dumps({'e': 'spawn', 't': 4000, 'bot': 2})+'\n')
                m.pop_read()
                self.assertEqual(m.pop['run_id'], 4000)
                self.assertEqual(m.pop['missions_done'], 0)
                self.assertFalse(m.pop['ended'])

    def test_transitions_not_duplicate_or_transport_failure(self):
        d, state = public_filter(fixture()), f.empty_state()
        now = datetime(2026, 10, 16, 6)
        self.assertEqual(f.events_for(d, state, now), [])
        self.assertEqual(f.events_for(public_filter({}), state, now), [])
        d['stats'].update(server_up=False, run_active=False)
        self.assertEqual(len(f.events_for(d, state, now)), 2)
        self.assertEqual(f.events_for(d, state, now), [])
        d['stats'].update(server_up=True, run_active=True, run_id=200000)
        self.assertEqual(len(f.events_for(d, state, now)), 2)
        d['stats']['run_id'] = 300000
        self.assertEqual(len(f.events_for(d, state, now)), 2)

    def test_watchdog_cursor_baseline_increment_partial_rotation(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'watchdog.log'
            path.write_text('old botpop despawn PRIVATE\n', encoding='utf-8')
            first = probe(path)
            self.assertEqual(first['hits'], 0)
            with path.open('a') as out:
                out.write('new botpop despawn PRIVATE\npartial botpop des')
            second = probe(path, first['offset'], first['file_id'])
            self.assertEqual(second['hits'], 1)
            with path.open('a') as out:
                out.write('pawn PRIVATE\n')
            third = probe(path, second['offset'], second['file_id'])
            self.assertEqual(third['hits'], 1)
            self.assertNotIn('PRIVATE', json.dumps(third))
            self.assertEqual(probe(path, third['offset'], third['file_id'])['hits'], 0)
            path.write_text('botpop despawn\n')
            self.assertEqual(probe(path, third['offset'], third['file_id'])['hits'], 1)

    def test_watchdog_appears_after_feed_started(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'watchdog.log'
            first = probe(path)
            path.write_text('botpop despawn PRIVATE\n')
            self.assertEqual(probe(path, first['offset'], first['file_id'])['hits'], 1)

    def test_0700_once_and_numeric_digest_only(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            (folder / 'numbers-demo.md').write_text(
                '# PRIVATE NAME\n| run | minutes | bots | boxes | missions done | kills | deaths |\n'
                '|---|---|---|---|---|---|---|\n| run8 | 30.5 | 1700 | 80 | 10 | 200 | 3 |\n'
                '## PRIVATE NAME\n/private/source secret\n', encoding='utf-8')
            digest = f.digest_payload(folder)
            self.assertNotIn('PRIVATE', json.dumps(digest))
            self.assertIn('run8', digest['content'])
            state, data = f.empty_state(), public_filter(fixture())
            self.assertEqual(f.events_for(data, state, datetime(2026, 10, 16, 6, 59), digest=digest), [])
            self.assertEqual(len(f.events_for(data, state, datetime(2026, 10, 16, 7), digest=digest)), 1)
            self.assertEqual(f.events_for(data, state, datetime(2026, 10, 16, 7, 1), digest=digest), [])


class Delivery(unittest.TestCase):
    def test_post_then_patch_same_id_and_replace_attachment(self):
        with tempfile.TemporaryDirectory() as temp:
            state, path = f.empty_state(), Path(temp) / 'state.json'
            calls = []
            def request(endpoint, method, payload, png):
                calls.append((endpoint, method, payload, png))
                return 200, {}, b'{"id":"12345"}'
            body = f.card_payload(public_filter(fixture()))
            self.assertTrue(f.deliver(state, path, 'https://example.invalid?wait=true', body, b'PNG', True, request, lambda: 100))
            self.assertTrue(f.deliver(state, path, 'https://example.invalid?wait=true', body, b'NEW', True, request, lambda: 160))
            self.assertEqual(calls[0][1], 'POST')
            self.assertEqual(calls[1][1], 'PATCH')
            self.assertEqual(calls[1][0], 'https://example.invalid/messages/12345')
            self.assertEqual(state['message_id'], '12345')
            self.assertEqual(calls[1][2]['attachments'], [{'id': 0, 'filename': 'bot-map.png'}])

    def test_rate_limit_preserves_event_and_waits_retry_after(self):
        with tempfile.TemporaryDirectory() as temp:
            state, path = f.empty_state(), Path(temp) / 'state.json'
            state['queue'] = [f.text_payload('Galaxy is down')]
            request = lambda *a: (429, {'Retry-After': '125'}, b'{"retry_after":130}')
            self.assertFalse(f.deliver(state, path, 'unused', state['queue'][0], request=request, clock=lambda: 10))
            self.assertEqual(state['next_at'], 140)
            self.assertEqual(len(state['queue']), 1)
            self.assertFalse(f.deliver(state, path, 'unused', state['queue'][0], request=lambda *a: self.fail(), clock=lambda: 139))

    def test_uncertain_post_blocks_restart_retry(self):
        with tempfile.TemporaryDirectory() as temp:
            state, path = f.empty_state(), Path(temp) / 'state.json'
            def request(*a):
                raise f.SafeError('Unknown delivery')
            with self.assertRaises(f.SafeError):
                f.deliver(state, path, 'unused', {}, live=True, request=request, clock=lambda: 100)
            self.assertIsNotNone(f.load_state(path)['inflight'])
            with self.assertRaises(f.SafeError):
                f.deliver(state, path, 'unused', {}, request=lambda *a: self.fail(), clock=lambda: 200)

    def test_failed_patch_retries_next_minute_and_404_stops(self):
        with tempfile.TemporaryDirectory() as temp:
            state, path = f.empty_state(), Path(temp) / 'state.json'
            state['message_id'] = '12345'
            def blip(*a):
                raise f.SafeError('Discord result unknown')
            self.assertFalse(f.deliver(state, path, 'https://example.invalid?wait=true', {}, b'P', True, blip, lambda: 100))
            self.assertIsNone(f.load_state(path)['inflight'])
            self.assertEqual(state['next_at'], 100 + f.INTERVAL)
            outage = lambda *a: (503, {}, b'')
            self.assertFalse(f.deliver(state, path, 'https://example.invalid?wait=true', {}, b'P', True, outage, lambda: 200))
            gone = lambda *a: (404, {}, b'')
            with self.assertRaises(f.SafeError):
                f.deliver(state, path, 'https://example.invalid?wait=true', {}, b'P', True, gone, lambda: 300)

    def test_success_spacing_waits_only_for_an_empty_bucket(self):
        self.assertEqual(f.bucket_wait({'X-RateLimit-Remaining': '4', 'X-RateLimit-Reset-After': '2.5'}), 1)
        self.assertEqual(f.bucket_wait({'X-RateLimit-Remaining': '0', 'X-RateLimit-Reset-After': '2.5'}), 2.5)
        self.assertEqual(f.bucket_wait({}), 1)

    def test_preview_overwrites_latest_card_and_map(self):
        data = public_filter(fixture())
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp)
            for minute in range(3):
                f.preview(path, f.card_payload(data), b'PNG', [], datetime(2026, 10, 16, 6, minute))
            self.assertEqual(sorted(p.name for p in path.iterdir()), ['latest-card.json', 'latest-map.png'])

    def test_multipart_payload_json_and_file(self):
        body, kind = f.multipart(f.card_payload(public_filter(fixture())), b'PNGDATA')
        self.assertIn(b'name="payload_json"', body)
        self.assertIn(b'name="files[0]"', body)
        self.assertIn(b'PNGDATA', body)
        self.assertIn('boundary=swg', kind)


if __name__ == '__main__':
    unittest.main()
