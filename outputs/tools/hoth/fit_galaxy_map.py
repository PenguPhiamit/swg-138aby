"""Read-only stock UI/grid fit. Generates diagnostics, never edits the client or TRE."""
from pathlib import Path
import hashlib,json,math,re
OUT=Path(__file__).resolve().parents[2]/'Documentation-support'
UI=OUT/'hoth/client-base/ui/ui_ticketpurchase.inc'
NAMES=['Corellia','Dantooine','Dathomir','Endor','Lok','Naboo','Rori','Talus','Tatooine','Yavin4']

def solve(matrix, vector):
    a=[list(r)+[v] for r,v in zip(matrix,vector)]
    for i in range(3):
        k=max(range(i,3),key=lambda k:abs(a[k][i]))
        a[i],a[k]=a[k],a[i]
        if abs(a[i][i])<1e-10:raise ValueError('grid anchors are singular')
        pivot=a[i][i];a[i]=[v/pivot for v in a[i]]
        for j in range(3):
            if j!=i:
                scale=a[j][i];a[j]=[x-scale*y for x,y in zip(a[j],a[i])]
    return [r[-1] for r in a]

def fit(points):
    x=[[p['grid'][0],p['grid'][1],1] for p in points]
    gram=[[sum(r[i]*r[j] for r in x) for j in range(3)] for i in range(3)]
    return [solve(gram,[sum(r[i]*p['pixel'][axis] for r,p in zip(x,points)) for i in range(3)]) for axis in range(2)]

def predict(coeff,grid):return [sum(a*b for a,b in zip(c,[*grid,1])) for c in coeff]

def main():
    lore=json.loads((OUT/'planets-coordinates.json').read_text(encoding='utf-8'))['planets']
    by_zone={p['zone']:p for p in lore};text=UI.read_text(encoding='latin-1');anchors=[]
    for name in NAMES:
        blocks=re.findall(r'<Button\b(.*?)>',text,re.S)
        block=next(b for b in blocks if re.search(r"\bName='button"+name+"'",b))
        def pair(key):return [int(x) for x in re.search(r"\b"+key+r"='(-?\d+,-?\d+)'",block)[1].split(',')]
        loc,size=pair('Location'),pair('Size');g=by_zone[name.lower()]['grid_center']
        anchors.append({'name':name,'grid':[g['column_A1'],g['row']],'pixel':[loc[i]+size[i]/2 for i in range(2)],'button_top_left':loc,'button_size':size})
    buckets={}
    for p in anchors:buckets.setdefault(tuple(p['grid']),[]).append(p)
    points=[{'names':[p['name'] for p in v],'grid':list(g),'pixel':[sum(p['pixel'][i] for p in v)/len(v) for i in range(2)]} for g,v in buckets.items()]
    coeff=fit(points)
    for p in points:
        p['fitted']=predict(coeff,p['grid']);p['residual_px']=math.dist(p['pixel'],p['fitted'])
        p['leave_one_out_error_px']=math.dist(p['pixel'],predict(fit([q for q in points if q is not p]),p['grid']))
    h=by_zone['hoth']['grid_center'];center=predict(coeff,[h['column_A1'],h['row']])
    # Current Hoth builder clones Endor's button. Preserve that size, not its location.
    endor=next(p for p in anchors if p['name']=='Endor');top=[center[i]-endor['button_size'][i]/2 for i in range(2)]
    report={'ui_file':str(UI),'ui_sha256':hashlib.sha256(UI.read_bytes()).hexdigest(),'coordinate_frame':'GalaxyMap-local button centres; x right, y down; no screen/resolution scaling applied','anchors':anchors,'independent_system_anchors':points,'affine_x_y_coefficients':coeff,'rmse_px':math.sqrt(sum(p['residual_px']**2 for p in points)/len(points)),'max_residual_px':max(p['residual_px'] for p in points),'max_leave_one_out_error_px':max(p['leave_one_out_error_px'] for p in points),'hoth':{'grid':'K-18','fitted_center':center,'endor_cloned_button_size':endor['button_size'],'candidate_button_top_left':[round(v) for v in top],'status':'approximate inference; not a verified in-client position'},'client_files_changed':False}
    report['fit_accepted'] = report['max_residual_px'] <= 30 and report['max_leave_one_out_error_px'] <= 60
    report['acceptance_rule'] = 'proposed diagnostic gate: max residual <=30px and leave-one-out <=60px; not an owner-approved layout rule'
    if not report['fit_accepted']:
        report['hoth']['status'] = 'REJECTED for automatic use: stock layout is inconsistent with one atlas affine fit'
        report['hoth']['adopt_candidate'] = False
    target=OUT/'hoth/galaxy-map-calibration.json';target.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    svg=['<svg xmlns="http://www.w3.org/2000/svg" width="720" height="600" viewBox="-60 -35 600 500"><rect x="-60" y="-35" width="600" height="500" fill="white"/><text x="-40" y="-12" font-family="sans-serif" font-size="12">Stock button centres (blue), atlas fit (grey), Hoth inference (red)</text>']
    for p in points:
        x,y=p['pixel'];fx,fy=p['fitted'];name='/'.join(p['names'])
        svg.append(f'<line x1="{x}" y1="{y}" x2="{fx}" y2="{fy}" stroke="#aaa"/><circle cx="{fx}" cy="{fy}" r="3" fill="#999"/><circle cx="{x}" cy="{y}" r="4" fill="#1d4ed8"/><text x="{x+6}" y="{y-6}" font-family="sans-serif" font-size="9">{name}</text>')
    x,y=center;svg.append(f'<circle cx="{x}" cy="{y}" r="6" fill="#dc2626"/><text x="{x+9}" y="{y}" font-family="sans-serif" font-size="11">Hoth K-18 (inferred)</text></svg>')
    (OUT/'hoth/galaxy-map-calibration.svg').write_text(''.join(svg),encoding='utf-8')
    print(json.dumps({k:report[k] for k in ('rmse_px','max_residual_px','max_leave_one_out_error_px','hoth')},indent=2))
if __name__=='__main__':main()
