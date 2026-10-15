"""Tests for the fleet dashboard's data shaping in live_map.py (Claude, 15 Oct 2026). Run: python test_live_map.py"""
import struct
import unittest
import zlib

import live_map as m

AREAS = [{'zone': 'tatooine', 'name': 'Mos Eisley', 'box': [3200, -5100, 3900, -4500]}]


class Labels(unittest.TestCase):
    def test_species_and_skills(self):
        self.assertEqual(m.species_label('twilek_female'), "Twi'lek female")
        self.assertEqual(m.species_label('moncal_male'), 'Mon Calamari male')
        self.assertEqual(m.skill_label('combat_rifleman_novice'), 'Rifleman (novice)')
        self.assertEqual(m.skill_label('outdoors_squadleader_master'), 'Squad Leader (master)')
        self.assertEqual(m.skill_label('combat_marksman'), 'Marksman')

    def test_roles_most_telling_first(self):
        self.assertEqual(m.roles_for('combat_marksman', ['outdoors_squadleader_master', 'science_medic_novice']),
                         ['leader', 'ranged', 'healer'])
        self.assertEqual(m.roles_for('combat_brawler', ['combat_polearm_master', 'science_medic_master']),
                         ['tank', 'melee', 'healer'])
        self.assertEqual(m.roles_for('crafting_artisan'), ['crafter'])

    def test_state(self):
        self.assertEqual(m.state_of(False, 'walking to 1, 2'), 'offline')
        self.assertEqual(m.state_of(True, 'walking to 1, 2', 'incapacitated'), 'down')
        self.assertEqual(m.state_of(True, 'stuck walking to 1, 2: no path'), 'stuck')
        self.assertEqual(m.state_of(True, 'fighting sevorrt'), 'fighting')
        self.assertEqual(m.state_of(True, 'walking to 1, 2'), 'moving')
        self.assertEqual(m.state_of(True, 'waiting for Benny to log in'), 'waiting')
        self.assertEqual(m.state_of(True, '/invite on Oren'), 'busy')
        self.assertEqual(m.state_of(True, ''), 'idle')

    def test_area(self):
        self.assertEqual(m.area_of('tatooine', 3528, -4804, AREAS), 'Mos Eisley')
        self.assertEqual(m.area_of('naboo', 3528, -4804, AREAS), 'sector F7')    # same spot, other planet
        self.assertEqual(m.area_of('tatooine', -8192, 8192, AREAS), 'sector A1')
        self.assertEqual(m.area_of('tatooine', 9000, -9000, AREAS), 'sector H8')  # clamped to the edge


class Reports(unittest.TestCase):
    REPORT = {'group': 'Forn', 'scenario': 'forn-escort.py', 'state': 'finished', 'events': {
        'Brask': [{'event': 'command_failed', 'command': 'attack', 'reason': 'wrong locomotion', 't': 10.0},
                  {'event': 'command_failed', 'command': 'attack', 'reason': 'wrong locomotion', 't': 20.0},
                  {'event': 'posture', 'name': 'me', 'posture': 'incapacitated', 't': 30.0},
                  {'event': 'posture', 'name': 'Ressa Vay', 'posture': 'dead', 't': 31.0},   # someone else's fall
                  {'event': 'system', 'text': '@base_player:prose_grant_xp', 't': 40.0}]}}

    def test_digest(self):
        d = m.report_digest(self.REPORT, started=1000.0)
        b = d['bots']['Brask']
        self.assertEqual(b['refused'], [[1010, 'attack', 'wrong locomotion'], [1020, 'attack', 'wrong locomotion']])
        self.assertEqual(b['down'], [[1030, 'incapacitated']])
        self.assertEqual((b['xp'], b['span']), (1, 40.0))

    def test_issues_fold_repeats_and_drop_old(self):
        m.roster['Brask'] = 'Forn'
        reports = {'Forn': m.report_digest(self.REPORT, started=1000.0)}
        bots = [{'name': 'Dask', 'group': 'Forn', 'online': True, 'doing': 'stuck walking to 5, 5: no path', 'since': 1100},
                {'name': 'Kor', 'group': 'Cresh', 'online': False, 'doing': 'stuck x'}]          # offline: not an issue
        play = m.play_digest([{'kind': 'combat', 'by_crew': True, 'what': '@cbt_spam:out_of_range',
                               'attacker_name': 'Brask Tolen', 't': 1090}])
        rows = m.issues(bots, reports, play, now=1200)
        kinds = sorted((r['kind'], r['bot'], r['count']) for r in rows)
        self.assertEqual(kinds, [('down', 'Brask', 1), ('refused', 'Brask', 1), ('refused', 'Brask', 2), ('stuck', 'Dask', 1)])
        self.assertEqual(rows[0]['kind'], 'stuck')                          # newest first
        self.assertEqual(m.issues(bots[1:], reports, play, now=1000 + 2 * 86400), [])

    def test_play(self):
        d = m.play_digest([{'kind': 'order', 'order': 'heal', 'heard_by': 'Mirren', 't': 5.0},
                           {'kind': 'player', 'health': 0.4, 't': 6.0}, {'kind': 'player', 'health': 0.9, 't': 7.0}])
        self.assertEqual((d['orders'], d['player_low'], d['last']), ([[5, 'heal', 'Mirren']], 0.4, 7))


class ServerLog(unittest.TestCase):
    def test_errors_fold_and_hide_addresses(self):
        line = ('Thu Oct 15 12:52:28 2026 [1792093948858 msec] (1044 s) Thread 32 - [ZoneClientSession 192.168.1.210:{}] '
                'ERROR - handleNetStatusRequest 192.168.1.210:{}: StreamIndexOutOfBoundsException at 8')
        lines = [line.format(p, p) for p in (45378, 47213)] + [
            'Thu Oct 15 12:53:00 2026 [1792093980000 msec] (1070 s) Thread 3 - [PlayerManager] ERROR - missing account 97',
            'Thu Oct 15 12:53:01 2026 [1792093981000 msec] (1076 s) Thread 3 - [PlayerManager] ERROR - missing account 98',
            'Thu Oct 15 12:53:02 2026 [1792093982000 msec] (1076 s) Thread 3 - [Zone] INFO - all fine']
        uptime, rows = m.error_digest(lines)
        self.assertEqual(uptime, 1076)
        self.assertEqual([(r['where'], r['count']) for r in rows], [('PlayerManager', 2), ('ZoneClientSession', 2)])
        self.assertEqual(rows[0]['msg'], 'missing account 98')             # the newest wording of a folded kind
        self.assertNotIn('192.168', rows[1]['msg'] + rows[1]['where'])


class Images(unittest.TestCase):
    @staticmethod
    def dds(w, h, fourcc, body, bits=0):
        head = bytearray(128)
        head[:4] = b'DDS '
        struct.pack_into('<II', head, 12, h, w)
        head[84:88] = fourcc
        struct.pack_into('<I', head, 88, bits)
        return bytes(head) + body

    def test_dxt1(self):
        # colour 0 pure red, colour 1 pure blue; first pixel index 0, second index 1, third index 2 (2/3 red), rest 3
        idx = 0 | 1 << 2 | 2 << 4 | sum(3 << 2 * i for i in range(3, 16))
        w, h, rgb = m.dds_rgb(self.dds(4, 4, b'DXT1', struct.pack('<HHI', 0xF800, 0x001F, idx)))
        self.assertEqual((w, h, len(rgb)), (4, 4, 48))
        self.assertEqual((rgb[0:3], rgb[3:6], rgb[6:9]), (b'\xff\x00\x00', b'\x00\x00\xff', b'\xaa\x00\x55'))

    def test_bgr(self):
        w, h, rgb = m.dds_rgb(self.dds(1, 1, b'\0\0\0\0', b'\x01\x02\x03', bits=24))
        self.assertEqual(rgb, b'\x03\x02\x01')
        self.assertIsNone(m.dds_rgb(b'not a dds'))

    def test_png(self):
        body = m.png(2, 1, b'\x01\x02\x03\x04\x05\x06')
        self.assertTrue(body.startswith(b'\x89PNG\r\n\x1a\n'))
        idat = body.index(b'IDAT')
        size = struct.unpack('>I', body[idat - 4:idat])[0]
        self.assertEqual(zlib.decompress(body[idat + 4:idat + 4 + size]), b'\x00\x01\x02\x03\x04\x05\x06')


if __name__ == '__main__':
    unittest.main()
