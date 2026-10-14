"""Static review evidence plus a Python model of the null-triangle counterexample.
This does not compile C++, load a map or test the running galaxy.
"""
import hashlib
import json
import re
from pathlib import Path

root = Path(__file__).resolve().parent
pf = (root / 'files/context/PathFinderManager.cpp').read_text()
floor = pf.split('int PathFinderManager::getFloorPath(', 1)[1].split('Vector3 PathFinderManager::transformToModelSpace', 1)[0]
assert floor.index('objectFloor == targetFloor') < floor.index('objectFloor == nullptr')
leash = (root / 'files/LeashCommand.h').read_text()
assert 'bool found = result == -1 ||' in leash
# Model exactly the relevant decision ordering; both failed lookups compare equal.
def floor_result(a, b):
    if a is b:
        return -1
    if a is None or b is None:
        return 1
    return 0
assert floor_result(None, None) == -1
assert floor_result(None, object()) == 1
body = (root / 'files/AgentControl.cpp').read_text()
move = body.split('JSONSerializationType AgentControl::moveTo(', 1)[1].split('JSONSerializationType AgentControl::sceneChanged', 1)[0]
assert 'sceneGeneration' not in move
assert 'sendTransform(heading, speed)' in move
mobile = root / 'files/c402e480/MMOCoreORB/bin/scripts/mobile'
creatures = set()
lairs = set()
for path in mobile.rglob('*.lua'):
    text = path.read_text()
    creatures.update(re.findall(r'addCreatureTemplate\([^,]+,\s*"([^"]+)"', text))
    lairs.update(re.findall(r'addLairTemplate\("([^"]+)"', text))
spawn = (mobile / 'spawn/hoth/hoth_world.lua').read_text()
spawn_refs = set(re.findall(r'lairTemplateName\s*=\s*"([^"]+)"', spawn))
assert spawn_refs <= lairs
result = dict(evidence='source assertions and Python model only; no C++/runtime execution',
    null_triangles_return_minus_one=True, on_floor_accepts_minus_one=True,
    straight_move_missing_scene_generation=True, creatures=len(creatures), lairs=len(lairs),
    world_spawn_refs=len(spawn_refs), missing_spawn_lairs=sorted(spawn_refs-lairs),
    files=[dict(path=str(p.relative_to(root)), sha256=hashlib.sha256(p.read_bytes()).hexdigest())
           for p in sorted((root/'files').rglob('*')) if p.is_file()])
(root/'offline-results.json').write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='files'}, indent=2))
