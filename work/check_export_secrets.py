from pathlib import Path
import re
base=Path('/mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h')
config=Path('/opt/swg/Core3/MMOCoreORB/bin/conf/config-local.lua').read_text()
text=re.sub(r'\s+','',(base/'tmp/pdfs/pdf-text.txt').read_text())
values=re.findall(r'^Core3\.DB(?:Pass|Secret)\s*=\s*"([^"]+)"',config,re.M)
assert len(values)==2,'Expected private database settings were not located.'
login=(base/'outputs/SWG-login.txt').read_text()
values.extend(re.findall(r'(?im)^\s*password\s*[:=]\s*(\S+)',login))
assert not any(value in text for value in values if len(value)>8),'A private credential appears in the export.'
print('Private database and detected owner credentials are absent from the PDF text.')
