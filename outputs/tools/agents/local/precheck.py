"""First-pass checks of the local model's research reports (Claude, 17 Oct 2026; owner: pre-check the 48 reports so
the review starts with the doubtful claims). Two chunk jobs for local_jobs.py:

  claim-check  Every "file:line" a report in Agent/local-research/<id>/report.md cites is looked up, first in that
               topic's own line-numbered copy of the source (<id>/src/), else in Core3-dev (or the project's bot
               scenarios for .py). A citation that can't be resolved (no such file, several files with that name,
               a line past the end) is listed without asking the model. The others go to the model as
               "claim + the cited lines", and it says "supported", "contradicted" or "not shown" for each.
  report-diff  For each topic that has both report.previous.md (the older report) and report.md, the model lists
               where the two disagree (numbers, conditions, messages, citations).

Both are first passes by a local model: the reviewer still checks each claim, and starts with the ones listed here.
Reads only reports and source text; the model sees nothing else.
"""
import json
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUTPUTS = HERE.parents[2]
RESEARCH = OUTPUTS / 'Agent' / 'local-research'
SCENARIOS = OUTPUTS / 'tools' / 'bots'
CORE3 = Path('/opt/swg/Core3-dev/MMOCoreORB')
CITE = re.compile(r'(?<![\w/.-])((?:[\w.-]+/)*[\w-]+\.(?:cpp|h|idl|lua|py))((?::\d+(?:-\d+)?)(?:,\s*\d+(?:-\d+)?)*)')
NUMBERED = re.compile(r'^\s*(\d+)\| ?(.*)$')
MAX_CLAIMS, MAX_LINES, CONTEXT = 40, 24, 2   # per report; cited lines shown per claim; lines around a single-line cite
SKIP_TOPICS = {'report-precheck', 'report-diff', 'test-index', 'scenario-review', 'claim-recheck'}
AUDIT = OUTPUTS / 'tools' / 'core3_audit' / 'command_audit.json'
SLASH = re.compile(r"""\.slash\(\s*['"]([A-Za-z0-9_]+)""")
SECTION3 = re.compile(r'^(#+)\s*(?:3[.)]?\s*)?what a (?:[\w-]+ )?test should check', re.I)
SCENARIO_PART = 14000   # characters of a scenario per chunk

INSTRUCTIONS = {
    'claim-check': """You check claims in research notes about a game server's source code (SWGEmu Core3: C++ and Lua).
Each input line is "<id>\t<claim> [CITED <file>:<lines>] CODE: <the cited lines>", where each code line is
"N: code" and " ¶ " separates them. Judge only from the code shown:
- "supported": the code shows what the claim says (its numbers, conditions, names and messages);
- "contradicted": the code shows something different (say what it shows);
- "not shown": these lines don't contain what the claim says, even if it may be true elsewhere.
Be strict with numbers, comparison signs and message names. Answer with JSON only:
{"items": [{"id": "<id exactly as given>", "verdict": "supported|contradicted|not shown", "why": "<at most 20 words>"}]}""",
    'report-diff': """You compare two research notes about the same game mechanic, an older one (OLD) and a newer one
(NEW), both written from the same server source code. Each input line is "<id>\tOLD: <text> NEW: <text>", where " ¶ "
marks a line break. List the points where they disagree: different numbers, conditions, timings, messages, or one
saying something works that the other says doesn't. Ignore wording, order, and points only one of them covers. At most
10 per input. Answer with JSON only:
{"items": [{"id": "<id exactly as given>", "disagreements": [{"point": "<what it is about>", "old": "<OLD says>",
"new": "<NEW says>"}]}]}. If they agree: "disagreements": [].""",
    'test-index': """You turn research notes into bot test steps for a Star Wars Galaxies emulator test server. Each input
line is "<id>\t<the notes' section 'What a bot test should check'>", where " ¶ " marks a line break. Write each check as
one step: the setup it needs, what the bot does, and what it should observe (a system message, a state, an item, a
number). Keep numbers, command names and message ids exactly as written; leave out anything that is not a check. At
most 8 per input. Answer with JSON only:
{"items": [{"id": "<id exactly as given>", "checks": [{"setup": "...", "do": "...", "expect": "..."}]}]}""",
    'scenario-review': """You review part of a Python test scenario that drives a bot on a Star Wars Galaxies emulator
test server (SWGEmu Core3). Each input line is "<id>\tCOMMANDS THE SERVER DOES NOT KNOW: <list or none> CODE: <the
code>", where " ¶ " marks a line break. bot.slash(name, ...) sends a server command; g.check(label, ok, detail) records
a pass or fail. List real problems only: a command the server does not know, a check that can never fail or never
pass, a wait with no timeout, a result read before it can arrive, a wrong comparison, a variable used before it is set,
or a step that leaves the bot stuck for the next test. Ignore style. At most 6 per input. Answer with JSON only:
{"items": [{"id": "<id exactly as given>", "findings": [{"where": "<function name or a short quote of the code>",
"problem": "<what is wrong>", "why": "<what happens because of it>"}]}]}. If nothing is wrong: "findings": [].""",
}
CHUNK = {'claim-check': 4, 'report-diff': 1, 'test-index': 1, 'scenario-review': 1}


def flat(text, cap):
    """One line for the chunk format: no tabs or line breaks, capped."""
    return ' '.join(str(text).replace('\t', ' ').split())[:cap]


def topics(root=RESEARCH):
    """Research topic folders with a report: [(id, folder)], map jobs and these checks left out."""
    try:
        queue = json.loads((root / 'queue.json').read_text(encoding='utf-8'))['topics']
    except (OSError, ValueError, KeyError):
        queue = []
    maps = {t['id'] for t in queue if t.get('kind') == 'map'}
    return [(p.name, p) for p in sorted(root.iterdir()) if p.is_dir() and (p / 'report.md').exists()
            and p.name not in maps and p.name not in SKIP_TOPICS]


def snapshot(folder):
    """{basename: [(relative path, {line number: code})]} from a topic's line-numbered source copies."""
    out = defaultdict(list)
    src = folder / 'src'
    for path in (src.rglob('*') if src.is_dir() else []):
        if not path.is_file():
            continue
        name = re.sub(r'\.lines-\d+-\d+$', '', path.name)
        lines = {}
        for text in path.read_text(encoding='utf-8', errors='replace').split('\n'):
            m = NUMBERED.match(text)
            if m:
                lines[int(m.group(1))] = m.group(2)
        rel = re.sub(r'\.lines-\d+-\d+$', '', path.relative_to(src).as_posix())
        out[name].append((rel, lines))
    return out


def tree_index():
    """{basename: [path]} for Core3-dev (git ls-files, read-only) and the project's bot tools."""
    index = defaultdict(list)
    try:
        listing = subprocess.run(['git', '-C', str(CORE3.parent), 'ls-files', 'MMOCoreORB/src', 'MMOCoreORB/bin/scripts'],
                                 capture_output=True, text=True, timeout=120).stdout.split()
    except (OSError, subprocess.SubprocessError):
        listing = []
    for rel in listing:
        index[rel.rsplit('/', 1)[-1]].append(CORE3.parent / rel)
    for path in SCENARIOS.rglob('*.py'):
        index[path.name].append(path)
    return index


def spans(text):
    """':12-14, 20' -> [(12, 14), (20, 20)]."""
    out = []
    for part in text.lstrip(':').split(','):
        a, _, b = part.strip().partition('-')
        out.append((int(a), int(b or a)))
    return out


def resolve(cited, snap, index):
    """(source name, {line: code} or None, problem or None) for a cited path."""
    name = cited.rsplit('/', 1)[-1]
    if '...' in cited:   # reports shorten paths as src/.../File.cpp: match on the name alone
        cited = name
    local = [(rel, lines) for rel, lines in snap.get(name, []) if rel.endswith(cited) or '/' not in cited]
    if local:
        merged = {}
        for _, lines in local:
            merged.update(lines)
        return local[0][0], merged, None
    found = [p for p in index.get(name, []) if p.as_posix().endswith(cited)]
    if not found:
        return cited, None, 'no file with that name in the topic copy, Core3-dev or the bot tools'
    if len({p.as_posix() for p in found}) > 1:
        return cited, None, f'{len(found)} files are named {name}; the citation does not say which'
    try:
        text = found[0].read_text(encoding='utf-8', errors='replace').split('\n')
    except OSError as error:
        return cited, None, f'unreadable ({error})'
    return found[0].as_posix(), {n: t for n, t in enumerate(text, 1)}, None


def claim_at(text, cite, cap=400):
    """The part of one report row that a citation belongs to, at most cap characters. A short row is the claim as it
    is; in a longer one, the sentence holding the citation (with the one before it while that fits), so a citation
    late in a paragraph is not cut off (18 Oct: player-vendors#3 lost its sentence to the old first-400 cut)."""
    if len(text) <= cap:
        return text
    at = text.find(cite)
    if at < 0:
        return text[:cap]
    starts = [0] + [s.end() for s in re.finditer(r'[.;]\s+(?=[A-Z0-9(])', text)]
    i = max(k for k, s in enumerate(starts) if s <= at)
    a, b = starts[i], starts[i + 1] if i + 1 < len(starts) else len(text)
    if i and b - starts[i - 1] <= cap:
        a = starts[i - 1]
    if b - a > cap:
        end = min(b, at + len(cite) + 40)
        a, b = max(a, end - cap), end
    return text[a:b].strip()


def claim_lines(root=RESEARCH, index=None):
    """([(id, chunk text)] for the model, [mechanical problems]) over every report's citations."""
    index = tree_index() if index is None else index
    lines, problems = [], []
    for tid, folder in topics(root):
        snap, seen, n = snapshot(folder), set(), 0
        for row in (folder / 'report.md').read_text(encoding='utf-8', errors='replace').split('\n'):
            clean = flat(re.sub(r'[*`#>]', '', row), 100000).lstrip('- ').strip()
            for m in CITE.finditer(row):
                claim = claim_at(clean, m.group(0))
                key = (m.group(1), m.group(2), claim)
                if key in seen or n >= MAX_CLAIMS:
                    continue
                seen.add(key)
                name, code, problem = resolve(m.group(1), snap, index)
                cite = f'{m.group(1)}{m.group(2)}'
                if problem is None:
                    wanted = []
                    for a, b in spans(m.group(2)):
                        a, b = (a - CONTEXT, b + CONTEXT) if a == b else (a, b)
                        wanted += [k for k in range(a, b + 1) if k in code][:MAX_LINES]
                    if not any(k in code for a, b in spans(m.group(2)) for k in range(a, b + 1)):
                        last = max(code) if code else 0
                        problem = (f'line {spans(m.group(2))[0][0]} is past the end ({last} lines)' if all(
                            a > last for a, _ in spans(m.group(2))) else 'the cited lines are not in the copy the topic read')
                if problem:
                    problems.append({'topic': tid, 'cite': cite, 'claim': claim, 'problem': problem})
                    continue
                n += 1
                excerpt = ' ¶ '.join(f'{k}: {code[k].strip()}' for k in wanted)
                lines.append((f'{tid}#{n}', flat(f'{claim} [CITED {name.rsplit("/", 1)[-1]}{m.group(2)}] CODE: {excerpt}', 2400)))
    return lines, problems


def diff_lines(root=RESEARCH, cap=9000):
    """[(topic, 'OLD: ... NEW: ...')] for every topic with both an older and a newer report."""
    out = []
    for tid, folder in topics(root):
        old = folder / 'report.previous.md'
        if old.exists():
            text = lambda p: ' ¶ '.join(l.strip() for l in p.read_text(encoding='utf-8', errors='replace').split('\n') if l.strip())
            out.append((tid, flat(f'OLD: {text(old)[:cap]} NEW: {text(folder / "report.md")[:cap]}', 2 * cap + 20)))
    return out


def cell(text, cap):
    return ' '.join(str(text).split())[:cap].replace('|', r'\|')


def claim_report(lines, items, problems):
    """Markdown for the claim check: worst reports first, then the contradicted and not-shown claims, then the
    citations that couldn't be resolved."""
    verdict = {i['id']: (str(i.get('verdict', '')).lower().strip(), i.get('why', '')) for i in items if i['id'] in lines}
    per = defaultdict(lambda: defaultdict(int))
    for cid in lines:
        per[cid.split('#')[0]][verdict.get(cid, ('unanswered', ''))[0]] += 1
    for p in problems:
        per[p['topic']]['citation problem'] += 1
    total = defaultdict(int)
    for counts in per.values():
        for k, v in counts.items():
            total[k] += v
    order = sorted(per, key=lambda t: -(per[t]['contradicted'] * 3 + per[t]['not shown'] + per[t]['citation problem']))
    out = [f'{len(lines)} cited claims in {len(per)} reports: ' + ', '.join(f'{v} {k}' for k, v in sorted(total.items())) + '.',
           '', '| Report | Claims | Contradicted | Not shown | Citation problems |', '|---|---|---|---|---|']
    out += [f'| {t} | {sum(v for k, v in per[t].items() if k != "citation problem")} | {per[t]["contradicted"]} | '
            f'{per[t]["not shown"]} | {per[t]["citation problem"]} |' for t in order]
    for kind, title in (('contradicted', 'Contradicted by the cited lines (check these first)'),
                        ('not shown', 'Not shown by the cited lines')):
        rows = [(cid, verdict[cid][1]) for cid in lines if verdict.get(cid, ('',))[0] == kind]
        if rows:
            out += ['', f'## {title}', '']
            out += [f'- **{cid.split("#")[0]}**: {cell(lines[cid].split(" CODE: ")[0], 300)} ({cell(why, 160)})' for cid, why in rows]
    if problems:
        out += ['', '## Citations that could not be checked (no model involved)', '']
        out += [f'- **{p["topic"]}** `{p["cite"]}`: {p["problem"]}. Claim: {cell(p["claim"], 200)}' for p in problems]
    return '\n'.join(out) + '\n'


def diff_report(lines, items):
    out = []
    for i in sorted((i for i in items if i['id'] in lines), key=lambda i: i['id']):
        rows = [d for d in (i.get('disagreements') or []) if isinstance(d, dict)]
        out += [f'## {i["id"]}', '', 'The two reports agree on the points both cover.' if not rows else
                '| Point | report.previous.md | report.md |\n|---|---|---|\n' + '\n'.join(
                    f'| {cell(d.get("point", ""), 80)} | {cell(d.get("old", ""), 200)} | {cell(d.get("new", ""), 200)} |'
                    for d in rows), '']
    return '\n'.join(out) + '\n' if out else 'No topic has both an older and a newer report.\n'


def test_index_lines(root=RESEARCH):
    """[(topic, section 3 of its report)] for every research report that has that section."""
    out = []
    for tid, folder in topics(root):
        rows, level = [], 0   # level: the heading's depth once inside section 3; a sub-heading stays in it
        for row in (folder / 'report.md').read_text(encoding='utf-8', errors='replace').split('\n'):
            m = SECTION3.match(row.strip())
            if m and not level:
                level = len(m.group(1))
                continue
            depth = len(row.strip()) - len(row.strip().lstrip('#'))
            if level and depth and depth <= level:
                break
            inside = bool(level)
            if inside and row.strip():
                rows.append(row.strip())
        if rows:
            out.append((tid, flat(' ¶ '.join(rows), 5000)))
    return out


def known_commands(path=AUDIT):
    try:
        return {r['command'].lower() for r in json.loads(path.read_text(encoding='utf-8'))['rows']}
    except (OSError, ValueError, KeyError):
        return None   # without the audit, no command is called unknown


def scenario_lines(folder=SCENARIOS / 'scenarios', known=None):
    """([(file#part, chunk text)], {file: [commands the server doesn't know]}) for every bot scenario."""
    known = known_commands() if known is None else known
    lines, unknown = [], {}
    for path in sorted(Path(folder).glob('*.py')):
        code = path.read_text(encoding='utf-8', errors='replace')
        missing = sorted({c for c in SLASH.findall(code) if known is not None and c.lower() not in known})
        if missing:
            unknown[path.name] = missing
        # one line per chunk, but keep the indentation: Python's blocks are in it
        text = ' ¶ '.join(line.rstrip().replace('\t', '    ') for line in code.split('\n'))
        parts = [text[i:i + SCENARIO_PART] for i in range(0, len(text), SCENARIO_PART)] or ['']
        for n, part in enumerate(parts, 1):
            lines.append((f'{path.name}#{n}', f'COMMANDS THE SERVER DOES NOT KNOW: {", ".join(missing) or "none"} '
                                              f'CODE: {part}'))
    return lines, unknown


def test_index_report(lines, items):
    out = ['Steps drafted from section 3 of each research report. Check a step against its report before a '
           'scenario uses it.', '']
    for i in sorted((i for i in items if i['id'] in lines), key=lambda i: i['id']):
        rows = [c for c in (i.get('checks') or []) if isinstance(c, dict)]
        if rows:
            out += [f'## {i["id"]}', '', '| Setup | Bot does | Expect |', '|---|---|---|']
            out += [f'| {cell(c.get("setup", ""), 160)} | {cell(c.get("do", ""), 160)} | {cell(c.get("expect", ""), 200)} |'
                    for c in rows]
            out.append('')
    return '\n'.join(out) + '\n'


def scenario_report(lines, items, unknown):
    out = ['A first pass over the bot scenarios. Each finding is a lead to check in the code, not a confirmed bug.', '']
    if unknown:
        out += ['## Commands the server does not know (found without the model)', '']
        out += [f'- `{name}`: {", ".join(cmds)}' for name, cmds in sorted(unknown.items())] + ['']
    for i in sorted((i for i in items if i['id'] in lines), key=lambda i: i['id']):
        rows = [f for f in (i.get('findings') or []) if isinstance(f, dict)]
        if rows:
            out += [f'## {i["id"]}', '', '| Where | Problem | Why it matters |', '|---|---|---|']
            out += [f'| {cell(f.get("where", ""), 100)} | {cell(f.get("problem", ""), 200)} | {cell(f.get("why", ""), 200)} |'
                    for f in rows]
            out.append('')
    return '\n'.join(out) + '\n'


def job_lines(job, folder):
    """The (id, text) lines for one of this module's jobs; side files for the report go into folder."""
    if job == 'claim-check':   # the citations that can't be resolved are listed without the model
        lines, problems = claim_lines()
        (folder / 'citation-problems.json').write_text(json.dumps(problems, indent=1, ensure_ascii=False), encoding='utf-8')
        return lines
    if job == 'scenario-review':
        lines, unknown = scenario_lines()
        (folder / 'unknown-commands.json').write_text(json.dumps(unknown, indent=1), encoding='utf-8')
        return lines
    return diff_lines() if job == 'report-diff' else test_index_lines()


def job_report(job, folder, lines, items):
    def side(name, default):
        path = folder / name
        return json.loads(path.read_text(encoding='utf-8')) if path.exists() else default
    if job == 'claim-check':
        return claim_report(lines, items, side('citation-problems.json', []))
    if job == 'scenario-review':
        return scenario_report(lines, items, side('unknown-commands.json', {}))
    return diff_report(lines, items) if job == 'report-diff' else test_index_report(lines, items)


if __name__ == '__main__':   # a dry run: how many claims and problems there would be, without the model
    claims, issues = claim_lines()
    print(f'{len(claims)} claims to check, {len(issues)} citation problems, {len(diff_lines())} report pairs')
    for p in issues[:10]:
        print('  ', p['topic'], p['cite'], '-', p['problem'])
    sys.exit(0)
