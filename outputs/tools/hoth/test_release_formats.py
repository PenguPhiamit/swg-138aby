"""C24 local format checks; scratch only, never build/publish the client archive."""
import sys
import tempfile
import unittest
from pathlib import Path

OUT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(OUT / 'tools'))
from swgfmt import tre_write, hoth_ui
from swgfmt.fmt_tools import read_tre, _inflate


def backfill(count, rolls, zones=12, maximum=5, present=None):
    present = set(present or ())
    for zone, roll in rolls:
        if zone not in present and count < maximum and roll * zones < count * 1000:
            present.add(zone)
            count += 1
    return count, present


class Formats(unittest.TestCase):
    def test_tre_independent_reader(self):
        files = {'a.txt': b'a' * 2000, 'empty.bin': b'', 'path/b.bin': bytes(range(256))}
        raw = tre_write.pack(files)
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'test.tre'
            path.write_bytes(raw)
            result = {}
            for entry in read_tre(str(path)):
                start = entry['offset']
                blob = raw[start:start + (entry['comp_size'] if entry['comp'] else entry['size'])]
                result[entry['name']] = _inflate(blob, entry['comp'], entry['size'])
            self.assertEqual(result, files)

    def test_tre_duplicate_case_is_rejected(self):
        with self.assertRaises(ValueError):
            tre_write.pack({'A.txt': b'a', 'a.txt': b'b'})

    def test_ui_stock_bytes_kept(self):
        def base(p):
            return (OUT / 'Documentation-support/hoth/client-base' / p).read_bytes()
        with tempfile.TemporaryDirectory() as folder:
            report = hoth_ui.stage_hoth_ui(folder, base)
            self.assertTrue(all(x['base_lines_kept'] and x['crlf_only'] for x in report['files'].values()))

    def test_r2_multiple_zones_reroll_loser_after_other_win(self):
        rolls = [('A', 200), ('B', 100)]
        first_count, first = backfill(2, rolls)
        second_count, second = backfill(first_count, rolls, present=first)
        self.assertEqual(first, {'B'})
        self.assertEqual(second, {'A', 'B'})  # counterexample to staged R2 idempotence claim


if __name__ == '__main__':
    unittest.main()
