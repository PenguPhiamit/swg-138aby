"""Offline tests for local_map.py and local_jobs.py (Claude, 15 Oct 2026). No Ollama, no network, no real memory
readings: the model, the memory check and the owner's-client check are stand-ins. Runs on Windows or in WSL:

    python -I test_local_map.py
"""
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import local_jobs
import local_map

BASE = 'http://127.0.0.1:11434'


class Model:
    """Stand-in for ask(): answers {"items": []} and records which chunks it saw; fails for texts in `fail`."""
    def __init__(self, fail=()):
        self.seen, self.fail = [], set(fail)

    def __call__(self, base, model, ctx, instruction, text, timeout=180):
        self.seen.append(text)
        if text in self.fail:
            raise ValueError('bad JSON')
        return {'items': [{'id': text.split('\t')[0], 'note': 'x'}]}


def run(out, chunks, model, headroom=lambda: 20.0, client=lambda: False, **kw):
    unloads = []
    code, summary = local_map.run(chunks, 'instr', out, BASE, 'qwen3:8b', 8192, headroom=headroom,
                                  unload=lambda base, m: unloads.append(m), client=client, asker=model,
                                  log=lambda line: None, **kw)
    return code, summary, unloads


class LocalMapTests(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.dir.cleanup)
        self.out = Path(self.dir.name)
        self.chunks = [{'id': f'c{n}', 'text': f'l{n}\ttext {n}'} for n in range(12)]
        sleep = mock.patch.object(local_map.time, 'sleep')
        sleep.start()
        self.addCleanup(sleep.stop)

    def test_all_chunks_answered_then_a_rerun_skips_them(self):
        model = Model()
        code, summary, unloads = run(self.out, self.chunks, model)
        self.assertEqual((code, len(model.seen)), (0, 12))
        # unloaded every 5 chunks (before the 6th and 11th) and once at the end: the prompt cache never piles up
        self.assertEqual(len(unloads), 3)
        again = Model()
        code, summary, _ = run(self.out, self.chunks, again)
        self.assertEqual((code, again.seen), (0, []))
        self.assertIn('12 done before', summary)

    def test_failed_chunks_are_retried_next_time(self):
        code, summary, _ = run(self.out, self.chunks, Model(fail={'l3\ttext 3'}))
        self.assertEqual(code, 3)
        self.assertIn('failed; rerun', summary)
        retry = Model()
        self.assertEqual(run(self.out, self.chunks, retry)[0], 0)
        self.assertEqual(retry.seen, ['l3\ttext 3'])

    def test_low_memory_pauses_after_trying_an_unload(self):
        readings = iter([20.0, 20.0, 3.0, 3.0])
        model = Model()
        code, summary, unloads = run(self.out, self.chunks, model, headroom=lambda: next(readings))
        self.assertEqual((code, len(model.seen)), (3, 2))
        self.assertIn('commit headroom 3.0 GB', summary)
        self.assertGreaterEqual(len(unloads), 2)   # the try, then the one at the end

    def test_unknown_memory_does_not_stop_the_run(self):
        self.assertEqual(run(self.out, self.chunks, Model(), headroom=lambda: None)[0], 0)

    def test_yields_to_the_owner(self):
        model = Model()
        code, summary, _ = run(self.out, self.chunks, model, client=lambda: True, yield_to_owner=True)
        self.assertEqual((code, model.seen), (3, []))
        self.assertIn("owner's SWG client", summary)

    def test_a_remote_server_gets_no_memory_checks_but_the_same_unloads(self):
        # 17 Oct: the prompt cache grows in the other PC's RAM too, so it is emptied there on the same schedule
        with mock.patch.object(local_map.ollama_url, 'is_local', return_value=False):
            code, _, unloads = run(self.out, self.chunks, Model(),
                                   headroom=mock.Mock(side_effect=AssertionError('this PC')))
        self.assertEqual((code, len(unloads)), (0, 3))


class LocalJobsTests(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.dir.cleanup)
        self.root = Path(self.dir.name)

    def test_chunk_ids_follow_the_content(self):
        lines = [(f'k{n}', f'text {n}') for n in range(90)]
        first, again = local_jobs.chunk_lines(lines), local_jobs.chunk_lines(lines)
        self.assertEqual([c['id'] for c in first], [c['id'] for c in again])
        self.assertEqual(len(first), 3)
        changed = local_jobs.chunk_lines(lines[:-1] + [('k89', 'other')])
        self.assertEqual([c['id'] for c in changed][:2], [c['id'] for c in first][:2])
        self.assertNotEqual(changed[2]['id'], first[2]['id'])

    def write_job(self, job, lines, answers):
        folder = self.root / job
        folder.mkdir()
        chunks = local_jobs.chunk_lines(lines)
        (folder / 'input.jsonl').write_text(''.join(json.dumps(c) + '\n' for c in chunks), encoding='utf-8')
        (folder / 'lines.json').write_text(json.dumps(dict(lines)), encoding='utf-8')
        records = [{'id': chunks[0]['id'], 'answer': {'items': answers}},
                   {'id': 'stale-chunk', 'answer': {'items': [{'id': lines[0][0], 'problem': 'old', 'fix': 'old'}]}}]
        (folder / 'results.jsonl').write_text(''.join(json.dumps(r) + '\n' for r in records), encoding='utf-8')
        return folder

    def test_proofread_report_keeps_real_ids_and_changed_fixes_only(self):
        lines = [('a.stf:one', 'Teh first line'), ('a.stf:two', 'Fine | text')]
        folder = self.write_job('proofread', lines, [
            {'id': 'a.stf:one', 'problem': 'typo', 'fix': 'The first line'},
            {'id': 'a.stf:two', 'problem': 'none', 'fix': 'Fine | text'},      # unchanged: dropped
            {'id': 'made:up', 'problem': 'x', 'fix': 'y'}])                       # not an input id: dropped
        self.assertEqual(local_jobs.report('proofread', folder), 2)
        text = (folder / 'report.md').read_text(encoding='utf-8')
        self.assertIn('| `a.stf:one` | Teh first line | typo | The first line |', text)
        self.assertNotIn('a.stf:two', text)
        self.assertNotIn('made:up', text)
        self.assertNotIn('old', text)   # the answer to a chunk that is no longer in the input

    def test_bot_gaps_group_by_kind_and_gap(self):
        lines = [('g1', 'Esk\t3x\t10/15 09:00\tBLOCKED: no terminal_bank nearby'),
                 ('g2', 'Esk\t2x\t10/15 10:00\tBLOCKED: no terminal_bank within reach'),
                 ('g3', 'Dorn\t1x\t10/14 22:00\tFAIL: leash | stops')]
        folder = self.write_job('bot-gaps', lines, [
            {'id': 'g1', 'gap': 'Bank terminal not reachable', 'kind': 'scenario'},
            {'id': 'g2', 'gap': 'bank terminal not reachable', 'kind': 'Scenario'},
            {'id': 'g3', 'gap': 'leash follow stops early', 'kind': 'server'}])
        local_jobs.report('bot-gaps', folder)
        text = (folder / 'report.md').read_text(encoding='utf-8')
        self.assertIn('| bank terminal not reachable | 2 | 5x | 10/15 10:00 |', text)
        self.assertLess(text.index('## server'), text.index('## scenario'))
        self.assertIn('leash \\| stops', text)

    def test_bot_notes_merge_lines_that_differ_only_in_numbers(self):
        group = self.root / 'Esk'
        group.mkdir()
        for n, (x, ok) in enumerate(((812, False), (950, False), (10, True))):
            (group / f'2026101{n}-report.json').write_text(json.dumps({
                'notes': [f'BLOCKED: no terminal_bank within {x} m', 'ordinary note'],
                'checks': [{'label': 'arrives', 'ok': ok, 'detail': f'{x} m short'}]}), encoding='utf-8')
        notes = dict(local_jobs.bot_notes(self.root))
        self.assertEqual(len(notes), 2)
        texts = sorted(line.split('\t', 3)[3] for line in notes.values())
        self.assertTrue(texts[0].startswith('BLOCKED: no terminal_bank within'))
        self.assertTrue(texts[1].startswith('FAIL: arrives'))
        counts = {line.split('\t', 3)[3].split(':')[0]: line.split('\t')[1] for line in notes.values()}
        self.assertEqual(counts, {'BLOCKED': '3x', 'FAIL': '2x'})   # the note is in all three, the check failed twice


class PrecheckTests(unittest.TestCase):
    """precheck.py (17 Oct): claims against their cited lines, and older against newer reports."""

    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.dir.cleanup)
        self.root = Path(self.dir.name)
        (self.root / 'queue.json').write_text(json.dumps({'topics': [{'id': 'camps'}, {'id': 'gaps', 'kind': 'map'}]}))
        camp = self.root / 'camps'
        (camp / 'src' / 'src' / 'server').mkdir(parents=True)
        (camp / 'src' / 'src' / 'server' / 'Camp.cpp.lines-10-14').write_text(
            ''.join(f'{n:6d}| line {n} of the camp code\n' for n in range(10, 15)))
        (camp / 'report.md').write_text('# Camps\n\n- Placing needs skill 5 (Camp.cpp:12).\n'
                                        '- Abandoned after 30 s (`src/.../Camp.cpp:13-14`); see also Gone.h:4.\n'
                                        '- Past the copy: Camp.cpp:900\n')
        (camp / 'report.previous.md').write_text('Old: skill 3.\n')
        (self.root / 'gaps').mkdir()
        (self.root / 'gaps' / 'report.md').write_text('a chunk job, not checked: Camp.cpp:12\n')

    def test_claims_carry_the_cited_lines_from_the_topics_own_copy(self):
        lines, problems = local_jobs.precheck.claim_lines(self.root, index={})
        self.assertEqual([i for i, _ in lines], ['camps#1', 'camps#2'])
        text = dict(lines)
        self.assertIn('Placing needs skill 5', text['camps#1'])
        self.assertIn('CODE: 10: line 10 of the camp code ¶ 11:', text['camps#1'])   # a single line gets 2 around it
        self.assertIn('14: line 14', text['camps#2'])
        self.assertNotIn('\t', ''.join(text.values()) + ''.join(t for _, t in lines))
        self.assertEqual(sorted(p['cite'] for p in problems), ['Camp.cpp:900', 'Gone.h:4'])
        self.assertIn('no file with that name', next(p['problem'] for p in problems if p['cite'] == 'Gone.h:4'))

    def test_claim_report_lists_the_doubtful_claims_first(self):
        lines, problems = local_jobs.precheck.claim_lines(self.root, index={})
        body = local_jobs.precheck.claim_report(dict(lines), [
            {'id': 'camps#1', 'verdict': 'contradicted', 'why': 'line 12 says nothing about skill'},
            {'id': 'camps#2', 'verdict': 'supported', 'why': 'ok'}, {'id': 'made#up', 'verdict': 'supported'}], problems)
        self.assertIn('2 cited claims in 1 reports', body)
        self.assertIn('| camps | 2 | 1 | 0 | 2 |', body)
        self.assertIn('## Contradicted by the cited lines (check these first)', body)
        self.assertIn('line 12 says nothing about skill', body)
        self.assertIn('`Gone.h:4`', body)
        self.assertNotIn('made#up', body)

    def test_report_diff_pairs_old_and_new_reports_only(self):
        pairs = dict(local_jobs.precheck.diff_lines(self.root))
        self.assertEqual(list(pairs), ['camps'])
        self.assertTrue(pairs['camps'].startswith('OLD: Old: skill 3. NEW: # Camps ¶'))
        body = local_jobs.precheck.diff_report(pairs, [{'id': 'camps', 'disagreements': [
            {'point': 'skill needed', 'old': '3', 'new': '5'}]}])
        self.assertIn('| skill needed | 3 | 5 |', body)

    def test_test_index_takes_section_three_only(self):
        (self.root / 'camps' / 'report.md').write_text('## 2. How it works\nnot this\n## 3. What a bot test should check\n'
                                                       '- Place a camp kit; expect "camp placed".\n## 4. Likely reasons\nnot this\n')
        lines = dict(local_jobs.precheck.test_index_lines(self.root))
        self.assertEqual(lines, {'camps': '- Place a camp kit; expect "camp placed".'})
        body = local_jobs.precheck.test_index_report(lines, [{'id': 'camps', 'checks': [
            {'setup': 'scout with a kit', 'do': 'use the kit', 'expect': 'camp placed'}]}])
        self.assertIn('| scout with a kit | use the kit | camp placed |', body)

    def test_scenario_review_flags_unknown_commands_without_the_model(self):
        folder = self.root / 'scenarios'
        folder.mkdir()
        (folder / 'a-test.py').write_text("def run(g):\n    bot.slash('agentGear', 'kit')\n    bot.slash('flyToTheMoon')\n")
        lines, unknown = local_jobs.precheck.scenario_lines(folder, known={'agentgear'})
        self.assertEqual(unknown, {'a-test.py': ['flyToTheMoon']})
        self.assertEqual([i for i, _ in lines], ['a-test.py#1'])
        self.assertIn("COMMANDS THE SERVER DOES NOT KNOW: flyToTheMoon CODE: def run(g): ¶     bot.slash('agentGear'", lines[0][1])
        body = local_jobs.precheck.scenario_report(dict(lines), [{'id': 'a-test.py#1', 'findings': [
            {'where': 'run', 'problem': 'no check after the command', 'why': 'the test always passes'}]}], unknown)
        self.assertIn('- `a-test.py`: flyToTheMoon', body)
        self.assertIn('| run | no check after the command | the test always passes |', body)

    def test_both_jobs_are_known_to_local_jobs(self):
        for job in ('claim-check', 'report-diff', 'test-index', 'scenario-review'):
            self.assertIn(job, local_jobs.INSTRUCTIONS)
            self.assertIn('JSON only', local_jobs.INSTRUCTIONS[job])


if __name__ == '__main__':
    unittest.main()
