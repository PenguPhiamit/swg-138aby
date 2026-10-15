"""C24 local format checks; scratch only, never build/publish the client archive."""
import sys
import itertools
import random
import subprocess
import tempfile
import unittest
from fractions import Fraction
from pathlib import Path

OUT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(OUT / 'tools'))
from swgfmt import tre_write, hoth_ui
from swgfmt.fmt_tools import read_tre, _inflate
from swgfmt.fmt_tools import dt_tool
from hoth_gameplay_check import HOTH_TYPES


def backfill(count, rolls, zones=12, maximum=5, present=None):
    """Historical R2 rule, retained only to demonstrate the original defect."""
    present = set(present or ())
    for zone, roll in rolls:
        if zone not in present and count < maximum and roll * zones < count * 1000:
            present.add(zone)
            count += 1
    return count, present


def scaled_pool(pool, zones, scale=0):
    """Arithmetic model of 3a0b154f; no server, database or C++ execution."""
    if scale <= 0 or pool <= 0 or zones <= 0:
        return pool
    return max(1, min((pool * zones + scale // 2) // scale, zones))


def stable_backfill(maps, rolls, zones=12, maximum=5, scale=0,
                    restriction='', in_shift=True):
    """Model only: fixed buckets stand in for String::hashCode() % 1000."""
    maps = set(maps)
    if not rolls or restriction or not in_shift or zones <= 0:
        return maps
    targets = {zone for zone, _ in rolls}
    baseline = len(maps - targets)
    denominator = scale if scale > 0 else zones
    cap = scaled_pool(maximum, zones, scale)
    for zone, roll in rolls:
        if zone not in maps and len(maps) < cap and roll * denominator < baseline * 1000:
            maps.add(zone)
    return maps


class ResourcePolicy(unittest.TestCase):
    def test_original_counterexample_fixed_with_scaling_on_and_off(self):
        original = {'stock0', 'stock1'}
        rolls = [('A', 200), ('B', 100), ('C', 999)]
        for scale in (0, 10):
            first = stable_backfill(original, rolls, scale=scale)
            self.assertEqual(first, original | {'B'})
            for _ in range(4):
                self.assertEqual(stable_backfill(first, rolls, scale=scale), first)

    def test_seeded_multi_zone_fixed_point_and_cap(self):
        rng = random.Random(24)
        for _ in range(20000):
            zones = rng.randint(4, 30)
            scale = rng.choice((0, 10))
            targets = [f'new{i}' for i in range(rng.randint(2, min(5, zones - 1)))]
            maps = {f'stock{i}' for i in range(rng.randint(0, zones - len(targets)))}
            maps.update(t for t in targets if rng.randrange(4) == 0)
            rolls = [(t, rng.randrange(1000)) for t in targets]
            maximum = rng.randint(1, 10)
            cap = scaled_pool(maximum, zones, scale)
            first = stable_backfill(maps, rolls, zones, maximum, scale)
            self.assertTrue(maps <= first)
            self.assertLessEqual(len(first), max(len(maps), cap))
            self.assertEqual(first - set(targets), maps - set(targets))
            for _ in range(4):
                self.assertEqual(stable_backfill(first, rolls, zones, maximum, scale), first)

    def test_target_order_only_selects_winner_when_cap_is_exhausted(self):
        maps = {f'stock{i}' for i in range(8)}
        rolls = [('A', 0), ('B', 0), ('C', 0)]
        for order in itertools.permutations(rolls):
            first = stable_backfill(maps, order, zones=13, maximum=7, scale=10)
            self.assertEqual(first, maps | {order[0][0]})  # scaled cap = 9
            self.assertEqual(stable_backfill(first, order, 13, 7, 10), first)
            self.assertEqual(stable_backfill(maps, order, 13, 10, 10), maps | {'A', 'B', 'C'})

    def test_existing_natural_target_maps_do_not_raise_odds(self):
        maps = {'stock0', 'stock1', 'A'}
        rolls = [('A', 0), ('B', 250), ('C', 100)]
        self.assertEqual(stable_backfill(maps, rolls, scale=10), maps | {'C'})
        # Two maps outside targets mean 20%, even though three maps already exist.

    def test_scaled_rounding_and_bounds_against_exact_fraction(self):
        for zones in range(1, 41):
            for scale in (1, 3, 10, 11, 40):
                last = 0
                for pool in range(1, 343):
                    expected = int(Fraction(pool * zones, scale) + Fraction(1, 2))
                    result = scaled_pool(pool, zones, scale)
                    self.assertEqual(result, max(1, min(expected, zones)))
                    self.assertGreaterEqual(result, last)
                    last = result
        self.assertEqual([scaled_pool(p, 12, 10) for p in (1, 3, 8)], [1, 4, 10])
        self.assertEqual(scaled_pool(8, 20, 10), 16)
        self.assertEqual(scaled_pool(1, 15, 10), 2)  # exact half rounds up

    def test_stock_and_empty_inputs_preserved(self):
        for pool in range(343):
            for scale in (0, -1):
                self.assertEqual(scaled_pool(pool, 12, scale), pool)
            self.assertEqual(scaled_pool(pool, 0, 10), pool)
        for pool in range(1, 11):
            self.assertEqual(scaled_pool(pool, 10, 10), pool)
        self.assertEqual(scaled_pool(0, 12, 10), 0)
        maps = {'stock0'}
        for kwargs in ({'restriction': 'hoth'}, {'in_shift': False}, {'zones': 0}):
            self.assertEqual(stable_backfill(maps, [('A', 0)], **kwargs), maps)
        self.assertEqual(stable_backfill(maps, []), maps)
        self.assertEqual(stable_backfill(set(), [('A', 0)], scale=10), set())

    def test_threshold_equality_and_no_deletion_above_cap(self):
        maps = {f'stock{i}' for i in range(8)}
        self.assertEqual(stable_backfill(maps, [('A', 799), ('B', 800)], maximum=8, scale=10), maps | {'A'})
        self.assertEqual(stable_backfill(maps, [('A', 0)], maximum=1, scale=10), maps)

    def test_changed_configuration_is_outside_fixed_point_contract(self):
        maps = {'stock0', 'stock1', 'A'}
        rolls = [('A', 0), ('B', 250)]
        self.assertEqual(stable_backfill(maps, rolls, scale=10), maps)
        self.assertEqual(stable_backfill(maps, [('B', 250)], scale=10), maps | {'B'})


class ResourceSourceBoundary(unittest.TestCase):
    """Read-only pinned-source checks; pairs the model with the reviewed wiring."""
    @classmethod
    def setUpClass(cls):
        cls.prefix = ['wsl', '-d', 'Debian', '-u', 'swgemu', '--', 'git', '-C', '/opt/swg/Core3-dev']
        cls.path = 'MMOCoreORB/src/server/zone/managers/resource/resourcespawner/ResourceSpawner.cpp'
        cls.source = cls.read('3a0b154f', cls.path)

    @classmethod
    def read(cls, revision, path):
        return subprocess.check_output(cls.prefix + ['show', revision + ':' + path], encoding='utf-8')

    def test_model_matches_reviewed_policy_wiring(self):
        compact = ' '.join(self.source.split())
        for fragment in (
            'if (poolScaleZones <= 0 || pool <= 0 || zones <= 0) return pool;',
            '(pool * zones + poolScaleZones / 2) / poolScaleZones',
            'Math::max(1, Math::min(scaled, zones))',
            'maxPool = scaledPool(resourceEntry->getMaxpool())',
            'zones = poolScaleZones > 0 ? poolScaleZones : activeResourceZones.size()',
            'if (!backfillZones.contains(resourceSpawn->getSpawnMapZone(i))) ++baseMaps;',
            'if (roll * zones >= baseMaps * 1000)',
            'scaledPool(resourceEntry->getMinpool()), scaledPool(resourceEntry->getMaxpool())',
        ):
            self.assertIn(fragment, compact)
        current = self.read('90044b8e', self.path)
        self.assertEqual(current, self.source)

    def test_top_up_is_identical_to_before_both_commits(self):
        def block(source):
            start = source.index('\t\t\t\tint minPool =')
            return source[start:source.index('\n\t\t\t\t// Backfill', start)]
        self.assertEqual(block(self.source), block(self.read('98ad1d1d^', self.path)))
        self.assertNotIn('scaledPool', block(self.source))

    def test_missing_key_default_and_zone_restriction_wiring(self):
        header = self.read('3a0b154f', self.path[:-4] + '.h')
        manager = self.read('3a0b154f', 'MMOCoreORB/src/server/zone/managers/resource/ResourceManagerImplementation.cpp')
        spawn = self.read('3a0b154f', 'MMOCoreORB/src/server/zone/objects/resource/ResourceSpawnImplementation.cpp')
        lua = self.read('sandbox', 'MMOCoreORB/bin/scripts/managers/resource_manager.lua')
        self.assertIn('int poolScaleZones = 0;', header)
        self.assertIn('setPoolScaleZones(lua->getGlobalInt("poolScaleZones"))', manager)
        self.assertNotIn('poolScaleZones', lua)
        self.assertIn('resourceEntry->getZoneRestriction().isEmpty()', self.source)
        self.assertIn('if (zonerestriction != "") {\n\t\tzonenames.add(zonerestriction);\n\t\treturn zonenames;', spawn)


class Formats(unittest.TestCase):
    def test_ten_minimum_pool_leaves_exist_in_staged_tree(self):
        table = dt_tool.read(str(OUT / 'Local-content/local_planets/datatables/resource/resource_tree.iff'))
        names = [r[1] for r in table['rows']]
        self.assertTrue(HOTH_TYPES <= set(names))
        self.assertTrue(all(names.count(name) == 1 for name in HOTH_TYPES))

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
