import os, sys, subprocess, json, time
from pathlib import Path
root=Path('/mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs')
script=root/'tools/bots/squad.py'; scenario=root/'tools/bots/scenarios/class-check.py'
start=time.monotonic()
for profession in ('combat_marksman','combat_brawler','outdoors_scout','science_medic','social_entertainer','crafting_artisan'):
    remaining=29-(time.monotonic()-start)/60
    if remaining < 5:
        raise SystemExit('Batch ceiling: insufficient time for another restored run')
    tester={'combat_marksman':'Aurek','combat_brawler':'Jesh','outdoors_scout':'Oren','science_medic':'Tamsin','social_entertainer':'Sela','crafting_artisan':'Aurek'}[profession]
    env=dict(os.environ, CLASS_CHECK_TESTER=tester, CLASS_CHECK_CONTEXT='after owner-requested MTG restart', CLASS_CHECK_PHASE='P1',CLASS_CHECK_PROFESSIONS=profession,CLASS_CHECK_GROUP='Aurek',CLASS_CHECK_MINUTES=str(min(23,remaining-5)))
    path=root/'Bot-reports/Aurek'/('class-check-'+profession+'-console.txt')
    print('START',profession,flush=True)
    with path.open('w') as log:
        result=subprocess.run([sys.executable,str(script),'run',str(scenario),'--group','Aurek','--rounds','1','--round-minutes','30','--no-fallback'],env=env,stdout=log,stderr=subprocess.STDOUT)
    report=json.loads((root/'Bot-reports/Aurek'/('class-check-'+profession+'.json')).read_text())
    print('END',profession,'completed',report.get('completed'),'counts',report['counts'],'cleanup_error',report.get('cleanup_error'),flush=True)
    if report.get('interrupted') or not report.get('completed') or not report.get('controls',{}).get('passed') or report.get('cleanup_error'):
        raise SystemExit('Controls or restoration incomplete; see '+str(path))
