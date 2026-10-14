"""C26 resource receipt patch, assigned GPT worktree only. No build/deploy."""
from pathlib import Path
import subprocess

ROOT = Path('/opt/swg/Core3-gpt')
assert subprocess.check_output(['git', '-C', str(ROOT), 'branch', '--show-current'], text=True).strip() == 'gpt/work'
assert not subprocess.check_output(['git', '-C', str(ROOT), 'status', '--porcelain'], text=True).strip()
header = ROOT / 'MMOCoreORB/src/client/agent/AgentControl.h'
source = ROOT / 'MMOCoreORB/src/client/agent/AgentControl.cpp'


def replace(text, old, new):
    assert text.count(old) == 1, old[:80]
    return text.replace(old, new)


h = header.read_text()
h = replace(h, '\t\tstd::vector<int> ham, maxHam;', '''\t\tstd::vector<int> ham, maxHam;
\t\t// RCNO baseline 3 / delta 3: omitted from JSON until authoritative quantity arrives.
\t\tbool resourceQuantityKnown = false;
\t\tint resourceQuantity = 0;
\t\tuint64 resourceSpawnId = 0;''')
s = source.read_text()
s = replace(s, '\tstd::string type = typeName(typeCode);\n\tpack->parseFloat(); // complexity', '''\tstd::string type = typeName(typeCode);
\tif (type == "RCNO") {
\t\tstd::lock_guard<std::recursive_mutex> lock(worldMutex);
\t\tworld[oid].resourceQuantityKnown = false;
\t}
\tpack->parseFloat(); // complexity''')
s = replace(s, '\tif (type != "CREO")\n\t\treturn;\n\n\t// Rest of TangibleObjectMessage3, then CreatureObjectMessage3',
'''\tif (type != "CREO" && type != "RCNO")
\t\treturn;

\t// Rest of TangibleObjectMessage3, then CreatureObjectMessage3 or ResourceContainerObjectMessage3''')
s = replace(s, '\tpack->parseByte(); // visible\n\tint posture = pack->parseByte();', '''\tpack->parseByte(); // visible
\tif (type == "RCNO") {
\t\tint quantity = pack->parseInt();
\t\tuint64 spawnId = pack->parseLong();
\t\tstd::lock_guard<std::recursive_mutex> lock(worldMutex);
\t\tWorldObject& object = world[oid];
\t\tobject.resourceQuantity = quantity;
\t\tobject.resourceSpawnId = spawnId;
\t\tobject.resourceQuantityKnown = quantity >= 0;
\t\treturn;
\t}
\tint posture = pack->parseByte();''')
s = replace(s, 'void AgentControl::onDelta(uint64 oid, uint32 typeCode, uint8 type, Message* pack) {',
'''void AgentControl::onDelta(uint64 oid, uint32 typeCode, uint8 type, Message* pack) {
\tif (typeName(typeCode) == "RCNO" && type == 3) {
\t\tstd::lock_guard<std::recursive_mutex> lock(worldMutex);
\t\tWorldObject& object = world[oid];
\t\ttry {
\t\t\tuint16 updates = pack->parseShort();
\t\t\tfor (int u = 0; u < updates; ++u) {
\t\t\t\tif (pack->parseShort() != 0x0B) {
\t\t\t\t\t// Unknown inherited field size: do not skip bytes or retain a falsely trusted receipt.
\t\t\t\t\tobject.resourceQuantityKnown = false;
\t\t\t\t\treturn;
\t\t\t\t}
\t\t\t\tint quantity = pack->parseInt();
\t\t\t\tobject.resourceQuantity = quantity;
\t\t\t\t// A quantity-only delta cannot establish the spawn identity before its baseline.
\t\t\t\tobject.resourceQuantityKnown = quantity >= 0 && object.resourceSpawnId != 0;
\t\t\t}
\t\t} catch (...) {
\t\t\tobject.resourceQuantityKnown = false;
\t\t\tthrow;
\t\t}
\t\treturn;
\t}''')
s = replace(s, '''\t\tif (owned) items.push_back({{"oid", object.oid}, {"parent", object.parent},
\t\t\t{"type", object.type}, {"name", object.name}, {"crc", object.crc}});''', '''\t\tif (owned) {
\t\t\tJSONSerializationType item = {{"oid", object.oid}, {"parent", object.parent},
\t\t\t\t{"type", object.type}, {"name", object.name}, {"crc", object.crc}};
\t\t\tif (object.type == "RCNO" && object.resourceQuantityKnown) {
\t\t\t\titem["units"] = object.resourceQuantity;
\t\t\t\titem["resource_spawn_id"] = object.resourceSpawnId;
\t\t\t}
\t\t\titems.push_back(item);
\t\t}''')
s = replace(s, '\t\t\t\tpack->parseLong();\n\t\t\t\tpack->parseAscii(type);\n\t\t\t\tresources.push_back({{"name", str(name)}, {"type", str(type)}});',
'''\t\t\t\tuint64 resourceId = pack->parseLong();
\t\t\t\tpack->parseAscii(type);
\t\t\t\tresources.push_back({{"name", str(name)}, {"type", str(type)}, {"resource_id", resourceId}});''')
header.write_text(h)
source.write_text(s)
print('Resource telemetry prepared; unbuilt/untested C++ in gpt/work only')
