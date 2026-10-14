"""Build the full Ossus terrain (terrain/ossus.trn plus its two painted bitmaps), verify it offline and survey it for
building sites. Our own code and design (Fable, 14 Oct 2026); story-neutral geography only.

    python -I ossus_terrain.py build            # staged/client/terrain/ossus.trn, the TGAs, out/ossus-report.json,
                                                #   out/ossus-sites.json, out/ossus-height.png
    python -I ossus_terrain.py verify <file>    # the offline checks on any .trn (no site survey)

What is in the file (all stock art referenced in place, by name; nothing copied out of the owner's client):
  - 9 shader families, 7 flora families, 6 radial families, 6 environment families, 5 fractals, 2 bitmaps;
  - layers: rolling hills, fine relief, forests (fractal patches), the Eocho mountains along the south edge,
    highland and summit bands, the Academy benchland (painted bitmap, replaced height), Imhar Canyon (painted
    bitmap, floor just above the water table), a lake basin, lake bed and shore, mossy valleys, cliff slopes,
    the Knossa landing pad and its clearing, the Knossa road in 500 m pieces, and 3 cave mouths (AEXC holes);
  - global water at the 6th percentile of the plains (hollows become lakes).
Three passes: a draft to read ground heights (pad, water table, benchland), a surveyed draft to pick the sites and
the road heights, then the final file. Verification: byte round trip, Core3-order re-read with no notes, structure
pairs seen in stock files, every shader/flora/radial/bitmap reference resolvable, a height survey on a 64 m grid
with the Core3 port (plus roads), flatness probes at every site, road height agreement, TGA round trips.
"""
import json
import math
import os
import struct
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, '..', 'Fable-planet-test', 'tools'))
import trn_read  # noqa: E402
from trn_iff import build, client_file, client_index, form, parse  # noqa: E402
from trn_blocks import (affector_environment, affector_exclude, affector_flora_collidable, affector_flora_non_collidable,  # noqa: E402
                        affector_height_constant, affector_height_fractal, affector_radial_far, affector_radial_near,
                        affector_road, affector_shader_constant, bitmap_family, boundary_circle, boundary_polyline,
                        boundary_rect, environment_family, filter_bitmap, filter_fractal, filter_height, filter_slope,
                        flora_family, fractal, header_chunk, layer, maps_form, radial, radial_family, shader_family, tree)
from trn_road import RoadHeightEvaluator  # noqa: E402
from tga import read_tga_grey, write_tga_grey  # noqa: E402

STAGED = os.path.join(ROOT, 'staged', 'client')
OUT = os.path.join(ROOT, 'out')
SIZE, CHUNK, TILES = 16384.0, 8.0, 2
HALF = SIZE / 2

# ---------------------------------------------------------------- the design (world x east, y north, metres)
PAD = {'cx': 0.0, 'cy': -3600.0, 'radius': 160.0, 'feather': 0.45, 'clearing': 300.0}
MOUNTAINS = {'rect': (-8192.0, -8192.0, 8192.0, -4800.0), 'feather': 0.7, 'height': 320.0}
BENCH = {'cx': 1600.0, 'cy': 2600.0, 'rx': 1250.0, 'ry': 850.0, 'rise': 110.0, 'falloff': 450.0,
         'rect': (-100.0, 1400.0, 3300.0, 3800.0), 'tga': 'terrain/ossus_academy.tga'}
CANYON = {'path': [(3400.0, -2000.0), (3900.0, -1500.0), (4300.0, -700.0), (4800.0, -200.0), (5300.0, 500.0),
                   (5600.0, 1200.0), (6100.0, 1600.0), (6600.0, 2000.0)],
          'floor_half_width': 90.0, 'wall': 100.0, 'tga': 'terrain/ossus_canyon.tga', 'tga_res': 512,
          'floor_above_water': 6.0,
          # the canyon cuts through an upland ("canyon country"): a wide painted mesa raised first, then the channel cut.
          # The frame rectangle keeps 1500 m around every path point so the mesa's falloff (800 + 600 m) ends inside it.
          'rect': (1900.0, -3500.0, 8100.0, 3500.0),
          'mesa_half_width': 700.0, 'mesa_falloff': 500.0, 'mesa_tga': 'terrain/ossus_mesa.tga', 'mesa_height': 100.0}
LAKE = {'cx': -3600.0, 'cy': 1200.0, 'radius': 600.0, 'feather': 0.6, 'below_water': 10.0}
ROAD = {'points': [(0.0, -3430.0), (250.0, -2600.0), (500.0, -1500.0), (800.0, -400.0), (1100.0, 700.0), (1300.0, 1500.0)],
        'width': 12.0, 'piece': 480.0, 'sample': 40.0}
WATER_PERCENTILE = 0.06
TIME_CYCLE = 7200.0
FLORA_BLOCKS = [(0, 128.0, 8.0, 2.0, 0), (0, 64.0, 4.0, 0.5, 0), (0, 30.0, 1.0, 0.0, 0), (128.0, 512.0, 32.0, 8.0, 0)]

# shader families: id, name, children (stock shader/<name>.sht, referenced by name)
SHADERS = {
    'grass': (1, 'ossus grass', [('grss_long_darkgreen', 1.0), ('grss_long_darkgreen_a1', 1.0), ('grss_long_darkgreen_a2', 1.0)]),
    'dry': (2, 'highland dry grass', [('grss_dant_yellow', 1.0), ('grss_dant_yellow_a1', 1.0), ('grss_dant_yellow_a2', 1.0)]),
    'forest': (3, 'forest floor', [('frst_fallenleaves', 1.0), ('frst_fallenleaves_a1', 1.0), ('frst_dirtwtwigs', 0.5)]),
    'moss': (4, 'mossy valleys', [('dirt_mossydirt', 1.0), ('dirt_mossydirt_a1', 1.0), ('dirt_mossydirt_a2', 1.0)]),
    'cliff': (5, 'cliff rock', [('rock_cliffbrwngray', 1.0), ('rock_cliffbrwngray_a1', 1.0), ('rock_cliffbrwngray_a2', 1.0)]),
    'summit': (6, 'summit limestone', [('rock_mtns_whitelimestone', 1.0), ('rock_mtns_whitelimestone_a1', 1.0), ('rock_mtns_whitelimestone_a2', 1.0)]),
    'canyon_floor': (7, 'canyon floor', [('dirt_dath_desertcanyonfloor', 1.0), ('dirt_dath_desertcanyonfloor_a2', 1.0), ('dirt_dath_desertcanyonfloor_a1', 0.25)]),
    'canyon_wall': (8, 'canyon wall', [('rock_dath_desertcanyon', 1.0), ('rock_dath_desertcanyon_a1', 1.0), ('rock_dath_desertcanyon_a2', 1.0)]),
    'lakebed': (9, 'lake bed and shore', [('rock_endorriverbed', 1.0), ('rock_endorriverbed_a1', 1.0), ('rock_endorriverbed_a2', 1.0)]),
    'road': (10, 'road dirt', [('dirt_everdirt', 1.0), ('dirt_everdirt_a1', 1.0), ('dirt_everdirt_a2', 1.0)]),
    'bench': (11, 'benchland meadow', [('grss_dant_pink', 1.0), ('grss_dant_pink_a1', 1.0), ('grss_dant_pink_a2', 1.0)]),
}
WATER_SHADER = 'wter_dant_lake'

# flora families (appearance/<name>.apt, stock): the stock Dantooine child parameters (displacement 0.01, period 0.1)
def _trees(names, mn=0.5, mx=1.0, weight=1.0):
    return [tree(n + '.apt', weight, 0, 0.01, 0.1, 0, 1, mn, mx) for n in names]


def _rocks(names):
    return [tree(n + '.apt', 1.0, 0, 0.01, 0.1, 1, 0, 1.0, 1.0) for n in names]


FLORA = {
    'plains_trees': (1, 'plains trees', 0.35, 0, _trees(['decd_blba_tree', 'decd_blba_tree_a1', 'decd_oaktreeleaves', 'decd_oaktreeleaves_a1',
                                                            'decd_hollytreeleaves', 'decd_whitebirchtreeleaves'])),
    'forest_trees': (2, 'forest trees', 1.0, 0, _trees(['decd_mapletreeleaves', 'decd_mapletreeleaves_a1', 'decd_mapletreeleaves_a2', 'decd_tallbirch',
                                                            'decd_tallbirchb', 'decd_ginkgotreeleaves', 'decd_dogwoodtreeleaves', 'decd_oakstump_sm'], 0.6, 1.1)),
    'pines': (3, 'mountain pines', 0.7, 0, _trees(['conf_mtns_pine_full', 'conf_mtns_pine_broken', 'conf_mtns_sparse'], 0.7, 1.2)),
    'rocks': (4, 'rocks', 0.5, 0, _rocks(['mtns_rock_grey', 'mtns_rock_moss_a2', 'mtns_rock_moss_a3', 'mtns_rock_grey_a4', 'rock_dant', 'rock_dant_a1'])),
    'plains_under': (5, 'plains undergrowth', 1.0, 0, _trees(['core_leaf_razorgrass_frst', 'core_leaf_razorgrass_mtns', 'flow_catalpaflower', 'flow_poppies_sm',
                                                                 'leaf_forestsprout'], 0.5, 1.0)),
    'forest_under': (6, 'forest undergrowth', 1.0, 0, _trees(['leaf_forestsprout', 'leaf_forestsprout_a2', 'leaf_bamboo_sm', 'decd_saplingclump_sm',
                                                                 'decd_saplingclump_sm_a1', 'decd_bush_dead01'], 0.5, 1.0)),
    'lillypads': (7, 'lillypads', 1.0, 1, _rocks(['frst_fltg_lillypad1', 'frst_fltg_lillypad_a1', 'frst_fltg_lillypad_cluster'])),
}

# radial families (shader/<name>.sht, stock): the stock Dantooine child parameters
def _near(names, weight=3.0, w=1.2, hmin=0.15, hmax=0.25, dist=10.0):
    return [radial(n, weight, dist, w, w, 1, hmin, hmax, 1) for n in names]


def _far(names):
    return [radial(n, 1.0, 10.0, 5.0, 10.0, 0, 0.25, 0.35, 0) for n in names]


RADIAL = {
    'plains_grass': (1, 'plains grass', [('radl_dant_grassflowers_a1', 3.0), ('radl_dant_grassflowers', 3.0), ('radl_flow_purplejd', 0.5)]),
    'ferns': (2, 'forest ferns', [('radl_endr_fern_green_longleaf', 1.0), ('radl_endr_fern_green_longleaf_a1', 1.0), ('radl_endr_fern_olive', 1.0), ('radl_darkfrstgrass', 1.0)]),
    'far_trees': (3, 'far trees', ['radl_decd_assorttrees_a1', 'radl_decd_assorttrees']),
    'tufts': (4, 'mountain tufts', [('radl_dsrt_grss_tuft_a1', 1.0), ('radl_grss_dsrt_tuft_a2', 1.0)]),
    'far_pines': (5, 'far pines', ['radl_ever_pinetree_far']),
    'meadow': (6, 'benchland meadow', [('radl_flow_purplejd', 1.0), ('radl_flower_poppy_red', 1.0), ('radl_grss_dant_yellow', 2.0), ('radl_grss_dant_yellow_a1', 2.0)]),
}

ENVS = {'plains': 1, 'forest': 2, 'mountains': 3, 'benchland': 4, 'canyon': 5, 'knossa': 6}
FRACTALS = {
    'hills': dict(fid=1, name='hills', seed=137, octaves=3, octaves_param=2.0, amplitude=0.5, freq=0.0022, comb=0),
    'ridges': dict(fid=2, name='mountains ridged', seed=3996, octaves=4, octaves_param=2.1, amplitude=0.55, freq=0.0016, comb=2),
    'forest': dict(fid=3, name='forest patches', seed=77, octaves=2, octaves_param=2.5, amplitude=0.4, freq=0.0009, comb=0),
    'detail': dict(fid=4, name='fine relief', seed=4242, octaves=2, octaves_param=2.0, amplitude=0.5, freq=0.02, comb=0),
    'bench': dict(fid=5, name='benchland texture', seed=911, octaves=2, octaves_param=2.0, amplitude=0.5, freq=0.004, comb=0),
}
HILLS_HEIGHT, DETAIL_HEIGHT, BENCH_TEXTURE = 90.0, 6.0, 10.0
FOREST_BAND = (0.56, 1.0)
HIGHLAND_BAND, SUMMIT_FROM = (140.0, 230.0), 230.0


# ---------------------------------------------------------------- painted bitmaps (256 px, south row first)
def _smooth(v):
    v = 0.0 if v < 0 else 1.0 if v > 1 else v
    return v * v * (3 - 2 * v)


def bench_value(x, y):
    dx, dy = x - BENCH['cx'], y - BENCH['cy']
    theta = math.atan2(dy, dx)
    wobble = 1.0 + 0.10 * math.sin(3 * theta + 0.7) + 0.06 * math.sin(5 * theta - 1.9) + 0.04 * math.sin(8 * theta + 2.3)
    rn = math.sqrt((dx / BENCH['rx']) ** 2 + (dy / BENCH['ry']) ** 2) / wobble
    mean_r = (BENCH['rx'] + BENCH['ry']) / 2 * wobble
    return _smooth((1.0 - rn) * mean_r / BENCH['falloff'])


def _dist_to_polyline(x, y, pts):
    best = float('inf')
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        vx, vy = bx - ax, by - ay
        t = ((x - ax) * vx + (y - ay) * vy) / (vx * vx + vy * vy)
        t = 0.0 if t < 0 else 1.0 if t > 1 else t
        d = math.hypot(x - (ax + t * vx), y - (ay + t * vy))
        if d < best:
            best = d
    return best


def canyon_value(x, y):
    d = _dist_to_polyline(x, y, CANYON['path'])
    w0 = CANYON['floor_half_width'] * (1.0 + 0.35 * math.sin(x * 0.0041 + y * 0.0023))
    if d <= w0:
        return 1.0
    return _smooth(1.0 - (d - w0) / CANYON['wall'])


def mesa_value(x, y):
    d = _dist_to_polyline(x, y, CANYON['path'])
    w0 = CANYON['mesa_half_width'] * (1.0 + 0.25 * math.sin(x * 0.0017 - y * 0.0013) + 0.15 * math.sin(y * 0.0031))
    if d <= w0:
        return 1.0
    return _smooth(1.0 - (d - w0) / CANYON['mesa_falloff'])


def paint(rect, fn, res=256):
    x0, y0, x1, y1 = rect
    rows = []
    for r in range(res):              # row 0 = south edge
        y = y0 + (r + 0.5) * (y1 - y0) / res
        # 254 at most: a 255 pixel is exactly 1.0 in the bitmap filter, the top of its (min, max) window, and whether
        # that passes depends on float rounding (Core3 clamps 1.0f to 0.99999; our port now does the same)
        rows.append([min(254, int(round(255 * fn(x0 + (c + 0.5) * (x1 - x0) / res, y)))) for c in range(res)])
    return rows


# ---------------------------------------------------------------- assembling the terrain

def groups():
    sgrp = form('SGRP', form('0006', *[shader_family(fid, name, '', (255, 255, 0), kids) for fid, name, kids in SHADERS.values()]))
    fgrp = form('FGRP', form('0008', *[flora_family(fid, name, (255, 255, 0), dens, kids, water) for fid, name, dens, water, kids in FLORA.values()]))
    rfams = []
    for fid, name, kids in RADIAL.values():
        children = _far(kids) if isinstance(kids[0], str) else _near([k for k, _ in kids])
        if not isinstance(kids[0], str):
            children = [radial(k, w, 10.0, 1.2, 1.2, 1, 0.15, 0.25, 1) for k, w in kids]
        rfams.append(radial_family(fid, name, (255, 255, 0), 1.0, children))
    rgrp = form('RGRP', form('0003', *rfams))
    egrp = form('EGRP', form('0002', *[environment_family(eid, 'ossus_' + name) for name, eid in ENVS.items()]))
    mgrp = form('MGRP', form('0000', *[fractal(f['fid'], f['name'], f['seed'], f['octaves'], f['octaves_param'], f['amplitude'],
                                               f['freq'], f['freq'] * (1.3 if f['comb'] == 2 else 1.0), f['comb']) for f in FRACTALS.values()]))
    bgrp = form('MGRP', form('0000', bitmap_family(1, 'academy benchland', BENCH['tga']), bitmap_family(2, 'imhar canyon', CANYON['tga']),
                             bitmap_family(3, 'canyon country mesa', CANYON['mesa_tga'])))
    return sgrp, fgrp, rgrp, egrp, mgrp, bgrp


def S(key):
    return SHADERS[key][0]


def F(key):
    return FLORA[key][0]


def R(key):
    return RADIAL[key][0]


def clear_flora(prefix):
    """Remove every flora and radial family (stock pattern: op 1 with remove_all = 1)."""
    return [affector_flora_collidable(prefix + ' no trees', F('plains_trees'), remove_all=1),
            affector_flora_non_collidable(prefix + ' no bushes', F('plains_under'), remove_all=1),
            affector_radial_near(prefix + ' no grass', R('plains_grass'), remove_all=1),
            affector_radial_far(prefix + ' no far', R('far_trees'), remove_all=1)]


def road_pieces(points, piece_len, sample_len, height_fn, end_height=None):
    """Cut the polyline into pieces at most piece_len long (Core3's AffectorRoad applies a road only within 500 m
    of its start point), each a 2-point road with one HDTA segment sampled every sample_len along it."""
    pieces = []
    for (ax, ay), (bx, by) in zip(points, points[1:]):
        leg = math.hypot(bx - ax, by - ay)
        n = max(1, int(math.ceil(leg / piece_len)))
        for i in range(n):
            t0, t1 = i / n, (i + 1) / n
            p0 = (round(ax + (bx - ax) * t0, 1), round(ay + (by - ay) * t0, 1))
            p1 = (round(ax + (bx - ax) * t1, 1), round(ay + (by - ay) * t1, 1))
            m = max(2, int(math.ceil(math.hypot(p1[0] - p0[0], p1[1] - p0[1]) / sample_len)) + 1)
            seg = []
            for k in range(m):
                t = k / (m - 1)
                x, y = p0[0] + (p1[0] - p0[0]) * t, p0[1] + (p1[1] - p0[1]) * t
                seg.append((x, round(height_fn(x, y), 2), y))
            pieces.append((p0, p1, seg))
    if end_height is not None:
        p0, p1, seg = pieces[-1]
        seg = seg[:-1] + [(seg[-1][0], end_height, seg[-1][2])]
        pieces[-1] = (p0, p1, seg)
    return pieces


def smooth_segment(seg, passes=2):
    out = list(seg)
    for _ in range(passes):
        out = [out[0]] + [(x, round((out[i - 1][1] + z + out[i + 1][1]) / 3, 2), y) for i, (x, z, y) in enumerate(out) if 0 < i < len(out) - 1] + [out[-1]]
    return out


def assemble(p):
    """p: dict of the heights read from the earlier passes (pad, water, bench, canyon, temple, caves, road pieces)."""
    sgrp, fgrp, rgrp, egrp, mgrp, bgrp = groups()
    H = FRACTALS
    lyrs = []
    lyrs.append(layer('base: rolling hills',
                      affector_height_fractal('hills', H['hills']['fid'], 0, HILLS_HEIGHT),
                      affector_shader_constant('grass', S('grass')),
                      affector_environment('plains', ENVS['plains']),
                      affector_radial_near('plains grass', R('plains_grass')),
                      affector_radial_far('far trees', R('far_trees'), feather_type=1, feather=0.5),
                      affector_flora_collidable('scattered trees', F('plains_trees'), feather_type=1, feather=0.5),
                      affector_flora_non_collidable('undergrowth', F('plains_under'), feather_type=1, feather=0.4)))
    lyrs.append(layer('fine relief', affector_height_fractal('detail', H['detail']['fid'], 1, DETAIL_HEIGHT)))
    lyrs.append(layer('forests',
                      filter_fractal('forest patches', H['forest']['fid'], FOREST_BAND[0], FOREST_BAND[1], feather_type=3, feather=0.4),
                      affector_shader_constant('forest floor', S('forest'), feather_type=1, feather=0.5),
                      affector_environment('forest', ENVS['forest'], feather=0.5),
                      affector_flora_collidable('forest trees', F('forest_trees'), feather_type=1, feather=0.3),
                      affector_flora_non_collidable('forest undergrowth', F('forest_under'), feather_type=1, feather=0.3),
                      affector_radial_near('ferns', R('ferns'), remove_all=1)))
    lyrs.append(layer('eocho mountains (south edge)',
                      boundary_rect('south band', *MOUNTAINS['rect'], feather_type=3, feather=MOUNTAINS['feather']),
                      affector_height_fractal('ridges', H['ridges']['fid'], 1, MOUNTAINS['height']),
                      affector_environment('mountains', ENVS['mountains'], feather=0.5)))
    lyrs.append(layer('highlands',
                      filter_height('highland band', HIGHLAND_BAND[0], HIGHLAND_BAND[1], feather_type=1, feather=0.3),
                      affector_shader_constant('dry grass', S('dry'), feather_type=1, feather=0.5),
                      affector_flora_collidable('pines', F('pines'), feather_type=1, feather=0.4),
                      affector_radial_near('tufts', R('tufts'), remove_all=1),
                      affector_radial_far('far pines', R('far_pines'), remove_all=1)))
    lyrs.append(layer('summits',
                      filter_height('above the highlands', SUMMIT_FROM, 2000.0, feather_type=1, feather=0.2),
                      affector_shader_constant('limestone', S('summit'), feather_type=1, feather=0.4),
                      *clear_flora('summit'),
                      affector_radial_near('summit tufts', R('tufts'))))
    lyrs.append(layer('academy benchland',
                      boundary_rect('bitmap frame', *BENCH['rect'], feather_type=0, feather=0.0),
                      filter_bitmap('painted benchland', 1),
                      affector_height_constant('raise to the bench', 0, p['bench_height']),
                      layer('benchland surface',
                            affector_height_fractal('bench texture', H['bench']['fid'], 1, BENCH_TEXTURE),
                            affector_shader_constant('meadow', S('bench'), feather_type=1, feather=0.3),
                            affector_environment('benchland', ENVS['benchland'], feather=0.5),
                            affector_radial_near('meadow flowers', R('meadow'), remove_all=1),
                            affector_flora_collidable('benchland rocks', F('rocks'), feather_type=1, feather=0.5))))
    lyrs.append(layer('canyon country (upland)',
                      boundary_rect('bitmap frame', *CANYON['rect'], feather_type=0, feather=0.0),
                      filter_bitmap('painted mesa', 3),
                      affector_height_constant('raise to the mesa', 0, p['mesa_height']),
                      layer('mesa surface',
                            affector_height_fractal('mesa texture', H['bench']['fid'], 1, BENCH_TEXTURE),
                            affector_shader_constant('dry grass', S('dry'), feather_type=1, feather=0.3),
                            affector_flora_collidable('mesa rocks', F('rocks'), feather_type=1, feather=0.5),
                            affector_radial_near('mesa tufts', R('tufts'), remove_all=1))))
    lyrs.append(layer('imhar canyon',
                      boundary_rect('bitmap frame', *CANYON['rect'], feather_type=0, feather=0.0),
                      filter_bitmap('painted canyon', 2),
                      affector_height_constant('cut to the floor', 0, p['canyon_floor']),
                      layer('canyon floor',
                            affector_shader_constant('canyon floor', S('canyon_floor'), feather_type=1, feather=0.2),
                            affector_environment('canyon', ENVS['canyon'], feather=0.3),
                            *clear_flora('canyon'),
                            affector_flora_collidable('canyon rocks', F('rocks'), feather_type=1, feather=0.5)),
                      layer('canyon walls',
                            filter_slope('wall slopes', 22.0, 90.0, feather_type=0, feather=0.2),
                            affector_shader_constant('canyon wall', S('canyon_wall')))))
    lyrs.append(layer('lake basin',
                      boundary_circle('basin', LAKE['cx'], LAKE['cy'], LAKE['radius'], feather_type=3, feather=LAKE['feather']),
                      affector_height_constant('sink below the water', 0, p['water'] - LAKE['below_water'])))
    lyrs.append(layer('lake bed and shore',
                      filter_height('under and just above the water', -100.0, p['water'] + 1.5, feather_type=1, feather=0.3),
                      affector_shader_constant('lake bed', S('lakebed'), feather_type=1, feather=0.4),
                      *clear_flora('shore'),
                      affector_flora_non_collidable('lillypads', F('lillypads'), feather_type=1, feather=0.5)))
    lyrs.append(layer('mossy valleys',
                      filter_height('low ground', p['water'] + 1.5, p['water'] + 9.0, feather_type=1, feather=0.6),
                      affector_shader_constant('moss', S('moss'), feather_type=1, feather=0.5)))
    lyrs.append(layer('cliff slopes',
                      filter_slope('steep', 24.0, 90.0, feather_type=0, feather=0.2),
                      affector_shader_constant('cliff rock', S('cliff'), feather_type=1, feather=0.0),
                      *clear_flora('cliff')))
    lyrs.append(layer('knossa landing pad (flattened)',
                      boundary_circle('pad', PAD['cx'], PAD['cy'], PAD['radius'], feather_type=3, feather=PAD['feather']),
                      affector_height_constant('flatten to local ground', 0, p['pad_height'])))
    lyrs.append(layer('knossa clearing',
                      boundary_circle('clearing', PAD['cx'], PAD['cy'], PAD['clearing'], feather_type=1, feather=0.3),
                      affector_shader_constant('packed dirt', S('road'), feather_type=1, feather=0.6),
                      affector_environment('knossa', ENVS['knossa'], feather=0.5),
                      *clear_flora('pad')))
    if p.get('temple'):
        t = p['temple']
        lyrs.append(layer('academy ruins pad (flattened)',
                          boundary_circle('ruins', t['x'], t['y'], t['radius'], feather_type=3, feather=0.4),
                          affector_height_constant('flatten', 0, t['height']),
                          layer('ruins clearing', boundary_circle('clearing', t['x'], t['y'], t['radius'] + 60.0, feather_type=1, feather=0.3),
                                *clear_flora('ruins'))))
    for i, (p0, p1, seg) in enumerate(p.get('road', [])):
        lyrs.append(layer('knossa road %02d' % (i + 1),
                          affector_road('road', [p0, p1], [seg], ROAD['width'], S('road'), feather_type=3, feather=0.15, feather_shader=3,
                                        feather_shader_distance=0.2)))
    if p.get('road'):
        pts = [p['road'][0][0]] + [piece[1] for piece in p['road']]
        lyrs.append(layer('knossa road clearing', boundary_polyline('verge', pts, ROAD['width'] * 1.4, feather_type=0, feather=0.0),
                          *clear_flora('road')))
    for i, c in enumerate(p.get('caves', [])):
        lyrs.append(layer('cave %d mouth' % (i + 1),
                          boundary_circle('apron', c['x'], c['y'], 30.0, feather_type=3, feather=0.5),
                          affector_height_constant('level apron', 0, c['height']),
                          affector_shader_constant('rock mouth', S('cliff'), feather_type=1, feather=0.3),
                          *clear_flora('cave'),
                          layer('hole', boundary_circle('mouth', c['x'], c['y'], 9.0, feather_type=0, feather=0.0), affector_exclude('terrain hole'))))
    tgen = form('TGEN', form('0000', sgrp, fgrp, rgrp, egrp, mgrp, bgrp, form('LYRS', *lyrs)))
    head = header_chunk('terrain/ossus.trn', SIZE, CHUNK, TILES, True, p['water'], WATER_SHADER, TIME_CYCLE, FLORA_BLOCKS)
    return build([form('PTAT', form('0014', head, tgen, maps_form(SIZE, CHUNK)))])


# ---------------------------------------------------------------- evaluation helpers

def make_evaluator(data, bitmaps):
    trn = trn_read.read_trn(data)
    loader = lambda name: trn_read.load_tga_grey(bitmaps[name])  # noqa: E731
    return trn, RoadHeightEvaluator(trn, loader)


def survey_grid(ev, step):
    """heights[j][i], row 0 = north edge, col 0 = west edge; cell centres."""
    n = int(SIZE / step)
    grid = []
    for j in range(n):
        y = HALF - (j + 0.5) * step
        grid.append([ev.height(-HALF + (i + 0.5) * step, y) for i in range(n)])
    return grid


def cell_xy(i, j, step):
    return -HALF + (i + 0.5) * step, HALF - (j + 0.5) * step


def window_stats(grid, i, j, r):
    vals = [grid[jj][ii] for jj in range(max(0, j - r), min(len(grid), j + r + 1)) for ii in range(max(0, i - r), min(len(grid), i + r + 1))]
    return min(vals), max(vals), sum(vals) / len(vals)


def probe(ev, x, y, radius, step=10.0):
    """Flatness over a disc: spread, steepest step between neighbouring samples on the two axes, mean."""
    hs = []
    xs = []
    v = -radius
    while v <= radius + 1e-6:
        xs.append(v)
        v += step
    centre = ev.height(x, y)
    for dx in xs:
        for dy in xs:
            if dx * dx + dy * dy <= radius * radius:
                hs.append(ev.height(x + dx, y + dy))
    steps = []
    for dx in xs:
        line = [ev.height(x + dx, y + dy) for dy in xs]
        steps += [abs(b - a) for a, b in zip(line, line[1:])]
    return {'centre': round(centre, 2), 'mean': round(sum(hs) / len(hs), 2), 'spread': round(max(hs) - min(hs), 2),
            'steepest_%dm_step' % int(step): round(max(steps), 2), 'samples': len(hs)}


def pick_sites(grid, step, water, bench_fn, probe_ev):
    """Candidate sites from the 64 m survey: flattest windows per region, and three hillside cave mouths."""
    n = len(grid)

    def relief(i, j, r):
        lo, hi, mean = window_stats(grid, i, j, r)
        return hi - lo, mean

    # the Academy ruins: flattest 5x5 window (320 m) fully on the benchland
    best = None
    for j in range(2, n - 2):
        for i in range(2, n - 2):
            x, y = cell_xy(i, j, step)
            if bench_fn(x, y) < 0.98:
                continue
            rel, mean = relief(i, j, 2)
            if best is None or rel < best[0]:
                best = (rel, x, y, mean)
    temple = {'x': best[1], 'y': best[2], 'radius': 130.0, 'height': round(best[3], 1), 'survey_relief_320m': round(best[0], 1)}

    # camps: flattest 3x3 windows (192 m) in four regions, above the water, away from the pad, the benchland and the canyon
    regions = {
        'camp_west_plains': lambda x, y: -7000 < x < -1500 and -3500 < y < 500,
        'camp_north_hills': lambda x, y: -4500 < x < 1000 and 3200 < y < 7000,
        'camp_east_canyon_rim': lambda x, y: 2600 < x < 7200 and -4200 < y < -2600 and 0.9 < mesa_value(x, y),
        'camp_south_foothills': lambda x, y: -6500 < x < 6500 and -4700 < y < -4100,
    }
    camps = []
    for name, inside in regions.items():
        best = None
        for j in range(1, n - 1):
            for i in range(1, n - 1):
                x, y = cell_xy(i, j, step)
                if not inside(x, y) or grid[j][i] < water + 4 or math.hypot(x - PAD['cx'], y - PAD['cy']) < 700:
                    continue
                rel, mean = relief(i, j, 1)
                if best is None or rel < best[0]:
                    best = (rel, x, y, mean)
        camps.append({'name': name, 'x': best[1], 'y': best[2], 'height': round(best[3], 1), 'survey_relief_192m': round(best[0], 1)})

    # cave mouths: a cell on a hillside (rise of 10-28 m to an uphill neighbour) with level ground on the downhill side;
    # the best candidates are then probed at 10 m so the slope by the mouth is a hillside, not a cliff
    caves = []
    zones = [('cave_foothills_west', lambda x, y: -6500 < x < -1500 and -5400 < y < -4700),
             ('cave_foothills_east', lambda x, y: 1500 < x < 6500 and -5400 < y < -4700),
             ('cave_north', lambda x, y: -3000 < x < 3000 and 4500 < y < 7500)]
    for name, inside in zones:
        cands = []
        for j in range(2, n - 2):
            for i in range(2, n - 2):
                x, y = cell_xy(i, j, step)
                if not inside(x, y) or grid[j][i] < water + 6:
                    continue
                h = grid[j][i]
                for di, dj, heading in ((1, 0, 90), (-1, 0, 270), (0, -1, 0), (0, 1, 180)):   # uphill direction
                    up = grid[j + dj][i + di] - h
                    down = h - grid[j - dj][i - di]
                    if 10 <= up <= 28 and abs(down) <= 6:
                        cands.append((abs(up - 16) + abs(down), x, y, h, (heading + 180) % 360))   # the mouth faces downhill
                        break
        cands.sort()
        for score, x, y, h, heading in cands[:25]:
            pr = probe(probe_ev, x, y, 25.0)
            if pr['steepest_10m_step'] <= 4.0 and 3.0 <= pr['spread'] <= 14.0:
                caves.append({'name': name, 'x': x, 'y': y, 'height': round(h, 1), 'mouth_faces_deg': heading, 'hillside_probe_before_apron': pr})
                break
    return temple, camps, caves


def write_png(path, rows):
    import zlib
    raw = b''.join(b'\x00' + bytes(r) for r in rows)

    def chunk(tag, data):
        return struct.pack('>I', len(data)) + tag + data + struct.pack('>I', zlib.crc32(tag + data) & 0xffffffff)
    png = b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', len(rows[0]), len(rows), 8, 0, 0, 0, 0))
    png += chunk(b'IDAT', zlib.compress(raw, 9)) + chunk(b'IEND', b'')
    with open(path, 'wb') as f:
        f.write(png)


def preview(grid, water, marks, path, gamma=0.5):
    lo = min(min(r) for r in grid)
    hi = max(max(r) for r in grid)
    rows = []
    for r in grid:
        rows.append([96 if h < water else int(255 * ((h - lo) / (hi - lo)) ** gamma) for h in r])
    n = len(grid)
    for x, y in marks:
        i, j = int((x + HALF) / SIZE * n), int((HALF - y) / SIZE * n)
        for d in range(-3, 4):
            for ii, jj in ((i + d, j), (i, j + d)):
                if 0 <= ii < n and 0 <= jj < n:
                    rows[jj][ii] = 255 if d else 0
    write_png(path, rows)
    return lo, hi


# ---------------------------------------------------------------- verification (as the prototype, plus the new pieces)

def structure_pairs(nodes, parent='<root>'):
    pairs = set()
    for n in nodes:
        label = f'FORM {n.form}' if n.is_form else n.tag
        pairs.add((parent, label))
        if n.is_form:
            pairs |= structure_pairs(n.children, label)
    return pairs


def verify(data, label, bitmaps, out=print):
    rep = {'file': label, 'bytes': len(data)}
    nodes = parse(data)
    rep['round_trip_identical'] = build(nodes) == data
    out(f'1. byte round trip: {"IDENTICAL" if rep["round_trip_identical"] else "DIFFERENT"}')
    trn = trn_read.read_trn(data)
    # FBIT is written stock-length (24 bytes: the client's gain float follows the 20 Core3 reads), so that note is expected
    unexpected = [n for n in trn['notes'] if not n.endswith('FBIT: 4 bytes after the fields Core3 reads')]
    rep['core3_order_notes'] = trn['notes']
    rep['core3_order_notes_unexpected'] = unexpected
    rep['rule_counts'] = trn_read.count_rules(trn['layers'])
    out(f'2. Core3-order re-read: version {trn["version"]}, {len(trn["layers"])} top layers, {len(trn["notes"])} notes '
        f'({len(unexpected)} unexpected)' + (': ' + '; '.join(unexpected) if unexpected else '') + f'; rules {rep["rule_counts"]}')
    stock = set()
    for ref in ('terrain/tutorial.trn', 'terrain/simple.trn', 'terrain/tatooine.trn', 'terrain/dantooine.trn', 'terrain/hoth.trn'):
        d = client_file(ref)
        if d:
            stock |= structure_pairs(parse(d))
    novel = sorted(structure_pairs(nodes) - stock)
    rep['structure_pairs_not_in_stock'] = [f'{a} > {b}' for a, b in novel]
    out(f'3. structure vs stock tutorial/simple/tatooine/dantooine + MTG hoth: {len(novel)} parent/child pairs not seen'
        + (': ' + ', '.join(rep['structure_pairs_not_in_stock']) if novel else ''))
    idx = client_index()
    missing = []
    for fam in trn['shaders']:
        for c in fam['children']:
            if ('shader/' + c['shader'] + '.sht').lower() not in idx:
                missing.append('shader ' + c['shader'])
    if ('shader/' + trn['header']['global_water_shader'] + '.sht').lower() not in idx:
        missing.append('water shader ' + trn['header']['global_water_shader'])
    for fam in trn['flora']:
        for c in fam['children']:
            if ('appearance/' + c['appearance']).lower() not in idx:
                missing.append('flora ' + c['appearance'])
    for fam in trn['radial']:
        for c in fam['children']:
            if ('shader/' + c['shader'] + '.sht').lower() not in idx:
                missing.append('radial ' + c['shader'])
    for b in trn['bitmaps'].values():
        if b['file'] not in bitmaps and b['file'].lower() not in idx:
            missing.append('bitmap ' + b['file'])
    rep['references_missing'] = missing
    rep['reference_counts'] = {'shaders': sum(len(f['children']) for f in trn['shaders']), 'flora': sum(len(f['children']) for f in trn['flora']),
                               'radial': sum(len(f['children']) for f in trn['radial']), 'bitmaps': len(trn['bitmaps'])}
    out(f'4. references ({rep["reference_counts"]}): missing {missing or "none"}')
    ok = rep['round_trip_identical'] and not unexpected and not novel and not missing
    rep['verdict'] = 'PASS' if ok else 'CHECK'
    return rep, trn


# ---------------------------------------------------------------- build

def build_all(out=print):
    t0 = time.time()
    os.makedirs(os.path.join(STAGED, 'terrain'), exist_ok=True)
    os.makedirs(OUT, exist_ok=True)
    # painted bitmaps (written now; the TGA round trip is part of the report)
    bitmaps = {}
    tga_checks = {}
    for name, rect, fn, res in ((BENCH['tga'], BENCH['rect'], bench_value, 256), (CANYON['tga'], CANYON['rect'], canyon_value, CANYON['tga_res']),
                                (CANYON['mesa_tga'], CANYON['rect'], mesa_value, 256)):
        rows = paint(rect, fn, res)
        path = os.path.join(STAGED, name.replace('/', os.sep))
        write_tga_grey(path, res, res, rows)
        with open(path, 'rb') as f:
            bitmaps[name] = f.read()
        w, h, back = read_tga_grey(bitmaps[name])
        edge = max(max(rows[0]), max(rows[-1]), max(r[0] for r in rows), max(r[-1] for r in rows))
        tga_checks[name] = {'bytes': len(bitmaps[name]), 'resolution': res, 'round_trip_identical': back == rows,
                            'core3_loader_accepts': trn_read.load_tga_grey(bitmaps[name]) is not None,
                            'max_value_on_frame_edge': edge}   # 0 means the painted shape ends inside its frame (no hard edge)
    out(f'bitmaps: {tga_checks}')

    # pass 0: draft without pad/bench/canyon/lake heights known -> read the ground, set the water table
    p = {'pad_height': 0.0, 'water': 14.0, 'bench_height': 0.0, 'canyon_floor': 0.0, 'mesa_height': 0.0}
    draft = assemble(p)
    trn0 = trn_read.read_trn(draft)
    base_layers = [l for l in trn0['layers'] if l['name'] in ('base: rolling hills', 'fine relief', 'eocho mountains (south edge)')]
    ev0 = RoadHeightEvaluator(dict(trn0, layers=base_layers))
    samples = sorted(ev0.height(x, y) for x in _frange(-HALF + 256, HALF, 512) for y in _frange(-HALF + 256, HALF, 512))
    p['water'] = round(samples[int(len(samples) * WATER_PERCENTILE)] * 2) / 2
    p['pad_height'] = round(ev0.height(PAD['cx'], PAD['cy']), 1)
    bench_ground = ev0.height(BENCH['cx'], BENCH['cy'])
    p['bench_height'] = round(bench_ground + BENCH['rise'], 1)
    p['canyon_floor'] = p['water'] + CANYON['floor_above_water']
    p['mesa_height'] = CANYON['mesa_height']
    out(f'pass 0 ({time.time() - t0:.0f} s): water {p["water"]} m (p{int(WATER_PERCENTILE * 100)} of the plains), pad {p["pad_height"]} m, '
        f'benchland {p["bench_height"]} m (ground {bench_ground:.1f} + {BENCH["rise"]}), mesa {p["mesa_height"]} m, canyon floor {p["canyon_floor"]} m')

    # pass 1: everything but the ruins pad, the road and the caves -> survey and pick sites
    trn1, ev1 = make_evaluator(assemble(p), bitmaps)
    step = 64.0
    grid = survey_grid(ev1, step)
    out(f'pass 1 ({time.time() - t0:.0f} s): surveyed {len(grid) ** 2} cells at {step:.0f} m')
    temple, camps, caves = pick_sites(grid, step, p['water'], bench_value, ev1)
    temple['height'] = round(ev1.height(temple['x'], temple['y']), 1)
    for c in caves:
        c['height'] = round(ev1.height(c['x'], c['y']), 1)
    p['temple'] = temple
    p['caves'] = caves
    road_points = ROAD['points'] + [(round(temple['x'] - 40.0, 1), round(temple['y'] - temple['radius'] - 20.0, 1))]
    pieces = road_pieces(road_points, ROAD['piece'], ROAD['sample'], ev1.height, end_height=temple['height'])
    p['road'] = [(p0, p1, smooth_segment(seg)) for p0, p1, seg in pieces]
    out(f'sites: ruins {temple}; camps {[(c["name"], c["x"], c["y"]) for c in camps]}; caves {[(c["name"], c["x"], c["y"]) for c in caves]}; '
        f'road {len(p["road"])} pieces')

    # pass 2: final
    data = assemble(p)
    path = os.path.join(STAGED, 'terrain', 'ossus.trn')
    with open(path, 'wb') as f:
        f.write(data)
    out(f'wrote {path} ({len(data)} bytes)')
    rep, trn = verify(data, path, bitmaps, out)
    ev = RoadHeightEvaluator(trn, lambda name: trn_read.load_tga_grey(bitmaps[name]))
    step = 32.0
    grid = survey_grid(ev, step)
    flat = [h for r in grid for h in r]
    rep['height_survey'] = {'grid_step_m': step, 'samples': len(flat), 'min': round(min(flat), 1), 'max': round(max(flat), 1),
                            'mean': round(sum(flat) / len(flat), 1), 'below_water_share': round(sum(h < p['water'] for h in flat) / len(flat), 3),
                            'water_height': p['water']}
    out(f'5. heights on the {step:.0f} m grid: {rep["height_survey"]}')
    pad_profile = [ev.height(PAD['cx'], PAD['cy'] + d) for d in range(0, int(PAD['radius']) + 400, 10)]
    sites = {'starport_pad': {'x': PAD['cx'], 'y': PAD['cy'], 'radius': PAD['radius'], 'height': p['pad_height'],
                              'flat_inner_radius': round((1 - PAD['feather']) * PAD['radius']), 'probe': probe(ev, PAD['cx'], PAD['cy'], 80.0),
                              'steepest_10m_step_walking_north_out': round(max(abs(b - a) for a, b in zip(pad_profile, pad_profile[1:])), 2)},
             'academy_ruins': dict(temple, probe=probe(ev, temple['x'], temple['y'], temple['radius'] - 10.0)),
             'camps': [dict(c, probe=probe(ev, c['x'], c['y'], 60.0)) for c in camps],
             'caves': [dict(c, hole_radius=9.0, probe=probe(ev, c['x'], c['y'], 25.0)) for c in caves],
             'lake': {'x': LAKE['cx'], 'y': LAKE['cy'], 'radius': LAKE['radius'], 'centre_height': round(ev.height(LAKE['cx'], LAKE['cy']), 1)},
             'benchland': {'cx': BENCH['cx'], 'cy': BENCH['cy'], 'height': p['bench_height'], 'centre_probe': probe(ev, BENCH['cx'], BENCH['cy'], 60.0, 20.0)},
             'canyon': {'path': CANYON['path'], 'floor_height': p['canyon_floor'], 'mesa_height': p['mesa_height'],
                        'floor_probe': probe(ev, *CANYON['path'][3], 40.0, 10.0),
                        'mesa_top_350m_east_of_path_point_3': round(ev.height(CANYON['path'][3][0] + 350, CANYON['path'][3][1]), 1),
                        'wall_profile_east_from_path_point_3_every_20m': [round(ev.height(CANYON['path'][3][0] + d, CANYON['path'][3][1]), 1) for d in range(0, 361, 20)]},
             'road': {'points': road_points, 'pieces': len(p['road']), 'width': ROAD['width']},
             'water_height': p['water'], 'units': 'metres, world x east / y north, heights from the Core3 port (server view)'}
    # road agreement: the road's surface vs the natural ground it was sampled from
    diffs = []
    for p0, p1, seg in p['road']:
        for x, z, y in seg[1:-1]:
            diffs.append(abs(ev.height(x, y) - z))
    sites['road']['max_road_vs_ground_m'] = round(max(diffs), 2)
    sites['road']['mean_road_vs_ground_m'] = round(sum(diffs) / len(diffs), 2)
    rep['sites'] = {k: v for k, v in sites.items() if k in ('starport_pad', 'academy_ruins', 'camps', 'caves', 'road')}
    marks = [(PAD['cx'], PAD['cy']), (temple['x'], temple['y'])] + [(c['x'], c['y']) for c in camps] + [(c['x'], c['y']) for c in caves]
    lo, hi = preview(grid, p['water'], marks, os.path.join(OUT, 'ossus-height.png'))
    rep['preview'] = {'file': 'out/ossus-height.png', 'resolution': len(grid), 'heights': [round(lo, 1), round(hi, 1)],
                      'legend': 'north up; black low, white high (gamma 0.5); mid-grey = under water; crosses = pad, ruins, camps, caves'}
    rep['tga'] = tga_checks
    rep['heights_used'] = {k: v for k, v in p.items() if k in ('pad_height', 'water', 'bench_height', 'canyon_floor', 'mesa_height')}
    rep['seconds'] = round(time.time() - t0)
    out(f'6. sites: pad spread {sites["starport_pad"]["probe"]["spread"]} m; ruins spread {sites["academy_ruins"]["probe"]["spread"]} m; '
        f'camps spread {[c["probe"]["spread"] for c in sites["camps"]]}; caves {[c["probe"]["spread"] for c in sites["caves"]]}; '
        f'road vs ground max {sites["road"]["max_road_vs_ground_m"]} m')
    out(f'VERDICT: {rep["verdict"]} ({rep["seconds"]} s)')
    with open(os.path.join(OUT, 'ossus-report.json'), 'w', encoding='utf-8') as f:
        json.dump(rep, f, indent=1)
    with open(os.path.join(OUT, 'ossus-sites.json'), 'w', encoding='utf-8') as f:
        json.dump(sites, f, indent=1)
    return rep


def _frange(start, stop, step):
    v = start
    while v < stop:
        yield v
        v += step


def main(argv):
    if not argv or argv[0] not in ('build', 'verify'):
        print(__doc__)
        return 2
    if argv[0] == 'verify':
        with open(argv[1], 'rb') as f:
            data = f.read()
        bitmaps = {}
        for name in (BENCH['tga'], CANYON['tga'], CANYON['mesa_tga']):
            path = os.path.join(STAGED, name.replace('/', os.sep))
            if os.path.exists(path):
                with open(path, 'rb') as f:
                    bitmaps[name] = f.read()
        rep, _ = verify(data, argv[1], bitmaps)
        print('VERDICT:', rep['verdict'])
        return 0 if rep['verdict'] == 'PASS' else 1
    rep = build_all()
    return 0 if rep['verdict'] == 'PASS' else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
