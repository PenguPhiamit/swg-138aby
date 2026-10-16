"""O7 terrain: the o6 craters, scorch fans, glass pan, rubble apron, the two first settlement fields and the glass plain,
as layers for Fable's ossus_terrain.py, without editing that tool. Our own code (Claude, 16 Oct 2026).

    python -I o7_terrain.py design                       # write ../terrain.json from the parameters below
    python -I o7_terrain.py build [--out DIR] [--stage]  # build ossus.trn with the layers
                                                         #   --out DIR  (default: a temp folder) nothing in the repo is touched
                                                         #   --stage    write Fable-ossus/staged/client/terrain/*.tga/ossus.trn and
                                                         #              Fable-ossus/out/*.json (the real rebuild; Claude's step)
    python -I o7_terrain.py build --plain [--out DIR]    # the same build without the o7 layers (must equal the staged file)

How the layers get in: ossus_terrain.assemble() builds the layer list inside one function, so this module wraps two
names in that module (layer() to remember the node of the 'academy ruins pad (flattened)' layer, form() to splice our
layers into the LYRS form right after it) and adds the new shader families to its SHADERS table. assemble() runs three
times in build_all(); the ruins layer exists only in the last (final) pass, so the site survey and the road heights of
the first passes are exactly the same as in the staged file.
"""
import json
import math
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from o7_common import O7, OSSUS, STAGED_CLIENT, STAGED_TRN, Terrain, jload, jsave  # noqa: E402
import ossus_terrain as ot  # noqa: E402
import trn_read  # noqa: E402
from trn_iff import Writer, chunk, form  # noqa: E402
from trn_write import ihdr  # noqa: E402

TERRAIN_JSON = os.path.join(O7, 'terrain.json')
INSERT_AFTER = 'academy ruins pad (flattened)'
RUINS = (2016.0, 2848.0)

# ---------------------------------------------------------------- the design (o6 sections 1 and 2, owner's answers of 15 Oct)
# Depths: the owner said 2-4 m deep "as designed"; o6's own list was 3.5 / 2.5 / 2.0 / 1.5 / 1.0, so the two shallowest are
# raised to the 2.0 m floor of the owner's range (o6_depth_m keeps Fable's numbers). Lip heights are tuned (see README) so
# that the ring beyond the bowl peaks at about 0.4 m: BCIR bowls here fall off steeply, a plain +0.4 m disc would vanish.
CRATERS = [
    # id, cx, cy, radius, depth, o6 depth, lip add height, fan length beyond the rim (None = no fan)
    (1, 1870.0, 2930.0, 22.0, 3.5, 3.5, 1.0, 60.0),
    (2, 2140.0, 2790.0, 18.0, 2.5, 2.5, 0.8, 55.0),
    (3, 2010.0, 3010.0, 14.0, 2.0, 2.0, 0.6, 45.0),
    (4, 1930.0, 2700.0, 12.0, 2.0, 1.5, 0.6, 40.0),
    (5, 2210.0, 2920.0, 9.0, 2.0, 1.0, 0.5, None),
]
BOWL_FEATHER, LIP_OUTER, LIP_FEATHER, LIP_CUT_OFFSET, LIP_CUT_FEATHER, BURN_MARGIN = 0.9, 6.0, 0.6, 1.0, 0.9, 10.0
FAN_HEADING = 225.0     # toward the south-west (compass degrees): the attack came from orbit at a low angle
FAN_FEATHER_M = 10.0    # BPOL feather is a distance in metres (stock Tatooine uses values up to 700)
GLASS_PAN = (RUINS[0], RUINS[1], 60.0, 0.25)
APRON = (RUINS[0], RUINS[1], 130.0, 0.35, 60.0)
FIELDS = [
    # key, label, cx, cy, radius, flatten height (m), feather
    ('westmarch', 'Westmarch', -5344.0, 96.0, 400.0, 46.0, 0.3),
    ('knossa_fields', 'Knossa Fields', 1500.0, -3300.0, 450.0, 50.0, 0.3),
]
GLASS_PLAIN = (1900.0, -4875.0, 2500.0, -4575.0)    # POI 17: flattest tested 600 x 300 m footprint; centre (2200, -4725)
# Owner 16 Oct 05:40: centre in the foothill window x 1850-2450 / y -4800 to -4500.
# Selected by tools/select_glass_plain.py: 25 m centre and footprint grids, minimum full-footprint relief.
GLASS_PLAIN_FEATHER_M = 25.0

SHADER_FAMILIES = {
    'crater': {'id': 12, 'name': 'crater floor (torn scorched earth)',
               'children': [['dirt_scorched_tornearth', 1.0], ['dirt_scorched_tornearth_a1', 1.0], ['dirt_scorched_tornearth_a2', 1.0]]},
    'scorch': {'id': 13, 'name': 'scorch fans (scorched earth)',
               'children': [['dirt_scorched_earth', 1.0], ['dirt_scorched_earth_a1', 1.0], ['dirt_scorched_earth_a2', 1.0]]},
}


def bcir(name, cx, cy, r, ft, f):
    return {'type': 'BCIR', 'name': name, 'cx': cx, 'cy': cy, 'radius': r, 'feather_type': ft, 'feather': f}


def design():
    layers = []
    craters_meta, fans_meta = [], []
    for cid, cx, cy, r, depth, o6d, lip, fan_len in CRATERS:
        kids = [
            {'name': 'crater %d bowl' % cid, 'boundaries': [bcir('bowl', cx, cy, r, 3, BOWL_FEATHER)],
             'affectors': [{'type': 'AHCN', 'name': 'dig %.1f m' % depth, 'op': 1, 'height': -depth}]},
            {'name': 'crater %d lip raise' % cid, 'boundaries': [bcir('lip', cx, cy, r + LIP_OUTER, 3, LIP_FEATHER)],
             'affectors': [{'type': 'AHCN', 'name': 'raise %.1f m' % lip, 'op': 1, 'height': lip}]},
            {'name': 'crater %d lip trim' % cid, 'boundaries': [bcir('trim', cx, cy, r + LIP_CUT_OFFSET, 3, LIP_CUT_FEATHER)],
             'affectors': [{'type': 'AHCN', 'name': 'lower %.1f m' % lip, 'op': 1, 'height': -lip}]},
            {'name': 'crater %d burn' % cid, 'boundaries': [bcir('burn', cx, cy, r + BURN_MARGIN, 3, 0.5)],
             'affectors': [{'type': 'ASCN', 'name': 'crater floor', 'family': 'crater', 'feather_type': 1, 'feather': 0.4},
                           {'type': 'CLEAR_FLORA', 'prefix': 'crater %d' % cid}]},
        ]
        layers.append({'name': 'o7 crater %d (r %.0f m, %.1f m deep)' % (cid, r, depth), 'children': kids})
        craters_meta.append({'id': cid, 'cx': cx, 'cy': cy, 'radius': r, 'depth_m': depth, 'o6_depth_m': o6d, 'lip_raise_m': lip,
                             'bowl_feather': BOWL_FEATHER, 'lip_outer_radius': r + LIP_OUTER, 'lip_trim_radius': r + LIP_CUT_OFFSET,
                             'burn_radius': r + BURN_MARGIN, 'distance_to_ruins_centre': round(math.hypot(cx - RUINS[0], cy - RUINS[1]), 1)})
    # scorch fans: a long triangle from each large crater toward the south-west
    hd = math.radians(FAN_HEADING)
    ux, uy = math.sin(hd), math.cos(hd)       # unit vector of the heading (east, north)
    px, py = uy, -ux                          # perpendicular
    for cid, cx, cy, r, depth, o6d, lip, fan_len in CRATERS:
        if fan_len is None:
            continue
        base = r * 0.9
        pts = [[round(cx + px * base, 1), round(cy + py * base, 1)], [round(cx - px * base, 1), round(cy - py * base, 1)],
               [round(cx + ux * (r + fan_len), 1), round(cy + uy * (r + fan_len), 1)]]
        layers.append({'name': 'o7 scorch fan %d' % cid, 'boundaries': [{'type': 'BPOL', 'name': 'fan', 'points': pts, 'feather_type': 3, 'feather': FAN_FEATHER_M}],
                       'affectors': [{'type': 'ASCN', 'name': 'scorched earth', 'family': 'scorch', 'feather_type': 1, 'feather': 0.4},
                                     {'type': 'CLEAR_FLORA', 'prefix': 'fan %d' % cid}]})
        fans_meta.append({'crater': cid, 'heading_deg': FAN_HEADING, 'length_beyond_rim_m': fan_len, 'points': pts, 'feather_m': FAN_FEATHER_M})
    # glass pan and rubble apron on the ruins pad
    gx, gy, gr, gf = GLASS_PAN
    layers.append({'name': 'o7 glass pan (r %.0f m)' % gr, 'boundaries': [bcir('pan', gx, gy, gr, 3, gf)],
                   'affectors': [{'type': 'ASCN', 'name': 'limestone sheen', 'family': 'summit', 'feather_type': 1, 'feather': 0.3},
                                 {'type': 'CLEAR_FLORA', 'prefix': 'glass pan'}]})
    ax, ay, ar, af, ain = APRON
    layers.append({'name': 'o7 rubble apron (r %.0f-%.0f m)' % (ain, ar), 'boundaries': [bcir('apron', ax, ay, ar, 3, af)],
                   'affectors': [{'type': 'CLEAR_FLORA', 'prefix': 'apron'}],
                   'children': [{'name': 'apron rocks (outside r %.0f)' % ain, 'invert_boundaries': True, 'boundaries': [bcir('inner', ax, ay, ain, 3, 0.3)],
                                 'affectors': [{'type': 'AFSC', 'name': 'rubble rocks', 'family': 'rocks', 'op': 1, 'remove_all': 0, 'feather_type': 1, 'feather': 0.5}]}]})
    # the two settlement fields (the other three of o6 stay unstaged)
    fields_meta = []
    for key, label, cx, cy, r, h, f in FIELDS:
        layers.append({'name': 'o7 field %s (flat to %.1f m)' % (label, h), 'boundaries': [bcir(label, cx, cy, r, 3, f)],
                       'affectors': [{'type': 'AHCN', 'name': 'flatten', 'op': 0, 'height': h},
                                     {'type': 'ASCN', 'name': 'plains grass', 'family': 'grass', 'feather_type': 1, 'feather': 0.4},
                                     {'type': 'CLEAR_FLORA', 'prefix': key}]})
        fields_meta.append({'key': key, 'label': label, 'cx': cx, 'cy': cy, 'radius': r, 'height_m': h, 'feather': f,
                            'flat_radius_m': round((1 - f) * r), 'ramp_m': round(f * r)})
    # POI 17: the supernova glass plain (terrain only)
    x0, y0, x1, y1 = GLASS_PLAIN
    layers.append({'name': 'o7 supernova glass plain (POI 17)', 'boundaries': [{'type': 'BPOL', 'name': 'plain', 'points': [[x0, y0], [x1, y0], [x1, y1], [x0, y1]],
                                                                               'feather_type': 3, 'feather': GLASS_PLAIN_FEATHER_M}],
                   'affectors': [{'type': 'ASCN', 'name': 'limestone', 'family': 'summit', 'feather_type': 1, 'feather': 0.3},
                                 {'type': 'CLEAR_FLORA', 'prefix': 'glass plain'}]})
    return {
        'schema': 'o7-terrain-1',
        'what': 'Layers for Fable-ossus/tools/ossus_terrain.py (read by o7_terrain.py). Coordinates: x east, y north, metres. '
                'BCIR feather is a fraction of the radius, BPOL feather is a distance in metres, AHCN op 0 sets the height, op 1 adds.',
        'insert_after_layer': INSERT_AFTER,
        'shader_families': SHADER_FAMILIES,
        'layers': layers,
        'design': {'craters': craters_meta, 'scorch_fans': fans_meta, 'glass_pan': {'cx': gx, 'cy': gy, 'radius': gr},
                   'rubble_apron': {'cx': ax, 'cy': ay, 'outer_radius': ar, 'inner_radius': ain},
                   'fields': fields_meta, 'glass_plain': {'rect': list(GLASS_PLAIN), 'poi': 17},
                   'held': ['North Reach', 'Rim Mesa', 'Lakeshore'], 'held_note': 'the owner kept three of the five o6 fields as later options; not staged'},
    }


# ---------------------------------------------------------------- layer specs -> nodes

def boundary_polygon(name, points, feather_type=0, feather=0.0, water=0, water_height=0.0, water_shader_size=2.0, water_shader=''):
    """BPOL 0005 (byte-identical to 54 of 57 stock Tatooine polygons in the check of 16 Oct; the three others differ in flags)."""
    w = Writer().i32(len(points))
    for x, y in points:
        w.f32(x).f32(y)
    w.i32(feather_type).f32(feather).i32(water).f32(water_height).f32(water_shader_size).cstr(water_shader)
    return form('BPOL', form('0005', ihdr(True, name), chunk('DATA', w.bytes())))


def _boundary(b):
    t = b['type']
    if t == 'BCIR':
        return ot.boundary_circle(b['name'], b['cx'], b['cy'], b['radius'], feather_type=b['feather_type'], feather=b['feather'])
    if t == 'BPOL':
        return boundary_polygon(b['name'], [tuple(p) for p in b['points']], b['feather_type'], b['feather'])
    if t == 'BREC':
        return ot.boundary_rect(b['name'], b['x0'], b['y0'], b['x1'], b['y1'], feather_type=b['feather_type'], feather=b['feather'])
    raise ValueError('boundary type %s' % t)


def _affectors(a):
    t = a['type']
    if t == 'AHCN':
        return [ot.affector_height_constant(a['name'], a['op'], a['height'])]
    if t == 'ASCN':
        return [ot.affector_shader_constant(a['name'], ot.S(a['family']), feather_type=a['feather_type'], feather=a['feather'])]
    if t == 'CLEAR_FLORA':
        return ot.clear_flora(a['prefix'])
    fl = {'AFSC': (ot.affector_flora_collidable, ot.F), 'AFSN': (ot.affector_flora_non_collidable, ot.F),
          'AFDN': (ot.affector_radial_near, ot.R), 'AFDF': (ot.affector_radial_far, ot.R)}
    if t in fl:
        make, fam = fl[t]
        return [make(a['name'], fam(a['family']), op=a.get('op', 1), remove_all=a.get('remove_all', 0), feather_type=a.get('feather_type', 0), feather=a.get('feather', 1.0))]
    raise ValueError('affector type %s' % t)


def build_layer(spec, layer_fn):
    rules = [_boundary(b) for b in spec.get('boundaries', [])]
    for a in spec.get('affectors', []):
        rules.extend(_affectors(a))
    rules.extend(build_layer(c, layer_fn) for c in spec.get('children', []))
    return layer_fn(spec['name'], *rules, invert_boundaries=bool(spec.get('invert_boundaries', False)))


class Patched:
    """Context manager: wraps ossus_terrain.layer / form and adds the shader families while a build runs."""

    def __init__(self, spec):
        self.spec = spec
        self.seen = {}

    def __enter__(self):
        self.orig_layer, self.orig_form, self.orig_shaders = ot.layer, ot.form, dict(ot.SHADERS)
        spec = self.spec

        def spy(name, *rules, **kw):
            node = self.orig_layer(name, *rules, **kw)
            self.seen[name] = node
            return node

        def spliced(tag, *children):
            if tag == 'LYRS' and self.seen.get(spec['insert_after_layer']) is not None:
                anchor = self.seen[spec['insert_after_layer']]
                kids = list(children)
                at = next(i for i, c in enumerate(kids) if c is anchor) + 1
                kids[at:at] = [build_layer(l, self.orig_layer) for l in spec['layers']]
                return self.orig_form(tag, *kids)
            return self.orig_form(tag, *children)

        ot.layer, ot.form = spy, spliced
        for key, fam in spec['shader_families'].items():
            ot.SHADERS[key] = (fam['id'], fam['name'], [tuple(c) for c in fam['children']])
        return self

    def __exit__(self, *exc):
        ot.layer, ot.form = self.orig_layer, self.orig_form
        ot.SHADERS.clear()
        ot.SHADERS.update(self.orig_shaders)
        return False


def build(out_dir, with_layers=True, quiet=False):
    spec = jload(TERRAIN_JSON)
    ot.STAGED = os.path.join(out_dir, 'staged', 'client') if out_dir else ot.STAGED
    ot.OUT = os.path.join(out_dir, 'out') if out_dir else ot.OUT
    log = (lambda *a, **k: None) if quiet else print
    if with_layers:
        with Patched(spec):
            rep = ot.build_all(out=log)
    else:
        rep = ot.build_all(out=log)
    return rep


# ---------------------------------------------------------------- checks on a built file

def _terrain_of(stage_dir):
    return Terrain(os.path.join(stage_dir, 'terrain', 'ossus.trn'), stage_dir)


def survey(new_dir):
    """Compare the o7 build with the staged file (no o7 layers): where the server height changed, craters, fields."""
    spec = jload(TERRAIN_JSON)
    new = _terrain_of(new_dir)
    old = Terrain()
    d = spec['design']
    rep = {'layers_added': len(spec['layers']), 'water_m': new.water}
    # 1. craters
    cr = []
    for c in d['craters']:
        best = {'id': c['id']}
        cx, cy, r = c['cx'], c['cy'], c['radius']
        centre_drop = old.h(cx, cy) - new.h(cx, cy)
        lip, slope = -1e9, 0.0
        profiles = []
        for b in range(0, 360, 45):
            ux, uy = math.cos(math.radians(b)), math.sin(math.radians(b))
            prof = [(dd, new.h(cx + ux * dd, cy + uy * dd) - old.h(cx + ux * dd, cy + uy * dd)) for dd in [i * 1.0 for i in range(0, int(r + 25))]]
            prof_h = [new.h(cx + ux * dd, cy + uy * dd) for dd in [i * 1.0 for i in range(0, int(r + 25))]]
            slope = max(slope, max(abs(prof_h[i + 1] - prof_h[i]) for i in range(len(prof_h) - 1)))
            lip = max(lip, max(v for dd, v in prof if dd >= r * 0.8))
            profiles.append(prof)
        # reach: farthest radius at which any height changed by more than 5 cm
        reach = max(dd for prof in profiles for dd, v in prof if abs(v) > 0.05) if any(abs(v) > 0.05 for prof in profiles for dd, v in prof) else 0
        best.update(centre_drop_m=round(centre_drop, 2), lip_peak_above_old_ground_m=round(lip, 2), steepest_1m_step_deg=round(math.degrees(math.atan(slope)), 1),
                    changes_reach_to_m=reach, lip_under_0_6_m=lip < 0.6, depth_in_owner_range_2_to_4=2.0 <= centre_drop <= 4.0 + 0.05)
        cr.append(best)
    rep['craters'] = cr
    # 2. fields
    fl = []
    for f in d['fields']:
        cx, cy, r, H, fe = f['cx'], f['cy'], f['radius'], f['height_m'], f['feather']
        flat_r = (1 - fe) * r
        hs = [new.h(px, py) for px, py in new.disc(cx, cy, flat_r - 2, 20.0)]
        core60 = new.relief(cx, cy, 60.0, 10.0)
        ramp_slope = new.max_slope_deg(cx, cy, r * 1.1, 20.0)
        old_slope = old.max_slope_deg(cx, cy, r * 1.1, 20.0)
        under = sum(1 for px, py in new.disc(cx, cy, r, 20.0) if new.h(px, py) < new.water) / max(1, len(new.disc(cx, cy, r, 20.0)))
        nb = [{'name': n, 'gap_m': round(math.hypot(cx - x, cy - y) - r - rr, 1)} for x, y, rr, n in
              __import__('o7_common').NOBUILD]
        fl.append({'key': f['key'], 'label': f['label'], 'flat_radius_m': round(flat_r), 'flat_core_height_min': round(min(hs), 2), 'flat_core_height_max': round(max(hs), 2),
                   'spread_over_r60_m': round(core60[2], 3), 'centre_height_m': round(new.h(cx, cy), 2), 'steepest_20m_step_deg_in_r1.1': round(ramp_slope, 1),
                   'natural_steepest_deg': round(old_slope, 1), 'share_under_water_in_field': round(under, 4), 'gap_to_no_build_circles_m': nb,
                   'min_gap_to_no_build_m': min(x['gap_m'] for x in nb)})
    rep['fields'] = fl
    # 3. whole-planet regression: server heights equal the staged file everywhere except inside the o7 discs
    zones = [(c['cx'], c['cy'], c['burn_radius'] + 12.0) for c in d['craters']] + [(f['cx'], f['cy'], f['radius'] + 5.0) for f in d['fields']]
    changed_in, changed_out, worst_out = 0, 0, 0.0
    n = 0
    step = 96.0
    x = -8192 + step / 2
    while x < 8192:
        y = -8192 + step / 2
        while y < 8192:
            n += 1
            diff = abs(new.h(x, y) - old.h(x, y))
            inside = any(math.hypot(x - zx, y - zy) <= zr for zx, zy, zr in zones)
            if diff > 1e-4:
                if inside:
                    changed_in += 1
                else:
                    changed_out += 1
                    worst_out = max(worst_out, diff)
            y += step
        x += step
    # the glass plain, scorch fans, glass pan and apron are client-only: heights must not move there beyond the craters
    rep['regression'] = {'grid_step_m': step, 'samples': n, 'changed_inside_o7_discs': changed_in, 'changed_outside_o7_discs': changed_out,
                         'worst_change_outside_m': round(worst_out, 4)}
    # 4. the glass plain relief (POI 17 is terrain only; flag if it is not a plain)
    gp = d['glass_plain']['rect']
    cxp, cyp = (gp[0] + gp[2]) / 2, (gp[1] + gp[3]) / 2
    sp = new.relief(cxp, cyp, 150.0, 25.0)
    rep['glass_plain'] = {'centre': [cxp, cyp], 'ground_min': round(sp[0], 1), 'ground_max': round(sp[1], 1), 'spread_m': round(sp[2], 1),
                          'steepest_25m_step_deg_r150': round(new.max_slope_deg(cxp, cyp, 150.0, 25.0), 1)}
    return rep


def main(argv):
    if not argv or argv[0] not in ('design', 'build', 'survey'):
        print(__doc__)
        return 2
    if argv[0] == 'design':
        jsave(TERRAIN_JSON, design())
        spec = jload(TERRAIN_JSON)
        print('wrote', TERRAIN_JSON, '-', len(spec['layers']), 'layers,', len(spec['shader_families']), 'new shader families')
        return 0
    out_dir = None
    stage = '--stage' in argv
    plain = '--plain' in argv
    if '--out' in argv:
        out_dir = argv[argv.index('--out') + 1]
    if argv[0] == 'survey':
        rep = survey(os.path.join(out_dir, 'staged', 'client'))
        print(json.dumps(rep, indent=1))
        return 0
    if stage:
        out_dir = None   # ossus_terrain's own STAGED and OUT
    elif out_dir is None:
        out_dir = tempfile.mkdtemp(prefix='o7-terrain-')
    rep = build(out_dir, with_layers=not plain)
    print('build verdict:', rep['verdict'], '; folder:', out_dir or '(staged)')
    return 0 if rep['verdict'] == 'PASS' else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
