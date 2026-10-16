"""C46's outbound schema: fixed labels, numeric telemetry, no source names or prose."""
import math
import re

ROLES = {'marksman': ('Marksman', '#e8c547'), 'brawler': ('Brawler', '#c79c6e'),
         'scout': ('Scout', '#7fd35b'), 'medic': ('Medic', '#4cc9f0'),
         'entertainer': ('Entertainer', '#f78fb3'), 'artisan': ('Artisan', '#ff8c42'),
         'explorer': ('Explorer', '#ffffff'), 'other': ('Other', '#a78bfa')}
PLANETS = frozenset('tatooine corellia naboo talus rori dantooine dathomir endor lok yavin4 hoth ossus'.split())
# Fixed game geography, never names from who.json, bot rows, logs or player settlements.
CITIES = {
    'tatooine': {'Mos Eisley': (3528, -4804), 'Mos Espa': (-2900, 2100), 'Mos Entha': (1290, 3130),
                 'Bestine': (-1290, -3590), 'Anchorhead': (60, -5330), 'Wayfar': (-5120, -6600)},
    'corellia': {'Coronet': (-150, -4720), 'Tyrena': (-5040, -2340), 'Kor Vella': (-3150, 2800),
                 'Doaba Guerfel': (3340, 5520), 'Bela Vistal': (6800, -5700)},
    'naboo': {'Theed': (-4850, 4160), 'Keren': (1580, 2830), 'Moenia': (4800, -4700),
              'Kaadara': (5200, 6700), 'Deeja Peak': (4700, -1400)},
    'talus': {'Dearic': (450, -3000), 'Nashal': (4350, 5200)},
    'rori': {'Narmle': (-5200, -2300), 'Restuss': (5300, 5600)},
}
STATES = frozenset('walking fighting dead incapacitated resting training idle moving waiting busy'.split())


def number(value, default=None):
    return value if type(value) in (int, float) and math.isfinite(value) and abs(value) < 1e15 else default


def public_filter(data):
    """Allowlist compact server-bot rows; generated labels replace *all* source names.

    Never copy chars, bots (squad roster), activities, issues, places or arbitrary text.
    The renderer consumes this projected object directly.
    """
    bots = []
    for i, row in enumerate(data.get('pop', [])):
        if not isinstance(row, list) or len(row) < 11 or row[3] not in PLANETS:
            continue
        bots.append({'label': f'Bot {i + 1}', 'planet': row[3],
                     'role': row[2] if row[2] in ROLES else 'other',
                     'x': number(row[4]), 'y': number(row[5]),
                     'state': row[6] if row[6] in STATES else 'idle',
                     'level': number(row[7], 1), 'boxes': number(row[8], 0),
                     'kills': number(row[9], 0), 'deaths': number(row[10], 0)})
    server = data.get('pop_server', {})
    feed = data.get('feed', {})
    # These keys contain numbers only, with no arbitrary telemetry fields forwarded.
    stats = {k: number(server.get(k)) for k in ('online', 'tick_ms_avg', 'tick_ms_max', 'rss_mb')}
    stats['online'] = stats['online'] if stats['online'] is not None else len(bots)
    stats.update({k: number(feed.get(k)) for k in ('missions_done', 'run_id', 'kills', 'deaths', 'boxes')})
    for k in ('kills', 'deaths', 'boxes'):
        if stats[k] is None:
            stats[k] = sum(b[k] for b in bots)
    stats['server_up'] = feed.get('server_up') if type(feed.get('server_up')) is bool else None
    stats['run_active'] = feed.get('run_active') if type(feed.get('run_active')) is bool else None
    if stats['server_up'] is False or stats['run_active'] is False:
        stats['online'] = 0
    if stats['server_up'] is False:
        bots = []
    return {'bots': bots, 'stats': stats, 'roles': ROLES,
            'cities': {p: CITIES.get(p, {}) for p in sorted({b['planet'] for b in bots})}}


def public_link(value):
    """Only a bare HTTPS quick-tunnel URL is permitted; no query, path or credentials."""
    value = value.strip()
    return value if re.fullmatch(r'https://[a-z0-9]+(?:-[a-z0-9]+)*\.trycloudflare\.com', value) else ''
