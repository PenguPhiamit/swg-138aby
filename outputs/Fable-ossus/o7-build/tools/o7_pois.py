"""O7 point-of-interest layouts: stock statics and buildings for o6's POIs 1-6, 8-16, 18 (POI 7 is held, POI 17 is terrain
only). Our own code (Claude, 16 Oct 2026). Every template is a stock one (client object template table of the winning
patch_14 archive) except where the README says otherwise; no MTG art is used. Positions come from searches on the o7
terrain build, so heights are the server's.

    layouts = generate(Terrain, census, terrain_spec)  ->  (objects, pois, npc_points, notes)

yaw is a compass heading in degrees (0 = +z faces north, 90 = east), the convention of o2's stage_snapshot.py.
"""
import math

from o7_common import (KNOSSA, WATER, Terrain, bearing, circle_poly_overlap, dist, jload, obb, poly_overlap, rot, size_xz,
                       tinfo, EXISTING_WS)

# ---------------------------------------------------------------- template helpers
G = 'object/static/structure/general/shared_%s.iff'
DA = 'object/static/structure/dantooine/shared_%s.iff'
MIL = 'object/static/structure/military/shared_%s.iff'
TA = 'object/static/structure/tatooine/shared_%s.iff'
CO = 'object/static/structure/corellia/shared_%s.iff'
IT = 'object/static/item/shared_%s.iff'
BM = 'object/building/military/shared_%s.iff'
BG = 'object/building/general/shared_%s.iff'
BE = 'object/building/endor/shared_%s.iff'

CAVE_MOUTH = (0.26, 18.0)       # entrance of the three flatland cave layouts, building space (x, z): portal 0 of the .pob
CAVE_FLOOR = 3.85               # entrance floor height above the building origin (portal 0, lowest vertex)

ID_NOTE = 'ids are assigned by make_o7.py'


class Frame:
    """A local frame: origin (ox, oy), heading in compass degrees; lx right, lz forward."""

    def __init__(self, ox, oy, heading):
        self.ox, self.oy, self.heading = ox, oy, heading % 360.0

    def at(self, lx, lz):
        dx, dy = rot(lx, lz, self.heading)
        return self.ox + dx, self.oy + dy

    def yaw(self, a=0.0):
        return (self.heading + a) % 360.0


class Layout:
    def __init__(self, T):
        self.T = T
        self.objs = []

    def add(self, poi, template, x, y, yaw, role, building=False, z=None, group=None, dz=0.0):
        zz = (self.T.h(x, y) if z is None else z) + dz
        o = {'template': template, 'x': round(x, 1), 'y': round(y, 1), 'z': round(zz, 2), 'yaw': round(yaw % 360.0, 1), 'poi': poi, 'role': role,
             'kind': 'building' if building else 'static', 'group': group or role}
        self.objs.append(o)
        return o


def face(frm, to):
    """Heading that points +z from one point at another."""
    return bearing(frm, to)


def best_flat(T, c, search_r, foot_r, step=10.0, w_dist=0.02):
    """The point within search_r of c whose ground is flattest over foot_r (spread plus a small distance penalty)."""
    best = None
    n = int(search_r // step)
    for i in range(-n, n + 1):
        for j in range(-n, n + 1):
            x, y = c[0] + i * step, c[1] + j * step
            d = math.hypot(i * step, j * step)
            if d > search_r:
                continue
            lo, hi, sp = T.relief(x, y, foot_r, 4.0)
            sc = sp + d * w_dist
            if best is None or sc < best[0]:
                best = (sc, x, y, sp)
    return best[1], best[2], best[3]


# ---------------------------------------------------------------- existing ruins (31 statics already in the snapshot)

def existing_ruins():
    """(template, x, y, yaw) of the 31 ruin statics already in o2's ossus.ws."""
    import math as m
    from swgfmt import ws_read
    nodes, templates = ws_read.read_ws(open(EXISTING_WS, 'rb').read())
    out = []
    for n in nodes:
        if n['depth'] == 0 and 'static' in n['template']:
            q = n['quat']
            out.append((n['template'], n['x'], n['y'], m.degrees(2 * m.atan2(q[2], q[0])) % 360.0))
    return out


# ---------------------------------------------------------------- the points of interest

def poi1_ruins(L, spec, rng_seed=7):
    """Craters' debris (3 per large crater), the downed pod, the memorial ring."""
    cr = {c['id']: c for c in spec['design']['craters']}
    # (template, angle in degrees from east counter-clockwise, offset beyond the rim in metres)
    plan = {
        1: [(G % 'poi_all_construction_stone_pile', 205, 11), (G % 'transport_debris_02', 292, 13), (G % 'atst_debris_01', 100, 5)],
        2: [(G % 'poi_all_construction_stone_pile', 250, 11), (G % 'poi_all_construction_metal_pile', 20, 5), (G % 'prp_junk_s5', 140, 5)],
        3: [(G % 'atat_debris_01', 330, 8), (G % 'atst_debris_01', 90, 5), (G % 'poi_all_construction_metal_pile', 200, 5)],
        4: [(G % 'prp_junk_s5', 70, 5), (G % 'poi_all_construction_metal_pile', 250, 5), (G % 'atat_debris_02', 160, 5)],
    }
    for cid, items in plan.items():
        c = cr[cid]
        for k, (t, ang, off) in enumerate(items):
            a = math.radians(ang)
            x, y = c['cx'] + (c['radius'] + off) * math.cos(a), c['cy'] + (c['radius'] + off) * math.sin(a)
            L.add(1, t, x, y, (ang * 3 + cid * 37 + k * 53) % 360, 'crater %d debris' % cid, group='crater debris')
    # the pod on the south lip of crater 2: o6 put it at (2160, 2700), 92 m from the nearest crater, so it goes on the lip
    c2 = cr[2]
    a = math.atan2(2700 - c2['cy'], 2160 - c2['cx'])
    px, py = c2['cx'] + 17.0 * math.cos(a), c2['cy'] + 17.0 * math.sin(a)
    L.add(1, G % 'escape_pod', px, py, 25.0, 'downed drop pod (crater 2 south lip)', group='pod')
    ax = math.radians(math.degrees(a) + 9)
    L.add(1, G % 'escape_pod_door', c2['cx'] + 27.0 * math.cos(ax), c2['cy'] + 27.0 * math.sin(ax), 70.0, 'pod hatch', group='pod')
    # memorial: six standing pillar stubs in a ring, no names
    mx, my = 1960.0, 2780.0
    for k in range(6):
        ang = k * 60.0
        x, y = mx + 6.0 * math.cos(math.radians(ang)), my + 6.0 * math.sin(math.radians(ang))
        L.add(1, DA % 'dant_jedi_temple_pillar_sm', x, y, face((x, y), (mx, my)), 'memorial pillar %d of 6' % (k + 1), group='memorial')
    return {'centre': (2016.0, 2848.0), 'radius': 240.0, 'o6_point': (2016.0, 2848.0)}


def search_ring(L, T, fixed, centre, template, mouth_dist_range, step_a=5.0, step_d=6.0, pad=5.0, max_relief=9.0, avoid=()):
    """Place a flatland-cave style building whose mouth faces `centre`: the smallest mouth distance without overlaps."""
    best = None
    d = mouth_dist_range[0]
    while d <= mouth_dist_range[1]:
        a = 0.0
        while a < 360.0:
            mx, my = centre[0] + d * math.sin(math.radians(a)), centre[1] + d * math.cos(math.radians(a))
            yaw = bearing((mx, my), centre)
            dx, dy = rot(CAVE_MOUTH[0], CAVE_MOUTH[1], yaw)
            ox, oy = mx - dx, my - dy
            poly = obb(template, ox, oy, yaw, pad)
            ok = not any(poly_overlap(poly, p) for p in fixed) and not any(circle_poly_overlap(cx, cy, r, poly) for cx, cy, r in avoid)
            if ok:
                lo, hi, sp = T.relief(ox, oy, 28, 8)
                if sp <= max_relief and (best is None or sp * 0.5 + d < best[0]):
                    best = (sp * 0.5 + d, mx, my, yaw, ox, oy, sp)
            a += step_a
        if best:
            break
        d += step_d
    return best


def cave_building(L, T, poi, template, mx, my, yaw, role):
    dx, dy = rot(CAVE_MOUTH[0], CAVE_MOUTH[1], yaw)
    ox, oy = mx - dx, my - dy
    z = T.h(mx, my) - CAVE_FLOOR
    return L.add(poi, template, ox, oy, yaw, role, building=True, z=z, group='building')


def poi2_sanctuary(L, T, spec, ruins_fixed, craters):
    tpl = BG % 'cave_06_flatland_s01_damprock'
    fixed = [obb(t, x, y, yaw, 4.0) for t, x, y, yaw in ruins_fixed]
    fixed += [obb(o['template'], o['x'], o['y'], o['yaw'], 2.0) for o in L.objs if o['poi'] == 1]
    avoid = [(c['cx'], c['cy'], c['burn_radius'] + 14.0) for c in craters] + [(1960.0, 2780.0, 12.0)]
    best = search_ring(L, T, fixed, (2016.0, 2848.0), tpl, (120.0, 230.0), avoid=avoid)
    _, mx, my, yaw, ox, oy, sp = best
    cave_building(L, T, 2, tpl, mx, my, yaw, 'hidden sanctuary (cave, 12 cells)')
    f = Frame(mx, my, yaw)
    for side in (-1, 1):
        x, y = f.at(side * 16.0, 11.0)
        L.add(2, G % 'poi_all_construction_stone_pile', x, y, yaw + side * 40, 'rubble at the mouth', group='rubble')
        x, y = f.at(side * 6.5, 5.0)
        L.add(2, DA % 'dant_jedi_temple_pillar_fallen', x, y, yaw + 90 + side * 25, 'fallen pillar at the mouth', group='rubble')
    x, y = f.at(0.0, 14.0)
    L.add(2, DA % 'dant_jedi_temple_pillar_base', x, y, yaw, 'half-buried pillar base', group='rubble', dz=-1.0)
    return {'centre': (mx, my), 'radius': 45.0, 'o6_point': (2016.0, 2848.0), 'yaw': yaw, 'mouth': (mx, my), 'relief': sp}


def poi3_garrison(L, T, spec, craters):
    """Krayt's garrison on the benchland rim north-east of the ruins, with a small dig in front of its gate."""
    ruins = (2016.0, 2848.0)
    zr = T.h(*ruins)
    best = None
    # the flat ground (relief <= 3 m over r 40) nearest the crest of the benchland, in the arc from north-north-west to south-east of the ruins
    for b in range(-30, 121, 3):
        for d in range(240, 340, 5):
            x, y = ruins[0] + d * math.sin(math.radians(b)), ruins[1] + d * math.cos(math.radians(b))
            if min(dist((x, y), (c['cx'], c['cy'])) - c['burn_radius'] for c in craters) < 60:
                continue
            lo, hi, sp = T.relief(x, y, 40, 8)
            if sp > 3.0:
                continue
            edge = next((rr for rr in range(20, 200, 10)
                         if any(T.h(x + rr * math.cos(a * math.pi / 8), y + rr * math.sin(a * math.pi / 8)) < zr - 8 for a in range(16))), None)
            if edge is None:
                continue
            sc = edge + 5.0 * sp + d / 100.0
            if best is None or sc < best[0]:
                best = (sc, x, y, sp, b, d, edge)
    _, gx, gy, sp, b, d, edge = best
    gx, gy = round(gx), round(gy)
    h = bearing((gx, gy), ruins)
    F = Frame(gx, gy, h)
    P = 3
    # perimeter: 48 x 40 m, front (toward the ruins) at lz = +20 with an 8 m gate
    W32, W16, W8 = MIL % 'military_wall_strong_imperial_32_style_01', MIL % 'military_wall_strong_imperial_16_style_01', MIL % 'military_wall_strong_imperial_style_01'
    COL = MIL % 'military_column_strong_imperial_style_01'
    for (lx, lz, t, a) in ((-8, 20, W32, 0), (20, 20, W8, 0), (-8, -20, W32, 0), (16, -20, W16, 0),
                           (-24, -4, W32, 90), (-24, 16, W8, 90), (24, -4, W32, 90), (24, 16, W8, 90)):
        x, y = F.at(lx, lz)
        L.add(P, t, x, y, F.yaw(a), 'perimeter wall', group='fortification')
    for (lx, lz) in ((-24, 20), (24, 20), (-24, -20), (24, -20), (8, 20), (16, 20)):
        x, y = F.at(lx, lz)
        L.add(P, COL, x, y, F.yaw(), 'wall column', group='fortification')
    for lx in (9.6, 14.4):                          # just inside the gate columns
        x, y = F.at(lx, 17.6)
        L.add(P, G % 'banner_imperial_style_01', x, y, F.yaw(), 'banner at the gate', group='banner')
    # two guard towers just inside the front corners; the door (local -z) faces the courtyard, so +z points outward
    for lx, a in ((-29.0, -90), (29.0, 90)):        # outside the front corners, doors toward the compound
        x, y = F.at(lx, 22.5)
        L.add(P, BM % 'mun_all_military_tower_impl_guard_s01', x, y, F.yaw(a), 'guard tower', building=True, group='building')
    # officer's quarters and two barracks on the cardinal axes of the compound; their doors (local +z) face the courtyard
    for (lx, lz, t, a, role) in ((-12.0, -10.5, BM % 'military_base_shed_imperial_style_officer_s01', 0, "commander's quarters"),
                                 (13.0, -10.5, BM % 'military_base_shed_imperial_barracks_s01', 0, 'barracks 1'),
                                 (-13.5, 6.5, BM % 'military_base_shed_imperial_barracks_s01', 90, 'barracks 2')):
        x, y = F.at(lx, lz)
        L.add(P, t, x, y, F.yaw(a), role, building=True, group='building')
    for k, (lx, lz) in enumerate(((18, 4), (18, 7.4), (14.6, 5.7))):
        x, y = F.at(lx, lz)
        L.add(P, G % ('palette_supply_0%d' % (k + 1)), x, y, F.yaw(), 'supplies', group='props')
    for k, (lx, lz) in enumerate(((6, 4), (7.6, 5.2), (5, 6.5), (1, -4))):
        x, y = F.at(lx, lz)
        L.add(P, TA % 'debris_tatt_crate_1', x, y, F.yaw(30 * k), 'crates', group='props')
    for k, (lx, lz) in enumerate(((3, -3), (4.4, -2))):
        x, y = F.at(lx, lz)
        L.add(P, TA % 'debris_tatt_drum_storage_1', x, y, F.yaw(40 * k), 'drums', group='props')
    for lx, lz in ((-4.0, 12.0), (2.0, 14.0)):
        x, y = F.at(lx, lz)
        L.add(P, G % 'streetlamp_medium_style_01', x, y, F.yaw(), 'lamp post', group='props')
    x, y = F.at(0, 0)
    L.add(P, G % 'campfire_fresh', x, y, F.yaw(), 'brazier fire', group='props')
    # the dig: 36-62 m in front of the gate, on the way to the ruins
    for (lx, lz, t, a, role) in ((-14, 40, CO % 'corl_tent_med', 15, 'dig tent'), (8, 42, CO % 'corl_tent_med', -20, 'dig tent'),
                                 (-3, 56, CO % 'corl_tent_small', 5, 'dig tent'),
                                 (-18, 54, G % 'allum_mine_car_s01', 80, 'spoil cart'), (15, 54, G % 'allum_mine_car_s01', 100, 'spoil cart'),
                                 (-10, 62, G % 'allum_mine_bucket_s01', 10, 'spoil bucket'), (6, 62, G % 'allum_mine_bucket_s01', 70, 'spoil bucket'),
                                 (-3, 46, G % 'campfire_fresh', 0, 'dig fire'), (-8, 50, G % 'camp_cot_s01', 90, 'cot'), (3, 51, G % 'camp_cot_s01', 95, 'cot'),
                                 (-22, 46, DA % 'dant_jedi_temple_pillar_fallen', 40, 'dug-up pillar'), (22, 47, DA % 'dant_jedi_temple_pillar_base', 0, 'dug-up pillar base'),
                                 (-6, 65, G % 'streetlamp_medium_style_01', 0, 'lamp post'), (-9, 37.5, TA % 'debris_tatt_crate_1', 30, 'crates'),
                                 (-7.8, 38.6, TA % 'debris_tatt_crate_1', 10, 'crates'), (16, 44, G % 'palette_supply_04', 20, 'supplies')):
        x, y = F.at(lx, lz)
        L.add(P, t, x, y, F.yaw(a), role, group='dig')
    return {'centre': (gx, gy), 'radius': 70.0, 'o6_point': (600.0, -3300.0), 'heading': h, 'relief': sp, 'bearing_from_ruins': b, 'dist_from_ruins': d, 'ground_drops_8m_within_m': edge,
            'gate': F.at(0, 20), 'dig': F.at(0, 50)}


def poi4_vaults(L, T):
    tpl = BG % 'cave_07_flatland_s02'
    mx, my = 2300.0, 1925.0
    cave_building(L, T, 4, tpl, mx, my, 0.0, 'Great Library vault (cave, 12 cells)')
    f = Frame(mx, my, 0.0)
    for side, lz in ((-1, 5.5), (1, 5.0), (-1, 12.0)):
        x, y = f.at(side * 8.0, lz)
        L.add(4, DA % 'dant_jedi_temple_pillar_base', x, y, 0, 'half-buried pillar base', group='ruin', dz=-1.1)
    for side in (-1, 1):
        x, y = f.at(side * 13.0, 3.0)
        L.add(4, DA % 'dant_jedi_temple_pillar_fallen', x, y, 90 + side * 30, 'fallen pillar', group='ruin')
    x, y = f.at(0, 7.0)
    L.add(4, DA % 'dant_jedi_temple_pillar_sm', x, y, 0, 'pillar stub at the door', group='ruin', dz=-0.8)
    # the dig camp, north of the cave's front
    for (lx, lz, t, a, role) in ((-14, 52, CO % 'corl_tent_med', 10, 'scholars tent'), (6, 54, CO % 'corl_tent_med', -15, 'scholars tent'),
                                 (-4, 64, CO % 'corl_tent_small', 0, 'store tent'), (-1, 58, G % 'campfire_fresh', 0, 'camp fire'),
                                 (-9, 59, G % 'camp_cot_s01', 90, 'cot'), (4, 60, G % 'camp_cot_s01', 85, 'cot'),
                                 (-18, 62, TA % 'debris_tatt_crate_1', 20, 'crates'), (-19.2, 63.1, TA % 'debris_tatt_crate_1', 50, 'crates'),
                                 (12, 66, G % 'palette_supply_03', 10, 'supplies'), (16, 67, G % 'palette_supply_05', 80, 'supplies'),
                                 (1, 68, G % 'streetlamp_medium_style_01', 0, 'lamp post'), (-12, 70, G % 'allum_mine_bucket_s01', 30, 'bucket'),
                                 (-22, 56, DA % 'dant_jedi_temple_pillar_fallen', 100, 'recovered pillar')):
        x, y = f.at(lx, lz)
        L.add(4, t, x, y, f.yaw(a), role, group='dig camp')
    return {'centre': (mx, my + 35), 'radius': 55.0, 'o6_point': (2300.0, 1900.0), 'mouth': (mx, my)}


def poi5_ysanna_camp(L, T):
    c = (-1325.0, -4950.0)
    F = Frame(c[0], c[1], 20.0)
    L.add(5, DA % 'dant_fire_pit', *F.at(0, 0), F.yaw(), 'camp fire pit', group='camp')
    for lx, lz, a in ((-13, 8, 120), (12, 10, 240), (3, -15, 0)):
        x, y = F.at(lx, lz)
        L.add(5, DA % 'dant_small_mudhut', x, y, bearing((x, y), c), 'hide tent (hut)', group='camp')
    x, y = F.at(-2, 22)
    L.add(5, DA % 'dant_large_rock_hut', x, y, bearing((x, y), c), "shaman's stone hut", group='camp')
    for k, (lx, lz) in enumerate(((7, 3), (-6, -4), (9, -6))):
        x, y = F.at(lx, lz)
        L.add(5, DA % ('dant_hide_tanning_s0%d' % (1 + k % 2)), x, y, F.yaw(70 * k), 'hide rack', group='camp')
    for k, (lx, lz) in enumerate(((5, 6), (-4, 5), (-8, -9))):
        x, y = F.at(lx, lz)
        L.add(5, DA % 'dant_rack_spears', x, y, F.yaw(50 * k), 'spear rack', group='camp')
    for lx, lz in ((3.5, 0.5), (-3.5, -1.5)):
        x, y = F.at(lx, lz)
        L.add(5, DA % 'dant_cooking_stone', x, y, F.yaw(30), 'cooking stone', group='camp')
    x, y = F.at(15, -4)
    L.add(5, DA % 'dant_mud_oven', x, y, F.yaw(200), 'mud oven', group='camp')
    for k, (lx, lz, t) in enumerate(((-4, 14, 'dant_skull_thune'), (4, 15, 'dant_skull_bol'), (-9, -10, 'dant_skull_lizard'), (-17, 17, 'dant_skull_bol'))):
        x, y = F.at(lx, lz)
        L.add(5, DA % t, x, y, F.yaw(60 * k), 'bone trophy', group='camp')
    for k, ang in enumerate((30, 150, 270, 330)):
        x, y = c[0] + 27.0 * math.cos(math.radians(ang)), c[1] + 27.0 * math.sin(math.radians(ang))
        L.add(5, DA % 'dant_totem_pole', x, y, face((x, y), c), 'boundary totem', group='camp')
    for k in range(7):
        ang = 200 + k * 20
        x, y = c[0] + 24.0 * math.cos(math.radians(ang)), c[1] + 24.0 * math.sin(math.radians(ang))
        L.add(5, DA % 'dant_fence_8m', x, y, (ang + 90) % 360, 'camp fence', group='fence')
    return {'centre': c, 'radius': 35.0, 'o6_point': (-1200.0, -5200.0)}


def poi6_stone_circle(L, T):
    cx, cy, sp = best_flat(T, (-900.0, -5600.0), 90.0, 22.0)
    c = (round(cx), round(cy))
    for k in range(7):
        ang = k * 360.0 / 7 + 10
        x, y = c[0] + 14.0 * math.cos(math.radians(ang)), c[1] + 14.0 * math.sin(math.radians(ang))
        L.add(6, G % ('rock_mossy_big' if k % 2 == 0 else 'rock_mossy_big_a1'), x, y, ang * 2 % 360, 'standing stone %d of 7' % (k + 1), group='circle')
    L.add(6, DA % 'dant_fire_pit', c[0], c[1], 0, 'ritual fire pit', group='circle')
    for ang in (90, 210, 330):
        x, y = c[0] + 6.5 * math.cos(math.radians(ang)), c[1] + 6.5 * math.sin(math.radians(ang))
        L.add(6, DA % 'dant_totem_pole', x, y, face((x, y), c), 'bone totem', group='circle')
    for k, (ang, t) in enumerate(((20, 'dant_skull_thune'), (140, 'dant_skull_bol'), (260, 'dant_skull_lizard'))):
        x, y = c[0] + 3.9 * math.cos(math.radians(ang)), c[1] + 3.9 * math.sin(math.radians(ang))
        L.add(6, DA % t, x, y, ang, 'bone offering', group='circle')
    for k in range(4):
        ang = 45 + k * 90
        x, y = c[0] + 21.0 * math.cos(math.radians(ang)), c[1] + 21.0 * math.sin(math.radians(ang))
        L.add(6, G % 'tato_cave_rock_large', x, y, ang, 'outlying stone', group='circle')
    return {'centre': c, 'radius': 24.0, 'o6_point': (-900.0, -5600.0)}


def poi8_hamlet(L, T):
    c = (-3050.0, 1100.0)
    lake = (-3600.0, 1200.0)
    h = bearing(c, lake)                # +z toward the water
    F = Frame(c[0], c[1], h)
    L.add(8, DA % 'dant_fire_pit', *F.at(0, 0), F.yaw(), 'hamlet fire pit', group='hamlet')
    for lx, lz, t in ((-14, 4, 'dant_small_mudhut'), (13, 2, 'dant_small_mudhut'), (0, -17, 'dant_large_mudhut')):
        x, y = F.at(lx, lz)
        L.add(8, DA % t, x, y, bearing((x, y), c), 'fisher house', group='hamlet')
    for k, lx in enumerate((-6, -2, 2, 6)):
        x, y = F.at(lx, 11.0)
        L.add(8, DA % 'dant_fish_rack', x, y, F.yaw(), 'fish and net rack', group='hamlet')
    x, y = F.at(5, -4)
    L.add(8, DA % 'dant_hide_tanning_s01', x, y, F.yaw(40), 'net-drying rack', group='hamlet')
    x, y = F.at(-4, -3)
    L.add(8, DA % 'dant_cooking_stone', x, y, F.yaw(20), 'cooking stone', group='hamlet')
    for k, lx in enumerate((-3, 3, 7.5)):
        x, y = F.at(lx, 13.5)
        L.add(8, IT % 'item_basket_closed', x, y, F.yaw(60 * k), 'bait basket', group='hamlet')
    for k in range(5):
        x, y = F.at(-24 + k * 8.0, -28)
        L.add(8, DA % 'dant_fence_8m', x, y, F.yaw(), 'garden fence', group='fence')
    for lx in (-9, 9):
        x, y = F.at(lx, 20)
        L.add(8, DA % 'dant_boundary_post', x, y, F.yaw(), 'shore post', group='hamlet')
    # the pier: from the first dry point at or under 39.5 m along the heading, three walkway pieces and a platform
    d = 20.0
    while d < 300 and T.h(*F.at(0, d)) > WATER + 1.0:
        d += 2.0
    start = d - 6.0
    for k in range(3):
        x, y = F.at(0, start + 8.0 + 16.0 * k)
        L.add(8, BE % 'endor_lake_walkway_straight', x, y, F.yaw(), 'pier walkway', building=False, z=max(T.h(x, y), WATER + 1.0), group='pier')
    x, y = F.at(0, start + 8.0 + 16.0 * 3 + 8.0)
    L.add(8, BE % 'endor_lake_platform', x, y, F.yaw(), 'pier platform', z=WATER + 1.0, group='pier')
    return {'centre': c, 'radius': 45.0, 'o6_point': (-2900.0, 1300.0), 'heading_to_lake': h, 'shore_distance': d, 'pier_end': F.at(0, start + 8.0 + 16.0 * 3 + 8.0)}


def poi9_adit(L, T):
    tpl = BG % 'cave_08_flatland_s03'
    path = T.ot.CANYON['path']
    mx, my = 4590.0, -310.0
    # face the canyon's centre line
    best = min(((dist((mx, my), (px, py)), px, py) for (ax, ay), (bx, by) in zip(path, path[1:])
                for t in [i / 40.0 for i in range(41)] for px, py in [(ax + (bx - ax) * t, ay + (by - ay) * t)]))
    yaw = bearing((mx, my), (best[1], best[2]))
    cave_building(L, T, 9, tpl, mx, my, yaw, 'kathracite adit (cave, 30 cells)')
    f = Frame(mx, my, yaw)
    # the working face in front of the mouth
    for (lx, lz, t, a, role) in ((-6, 9, G % 'allum_mine_car_s01', 90, 'ore cart'), (6.5, 11, G % 'allum_mine_car_s01', 85, 'ore cart'), (0, 16, G % 'allum_mine_car_s01', 10, 'ore cart'),
                                 (-9, 7, G % 'allum_mine_support_s01', 0, 'timber prop'), (9, 7, G % 'allum_mine_support_s01', 0, 'timber prop'),
                                 (-9, 12, G % 'allum_mine_support_s01', 0, 'timber prop'), (9, 12, G % 'allum_mine_support_s01', 0, 'timber prop'),
                                 (-4, 5, G % 'allum_mine_wall_lamp_s01', 0, 'lamp'), (4.5, 5, G % 'allum_mine_wall_lamp_s01', 0, 'lamp'),
                                 (-12, 18, G % 'allum_mine_bucket_s01', 40, 'bucket'), (12, 17, G % 'allum_mine_bucket_s01', 100, 'bucket'),
                                 (-15, 24, G % 'allum_mine_pipes_s01', 90, 'pipes'), (14, 24, G % 'allum_mine_device_s01', 20, 'crusher'),
                                 (-10, 28, G % 'palette_supply_02', 15, 'supplies'),
                                 (-12.5, 29, TA % 'debris_tatt_crate_metal_1', 60, 'crate'), (-8.5, 30, TA % 'debris_tatt_drum_dented_1', 0, 'drum')):
        x, y = f.at(lx, lz)
        L.add(9, t, x, y, f.yaw(a), role, group='adit works')
    return {'centre': f.at(0, 15), 'radius': 50.0, 'o6_point': (4500.0, -300.0), 'mouth': (mx, my), 'yaw': yaw}


def poi10_bridge(L, T):
    """A chain of the 32.5 m Tatooine small-bridge piece across Imhar Canyon, rim to rim."""
    tpl = TA % 'bridge_tatooine_small_style_03'
    c = (4470.0, -530.0)
    h = 135.0                                   # perpendicular to the canyon's 45 degree heading
    u = (math.sin(math.radians(h)), math.cos(math.radians(h)))
    rim = []
    for s in (-1, 1):
        d = 0.0
        while d < 400 and T.h(c[0] + s * u[0] * d, c[1] + s * u[1] * d) < 100.0:
            d += 2.0
        rim.append(d)
    span = rim[0] + rim[1]
    n = int(math.ceil((span + 10.0) / 32.5))
    start = -rim[0] - (n * 32.5 - span) / 2.0
    # deck level: the mesa top 14 m beyond each rim contour, where the end pieces rest (the contour itself is a few metres lower)
    deck = round(max(T.h(c[0] - u[0] * (rim[0] + 14.0), c[1] - u[1] * (rim[0] + 14.0)), T.h(c[0] + u[0] * (rim[1] + 14.0), c[1] + u[1] * (rim[1] + 14.0))), 2)
    for k in range(n):
        d = start + 32.5 * (k + 0.5)
        L.add(10, tpl, c[0] + u[0] * d, c[1] + u[1] * d, h, 'bridge span %d of %d' % (k + 1, n), z=deck, group='bridge')
    return {'centre': c, 'radius': 160.0, 'o6_point': (4300.0, -700.0), 'span_m': span, 'pieces': n, 'deck_height': deck, 'rim_walk_m': rim}


def poi11_knossa(L, T):
    """The old town round the starport: market street south of the building, half-ruined blocks east and west."""
    P = 11
    pad = KNOSSA
    # market street along y = pad - 66, tents facing the street
    for k, x0 in enumerate((-54.0, -26.0, 2.0)):
        L.add(P, BG % 'merchant_tent_all_s01', pad[0] + x0, pad[1] - 62.0, 180.0, 'market tent (with interior)', building=True, group='market')
    for k, x0 in enumerate((-60.0, -36.0, 40.0, 62.0)):
        L.add(P, CO % ('corl_tent_large' if k % 2 == 0 else 'corl_tent_med'), pad[0] + x0, pad[1] - 76.0, 0.0, 'market tent', group='market')
    for k, (x0, y0) in enumerate(((-14, -69.5), (-10.4, -70.2), (12, -68.5), (16, -69.3), (30, -70))):
        L.add(P, TA % ('debris_tatt_crate_1' if k % 2 == 0 else 'debris_tatt_drum_storage_1'), pad[0] + x0, pad[1] + y0, 33 * k, 'market goods', group='market')
    for k, x0 in enumerate((-18.0, 18.0)):
        L.add(P, G % 'palette_supply_0%d' % (k + 1), pad[0] + x0, pad[1] - 78.0, 90.0, 'stock pallets', group='market')
    L.add(P, G % 'streetlamp_medium_style_01', pad[0] - 40, pad[1] - 66.0, 0, 'street lamp', group='market')
    L.add(P, G % 'streetlamp_medium_style_01', pad[0] + 22, pad[1] - 66.0, 0, 'street lamp', group='market')
    # west block: a cantina (the Dantooine Imperial-style shed), two hovels, a broken wall
    L.add(P, BM % 'military_base_shed_imperial_style_cantina_s01', pad[0] - 82.0, pad[1] - 10.0, 90.0, 'cantina', building=True, group='west block')
    L.add(P, TA % 'stone_hovel_tatooine_style_01', pad[0] - 82.0, pad[1] - 34.0, 90.0, 'hovel', group='west block')
    L.add(P, TA % 'stone_hovel_tatooine_style_01', pad[0] - 88.0, pad[1] - 50.0, 80.0, 'hovel', group='west block')
    L.add(P, TA % 'wall_ruined_tatooine_large_style_01', pad[0] - 70.0, pad[1] + 18.0, 90.0, 'ruined wall', group='west block')
    L.add(P, TA % 'pillar_ruined_large_style_01', pad[0] - 70.0, pad[1] + 30.0, 0.0, 'ruined pillar', group='west block')
    # east block: the junk dealer's shed, a collapsed rock hut, a broken wall
    L.add(P, TA % 'shed_junkshop_watto', pad[0] + 84.0, pad[1] - 40.0, 270.0, 'junk dealer shed', group='east block')
    L.add(P, DA % 'dant_large_rock_hut_dest', pad[0] + 90.0, pad[1] - 8.0, 270.0, 'collapsed hut', group='east block')
    L.add(P, TA % 'wall_ruined_tatooine_large_style_02', pad[0] + 74.0, pad[1] + 22.0, 90.0, 'ruined wall', group='east block')
    L.add(P, TA % 'pillar_ruined_small_style_01', pad[0] + 74.0, pad[1] + 34.0, 0.0, 'ruined pillar', group='east block')
    return {'centre': pad, 'radius': 100.0, 'o6_point': pad}


def poi12_markers(L, T):
    """Sixteen memorial pillars along the Knossa road, one at the end of each 480 m piece, alternating sides."""
    pieces = []
    for lay in T.trn['layers']:
        if lay['name'].startswith('knossa road ') and lay['name'] != 'knossa road clearing':
            for r in lay['affectors']:
                if r['type'] == 'AROA':
                    pieces.append(r['points'])
    pts = []
    for k, (p0, p1) in enumerate(pieces):
        dx, dy = p1[0] - p0[0], p1[1] - p0[1]
        n = math.hypot(dx, dy)
        ux, uy = dx / n, dy / n
        pref = 1 if k % 2 == 0 else -1
        # 8-12 m off the centre line (the road is 12 m wide): the calmest ground, the preferred side winning ties
        cands = sorted(((T.max_slope_deg(p1[0] + (-uy) * s * off, p1[1] + ux * s * off, 4.0, 2.0) + (0.0 if s == pref else 1.5), s, off)
                        for s in (pref, -pref) for off in (8.0, 9.0, 10.0, 12.0)))
        _, side, off = cands[0]
        x, y = p1[0] + (-uy) * side * off, p1[1] + ux * side * off
        yaw = bearing((x, y), p1)
        L.add(12, DA % 'dant_jedi_temple_pillar_sm', x, y, yaw, 'road marker %d of %d' % (k + 1, len(pieces)), group='markers')
        pts.append((x, y))
    return {'centre': pts[len(pts) // 2], 'radius': 2000.0, 'o6_point': None, 'markers': len(pts), 'points': pts}


def poi13_watch(L, T):
    cx, cy, sp = best_flat(T, (300.0, -6400.0), 60.0, 16.0, w_dist=0.05)
    c = (round(cx), round(cy))
    F = Frame(c[0], c[1], 0.0)
    for lx, lz in ((-8, -8), (8, -8)):
        L.add(13, DA % 'dant_jedi_temple_pillar_base', *F.at(lx, lz), 0, 'watch tower base', group='ruin')
    L.add(13, DA % 'dant_jedi_temple_pillar', *F.at(-8, 8), 0, 'standing pillar', group='ruin')
    L.add(13, DA % 'dant_jedi_temple_pillar_med', *F.at(8, 8), 0, 'standing pillar (broken)', group='ruin')
    L.add(13, DA % 'dant_jedi_temple_pillar_fallen', *F.at(-2, 0), 40, 'fallen pillar', group='ruin')
    L.add(13, DA % 'dant_jedi_temple_pillar_fallen', *F.at(4, -3), 110, 'fallen pillar', group='ruin')
    L.add(13, DA % 'dant_jedi_wall_2', *F.at(0, 12), 90, 'wall stub', group='ruin')
    L.add(13, DA % 'dant_jedi_wall_2', *F.at(-12, 0), 0, 'wall stub', group='ruin')
    L.add(13, DA % 'dant_jedi_wall_1', *F.at(12, -2), 0, 'wall stub', group='ruin')
    L.add(13, DA % 'dant_jedi_temple_pillar_sm', *F.at(0, -9), 0, 'low pillar', group='ruin')
    L.add(13, G % 'rock_mossy_big', *F.at(15, 12), 40, 'boulder', group='ruin')
    L.add(13, G % 'rock_mossy_big_a1', *F.at(-16, -12), 200, 'boulder', group='ruin')
    return {'centre': c, 'radius': 22.0, 'o6_point': c}


def poi14_sith_post(L, T, cave):
    """Outside dressing on the west foothill cave's apron; the cells are dressed by screenplay."""
    mx, my = cave
    F = Frame(mx, my, 0.0)
    for lx in (-11.0, 11.0):
        L.add(14, G % 'banner_imperial_style_01', *F.at(lx, 6.0), 0, 'banner at the mouth', group='post')
    for k, (lx, lz) in enumerate(((-14, 12), (-18.5, 13), (17, 11))):
        L.add(14, MIL % 'bunker_crate_style_01', *F.at(lx, lz), 20 * k, 'crates', group='post')
    for k, (lx, lz) in enumerate(((13, 17), (14.3, 18.5))):
        L.add(14, TA % 'debris_tatt_drum_storage_1', *F.at(lx, lz), 40 * k, 'drums', group='post')
    L.add(14, G % 'palette_supply_02', *F.at(-14.5, 19.5), 0, 'supply pallet', group='post')
    L.add(14, G % 'data_terminal_free_s2', *F.at(8.0, 9.0), 160, 'field terminal (outside)', group='post')
    L.add(14, G % 'campfire_burnt', *F.at(-4.0, 16.0), 0, 'cold campfire', group='post')
    return {'centre': (mx, my + 6), 'radius': 22.0, 'o6_point': (-2976.0, -4960.0), 'mouth': (mx, my)}


def poi15_crash(L, T):
    c = (-1500.0, 5200.0)
    F = Frame(c[0], c[1], 38.0)
    L.add(15, G % 'xwing', *F.at(0, 0), F.yaw(), 'crashed Alliance fighter', group='wreck')
    L.add(15, G % 'poi_all_construction_metal_pile', *F.at(-9, 10), F.yaw(30), 'wreckage', group='wreck')
    L.add(15, G % 'poi_all_construction_metal_pile', *F.at(8, 14), F.yaw(140), 'wreckage', group='wreck')
    L.add(15, G % 'prp_junk_s5', *F.at(-10, -3), F.yaw(60), 'wreckage', group='wreck')
    L.add(15, G % 'atat_debris_02', *F.at(11, 4), F.yaw(110), 'wreckage', group='wreck')
    L.add(15, G % 'atst_debris_01', *F.at(3, 18), F.yaw(10), 'wreckage', group='wreck')
    L.add(15, CO % 'corl_tent_small', *F.at(24, -8), F.yaw(-30), "survivor's tent", group='camp')
    L.add(15, G % 'campfire_fresh', *F.at(20, -2), 0, 'camp fire', group='camp')
    L.add(15, G % 'camp_cot_s01', *F.at(27, -1), F.yaw(80), 'cot', group='camp')
    L.add(15, TA % 'debris_tatt_crate_1', *F.at(21, -13), F.yaw(30), 'salvaged crate', group='camp')
    return {'centre': c, 'radius': 35.0, 'o6_point': c}


def poi16_sky_burial(L, T):
    """On the mesa top at the canyon rim nearest to o6's (5000, 900), which is flat mesa 280 m from the rim."""
    o6 = (5000.0, 900.0)
    best = None
    for i in range(-320, 321, 8):
        for j in range(-320, 321, 8):
            x, y = o6[0] + i, o6[1] + j
            if T.h(x, y) < 103.0:
                continue
            drop = [(a, b) for a, b in ((20, 0), (-20, 0), (0, 20), (0, -20), (14, 14), (-14, -14), (14, -14), (-14, 14)) if T.h(x + a, y + b) < 98.0]
            if drop:
                d = math.hypot(i, j)
                if best is None or d < best[0]:
                    best = (d, x, y, drop)
    _, ex, ey, drop = best
    # edge direction = mean of the drop vectors; stand 14 m back from it
    ox = sum(a for a, b in drop) / len(drop)
    oy = sum(b for a, b in drop) / len(drop)
    n = math.hypot(ox, oy) or 1.0
    ux, uy = ox / n, oy / n                      # points toward the drop
    cx, cy = ex - ux * 16.0, ey - uy * 16.0
    h = bearing((cx, cy), (cx + ux, cy + uy))
    F = Frame(cx, cy, h)
    L.add(16, BE % 'endor_lake_platform', *F.at(0, 0), F.yaw(), 'wooden burial platform', group='platform', dz=0.0)
    for k, (lx, lz) in enumerate(((-11.5, -6), (11.5, -6), (-11.5, 6), (11.5, 6))):
        L.add(16, DA % 'dant_totem_pole', *F.at(lx, lz), F.yaw(30 * k), 'bone totem', group='platform')
    for k, (lx, lz, t) in enumerate(((-5, 2, 'dant_skull_bol'), (4, -3, 'dant_skull_thune'), (0, 5, 'dant_skull_lizard'))):
        L.add(16, DA % t, *F.at(lx, lz), F.yaw(77 * k), 'bone offering', group='platform', dz=0.3)
    L.add(16, G % 'skeleton_human_headandbody', *F.at(-2, -1), F.yaw(20), 'laid-out bones', group='platform', dz=0.3)
    for k, lx in enumerate((-14, 14)):
        L.add(16, DA % 'dant_rack_spears', *F.at(lx, -9), F.yaw(10 * k), 'spear rack', group='platform')
    return {'centre': (cx, cy), 'radius': 20.0, 'o6_point': o6, 'rim_point': (ex, ey), 'heading': h}


def poi18_hutt(L, T):
    c = (3400.0, -2300.0)
    F = Frame(c[0], c[1], 0.0)
    L.add(18, G % 'landing_pad_transport', *F.at(0, 0), 0.0, 'landing pad', group='field')
    for k, (lx, lz, t) in enumerate(((-30, 20, 'corl_tent_large'), (-14, 26, 'corl_tent_med'), (10, 26, 'corl_tent_hut_s01'), (30, 20, 'corl_tent_med'))):
        L.add(18, CO % t, *F.at(lx, lz), F.yaw(180 + 12 * k), 'broker tent', group='camp')
    for k, (lx, lz) in enumerate(((-7.5, 22), (-4.5, 22), (-1.5, 22), (1.5, 22))):
        L.add(18, G % ('palette_supply_0%d' % (1 + k % 5)), *F.at(lx, lz), F.yaw(), 'cargo pallets', group='camp')
    for k, (lx, lz) in enumerate(((-24, 14), (-23, 15.5), (24, 15), (25, 13.5))):
        L.add(18, IT % 'item_crate_spice', *F.at(lx, lz), F.yaw(20 * k), 'spice crates', group='camp')
    for lx in (-27.0, 27.0):
        L.add(18, G % 'streetlamp_medium_style_01', *F.at(lx, 0.0), 0, 'landing light', group='field')
    L.add(18, G % 'campfire_fresh', *F.at(0, 30), 0, 'camp fire', group='camp')
    L.add(18, TA % 'debris_tatt_drum_storage_2', *F.at(18, 24), 0, 'fuel drum', group='camp')
    L.add(18, TA % 'debris_tatt_drum_storage_1', *F.at(19.5, 25), 50, 'fuel drum', group='camp')
    return {'centre': c, 'radius': 45.0, 'o6_point': c}
