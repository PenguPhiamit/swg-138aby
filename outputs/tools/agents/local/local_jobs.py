"""Inputs, instructions and reports for the local model's chunk jobs (Claude, 15 Oct 2026). idle_research.py runs
these for queue topics of kind "map"; each can also be run by hand:

    python3 local_jobs.py prepare JOB DIR    # writes DIR/input.jsonl and DIR/instruction.txt
    python3 local_jobs.py report JOB DIR     # turns DIR/results.jsonl into DIR/report.md

Jobs:
  proofread  Player-facing text that is ours: every string in the test client archive (SWG-client/local_planets.tre)
             whose text differs from the same key in the stock and MTG archives, plus the messages added to Core3-dev
             since the live branch (string literals on added lines of sandbox..dev, read with git as swgemu). The
             model lists typos, grammar and inconsistent names; nothing is changed by it.
  bot-gaps   Every BLOCKED, NO_EFFECT, FAIL or failed check in Bot-reports/*/*.json, de-duplicated (numbers and ids
             masked), with how often and when last seen. The model names the missing feature or bug behind each note,
             so the report lists gaps by feature instead of 381 raw lines.
Both are drafts by an 8B model: Claude or ChatGPT checks an item before acting on it.
"""
import hashlib
import json
import re
import subprocess
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUTPUTS = HERE.parents[2]
sys.path.insert(0, str(OUTPUTS / 'tools'))
CLIENT = OUTPUTS / 'SWG-client'
OURS = 'local_planets.tre'
CORE3_DEV = '/opt/swg/Core3-dev'
PER_CHUNK = 40

INSTRUCTIONS = {
    'proofread': """You proofread player-facing text for a Star Wars Galaxies game server (US English, pre-CU era).
Each input line is "<id>\t<text>". Report only real problems: spelling mistakes, grammar, wrong or missing punctuation,
doubled words, wrong capitalisation, a name spelled two different ways, text that is cut off or has leftover
placeholders or markup. Star Wars names (planets, species, creatures, characters, invented NPC and place names) are
correct as written unless the same name is spelled differently elsewhere in the input. Don't rewrite style or tone.
Answer with JSON only: {"items": [{"id": "<id exactly as given>", "problem": "<short>", "fix": "<corrected text>"}]}.
If nothing is wrong: {"items": []}.""",
    'bot-gaps': """You sort test notes from automated bot tests on a Star Wars Galaxies emulator test server.
Each input line is "<id>\t<group>\t<count>x\t<last seen>\t<note>". For every line, name what is missing or broken
behind it, in 3-8 words (for example "mission terminal not reachable", "bot cannot open trade window",
"leash follow stops early"), and say whose problem it is:
- "body": the bot client lacks a feature (it can't see, click, trade, craft...);
- "server": the game server behaves wrong or lacks something;
- "scenario": the test script checks the wrong thing or looks in the wrong place;
- "staging": the test setup failed (missing item, wrong place, target out of range, inventory full);
- "unclear".
Use the same words for the same problem so lines group together. Answer with JSON only:
{"items": [{"id": "<id exactly as given>", "gap": "<3-8 words>", "kind": "body|server|scenario|staging|unclear"}]}.""",
}


def chunk_lines(lines, size=PER_CHUNK):
    """[(id, text)] -> chunk dicts with stable ids (a hash of their content), so reruns reuse finished answers."""
    out = []
    for start in range(0, len(lines), size):
        part = lines[start:start + size]
        text = '\n'.join(f'{i}\t{t}' for i, t in part)
        out.append({'id': hashlib.sha1(text.encode('utf-8')).hexdigest()[:16], 'text': text})
    return out


# ------------------------------------------------------------------ proofread

def archive_strings():
    """[(id, text)] for strings in our test archive that are new or changed against every other client archive."""
    from swgfmt import fmt_tools, swg_tables
    ours = CLIENT / OURS
    if not ours.exists():
        return []

    def stf(path, entry):
        with open(path, 'rb') as f:
            f.seek(entry['offset'])
            blob = f.read(entry['comp_size'] if entry['comp'] else entry['size'])
        return dict(swg_tables.stf_items(swg_tables.read_stf(fmt_tools._inflate(blob, entry['comp'], entry['size']))))

    entries = {e['name']: e for e in fmt_tools.read_tre(str(ours)) if e['name'].endswith('.stf')}
    others = [p for p in fmt_tools.walk_tres(str(CLIENT)) if Path(p).name.lower() != OURS]
    stock = defaultdict(dict)   # name -> {key: text} from every other archive, later (higher priority) ones winning
    for archive in others:
        try:
            listing = {e['name']: e for e in fmt_tools.read_tre(archive)}
        except (OSError, ValueError):
            continue
        for name in entries.keys() & listing.keys():
            try:
                stock[name].update(stf(archive, listing[name]))
            except Exception:   # an empty or damaged entry in someone else's archive: nothing to compare against
                continue
    lines = []
    for name, entry in sorted(entries.items()):
        for key, text in stf(str(ours), entry).items():
            if text.strip() and stock[name].get(key) != text and re.search(r'[A-Za-z]{2}', text):
                lines.append((f'{name.removeprefix("string/en/")}:{key}', ' '.join(text.split())))
    return lines


LITERAL = re.compile(r'"((?:[^"\\]|\\.)*)"')   # every literal, in order, so short ones keep their quotes paired
NOT_PLAYER_FACING = ('/src/client/', '/Agent')   # the bot client, and the test galaxy's agent-only staff commands


def server_strings():
    """[(id, text)] for message-like string literals on lines added to Core3-dev since the live branch."""
    command = ['git', '-C', CORE3_DEV, 'diff', '-U0', 'sandbox..dev', '--', '*.lua', '*.h', '*.cpp']
    if sys.platform == 'win32':
        command = ['wsl', '-d', 'Debian', '-u', 'swgemu', '--exec'] + command
    try:
        diff = subprocess.run(command, capture_output=True, text=True, errors='replace', timeout=300).stdout
    except (OSError, subprocess.SubprocessError):
        return []
    seen, lines, path = set(), [], '?'
    for line in diff.splitlines():
        if line.startswith('+++ '):
            full = '/' + line[6:]
            path = None if any(part in full for part in NOT_PLAYER_FACING) else full.rsplit('/', 1)[-1]
            continue
        if path is None or not line.startswith('+') or line.startswith('+++'):
            continue
        for text in LITERAL.findall(line):
            text = text.replace('\\"', '"').replace('\\n', ' ').strip()
            words = re.findall(r"[A-Za-z][A-Za-z']+", text)
            if (len(text) < 12 or ' ' not in text or len(words) < 3 or '/' in text.split()[0]
                    or text.startswith(('@', 'object/', 'SELECT', 'UPDATE')) or text in seen):
                continue
            seen.add(text)
            lines.append((f'{path}:{len(lines) + 1}', ' '.join(text.split())))
    return lines


# ------------------------------------------------------------------ bot gaps

MASK = re.compile(r'\b0x[0-9a-f]+\b|\b\d+(?:\.\d+)?\b', re.I)


def bot_notes(root=OUTPUTS / 'Bot-reports'):
    """[(id, line)] of de-duplicated problem notes from the bots' JSON reports, newest first."""
    seen = {}
    for report in sorted(Path(root).glob('*/*.json')):
        try:
            data = json.loads(report.read_text(encoding='utf-8'))
        except (OSError, ValueError):
            continue
        if not isinstance(data, dict):
            continue
        group = report.parent.name
        when = datetime.fromtimestamp(report.stat().st_mtime).strftime('%m/%d %H:%M')
        found = []
        for note in data.get('notes') or []:
            if isinstance(note, str) and re.match(r'\s*(BLOCKED|NO_EFFECT|FAIL)', note):
                found.append(note)
        for check in data.get('checks') or []:
            if isinstance(check, dict) and check.get('ok') is False:
                found.append(f'FAIL: {check.get("label", "?")}: {str(check.get("detail", ""))[:160]}')
        for row in data.get('results') or []:   # class-check reports
            if isinstance(row, dict) and str(row.get('verdict', '')).upper() in ('BLOCKED', 'NO_EFFECT', 'FAIL'):
                found.append(f'{row["verdict"]}: {row.get("ability", "?")}: {str(row.get("reason") or "")[:160]}')
        for note in found:
            text = ' '.join(note.split())[:240]
            key = (group, MASK.sub('#', text.lower()))
            entry = seen.setdefault(key, {'group': group, 'text': text, 'count': 0, 'last': when})
            entry['count'] += 1
            entry['last'] = max(entry['last'], when)
    rows = sorted(seen.values(), key=lambda e: (e['last'], e['count']), reverse=True)
    return [(f'g{n}', f'{e["group"]}\t{e["count"]}x\t{e["last"]}\t{e["text"]}') for n, e in enumerate(rows, 1)]


# ------------------------------------------------------------------ prepare / report

def prepare(job, folder):
    folder.mkdir(parents=True, exist_ok=True)
    lines = archive_strings() + server_strings() if job == 'proofread' else bot_notes()
    chunks = chunk_lines(lines)
    (folder / 'input.jsonl').write_text(''.join(json.dumps(c, ensure_ascii=False) + '\n' for c in chunks),
                                        encoding='utf-8')
    (folder / 'instruction.txt').write_text(INSTRUCTIONS[job] + '\n', encoding='utf-8')
    (folder / 'lines.json').write_text(json.dumps(dict(lines), indent=1, ensure_ascii=False), encoding='utf-8')
    return len(lines), len(chunks)


def answers(folder):
    """Items from answers to the chunks of the current input only: a rerun of prepare renumbers the lines, so an
    answer to an older chunk (another id, as chunk ids hash their text) would point at the wrong line."""
    current = {json.loads(line)['id'] for line in (folder / 'input.jsonl').read_text(encoding='utf-8').splitlines()
               if line.strip()}
    out = []
    results = folder / 'results.jsonl'
    for line in (results.read_text(encoding='utf-8').splitlines() if results.exists() else []):
        try:
            record = json.loads(line)
            if record['id'] not in current:
                continue
            items = record['answer'].get('items') or []
        except (ValueError, KeyError, AttributeError):
            continue
        out += [i for i in items if isinstance(i, dict) and isinstance(i.get('id'), str)]
    return out


def cell(text, cap):
    """One Markdown table cell: one line, capped, pipes escaped."""
    return ' '.join(str(text).split())[:cap].replace('|', r'\|')


def report(job, folder):
    lines = json.loads((folder / 'lines.json').read_text(encoding='utf-8'))
    items = [i for i in answers(folder) if i['id'] in lines]   # drop ids the model made up
    head = (f'# Local model: {job} (draft)\n\nWritten by the local model through `tools/agents/local/local_jobs.py`; '
            f'{len(lines)} input lines. An 8B model\'s draft: check each item before acting on it.\n\n')
    if job == 'proofread':
        body = '| String | Text now | Problem | Suggested |\n|---|---|---|---|\n' + ''.join(
            f'| `{i["id"]}` | {cell(lines[i["id"]], 140)} | {cell(i.get("problem", ""), 80)} | {cell(i.get("fix", ""), 140)} |\n'
            for i in sorted(items, key=lambda i: i['id']) if str(i.get('fix', '')).strip() != lines[i['id']].strip())
    else:
        groups = defaultdict(list)
        for i in items:
            groups[(str(i.get('kind', 'unclear')).lower(), str(i.get('gap', '?')).strip().lower())].append(i['id'])
        body = ''
        for kind in ('body', 'server', 'scenario', 'staging', 'unclear'):
            rows = sorted(((gap, ids) for (k, gap), ids in groups.items() if k == kind),
                          key=lambda r: -sum(int(lines[i].split('\t')[1].rstrip('x')) for i in r[1]))
            if not rows:
                continue
            body += f'\n## {kind}\n\n| Gap | Notes | Seen | Last | Example |\n|---|---|---|---|---|\n'
            for gap, ids in rows:
                parts = [lines[i].split('\t') for i in ids]
                seen = sum(int(p[1].rstrip('x')) for p in parts)
                body += f'| {cell(gap, 60)} | {len(ids)} | {seen}x | {max(p[2] for p in parts)} | {cell(parts[0][3], 120)} |\n'
    (folder / 'report.md').write_text(head + (body or 'Nothing found.\n'), encoding='utf-8', newline='\n')
    return len(items)


def main():
    if len(sys.argv) != 4 or sys.argv[1] not in ('prepare', 'report') or sys.argv[2] not in INSTRUCTIONS:
        print(__doc__)
        return 2
    folder = Path(sys.argv[3])
    if sys.argv[1] == 'prepare':
        lines, chunks = prepare(sys.argv[2], folder)
        print(f'{sys.argv[2]}: {lines} lines in {chunks} chunks')
    else:
        print(f'{sys.argv[2]}: {report(sys.argv[2], folder)} items in report.md')
    return 0


if __name__ == '__main__':
    sys.exit(main())
