from pathlib import Path
import subprocess
p=Path('outputs/Agent/to-claude.md')
current=p.read_bytes()
marker=b'### 2026-10-15 23:46 ChatGPT\r\n'
assert current.count(marker)==1
message=current[current.index(marker):]
original=subprocess.check_output(['git','show','HEAD:outputs/Agent/to-claude.md'])
p.write_bytes(original + (b'\r\n' if original.endswith(b'\n') else b'\r\n\r\n') + message)
assert p.read_bytes().startswith(original)
print('Inbox original byte prefix/line endings preserved; new message uses CRLF')
