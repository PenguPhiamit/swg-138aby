"""Build a static triage view from the latest saved report per squad. Never controls clients.

    python outputs/tools/squad_health_report.py
    python outputs/tools/squad_health_report.py --reports PATH --output PATH

Preserves check counts and blocked notes separately. A safe prerequisite stop is not a full gameplay pass.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse,json
HERE=Path(__file__).resolve().parent
GROUPS=('Aurek','Besh','Cresh','Dorn','Esk')

def summarize(data, source):
    checks=data.get('checks',[])
    if not isinstance(checks,list) or any(not isinstance(c,dict) or type(c.get('ok')) is not bool for c in checks):
        raise ValueError('checks must be a list of labelled boolean results')
    passed=sum(c['ok'] for c in checks)
    notes=data.get('notes',[])
    if not isinstance(notes,list) or any(not isinstance(n,str) for n in notes):raise ValueError('notes must be strings')
    blocked=[n for n in notes if n.upper().startswith('BLOCKED')]
    failures=[{'label':str(c.get('label','unlabelled')),'detail':c.get('detail')} for c in checks if not c['ok']]
    errors=[]
    if data.get('error'):errors.append(str(data['error']))
    if data.get('passed')!=passed or data.get('total')!=len(checks):errors.append('stored check totals disagree with boolean check records')
    state='ERROR' if errors else 'FAIL' if failures else 'BLOCKED' if blocked else 'NO_CHECKS' if not checks else 'PASS'
    return {'group':str(data.get('group','unknown')),'scenario':str(data.get('scenario','unknown')),
            'started':data.get('started'),'seconds':data.get('seconds'),'source':source,'state':state,
            'passed':passed,'total':len(checks),'failures':failures,'blocked_notes':blocked,'errors':errors,
            'build_revision':data.get('build_revision') or data.get('revision'),
            'scope':'saved report only; not live bot/server state'}

def collect(root):
    records=[]
    for group in GROUPS:
        # Timestamp-prefixed filenames are the harness convention. Ignore aggregate/run/manifest JSON.
        candidates=sorted((root/group).glob('[0-9]*-*.json'))
        if not candidates:
            records.append({'group':group,'state':'NOT_RUN','source':None,'passed':0,'total':0,'failures':[],
                            'blocked_notes':[],'errors':[],'scenario':None,'build_revision':None})
            continue
        path=candidates[-1]
        try:
            item=summarize(json.loads(path.read_text(encoding='utf-8')),str(path.relative_to(root)))
            if item['group']!=group:raise ValueError('report group differs from containing folder')
        except (OSError,ValueError,TypeError) as exc:
            item={'group':group,'state':'ERROR','source':str(path.relative_to(root)),'passed':0,'total':0,
                  'failures':[],'blocked_notes':[],'errors':[str(exc)],'scenario':None,'build_revision':None}
        records.append(item)
    return records

def safe(text):return str(text).replace('|','\\|').replace('\n',' ').replace('\r',' ')[:450]

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reports',type=Path,default=HERE.parent/'Bot-reports')
    parser.add_argument('--output',type=Path,default=HERE.parent/'Bot-reports/triage')
    args=parser.parse_args();records=collect(args.reports)
    payload={'generated_utc':datetime.now(timezone.utc).isoformat(),'scope':'latest saved report per squad, possibly different runs/builds; no pooled pass rate','records':records}
    args.output.mkdir(parents=True,exist_ok=True)
    (args.output/'latest.json').write_text(json.dumps(payload,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    text='# Squad triage — saved reports, not live status\n\n'+payload['scope']+'. PASS means only the recorded checks; BLOCKED means prerequisites or capabilities prevented completion. Missing build revisions prevent build-to-build comparison. Original reports are unchanged.\n\n| Squad | Scenario | State | Recorded checks | Evidence |\n|---|---|---|---|---|\n'
    import os
    for r in records:
        link='not run' if not r['source'] else '[report]('+Path(os.path.relpath(args.reports/r['source'],args.output)).as_posix()+')'
        text+=f"| {r['group']} | {safe(r['scenario'])} | {r['state']} | {r['passed']}/{r['total']} | {link} |\n"
    for r in records:
        if r['failures'] or r['blocked_notes'] or r['errors']:
            text+='\n## '+r['group']+'\n\n'
            for e in r['errors']:text+='- Report/runtime error: '+safe(e)+'\n'
            for e in r['failures']:text+='- Failed check: '+safe(e['label'])+' — '+safe(e['detail'])+'\n'
            for e in r['blocked_notes']:text+='- '+safe(e)+'\n'
    (args.output/'latest.md').write_text(text,encoding='utf-8')
    print('\n'.join(f"{r['group']}: {r['state']} {r['passed']}/{r['total']} ({r['scenario']})" for r in records))
if __name__=='__main__':main()
