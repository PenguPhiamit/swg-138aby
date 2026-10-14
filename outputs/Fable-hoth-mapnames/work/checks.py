import sys, os, json, hashlib, tempfile, shutil
B = 'C:/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Fable-hoth-mapnames'
sys.path.insert(0, B + '/tools')
import hoth_names as H
stage = B + '/staged/client'
rep = H.stage_hoth_names(stage, snippet_path=H.SNIPPET)           # deterministic re-run
ver = H.verify(stage)
# idempotence: a second pass with the staged files as base adds nothing and writes identical bytes
def staged_base(name):
    p = os.path.join(stage, name.replace('/', os.sep))
    return open(p, 'rb').read() if os.path.exists(p) else None
tmp = tempfile.mkdtemp()
rep2 = H.stage_hoth_names(tmp, base=staged_base)
idem = {rel: {'added': len(rep2['files'][rel]['added']), 'identical': rep2['files'][rel]['sha256'] == rep['files'][rel]['sha256']} for rel in H.FILES}
# held sites and large-first on a scratch dir
tmp2 = tempfile.mkdtemp()
rep3 = H.stage_hoth_names(tmp2, include_held=True, large_first=True)
held = {'sites': len(rep3['sites']), 'hoth_markers': len(rep3['files'][H.POI_TABLE]['hoth_rows']),
        'label_rows': len(rep3['files'][H.REGION_TABLE]['rows']), 'first_label': rep3['files'][H.REGION_TABLE]['rows'][0][0]}
shutil.rmtree(tmp); shutil.rmtree(tmp2)
summary = {rel: {k: v for k, v in rep['files'][rel].items() if k not in ('rows', 'hoth_rows', 'columns', 'types')} for rel in H.FILES}
for rel in H.FILES:
    a = summary[rel]; a['added'] = len(a['added']); a['existing'] = len(a['existing'])
out = {'built': '2026-10-14', 'tool': 'tools/hoth_names.py', 'sites_on': rep['sites'], 'files': summary,
       'hoth_marker_rows': rep['files'][H.POI_TABLE]['hoth_rows'], 'label_rows': rep['files'][H.REGION_TABLE]['rows'],
       'verify': ver, 'second_pass_with_staged_base': idem, 'held_and_large_first_scratch': held,
       'snippet_rows': rep['snippet']['rows']}
json.dump(out, open(B + '/checks.json', 'w'), indent=1)
print(json.dumps({'verify_ok': ver['ok'], 'idempotent': idem, 'held': held, 'files': {r: (summary[r]['bytes'], summary[r]['added']) for r in H.FILES}}, indent=1))
