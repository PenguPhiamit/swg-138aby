"""Independent packet-layout fixtures; these do NOT execute the C++ observer.

Reference: Core3 PlayerObjectMessage8, WaypointList, and WaypointObject writer.
Use alongside a real client build and captured baseline/delta acceptance tests.
"""
import io
import struct
import unittest


def encode_waypoint(oid=42, name='Ria', x=12.5, y=-24.0, z=7.0):
    name = name.encode('utf-16-le')
    return (struct.pack('<IfffQI', 0, x, z, y, 0, 123)
            + struct.pack('<I', len(name) // 2) + name
            + struct.pack('<QBB', oid, 1, 1))


def read(stream, fmt):
    size = struct.calcsize(fmt)
    data = stream.read(size)
    if len(data) != size:
        raise ValueError('truncated packet')
    return struct.unpack(fmt, data)


def waypoint(stream, key):
    cell, x, z, y, unused, planet = read(stream, '<IfffQI')
    units, = read(stream, '<I')
    if units > 1000:
        raise ValueError('oversized fixture name')
    raw = stream.read(units * 2)
    if len(raw) != units * 2:
        raise ValueError('truncated name')
    oid, color, active = read(stream, '<QBB')
    if key != oid:
        raise ValueError('key mismatch')
    return dict(oid=oid, x=x, y=y, z=z, name=raw.decode('utf-16-le'), active=bool(active))


def apply_map(data, points, previous, known=True):
    stream = io.BytesIO(data)
    count, counter = read(stream, '<II')
    if count > 1000:
        raise ValueError('oversized map')
    fresh = points.copy()
    for _ in range(count):
        op, key = read(stream, '<BQ')
        item = waypoint(stream, key)  # drop carries the complete value too
        if op == 1:
            fresh.pop(key, None)
        elif op in (0, 2):
            fresh[key] = item
        else:
            raise ValueError('unknown operation')
    if stream.read():
        raise ValueError('unexpected trailing fixture bytes')
    return fresh, counter, known and counter == (previous + count) % 2**32


def delta(op=0, key=42, counter=1, **kwargs):
    return struct.pack('<IIBQ', 1, counter, op, key) + encode_waypoint(**kwargs)


class TelemetryWireTests(unittest.TestCase):
    def test_coordinates_unicode_and_active(self):
        item = waypoint(io.BytesIO(encode_waypoint(name='Ria ☃')), 42)
        self.assertEqual((item['x'], item['y'], item['z']), (12.5, -24, 7))
        self.assertEqual(item['name'], 'Ria ☃')
        self.assertTrue(item['active'])

    def test_add_update_drop_include_value(self):
        points, counter, known = apply_map(delta(), {}, 0)
        self.assertTrue(known)
        points, counter, known = apply_map(delta(2, counter=2, x=50), points, counter)
        self.assertEqual(points[42]['x'], 50)
        points, counter, known = apply_map(delta(1, counter=3), points, counter)
        self.assertEqual(points, {})
        self.assertTrue(known)

    def test_gap_never_recovers_without_baseline(self):
        points, counter, known = apply_map(delta(counter=3), {}, 0)
        self.assertFalse(known)
        self.assertFalse(apply_map(delta(counter=4), points, counter, known)[2])

    def test_counter_wrap(self):
        self.assertTrue(apply_map(delta(counter=0), {}, 2**32 - 1)[2])

    def test_mismatch_unknown_and_truncation(self):
        for data in (delta(key=43), delta(op=7), delta()[:-1]):
            with self.subTest(data=data), self.assertRaises(ValueError):
                apply_map(data, {}, 0)

    def test_zero_credits_and_units_are_values(self):
        self.assertEqual(read(io.BytesIO(struct.pack('<ii', 0, 0)), '<ii'), (0, 0))
        self.assertEqual(read(io.BytesIO(struct.pack('<iQ', 250, 99)), '<iQ'), (250, 99))


if __name__ == '__main__':
    unittest.main()
