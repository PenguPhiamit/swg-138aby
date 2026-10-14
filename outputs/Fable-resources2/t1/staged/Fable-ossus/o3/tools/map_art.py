"""map_art.stage_map_art(stage_dir): Ossus map art from our own terrain (Fable O3, 14 Oct 2026), story-neutral.

Writes under stage_dir (client paths):
  texture/ui_map_ossus.dds                    1024x1024 planetary map: hillshaded relief from the Core3 height port of our
                                              terrain/ossus.trn, water at the terrain's water table, the Knossa road; A8R8G8B8
  texture/ui_planet_sel_ossus.dds             256x256 globe texture with a 9-level mip chain (stock pattern), wrapped seamlessly
  appearance/ui_planet_sel_ossus.apt          stock appearance/ui_planet_sel_tato.apt with its mesh reference renamed
  appearance/mesh/ui_planet_sel_ossus.msh     stock ui_planet_sel_tato.msh with its shader reference renamed
  shader/ui_planet_sel_ossus.sht              stock shader/ui_planet_sel_tatt_as8.sht with its texture reference renamed
  texture/loading/ossus/ui_load_ossus.dds     512x512 loading tile (the map, box-filtered, vignetted; stock tiles are 512 A8R8G8B8)
  datatables/loading/ossus.iff                O1c's table with every row's Picture pointing at the tile above
  out/ui_map_ossus.png, out/ui_planet_sel_ossus.png   previews (PNG) of the two textures
Every stock file is parsed and rebuilt byte-exact before its reference string is changed (trn_iff), the DDS writer is
dds.py (self-tested on stock files). No wiki or third-party image is used: the pixels come from our heightfield.

    python -I map_art.py <stage_dir> [--res 1024]     build (about two minutes for the 1024 render)
    python -I map_art.py --check <stage_dir>          re-read a staged set: headers, chains, table references
"""
import hashlib
import json
import math
import os
import struct
import sys
import time
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
O3 = os.path.dirname(HERE)
OSSUS = os.path.dirname(O3)
OUTPUTS = os.path.dirname(OSSUS)
for rel in ('tools', 'Fable-planet-test/tools', 'Fable-ossus/tools', 'Fable-ossus/o3/tools'):   # trn_read, trn_road and dds stay beside their batches
    p = os.path.join(OUTPUTS, rel)
    if p not in sys.path:
        sys.path.insert(0, p)
from swgfmt import trn_iff  # noqa: E402
import trn_read  # noqa: E402
from swgfmt import swg_tables as st  # noqa: E402
import dds  # noqa: E402
from trn_road import RoadHeightEvaluator  # noqa: E402

TRN = os.path.join(OSSUS, 'staged', 'client', 'terrain', 'ossus.trn')
TGA_DIR = os.path.join(OSSUS, 'staged', 'client', 'terrain')
SITES = os.path.join(OSSUS, 'out', 'ossus-sites.json')
LOADING_O1 = os.path.join(OSSUS, 'staged', 'client', 'datatables', 'loading', 'ossus.iff')
STOCK = {'apt': 'appearance/ui_planet_sel_tato.apt', 'msh': 'appearance/mesh/ui_planet_sel_tato.msh', 'sht': 'shader/ui_planet_sel_tatt_as8.sht'}
OURS = {'apt': 'appearance/ui_planet_sel_ossus.apt', 'msh': 'appearance/mesh/ui_planet_sel_ossus.msh', 'sht': 'shader/ui_planet_sel_ossus.sht',
        'globe': 'texture/ui_planet_sel_ossus.dds', 'map': 'texture/ui_map_ossus.dds', 'tile': 'texture/loading/ossus/ui_load_ossus.dds',
        'loading': 'datatables/loading/ossus.iff'}
TILE_REF = 'loading/ossus/ui_load_ossus'

# height bands (m) -> colour; water below the terrain's water table. Dry scrub world with a green benchland and grey rock.
BANDS = [(38.5, (168, 156, 108)), (46.0, (142, 140, 86)), (60.0, (118, 132, 78)), (85.0, (146, 128, 84)), (110.0, (150, 104, 76)),
         (140.0, (120, 110, 84)), (165.0, (108, 138, 92)), (180.0, (118, 118, 110)), (400.0, (176, 176, 170))]
WATER_MIN_DEPTH = 0.75     # hollows shallower than this are shown as damp ground, not ponds
WATER_DEEP, WATER_SHALLOW = (26, 52, 92), (70, 110, 150)


def client_file(name):
    idx = trn_iff.client_index()
    return trn_iff.open_tre_entry(os.path.join(trn_iff.CLIENT, idx[name]), name)


def evaluator():
    with open(TRN, 'rb') as f:
        trn = trn_read.read_trn(f.read())
    bitmaps = {}
    for e in trn['bitmaps'].values():
        with open(os.path.join(TGA_DIR, os.path.basename(e['file'])), 'rb') as f:
            bitmaps[e['file']] = f.read()
    ev = RoadHeightEvaluator(trn, lambda n: trn_read.load_tga_grey(bitmaps[n]))
    return trn, ev


def _lerp(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def land_colour(h):
    prev_h, prev_c = BANDS[0]
    if h <= prev_h:
        return prev_c
    for bh, bc in BANDS[1:]:
        if h <= bh:
            return _lerp(prev_c, bc, (h - prev_h) / (bh - prev_h))
        prev_h, prev_c = bh, bc
    return BANDS[-1][1]


def render_heights(ev, res, size):
    """Height grid, north up: row 0 = y = +size/2."""
    step = size / res
    grid = []
    for j in range(res):
        y = size / 2 - (j + 0.5) * step
        grid.append([ev.height(-size / 2 + (i + 0.5) * step, y) for i in range(res)])
    return grid


def shade_map(grid, water, step, road=None, road_width=2.0):
    res = len(grid)
    lx, ly, lz = -0.55, 0.55, 0.63      # light from the north-west, fairly high
    rows = []
    road_px = set()
    if road:
        pts = [((x + 8192.0) / step, (8192.0 - y) / step) for x, y in road]
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            n = int(max(abs(x1 - x0), abs(y1 - y0)) * 2) + 1
            for k in range(n + 1):
                t = k / n
                cx, cy = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
                r = road_width / 2
                for py in range(int(cy - r), int(cy + r) + 1):
                    for px in range(int(cx - r), int(cx + r) + 1):
                        if 0 <= px < res and 0 <= py < res and (px + 0.5 - cx) ** 2 + (py + 0.5 - cy) ** 2 <= r * r:
                            road_px.add((px, py))
    for j in range(res):
        row = []
        for i in range(res):
            h = grid[j][i]
            if h < water - WATER_MIN_DEPTH:
                d = min(1.0, (water - h) / 12.0)
                c = _lerp(WATER_SHALLOW, WATER_DEEP, d)
                shade = 1.0
            else:
                hl = grid[j][max(0, i - 1)]
                hr = grid[j][min(res - 1, i + 1)]
                hu = grid[max(0, j - 1)][i]
                hd = grid[min(res - 1, j + 1)][i]
                dx = 2.5 * (hr - hl) / (2 * step)      # vertical exaggeration: the plains roll gently at 16 m a pixel
                dy = 2.5 * (hu - hd) / (2 * step)
                nx, ny, nz = -dx, -dy, 1.0
                ln = math.sqrt(nx * nx + ny * ny + nz * nz)
                dot = (nx * lx + ny * ly + nz * lz) / ln
                shade = 0.35 + 0.65 * max(0.0, dot) / max(1e-6, lz)
                shade = min(1.2, shade)
                c = land_colour(h)
                if h < water:
                    c = _lerp(c, (96, 104, 92), 0.5)    # damp hollow
                if (i, j) in road_px:
                    c = (92, 72, 52)
            row.append(tuple(max(0, min(255, int(v * shade))) for v in c) + (255,))
        rows.append(row)
    return rows


def globe_texture(map_rows, size=256, blend=0.12):
    """Equirectangular 256x256 from the map: the western hemisphere is the map, the eastern the map turned 180 degrees,
    crossfaded over `blend` of the width at both seams so the sphere wraps without a visible edge; latitude runs over
    the map north to south, darkened towards the poles."""
    res = len(map_rows)

    def west(t, lat):
        return map_rows[int(min(res - 1, lat * res))][int(min(res - 1, t * res))]

    def east(t, lat):
        return map_rows[int(min(res - 1, (1.0 - lat) * res))][int(min(res - 1, (1.0 - t) * res))]
    out = []
    for v in range(size):
        lat = (v + 0.5) / size                       # 0 = north pole
        pole = 1.0 - 0.45 * (abs(lat - 0.5) * 2) ** 3
        row = []
        for u in range(size):
            t = (u + 0.5) / size                     # longitude 0..1
            if t < 0.5:
                a, b, local = west(t * 2, lat), east(t * 2, lat), t * 2
                w = 1.0 if blend < local < 1.0 - blend else (local / blend if local <= blend else (1.0 - local) / blend)
                px = _lerp(b[:3], a[:3], w * 0.5 + 0.5) if local <= blend or local >= 1.0 - blend else a[:3]
            else:
                a, b, local = east((t - 0.5) * 2, lat), west((t - 0.5) * 2, lat), (t - 0.5) * 2
                w = 1.0 if blend < local < 1.0 - blend else (local / blend if local <= blend else (1.0 - local) / blend)
                px = _lerp(b[:3], a[:3], w * 0.5 + 0.5) if local <= blend or local >= 1.0 - blend else a[:3]
            row.append((int(px[0] * pole), int(px[1] * pole), int(px[2] * pole), 255))
        out.append(row)
    return out


def loading_tile(map_rows, size=512):
    rows = map_rows
    while len(rows) > size:
        rows = dds._box_down(rows)
    if len(rows) < size:                      # low-resolution trial renders: nearest-neighbour up
        k = size // len(rows)
        rows = [[px for px in row for _ in range(k)] for row in rows for _ in range(k)]
    out = []
    for j in range(size):
        row = []
        for i in range(size):
            dx, dy = (i + 0.5) / size - 0.5, (j + 0.5) / size - 0.5
            vig = 1.0 - 0.6 * max(0.0, math.sqrt(dx * dx + dy * dy) - 0.3) / 0.41
            r, g, b, a = rows[j][i]
            row.append((int(r * vig), int(g * vig), int(b * vig), 255))
        out.append(row)
    return out


def write_png(path, rows):
    h, w = len(rows), len(rows[0])
    raw = b''.join(b'\0' + bytes(c for px in row for c in px[:3]) for row in rows)

    def chunk(tag, data):
        return struct.pack('>I', len(data)) + tag + data + struct.pack('>I', zlib.crc32(tag + data) & 0xffffffff)
    png = b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0)) + chunk(b'IDAT', zlib.compress(raw, 6)) + chunk(b'IEND', b'')
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'wb') as f:
        f.write(png)


def rename_reference(data, old, new):
    """Rebuild an IFF file with the NAME chunk holding `old` changed to `new` (both without the NUL); byte round trip first."""
    nodes = trn_iff.parse(data)
    if trn_iff.build(nodes) != data:
        raise AssertionError('stock file does not round-trip')
    hits = []

    def walk(ns):
        for n in ns:
            if n.is_form:
                walk(n.children)
            elif n.tag == 'NAME' and n.data == old.encode('latin-1') + b'\0':
                n.data = new.encode('latin-1') + b'\0'
                hits.append(n)
    walk(nodes)
    if len(hits) != 1:
        raise AssertionError('expected one NAME chunk %r, found %d' % (old, len(hits)))
    return trn_iff.build(nodes)


def stage_map_art(stage_dir, res=1024):
    t0 = time.time()
    report = {'files': {}, 'render': {}}

    def out(rel, data, info=None):
        path = os.path.join(stage_dir, rel.replace('/', os.sep))
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'wb') as f:
            f.write(data)
        report['files'][rel] = dict(info or {}, bytes=len(data), sha256=hashlib.sha256(data).hexdigest())

    trn, ev = evaluator()
    size = trn['header']['size']
    water = trn['header']['global_water_height']
    with open(SITES, encoding='utf-8') as f:
        sites = json.load(f)
    grid = render_heights(ev, res, size)
    flat = [h for row in grid for h in row]
    report['render'] = {'res': res, 'size_m': size, 'water_m': water, 'height_min': min(flat), 'height_max': max(flat),
                        'water_fraction': sum(1 for h in flat if h < water) / len(flat), 'seconds_heights': round(time.time() - t0, 1)}
    rows = shade_map(grid, water, size / res, road=sites['road']['points'], road_width=max(2.0, res / 512))
    out(OURS['map'], dds.encode(rows, mips=1), {'what': 'planetary map, A8R8G8B8, no mips (stock maps have none)'})
    write_png(os.path.join(O3, 'out', 'ui_map_ossus.png'), rows)
    globe = globe_texture(rows, 256)
    out(OURS['globe'], dds.encode(globe, mips=0), {'what': 'globe texture, A8R8G8B8, 9 mips like stock ui_planet_sel_*.dds'})
    write_png(os.path.join(O3, 'out', 'ui_planet_sel_ossus.png'), globe)
    tile = loading_tile(rows, 512)
    out(OURS['tile'], dds.encode(tile, mips=1), {'what': 'loading tile, 512 A8R8G8B8 like texture/loading/lok/ui_load_lok.dds'})
    # the stock globe chain, references renamed (byte round trip of each stock file asserted inside)
    out(OURS['apt'], rename_reference(client_file(STOCK['apt']), 'appearance/mesh/ui_planet_sel_tato.msh', OURS['msh']), {'from': STOCK['apt']})
    out(OURS['msh'], rename_reference(client_file(STOCK['msh']), 'shader/ui_planet_sel_tatt_as8.sht', OURS['sht']), {'from': STOCK['msh']})
    out(OURS['sht'], rename_reference(client_file(STOCK['sht']), 'texture/ui_planet_sel_tatt.dds', OURS['globe']), {'from': STOCK['sht']})
    # the loading table: O1c's rows, Picture -> our tile
    with open(LOADING_O1, 'rb') as f:
        ld = f.read()
    t = st.read_dtii(ld)
    assert st.write_dtii(t) == ld
    pic = t['columns'].index('Picture')
    for r in t['rows']:
        r[pic] = TILE_REF
    out(OURS['loading'], st.write_dtii(t), {'rows': [list(r) for r in t['rows']], 'from': 'O1c datatables/loading/ossus.iff'})
    report['seconds'] = round(time.time() - t0, 1)
    report['note_waypoint_planets'] = "datatables/player/waypoint_planets.iff row 'ossus' still names the placeholder ui_planet_sel_dant.apt (O1 stage_tables PLACEHOLDERS['planet_model']); set it to ui_planet_sel_ossus.apt when this is packed"
    return report


def check(stage_dir):
    res = {}

    def load(rel):
        with open(os.path.join(stage_dir, rel.replace('/', os.sep)), 'rb') as f:
            return f.read()
    for key in ('map', 'globe', 'tile'):
        d = dds.read(load(OURS[key]))
        h = d['header']
        levels = sum(max(1, h['width'] >> i) * max(1, h['height'] >> i) * 4 for i in range(max(1, h['mips'])))
        res[OURS[key]] = {'w': h['width'], 'h': h['height'], 'mips': h['mips'], 'bpp': h['bpp'], 'uncompressed': dds.is_uncompressed(h),
                          'data_matches_levels': len(d['data']) == levels, 'rewrite_identical': dds.write(d) == load(OURS[key])}
    strings = {}
    for key in ('apt', 'msh', 'sht'):
        data = load(OURS[key])
        nodes = trn_iff.parse(data)
        names = []

        def walk(ns):
            for n in ns:
                if n.is_form:
                    walk(n.children)
                elif n.tag == 'NAME':
                    names.append(n.data.rstrip(b'\0').decode('latin-1'))
        walk(nodes)
        strings[key] = names
        res[OURS[key]] = {'parses': True, 'rebuild_identical': trn_iff.build(nodes) == data, 'names': names}
    res['chain'] = {'apt->msh': OURS['msh'] in strings['apt'], 'msh->sht': OURS['sht'] in strings['msh'], 'sht->dds': OURS['globe'] in strings['sht']}
    t = st.read_dtii(load(OURS['loading']))
    pic = t['columns'].index('Picture')
    res[OURS['loading']] = {'rows': len(t['rows']), 'all_point_at_tile': all(r[pic] == TILE_REF for r in t['rows']),
                            'tile_exists': os.path.exists(os.path.join(stage_dir, 'texture', *TILE_REF.split('/')) + '.dds')}
    res['ok'] = all(v.get('rewrite_identical', True) and v.get('rebuild_identical', True) and v.get('data_matches_levels', True)
                    and v.get('all_point_at_tile', True) and v.get('tile_exists', True) for v in res.values() if isinstance(v, dict)) and all(res['chain'].values())
    return res


def main(argv):
    if argv and argv[0] == '--check':
        r = check(argv[1])
        print(json.dumps(r, indent=1))
        return 0 if r['ok'] else 1
    if not argv:
        print(__doc__)
        return 2
    res = int(argv[argv.index('--res') + 1]) if '--res' in argv else 1024
    rep = stage_map_art(argv[0], res)
    print(json.dumps(rep, indent=1))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
