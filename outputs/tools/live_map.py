"""Live map of the test galaxy (Claude, 15 Oct 2026). Inside Debian:

    python3 live_map.py [--port 8765]

then open http://localhost:8765 on Windows (WSL mirrored networking reaches it). The idea is item 1 of the
TortoiseBots study (Documentation-support/tortoisebots-study.md): Sagiroth's observability dashboard, a 2D map per
planet with a marker per bot. Our code; nothing ported.

Read-only. It reads the test galaxy's log/who.json (names, planets and positions; account ids and IPs are dropped and
never sent to the page), the squads' activity records (Bot-reports/runs/*-activity.json), the bot roster
(tools/bots/groups.json) and the known places (tools/bots/places.json). It never talks to a bot or to the server.
Positions are as fresh as who.json, which Core3 writes every Core3.OnlineLogSeconds (default 300 s; tools/test_galaxy.py
sets 10) and on logins. Listens on 127.0.0.1 only.
"""
import argparse
import json
import os
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUTPUTS = HERE.parent
WHO = Path('/opt/swg/testgalaxy/Core3/MMOCoreORB/bin/log/who.json')
RUNS = OUTPUTS / 'Bot-reports' / 'runs'
GROUPS = HERE / 'bots' / 'groups.json'
PLACES = HERE / 'bots' / 'places.json'
CITY_PLANET = {'mos_eisley': 'tatooine', 'coronet': 'corellia', 'theed': 'naboo', 'mos_espa': 'tatooine'}
TRAIL = 40

roster = {}     # first name -> group
trails = {}     # first name -> [(x, y)]
seen = {'mtime': 0.0}


def load_roster():
    roster.clear()
    try:
        groups = json.loads(GROUPS.read_text(encoding='utf-8'))['groups']
    except (OSError, ValueError, KeyError):
        return
    for group, info in groups.items():
        for member in info.get('members', []):
            roster[member.get('name', '').split(' ')[0]] = group
    roster.setdefault('Kael', 'Kael')


def places():
    try:
        data = json.loads(PLACES.read_text(encoding='utf-8'))
    except (OSError, ValueError):
        return []
    out = []
    for city, info in data.items():
        zone = info.get('planet') or CITY_PLANET.get(city)
        if not zone or not isinstance(info, dict):
            continue
        for kind, rows in info.get('terminals', {}).items():
            for row in rows:
                if 'x' in row and 'y' in row:
                    out.append({'zone': zone, 'kind': kind.replace('terminal_', '').replace('_name', ''),
                                'x': row['x'], 'y': row['y']})
    return out


def activity():
    rows = []
    now = time.time()
    for path in sorted(RUNS.glob('*-activity.json')):
        try:
            row = json.loads(path.read_text(encoding='utf-8'))
        except (OSError, ValueError):
            continue
        rows.append({'group': row.get('group', path.stem.split('-')[0]), 'scenario': row.get('scenario', ''),
                     'state': row.get('state', ''), 'detail': str(row.get('detail', ''))[:160],
                     'age': max(0, round(now - float(row.get('updated', 0))))})   # a running round stamps ahead
    return rows


def snapshot():
    chars, age, error = [], None, ''
    try:
        mtime = WHO.stat().st_mtime
        age = round(time.time() - mtime)
        clients = json.loads(WHO.read_text(encoding='utf-8', errors='replace')).get('clients', [])
    except (OSError, ValueError) as e:
        clients, error = [], f'cannot read who.json: {type(e).__name__}'
        mtime = seen['mtime']
    fresh = mtime != seen['mtime']
    seen['mtime'] = mtime
    for c in clients:
        name = c.get('firstName') or '?'
        x, y = float(c.get('worldPositionX', 0)), float(c.get('worldPositionY', 0))
        zone = c.get('zone') or '?'
        trail = trails.setdefault(name, [])
        if fresh and (not trail or trail[-1][:2] != [x, y] or trail[-1][2] != zone):
            trail.append([x, y, zone])
            del trail[:-TRAIL]
        group = roster.get(name)
        chars.append({'name': name, 'zone': zone, 'x': x, 'y': y, 'kind': 'bot' if group else 'player',
                      'group': group or '', 'online_s': c.get('sessionSeconds'),
                      'trail': [[tx, ty] for tx, ty, tz in trail if tz == zone]})
    return {'who_age': age, 'error': error, 'time': time.strftime('%H:%M:%S'), 'chars': chars,
            'activity': activity(), 'places': places()}


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith('/data.json'):
            body, kind = json.dumps(snapshot()).encode(), 'application/json'
        elif self.path in ('/', '/index.html'):
            body, kind = PAGE.encode(), 'text/html; charset=utf-8'
        else:
            self.send_error(404)
            return
        self.send_response(200)
        self.send_header('Content-Type', kind)
        self.send_header('Cache-Control', 'no-store')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


PAGE = r'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Test Galaxy Map</title>
<style>
:root{--bg:#f6f5f2;--panel:#ffffff;--ink:#1d1d1b;--muted:#6b6a65;--line:#e2e0da;--grid:#ecebe6;--grid2:#d9d7d0;
--you:#c98a00;--place:#8d8a80;--accent:#2f6fde}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#141413;--panel:#1d1d1b;--ink:#ecebe6;--muted:#9c9a92;
--line:#2e2d2a;--grid:#22211f;--grid2:#33322e;--you:#f2b632;--place:#77756d;--accent:#6c9cff}}
:root[data-theme="dark"]{--bg:#141413;--panel:#1d1d1b;--ink:#ecebe6;--muted:#9c9a92;--line:#2e2d2a;--grid:#22211f;
--grid2:#33322e;--you:#f2b632;--place:#77756d;--accent:#6c9cff}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:14px/1.4 system-ui,-apple-system,"Segoe UI",sans-serif}
header{display:flex;flex-wrap:wrap;gap:8px 16px;align-items:center;padding:10px 16px;border-bottom:1px solid var(--line)}
h1{font-size:16px;margin:0;font-weight:600}#status{color:var(--muted);font-size:13px}
#tabs{display:flex;flex-wrap:wrap;gap:6px}#tabs button,.tool{border:1px solid var(--line);background:var(--panel);color:var(--ink);
border-radius:6px;padding:4px 10px;font:inherit;cursor:pointer}#tabs button.on{border-color:var(--accent);color:var(--accent);font-weight:600}
main{display:grid;grid-template-columns:minmax(0,1fr) 320px;gap:12px;padding:12px 16px}
@media (max-width:860px){main{grid-template-columns:1fr}}
#wrap{position:relative;background:var(--panel);border:1px solid var(--line);border-radius:8px;overflow:hidden;aspect-ratio:1/1;max-height:82vh}
canvas{width:100%;height:100%;display:block;cursor:grab;touch-action:none}
#tip{position:absolute;pointer-events:none;background:var(--panel);border:1px solid var(--line);border-radius:6px;padding:4px 8px;
font-size:12px;display:none;white-space:nowrap}
#tools{position:absolute;top:8px;left:8px;display:flex;gap:6px}
aside{display:flex;flex-direction:column;gap:12px;min-width:0}section{background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:10px 12px}
h2{font-size:13px;margin:0 0 6px;color:var(--muted);font-weight:600;text-transform:uppercase;letter-spacing:.04em}
table{width:100%;border-collapse:collapse;font-size:13px}td{padding:3px 4px;border-top:1px solid var(--line);vertical-align:top}
td.n{font-variant-numeric:tabular-nums;color:var(--muted);text-align:right;white-space:nowrap}
.dot{display:inline-block;width:9px;height:9px;border-radius:50%;margin-right:6px;vertical-align:middle}
.small{font-size:12px;color:var(--muted)}tr.pick td{background:color-mix(in srgb,var(--accent) 12%,transparent)}
tbody tr{cursor:pointer}
</style></head><body>
<header><h1>Test galaxy</h1><div id="tabs"></div><div id="status">loading…</div></header>
<main><div id="wrap"><canvas id="map"></canvas><div id="tools"><button class="tool" id="fit">Fit</button>
<button class="tool" id="whole">Whole planet</button></div><div id="tip"></div></div>
<aside><section><h2>On this planet</h2><table><tbody id="people"></tbody></table></section>
<section><h2>Squads</h2><table><tbody id="squads"></tbody></table>
<div class="small" style="margin-top:6px">Positions come from the server's player list (who.json); trails show where each one was at earlier updates.</div></section></aside></main>
<script>
const COLORS={Aurek:'#d1495b',Besh:'#2f9e44',Cresh:'#2f6fde',Dorn:'#8e5bd6',Esk:'#e07b00',Kael:'#0ca5a5'};
const cv=document.getElementById('map'),ctx=cv.getContext('2d'),tip=document.getElementById('tip');
let data=null,zone=localGet('zone')||'tatooine',view=null,picked=null,drag=null,hits=[],fitted=false;
function localGet(k){try{return localStorage.getItem('map.'+k)}catch(e){return null}}
function localSet(k,v){try{localStorage.setItem('map.'+k,v)}catch(e){}}
function css(n){return getComputedStyle(document.documentElement).getPropertyValue(n).trim()}
function color(c){return c.kind==='player'?css('--you'):(COLORS[c.group]||css('--accent'))}
function here(){return data?data.chars.filter(c=>c.zone===zone):[]}
function fit(whole){const pts=[];if(!whole){here().forEach(c=>{pts.push([c.x,c.y]);c.trail.forEach(p=>pts.push(p))})}
 if(!pts.length){view={cx:0,cy:0,span:16384};return}
 let x0=Math.min(...pts.map(p=>p[0])),x1=Math.max(...pts.map(p=>p[0])),y0=Math.min(...pts.map(p=>p[1])),y1=Math.max(...pts.map(p=>p[1]));
 view={cx:(x0+x1)/2,cy:(y0+y1)/2,span:Math.max(200,(Math.max(x1-x0,y1-y0))*1.4)}}
function toScreen(x,y){const s=cv.width/view.span;return[(x-view.cx)*s+cv.width/2,(view.cy-y)*s+cv.height/2]}
function toWorld(px,py){const s=cv.width/view.span;return[(px-cv.width/2)/s+view.cx,view.cy-(py-cv.height/2)/s]}
function draw(){const r=cv.getBoundingClientRect(),d=devicePixelRatio||1;cv.width=r.width*d;cv.height=r.height*d;
 if(!view)fit(false);ctx.clearRect(0,0,cv.width,cv.height);
 const steps=[16,32,64,128,256,512,1024,2048,4096];let step=steps.find(s=>view.span/s<=12)||4096;
 const [wx0,wy1]=toWorld(0,0),[wx1,wy0]=toWorld(cv.width,cv.height);ctx.lineWidth=1*d;ctx.font=(11*d)+'px system-ui';
 for(let gx=Math.ceil(wx0/step)*step;gx<=wx1;gx+=step){const[x]=toScreen(gx,0);ctx.strokeStyle=gx===0?css('--grid2'):css('--grid');
  ctx.beginPath();ctx.moveTo(x,0);ctx.lineTo(x,cv.height);ctx.stroke();ctx.fillStyle=css('--muted');ctx.fillText(gx,x+3*d,cv.height-4*d)}
 for(let gy=Math.ceil(wy0/step)*step;gy<=wy1;gy+=step){const[,y]=toScreen(0,gy);ctx.strokeStyle=gy===0?css('--grid2'):css('--grid');
  ctx.beginPath();ctx.moveTo(0,y);ctx.lineTo(cv.width,y);ctx.stroke();ctx.fillStyle=css('--muted');ctx.fillText(gy,3*d,y-3*d)}
 hits=[];(data?data.places:[]).filter(p=>p.zone===zone).forEach(p=>{const[x,y]=toScreen(p.x,p.y);ctx.fillStyle=css('--place');
  ctx.fillRect(x-2*d,y-2*d,4*d,4*d);hits.push({x,y,label:p.kind+' ('+Math.round(p.x)+', '+Math.round(p.y)+')'})});
 here().forEach(c=>{if(c.trail.length<2)return;ctx.strokeStyle=color(c);ctx.globalAlpha=.35;ctx.lineWidth=2*d;ctx.beginPath();
  c.trail.forEach((p,i)=>{const[x,y]=toScreen(p[0],p[1]);i?ctx.lineTo(x,y):ctx.moveTo(x,y)});ctx.stroke();ctx.globalAlpha=1});
 const spots=[];here().sort((a,b)=>(a.kind>b.kind?-1:1)).forEach(c=>{const[x,y]=toScreen(c.x,c.y);
  const s=spots.find(s=>Math.hypot(s.x-x,s.y-y)<14*d);if(s)s.list.push(c);else spots.push({x,y,list:[c]})});
 spots.forEach(s=>{s.list.forEach((c,i)=>{const a=i*2.4,r0=s.list.length>1?Math.min(4+i*1.6,22)*d:0;const x=s.x+Math.cos(a)*r0,y=s.y+Math.sin(a)*r0;
   const rad=(c.kind==='player'?7:5)*d*(picked===c.name?1.5:1);ctx.fillStyle=color(c);ctx.beginPath();ctx.arc(x,y,rad,0,7);ctx.fill();
   ctx.strokeStyle=css('--panel');ctx.lineWidth=2*d;ctx.stroke();
   hits.push({x,y,label:c.name+(c.group?' · '+c.group:' · you')+' ('+Math.round(c.x)+', '+Math.round(c.y)+')',name:c.name})});
  const first=s.list[0],more=s.list.length-1;ctx.fillStyle=css('--ink');ctx.font=(first.kind==='player'?'600 ':'')+(12*d)+'px system-ui';
  ctx.fillText(first.name+(more?' +'+more:''),s.x+(more?26:10)*d,s.y+4*d)})}
function render(){if(!data)return;if(!fitted&&here().length){fit(false);fitted=true}const zones={};data.chars.forEach(c=>zones[c.zone]=(zones[c.zone]||0)+1);
 if(!zones[zone]&&Object.keys(zones).length)zone=Object.keys(zones).sort((a,b)=>zones[b]-zones[a])[0];
 document.getElementById('tabs').innerHTML=Object.keys(zones).sort().map(z=>`<button class="${z===zone?'on':''}" data-z="${z}">${z} · ${zones[z]}</button>`).join('');
 const age=data.who_age==null?'?':data.who_age<90?data.who_age+' s':Math.round(data.who_age/60)+' min';
 document.getElementById('status').textContent=(data.error||`${data.chars.length} online · positions ${age} old · page ${data.time}`);
 document.getElementById('people').innerHTML=here().sort((a,b)=>(a.kind>b.kind?-1:1)||a.name.localeCompare(b.name)).map(c=>
  `<tr data-n="${c.name}" class="${picked===c.name?'pick':''}"><td><span class="dot" style="background:${color(c)}"></span>${c.name}</td><td class="small">${c.group||'you'}</td><td class="n">${Math.round(c.x)}, ${Math.round(c.y)}</td></tr>`).join('')||'<tr><td class="small">nobody</td></tr>';
 document.getElementById('squads').innerHTML=data.activity.map(a=>`<tr><td><span class="dot" style="background:${COLORS[a.group]||css('--accent')}"></span>${a.group}</td>
  <td>${a.scenario.replace('.py','')}<div class="small">${a.state}${a.age<3600?' · '+Math.round(a.age/60)+' min ago':''}</div></td></tr>`).join('');
 draw()}
async function poll(){try{data=await (await fetch('data.json',{cache:'no-store'})).json();render()}catch(e){document.getElementById('status').textContent='map server not answering'}}
document.getElementById('tabs').onclick=e=>{const z=e.target.dataset.z;if(z){zone=z;localSet('zone',z);view=null;render()}};
document.getElementById('people').onclick=e=>{const tr=e.target.closest('tr');if(!tr)return;picked=tr.dataset.n;const c=here().find(c=>c.name===picked);
 if(c){view={cx:c.x,cy:c.y,span:Math.min(view.span,600)}}render()};
document.getElementById('fit').onclick=()=>{fit(false);draw()};document.getElementById('whole').onclick=()=>{fit(true);draw()};
cv.addEventListener('wheel',e=>{e.preventDefault();const d=devicePixelRatio||1,r=cv.getBoundingClientRect(),[wx,wy]=toWorld((e.clientX-r.left)*d,(e.clientY-r.top)*d);
 const k=e.deltaY>0?1.25:.8;view.span=Math.min(20000,Math.max(40,view.span*k));const[nx,ny]=toWorld((e.clientX-r.left)*d,(e.clientY-r.top)*d);
 view.cx+=wx-nx;view.cy+=wy-ny;draw()},{passive:false});
cv.addEventListener('pointerdown',e=>{drag={x:e.clientX,y:e.clientY,cx:view.cx,cy:view.cy};cv.setPointerCapture(e.pointerId)});
cv.addEventListener('pointerup',()=>drag=null);
cv.addEventListener('pointermove',e=>{const d=devicePixelRatio||1,r=cv.getBoundingClientRect();
 if(drag){const s=view.span/cv.width*d;view.cx=drag.cx-(e.clientX-drag.x)*s;view.cy=drag.cy+(e.clientY-drag.y)*s;draw();return}
 const px=(e.clientX-r.left)*d,py=(e.clientY-r.top)*d,h=hits.filter(h=>Math.hypot(h.x-px,h.y-py)<10*d).pop();
 if(h){tip.style.display='block';tip.textContent=h.label;tip.style.left=(e.clientX-r.left+12)+'px';tip.style.top=(e.clientY-r.top+12)+'px'}else tip.style.display='none'});
addEventListener('resize',draw);poll();setInterval(poll,5000);
</script></body></html>
'''


def main():
    parser = argparse.ArgumentParser(description='Live map of the test galaxy (read-only).')
    parser.add_argument('--port', type=int, default=8765)
    args = parser.parse_args()
    load_roster()
    server = ThreadingHTTPServer(('127.0.0.1', args.port), Handler)
    print(f'live map on http://localhost:{args.port} (who.json: {WHO})', flush=True)
    server.serve_forever()


if __name__ == '__main__':
    main()
