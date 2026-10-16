"""C46 staging: anonymous bot-map card, transition alerts and 07:00 local digest.

Windows, from the project root (after Claude reviews and the owner enables posting):
  C:/Users/Pengw/miniconda3/python.exe outputs/tools/bots/discord_feed.py --once
  C:/Users/Pengw/miniconda3/python.exe outputs/tools/bots/discord_feed.py --send
Default previews under outputs/Agent/discord-feed/preview; --once previews one cycle.
Stop the foreground loop with Ctrl+C. No service is installed. --send is the explicit
enable switch, never implied by a webhook existing. The owner manually pins the FIRST
card in Discord once; webhook credentials can edit that card but cannot pin it.

Webhook: C:/Users/Pengw/.swg-private/discord-webhook.txt (never read in dry runs).
State/message ID: Agent/discord-feed/state.json; preview state is separate. Never
delete live state to retry an uncertain POST: reconcile inflight first. No raw logs,
report prose, account names or bot names are sent. Link must be a bare quick-tunnel
HTTPS URL. Source failure is UNKNOWN, not a server-down or run-ended transition.
Delivery/tunnel/public serving remain untested until Claude's reviewed start.
"""
import argparse
from datetime import datetime
import io
import json
from pathlib import Path
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
import uuid

from PIL import Image, ImageDraw, ImageFont

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))
from agents.discord_post import (SafeError, NoRedirect, private_file, read_webhook,
                                 sanitize, save_state, send_lock, retry_seconds)
from bots.public_map_data import public_filter, public_link, ROLES, number

OUTPUTS = TOOLS.parent
HOME = OUTPUTS / 'Agent/discord-feed'
SOURCE = 'http://localhost:8765/data.json'
WEBHOOK = Path('C:/Users/Pengw/.swg-private/discord-webhook.txt')
INTERVAL = 60


def read_data():
    # Fixed loopback origin, no proxy or redirect to an arbitrary/private endpoint.
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())
    with opener.open(SOURCE, timeout=10) as response:
        return json.loads(response.read(16 << 20))


def render_map(data):
    """One original-grid panel per populated planet; no downloaded/client bitmap."""
    planets = sorted({b['planet'] for b in data['bots']})
    cols = min(3, max(1, len(planets)))
    rows = max(1, (len(planets) + cols - 1) // cols)
    panel, head, foot = 500, 64, 84
    image = Image.new('RGB', (cols * panel, head + rows * panel + foot), '#0d1117')
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default(size=15)
    title = ImageFont.load_default(size=22)
    draw.text((20, 15), 'Galaxy bot map', font=title, fill='#e6e8eb')
    for i, planet in enumerate(planets):
        left, top = (i % cols) * panel, head + (i // cols) * panel
        bots = [b for b in data['bots'] if b['planet'] == planet]
        draw.text((left + 20, top + 8), f'{planet.title()} | {len(bots):,} bots', font=title, fill='#e6e8eb')
        x0, y0, size = left + 28, top + 50, panel - 56
        def xy(x, y):
            return x0 + (x + 8192) / 16384 * size, y0 + (8192 - y) / 16384 * size
        draw.rectangle((x0, y0, x0 + size, y0 + size), fill='#151b23', outline='#394555')
        for n in range(-8192, 8193, 2048):
            x, y = xy(n, n)
            draw.line((x, y0, x, y0 + size), fill='#303c49')
            draw.line((x0, y, x0 + size, y), fill='#303c49')
        for b in bots:
            if b['x'] is None or b['y'] is None:
                continue
            x, y = xy(b['x'], b['y'])
            if x0 <= x <= x0 + size and y0 <= y <= y0 + size:
                draw.ellipse((x-2, y-2, x+2, y+2), fill=ROLES[b['role']][1])
        for city, (cx, cy) in data['cities'].get(planet, {}).items():
            x, y = xy(cx, cy)
            # Draw labels last, on a solid backing; clamped inside each panel.
            width = draw.textlength(city, font=font)
            x = min(max(x + 5, x0 + 2), x0 + size - width - 4)
            y = min(max(y - 16, y0 + 2), y0 + size - 19)
            draw.rectangle((x-2, y-1, x+width+2, y+17), fill='#151b23')
            draw.text((x, y), city, font=font, fill='#c1cad4')
    if not planets:
        draw.text((24, head + 40), 'No server bots in the latest snapshot', font=title, fill='#adb7c4')
    for i, (_, (name, color)) in enumerate(ROLES.items()):
        x, y = 20 + (i % 4) * (image.width - 40) / 4, image.height - foot + 10 + (i // 4) * 30
        draw.ellipse((x, y+4, x+8, y+12), fill=color)
        draw.text((x+14, y), name, font=font, fill='#e6e8eb')
    result = io.BytesIO()
    image.save(result, format='PNG')
    return result.getvalue()


def display(value, suffix=''):
    value = number(value)
    return 'Unknown' if value is None else f'{value:,}{suffix}'


def card_payload(data, link=''):
    s = data['stats']
    up = s['server_up']
    status = 'Up' if up is True else 'Down' if up is False else 'Unknown'
    fields = [('Galaxy', status), ('Bots online', display(s['online'])),
              ('Kills', display(s['kills'])), ('Deaths', display(s['deaths'])),
              ('Missions done', display(s['missions_done'])), ('Boxes', display(s['boxes'])),
              ('Tick average', display(s['tick_ms_avg'], ' ms')),
              ('Tick maximum', display(s['tick_ms_max'], ' ms')),
              ('Memory RSS', display(s['rss_mb'], ' MB'))]
    embed = {'title': sanitize('Galaxy bot status'), 'color': 0x3FB950 if up else 0xD29922,
             'fields': [{'name': sanitize(k), 'value': sanitize(v), 'inline': True} for k, v in fields],
             'image': {'url': 'attachment://bot-map.png'},
             'footer': {'text': sanitize('Updates every minute | freshness-based status')}}
    link = public_link(link)
    # sanitize deliberately removes all URLs; the only exception is this separately
    # validated structured embed URL, never a relaxation of sanitize's protections.
    if link:
        embed['url'] = link
        embed['title'] = sanitize('Open the live galaxy bot map')
    else:
        embed['description'] = sanitize('Public link not available')
    return {'allowed_mentions': {'parse': [], 'users': [], 'roles': [], 'replied_user': False},
            'embeds': [embed], 'attachments': [{'id': 0, 'filename': 'bot-map.png'}]}


def text_payload(text):
    return {'content': sanitize(text)[:1800],
            'allowed_mentions': {'parse': [], 'users': [], 'roles': [], 'replied_user': False}}


def digest_payload(folder):
    """Newest numeric report table only. No prose, names, headings or filenames leave."""
    files = list(folder.glob('numbers-*.md'))
    if not files:
        return None
    file = max(files, key=lambda p: (p.stat().st_mtime_ns, p.name))
    text = file.read_text(encoding='utf-8-sig')
    headers, found = None, None
    wanted = {'minutes', 'bots', 'boxes', 'missions done', 'kills', 'deaths'}
    for line in text.splitlines():
        cells = [s.strip() for s in line.strip().strip('|').split('|')]
        if cells and cells[0] == 'run' and wanted.issubset(cells):
            headers = cells
        elif headers and len(cells) == len(headers) and re.fullmatch(r'run\d+[a-z]?', cells[0]):
            values = {k: cells[headers.index(k)] for k in wanted}
            if all(re.fullmatch(r'\d+(?:\.\d+)?', v) for v in values.values()):
                found = (cells[0], values)
        elif line.startswith('## ') and headers:
            break
    if not found:
        return None
    run, values = found
    return text_payload('Morning launch simulation digest\nLatest recorded report: ' + run + '\n' +
                        '\n'.join(k.title() + ': ' + values[k] for k in sorted(wanted)) +
                        '\nRecorded results; the report may predate today.')


def watchdog_probe(cursor=None):
    """Read only, through a WSL script file; never echo watchdog log lines."""
    script = TOOLS / 'bots/watchdog_probe.py'
    wsl_path = '/mnt/' + script.drive[0].lower() + str(script)[2:].replace('\\', '/')
    args = ['wsl', '-d', 'Debian', '-u', 'swgemu', '--', 'python3', wsl_path]
    if cursor:
        args += ['--offset', str(cursor['offset']), '--file-id', cursor['file_id']]
    try:
        result = subprocess.run(args, capture_output=True, timeout=10, check=True)
        data = json.loads(result.stdout)
        if (type(data['hits']) is not int or type(data['offset']) is not int
                or not re.fullmatch(r'\d+:\d+', data['file_id'])):
            return None
        return data
    except (OSError, ValueError, KeyError, subprocess.SubprocessError):
        return None


def events_for(data, state, now, watchdog=None, digest=None):
    """Queue transitions once; preserve last known state when telemetry is unknown."""
    events = []
    observed = state.setdefault('observed', {})
    stats = data['stats']
    for key, on, off in [('server_up', 'Galaxy is back', 'Galaxy is down'),
                         ('run_active', 'Launch simulation started', 'Launch simulation ended')]:
        value = stats[key]
        if type(value) is bool:
            if key in observed and observed[key] != value:
                events.append(text_payload(on if value else off))
            observed[key] = value
    run = stats['run_id']
    if run is not None:
        if observed.get('run_id') is not None and observed['run_id'] != run and stats['run_active'] is True:
            # A new run can start and end between minute polls.
            if not any('started' in e['content'] for e in events):
                events += [text_payload('Launch simulation ended'), text_payload('Launch simulation started')]
        observed['run_id'] = run
    if watchdog:
        if state.get('watchdog') and watchdog['hits'] > 0:
            events.append(text_payload('Memory watchdog: bot population despawned'))
        state['watchdog'] = {k: watchdog[k] for k in ('file_id', 'offset')}
    day = now.date().isoformat()
    if now.hour >= 7 and digest and state.get('digest_day') != day:
        events.append(digest)
        state['digest_day'] = day
    return events


def multipart(payload, png=None):
    if png is None:
        return json.dumps(payload).encode(), 'application/json'
    boundary = 'swg' + uuid.uuid4().hex
    body = (f'--{boundary}\r\nContent-Disposition: form-data; name="payload_json"\r\n'
            'Content-Type: application/json\r\n\r\n').encode() + json.dumps(payload).encode()
    body += (f'\r\n--{boundary}\r\nContent-Disposition: form-data; name="files[0]"; '
             'filename="bot-map.png"\r\nContent-Type: image/png\r\n\r\n').encode()
    body += png + f'\r\n--{boundary}--\r\n'.encode()
    return body, 'multipart/form-data; boundary=' + boundary


def discord_request(endpoint, method, payload, png):
    body, kind = multipart(payload, png)
    req = urllib.request.Request(endpoint, body, {'Content-Type': kind, 'User-Agent': 'SWG-map-feed/1.0'}, method=method)
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())
    try:
        with opener.open(req, timeout=20) as response:
            return response.status, dict(response.headers.items()), response.read(1 << 20)
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers.items()), e.read(8192)
    except Exception:
        raise SafeError('Discord result unknown; reconcile inflight state before retrying.') from None


def deliver(state, path, endpoint, payload, png=None, live=False, request=discord_request, clock=time.time):
    """Persist intent; rate-limit rejections retry later, uncertain POSTs never blindly retry."""
    if state.get('inflight'):
        raise SafeError('Unconfirmed previous request; reconcile inflight state before retrying.')
    if clock() < state.get('next_at', 0):
        return False
    message = state.get('message_id') if live else None
    if message is not None and (not isinstance(message, str) or not re.fullmatch(r'\d+', message)):
        raise SafeError('Invalid message ID; refused.')
    method = 'PATCH' if message else 'POST'
    target = endpoint.split('?', 1)[0] + '/messages/' + message if message else endpoint
    state['inflight'] = {'method': method, 'live': live}
    save_state(path, state)
    try:
        code, headers, response = request(target, method, payload, png)
    except SafeError:
        if method != 'PATCH':
            raise
        code, headers, response = None, {}, b''
    if code == 429:
        state.update(inflight=None, next_at=clock() + retry_seconds(headers, response))
        save_state(path, state)
        return False
    if method == 'PATCH' and (code is None or code >= 500):
        # Editing the one card is idempotent: a network blip or a Discord outage retries next minute
        # instead of stopping the feed (Claude's C46 review). A 404 (card deleted) still stops it.
        state.update(inflight=None, next_at=clock() + INTERVAL)
        save_state(path, state)
        return False
    if not 200 <= code < 300:
        if 400 <= code < 500:
            state['inflight'] = None
        save_state(path, state)
        raise SafeError('Discord rejected or could not confirm the request; inspect state before retrying.')
    if live and not message:
        try:
            ident = json.loads(response)['id']
            if not isinstance(ident, str) or not re.fullmatch(r'\d+', ident):
                raise ValueError()
            state['message_id'] = ident
        except (ValueError, KeyError, TypeError):
            raise SafeError('Posted card has no confirmed message ID; reconcile inflight state.') from None
    if not live:
        state['queue'].pop(0)
    else:
        state['last_live'] = clock()
    state['inflight'] = None
    state['next_at'] = clock() + bucket_wait(headers)
    save_state(path, state)
    return True


def bucket_wait(headers):
    """After a success, wait for the bucket reset only when it is empty, else one second. (retry_seconds floors at
    60 s for a 429, which turned every success into a 60-s pause: an upload over 1 s skipped a minute's update.)"""
    h = {k.lower(): v for k, v in headers.items()}
    if h.get('x-ratelimit-remaining') != '0':
        return 1
    try:
        wait = float(h.get('x-ratelimit-reset-after', 1))
    except (TypeError, ValueError):
        return INTERVAL
    return min(INTERVAL, max(1, wait)) if wait == wait else INTERVAL


def empty_state():
    return {'version': 1, 'message_id': None, 'observed': {}, 'queue': [], 'inflight': None,
            'next_at': 0, 'last_live': 0}


def load_state(path):
    if not path.exists():
        return empty_state()
    state = json.loads(path.read_text(encoding='utf-8'))
    if (state.get('version') != 1 or not isinstance(state.get('queue'), list)
            or not isinstance(state.get('observed'), dict)
            or any(number(state.get(k)) is None or state[k] < 0 for k in ('next_at', 'last_live'))
            or state.get('message_id') is not None and (not isinstance(state['message_id'], str)
                or not re.fullmatch(r'\d+', state['message_id']))):
        raise SafeError('Invalid feed state; refused.')
    return state


def preview(folder, payload, png, events, now):
    """The latest card and map are overwritten (a file per minute filled the disk); alerts are rare and kept."""
    folder.mkdir(parents=True, exist_ok=True)
    stem = now.strftime('%Y%m%d-%H%M%S')
    (folder / 'latest-card.json').write_text(json.dumps(payload, indent=2), encoding='utf-8')
    (folder / 'latest-map.png').write_bytes(png)
    for i, event in enumerate(events):
        (folder / (stem + f'-event-{i}.json')).write_text(json.dumps(event, indent=2), encoding='utf-8')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--send', action='store_true')
    mode.add_argument('--dry-run', action='store_true', help='Default: previews only')
    parser.add_argument('--once', action='store_true')
    args = parser.parse_args(argv)
    HOME.mkdir(parents=True, exist_ok=True)
    state_path = HOME / ('state.json' if args.send else 'preview-state.json')
    try:
        # The lock is held for the entire run, not just one network call.
        with send_lock(state_path):
            state = load_state(state_path)
            endpoint = read_webhook(private_file(WEBHOOK)) if args.send else None
            if state.get('inflight'):
                raise SafeError('Unconfirmed previous request; reconcile state before restarting.')
            while True:
                start = time.monotonic()
                now = datetime.now().astimezone()
                try:
                    data = public_filter(read_data())
                except Exception:
                    data = public_filter({})  # No false galaxy/run transitions on a failed map fetch.
                try:
                    link = public_link((HOME / 'public-url.txt').read_text(encoding='utf-8'))
                except OSError:
                    link = ''
                digest = digest_payload(OUTPUTS / 'Bot-reports/launch-sim')
                events = events_for(data, state, now, watchdog_probe(state.get('watchdog')), digest)
                payload, png = card_payload(data, link), render_map(data)
                preview(HOME / 'preview', payload, png, events, now)
                if args.send:
                    state['queue'].extend(events)
                    save_state(state_path, state)
                    # Drain alerts first; a rejected event stays queued during cooldown.
                    while state['queue']:
                        if not deliver(state, state_path, endpoint, state['queue'][0]):
                            break
                        if state['queue']:
                            time.sleep(max(0, state['next_at'] - time.time()))
                    if not state['queue'] and time.time() - state.get('last_live', 0) >= INTERVAL:
                        delay = state.get('next_at', 0) - time.time()
                        if 0 < delay <= 1:
                            time.sleep(delay)
                        deliver(state, state_path, endpoint, payload, png, live=True)
                else:
                    save_state(state_path, state)
                if args.once:
                    return 0
                time.sleep(max(0, INTERVAL - (time.monotonic() - start)))
    except KeyboardInterrupt:
        return 0
    except SafeError as error:
        print(str(error), file=sys.stderr)
    except Exception:
        print('Input, state or I/O error; no private details printed.', file=sys.stderr)
    return 2


if __name__ == '__main__':
    sys.exit(main())
