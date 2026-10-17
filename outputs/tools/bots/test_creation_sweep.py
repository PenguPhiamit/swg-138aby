"""Offline tests for scenarios/creation-sweep.py: synthetic creation tables, client logs and status replies; no
galaxy, database or credentials."""
import importlib.util
import os
import random
import re
import unittest
from pathlib import Path
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('creation_sweep', Path(__file__).parent / 'scenarios/creation-sweep.py')
cs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cs)
st = cs.st

# The stock rows (patch_11_00 racial_mods / attribute_limits, patch_03 profession_mods) plus our Chiss and Hutt.
RACIAL = {'bothan': [0, 0, 0, 300, 300, 100, 100, 100, 0], 'human': [100] * 9,
          'moncal': [0, 0, 0, 0, 0, 150, 300, 300, 150], 'rodian': [0, 0, 0, 200, 200, 450, 0, 0, 50],
          'trandoshan': [250, 300, 400, 0, 0, 0, 0, 0, 100], 'twilek': [0, 0, 250, 250, 300, 0, 100, 0, 0],
          'wookiee': [350, 350, 150, 200, 100, 100, 100, 150, 100], 'zabrak': [200, 0, 0, 300, 0, 0, 0, 0, 400],
          'sullustan': [150, 0, 0, 250, 50, 50, 200, 100, 100], 'ithorian': [400, 100, 100, 100, 0, 0, 200, 0, 0],
          'chiss': [100] * 9, 'hutt': list(cs.HUTT_RACIAL)}
PROFESSION_MODS = {'crafting_artisan': [600, 300, 300, 800, 400, 300, 900, 400, 500],
                   'combat_brawler': [1000, 500, 400, 800, 350, 350, 500, 300, 300],
                   'social_entertainer': [500, 300, 300, 1000, 400, 400, 800, 400, 400],
                   'combat_marksman': [1000, 450, 300, 800, 450, 300, 600, 300, 300],
                   'science_medic': [600, 300, 300, 700, 300, 300, 1000, 500, 500],
                   'outdoors_scout': [800, 300, 350, 800, 400, 400, 700, 350, 400]}
HUMAN_LIMITS = [400, 1100] * 9 + [5400]
IMPORTED_HUTT = ('Hutts are a species of large gastropods.\r\n\r\nThey rule much of the Outer Rim.\r\n\r\n'
                 'ATTRIBUTES\n\n')  # F3's failing case: imported multi-paragraph lore with contradictory stats


def desc(prose, values):
    return prose + '\r\n\r\nATTRIBUTES\n\n' + '\n'.join(
        '\\>024%s: \\>128+%d\\>000' % (name.capitalize(), value) for name, value in zip(cs.ATTRIBUTES, values))


def stf(items):
    table = st.stf_new()
    for key, text in items.items():
        st.stf_add(table, key, text)
    return table


def tables(racial=None, limits=None, texts=None, skill=cs.HUTT_SKILL, drop_female=()):
    racial = dict(RACIAL, **(racial or {}))
    pairs = [(s, f'{s}_male', '' if s in drop_female else f'{s}_female') for s in racial]
    texts = dict({f'desc_{s}': desc(cs.HUTT_TEXT_START + ' and beyond.' if s == 'hutt' else f'The {s}.', racial[s])
                  for s in racial}, **(texts or {}))
    found = {
        'racial': {'rows': [[m, f] + racial[s] for s, m, f in pairs]},
        'limits': {'rows': [[m, f] + ((limits or {}).get(s) or (cs.HUTT_LIMITS if s == 'hutt' else HUMAN_LIMITS))
                            for s, m, f in pairs]},
        'professions': {'rows': [[p] + v for p, v in PROFESSION_MODS.items()]},
        'species_text': stf(texts), 'skl_n': stf({'species_hutt': skill[0]}), 'skl_d': stf({'species_hutt': skill[1]}),
    }
    return cs.tables_from(found, {'racial': 'local_planets.tre'})


def checks(t):
    return {label: (ok, detail) for label, ok, detail in cs.data_checks(t)}


def valid_name(name, species):
    """NameManager::validateName's length and character rules for the species files on dev (name_manager.lua)."""
    first, _, last = name.partition(' ')
    low = 4 if species == 'hutt' else 3
    if not low <= len(first) <= 15 or not first.isalpha():
        return False
    if species == 'wookiee':
        return last == ''
    return last == '' or (low <= len(last) <= (15 if species == 'hutt' else 20) and last.isalpha())


class Data(unittest.TestCase):
    def test_good_tables_pass_every_check(self):
        results = checks(tables())
        self.assertEqual(len(results), 7)
        self.assertTrue(all(ok for ok, _ in results.values()), results)

    def test_f2_wookiee_row_and_human_limits_fail(self):
        results = checks(tables(racial={'hutt': RACIAL['wookiee']}, limits={'hutt': HUMAN_LIMITS}))
        self.assertFalse(results['data: Hutt racial row is S7 5.2 (C54 F2)'][0])
        self.assertFalse(results['data: Hutt attribute limits follow S7 (C54 F2)'][0])

    def test_hutt_limits_are_the_stock_derivation(self):
        self.assertEqual(cs.HUTT_LIMITS, [400, 1100, 450, 650, 600, 700, 300, 1000, 300, 450, 350, 450, 300, 1000,
                                          300, 500, 600, 800, 5400])

    def test_f3_imported_text_fails(self):
        lore = desc(IMPORTED_HUTT.split('\r\n\r\nATTRIBUTES')[0], [0, 0, 250, 250, 300, 0, 100, 0, 0])
        results = checks(tables(texts={'desc_hutt': lore}))
        ok, detail = results['data: Hutt creation text is S7 5.1 with the approved attributes (C54 F3)']
        self.assertFalse(ok)
        self.assertIn('not the S7 prose', detail)
        self.assertIn('more than one paragraph', detail)
        self.assertFalse(results["data: our species' creation texts show their racial rows (C54 F3)"][0])
        self.assertTrue(results['data: stock creation texts show their racial rows (SOE text)'][0])

    def test_stock_text_mismatch_is_reported_apart(self):
        # The stock Sullustan text shows the Zabrak's numbers (patch_12_00, found 17 Oct).
        results = checks(tables(texts={'desc_sullustan': desc('Sullustans.', RACIAL['zabrak'])}))
        ok, detail = results['data: stock creation texts show their racial rows (SOE text)']
        self.assertFalse(ok)
        self.assertIn('sullustan shows [200, 0, 0, 300', detail)
        self.assertTrue(results["data: our species' creation texts show their racial rows (C54 F3)"][0])

    def test_missing_species_and_gender(self):
        t = tables(drop_female=('wookiee',))
        t['pairs'] = [p for p in t['pairs'] if p[0] != 'chiss']
        ok, detail = checks(t)['data: the creation tables list the 12 species']
        self.assertFalse(ok)
        self.assertIn("missing ['chiss']", detail)
        self.assertIn("['wookiee female']", detail)

    def test_skill_labels(self):
        self.assertFalse(checks(tables(skill=('Species Hutt', 'Hutt')))['data: Hutt skill labels (C54 F3)'][0])

    def test_attribute_block(self):
        self.assertEqual(cs.attribute_block(desc('x', RACIAL['wookiee'])), RACIAL['wookiee'])
        self.assertIsNone(cs.attribute_block('No block here.'))
        self.assertIsNone(cs.attribute_block('ATTRIBUTES\n\n\\>024Health: \\>128+100\\>000'))  # eight missing

    def test_expected_attributes(self):
        t = tables()
        # Fresh start, 16 Oct: a human Entertainer had 600/1100/900 and the Hutt Artisan 700/800/900 (H/A/M).
        human = cs.expected_attributes(t, 'human_female', 'social_entertainer')
        self.assertEqual([human[0], human[3], human[6]], [600, 1100, 900])
        self.assertEqual(cs.expected_attributes(t, 'hutt_male', 'crafting_artisan'),
                         [700, 450, 600, 800, 400, 350, 900, 400, 800])
        self.assertIsNone(cs.expected_attributes(t, 'nautolan_male', 'crafting_artisan'))
        self.assertIsNone(cs.expected_attributes(t, 'human_male', 'jedi'))


def creation_table(blocks):
    """A profession_defaults-shaped IFF: a skill form, then one PTMP block per player template."""
    iff = cs.iff
    ptmps = [iff.form('PTMP', iff.chunk('NAME', f'object/creature/player/shared_{who}.iff'.encode() + b'\0'),
                      *[iff.chunk('ITEM', b'\0\0\0\0' + item.encode() + b'\0') for item in items])
             for who, items in blocks.items()]
    return iff.build([iff.form('PRFI', iff.form('0000', iff.form('SKLS', iff.chunk('SKIL', b'x\0')), *ptmps))])


class StartingItems(unittest.TestCase):
    def test_items_and_missing_templates(self):
        import tempfile
        data = creation_table({'ithorian_male': ['object/tangible/wearables/ithorian/shared_ith_jacket_s16.iff',
                                                 'object/tangible/wearables/ithorian/shared_ith_pants_s01.iff'],
                               'hutt_male': []})
        self.assertEqual(cs.starting_items(data), [
            ('ithorian_male', 'object/tangible/wearables/ithorian/ith_jacket_s16.iff'),
            ('ithorian_male', 'object/tangible/wearables/ithorian/ith_pants_s01.iff')])
        with tempfile.TemporaryDirectory() as scripts:
            lua = Path(scripts, 'object/tangible/wearables/ithorian/ith_pants_s01.lua')
            lua.parent.mkdir(parents=True)
            lua.write_text('-- template')
            label, ok, detail = cs.starting_item_check(read=lambda rel: (data, 'x'), scripts=Path(scripts))
        self.assertFalse(ok)
        self.assertEqual(detail.split('; ')[0],
                         'default_pc_equipment ithorian_male: object/tangible/wearables/ithorian/ith_jacket_s16.iff')
        self.assertIn('combat_brawler ithorian_male', detail)
        self.assertEqual(cs.starting_item_check(scripts=Path('/no/such/folder'))[1], None)


class Plan(unittest.TestCase):
    def plan(self, taken=(), accounts=24, seed='s'):
        return cs.plan_characters(tables()['pairs'], [f'a{i}' for i in range(accounts)], set(taken), random.Random(seed))

    def test_24_characters_professions_accounts_names(self):
        chars, unplaced = self.plan()
        self.assertEqual(len(chars), 24)
        self.assertEqual(unplaced, [])
        self.assertEqual({(c['species'], c['gender']) for c in chars},
                         {(s, g) for s in cs.SPECIES for g in ('male', 'female')})
        for profession in cs.PROFESSIONS:
            self.assertEqual(sum(c['profession'] == profession for c in chars), 4)
        self.assertEqual(len({c['account'] for c in chars}), 24)
        firsts = [c['name'].split()[0].lower() for c in chars]
        self.assertEqual(len(set(firsts)), 24)
        for c in chars:
            self.assertTrue(valid_name(c['name'], c['species']), c)
        same_species = {}
        for c in chars:
            same_species.setdefault(c['species'], set()).add(c['profession'])
        self.assertTrue(all(len(v) == 2 for v in same_species.values()))

    def test_name_cases_land_where_they_fit(self):
        chars, _ = self.plan()
        cases = {c['case']: c for c in chars if c['case']}
        self.assertEqual(len(cases), 1 + len(cs.TRAPS) + len(cs.CANON_SURNAMES) + 1)
        hutt = next(c for c in chars if c['case'] and 'kajidic' in c['case'])
        self.assertEqual(hutt['species'], 'hutt')
        self.assertIn(hutt['name'].split()[1], cs.HUTT_SURNAMES)
        for c in chars:
            if c['species'] == 'hutt' and c is not hutt:
                self.assertIsNone(c['case'])
            if c['case'] and c['case'].startswith('canon surname'):
                self.assertNotEqual(c['species'], 'wookiee')
                self.assertEqual(c['name'].split()[1], c['case'].split()[-1])
        for label, pool in cs.TRAPS:
            self.assertEqual(cases[label]['name'].split()[0], pool[0])

    def test_taken_names_are_skipped(self):
        chars, _ = self.plan(taken={'rebecca', 'declan', 'cecily', 'becca', 'rhecan', 'lando', 'leia'})
        trap = next(c for c in chars if c['case'] == '"ec" inside a name')
        first = trap['name'].split()[0]
        self.assertTrue(first.startswith('Rebecca') and len(first) > 7 and 'ec' in first.lower())
        self.assertEqual(next(c for c in chars if c['case'] == 'canon first name')['name'].split()[0], 'Carl')

    def test_no_canon_first_name_left(self):
        chars, unplaced = self.plan(taken={n.lower() for n in cs.CANON_FIRST})
        self.assertFalse(any(c['case'] == 'canon first name' for c in chars))
        self.assertEqual(unplaced, [])

    def test_too_few_accounts(self):
        with self.assertRaises(ValueError):
            self.plan(accounts=23)

    def test_made_word_avoids_taken_and_reserved(self):
        rng = random.Random(1)
        taken = set()
        for _ in range(300):
            word = cs.made_word(rng, taken)
            self.assertTrue(4 <= len(word) <= 12 and word.isalpha() and word[0].isupper())
            self.assertNotIn(word.lower(), taken | cs.RESERVED)
            taken.add(word.lower())

    def test_refusals(self):
        rng = random.Random(2)
        out = cs.plan_refusals([f'a{i}' for i in range(8)], {'zor'}, 'Kael', rng)
        self.assertEqual(len(out), len(cs.REFUSALS))
        by_label = {r['label']: r for r in out}
        self.assertEqual(by_label['a 3-letter Hutt name']['name'], 'Gub')
        self.assertTrue(by_label['a name in use']['name'].startswith('Kael '))
        self.assertTrue(by_label['Admin']['name'].startswith('Admin '))
        self.assertTrue(by_label['Bank as a surname']['name'].endswith(' Bank'))
        self.assertTrue(re.fullmatch(r'[A-Z][a-z]+9 [A-Z][a-z]+', by_label['digits']['name']))
        self.assertEqual(len(by_label['a Wookiee surname']['name'].split()), 2)
        self.assertEqual(len({r['account'] for r in out}), len(out))
        self.assertEqual(len(cs.plan_refusals([f'a{i}' for i in range(8)], set(), None, rng)), len(cs.REFUSALS) - 1)

    def test_choose_accounts(self):
        now = 1_000_000
        rows = [('a', '1', '1', str(now - 3600)), ('b', '2', '1', str(now - 4000)), ('c', '3', '14', '0'),
                ('d', '4', '1', f'{now - 9000}.000000'), ('e', '5', '1', '0')]
        self.assertEqual([r[0] for r in cs.choose_accounts(rows, now, 9, 15)], ['b', 'd', 'e'])
        self.assertEqual([r[0] for r in cs.choose_accounts(rows, now, 2, 15)], ['b', 'd'])
        self.assertEqual(cs.minutes_to_wait(rows, now), 6)
        self.assertEqual(cs.minutes_to_wait(rows[1:], now), 0)


# Lines as the dev core3client writes them (Documentation-support/fresh-start create logs, 16 Oct).
SUCCESS_LOG = ('(0 s) [CreateCharacter]   Skip Tutorial: true\n'
               '(0 s) [ZonePacketHandler] Character creation SUCCESS - OID: 281475002573227\n'
               '(0 s) [CreateCharacter] Character created successfully - OID: 281475002573227\n')
FAILED_LOG = ('(0 s) [ConnectToZone] Cleaning up login conn(0 s) [ZonePacketHandler] ERROR - Character creation FAILED\n'
              '(0 s) [ZonePacketHandler] ERROR -   Error code: name_declined_racially_inappropriate\n'
              '(0 s) [CoreClient] ERROR - createCharacter failed: Character creation failed: '
              'name_declined_racially_inappropriate\n')
HOUR_LOG = ('(0 s) [ZonePacketHandler] ERROR - Zone ERROR: Create Error - You are only permitted to create one '
            'character per hour. Repeat attempts prior to 1 hour elapsing will reset the timer.\n')


class Results(unittest.TestCase):
    def test_creation_result(self):
        self.assertEqual(cs.creation_result(SUCCESS_LOG), {'created': True, 'oid': 281475002573227})
        self.assertEqual(cs.creation_result(FAILED_LOG),
                         {'created': False, 'code': 'name_declined_racially_inappropriate'})
        hour = cs.creation_result(HOUR_LOG)
        self.assertEqual(hour['code'], 'error_message')
        self.assertTrue(hour['message'].startswith('Create Error: You are only permitted to create one character'))
        self.assertEqual(cs.creation_result('(0 s) [CoreClient] ERROR - Character creation timeout\n')['code'],
                         'no_reply')
        self.assertEqual(cs.creation_result('')['message'], 'no creation reply in the log')

    def row(self, **kw):
        t = tables()
        want = cs.expected_attributes(t, 'hutt_male', 'crafting_artisan')
        attrs = dict(zip(cs.ATTRIBUTES, want))
        row = {'species': 'hutt', 'template': 'hutt_male', 'profession': 'crafting_artisan', 'name': 'Renro Besadii',
               'created': True, 'oid': 5, 'login_s': 21.5, 'shown_name': 'Renro Besadii',
               'crc': cs.template_crc('object/creature/player/shared_hutt_male.iff'),
               'db_template': 'object/creature/player/hutt_male.iff',
               'status': {'me': {'attributes': dict(attrs), 'max_attributes': dict(attrs)}}}
        row.update(kw)
        return row, t

    def test_judge_pass(self):
        row, t = self.row()
        self.assertEqual(cs.judge(row, t), [])
        self.assertEqual(cs.hutt_s7_problems(row, t), [])

    def test_judge_finds_each_fault(self):
        row, t = self.row(crc=1, shown_name='Renro', db_template='object/creature/player/wookiee_male.iff')
        row['status']['me']['max_attributes']['constitution'] = 450
        row['status']['me']['attributes']['willpower'] = 10
        problems = cs.judge(row, t)
        self.assertTrue(any(p.startswith('object CRC 1') for p in problems))
        self.assertTrue(any(p.startswith('shown name') for p in problems))
        self.assertTrue(any('wookiee_male' in p for p in problems))
        self.assertIn('constitution max 450, expected 600', problems)
        self.assertIn('willpower 10 of 800', problems)
        self.assertEqual(cs.hutt_s7_problems(row, t), ['racial part [100, 150, 150, 0, 0, 50, 0, 0, 300], '
                                                       'S7 [100, 150, 300, 0, 0, 50, 0, 0, 300]'])

    def test_judge_not_created_or_no_login(self):
        row, t = self.row(created=False, code='error_message', message='Create Error: one per hour')
        self.assertEqual(cs.judge(row, t), ['not created: error_message Create Error: one per hour'])
        row, t = self.row(login_s=None, login_error='Scene timeout')
        self.assertEqual(cs.judge(row, t), ['created (oid 5) but no login: Scene timeout'])

    def test_old_body_without_attributes(self):
        row, t = self.row(status={'me': {'ham': {'health': 700}, 'max_ham': {'health': 700}}})
        self.assertIn('nine-attribute', cs.judge(row, t)[0])

    def test_console_findings(self):
        lines = ['x BaseClient::handleNetStatusRequest ERROR StreamIndexOutOfBoundsException at 8',
                 'x ERROR decreaseOnlineCharCount missing account 7 in onlineZoneClientMap',
                 'x [PlayerCreationManager] ERROR - Failed to load starting items.',
                 'x [ZoneServer] ERROR - object 281475002573227 has no zone',
                 'x [Zone] ERROR - Renro is in a wall',
                 'x [AiAgent] ERROR - path failed',
                 'x INFO nothing']
        ours, noise, other = cs.console_findings(lines, ['Renro'], [281475002573227])
        self.assertEqual(len(ours), 3)
        self.assertEqual((noise, other), (2, 1))

    def test_console_error_after_our_login_on_the_same_thread(self):
        # 17 Oct, 6:17:55 AM: the Ithorian Brawler's starting jacket has no server template.
        t = 'Sat Oct 17 06:17:55 2026 [1792243075091 msec] (1110 s) Thread %s - '
        lines = [t % 27 + '[ZoneClientSession 192.168.1.210:46489] INFO - Player 281475004100675 logged in.',
                 t % 32 + '[ZoneClientSession 192.168.1.210:47983] INFO - Deleted Session',
                 t % 27 + '[ObjectManager] ERROR - Failed to create object with unknown CRC: 0xf940567d',
                 t % 27 + '[ObjectManager] ERROR - could not create object CRC = 0xf940567d template:',
                 t % 32 + '[AiAgent] ERROR - path failed',
                 t % 27 + '[ZoneClientSession 192.168.1.210:46489] INFO - CheckupTime = 2000',
                 t % 27 + '[AiAgent] ERROR - path failed']
        ours, noise, other = cs.console_findings(lines, ['Drais'], [281475004100675])
        self.assertEqual(len(ours), 2)
        self.assertIn('0xf940567d', ours[0])
        self.assertEqual((noise, other), (0, 2))

    def test_no_database_row(self):
        row, t = self.row(db_template=None)
        self.assertIn('no database row (characters or characters_dirty)', cs.judge(row, t))

    def test_cleanup_statements_are_the_login_servers(self):
        self.assertEqual(cs.cleanup_statements(281475002573227, 11), [
            'INSERT INTO deleted_characters SELECT *, 0 as db_deleted FROM characters WHERE character_oid = '
            '281475002573227 AND account_id = 11 AND galaxy_id = 2;',
            'DELETE FROM characters WHERE character_oid = 281475002573227 AND account_id = 11 AND galaxy_id = 2;'])
        with self.assertRaises(ValueError):
            cs.cleanup_statements('1 OR 1=1', 11)


class Cleanup(unittest.TestCase):
    """delete_characters against a fake database: rows wait in characters_dirty until a save moves them."""

    def setUp(self):
        self.tables = {'characters_dirty': {1: (11, 'Rebecca', 'x'), 2: (12, 'Victor', 'x'), 3: (13, 'Other', 'x')},
                       'characters': {}, 'deleted_characters': {}}
        self.statements, self.polls = [], 0

    def rows(self, oids):
        self.polls += 1
        if self.polls == 3:  # the zone's save, between the second and third poll
            self.tables['characters'].update(self.tables['characters_dirty'])
            self.tables['characters_dirty'].clear()
        out = {}
        for table in ('characters_dirty', 'characters'):
            for oid in oids:
                if oid in self.tables[table]:
                    out[oid] = self.tables[table][oid] + (table,)
        return out

    def run_sql(self, statement):
        self.statements.append(statement)
        oid = int(re.search(r'character_oid = (\d+)', statement).group(1))
        if statement.startswith('INSERT'):
            self.tables['deleted_characters'][oid] = self.tables['characters'][oid]
        elif statement.startswith('DELETE'):
            del self.tables['characters'][oid]
        elif 'FROM deleted_characters' in statement:
            return f"{int(oid in self.tables['deleted_characters'])}\n"
        elif 'FROM characters' in statement:
            return f"{int(oid in self.tables['characters'])}\n"
        return ''

    def created(self):
        return [{'oid': 1, 'account': 'grek1', 'name': 'Rebecca Quel'}, {'oid': 2, 'account': 'grek2', 'name': 'Victor A'},
                {'oid': 3, 'account': 'grek3', 'name': 'Wrong Name'}, {'oid': 4, 'account': 'grek4', 'name': 'Gone'}]

    def test_waits_for_the_save_then_deletes_only_matching_rows(self):
        ids = {'grek1': 11, 'grek2': 12, 'grek3': 13, 'grek4': 14}
        sleeps = []
        states = dict(cs.delete_characters(self.created(), ids, wait_s=600, rows=self.rows, run=self.run_sql,
                                           sleep=sleeps.append))
        self.assertEqual(states[1], 'deleted')
        self.assertEqual(states[2], 'deleted')
        self.assertTrue(states[3].startswith('skipped'))  # first name differs: never touched
        self.assertTrue(states[4].startswith('skipped'))  # no row anywhere
        self.assertEqual(sleeps, [15, 15])
        self.assertEqual(set(self.tables['deleted_characters']), {1, 2})
        self.assertEqual(set(self.tables['characters']), {3})
        self.assertFalse(any('character_oid = 3' in s for s in self.statements))

    def test_no_save_in_time(self):
        self.polls = -100  # the save never comes
        states = dict(cs.delete_characters(self.created()[:1], {'grek1': 11}, wait_s=0, rows=self.rows,
                                           run=self.run_sql, sleep=lambda s: None))
        self.assertEqual(states[1], 'still in characters_dirty after 0 s: no save ran')
        self.assertEqual(self.statements, [])


class FakeGroup:
    def __init__(self):
        self.checks, self.notes = [], []

    def check(self, label, ok, detail=''):
        self.checks.append((label, bool(ok), detail))
        return bool(ok)

    def note(self, text):
        self.notes.append(text)

    def checkpoint(self):
        pass


class Run(unittest.TestCase):
    def test_data_only(self):
        g = FakeGroup()
        with patch.object(cs, 'load_tables', return_value=tables()), \
                patch.dict(os.environ, {'CREATION_SWEEP_DATA_ONLY': '1'}), patch('builtins.print') as shown:
            cs.run(g)
        self.assertEqual(len(g.checks), 7 + sum(check()[1] is not None for check in (cs.archive_check,
                                                                                    cs.starting_item_check)))
        self.assertIn('data only: no character created', g.notes)
        self.assertIn('hutt_female', shown.call_args[0][0])

    def test_live_needs_root_and_galaxy(self):
        g = FakeGroup()
        with patch.object(cs, 'load_tables', return_value=tables()), patch.object(cs, 'is_root', return_value=False), \
                patch.object(cs, 'galaxy_running', return_value=False), patch.dict(os.environ, {}, clear=False):
            os.environ.pop('CREATION_SWEEP_DATA_ONLY', None)
            cs.run(g)
        self.assertTrue(g.notes[-1].startswith('BLOCKED: the live sweep runs standalone as root'))

    def test_unreadable_tables(self):
        g = FakeGroup()
        with patch.object(cs, 'load_tables', side_effect=LookupError('racial_mods.iff is in no archive')):
            cs.run(g)
        self.assertTrue(g.notes[0].startswith('ERROR: creation tables unreadable'))

    def test_options(self):
        with patch.dict(os.environ, {'CREATION_SWEEP_PARALLEL': '40', 'CREATION_SWEEP_ACCOUNTS': 'leth1,leth2',
                                     'CREATION_SWEEP_KEEP': '1'}):
            self.assertEqual(cs.options(), {'data_only': False, 'keep': True, 'parallel': 12,
                                            'accounts': ['leth1', 'leth2']})


if __name__ == '__main__':
    unittest.main()
