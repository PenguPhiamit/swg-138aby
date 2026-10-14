"""Prepare a reviewable client patch locally; never edits or runs /opt/swg."""
from pathlib import Path
import difflib
import shutil

ROOT = Path(__file__).resolve().parent
FILES = {'AgentControl.h': 'client/agent/AgentControl.h',
         'AgentControl.cpp': 'client/agent/AgentControl.cpp',
         'ZonePacketHandler.cpp': 'client/zone/ZonePacketHandler.cpp'}
for name in FILES:
    base = ROOT / (name + '.base')
    if not base.exists():
        shutil.copyfile(ROOT / name, base)

def replace(text, old, new):
    assert text.count(old) == 1, old[:100]
    return text.replace(old, new, 1)

h = (ROOT/'AgentControl.h.base').read_text(encoding='utf-8-sig')
h = replace(h, '\tvoid onObjController(uint32 type, uint64 oid, Message* pack);',
'''\tvoid onObjController(uint32 type, uint64 oid, Message* pack);
\tbool onStandalonePacket(uint32 opcode, Message* pack);''')
h = replace(h, '\tstd::vector<std::string> conversationOptions;',
'''\tbool conversationActive = false;
\tuint64 conversationNpc = 0;
\tuint8 radialCounter = 0;
\tstd::map<uint64, JSONSerializationType> radialMenus;
\tstd::map<uint32, JSONSerializationType> suiPages;
\tJSONSerializationType inventorySnapshot();
\tstd::vector<std::string> conversationOptions;''')

c = (ROOT/'AgentControl.cpp.base').read_text(encoding='utf-8-sig')
c = replace(c, '\t\tself = oid;', '''\t\tself = oid;
\t\tradialMenus.clear(); suiPages.clear(); conversationOptions.clear();
\t\tconversationActive = false; conversationNpc = 0;''')
c = replace(c, '\t\tworld.erase(it);', '\t\tradialMenus.erase(oid);\n\t\tworld.erase(it);')
c = replace(c, '\tcase 0xDD: // NPC conversation started\n\t\temit({{"event", "conversation_start"}, {"npc_oid", pack->parseLong()}});',
'''\tcase 0xDD: // NPC conversation started
\t\tconversationNpc = pack->parseLong();
\t\tconversationActive = true;
\t\temit({{"event", "conversation_start"}, {"npc_oid", conversationNpc}});''')
c = replace(c, '\t\tconversationOptions.clear();\n\t\temit({{"event", "conversation_end"}});',
'''\t\tconversationOptions.clear();
\t\tconversationActive = false;
\t\tconversationNpc = 0;
\t\temit({{"event", "conversation_end"}});''')
c = replace(c, '\tcase 0xDF: { // NpcConversationMessage\n\t\tUnicodeString message;\n\t\tpack->parseUnicode(message);\n\t\temit({{"event", "npc_says"}, {"text", str(message.toString())}});',
'''\tcase 0xDF: { // NpcConversationMessage: Unicode or embedded StringId parameters
\t\tint offset = pack->getOffset();
\t\tUnicodeString message;
\t\tpack->parseUnicode(message);
\t\tstd::string text = str(message.toString());
\t\tif (text.empty() && offset + 12 <= pack->size()) {
\t\t\tpack->setOffset(offset);
\t\t\tpack->parseInt(); // encoded UTF-16-length wrapper
\t\t\tpack->parseShort();
\t\t\tString file, key;
\t\t\tpack->parseAscii(file); pack->parseInt(); pack->parseAscii(key);
\t\t\tif (!file.isEmpty() && !key.isEmpty()) text = "@" + str(file) + ":" + str(key);
\t\t}
\t\temit({{"event", "npc_says"}, {"text", text}});''')
# Incoming menus are server-provided; selection below is restricted to these IDs.
c = replace(c, '\tcase 0xF4: { // SpatialChat', '''\tcase 0x147: { // ObjectMenuResponse (header's trailing int already consumed)
\t\tuint64 target = pack->parseLong();
\t\tpack->parseLong();
\t\tuint32 count = pack->parseInt();
\t\tif (count > 256) throw std::runtime_error("oversized radial menu");
\t\tJSONSerializationType items = JSONSerializationType::array();
\t\tfor (uint32 i = 0; i < count; ++i) {
\t\t\tuint8 index = pack->parseByte(), parent = pack->parseByte();
\t\t\tuint8 radial = pack->parseByte(), callback = pack->parseByte();
\t\t\tUnicodeString label; pack->parseUnicode(label);
\t\t\titems.push_back({{"index", index}, {"parent", parent}, {"radial_id", radial},
\t\t\t\t{"callback", callback}, {"label", str(label.toString())}});
\t\t}
\t\tuint8 counter = pack->parseByte();
\t\t{ std::lock_guard<std::recursive_mutex> lock(worldMutex); radialMenus[target] = items; }
\t\temit({{"event", "radial_menu"}, {"target", target}, {"counter", counter}, {"items", items}});
\t\tbreak;
\t}
\tcase 0xF4: { // SpatialChat''')
c = replace(c, 'JSONSerializationType AgentControl::status() {', r'''
bool AgentControl::onStandalonePacket(uint32 opcode, Message* pack) {
    if (opcode != 0xD44B7259) return false; // SuiCreatePageMessage
    try {
        uint32 page = pack->parseInt(); String script; pack->parseAscii(script);
        uint32 count = pack->parseInt();
        if (count > 4096) throw std::runtime_error("oversized SUI command list");
        JSONSerializationType commands = JSONSerializationType::array();
        for (uint32 i = 0; i < count; ++i) {
            uint8 kind = pack->parseByte();
            uint32 wideCount = pack->parseInt();
            if (wideCount > 256) throw std::runtime_error("oversized SUI wide list");
            JSONSerializationType wide = JSONSerializationType::array(), narrow = JSONSerializationType::array();
            for (uint32 n = 0; n < wideCount; ++n) { UnicodeString v; pack->parseUnicode(v); wide.push_back(str(v.toString())); }
            uint32 narrowCount = pack->parseInt();
            if (narrowCount > 256) throw std::runtime_error("oversized SUI narrow list");
            for (uint32 n = 0; n < narrowCount; ++n) { String v; pack->parseAscii(v); narrow.push_back(str(v)); }
            commands.push_back({{"kind", kind}, {"wide", wide}, {"narrow", narrow}});
        }
        uint64 target = pack->parseLong(); float distance = pack->parseFloat(); pack->parseLong();
        JSONSerializationType data = {{"page_id", page}, {"script", str(script)},
            {"target", target}, {"close_distance", distance}, {"commands", commands}};
        { std::lock_guard<std::recursive_mutex> lock(worldMutex); suiPages[page] = data; }
        emit({{"event", "sui_page"}, {"page", data}});
    } catch (...) { emit({{"event", "packet_parse_error"}, {"packet", "SuiCreatePageMessage"}}); }
    return true;
}

JSONSerializationType AgentControl::inventorySnapshot() {
    std::lock_guard<std::recursive_mutex> lock(worldMutex);
    JSONSerializationType items = JSONSerializationType::array();
    for (const auto& entry : world) {
        const WorldObject& object = entry.second;
        if (object.oid == self || object.type == "PLAY") continue;
        uint64 parent = object.parent;
        bool owned = false;
        for (int depth = 0; parent && depth < 32; ++depth) {
            if (parent == self) { owned = true; break; }
            auto it = world.find(parent);
            if (it == world.end() || it->second.parent == parent) break;
            parent = it->second.parent;
        }
        if (owned) items.push_back({{"oid", object.oid}, {"parent", object.parent},
            {"type", object.type}, {"name", object.name}, {"crc", object.crc}});
    }
    return {{"ok", true}, {"self", self}, {"items", items}};
}

JSONSerializationType AgentControl::status() {''')
c = replace(c, '\tif (cmd == "ping")', r'''
    if (cmd == "inventory") return inventorySnapshot();
    if (cmd == "sui_pages") {
        std::lock_guard<std::recursive_mutex> lock(worldMutex);
        JSONSerializationType pages = JSONSerializationType::array();
        for (const auto& entry : suiPages) pages.push_back(entry.second);
        return {{"ok", true}, {"pages", pages}};
    }
    if (cmd == "radial_menu") {
        uint64 target = request.value("target", (uint64)0);
        if (!target) return {{"ok", false}, {"error", "target required"}};
        ObjectControllerMessage* msg = new ObjectControllerMessage(self, 0x23, 0x146);
        msg->insertLong(target); msg->insertLong(self); msg->insertInt(1);
        msg->insertByte(1); msg->insertByte(0); msg->insertByte(20); msg->insertByte(3);
        msg->insertUnicode(UnicodeString("")); msg->insertByte(++radialCounter);
        zone->getZoneClient()->sendMessage(msg);
        return {{"ok", true}, {"requested", target}};
    }
    if (cmd == "select_radial") {
        uint64 target = request.value("target", (uint64)0);
        int radial = request.value("radial_id", -1); bool offered = false;
        { std::lock_guard<std::recursive_mutex> lock(worldMutex);
          auto it = radialMenus.find(target);
          if (it != radialMenus.end()) for (const auto& item : it->second)
              if (item.value("radial_id", -1) == radial) offered = true; }
        if (!offered) return {{"ok", false}, {"error", "request menu first and select a returned radial_id"}};
        BaseMessage* msg = new BaseMessage(); msg->insertShort(3); msg->insertInt(0x7CA18726);
        msg->insertLong(target); msg->insertByte((uint8)radial);
        zone->getZoneClient()->sendMessage(msg);
        return {{"ok", true}, {"selected", radial}, {"target", target}};
    }
    if (cmd == "mission_list") {
        uint64 target = request.value("target", (uint64)0);
        if (!target) return {{"ok", false}, {"error", "mission terminal target required"}};
        ObjectControllerMessage* msg = new ObjectControllerMessage(self, 0x23, 0xF5);
        msg->insertByte(0); msg->insertByte(++radialCounter); msg->insertLong(target);
        zone->getZoneClient()->sendMessage(msg);
        return {{"ok", true}, {"requested", target}, {"note", "mission deltas still need structured decoding"}};
    }
    if (cmd == "sui_respond") {
        uint32 page = request.value("page_id", (uint32)0);
        uint32 event = request.value("event", (uint32)0);
        JSONSerializationType args = request.value("args", JSONSerializationType::array());
        { std::lock_guard<std::recursive_mutex> lock(worldMutex);
          if (!suiPages.count(page)) return {{"ok", false}, {"error", "unknown SUI page"}}; }
        if (!args.is_array() || args.size() > 64) return {{"ok", false}, {"error", "invalid SUI arguments"}};
        for (const auto& arg : args) if (!arg.is_string()) return {{"ok", false}, {"error", "SUI arguments must be strings"}};
        BaseMessage* msg = new BaseMessage(); msg->insertShort(5); msg->insertInt(0x092D3564);
        msg->insertInt(page); msg->insertInt(event); msg->insertInt(args.size()); msg->insertInt(0);
        for (const auto& arg : args) msg->insertUnicode(UnicodeString(arg.get<std::string>().c_str()));
        zone->getZoneClient()->sendMessage(msg);
        { std::lock_guard<std::recursive_mutex> lock(worldMutex); suiPages.erase(page); }
        return {{"ok", true}, {"responded", page}};
    }
\tif (cmd == "ping")'''.replace('\\t', '\t'))
c = replace(c, '\t\tint index = request.value("index", 0);', '''\t\tint index = request.value("index", 0);
\t\tif (!conversationActive || index < 0 || index >= (int)conversationOptions.size())
\t\t\treturn {{"ok", false}, {"error", "no active conversation option at that index"}};''')
z = (ROOT/'ZonePacketHandler.cpp.base').read_text(encoding='utf-8-sig')
z = replace(z, '\tsys::uint32 opcode = pack->parseInt();', '''\tsys::uint32 opcode = pack->parseInt();
\tif (AgentControl::get() != nullptr && AgentControl::get()->onStandalonePacket(opcode, pack)) {
\t\tzone->signal(opcode);
\t\treturn;
\t}''')
outputs = {'AgentControl.h': h, 'AgentControl.cpp': c, 'ZonePacketHandler.cpp': z}
patch = []
for name, data in outputs.items():
    (ROOT/name).write_text(data, encoding='utf-8')
    original = (ROOT/(name+'.base')).read_text(encoding='utf-8-sig')
    patch.extend(difflib.unified_diff(original.splitlines(True), data.splitlines(True),
        fromfile='a/MMOCoreORB/src/'+FILES[name], tofile='b/MMOCoreORB/src/'+FILES[name]))
(ROOT/'agent-capabilities.patch').write_text(''.join(patch), encoding='utf-8')
print('Staged source and patch written outside /opt/swg; NOT deployed or in-game tested.')
