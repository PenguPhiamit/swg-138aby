"""Write a minimal, valid SWG terrain (.trn, FORM PTAT version 0014) and prove it. Our own code (Fable, 14 Oct 2026).

    python -I trn_write.py build [--out DIR] [--name ossus_test]   # write <DIR>/terrain/<name>.trn + a report
    python -I trn_write.py verify <file.trn>                       # the same checks on any .trn

The prototype is the Ossus test world (see ../README.md): rolling hills from one fractal, a mountain range along
the south edge from a second (ridged) fractal, a flat landing pad whose height is taken from the ground around it
(the Hoth cliff lesson), a global water table, one shader family (stock Dantooine dark-green grass, so the client
already has every shader it names), one environment family, and no flora or radial families (SOE's own tutorial
and simple terrains ship that way too).

Only chunk versions that the stock 0014 files use are written:
  PTAT 0014; TGEN 0000; SGRP 0006; FGRP 0008; RGRP 0003; EGRP 0002; MGRP 0000 / MFRC 0001; LYRS; LAYR 0003;
  IHDR 0001; BREC 0002; BCIR 0002; AHFR 0003; AHCN 0000; ASCN 0001; AENV 0000; maps 0001.
Field order follows Core3-dev src/terrain/** (what the server reads) and matches the stock files byte layout for
byte layout (checked with trn_read.py on every stock planet).

Verification (both commands):
  1. byte round trip through our IFF tree code (parse -> build -> identical bytes);
  2. strict re-read in Core3's chunk order with trn_read.read_trn, which must produce no notes;
  3. structure check: every (parent form, child) pair in our file also occurs in stock tutorial.trn or tatooine.trn;
  4. a height survey with the Core3 port in trn_read (validated against the Hoth server heights): range, water
     share, pad flatness, and the steepest 10 m step across the pad edge;
  5. every shader the file names resolves to a file in the owner's client archives.
Nothing is installed anywhere; the output stays in this folder.
"""
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from trn_iff import Writer, build, chunk, client_file, form, load, parse  # noqa: E402
import trn_read  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_OUT = os.path.join(HERE, '..', 'out')


# ---------------------------------------------------------------- building blocks

def ihdr(enabled, name):
    return form('IHDR', form('0001', chunk('DATA', Writer().i32(1 if enabled else 0).cstr(name).bytes())))


def layer(name, *rules, invert_boundaries=False, invert_filters=False, enabled=True):
    adta = Writer().u32(1 if invert_boundaries else 0).u32(1 if invert_filters else 0).u32(1).cstr('').bytes()
    return form('LAYR', form('0003', ihdr(enabled, name), chunk('ADTA', adta), *rules))


def boundary_rect(name, x0, y0, x1, y1, feather_type=3, feather=0.0):
    data = Writer().f32(x0).f32(y0).f32(x1).f32(y1).i32(feather_type).f32(feather).bytes()
    return form('BREC', form('0002', ihdr(True, name), chunk('DATA', data)))


def boundary_circle(name, cx, cy, radius, feather_type=3, feather=0.0):
    data = Writer().f32(cx).f32(cy).f32(radius).i32(feather_type).f32(feather).bytes()
    return form('BCIR', form('0002', ihdr(True, name), chunk('DATA', data)))


def affector_height_fractal(name, fractal_id, op, height):
    parm = Writer().i32(fractal_id).i32(op).f32(height).bytes()
    return form('AHFR', form('0003', ihdr(True, name), form('DATA', chunk('PARM', parm))))


def affector_height_constant(name, op, height):
    return form('AHCN', form('0000', ihdr(True, name), chunk('DATA', Writer().i32(op).f32(height).bytes())))


def affector_shader_constant(name, family_id, feather_type=0, feather=1.0):
    data = Writer().i32(family_id).i32(feather_type).f32(feather).bytes()
    return form('ASCN', form('0001', ihdr(True, name), chunk('DATA', data)))


def affector_environment(name, environment_id, feather=1.0):
    data = Writer().i32(environment_id).i32(0).f32(feather).bytes()
    return form('AENV', form('0000', ihdr(True, name), chunk('DATA', data)))


def shader_family(fid, name, surface_file, rgb, children, shader_size=2.0, feather_clamp=1.0):
    w = Writer().i32(fid).cstr(name).cstr(surface_file).u8(rgb[0]).u8(rgb[1]).u8(rgb[2]).f32(shader_size).f32(feather_clamp)
    w.i32(len(children))
    for shader, weight in children:
        w.cstr(shader).f32(weight)
    return chunk('SFAM', w.bytes())


def environment_family(eid, name, rgb=(0, 0, 0), feather_clamp=1.0):
    data = Writer().i32(eid).cstr(name).u8(rgb[0]).u8(rgb[1]).u8(rgb[2]).f32(feather_clamp).bytes()
    return form('EFAM', chunk('DATA', data))


def fractal(fid, name, seed, octaves, octaves_param, amplitude, x_freq, y_freq, combination, x_offset=0.0,
            z_offset=0.0, bias=0, bias_value=0.5, gain=0, gain_value=0.7):
    w = (Writer().i32(seed).i32(bias).f32(bias_value).i32(gain).f32(gain_value).u32(octaves).f32(octaves_param)
         .f32(amplitude).f32(x_freq).f32(y_freq).f32(x_offset).f32(z_offset).u32(combination))
    return form('MFAM', chunk('DATA', Writer().i32(fid).cstr(name).bytes()), form('MFRC', form('0001', chunk('DATA', w.bytes()))))


def header_chunk(name, size, chunk_size, tiles_per_chunk, water_on, water_height, water_shader, time_cycle,
                 flora_blocks):
    w = (Writer().cstr(name).f32(size).f32(chunk_size).u32(tiles_per_chunk).u32(1 if water_on else 0)
         .f32(water_height).f32(2.0).cstr(water_shader).f32(time_cycle))
    for i, (mn, mx, tile, border, seed) in enumerate(flora_blocks):
        if i < 3:
            w.u32(int(mn))  # Core3 reads the first three minimum distances as unsigned ints
        else:
            w.f32(mn)       # and the radial-far minimum as a float
        w.f32(mx).f32(tile).f32(border).u32(seed)
    return chunk('DATA', w.bytes())


def maps_form(size, chunk_size):
    """Stock small terrains (tutorial, simple, taanab) carry empty water and seed maps; the big planets carry
    size/chunk-size bitmaps (2048 x 2048 bits). Empty maps are what SOE shipped for a terrain without them."""
    return form('0001', chunk('DATA', Writer().f32(0).f32(0).i32(0).i32(0).bytes()), chunk('WMAP', b''), chunk('SMAP', b''))


# ---------------------------------------------------------------- the Ossus test world

OSSUS = {
    'name': 'ossus_test',
    'size': 16384.0, 'chunk': 8.0, 'tiles': 2,
    'water_height': 14.0, 'water_percentile': 0.06,  # water table = 6th percentile of the draft ground (lakes in hollows)
    'water_shader': 'wter_dant_lake',  # stock shader/wter_dant_lake.sht (Dantooine lakes)
    'time_cycle': 7200.0,
    'flora_blocks': [(0, 128.0, 16.0, 4.0, 0), (0, 50.0, 4.0, 1.5, 0), (0, 28.0, 1.0, 0.48, 0), (120.0, 500.0, 32.0, 12.0, 0)],
    'shader': (1, 'grass_dark_green', 'abstract/terrain_surface/grass.iff', (80, 140, 60),
               [('grss_long_darkgreen', 1.0), ('grss_long_darkgreen_a1', 1.0), ('grss_long_darkgreen_a2', 1.0)]),
    'environment': (1, 'ossus'),
    'hills': {'id': 1, 'seed': 137, 'octaves': 3, 'octaves_param': 2.0, 'amplitude': 0.5, 'freq': 0.0022, 'height': 90.0},
    'mountains': {'id': 2, 'seed': 3996, 'octaves': 4, 'octaves_param': 2.1, 'amplitude': 0.55, 'freq': 0.0016, 'height': 320.0,
                  'rect': (-8192.0, -8192.0, 8192.0, -4800.0), 'feather': 0.7},
    'pad': {'cx': 0.0, 'cy': -3600.0, 'radius': 160.0, 'feather': 0.45},
}


def build_terrain(p=OSSUS):
    """Return (bytes, info). The pad height is read from the hills+mountains layers at the pad centre first."""
    hills, mts, pad = p['hills'], p['mountains'], p['pad']
    sgrp = form('SGRP', form('0006', shader_family(*p['shader'])))
    fgrp = form('FGRP', form('0008'))
    rgrp = form('RGRP', form('0003'))
    egrp = form('EGRP', form('0002', environment_family(*p['environment'])))
    mgrp = form('MGRP', form('0000',
                             fractal(hills['id'], 'hills', hills['seed'], hills['octaves'], hills['octaves_param'],
                                     hills['amplitude'], hills['freq'], hills['freq'], 0),
                             fractal(mts['id'], 'mountains ridged', mts['seed'], mts['octaves'], mts['octaves_param'],
                                     mts['amplitude'], mts['freq'], mts['freq'] * 1.3, 2)))

    def layers(pad_height):
        base = layer('ossus base: rolling hills',
                     affector_height_fractal('hills', hills['id'], 0, hills['height']),
                     affector_shader_constant('grass everywhere', p['shader'][0]),
                     affector_environment('environment', p['environment'][0]))
        mountains = layer('eocho mountains (south edge)',
                          boundary_rect('south band', *mts['rect'], feather_type=3, feather=mts['feather']),
                          affector_height_fractal('ridges', mts['id'], 1, mts['height']))
        landing = layer('knossa landing pad (flattened)',
                        boundary_circle('pad', pad['cx'], pad['cy'], pad['radius'], feather_type=3, feather=pad['feather']),
                        affector_height_constant('flatten to local ground', 0, pad_height))
        return form('LYRS', base, mountains, landing)

    def assemble(pad_height):
        tgen = form('TGEN', form('0000', sgrp, fgrp, rgrp, egrp, mgrp, layers(pad_height)))
        head = header_chunk('terrain/%s.trn' % p['name'], p['size'], p['chunk'], p['tiles'], True, p['water_height'],
                            p['water_shader'], p['time_cycle'], p['flora_blocks'])
        return build([form('PTAT', form('0014', head, tgen, maps_form(p['size'], p['chunk'])))])

    # pass 1: a draft with the pad at 0, to read the natural ground height at the pad centre and to survey the
    # hills so the water table sits a little below the plains (the hollows become lakes); pass 2: the real file
    draft = trn_read.read_trn(assemble(0.0))
    draft['layers'] = draft['layers'][:2]  # hills + mountains only
    ev = trn_read.HeightEvaluator(draft)
    ground = ev.height(pad['cx'], pad['cy'])
    pad_height = round(ground, 1)
    half, step = p['size'] / 2, 512.0
    samples = sorted(ev.height(x, y) for x in _frange(-half + step / 2, half, step) for y in _frange(-half + step / 2, half, step))
    if p.get('water_percentile') is not None:
        p['water_height'] = round(samples[int(len(samples) * p['water_percentile'])] * 2) / 2
    data = assemble(pad_height)
    return data, {'pad_height': pad_height, 'pad_centre': (pad['cx'], pad['cy']), 'water_height': p['water_height'],
                  'draft_ground_percentiles': {k: round(samples[int(len(samples) * k)], 1) for k in (0.02, 0.1, 0.5, 0.9, 0.99)}}


def _frange(start, stop, step):
    v = start
    while v < stop:
        yield v
        v += step


# ---------------------------------------------------------------- verification

def structure_pairs(nodes, parent='<root>'):
    pairs = set()
    for n in nodes:
        label = f'FORM {n.form}' if n.is_form else n.tag
        pairs.add((parent, label))
        if n.is_form:
            pairs |= structure_pairs(n.children, label)
    return pairs


def verify(data, label, pad=None, out=print):
    report = {'file': label, 'bytes': len(data)}
    nodes = parse(data)
    report['round_trip_identical'] = build(nodes) == data
    out(f'1. byte round trip: {"IDENTICAL" if report["round_trip_identical"] else "DIFFERENT"}')

    trn = trn_read.read_trn(data)
    report['core3_order_notes'] = trn['notes']
    out(f'2. Core3-order re-read: version {trn["version"]}, {len(trn["layers"])} top layers, '
        f'{len(trn["notes"])} notes' + (': ' + '; '.join(trn['notes']) if trn['notes'] else ''))

    stock = set()
    for ref in ('terrain/tutorial.trn', 'terrain/simple.trn', 'terrain/tatooine.trn'):
        ref_data = client_file(ref)
        if ref_data:
            stock |= structure_pairs(parse(ref_data))
    mine = structure_pairs(nodes)
    novel = sorted(mine - stock)
    report['structure_pairs_not_in_stock'] = [f'{a} > {b}' for a, b in novel]
    out(f'3. structure vs stock tutorial+tatooine: {len(mine)} parent/child pairs, {len(novel)} not seen in stock'
        + (': ' + ', '.join(report['structure_pairs_not_in_stock']) if novel else ''))

    ev = trn_read.HeightEvaluator(trn)
    half = trn['header']['size'] / 2
    step = 256.0
    heights = []
    x = -half + step / 2
    while x < half:
        y = -half + step / 2
        while y < half:
            heights.append(ev.height(x, y))
            y += step
        x += step
    water = trn['header']['global_water_height'] if trn['header']['use_global_water_table'] else None
    report['height_survey'] = {
        'samples': len(heights), 'grid_step_m': step, 'min': round(min(heights), 1), 'max': round(max(heights), 1),
        'mean': round(sum(heights) / len(heights), 1),
        'below_water_share': round(sum(h < water for h in heights) / len(heights), 3) if water is not None else None,
    }
    out(f'4. heights on a {step:.0f} m grid ({len(heights)} samples): min {min(heights):.1f} m, max {max(heights):.1f} m, '
        f'mean {sum(heights) / len(heights):.1f} m' + (f', {report["height_survey"]["below_water_share"] * 100:.1f}% under water at {water:.0f} m' if water is not None else ''))
    if pad:
        cx, cy, r = pad['cx'], pad['cy'], pad['radius']
        centre = ev.height(cx, cy)
        inner = [ev.height(cx + dx, cy + dy) for dx in (-40, 0, 40) for dy in (-40, 0, 40)]
        profile = [ev.height(cx, cy + d) for d in range(0, int(r) + 400, 10)]
        steepest = max(abs(b - a) for a, b in zip(profile, profile[1:]))
        report['pad'] = {'centre_height': round(centre, 2), 'inner_spread': round(max(inner) - min(inner), 3),
                         'steepest_10m_step_out_to_%dm' % (int(r) + 400): round(steepest, 2)}
        out(f'   pad: centre {centre:.2f} m, spread over the inner 80 m {max(inner) - min(inner):.3f} m, '
            f'steepest 10 m step walking north out of the pad {steepest:.2f} m')

    from trn_iff import client_index
    idx = client_index()
    missing = []
    for fam in trn['shaders']:
        for ref in [fam['file']] + [c['shader'] for c in fam['children']]:
            if ref and ref.lower() not in idx and ('shader/' + ref + '.sht').lower() not in idx:
                missing.append(ref)
    ws = trn['header']['global_water_shader']
    if ws and ('shader/' + ws + '.sht').lower() not in idx:
        missing.append(ws)
    report['shader_refs_missing_in_client'] = missing
    out(f'5. shader references missing in the client archives: {missing or "none"}')
    ok = (report['round_trip_identical'] and not trn['notes'] and not novel and not missing)
    report['verdict'] = 'PASS' if ok else 'CHECK'
    out(f'VERDICT: {report["verdict"]}')
    return report


def main(argv):
    if not argv or argv[0] not in ('build', 'verify'):
        print(__doc__)
        return 2
    if argv[0] == 'verify':
        data = load(argv[1])
        verify(data, argv[1])
        return 0
    out_dir, name = DEFAULT_OUT, OSSUS['name']
    i = 1
    while i < len(argv):
        if argv[i] == '--out':
            out_dir, i = argv[i + 1], i + 2
        elif argv[i] == '--name':
            name, i = argv[i + 1], i + 2
        else:
            i += 1
    params = dict(OSSUS, name=name)
    data, info = build_terrain(params)
    os.makedirs(os.path.join(out_dir, 'terrain'), exist_ok=True)
    path = os.path.join(out_dir, 'terrain', name + '.trn')
    with open(path, 'wb') as f:
        f.write(data)
    print(f'wrote {path} ({len(data)} bytes); pad flattened to {info["pad_height"]} m, the natural ground at {info["pad_centre"]}')
    report = verify(data, path, pad=params['pad'])
    report.update(info)
    with open(os.path.join(out_dir, name + '-report.json'), 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
    print('report:', os.path.join(out_dir, name + '-report.json'))
    return 0 if report['verdict'] == 'PASS' else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
