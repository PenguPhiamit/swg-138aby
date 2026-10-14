from pathlib import Path
import json
root=Path(__file__).resolve().parents[1]
audit=json.loads((root/'work/content-audit.json').read_text())
lines=['# SWG content warning inventory','','October 13, 2026. Read-only archive index audit.','',
'All 51 configured server archives are present. Thirty-five distinct paths appeared in the audited startup warnings. A file can be present but unsupported by a server parser.','',
'The scan decoded 116 version-0005 archives across the server set and original disc; it did not decode 59 newer version-0006 original disc archives. “No match” below applies only to decoded archives.','',
'| Warning path | Index evidence | Interpretation |','|---|---|---|']
for name,hits in audit['missing_assets'].items():
    if name=='appearance/pt_light_indoor_glow.prt':
        evidence='Loaded `patch_07.tre`; `PEFT` particle form'
        meaning='Present; server leaves particle form uninstantiated'
    elif hits:
        evidence='; '.join(sorted(set('Original disc `'+x['archive']+'`' for x in hits)))
        meaning='Later-patch asset outside configured pre-CU set; compatibility review needed'
    else:
        evidence='No match in decoded indexes'
        if name.startswith('datatables/space/'):
            meaning='Ship hardpoint lookup; loader tolerates absent table; ship support unverified'
        elif name.startswith('clientdata/ship/'):
            meaning='Ship client-data lookup; collision/attachment data needs review'
        elif name=='snapshot/tutorial.ws':
            meaning='Snapshot is optional in loader; tutorial is created by screenplay'
        elif 'godclient' in name:
            meaning='Referenced by developer/no-build marker templates; likely helper asset'
        else:
            meaning='Unresolved object/effect/template reference; investigate specific usage'
    lines.append(f'| `{name}` | {evidence} | {meaning} |')
lines+=['','The “expected SHOT, found SSHP” template warnings and Mantis credential error are separate from these missing-path rows. See SWG-content-research.md for their assessment.','']
(root/'outputs/SWG-content-warning-inventory.md').write_text('\n'.join(lines),encoding='utf-8')
print('Wrote detailed inventory with',len(audit['missing_assets']),'paths.')
