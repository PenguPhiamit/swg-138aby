"""Ossus O15: reads the blade-draw capture (mirage-draws-<pid>.log) for the light whip's step 0 (Claude, 18 Oct 2026).

The question (Documentation-support/lightwhip-design.md, step 0): can the blade's base and tip be recovered every
frame from the game's draw? The first capture (18 Oct, 8:46 PM) showed how the client draws a blade: per blade per
frame a 4-vertex triangle fan in object space, x at plus and minus half the width, y 0, z from 0 (base) to the
current length (tip), plus a line list over the fan's first two vertices (one edge). A blade that is off or still
igniting draws with length 0. For each blade program this reports:
  - the calls, vertex counts, layouts and vertex programs seen;
  - how c4-c7 (object to world) are packed: "dot" (world.x = dot(p, c4), the default column-major packing of
    SWG's mul(p, M)) or "rows" (world = p.x*c4 + p.y*c5 + p.z*c6 + c7), told apart by where the 0 0 0 1 sits;
  - whether every quad has that shape, the full length, the ignition, the scale and where vertex 0 sits;
  - each blade on screen as a track (the base nearest the frame before), its frames, gaps and base and tip speed.
Then a verdict: step 3 can use this, or which check failed.

Usage: python capture_read.py [log ...] [--csv out.csv]
Without a log it reads every SWG-client/mirage-draws-*.log. Pure Python (no numpy on this PC).
"""
import argparse
import csv
import glob
import math
import os
import re
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CLIENT = os.path.join(os.path.dirname(os.path.dirname(HERE)), 'SWG-client')
NAMES = {0xacc853c5: 'stock saber', 0x0ea2a331: 'O14 saber (4c5a29d0)', 0xfac25b60: 'O14 saber (b9fbc48a)',
         0x238eb66a: 'light whip'}

HEAD = re.compile(r'^draw (\d+) frame (\d+) t ([\d.]+) ps 0x([0-9a-f]+) (\w+) type (\d+)(.*)$')


def floats(text):
    return [float(x) for x in text.replace('|', ' ').split()]


def parse(path):
    draws, notes, cur = [], [], None
    for line in open(path, errors='replace'):
        line = line.rstrip('\n')
        m = HEAD.match(line)
        if m:
            cur = {'n': int(m[1]), 'frame': int(m[2]), 't': float(m[3]), 'ps': int(m[4], 16), 'kind': m[5],
                   'type': int(m[6]), 'args': m[7].strip(), 'pos': [], 'rows': [], 'c': {}, 'ff': {}}
            draws.append(cur)
            continue
        if not line.startswith(' '):
            if line.strip():
                notes.append(line.strip())
            continue
        if cur is None:
            continue
        s = line.strip()
        if s.startswith('pos '):
            cur['pos'] = [tuple(float(v) for v in p.split(',')) for p in s[4:].split() if ',' in p]
            cur['pos_cut'] = s.endswith('...')
        elif re.match(r'^v\d+ ', s):
            cur['rows'].append(s)
        elif re.match(r'^c\d+-c\d+ ', s):
            k = int(s[1:s.index('-')])
            v = floats(s.split(' ', 1)[1])
            for i in range(4):
                cur['c'][k + i] = v[i * 4:i * 4 + 4]
        elif s.startswith('fixed function '):
            name, rest = s[len('fixed function '):].split(' ', 1)
            v = floats(rest)
            cur['ff'][name] = [v[i * 4:i * 4 + 4] for i in range(4)]
        elif s.startswith('stream0 '):
            cur['stream'] = s
        elif s.startswith('layout '):
            cur['layout'] = s[7:]
        elif s.startswith('vs 0x'):
            cur['vs'] = s.split()[1]
        elif s.startswith('ps c3 '):
            v = floats(s.replace('ps c3', '').replace('c7', ''))
            cur['c3'], cur['c7'] = v[:4], v[4:8]
        elif s.startswith('indices '):
            cur['indices'] = [int(x) for x in s.split()[1:]]
        else:
            cur.setdefault('other', []).append(s)
    return draws, notes


# ---- small vector helpers ----

def sub(a, b):
    return tuple(x - y for x, y in zip(a, b))


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def norm(a):
    return math.sqrt(dot(a, a))


def mean_pt(ps):
    return tuple(sum(p[i] for p in ps) / len(ps) for i in range(3))


def apply(m, p, conv):
    v = (p[0], p[1], p[2], 1.0)
    if conv == 'dot':
        r = [dot(v, m[i]) for i in range(4)]
    else:
        r = [sum(v[k] * m[k][i] for k in range(4)) for i in range(4)]
    w = r[3] if abs(r[3]) > 1e-9 else 1.0
    return (r[0] / w, r[1] / w, r[2] / w), r[3]


def world_matrix(d):
    if all(k in d['c'] for k in (4, 5, 6, 7)):
        return [d['c'][4], d['c'][5], d['c'][6], d['c'][7]], None
    if 'world' in d['ff']:
        return d['ff']['world'], 'rows'   # fixed function: row vectors, translation in the 4th row
    return None, None


def guess_conv(m):
    """'dot' when the 4th register is 0 0 0 1, 'rows' when the 4th column is 0 0 0 1, '' when both or neither."""
    eps = 1e-4
    is_dot = all(abs(m[3][i] - (1.0 if i == 3 else 0.0)) < eps for i in range(4))
    is_rows = all(abs(m[i][3] - (1.0 if i == 3 else 0.0)) < eps for i in range(4))
    if is_dot and not is_rows:
        return 'dot'
    if is_rows and not is_dot:
        return 'rows'
    return ''


def axis_ends(ps):
    """The long axis (power iteration on the covariance) and the centres of its two end caps."""
    c = mean_pt(ps)
    q = [sub(p, c) for p in ps]
    cov = [[sum(a[i] * a[j] for a in q) for j in range(3)] for i in range(3)]
    v = (1.0, 0.7, 0.3)
    for _ in range(60):
        v = tuple(dot(cov[i], v) for i in range(3))
        n = norm(v)
        if n < 1e-12:
            return None
        v = tuple(x / n for x in v)
    t = [dot(a, v) for a in q]
    lo, hi = min(t), max(t)
    length = hi - lo
    if length < 1e-6:
        return None
    tol = 0.08 * length
    a = mean_pt([p for p, s in zip(ps, t) if s <= lo + tol])
    b = mean_pt([p for p, s in zip(ps, t) if s >= hi - tol])
    width = 2 * max(norm(sub(sub(p, c), tuple(s * x for x in v))) for p, s in zip(ps, t))
    return {'a': a, 'b': b, 'len': norm(sub(b, a)), 'width': width, 't': t, 'lo': lo, 'hi': hi}


def fmt(p):
    return '(%.3f, %.3f, %.3f)' % p


def pct(n, d):
    return '%d of %d (%.0f%%)' % (n, d, 100.0 * n / d) if d else '0 of 0'


def blade_ends(d):
    """SWG's blade quad (first capture, 18 Oct 8:46 PM): a 4-vertex fan at y 0, x at plus and minus half the width,
    z from 0 (base) to the blade's current length (tip). Returns the object-space base, tip, length and half width,
    or None when the draw has another shape."""
    ps = d['pos']
    if d['type'] != 6 or len(ps) != 4:
        return None
    zs = [p[2] for p in ps]
    lo, hi = min(zs), max(zs)
    if any(abs(p[1]) > 1e-3 for p in ps) or any(min(abs(z - lo), abs(z - hi)) > 1e-3 for z in zs):
        return None
    base = mean_pt([p for p in ps if abs(p[2] - lo) <= 1e-3])
    tip = mean_pt([p for p in ps if abs(p[2] - hi) <= 1e-3])
    return {'base': base, 'tip': tip, 'len': hi - lo, 'half': max(abs(p[0]) for p in ps),
            'v0_tip': abs(ps[0][2] - hi) <= 1e-3}


def analyse(path, csv_rows):
    draws, notes = parse(path)
    print('==== %s: %d draws' % (os.path.basename(path), len(draws)))
    for n in notes[:4]:
        print('  note:', n)
    keys = sum(1 for n in notes if n.startswith('capture key'))
    if keys:
        print('  capture key pressed %d times' % keys)
    by_ps = {}
    for d in draws:
        by_ps.setdefault(d['ps'], []).append(d)
    verdicts = []
    for ps, ds in sorted(by_ps.items(), key=lambda kv: kv[1][0]['n']):
        name = NAMES.get(ps, 'unknown program')
        print('\n-- 0x%08x %s: %d draws, frames %d to %d' % (ps, name, len(ds), ds[0]['frame'], ds[-1]['frame']))
        print('  calls:', ', '.join('%s type %d, %d vertices: %d' % (k, t, n, sum(
            1 for d in ds if (d['kind'], d['type'], len(d['pos'])) == (k, t, n)))
            for k, t, n in sorted({(d['kind'], d['type'], len(d['pos'])) for d in ds})))
        print('  layouts:', '; '.join(sorted({d['layout'] for d in ds if 'layout' in d})) or '(logged at first use only)')
        print('  vertex programs:', ', '.join(sorted({d.get('vs', '-') for d in ds})))

        # how c4-c7 are packed
        convs = {}
        for d in ds:
            m, forced = world_matrix(d)
            if m is not None:
                g = forced or guess_conv(m)
                convs[g] = convs.get(g, 0) + 1
        sure = {k: v for k, v in convs.items() if k}
        conv = max(sure, key=sure.get) if sure else 'dot'
        print('  c4-c7 packing:', ', '.join('%s %d' % (k or 'undecided', v) for k, v in convs.items()) or 'none',
              '-> "%s"' % conv)

        # the quads: shape, lit or not, world ends
        quads = [d for d in ds if d['type'] == 6]
        lines = [d for d in ds if d['type'] == 2]
        other = [d for d in ds if d['type'] not in (2, 6)]
        rec, odd, off = [], 0, 0
        for d in quads:
            e = blade_ends(d)
            m, forced = world_matrix(d)
            if e is None or m is None:
                odd += 1
                continue
            if e['len'] < 0.01:
                off += 1
                continue
            c = forced or conv
            base, tip = apply(m, e['base'], c)[0], apply(m, e['tip'], c)[0]
            scale = norm(sub(tip, base)) / e['len']
            rec.append({'d': d, 'base': base, 'tip': tip, 'olen': e['len'], 'wlen': norm(sub(tip, base)),
                        'half': e['half'], 'scale': scale, 'v0_tip': e['v0_tip'],
                        'cam': tuple(d['c'][8][:3]) if 8 in d['c'] else None})
        print('  quads (fan, 4 vertices): %d; edge lines (line list, the quad\'s first 2 vertices): %d; other: %d'
              % (len(quads), len(lines), len(other)))
        print('  quads with the base-to-tip shape:', pct(len(quads) - odd, len(quads)),
              '; lit (length > 1 cm):', len(rec), '; zero length (off or igniting):', off)
        if not rec:
            verdicts.append((ps, name, False, 'no lit blade quad with the expected shape' if odd < len(quads) else
                             'the quads have another shape'))
            continue
        olens = sorted({round(r['olen'], 2) for r in rec})
        full = max(r['olen'] for r in rec)
        nfull = sum(1 for r in rec if r['olen'] > full - 0.01)
        print('  object length: full %.2f in %d draws, growing or shrinking in %d (%.2f to %.2f)'
              % (full, nfull, len(rec) - nfull, olens[0], olens[-1]))
        print('  half width %.3f; object to world scale %.3f to %.3f; world length at full %.3f'
              % (statistics.mean(r['half'] for r in rec), min(r['scale'] for r in rec),
                 max(r['scale'] for r in rec), statistics.mean(r['wlen'] for r in rec if r['olen'] > full - 0.01)))
        print('  vertex 0 at the tip:', pct(sum(1 for r in rec if r['v0_tip']), len(rec)))

        # blades on screen: tracks matched by the nearest base from the frame before
        tracks = []
        for r in rec:
            f = r['d']['frame']
            best, bd = None, 1.0
            for tr in tracks:
                last = tr[-1]
                if last['d']['frame'] < f and f - last['d']['frame'] <= 10:
                    dist = norm(sub(r['base'], last['base']))
                    if dist < bd:
                        best, bd = tr, dist
            if best is None:
                tracks.append([r])
            else:
                best.append(r)
        tracks.sort(key=len, reverse=True)
        print('  blades tracked (base within 1 m of the frame before): %d; the longest:' % len(tracks))
        gaps_total = spans_total = 0
        vb_all, vt_all = [], []
        for tr in tracks[:4]:
            fr = [r['d']['frame'] for r in tr]
            span = fr[-1] - fr[0] + 1
            seen = len(set(fr))
            vb, vt, jumps = [], [], 0
            for r0, r1 in zip(tr, tr[1:]):
                df = r1['d']['frame'] - r0['d']['frame']
                dt = r1['d']['t'] - r0['d']['t']
                if df != 1 or dt <= 0:
                    continue
                vb.append(norm(sub(r1['base'], r0['base'])) / dt)
                vt.append(norm(sub(r1['tip'], r0['tip'])) / dt)
            cams = [norm(sub(r['base'], r['cam'])) for r in tr if r['cam']]
            print('    frames %d-%d: %d draws, %d of %d frames; base speed median %.2f max %.2f m/s, tip median %.2f '
                  'max %.2f m/s; camera %.1f m' % (fr[0], fr[-1], len(tr), seen, span,
                                                    statistics.median(vb) if vb else 0, max(vb) if vb else 0,
                                                    statistics.median(vt) if vt else 0, max(vt) if vt else 0,
                                                    statistics.median(cams) if cams else 0))
        for tr in tracks:
            fr = [r['d']['frame'] for r in tr]
            # frames inside a track's runs (a run breaks at a gap of more than 10 frames: budget or off screen)
            spans_total += len(set(fr))
            gaps_total += sum(b - a - 1 for a, b in zip(fr, fr[1:]) if 1 < b - a <= 10)
            for r0, r1 in zip(tr, tr[1:]):
                dt = r1['d']['t'] - r0['d']['t']
                if r1['d']['frame'] - r0['d']['frame'] == 1 and dt > 0:
                    vb_all.append(norm(sub(r1['base'], r0['base'])) / dt)
                    vt_all.append(norm(sub(r1['tip'], r0['tip'])) / dt)
        print('  frames missing inside tracks (gaps of 2 to 10 frames): %d, against %d frames seen'
              % (gaps_total, spans_total))
        if vb_all:
            print('  all tracks: base speed mean %.2f m/s, tip mean %.2f m/s' % (statistics.mean(vb_all),
                                                                               statistics.mean(vt_all)))

        for r in rec:
            d = r['d']
            csv_rows.append([os.path.basename(path), '0x%08x' % ps, d['n'], d['frame'], d['t'], d['kind'], d['type'],
                             len(d['pos'])] + ['%.4f' % x for x in r['base'] + r['tip']] +
                            ['%.4f' % r['wlen'], '%.4f' % r['olen']])

        fails = []
        if odd:
            fails.append('%d quads have another shape' % odd)
        if sum(1 for r in rec if r['v0_tip']) not in (0, len(rec)):
            fails.append('vertex 0 is not always at the same end')
        if spans_total and gaps_total > 0.02 * spans_total:
            fails.append('%d frames missing inside tracks' % gaps_total)
        if not sure:
            fails.append('the c4-c7 packing was not decided')
        verdicts.append((ps, name, not fails, '; '.join(fails) or
                         'base = object (0, 0, 0), tip = object (0, 0, length) through c4-c7 ("%s"); full length '
                         '%.2f (world %.2f)' % (conv, full, full * statistics.mean(r['scale'] for r in rec))))

    print('\n== verdict')
    for ps, name, ok, why in verdicts:
        print('  0x%08x %s: %s -- %s' % (ps, name, 'base and tip recoverable every frame' if ok else 'NOT YET', why))
    return verdicts


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument('logs', nargs='*')
    ap.add_argument('--csv')
    args = ap.parse_args(argv)
    logs = args.logs or sorted(glob.glob(os.path.join(CLIENT, 'mirage-draws-*.log')), key=os.path.getmtime)
    if not logs:
        raise SystemExit('no mirage-draws-*.log in %s (log_draws=0, or no blade drawn yet?)' % CLIENT)
    rows = []
    for p in logs:
        analyse(p, rows)
        print()
    if args.csv:
        with open(args.csv, 'w', newline='') as f:
            w = csv.writer(f)
            w.writerow(['log', 'ps', 'draw', 'frame', 't', 'kind', 'type', 'verts', 'ax', 'ay', 'az', 'bx', 'by', 'bz',
                        'world_length', 'object_length'])
            w.writerows(rows)
        print('per-draw ends written to', args.csv)


if __name__ == '__main__':
    main(sys.argv[1:])
