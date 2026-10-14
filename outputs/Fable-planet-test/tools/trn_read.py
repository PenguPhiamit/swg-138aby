"""Read a SWG .trn (procedural terrain, FORM PTAT) the way Core3 reads it, and evaluate heights the way Core3 does.
Our own code (Fable, 14 Oct 2026). The field layouts follow Core3-dev, MMOCoreORB/src/terrain/** (AGPL-3.0,
read as reference); the height evaluation is a Python port of ProceduralTerrainAppearance::getHeight and the
affector/filter/boundary classes, kept only for checking our own files.

    python -I trn_read.py summary <spec>              # header, families, fractals, layer tree
    python -I trn_read.py check <spec>                # strict walk in Core3's order; lists anything Core3 skips
    python -I trn_read.py height <spec> x y [x y ...] # server-style heights (TerrainManager rounds to 0.1 m)

<spec> is a file path, client:<path> (owner's client archives, stock first then MTG) or tre:<archive>:<path>.

How Core3 walks the file (every "next" below means the next child, in file order, exactly like IffStream):
  FORM PTAT > FORM 0013|0014 > DATA header, FORM TGEN, FORM 0000|0001 (the maps; no MAPS wrapper)
  FORM TGEN > FORM 0000 > SGRP, FGRP, RGRP, EGRP, MGRP (fractals), [MGRP (bitmaps)], LYRS | LAYR
  FORM LAYR > FORM 0003 > FORM IHDR, ADTA chunk, then any number of boundary / filter / affector / LAYR forms
  rule forms: FORM <TAG> > FORM <version> > FORM IHDR (> FORM 0001 > DATA) then DATA (or FORM DATA > PARM)
"""
import math
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from trn_iff import Reader, load, parse  # noqa: E402


class ParseError(Exception):
    pass


class Cursor:
    """Walks a FORM's children in order. openForm/openChunk in Core3 always take the NEXT child, so do we."""

    def __init__(self, node, path):
        self.node, self.i, self.path = node, 0, path

    def peek(self):
        return self.node.children[self.i] if self.i < len(self.node.children) else None

    def remaining(self):
        return len(self.node.children) - self.i

    def form(self, ftype=None):
        n = self.peek()
        if n is None or not n.is_form or (ftype is not None and n.form != ftype):
            raise ParseError(f'{self.path}: expected FORM {ftype or "<any>"}, found {n}')
        self.i += 1
        return Cursor(n, f'{self.path}/{n.form}')

    def chunk(self, tag=None):
        n = self.peek()
        if n is None or n.is_form or (tag is not None and n.tag != tag):
            raise ParseError(f'{self.path}: expected chunk {tag or "<any>"}, found {n}')
        self.i += 1
        return Reader(n.data)

    def peek_form_type(self):
        n = self.peek()
        return n.form if (n is not None and n.is_form) else None

    def skip(self):
        self.i += 1


def versioned(cur, accepted, what, notes):
    """Core3: version = getNextFormType(); openForm(version); switch (version) {accepted...; default: print error}."""
    ver = cur.form()
    if ver.node.form not in accepted:
        notes.append(f'{what}: version {ver.node.form} is not one Core3 reads ({", ".join(accepted)}); Core3 logs an error and reads no fields')
        return ver, False
    return ver, True


def read_ihdr(cur, notes):
    ihdr = cur.form('IHDR')
    ver, ok = versioned(ihdr, ('0001',), 'IHDR', notes)
    if not ok:
        return {'enabled': False, 'name': '?'}
    r = ver.chunk('DATA')
    return {'enabled': r.i32() != 0, 'name': r.cstr()}


# ---------------------------------------------------------------- groups

def read_shader_group(cur, notes):
    g = cur.form('SGRP')
    ver, ok = versioned(g, ('0006',), 'SGRP', notes)
    out = []
    if not ok:
        return out
    while ver.remaining():
        r = ver.chunk('SFAM')
        fam = {'id': r.i32(), 'name': r.cstr(), 'file': r.cstr(), 'rgb': (r.u8(), r.u8(), r.u8()),
               'shader_size': r.f32(), 'feather_clamp': r.f32(), 'children': []}
        for _ in range(r.i32()):
            fam['children'].append({'shader': r.cstr(), 'weight': r.f32()})
        out.append(fam)
    return out


def read_flora_group(cur, notes):
    g = cur.form('FGRP')
    ver, ok = versioned(g, ('0008',), 'FGRP', notes)
    out = []
    if not ok:
        return out
    while ver.remaining():
        r = ver.chunk('FFAM')
        fam = {'id': r.i32(), 'name': r.cstr(), 'rgb': (r.u8(), r.u8(), r.u8()), 'density': r.f32(),
               'floats_on_water': r.u32(), 'children': []}
        for _ in range(r.i32()):
            fam['children'].append({'appearance': r.cstr(), 'weight': r.f32(), 'align_to_terrain': r.u32(),
                                    'displacement': r.f32(), 'period': r.f32(), 'sway': r.u32(), 'scale': r.i32(),
                                    'min_scale': r.f32(), 'max_scale': r.f32()})
        out.append(fam)
    return out


def read_radial_group(cur, notes):
    g = cur.form('RGRP')
    ver, ok = versioned(g, ('0003',), 'RGRP', notes)
    out = []
    if not ok:
        return out
    while ver.remaining():
        r = ver.chunk('RFAM')
        fam = {'id': r.i32(), 'name': r.cstr(), 'rgb': (r.u8(), r.u8(), r.u8()), 'density': r.f32(), 'children': []}
        for _ in range(r.i32()):
            fam['children'].append({'shader': r.cstr(), 'weight': r.f32(), 'distance': r.f32(), 'min_width': r.f32(),
                                    'max_width': r.f32(), 'maintain_aspect': r.i32(), 'min_height': r.f32(),
                                    'max_height': r.f32(), 'align_to_terrain': r.i32(), 'var9': r.u32()})
        out.append(fam)
    return out


def read_environment_group(cur, notes):
    g = cur.form('EGRP')
    ver, ok = versioned(g, ('0002',), 'EGRP', notes)
    out = []
    if not ok:
        return out
    while ver.remaining():
        e = ver.form('EFAM')
        r = e.chunk('DATA')
        out.append({'id': r.i32(), 'name': r.cstr(), 'rgb': (r.u8(), r.u8(), r.u8()), 'feather_clamp': r.f32()})
    return out


def read_fractal_group(cur, notes):
    g = cur.form('MGRP')
    ver, ok = versioned(g, ('0000',), 'MGRP(fractals)', notes)
    out = {}
    if not ok:
        return out
    while ver.remaining():
        fam = ver.form('MFAM')
        r = fam.chunk('DATA')
        fid, name = r.i32(), r.cstr()
        mf = fam.form('MFRC')
        v, ok2 = versioned(mf, ('0001',), f'MFRC {name}', notes)
        if not ok2:
            continue
        r = v.chunk('DATA')
        out[fid] = {'id': fid, 'name': name, 'seed': r.i32(), 'bias': r.i32(), 'bias_value': r.f32(), 'gain': r.i32(),
                    'gain_value': r.f32(), 'octaves': r.u32(), 'octaves_param': r.f32(), 'amplitude': r.f32(),
                    'x_freq': r.f32(), 'y_freq': r.f32(), 'x_offset': r.f32(), 'z_offset': r.f32(),
                    'combination': r.u32()}
    return out


def read_bitmap_group(cur, notes):
    g = cur.form('MGRP')
    ver, ok = versioned(g, ('0000',), 'MGRP(bitmaps)', notes)
    out = {}
    if not ok:
        return out
    while ver.remaining():
        fam = ver.form('MFAM')
        r = fam.chunk('DATA')
        fid = r.i32()
        out[fid] = {'id': fid, 'name': r.cstr(), 'file': r.cstr()}
    return out


# ---------------------------------------------------------------- layer rules

SKIPPED_BY_CORE3 = {'ACBM', 'AFBM', 'AHBM', 'AHSM', 'ASBM', 'BALL', 'BSPL'}

BOUNDARY_VERSIONS = {'BCIR': ('0002',), 'BREC': ('0002', '0003'), 'BPOL': ('0005',), 'BPLN': ('0001',)}
FILTER_VERSIONS = {'FHGT': ('0002',), 'FFRA': ('0005',), 'FSLP': ('0002',), 'FDIR': ('0000',), 'FSHD': ('0000',),
                   'FBIT': ('0000',)}
AFFECTOR_VERSIONS = {'AHCN': ('0000',), 'AHFR': ('0003',), 'AHTR': ('0004',), 'ASCN': ('0001',), 'ASRP': ('0001',),
                     'ACCN': ('0000',), 'ACRH': ('0000',), 'ACRF': ('0001',), 'AFSN': ('0004',), 'AFSC': ('0004',),
                     'AFCN': ('0004',), 'AFDN': ('0002',), 'AFDF': ('0002',), 'ARCN': ('0002',), 'AEXC': ('0000',),
                     'APAS': ('0000',), 'AENV': ('0000',), 'AROA': ('0005',), 'ARIV': ('0005',)}


def _points(r):
    return [(r.f32(), r.f32()) for _ in range(r.i32())]


def read_road_data(cur, notes):
    """FORM ROAD|HDTA > FORM 0001 > SGMT chunks (x, z, y floats). Kept raw; Core3 only uses HDTA for heights."""
    kind = cur.peek_form_type()
    f = cur.form(kind)
    ver, ok = versioned(f, ('0001',), kind, notes)
    segments = []
    if ok:
        while ver.remaining():
            r = ver.chunk('SGMT')
            segments.append([(r.f32(), r.f32(), r.f32()) for _ in range(len(r.data) // 12)])
    return kind, segments


def read_rule(cur, notes):
    """Parse the next child of a layer: boundary, filter, affector or child layer. Mirrors Layer::parseFromIffStream."""
    tag = cur.peek_form_type()
    if tag is None:
        n = cur.peek()
        notes.append(f'{cur.path}: chunk {n.tag} where Core3 expects a FORM (it would throw)')
        cur.skip()
        return None
    if tag == 'LAYR':
        return read_layer(cur, notes)
    if tag in SKIPPED_BY_CORE3:
        cur.skip()
        return {'kind': 'skipped', 'type': tag}
    versions = BOUNDARY_VERSIONS.get(tag) or FILTER_VERSIONS.get(tag) or AFFECTOR_VERSIONS.get(tag)
    if versions is None:
        notes.append(f'{cur.path}: unknown rule type {tag}; Core3 prints "Unknown Type" and skips it')
        cur.skip()
        return {'kind': 'unknown', 'type': tag}
    kind = 'boundary' if tag in BOUNDARY_VERSIONS else 'filter' if tag in FILTER_VERSIONS else 'affector'
    f = cur.form(tag)
    ver, ok = versioned(f, versions, tag, notes)
    rule = {'kind': kind, 'type': tag, 'version': ver.node.form}
    if not ok:
        return rule
    rule.update(read_ihdr(ver, notes))
    if tag in ('FFRA', 'FBIT', 'AHFR', 'ACRF'):
        d = ver.form('DATA')
        r = d.chunk('PARM')
    elif tag in ('AROA', 'ARIV'):
        d = ver.form('DATA')
        rule['road_kind'], rule['segments'] = read_road_data(d, notes)
        r = d.chunk('DATA')
    else:
        r = ver.chunk('DATA')
    v = ver.node.form
    if tag == 'BCIR':
        rule.update(cx=r.f32(), cy=r.f32(), radius=r.f32(), feather_type=r.i32(), feather=r.f32())
    elif tag == 'BREC':
        rule.update(x0=r.f32(), y0=r.f32(), x1=r.f32(), y1=r.f32(), feather_type=r.i32(), feather=r.f32())
        if v == '0003':
            rule.update(water=r.i32(), var7=r.i32(), water_height=r.f32(), water_shader_size=r.f32(), water_shader=r.cstr())
    elif tag == 'BPOL':
        rule.update(points=_points(r), feather_type=r.i32(), feather=r.f32(), water=r.i32(), water_height=r.f32(),
                    water_shader_size=r.f32(), water_shader=r.cstr())
    elif tag == 'BPLN':
        rule.update(points=_points(r), feather_type=r.i32(), feather=r.f32(), line_width=r.f32())
    elif tag == 'FHGT':
        rule.update(min=r.f32(), max=r.f32(), feather_type=r.i32(), feather=r.f32())
    elif tag == 'FFRA':
        rule.update(fractal=r.i32(), feather_type=r.i32(), feather=r.f32(), min=r.f32(), max=r.f32(), scale=r.f32())
    elif tag == 'FSLP':
        rule.update(min_angle=r.f32(), max_angle=r.f32(), feather_type=r.i32(), feather=r.f32())
    elif tag == 'FDIR':
        rule.update(min_deg=r.f32(), max_deg=r.f32(), feather_type=r.i32(), feather=r.f32())
    elif tag == 'FSHD':
        rule.update(shader=r.i32())
    elif tag == 'FBIT':
        rule.update(bitmap=r.i32(), feather_type=r.i32(), feather=r.f32(), min=r.f32(), max=r.f32())
    elif tag == 'AHCN':
        rule.update(op=r.i32(), height=r.f32())
    elif tag == 'AHFR':
        rule.update(fractal=r.i32(), op=r.i32(), height=r.f32())
    elif tag == 'AHTR':
        rule.update(flat_ratio=r.f32(), height=r.f32())
    elif tag == 'ASCN':
        rule.update(family=r.i32(), feather_type=r.i32(), feather=r.f32())
    elif tag == 'ASRP':
        rule.update(old_family=r.i32(), new_family=r.i32(), feather_type=r.i32(), feather=r.f32())
    elif tag == 'ACCN':
        rule.update(op=r.i32(), rgb=(r.u8(), r.u8(), r.u8()))
    elif tag == 'ACRH':
        rule.update(op=r.i32(), min=r.f32(), max=r.f32(), ramp=r.cstr())
    elif tag == 'ACRF':
        rule.update(fractal=r.i32(), op=r.u8(), ramp=r.cstr())
    elif tag in ('AFSN', 'AFSC', 'AFCN', 'AFDN', 'AFDF', 'ARCN'):
        rule.update(family=r.i32(), op=r.i32(), remove_all=r.i32(), feather_type=r.i32(), feather=r.f32())
    elif tag == 'AEXC':
        pass
    elif tag == 'APAS':
        rule.update(passable=r.u8(), var2=r.i32())
    elif tag == 'AENV':
        rule.update(environment=r.i32(), var2=r.i32(), feather=r.f32())
    elif tag == 'AROA':
        rule.update(points=_points(r), width=r.f32(), family=r.i32(), feather_type=r.i32(), feather=r.f32(),
                    feather_shader=r.i32(), feather_shader_distance=r.f32())
    elif tag == 'ARIV':
        rule.update(points=_points(r), width=r.f32(), var3=r.i32(), var4=r.i32(), var5=r.i32(), var6=r.f32(),
                    var7=r.f32(), var8=r.f32(), var9=r.i32(), var10=r.f32(), var11=r.f32(), var12=r.f32(), shader=r.cstr())
    if r.remaining:
        notes.append(f'{cur.path}/{tag}: {r.remaining} bytes after the fields Core3 reads')
    return rule


def read_layer(cur, notes):
    f = cur.form('LAYR')
    ver, ok = versioned(f, ('0003',), 'LAYR', notes)
    layer = {'kind': 'layer', 'boundaries': [], 'filters': [], 'affectors': [], 'children': [], 'rules': []}
    if not ok:
        return layer
    layer.update(read_ihdr(ver, notes))
    r = ver.chunk('ADTA')
    layer.update(invert_boundaries=r.u32() != 0, invert_filters=r.u32() != 0, adta_var3=r.u32(), adta_var4=r.cstr())
    while ver.remaining():
        rule = read_rule(ver, notes)
        if rule is None:
            continue
        layer['rules'].append(rule)
        if rule['kind'] == 'layer':
            layer['children'].append(rule)
        elif rule['kind'] in ('boundary', 'filter', 'affector'):
            layer[rule['kind'] if rule['kind'] != 'boundary' else 'boundaries'].append(rule) if rule['kind'] == 'boundary' \
                else layer[rule['kind'] + 's'].append(rule)
    return layer


# ---------------------------------------------------------------- whole file

FLORA_BLOCKS = ('flora_collidable', 'flora_non_collidable', 'radial_near', 'radial_far')


def read_trn(data):
    """Dict with 'version', 'header', 'shaders', 'flora', 'radial', 'environments', 'fractals', 'bitmaps', 'layers',
    'maps' and 'notes' (everything Core3 would complain about or skip)."""
    notes = []
    root = Cursor(parse(data) and _Root(parse(data)), '')
    ptat = root.form('PTAT')
    ver, ok = versioned(ptat, ('0013', '0014'), 'PTAT', notes)
    if not ok:
        raise ParseError('not a terrain version Core3 reads: ' + ver.node.form)
    out = {'version': ver.node.form, 'notes': notes}
    r = ver.chunk('DATA')
    h = {'name': r.cstr(), 'size': r.f32(), 'chunk_size': r.f32(), 'tiles_per_chunk': r.u32(),
         'use_global_water_table': r.u32(), 'global_water_height': r.f32(), 'global_water_shader_size': r.f32(),
         'global_water_shader': r.cstr(), 'time_cycle': r.f32()}
    if out['version'] == '0013':
        h['discarded_0013'] = [r.cstr(), r.cstr(), r.f32(), r.cstr(), r.f32(), r.cstr(), r.f32(), r.cstr(), r.f32(), r.u32(), r.cstr()]
    for block in FLORA_BLOCKS:
        h[block] = {'min_distance': r.f32(), 'max_distance': r.f32(), 'tile_size': r.f32(), 'tile_border': r.f32(),
                    'seed': r.u32()}
    if r.remaining:
        notes.append(f'PTAT DATA: {r.remaining} bytes after the fields Core3 reads')
    out['header'] = h
    tgen = ver.form('TGEN')
    tver, ok = versioned(tgen, ('0000',), 'TGEN', notes)
    if ok:
        out['shaders'] = read_shader_group(tver, notes)
        out['flora'] = read_flora_group(tver, notes)
        out['radial'] = read_radial_group(tver, notes)
        out['environments'] = read_environment_group(tver, notes)
        out['fractals'] = read_fractal_group(tver, notes)
        out['bitmaps'] = read_bitmap_group(tver, notes) if tver.peek_form_type() == 'MGRP' else {}
        if tver.peek_form_type() == 'LAYR':
            out['layers'] = [read_layer(tver, notes)]
        else:
            lyrs = tver.form('LYRS')
            out['layers'] = []
            while lyrs.remaining():
                out['layers'].append(read_layer(lyrs, notes))
    mver, ok = versioned(ver, ('0000', '0001'), 'maps', notes)
    out['maps'] = {'version': mver.node.form}
    if ok and mver.node.form == '0001':
        r = mver.chunk('DATA')
        out['maps'].update(var1=r.f32(), var2=r.f32(), var3=r.i32(), var4=r.i32())
        out['maps']['wmap_bytes'] = len(mver.chunk('WMAP').data)
        out['maps']['smap_bytes'] = len(mver.chunk('SMAP').data)
    if ver.remaining():
        notes.append(f'PTAT/{out["version"]}: {ver.remaining()} extra children after the maps (Core3 ignores them)')
    return out


class _Root:
    """Wraps the top-level record list so the root Cursor can treat it like a form."""

    def __init__(self, children):
        self.children, self.is_form, self.form, self.tag = children, True, '<root>', 'FORM'


# ---------------------------------------------------------------- height evaluation (port of Core3)

class Random:
    """trn/Random.h: Park-Miller minimal standard with a 322-entry shuffle table (Numerical Recipes ran1 style)."""

    def __init__(self, seed):
        self.seed = -seed
        self.unknown = 0
        self.table = [0] * 322

    def _step(self):
        s = self.seed
        s = 16807 * (s % 127773) - 2836 * (s // 127773)  # == 16807*s - 0x7FFFFFFF*(s/127773) in wrapped int32
        if s < 0:
            s += 0x7FFFFFFF
        self.seed = s

    def next(self):
        if self.seed <= 0 or self.unknown == 0:
            v2 = -self.seed
            self.seed = v2 if v2 >= 1 else 1
            for i in range(329, -1, -1):
                self._step()
                if i < 322:
                    self.table[i] = self.seed
            self.unknown = self.table[0]
        self._step()
        idx = int(self.unknown / 6669205.0)
        self.unknown = self.table[idx]
        self.table[idx] = self.seed
        return self.unknown


class PerlinNoise:
    """trn/PerlinNoise.h (Ken Perlin's reference noise, seeded from Random)."""
    B, BM, N = 0x100, 0xff, 0x1000

    def __init__(self, rand):
        B = self.B
        p = list(range(B)) + [0] * (B + 2)
        g1 = [0.0] * (2 * B + 2)
        g2 = [[0.0, 0.0] for _ in range(2 * B + 2)]
        for i in range(B):
            g1[i] = ((rand.next() % (B + B)) - B) / B
            v = [((rand.next() % (B + B)) - B) / B for _ in range(2)]
            s = math.sqrt(v[0] * v[0] + v[1] * v[1])
            g2[i] = [v[0] / s, v[1] / s] if s else v
        i = B - 1
        while i:
            k = p[i]
            j = rand.next() % B
            p[i] = p[j]
            p[j] = k
            i -= 1
        for i in range(B + 2):
            p[B + i] = p[i]
            g1[B + i] = g1[i]
            g2[B + i] = list(g2[i])
        self.p, self.g1, self.g2 = p, g1, g2

    @staticmethod
    def _setup(v):
        t = v + PerlinNoise.N
        it = int(t)  # C cast truncates toward zero
        n = 1 if (t < 0.0 and t != float(it)) else 0
        b0 = (it - n) & PerlinNoise.BM
        b1 = (b0 + 1) & PerlinNoise.BM
        r0 = t - (it - n)
        return b0, b1, r0, r0 - 1.0

    @staticmethod
    def _s(t):
        return t * t * (3.0 - 2.0 * t)

    def noise2(self, x, y):
        bx0, bx1, rx0, rx1 = self._setup(x)
        by0, by1, ry0, ry1 = self._setup(y)
        p, g2 = self.p, self.g2
        i, j = p[bx0], p[bx1]
        b00, b10, b01, b11 = p[i + by0], p[j + by0], p[i + by1], p[j + by1]
        sx, sy = self._s(rx0), self._s(ry0)
        q = g2[b00]; u = rx0 * q[0] + ry0 * q[1]
        q = g2[b10]; v = rx1 * q[0] + ry0 * q[1]
        a = u + sx * (v - u)
        q = g2[b01]; u = rx0 * q[0] + ry1 * q[1]
        q = g2[b11]; v = rx1 * q[0] + ry1 * q[1]
        b = u + sx * (v - u)
        return a + sy * (b - a)


class Fractal:
    """MapFractal: octaves of Perlin noise combined one of five ways, then optional bias and gain."""

    def __init__(self, f):
        self.f = f
        self.noise = PerlinNoise(Random(f['seed']))
        total, amp = 0.0, 1.0
        for _ in range(f['octaves']):
            total += amp
            amp *= f['amplitude']
        self.offset32 = 1.0 / total if total else 0.0

    def get(self, x, y):
        f = self.f
        vx, vy = x * f['x_freq'] + f['x_offset'], y * f['y_freq'] + f['z_offset']
        comb = f['combination']
        freq, amp, acc = 1.0, 1.0, 0.0
        for _ in range(f['octaves']):
            n = self.noise.noise2(vx * freq, vy * freq)
            if comb in (0, 1):
                acc += n * amp
            elif comb == 2:
                acc += (1.0 - abs(n)) * amp
            elif comb == 3:
                acc += abs(n) * amp
            elif comb == 4:
                acc += (1.0 - min(max(n, 0.0), 1.0)) * amp
            elif comb == 5:
                acc += min(max(n, 0.0), 1.0) * amp
            freq *= f['octaves_param']
            amp *= f['amplitude']
        result = (acc * self.offset32 + 1.0) * 0.5 if comb in (0, 1) else acc * self.offset32
        if f['bias']:
            result = math.pow(result, math.log(f['bias_value']) / math.log(0.5)) if result > 0 else 0.0
        if f['gain']:
            if result < 0.001:
                return 0.0
            if result > 0.999:
                return 1.0
            g = math.log(1.0 - f['gain_value']) / math.log(0.5)
            if result < 0.5:
                return math.pow(result * 2, g) * 0.5
            result = 1.0 - math.pow((1.0 - result) * 2, g) * 0.5
        return result


def feathering(value, ftype):
    if ftype == 1:
        return value * value
    if ftype == 2:
        return math.sqrt(value) if value >= 0 else 0.0
    if ftype == 3:
        return value * value * (3 - 2 * value)
    if ftype == 0:
        return value
    return 0.0


def _clamp01(v):
    return 0.0 if v < 0 else 1.0 if v > 1 else v


def boundary_process(b, x, y):
    t = b['type']
    if t == 'BCIR':
        dx, dy = b['cx'] - x, b['cy'] - y
        d2, r2 = dx * dx + dy * dy, b['radius'] * b['radius']
        if d2 > r2:
            return 0.0
        inner = (1.0 - _clamp01(b['feather'])) * b['radius']
        inner2 = inner * inner
        return 1.0 - (d2 - inner2) / (r2 - inner2) if d2 > inner2 else 1.0
    if t == 'BREC':
        x0, x1 = sorted((b['x0'], b['x1']))
        y0, y1 = sorted((b['y0'], b['y1']))
        if x < x0 or x > x1 or y < y0 or y > y1:
            return 0.0
        fa = _clamp01(b['feather'])
        if fa == 0.0:
            return 1.0
        side = min(x1 - x0, y1 - y0)
        v30 = fa * side * 0.5
        if not (x < x1 - v30 or x > x0 + v30 or y < y1 - v30 or y > y0 + v30):
            return 1.0
        v29 = min(v30, x - x0, x1 - x, y - y0, y1 - y)
        return v29 / v30 if v30 else 1.0
    if t == 'BPOL':
        pts = b['points']
        if not pts:
            return 0.0
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        if x < min(xs) or x > max(xs) or y < min(ys) or y > max(ys):
            return 0.0
        inside = False
        last = pts[-1]
        for p in pts:
            if (p[1] <= y < last[1]) or (last[1] <= y < p[1]):
                if (y - p[1]) * (last[0] - p[0]) / (last[1] - p[1]) + p[0] > x:
                    inside = not inside
            last = p
        if not inside:
            return 0.0
        fa = b['feather']
        if fa == 0.0:
            return 1.0
        best = fa * fa
        orig = best
        for p in pts:
            d = (y - p[1]) ** 2 + (x - p[0]) ** 2
            if d < best:
                best = d
        last = pts[-1]
        for p in pts:
            vx, vy = p[0] - last[0], p[1] - last[1]
            denom = vx * vx + vy * vy
            if denom:
                tt = ((x - last[0]) * vx + (y - last[1]) * vy) / denom
                if 0.0 <= tt <= 1.0:
                    d = (x - (vx * tt + last[0])) ** 2 + (y - (vy * tt + last[1])) ** 2
                    if d < best:
                        best = d
            last = p
        return 1.0 if abs(best - orig) <= 0.0001 else math.sqrt(best) / fa
    if t == 'BPLN':
        pts, w = b['points'], b['line_width']
        if not pts:
            return 0.0
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        if x < min(xs) - w or x > max(xs) + w or y < min(ys) - w or y > max(ys) + w:
            return 0.0
        best = w * w
        full = best
        for p in pts:
            d = (y - p[1]) ** 2 + (x - p[0]) ** 2
            if d < best:
                best = d
        for p, q in zip(pts, pts[1:]):
            vx, vy = q[0] - p[0], q[1] - p[1]
            denom = vx * vx + vy * vy
            if denom:
                tt = ((y - p[1]) * vy + (x - p[0]) * vx) / denom
                if 0.0 <= tt <= 1.0:
                    d = (x - (vx * tt + p[0])) ** 2 + (y - (vy * tt + p[1])) ** 2
                    if d < best:
                        best = d
        if best >= full:
            return 0.0
        inner = (1.0 - b['feather']) * w
        return 1.0 - (math.sqrt(best) - inner) / (w - inner) if best >= inner * inner else 1.0
    return 0.0


class HeightEvaluator:
    """Port of ProceduralTerrainAppearance::getHeight / processTerrain (height affectors only)."""

    def __init__(self, trn, bitmap_loader=None):
        self.trn = trn
        self.fractals = {k: Fractal(v) for k, v in trn.get('fractals', {}).items()}
        self.bitmap_loader = bitmap_loader
        self.bitmaps = {}
        self.warnings = []

    def _bitmap(self, bid):
        if bid not in self.bitmaps:
            entry = self.trn.get('bitmaps', {}).get(bid)
            self.bitmaps[bid] = self.bitmap_loader(entry['file']) if (entry and self.bitmap_loader) else None
        return self.bitmaps[bid]

    def filter_process(self, flt, x, y, transform, base, rect):
        t = flt['type']
        if t == 'FHGT':
            lo, hi = flt['min'], flt['max']
            if not (lo < base < hi):
                return 0.0
            v9 = (hi - lo) * flt['feather'] * 0.5
            if lo + v9 <= base:
                return 1.0 if hi - v9 >= base else (hi - base) / v9
            return (base - lo) / v9
        if t == 'FFRA':
            fr = self.fractals.get(flt['fractal'])
            if fr is None:
                self.warnings.append(f'filter {flt["name"]}: fractal {flt["fractal"]} missing (Core3 returns 1)')
                return 1.0
            n = fr.get(x, y) * flt['scale']
            lo, hi = flt['min'], flt['max']
            if not (lo < n < hi):
                return 0.0
            v9 = (hi - lo) * flt['feather'] * 0.5
            if lo + v9 <= n:
                return 1.0 if hi - v9 >= n else (hi - n) / v9
            return (n - lo) / v9
        if t == 'FBIT':
            bm = self._bitmap(flt['bitmap'])
            if bm is None:
                self.warnings.append(f'filter {flt["name"]}: bitmap {flt["bitmap"]} not loaded (Core3 returns 1 if missing)')
                return 1.0
            return bitmap_filter(bm, flt, x, y, rect)
        # FSLP, FDIR and FSHD do not override the virtual process() in Core3, so the base class returns 0.
        return 0.0

    def affector_process(self, a, x, y, transform, base):
        t = a['type']
        if transform == 0:
            return base
        if t == 'AHCN':
            h, op = a['height'], a['op']
            if op == 1:
                return transform * h + base
            if op == 2:
                return base - transform * h
            if op == 3:
                return base + (base * h - base) * transform
            if op == 4:
                return 0.0
            return (1.0 - transform) * base + transform * h
        if t == 'AHFR':
            fr = self.fractals.get(a['fractal'])
            if fr is None:
                self.warnings.append(f'affector {a["name"]}: fractal {a["fractal"]} missing')
                return base
            n = fr.get(x, y) * a['height']
            op = a['op']
            if op == 1:
                return base + n * transform
            if op == 2:
                return base - n * transform
            if op == 3:
                return base + (n * base - base) * transform
            if op == 4:
                return base
            return base + (n - base) * transform
        if t == 'AHTR':
            h = a['height']
            if h <= 0:
                return base
            var1 = math.fmod(base, h)
            if base == 0:
                var1 += h
            var2 = base - var1
            var3 = h * a['flat_ratio'] + var2
            var4 = h + var2
            if base > var3:
                var2 = (base - var3) / (var4 - var3) * (var4 - var2) + var2
            return (var2 - base) * transform + base
        if t == 'AROA':
            self.warnings.append(f'road affector {a["name"]}: road heights not ported; ignored')
        return base

    def process_layer(self, layer, x, y, base, affector_transform):
        transform, has_boundaries = 0.0, False
        rect = [float('inf'), float('-inf'), float('inf'), float('-inf')]
        for b in layer['boundaries']:
            if not b['enabled']:
                continue
            has_boundaries = True
            result = boundary_process(b, x, y)
            if result != 0.0:
                bb = boundary_bbox(b)
                rect = [min(rect[0], bb[0]), max(rect[1], bb[1]), min(rect[2], bb[2]), max(rect[3], bb[3])]
            result = feathering(result, b['feather_type'])
            if result > transform:
                transform = result
            if transform >= 1:
                break
        if not has_boundaries:
            transform = 1.0
        if layer['invert_boundaries']:
            transform = 1.0 - transform
        if transform != 0.0:
            for f in layer['filters']:
                if not f['enabled']:
                    continue
                result = feathering(self.filter_process(f, x, y, transform, base, rect), f.get('feather_type', 0))
                if transform > result:
                    transform = result
                if transform == 0:
                    break
            if layer['invert_filters']:
                transform = 1.0 - transform
            if transform != 0.0:
                for a in layer['affectors']:
                    if a['enabled'] and a['type'] in ('AHCN', 'AHFR', 'AHTR', 'AROA'):
                        base = self.affector_process(a, x, y, transform * affector_transform, base)
                for child in layer['children']:
                    if child['enabled']:
                        base = self.process_layer(child, x, y, base, affector_transform * transform)
        return base

    def height(self, x, y):
        base = 0.0
        for layer in self.trn.get('layers', []):
            if layer['enabled']:
                base = self.process_layer(layer, x, y, base, 1.0)
        return base

    def server_height(self, x, y):
        """TerrainManager::getHeight: out of bounds gives 0, otherwise the coordinates are floored to 0.1 m."""
        half = self.trn['header']['size'] / 2
        if x <= -half or x >= half or y <= -half or y >= half:
            return 0.0
        return self.height(math.floor(x * 10) / 10.0, math.floor(y * 10) / 10.0)


def boundary_bbox(b):
    t = b['type']
    if t == 'BCIR':
        return b['cx'] - b['radius'], b['cx'] + b['radius'], b['cy'] - b['radius'], b['cy'] + b['radius']
    if t == 'BREC':
        return min(b['x0'], b['x1']), max(b['x0'], b['x1']), min(b['y0'], b['y1']), max(b['y0'], b['y1'])
    pts = b['points']
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    w = b.get('line_width', 0.0)
    return min(xs) - w, max(xs) + w, min(ys) - w, max(ys) + w


def load_tga_grey(data):
    """8-bit greyscale TGA (type 3, uncompressed) as Core3's TargaBitmap stores it: row-major, flipped as Core3 does.
    Returns (width, height, bytes) or None for formats Core3 rejects."""
    idlen, cmaptype, datatype = data[0], data[1], data[2]
    cmaplen = struct.unpack_from('<H', data, 5)[0]
    width, height, bpp = struct.unpack_from('<HHB', data, 12)
    if datatype != 3 or bpp != 8:
        return None
    pos = 18 + idlen + cmaptype * cmaplen
    pixels = bytearray(width * height)
    # Core3 fills pixelData[i * width + j] for i = width-1 .. 0, j = 0 .. height-1, reading in file order.
    for i in range(width - 1, -1, -1):
        for j in range(height):
            idx = i * width + j
            if idx < len(pixels):
                pixels[idx] = data[pos]
            pos += 1
    return width, height, bytes(pixels)


def bitmap_filter(bm, flt, x, y, rect):
    """FilterBitmap::process: bilinear sample of the greyscale map stretched over the layer's boundary rectangle."""
    width, height, px = bm
    if not (rect[1] > rect[0] and rect[3] > rect[2]):
        return 0.0
    tx = (x - rect[0]) * width / (rect[1] - rect[0])
    ty = (y - rect[2]) * height / (rect[3] - rect[2])
    tx = min(tx, width - 1)
    ty = min(ty, height - 1)
    v41, v43 = int(ty), int(tx)
    v39 = min(tx + 1, width - 1)
    arg1 = min(int(ty) + 1, height - 1)
    v25 = width * (height - v41 - 1)
    v26 = int(v39 * width / width)
    v27 = int(v43 * width / width)

    def get(i):
        return px[i] if 0 <= i < len(px) else 0
    v28 = get(v27 + v25)
    arg2 = get(v26 + v25)
    v29 = width * (height - int(arg1) - 1)
    arg6 = get(v29 + v27)
    arg1v = get(v26 + v29)
    v30, v31 = tx - v43, ty - v41
    k = 0.003921568859368563
    m = (v31 * (1.0 - v30) * arg6 * k + v31 * v30 * arg1v * k + (1.0 - v31) * (1.0 - v30) * v28 * k
         + (1.0 - v31) * v30 * arg2 * k)
    if m == 1.0:
        m = 0.9999899864196777
    lo, hi, fa = flt['min'], flt['max'], flt['feather']
    if not (lo < m < hi):
        return 0.0
    v35 = (hi - lo) * fa * 0.5
    if m >= lo + v35:
        return m if m <= hi - v35 else m * (hi - m) / v35
    return m * (m - lo) / v35


def client_bitmap_loader(name):
    from trn_iff import client_file
    data = client_file(name)
    return load_tga_grey(data) if data else None


# ---------------------------------------------------------------- printing

def _rule_line(r):
    t = r.get('type')
    k = r.get('kind')
    if k in ('skipped', 'unknown'):
        return f'{t} ({k} by Core3)'
    name = r.get('name', '?')
    en = '' if r.get('enabled', True) else ' (disabled)'
    fields = {k2: v for k2, v in r.items() if k2 not in ('kind', 'type', 'version', 'name', 'enabled', 'points', 'segments')}
    if 'points' in r:
        fields['points'] = len(r['points'])
    if 'segments' in r:
        fields['segments'] = len(r['segments'])
    txt = ', '.join(f'{k2}={v:.3g}' if isinstance(v, float) else f'{k2}={v}' for k2, v in fields.items())
    return f'{t} v{r["version"]} "{name}"{en} {txt}'


def print_layer(layer, depth, out):
    pad = '  ' * depth
    en = '' if layer.get('enabled', True) else ' (disabled)'
    out(f'{pad}LAYR "{layer.get("name", "?")}"{en} invert_b={layer.get("invert_boundaries")} invert_f={layer.get("invert_filters")}')
    for r in layer['rules']:
        if r['kind'] == 'layer':
            print_layer(r, depth + 1, out)
        else:
            out(f'{pad}  {_rule_line(r)}')


def summary(trn, out=print, layers=True):
    h = trn['header']
    out(f'PTAT version {trn["version"]}: "{h["name"]}"')
    out(f'  size {h["size"]:.0f} m, chunk {h["chunk_size"]:.0f} m, tiles/chunk {h["tiles_per_chunk"]}, '
        f'global water {h["use_global_water_table"]} at {h["global_water_height"]:.1f} m, shader "{h["global_water_shader"]}" '
        f'size {h["global_water_shader_size"]:.0f}, time cycle {h["time_cycle"]:.3g}')
    for block in FLORA_BLOCKS:
        b = h[block]
        out(f'  {block}: min {b["min_distance"]:.3g} max {b["max_distance"]:.3g} tile {b["tile_size"]:.3g} border {b["tile_border"]:.3g} seed {b["seed"]}')
    out(f'  shader families ({len(trn.get("shaders", []))}):')
    for f in trn.get('shaders', []):
        out(f'    {f["id"]} "{f["name"]}" file "{f["file"]}" rgb {f["rgb"]} size {f["shader_size"]:.3g} clamp {f["feather_clamp"]:.3g} '
            + ', '.join(f'{c["shader"]}:{c["weight"]:.3g}' for c in f['children']))
    out(f'  flora families ({len(trn.get("flora", []))}):')
    for f in trn.get('flora', []):
        out(f'    {f["id"]} "{f["name"]}" density {f["density"]:.3g} water {f["floats_on_water"]} '
            + ', '.join(c['appearance'] for c in f['children']))
    out(f'  radial families ({len(trn.get("radial", []))}):')
    for f in trn.get('radial', []):
        out(f'    {f["id"]} "{f["name"]}" density {f["density"]:.3g} ' + ', '.join(c['shader'] for c in f['children']))
    out(f'  environments: ' + ', '.join(f'{e["id"]}:"{e["name"]}"' for e in trn.get('environments', [])))
    out(f'  fractals ({len(trn.get("fractals", {}))}):')
    for f in trn.get('fractals', {}).values():
        out(f'    {f["id"]} "{f["name"]}" seed {f["seed"]} oct {f["octaves"]} x{f["octaves_param"]:.3g} amp {f["amplitude"]:.3g} '
            f'freq {f["x_freq"]:.4g}/{f["y_freq"]:.4g} off {f["x_offset"]:.3g}/{f["z_offset"]:.3g} comb {f["combination"]} '
            f'bias {f["bias"]}/{f["bias_value"]:.3g} gain {f["gain"]}/{f["gain_value"]:.3g}')
    out(f'  bitmaps: ' + ', '.join(f'{b["id"]}:"{b["file"]}"' for b in trn.get('bitmaps', {}).values()))
    out(f'  maps: {trn["maps"]}')
    out(f'  top-level layers: {len(trn.get("layers", []))}')
    if layers:
        for layer in trn.get('layers', []):
            print_layer(layer, 2, out)
    if trn['notes']:
        out('  NOTES (what Core3 would skip or reject):')
        for n in trn['notes']:
            out('    - ' + n)


def count_rules(layers):
    counts = {}
    def visit(layer):
        counts['LAYR'] = counts.get('LAYR', 0) + 1
        for r in layer['rules']:
            if r['kind'] == 'layer':
                visit(r)
            else:
                counts[r['type']] = counts.get(r['type'], 0) + 1
    for l in layers:
        visit(l)
    return counts


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    cmd, spec = argv[0], argv[1]
    data = load(spec)
    trn = read_trn(data)
    if cmd == 'summary':
        summary(trn)
    elif cmd == 'check':
        summary(trn, layers=False)
        print('  rule counts:', count_rules(trn.get('layers', [])))
        print('  RESULT:', 'parsed in Core3 order with no notes' if not trn['notes'] else f'{len(trn["notes"])} notes above')
    elif cmd == 'height':
        ev = HeightEvaluator(trn, client_bitmap_loader)
        coords = [float(v) for v in argv[2:]]
        for x, y in zip(coords[::2], coords[1::2]):
            print(f'  ({x:.1f}, {y:.1f}) -> {ev.server_height(x, y):.2f} m')
        for w in sorted(set(ev.warnings)):
            print('  warning:', w)
    else:
        print(__doc__)
        return 2
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
