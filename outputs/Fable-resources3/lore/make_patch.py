"""C29 dev patch: minimum-pool lines for the two lore leaves, on top of the current dev resource_manager.lua (work/orig, copied
read-only from /opt/swg/Core3-dev) -> work/new, diff -> patch/core3-c29-lore-pools.patch. The anchor is the end of the R3 part-2
Ossus block. python -I make_patch.py"""
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
L = 'MMOCoreORB/bin/scripts/managers/resource_manager.lua'
LF = chr(10)
src = open(os.path.join(HERE, 'work', 'orig', L), encoding='utf-8', newline='').read()
anchor = '\ttable.insert(minimumpoolincludes, {ossusType, 1})' + LF + 'end' + LF
assert src.count(anchor) == 1, 'the R3 part-2 Ossus block is not where expected'
assert 'crystalline_adegan_ossus' not in src and 'vegetable_fungi_lumni_hoth' not in src, 'already applied'
block = (anchor +
         '-- C29 (Fable, 14 Oct 2026): two Legends materials in the merged resource_tree.iff of the test-session local_planets.tre' + LF +
         '-- (stage_lore_materials): the Adegan crystal gem on Ossus and the lumni lichen fungus on Hoth; one of each always in spawn,' + LF +
         '-- on its own planet only (the _ossus / _hoth substring is the zone restriction).' + LF +
         'for _, loreType in ipairs({"crystalline_adegan_ossus", "vegetable_fungi_lumni_hoth"}) do' + LF +
         '\ttable.insert(minimumpoolincludes, {loreType, 1})' + LF + 'end' + LF)
new = src.replace(anchor, block)
dst = os.path.join(HERE, 'work', 'new', L)
os.makedirs(os.path.dirname(dst), exist_ok=True)
open(dst, 'w', encoding='utf-8', newline='').write(new)
p = subprocess.run(['diff', '-u', '--label', 'a/' + L, '--label', 'b/' + L, os.path.join(HERE, 'work', 'orig', L), dst], capture_output=True)
os.makedirs(os.path.join(HERE, 'patch'), exist_ok=True)
out = os.path.join(HERE, 'patch', 'core3-c29-lore-pools.patch')
open(out, 'wb').write(p.stdout)
print('patch lines', len(p.stdout.splitlines()), '->', out)
