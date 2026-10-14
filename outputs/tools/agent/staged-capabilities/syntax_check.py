"""Read existing build flags and syntax-check staged copies; no build or deployment."""
from pathlib import Path
import json, shlex, subprocess

ROOT = Path(__file__).resolve().parent
BUILD = Path('/opt/swg/Core3-dev/MMOCoreORB/build/dev')
result = subprocess.run(['ninja', '-C', str(BUILD), '-t', 'compdb'], capture_output=True, text=True, check=True)
commands = json.loads(result.stdout)
summary = []
for name in ('AgentControl.cpp', 'ZonePacketHandler.cpp'):
    candidates = [c for c in commands if c.get('file', '').endswith('/'+name) and '/client/' in c.get('file', '')]
    if len(candidates) != 1:
        raise SystemExit(f'Expected one client compile command for {name}, got {len(candidates)}')
    original = shlex.split(candidates[0]['command'])
    safe = []
    skip = False
    for arg in original:
        if skip:
            skip = False
            continue
        if arg in ('-o', '-MF', '-MT', '-MQ'):
            skip = True
            continue
        if arg in ('-c', '-MD', '-MMD', '-MP') or arg == candidates[0]['file']:
            continue
        safe.append(arg)
    safe += ['-fsyntax-only', '-I'+str(Path(candidates[0]['file']).parent),
             '-include', str(ROOT/'AgentControl.h'), str(ROOT/name)]
    checked = subprocess.run(safe, cwd=ROOT, capture_output=True, text=True)
    diagnostic = checked.stdout + checked.stderr
    (ROOT/(name+'.diagnostics.txt')).write_text(diagnostic)
    summary.append({'file': name, 'syntax_exit_code': checked.returncode})
    print(name, 'PASS' if checked.returncode == 0 else 'FAIL')
    if checked.returncode:
        print(diagnostic[-7000:])
(ROOT/'syntax-results.json').write_text(json.dumps(summary, indent=2))
raise SystemExit(0 if all(x['syntax_exit_code'] == 0 for x in summary) else 1)
