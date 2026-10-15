"""E0: fit the NGE Echo Base building to MTG's three terrain cut-outs on Hoth, and list its client files (Fable, 14 Oct 2026).
Our own readers: swgfmt.trn_iff (IFF, archives, load order), a minimal portal-layout parse here, the Hoth terrain height
port (Fable-hoth-batchA/tools/hoth_survey.evaluator) and our asset_refs scanner for the closure.
    python -I fit_echo_base.py > ../out/fit.json
"""
import json
import math
import os
import re
import struct
import sys

OUTPUTS = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
sys.path.insert(0, os.path.join(OUTPUTS, 'tools'))
sys.path.insert(0, os.path.join(OUTPUTS, 'Fable-hoth-batchA', 'tools'))
sys.path.insert(0, os.path.join(OUTPUTS, 'Fable-live-client', 't2', 'staged', 'tools', 'swgfmt'))
from swgfmt import trn_iff as I  # noqa: E402
import asset_refs  # noqa: E402
import hoth_survey  # noqa: E402

TEMPLATE = 'object/building/heroic/shared_echo_base.iff'
POB = 'appearance/echo_base_pob.pob'
CUTOUTS = {'hangar': [(-5326.75, 5714.75), (-5277.5, 5681.25), (-5287.25, 5669.0), (-5337.25, 5704.5)],
           'main': [(-5049.25, 5419.0625), (-5040.6875, 5411.625), (-5051.625, 5400.75), (-5059.875, 5408.3125)],
           'tower': [(-5039.625, 5112.125), (-5033.125, 5112.125), (-5033.125, 5099.8125), (-5039.625, 5099.8125)]}
idx = I.client_index()


def get(name):
    arc = idx.get(name.lower())
    return None if arc is None else I.open_tre_entry(os.path.join(I.CLIENT, arc), name)


def forms(node, path=''):
    for n in node.children:
        p = path + '/' + (n.form if n.is_form else n.tag)
        yield p, n
        if n.is_form:
            yield from forms(n, p)


def read_pob(data):
    root = I.parse(data)[0]
    portals, cells = [], []
    for p, n in forms(root):
        if p.endswith('/PRTS/IDTL/0000/VERT'):
            v = struct.unpack('<%df' % (len(n.data) // 4), n.data)
            portals.append([(v[i], v[i + 1], v[i + 2]) for i in range(0, len(v), 3)])
        if p.endswith('/CELS/CELL/0005') and n.is_form:
            cell = {'portals': [], 'name': None}
            for q, m in forms(n):
                if m.tag == 'DATA' and cell['name'] is None:
                    parts = m.data.split(b'\0')
                    cell['name'] = parts[1].decode('latin-1') if len(parts) > 1 else '?'
                    cell['data'] = m.data[:80]
                if q.endswith('/PRTL') and m.is_form:          # FORM PRTL holding one '0005' chunk:
                    for r in m.children:                     # u8 u8 | int32 portal geometry | u8 | int32 target cell | ...
                        if not r.is_form and len(r.data) >= 11:
                            cell['portals'].append({'geometry': struct.unpack_from('<i', r.data, 2)[0], 'target': struct.unpack_from('<i', r.data, 7)[0], 'raw': r.data[:12].hex()})
            cells.append(cell)
    return portals, cells


def centroid(pts):
    return (sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts))


def extent(pts):
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    return max(xs) - min(xs), max(ys) - min(ys)


def fit(local, world):
    """Rigid 2D fit (rotation + translation, optional mirror) of local points onto world points; returns the best."""
    best = None
    for mirror in (1, -1):
        L = [(x * mirror, z) for x, z in local]
        cl, cw = centroid(L), centroid(world)
        a = sum((lx - cl[0]) * (wy - cw[1]) - (lz - cl[1]) * (wx - cw[0]) for (lx, lz), (wx, wy) in zip(L, world))
        b = sum((lx - cl[0]) * (wx - cw[0]) + (lz - cl[1]) * (wy - cw[1]) for (lx, lz), (wx, wy) in zip(L, world))
        th = math.atan2(a, b)
        c, s = math.cos(th), math.sin(th)
        ox, oy = cw[0] - (c * cl[0] - s * cl[1]), cw[1] - (s * cl[0] + c * cl[1])
        mapped = [(ox + c * lx - s * lz, oy + s * lx + c * lz) for lx, lz in L]
        resid = [math.hypot(mx - wx, my - wy) for (mx, my), (wx, wy) in zip(mapped, world)]
        cand = {'mirror_x': mirror == -1, 'theta_rad': th, 'theta_deg': math.degrees(th), 'origin': (ox, oy), 'residual_m': resid, 'rms_m': math.sqrt(sum(r * r for r in resid) / len(resid)), 'mapped': mapped}
        if best is None or cand['rms_m'] < best['rms_m']:
            best = cand
    return best


def main():
    out = {'template': TEMPLATE, 'template_archive': idx.get(TEMPLATE), 'pob_archive': idx.get(POB)}
    portals, cells = read_pob(get(POB))
    out['portal_geometries'] = len(portals)
    out['cells'] = len(cells)
    out['cell_names'] = [c['name'] for c in cells][:41]
    ext = cells[0]['portals']                       # cell 0 = the outside
    out['exterior_portals'] = []
    for pr in ext:
        g = pr['geometry']
        if 0 <= g < len(portals):
            pts = portals[g]
            cx = sum(p[0] for p in pts) / len(pts); cy = sum(p[1] for p in pts) / len(pts); cz = sum(p[2] for p in pts) / len(pts)
            w = extent([(p[0], p[2]) for p in pts])
            out['exterior_portals'].append({'geometry': g, 'to_cell': pr['target'], 'to_cell_name': cells[pr['target']]['name'] if 0 <= pr['target'] < len(cells) else '?',
                                            'centre_local_xyz': (round(cx, 2), round(cy, 2), round(cz, 2)), 'floor_y': round(min(p[1] for p in pts), 2),
                                            'top_y': round(max(p[1] for p in pts), 2), 'width_x_m': round(w[0], 1), 'width_z_m': round(w[1], 1), 'vertices': len(pts)})
    # pair the exterior portals with the cut-outs by size: the widest to the hangar, the smallest to the tower
    cuts = {k: {'centre': centroid(v), 'extent': extent(v), 'span': math.hypot(*extent(v))} for k, v in CUTOUTS.items()}
    out['cutouts'] = {k: {'centre': (round(v['centre'][0], 1), round(v['centre'][1], 1)), 'extent_m': (round(v['extent'][0], 1), round(v['extent'][1], 1))} for k, v in cuts.items()}
    # pairing by the distances between doors: local |1-0| 381 m = hangar-main 381 m, |1-4| 651 m = hangar-tower 645 m,
    # |0-4| 309 m = main-tower 304 m (the by-size pairing of the widest openings was 124 m off)
    PAIRING = {1: 'hangar', 0: 'main', 4: 'tower'}
    byg = {p['geometry']: p for p in out['exterior_portals']}
    pairs = [(byg[g], k) for g, k in PAIRING.items()]
    out['pairing'] = [(g, k, 'portal %.1fx%.1f m, cut-out %.1fx%.1f m' % (byg[g]['width_x_m'], byg[g]['width_z_m'], *cuts[k]['extent'])) for g, k in PAIRING.items()]
    def dist(a, b):
        return math.hypot(a[0] - b[0], a[1] - b[1])
    out['door_distances_m'] = {'local_hangar_main': round(dist((byg[1]['centre_local_xyz'][0], byg[1]['centre_local_xyz'][2]), (byg[0]['centre_local_xyz'][0], byg[0]['centre_local_xyz'][2])), 1),
                               'world_hangar_main': round(dist(cuts['hangar']['centre'], cuts['main']['centre']), 1),
                               'local_hangar_tower': round(dist((byg[1]['centre_local_xyz'][0], byg[1]['centre_local_xyz'][2]), (byg[4]['centre_local_xyz'][0], byg[4]['centre_local_xyz'][2])), 1),
                               'world_hangar_tower': round(dist(cuts['hangar']['centre'], cuts['tower']['centre']), 1),
                               'local_main_tower': round(dist((byg[0]['centre_local_xyz'][0], byg[0]['centre_local_xyz'][2]), (byg[4]['centre_local_xyz'][0], byg[4]['centre_local_xyz'][2])), 1),
                               'world_main_tower': round(dist(cuts['main']['centre'], cuts['tower']['centre']), 1)}
    local = [(p['centre_local_xyz'][0], p['centre_local_xyz'][2]) for p, k in pairs]
    world = [cuts[k]['centre'] for p, k in pairs]
    f = fit(local, world)
    out['fit'] = {k: v for k, v in f.items() if k != 'mapped'}
    out['fit']['mapped_doors'] = [(k, (round(m[0], 1), round(m[1], 1)), 'cut-out', (round(w[0], 1), round(w[1], 1))) for (p, k), m, w in zip(pairs, f['mapped'], world)]
    ev = hoth_survey.evaluator()
    heights = {k: round(ev.height(*cuts[k]['centre']), 1) for k in cuts}
    out['terrain_at_cutouts_m'] = heights
    floors = [(k, p['floor_y']) for p, k in pairs]
    zs = [(k, round(heights[k] - fy, 1)) for k, fy in floors]
    out['building_z_from_each_door'] = zs
    out['building_z_choice'] = round(sum(z for _, z in zs) / len(zs), 1)
    out['building_z_spread_m'] = round(max(z for _, z in zs) - min(z for _, z in zs), 1)
    # closure: every client file the building needs, through the loaded archives
    seen, queue, missing, by_archive = set(), [TEMPLATE], [], {}
    leaves = ('.dds', '.tga', '.wav', '.snd')
    while queue:
        path = queue.pop()
        if path in seen:
            continue
        seen.add(path)
        data = get(path)
        if data is None:
            missing.append(path)
            continue
        by_archive[idx[path]] = by_archive.get(idx[path], 0) + 1
        if path.endswith(leaves) or path.endswith('.flr'):
            continue
        for r in asset_refs.refs(data):
            if r not in seen and r != path:
                queue.append(r)
    out['closure'] = {'files': len(seen), 'missing': sorted(missing), 'by_archive': by_archive}
    print(json.dumps(out, indent=1))


if __name__ == '__main__':
    main()
