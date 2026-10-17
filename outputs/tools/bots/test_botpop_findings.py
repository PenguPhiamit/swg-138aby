"""Offline checks for botpop_findings.py and planet_census.py on small synthetic logs; no server or bot access."""
import csv
import json
import os
import tempfile
import unittest

from botpop_findings import metrics, findings, render, main as findings_main, signature
from planet_census import main as census_main, read, square


def row(e, t, **kw):
    return dict(e=e, t=t * 1000, **dict({'bot': 1}, **kw))


def spawn(bot, role, t=0, planet='tatooine'):
    return row('spawn', t, bot=bot, role=role, city='Bestine', planet=planet, x=0, y=0)


def missions(bot, role, taken, done, t0=10):
    rows = []
    for i in range(taken):
        t = t0 + i * 10
        rows.append(row('mission_take', t, bot=bot, role=role, lvl=2, mlvl=3, reward=500, planet='tatooine', x=0, y=0))
        if i < done:
            rows.append(row('mission_done', t + 5, bot=bot, role=role, paid=500, reward=500, planet='tatooine', x=0, y=0))
        else:
            rows.append(row('mission_abort', t + 5, bot=bot, role=role, lair_seen=True, planet='tatooine', x=0, y=0))
    return rows


def lair_check(bot, t, ranged, damage, los=True, attackable=True):
    return row('lair_check', t, bot=bot, lair='tatooine_womprat_lair', dist=5, los=los, weapon='rifle' if ranged else 'unarmed',
               ranged=ranged, max_range=64 if ranged else 5, attackable=attackable, posture=0, damage=damage, max=1000,
               planet='tatooine', x=100, y=100)


def read_text(path):
    with open(path, encoding='utf-8') as f:
        return f.read()


def status(found, section, contains=''):
    return [st for sec, st, text in found if sec.startswith(section) and contains in text]


class FindingsTest(unittest.TestCase):
    def base(self):
        rows = [spawn(1, 'brawler'), spawn(2, 'marksman'), spawn(3, 'medic')]
        rows += missions(1, 'brawler', 25, 12) + missions(2, 'marksman', 25, 1, t0=20)
        rows += [row('server', 600 + i * 60, online=3, tick_ms_avg=2, tick_ms_max=30, skipped=0, rss_mb=100, travels=0) for i in range(3)]
        return rows

    def test_combat_role_under_ten_percent_fails(self):
        f = findings(metrics(self.base()))
        self.assertEqual(status(f, 'Missions', 'marksman:'), ['FAIL'])
        self.assertEqual(status(f, 'Missions', 'brawler:'), ['PASS'])
        self.assertIn('24 aborted after finding the lair', [t for s, st, t in f if 'marksman:' in t][0])

    def test_lair_check_ranged_flat_damage_is_fail_melee_pass(self):
        rows = self.base()
        rows += [row('mission_take', 900, bot=2, role='marksman', lvl=2, mlvl=3, reward=1, planet='tatooine', x=0, y=0)]
        rows += [lair_check(2, 960 + 60 * i, True, 0) for i in range(3)]
        rows += [row('mission_take', 900, bot=1, role='brawler', lvl=2, mlvl=3, reward=1, planet='tatooine', x=0, y=0)]
        rows += [lair_check(1, 960 + 60 * i, False, 100 * i) for i in range(3)]
        m = metrics(rows)
        self.assertEqual((m['lair_check']['ranged']['judged_attempts'], m['lair_check']['ranged']['damage_never_rose']), (1, 1))
        self.assertEqual(m['lair_check']['melee']['damage_never_rose'], 0)
        f = findings(m)
        self.assertEqual(status(f, 'Mission lairs', 'ranged:'), ['FAIL'])
        self.assertIn('shots fire and do no damage', [t for s, st, t in f if t.startswith('ranged:')][0])
        self.assertEqual(status(f, 'Mission lairs', 'melee:'), ['PASS'])

    def test_lair_check_names_the_failing_check(self):
        rows = self.base() + [lair_check(2, 960 + 60 * i, True, 0, los=False) for i in range(2)]
        text = [t for s, st, t in findings(metrics(rows)) if t.startswith('ranged:')][0]
        self.assertIn('line of sight false 100%', text)
        self.assertIn('Most failing check: line of sight', text)

    def test_no_lair_check_rows_is_watch(self):
        self.assertEqual(status(findings(metrics(self.base())), 'Mission lairs'), ['WATCH'])

    def test_killers_eight_above_fail_and_listed(self):
        rows = self.base() + [row('death', 700 + i, bot=1, killer='womp_rat', klvl=12, lvl=2, planet='tatooine', x=0, y=0) for i in range(3)]
        rows += [row('death', 710, bot=2, killer='kreetle', klvl=3, lvl=2, planet='tatooine', x=0, y=0)]
        f = findings(metrics(rows))
        leak = [(st, t) for s, st, t in f if t.startswith('Killers 8')][0]
        self.assertEqual(leak[0], 'FAIL')
        self.assertIn('womp_rat (level 12, tatooine) 3', leak[1])

    def test_travel_attempted_vs_done(self):
        f = findings(metrics(self.base()))
        self.assertEqual(status(f, 'Travel'), ['WATCH'])
        rows = self.base() + [row('travel', 100, bot=1, planet='tatooine', to_planet='naboo', reason='level'),
                              row('travel', 110, bot=2, planet='tatooine', to_planet='naboo', reason='level'),
                              row('snap', 120, bot=1, role='brawler', travels=1, planet='naboo', x=0, y=0)]
        m = metrics(rows)
        self.assertEqual((m['travel']['attempted'], m['travel']['done']), (2, 1))
        self.assertEqual(status(findings(m), 'Travel'), ['FAIL'])

    def test_training_refusals_count_bots(self):
        rows = self.base() + [row('broke', 50, bot=1, skill='a', cost=250, credits=200), row('broke', 51, bot=1, skill='a', cost=250, credits=200)]
        m = metrics(rows)
        self.assertEqual((m['training']['bots_refused'], m['training']['pairs'], m['training']['rows']), (1, 1, 2))
        self.assertEqual(status(findings(m), 'Training'), ['WATCH'])

    def test_ticks_fail_on_stall(self):
        rows = self.base() + [row('server', 900, online=3, tick_ms_avg=50, tick_ms_max=2100, skipped=40, rss_mb=120)]
        self.assertEqual(status(findings(metrics(rows)), 'Server ticks'), ['FAIL'])
        self.assertEqual(status(findings(metrics(self.base())), 'Server ticks'), ['PASS'])

    def test_core3_log_new_errors_and_leg_counters(self):
        rows = self.base()
        start, end = 0, 900 * 1000
        lines = [f'Fri Oct 16 2026 [{start + 1000:013d} msec] (1 s) Thread 2 - [Lua] INFO - file:a.lua ERROR cannot open a.lua\n',
                 f'Fri Oct 16 2026 [{start + 300000:013d} msec] (1 s) Thread 2 - [Lua] INFO - file:a.lua ERROR cannot open a.lua\n',
                 f'Fri Oct 16 2026 [{start + 300001:013d} msec] (1 s) Thread 3 - [Zone] ERROR - object 12345 has no zone\n',
                 f'Fri Oct 16 2026 [{start + 400000:013d} msec] (1 s) Thread 4 - [BotPop] INFO - mode all, online 3, failed 0, '
                 'no path 2, routes 100 (1 deferred, 3 none), legs stopped: no start 1, no end 0, no path 6, partial 1, unloaded mesh 0, snapped 4\n',
                 f'Fri Oct 16 2026 [{end + 500000:013d} msec] (1 s) Thread 3 - [Zone] ERROR - after the run\n']
        with tempfile.TemporaryDirectory() as d:
            log = os.path.join(d, 'core3.log')
            with open(log, 'w') as f:
                f.writelines(lines)
            # the spawn rows are at t=0, so the first error line is inside the run; move the run start later
            for r in rows:
                r['t'] += 200000
            m = metrics(rows, log)
        c3 = m['core3']
        self.assertEqual((c3['error_lines'], c3['signatures'], c3['new_signatures']), (2, 2, 1))
        self.assertEqual(c3['stats']['routes'], 100)
        self.assertEqual(sum(c3['stats'][k] for k in ('no start', 'no end', 'no path', 'partial', 'unloaded mesh')), 8)
        f = findings(m)
        self.assertEqual(status(f, 'Routes'), ['FAIL'])
        self.assertEqual(status(f, 'Server errors'), ['WATCH'])

    def test_old_stats_line_without_route_counts(self):
        rows = [dict(r, t=r['t'] + 200000) for r in self.base()]
        line = ('Fri Oct 16 2026 [0000000400000 msec] (1 s) Thread 3 - [BotPop] INFO - mode all, online 1700, steps 2319.57 ms per second '
                'across workers, slowest chunk 272.92 ms, real players 2, spawned 1700, logged out 0, failed 0, no path 3\n')
        with tempfile.TemporaryDirectory() as d:
            log = os.path.join(d, 'core3.log')
            with open(log, 'w') as f:
                f.write(line)
            m = metrics(rows, log)
        self.assertEqual((m['core3']['stats_lines'], m['core3']['stats_lines_with_routes'], m['core3']['steps_ms_per_s_median']), (1, 0, 2319.6))
        f = findings(m)
        self.assertIn('this build logs no route counts', [t for s, st, t in f if s == 'Routes'][0])
        self.assertIn('Bot steps 2319.6 ms', [t for s, st, t in f if s == 'Server ticks'][0])

    def test_signature_groups_numbers_and_addresses(self):
        a = signature('x [1 msec] (2 s) Thread 2 - [ZoneClientSession 192.168.1.210:48538] ERROR - 192.168.1.210:48538: StreamI 0x1f')
        b = signature('x [9 msec] (3 s) Thread 5 - [ZoneClientSession 10.0.0.1:1] ERROR - 10.0.0.1:1: StreamI 0x2e')
        self.assertEqual(a, b)

    def test_main_writes_files_and_compares_with_previous(self):
        with tempfile.TemporaryDirectory() as d:
            log = os.path.join(d, 'a.jsonl')
            with open(log, 'w') as f:
                f.writelines(json.dumps(r) + '\n' for r in self.base())
            findings_main([log, '--name', 'run1', '--out-dir', d])
            later = [dict(r, t=r['t'] + 10 ** 7) for r in self.base()]
            log2 = os.path.join(d, 'b.jsonl')
            with open(log2, 'w') as f:
                f.writelines(json.dumps(r) + '\n' for r in later)
            findings_main([log2, '--name', 'run2', '--out-dir', d])
            text = read_text(os.path.join(d, 'findings-run2.md'))
            self.assertIn('Compared with: run1', text)
            self.assertIn('(run1: 4%)', text)
            self.assertIn('**FAIL**', text.replace('## FAIL', '**FAIL**'))
            self.assertTrue(os.path.exists(os.path.join(d, 'findings-run2.json')))
            self.assertRegex(text, r'\d{1,2}:\d\d [AP]M')


class CensusTest(unittest.TestCase):
    def log(self, d):
        rows = [row('snap', 1, bot=1, role='explorer', planet='ossus', x=10, y=10),
                row('seen', 2, bot=1, kind='creature', name='kwi', lvl=6, planet='ossus', x=1500, y=-2500, z=3),
                row('seen', 3, bot=2, kind='creature', name='kwi', lvl=6, planet='ossus', x=1510, y=-2510, z=3),  # same 256 m square
                row('seen', 4, bot=1, kind='creature', name='kwi', lvl=9, planet='ossus', x=4000, y=4000, z=3),
                row('seen', 5, bot=1, kind='static', name='unknown_object', planet='ossus', x=100, y=200, z=7),
                row('seen', 6, bot=1, kind='lair', name='kwi_lair', lvl=8, planet='ossus', x=100, y=200, z=7),
                row('snap', 7, bot=5, role='brawler', planet='tatooine', x=3500, y=-4700),
                row('kill', 8, bot=5, target='womp_rat', tlvl=4, planet='tatooine', x=3500, y=-4700),
                row('death', 9, bot=5, killer='womp_rat', klvl=10, planet='tatooine', x=3600, y=-4700),
                row('lair', 10, bot=5, lair='tatooine_womprat_lair', planet='tatooine', x=3700, y=-4700),
                row('snap', 11, bot=6, role='medic', planet='naboo', x=0, y=0)]
        path = os.path.join(d, 'log.jsonl')
        with open(path, 'w') as f:
            f.writelines(json.dumps(r) + '\n' for r in rows)
        return path

    def test_square_clamps_to_planet(self):
        self.assertEqual(square(8191.5, -8192), (7, -8))
        self.assertEqual(square(3500, -4700), (3, -5))

    def test_planets_with_explorers_or_hunters_only(self):
        with tempfile.TemporaryDirectory() as d:
            out = os.path.join(d, 'out')
            census_main([self.log(d), '--name', 'runX', '--out', out])
            self.assertEqual(sorted(os.listdir(out)), ['README.md', 'ossus.csv', 'ossus.md', 'tatooine.csv', 'tatooine.md'])
            ossus = read_text(os.path.join(out, 'ossus.md'))
            self.assertIn('| kwi | 6-9 |', ossus)
            self.assertIn('Static objects with no name', ossus)
            tat = read_text(os.path.join(out, 'tatooine.md'))
            self.assertIn('| womp_rat | 4-10 | 1 | 1 |', tat)
            self.assertIn('botpop explore 50 tatooine', tat)
            self.assertIn('tatooine_womprat_lair', tat)
            readme = read_text(os.path.join(out, 'README.md'))
            self.assertIn('No explorers on tatooine', readme)
            self.assertIn('botpop explore N <planet>', readme)
            with open(os.path.join(out, 'ossus.csv'), encoding='utf-8') as f:
                kwi = [r for r in csv.DictReader(f) if r['template'] == 'kwi']
            self.assertEqual(sorted((r['square_x_km'], r['square_y_km'], r['events']) for r in kwi), [('1', '-3', '1'), ('4', '4', '1')])

    def test_sightings_deduplicated_per_256m_square(self):
        with tempfile.TemporaryDirectory() as d:
            pl = read(self.log(d))['ossus']
            self.assertEqual(sum(pl.things[('creature', 'kwi')].sources.values()), 2)
            self.assertIn(('unnamed', 'unknown_object'), pl.things)


if __name__ == '__main__':
    unittest.main()
