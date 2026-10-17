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
SKIP_TOPICS = {'report-precheck', 'report-diff'}

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
}
CHUNK = {'claim-check': 4, 'report-diff': 1}


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


def claim_lines(root=RESEARCH, index=None):
    """([(id, chunk text)] for the model, [mechanical problems]) over every report's citations."""
    index = tree_index() if index is None else index
    lines, problems = [], []
    for tid, folder in topics(root):
        snap, seen, n = snapshot(folder), set(), 0
        for row in (folder / 'report.md').read_text(encoding='utf-8', errors='replace').split('\n'):
            claim = flat(re.sub(r'[*`#>]', '', row), 400).lstrip('- ').strip()
            for m in CITE.finditer(row):
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


if __name__ == '__main__':   # a dry run: how many claims and problems there would be, without the model
    claims, issues = claim_lines()
    print(f'{len(claims)} claims to check, {len(issues)} citation problems, {len(diff_lines())} report pairs')
    for p in issues[:10]:
        print('  ', p['topic'], p['cite'], '-', p['problem'])
    sys.exit(0)
