from pathlib import Path
from datetime import datetime
p=Path('outputs/SWG-handoff.md')
b=p.read_bytes()
Path('work/c45-handoff-before.bin').write_bytes(b)
s=b.decode('utf-8')
assert '**C45:' not in s
stamp=datetime.now().strftime('%Y-%m-%d %H:%M')
row=f'| **C45: C44-F1 crafting recipe fix + mission-type audit** | ChatGPT, High | claimed {stamp} | Owner-authorized isolated branch `gpt/c45-mission-recipes` from dev `40af2c78`, Core3-gpt only; Claude retains dev/test galaxy and run 6; no restarts; review/cherry-pick by Claude |\r\n'
anchor='|---|---|---|---|\r\n'
assert anchor in s
s=s.replace(anchor,anchor+row,1)
s=s.replace('ChatGPT owns `/opt/swg/Core3-gpt` (C41 packet writer claimed 2026-10-15 12:49).','ChatGPT owns `/opt/swg/Core3-gpt` (C45 mission recipe fix claimed '+stamp+'; owner-authorized branch only).',1)
p.write_bytes(s.encode('utf-8'))
print('C45 claimed; Claude lock retained; CRLF preserved')
