"""Write ../checks.json: the stage report (work/stage-1024.log), map_art.check() on staged/client and the dds self-test."""
import io
import json
import os
import sys
from contextlib import redirect_stdout

HERE = os.path.dirname(os.path.abspath(__file__))
O3 = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import map_art  # noqa: E402
import dds  # noqa: E402

log = open(os.path.join(O3, 'work', 'stage-1024.log'), encoding='utf-8').read()
log = log[log.index('{'):]
report = json.loads(log[:log.rindex('}') + 1])
chk = map_art.check(os.path.join(O3, 'staged', 'client'))
buf = io.StringIO()
with redirect_stdout(buf):
    ok = dds.selftest()
out = {'built': '2026-10-14', 'tool': 'tools/map_art.py --res 1024', 'stage_report': report, 'check': chk,
       'dds_selftest': {'passed': ok, 'log': buf.getvalue().splitlines()}}
with open(os.path.join(O3, 'checks.json'), 'w', encoding='utf-8') as f:
    json.dump(out, f, indent=1)
print('check ok', chk['ok'], 'dds selftest', ok, 'files', len(report['files']), 'render', report['render'])
