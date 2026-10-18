from pathlib import Path
import subprocess
r=Path(__file__).resolve().parents[1]
p=r/'outputs/Agent/to-claude.md'
current=p.read_bytes()
mark=b'### 2026-10-16 09:12 ChatGPT: C54 ready'
at=current.index(mark)
old=subprocess.check_output(['git','show','HEAD:outputs/Agent/to-claude.md'],cwd=r)
p.write_bytes(old.rstrip(b'\r\n')+b'\r\n\r\n'+current[at:])
p=r/'outputs/SWG-handoff.md'
p.write_bytes(p.read_bytes().rstrip(b'\r\n')+b'\r\n')
