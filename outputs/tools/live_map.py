"""Live map of the test galaxy (Claude, 15 Oct 2026). Inside Debian:

    python3 live_map.py [--port 8765]

then open http://localhost:8765 on Windows (WSL mirrored networking reaches it). The idea is item 1 of the
TortoiseBots study (Documentation-support/tortoisebots-study.md): Sagiroth's observability dashboard, a 2D map per
planet with a marker per bot. Our code; nothing ported.

Fleet dashboard (owner, 15 Oct, with screenshots of that dashboard): one page with a sidebar. Overview; Bots (a
searchable list, field filters such as `planet:endor prof:rifleman doing:stuck`, and a detail panel per bot: species,
professions, bars, credits, target, role, gear, activity); Map (planet tabs, area chips, dots by profession, trails, the
planet's own map image decoded from the client's texture/ui_map_<planet>.dds and cached under /var/tmp/swg-bots/mapimg);
Activity; Issues (stuck, refused commands, dead or incapacitated, from the labels, the squads' latest reports and
Bot-reports/play); Server (who.json, uptime and the test galaxy's error lines, IPs removed). The roster is groups.json
plus the fleet test's load-groups.json; species and professions come from there. Health, credits, target and posture
appear once a bot's squad.py publishes them from a status or fight reply.

Read-only. It reads the test galaxy's log/who.json (names, planets and positions; account ids and IPs are dropped and
never sent to the page), the squads' activity records (Bot-reports/runs/*-activity.json), the bot roster
(tools/bots/groups.json) and the known places (tools/bots/places.json). It never talks to a bot or to the server.
Positions are as fresh as who.json, which Core3 writes every Core3.OnlineLogSeconds (default 300 s; tools/test_galaxy.py
sets 10) and on logins. Listens on 127.0.0.1 only.

Labels and live positions (owner, 15 Oct: "relabel the tracker so i can read what everyone is doing ... closer to a
live view"): squad.py writes what each bot is doing ("walking to 3830, -4520", "/polearmLegHit2 on sevorrt") and its
own latest position to /var/tmp/swg-bots/now/<name>.json on every command; a bot's own position is used when it is
fresher than who.json. The page refreshes every 1.5 s.

Temporary log (owner, 15 Oct: "maybe the tracker can keep some temp logs?"): every 3 s, if any bot moved or changed
what it is doing, or a squad changed state, a background thread appends machine lines to
Bot-reports/tracker/<yyyymmdd-hh>.jsonl and a readable snapshot (a line per bot: where, doing what, for how long, in
which scenario) to <yyyymmdd-hh>.txt. Files older than 48 hours are deleted; the folder is not in git. Players who are
not bots (the owner) are never logged.
"""
import argparse
import collections
import json
import os
import re
import struct
import sys
import threading
import time
import zlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

HERE = Path(__file__).resolve().parent
OUTPUTS = HERE.parent
WHO = Path('/opt/swg/testgalaxy/Core3/MMOCoreORB/bin/log/who.json')
RUNS = OUTPUTS / 'Bot-reports' / 'runs'
GROUPS = HERE / 'bots' / 'groups.json'
PLACES = HERE / 'bots' / 'places.json'
CITY_PLANET = {'mos_eisley': 'tatooine', 'coronet': 'corellia', 'theed': 'naboo', 'mos_espa': 'tatooine'}
TRAIL = 40
LOGS = OUTPUTS / 'Bot-reports' / 'tracker'
KEEP_HOURS = 48
NOW = Path('/var/tmp/swg-bots/now')   # squad.py: what each bot is doing, and where it last said it was
NOW_FRESH = 15 * 60                   # an older label is stale (the bot's script ended)
NAVMAPS = OUTPUTS / 'Bot-reports' / 'navmaps'   # tools/navmap.py: building floor plans for /floor
LOAD_GROUPS = HERE / 'bots' / 'load-groups.json'   # tools/bots/load_fleet.py: the fleet test's extra bodies
REPORTS = OUTPUTS / 'Bot-reports'               # <group>/<stamp>-<scenario>.json: each squad run's report
PLAY = REPORTS / 'play'                         # escort.py's play data (.jsonl)
CORE3_LOG = WHO.parent / 'core3.log'
MAPIMG = NOW.parent / 'mapimg'                  # planet maps decoded from the client (derived from its files: not in git)
HISTORY = 60                                    # label changes kept per bot for the Activity tab

roster = {}     # first name -> group
profiles = {}   # first name -> {'full', 'group', 'species', 'profession', 'skills'}
trails = {}     # first name -> [(x, y)]
history = {}    # first name -> deque of [t, doing, zone, x, y], newest last
_cache = {}     # (kind, path) -> (mtime, value)


def load_roster():
    roster.clear()
    profiles.clear()
    for path in (GROUPS, LOAD_GROUPS):
        try:
            groups = json.loads(path.read_text(encoding='utf-8'))['groups']
        except (OSError, ValueError, KeyError):
            continue
        for group, info in groups.items():
            for member in info.get('members', []):
                first = member.get('name', '').split(' ')[0]
                roster[first] = group
                profiles[first] = {'full': member.get('name', first), 'group': group,
                                   'species': member.get('race', ''), 'profession': member.get('profession', ''),
                                   'skills': list(info.get('training', {}).get(first, []))}
    roster.setdefault('Kael', 'Kael')


# ---- shaping (tested in test_live_map.py) ----

SPECIES = {'moncal': 'Mon Calamari', 'twilek': "Twi'lek", 'human': 'Human', 'rodian': 'Rodian', 'zabrak': 'Zabrak',
           'bothan': 'Bothan', 'trandoshan': 'Trandoshan', 'wookiee': 'Wookiee', 'ithorian': 'Ithorian', 'sullustan': 'Sullustan'}
# Skill-name word -> combat role, in the order a role is named first (a squad leader who shoots is a leader).
ROLES = (('squadleader', 'leader'), ('polearm', 'tank'), ('2hsword', 'melee'), ('1hsword', 'melee'), ('brawler', 'melee'),
         ('unarmed', 'melee'), ('rifleman', 'ranged'), ('pistol', 'ranged'), ('carbine', 'ranged'), ('marksman', 'ranged'),
         ('commando', 'ranged'), ('bountyhunter', 'ranged'), ('medic', 'healer'), ('doctor', 'healer'),
         ('dancer', 'buffer'), ('musician', 'buffer'), ('entertainer', 'buffer'), ('ranger', 'scout'), ('scout', 'scout'),
         ('artisan', 'crafter'), ('architect', 'crafter'), ('chef', 'crafter'), ('tailor', 'crafter'), ('weaponsmith', 'crafter'))
WORDS = {'squadleader': 'Squad Leader', '1hsword': 'Swordsman', '2hsword': 'Fencer', 'polearm': 'Pikeman',
         'bountyhunter': 'Bounty Hunter', 'unarmed': 'Teras Kasi'}


def species_label(race):
    """'twilek_female' -> "Twi'lek female"."""
    kind, _, sex = (race or '').partition('_')
    return (SPECIES.get(kind, kind.capitalize()) + (' ' + sex if sex else '')).strip()


def skill_label(skill):
    """'combat_rifleman_novice' -> 'Rifleman (novice)', 'outdoors_squadleader_master' -> 'Squad Leader (master)',
    'combat_marksman' -> 'Marksman'."""
    parts = (skill or '').split('_')[1:] or [skill or '']
    name = WORDS.get(parts[0], parts[0].capitalize())
    return name + (f" ({' '.join(parts[1:])})" if parts[1:] else '')


def roles_for(profession, skills=()):
    """Combat roles a bot's starting profession and trained skills give it, most telling first."""
    words = set('_'.join([profession or ''] + list(skills)).split('_'))
    out = []
    for word, role in ROLES:
        if word in words and role not in out:
            out.append(role)
    return out


def state_of(online, doing, posture=None):
    """One word for the Bots page's state chips."""
    d = (doing or '').lower()
    if not online:
        return 'offline'
    if posture in ('dead', 'incapacitated'):
        return 'down'
    if d.startswith('stuck'):
        return 'stuck'
    if d.startswith('fighting') or posture == 'combat':
        return 'fighting'
    if d.startswith(('walking', 'following', 'travelling')):
        return 'moving'
    if d.startswith(('waiting', 'holding')) or 'waiting' in d:
        return 'waiting'
    return 'busy' if d else 'idle'


def area_of(zone, x, y, areas):
    """A named area from places.json when the spot is inside its box, else the planet's 2 km sector ('sector D4':
    columns A-H west to east, rows 1-8 north to south)."""
    for a in areas:
        x0, y0, x1, y1 = a['box']
        if a['zone'] == zone and min(x0, x1) <= x <= max(x0, x1) and min(y0, y1) <= y <= max(y0, y1):
            return a['name']
    col = min(7, max(0, int((x + 8192) // 2048)))
    row = min(7, max(0, int((8192 - y) // 2048)))
    return f'sector {"ABCDEFGH"[col]}{row + 1}'


def report_digest(report, started=None):
    """A squad report (Bot-reports/<group>/*.json) cut to what the dashboard shows per bot: refused commands, its own
    falls (dead or incapacitated) and XP grants, with absolute times. `started` is the report's start in epoch
    seconds (its 'started' text in local time otherwise)."""
    if started is None:
        try:
            started = time.mktime(time.strptime(report.get('started', ''), '%Y-%m-%d %H:%M:%S'))
        except (ValueError, OverflowError):
            started = 0.0
    bots = {}
    for name, events in (report.get('events') or {}).items():
        row = bots.setdefault(name, {'refused': [], 'down': [], 'xp': 0, 'span': 0.0})
        for e in events:
            t = started + float(e.get('t') or 0)
            row['span'] = max(row['span'], float(e.get('t') or 0))
            kind = e.get('event')
            if kind == 'command_failed':
                row['refused'].append([round(t), str(e.get('command', '?')), str(e.get('reason', '?'))])
            elif kind == 'posture' and e.get('name') == 'me' and e.get('posture') in ('dead', 'incapacitated'):
                row['down'].append([round(t), e['posture']])
            elif kind == 'system' and 'grant_xp' in str(e.get('text', '')):
                row['xp'] += 1
    return {'group': report.get('group', ''), 'scenario': report.get('scenario', ''), 'state': report.get('state', ''),
            'started': round(started), 'seconds': report.get('seconds'), 'bots': bots}


def play_digest(rows):
    """Escort play data (Bot-reports/play/*.jsonl rows) cut to the crew's failed attacks and the orders they heard."""
    misses, orders, low = collections.Counter(), [], None
    for r in rows:
        if r.get('kind') == 'combat' and r.get('by_crew') and 'out_of_range' in str(r.get('what', '')):
            misses[str(r.get('attacker_name') or '?').split(' ')[0]] += 1
        elif r.get('kind') == 'order':
            orders.append([round(r.get('t', 0)), r.get('order'), r.get('heard_by')])
        elif r.get('kind') == 'player' and isinstance(r.get('health'), (int, float)):
            low = r['health'] if low is None else min(low, r['health'])
    last = max((r.get('t', 0) for r in rows), default=0)
    return {'out_of_range': dict(misses), 'orders': orders[-20:], 'player_low': low, 'last': round(last)}


def issues(bots, reports, play, now, window=24 * 3600):
    """Stuck, down and refused, newest first. bots: the dashboard's bot rows; reports: {group: report_digest};
    play: play_digest of the newest escort run or None."""
    out = []
    for b in bots:
        if b.get('online') and str(b.get('doing', '')).startswith('stuck'):
            out.append({'kind': 'stuck', 'bot': b['name'], 'group': b['group'], 'detail': b['doing'], 'count': 1,
                        't': round(b.get('since') or now)})
        if b.get('online') and b.get('posture') in ('dead', 'incapacitated'):
            out.append({'kind': 'down', 'bot': b['name'], 'group': b['group'], 'detail': b['posture'] + ' now',
                        'count': 1, 't': round(b.get('vitals_at') or now)})
    for group, rep in reports.items():
        for name, row in rep['bots'].items():
            seen = {}
            for t, command, reason in row['refused']:
                if now - t < window:
                    key = (command, reason)
                    hit = seen.setdefault(key, {'kind': 'refused', 'bot': name, 'group': group,
                                                'detail': f'/{command}: {reason}', 'count': 0, 't': t})
                    hit['count'] += 1
                    hit['t'] = max(hit['t'], t)
            out.extend(seen.values())
            for t, posture in row['down']:
                if now - t < window:
                    out.append({'kind': 'down', 'bot': name, 'group': group, 'detail': f"{posture} ({rep['scenario']})",
                                'count': 1, 't': t})
    if play and now - play['last'] < window:
        for name, n in play['out_of_range'].items():
            out.append({'kind': 'refused', 'bot': name, 'group': roster.get(name, ''), 'detail': 'attack out of range (escort)',
                        'count': n, 't': play['last']})
    return sorted(out, key=lambda r: -r['t'])


LOG_LINE = re.compile(r'^(\w{3} \w{3} +\d+ [\d:]+ \d{4}) \[\d+ msec\] \((\d+) s\) Thread \d+ - \[([^\]]*)\] '
                      r'(ERROR|WARNING|FATAL) - (.*)$')
IP = re.compile(r'\b\d{1,3}(?:\.\d{1,3}){3}(?::\d+)?\b')


def error_digest(lines, limit=40):
    """Core3 log lines -> (uptime seconds from the newest line, [{'level', 'where', 'msg', 'count', 'last'}]) with
    repeats folded together and IP addresses removed (the page never shows them)."""
    uptime, seen = None, {}
    for line in lines:
        m = re.search(r'\[\d+ msec\] \((\d+) s\)', line)
        if m:
            uptime = int(m.group(1))
        m = LOG_LINE.match(line.rstrip())
        if not m:
            continue
        when, _, where, level, msg = m.groups()
        where, msg = IP.sub('<ip>', where).replace(' <ip>', ''), IP.sub('<ip>', msg)
        key = (level, where, re.sub(r'\d+', '#', msg)[:200])   # 'missing account 97' and '... 98' are one kind
        row = seen.setdefault(key, {'level': level, 'where': where, 'msg': '', 'count': 0, 'last': ''})
        row.update(count=row['count'] + 1, last=when, msg=msg[:300])
    rows = sorted(seen.values(), key=lambda r: r['last'], reverse=True)
    return uptime, rows[:limit]


def dds_rgb(data):
    """(width, height, RGB bytes) of a DXT1, DXT5 or plain 24/32-bit DDS (the client's ui_map textures), or None."""
    if data[:4] != b'DDS ' or len(data) < 128:
        return None
    h, w = struct.unpack_from('<II', data, 12)
    fourcc, bits = data[84:88], struct.unpack_from('<I', data, 88)[0]
    if fourcc in (b'DXT1', b'DXT5'):
        step, skip = (8, 0) if fourcc == b'DXT1' else (16, 8)
        out, pos = bytearray(w * h * 3), 128
        for by in range(0, h, 4):
            for bx in range(0, w, 4):
                c0, c1, idx = struct.unpack_from('<HHI', data, pos + skip)
                pos += step
                pal = []
                for c in (c0, c1):
                    pal.append(((c >> 11 & 31) * 255 // 31, (c >> 5 & 63) * 255 // 63, (c & 31) * 255 // 31))
                a, b = pal
                if c0 > c1 or fourcc == b'DXT5':
                    pal += [tuple((2 * a[i] + b[i]) // 3 for i in range(3)), tuple((a[i] + 2 * b[i]) // 3 for i in range(3))]
                else:
                    pal += [tuple((a[i] + b[i]) // 2 for i in range(3)), (0, 0, 0)]
                pal = [bytes(p) for p in pal]
                for row in range(min(4, h - by)):
                    base = ((by + row) * w + bx) * 3
                    line = b''.join(pal[idx >> (2 * (row * 4 + col)) & 3] for col in range(min(4, w - bx)))
                    out[base:base + len(line)] = line
        return w, h, bytes(out)
    if fourcc == b'\0\0\0\0' and bits in (24, 32):
        size, px = w * h, bits // 8
        raw = data[128:128 + size * px]
        out = bytearray(size * 3)
        out[0::3], out[1::3], out[2::3] = raw[2::px], raw[1::px], raw[0::px]   # stored BGR(A)
        return w, h, bytes(out)
    return None


def png(w, h, rgb):
    """A plain RGB PNG (no imaging library in the WSL Python)."""
    def part(tag, body):
        return struct.pack('>I', len(body)) + tag + body + struct.pack('>I', zlib.crc32(tag + body) & 0xFFFFFFFF)
    rows = b''.join(b'\0' + rgb[y * w * 3:(y + 1) * w * 3] for y in range(h))
    return (b'\x89PNG\r\n\x1a\n' + part(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0))
            + part(b'IDAT', zlib.compress(rows, 6)) + part(b'IEND', b''))


_map_lock = threading.Lock()


def map_image(planet):
    """PNG bytes of the planet's own map (texture/ui_map_<planet>.dds from the client's archives), cached on the WSL
    disk; None when the client has no such map."""
    if not re.fullmatch(r'[a-z0-9_]+', planet or ''):
        return None
    cached = MAPIMG / f'{planet}.png'
    with _map_lock:
        if cached.is_file():
            return cached.read_bytes()
        try:
            sys.path.insert(0, str(HERE))
            from swgfmt import trn_iff
            data = trn_iff.client_file(f'texture/ui_map_{planet}.dds')
        except Exception:   # no client folder, or an archive the reader does not know
            return None
        decoded = dds_rgb(data) if data else None
        if not decoded:
            return None
        body = png(*decoded)
        try:
            MAPIMG.mkdir(parents=True, exist_ok=True)
            cached.write_bytes(body)
        except OSError:
            pass
        return body


def places():
    try:
        data = json.loads(PLACES.read_text(encoding='utf-8'))
    except (OSError, ValueError):
        return []
    out = []
    for city, info in data.items():
        zone = info.get('planet') or CITY_PLANET.get(city)
        if not zone or not isinstance(info, dict):
            continue
        for kind, rows in info.get('terminals', {}).items():
            for row in rows:
                if 'x' in row and 'y' in row:
                    out.append({'zone': zone, 'kind': kind.replace('terminal_', '').replace('_name', ''),
                                'x': row['x'], 'y': row['y']})
    return out


def activity():
    rows = []
    now = time.time()
    for path in sorted(RUNS.glob('*-activity.json')):
        try:
            row = json.loads(path.read_text(encoding='utf-8'))
        except (OSError, ValueError):
            continue
        rows.append({'group': row.get('group', path.stem.split('-')[0]), 'scenario': row.get('scenario', ''),
                     'state': row.get('state', ''), 'detail': str(row.get('detail', ''))[:160],
                     'age': max(0, round(now - float(row.get('updated', 0))))})   # a running round stamps ahead
    return rows


def now_records():
    """name -> the bot's own 'now' record (squad.py), however old."""
    out = {}
    for path in NOW.glob('*.json') if NOW.is_dir() else ():
        try:
            row = json.loads(path.read_text(encoding='utf-8'))
        except (OSError, ValueError):
            continue
        out[row.get('name') or path.stem] = row
    return out


def labels():
    """name -> the bot's own 'now' record (squad.py), if it is fresh."""
    now = time.time()
    return {name: row for name, row in now_records().items() if now - float(row.get('updated', 0)) < NOW_FRESH}


def areas():
    """Named areas from places.json: {'zone', 'name', 'box': [x0, y0, x1, y1]}."""
    try:
        data = json.loads(PLACES.read_text(encoding='utf-8'))
    except (OSError, ValueError):
        return []
    return [{'zone': info.get('planet') or CITY_PLANET.get(city), 'name': city.replace('_', ' ').title(),
             'box': info['area']} for city, info in data.items()
            if isinstance(info, dict) and len(info.get('area') or []) == 4 and (info.get('planet') or CITY_PLANET.get(city))]


def cached(kind, path, build):
    """build(path), recomputed only when the file changes."""
    try:
        mtime = path.stat().st_mtime
    except OSError:
        return None
    hit = _cache.get((kind, path))
    if hit and hit[0] == mtime:
        return hit[1]
    value = build(path)
    _cache[(kind, path)] = (mtime, value)
    return value


def latest_reports(max_age=24 * 3600):
    """{group: report_digest} of each squad's newest report from the last day."""
    out, now = {}, time.time()
    for group in sorted(set(roster.values())):
        folder = REPORTS / group
        if not folder.is_dir():
            continue
        paths = sorted(p for p in folder.glob('2*.json'))
        if not paths or now - paths[-1].stat().st_mtime > max_age:
            continue
        try:
            digest = cached('report', paths[-1], lambda p: report_digest(json.loads(p.read_text(encoding='utf-8'))))
        except (OSError, ValueError):
            continue
        if digest:
            digest['file'] = paths[-1].name
            out[group] = digest
    return out


def latest_play():
    paths = sorted(PLAY.glob('*.jsonl')) if PLAY.is_dir() else []

    def build(path):
        rows = []
        for line in path.read_text(encoding='utf-8', errors='replace').splitlines():
            try:
                rows.append(json.loads(line))
            except ValueError:
                pass
        return dict(play_digest(rows), file=path.name)
    return cached('play', paths[-1], build) if paths else None


def present():
    """Everyone online, with the freshest position known and, for bots, what they are doing.
    Returns (chars, who_age, error, who_mtime)."""
    chars, age, error, now = [], None, '', time.time()
    try:
        mtime = WHO.stat().st_mtime
        age = round(now - mtime)
        clients = json.loads(WHO.read_text(encoding='utf-8', errors='replace')).get('clients', [])
    except (OSError, ValueError) as e:
        clients, error, mtime = [], f'cannot read who.json: {type(e).__name__}', 0.0
    told = labels()
    for c in clients:
        name = c.get('firstName') or '?'
        x, y = float(c.get('worldPositionX', 0)), float(c.get('worldPositionY', 0))
        zone, pos_s = c.get('zone') or '?', age
        own = told.get(name, {}) if name in roster else {}
        # A bot's own status reply is usually fresher than who.json (written every few seconds at best).
        if own.get('pos_at', 0) > mtime and own.get('zone', zone) == zone and own.get('x') is not None:
            x, y, pos_s = own['x'], own['y'], round(now - own['pos_at'])
        doing = own.get('doing', '')
        local = own.get('cell') and now - float(own.get('local_at', 0)) < 60
        chars.append({'name': name, 'zone': zone, 'x': x, 'y': y, 'pos_s': pos_s,
                      'kind': 'bot' if name in roster else 'player', 'group': roster.get(name, ''),
                      'online_s': c.get('sessionSeconds'), 'indoors': bool(own.get('cell')),
                      'doing': doing, 'doing_s': round(now - own['since']) if doing and own.get('since') else None,
                      **({'cell': own['cell'], 'lx': own.get('lx'), 'ly': own.get('ly'), 'lz': own.get('lz')} if local else {})})
    return chars, age, error, mtime


def escorted():
    """Players an escort crew is with indoors (escort.py puts the player's cell and spot in the leader's label)."""
    out, now = [], time.time()
    for row in labels().values():
        seen = row.get('escorted')
        if seen and now - float(seen.get('at', 0)) < 20:
            out.append(seen)
    return out


def bot_rows(chars, reports):
    """Every bot on the roster, online or not, for the Bots page: its profile, where it is, what it is doing and the
    vitals and credits its last status reply gave."""
    online, told, now, places_ = {c['name']: c for c in chars}, now_records(), time.time(), areas()
    out = []
    for name, prof in sorted(profiles.items()):
        c, own = online.get(name), told.get(name, {})
        rep = reports.get(prof['group'], {}).get('bots', {}).get(name)
        zone = c['zone'] if c else own.get('zone', '')
        x, y = (c['x'], c['y']) if c else (own.get('x'), own.get('y'))
        fresh = now - float(own.get('updated', 0)) < NOW_FRESH
        doing = (c or {}).get('doing', '') if c else ''
        vitals = now - float(own.get('vitals_at', 0)) < NOW_FRESH
        row = {'name': name, 'full': prof['full'], 'group': prof['group'], 'online': bool(c),
               'species': species_label(prof['species']), 'prof': prof['profession'].split('_')[-1],
               'profession': skill_label(prof['profession']), 'skills': [skill_label(s) for s in prof['skills']],
               'roles': roles_for(prof['profession'], prof['skills']), 'zone': zone, 'x': x, 'y': y,
               'area': area_of(zone, x, y, places_) if x is not None and y is not None else '',
               'indoors': bool((c or {}).get('indoors')), 'doing': doing, 'doing_s': (c or {}).get('doing_s'),
               'since': own.get('since') if fresh else None, 'label_age': round(now - own['updated']) if own.get('updated') else None,
               'online_s': (c or {}).get('online_s'), 'last_doing': own.get('doing', ''),
               'posture': own.get('posture') if vitals else None, 'vitals_at': own.get('vitals_at') if vitals else None,
               'state': state_of(bool(c), doing, own.get('posture') if vitals else None)}
        for key in ('ham', 'max_ham', 'level', 'target', 'cash_credits', 'bank_credits'):
            if own.get(key) is not None and (vitals or key.endswith('credits')):
                row[key] = own[key]
        if rep:
            hours = max(rep['span'], 60) / 3600
            row.update(refused=len(rep['refused']), downs=len(rep['down']), xp=rep['xp'],
                       xp_per_hour=round(rep['xp'] / hours, 1) if rep['xp'] else None)
        out.append(row)
    return out


def snapshot():
    chars, age, error, mtime = present()
    for c in chars:
        trail = trails.setdefault(c['name'], [])
        if not trail or trail[-1][:2] != [c['x'], c['y']] or trail[-1][2] != c['zone']:
            trail.append([c['x'], c['y'], c['zone']])
            del trail[:-TRAIL]
        c['trail'] = [[tx, ty] for tx, ty, tz in trail if tz == c['zone']]
    reports = latest_reports()
    bots = bot_rows(chars, reports)
    return {'who_age': age, 'error': error, 'time': time.strftime('%H:%M:%S'), 'chars': chars,
            'activity': activity(), 'places': places(), 'escorted': escorted(), 'bots': bots, 'areas': areas(),
            'issues': issues(bots, reports, latest_play(), time.time())}


def bot_detail(name):
    """The detail panel's Activity and Gear tabs: recent labels, refused commands, falls and inventory."""
    own = now_records().get(name, {})
    group = roster.get(name, '')
    rep = latest_reports().get(group)
    row = (rep or {}).get('bots', {}).get(name, {})
    return {'name': name, 'history': list(history.get(name, []))[::-1],
            'refused': row.get('refused', [])[-30:][::-1], 'down': row.get('down', [])[::-1],
            'report': {k: rep[k] for k in ('scenario', 'state', 'started', 'seconds', 'file')} if rep else None,
            'items': own.get('items'), 'items_at': own.get('items_at')}


def fleet_feed(limit=150):
    """The newest label changes across the fleet, for the Activity page."""
    rows = [[t, name, doing, zone] for name, h in list(history.items()) for t, doing, zone, _, _ in h]
    return sorted(rows, key=lambda r: -r[0])[:limit]


def server_info():
    """The Server page: who.json in brief, uptime and error lines from the end of core3.log, and the log files."""
    info, now = {'who': None, 'uptime': None, 'errors': [], 'logs': []}, time.time()
    try:
        who = json.loads(WHO.read_text(encoding='utf-8', errors='replace'))
        clients = who.get('clients', [])
        info['who'] = {'stamp': who.get('@timestamp', ''), 'age': round(now - WHO.stat().st_mtime), 'clients': len(clients),
                       'bots': sum(1 for c in clients if c.get('firstName') in roster),
                       'players': sorted(c.get('firstName', '?') for c in clients if c.get('firstName') not in roster),
                       'planets': dict(collections.Counter(c.get('zone', '?') for c in clients))}
    except (OSError, ValueError):
        pass
    try:
        with open(CORE3_LOG, 'rb') as f:
            f.seek(max(0, CORE3_LOG.stat().st_size - 768 * 1024))
            tail = f.read().decode('utf-8', 'replace').splitlines()[1:]
        info['uptime'], info['errors'] = error_digest(tail)
        info['log_age'] = round(now - CORE3_LOG.stat().st_mtime)
    except OSError:
        pass
    for path in sorted(WHO.parent.glob('*.log')):
        st = path.stat()
        info['logs'].append({'name': path.name, 'kb': round(st.st_size / 1024), 'age': round(now - st.st_mtime)})
    return info


def seed_history():
    """Fill the Activity tab's label history from the last two hours of tracker logs, so a restart keeps it."""
    for path in sorted(LOGS.glob('*.jsonl'))[-2:] if LOGS.is_dir() else ():
        for line in path.read_text(encoding='utf-8', errors='replace').splitlines():
            try:
                r = json.loads(line)
            except ValueError:
                continue
            if r.get('kind') == 'bot':
                remember(r['name'], r.get('t', 0), r.get('doing', ''), r.get('zone', ''), r.get('x'), r.get('y'))


def remember(name, t, doing, zone, x, y):
    h = history.setdefault(name, collections.deque(maxlen=HISTORY))
    if doing and (not h or h[-1][1] != doing):
        h.append([round(t), doing, zone, x, y])


def readable(chars, scenario):
    """One snapshot as text: a line per bot, grouped by squad, saying where it is and what it is doing."""
    rows = sorted((c for c in chars if c['kind'] == 'bot'), key=lambda c: (c['group'], c['name']))
    out = [time.strftime('%H:%M:%S') + ' ' + '-' * 60]
    for c in rows:
        doing = (c['doing'] or 'idle') + (f" ({c['doing_s']} s)" if c['doing_s'] is not None else '')
        where = f"{c['zone']} {c['x']:.0f} {c['y']:.0f}" + (' indoors' if c['indoors'] else '')
        job = scenario.get(c['group'], '')
        out.append(f"  {c['name']:<8} {c['group']:<6} {where:<28} {doing}" + (f"   [{job}]" if job else ''))
    return '\n'.join(out) + '\n'


def record(last, every=3):
    """The temporary log (see the top of this file). Runs forever in its own thread: every few seconds, if any
    bot moved, changed what it is doing, or a squad changed state, it appends machine lines (.jsonl) and a
    readable snapshot of every bot (.txt)."""
    while True:
        try:
            load_roster()  # a crew added to groups.json is logged without a restart
            chars, _, _, _ = present()
            stamp, lines = round(time.time()), []
            for c in chars:
                if c['kind'] != 'bot':
                    continue
                state = (c['zone'], round(c['x']), round(c['y']), c['doing'], c.get('cell'), c.get('lx'), c.get('ly'))
                if last.get(c['name']) != state:
                    last[c['name']] = state
                    remember(c['name'], stamp, c['doing'], c['zone'], round(c['x']), round(c['y']))
                    lines.append({'t': stamp, 'kind': 'bot', **{k: c[k] for k in (
                        'name', 'group', 'zone', 'x', 'y', 'indoors', 'doing', 'doing_s', 'pos_s')},
                        **{k: c[k] for k in ('cell', 'lx', 'ly', 'lz') if k in c}})
            scenario = {}
            for row in activity():
                scenario[row['group']] = f"{row['scenario'].replace('.py', '')}: {row['state']}" if row['scenario'] else row['state']
                state = (row['scenario'], row['state'], row['detail'])
                if last.get('activity:' + row['group']) != state:
                    last['activity:' + row['group']] = state
                    lines.append(dict(row, t=stamp, kind='activity'))
            if lines:
                LOGS.mkdir(parents=True, exist_ok=True)
                hour = time.strftime('%Y%m%d-%H')
                with open(LOGS / f'{hour}.jsonl', 'a', encoding='utf-8') as f:
                    f.write(''.join(json.dumps(line) + '\n' for line in lines))
                with open(LOGS / f'{hour}.txt', 'a', encoding='utf-8') as f:
                    f.write(readable(chars, scenario))
            cutoff = time.time() - KEEP_HOURS * 3600
            for old in list(LOGS.glob('*.jsonl')) + list(LOGS.glob('*.txt')):
                if old.stat().st_mtime < cutoff:
                    old.unlink()
        except (OSError, ValueError):
            pass
        time.sleep(every)


def navmaps():
    """The floor plans navmap.py built: name, planet, building and the server ids of its cells."""
    out = []
    for path in sorted(NAVMAPS.glob('*.json')):
        try:
            plan = json.loads(path.read_text(encoding='utf-8'))
        except (OSError, ValueError):
            continue
        out.append({'name': path.stem, 'planet': plan.get('planet'), 'building': plan.get('building'),
                    'template': plan.get('template', '').rsplit('/', 1)[-1],
                    'cells': [c['oid'] for c in plan.get('cells', []) if c.get('oid')]})
    return out


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        url = urlparse(self.path)
        if self.path.startswith('/data.json'):
            body, kind = json.dumps(snapshot()).encode(), 'application/json'
        elif url.path == '/bot.json':
            body, kind = json.dumps(bot_detail(parse_qs(url.query).get('name', [''])[0])).encode(), 'application/json'
        elif url.path == '/feed.json':
            body, kind = json.dumps(fleet_feed()).encode(), 'application/json'
        elif url.path == '/server.json':
            body, kind = json.dumps(server_info()).encode(), 'application/json'
        elif url.path.startswith('/mapimg/') and url.path.endswith('.png'):
            body, kind = map_image(url.path[len('/mapimg/'):-4]), 'image/png'
            if body is None:
                self.send_error(404)
                return
        elif self.path.startswith('/navmaps.json'):
            body, kind = json.dumps(navmaps()).encode(), 'application/json'
        elif self.path.startswith('/navmap/') and self.path.endswith('.json') and '..' not in self.path:
            target = NAVMAPS / self.path[len('/navmap/'):].split('?')[0]
            if not target.is_file():
                self.send_error(404)
                return
            body, kind = target.read_bytes(), 'application/json'
        elif self.path.split('?')[0] in ('/floor', '/floor.html'):
            body, kind = FLOOR_PAGE.encode(), 'text/html; charset=utf-8'
        elif url.path in ('/', '/index.html'):
            body, kind = PAGE.encode(), 'text/html; charset=utf-8'
        else:
            self.send_error(404)
            return
        self.send_response(200)
        self.send_header('Content-Type', kind)
        self.send_header('Cache-Control', 'no-store')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


PAGE = r'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Test Galaxy Fleet</title><link rel="icon" href="data:,">
<style>
:root{--bg:#0d1117;--side:#10151c;--panel:#151b23;--panel2:#1b222c;--ink:#e6e8eb;--muted:#8b949e;--line:#28303a;
--accent:#3fb950;--accent2:#2ea04326;--warn:#d29922;--bad:#f85149;--info:#58a6ff;--gold:#e3b341;--veil:rgba(0,0,0,.18);
--halo:rgba(0,0,0,.8);--grid:#1f2630;--grid2:#2c3540;--place:#8b949e;--you:#ffffff;--hp:#2ea043;--ap:#d29922;--mp:#388bfd}
@media (prefers-color-scheme:light){:root:not([data-theme="dark"]){--bg:#f6f7f9;--side:#eef0f3;--panel:#ffffff;--panel2:#f3f4f6;
--ink:#1f2328;--muted:#656d76;--line:#d8dee4;--accent:#1a7f37;--accent2:#1a7f3718;--warn:#9a6700;--bad:#cf222e;--info:#0969da;
--gold:#9a6700;--veil:rgba(255,255,255,.08);--halo:rgba(255,255,255,.9);--grid:#eceff2;--grid2:#d0d7de;--place:#8c959f;--you:#1f2328}}
:root[data-theme="light"]{--bg:#f6f7f9;--side:#eef0f3;--panel:#ffffff;--panel2:#f3f4f6;--ink:#1f2328;--muted:#656d76;
--line:#d8dee4;--accent:#1a7f37;--accent2:#1a7f3718;--warn:#9a6700;--bad:#cf222e;--info:#0969da;--gold:#9a6700;
--veil:rgba(255,255,255,.08);--halo:rgba(255,255,255,.9);--grid:#eceff2;--grid2:#d0d7de;--place:#8c959f;--you:#1f2328}
*{box-sizing:border-box}html,body{margin:0;background:var(--bg);color:var(--ink);font:14px/1.45 system-ui,-apple-system,"Segoe UI",sans-serif}
a{color:var(--info)}button,input{font:inherit;color:inherit}
#app{display:grid;grid-template-columns:220px minmax(0,1fr);min-height:100vh}
#side{background:var(--side);border-right:1px solid var(--line);display:flex;flex-direction:column;padding:16px 10px;position:sticky;top:0;height:100vh}
.brand{display:flex;align-items:center;gap:8px;font-weight:700;font-size:16px;padding:0 8px 18px}
.brand svg{color:var(--accent)}.brand small{margin-left:auto;font:11px ui-monospace,monospace;color:var(--muted)}
nav{display:flex;flex-direction:column;gap:2px}nav .sec{font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);padding:14px 10px 4px}
nav a{display:flex;align-items:center;gap:10px;padding:7px 10px;border-radius:6px;color:var(--ink);text-decoration:none;opacity:.85;position:relative}
nav a:hover{background:var(--panel2);opacity:1}nav a.on{background:var(--accent2);opacity:1;font-weight:600}
nav a.on::before{content:"";position:absolute;left:-10px;top:6px;bottom:6px;width:3px;border-radius:2px;background:var(--accent)}
nav svg{width:16px;height:16px;flex:none;color:var(--muted)}nav a.on svg{color:var(--accent)}
.badge{margin-left:auto;font-size:11px;background:var(--bad);color:#fff;border-radius:9px;padding:0 6px;font-weight:600}
.badge:empty{display:none}
.foot{margin-top:auto;display:flex;justify-content:space-between;padding:0 8px;font-size:13px;color:var(--muted)}.foot a{color:var(--muted)}
#main{min-width:0}
header{display:flex;flex-wrap:wrap;align-items:center;gap:10px 14px;padding:14px 24px;border-bottom:1px solid var(--line);position:sticky;top:0;background:var(--bg);z-index:5}
header h1{font-size:20px;margin:0;font-weight:700;margin-right:auto}
.search{position:relative}.search input{width:260px;max-width:52vw;background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:6px 34px 6px 10px}
.search kbd{position:absolute;right:8px;top:6px;font:11px ui-monospace,monospace;border:1px solid var(--line);border-radius:4px;padding:0 5px;color:var(--muted)}
.pill{display:flex;align-items:center;gap:8px;border:1px solid var(--line);border-radius:999px;padding:5px 12px;font-size:13px;background:var(--panel)}
.pill i{width:8px;height:8px;border-radius:50%;background:var(--muted)}.pill.ok{border-color:color-mix(in srgb,var(--accent) 50%,transparent);background:var(--accent2)}
.pill.ok i{background:var(--accent)}.pill.warn i{background:var(--warn)}.pill.bad i{background:var(--bad)}
.btn{background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:6px 12px;cursor:pointer;white-space:nowrap}.btn:hover{background:var(--panel2)}
.page{padding:20px 24px;display:none;flex-direction:column;gap:16px}.page.on{display:flex}
.card{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:14px 16px;min-width:0}
.cardhead{display:flex;justify-content:space-between;align-items:baseline;gap:10px;margin-bottom:8px;flex-wrap:wrap}
.cardhead b{font-size:15px}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px}
.stat .k{font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:var(--muted)}.stat .v{font-size:28px;font-weight:700;line-height:1.2;font-variant-numeric:tabular-nums}
.stat .s{font-size:12px;color:var(--muted)}
.cols{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:16px}
.row{display:flex;flex-wrap:wrap;gap:8px 10px;align-items:center}.grow{flex:1}
.row input[type=text],.row input:not([type]){flex:1;min-width:200px;background:var(--bg);border:1px solid var(--line);border-radius:8px;padding:7px 10px}
.lbl{font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);font-weight:600;min-width:52px}
.seg{display:inline-flex;border:1px solid var(--line);border-radius:8px;overflow:hidden}.seg button{border:0;background:transparent;padding:6px 12px;cursor:pointer;color:var(--muted)}
.seg button.on{background:var(--panel2);color:var(--ink);font-weight:600}
.chips{display:flex;flex-wrap:wrap;gap:6px;margin-top:10px}.chip{display:inline-flex;align-items:center;gap:6px;border:1px solid var(--line);
border-radius:999px;padding:3px 10px;font-size:13px;background:var(--panel2);cursor:pointer;white-space:nowrap}
.chip b{font-weight:600}.chip .n{color:var(--muted);font-variant-numeric:tabular-nums}.chip.on{border-color:var(--info);background:color-mix(in srgb,var(--info) 16%,transparent)}
.dot{display:inline-block;width:9px;height:9px;border-radius:50%;flex:none}
table{width:100%;border-collapse:collapse;font-size:13px}th{text-align:left;font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);
font-weight:600;padding:8px 10px;border-bottom:1px solid var(--line);white-space:nowrap}th[data-s]{cursor:pointer}th.on{color:var(--info)}
td{padding:8px 10px;border-bottom:1px solid var(--line);vertical-align:top}tbody tr.click{cursor:pointer}tbody tr.click:hover td{background:var(--panel2)}
tr.pick td{background:var(--accent2)}td.n{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap;color:var(--muted)}
.small{font-size:12px;color:var(--muted)}.mono{font-family:ui-monospace,monospace}.ell{max-width:340px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.tag{display:inline-block;font:600 11px ui-monospace,monospace;letter-spacing:.04em;text-transform:uppercase;border-radius:4px;padding:1px 6px;
background:color-mix(in srgb,var(--info) 18%,transparent);color:var(--info)}
.tag.ok{background:var(--accent2);color:var(--accent)}.tag.off{background:var(--panel2);color:var(--muted)}.tag.bad{background:color-mix(in srgb,var(--bad) 18%,transparent);color:var(--bad)}
.tag.warn{background:color-mix(in srgb,var(--warn) 18%,transparent);color:var(--warn)}
.scroll{overflow-x:auto}
.mapwrap{position:relative;background:var(--panel);border:1px solid var(--line);border-radius:10px;overflow:hidden;aspect-ratio:1/1;max-height:78vh;width:100%}
.mapwrap canvas{width:100%;height:100%;display:block;cursor:grab;touch-action:none}
.maptools{position:absolute;top:10px;left:10px;display:flex;gap:6px}.maptools .btn{padding:4px 10px;font-size:13px;background:color-mix(in srgb,var(--panel) 88%,transparent)}
#tip{position:absolute;pointer-events:none;background:var(--panel);border:1px solid var(--line);border-radius:6px;padding:4px 8px;font-size:12px;display:none;white-space:nowrap;z-index:2}
#maploading{position:absolute;right:12px;top:12px;font-size:12px;color:var(--muted)}
.legend{display:flex;flex-wrap:wrap;gap:4px 14px;margin-top:10px;font-size:13px;color:var(--muted)}.legend span{display:inline-flex;align-items:center;gap:6px}
label.check{display:inline-flex;align-items:center;gap:6px;font-size:13px;cursor:pointer}
#drawer{position:fixed;inset:0 0 0 auto;width:min(760px,100%);background:var(--panel);border-left:1px solid var(--line);box-shadow:-12px 0 32px rgba(0,0,0,.35);
z-index:20;overflow-y:auto;padding:20px 24px;display:none}#drawer.on{display:block}
.dhead{display:flex;gap:12px;align-items:flex-start}.dhead h2{margin:0;font-size:24px;color:var(--gold)}.dhead .acts{margin-left:auto;display:flex;gap:8px;align-items:center}
.roles{color:var(--warn);font-weight:600;margin-top:4px}
.vitals{display:grid;grid-template-columns:repeat(3,minmax(0,1fr)) auto;gap:10px;align-items:center;margin:18px 0 6px}
.bar{position:relative;height:22px;border-radius:4px;background:var(--bg);overflow:hidden;border:1px solid var(--line)}
.bar i{position:absolute;inset:0 auto 0 0;display:block}.bar span{position:relative;display:block;text-align:center;font:600 12px/20px ui-monospace,monospace;color:#fff;text-shadow:0 1px 2px #000}
.bar span.none{color:var(--muted);text-shadow:none;font-weight:400}
.money{text-align:right;font:13px ui-monospace,monospace;color:var(--gold)}
.tabs{display:flex;flex-wrap:wrap;gap:4px;border-bottom:1px solid var(--line);margin:14px 0 14px}.tabs button{border:1px solid transparent;border-bottom:0;background:none;
padding:7px 14px;cursor:pointer;color:var(--muted);border-radius:8px 8px 0 0;font-weight:600}.tabs button.on{color:var(--ink);border-color:var(--line);background:var(--panel2)}
.kv{display:grid;grid-template-columns:max-content minmax(0,1fr);gap:7px 16px;font-size:14px}.kv dt{color:var(--muted)}.kv dd{margin:0;text-align:right;overflow-wrap:anywhere}
.cardk{font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);font-weight:600;margin-bottom:10px}
.empty{color:var(--muted);font-size:13px;padding:6px 0}
.ptabs{display:inline-flex;flex-wrap:wrap;border:1px solid var(--line);border-radius:8px;overflow:hidden}.ptabs button{border:0;background:transparent;padding:6px 14px;cursor:pointer;color:var(--muted)}
.ptabs button.on{background:var(--panel2);color:var(--ink);font-weight:600}
@media (max-width:820px){#app{grid-template-columns:1fr}#side{position:static;height:auto;flex-direction:row;flex-wrap:wrap;align-items:center;padding:8px 12px;gap:6px}
 .brand{padding:0 8px 0 0}nav{flex-direction:row;flex-wrap:wrap}nav .sec{display:none}nav a.on::before{display:none}.foot{display:none}
 header{padding:10px 16px}.page{padding:16px}.search input{width:180px}.vitals{grid-template-columns:1fr}.money{text-align:left}}
</style></head><body>
<div id="app">
<aside id="side">
 <div class="brand"><svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2 3 7l9 5 9-5-9-5Zm-9 9 9 5 9-5-2.2-1.2L12 13.6 5.2 9.8 3 11Zm0 4 9 5 9-5-2.2-1.2L12 17.6l-6.8-3.8L3 15Z"/></svg>Test Galaxy<small>Core3</small></div>
 <nav id="nav">
  <a href="#overview" data-p="overview"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/></svg>Overview</a>
  <div class="sec">Fleet</div>
  <a href="#bots" data-p="bots"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="9" cy="8" r="4"/><path d="M2 21c0-4 3-6 7-6s7 2 7 6M16 4a4 4 0 0 1 0 8M22 21c0-3-1.5-5-4-5.7"/></svg>Bots</a>
  <a href="#map" data-p="map"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m3 6 6-3 6 3 6-3v15l-6 3-6-3-6 3V6Zm6-3v15m6-12v15"/></svg>Map</a>
  <div class="sec">Insight</div>
  <a href="#activity" data-p="activity"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 12h4l3 8 4-16 3 8h4"/></svg>Activity</a>
  <div class="sec">Operations</div>
  <a href="#issues" data-p="issues"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 3 2 20h20L12 3Zm0 6v5m0 3v.5"/></svg>Issues<span class="badge" id="nIssues"></span></a>
  <a href="#server" data-p="server"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 21v-7m0-4V3m8 18v-9m0-4V3m8 18v-5m0-4V3M1 14h6m2-6h6m2 8h6"/></svg>Server</a>
 </nav>
 <div class="foot"><a href="/floor">Floor plans ↗</a><span id="clock"></span></div>
</aside>
<div id="main">
<header><h1 id="title">Overview</h1>
 <div class="search"><input id="find" placeholder="Find a bot…" autocomplete="off"><kbd>/</kbd></div>
 <div class="pill" id="pill"><i></i><span>loading…</span></div><button class="btn" id="refresh">Refresh</button></header>

<section class="page" id="p-overview">
 <div class="stats" id="ovStats"></div>
 <div class="cols"><div class="card"><div class="cardhead"><b>Squads</b><span class="small">from each squad's activity record</span></div><div class="scroll"><table><tbody id="ovSquads"></tbody></table></div></div>
 <div class="card"><div class="cardhead"><b>Doing now</b><a href="#bots" class="small">all bots</a></div><div class="chips" id="ovStates" style="margin-top:0"></div>
  <div class="cardhead" style="margin-top:16px"><b>Planets</b><a href="#map" class="small">map</a></div><div class="chips" id="ovPlanets" style="margin-top:0"></div>
  <div class="cardhead" style="margin-top:16px"><b>Latest issues</b><a href="#issues" class="small">all issues</a></div><table><tbody id="ovIssues"></tbody></table></div></div>
</section>

<section class="page" id="p-bots">
 <div class="card"><div class="row"><input id="q" placeholder="Name, profession or fields — planet:tatooine prof:rifleman doing:stuck squad:forn role:healer area:&quot;mos eisley&quot;" autocomplete="off">
  <div class="seg" id="seg"><button data-o="all">All</button><button data-o="online">Online</button><button data-o="offline">Offline</button></div></div>
  <div class="chips" id="stateChips"></div><div class="chips" id="profChips"></div></div>
 <div class="card"><div class="cardhead"><b id="botCount"></b><span class="small">Fields: planet, area, prof, role, squad, species, doing, state, name. Click a bot for details.</span></div>
  <div class="scroll"><table><thead><tr><th data-s="name">Name</th><th data-s="prof">Profession</th><th data-s="group">Squad</th><th data-s="zone">Where</th><th data-s="doing">Doing</th><th data-s="since" style="text-align:right">For</th></tr></thead><tbody id="botRows"></tbody></table></div></div>
</section>

<section class="page" id="p-map">
 <div class="card">
  <div class="row"><span class="lbl">Planet</span><div class="ptabs" id="planetTabs"></div><span class="grow"></span>
   <label class="check"><input type="checkbox" id="trailsOn" checked> Path trails</label><label class="check"><input type="checkbox" id="labelsOn" checked> Labels</label></div>
  <div class="row" style="margin-top:10px"><span class="lbl">Area</span><input id="areaFilter" placeholder="Filter areas…" autocomplete="off"><span class="tag" id="areaCount"></span></div>
  <div class="chips" id="areaChips"></div><div class="legend" id="legend"></div></div>
 <div class="mapwrap" id="wrap"><canvas id="map"></canvas><div class="maptools"><button class="btn" id="fit">Fit</button><button class="btn" id="whole">Whole planet</button></div><div id="maploading"></div><div id="tip"></div></div>
 <div class="small" id="indoorLine"></div>
</section>

<section class="page" id="p-activity">
 <div class="card"><div class="cardhead"><b>Squads</b><span class="small">scenario and state, from Bot-reports/runs</span></div><div class="scroll"><table><thead><tr><th>Squad</th><th>Scenario</th><th>State</th><th>Detail</th><th style="text-align:right">Updated</th></tr></thead><tbody id="actSquads"></tbody></table></div></div>
 <div class="card"><div class="cardhead"><b>What the fleet did</b><span class="small">every change of a bot's label, newest first (kept in memory and seeded from Bot-reports/tracker)</span></div>
  <div class="row"><input id="feedQ" placeholder="Filter by bot, planet or words…" autocomplete="off"></div><div class="scroll"><table><tbody id="feed"></tbody></table></div></div>
</section>

<section class="page" id="p-issues">
 <div class="card"><div class="cardhead"><b id="issueCount"></b><span class="small">stuck now (labels), dead or incapacitated (status replies and squad reports), refused commands (squad reports, last 24 h) and escort play data</span></div>
  <div class="chips" id="issueChips" style="margin-top:0"></div></div>
 <div class="card"><div class="scroll"><table><thead><tr><th>When</th><th>Bot</th><th>Squad</th><th>Kind</th><th>What</th><th style="text-align:right">Times</th></tr></thead><tbody id="issueRows"></tbody></table></div></div>
</section>

<section class="page" id="p-server">
 <div class="stats" id="srvStats"></div>
 <div class="card"><div class="cardhead"><b>Error lines</b><span class="small">the end of the test galaxy's core3.log, repeats folded, addresses removed</span></div><div class="scroll"><table><thead><tr><th>Last</th><th>Level</th><th>Where</th><th>Message</th><th style="text-align:right">Times</th></tr></thead><tbody id="srvErrors"></tbody></table></div></div>
 <div class="cols"><div class="card"><div class="cardhead"><b>Online now</b><span class="small">who.json</span></div><div id="srvWho"></div></div>
 <div class="card"><div class="cardhead"><b>Log files</b><span class="small">bin/log</span></div><table><tbody id="srvLogs"></tbody></table></div></div>
</section>
</div></div>

<div id="drawer" role="dialog" aria-label="Bot detail">
 <div class="dhead"><div><h2 id="dName"></h2><div class="small" id="dSub"></div><div class="roles" id="dRoles"></div></div>
  <div class="acts"><span id="dOnline"></span><button class="btn" id="dMap">Show on map</button><button class="btn" id="dClose" aria-label="Close">✕</button></div></div>
 <div class="vitals" id="dVitals"></div>
 <div class="tabs" id="dTabs"><button data-t="overview">Overview</button><button data-t="gear">Gear &amp; skills</button><button data-t="activity">Activity</button></div>
 <div id="dBody"></div>
</div>

<script>
const PROF={marksman:['Marksman','#e8c547'],brawler:['Brawler','#c79c6e'],scout:['Scout','#7fd35b'],medic:['Medic','#4cc9f0'],
 entertainer:['Entertainer','#f78fb3'],artisan:['Artisan','#ff8c42'],other:['Other','#a78bfa']};
const TITLES={overview:'Overview',bots:'Bots',map:'Map',activity:'Activity',issues:'Issues',server:'Server'};
const STATES=['fighting','moving','waiting','busy','idle','stuck','down','offline'];
const STATE_COL={fighting:'--bad',moving:'--info',waiting:'--gold',busy:'--accent',idle:'--muted',stuck:'--warn',down:'--bad',offline:'--muted'};
let data=null,page='overview',picked=null,detailTab='overview',detail=null,botSort='name',online='all',stateF='',profF='',issueF='';
let zone=localGet('zone')||'tatooine',view=null,drag=null,hits=[],fitted=false,areaFocus='',imgs={},feed=[],server=null;
function localGet(k){try{return localStorage.getItem('fleet.'+k)}catch(e){return null}}
function localSet(k,v){try{localStorage.setItem('fleet.'+k,v)}catch(e){}}
function $(id){return document.getElementById(id)}
function css(n){return getComputedStyle(document.documentElement).getPropertyValue(n).trim()}
function esc(t){return String(t??'').replace(/[&<>"]/g,ch=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[ch]))}
function ago(s){return s==null?'':s<90?Math.round(s)+' s':s<5400?Math.round(s/60)+' min':Math.round(s/3600)+' h'}
function clock(t){return t?new Date(t*1000).toTimeString().slice(0,8):''}
function num(n){return n==null?'–':Number(n).toLocaleString()}
function profCol(p){return (PROF[p]||PROF.other)[1]}
function bot(name){return data?data.bots.find(b=>b.name===name):null}
function charOf(name){return data?data.chars.find(c=>c.name===name):null}
function stateDot(s){return `<span class="dot" style="background:var(${STATE_COL[s]||'--muted'})"></span>`}
function where(b){return b.zone?`${esc(b.zone)}<div class="small">${esc(b.area)}${b.indoors?' · indoors':''}</div>`:'<span class="small">never seen</span>'}

/* ---- routing ---- */
function route(){const h=location.hash.slice(1);const [p,qs]=h.split('?');page=TITLES[p]?p:'overview';
 const prm=new URLSearchParams(qs||'');const b=prm.get('bot');
 document.querySelectorAll('.page').forEach(s=>s.classList.toggle('on',s.id==='p-'+page));
 document.querySelectorAll('#nav a').forEach(a=>a.classList.toggle('on',a.dataset.p===page));
 $('title').textContent=TITLES[page];if(b){openBot(b,false)}else{$('drawer').classList.remove('on');if(page!=='map')picked=null}
 if(page==='activity')loadFeed();if(page==='server')loadServer();render()}
addEventListener('hashchange',route);

/* ---- polling ---- */
async function poll(){try{data=await(await fetch('data.json',{cache:'no-store'})).json()}catch(e){setPill('bad','tracker not answering');return}render()}
async function loadFeed(){try{feed=await(await fetch('feed.json',{cache:'no-store'})).json();if(page==='activity')renderActivity()}catch(e){}}
async function loadServer(){try{server=await(await fetch('server.json',{cache:'no-store'})).json();if(page==='server')renderServer()}catch(e){}}
async function loadDetail(){if(!picked)return;try{detail=await(await fetch('bot.json?name='+encodeURIComponent(picked),{cache:'no-store'})).json();renderDetail()}catch(e){}}
function setPill(kind,text){const p=$('pill');p.className='pill '+kind;p.querySelector('span').innerHTML=text}

function render(){if(!data)return;
 const bots=data.chars.filter(c=>c.kind==='bot').length,players=data.chars.filter(c=>c.kind==='player').length;
 if(data.error)setPill('bad',esc(data.error));
 else if(data.who_age!=null&&data.who_age>120)setPill('warn',`server list ${ago(data.who_age)} old · <b>${bots}</b> bots · <b>${players}</b> player${players===1?'':'s'}`);
 else setPill('ok',`running · <b>${bots}</b> bots · <b>${players}</b> player${players===1?'':'s'}`);
 $('nIssues').textContent=data.issues.length||'';$('clock').textContent=data.time;
 if(page==='overview')renderOverview();if(page==='bots')renderBots();if(page==='map')renderMap();
 if(page==='activity')renderActivity();if(page==='issues')renderIssues();if(picked)renderDetail()}

/* ---- overview ---- */
function stat(k,v,s){return `<div class="card stat"><div class="k">${k}</div><div class="v">${v}</div><div class="s">${s||''}</div></div>`}
function renderOverview(){const B=data.bots,on=B.filter(b=>b.online);const players=data.chars.filter(c=>c.kind==='player');
 const running=data.activity.filter(a=>a.state==='running').length;
 $('ovStats').innerHTML=stat('Bots online',on.length,`of ${B.length} on the roster`)+stat('Players',players.length,players.map(p=>esc(p.name)).join(', ')||'nobody')+
  stat('Indoors',on.filter(b=>b.indoors).length,'<a href="/floor">floor plans</a>')+stat('Issues',data.issues.length,'<a href="#issues">stuck, down, refused</a>')+
  stat('Squads running',running,`${data.activity.length} squads known`);
 $('ovSquads').innerHTML=data.activity.map(a=>`<tr><td><b>${esc(a.group)}</b></td><td>${esc(a.scenario.replace('.py',''))}<div class="small">${esc(a.state)}${a.age<86400?' · '+ago(a.age)+' ago':''}</div></td></tr>`).join('')||'<tr><td class="empty">no squad records</td></tr>';
 const sc={};on.forEach(b=>sc[b.state]=(sc[b.state]||0)+1);
 $('ovStates').innerHTML=STATES.filter(s=>sc[s]).map(s=>`<a class="chip" href="#bots" onclick="stateF='${s}'">${stateDot(s)}<b>${s}</b><span class="n">${sc[s]}</span></a>`).join('')||'<span class="empty">no bots online</span>';
 const pc={};data.chars.forEach(c=>pc[c.zone]=(pc[c.zone]||0)+1);
 $('ovPlanets').innerHTML=Object.keys(pc).sort().map(z=>`<a class="chip" href="#map" onclick="setZone('${esc(z)}')"><b>${esc(z)}</b><span class="n">${pc[z]}</span></a>`).join('')||'<span class="empty">nobody online</span>';
 $('ovIssues').innerHTML=data.issues.slice(0,6).map(issueRow).join('')||'<tr><td class="empty">none</td></tr>'}

/* ---- bots ---- */
const FIELDS={planet:b=>b.zone,zone:b=>b.zone,area:b=>b.area,prof:b=>[b.prof,b.profession,...b.skills].join(' '),profession:b=>[b.prof,b.profession,...b.skills].join(' '),
 role:b=>b.roles.join(' '),squad:b=>b.group,group:b=>b.group,species:b=>b.species,race:b=>b.species,doing:b=>(b.doing||'')+' '+b.state,
 state:b=>b.state,name:b=>b.full};
function parseQuery(q){const out=[],re=/(\w+):(?:"([^"]*)"|(\S+))|"([^"]*)"|(\S+)/g;let m;
 while((m=re.exec(q))){if(m[1])out.push({f:m[1].toLowerCase(),v:(m[2]??m[3]).toLowerCase()});else out.push({f:'',v:(m[4]??m[5]).toLowerCase()})}return out}
function matches(b,terms){return terms.every(t=>{const get=FIELDS[t.f];
 const hay=get?get(b):[b.full,b.group,b.prof,b.profession,b.skills.join(' '),b.zone,b.area,b.doing,b.species,b.roles.join(' '),b.state].join(' ');
 return String(hay||'').toLowerCase().includes(t.v)})}
function filtered(){const terms=parseQuery($('q').value);return data.bots.filter(b=>(online==='all'||(online==='online')===b.online)&&matches(b,terms))}
function sortKey(b){return botSort==='since'?-(b.doing_s??-1):botSort==='prof'?b.prof+b.name:botSort==='zone'?(b.zone||'~')+b.area+b.name:
 botSort==='doing'?(b.doing||'~')+b.name:botSort==='group'?b.group+b.name:b.name}
function renderBots(){const base=filtered();const sc={},pc={};base.forEach(b=>{sc[b.state]=(sc[b.state]||0)+1;pc[b.prof]=(pc[b.prof]||0)+1});
 const rows=base.filter(b=>(!stateF||b.state===stateF)&&(!profF||b.prof===profF));
 $('stateChips').innerHTML=`<span class="chip ${stateF?'':'on'}" data-st=""><b>Any state</b><span class="n">${base.length}</span></span>`+
  STATES.filter(s=>sc[s]).map(s=>`<span class="chip ${stateF===s?'on':''}" data-st="${s}">${stateDot(s)}${s}<span class="n">${sc[s]}</span></span>`).join('');
 $('profChips').innerHTML=`<span class="chip ${profF?'':'on'}" data-pf=""><b>All professions</b><span class="n">${base.length}</span></span>`+
  Object.keys(pc).sort().map(p=>`<span class="chip ${profF===p?'on':''}" data-pf="${esc(p)}"><span class="dot" style="background:${profCol(p)}"></span>${esc((PROF[p]||[p])[0])}<span class="n">${pc[p]}</span></span>`).join('');
 $('seg').querySelectorAll('button').forEach(x=>x.classList.toggle('on',x.dataset.o===online));
 document.querySelectorAll('#p-bots th').forEach(th=>th.classList.toggle('on',th.dataset.s===botSort));
 $('botCount').textContent=`${rows.length} of ${data.bots.length} bots`;
 rows.sort((a,b)=>{const x=sortKey(a),y=sortKey(b);return x<y?-1:x>y?1:0});
 $('botRows').innerHTML=rows.map(b=>`<tr class="click ${picked===b.name?'pick':''}" data-b="${esc(b.name)}"><td><span class="dot" style="background:${profCol(b.prof)}"></span> <b>${esc(b.name)}</b><div class="small">${esc(b.full)}</div></td>
  <td>${esc(b.profession)}<div class="small">${esc(b.skills.join(', ')||b.species)}</div></td><td>${esc(b.group)}</td><td>${where(b)}</td>
  <td>${stateDot(b.state)} <span class="ell" style="display:inline-block;vertical-align:bottom">${esc(b.online?(b.doing||b.state):'offline')}</span>${!b.online&&b.last_doing?`<div class="small ell">last: ${esc(b.last_doing)}</div>`:''}</td>
  <td class="n">${b.online&&b.doing_s!=null?ago(b.doing_s):''}</td></tr>`).join('')||'<tr><td colspan="6" class="empty">no bot matches</td></tr>'}

/* ---- detail drawer ---- */
function openBot(name,push=true){picked=name;detail=null;$('drawer').classList.add('on');if(push&&page!=='map')history.replaceState(null,'','#'+page+'?bot='+encodeURIComponent(name));
 renderDetail();loadDetail()}
function closeBot(push=true){picked=null;$('drawer').classList.remove('on');if(push)history.replaceState(null,'','#'+page);render()}
function bar(label,cur,max,col){const ok=cur!=null&&max;const pct=ok?Math.max(0,Math.min(100,cur/max*100)):0;
 return `<div class="bar" title="${label}"><i style="width:${pct}%;background:${col}"></i><span class="${ok?'':'none'}">${ok?num(cur)+' / '+num(max)+' '+label:label+' not reported'}</span></div>`}
function kv(rows){return '<dl class="kv">'+rows.filter(r=>r).map(([k,v])=>`<dt>${k}</dt><dd>${v}</dd>`).join('')+'</dl>'}
function renderDetail(){if(!picked||!data)return;const b=bot(picked);if(!b){$('dName').textContent=picked;$('dBody').innerHTML='<div class="empty">not on the roster</div>';return}
 $('dName').innerHTML=`<span class="dot" style="background:${profCol(b.prof)};width:14px;height:14px;vertical-align:middle"></span> ${esc(b.full)}`;
 $('dSub').textContent=`${b.species} ${b.profession} · squad ${b.group}${b.level?' · level '+b.level:''}`;
 $('dRoles').textContent=b.skills.length?b.skills.join(' / '):b.profession;
 $('dOnline').innerHTML=b.online?'<span class="tag ok">online</span>':'<span class="tag off">offline</span>';
 const h=b.ham||{},m=b.max_ham||{};
 $('dVitals').innerHTML=bar('HP',h.health,m.health,'var(--hp)')+bar('Action',h.action,m.action,'var(--ap)')+bar('Mind',h.mind,m.mind,'var(--mp)')+
  `<div class="money">${b.cash_credits!=null?num(b.cash_credits)+' cr':'credits not reported'}${b.bank_credits!=null?`<div class="small">bank ${num(b.bank_credits)} cr</div>`:''}${b.vitals_at?`<div class="small">status ${ago(Date.now()/1000-b.vitals_at)} ago</div>`:''}</div>`;
 $('dTabs').querySelectorAll('button').forEach(x=>x.classList.toggle('on',x.dataset.t===detailTab));
 const sq=data.activity.find(a=>a.group===b.group);let html='';
 if(detailTab==='overview'){
  html=`<div class="cols"><div class="card"><div class="cardk">Right now</div>${kv([['Status',`${stateDot(b.state)} ${b.state}`],['Doing',esc(b.online?(b.doing||'nothing said'):(b.last_doing?'last: '+b.last_doing:'–'))],
   b.online&&b.doing_s!=null&&['For',ago(b.doing_s)],['Target',b.target?`<b style="color:var(--bad)">${esc(b.target)}</b>`:'–'],['Posture',esc(b.posture||'–')],
   ['Combat role',b.roles.length?b.roles.map((r,i)=>`<span class="tag ${i?'off':''}">${esc(r)}</span>`).join(' '):'–'],['Online for',b.online_s!=null?ago(b.online_s):'–']])}</div>
   <div class="card"><div class="cardk">Where and how it is going</div>${kv([['Planet',esc(b.zone||'–')],['Area',esc(b.area||'–')],
   ['Position',b.x!=null?Math.round(b.x)+', '+Math.round(b.y)+(b.indoors?' (indoors)':''):'–'],['Squad',esc(b.group)],
   ['Scenario',sq?esc(sq.scenario.replace('.py',''))+` <span class="small">${esc(sq.state)}</span>`:'–'],
   ['XP grants per hour',b.xp_per_hour!=null?`${b.xp_per_hour} <span class="small">(${b.xp} in the last report)</span>`:'<span class="small">none in the last report</span>'],
   ['Refused commands',b.refused!=null?b.refused:'–'],['Falls',b.downs!=null?b.downs:'–']])}</div></div>`}
 else if(detailTab==='gear'){const it=detail&&detail.items;
  html=`<div class="cols"><div class="card"><div class="cardk">Skills</div>${kv([['Species',esc(b.species)],['Starting profession',esc(b.profession)],
   ...b.skills.map((s,i)=>[i?'':'Trained',esc(s)])])}</div><div class="card"><div class="cardk">Gear and inventory</div>${!it?'<div class="empty">No inventory reply yet: a bot publishes its gear and bag when its scenario runs the inventory command.</div>':
   '<table><tbody>'+it.map(i=>`<tr><td>${esc(i.name)}</td><td class="n">${i.worn?'<span class="tag">worn</span>':'bag'}</td></tr>`).join('')+'</tbody></table>'+
   `<div class="small">${it.length} items · listed ${ago(Date.now()/1000-detail.items_at)} ago</div>`}</div></div>`}
 else{const d=detail;if(!d){html='<div class="empty">loading…</div>'}else{
  html=`<div class="card"><div class="cardk">Recent labels</div><table><tbody>${d.history.map(r=>`<tr><td class="n" style="text-align:left">${clock(r[0])}</td><td>${esc(r[1])}</td><td class="small">${esc(r[2])}</td></tr>`).join('')||'<tr><td class="empty">no label changes seen since the tracker started</td></tr>'}</tbody></table></div>
  <div class="card" style="margin-top:16px"><div class="cardk">Refused commands and falls${d.report?` · ${esc(d.report.scenario)} report, started ${clock(d.report.started)}`:''}</div><table><tbody>
  ${d.down.map(r=>`<tr><td class="n" style="text-align:left">${clock(r[0])}</td><td><span class="tag bad">${esc(r[1])}</span></td><td></td></tr>`).join('')}
  ${d.refused.map(r=>`<tr><td class="n" style="text-align:left">${clock(r[0])}</td><td class="mono">/${esc(r[1])}</td><td class="small">${esc(r[2])}</td></tr>`).join('')}
  ${!d.down.length&&!d.refused.length?'<tr><td class="empty">none in the squad\'s latest report</td></tr>':''}</tbody></table></div>`}}
 $('dBody').innerHTML=html}
$('dTabs').onclick=e=>{const t=e.target.dataset.t;if(t){detailTab=t;if(t!=='overview')loadDetail();renderDetail()}};
$('dClose').onclick=()=>closeBot();
$('dMap').onclick=()=>{const b=bot(picked);if(!b||!b.zone)return;showOnMap(b)};
function showOnMap(b){setZone(b.zone);view={cx:b.x||0,cy:b.y||0,span:800};fitted=true;const n=b.name;$('drawer').classList.remove('on');location.hash='#map';picked=n}
addEventListener('keydown',e=>{if(e.key==='Escape'&&picked)closeBot();if(e.key==='/'&&document.activeElement.tagName!=='INPUT'){e.preventDefault();$('find').focus()}});

/* ---- map ---- */
const cv=$('map'),ctx=cv.getContext('2d'),tip=$('tip');
function setZone(z){if(z!==zone){zone=z;localSet('zone',z);view=null;fitted=false;areaFocus=''}}
function here(){return data?data.chars.filter(c=>c.zone===zone):[]}
function profOf(c){const b=bot(c.name);return b?b.prof:'other'}
function colorOf(c){return c.kind==='player'?css('--you'):profCol(profOf(c))}
function mapImg(z){if(!imgs[z]){const img=new Image();imgs[z]={img,ok:false,failed:false};img.onload=()=>{imgs[z].ok=true;if(page==='map')draw()};
 img.onerror=()=>{imgs[z].failed=true;if(page==='map')draw()};img.src='mapimg/'+encodeURIComponent(z)+'.png'}return imgs[z]}
function fit(whole){const pts=[];if(!whole){here().forEach(c=>{pts.push([c.x,c.y]);c.trail.forEach(p=>pts.push(p))})}
 if(!pts.length){view={cx:0,cy:0,span:16384};return}
 const xs=pts.map(p=>p[0]),ys=pts.map(p=>p[1]),x0=Math.min(...xs),x1=Math.max(...xs),y0=Math.min(...ys),y1=Math.max(...ys);
 view={cx:(x0+x1)/2,cy:(y0+y1)/2,span:Math.max(300,Math.max(x1-x0,y1-y0)*1.5)}}
function toScreen(x,y){const s=cv.width/view.span;return[(x-view.cx)*s+cv.width/2,(view.cy-y)*s+cv.height/2]}
function toWorld(px,py){const s=cv.width/view.span;return[(px-cv.width/2)/s+view.cx,view.cy-(py-cv.height/2)/s]}
function clip(t,n){return t.length>n?t.slice(0,n-1)+'…':t}
function draw(){const r=cv.getBoundingClientRect(),d=devicePixelRatio||1;if(!r.width)return;cv.width=r.width*d;cv.height=r.height*d;
 if(!view)fit(false);ctx.clearRect(0,0,cv.width,cv.height);const im=mapImg(zone),pic=im.ok;
 $('maploading').textContent=im.ok||im.failed?(im.failed?'no map image for this planet: grid only':''):'loading the planet map…';
 if(pic){const[x0,y0]=toScreen(-8192,8192),[x1,y1]=toScreen(8192,-8192);ctx.drawImage(im.img,x0,y0,x1-x0,y1-y0);ctx.fillStyle=css('--veil');ctx.fillRect(0,0,cv.width,cv.height)}
 const steps=[16,32,64,128,256,512,1024,2048,4096];const step=steps.find(s=>view.span/s<=12)||4096;
 const[wx0,wy1]=toWorld(0,0),[wx1,wy0]=toWorld(cv.width,cv.height);ctx.lineWidth=d;ctx.font=(11*d)+'px system-ui';ctx.globalAlpha=pic?.35:1;
 for(let gx=Math.ceil(wx0/step)*step;gx<=wx1;gx+=step){const[x]=toScreen(gx,0);ctx.strokeStyle=css(gx===0?'--grid2':'--grid');ctx.beginPath();ctx.moveTo(x,0);ctx.lineTo(x,cv.height);ctx.stroke();ctx.fillStyle=css('--muted');ctx.fillText(gx,x+3*d,cv.height-4*d)}
 for(let gy=Math.ceil(wy0/step)*step;gy<=wy1;gy+=step){const[,y]=toScreen(0,gy);ctx.strokeStyle=css(gy===0?'--grid2':'--grid');ctx.beginPath();ctx.moveTo(0,y);ctx.lineTo(cv.width,y);ctx.stroke();ctx.fillStyle=css('--muted');ctx.fillText(gy,3*d,y-3*d)}
 ctx.globalAlpha=1;hits=[];
 if(areaFocus){const a=areaBox(areaFocus);if(a){const[p,q]=toScreen(a[0],a[3]),[s,t]=toScreen(a[2],a[1]);ctx.strokeStyle=css('--info');ctx.setLineDash([6*d,4*d]);ctx.lineWidth=1.5*d;ctx.strokeRect(p,q,s-p,t-q);ctx.setLineDash([])}}
 (data?data.places:[]).filter(p=>p.zone===zone).forEach(p=>{const[x,y]=toScreen(p.x,p.y);ctx.fillStyle=css('--place');ctx.fillRect(x-2*d,y-2*d,4*d,4*d);
  hits.push({x,y,label:p.kind+' ('+Math.round(p.x)+', '+Math.round(p.y)+')'})});
 if($('trailsOn').checked)here().forEach(c=>{if(c.trail.length<2)return;ctx.strokeStyle=colorOf(c);ctx.globalAlpha=.5;ctx.lineWidth=2*d;ctx.beginPath();
  c.trail.forEach((p,i)=>{const[x,y]=toScreen(p[0],p[1]);i?ctx.lineTo(x,y):ctx.moveTo(x,y)});ctx.stroke();ctx.globalAlpha=1});
 const spots=[];here().sort((a,b)=>(a.kind>b.kind?-1:1)).forEach(c=>{const[x,y]=toScreen(c.x,c.y);const s=spots.find(s=>Math.hypot(s.x-x,s.y-y)<14*d);if(s)s.list.push(c);else spots.push({x,y,list:[c]})});
 const halo=pic?'rgba(0,0,0,.8)':css('--halo'),ink=pic?'#fff':css('--ink');
 spots.forEach(s=>{s.list.forEach((c,i)=>{const a=i*2.4,r0=s.list.length>1?Math.min(4+i*1.6,22)*d:0,x=s.x+Math.cos(a)*r0,y=s.y+Math.sin(a)*r0;
   const rad=(c.kind==='player'?7:5)*d*(picked===c.name?1.6:1);ctx.fillStyle=colorOf(c);ctx.beginPath();ctx.arc(x,y,rad,0,7);ctx.fill();
   ctx.strokeStyle=picked===c.name?css('--info'):'rgba(0,0,0,.7)';ctx.lineWidth=(picked===c.name?3:1.5)*d;ctx.stroke();
   hits.push({x,y,name:c.kind==='bot'?c.name:null,label:c.name+(c.group?' · '+c.group:' · player')+': '+(c.kind==='player'?'you':(c.doing||'idle'))+' ('+Math.round(c.x)+', '+Math.round(c.y)+')'})});
  if(!$('labelsOn').checked)return;const shown=s.list.slice(0,6),lx=s.x+(s.list.length>1?28:10)*d,top=s.y+4*d-(shown.length-1)*7*d;
  shown.forEach((c,i)=>{const y=top+i*14*d,text=c.name+(c.kind==='bot'?' — '+clip(c.doing||'idle',34):'');ctx.font=(c.kind==='player'?'600 ':'')+(12*d)+'px system-ui';
   ctx.lineWidth=3*d;ctx.strokeStyle=halo;ctx.strokeText(text,lx,y);ctx.fillStyle=ink;ctx.fillText(text,lx,y)});
  if(s.list.length>shown.length){ctx.fillStyle=ink;ctx.fillText('+'+(s.list.length-shown.length)+' more',lx,top+shown.length*14*d)}})}
function sectorBox(n){const m=/^sector ([A-H])([1-8])$/.exec(n);if(!m)return null;const c='ABCDEFGH'.indexOf(m[1]),r=+m[2]-1;return[-8192+c*2048,8192-(r+1)*2048,-8192+(c+1)*2048,8192-r*2048]}
function areaBox(n){const a=(data?data.areas:[]).find(a=>a.zone===zone&&a.name===n);if(a){const[x0,y0,x1,y1]=a.box;return[Math.min(x0,x1),Math.min(y0,y1),Math.max(x0,x1),Math.max(y0,y1)]}return sectorBox(n)}
function renderMap(){const zones={},bz={};data.chars.forEach(c=>zones[c.zone]=(zones[c.zone]||0)+1);
 if(!zones[zone]&&Object.keys(zones).length&&!picked)setZone(Object.keys(zones).sort((a,b)=>zones[b]-zones[a])[0]);
 if(!fitted&&here().length){fit(false);fitted=true}
 $('planetTabs').innerHTML=Object.keys(zones).sort().map(z=>`<button class="${z===zone?'on':''}" data-z="${esc(z)}"><b>${esc(z)}</b> · ${zones[z]}</button>`).join('')||'<span class="empty" style="padding:6px 10px">nobody online</span>';
 const ac={};data.bots.filter(b=>b.online&&b.zone===zone).forEach(b=>ac[b.area]=(ac[b.area]||0)+1);const f=$('areaFilter').value.toLowerCase();
 const names=Object.keys(ac).filter(a=>a.toLowerCase().includes(f)).sort((a,b)=>ac[b]-ac[a]||a.localeCompare(b));
 $('areaCount').textContent=Object.keys(ac).length+' areas';
 $('areaChips').innerHTML=names.map(a=>`<span class="chip ${areaFocus===a?'on':''}" data-a="${esc(a)}"><b>${esc(a)}</b><span class="n">${ac[a]}</span></span>`).join('')||'<span class="empty">no bots here</span>';
 const pc={};data.bots.filter(b=>b.online&&b.zone===zone).forEach(b=>pc[b.prof]=1);
 $('legend').innerHTML=Object.keys(PROF).filter(p=>pc[p]).map(p=>`<span><span class="dot" style="background:${PROF[p][1]}"></span>${PROF[p][0]}</span>`).join('')+
  (here().some(c=>c.kind==='player')?`<span><span class="dot" style="background:var(--you);outline:1px solid var(--muted)"></span>Player</span>`:'')+
  `<span><span class="dot" style="background:var(--place);border-radius:1px"></span>Terminal</span>`;
 const inside=data.bots.filter(b=>b.online&&b.indoors).length,away=data.chars.filter(c=>c.zone!==zone).length;
 $('indoorLine').innerHTML=`${inside} bot${inside===1?'':'s'} indoors (<a href="/floor">see the floor plans</a>) · ${away} on other planets · positions come from each bot's own reply when it is fresher than who.json (${data.who_age!=null?ago(data.who_age)+' old':'unknown'}).`;
 draw()}
$('planetTabs').onclick=e=>{const z=e.target.closest('button')?.dataset.z;if(z){setZone(z);render()}};
$('areaChips').onclick=e=>{const a=e.target.closest('.chip')?.dataset.a;if(a==null)return;if(areaFocus===a){areaFocus='';fit(false)}else{areaFocus=a;const b=areaBox(a);
 if(b)view={cx:(b[0]+b[2])/2,cy:(b[1]+b[3])/2,span:Math.max(b[2]-b[0],b[3]-b[1])*1.15}}render()};
$('areaFilter').oninput=()=>render();$('trailsOn').onchange=draw;$('labelsOn').onchange=draw;
$('fit').onclick=()=>{areaFocus='';fit(false);render()};$('whole').onclick=()=>{fit(true);draw()};
cv.addEventListener('wheel',e=>{e.preventDefault();const d=devicePixelRatio||1,r=cv.getBoundingClientRect(),[wx,wy]=toWorld((e.clientX-r.left)*d,(e.clientY-r.top)*d);
 view.span=Math.min(20000,Math.max(40,view.span*(e.deltaY>0?1.25:.8)));const[nx,ny]=toWorld((e.clientX-r.left)*d,(e.clientY-r.top)*d);view.cx+=wx-nx;view.cy+=wy-ny;draw()},{passive:false});
cv.addEventListener('pointerdown',e=>{drag={x:e.clientX,y:e.clientY,cx:view.cx,cy:view.cy,moved:false};cv.setPointerCapture(e.pointerId)});
cv.addEventListener('pointerup',e=>{const was=drag;drag=null;if(was&&!was.moved){const d=devicePixelRatio||1,r=cv.getBoundingClientRect();
 const h=hits.filter(h=>h.name&&Math.hypot(h.x-(e.clientX-r.left)*d,h.y-(e.clientY-r.top)*d)<10*d).pop();if(h)openBot(h.name)}});
cv.addEventListener('pointermove',e=>{const d=devicePixelRatio||1,r=cv.getBoundingClientRect();
 if(drag){if(Math.hypot(e.clientX-drag.x,e.clientY-drag.y)>3)drag.moved=true;const s=view.span/cv.width*d;view.cx=drag.cx-(e.clientX-drag.x)*s;view.cy=drag.cy+(e.clientY-drag.y)*s;draw();return}
 const px=(e.clientX-r.left)*d,py=(e.clientY-r.top)*d,h=hits.filter(h=>Math.hypot(h.x-px,h.y-py)<10*d).pop();
 if(h){tip.style.display='block';tip.textContent=h.label;tip.style.left=Math.min(e.clientX-r.left+12,r.width-tip.offsetWidth-6)+'px';tip.style.top=(e.clientY-r.top+12)+'px'}else tip.style.display='none'});
cv.addEventListener('pointerleave',()=>tip.style.display='none');

/* ---- activity ---- */
function renderActivity(){if(!data)return;
 $('actSquads').innerHTML=data.activity.map(a=>`<tr><td><b>${esc(a.group)}</b></td><td>${esc(a.scenario.replace('.py',''))}</td><td><span class="tag ${a.state==='running'?'ok':a.state==='failed'?'bad':'off'}">${esc(a.state||'–')}</span></td>
  <td class="small" style="max-width:420px">${esc(a.detail)}</td><td class="n">${ago(a.age)} ago</td></tr>`).join('')||'<tr><td class="empty">no squad records</td></tr>';
 const f=$('feedQ').value.toLowerCase();
 $('feed').innerHTML=feed.filter(r=>!f||(r[1]+' '+r[2]+' '+r[3]).toLowerCase().includes(f)).slice(0,120).map(r=>{const b=bot(r[1]);
  return `<tr class="click" data-b="${esc(r[1])}"><td class="n" style="text-align:left;width:80px">${clock(r[0])}</td><td style="width:110px"><span class="dot" style="background:${profCol(b?b.prof:'other')}"></span> <b>${esc(r[1])}</b></td><td>${esc(r[2])}</td><td class="small">${esc(r[3])}</td></tr>`}).join('')||'<tr><td class="empty">nothing yet</td></tr>'}
$('feedQ').oninput=renderActivity;

/* ---- issues ---- */
const KIND_TAG={stuck:'warn',down:'bad',refused:''};
function issueRow(i){return `<tr class="click" data-b="${esc(i.bot)}"><td class="n" style="text-align:left">${clock(i.t)}</td><td><b>${esc(i.bot)}</b></td><td>${esc(i.group)}</td>
 <td><span class="tag ${KIND_TAG[i.kind]}">${esc(i.kind)}</span></td><td>${esc(i.detail)}</td><td class="n">${i.count>1?'×'+i.count:''}</td></tr>`}
function renderIssues(){const kc={};data.issues.forEach(i=>kc[i.kind]=(kc[i.kind]||0)+1);const rows=data.issues.filter(i=>!issueF||i.kind===issueF);
 $('issueCount').textContent=`${data.issues.length} issue${data.issues.length===1?'':'s'}`;
 $('issueChips').innerHTML=`<span class="chip ${issueF?'':'on'}" data-k=""><b>All</b><span class="n">${data.issues.length}</span></span>`+
  ['stuck','down','refused'].map(k=>`<span class="chip ${issueF===k?'on':''}" data-k="${k}">${k}<span class="n">${kc[k]||0}</span></span>`).join('');
 $('issueRows').innerHTML=rows.map(issueRow).join('')||'<tr><td colspan="6" class="empty">no issues</td></tr>'}
$('issueChips').onclick=e=>{const k=e.target.closest('.chip')?.dataset.k;if(k!=null){issueF=k;renderIssues()}};

/* ---- server ---- */
function renderServer(){const s=server;if(!s){$('srvStats').innerHTML=stat('Server','…','loading');return}const w=s.who;
 $('srvStats').innerHTML=stat('Uptime',s.uptime!=null?ago(s.uptime):'–',s.log_age!=null?'log written '+ago(s.log_age)+' ago':'no core3.log')+
  stat('Online',w?w.clients:'–',w?`${w.bots} bots · ${w.players.length} players`:'who.json unreadable')+
  stat('Player list',w?ago(w.age)+' old':'–',w?esc(w.stamp.slice(11,19)):'')+stat('Error kinds',s.errors.length,'in the last 768 KB of the log');
 $('srvErrors').innerHTML=s.errors.map(e=>`<tr><td class="n" style="text-align:left">${esc(e.last.slice(11,19))}</td><td><span class="tag ${e.level==='WARNING'?'warn':'bad'}">${esc(e.level)}</span></td>
  <td class="small">${esc(e.where)}</td><td class="mono" style="font-size:12px;overflow-wrap:anywhere">${esc(e.msg)}</td><td class="n">×${e.count}</td></tr>`).join('')||'<tr><td colspan="5" class="empty">no error lines</td></tr>';
 $('srvWho').innerHTML=w?kv([['Players',esc(w.players.join(', ')||'none')],['Bots',w.bots],...Object.entries(w.planets).map(([z,n])=>[esc(z),n])]):'<div class="empty">who.json unreadable</div>';
 $('srvLogs').innerHTML=s.logs.map(l=>`<tr><td class="mono">${esc(l.name)}</td><td class="n">${num(l.kb)} KB</td><td class="n">${ago(l.age)} ago</td></tr>`).join('')}

/* ---- wiring ---- */
document.addEventListener('click',e=>{const tr=e.target.closest('tr[data-b]');if(tr){openBot(tr.dataset.b);return}
 const st=e.target.closest('[data-st]');if(st){stateF=st.dataset.st;renderBots();return}const pf=e.target.closest('[data-pf]');if(pf){profF=pf.dataset.pf;renderBots();return}
 const th=e.target.closest('th[data-s]');if(th){botSort=th.dataset.s;renderBots()}});
$('seg').onclick=e=>{const o=e.target.dataset.o;if(o){online=o;renderBots()}};
$('q').oninput=()=>{stateF='';renderBots()};
$('find').addEventListener('keydown',e=>{if(e.key==='Enter'){$('q').value=$('find').value;$('find').value='';location.hash='#bots';$('find').blur();
 const hit=data&&data.bots.filter(b=>matches(b,parseQuery($('q').value)));if(hit&&hit.length===1)openBot(hit[0].name)}});
$('refresh').onclick=()=>{poll();if(page==='activity')loadFeed();if(page==='server')loadServer();if(picked)loadDetail()};
addEventListener('resize',()=>{if(page==='map')draw()});
route();poll();setInterval(poll,1500);setInterval(()=>{if(page==='activity')loadFeed();if(page==='server')loadServer();if(picked&&detailTab!=='overview')loadDetail()},5000);
</script></body></html>
'''


# Floor plan of a building interior (owner, 15 Oct: "try and find a way to actually track them and map the navmesh"):
# the cells' floor meshes from tools/navmap.py (pale: where a body can stand; dark lines: walls, Core3's uncrossable
# edges; orange: blocking edges), the bots inside at their cell-local spots with labels and trails, the escorted
# player, and an X wherever a bot reported itself stuck.
FLOOR_PAGE = r'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Floor Plans</title>
<style>
:root{--bg:#f6f5f2;--panel:#ffffff;--ink:#1d1d1b;--muted:#6b6a65;--line:#e2e0da;--floor:#e9eef6;--floor2:#f3f2ee;
--wall:#3a3a36;--block:#d9822b;--you:#c98a00;--stuck:#d1495b;--accent:#2f6fde}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#141413;--panel:#1d1d1b;--ink:#ecebe6;--muted:#9c9a92;
--line:#2e2d2a;--floor:#22303f;--floor2:#1f1f1d;--wall:#cfcdc5;--block:#f0a050;--you:#f2b632;--stuck:#ff6b7d;--accent:#6c9cff}}
:root[data-theme="dark"]{--bg:#141413;--panel:#1d1d1b;--ink:#ecebe6;--muted:#9c9a92;--line:#2e2d2a;--floor:#22303f;
--floor2:#1f1f1d;--wall:#cfcdc5;--block:#f0a050;--you:#f2b632;--stuck:#ff6b7d;--accent:#6c9cff}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:14px/1.4 system-ui,-apple-system,"Segoe UI",sans-serif}
header{display:flex;flex-wrap:wrap;gap:8px 16px;align-items:center;padding:10px 16px;border-bottom:1px solid var(--line)}
h1{font-size:16px;margin:0;font-weight:600}#status{color:var(--muted);font-size:13px}
.bar{display:flex;flex-wrap:wrap;gap:6px}.bar button,.tool{border:1px solid var(--line);background:var(--panel);color:var(--ink);
border-radius:6px;padding:4px 10px;font:inherit;cursor:pointer;text-decoration:none}.bar button.on{border-color:var(--accent);color:var(--accent);font-weight:600}
main{display:grid;grid-template-columns:minmax(0,1fr) 320px;gap:12px;padding:12px 16px}@media (max-width:860px){main{grid-template-columns:1fr}}
#wrap{position:relative;background:var(--panel);border:1px solid var(--line);border-radius:8px;overflow:hidden;aspect-ratio:1/1;max-height:82vh}
canvas{width:100%;height:100%;display:block;cursor:grab;touch-action:none}
#tip{position:absolute;pointer-events:none;background:var(--panel);border:1px solid var(--line);border-radius:6px;padding:4px 8px;font-size:12px;display:none;white-space:nowrap}
aside{display:flex;flex-direction:column;gap:12px;min-width:0}section{background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:10px 12px}
h2{font-size:13px;margin:0 0 6px;color:var(--muted);font-weight:600;text-transform:uppercase;letter-spacing:.04em}
table{width:100%;border-collapse:collapse;font-size:13px}td{padding:3px 4px;border-top:1px solid var(--line);vertical-align:top}
.small{font-size:12px;color:var(--muted)}.dot{display:inline-block;width:9px;height:9px;border-radius:50%;margin-right:6px;vertical-align:middle}
</style></head><body>
<header><h1>Floor plans</h1><div class="bar" id="maps"></div><div class="bar" id="levels"></div><div id="status">loading…</div>
<a class="tool" href="/#map">World map</a></header>
<main><div id="wrap"><canvas id="map"></canvas><div id="tip"></div></div>
<aside><section><h2>Inside</h2><table><tbody id="inside"></tbody></table></section>
<section><h2>Stuck spots</h2><table><tbody id="stuck"></tbody></table>
<div class="small" style="margin-top:6px">Pale: the floor mesh Core3 paths over. Dark lines: walls (uncrossable edges). Orange: blocking edges. X: a bot said it was stuck there. Trails are kept while this page is open.</div></section></aside></main>
<script>
const COLORS={Aurek:'#d1495b',Besh:'#2f9e44',Cresh:'#2f6fde',Dorn:'#8e5bd6',Esk:'#e07b00',Forn:'#c2185b',Kael:'#0ca5a5'};
const cv=document.getElementById('map'),ctx=cv.getContext('2d'),tip=document.getElementById('tip');
let maps=[],plan=null,planName=null,cellInfo={},data=null,view=null,drag=null,hits=[],level='all',trails={},stuck=[],autoPicked=false;
function css(n){return getComputedStyle(document.documentElement).getPropertyValue(n).trim()}
function esc(t){return String(t).replace(/[&<>"]/g,ch=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[ch]))}
function lvl(h){return h==null?null:Math.round(h/4)*4}
function inside(){if(!data||!plan)return[];const out=[];data.chars.forEach(c=>{if(c.cell&&cellInfo[c.cell])out.push(c)});
 (data.escorted||[]).forEach(p=>{if(cellInfo[p.cell])out.push({name:p.name,kind:'player',cell:p.cell,lx:p.lx,ly:p.ly,lz:p.lz,doing:'',group:''})});return out}
function shown(cell){return level==='all'||lvl(cell.height)===level}
function fit(){if(!plan)return;let x0=1e9,x1=-1e9,y0=1e9,y1=-1e9;plan.cells.filter(shown).forEach(c=>c.tris.forEach(t=>t.forEach(p=>{
 x0=Math.min(x0,p[0]);x1=Math.max(x1,p[0]);y0=Math.min(y0,p[1]);y1=Math.max(y1,p[1])})));if(x0>x1){view={cx:0,cy:0,span:100};return}
 view={cx:(x0+x1)/2,cy:(y0+y1)/2,span:Math.max(20,Math.max(x1-x0,y1-y0)*1.1)}}
function toS(x,y){const s=cv.width/view.span;return[(x-view.cx)*s+cv.width/2,(view.cy-y)*s+cv.height/2]}
function toW(px,py){const s=cv.width/view.span;return[(px-cv.width/2)/s+view.cx,view.cy-(py-cv.height/2)/s]}
function draw(){const r=cv.getBoundingClientRect(),d=devicePixelRatio||1;cv.width=r.width*d;cv.height=r.height*d;ctx.clearRect(0,0,cv.width,cv.height);
 if(!plan||!view)return;hits=[];const s=cv.width/view.span;
 plan.cells.forEach(c=>{const on=shown(c);ctx.fillStyle=on?css('--floor'):css('--floor2');ctx.globalAlpha=on?1:.35;
  c.tris.forEach(t=>{ctx.beginPath();t.forEach((p,i)=>{const[x,y]=toS(p[0],p[1]);i?ctx.lineTo(x,y):ctx.moveTo(x,y)});ctx.closePath();ctx.fill()})});
 ctx.globalAlpha=1;plan.cells.filter(shown).forEach(c=>{[['walls','--wall',1.4],['blocks','--block',1.6]].forEach(([k,col,w])=>{
  ctx.strokeStyle=css(col);ctx.lineWidth=w*d;ctx.beginPath();c[k].forEach(e=>{const[a,b]=toS(e[0],e[1]),[p,q]=toS(e[2],e[3]);ctx.moveTo(a,b);ctx.lineTo(p,q)});ctx.stroke()})
  if(s*8>40*d&&c.tris.length){let sx=0,sy=0,n=0;c.tris.forEach(t=>t.forEach(p=>{sx+=p[0];sy+=p[1];n++}));const[x,y]=toS(sx/n,sy/n);
   ctx.fillStyle=css('--muted');ctx.font=(10*d)+'px system-ui';ctx.fillText(c.room,x-12*d,y)}});
 Object.entries(trails).forEach(([name,t])=>{const pts=t.filter(p=>cellInfo[p[0]]&&shown(cellInfo[p[0]]));if(pts.length<2)return;
  ctx.strokeStyle=COLORS[t.group]||css('--accent');ctx.globalAlpha=.4;ctx.lineWidth=2*d;ctx.beginPath();
  pts.forEach((p,i)=>{const[x,y]=toS(p[1],p[2]);i?ctx.lineTo(x,y):ctx.moveTo(x,y)});ctx.stroke();ctx.globalAlpha=1});
 stuck.forEach(st=>{if(!cellInfo[st.cell]||!shown(cellInfo[st.cell]))return;const[x,y]=toS(st.x,st.y);ctx.strokeStyle=css('--stuck');ctx.lineWidth=2.5*d;
  ctx.beginPath();ctx.moveTo(x-5*d,y-5*d);ctx.lineTo(x+5*d,y+5*d);ctx.moveTo(x+5*d,y-5*d);ctx.lineTo(x-5*d,y+5*d);ctx.stroke();
  hits.push({x,y,label:'stuck: '+st.name+' at '+st.time+' ('+st.room+')'})});
 inside().forEach((c,i)=>{if(c.lx==null)return;const[x,y]=toS(c.lx,c.ly);const col=c.kind==='player'?css('--you'):(COLORS[c.group]||css('--accent'));
  ctx.fillStyle=col;ctx.beginPath();ctx.arc(x,y,(c.kind==='player'?7:5)*d,0,7);ctx.fill();ctx.strokeStyle=css('--panel');ctx.lineWidth=2*d;ctx.stroke();
  const text=c.name+(c.doing?' — '+(c.doing.length>34?c.doing.slice(0,33)+'…':c.doing):'');ctx.font=(c.kind==='player'?'600 ':'')+(12*d)+'px system-ui';
  ctx.lineWidth=3*d;ctx.strokeStyle=css('--panel');ctx.strokeText(text,x+9*d,y+4*d+i%2*12*d);ctx.fillStyle=css('--ink');ctx.fillText(text,x+9*d,y+4*d+i%2*12*d);
  hits.push({x,y,label:c.name+' · '+(cellInfo[c.cell]||{}).room+' · height '+(c.lz!=null?c.lz.toFixed(1):'?')+(c.doing?' · '+c.doing:'')})})}
function sideList(){const rows=inside();document.getElementById('inside').innerHTML=rows.map(c=>`<tr><td><span class="dot" style="background:${c.kind==='player'?css('--you'):(COLORS[c.group]||css('--accent'))}"></span><b>${esc(c.name)}</b>
 <div class="small">${esc((cellInfo[c.cell]||{}).room||'')} · height ${c.lz!=null?c.lz.toFixed(1):'?'}${c.doing?' · '+esc(c.doing):''}</div></td></tr>`).join('')||'<tr><td class="small">nobody inside</td></tr>';
 document.getElementById('stuck').innerHTML=stuck.slice(-12).reverse().map(s=>`<tr><td>${esc(s.name)}<div class="small">${s.time} · ${esc(s.room)} · ${s.x.toFixed(1)}, ${s.y.toFixed(1)}</div></td></tr>`).join('')||'<tr><td class="small">none yet</td></tr>'}
function levels(){if(!plan)return;const hs=[...new Set(plan.cells.filter(c=>c.height!=null).map(c=>lvl(c.height)))].sort((a,b)=>b-a);
 document.getElementById('levels').innerHTML=['all',...hs].map(h=>`<button class="${h===level?'on':''}" data-l="${h}">${h==='all'?'all levels':'level '+h}</button>`).join('')}
async function loadPlan(name){const r=await fetch('navmap/'+name+'.json',{cache:'no-store'});plan=await r.json();planName=name;cellInfo={};
 plan.cells.forEach(c=>{if(c.oid)cellInfo[c.oid]=c});level='all';levels();fit();renderMaps();draw()}
function renderMaps(){document.getElementById('maps').innerHTML=maps.map(m=>`<button class="${m.name===planName?'on':''}" data-m="${m.name}">${esc(m.template.replace('shared_','').replace('.iff',''))} · ${m.planet}</button>`).join('')||'<span class="small">no floor plans yet: python tools/navmap.py build &lt;planet&gt; &lt;building id&gt;</span>'}
async function poll(){try{data=await(await fetch('data.json',{cache:'no-store'})).json()}catch(e){document.getElementById('status').textContent='map server not answering';return}
 if(!autoPicked&&maps.length){const counts=maps.map(m=>data.chars.filter(c=>c.cell&&m.cells.includes(c.cell)).length);const best=counts.indexOf(Math.max(...counts));
  if(counts[best]>0||!plan){autoPicked=counts[best]>0;await loadPlan(maps[best].name)}}
 const now=new Date().toTimeString().slice(0,8);inside().forEach(c=>{if(c.lx==null)return;const t=trails[c.name]||(trails[c.name]=Object.assign([],{group:c.group}));
  const last=t[t.length-1];if(!last||last[0]!==c.cell||Math.hypot(last[1]-c.lx,last[2]-c.ly)>0.3){t.push([c.cell,c.lx,c.ly]);if(t.length>200)t.shift()}
  if(String(c.doing).startsWith('stuck')&&!stuck.some(s=>s.name===c.name&&Math.hypot(s.x-c.lx,s.y-c.ly)<1&&s.cell===c.cell))
   stuck.push({name:c.name,cell:c.cell,x:c.lx,y:c.ly,time:now,room:(cellInfo[c.cell]||{}).room||''})});
 document.getElementById('status').textContent=`${inside().length} inside · ${data.time}`;sideList();draw()}
document.getElementById('maps').onclick=e=>{const n=e.target.dataset.m;if(n){autoPicked=true;loadPlan(n)}};
document.getElementById('levels').onclick=e=>{const l=e.target.dataset.l;if(l!==undefined){level=l==='all'?'all':Number(l);levels();fit();draw()}};
cv.addEventListener('wheel',e=>{e.preventDefault();if(!view)return;const d=devicePixelRatio||1,r=cv.getBoundingClientRect(),[wx,wy]=toW((e.clientX-r.left)*d,(e.clientY-r.top)*d);
 view.span=Math.min(2000,Math.max(5,view.span*(e.deltaY>0?1.25:.8)));const[nx,ny]=toW((e.clientX-r.left)*d,(e.clientY-r.top)*d);view.cx+=wx-nx;view.cy+=wy-ny;draw()},{passive:false});
cv.addEventListener('pointerdown',e=>{if(view){drag={x:e.clientX,y:e.clientY,cx:view.cx,cy:view.cy};cv.setPointerCapture(e.pointerId)}});
cv.addEventListener('pointerup',()=>drag=null);
cv.addEventListener('pointermove',e=>{const d=devicePixelRatio||1,r=cv.getBoundingClientRect();
 if(drag){const s=view.span/cv.width*d;view.cx=drag.cx-(e.clientX-drag.x)*s;view.cy=drag.cy+(e.clientY-drag.y)*s;draw();return}
 const px=(e.clientX-r.left)*d,py=(e.clientY-r.top)*d,h=hits.filter(h=>Math.hypot(h.x-px,h.y-py)<10*d).pop();
 if(h){tip.style.display='block';tip.textContent=h.label;tip.style.left=(e.clientX-r.left+12)+'px';tip.style.top=(e.clientY-r.top+12)+'px'}else tip.style.display='none'});
addEventListener('resize',draw);
(async()=>{try{maps=await(await fetch('navmaps.json',{cache:'no-store'})).json()}catch(e){}renderMaps();await poll();setInterval(poll,1500)})();
</script></body></html>
'''


def main():
    parser = argparse.ArgumentParser(description='Live map of the test galaxy (read-only).')
    parser.add_argument('--port', type=int, default=8765)
    args = parser.parse_args()
    load_roster()
    seed_history()
    threading.Thread(target=record, args=({},), daemon=True).start()
    server = ThreadingHTTPServer(('127.0.0.1', args.port), Handler)
    print(f'live map on http://localhost:{args.port} (who.json: {WHO})', flush=True)
    server.serve_forever()


if __name__ == '__main__':
    main()
