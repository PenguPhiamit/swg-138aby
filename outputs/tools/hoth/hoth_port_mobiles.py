"""Hoth creatures slice: port Bellum Gero's ordinary Hoth mobiles, lairs and world spawn group into the dev tree.

Inside Debian, as swgemu (writes LF files in /opt/swg/Core3-dev only):
    python3 /mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/tools/hoth/hoth_port_mobiles.py [--dry-run]

Source: Bellum Gero (github.com/Miphstoe/BellumGero-Live) at 1f4438a1, AGPL-3.0, pinned in work/research.
What it does (C12 slice "ordinary creature definitions -> verified outdoor spawns"):
  - mobile/hoth/hoth_*.lua: copied with stats, levels and attacks as published (owner, 14 Oct: keep Bellum's endgame
    levels). Loot groups our server doesn't define are removed (Bellum's tokens, jedi_robe, the hoth_* reward groups;
    their reward chains are a later slice). The glacial rancor world boss is left out: its body
    (object/mobile/exotic_rancor.iff) is in no archive our client loads.
  - mobile/lair/{creature_dynamic,creature_lair,npc_dynamic}/hoth/*.lua and mobile/spawn/hoth/hoth_world.lua: copied.
  - Registration: one include each in mobile/serverobjects.lua, the three lair serverobjects files and
    spawn/serverobjects.lua, and a world-spawner region in managers/planet/hoth_regions.lua (only loaded where
    ZonesEnabled lists hoth).
Each copied file starts with a notice naming the source, its licence and what changed. Re-running is safe: files are
rewritten from the source and registrations are added only once.
"""
import re, sys
from pathlib import Path

SRC = Path('/mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/work/research/Miphstoe_BellumGero-Live/MMOCoreORB/bin/scripts')
DST = Path('/opt/swg/Core3-dev/MMOCoreORB/bin/scripts')
REV = '1f4438a1'
LEAVE_OUT = {'hoth_glacial_rancor'}
DRY = '--dry-run' in sys.argv


def notice(rel, changes):
    return (f'-- Adapted from Bellum Gero (github.com/Miphstoe/BellumGero-Live, revision {REV}, AGPL-3.0),\n'
            f'-- MMOCoreORB/bin/scripts/{rel}. Ported to this server 14 Oct 2026 (Claude; see outputs/Documentation-support/hoth-port-log.md).\n'
            + ''.join(f'-- {c}\n' for c in changes) + '\n')


def block_end(text, start):
    """Index just past the '}' matching the '{' at text[start]."""
    depth, i = 0, start
    while True:
        depth += {'{': 1, '}': -1}.get(text[i], 0)
        i += 1
        if depth == 0:
            return i


def strip_loot(text, known):
    """Remove lootGroups entries that name a group we don't have. Returns (text, removed group names)."""
    m = re.search(r'lootGroups\s*=\s*\{', text)
    if not m:
        return text, []
    open_at = m.end() - 1
    close_at = block_end(text, open_at)
    body = text[open_at + 1:close_at - 1]
    entries, i = [], 0
    while True:
        j = body.find('{', i)
        if j < 0:
            break
        k = block_end(body, j)
        entries.append(body[j:k])
        i = k
    kept, removed = [], []
    for e in entries:
        groups = re.findall(r'group\s*=\s*"([^"]+)"', e)
        missing = [g for g in groups if g not in known]
        (removed.extend(missing) if missing else kept.append(e))
    indent = '\n\t\t'
    new_body = ('{' + ','.join(indent + e for e in kept) + '\n\t}') if kept else '{}'
    return text[:open_at] + new_body + text[close_at:], sorted(set(removed))


def write(path, text):
    if DRY:
        print(f'would write {path.relative_to(DST)} ({len(text)} bytes)')
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding='utf-8', newline='\n')
    print(f'wrote {path.relative_to(DST)}')


def add_once(path, marker, addition, after=None):
    text = path.read_text(encoding='utf-8')
    if marker in text:
        print(f'already in {path.relative_to(DST)}: {marker}')
        return
    if after:
        assert text.count(after) == 1, (path, after)
        text = text.replace(after, after + addition)
    else:
        text = text.rstrip('\n') + '\n' + addition
    if DRY:
        print(f'would add to {path.relative_to(DST)}: {addition.strip()[:90]}')
        return
    path.write_text(text, encoding='utf-8', newline='\n')
    print(f'added to {path.relative_to(DST)}: {addition.strip()[:90]}')


def main():
    known = set()
    for f in (DST / 'loot').rglob('*.lua'):
        known.update(re.findall(r'addLootGroupTemplate\("([^"]+)"', f.read_text(encoding='utf-8', errors='replace')))
    print(f'{len(known)} loot groups defined in dev')

    ported = []
    for f in sorted((SRC / 'mobile/hoth').glob('hoth_*.lua')):
        name = f.stem
        if name in LEAVE_OUT:
            print(f'left out {name}')
            continue
        text, removed = strip_loot(f.read_text(encoding='utf-8'), known)
        changes = [f'Changed: removed loot groups this server lacks: {", ".join(removed)}.'] if removed else ['Unchanged.']
        write(DST / 'mobile/hoth' / f.name, notice(f'mobile/hoth/{f.name}', changes) + text.lstrip('﻿'))
        ported.append(f.name)
    reg = ''.join(f'includeFile("hoth/{n}")\n' for n in ported)
    write(DST / 'mobile/hoth/serverobjects.lua',
          notice('mobile/hoth/serverobjects.lua', [f'Changed: {", ".join(sorted(LEAVE_OUT))} left out (client lacks its body).']) + reg)

    lair_includes = {}
    for kind in ('creature_dynamic', 'creature_lair', 'npc_dynamic'):
        for f in sorted((SRC / 'mobile/lair' / kind / 'hoth').glob('*.lua')):
            rel = f'mobile/lair/{kind}/hoth/{f.name}'
            write(DST / rel, notice(rel, ['Unchanged.']) + f.read_text(encoding='utf-8'))
            lair_includes.setdefault(kind, []).append(f'includeFile("lair/{kind}/hoth/{f.name}")\n')
    rel = 'mobile/spawn/hoth/hoth_world.lua'
    write(DST / rel, notice(rel, ['Unchanged.']) + (SRC / rel).read_text(encoding='utf-8'))

    add_once(DST / 'mobile/serverobjects.lua', 'includeFile("hoth/serverobjects.lua")',
             'includeFile("hoth/serverobjects.lua") -- Sandbox: Hoth creatures (Bellum Gero, AGPL-3.0)\n',
             after='includeFile("herald/serverobjects.lua")\n')
    for kind, lines in lair_includes.items():
        add_once(DST / f'mobile/lair/{kind}/serverobjects.lua', lines[0].strip(),
                 '\n-- Sandbox: Hoth (Bellum Gero, AGPL-3.0)\n' + ''.join(lines))
    add_once(DST / 'mobile/spawn/serverobjects.lua', 'includeFile("spawn/hoth/hoth_world.lua")',
             '\n-- Sandbox: Hoth world spawns (Bellum Gero, AGPL-3.0)\nincludeFile("spawn/hoth/hoth_world.lua")\n')
    add_once(DST / 'managers/planet/hoth_regions.lua', '{"hoth_world_spawner"',
             '\n\t-- World spawner: lairs, herds and patrols from mobile/spawn/hoth/hoth_world.lua (as Bellum Gero, 1024 at most).\n'
             '\t-- Outside the outpost (CITY + NOSPAWNAREA, 200 m) and the no-spawn edges.\n'
             '\t{"hoth_world_spawner", 0, 0, {RECTANGLE, 0, 0}, SPAWNAREA + WORLDSPAWNAREA, {"hoth_world"}, 1024},\n',
             after='\t{"hoth_ice_caves_nobuild", -400, 2600, {CIRCLE, 450}, NOBUILDZONEAREA},\n')


if __name__ == '__main__':
    main()
