from pathlib import Path
import re
root=Path(__file__).resolve().parents[1]
board=root/'outputs/SWG-handoff.md'
s=board.read_bytes().decode('utf-8')
old='**C48 — claimed ChatGPT, 16 Oct 3:59 AM (Medium): run-8 read-only analysis and morning sheet; no bot commands or galaxy changes.**'
new='**C48 — done ChatGPT, 16 Oct 4:03 AM (Medium): [morning sheet](Bot-reports/launch-sim/MORNING-SHEET.md), [run-8 numbers](Bot-reports/launch-sim/numbers-run8.md), [style/SP and watchdog](Bot-reports/launch-sim/run8-style-watchdog.md); report commit `bc166df`. Active-run checkpoint through 3:59 AM; no bot commands or galaxy changes.**'
assert old in s
s=s.replace(old,new,1)
head,log=s.split('## Log\r\n',1)
entries=re.split(r'(?=^### )',log,flags=re.M)
entries=[x for x in entries if x.strip()]
entry='### 2026-10-16 04:03 ChatGPT: C48 overnight checkpoint and morning sheet\r\n\r\n- Reports `bc166df`: run 8 through 3:59 AM, 1,700 bots, 20,009 kills, 1,043 deaths, 2,358 completed missions; style/SP totals reconcile. Morning sheet lists 29 owner decisions with recommendations; watchdog has no recorded low-memory despawn, latest 6,646 MB available. 748 snapshots exceed their assigned point-budget label; cap enforcement unverified. Read-only WSL analysis only; crafting/full-datapad, Hutt/Ossus client checks and live release remain open. Next: owner decisions and Claude runtime follow-up; oldest log entry archived.\r\n\r\n'
kept=[entry]+entries
removed=kept[4:]
archive=root/'outputs/SWG-handoff-archive.md'
if removed:
    a=archive.read_bytes().decode('utf-8')
    a=a.rstrip('\r\n')+'\r\n\r\n## Moved 2026-10-16 04:03 (C48)\r\n\r\n'+''.join(removed).rstrip('\r\n')+'\r\n'
    archive.write_bytes(a.encode('utf-8'))
board.write_bytes((head+'## Log\r\n\r\n'+''.join(kept[:4]).rstrip('\r\n')+'\r\n').encode('utf-8'))
road=root/'outputs/SWG-roadmap.md'
r=road.read_bytes().decode('utf-8')
r=r.rstrip('\r\n')+'\r\n\r\n- [x] C48 overnight analysis / owner morning sheet (16 Oct, ChatGPT): [run-8 numbers](Bot-reports/launch-sim/numbers-run8.md), [style/SP and watchdog](Bot-reports/launch-sim/run8-style-watchdog.md), [29 owner decisions](Bot-reports/launch-sim/MORNING-SHEET.md); `bc166df`. Active checkpoint through 3:59 AM only; no bot commands or galaxy changes. Runtime/client and live-release gates remain open.\r\n'
road.write_bytes(r.encode('utf-8'))
# Check relative links in all deliverables and the handoff line endings/count.
for p in (root/'outputs/Bot-reports/launch-sim').glob('*.md'):
    if p.name not in {'MORNING-SHEET.md','numbers-run8.md','run8-style-watchdog.md'}: continue
    for target in re.findall(r'\]\(([^)]+)\)',p.read_text(encoding='utf-8')):
        if '://' not in target:
            assert (p.parent/target.split('#')[0]).exists(),(p,target)
b=board.read_bytes(); assert b.count(b'\r\n')==b.count(b'\n')
assert len(re.findall(r'^### ',b.decode().split('## Log\r\n',1)[1],re.M))==4
print('Checked report links, CRLF board, four newest log entries.')
