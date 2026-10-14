"""Height evaluator with roads: the prototype's Core3 port (Fable-planet-test/tools/trn_read.py) plus a port of
AffectorRoad::process, RoadRectangle, HeightData::findNearestHeight and Segment (Core3-dev src/terrain/layer/**,
AGPL-3.0, read as reference; the Hakry 2024 road code). Our own code (Fable, 14 Oct 2026), kept only for checking
our own terrain. Core3's reader loads the HDTA segments and smooths them (Segment::createRoadwayHeights); the
evaluator does the same from the parsed 'segments' lists.
"""
import math
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'Fable-planet-test', 'tools'))
import trn_read  # noqa: E402

OUT_OF_RANGE = 500.0


class Segment:
    def __init__(self, points):   # points as parsed: (x, z, y)
        self.positions = [(x, y, z) for x, z, y in points]   # (x, y, z) world x, world y, height
        self.flat = False
        last_z = 0.0
        for x, y, z in self.positions:
            self.flat = (z == last_z)
            last_z = z
        self._create_roadway_heights()

    def _create_roadway_heights(self):
        if self.flat or len(self.positions) < 3:
            return
        old = self.positions
        new = [old[0]]
        for i in range(1, len(old) - 1):
            z_avg = (old[i - 1][2] + old[i][2] + old[i + 1][2]) / 3.0
            new.append((old[i][0], old[i][1], z_avg))
        new.append(old[-1])
        self.positions = new

    def has_initial_coordinate(self, x, y):
        return bool(self.positions) and self.positions[0][0] == x and self.positions[0][1] == y

    def find_nearest_height(self, base, px, py, cx, cy, direction):
        n = len(self.positions)
        if n < 3 or self.flat:
            return self.positions[0][2]
        first, last = self.positions[0], self.positions[-1]
        d_first = (first[0] - px) ** 2 + (first[1] - py) ** 2
        d_last = (last[0] - px) ** 2 + (last[1] - py) ** 2
        dx, dy = cx - px, cy - py
        rotated_y = dx * math.sin(-direction) - dy * math.cos(-direction)
        ry2 = rotated_y * rotated_y
        new_height, seg = 0.0, -1
        half = (n - 1) // 2
        if d_first <= d_last:
            for i in range(1, n):
                p = self.positions[i]
                if (p[0] - cx) ** 2 + (p[1] - cy) ** 2 > ry2 and i <= half:
                    continue
                seg, new_height = i, p[2]
                break
        else:
            for i in range(n - 1, 0, -1):
                p = self.positions[i]
                if (p[0] - cx) ** 2 + (p[1] - cy) ** 2 > ry2 and i > half:
                    continue
                seg, new_height = i + 1, p[2]
                break
        if 0 < seg <= n - 1:
            b, a = self.positions[seg - 1], self.positions[seg]
            total = math.hypot(a[0] - b[0], a[1] - b[1])
            after_from_centre = math.hypot(a[0] - cx, a[1] - cy)
            pos_dist = total - abs(after_from_centre - abs(rotated_y))
            if rotated_y > 0 and half + 1 == seg:
                pos_dist = total - (after_from_centre + abs(rotated_y))
            var = min(max(pos_dist / total if total else 1.0, 0.001), 1.0)
            new_height = b[2] + var * (a[2] - b[2])
        return new_height if new_height != 0.0 else base


class RoadRect:
    def __init__(self, x0, y0, x1, y1, start_x, start_y, width, direction):
        self.cx, self.cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
        self.start = (start_x, start_y)
        self.width, self.height, self.direction = width, math.hypot(x1 - x0, y1 - y0), direction

    def contains(self, x, y):
        dx, dy = self.cx - x, self.cy - y
        rx = dx * math.cos(-self.direction) + dy * math.sin(-self.direction)
        ry = dx * math.sin(-self.direction) - dy * math.cos(-self.direction)
        return abs(rx) <= self.width / 2.0 and abs(ry) <= self.height / 2.0


class Road:
    def __init__(self, rule):
        pts = rule['points']
        self.start, self.end, self.mids = pts[0], pts[-1], pts[1:-1]
        self.width = rule['width'] * 0.7
        self.segments = [Segment(s) for s in rule.get('segments', [])] if rule.get('road_kind') == 'HDTA' else []
        self.rects = []
        p = self.start
        for m in self.mids:
            self._add_rect(p, m)
            p = m
        self._add_rect(p, self.end)

    def _add_rect(self, p1, p2):
        half = self.width / 2.0
        ang = math.atan2(p1[1] - p2[1], p1[0] - p2[0])
        ang = math.pi / 2 - ang
        if ang < 0:
            ang = math.pi + (math.pi + ang)
        x_ll = p2[0] + (-half * math.cos(ang))
        y_ll = p2[1] + (half * math.sin(ang))
        x_ur = p1[0] + (half * math.cos(ang))
        y_ur = p1[1] + (-half * math.sin(ang))
        self.rects.append(RoadRect(x_ll, y_ll, x_ur, y_ur, p1[0], p1[1], self.width, ang))

    def process(self, x, y, transform, base):
        if not self.segments or transform == 0:
            return base
        if (x - self.start[0]) ** 2 + (y - self.start[1]) ** 2 > OUT_OF_RANGE * OUT_OF_RANGE:
            return base
        for r in self.rects:
            if r.contains(x, y):
                for s in self.segments:
                    if s.has_initial_coordinate(*r.start):
                        return s.find_nearest_height(base, x, y, r.cx, r.cy, r.direction)
                return base
        return base


def _f32(v):
    return struct.unpack('<f', struct.pack('<f', v))[0]


def bitmap_filter32(bm, flt, x, y, rect):
    """FilterBitmap::process with Core3's float arithmetic at the one point where it matters: a saturated (255)
    pixel gives m = 255 * (1/255 in float) == 1.0f exactly, which Core3 then clamps to 0.99999; in double arithmetic
    the product is 1.00000006 and the max test (m < 1) would wrongly reject it."""
    width, height, px = bm
    if not (rect[1] > rect[0] and rect[3] > rect[2]):
        return 0.0
    tx = min((x - rect[0]) * width / (rect[1] - rect[0]), width - 1)
    ty = min((y - rect[2]) * height / (rect[3] - rect[2]), height - 1)
    v41, v43 = int(ty), int(tx)
    v39 = min(tx + 1, width - 1)
    arg1 = min(int(ty) + 1, height - 1)
    v25 = width * (height - v41 - 1)
    v26, v27 = int(v39), int(v43)

    def get(i):
        return px[i] if 0 <= i < len(px) else 0
    v28, arg2 = get(v27 + v25), get(v26 + v25)
    v29 = width * (height - int(arg1) - 1)
    arg6, arg1v = get(v29 + v27), get(v26 + v29)
    v30, v31 = tx - v43, ty - v41
    k = 0.003921568859368563
    m = _f32(v31 * (1.0 - v30) * arg6 * k + v31 * v30 * arg1v * k + (1.0 - v31) * (1.0 - v30) * v28 * k + (1.0 - v31) * v30 * arg2 * k)
    if m == 1.0:
        m = 0.9999899864196777
    lo, hi, fa = flt['min'], flt['max'], flt['feather']
    if not (lo < m < hi):
        return 0.0
    v35 = (hi - lo) * fa * 0.5
    if m >= lo + v35:
        return m if m <= hi - v35 else m * (hi - m) / v35
    return m * (m - lo) / v35


class RoadHeightEvaluator(trn_read.HeightEvaluator):
    """HeightEvaluator that also applies AROA affectors (HDTA roads), as ProceduralTerrainAppearance does, and
    samples bitmap filters with float32 rounding (see bitmap_filter32)."""

    def __init__(self, trn, bitmap_loader=None):
        super().__init__(trn, bitmap_loader)
        self.roads = {}

    def filter_process(self, flt, x, y, transform, base, rect):
        if flt['type'] == 'FBIT':
            bm = self._bitmap(flt['bitmap'])
            if bm is None:
                self.warnings.append(f'filter {flt["name"]}: bitmap {flt["bitmap"]} not loaded (Core3 returns 1 if missing)')
                return 1.0
            return bitmap_filter32(bm, flt, x, y, rect)
        return super().filter_process(flt, x, y, transform, base, rect)

    def affector_process(self, a, x, y, transform, base):
        if a['type'] == 'AROA':
            key = id(a)
            if key not in self.roads:
                self.roads[key] = Road(a)
            return self.roads[key].process(x, y, transform, base)
        return super().affector_process(a, x, y, transform, base)
