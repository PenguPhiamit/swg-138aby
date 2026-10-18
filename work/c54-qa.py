from pathlib import Path
import subprocess
r=Path('/opt/swg/Core3-gpt')
files=sorted((r/'MMOCoreORB/bin/scripts').rglob('*.lua'))
errors=[]
for p in files:
 q=subprocess.run(['luac5.3','-p',str(p)],capture_output=True,text=True)
 if q.returncode:errors.append((str(p.relative_to(r)),q.stderr))
print('ALL LUA',len(files),'files;',len(errors),'errors')
for p,e in errors:print(p,e)
subprocess.run(['lua5.3','/mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/work/c54-qa.lua'],check=True)
print('CONFIGURED BUILDS',list(r.rglob('CMakeCache.txt')))
raise SystemExit(bool(errors))
