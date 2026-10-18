from pathlib import Path
import sys
r=Path('/opt/swg/Core3-gpt/MMOCoreORB')
for pattern in sys.argv[1:]:
 for p in r.glob(pattern):
  print('\nFILE',p.relative_to(r))
  print(p.read_text() if p.is_file() else 'directory')
