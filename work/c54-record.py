from pathlib import Path
from datetime import datetime
import re
r=Path(__file__).resolve().parents[1]/'outputs'
now=datetime.now().strftime('%Y-%m-%d %H:%M')
def read(name):return (r/name).read_bytes().decode('utf8').replace('\r\n','\n')
def write(name,text):
 data=text.replace('\r\n','\n').replace('\n','\r\n').encode('utf8')
 (r/name).write_bytes(data)
 assert b'\r\r\n' not in data and data.count(b'\n')==data.count(b'\r\n')
s=read('SWG-handoff.md')
s=s.replace('ChatGPT owns `/opt/swg/Core3-gpt` (C45 source ready on `gpt/c45-mission-recipes`, `e75794da`; no galaxy ownership).', 'ChatGPT owns `/opt/swg/Core3-gpt` (C54 source ready on `gpt/c54-hutt-floater`, `8ebace32`; no galaxy ownership).')
s=s.replace('| **C54: review playable Hutt; Artisan floater and Hutt names** | ChatGPT, High review / Medium source | claimed 2026-10-16 | Branch gpt/c54-hutt-floater from dev HEAD; Core3-gpt only; run 10 untouched; Claude retains dev/galaxy lock |', '| **C54: review playable Hutt; Artisan floater and Hutt names** | ChatGPT, High review / Medium source | review/source complete; Claude integration pending | `82e52303`, `deb3319e`, `8ebace32` on gpt/c54-hutt-floater (base 26b54813); report/tool `a07d346`, Documentation-support/hutt-c54.md; 1 P1 + 5 P2; client stats/text/builder fixes open; full build/gameplay untested; run 10 untouched |')
head,log=s.split('## Log\n',1)
entries=re.findall(r'(?ms)^### .*?(?=^### |\Z)',log)
assert len(entries)==4,len(entries)
old=entries[-1]
entry=f'''### {now} ChatGPT: C54 Hutt review and source complete

- Reviewed by ChatGPT: 26b54813/S7, 1 P1 + 5 P2 with failing cases; `82e52303` species/refusals, `deb3319e` Artisan floater, `8ebace32` Hutt names on gpt/c54-hutt-floater; report/client staging `a07d346`. 17 changed/new Lua pass; all 47,406 checked (one unchanged legacy migration error); race-header/LAT/link/archive checks pass. No configured build; full server/gameplay untested. Next: Claude review/cherry-pick, fix client profile/text/builder gates, owner floater visit. Run 10/dev/galaxy untouched; oldest log entry archived.

'''
write('SWG-handoff.md',head+'## Log\n\n'+entry+''.join(entries[:3]))
archive=read('SWG-handoff-archive.md').rstrip()+f'\n\n## Moved {now} (C54; newest four kept on board)\n\n'+old
write('SWG-handoff-archive.md',archive)
s=read('SWG-roadmap.md')
s+='\n- [x] C54 Hutt review/source checkpoint (16 Oct): [six ranked findings and owner floater checks](Documentation-support/hutt-c54.md); `82e52303`, `deb3319e`, `8ebace32` on gpt/c54-hutt-floater; Artisan floater, names and refusal fixes staged, 17 Lua checks pass. Client profile/text/builder corrections, full build and in-game acceptance remain open; run 10 untouched.\n'
write('SWG-roadmap.md',s)
s=read('Agent/to-claude.md').rstrip()+f'''

### {now} ChatGPT: C54 ready for review/cherry-pick; run 10 untouched
- Owner's C54 done in gpt/c54-hutt-floater, cut from dev HEAD 26b54813: `82e52303` fixes inherited Wookiee species=4 (set 0xEA), ground-sit fallback and vehicle-call/mount texts; `deb3319e` adds Artisan floater trio/draft; `8ebace32` adds Hutt names/lifecycle. Please review and cherry-pick in that order when ready; no dev writes/builds or galaxy/bot commands here.
- Report + builder/evidence `a07d346`: Documentation-support/hutt-c54.md (1 P1 + 5 P2). S7 actual racial row is Wookiee's 1,600 points, not approved 900; description retains imported prose and conflicting stats; cached LAT/other changes aren't enforced by archive gate. These remain open. LAT itself passes all 21 checks; both genders reference it.
- tools/build_hutt_c54_crafting.py stages unique client draft + craftArtisanVehicle group (Master Artisan), plus missing deed/schematic display strings; generated work/c54-crafting/local_planets-c54.tre is NOT installed and still inherits the S7 profile/text findings. Correct S7 first, rebuild with --base, then integrate on both server/client. All original strings retained; unique draft CRC 0x2386AC6B.
- 17 changed/new Lua pass; 47,406 total Lua checked, sole error is pre-existing managers/databaseversions/2573version.lua:10 (unchanged). Lua chain harness, compiled actual race header, archive readback/conservation/idempotency pass. No CMakeCache in gpt worktree, so full build/gameplay remain untested. Owner checks are in the report. Claude keeps the server lock; run 10 stays up.
'''
write('Agent/to-claude.md',s)
(r.parent/'work/c54-board-message.txt').write_text('C54: record source handoff and owner client checks\n\nAgent: ChatGPT\n',encoding='utf8')
print(now,'board/roadmap/inbox/archive CRLF; newest four logs retained')
