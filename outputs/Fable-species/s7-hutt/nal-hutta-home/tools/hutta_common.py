"""Shared helpers for PL-04, Nal Hutta as the Hutt home (Claude, 17 Oct 2026). Our own code.

Reads the client's Bilbousa snapshot (snapshot/hutta.ws, Darklight's layout in MTG 022) and terrain (terrain/hutta.trn,
MTG's mtg_planets.tre) read-only, in memory, and reuses the Ossus O7 footprint helpers (Fable-ossus/o7-build/tools).
Windows Python: C:/Users/Pengw/miniconda3/python.exe -I <script>
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
HOME = os.path.normpath(os.path.join(HERE, '..'))
S7 = os.path.normpath(os.path.join(HOME, '..'))
OUTPUTS = os.path.normpath(os.path.join(S7, '..', '..'))
H = os.path.dirname(OUTPUTS)
sys.path.insert(0, os.path.join(OUTPUTS, 'tools'))
sys.path.insert(0, os.path.join(OUTPUTS, 'Fable-planet-test', 'tools'))
sys.path.insert(0, os.path.join(OUTPUTS, 'Fable-ossus', 'o7-build', 'tools'))
from o7_common import obb, poly_overlap, circle_poly_overlap, tinfo, size_xz, jload, jsave, rot, client_idx, crc_tables  # noqa: E402,F401

WATER = 75.0
TOWN_CENTRE = (-747.0, 1556.0)       # the city region's centre (hutta_regions.lua)


def ws_nodes():
    from swgfmt import trn_iff, ws_read
    return ws_read.read_ws(trn_iff.client_file('snapshot/hutta.ws'))


def yaw_of(q):
    w, _x, y, _z = q
    return math.degrees(2 * math.atan2(y, w))


def existing_footprints(pad=0.0):
    """(id, template, x, y, yaw, polygon) for every world-level node of the base snapshot."""
    nodes, _ = ws_nodes()
    out = []
    for n in nodes:
        if n['depth'] != 0:
            continue
        yaw = yaw_of(n['quat'])
        out.append((n['id'], n['template'], n['x'], n['y'], yaw, obb(n['template'], n['x'], n['y'], yaw, pad)))
    return out


class Terrain:
    """Ground heights from hutta.trn through Fable's Core3 port (Fable-planet-test/tools/trn_read.py).

    Five BREC boundaries in this file are version 0004, which Core3 does not read (it logs an error and reads no
    fields); they are dropped here, which is what Core3's server does with them. The client may differ there."""

    def __init__(self):
        import trn_read
        from swgfmt import trn_iff
        trn = trn_read.read_trn(trn_iff.client_file('terrain/hutta.trn'))

        def fix(layers):
            for layer in layers:
                layer['boundaries'] = [b for b in layer.get('boundaries', []) if 'enabled' in b]
                fix(layer.get('children', []))
        fix(trn['layers'])
        self.ev = trn_read.HeightEvaluator(trn, trn_read.client_bitmap_loader)
        self._cache = {}

    def h(self, x, y):
        k = (round(x, 1), round(y, 1))
        if k not in self._cache:
            self._cache[k] = self.ev.height(x, y)
        return self._cache[k]

    def disc(self, x, y, r, step=6.0):
        hs = []
        v = -r
        while v <= r + 1e-6:
            w = -r
            while w <= r + 1e-6:
                if v * v + w * w <= r * r:
                    hs.append(self.h(x + v, y + w))
                w += step
            v += step
        return min(hs), max(hs)
