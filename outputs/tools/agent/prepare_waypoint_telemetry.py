"""C26 PLAY8 waypoint observation in assigned GPT worktree, no build/deploy."""
from pathlib import Path
import subprocess
root = Path('/opt/swg/Core3-gpt')
assert subprocess.check_output(['git', '-C', str(root), 'branch', '--show-current'], text=True).strip() == 'gpt/work'
assert not subprocess.check_output(['git', '-C', str(root), 'status', '--porcelain'], text=True).strip()


def replace(s, old, new):
    assert s.count(old) == 1, old[:80]
    return s.replace(old, new)


header = root / 'MMOCoreORB/src/client/agent/AgentControl.h'
source = root / 'MMOCoreORB/src/client/agent/AgentControl.cpp'
handler = root / 'MMOCoreORB/src/client/zone/ZonePacketHandler.cpp'
h = header.read_text()
h = replace(h, '\t\tuint64 resourceSpawnId = 0;', '''\t\tuint64 resourceSpawnId = 0;
\t\t// PLAY8 map belongs to this ghost; only export the ghost contained by self.
\t\tbool waypointsKnown = false;
\t\tuint32 waypointCounter = 0;
\t\tstd::map<uint64, JSONSerializationType> waypoints;''')
h = replace(h, '\tvoid onBaseline6(uint64 oid, uint32 typeCode, Message* pack);',
            '\tvoid onBaseline6(uint64 oid, uint32 typeCode, Message* pack);\n\tvoid onBaseline8(uint64 oid, uint32 typeCode, Message* pack);')
s = source.read_text()
anchor = 'static std::string missionTypeName(uint32 crc) {'
helpers = '''// PlayerObjectMessage8 begins with an XP DeltaVectorMap<String,int>, including op bytes.
static void skipAgentExperienceMap(Message* pack) {
\tuint32 count = pack->parseInt();
\tpack->parseInt();
\tif (count > 1000) throw std::runtime_error("oversized experience map");
\tfor (uint32 i = 0; i < count; ++i) {
\t\tpack->parseByte();
\t\tString key;
\t\tpack->parseAscii(key);
\t\tpack->parseInt();
\t}
}

// WaypointObjectImplementation::insertToMessage, not a SceneObject baseline.
static JSONSerializationType readAgentWaypoint(Message* pack, uint64 key) {
\tuint32 cell = pack->parseInt();
\tfloat x = pack->parseFloat(), z = pack->parseFloat(), y = pack->parseFloat();
\tpack->parseLong();
\tuint32 planetCRC = pack->parseInt();
\tUnicodeString name;
\tpack->parseUnicode(name);
\tuint64 oid = pack->parseLong();
\tuint8 color = pack->parseByte(), active = pack->parseByte();
\tif (oid != key) throw std::runtime_error("waypoint key mismatch");
\treturn {{"oid", oid}, {"cell", cell}, {"x", x}, {"y", y}, {"z", z},
\t\t{"planet", planetName(planetCRC)}, {"planet_crc", planetCRC},
\t\t{"name", str(name.toString())}, {"color", color}, {"active", active != 0}};
}

void AgentControl::onBaseline8(uint64 oid, uint32 typeCode, Message* pack) {
\tif (typeName(typeCode) != "PLAY") return;
\tstd::lock_guard<std::recursive_mutex> lock(worldMutex);
\tWorldObject& object = world[oid];
\tobject.oid = oid;
\tobject.type = "PLAY";
\tobject.waypointsKnown = false;
\tskipAgentExperienceMap(pack);
\tuint32 count = pack->parseInt(), counter = pack->parseInt();
\tif (count > 1000) throw std::runtime_error("oversized waypoint map");
\tstd::map<uint64, JSONSerializationType> fresh;
\tfor (uint32 i = 0; i < count; ++i) {
\t\tif (pack->parseByte() != 0) throw std::runtime_error("unexpected waypoint baseline operation");
\t\tuint64 key = pack->parseLong();
\t\tfresh[key] = readAgentWaypoint(pack, key);
\t}
\tobject.waypoints = fresh;
\tobject.waypointCounter = counter;
\tobject.waypointsKnown = true;
}

'''
s = replace(s, anchor, helpers + anchor)
s = replace(s, 'void AgentControl::onDelta(uint64 oid, uint32 typeCode, uint8 type, Message* pack) {',
'''void AgentControl::onDelta(uint64 oid, uint32 typeCode, uint8 type, Message* pack) {
\tif (typeName(typeCode) == "PLAY" && type == 8) {
\t\tstd::lock_guard<std::recursive_mutex> lock(worldMutex);
\t\tWorldObject& object = world[oid];
\t\ttry {
\t\t\tuint16 updates = pack->parseShort();
\t\t\tfor (int u = 0; u < updates; ++u) {
\t\t\t\tuint16 index = pack->parseShort();
\t\t\t\tif (index == 0) { skipAgentExperienceMap(pack); continue; }
\t\t\t\tif (index == 2 || index == 3) { pack->parseInt(); continue; }
\t\t\t\tif (index != 1) { object.waypointsKnown = false; return; }
\t\t\t\tuint32 count = pack->parseInt(), counter = pack->parseInt();
\t\t\t\tif (count > 1000) throw std::runtime_error("oversized waypoint delta");
\t\t\t\tbool consecutive = counter == object.waypointCounter + count;
\t\t\t\tauto fresh = object.waypoints;
\t\t\t\tfor (uint32 i = 0; i < count; ++i) {
\t\t\t\t\tuint8 op = pack->parseByte();
\t\t\t\t\tuint64 key = pack->parseLong();
\t\t\t\t\tauto waypoint = readAgentWaypoint(pack, key); // drop also serializes the value
\t\t\t\t\tif (op == 1) fresh.erase(key);
\t\t\t\t\telse if (op == 0 || op == 2) fresh[key] = waypoint;
\t\t\t\t\telse throw std::runtime_error("unknown waypoint delta operation");
\t\t\t\t}
\t\t\t\tobject.waypoints = fresh;
\t\t\t\tobject.waypointCounter = counter;
\t\t\t\tobject.waypointsKnown = object.waypointsKnown && consecutive;
\t\t\t}
\t\t} catch (...) { object.waypointsKnown = false; throw; }
\t\treturn;
\t}''')
s = replace(s, '\treturn result;\n}\n\nJSONSerializationType AgentControl::look(',
'''\tfor (const auto& entry : world) {
\t\tconst WorldObject& ghost = entry.second;
\t\tif (ghost.type != "PLAY" || ghost.parent != self || !ghost.waypointsKnown) continue;
\t\tJSONSerializationType points = JSONSerializationType::array();
\t\tfor (const auto& waypoint : ghost.waypoints) points.push_back(waypoint.second);
\t\tresult["waypoints"] = points;
\t\tbreak;
\t}
\treturn result;
}

JSONSerializationType AgentControl::look(''')
z = handler.read_text()
z = replace(z, 'if ((type == 1 || type == 3 || type == 6) && AgentControl::get() != nullptr)',
            'if ((type == 1 || type == 3 || type == 6 || type == 8) && AgentControl::get() != nullptr)')
z = replace(z, '\t\t\telse\n\t\t\t\tAgentControl::get()->onBaseline6(oid, nametype, pack);',
'''\t\t\telse if (type == 6)
\t\t\t\tAgentControl::get()->onBaseline6(oid, nametype, pack);
\t\t\telse
\t\t\t\tAgentControl::get()->onBaseline8(oid, nametype, pack);''')
header.write_text(h)
source.write_text(s)
handler.write_text(z)
print('Waypoint telemetry prepared; unbuilt/untested C++')
