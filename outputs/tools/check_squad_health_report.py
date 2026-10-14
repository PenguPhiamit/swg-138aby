"""Offline regression fixtures for saved-report semantics; no game/socket access."""
import importlib.util,tempfile,json
from pathlib import Path
p=Path(__file__).with_name('squad_health_report.py');s=importlib.util.spec_from_file_location('health',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)

def report(checks,notes=(),error=None):return {'group':'Aurek','scenario':'fixture.py','passed':sum(c['ok'] for c in checks),'total':len(checks),'checks':checks,'notes':list(notes),'error':error}
assert m.summarize(report([{'label':'approach','ok':True}],['BLOCKED: no eligible mission']),'x')['state']=='BLOCKED'
assert m.summarize(report([],['BLOCKED: hospital cell unavailable']),'x')['state']=='BLOCKED'
r=m.summarize(report([{'label':'receipt','ok':False}],['BLOCKED: quantity omitted']),'x');assert r['state']=='FAIL' and r['blocked_notes'] and r['total']==1
r=report([{'label':'real effect','ok':False}]);r['passed']=1
assert m.summarize(r,'x')['state']=='ERROR'
assert m.summarize(report([]),'x')['state']=='NO_CHECKS'
assert m.summarize(report([{'label':'effect','ok':True}]),'x')['state']=='PASS'
with tempfile.TemporaryDirectory() as folder:
 root=Path(folder);(root/'Aurek').mkdir();(root/'Aurek/20261014-000001-bad.json').write_text('{broken')
 rows=m.collect(root);assert rows[0]['state']=='ERROR' and all(r['state']=='NOT_RUN' for r in rows[1:])
print('PASS: blocked-vs-pass, mixed fail/block, inconsistent totals, no-check, malformed and absent reports')
