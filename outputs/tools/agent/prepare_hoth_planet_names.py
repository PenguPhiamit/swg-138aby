"""C26 custom-planet IDs in mission/waypoint telemetry, GPT worktree only."""
from pathlib import Path
import subprocess
root = Path('/opt/swg/Core3-gpt')
assert subprocess.check_output(['git', '-C', str(root), 'branch', '--show-current'], text=True).strip() == 'gpt/work'
assert not subprocess.check_output(['git', '-C', str(root), 'status', '--porcelain'], text=True).strip()
p = root / 'MMOCoreORB/src/client/agent/AgentControl.cpp'
s = p.read_text()
old = '"endor", "dathomir", "tutorial", "dungeon1"};'
assert s.count(old) == 1
p.write_text(s.replace(old, '"endor", "dathomir", "tutorial", "dungeon1", "hoth", "ossus"};'))
print('Planet telemetry includes Hoth/Ossus; unbuilt')
