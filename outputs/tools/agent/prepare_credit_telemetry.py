"""C26 own-character credits, GPT worktree only. No build/deploy."""
from pathlib import Path
import subprocess
ROOT = Path('/opt/swg/Core3-gpt')
assert subprocess.check_output(['git', '-C', str(ROOT), 'branch', '--show-current'], text=True).strip() == 'gpt/work'
assert not subprocess.check_output(['git', '-C', str(ROOT), 'status', '--porcelain'], text=True).strip()


def replace(text, old, new):
    assert text.count(old) == 1, old[:80]
    return text.replace(old, new)


header = ROOT / 'MMOCoreORB/src/client/agent/AgentControl.h'
source = ROOT / 'MMOCoreORB/src/client/agent/AgentControl.cpp'
handler = ROOT / 'MMOCoreORB/src/client/zone/ZonePacketHandler.cpp'
h = header.read_text()
h = replace(h, '\t\tstd::vector<int> ham, maxHam;', '''\t\tstd::vector<int> ham, maxHam;
\t\tbool bankCreditsKnown = false, cashCreditsKnown = false;
\t\tint bankCredits = 0, cashCredits = 0;''')
h = replace(h, '\tvoid onBaseline3(uint64 oid, uint32 typeCode, Message* pack);',
'''\tvoid onBaseline1(uint64 oid, uint32 typeCode, Message* pack);
\tvoid onBaseline3(uint64 oid, uint32 typeCode, Message* pack);''')
s = source.read_text()
s = replace(s, 'void AgentControl::onBaseline3(uint64 oid, uint32 typeCode, Message* pack) {',
'''void AgentControl::onBaseline1(uint64 oid, uint32 typeCode, Message* pack) {
\tif (typeName(typeCode) != "CREO") return;
\tstd::lock_guard<std::recursive_mutex> lock(worldMutex);
\tif (oid != self) return; // own balances only, never other players' financial data
\tWorldObject& object = world[oid];
\tobject.bankCreditsKnown = object.cashCreditsKnown = false;
\tint bank = pack->parseInt(); // CreatureObjectMessage1 fields 0/1
\tint cash = pack->parseInt();
\tobject.bankCredits = bank;
\tobject.cashCredits = cash;
\tobject.bankCreditsKnown = object.cashCreditsKnown = true;
}

void AgentControl::onBaseline3(uint64 oid, uint32 typeCode, Message* pack) {''')
s = replace(s, 'void AgentControl::onDelta(uint64 oid, uint32 typeCode, uint8 type, Message* pack) {',
'''void AgentControl::onDelta(uint64 oid, uint32 typeCode, uint8 type, Message* pack) {
\tif (typeName(typeCode) == "CREO" && type == 1) {
\t\tstd::lock_guard<std::recursive_mutex> lock(worldMutex);
\t\tif (oid != self) return;
\t\tWorldObject& object = world[oid];
\t\ttry {
\t\t\tuint16 updates = pack->parseShort();
\t\t\tfor (int u = 0; u < updates; ++u) {
\t\t\t\tuint16 index = pack->parseShort();
\t\t\t\tif (index == 0) {
\t\t\t\t\tobject.bankCredits = pack->parseInt();
\t\t\t\t\tobject.bankCreditsKnown = true;
\t\t\t\t} else if (index == 1) {
\t\t\t\t\tobject.cashCredits = pack->parseInt();
\t\t\t\t\tobject.cashCreditsKnown = true;
\t\t\t\t} else {
\t\t\t\t\t// Unknown list size may hide later balance updates. Omit rather than trust stale money.
\t\t\t\t\tobject.bankCreditsKnown = object.cashCreditsKnown = false;
\t\t\t\t\treturn;
\t\t\t\t}
\t\t\t}
\t\t} catch (...) {
\t\t\tobject.bankCreditsKnown = object.cashCreditsKnown = false;
\t\t\tthrow;
\t\t}
\t\treturn;
\t}''')
s = replace(s, '\treturn {{"ok", true}, {"self", self}, {"planet", planet}, {"x", selfX}, {"y", selfY}, {"z", selfZ},',
'''\tJSONSerializationType result = {{"ok", true}, {"self", self}, {"planet", planet}, {"x", selfX}, {"y", selfY}, {"z", selfZ},''')
s = replace(s, '\t\t\t{"conversation_options", conversationOptions}};\n}',
'''\t\t\t{"conversation_options", conversationOptions}};
\tauto own = world.find(self);
\tif (own != world.end()) {
\t\tif (own->second.bankCreditsKnown) result["bank_credits"] = own->second.bankCredits;
\t\tif (own->second.cashCreditsKnown) result["cash_credits"] = own->second.cashCredits;
\t}
\treturn result;
}''')
z = handler.read_text()
z = replace(z, 'if ((type == 3 || type == 6) && AgentControl::get() != nullptr)',
            'if ((type == 1 || type == 3 || type == 6) && AgentControl::get() != nullptr)')
z = replace(z, '\t\t\tif (type == 3)\n\t\t\t\tAgentControl::get()->onBaseline3',
'''\t\t\tif (type == 1)
\t\t\t\tAgentControl::get()->onBaseline1(oid, nametype, pack);
\t\t\telse if (type == 3)
\t\t\t\tAgentControl::get()->onBaseline3''')
header.write_text(h)
source.write_text(s)
handler.write_text(z)
print('Own-character credits prepared; unbuilt/untested C++')
