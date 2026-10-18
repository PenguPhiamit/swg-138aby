"""Offline tests for the 18 Oct chunk jobs in local_jobs.py: log-triage, board-trim and scenario-draft (Claude,
18 Oct 2026). Each runs the job's prepare step on small stand-in files and its report on made-up answers: no Ollama,
no network, nothing under /opt/swg. Runs on Windows or in WSL:

    python -I test_local_jobs.py
"""
import json
import sys
import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import local_jobs

LOG = """\
Thu Oct 15 23:31:16 2026 [1 msec] (14 s) Thread 2 - [Lua] INFO - file:old.lua ERROR cannot open old.lua
Thu Oct 15 23:40:00 2026 [1 msec] (600 s) Thread 2 - [ZoneServer Test Galaxy] ERROR - before the restart
Thu Oct 15 23:52:04 2026 [1 msec] (0 s) Thread 0 - [Core] DEBUG - initializing context
Thu Oct 15 23:52:05 2026 [1 msec] (1 s) Thread 2 - [SharedObjectTemplate prop_1_a] WARNING - could not open lua derv: object/x/base_1.iff
Thu Oct 15 23:52:05 2026 [1 msec] (1 s) Thread 2 - [SharedObjectTemplate prop_22_b] WARNING - could not open lua derv: object/x/base_1.iff
Thu Oct 15 23:52:06 2026 [1 msec] (2 s) Thread 2 - [Lua] INFO - file:scripts/a.lua ERROR cannot open scripts/a.lua
Thu Oct 15 23:52:06 2026 [1 msec] (2 s) Thread 2 - [Lua] INFO - loaded 12 files
Fri Oct 16 13:05:00 2026 [1 msec] (47000 s) Thread 32 - [ZoneClientSession 192.168.1.210:45450] ERROR - handleNetStatusRequest 192.168.1.210:45450: StreamIndexOutOfBoundsException at 8
Fri Oct 16 13:05:01 2026 [1 msec] (47001 s) Thread 32 - [ZoneClientSession 192.168.1.210:47998] ERROR - handleNetStatusRequest 192.168.1.210:47998: StreamIndexOutOfBoundsException at 8
Fri Oct 16 13:05:01 2026 [1 msec] (46990 s) Thread 7 - [ZoneClientSession 192.168.1.210:47998] ERROR - handleNetStatusRequest 192.168.1.210:47998: StreamIndexOutOfBoundsException at 8
Fri Oct 16 13:06:00 2026 [1 msec] (47060 s) Thread 5 - [CreatureObject] ERROR - skill points mismatch calculated: 250 found: 248
0 users connected (0 max, 0 total, 0 deleted)
terminate called after throwing an instance of 'ArrayIndexOutOfBoundsException'
"""


class Folder(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.dir.cleanup)
        self.root = Path(self.dir.name)

    def patch(self, target, name, value):
        patcher = mock.patch.object(target, name, value)
        patcher.start()
        self.addCleanup(patcher.stop)

    def answer(self, folder, items, chunk=0):
        """Write a results.jsonl as local_map.py would, answering one chunk of the prepared input."""
        chunks = [json.loads(line) for line in (folder / 'input.jsonl').read_text(encoding='utf-8').splitlines()]
        (folder / 'results.jsonl').write_text(json.dumps({'id': chunks[chunk]['id'], 'answer': {'items': items}}) + '\n',
                                              encoding='utf-8')

    def report(self, job, folder):
        local_jobs.report(job, folder)
        return (folder / 'report.md').read_text(encoding='utf-8')


class LogTriageTests(Folder):
    def setUp(self):
        super().setUp()
        self.log = self.root / 'core3.log'
        self.log.write_text(LOG, encoding='utf-8')
        self.patch(local_jobs, 'LOG_KNOWN', self.root / 'no-known-list.txt')

    def test_only_the_last_start_collapsed_by_pattern(self):
        folder = self.root / 'triage'
        self.assertEqual(local_jobs.prepare('log-triage', folder, str(self.log)), (5, 1))
        lines = json.loads((folder / 'lines.json').read_text(encoding='utf-8'))
        text = '\n'.join(lines.values())
        self.assertNotIn('before the restart', text)   # the run before the last start
        self.assertNotIn('old.lua', text)
        self.assertNotIn('loaded', text)                # an ordinary INFO line
        self.assertNotIn('users connected', text)       # a status line without the header
        self.assertNotIn('192.168', text)
        # the three net-status lines are one pattern, the jitter (46990 after 47001) is not a restart, biggest first
        self.assertEqual(lines['p1'], 'ERROR\t3x\t10/16 1:05 PM\t[ZoneClientSession] handleNetStatusRequest <ip>: '
                                      'StreamIndexOutOfBoundsException at #')
        self.assertIn('WARNING\t2x\t10/15 11:52 PM\t[SharedObjectTemplate] could not open lua derv: object/x/base_#.iff',
                      lines.values())
        self.assertIn('INFO\t1x\t10/15 11:52 PM\t[Lua] file:scripts/a.lua ERROR cannot open scripts/a.lua', lines.values())
        self.assertIn('ERROR\t1x\t10/16 1:06 PM\t[CreatureObject] skill points mismatch calculated: # found: #',
                      lines.values())
        self.assertTrue(any(v.startswith('RAW\t1x\t') and 'terminate called' in v for v in lines.values()))
        meta = json.loads((folder / 'log-meta.json').read_text(encoding='utf-8'))
        self.assertEqual((meta['since'], meta['matched'], meta['patterns']), ('10/15 11:52 PM', 8, 5))
        self.assertIn('crash-risk', (folder / 'instruction.txt').read_text(encoding='utf-8'))

    def test_the_log_comes_from_the_argument_the_topic_or_the_test_galaxy(self):
        research = self.root / 'research'
        research.mkdir()
        (research / 'queue.json').write_text(json.dumps({'topics': [
            {'id': 'triage-live', 'kind': 'map', 'job': 'log-triage', 'log': 'live'},
            {'id': 'triage-file', 'kind': 'map', 'job': 'log-triage', 'log': str(self.log)}]}))
        self.patch(local_jobs.precheck, 'RESEARCH', research)
        self.assertEqual(local_jobs.log_path(research / 'triage-live'), local_jobs.LOGS['live'])
        self.assertEqual(local_jobs.log_path(research / 'other'), local_jobs.LOGS['test'])
        self.assertEqual(local_jobs.log_path(research / 'triage-live', 'test'), local_jobs.LOGS['test'])
        self.assertEqual(local_jobs.log_path(research / 'other', '/opt/swg/x/log/'), '/opt/swg/x/log/core3.log')
        self.assertEqual(local_jobs.prepare('log-triage', research / 'triage-file')[0], 5)

    def test_listed_patterns_skip_the_model_and_the_report_puts_crash_risks_first(self):
        known = self.root / 'log-known.txt'
        known.write_text('# comment\ncould not open lua derv\tstock: templates for later content\n', encoding='utf-8')
        self.patch(local_jobs, 'LOG_KNOWN', known)
        folder = self.root / 'triage'
        local_jobs.prepare('log-triage', folder, str(self.log))
        lines = json.loads((folder / 'lines.json').read_text(encoding='utf-8'))
        self.assertEqual(len(lines), 4)
        self.assertNotIn('lua derv', '\n'.join(lines.values()))
        ids = {v.split('\t')[3][:20]: k for k, v in lines.items()}
        self.answer(folder, [
            {'id': ids['[ZoneClientSession] '], 'verdict': 'known and harmless', 'why': 'a bot | sends a short packet'},
            {'id': ids['[CreatureObject] ski'], 'verdict': 'new', 'why': 'skill data and points disagree'},
            {'id': ids["terminate called aft"], 'verdict': 'Crash risk', 'why': 'the process aborted'},
            {'id': 'p99', 'verdict': 'crash-risk', 'why': 'made up'}])
        text = self.report('log-triage', folder)
        self.assertIn('8 error and warning lines in 5 patterns, 1 of them known from log-known.txt', text)
        self.assertIn('crash-risk: 1, new: 1, known: 2, no answer: 1.', text)
        rows = [r for r in text.splitlines() if r.startswith('| ') and not r.startswith('| Verdict')]
        self.assertEqual([r.split(' | ')[0] for r in rows],
                         ['| crash-risk', '| new', '| known', '| known', '| no answer'])
        self.assertIn('| known | ERROR | 3 | 10/16 1:05 PM |', text)
        self.assertIn('a bot \\| sends a short packet', text)
        self.assertIn('log-known.txt: stock: templates for later content', text)
        self.assertNotIn('made up', text)


def twelve_hour(d):
    return f'{d:%Y-%m-%d} {d.hour % 12 or 12}:{d:%M} {"AM" if d.hour < 12 else "PM"}'


class BoardTrimTests(Folder):
    def setUp(self):
        super().setUp()
        now = datetime.now()
        recent, old, older = now - timedelta(days=1), now - timedelta(days=3), now - timedelta(days=5)
        self.old = twelve_hour(old)
        self.board = self.root / 'SWG-handoff.md'
        self.board.write_text(
            '# Board\n\n## Task board\n\n### 2020-01-01 1:00 PM Claude: not a log entry\n\nrow\n\n'
            '## Log\n\n'
            f'### {recent:%Y-%m-%d %H:%M} Claude: too new\n\n- stays\n\n'
            f'### {self.old} Claude: missions run 30\n\n- Fixed in dev `1be13676` on run 30; the owner, 17 Oct: '
            '"keep the bots busy".\n\t- second line\n\n'
            f'### {older:%Y-%m-%d %H:%M} ChatGPT: C54 review\n\n- Reviewed `a07d346`.\n\n'
            '## Instructions\n\n### 2020-01-02 2:00 PM Claude: after the log\n', encoding='utf-8')
        self.patch(local_jobs, 'BOARD', self.board)

    def test_only_log_entries_older_than_two_days(self):
        folder = self.root / 'trim'
        self.assertEqual(local_jobs.prepare('board-trim', folder), (2, 1))
        lines = json.loads((folder / 'lines.json').read_text(encoding='utf-8'))
        self.assertEqual(list(lines), ['b1', 'b2'])
        self.assertEqual(lines['b1'], f'{self.old} Claude: missions run 30 ¶ - Fixed in dev `1be13676` on run 30; the '
                                      'owner, 17 Oct: "keep the bots busy". ¶ - second line')
        self.assertTrue(lines['b2'].endswith('ChatGPT: C54 review ¶ - Reviewed `a07d346`.'))
        self.assertEqual(local_jobs.board_facts(lines['b1']), ['1be13676', 'run 30', 'keep the bots busy'])
        self.assertEqual(self.board.read_text(encoding='utf-8').count('###'), 5)   # the board itself is untouched

    def test_report_proposes_lines_and_names_what_they_dropped(self):
        folder = self.root / 'trim'
        local_jobs.prepare('board-trim', folder)
        self.answer(folder, [{'id': 'b1', 'line': 'Missions fixed in dev 1be13676.'}])
        text = self.report('board-trim', folder)
        self.assertIn(f'### {self.old} Claude: missions run 30\n\n- {self.old} Claude: Missions fixed in dev 1be13676.\n'
                      '- **Dropped from the line:** `run 30`, "keep the bots busy"', text)
        self.assertIn('ChatGPT: C54 review\n\n- No answer yet.', text)
        self.assertIn('This job changes nothing', text)


PLAN = """\
#### 7. Skills, XP, trainers
- **Check:** each profession trains.
- **Gaps:** training at a real trainer is untested.
- **Pass:** a `trainer-buy` scenario buys one novice box.

#### 18. Vehicles and mounts
- **Gaps:** the body cannot mount.
- **Pass:** a scenario calls a speeder and mounts.

## 3. Gaps to close first

| Rank | Gap | Why first | Who | Done when |
|---|---|---|---|---|
| 3 | Training at a real trainer, and the class check | first hour | GPT | section 7 |
| 6 | ~~Doctor and entertainer buffs~~ **done 17 Oct** | social | GPT | sections 22, 23 |
| 14 | Vehicles and mounts | later | GPT | section 18 |
"""


class ScenarioDraftTests(Folder):
    def setUp(self):
        super().setUp()
        research = self.root / 'research'
        for tid, notes in (('skills-training', '- Buy the novice box at a trainer; expect `@skill_teacher:prose_pay`.'),
                           ('vehicle-mount', '- Call the speeder; expect state RIDINGMOUNT.'),
                           ('guilds', '- Not an open area this time.')):
            (research / tid).mkdir(parents=True)
            (research / tid / 'report.md').write_text(f'## 2. How\nnot this\n## 3. What a bot test should check\n{notes}\n'
                                                      '## 4. Why\nnot this\n', encoding='utf-8')
        (research / 'queue.json').write_text(json.dumps({'topics': []}))
        plan = self.root / 'plan.md'
        plan.write_text(PLAN, encoding='utf-8')
        self.patch(local_jobs.precheck, 'RESEARCH', research)
        self.patch(local_jobs, 'TEST_PLAN', plan)

    def test_one_input_per_open_area_with_the_api_and_the_example(self):
        folder = self.root / 'drafts-topic'
        self.assertEqual(local_jobs.prepare('scenario-draft', folder), (2, 2))
        lines = json.loads((folder / 'lines.json').read_text(encoding='utf-8'))
        self.assertEqual(list(lines), ['trainers', 'vehicles'])   # buffs is done; the rest have no row in section 3
        self.assertEqual(lines['trainers'], 'Training at a real trainer. TEST PLAN: section 7: Gaps: training at a real '
                                            'trainer is untested. ¶ section 7: Pass: a `trainer-buy` scenario buys one '
                                            'novice box. NOTES: [skills-training] - Buy the novice box at a trainer; '
                                            'expect `@skill_teacher:prose_pay`.')
        self.assertIn('NOTES: [vehicle-mount] - Call the speeder', lines['vehicles'])
        instruction = (folder / 'instruction.txt').read_text(encoding='utf-8')
        self.assertIn('BOT API (tools/bots/squad.py):\nclass Bot:\n', instruction)
        self.assertIn('    walk(x, y, z=None, cell=None, tries=3)  # move, repeated while it times out', instruction)
        self.assertIn("\nclass Group:\n", instruction)
        self.assertIn("    check(label, ok, detail='')  # Record a pass/fail check; returns ok.", instruction)
        self.assertNotIn('creds(', instruction)
        self.assertIn('A FINISHED SCENARIO (tools/bots/scenarios/aurek-hunt.py):\n"""Aurek', instruction)
        self.assertIn('def run(g):', instruction)

    def test_drafts_go_to_the_topic_folder_with_checks_made_without_the_model(self):
        folder = self.root / 'drafts-topic'
        local_jobs.prepare('scenario-draft', folder)
        chunks = [json.loads(line) for line in (folder / 'input.jsonl').read_text(encoding='utf-8').splitlines()]
        good = ('"""Trainers: buy one novice box."""\nGROUP = \'TODO\'\n\n\ndef run(g):\n    bot = g.bots[0]\n'
                "    bot.slash('agentGear', 'kit')\n    bot.slash('flyToTheMoon')\n    bot.teleport(1, 2)\n"
                "    g.check('box bought', 'prose_pay' in ' '.join(bot.messages()).lower())\n")
        records = [{'id': chunks[0]['id'], 'answer': {'items': [
                       {'id': 'trainers', 'code': good, 'gaps': ['the trainer window | its list']}]}},
                   {'id': chunks[1]['id'], 'answer': {'items': [{'id': 'vehicles', 'code': 'def run(g):\n    g.check(\n'}]}}]
        (folder / 'results.jsonl').write_text(''.join(json.dumps(r) + '\n' for r in records), encoding='utf-8')
        with mock.patch.object(local_jobs.precheck, 'known_commands', return_value={'agentgear'}):
            text = self.report('scenario-draft', folder)
        self.assertEqual(sorted(p.name for p in (folder / 'drafts').iterdir()), ['trainers.py', 'vehicles.py'])
        draft = (folder / 'drafts' / 'trainers.py').read_text(encoding='utf-8')
        self.assertTrue(draft.startswith('# DRAFT by a local model'))
        self.assertTrue(draft.endswith(good))
        self.assertIn('| trainers | `drafts/trainers.py`, 10 lines | ok | flyToTheMoon | teleport | '
                      'the trainer window \\| its list |', text)
        self.assertIn('| vehicles | `drafts/vehicles.py`, 2 lines | line 2:', text)
        self.assertIn('Left out as done or no longer listed open: buffs, surveys, groups-mail-guilds,', text)

    def test_all_three_jobs_are_known(self):
        for job in ('log-triage', 'board-trim', 'scenario-draft'):
            self.assertIn('JSON only', local_jobs.INSTRUCTIONS[job])
            self.assertIn(job, local_jobs.CHUNK)


if __name__ == '__main__':
    unittest.main()
