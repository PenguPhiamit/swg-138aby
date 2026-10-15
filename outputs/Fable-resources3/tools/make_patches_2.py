"""R3 part 2: the Ossus minimum-pool lines on top of the part-1 resource_manager.lua (work/new -> work/new2)."""
import os
import subprocess
import sys

R = 'C:/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Fable-resources3'
sys.path.insert(0, R + '/tools')
import ossus_minerals  # noqa: E402

L = 'MMOCoreORB/bin/scripts/managers/resource_manager.lua'
LF = chr(10)
src = open(R + '/work/new/' + L, encoding='utf-8', newline='').read()
enums = [e for _, es, _, _ in ossus_minerals.PLAN for e in es]
anchor = '\ttable.insert(minimumpoolincludes, {hothType, 1})' + LF + 'end' + LF
assert src.count(anchor) == 1
block = (anchor + '-- R3 part 2 (Fable, 14 Oct 2026): Ossus\'s own fourteen minerals, gas and fuels (<class>_ossus, gems <class>_ossus_<n>), in the' + LF +
         '-- merged resource_tree.iff of the test-session local_planets.tre (stage_ossus_minerals); one of each always in spawn, on Ossus only.' + LF +
         'for _, ossusType in ipairs({' + ', '.join('"%s"' % e for e in enums[:7]) + ',' + LF +
         '\t\t' + ', '.join('"%s"' % e for e in enums[7:]) + '}) do' + LF +
         '\ttable.insert(minimumpoolincludes, {ossusType, 1})' + LF + 'end' + LF)
new = src.replace(anchor, block)
os.makedirs(os.path.dirname(R + '/work/new2/' + L), exist_ok=True)
open(R + '/work/new2/' + L, 'w', encoding='utf-8', newline='').write(new)
p = subprocess.run(['diff', '-u', '--label', 'a/' + L, '--label', 'b/' + L, R + '/work/new/' + L, R + '/work/new2/' + L], capture_output=True)
open(R + '/patch/core3-r3-2-ossus-pools.patch', 'wb').write(p.stdout)
print('part-2 pool patch lines', len(p.stdout.splitlines()), 'enums', len(enums))
