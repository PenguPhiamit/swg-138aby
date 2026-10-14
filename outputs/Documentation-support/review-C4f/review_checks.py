"""Read-only C4f checks. Writes evidence/scratch only inside this review directory."""
from pathlib import Path
import hashlib
import importlib.util
import json
import re
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.dont_write_bytecode = True

def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj

def wsl(*args):
    return subprocess.check_output(['wsl', '-d', 'Debian', '-u', 'swgemu', '--', *args])

def capture():
    records = []
    for patch in sorted(HERE.glob('000*.patch')):
        commit = patch.read_text(encoding='utf-8').split()[1]
        paths = re.findall(r'^diff --git a/(.*?) b/', patch.read_text(encoding='utf-8'), re.M)
        for path in paths:
            blob = wsl('git', '-C', '/opt/swg/Core3-dev', 'show', commit + ':' + path)
            out = HERE / 'sources' / commit[:8] / path
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_bytes(blob)
            records.append({'commit': commit, 'path': path, 'sha256': hashlib.sha256(blob).hexdigest()})
    context = [
        'src/server/zone/managers/resource/resourcespawner/resourcetree/ResourceTree.cpp',
        'src/server/zone/managers/resource/resourcespawner/resourcetree/ResourceTreeNode.cpp',
        'src/server/zone/managers/creature/SpawnAreaMap.h',
        'src/server/zone/objects/region/SpawnAreaImplementation.cpp',
        'src/server/zone/managers/objectcontroller/ObjectControllerImplementation.cpp',
        'src/server/zone/managers/objectcontroller/command/CommandConfigManager.cpp',
        'src/server/zone/objects/creature/commands/QueueCommand.h',
        'src/server/zone/objects/creature/variables/Skill.h',
        'src/server/zone/managers/skill/SkillManager.cpp',
        'src/server/zone/objects/tangible/TangibleObject.idl',
        'src/templates/crcstringtable/CrcStringTable.cpp',
        'src/server/zone/GroundZoneContainerComponent.cpp',
        'src/server/zone/managers/creature/CreatureManagerImplementation.cpp',
        'src/server/zone/managers/creature/SpawnAreaMap.cpp',
        'src/server/zone/objects/tangible/deed/vehicle/VehicleDeedImplementation.cpp',
        'bin/scripts/object/custom_content/tangible/deed/vehicle_deed/landspeeder_ab1_deed.lua',
        'src/templates/tangible/VehicleDeedTemplate.h',
        'src/templates/LootItemTemplate.h',
        'src/server/zone/objects/tangible/deed/vehicle/VehicleDeed.idl',
        'src/server/zone/managers/loot/LootManagerImplementation.cpp',
        'src/server/zone/managers/loot/LootValues.cpp',
        'src/server/zone/objects/tangible/TangibleObjectImplementation.cpp',
        'src/server/zone/objects/area/events/ActiveAreaEvent.cpp',
        'utils/engine3/MMOEngine/src/system/util/SynchronizedVectorMap.h',
        'utils/engine3/MMOEngine/src/engine/core/ManagedObject.cpp',
        'src/autogen/server/zone/objects/region/SpawnArea.cpp',
    ]
    head = wsl('git', '-C', '/opt/swg/Core3-dev', 'rev-parse', 'HEAD').decode().strip()
    for path in context:
        full = '/opt/swg/Core3-dev/MMOCoreORB/' + path
        try:
            blob = wsl('cat', full)
        except subprocess.CalledProcessError:
            continue
        out = HERE / 'context' / path
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(blob)
        records.append({'context_at_head': head, 'path': full, 'sha256': hashlib.sha256(blob).hexdigest()})
    for rel in ['tools/hoth/hoth_client_build.py', 'tools/test_galaxy.py',
                'tools/hoth/hoth_port_loot.py', 'tools/hoth/hoth_loot_inventory.py',
                'tools/hoth/hoth_loot_core3_check.py', 'tools/owner_content/botanist_server.py']:
        blob = (ROOT / 'outputs' / rel).read_bytes()
        out = HERE / 'tool-snapshot' / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(blob)
        records.append({'tool': rel, 'sha256': hashlib.sha256(blob).hexdigest()})
    return records

def effective(rows):
    """Port of Core3 ResourceTree's carried columns/class stack, without spawning."""
    classes, stfs, container, random_name = [], [], '', ''
    out = {}
    for row in rows[1:]:
        for j in range(3, 10):
            if not row[j]:
                continue
            while len(classes) > j - 3:
                classes.pop(j - 3)
                stfs.pop(j - 3)
            classes.append(row[j])
            stfs.append(row[1])
        container = row[49] or container
        random_name = row[50] or random_name
        out[row[1]] = [list(classes), list(stfs), container, random_name]
    return out

def checks():
    build = module('c4f_build', ROOT / 'outputs/tools/hoth/hoth_client_build.py')
    port = module('c4f_port', ROOT / 'outputs/tools/hoth/hoth_port_loot.py')
    results = {}
    stage = Path(build.STAGE)
    protected = [p for p in stage.rglob('*') if p.is_file()] + [Path(build.TRE)]
    before = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in protected}
    with tempfile.TemporaryDirectory(prefix='scratch-', dir=HERE) as scratch:
        temp = Path(scratch)
        def destination(path):
            out = temp / path
            out.parent.mkdir(parents=True, exist_ok=True)
            return str(out)
        build.dst = destination
        # Existing baselines only: any attempted new baseline is redirected to scratch.
        original_src = build.src
        build.src = lambda path: original_src(path) if Path(original_src(path)).exists() else destination('base/' + path)
        results['object_crc_report'] = build.object_crc_table()
        crc_path = 'misc/object_template_crc_string_table.iff'
        table = build.cstb_tool.read(destination(crc_path))
        results['crc_hash_mismatches'] = [name for name, crc in table.items() if build.cstb_tool.soe_crc(name.lower()) != crc]
        results['crc_sorted'] = list(table.values()) == sorted(table.values())
        results['crc_matches_staged'] = Path(destination(crc_path)).read_bytes() == (stage / crc_path).read_bytes()
        results['resource_report'] = build.resource_tree()
        resource_path = 'datatables/resource/resource_tree.iff'
        stock = build.dt_tool.read(original_src(resource_path))
        merged = build.dt_tool.read(destination(resource_path))
        old, new = effective(stock['rows']), effective(merged['rows'])
        results['stock_effective_resource_changes'] = [name for name in old if old[name] != new[name]]
        results['hoth_resource_effective'] = {name: value for name, value in new.items() if name.endswith('_hoth')}
        results['resources_match_staged'] = Path(destination(resource_path)).read_bytes() == (stage / resource_path).read_bytes()
        results['count_column_changes'] = [[r[1], r[10:12], merged['rows'][next(i for i, x in enumerate(merged['rows']) if x[1] == r[1])][10:12]] for r in stock['rows'] if r[10:12] != merged['rows'][next(i for i, x in enumerate(merged['rows']) if x[1] == r[1])][10:12]]
        # Inspect current load order but expose only archive names and command rows.
        results['current_skill_winner'] = build.winning('datatables/skill/skills.iff')[0]
        results['botanist_clean_report'] = build.botanist()
        results['botanist_clean_matches_staged'] = all(Path(destination(path)).read_bytes() == (stage / path).read_bytes()
            for path in ['datatables/skill/skills.iff', *build.BOTANIST_STRINGS])
        for path in ['datatables/command/command_table.iff', 'datatables/command/command_table_ground.iff']:
            raw = build.swg_client_data.client_file(path)
            if raw:
                results[path] = [r for r in build.swg_client_data.datatable(raw) if any(str(v).lower() in ('spawnstatus', 'showspawnregion') for v in r.values())]
        # Execute Botanist against its own prior output in isolated scratch, as when a test-session archive wins.
        build.winning = lambda path: ('local_planets.tre', (stage / path).read_bytes())
        try:
            build.botanist()
            results['botanist_repeat'] = 'unexpected success'
        except AssertionError as exc:
            results['botanist_repeat'] = {'exception': type(exc).__name__, 'message': str(exc), 'root_already_present': True}
        # Skill defaults and Botanist's inserted rows from the actual staged output.
        skill = build.dt_tool.read(str(stage / 'datatables/skill/skills.iff'))
        results['skill_schema'] = list(zip(skill['names'], skill['types']))
        results['botanist_rows'] = [dict(zip(skill['names'], r)) for r in skill['rows'] if str(r[0]).startswith('outdoors_botanist')]
        # add_drop against all actual mobile before/after snapshots.
        c = 'b7f03b0e'
        root = HERE / 'sources' / c / 'MMOCoreORB/bin/scripts'
        loot_groups = {}
        for path in (root / 'loot/groups/hoth').glob('*.lua'):
            weights = [int(v) for v in re.findall(r'weight = (\d+)', path.read_text())]
            loot_groups[path.stem] = {'items': len(weights), 'total': sum(weights), 'range': [min(weights), max(weights)]}
        results['loot_weights'] = loot_groups
        missing_crcs = []
        for path in (root / 'loot/items/hoth').glob('*.lua'):
            name = re.search(r'directObjectTemplate = "([^"]+)"', path.read_text()).group(1)
            head, tail = name.rsplit('/', 1)
            shared = head + '/shared_' + tail
            if shared not in table:
                missing_crcs.append([path.name, shared])
        results['loot_shared_crc_missing'] = missing_crcs
        failures = []
        for path in (root / 'mobile/hoth').glob('*.lua'):
            rel = 'MMOCoreORB/bin/scripts/mobile/hoth/' + path.name
            old_text = wsl('git', '-C', '/opt/swg/Core3-dev', 'show', c + '^:' + rel).decode()
            expected = old_text
            for group, mobs, chance in port.TIERS:
                if path.stem in mobs:
                    expected, _ = port.add_drop(expected, group, chance)
            def body(text):
                start = re.search(r'lootGroups\s*=\s*\{', text).end() - 1
                return text[start:port.block_end(text, start)]
            if body(expected) != body(path.read_text(encoding='utf-8')):
                failures.append(path.name)
            repeat, changed = port.add_drop(expected, next(g for g, ms, ch in port.TIERS if path.stem in ms), 300000)
            if changed or repeat != expected:
                failures.append(path.name + ': not idempotent')
        results['loot_mobile_reconstruction_failures'] = failures
        results['loot_mobile_count'] = len(list((root / 'mobile/hoth').glob('*.lua')))
    after = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in protected}
    results['staged_files_unchanged'] = before == after
    return results

if __name__ == '__main__':
    records = capture()
    results = checks()
    (HERE / 'source-manifest.json').write_text(json.dumps(records, indent=2) + '\n', encoding='utf-8')
    (HERE / 'offline-results.json').write_text(json.dumps(results, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in results.items() if k not in ('hoth_resource_effective', 'skill_schema', 'count_column_changes', 'botanist_rows')}, indent=2))
