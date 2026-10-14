"""Esk: map a city's terminals. The three bots split a grid over the town, walk it, and record every terminal
they see (mission, bank, bazaar, travel, ...) in tools/bots/places.json, which other scenarios read.
City objects come from the world snapshot, not scripts, so walking is the only way to find them."""
import json
from pathlib import Path

GROUP = 'Esk'
CITY = 'mos_eisley'
AREA = (3200, -5100, 3900, -4500)  # x0, y0, x1, y1 (the town centre has no mission terminal)
STEP = 120
PLACES = Path(__file__).resolve().parents[1] / 'places.json'


def run(g):
    x0, y0, x1, y1 = AREA
    points = [(x, y) for y in range(y0, y1 + 1, STEP) for x in range(x0, x1 + 1, STEP)]
    found = {}

    def sweep(bot, share):
        for x, y in share:
            trip = bot.walk(x, y, tries=2)
            if not trip.get('arrived') and 'could not reach' not in str(trip.get('error', '')):
                continue
            for obj in bot.look(radius=80, type='TANO', limit=400):
                name = str(obj.get('name', ''))
                if 'terminal' in name or 'collector' in name:
                    found[f"{name}@{obj['x']:.0f},{obj['y']:.0f}"] = {'name': name, 'x': round(obj['x'], 1), 'y': round(obj['y'], 1)}

    g.parallel(*[lambda b=b, i=i: sweep(b, points[i::3]) for i, b in enumerate(g.bots)])
    try:
        places = json.loads(PLACES.read_text(encoding='utf-8'))
    except (OSError, ValueError):
        places = {}
    kinds = {}
    for items in places.get(CITY, {}).get('terminals', {}).values():  # keep what earlier runs found
        for item in items:
            found.setdefault(f"{item['name']}@{item['x']:.0f},{item['y']:.0f}", item)
    for item in found.values():
        kind = item['name'].split(':')[-1]
        kinds.setdefault(kind, []).append(item)
    places[CITY] = {'area': AREA, 'terminals': kinds}
    PLACES.write_text(json.dumps(places, indent=1), encoding='utf-8')
    g.check(f'terminals mapped in {CITY}', found, {k: len(v) for k, v in kinds.items()})
    missions = [t for k, v in kinds.items() if 'mission' in k for t in v]
    g.check('mission terminals found', missions, missions[:4])
