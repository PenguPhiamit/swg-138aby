"""Expose already received secondary attributes; isolated GPT worktree only."""
from pathlib import Path
import subprocess

root = Path('/opt/swg/Core3-gpt')
assert subprocess.check_output(['git', '-C', str(root), 'branch', '--show-current'], text=True).strip() == 'gpt/work'
assert not subprocess.check_output(['git', '-C', str(root), 'status', '--porcelain'], text=True).strip()
path = root / 'MMOCoreORB/src/client/agent/AgentControl.cpp'
source = path.read_text()
anchor = '\t\tstate["max_ham"] = {{"health", object.maxHam[0]}, {"action", object.maxHam[3]}, {"mind", object.maxHam[6]}};'
assert source.count(anchor) == 1
source = source.replace(anchor, anchor + '''
		// CreatureAttribute.cpp indices. Existing three-pool keys remain compatible.
		static const char* names[] = {"health", "strength", "constitution", "action", "quickness",
			"stamina", "mind", "focus", "willpower"};
		JSONSerializationType current = JSONSerializationType::object(), maximum = JSONSerializationType::object();
		for (int i = 0; i < 9; ++i) {
			current[names[i]] = object.ham[i];
			maximum[names[i]] = object.maxHam[i];
		}
		state["attributes"] = current;
		state["max_attributes"] = maximum;''')
path.write_text(source)
