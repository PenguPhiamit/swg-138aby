#!/usr/bin/env python3
"""Build the pre-CU class-check map: professions.json, commands.json, matrix.md.

Reads (read-only):
  * the client data tables  datatables/skill/skills.iff  and  datatables/command/command_table*.iff, plus the
    English name tables  string/en/skl_n.stf / cmd_n.stf, through outputs/tools/swgfmt (our own reader);
  * the server source in WSL Debian, /opt/swg/Core3-dev/MMOCoreORB  (command Lua scripts, command C++ headers,
    CommandConfigManager registration, a few engine files for message citations).

It writes ONLY inside its own folder (outputs/Claude-class-check/). It never touches /opt/swg, never starts a
server or a bot, and does not read config-local.lua or anything under /opt/swg/agent.

Which copy of a data table is used: the server's. The archive search order is TreFiles in the public
bin/conf/config.lua (newest first, first hit wins), looked up in outputs/SWG-client. If the live client resolves a file
from a different archive (today local_planets.tre adds outdoors_botanist and species_chiss), the differences are
listed in matrix.md and professions.json meta, and are not part of the counts. Without a readable config.lua (for
example with --src pointing at a partial copy) it falls back to the live client order.

Outputs: professions.json (boxes, closure costs, suggested_builds, proposed_run_order), commands.json (one entry per
ability token granted by a profession box), matrix.md. test-plan.md next to it is written by hand from these.

Run (Windows, from any folder):
    python -I outputs/Claude-class-check/build_matrix.py
    python -I outputs/Claude-class-check/build_matrix.py --src C:/some/MMOCoreORB-copy     # use a local copy instead of WSL
    python -I outputs/Claude-class-check/build_matrix.py --keep-snapshot                   # leave the extracted source in %TEMP%

How the source is read: a small bash script (written to %TEMP%) is run with
`wsl -d Debian -u root -- bash /mnt/c/.../script.sh`; it tars the few source folders we need into a file in %TEMP%
(read-only on the Debian side), and this script unpacks that tar into %TEMP%\\cc_snapshot_<pid>. Line numbers quoted in
the outputs refer to the files as they are in Core3-dev at the commit printed in matrix.md.

Terminology used in the outputs (see the "Rules" section of matrix.md):
  ability   a token in the COMMANDS column of skills.iff; a box "grants" abilities.
  command   a row of command_table*.iff (what the player types: /name). A command is gated by its characterAbility.
  handler   the C++ class registered for a command in CommandConfigManager*.cpp.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time
from collections import Counter, OrderedDict, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUTPUTS = HERE.parent
sys.path.insert(0, str(OUTPUTS / 'tools'))
from swgfmt import trn_iff, swg_tables as st  # noqa: E402

WSL_ROOT = '/opt/swg/Core3-dev/MMOCoreORB'
CMD_H = 'src/server/zone/objects/creature/commands'
CFG_DIR = 'src/server/zone/managers/objectcontroller/command'
LUA_DIR = 'bin/scripts/commands'

STARTERS = ['combat_brawler', 'combat_marksman', 'outdoors_scout', 'science_medic', 'crafting_artisan',
            'social_entertainer']

# ----------------------------------------------------------------------------------------------------------------
# Source access
# ----------------------------------------------------------------------------------------------------------------

SNAP_SCRIPT = r'''#!/bin/bash
# Read-only: tar the folders the class check needs. Writes only to the tar file under /mnt/c (Windows temp).
R=__ROOT__
OUT="__OUT__"
cd "$R" || exit 1
tar -cf "$OUT" --exclude=autogen src/server src/templates src/client/agent bin/scripts/commands bin/scripts/managers bin/scripts/object/weapon bin/scripts/object/tangible/instrument bin/conf/config.lua 2>&1 | head -5
if [ -f "__PATS__" ]; then
  grep -rnoF -f "__PATS__" bin/scripts/object bin/scripts/screenplays --include=*.lua 2>/dev/null | head -40000 > "$OUT.refs"
fi
runuser -u swgemu -- git -C /opt/swg/Core3-dev log -1 --format='%h %ad %s' --date=short > "$OUT.head" 2>&1
runuser -u swgemu -- git -C /opt/swg/Core3-dev rev-parse --abbrev-ref HEAD >> "$OUT.head" 2>&1
'''


def win_to_wsl(p):
    p = str(p).replace('\\', '/')
    m = re.match(r'^([A-Za-z]):/(.*)$', p)
    return '/mnt/%s/%s' % (m.group(1).lower(), m.group(2)) if m else p


def take_snapshot(tokens=()):
    """Returns (folder, git head text, {token: ['file:line', ...]} from a grep of Lua object templates/screenplays)."""
    tmp = Path(tempfile.gettempdir())
    tar_path = tmp / ('cc_snapshot_%d.tar' % os.getpid())
    script = tmp / ('cc_snapshot_%d.sh' % os.getpid())
    pats = tmp / ('cc_snapshot_%d.pats' % os.getpid())
    pats.write_text('\n'.join('"%s"' % t for t in tokens) + '\n', encoding='utf-8', newline='\n')
    script.write_text(SNAP_SCRIPT.replace('__ROOT__', WSL_ROOT).replace('__OUT__', win_to_wsl(tar_path))
                      .replace('__PATS__', win_to_wsl(pats)), encoding='utf-8', newline='\n')
    env = dict(os.environ, MSYS_NO_PATHCONV='1')
    r = subprocess.run(['wsl', '-d', 'Debian', '-u', 'root', '--', 'bash', win_to_wsl(script)],
                       capture_output=True, text=True, env=env, timeout=600)
    if r.returncode != 0 or not tar_path.exists():
        raise SystemExit('snapshot failed: rc=%s %s %s' % (r.returncode, r.stdout[-300:], r.stderr[-300:]))
    dest = tmp / ('cc_snapshot_%d' % os.getpid())
    if dest.exists():
        shutil.rmtree(dest, ignore_errors=True)
    dest.mkdir()
    with tarfile.open(tar_path) as t:
        for member in t.getmembers():
            # plain files and dirs only; names are relative and checked
            if member.isfile() or member.isdir():
                if member.name.startswith('/') or '..' in member.name.split('/'):
                    continue
                t.extract(member, dest)
    head = ''
    hp = Path(str(tar_path) + '.head')
    if hp.exists():
        head = hp.read_text(encoding='utf-8', errors='replace')
    lua_refs = defaultdict(list)
    rp = Path(str(tar_path) + '.refs')
    if rp.exists():
        for line in rp.read_text(encoding='utf-8', errors='replace').splitlines():
            m = re.match(r'^(.*?):(\d+):"(.*)"$', line)
            if m and len(lua_refs[m.group(3)]) < 3:
                lua_refs[m.group(3)].append('bin/scripts/%s:%s' % (m.group(1), m.group(2)))
    for f in (script, tar_path, hp, rp, pats):
        try:
            f.unlink()
        except OSError:
            pass
    return dest, head, lua_refs


class Src:
    """Files of the Core3 source snapshot, with line access for citations."""

    def __init__(self, root):
        self.root = Path(root)
        self._cache = {}

    def path(self, rel):
        return self.root / rel

    def exists(self, rel):
        return self.path(rel).exists()

    def text(self, rel):
        if rel not in self._cache:
            self._cache[rel] = self.path(rel).read_text(encoding='latin-1')
        return self._cache[rel]

    def lines(self, rel):
        return self.text(rel).split('\n')

    def find_line(self, rel, needle, start=0):
        """1-based line number of the first line at/after `start` (1-based) containing needle, or None."""
        for i, line in enumerate(self.lines(rel)[max(start - 1, 0):], start=max(start, 1)):
            if needle in line:
                return i
        return None

    def listdir(self, rel):
        p = self.path(rel)
        return sorted(os.listdir(p)) if p.exists() else []


# ----------------------------------------------------------------------------------------------------------------
# Skills table
# ----------------------------------------------------------------------------------------------------------------

DATA_FILES = [('skills', 'datatables/skill/skills.iff'), ('cmd_shared', 'datatables/command/command_table.iff'),
              ('cmd_ground', 'datatables/command/command_table_ground.iff'),
              ('cmd_space', 'datatables/command/command_table_space.iff'), ('skl_n', 'string/en/skl_n.stf'),
              ('cmd_n', 'string/en/cmd_n.stf')]


def parse_tre_files(src):
    """TreFiles from the server's public config.lua (never config-local.lua): newest archive first, first hit wins."""
    rel = 'bin/conf/config.lua'
    if not src.exists(rel):
        return None
    t = strip_lua_comments(src.text(rel))
    m = re.search(r'TreFiles\s*=\s*\{(.*?)\}', t, re.S)
    return re.findall(r'"([^"]+)"', m.group(1)) if m else None


def server_file(name, order):
    """(bytes, archive) from the first archive in the server's TreFiles order that holds `name`, or (None, None)."""
    for arch in order or []:
        path = os.path.join(trn_iff.CLIENT, arch)
        if os.path.exists(path):
            data = trn_iff.open_tre_entry(path, name)
            if data is not None:
                return data, arch
    return None, None


def load_tables(order=None):
    """Tables as the live client resolves them (order=None) or as the server's TreFiles order resolves them."""
    idx = trn_iff.client_index()
    t = {'archives': OrderedDict(), 'client_archives': OrderedDict()}
    for key, name in DATA_FILES:
        data, arch = (None, None)
        if order:
            data, arch = server_file(name, order)
        if data is None:
            data, arch = trn_iff.client_file(name), idx.get(name)
        if data is None:
            raise SystemExit('data file not found: ' + name)
        t['archives'][name] = arch
        t['client_archives'][name] = idx.get(name)
        if name.endswith('.iff'):
            t[key] = st.dtii_dicts(st.read_dtii(data))
        else:
            t[key] = dict(st.stf_items(st.read_stf(data)))
    return t


def table_differences(a, b):
    """Rows (skills by NAME, commands by commandName) present in a but not b, or changed. a = client, b = server order."""
    out = OrderedDict()
    for key, col in (('skills', 'NAME'), ('cmd_shared', 'commandName'), ('cmd_ground', 'commandName'), ('cmd_space', 'commandName')):
        bm, am = defaultdict(list), defaultdict(list)   # a few names appear twice in one table
        for r in b[key]:
            bm[r[col]].append(r)
        for r in a[key]:
            am[r[col]].append(r)
        added = [n for n in am if n not in bm]
        changed = [n for n in am if n in bm and am[n] != bm[n]]
        removed = [n for n in bm if n not in am]
        if added or changed or removed:
            out[key] = OrderedDict([('only_in_client_archive', added), ('changed_in_client_archive', changed),
                                    ('only_in_server_order', removed)])
    return out


def csv(s):
    return [x for x in (s or '').split(',') if x]


def parse_mods(s):
    out = OrderedDict()
    for part in csv(s):
        k, _, v = part.partition('=')
        try:
            out[k] = int(v)
        except ValueError:
            try:
                out[k] = float(v)
            except ValueError:
                out[k] = v
    return out


def build_professions(tables):
    rows = tables['skills']
    by = {r['NAME']: r for r in rows}
    names = tables['skl_n']

    def profession_of(r):
        seen = set()
        while r is not None:
            if r['IS_PROFESSION']:
                return r['NAME']
            if r['NAME'] in seen:
                return None
            seen.add(r['NAME'])
            r = by.get(r['PARENT'])
        return None

    def box(r):
        prereq = csv(r['SKILLS_REQUIRED'])
        return OrderedDict([
            ('name', r['NAME']),
            ('english_name', names.get(r['NAME'], '')),
            ('parent', r['PARENT']),
            ('is_title', bool(r['IS_TITLE'])),
            ('hidden', bool(r['IS_HIDDEN'])),
            ('god_only', bool(r['GOD_ONLY'])),
            ('prerequisites', prereq),
            ('prerequisites_required_count', r['SKILLS_REQUIRED_COUNT']),
            ('preclusions', csv(r['PRECLUSION_SKILLS'])),
            ('skill_points', r['POINTS_REQUIRED']),
            ('money_cost', r['MONEY_REQUIRED']),
            ('xp_type', r['XP_TYPE']),
            ('xp_cost', r['XP_COST']),
            ('xp_cap', r['XP_CAP']),
            ('missions_required', r['MISSIONS_REQUIRED']),
            ('apprenticeships_required', r['APPRENTICESHIPS_REQUIRED']),
            ('stats_required', r['STATS_REQUIRED']),
            ('species_required', r['SPECIES_REQUIRED']),
            ('jedi_state_required', r['JEDI_STATE_REQUIRED']),
            ('skill_ability', r['SKILL_ABILITY']),
            ('abilities', csv(r['COMMANDS'])),
            ('skill_mods', parse_mods(r['SKILL_MODS'])),
            ('schematics_granted', csv(r['SCHEMATICS_GRANTED'])),
            ('schematics_revoked', csv(r['SCHEMATICS_REVOKED'])),
        ])

    categories = {r['NAME']: r for r in rows if r['PARENT'] == '' and not r['IS_PROFESSION']}
    professions = OrderedDict()
    skipped = []
    for r in rows:
        if r['IS_PROFESSION']:
            cat = r['PARENT']
            if r['NAME'] in STARTERS:
                tier = 'starter'
            elif cat in ('jedi', 'force_sensitive', 'force_discipline', 'force_rank', 'force_title'):
                tier = 'jedi_force'
            elif cat in ('pilot', 'shipwright'):
                tier = 'space'
            else:
                tier = 'elite'
            professions[r['NAME']] = OrderedDict([
                ('name', r['NAME']),
                ('english_name', names.get(r['NAME'], '')),
                ('category', cat),
                ('tier', tier),
                ('god_only', bool(r['GOD_ONLY'])),
                ('profession_row_abilities', csv(r['COMMANDS'])),
                ('boxes', []),
            ])
    for r in rows:
        p = profession_of(r)
        if p is None:
            continue
        if r['IS_PROFESSION']:
            continue
        professions[p]['boxes'].append(box(r))
    # branch/ordering metadata: depth in the prerequisite chain
    for p in professions.values():
        for b in p['boxes']:
            b['kind'] = ('novice' if b['name'].endswith('_novice') else
                         'master' if b['name'].endswith('_master') else 'branch')
        p['box_count'] = len(p['boxes'])
    # skipped = everything with no profession ancestor
    for r in rows:
        if profession_of(r) is not None:
            continue
        n = r['NAME']
        if n.startswith('social_language'):
            reason = 'species language (speak/comprehend skill)'
        elif n.startswith('species_'):
            reason = 'species innate skill (granted at character creation, not trainable)'
        elif n in categories or r['PARENT'] == '':
            reason = ('category/root node, not a profession' if r['GOD_ONLY'] else
                      'baseline/demo root skill with no profession' + ('' if csv(r['COMMANDS']) else ' and no abilities'))
        elif n.startswith('utility'):
            reason = 'utility/demo placeholder skill'
        elif n.startswith('pilot_spacetest'):
            reason = 'space test placeholder skill'
        else:
            reason = 'no profession ancestor in skills.iff'
        skipped.append(OrderedDict([('name', n), ('english_name', names.get(n, '')), ('parent', r['PARENT']),
                                    ('reason', reason), ('abilities', csv(r['COMMANDS']))]))
    return professions, skipped


# ----------------------------------------------------------------------------------------------------------------
# Command tables
# ----------------------------------------------------------------------------------------------------------------

LOCO_COLS = ['standing', 'sneaking', 'walking', 'running', 'kneeling', 'crouchSneaking', 'crouchWalking', 'prone',
             'crawling', 'climbingStationary', 'climbing', 'hovering', 'flying', 'lyingDown', 'sitting',
             'skillAnimating', 'drivingVehicle', 'ridingCreature', 'knockedDown', 'incapacitated', 'dead',
             'blocking']
TARGET_TYPE = {0: 'none', 1: 'required', 2: 'optional'}


def command_row_summary(src_name, r):
    inv_loco = [c for c in LOCO_COLS if not r.get('L:' + c, 1)]
    inv_state = [k[2:] for k in r if k.startswith('S:') and not r[k]]
    return OrderedDict([
        ('table', src_name),
        ('command_name', r['commandName']),
        ('character_ability', r['characterAbility']),
        ('default_priority', r['defaultPriority']),
        ('default_time', r['defaultTime']),
        ('target_type', r['targetType']),
        ('target_type_label', TARGET_TYPE.get(r['targetType'], '?')),
        ('max_range_to_target', r['maxRangeToTarget']),
        ('add_to_combat_queue', bool(r.get('addToCombatQueue', 0))),
        ('command_group', r['commandGroup'] & 0xFFFFFFFF),
        ('disabled_column', bool(r['disabled'])),
        ('god_level', r['godLevel']),
        ('allowed_postures', [lbl for lbl, col in (('standing', 'standing'), ('kneeling', 'kneeling'), ('prone', 'prone'),
                                                    ('sitting', 'sitting')) if r.get('L:' + col, 1)]),
        ('invalid_locomotions', inv_loco),
        ('invalid_states', inv_state),
    ])


def index_commands(tables):
    """lowercase command name -> list of (table name, row). Order matters: the server loads shared, ground, space."""
    by_name = defaultdict(list)
    for tname, key in (('shared', 'cmd_shared'), ('ground', 'cmd_ground'), ('space', 'cmd_space')):
        for r in tables[key]:
            by_name[r['commandName'].strip().lower()].append((tname, r))
    return by_name


# ----------------------------------------------------------------------------------------------------------------
# Lua command scripts
# ----------------------------------------------------------------------------------------------------------------

def strip_lua_comments(t):
    t = re.sub(r'--\[\[.*?\]\]', lambda m: '\n' * m.group(0).count('\n'), t, flags=re.S)
    out = []
    for line in t.split('\n'):
        # drop "-- comment" outside of strings (scripts here do not put '--' inside strings)
        in_s = None
        cut = None
        i = 0
        while i < len(line):
            c = line[i]
            if in_s:
                if c == '\\':
                    i += 1
                elif c == in_s:
                    in_s = None
            else:
                if c in '"\'':
                    in_s = c
                elif line.startswith('--', i):
                    cut = i
                    break
            i += 1
        out.append(line if cut is None else line[:cut])
    return '\n'.join(out)


def split_top(s, sep=','):
    parts, depth, cur, in_s = [], 0, [], None
    i = 0
    while i < len(s):
        c = s[i]
        if in_s:
            cur.append(c)
            if c == '\\' and i + 1 < len(s):
                i += 1
                cur.append(s[i])
            elif c == in_s:
                in_s = None
        elif c in '"\'':
            in_s = c
            cur.append(c)
        elif c in '({[':
            depth += 1
            cur.append(c)
        elif c in ')}]':
            depth -= 1
            cur.append(c)
        elif c == sep and depth == 0:
            parts.append(''.join(cur))
            cur = []
        else:
            cur.append(c)
        i += 1
    tail = ''.join(cur)
    if tail.strip():
        parts.append(tail)
    return parts


def match_brace(t, start):
    depth, in_s, i = 0, None, start
    while i < len(t):
        c = t[i]
        if in_s:
            if c == '\\':
                i += 1
            elif c == in_s:
                in_s = None
        elif c in '"\'':
            in_s = c
        elif c == '{':
            depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0:
                return i
        i += 1
    return len(t) - 1


def lua_scalar(v):
    v = v.strip()
    if len(v) >= 2 and v[0] in '"\'' and v[-1] == v[0]:
        return v[1:-1]
    if v in ('true', 'false'):
        return v == 'true'
    try:
        return int(v)
    except ValueError:
        pass
    try:
        return float(v)
    except ValueError:
        pass
    return re.sub(r'\s+', ' ', v)


def lua_call_args(v):
    m = re.match(r'^\s*(\w+)\s*\((.*)\)\s*$', v, re.S)
    if not m:
        return None, None
    return m.group(1), [re.sub(r'\s+', ' ', a.strip()) for a in split_top(m.group(2))]


def parse_lua_command(text):
    """Returns a list of dicts (one per table that has a `name`), each: {'var', 'fields': OrderedDict, 'line'}."""
    t = strip_lua_comments(text)
    out = []
    for m in re.finditer(r'^\s*(\w+)\s*=\s*\{', t, re.M):
        start = t.index('{', m.start())
        end = match_brace(t, start)
        body = t[start + 1:end]
        fields = OrderedDict()
        for part in split_top(body):
            mm = re.match(r'^\s*(\w+)\s*=\s*(.*)$', part, re.S)
            if mm:
                fields[mm.group(1)] = mm.group(2).strip()
        if 'name' in fields:
            out.append({'var': m.group(1), 'fields': fields, 'line': t[:m.start()].count('\n') + 1})
    return out


EFFECT_ARGS = ['effect', 'defender_exclusion_timers', 'defender_state_defense_mods', 'defender_jedi_mods',
               'chance', 'strength', 'length']


def summarize_effects(raw):
    """stateEffects = { StateEffect(...), ... } -> list of short dicts."""
    inner = raw.strip()
    if inner.startswith('{') and inner.endswith('}'):
        inner = inner[1:-1]
    res = []
    for part in split_top(inner):
        fn, args = lua_call_args(part)
        if fn == 'StateEffect' and args:
            d = OrderedDict(zip(EFFECT_ARGS, args))
            res.append(OrderedDict([('effect', d.get('effect')), ('chance', lua_scalar(d.get('chance', '0'))),
                                    ('strength', lua_scalar(d.get('strength', '0'))),
                                    ('length', lua_scalar(d.get('length', '0')))]))
        elif fn == 'DotEffect' and args:
            keys = ['dot_type', 'defender_state_defense_mods', 'pool', 'hit_damage', 'potency', 'chance', 'strength',
                    'duration', 'primary_percent', 'secondary_percent']
            d = OrderedDict(zip(keys, args))
            res.append(OrderedDict([('dot', d.get('dot_type')), ('pool', d.get('pool')), ('chance', lua_scalar(d.get('chance', '0'))),
                                    ('strength', lua_scalar(d.get('strength', '0'))),
                                    ('duration', lua_scalar(d.get('duration', '0')))]))
    return res


# fields worth keeping from a Lua script (parseVariableData in CommandConfigManager.cpp lists all that are read)
LUA_KEEP = ['cooldown', 'cooldownString', 'targetType', 'disabled', 'maxRangeToTarget', 'addToCombatQueue',
            'characterAbility', 'defaultPriority', 'defaultTime', 'invalidStateMask', 'invalidLocomotions',
            'forceAttack', 'damageMultiplier', 'accuracyBonus', 'speedMultiplier', 'minDamage', 'maxDamage',
            'damageType', 'speed', 'poolsToDamage', 'weaponType', 'healthCostMultiplier', 'actionCostMultiplier',
            'mindCostMultiplier', 'forceCostMultiplier', 'forceCost', 'visMod', 'coneRange', 'range',
            'accuracySkillMod', 'areaAction', 'splashDamage', 'coneAction', 'coneAngle', 'areaRange', 'combatSpam',
            'animation', 'effectString', 'trails', 'action', 'buffClass', 'duration', 'clientEffect', 'speedMod',
            'healAmount', 'healWoundAmount', 'attributesToHeal', 'woundAttributesToHeal', 'healBleedingCost',
            'healFireCost', 'healDiseaseCost', 'healPoisonCost', 'healBattleFatigue', 'healStateCost',
            'statesToHeal', 'bleedHealIterations', 'poisonHealIterations', 'diseaseHealIterations',
            'fireHealIterations', 'allowedTarget']


def load_lua_scripts(src):
    """Reads commands.lua (which files run) and every script. Returns dict with by_name and registration checks."""
    listed = re.findall(r'RunSlashCommandsFile\("([^"]+)"\)', src.text(LUA_DIR + '/commands.lua'))
    files = [f for f in src.listdir(LUA_DIR) if f.endswith('.lua') and f != 'commands.lua']
    by_name = {}
    dup = []
    for f in files:
        rel = '%s/%s' % (LUA_DIR, f)
        for ent in parse_lua_command(src.text(rel)):
            name = lua_scalar(ent['fields']['name'])
            if not isinstance(name, str):
                continue
            fields = OrderedDict()
            for k, v in ent['fields'].items():
                if k in ('stateEffects', 'dotEffects'):
                    fields[k] = summarize_effects(v)
                elif k in LUA_KEEP:
                    fields[k] = lua_scalar(v)
            rec = {'file': rel, 'line': ent['line'], 'var': ent['var'], 'fields': fields,
                   'in_commands_lua': f in listed, 'all_keys': list(ent['fields'].keys())}
            key = name.strip().lower()
            if key in by_name:
                dup.append((key, by_name[key]['file'], rel))
            by_name[key] = rec
    missing_files = [f for f in listed if f not in files]
    unlisted = [f for f in files if f not in listed]
    return {'by_name': by_name, 'listed': listed, 'missing_files': missing_files, 'unlisted': unlisted,
            'duplicates': dup}


# ----------------------------------------------------------------------------------------------------------------
# C++ handlers
# ----------------------------------------------------------------------------------------------------------------

def strip_cpp_comments(t):
    t = re.sub(r'/\*.*?\*/', lambda m: re.sub(r'[^\n]', ' ', m.group(0)), t, flags=re.S)
    return re.sub(r'//[^\n]*', lambda m: ' ' * len(m.group(0)), t)


def match_brace_cpp(t, start):
    depth, i = 0, start
    n = len(t)
    in_s = None
    while i < n:
        c = t[i]
        if in_s:
            if c == '\\':
                i += 1
            elif c == in_s:
                in_s = None
        elif c in '"\'':
            in_s = c
        elif c == '{':
            depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0:
                return i
        i += 1
    return n - 1


CLASS_RE = re.compile(r'\bclass\s+(\w+)\s*(?::\s*public\s+([\w:]+))?\s*\{')
DOQ_RE = re.compile(r'\bint\s+(?:(\w+)::)?doQueueCommand\s*\([^)]*\)\s*(?:const)?\s*(?:override)?\s*\{')


def scan_handlers(src):
    """class name -> {'base', 'file', 'line', 'doq': (file, start_line, end_line, body) or None}"""
    classes = {}
    rels = []
    root = src.path(CMD_H)
    for dp, dn, fn in os.walk(root):
        for f in fn:
            if f.endswith(('.h', '.cpp')):
                rels.append(os.path.relpath(os.path.join(dp, f), src.root).replace('\\', '/'))
    rels.sort()
    for rel in rels:
        raw = src.text(rel)
        t = strip_cpp_comments(raw)
        for m in CLASS_RE.finditer(t):
            classes.setdefault(m.group(1), {'base': m.group(2), 'file': rel,
                                            'line': t[:m.start()].count('\n') + 1, 'doq': None, 'raw_file': rel})
        for m in DOQ_RE.finditer(t):
            owner = m.group(1)
            if owner is None:
                prior = list(CLASS_RE.finditer(t[:m.start()]))
                owner = prior[-1].group(1) if prior else None
            if owner is None:
                continue
            end = match_brace_cpp(t, m.end() - 1)
            start_line = t[:m.start()].count('\n') + 1
            end_line = t[:end].count('\n') + 1
            body = t[m.end() - 1:end + 1]
            classes.setdefault(owner, {'base': None, 'file': rel, 'line': start_line, 'doq': None, 'raw_file': rel})
            classes[owner]['doq'] = {'file': rel, 'start': start_line, 'end': end_line, 'body': body}
    return classes


def parse_registrations(src):
    """lowercase command name -> (class, file, line)"""
    regs = {}
    for f in src.listdir(CFG_DIR):
        if not f.endswith('.cpp'):
            continue
        rel = '%s/%s' % (CFG_DIR, f)
        for i, line in enumerate(src.lines(rel), start=1):
            m = re.search(r'registerCommand<(\w+)>\(String\("([^"]+)"\)\.toLowerCase\(\)\)', line)
            if m:
                regs[m.group(2).lower()] = (m.group(1), rel, i)
    return regs


def chain_of(cls, classes):
    out, seen = [], set()
    while cls and cls not in seen:
        out.append(cls)
        seen.add(cls)
        cls = classes.get(cls, {}).get('base')
    return out


NORM_RE = re.compile(r'\s+')

# calls that mean "this handler really does something"
REAL_HINTS = ['doCombatAction', 'doJedi', 'CombatManager', 'sendSystemMessage', 'getZoneServer', 'Manager',
              'inflictDamage', 'addBuff', 'Buff(', 'healDamage', 'healWound', 'setPosture', 'getObject(',
              'transferObject', 'createObject', 'Session', 'startDancing', 'startPlaying', 'Sui', 'sendMessage',
              'broadcast', 'addState', 'setState', 'setBerserkedState', 'activateInjuryTreatment', 'dotpack',
              'DotPack', 'executeCommand', 'enqueueCommand', 'Task', 'schedule(']


def analyze_body(body):
    """Classify a doQueueCommand body (comments stripped)."""
    b = NORM_RE.sub(' ', body).strip()
    inner = b[1:-1].strip() if b.startswith('{') and b.endswith('}') else b
    # remove the standard guard lines
    core = re.sub(r'if\s*\(\s*!\s*checkStateMask\s*\(\s*creature\s*\)\s*\)\s*return\s+INVALIDSTATE\s*;', '', inner)
    core = re.sub(r'if\s*\(\s*!\s*checkInvalidLocomotions\s*\(\s*creature\s*\)\s*\)\s*return\s+INVALIDLOCOMOTION\s*;', '', core)
    core = core.strip()
    if core in ('return SUCCESS;', 'return 0;'):
        return 'template_stub', 'only the state/locomotion guards, then return SUCCESS'
    if re.fullmatch(r'return (GENERALERROR|INSUFFICIENTPERMISSION|INVALIDTARGET|INVALIDPARAMETERS);', core):
        return 'always_fails', core
    if re.fullmatch(r'error\s*\(.*?\)\s*;\s*return SUCCESS;', core):
        return 'error_stub', 'logs an error and returns SUCCESS'
    if core == '':
        return 'empty', 'empty body'
    return 'real', ''


def handler_info(cmd_name, regs, classes):
    """Resolve the handler for a lowercase command name."""
    reg = regs.get(cmd_name)
    if reg is None:
        return None
    cls, cfg_file, cfg_line = reg
    chain = chain_of(cls, classes)
    info = OrderedDict([
        ('class', cls),
        ('class_chain', chain),
        ('registered_at', '%s:%d' % (cfg_file, cfg_line)),
        ('file', classes.get(cls, {}).get('file')),
        ('class_line', classes.get(cls, {}).get('line')),
    ])
    if cls not in classes:
        info.update(status='class_not_found', reason='registered class %s has no header in %s' % (cls, CMD_H),
                    doq=None)
        return info
    # effective doQueueCommand: first class in the chain that has one
    eff = None
    for c in chain:
        d = classes.get(c, {}).get('doq')
        if d:
            eff = (c, d)
            break
    if eff is None:
        info.update(status='abstract', reason='no doQueueCommand found in the class chain', doq=None)
        return info
    owner, d = eff
    kind, why = analyze_body(d['body'])
    info['doq'] = '%s:%d-%d' % (d['file'], d['start'], d['end'])
    info['doq_owner'] = owner
    info['doq_inherited'] = owner != cls
    info['body_size'] = len(NORM_RE.sub(' ', d['body']))
    info['status'] = kind
    info['reason'] = why
    return info


# ----------------------------------------------------------------------------------------------------------------
# Messages in a handler (citations for the test plan)
# ----------------------------------------------------------------------------------------------------------------

MSG_RE = re.compile(r'"(@[a-z_0-9]+:[A-Za-z_0-9]+)"')
SPAM_RE = re.compile(r'(?:sendStateCombatSpam|StringIdChatParameter|setStringId|CombatSpam)\s*\(?[^;]*?"([a-z_0-9]+)"\s*,\s*"([A-Za-z_0-9]+)"')
FAILISH = re.compile(r'(fail|cannot|can_not|cant|no_|not_|invalid|error|too_|must|already|need|insufficient|out_of_range|'
                     r'wrong|unable|denied|refus|lost|none|nothing|prone|mounted|incap|dead|missing|require)', re.I)
OKISH = re.compile(r'(success|_ok\b|applied|_start|start_self|begin|completed?|done)', re.I)


def messages_in(src, rel, start, end):
    """List of (line, key, role) for stringid system messages inside lines [start,end] of rel."""
    res = []
    lines = src.lines(rel)
    for i in range(start, min(end, len(lines)) + 1):
        line = lines[i - 1]
        code = line.split('//')[0]
        keys = MSG_RE.findall(code)
        for m in SPAM_RE.finditer(code):
            keys.append('@%s:%s' % (m.group(1), m.group(2)))
        for k in keys:
            key = k.split(':')[1]
            # Heuristic on the string-table key only (the handler code decides what is really a success).
            role = ('failure' if FAILISH.search(key) and not OKISH.search(key) else
                    'success' if OKISH.search(key) else 'unclassified')
            res.append((i, k, role))
    seen, out = set(), []
    for t in res:
        if (t[0], t[1]) not in seen:
            seen.add((t[0], t[1]))
            out.append(t)
    return out


# ----------------------------------------------------------------------------------------------------------------
# Weapon classes (Lua weaponType bitmasks) and weapon templates
# ----------------------------------------------------------------------------------------------------------------

BASE_WEAPONS = ['UNARMEDWEAPON', 'ONEHANDMELEEWEAPON', 'TWOHANDMELEEWEAPON', 'POLEARMWEAPON', 'PISTOLWEAPON',
                'CARBINEWEAPON', 'RIFLEWEAPON', 'LIGHTNINGRIFLEWEAPON', 'SPECIALHEAVYWEAPON', 'HEAVYWEAPON',
                'GRENADEWEAPON', 'THROWNWEAPON', 'MINEWEAPON', 'ONEHANDJEDIWEAPON', 'TWOHANDJEDIWEAPON',
                'POLEARMJEDIWEAPON']
WEAPON_LABEL = {
    'UNARMEDWEAPON': 'unarmed', 'ONEHANDMELEEWEAPON': '1h melee', 'TWOHANDMELEEWEAPON': '2h melee',
    'POLEARMWEAPON': 'polearm', 'PISTOLWEAPON': 'pistol', 'CARBINEWEAPON': 'carbine', 'RIFLEWEAPON': 'rifle',
    'LIGHTNINGRIFLEWEAPON': 'lightning rifle', 'SPECIALHEAVYWEAPON': 'special heavy (flame/acid/lightning beam)',
    'HEAVYWEAPON': 'heavy', 'GRENADEWEAPON': 'grenade', 'THROWNWEAPON': 'thrown', 'MINEWEAPON': 'mine',
    'ONEHANDJEDIWEAPON': '1h lightsaber', 'TWOHANDJEDIWEAPON': '2h lightsaber',
    'POLEARMJEDIWEAPON': 'polearm lightsaber',
}


def parse_weapon_bits(src):
    rel = 'src/templates/tangible/SharedWeaponObjectTemplate.h'
    t = src.text(rel)
    bits = {}
    for m in re.finditer(r'\b([A-Z]+WEAPON)\s*=\s*(0x[0-9A-Fa-f]+|\d+)', t):
        bits[m.group(1)] = int(m.group(2), 0)
    return bits, rel


def eval_weapon_expr(expr, bits):
    """'PISTOLWEAPON' / 'A + B' / 'A | B' -> mask, or None if not understood."""
    if not isinstance(expr, str):
        return None
    mask = 0
    for part in re.split(r'[+|]', expr):
        part = part.strip().strip('()')
        if part not in bits:
            return None
        mask |= bits[part]
    return mask


def weapon_classes_for(mask, bits):
    if mask is None:
        return None
    if mask == bits.get('ANYWEAPON'):
        return ['any']
    return [n for n in BASE_WEAPONS if n in bits and (mask & bits[n]) == bits[n]]


XP_TO_BASE = {
    'combat_meleespecialize_unarmed': 'UNARMEDWEAPON', 'combat_meleespecialize_onehand': 'ONEHANDMELEEWEAPON',
    'combat_meleespecialize_twohand': 'TWOHANDMELEEWEAPON', 'combat_meleespecialize_polearm': 'POLEARMWEAPON',
    'combat_rangedspecialize_pistol': 'PISTOLWEAPON', 'combat_rangedspecialize_carbine': 'CARBINEWEAPON',
    'combat_rangedspecialize_rifle': 'RIFLEWEAPON', 'combat_rangedspecialize_heavy': 'SPECIALHEAVYWEAPON',
    'combat_rangedspecialize_bactarifle': 'RIFLEWEAPON',
    'combat_meleespecialize_onehandlightsaber': 'ONEHANDJEDIWEAPON',
    'combat_meleespecialize_twohandlightsaber': 'TWOHANDJEDIWEAPON',
    'combat_meleespecialize_polearmlightsaber': 'POLEARMJEDIWEAPON',
}


def scan_weapon_templates(src, client_index):
    """Server weapon templates -> list of dicts (template, class, certs). Class comes from xpType (set in every template)."""
    out = []
    root = src.path('bin/scripts/object/weapon')
    if not root.exists():
        return out
    for dp, dn, fn in os.walk(root):
        rel_dir = os.path.relpath(dp, src.root).replace('\\', '/')
        parts = rel_dir.split('/')
        if any(p in ('base', 'creature', 'droid', 'vehicle', 'turret', 'mine', 'trap') for p in parts):
            continue
        for f in fn:
            if not f.endswith('.lua') or f in ('objects.lua', 'serverobjects.lua'):
                continue
            rel = rel_dir + '/' + f
            t = strip_lua_comments(src.text(rel))
            xp = re.search(r'xpType\s*=\s*"([^"]+)"', t)
            cert = re.search(r'certificationsRequired\s*=\s*\{([^}]*)\}', t)
            if not xp:
                continue
            certs = re.findall(r'"([^"]+)"', cert.group(1)) if cert else []
            tpl = rel[len('bin/scripts/'):-4] + '.iff'
            shared = os.path.dirname(tpl) + '/shared_' + os.path.basename(tpl)
            wclass = XP_TO_BASE.get(xp.group(1))
            if wclass is None:
                if 'crafted_saber' in rel or 'lightsaber' in rel:
                    wclass = ('TWOHANDJEDIWEAPON' if '/2h_sword/' in rel else
                              'POLEARMJEDIWEAPON' if '/polearm/' in rel else 'ONEHANDJEDIWEAPON')
                elif '/grenade/' in rel:
                    wclass = 'GRENADEWEAPON'
            out.append(OrderedDict([('template', tpl), ('xp_type', xp.group(1)),
                                    ('weapon_class', wclass), ('certifications', certs),
                                    ('in_client_data', shared.lower() in client_index), ('file', rel)]))
    out.sort(key=lambda w: w['template'])
    return out


# ----------------------------------------------------------------------------------------------------------------
# Ability families, references, kinds
# ----------------------------------------------------------------------------------------------------------------

INSTRUMENTS = ['slitherhorn', 'fizz', 'fanfar', 'kloohorn', 'mandoviol', 'traz', 'bandfill', 'flutedroopy',
               'omnibox', 'nalargon']


def ability_reference_index(src, tokens):
    """token -> ['file:line', ...] for exact quoted occurrences in server C++/IDL and Lua managers (not screenplays)."""
    want = set(tokens)
    hits = defaultdict(list)
    roots = ['src/server', 'src/templates', 'bin/scripts/managers', 'bin/scripts/commands']
    pat = re.compile(r'"([^"\n\\]{2,80})"')
    for r in roots:
        base = src.path(r)
        for dp, dn, fn in os.walk(base):
            for f in fn:
                if not f.endswith(('.cpp', '.h', '.idl', '.lua')):
                    continue
                rel = os.path.relpath(os.path.join(dp, f), src.root).replace('\\', '/')
                if f == 'commands.lua' or rel.startswith(CFG_DIR + '/'):
                    continue
                text = src.text(rel)
                for m in pat.finditer(text):
                    if m.group(1) in want and len(hits[m.group(1)]) < 4:
                        hits[m.group(1)].append('%s:%d' % (rel, text.count('\n', 0, m.start()) + 1))
    return hits


def dynamic_refs(src, token):
    """Places that build the ability name at run time (prefix + variable), which a literal scan cannot see."""
    rules = [
        (r'^(melee|ranged)_damage_mitigation_\d$', 'src/server/zone/managers/combat/CombatManager.cpp', 'hasAbility(mitString + i)'),
        (r'^startDance\+', 'src/server/zone/managers/skill/PerformanceManager.cpp', 'return ghost->hasAbility(performance->getRequiredDance());'),
        (r'^startMusic\+', 'src/server/zone/managers/skill/PerformanceManager.cpp', 'return ghost->hasAbility(performance->getRequiredSong());'),
        (r'^flourish\+', 'src/server/zone/objects/creature/commands/FlourishCommand.h', 'hasAbility(fullString)'),
        (r'^cert_', 'src/server/zone/objects/tangible/weapon/WeaponObjectImplementation.cpp', '!ghost->hasAbility(cert)'),
        (r'^droidcommand_', 'src/server/zone/packets/object/DroidCommandProgrammingCallback.h', '!ghost->hasAbility(command)'),
        (r'^(%s)$' % '|'.join(INSTRUMENTS), 'src/server/zone/managers/skill/PerformanceManager.cpp', 'return ghost->hasAbility(instr);'),
    ]
    out = []
    for pat, rel, needle in rules:
        if re.search(pat, token) and src.exists(rel):
            ln = src.find_line(rel, needle)
            if ln:
                out.append('%s:%d (built at run time)' % (rel, ln))
    return out


def classify_noncommand_ability(a):
    """For an ability with no command row: (ability_type, kind, reason, tags)."""
    if a.startswith('cert_'):
        return ('certification', 'passive',
                'weapon/ship/structure certification; no command. Checked when an item is equipped or used '
                '(WeaponObjectImplementation.cpp: hasAbility(cert))', [])
    if a.startswith('private_'):
        return ('private_flag', 'passive',
                'internal "private_" flag used by the skill system and client; no command', [])
    if a.startswith('startDance+'):
        return ('performance', 'performance',
                'dance the player may perform: /startDance %s (PerformanceManager::canPerformDance checks this ability)' % a.split('+', 1)[1],
                ['performance'])
    if a.startswith('startMusic+'):
        return ('performance', 'performance',
                'song the player may play: /startMusic %s with a matching instrument equipped (PerformanceManager::canPlaySong)' % a.split('+', 1)[1],
                ['performance', 'item:instrument'])
    if a.startswith('flourish+'):
        return ('performance', 'performance',
                '/flourish %s while dancing or playing (FlourishCommand checks hasAbility("flourish+N"))' % a.split('+', 1)[1],
                ['performance', 'performing'])
    if a in INSTRUMENTS:
        return ('instrument_skill', 'item',
                'allows playing the %s instrument (PerformanceManager::canPlayInstrument); needs that instrument item' % a,
                ['item:instrument:' + a])
    if a.startswith('droidcommand_'):
        return ('droid_program', 'passive', 'droid programming ability (space/droid program list); no ground command', [])
    if a.startswith(('place_', 'city_', 'manage_')) or a.endswith('_fees_1') or a in (
            'access_fee', 'premium_auctions', 'ad_fees_1', 'installmissionterminal'):
        return ('permission_flag', 'passive',
                'structure/city/vendor permission; checked with hasAbility() in the structure and city code', [])
    if a.startswith(('pet_', 'trick', 'train_mount')):
        return ('pet_flag', 'passive', 'pet-command / training flag; the pet commands themselves are AI-only', [])
    if a.startswith(('areatrack_', 'slice_')):
        return ('feature_flag', 'passive', 'feature flag for a command or menu entry; no command row of its own', [])
    return ('other_flag', 'passive', 'no command row; purpose only inferable from the references listed', [])


def scan_notes(src, info, classes):
    """TODO-style comments in the handler's own header file."""
    if not info or info.get('class') not in classes:
        return []
    rel = classes[info['class']]['file']
    if os.path.basename(rel) in ('CombatQueueCommand.h', 'QueueCommand.h', 'QueueCommand.cpp', 'JediQueueCommand.h',
                                 'ForceHealQueueCommand.h', 'ForceHealQueueCommand.cpp', 'SquadLeaderCommand.h',
                                 'ForcePowersQueueCommand.h'):
        return []
    out = []
    for i, line in enumerate(src.lines(rel), start=1):
        m = re.search(r'(TODO|FIXME|@TODO|not implemented|unimplemented|has no effect|was broken)', line, re.I)
        if m:
            out.append('%s:%d %s' % (rel, i, line.strip()[:160]))
    return out[:4]


STUB_NOTES = {
    'survey': 'the real check is in the survey tool: SurveyToolImplementation.cpp handleObjectMenuSelect needs hasAbility("survey") '
              '(failure message @error_message:insufficient_skill); test by using a survey tool, not by /survey',
    'customizevehicle': 'no other server reference to this command was found; treat as unimplemented',
}


def config_warnings(handler, lua_rec, classes):
    """Latent-stub hints: handler is real but its Lua configuration would make it do nothing."""
    out = []
    if not handler or handler.get('status') != 'real':
        return out
    chain = handler['class_chain']
    f = lua_rec['fields'] if lua_rec else {}
    if 'ForceHealQueueCommand' in chain and lua_rec:
        keys = ('healAmount', 'healWoundAmount', 'healBleedingCost', 'healFireCost', 'healDiseaseCost', 'healPoisonCost',
                'healBattleFatigue', 'healStateCost', 'statesToHeal')
        if not any(f.get(k) not in (None, 0, 0.0, '0') for k in keys):
            out.append('Force heal with no heal amount or cure cost set in its Lua script')
    if 'JediQueueCommand' in chain and not ({'ForceHealQueueCommand', 'ForcePowersQueueCommand', 'JediCombatQueueCommand',
                                              'CombatQueueCommand'} & set(chain)) and lua_rec:
        if 'duration' not in f and handler['class'] not in ('RegainConsciousnessCommand', 'AvoidIncapacitationCommand',
                                                            'ChannelForceCommand', 'ForceMeditateCommand'):
            out.append('Force buff with no duration in its Lua script')
    d = (classes.get(handler.get('doq_owner') or handler['class'], {}) or {}).get('doq')
    generic = bool(d) and 'doCombatAction' in d['body'] and 'ForcePowersQueueCommand' not in chain
    if 'CombatQueueCommand' in chain and generic and f:
        dm = f.get('damageMultiplier')
        if dm == 0 and not f.get('stateEffects') and not f.get('dotEffects'):
            out.append('damageMultiplier 0 and no state or dot effects configured: the attack has no effect')
    return out


def bot_call(slash, kind, tags):
    """How a Bot (tools/bots/squad.py) would call it: slash(name, args, target)."""
    target = {'attack': 'hostile', 'heal_other': 'friendly', 'target_friendly': 'friendly',
              'self': 'self_or_none'}.get(kind, 'none')
    if kind == 'attack' and 'corpse' in tags:
        target = 'corpse'
    if 'creature_target' in tags:
        target = 'creature'
    return OrderedDict([('call', "bot.slash('%s', args='', target=<%s>)" % (slash, target)), ('target', target)])


def _k(kind, why, tags=(), notes=()):
    return {'kind': kind, 'why': why, 'tags': list(tags), 'notes': list(notes)}


# Commands whose handler is a plain QueueCommand (or whose base-class rule does not fit). Set by reading each
# handler (line ranges are in commands.json). Anything not here and not matched by a class rule is "unknown".
KIND_BY_COMMAND = {
    'aim': _k('self', 'sets the AIMING state on the user; ranged weapon only (INVALIDWEAPON otherwise); no damage', ['weapon:ranged']),
    'areatrack': _k('self', 'opens a selection window (SUI); no target', ['sui'], ['the track starts only after the SUI answer']),
    'avoidincapacitation': _k('self', 'Force self-buff', ['force_power', 'no_armor']),
    'berserk1': _k('self', 'self buff (BERSERK state); melee/unarmed weapon, random fail roll 25+mod', ['weapon:melee_or_unarmed']),
    'berserk2': _k('self', 'self buff (BERSERK state); melee/unarmed weapon, random fail roll', ['weapon:melee_or_unarmed']),
    'centerofbeing': _k('self', 'self buff; needs a melee/polearm/unarmed weapon and the center_of_being skill mods', ['weapon:melee_or_unarmed']),
    'channelforce': _k('self', 'restores Force power at a HAM cost; fails silently when Force is already full', ['force_power', 'no_armor']),
    'colorlights': _k('performance', 'effect on an active performance (arg = level); needs a running dance or song', ['performing']),
    'conceal': _k('self', 'toggles the mask-scent buff on the user (target optional, players only)', []),
    'customizevehicle': _k('item', 'customizes a vehicle', ['vehicle'], ['handler is a template stub']),
    'dazzle': _k('performance', 'effect on an active performance (arg = level)', ['performing']),
    'diagnose': _k('target_friendly', 'opens a patient window for a creature target (not droid/vehicle)', ['friendly_target', 'sui']),
    'distract': _k('performance', 'effect on an active performance (arg = level)', ['performing']),
    'dragincapacitatedplayer': _k('target_friendly', 'drags an incapacitated player; needs skill science_medic_injury_speed_02', ['incapacitated_friendly']),
    'drainforce': _k('attack', 'drains Force from a hostile player target (creatures have none: @jedi_spam:target_no_force)', ['hostile_target', 'force_power', 'no_armor']),
    'emboldenpets': _k('self', "buffs the owner's pets", ['pet'], ['no target; needs at least one pet']),
    'enragepets': _k('self', "enrages the owner's pets", ['pet'], ['no target; needs at least one pet']),
    'feigndeath': _k('self', 'feign death; only usable in combat (@combat_effects:feign_no_combat otherwise)', ['combat_state']),
    'firejet': _k('performance', 'effect on an active performance (arg = level)', ['performing']),
    'firstaid': _k('heal_other', 'first aid on a bleeding target', ['wounded_friendly', 'item:medicine']),
    'forage': _k('self', 'starts foraging (ForageManager, scout)', ['outdoors']),
    'forcemeditate': _k('self', 'Force meditation; not in combat, no armor', ['force_power', 'no_armor']),
    'forceofwill': _k('self', 'only works while the user is incapacitated and recovery is pending', ['incapacitated_self'], ['hard to test: needs the bot to be incapacitated']),
    'grantzoningrights': _k('target_friendly', 'grants city zoning rights to a player in the same city; user must be city militia', ['friendly_target', 'city']),
    'harvestcorpse': _k('attack', 'harvests a dead creature (needs a corpse: kill a creature first)', ['corpse']),
    'healdamage': _k('heal_other', 'heals HAM damage with a stimpack; target wounded', ['wounded_friendly', 'item:stimpack']),
    'healenhance': _k('target_friendly', 'applies an enhancement (buff) medpack to a target', ['friendly_target', 'item:enhance_pack']),
    'healmind': _k('heal_other', "heals Mind damage of a target at the user's own Mind cost", ['wounded_friendly']),
    'healstate': _k('heal_other', 'cures a state (stun, dizzy, ...) with a state pack', ['wounded_friendly', 'item:state_pack']),
    'healwound': _k('heal_other', 'heals wounds with a wound pack', ['wounded_friendly', 'item:wound_pack']),
    'installmissionterminal': _k('item', 'mayor-only city job: installs a mission terminal', ['city', 'sui']),
    'maskscent': _k('self', 'toggles mask scent on the user', []),
    'medicalforage': _k('self', 'starts medical foraging (ForageManager)', ['outdoors']),
    'meditate': _k('self', 'starts meditating; not in combat', []),
    'powerboost': _k('self', 'Power Boost buff; only while meditating', ['meditating']),
    'quickheal': _k('heal_other', 'quick heal of a target (Mind cost)', ['wounded_friendly']),
    'recruitskilltrainer': _k('item', 'mayor-only city job: recruits a skill trainer', ['city', 'sui']),
    'registerwithlocation': _k('item', 'registers the user with a medical or entertainment building (user must stand inside one)', ['building:medical_or_entertainment']),
    'rescue': _k('target_friendly', 'rescues a grouped ally', ['group_member', 'friendly_target']),
    'reviveplayer': _k('heal_other', 'revives an incapacitated or dead player with a revive pack', ['incapacitated_friendly', 'item:revive_pack']),
    'sample': _k('item', 'samples a resource with a survey tool (not in combat)', ['item:survey_tool', 'resource_point']),
    'sampledna': _k('attack', 'takes a DNA sample from a live creature target (bio-engineer skill)', ['creature_target']),
    'serversysgroup': _k('self', 'group message from the squad leader; needs a group and being its leader', ['group_leader']),
    'smokebomb': _k('performance', 'effect on an active performance (arg = level)', ['performing']),
    'spotlight': _k('performance', 'effect on an active performance (arg = level)', ['performing']),
    'startdance': _k('performance', 'starts a dance by name (arg); needs the matching startDance+<name> ability', ['performance']),
    'startmusic': _k('performance', 'starts a song by name (arg); needs an equipped instrument and the startMusic+<name> ability', ['performance', 'item:instrument']),
    'stopdance': _k('performance', 'stops the active dance', ['performing']),
    'stopmusic': _k('performance', 'stops the active song', ['performing']),
    'survey': _k('item', 'survey command; the handler is a template stub, real surveying goes through the survey tool', ['item:survey_tool'], ['handler is a template stub; see survey tool code']),
    'takecover': _k('self', 'takes cover (COVER state), costs Action', ['combat_state_optional']),
    'tame': _k('attack', 'tames a baby creature target (creature handler)', ['creature_target']),
    'tendwound': _k('heal_other', 'tend wounds on a target', ['wounded_friendly']),
    'tenddamage': _k('heal_other', 'tend damage on a target', ['wounded_friendly']),
    'transferforce': _k('target_friendly', 'transfers Force to a friendly player target', ['friendly_target', 'force_power', 'no_armor']),
    'tumbletokneeling': _k('self', 'tumble to kneeling with a defense buff; costs Action', []),
    'tumbletoprone': _k('self', 'tumble to prone with a defense buff; costs Action', []),
    'tumbletostanding': _k('self', 'tumble to standing with a defense buff; costs Action', []),
    'ventriloquism': _k('performance', 'effect on an active performance (arg = level)', ['performing']),
    'regainconsciousness': _k('self', 'Force self-recovery from incapacitation', ['incapacitated_self', 'force_power']),
    # combat-family commands that are debuffs on a target (still need a hostile target)
    'intimidate1': _k('attack', 'state attack (intimidate) on a hostile target; no damage', ['hostile_target']),
    'intimidate2': _k('attack', 'state attack (intimidate) on a hostile target; no damage', ['hostile_target']),
    'warcry1': _k('attack', 'cone debuff (next-attack delay) on hostile targets in front; no damage', ['hostile_target']),
    'warcry2': _k('attack', 'cone debuff (next-attack delay) on hostile targets in front; no damage', ['hostile_target']),
    'taunt': _k('attack', 'taunt (state/aggro) on a hostile target; no damage', ['hostile_target']),
}


# ----------------------------------------------------------------------------------------------------------------
# Classification of one ability / command
# ----------------------------------------------------------------------------------------------------------------

KINDS = ['self', 'attack', 'heal_other', 'target_friendly', 'item', 'crafting', 'performance', 'passive', 'unknown']
STUB_STATUSES = ('template_stub', 'error_stub', 'always_fails', 'empty', 'abstract', 'class_not_found')


def weapon_tags(mask, bits):
    if mask is None:
        return []
    if mask == bits.get('ANYWEAPON'):
        return []
    if mask == bits.get('RANGEDWEAPON'):
        return ['weapon:ranged']
    if mask == bits.get('MELEEWEAPON'):
        return ['weapon:melee']
    if mask == bits.get('JEDIWEAPON'):
        return ['weapon:lightsaber']
    return ['weapon:' + WEAPON_LABEL[n] for n in weapon_classes_for(mask, bits) or []]


def affliction_tags(name):
    """The specific affliction a healing command needs on its patient (plain HAM damage is not listed)."""
    n = name.lower()
    out = []
    if 'wound' in n or n.startswith('totalheal'):
        out.append('affliction:wounds')
    if 'battlefatigue' in n:
        out.append('affliction:battle_fatigue')
    if n in ('healstate', 'healstatesself', 'healstatesother'):
        out.append('affliction:state')
    if 'curedisease' in n:
        out.append('affliction:disease')
    if 'curepoison' in n:
        out.append('affliction:poison')
    if n == 'extinguishfire':
        out.append('affliction:fire')
    if n in ('firstaid', 'stopbleeding'):
        out.append('affliction:bleeding')
    return out


def classify_command(cname, rows, handler, lua_rec, bits):
    r = _classify_command(cname, rows, handler, lua_rec, bits)
    if r['kind'] in ('self', 'heal_other', 'target_friendly'):
        r['tags'] = list(r['tags']) + [t for t in affliction_tags(cname) if t not in r['tags']]
    return r


def _classify_command(cname, rows, handler, lua_rec, bits):
    """-> dict(kind, rule, why, tags, notes). `rule` names which rule fired so the outputs can be audited."""
    tables_present = {t for t, _ in rows}
    chain = handler['class_chain'] if handler else []
    fields = lua_rec['fields'] if lua_rec else {}
    tags, notes = [], []
    if tables_present == {'space'}:
        return dict(kind='unknown', rule='R1 space-only', tags=['ship'], notes=[],
                    why='defined only in command_table_space.iff: needs a piloted ship in space; a ground bot cannot run it')
    if handler is None:
        return dict(kind='unknown', rule='R2 no handler', tags=[], notes=[],
                    why='no C++ class is registered for this command name in CommandConfigManager*.cpp')
    mask = eval_weapon_expr(fields.get('weaponType'), bits) if 'weaponType' in fields else bits.get('ANYWEAPON')
    combat_family = 'CombatQueueCommand' in chain
    if combat_family and mask is not None:
        tags += weapon_tags(mask, bits)
    ov = KIND_BY_COMMAND.get(cname)
    if ov:
        t = list(ov['tags'])
        # combat-family overrides still get their weapon requirement from Lua
        t += [x for x in tags if x not in t and combat_family]
        return dict(kind=ov['kind'], rule='R3 per-command table', why=ov['why'], tags=t, notes=list(ov['notes']))
    if 'ForceHealQueueCommand' in chain:
        at = str(fields.get('allowedTarget', ''))
        if 'SELF' in at and 'OTHER' in at:
            return dict(kind='heal_other', rule='R4 Force heal, self or other',
                        tags=['force_power', 'no_armor', 'wounded_friendly'],
                        notes=['Lua allowedTarget is SELF + OTHER: also works on the user'],
                        why='Force cure usable on the user or on another player (ForceHealQueueCommand)')
        if cname.endswith('self') or re.search(r'self\d?$', cname) or at.endswith('SELF'):
            return dict(kind='self', rule='R4 Force heal, self variant', tags=['force_power', 'no_armor', 'damaged_self'],
                        notes=[], why='Force heal on the user (ForceHealQueueCommand)')
        if re.search(r'other\d?$', cname) or at.endswith('OTHER'):
            return dict(kind='heal_other', rule='R4 Force heal, other variant',
                        tags=['force_power', 'no_armor', 'wounded_friendly'], notes=[],
                        why='Force heal on another player (ForceHealQueueCommand)')
        return dict(kind='self', rule='R4 Force heal, no suffix', tags=['force_power', 'no_armor', 'damaged_self'],
                    notes=['allowedTarget is automatic: also works on a ranged friendly target'],
                    why='Force cure on the user by default (ForceHealQueueCommand, TARGET_AUTO)')
    if 'JediCombatQueueCommand' in chain:
        return dict(kind='attack', rule='R5 lightsaber attack', tags=['hostile_target', 'force_power', 'no_armor'] + tags,
                    notes=[], why='lightsaber attack through CombatQueueCommand::doCombatAction')
    if 'ForcePowersQueueCommand' in chain:
        return dict(kind='attack', rule='R6 Force power on a target', tags=['hostile_target', 'force_power', 'no_armor'] + tags,
                    notes=[], why='Force power aimed at a hostile target (ForcePowersQueueCommand)')
    if 'JediQueueCommand' in chain:
        return dict(kind='self', rule='R7 Force buff', tags=['force_power', 'no_armor'], notes=[],
                    why='Force self-buff through JediQueueCommand::doJediSelfBuffCommand')
    if 'SquadLeaderCommand' in chain:
        return dict(kind='self', rule='R8 squad leader', tags=['group_leader', 'group_member'], notes=[],
                    why='group buff/order issued by a squad leader; needs a group')
    if 'CurePackCommand' in chain:
        return dict(kind='heal_other', rule='R9 cure pack', tags=['wounded_friendly', 'item:cure_pack'], notes=[],
                    why='cure pack (disease/poison/fire) applied to a target')
    if 'DotPackCommand' in chain:
        return dict(kind='attack', rule='R10 dot pack', tags=['hostile_target', 'item:dot_pack'], notes=[],
                    why='applies a poison/disease dart pack to a hostile target')
    if combat_family:
        return dict(kind='attack', rule='R11 combat command', tags=['hostile_target'] + tags, notes=[],
                    why='CombatQueueCommand-derived: damage/state attack on a hostile target')
    return dict(kind='unknown', rule='R12 not classified', tags=[], notes=[],
                why='handler is a plain QueueCommand with no entry in KIND_BY_COMMAND')


# ----------------------------------------------------------------------------------------------------------------
# Entries
# ----------------------------------------------------------------------------------------------------------------

def build_entries(ctx):
    profs, tables, src = ctx['profs'], ctx['tables'], ctx['src']
    cmds, by_ab, regs, classes, lua, bits = ctx['cmds'], ctx['by_ab'], ctx['regs'], ctx['classes'], ctx['lua'], ctx['bits']
    cmd_n = tables['cmd_n']
    grants = OrderedDict()
    for p in profs.values():
        for ab in p['profession_row_abilities']:
            grants.setdefault(ab, []).append((p['name'], '(profession row)'))
        for b in p['boxes']:
            for ab in b['abilities']:
                grants.setdefault(ab, []).append((p['name'], b['name']))
    # references for abilities without command rows
    nocmd = []
    for ab in grants:
        al = ab.lower()
        if not by_ab.get(al) and al not in cmds:
            nocmd.append(ab)
    refs = ability_reference_index(src, nocmd)
    for ab in nocmd:
        extra = list(ctx.get('lua_refs', {}).get(ab, [])) + dynamic_refs(src, ab)
        refs[ab] = list(refs.get(ab, [])) + [x for x in extra if x not in refs.get(ab, [])]
    entries = []
    for ab in sorted(grants, key=lambda s: s.lower()):
        al = ab.lower()
        names = list(by_ab.get(al, []))
        gate_kind = 'characterAbility'
        if not names and al in cmds:
            names, gate_kind = [al], 'command_name_only'
        gb = [OrderedDict([('profession', p), ('box', b)]) for p, b in grants[ab]]
        e = OrderedDict([('ability', ab), ('english_name', ''), ('ability_type', ''), ('slash', None),
                         ('granted_by', gb), ('professions', sorted({p for p, _ in grants[ab]}))])
        if names:
            # primary: the command named like the ability, else the first one
            primary = al if al in names else names[0]
            rows = cmds[primary]
            prefer = [r for t, r in rows if t != 'space'] or [r for t, r in rows]
            row_tab = next((t for t, r in rows if r is prefer[0]), rows[0][0])
            row = prefer[0]
            handler = handler_info(primary, regs, classes)
            lua_rec = lua['by_name'].get(primary)
            cl = classify_command(primary, rows, handler, lua_rec, bits)
            e['ability_type'] = 'command'
            e['slash'] = row['commandName']
            e['english_name'] = cmd_n.get(primary, '')
            e['gate'] = OrderedDict([
                ('how', gate_kind),
                ('command_requires_ability', row['characterAbility']),
                ('ungated', row['characterAbility'] == ''),
                ('note', ('the command has no characterAbility: any player can run it, so a successful run does '
                          'not prove this box granted it') if row['characterAbility'] == '' else
                         ('this ability token is not the command\'s gate (it requires "%s")' % row['characterAbility'])
                         if row['characterAbility'].lower() != al else '')])
            e['commands'] = []
            for n in names:
                rr = cmds[n]
                rp = [r for t, r in rr if t != 'space'] or [r for t, r in rr]
                h2 = handler_info(n, regs, classes)
                e['commands'].append(OrderedDict([
                    ('name', rp[0]['commandName']), ('primary', n == primary),
                    ('handler_class', h2['class'] if h2 else None), ('handler_status', h2['status'] if h2 else 'missing')]))
            e['command_table'] = command_row_summary(row_tab, row)
            e['tables_defining'] = sorted({t for t, _ in rows})
            if lua_rec:
                e['lua'] = OrderedDict([('file', '%s:%d' % (lua_rec['file'], lua_rec['line'])),
                                        ('registered_in_commands_lua', lua_rec['in_commands_lua']),
                                        ('settings', lua_rec['fields'])])
                mask = eval_weapon_expr(lua_rec['fields'].get('weaponType'), bits) if 'weaponType' in lua_rec['fields'] else None
                if mask is not None:
                    e['weapon_requirement'] = weapon_classes_for(mask, bits)
            else:
                e['lua'] = None
            if handler is None:
                e['handler'] = OrderedDict([('status', 'missing'), ('reason', 'no registerCommand<> line for "%s"' % primary)])
            else:
                hh = OrderedDict(handler)
                e['handler'] = hh
                e['handler']['notes'] = scan_notes(src, handler, classes)
                d = classes.get(handler.get('doq_owner') or handler['class'], {}).get('doq')
                if d:
                    e['messages'] = [OrderedDict([('at', '%s:%d' % (d['file'], ln)), ('key', k), ('role_guess', r)])
                                     for ln, k, r in messages_in(src, d['file'], d['start'], d['end'])]
            spam = (lua_rec['fields'].get('combatSpam') if lua_rec else None)
            if spam:
                e['combat_spam_keys'] = ['@cbt_spam:%s_%s' % (spam, s) for s in ('hit', 'miss', 'evade', 'counter', 'block')]
            status = e['handler'].get('status')
            e['stub'] = status in STUB_STATUSES or status == 'missing'
            e['stub_reason'] = e['handler'].get('reason', '') if e['stub'] else ''
            e['test_kind'] = cl['kind']
            e['test_kind_rule'] = cl['rule']
            e['test_kind_reason'] = cl['why']
            e['setup_tags'] = cl['tags']
            e['notes'] = list(cl['notes'])
            if primary in STUB_NOTES and e['stub']:
                e['notes'].append(STUB_NOTES[primary])
            e['config_warnings'] = config_warnings(handler, lua_rec, classes)
            e['bot_call'] = bot_call(row['commandName'], cl['kind'], cl['tags'])
            if lua_rec is None and handler and 'CombatQueueCommand' in handler['class_chain']:
                e['notes'].append('no Lua script: combat defaults apply (damageMultiplier 1, any weapon, random pool)')
            if lua_rec and not lua_rec['in_commands_lua']:
                e['notes'].append('Lua script exists but is not listed in commands.lua: settings are never applied')
        else:
            atype, kind, why, tags = classify_noncommand_ability(ab)
            e['ability_type'] = atype
            e['english_name'] = ''
            e['commands'] = []
            e['handler'] = None
            e['stub'] = False
            e['stub_reason'] = ''
            e['test_kind'] = kind
            e['test_kind_rule'] = 'R0 ability without command row (%s)' % atype
            e['test_kind_reason'] = why
            e['setup_tags'] = tags
            e['notes'] = []
            e['server_references'] = refs.get(ab, [])
            if not refs.get(ab):
                e['notes'].append('no occurrence of this ability name found in the server C++ / Lua managers / object templates scanned: '
                                  'nothing on the server was seen checking it (client-side use cannot be ruled out)')
            if atype == 'private_flag':
                e['notes'].append('the private_* SKILL MODS in the boxes are read by CombatManager; this private_* ABILITY token is not')
            if atype in ('performance', 'instrument_skill'):
                e['slash'] = {'startDance': 'startDance', 'startMusic': 'startMusic', 'flourish': 'flourish'}.get(ab.split('+')[0])
                if atype == 'performance':
                    e['args'] = ab.split('+', 1)[1] if '+' in ab else ''
                    e['bot_call'] = OrderedDict([('call', "bot.slash('%s', args='%s')" % (e['slash'], e['args'])),
                                                 ('target', 'none')])
        entries.append(e)
    return entries, refs


# ----------------------------------------------------------------------------------------------------------------
# Readiness with today's bot tooling
# ----------------------------------------------------------------------------------------------------------------

# Setup tags the current tooling already covers: /agentgear basic|boss|support|survey (AgentGearCommand.h), squad.py
# groups, creatures to fight, a second bot to stand next to (and to hurt in a fight).
READY_TAGS = {'hostile_target', 'creature_target', 'friendly_target', 'wounded_friendly', 'group_leader', 'group_member',
              'performing', 'performance', 'sui', 'outdoors', 'combat_state', 'combat_state_optional', 'meditating',
              'damaged_self', 'force_power', 'no_armor', 'weapon:pistol', 'weapon:rifle', 'weapon:ranged',
              'weapon:1h melee', 'weapon:melee_or_unarmed', 'weapon:melee', 'item:stimpack', 'item:enhance_pack',
              'item:instrument', 'item:instrument:slitherhorn', 'item:survey_tool'}
# Needs a staged situation the scenario must build (no new server code).
STAGING_TAGS = {'corpse', 'incapacitated_friendly', 'incapacitated_self', 'building:medical_or_entertainment',
                'resource_point', 'affliction:wounds', 'affliction:battle_fatigue', 'affliction:state',
                'affliction:disease', 'affliction:poison', 'affliction:fire', 'affliction:bleeding'}
WORLD_BLOCK_TAGS = {'city', 'pet', 'vehicle'}
# Needs an item kit that /agentgear does not have: tag -> (proposed kit, candidate templates)
KIT_PROPOSALS = OrderedDict([
    ('weapon:carbine', ('carbine', ['object/weapon/ranged/carbine/carbine_cdef.iff'])),
    ('weapon:polearm', ('polearm', ['object/weapon/melee/polearm/lance_staff_wood_s1.iff'])),
    ('weapon:unarmed', ('unarmed', ['(no weapon: unequip the current one with transferItemWeapon)'])),
    ('weapon:2h melee', ('twohand', ['object/weapon/melee/axe/axe_heavy_duty.iff'])),
    ('weapon:special heavy (flame/acid/lightning beam)', ('heavy', ['object/weapon/ranged/heavy/heavy_acid_beam.iff',
                                                                       'object/weapon/ranged/heavy/heavy_lightning_beam.iff',
                                                                       'object/weapon/ranged/heavy/heavy_particle_beam.iff'])),
    ('weapon:1h lightsaber', ('saber1h', ['a 1h lightsaber template (see weapon table)'])),
    ('weapon:2h lightsaber', ('saber2h', ['a 2h lightsaber template (see weapon table)'])),
    ('weapon:polearm lightsaber', ('saberpole', ['a polearm lightsaber template (see weapon table)'])),
    ('weapon:lightsaber', ('saber1h', ['a 1h lightsaber template (see weapon table)'])),
    ('item:wound_pack', ('medicine2', ['object/tangible/medicine/crafted/medpack_wound_health_a.iff'])),
    ('item:state_pack', ('medicine2', ['object/tangible/medicine/crafted/medpack_blinded_a.iff',
                                       'object/tangible/medicine/crafted/medpack_dizzy_a.iff',
                                       'object/tangible/medicine/crafted/medpack_stunned_a.iff'])),
    ('item:cure_pack', ('medicine2', ['object/tangible/medicine/crafted/medpack_cure_disease_a.iff',
                                      'object/tangible/medicine/crafted/medpack_cure_poison_a.iff'])),
    ('item:dot_pack', ('medicine2', ['object/tangible/medicine/crafted/medpack_poison_health_a.iff',
                                     'object/tangible/medicine/crafted/medpack_disease_health_a.iff'])),
    ('item:revive_pack', ('medicine2', ['object/tangible/medicine/crafted/medpack_revive.iff'])),
    ('item:medicine', ('medicine2', ['object/tangible/medicine/crafted/crafted_stimpack_sm_s1_a.iff'])),
])


def assess_readiness(entries, costs):
    """Adds readiness / readiness_missing to every entry; returns the kit shopping list {kit: {tags, abilities}}."""
    blocked_prof = {n for n, c in costs.items() if c['grant_status'] != 'ok' and c['agentgear_profession'] != 'ok'}
    kits = OrderedDict()
    for e in entries:
        tags = set(e['setup_tags'])
        if e['test_kind'] == 'passive':
            e['readiness'], e['readiness_missing'] = 'n/a_passive', []
            continue
        missing = []
        status = 'ready'
        if 'ship' in tags:
            status = 'blocked_space'
            missing.append('ship')
        elif 'force_power' in tags and set(e['professions']) <= blocked_prof:
            status = 'blocked_jedi'
            missing.append('Jedi state / Jedi manager')
        elif tags & WORLD_BLOCK_TAGS:
            status = 'blocked_world'
            missing += sorted(tags & WORLD_BLOCK_TAGS)
        else:
            newkit = [t for t in tags if t in KIT_PROPOSALS or (t.startswith('item:instrument:') and t != 'item:instrument:slitherhorn')]
            if newkit:
                status = 'needs_new_kit'
                missing += sorted(newkit)
                for t in newkit:
                    inst = {'flutedroopy': 'flute_droopy', 'kloohorn': 'kloo_horn', 'omnibox': 'ommni_box'}.get(
                        t.split(':')[-1], t.split(':')[-1])
                    kit = KIT_PROPOSALS.get(t, ('instruments', []))
                    k = kits.setdefault(kit[0], {'templates': list(kit[1]), 'tags': set(), 'abilities': set()})
                    if kit[0] == 'instruments':
                        tpl = 'object/tangible/instrument/%s.iff' % inst
                        if tpl not in k['templates']:
                            k['templates'].append(tpl)
                    k['tags'].add(t)
                    k['abilities'].add(e['ability'])
            elif tags & STAGING_TAGS:
                status = 'needs_staging'
                missing += sorted(tags & STAGING_TAGS)
        e['readiness'], e['readiness_missing'] = status, missing
    return kits


# ----------------------------------------------------------------------------------------------------------------
# Skill-point feasibility and builds
# ----------------------------------------------------------------------------------------------------------------

def closure_of(names, byn):
    seen, stack = [], list(names)
    while stack:
        n = stack.pop()
        if n in seen or n not in byn:
            continue
        seen.append(n)
        stack.extend(x for x in csv(byn[n]['SKILLS_REQUIRED']))
    return seen


def profession_costs(profs, tables, cap):
    byn = {r['NAME']: r for r in tables['skills']}
    res = OrderedDict()
    for p in profs.values():
        own = [b['name'] for b in p['boxes']]
        needed_by_others = {x for b in p['boxes'] for x in b['prerequisites']}
        tops = [n for n in own if n not in needed_by_others]
        cl = closure_of(tops, byn)
        pts = sum(byn[n]['POINTS_REQUIRED'] for n in cl)
        blockers = []
        for n in cl:
            r = byn[n]
            if r['JEDI_STATE_REQUIRED']:
                blockers.append('%s needs Jedi state %d' % (n, r['JEDI_STATE_REQUIRED']))
            elif n.startswith('force_'):
                blockers.append('%s goes through JediManager::canLearnSkill (Lua)' % n)
        god = [n for n in cl if byn[n]['GOD_ONLY']]
        # path 1: /agentskill (awardSkill, point cap applies, god_only is not checked)
        status = 'ok'
        if blockers:
            status = 'blocked_jedi'
        elif pts > cap:
            status = 'over_cap'
        # path 2: /agentgear profession <name> (no point cap; refuses god_only professions and god_only boxes)
        if p['god_only']:
            ag = 'unavailable_god_only_profession'
        elif god:
            ag = 'partial_god_only_boxes'
        elif blockers:
            ag = 'partial_jedi'
        else:
            ag = 'ok'
        res[p['name']] = OrderedDict([
            ('top_boxes', tops), ('closure_boxes', len(cl)), ('closure_skill_points', pts),
            ('own_skill_points', sum(b['skill_points'] for b in p['boxes'])),
            ('other_professions_needed', sorted({profession_of_box(n, profs) for n in cl} - {p['name'], None})),
            ('grant_status', status), ('agentgear_profession', ag), ('blockers', sorted(set(blockers))[:6]),
            ('hidden_god_only_boxes', len(god)),
            ('closure_names', cl)])
    return res


def profession_of_box(name, profs):
    for p in profs.values():
        for b in p['boxes']:
            if b['name'] == name:
                return p['name']
    return None


def suggest_builds(profs, costs, tables, cap):
    """First-fit-decreasing packing of grantable professions into characters of <= cap skill points."""
    byn = {r['NAME']: r for r in tables['skills']}

    def precluded(a, b):
        sa, sb = set(a), set(b)
        return any(set(csv(byn[n]['PRECLUSION_SKILLS'])) & sb for n in sa if n in byn) or             any(set(csv(byn[n]['PRECLUSION_SKILLS'])) & sa for n in sb if n in byn)

    # pilot_* professions only have space commands and exclude each other; they are left out of ground builds
    items = [(n, c) for n, c in costs.items() if c['grant_status'] == 'ok' and not n.startswith('pilot_')]
    items.sort(key=lambda x: -x[1]['closure_skill_points'])
    builds = []
    for name, c in items:
        placed = False
        for b in builds:
            union = set(b['boxes']) | set(c['closure_names'])
            pts = sum(byn[n]['POINTS_REQUIRED'] for n in union)
            if pts <= cap and not precluded(b['boxes'], c['closure_names']):
                b['professions'].append(name)
                b['boxes'] = sorted(union)
                b['skill_points'] = pts
                placed = True
                break
        if not placed:
            builds.append({'professions': [name], 'boxes': sorted(set(c['closure_names'])),
                           'skill_points': c['closure_skill_points']})
    tier_rank = {'starter': 0, 'elite': 1, 'jedi_force': 2, 'space': 3}
    # run order: characters holding a starter profession first, Jedi last; packing order breaks ties
    builds.sort(key=lambda b: (min(tier_rank.get(profs[n]['tier'], 9) for n in b['professions']),
                               max(tier_rank.get(profs[n]['tier'], 9) for n in b['professions']) >= 2))
    for i, b in enumerate(builds, start=1):
        # test order inside a character: starters first, then elites, cheapest closure first
        b['professions'].sort(key=lambda n: (tier_rank.get(profs[n]['tier'], 9), costs[n]['closure_skill_points'], n))
        b['id'] = 'build%02d' % i
        tops = []
        for n in b['professions']:
            tops += costs[n]['top_boxes']
        b['agentskill_boxes'] = sorted(set(tops))
        b['agentskill_calls'] = [' '.join(b['agentskill_boxes'][i:i + 16]) for i in range(0, len(b['agentskill_boxes']), 16)]
        b.pop('boxes', None)
    return builds


# ----------------------------------------------------------------------------------------------------------------
# Output
# ----------------------------------------------------------------------------------------------------------------

REFERENCE_LINES = [
    ('ability is required before a command runs (client error 2)', 'src/server/zone/managers/objectcontroller/ObjectControllerImplementation.cpp', 'if (!playerObject->hasAbility(characterAbility))'),
    ('an unregistered command is dropped with no reply', 'src/server/zone/managers/objectcontroller/ObjectControllerImplementation.cpp', 'unregistered queue command'),
    ('handler result goes to onFail / onComplete', 'src/server/zone/managers/objectcontroller/ObjectControllerImplementation.cpp', 'queueCommand->onFail(actionCount, object, errorNumber)'),
    ('command table files that define commands', 'src/server/zone/managers/objectcontroller/command/CommandConfigManager.h', 'loadCommandData("datatables/command/command_tables_shared.iff")'),
    ('Lua fields the server reads', 'src/server/zone/managers/objectcontroller/command/CommandConfigManager.cpp', 'void CommandConfigManager::parseVariableData'),
    ('return codes of a handler', 'src/server/zone/objects/creature/commands/QueueCommand.h', 'const static int INVALIDWEAPON = 5;'),
    ('wrong weapon message', 'src/server/zone/objects/creature/commands/QueueCommand.cpp', '@cbt_spam:no_attack_wrong_weapon'),
    ('Jedi armor message', 'src/server/zone/objects/creature/commands/QueueCommand.cpp', '@jedi_spam:not_with_armor'),
    ('cooldown message', 'src/server/zone/objects/creature/commands/QueueCommand.cpp', 'again yet, please wait'),
    ('combat: out of range message', 'src/server/zone/objects/creature/commands/CombatQueueCommand.h', '@error_message:target_out_of_range'),
    ('combat: line of sight message', 'src/server/zone/objects/creature/commands/CombatQueueCommand.h', '@cbt_spam:los_fail'),
    ('combat: weapon type check', 'src/server/zone/objects/creature/commands/CombatQueueCommand.h', 'return INVALIDWEAPON;'),
    ('combat: hit/miss/evade spam keys', 'src/server/zone/objects/creature/commands/CombatQueueCommand.h', 'stringName += "_hit";'),
    ('self buff example: success message', 'src/server/zone/objects/creature/commands/Berserk1Command.h', '@cbt_spam:berserk_success_single'),
    ('self buff example: failure message', 'src/server/zone/objects/creature/commands/Berserk1Command.h', '@cbt_spam:berserk_fail_single'),
    ('performance example: success message', 'src/server/zone/objects/creature/commands/StartMusicCommand.h', '@performance:music_start_self'),
    ('performance example: no instrument', 'src/server/zone/objects/creature/commands/StartMusicCommand.h', '@performance:music_no_instrument'),
    ('performance effect without a performance', 'src/server/zone/objects/creature/commands/DazzleCommand.h', '@performance:effect_not_performing'),
    ('heal example: no line of sight', 'src/server/zone/objects/creature/commands/HealDamageCommand.h', '@healing:no_line_of_sight'),
    ('heal example: not permitted to help', 'src/server/zone/objects/creature/commands/ForceHealQueueCommand.cpp', '@jedi_spam:no_help_target'),
    ('bot body: command_failed event', 'src/client/agent/AgentControl.cpp', '"command_failed"'),
    ('bot body: command_failed reason names (index = error code)', 'src/client/agent/AgentControl.cpp', 'static const char* reasons[]'),
    ('equip a weapon or instrument: /transferItemWeapon <dest oid> 4 0 0 0', 'src/server/zone/objects/creature/commands/TransferItemWeaponCommand.h', 'int transferType = tokenizer.getIntToken();'),
    ('bot body: system message event','src/client/agent/AgentControl.cpp', '{"event", "system"}, {"text", str(text)}'),
    ('bot body: combat event', 'src/client/agent/AgentControl.cpp', '{"event", "combat"}'),
    ('bot body: posture/combat state events', 'src/client/agent/AgentControl.cpp', '"combat_started"'),
    ('/agentskill: grants boxes and prerequisites, 16 per call', 'src/server/zone/objects/creature/commands/AgentSkillCommand.h', 'count++ < 16'),
    ('/agentskill: answer prefix', 'src/server/zone/objects/creature/commands/AgentSkillCommand.h', '"[agentskill] "'),
    ('/agentgear: the only item kits', 'src/server/zone/objects/creature/commands/AgentGearCommand.h', 'kit != "basic" && kit != "boss"'),
    ('/agentgear profession <name>: whole profession, no point limit', 'src/server/zone/objects/creature/commands/AgentGearCommand.h', 'kit.beginsWith("profession ")'),
    ('/agentgear profession: refused for god-only or non-profession rows', 'src/server/zone/objects/creature/commands/AgentGearCommand.h', 'root->isGodOnly()'),
    ('/agentgear profession clear (unlearn all)', 'src/server/zone/objects/creature/commands/AgentGearCommand.h', 'manager->surrenderAllSkills(creature, true, false, true)'),
    ('/agentgear profession: answer carries granted/failed/skills', 'src/server/zone/objects/creature/commands/AgentGearCommand.h', 'reply["skills"] = skills;'),
    ('squad.py gear(): skipped when armor is already carried', 'tools/bots/squad.py', "already has {armor}"),
    ('/agentgear: support kit (medic packs, camps, instrument)', 'src/server/zone/objects/creature/commands/AgentGearCommand.h', 'object/tangible/instrument/slitherhorn.iff'),
    ('skill point cap', 'src/server/zone/managers/skill/SkillManager.cpp', 'Core3.Sandbox.SkillPoints'),
    ('Jedi state gate for boxes', 'src/server/zone/managers/skill/SkillManager.cpp', 'getJediState() < skill->getJediStateRequired()'),
    ('force_* boxes go through the Jedi manager', 'src/server/zone/managers/skill/SkillManager.cpp', 'JediManager::instance()->canLearnSkill'),
    ('abilities are added only when the table lists them', 'src/server/zone/managers/skill/SkillManager.cpp', 'if (ability != nullptr && !ghost->hasAbility(abilityName))'),
    ('weapon certification check', 'src/server/zone/objects/tangible/weapon/WeaponObjectImplementation.cpp', '!ghost->hasAbility(cert)'),
    ('instrument skill check', 'src/server/zone/managers/skill/PerformanceManager.cpp', 'return ghost->hasAbility(instr);'),
    ('flourish ability check', 'src/server/zone/objects/creature/commands/FlourishCommand.h', 'hasAbility(fullString)'),
]


def resolve_references(src):
    out = []
    for label, rel, needle in REFERENCE_LINES:
        if rel.startswith('tools/'):  # a file of this repo (outputs/), not of Core3
            local = OUTPUTS / rel
            ln = None
            if local.exists():
                for i, line in enumerate(local.read_text(encoding='utf-8', errors='replace').split('\n'), start=1):
                    if needle in line:
                        ln = i
                        break
            out.append(OrderedDict([('what', label), ('file', 'outputs/' + rel), ('line', ln), ('needle', needle)]))
            continue
        ln = src.find_line(rel, needle) if src.exists(rel) else None
        out.append(OrderedDict([('what', label), ('file', rel), ('line', ln), ('needle', needle)]))
    return out


def md_table(headers, rows):
    out = ['| ' + ' | '.join(headers) + ' |', '|' + '|'.join(['---'] * len(headers)) + '|']
    for r in rows:
        out.append('| ' + ' | '.join(str(c).replace('|', '/') for c in r) + ' |')
    return '\n'.join(out)


def summarize(profs, entries):
    by_ab = {e['ability']: e for e in entries}
    rows = []
    for p in profs.values():
        abil = []
        for ab in p['profession_row_abilities']:
            abil.append(ab)
        for b in p['boxes']:
            abil += b['abilities']
        abil = sorted(set(abil), key=str.lower)
        kc = Counter(by_ab[a]['test_kind'] for a in abil)
        cmd = [a for a in abil if by_ab[a]['ability_type'] == 'command']
        stubs = [a for a in cmd if by_ab[a]['stub']]
        schem = sum(len(b['schematics_granted']) for b in p['boxes'])
        rows.append(OrderedDict([('profession', p['name']), ('tier', p['tier']), ('boxes', p['box_count']),
                                 ('abilities', len(abil)), ('commands', len(cmd)), ('kinds', dict(kc)),
                                 ('stubs', len(stubs)), ('stub_abilities', stubs), ('schematic_groups', schem)]))
    return rows


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--src', help='a local MMOCoreORB folder (instead of snapshotting WSL Debian)')
    ap.add_argument('--keep-snapshot', action='store_true')
    ap.add_argument('--out', default=str(HERE))
    args = ap.parse_args()
    out = Path(args.out)
    began = time.time()
    snap_dir, head, lua_refs = None, '', {}
    client_tables = load_tables()   # the live client's winning archives; used for the token list and the difference note
    profs0, _ = build_professions(client_tables)
    all_tokens = sorted({a for p in profs0.values() for b in p['boxes'] for a in b['abilities']})
    if args.src:
        root = Path(args.src)
    else:
        snap_dir, head, lua_refs = take_snapshot(all_tokens)
        root = snap_dir
    try:
        src = Src(root)
        tre_order = parse_tre_files(src)
        tables = load_tables(tre_order)
        differences = table_differences(client_tables, tables)
        profs, skipped = build_professions(tables)
        cmds = index_commands(tables)
        by_ab = defaultdict(list)
        for n, rows in cmds.items():
            for t, r in rows:
                if r['characterAbility'] and n not in by_ab[r['characterAbility'].lower()]:
                    by_ab[r['characterAbility'].lower()].append(n)
        lua = load_lua_scripts(src)
        specials = {m.lower() for m in re.findall(r'createCommand\(String\("(\w+)"\)', src.text(CFG_DIR + '/CommandConfigManager.cpp'))}
        lua['orphans'] = sorted(n for n in lua['by_name'] if n not in cmds and n not in specials)
        lua['table_commands_without_lua'] = sorted(n for n in cmds if n not in lua['by_name'])
        classes = scan_handlers(src)
        regs = parse_registrations(src)
        bits, bits_file = parse_weapon_bits(src)
        ctx = dict(profs=profs, tables=tables, src=src, cmds=cmds, by_ab=by_ab, regs=regs, classes=classes, lua=lua,
                   bits=bits, lua_refs=lua_refs)
        entries, refs = build_entries(ctx)
        # skill points
        cap = 250
        m = re.search(r'Core3\.Sandbox\.SkillPoints",\s*(\d+)', src.text('src/server/zone/managers/skill/SkillManager.cpp'))
        if m:
            cap = int(m.group(1))
        costs = profession_costs(profs, tables, cap)
        builds = suggest_builds(profs, costs, tables, cap)
        kits = assess_readiness(entries, costs)
        summary = summarize(profs, entries)
        client_index = trn_iff.client_index()
        weapons = scan_weapon_templates(src, client_index)
        ref_lines = resolve_references(src)
        # species certifications (every species gets them at creation)
        species_rows = [s for s in skipped if s['name'].startswith('species_')]
        species_certs = None
        for s in species_rows:
            c = {a for a in s['abilities'] if a.startswith('cert_')}
            species_certs = c if species_certs is None else species_certs & c
        species_certs = sorted(species_certs or [])
        cert_granted_by = defaultdict(list)
        for p in profs.values():
            for b in p['boxes']:
                for a in b['abilities']:
                    cert_granted_by[a].append(b['name'])

        # ---- attach per-box command summaries to professions
        e_by = {e['ability']: e for e in entries}
        for p in profs.values():
            p['closure'] = OrderedDict((k, v) for k, v in costs[p['name']].items() if k != 'closure_names')
            for b in p['boxes']:
                b['commands'] = [OrderedDict([('ability', a), ('slash', e_by[a]['slash']), ('ability_type', e_by[a]['ability_type']),
                                              ('test_kind', e_by[a]['test_kind']), ('stub', e_by[a]['stub'])])
                                 for a in b['abilities']]

        meta = OrderedDict([
            ('generated_at', time.strftime('%Y-%m-%d %H:%M:%S')),
            ('generator', 'outputs/Claude-class-check/build_matrix.py'),
            ('core3_dev_head', head.strip().replace('\n', ' ') if head else 'unknown (--src used)'),
            ('data_archives', tables['archives']),
            ('data_resolution', 'server TreFiles order from bin/conf/config.lua' if tre_order else 'live client order (config.lua not readable)'),
            ('client_vs_server_table_differences', differences),
            ('client_winning_archives', tables['client_archives']),
            ('skill_point_cap', cap),
            ('counts', OrderedDict([
                ('professions', len(profs)), ('boxes', sum(p['box_count'] for p in profs.values())),
                ('skipped_skills', len(skipped)), ('ability_tokens', len(entries)),
                ('command_abilities', sum(1 for e in entries if e['ability_type'] == 'command')),
                ('distinct_command_rows', len({x['name'].lower() for e in entries if e['ability_type'] == 'command' for x in e['commands']})),
                ('stub_command_abilities', sum(1 for e in entries if e['stub'])),
                ('test_kinds', dict(Counter(e['test_kind'] for e in entries))),
                ('readiness_now', dict(Counter(e['readiness'] for e in entries)))])),
            ('lua_scripts', OrderedDict([('loaded', len(lua['by_name'])), ('listed_in_commands_lua', len(lua['listed'])),
                                         ('missing_files', lua['missing_files']), ('unlisted_files', lua['unlisted']),
                                         ('duplicate_names', lua['duplicates']),
                                         ('script_names_matching_no_command', lua['orphans']),
                                         ('table_commands_without_script', len(lua['table_commands_without_lua']))])),
        ])
        order = run_order(profs, entries, costs)
        write_json(out / 'professions.json', OrderedDict([
            ('meta', meta), ('professions', list(profs.values())), ('skipped', skipped),
            ('suggested_builds', builds), ('proposed_run_order', order)]))
        write_json(out / 'commands.json', OrderedDict([
            ('meta', meta), ('test_kinds', KINDS),
            ('rules', [OrderedDict([('rule', r), ('text', t)]) for r, t in RULE_TEXT]), ('commands', entries)]))
        write_matrix(out / 'matrix.md', meta, profs, entries, summary, costs, builds, weapons, species_certs,
                     cert_granted_by, ref_lines, lua, skipped, refs, cmds, tables, classes, regs, kits, order)
        c = meta['counts']
        print('professions=%d boxes=%d abilities=%d command_abilities=%d stubs=%d unknown=%d' % (
            c['professions'], c['boxes'], c['ability_tokens'], c['command_abilities'], c['stub_command_abilities'],
            c['test_kinds'].get('unknown', 0)))
        print('kinds:', c['test_kinds'])
        print('builds:', len(builds), ' seconds: %.1f' % (time.time() - began))
        bad = [r for r in ref_lines if r['line'] is None]
        if bad:
            print('WARNING: reference lines not found:', [(r['file'], r['needle']) for r in bad])
    finally:
        if snap_dir is not None and not args.keep_snapshot:
            shutil.rmtree(snap_dir, ignore_errors=True)


RUN_PHASES = [
    ('P1 starters', ['combat_marksman', 'combat_brawler', 'outdoors_scout', 'science_medic', 'social_entertainer',
                     'crafting_artisan']),
    ('P2 elites whose weapons and items exist today', ['combat_rifleman', 'combat_pistol', 'combat_1hsword', 'social_dancer',
                                                       'social_musician', 'outdoors_ranger', 'science_doctor',
                                                       'outdoors_squadleader', 'combat_smuggler', 'outdoors_bio_engineer',
                                                       'outdoors_creaturehandler', 'social_imagedesigner',
                                                       'social_politician']),
    ('P3 elites that need new weapon or medicine kits', ['combat_carbine', 'combat_2hsword', 'combat_polearm',
                                                         'combat_unarmed', 'combat_commando', 'combat_bountyhunter',
                                                         'science_combatmedic']),
    ('P4 crafting elites (grant check only)', ['crafting_armorsmith', 'crafting_weaponsmith', 'crafting_chef',
                                               'crafting_tailor', 'crafting_architect', 'crafting_droidengineer',
                                               'crafting_merchant', 'crafting_shipwright']),
    ('P5 Jedi and Force', ['jedi_padawan', 'jedi_light_side_journeyman', 'jedi_light_side_master',
                           'jedi_dark_side_journeyman', 'jedi_dark_side_master', 'force_sensitive_combat_prowess',
                           'force_sensitive_enhanced_reflexes', 'force_sensitive_crafting_mastery',
                           'force_sensitive_heightened_senses', 'force_title_jedi', 'force_discipline_light_saber',
                           'force_discipline_powers', 'force_discipline_healing', 'force_discipline_enhancements',
                           'force_discipline_defender', 'force_rank_light', 'force_rank_dark']),
    ('P6 space (cannot be tried on the ground)', ['pilot_rebel_navy', 'pilot_imperial_navy', 'pilot_neutral']),
]


def run_order(profs, entries, costs):
    """One row per profession in the proposed order, with the abilities a run of that profession tries."""
    by_ab = {e['ability']: e for e in entries}
    listed = {n for _, names in RUN_PHASES for n in names}
    phases = [(t, [n for n in names if n in profs]) for t, names in RUN_PHASES]
    extra = [n for n in profs if n not in listed]
    if extra:
        phases.append(('P7 not placed by RUN_PHASES (new professions)', extra))
    byn_box = {b['name']: b for p in profs.values() for b in p['boxes']}
    rows = []
    step = 0
    for title, names in phases:
        for n in names:
            step += 1
            p = profs[n]
            own = {b['name'] for b in p['boxes']}
            prereq_boxes = [x for x in costs[n]['closure_names'] if x not in own]
            prereq_abil = {a for x in prereq_boxes if x in byn_box for a in byn_box[x]['abilities']}
            own_abil = []
            for b in p['boxes']:
                for a in b['abilities']:
                    if a not in own_abil:
                        own_abil.append(a)
            tries = [a for a in own_abil if by_ab[a]['test_kind'] != 'passive']
            excl = [a for a in tries if a not in prereq_abil]
            rd = Counter(by_ab[a]['readiness'] for a in tries)
            if costs[n]['agentgear_profession'] == 'ok':
                grant = "/agentgear profession %s" % n
            elif costs[n]['grant_status'] == 'ok':
                grant = '/agentskill ' + ' '.join(costs[n]['top_boxes'])
            else:
                grant = 'blocked (%s)' % '; '.join(costs[n]['blockers'][:1] or [costs[n]['agentgear_profession']])
            if grant.startswith('blocked'):
                rd = Counter({'blocked_jedi': len(tries)})
            rows.append(OrderedDict([('step', step), ('phase', title), ('profession', n), ('grant', grant),
                                     ('tries', len(tries)), ('exclusive_to_this_profession', len(excl)),
                                     ('prerequisite_professions', costs[n]['other_professions_needed']),
                                     ('readiness', dict(rd)), ('abilities', tries), ('exclusive_abilities', excl)]))
    return rows


def write_json(path, obj):
    path.write_text(json.dumps(obj, indent=1, ensure_ascii=False) + '\n', encoding='utf-8', newline='\n')


RULE_TEXT = [
    ('R0', 'Ability token with no command row: certification / private flag / permission flag / droid program / pet flag '
           '= passive; startDance+x, startMusic+x, flourish+n = performance; instrument names = item (instrument).'),
    ('R1', 'Command defined only in command_table_space.iff = unknown (space-only, needs a ship).'),
    ('R2', 'Command row without a registered C++ class = unknown.'),
    ('R3', 'Plain-QueueCommand handlers (and combat-family debuffs such as warcry/taunt) are listed by name in '
           'KIND_BY_COMMAND, each set after reading the handler; the reason text says what the handler requires.'),
    ('R4', 'ForceHealQueueCommand classes: a name ending in Self or Lua allowedTarget SELF = self; a name ending in '
           'Other, or allowedTarget OTHER or SELF + OTHER = heal_other (the SELF + OTHER cures also work on the user).'),
    ('R5', 'JediCombatQueueCommand (lightsaber moves) = attack, needs a lightsaber, Force power and no armor.'),
    ('R6', 'ForcePowersQueueCommand = attack on a hostile target (Force power, no armor).'),
    ('R7', 'JediQueueCommand = self (Force buff).'),
    ('R8', 'SquadLeaderCommand = self with a group (the bot must lead a group).'),
    ('R9', 'CurePackCommand = heal_other (cure pack item, afflicted friendly target).'),
    ('R10', 'DotPackCommand = attack (dot pack item, hostile target).'),
    ('R11', 'Any other CombatQueueCommand descendant = attack (hostile target); weapon class comes from the Lua weaponType.'),
    ('R12', 'Anything else = unknown.'),
]


def write_matrix(path, meta, profs, entries, summary, costs, builds, weapons, species_certs, cert_granted_by,
                 ref_lines, lua, skipped, refs, cmds, tables, classes, regs, kits, order):
    c = meta['counts']
    L = []
    A = L.append
    A('# Pre-CU class check: profession / ability matrix')
    A('')
    A('Generated %s by `outputs/Claude-class-check/build_matrix.py` (re-run it after any server or table change).' % meta['generated_at'])
    A('Source: Core3-dev `%s`. Data tables resolved by: %s. Archives: %s.' % (
        meta['core3_dev_head'], meta['data_resolution'],
        '; '.join('`%s` from %s' % (k.split('/')[-1], v) for k, v in meta['data_archives'].items())))
    diffs = meta['client_vs_server_table_differences']
    if diffs:
        A('')
        A('**The live client resolves some of these files differently** (`%s`). Rows that exist only in the client\'s winning archive are NOT in this matrix: %s. '
          'The server does not list that archive in config.lua; if config-local.lua adds it (not read), the server has those rows too.' % (
              ', '.join('%s from %s' % (k.split('/')[-1], v) for k, v in meta['client_winning_archives'].items() if v != meta['data_archives'][k]),
              '; '.join('%s: %s' % (k, ', '.join(v['only_in_client_archive'] + ['changed ' + x for x in v['changed_in_client_archive']]) or 'none') for k, v in diffs.items())))
    A('')
    A('## Totals')
    A('')
    A(md_table(['what', 'count'], [
        ['professions (IS_PROFESSION rows)', c['professions']],
        ['skill boxes (excluding the profession root rows)', c['boxes']],
        ['skipped skills (languages, species, category roots, placeholders)', c['skipped_skills']],
        ['ability tokens granted by profession boxes (distinct)', c['ability_tokens']],
        ['... of which resolve to a command row (slash command)', c['command_abilities']],
        ['distinct command rows reached', c['distinct_command_rows']],
        ['command abilities whose handler looks like a stub or is missing', c['stub_command_abilities']],
    ] + [['test kind `%s`' % k, c['test_kinds'].get(k, 0)] for k in KINDS]))
    A('')
    A('Table check: %d Lua command scripts loaded, %d listed in commands.lua, missing files %s, unlisted files %s.' % (
        meta['lua_scripts']['loaded'], meta['lua_scripts']['listed_in_commands_lua'],
        meta['lua_scripts']['missing_files'] or 'none', meta['lua_scripts']['unlisted_files'] or 'none'))
    A('')
    A('## Per profession')
    A('')
    A('`abilities` = distinct tokens in the profession\'s COMMANDS columns; `cmd` = those that are slash commands. The kind columns count abilities '
      '(see Test-kind rules). `stub` counts command abilities with a stub-looking handler. `pts` = skill points of the profession\'s own boxes / '
      'of the whole prerequisite closure. `schem` = schematic groups granted.')
    A('')
    hdr = ['profession', 'tier', 'boxes', 'pts own/closure', 'abil', 'cmd'] + KINDS + ['stub', 'schem']
    rows = []
    for s in summary:
        k = s['kinds']
        cst = costs[s['profession']]
        rows.append([s['profession'], s['tier'], s['boxes'], '%d/%d' % (cst['own_skill_points'], cst['closure_skill_points']),
                     s['abilities'], s['commands']] + [k.get(x, 0) for x in KINDS] + [s['stubs'], s['schematic_groups']])
    A(md_table(hdr, rows))
    A('')
    # ---- stubs
    A('## Stub-looking or missing-handler commands')
    A('')
    A('A handler is a *template stub* when its `doQueueCommand` only runs the state/locomotion guards and returns SUCCESS. The command then '
      '"succeeds" with no effect from this class; any real feature behind it must live in another code path (a packet handler, a radial menu, a tool object). '
      'A command row with no registered class would be dropped silently by the server (ObjectControllerImplementation.cpp, "unregistered queue command"); the count of those is below.')
    A('')
    st_rows = []
    for e in entries:
        if e['ability_type'] == 'command' and e['stub']:
            h = e['handler']
            st_rows.append([e['ability'], e['slash'], ', '.join(e['professions']), h.get('class', '-'), h.get('status'), h.get('doq', '-'), e['stub_reason'], '; '.join(e.get('notes', []))])
    if st_rows:
        A(md_table(['ability', 'command', 'professions', 'class', 'status', 'doQueueCommand', 'reason', 'notes'], st_rows))
    else:
        A('None among profession abilities.')
    A('')
    unreg = [n for n in cmds if n not in regs]
    A('Command rows (all three tables) without a registered handler class: **%d**%s.' % (len(unreg), (' (' + ', '.join(unreg[:30]) + ')') if unreg else ''))
    tstub = sorted(n for n in cmds if (handler_info(n, regs, classes) or {}).get('status') in STUB_STATUSES)
    A('')
    A('Template-stub command rows anywhere in the tables (not only the ones a profession grants): **%d**. Those granted by a profession are in the table above; '
      'the rest are staff/admin, city, vendor or client-side commands and are not part of a class check.' % len(tstub))
    A('')
    # implementation notes
    A('### Handlers with TODO / "no effect" comments in their own header')
    A('')
    nrows = []
    for e in entries:
        if e['ability_type'] == 'command' and e.get('handler') and e['handler'].get('notes'):
            nrows.append([e['ability'], ', '.join(e['professions'][:3]), '<br>'.join(e['handler']['notes'])])
    A(md_table(['ability', 'professions', 'notes (file:line text)'], nrows) if nrows else 'None.')
    A('')
    # other findings
    A('## Other findings from the source')
    A('')
    ungated = [e for e in entries if e['ability_type'] == 'command' and e['gate']['ungated']]
    A('* **Ungated commands** (command table has no characterAbility, so any player can run them; a "works" result proves nothing about the box): %d: %s.' % (
        len(ungated), ', '.join(sorted(e['slash'] for e in ungated)) or 'none'))
    mism = [e for e in entries if e['ability_type'] == 'command' and e['gate']['note'] and not e['gate']['ungated']]
    A('* **Ability token is not the command\'s gate**: %s.' % (', '.join('%s (needs %s)' % (e['ability'], e['gate']['command_requires_ability']) for e in mism) or 'none'))
    multi = [e for e in entries if e['ability_type'] == 'command' and len(e['commands']) > 1]
    A('* **One ability gates several commands**: %s.' % ('; '.join('%s -> %s' % (e['ability'], ', '.join(x['name'] for x in e['commands'])) for e in multi) or 'none'))
    nolua = [e for e in entries if e['ability_type'] == 'command' and e.get('lua') is None and e['handler'] and 'CombatQueueCommand' in e['handler'].get('class_chain', [])]
    A('* **Combat commands with no Lua script** (defaults apply): %s.' % (', '.join(e['slash'] for e in nolua) or 'none'))
    disabled = [e for e in entries if e['ability_type'] == 'command' and e.get('lua') and e['lua']['settings'].get('disabled') is True]
    A('* **Lua scripts whose `name` matches no command row**: %s. **Command rows with no Lua script**: %d (all-profession commands among them: %s).' % (
        ', '.join(lua['orphans']) or 'none', len(lua['table_commands_without_lua']),
        ', '.join(sorted({e['slash'] for e in entries if e['ability_type'] == 'command' and e.get('lua') is None})) or 'none'))
    A('* **Lua `disabled = true`**: %s.' % (', '.join(e['slash'] for e in disabled) or 'none'))
    spaceonly = [e for e in entries if e['test_kind_rule'] == 'R1 space-only']
    A('* **Space-only commands** (cannot be tried on the ground): %d (%s).' % (len(spaceonly), ', '.join(sorted({p for e in spaceonly for p in e['professions']}))))
    crafting_cmds = [e for e in entries if e['test_kind'] == 'crafting']
    A('* **Crafting**: %d abilities have test kind `crafting`. Crafting professions grant skill mods and schematic groups (professions.json, `schematics_granted`), not slash commands.' % len(crafting_cmds))
    unref = defaultdict(list)
    for e in entries:
        if e['ability_type'] not in ('command', 'certification', 'performance', 'instrument_skill') and not e.get('server_references'):
            unref[e['ability_type']].append(e['ability'])
    A('* **Granted abilities with no command row and no server reference found** (quoted-name scan of src/server, src/templates, bin/scripts/managers, '
      'commands, object templates and screenplays, plus the run-time-built names listed in `dynamic_refs`):')
    for k, v in sorted(unref.items()):
        v = sorted(v)
        A('  * %s (%d): %s' % (k, len(v), ', '.join(v[:12]) + (' ... (full list in commands.json)' if len(v) > 12 else '')))
    cw = [(e['ability'], w) for e in entries for w in e.get('config_warnings', [])]
    A('* **Real handler, but its Lua configuration looks inert**: %s.' % ('; '.join('%s (%s)' % x for x in cw) or 'none found'))
    A('* **Hidden / god-only boxes**: %s of the jedi_* boxes are flagged god_only in skills.iff. `awardSkill` does not check that flag (it checks prerequisites, species, Jedi state, and force_* via the Jedi manager), so `/agentskill` should be able to grant them; this has not been tried.' %
      sum(1 for p in profs.values() for b in p['boxes'] if b['god_only']))
    A('')
    # special setup
    A('## Commands that need special setup')
    A('')
    tagmap = defaultdict(list)
    for e in entries:
        if e['test_kind'] == 'passive':
            continue
        for t in e['setup_tags']:
            tagmap[t].append(e['ability'])
    descr = {
        'hostile_target': 'a hostile creature or training target in range (and line of sight)',
        'creature_target': 'a live creature that can be sampled/tamed',
        'corpse': 'a dead creature (kill one first)',
        'friendly_target': 'a second bot standing near, not in PvP',
        'wounded_friendly': 'a second bot with HAM damage, wounds, bleeding or a state',
        'incapacitated_friendly': 'a second bot that is incapacitated (or dead for revive)',
        'group_leader': 'the bot leads a group with at least one other member',
        'group_member': 'at least one group member near the leader',
        'force_power': 'Force power in the pool (Jedi skill mods) and no armor worn',
        'no_armor': 'no armor worn',
        'performing': 'the bot is dancing or playing music (start one first)',
        'performance': 'entertainer: run the dance/song first',
        'pet': 'an owned pet',
        'ship': 'a piloted ship (space)',
        'vehicle': 'a vehicle',
        'city': 'a city with the bot as mayor or militia',
        'sui': 'a pop-up window answer',
        'combat_state': 'the bot is in combat',
        'combat_state_optional': 'works with or without combat; the roll is harder in combat',
        'meditating': 'the bot is meditating',
        'incapacitated_self': 'the bot itself is incapacitated',
        'outdoors': 'outdoors, not in a building',
        'resource_point': 'a surveyed resource point',
        'building:medical_or_entertainment': 'inside a medical or entertainment building',
        'damaged_self': 'the bot has HAM damage or an affliction to heal',
        'affliction:wounds': 'the patient has wounds (sustained combat damage)',
        'affliction:battle_fatigue': 'the patient has battle fatigue',
        'affliction:state': 'the patient is stunned, dizzy, blind or intimidated',
        'affliction:disease': 'the patient is diseased',
        'affliction:poison': 'the patient is poisoned',
        'affliction:fire': 'the patient is on fire',
        'affliction:bleeding': 'the patient is bleeding',
    }
    rows = []
    for t in sorted(tagmap, key=lambda s: (not s.startswith('weapon:'), s)):
        d = descr.get(t)
        if t.startswith('weapon:'):
            d = 'weapon class: ' + t.split(':', 1)[1]
        if t.startswith('item:'):
            d = 'item in inventory/equipped: ' + t.split(':', 1)[1].replace('_', ' ')
        names = sorted(set(tagmap[t]), key=str.lower)
        rows.append([t, d or '', len(names), ', '.join(names[:40]) + (' ...' if len(names) > 40 else '')])
    A(md_table(['setup tag', 'what the bot needs', 'abilities', 'which (first 40)'], rows))
    A('')
    A('Full per-ability lists are in commands.json (`setup_tags`).')
    A('')
    # rules
    A('## Test-kind rules')
    A('')
    A('The rule that fired is stored with every entry (`test_kind_rule`). Order matters.')
    A('')
    A(md_table(['rule', 'text'], [[r, t] for r, t in RULE_TEXT]))
    A('')
    A('`target_type` in the command table is stored by the server but never read (QueueCommand.h getter only); 0/1/2 are read as none/required/optional by the SWG command-table convention, which is not verified in this source.')
    A('')
    # grant
    A('## Granting a profession to a bot')
    A('')
    A('Two server helpers exist (test galaxy only, bot accounts in Core3.AgentAccounts):')
    A('')
    A('* `/agentgear profession <name>`: grants every box of an IS_PROFESSION row plus all prerequisites (also from other professions) '
      'with no XP and no skill-point limit; `/agentgear profession clear` surrenders all skills (character-builder "Unlearn All Skills"); `/agentgear profession list` '
      'answers with the current boxes. It refuses god_only professions and skips god_only boxes. Species/Jedi prerequisites are still enforced, so Force boxes land in `failed`.')
    A('* `/agentskill <box> ...`: awards boxes plus prerequisites without XP, but the point cap applies (%d, `Core3.Sandbox.SkillPoints` default; the live value may differ in '
      'config-local.lua, which was not read) and there is no revoke. It does not check the god_only flag.' % meta['skill_point_cap'])
    A('')
    A('`agentgear` column: `ok` = every box should be granted; `unavailable_god_only_profession` = refused (use /agentskill); `partial_*` = some boxes will be in `failed`. '
      '`agentskill` column: `ok`, `over_cap`, or `blocked_jedi` (a box needs Jedi state or goes through the Jedi manager).')
    A('')
    rows = []
    for n, cst in costs.items():
        rows.append([n, cst['closure_skill_points'], cst['closure_boxes'], cst['agentgear_profession'], cst['grant_status'],
                     ', '.join(cst['other_professions_needed'][:4]), '; '.join(cst['blockers'][:2])])
    A(md_table(['profession', 'closure pts', 'closure boxes', 'agentgear', 'agentskill', 'also grants boxes of', 'blockers'], rows))
    A('')
    A('### Fallback: suggested /agentskill builds (first-fit packing, <= %d points per character, no revoke)' % meta['skill_point_cap'])
    A('')
    A(md_table(['build', 'points', 'professions (test order)', '/agentskill calls'], [
        [b['id'], b['skill_points'], ', '.join(b['professions']), ' | '.join(b['agentskill_calls'])] for b in builds]))
    A('')
    # run order
    A('## Proposed run order (one profession per run)')
    A('')
    A("Each run: `/agentgear profession clear`, grant the profession (it also grants boxes of the professions it needs), try every non-passive ability granted by the profession's own boxes, "
      "then the next row. `tries` = abilities tried; `excl` = of those, abilities that none of the prerequisite professions' boxes grant (a success proves this profession's boxes give it); "
      'the others also come from a prerequisite profession. Readiness counts are ready / needs_staging / needs_new_kit / blocked.')
    A('')
    rows = []
    for r in order:
        rd = r['readiness']
        rows.append([r['step'], r['phase'].split(' ')[0], r['profession'], r['grant'], r['tries'], r['exclusive_to_this_profession'],
                     '%d / %d / %d / %d' % (rd.get('ready', 0), rd.get('needs_staging', 0), rd.get('needs_new_kit', 0),
                                            sum(v for k, v in rd.items() if k.startswith('blocked')))])
    A(md_table(['step', 'phase', 'profession', 'grant', 'tries', 'excl', 'ready / staging / new kit / blocked'], rows))
    A('')
    A('Phases: ' + '; '.join(t for t, _ in RUN_PHASES) + '.')
    A('')
    # readiness
    A("## Readiness with today's bot tooling")
    A('')
    A('`ready` = can be tried with `/agentgear` kits, `/agentskill`, a creature to fight and a second bot. `needs_new_kit` = an item or weapon `/agentgear` does not give. '
      '`needs_staging` = a situation the scenario must build (corpse, downed ally, building, survey point). `blocked_world` = city/pet/vehicle. '
      '`blocked_space` = ship. `blocked_jedi` = every profession that grants it needs Jedi state or the Jedi manager.')
    A('')
    order = ['ready', 'needs_staging', 'needs_new_kit', 'blocked_world', 'blocked_jedi', 'blocked_space', 'n/a_passive']
    rows = []
    for k in KINDS:
        row = [k]
        for st_ in order:
            row.append(sum(1 for e in entries if e['test_kind'] == k and e['readiness'] == st_))
        rows.append(row)
    rows.append(['total'] + [sum(1 for e in entries if e['readiness'] == st_) for st_ in order])
    A(md_table(['test kind'] + order, rows))
    A('')
    A('Kits the scenario needs that `/agentgear` does not have (proposed names; templates are candidates and not tried):')
    A('')
    A(md_table(['proposed kit', 'candidate templates', 'abilities it unlocks', 'which (first 12)'], [
        [k, '<br>'.join(v['templates']), len(v['abilities']), ', '.join(sorted(v['abilities'], key=str.lower)[:12])]
        for k, v in kits.items()]))
    A('')
    # weapons
    A('## Weapon classes and candidate templates')
    A('')
    A('Every species starts with these certifications: %s.' % (', '.join(species_certs) or 'unknown'))
    A('')
    byclass = defaultdict(list)
    for w in weapons:
        byclass[w['weapon_class'] or 'other'].append(w)
    rows = []
    for cl in BASE_WEAPONS + ['other']:
        ws = byclass.get(cl, [])
        if not ws:
            continue
        free = [w for w in ws if w['certifications'] and all(x in species_certs for x in w['certifications'])]
        free = [w for w in free if w['in_client_data']] or free
        others = [w for w in ws if w not in free and w['certifications'] and w['in_client_data']]
        # prefer weapons whose cert comes from a novice box (cheapest to grant), then by name
        others.sort(key=lambda w: (0 if any('novice' in b for c in w['certifications'] for b in cert_granted_by.get(c, [])) else 1,
                                   w['template']))
        seen_certs, extra = set(), []
        for w in others:
            key = tuple(w['certifications'])
            if key in seen_certs or len(extra) >= 3:
                continue
            seen_certs.add(key)
            gb = sorted({b for c in w['certifications'] for b in cert_granted_by.get(c, [])})
            extra.append('%s [%s <- %s]' % (w['template'], ','.join(w['certifications']), ', '.join(gb[:2]) or 'no profession box grants it'))
        rows.append([WEAPON_LABEL.get(cl, cl), len(ws), len(free),
                     '<br>'.join('%s (%s)' % (w['template'], ','.join(w['certifications'])) for w in free[:2]) or '-',
                     '<br>'.join(extra) or '-'])
    A(md_table(['weapon class', 'templates', 'species-cert usable', 'species-cert candidates', 'other candidates [cert <- box that grants it]'], rows))
    A('')
    A('Class comes from the template\'s `xpType`; candidates must also have a `shared_` template in the client data (`in_client_data`). Lightsabers are not species-usable; '
      'their certs come from jedi_* / force_title boxes.')
    A('')
    A('## Reference lines used by test-plan.md (generated from the current source)')
    A('')
    A(md_table(['what', 'file', 'line'], [[r['what'], r['file'], r['line'] if r['line'] else 'NOT FOUND'] for r in ref_lines]))
    A('')
    path.write_text('\n'.join(L) + '\n', encoding='utf-8', newline='\n')


if __name__ == '__main__':
    main()
