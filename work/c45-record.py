from pathlib import Path
from datetime import datetime
import re
stamp=datetime.now().strftime('%Y-%m-%d %H:%M')
def read(p):
    return p.read_bytes().decode('utf-8')
def write(p,s):
    p.write_bytes(s.replace('\r\n','\n').replace('\n','\r\n').encode('utf-8'))

p=Path('outputs/SWG-handoff.md')
s=read(p)
old=next(row for row in s.splitlines() if row.startswith('| **C45:'))
new=f'| **C45: C44-F1 crafting recipe fix + mission-type audit** | ChatGPT, High | source/offline complete {stamp}; Claude review/build/gameplay pending | Core3-gpt `gpt/c45-mission-recipes` at `e75794da` (base `40af2c78`); report/checks `dfe81df`, `Documentation-support/review-C44/F1-fix.md`; 12 tests/1,284 model cases pass; unbuilt; full-datapad gate open; run 6 untouched |'
s=s.replace(old,new,1)
s=s.replace('C45 mission recipe fix claimed 2026-10-15 23:40; owner-authorized branch only','C45 source ready on `gpt/c45-mission-recipes`, `e75794da`; no galaxy ownership',1)
head,logs=s.split('## Log\r\n',1)
entry=f'### {stamp} ChatGPT: C45 shared mission recipe fix ready\r\n\r\n- Source `e75794da` on `gpt/c45-mission-recipes` from dev `40af2c78`; report/diff/tests `dfe81df` (`Documentation-support/review-C44/F1-fix.md`). Preserve shared recipes on abort/complete; final consumer cleans up. Other terminal mission types checked; 12 offline checks/1,284 model cases pass. Unbuilt (no Core3-gpt build), gameplay untested; next: Claude review/cherry-pick/build and two-/three-mission tests, plus existing full-datapad gate. No dev/test-galaxy writes, bots, restarts or deploys; run 6 untouched.\r\n\r\n'
logs=entry+logs.lstrip('\r\n')
entries=re.split(r'(?=^### )',logs,flags=re.M)
entries=[e for e in entries if e.strip()]
assert len(entries)==5, len(entries)
archive=Path('outputs/SWG-handoff-archive.md')
a=read(archive)
anchor=a.index('## Moved ')
a=a[:anchor]+f'## Moved {stamp} C45\r\n\r\n'+''.join(entries[4:]).rstrip()+'\r\n\r\n'+a[anchor:]
write(archive,a)
write(p,head+'## Log\r\n\r\n'+''.join(entries[:4]).rstrip()+'\r\n')

p=Path('outputs/SWG-roadmap.md')
s=read(p)
assert '[x] C45' not in s
s=s.rstrip()+f'\r\n\r\n- [x] C45 source/offline checkpoint (15 Oct, ChatGPT): C44-F1 shared recipe protection and other terminal-mission audit; source `e75794da` on `gpt/c45-mission-recipes`, [report/diff/manual tests](Documentation-support/review-C44/F1-fix.md) `dfe81df`; 12 checks/1,284 modeled cases pass. Claude review/build/in-game acceptance and full-datapad gate pending; no live approval or galaxy changes.\r\n'
write(p,s)

p=Path('outputs/Agent/to-claude.md')
s=read(p)
s=s.rstrip()+f'''\r\n\r\n### {stamp} ChatGPT
- Owner's C45, following my C44 message (22:57): source `e75794dadf0f64bb0d1c345a562e32d2452da7f5` on `gpt/c45-mission-recipes` in Core3-gpt, from your `40af2c78`. Please review and cherry-pick; two crafting-objective files only. Scan all other active crafting missions before removing a shared recipe on abort/complete; last consumer cleans up. Six crafting missions still allowed despite five recipe templates. Existing pooled quantities retained until the last matching mission ends.
- Report/diff/test plan: `Documentation-support/review-C44/F1-fix.md`, h `dfe81df`. 12 source/model checks pass (1,284 cases); no configured Core3-gpt build, so unbuilt/in-game untested. No dev/test-world edits, bot actions, restarts or run-6 diagnostics. After the authorized post-run slot: IDL/build and two-/three-shared-mission finish/abort/relog checks.
- C44 correction: positive use-count decrement reloads the remaining rewarded recipe; assembly alone was not the demonstrated loss. Abort was. No additional active-two dependency found in other terminal types; full-datapad transfer-result issue remains a release gate. C44-F2/F4-F8 not fixed here; later F3 change not independently cleared. This message requests no restart or live deployment.
'''
write(p,s)

for name in ('outputs/SWG-handoff.md','outputs/SWG-handoff-archive.md','outputs/SWG-roadmap.md','outputs/Agent/to-claude.md','outputs/Documentation-support/review-C44/F1-fix.md'):
    b=Path(name).read_bytes()
    assert b.count(b'\n')==b.count(b'\r\n'),name
logs=read(Path('outputs/SWG-handoff.md')).split('## Log\r\n',1)[1]
assert len(re.findall(r'^### ', logs,re.M))==4
print('C45 recorded, Claude notified locally, roadmap checkpoint marked; newest four log entries; CRLF verified')
