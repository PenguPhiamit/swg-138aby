"""Shared helpers for the Ossus o7 build data (Claude, 16 Oct 2026): paths, the terrain evaluator (Core3 port), template
facts from the owner's client archives (read-only, in memory), the census, geometry. Our own code. Windows Python:
    C:/Users/Pengw/miniconda3/python.exe -I <script>
"""
import csv
import json
import math
import os
import re
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
O7 = os.path.normpath(os.path.join(HERE, '..'))
OSSUS = os.path.normpath(os.path.join(O7, '..'))
OUTPUTS = os.path.normpath(os.path.join(OSSUS, '..'))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(OSSUS, 'tools'))
sys.path.insert(0, os.path.join(OUTPUTS, 'tools'))
sys.path.insert(0, os.path.join(OUTPUTS, 'Fable-planet-test', 'tools'))

CENSUS_CSV = os.path.join(OUTPUTS, 'Bot-reports', 'launch-sim', 'ossus-census.csv')
CENSUS_MD = os.path.join(OUTPUTS, 'Bot-reports', 'launch-sim', 'ossus-census.md')
STAGED_TRN = os.path.join(OSSUS, 'staged', 'client', 'terrain', 'ossus.trn')
STAGED_CLIENT = os.path.join(OSSUS, 'staged', 'client')
EXISTING_WS = os.path.join(OSSUS, 'o2', 'staged', 'client', 'snapshot', 'ossus.ws')

KNOSSA = (0.0, -3600.0)
WATER = 38.5
# the no-build circles in o2's ossus_regions.lua (x, y, radius, name); the four edge strips are listed separately
NOBUILD = [(0.0, -3600.0, 320.0, 'Knossa (city r 200 inside)'),
           (2016.0, 2848.0, 260.0, 'Academy ruins'),
           (-2976.0, -4960.0, 120.0, 'west foothill cave'),
           (4896.0, -4960.0, 120.0, 'east foothill cave'),
           (1376.0, 5920.0, 120.0, 'north cave')]
EDGE_STRIPS = 360.0   # the four edge strips are 360 m wide (8000 - 7640)


def dist(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


def bearing(frm, to):
    """Compass heading in degrees (0 north, 90 east) from one point to another."""
    return math.degrees(math.atan2(to[0] - frm[0], to[1] - frm[1])) % 360.0


def rot(lx, lz, yaw):
    """Building-space (x right, z forward) to a world offset (east, north) for a yaw (o2 stage_snapshot.local_to_world)."""
    h = math.radians(yaw)
    return lx * math.cos(h) + lz * math.sin(h), -lx * math.sin(h) + lz * math.cos(h)


# ---------------------------------------------------------------- terrain

class Terrain:
    """Height queries on a built ossus.trn through Fable's Core3 port (roads included)."""

    def __init__(self, trn_path=STAGED_TRN, tga_dir=STAGED_CLIENT):
        import ossus_terrain as ot
        self.ot = ot
        data = open(trn_path, 'rb').read()
        bitmaps = {}
        for name in (ot.BENCH['tga'], ot.CANYON['tga'], ot.CANYON['mesa_tga']):
            bitmaps[name] = open(os.path.join(tga_dir, name.replace('/', os.sep)), 'rb').read()
        self.trn, self.ev = ot.make_evaluator(data, bitmaps)
        self.water = self.trn['header']['global_water_height']
        self._cache = {}

    def h(self, x, y):
        k = (round(x, 2), round(y, 2))
        v = self._cache.get(k)
        if v is None:
            v = self._cache[k] = self.ev.height(x, y)
        return v

    def disc(self, x, y, r, step=5.0):
        pts = []
        v = -r
        while v <= r + 1e-6:
            w = -r
            while w <= r + 1e-6:
                if v * v + w * w <= r * r:
                    pts.append((x + v, y + w))
                w += step
            v += step
        return pts

    def relief(self, x, y, r, step=5.0):
        """(min, max, spread) of the ground over a disc."""
        hs = [self.h(px, py) for px, py in self.disc(x, y, r, step)]
        return min(hs), max(hs), max(hs) - min(hs)

    def max_slope_deg(self, x, y, r, step=5.0):
        """Steepest slope between neighbouring samples (step apart on both axes) over a disc, degrees."""
        best = 0.0
        for px, py in self.disc(x, y, r, step):
            h0 = self.h(px, py)
            for dx, dy in ((step, 0.0), (0.0, step)):
                if (px + dx - x) ** 2 + (py + dy - y) ** 2 <= r * r:
                    best = max(best, abs(self.h(px + dx, py + dy) - h0) / step)
        return math.degrees(math.atan(best))


# ---------------------------------------------------------------- census

class Census:
    def __init__(self):
        self.rows = []
        with open(CENSUS_CSV, newline='') as f:
            for r in csv.DictReader(f):
                self.rows.append({'kind': r['kind'], 'name': r['name'], 'lvl': r['lvl'], 'x': int(r['x']), 'y': int(r['y']), 'z': int(r['z'])})
        self.samples = [r for r in self.rows if r['name'] == 'helper_r2_unit' or r['kind'] != 'creature' or True]
        self.fauna = [r for r in self.rows if r['kind'] == 'creature' and r['name'] not in ('helper_r2_unit', 'Transport Shuttle')]
        self.props = [r for r in self.rows if r['kind'] == 'static']
        self.flat = []
        for line in open(CENSUS_MD, encoding='utf-8'):
            m = re.match(r'\|\s*(-?\d+)/(-?\d+)\s*\|\s*(\d+)\s*\|\s*([\d.]+)\s*\|\s*(\d+)\s*\|', line)
            if m:
                self.flat.append({'x': int(m.group(1)), 'y': int(m.group(2)), 'z': int(m.group(3)), 'range': float(m.group(4)), 'samples': int(m.group(5))})

    def nearest_sample(self, x, y):
        """The census row (any kind, all carry a ground z; z is truncated to whole metres by the census tool) nearest (x, y)."""
        best, bd = None, 1e18
        for r in self.rows:
            d = (r['x'] - x) ** 2 + (r['y'] - y) ** 2
            if d < bd:
                best, bd = r, d
        return best, math.sqrt(bd)

    def around(self, x, y, radius, rows):
        return [(math.hypot(r['x'] - x, r['y'] - y), r) for r in rows if math.hypot(r['x'] - x, r['y'] - y) <= radius]


# ---------------------------------------------------------------- client template facts

_idx = None
_stock = None
_merged = None


def client_idx():
    global _idx
    if _idx is None:
        from swgfmt import trn_iff
        _idx = trn_iff.client_index()
    return _idx


def crc_tables():
    """(stock names, merged names): the object template CRC string table of the winning stock copy and of the installed
    local_planets.tre (stock + MTG + Hoth)."""
    global _stock, _merged
    if _stock is None:
        from swgfmt import trn_iff, swg_tables as st
        _stock = set(n for _, n in st.read_cstb(trn_iff.client_file('misc/object_template_crc_string_table.iff'))['entries'])
        _merged = set(n for _, n in st.read_cstb(trn_iff.open_tre_entry(os.path.join(trn_iff.CLIENT, 'local_planets.tre'),
                                                                        'misc/object_template_crc_string_table.iff'))['entries'])
    return _stock, _merged


def _extents(appearance, depth=0):
    from swgfmt.trn_iff import client_file, parse
    d = client_file(appearance)
    if d is None or depth > 4:
        return None
    try:
        root = parse(d)[0]
    except Exception:
        return None
    if root.form == 'APT ':
        inner = re.findall(rb'appearance/[A-Za-z0-9_/\.]+', d)
        return _extents(inner[0].decode(), depth + 1) if inner else None

    def find(nodes, tag):
        for n in nodes:
            if n.is_form and n.form == tag:
                return n
        return None
    try:
        appr = find(root.children[0].children, 'APPR')
        exbx = find(appr.children[0].children, 'EXBX') if appr else None
        if exbx is None:
            for inner in re.findall(rb'appearance/[A-Za-z0-9_/\.]+\.(?:msh|lod|mgn|cmp)', d):
                e = _extents(inner.decode(), depth + 1)
                if e:
                    return e
            return None
        box = [c for c in exbx.children[0].children if not c.is_form and c.tag == 'BOX '][0]
        f = struct.unpack('<6f', box.data)
        return {'max': [round(v, 2) for v in f[:3]], 'min': [round(v, 2) for v in f[3:]]}
    except Exception:
        return None


def _pob(path):
    """(portals, cells, crc, exterior extents, first portal centre) of a portal layout."""
    from swgfmt.trn_iff import Reader, client_file, parse
    d = client_file(path)
    if d is None:
        return None
    root = parse(d)[0]
    v = root.children[0]
    info = {'portals': 0, 'cells': 0, 'crc': 0, 'exterior': None, 'ext': None, 'entrance': None}
    for c in v.children:
        if not c.is_form and c.tag == 'DATA':
            info['portals'], info['cells'] = struct.unpack('<ii', c.data)
        elif not c.is_form and c.tag == 'CRC ':
            info['crc'] = struct.unpack('<I', c.data)[0]
        elif c.is_form and c.form == 'CELS':
            cv = c.children[0].children[0]
            data = [x for x in cv.children if not x.is_form and x.tag == 'DATA'][0]
            r = Reader(data.data)
            r.i32(); r.u8(); r.cstr()
            info['exterior'] = r.cstr()
            info['ext'] = _extents(info['exterior'])
        elif c.is_form and c.form == 'PRTS' and c.children and info['entrance'] is None:
            p = c.children[0]
            n = struct.unpack('<i', p.data[:4])[0]
            f = struct.unpack('<%df' % (3 * n), p.data[4:4 + 12 * n])
            vs = [(f[3 * i], f[3 * i + 1], f[3 * i + 2]) for i in range(n)]
            info['entrance'] = {'x': round(sum(v[0] for v in vs) / n, 2), 'z': round(sum(v[2] for v in vs) / n, 2),
                                'floor_y': round(min(v[1] for v in vs), 2), 'top_y': round(max(v[1] for v in vs), 2)}
    return info


_tcache = {}


def tinfo(template):
    """Facts about a client object template: table membership, client file, appearances present, extents, portal layout."""
    if template in _tcache:
        return _tcache[template]
    from swgfmt.trn_iff import client_file
    stock, merged = crc_tables()
    idx = client_idx()
    out = {'template': template, 'in_stock_table': template in stock, 'in_merged_table': template in merged,
           'client_file': template.lower() in idx, 'appearances': [], 'missing_appearances': [], 'ext': None, 'pob': None}
    d = client_file(template)
    if d is not None:
        apps = sorted(set(a.decode() for a in re.findall(rb'appearance/[A-Za-z0-9_/\.]+\.(?:apt|lod|msh|mgn|pob|sat|cmp|flr|iff)', d)))
        out['appearances'] = apps
        out['missing_appearances'] = [a for a in apps if a.lower() not in idx]
        for a in apps:
            if a.endswith('.pob'):
                out['pob'] = a
                p = _pob(a)
                if p:
                    out['pob_info'] = p
                    out['ext'] = p['ext']
            elif out['ext'] is None:
                out['ext'] = _extents(a)
    _tcache[template] = out
    return out


def size_xz(template):
    """Footprint box in object space: (minx, maxx, minz, maxz); 1 m square if the client gives none."""
    e = tinfo(template)['ext']
    if not e:
        return (-0.5, 0.5, -0.5, 0.5)
    return (e['min'][0], e['max'][0], e['min'][2], e['max'][2])


# ---------------------------------------------------------------- footprints and overlap

CAVE_SOLID_Z = 18.0     # a flatland cave's mouth is at z = 18 in building space; the box beyond it is the open apron


def solid_box(template):
    """Footprint box used for overlap tests: the whole exterior box, except that the open apron in front of a flatland
    cave's mouth (z beyond the entrance) is left free for props."""
    x0, x1, z0, z1 = size_xz(template)
    if 'flatland' in template:
        z1 = min(z1, CAVE_SOLID_Z)
    return x0, x1, z0, z1


def obb(template, x, y, yaw, pad=0.0):
    """World polygon (east, north) of a template's footprint box at (x, y) with a yaw."""
    x0, x1, z0, z1 = solid_box(template)
    pts = []
    for lx, lz in ((x0 - pad, z0 - pad), (x1 + pad, z0 - pad), (x1 + pad, z1 + pad), (x0 - pad, z1 + pad)):
        dx, dy = rot(lx, lz, yaw)
        pts.append((x + dx, y + dy))
    return pts


def poly_overlap(a, b):
    """Separating-axis test for two convex polygons."""
    for poly in (a, b):
        for i in range(len(poly)):
            x1, y1 = poly[i]
            x2, y2 = poly[(i + 1) % len(poly)]
            ax, ay = -(y2 - y1), x2 - x1
            pa = [ax * px + ay * py for px, py in a]
            pb = [ax * px + ay * py for px, py in b]
            if max(pa) < min(pb) or max(pb) < min(pa):
                return False
    return True


def circle_poly_overlap(cx, cy, r, poly):
    for i in range(len(poly)):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % len(poly)]
        vx, vy = x2 - x1, y2 - y1
        den = vx * vx + vy * vy
        t = 0.0 if den == 0 else max(0.0, min(1.0, ((cx - x1) * vx + (cy - y1) * vy) / den))
        if math.hypot(cx - (x1 + t * vx), cy - (y1 + t * vy)) <= r:
            return True
    # centre inside the polygon
    inside = False
    for i in range(len(poly)):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % len(poly)]
        if (y1 > cy) != (y2 > cy) and cx < (x2 - x1) * (cy - y1) / (y2 - y1) + x1:
            inside = not inside
    return inside


def jload(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def jsave(path, obj):
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(obj, f, indent=1, ensure_ascii=False)
        f.write('\n')
