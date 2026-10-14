"""Hoth terrain scan: server-side heights on a grid around the outpost (Claude, 14 Oct 2026; owner: "are you able to
anylze the terrain somehow? find a spot?").

    squad.py run /mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/tools/hoth/hoth_terrain_scan.py

Read-only: Esk (on Hoth, any posture) asks the server's agent helper for the terrain height at each grid point
(the `height` request, answered from the server's own copy of hoth.trn). Writes tools/hoth/data/hoth_heights.json;
tools/hoth/hoth_terrain_analyse.py turns it into slope maps and candidate spots.
"""
import json, time
from pathlib import Path

GROUP = 'Esk'
PAD = (20.3, -1982.2)
OUT = Path(__file__).resolve().parent / 'data' / 'hoth_heights.json'
BUDGET_S = 900          # stop sampling after 15 minutes
RINGS = [(1500, 50), (4000, 125)]  # (half-width m, step m): fine near the outpost, coarse further out


def run(g):
    esk = g['Esk']
    if not g.check('Esk is on Hoth', esk.status().get('planet') == 'hoth', esk.status().get('planet')):
        return
    t0 = time.time()
    for _ in range(5):
        esk.request('height', 10, x=PAD[0], y=PAD[1])
    per = (time.time() - t0) / 5
    g.note(f'{per * 1000:.0f} ms per height query')
    points, seen = [], set()
    start = time.time()
    for half, step in RINGS:
        n = int(half // step)
        for i in range(-n, n + 1):
            for j in range(-n, n + 1):
                x, y = round(PAD[0] + i * step), round(PAD[1] + j * step)
                if (x, y) in seen or not (-8000 <= x <= 8000 and -8000 <= y <= 8000):
                    continue
                seen.add((x, y))
                if time.time() - start > BUDGET_S:
                    break
                r = esk.request('height', 10, x=x, y=y)
                if r.get('ok') and r.get('z') is not None:
                    points.append((x, y, round(r['z'], 2)))
        g.note(f'ring {half} m / {step} m done: {len(points)} points, {time.time() - start:.0f} s')
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({'planet': 'hoth', 'pad': PAD, 'rings': RINGS, 'points': points}))
    g.check('heights sampled', len(points) > 1000, f'{len(points)} points -> {OUT.name}')
