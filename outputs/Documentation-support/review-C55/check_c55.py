"""Read-only pinned source/data checks; never contacts the galaxy or writes under /opt/swg."""
import collections
import json
from pathlib import Path
import re
import shutil
import subprocess

ROOT = Path('/opt/swg/Core3-dev')
OUT = Path(__file__).resolve().parent
PINS = ['b20a46d7', '40af2c78', '64156084', '74fa3e8c', '3dca6772', '61f5d886', '26b54813']
ENV = dict(__import__('os').environ, GIT_OPTIONAL_LOCKS='0')
def git(*args):
    return subprocess.check_output(['git', '-C', str(ROOT), *args], env=ENV, text=True)
def show(pin, path):
    return git('show', pin + ':' + path)

luac = shutil.which('luac5.3') or shutil.which('luac')
assert luac, 'Lua compiler required'
result = {'head_start': git('rev-parse', 'HEAD').strip(), 'pins': {}, 'lua': [], 'city_proposals': {}, 'references': [], 'spawn_gate': {}}
paths = set()
for pin in PINS:
    changed = git('diff-tree', '--no-commit-id', '--name-only', '-r', pin).splitlines()
    result['pins'][pin] = {'full_hash': git('rev-parse', pin).strip(), 'changed_files': changed}
    for path in changed:
        if path.endswith('.lua'):
            paths.add(path)
            proc = subprocess.run([luac, '-p', '-'], input=show(pin, path), text=True, capture_output=True)
            result['lua'].append({'pin': pin, 'path': path, 'returncode': proc.returncode, 'error': proc.stderr})
for path in sorted(paths):
    proc = subprocess.run([luac, '-p', '-'], input=show('HEAD', path), text=True, capture_output=True)
    result['lua'].append({'pin': result['head_start'], 'path': path, 'returncode': proc.returncode, 'error': proc.stderr})

# Resolve every newly referenced lair/mobile against tracked source at the introducing commit.
for pin in ['b20a46d7', '64156084']:
    tree = git('ls-tree', '-r', '--name-only', pin, 'MMOCoreORB/bin/scripts/mobile').splitlines()
    by_name = collections.defaultdict(list)
    for path in tree:
        by_name[Path(path).stem].append(path)
    diff = git('show', '--format=', pin)
    for line in diff.splitlines():
        if not line.startswith('+') or line.startswith('+++'):
            continue
        names = re.findall(r'lairTemplateName = "([^"]+)"|spawnMobile\(self.planet, "([^"]+)"|mobiles = \{\{"([^"]+)"', line)
        for match in names:
            name = next(v for v in match if v)
            candidates = by_name[name]
            assert candidates, (pin, name)
            source = show(pin, candidates[0])
            result['references'].append({'pin': pin, 'name': name, 'path': candidates[0], 'level': re.findall(r'level\s*=\s*(\d+)', source)})

unique = {}
for row in result['references']:
    key = (row['pin'], row['name'])
    if key not in unique:
        unique[key] = dict(row, mentions=0)
    unique[key]['mentions'] += 1
result['references'] = list(unique.values())

proposal = (OUT.parents[1] / 'Bot-reports/launch-sim/city-spawn-proposals.patch').read_text()
actual = git('show', '--format=', '64156084')
def added_content(diff):
    return collections.Counter(line[1:] for line in diff.splitlines() if line.startswith('+') and not line.startswith('+++') and ('spawnMobile(' in line or 'lairTemplateName =' in line))
assert added_content(proposal) == added_content(actual), 'proposals differ from committed additions'
removed = lambda diff: collections.Counter(line[1:] for line in diff.splitlines() if line.startswith('-') and not line.startswith('---') and 'lairTemplateName =' in line)
assert removed(proposal) == removed(actual), 'proposal removals differ'
result['proposal_added_rows_match'] = True
result['proposal_removed_lair_rows_match'] = True
for city in ['corellia_coronet', 'corellia_tyrena', 'talus_dearic', 'talus_nashal', 'naboo_kaadara']:
    path = 'MMOCoreORB/bin/scripts/screenplays/cities/' + city + '.lua'
    patch = git('show', '--format=', '64156084', '--', path)
    result['city_proposals'][city] = sum(line.startswith('+') and 'spawnMobile(' in line for line in patch.splitlines())

path = 'MMOCoreORB/bin/scripts/mobile/spawn/tatooine/tatooine_hard_krayt_ne.lua'
text = show('b20a46d7', path)
rows = [(n, int(d)) for n, d in re.findall(r'lairTemplateName = "([^"]+)".*?minDifficulty = (\d+)', text, re.S)]
result['spawn_gate'] = {'base': 10, 'solo_max': 25, 'solo_threshold': 85, 'krayt_rows': rows, 'solo_rejected': [n for n, d in rows if d > 85]}
assert len(rows) == len(result['spawn_gate']['solo_rejected']) == 4
result['head_end'] = git('rev-parse', 'HEAD').strip()
result['lua_invocations'] = len(result['lua'])
result['distinct_lua_files'] = len(paths)
result['lua_failures'] = [row for row in result['lua'] if row['returncode']]
assert not result['lua_failures']
(OUT/'checks.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({key: result[key] for key in ['head_start','head_end','lua_invocations','distinct_lua_files','lua_failures','city_proposals','spawn_gate']}, indent=2))
