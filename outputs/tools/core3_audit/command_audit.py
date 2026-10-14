"""Which Core3 slash commands actually do something? Read-only audit of the dev tree's command code. (Claude, 14 Oct 2026.)

Inside Debian (reads /opt/swg/Core3-dev, writes only the two outputs below):
    python3 -I /mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/tools/core3_audit/command_audit.py

For every command registered in CommandConfigManager*.cpp it reads the class's doQueueCommand() and classifies it:
  stub         the body is only the standard state/locomotion checks and `return SUCCESS` (the server accepts the
               command and does nothing)
  not-impl     it only tells the player it isn't implemented
  base-class   it hands over to a shared engine (combat, Jedi, force heal, squad leader, ...) whose data lives in lua
  inherits     the class has no doQueueCommand of its own
  todo         real code, but the source carries a TODO/FIXME/"not implemented" note
  implemented  real code
It also lists who gets each command: the client's skills.iff COMMANDS column (professions, and the staff skills such
as admin_base) and the staff levels in bin/scripts/staff/levels/*.lua.
Static reading only: "implemented" means there is code, not that the code was tested in game.

Outputs: outputs/Documentation-support/core3-command-audit.md and outputs/tools/core3_audit/command_audit.json.
"""
import collections, glob, json, os, re, sys

CORE = '/opt/swg/Core3-dev/MMOCoreORB'
CMD_DIR = f'{CORE}/src/server/zone/objects/creature/commands'
HERE = os.path.dirname(os.path.abspath(__file__))
OUT_MD = os.path.join(HERE, '..', '..', 'Documentation-support', 'core3-command-audit.md')
OUT_JSON = os.path.join(HERE, 'command_audit.json')
sys.path.insert(0, os.path.join(HERE, '..', 'owner_content'))

ENGINE_CALLS = {
    'doCombatAction': 'combat', 'doJediSelfBuffCommand': 'jedi buff', 'doJediCombatAction': 'jedi combat',
    'runCommand': 'force heal', 'doHealing': 'healing', 'doSquadLeaderCommand': 'squad leader',
    'doForcePower': 'force power',
}
BOILERPLATE = [
    r'if\s*\(\s*!\s*checkStateMask\s*\(\s*creature\s*\)\s*\)\s*\{?\s*return\s+INVALIDSTATE\s*;\s*\}?',
    r'if\s*\(\s*!\s*checkInvalidLocomotions\s*\(\s*creature\s*\)\s*\)\s*\{?\s*return\s+INVALIDLOCOMOTION\s*;\s*\}?',
    r'return\s+SUCCESS\s*;',
]


def strip_comments(text):
    text = re.sub(r'/\*.*?\*/', ' ', text, flags=re.S)
    return re.sub(r'//[^\n]*', ' ', text)


def method_body(text, name):
    """Body text of `int name(` ... { ... } or None."""
    m = re.search(r'\b' + name + r'\s*\([^)]*\)\s*(const)?\s*\{', text)
    if not m:
        return None
    i, depth = m.end() - 1, 0
    for j in range(i, len(text)):
        depth += {'{': 1, '}': -1}.get(text[j], 0)
        if depth == 0:
            return text[i + 1:j]
    return None


def classify(path):
    raw = open(path, encoding='utf-8', errors='replace').read()
    base = re.search(r'class\s+\w+\s*:\s*public\s+(\w+)', raw)
    base = base[1] if base else '?'
    todo = bool(re.search(r'TODO|FIXME|not (yet )?implemented|unimplemented', raw, re.I))
    code = strip_comments(raw)
    body = method_body(code, 'doQueueCommand')
    if body is None:
        return 'inherits', base, todo, ''
    rest = body
    for pat in BOILERPLATE:
        rest = re.sub(pat, ' ', rest)
    rest = re.sub(r'\s+', ' ', rest).strip()
    if rest in ('', '{}', '{ }'):
        return 'stub', base, todo, ''
    if re.fullmatch(r'(creature|player)->sendSystemMessage\([^;]*\);\s*(return \w+;)?', rest) and \
            re.search(r'implement|not (yet )?(available|supported)|disabled', rest, re.I):
        return 'not-impl', base, todo, rest[:120]
    for call, engine in ENGINE_CALLS.items():
        if re.fullmatch(r'.{0,400}return\s+' + call + r'\s*\(.*', rest) and rest.count(';') <= 6:
            return 'base-class', base, todo, engine
    return ('todo' if todo else 'implemented'), base, todo, ''


def registry():
    reg = {}
    for f in glob.glob(f'{CORE}/src/server/zone/managers/objectcontroller/command/CommandConfigManager*.cpp'):
        for cls, name in re.findall(r'registerCommand<(\w+)>\(String\("([^"]+)"\)', open(f, encoding='utf-8', errors='replace').read()):
            reg[name.lower()] = cls
    return reg


def staff_levels():
    levels = {}
    for f in glob.glob(f'{CORE}/bin/scripts/staff/levels/*.lua'):
        t = open(f, encoding='utf-8', errors='replace').read()
        name = re.search(r'name\s*=\s*"([^"]+)"', t)
        lvl = re.search(r'level\s*=\s*(\d+)', t)
        if name:
            levels[name[1]] = (int(lvl[1]) if lvl else None, re.findall(r'"(admin_[a-z0-9_]+)"', t))
    return levels


def grants():
    """command -> skills that grant it, from the client's skills.iff."""
    try:
        import swg_client_data as c
        rows = c.datatable(c.client_file('datatables/skill/skills.iff'))
    except Exception as e:  # the client archives are readable from WSL through /mnt/c
        print(f'skills.iff not read: {e}')
        return {}
    out = collections.defaultdict(list)
    for r in rows:
        for cmd in (r.get('COMMANDS') or '').split(','):
            if cmd.strip():
                out[cmd.strip().lower()].append(r['NAME'])
    # Staff skills are not in skills.iff: Core3 adds them from lua (SkillManager::loadFromLua, scripts/skills/).
    for f in glob.glob(f'{CORE}/bin/scripts/skills/**/*.lua', recursive=True):
        t = open(f, encoding='utf-8', errors='replace').read()
        name = re.search(r'skillName\s*=\s*"([^"]+)"', t)
        block = re.search(r'commands\s*=\s*\{(.*?)\}', t, re.S)
        if name and block:
            for cmd in re.findall(r'"([^"]+)"', block[1]):
                out[cmd.lower()].append(name[1])
    return out


def who(skills):
    if not skills:
        return 'no skill grants it'
    staff = sorted({s for s in skills if s.startswith('admin_')})
    other = [s for s in skills if not s.startswith('admin_')]
    parts = []
    if staff:
        parts.append('staff: ' + ', '.join(staff))
    if other:
        parts.append(f'{len(other)} skill box(es), e.g. ' + ', '.join(other[:3]))
    return '; '.join(parts)


def main():
    reg, levels, granted = registry(), staff_levels(), grants()
    files = {os.path.basename(p)[:-2]: p for p in glob.glob(f'{CMD_DIR}/**/*.h', recursive=True)}
    rows = []
    for name, cls in sorted(reg.items()):
        path = files.get(cls)
        if not path:
            rows.append(dict(command=name, cls=cls, status='no-source', base='?', todo=False, note='class header not found'))
            continue
        status, base, todo, note = classify(path)
        rows.append(dict(command=name, cls=cls, status=status, base=base, todo=todo, note=note,
                         file=os.path.relpath(path, CORE), granted_by=granted.get(name, [])))
    unregistered = sorted(set(files) - set(reg.values()) - {'QueueCommand', 'CombatQueueCommand'})
    json.dump(dict(rows=rows, staff_levels={k: dict(level=v[0], skills=v[1]) for k, v in levels.items()},
                   unregistered_classes=unregistered), open(OUT_JSON, 'w'), indent=1)

    count = collections.Counter(r['status'] for r in rows)
    staff_cmds = [r for r in rows if any(s.startswith('admin_') for s in r.get('granted_by', []))]
    lines = ['# Core3 slash commands: what has code and what does not', '',
             'Generated by `tools/core3_audit/command_audit.py` (Claude, 14 Oct 2026) from `/opt/swg/Core3-dev`. '
             'Static reading of each command\'s `doQueueCommand()`: "implemented" means there is real code, not that '
             'it was tested in game. Owner, 14 Oct: "we may need to look at the core3 files and figure out what actually works".', '',
             f'**{len(rows)} registered commands:** ' + ', '.join(f'{k} {v}' for k, v in count.most_common()) + '.', '',
             '| Status | Meaning |', '|---|---|',
             '| stub | Accepted by the server and does nothing (only the standard checks and `return SUCCESS`) |',
             '| not-impl | Only tells the player it isn\'t implemented |',
             '| base-class | Hands over to a shared engine (combat, Jedi, healing, squad leader); its numbers live in lua |',
             '| inherits | No command code of its own; the parent class does the work |',
             '| todo | Real code with a TODO/FIXME/"not implemented" note in the source |',
             '| implemented | Real code |', '',
             '**Read "stub" with care.** It means the slash-command handler is empty, not that the feature is missing. '
             'Many player features run through other routes: the client sends its own message packets (auctions, logout, '
             'crafting sessions), or the action runs from a radial menu or by using the object (eating, harvester controls). '
             'For player commands treat a stub as "check in game". The staff stubs are the meaningful list: those are admin '
             'tools that answer and do nothing.', '',
             '## God Mode and staff commands (14 Oct finding)', '',
             '- `/setGodMode <name|self> on|off` toggles the `admin` ability. A command marked admin-only is refused '
             '(`ObjectControllerImplementation.cpp`, "attempted to use ... without permissions" in the admin log) unless the '
             'player has God Mode and that command\'s ability. `/setGodMode` itself is not admin-only and no skill grants it; '
             'it checks for the `admin_base` skill instead.',
             '- God Mode does **not** make you immune. `/invulnerable` does (it clears the PLAYER pvp flag, which combat treats '
             'as invulnerable); `/invulnerable invis` turns invisible.',
             '- "todo" can still be working code: `/goto` is 197 lines with an optimisation TODO.', '',
             '| Staff level | Level | Staff skills |', '|---|---|---|']
    for name, (lvl, skills) in sorted(levels.items(), key=lambda kv: -(kv[1][0] or 0)):
        lines.append(f'| {name} | {lvl} | {", ".join(skills) or "-"} |')
    dead = [r for r in staff_cmds if r['status'] == 'stub']
    lines += ['', f'### Staff commands ({len(staff_cmds)})', '',
              f'**{len(dead)} of the {len(staff_cmds)} staff commands are stubs:** the server accepts them and nothing happens. '
              'Stubs and TODOs are listed first.', '',
              '| Command | Status | Granted by | Note |', '|---|---|---|---|']
    for r in sorted(staff_cmds, key=lambda r: (r['status'] not in ('stub', 'not-impl', 'todo'), r['command'])):
        lines.append(f"| `/{r['command']}` | {r['status']} | {who(r['granted_by'])} | {r['note']} |")
    for status in ('stub', 'not-impl', 'todo'):
        part = [r for r in rows if r['status'] == status and r not in staff_cmds]
        lines += ['', f'## Player commands: {status} ({len(part)})', '', '| Command | Class | Granted by |', '|---|---|---|']
        lines += [f"| `/{r['command']}` | {r['cls']} | {who(r['granted_by'])} |" for r in part]
    eng = collections.Counter(r['note'] for r in rows if r['status'] == 'base-class')
    lines += ['', '## Commands handled by shared engines', '',
              ', '.join(f'{k}: {v}' for k, v in eng.most_common()) + '.', '',
              f'## Command classes with source but no registration ({len(unregistered)})', '',
              ', '.join(f'`{u}`' for u in unregistered) or '-', '']
    with open(OUT_MD, 'w', encoding='utf-8', newline='\r\n') as f:
        f.write('\n'.join(lines))
    print(f'{len(rows)} commands: {dict(count)}; staff {len(staff_cmds)}; unregistered classes {len(unregistered)}')
    print(f'wrote {OUT_MD} and {OUT_JSON}')


if __name__ == '__main__':
    main()
