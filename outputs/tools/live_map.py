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

Labels and live positions (owner, 15 Oct: "relabel the tracker so i can read what everyone is doing ... closer to a
live view"): squad.py writes what each bot is doing ("walking to 3830, -4520", "/polearmLegHit2 on sevorrt") and its
own latest position to /var/tmp/swg-bots/now/<name>.json on every command; a bot's own position is used when it is
fresher than who.json. The page refreshes every 1.5 s.

Temporary log (owner, 15 Oct: "maybe the tracker can keep some temp logs?"): every 3 s, if any bot moved or changed
what it is doing, or a squad changed state, a background thread appends machine lines to
Bot-reports/tracker/<yyyymmdd-hh>.jsonl and a readable snapshot (a line per bot: where, doing what, for how long, in
which scenario) to <yyyymmdd-hh>.txt. Files older than 48 hours are deleted; the folder is not in git. Players who are
not bots (the owner) are never logged.
"""
import argparse
import json
import os
import threading
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
LOGS = OUTPUTS / 'Bot-reports' / 'tracker'
KEEP_HOURS = 48
NOW = Path('/var/tmp/swg-bots/now')   # squad.py: what each bot is doing, and where it last said it was
NOW_FRESH = 15 * 60                   # an older label is stale (the bot's script ended)
NAVMAPS = OUTPUTS / 'Bot-reports' / 'navmaps'   # tools/navmap.py: building floor plans for /floor

roster = {}     # first name -> group
trails = {}     # first name -> [(x, y)]


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


def labels():
    """name -> the bot's own 'now' record (squad.py), if it is fresh."""
    out, now = {}, time.time()
    for path in NOW.glob('*.json') if NOW.is_dir() else ():
        try:
            row = json.loads(path.read_text(encoding='utf-8'))
        except (OSError, ValueError):
            continue
        if now - float(row.get('updated', 0)) < NOW_FRESH:
            out[row.get('name') or path.stem] = row
    return out


def present():
    """Everyone online, with the freshest position known and, for bots, what they are doing.
    Returns (chars, who_age, error, who_mtime)."""
    chars, age, error, now = [], None, '', time.time()
    try:
        mtime = WHO.stat().st_mtime
        age = round(now - mtime)
        clients = json.loads(WHO.read_text(encoding='utf-8', errors='replace')).get('clients', [])
    except (OSError, ValueError) as e:
        clients, error, mtime = [], f'cannot read who.json: {type(e).__name__}', 0.0
    told = labels()
    for c in clients:
        name = c.get('firstName') or '?'
        x, y = float(c.get('worldPositionX', 0)), float(c.get('worldPositionY', 0))
        zone, pos_s = c.get('zone') or '?', age
        own = told.get(name, {}) if name in roster else {}
        # A bot's own status reply is usually fresher than who.json (written every few seconds at best).
        if own.get('pos_at', 0) > mtime and own.get('zone', zone) == zone and own.get('x') is not None:
            x, y, pos_s = own['x'], own['y'], round(now - own['pos_at'])
        doing = own.get('doing', '')
        local = own.get('cell') and now - float(own.get('local_at', 0)) < 60
        chars.append({'name': name, 'zone': zone, 'x': x, 'y': y, 'pos_s': pos_s,
                      'kind': 'bot' if name in roster else 'player', 'group': roster.get(name, ''),
                      'online_s': c.get('sessionSeconds'), 'indoors': bool(own.get('cell')),
                      'doing': doing, 'doing_s': round(now - own['since']) if doing and own.get('since') else None,
                      **({'cell': own['cell'], 'lx': own.get('lx'), 'ly': own.get('ly'), 'lz': own.get('lz')} if local else {})})
    return chars, age, error, mtime


def escorted():
    """Players an escort crew is with indoors (escort.py puts the player's cell and spot in the leader's label)."""
    out, now = [], time.time()
    for row in labels().values():
        seen = row.get('escorted')
        if seen and now - float(seen.get('at', 0)) < 20:
            out.append(seen)
    return out


def snapshot():
    chars, age, error, mtime = present()
    for c in chars:
        trail = trails.setdefault(c['name'], [])
        if not trail or trail[-1][:2] != [c['x'], c['y']] or trail[-1][2] != c['zone']:
            trail.append([c['x'], c['y'], c['zone']])
            del trail[:-TRAIL]
        c['trail'] = [[tx, ty] for tx, ty, tz in trail if tz == c['zone']]
    return {'who_age': age, 'error': error, 'time': time.strftime('%H:%M:%S'), 'chars': chars,
            'activity': activity(), 'places': places(), 'escorted': escorted()}


def readable(chars, scenario):
    """One snapshot as text: a line per bot, grouped by squad, saying where it is and what it is doing."""
    rows = sorted((c for c in chars if c['kind'] == 'bot'), key=lambda c: (c['group'], c['name']))
    out = [time.strftime('%H:%M:%S') + ' ' + '-' * 60]
    for c in rows:
        doing = (c['doing'] or 'idle') + (f" ({c['doing_s']} s)" if c['doing_s'] is not None else '')
        where = f"{c['zone']} {c['x']:.0f} {c['y']:.0f}" + (' indoors' if c['indoors'] else '')
        job = scenario.get(c['group'], '')
        out.append(f"  {c['name']:<8} {c['group']:<6} {where:<28} {doing}" + (f"   [{job}]" if job else ''))
    return '\n'.join(out) + '\n'


def record(last, every=3):
    """The temporary log (see the top of this file). Runs forever in its own thread: every few seconds, if any
    bot moved, changed what it is doing, or a squad changed state, it appends machine lines (.jsonl) and a
    readable snapshot of every bot (.txt)."""
    while True:
        try:
            load_roster()  # a crew added to groups.json is logged without a restart
            chars, _, _, _ = present()
            stamp, lines = round(time.time()), []
            for c in chars:
                if c['kind'] != 'bot':
                    continue
                state = (c['zone'], round(c['x']), round(c['y']), c['doing'], c.get('cell'), c.get('lx'), c.get('ly'))
                if last.get(c['name']) != state:
                    last[c['name']] = state
                    lines.append({'t': stamp, 'kind': 'bot', **{k: c[k] for k in (
                        'name', 'group', 'zone', 'x', 'y', 'indoors', 'doing', 'doing_s', 'pos_s')},
                        **{k: c[k] for k in ('cell', 'lx', 'ly', 'lz') if k in c}})
            scenario = {}
            for row in activity():
                scenario[row['group']] = f"{row['scenario'].replace('.py', '')}: {row['state']}" if row['scenario'] else row['state']
                state = (row['scenario'], row['state'], row['detail'])
                if last.get('activity:' + row['group']) != state:
                    last['activity:' + row['group']] = state
                    lines.append(dict(row, t=stamp, kind='activity'))
            if lines:
                LOGS.mkdir(parents=True, exist_ok=True)
                hour = time.strftime('%Y%m%d-%H')
                with open(LOGS / f'{hour}.jsonl', 'a', encoding='utf-8') as f:
                    f.write(''.join(json.dumps(line) + '\n' for line in lines))
                with open(LOGS / f'{hour}.txt', 'a', encoding='utf-8') as f:
                    f.write(readable(chars, scenario))
            cutoff = time.time() - KEEP_HOURS * 3600
            for old in list(LOGS.glob('*.jsonl')) + list(LOGS.glob('*.txt')):
                if old.stat().st_mtime < cutoff:
                    old.unlink()
        except (OSError, ValueError):
            pass
        time.sleep(every)


def navmaps():
    """The floor plans navmap.py built: name, planet, building and the server ids of its cells."""
    out = []
    for path in sorted(NAVMAPS.glob('*.json')):
        try:
            plan = json.loads(path.read_text(encoding='utf-8'))
        except (OSError, ValueError):
            continue
        out.append({'name': path.stem, 'planet': plan.get('planet'), 'building': plan.get('building'),
                    'template': plan.get('template', '').rsplit('/', 1)[-1],
                    'cells': [c['oid'] for c in plan.get('cells', []) if c.get('oid')]})
    return out


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith('/data.json'):
            body, kind = json.dumps(snapshot()).encode(), 'application/json'
        elif self.path.startswith('/navmaps.json'):
            body, kind = json.dumps(navmaps()).encode(), 'application/json'
        elif self.path.startswith('/navmap/') and self.path.endswith('.json') and '..' not in self.path:
            target = NAVMAPS / self.path[len('/navmap/'):].split('?')[0]
            if not target.is_file():
                self.send_error(404)
                return
            body, kind = target.read_bytes(), 'application/json'
        elif self.path.split('?')[0] in ('/floor', '/floor.html'):
            body, kind = FLOOR_PAGE.encode(), 'text/html; charset=utf-8'
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
<header><h1>Test galaxy</h1><div id="tabs"></div><div id="status">loading…</div><a class="tool" href="/floor" style="text-decoration:none">Floor plans</a></header>
<main><div id="wrap"><canvas id="map"></canvas><div id="tools"><button class="tool" id="fit">Fit</button>
<button class="tool" id="whole">Whole planet</button></div><div id="tip"></div></div>
<aside><section><h2>On this planet</h2><table><tbody id="people"></tbody></table></section>
<section><h2>Squads</h2><table><tbody id="squads"></tbody></table>
<div class="small" style="margin-top:6px">A bot's position comes from its own last report when that is fresher than the server's player list (who.json). Labels say what each bot is doing and for how long; trails show where it was.</div></section></aside></main>
<script>
const COLORS={Aurek:'#d1495b',Besh:'#2f9e44',Cresh:'#2f6fde',Dorn:'#8e5bd6',Esk:'#e07b00',Forn:'#c2185b',Kael:'#0ca5a5'};
function says(c){return c.kind==='player'?'you':(c.doing||'idle')+(c.doing_s!=null?' · '+ago(c.doing_s):'')+(c.indoors?' · indoors':'')}
function ago(s){return s<90?s+' s':s<5400?Math.round(s/60)+' min':Math.round(s/3600)+' h'}
function clip(t,n){return t.length>n?t.slice(0,n-1)+'…':t}
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
   hits.push({x,y,label:c.name+(c.group?' · '+c.group:' · you')+': '+says(c)+' ('+Math.round(c.x)+', '+Math.round(c.y)+')',name:c.name})});
  const shown=s.list.slice(0,6),lx=s.x+(s.list.length>1?28:10)*d,top=s.y+4*d-(shown.length-1)*7*d;
  shown.forEach((c,i)=>{const y=top+i*14*d,text=c.name+(c.kind==='bot'?' — '+clip(c.doing||'idle',34):'');
   ctx.font=(c.kind==='player'?'600 ':'')+(12*d)+'px system-ui';ctx.lineWidth=3*d;ctx.strokeStyle=css('--panel');ctx.strokeText(text,lx,y);
   ctx.fillStyle=css('--ink');ctx.fillText(text,lx,y)});
  if(s.list.length>shown.length){ctx.fillStyle=css('--muted');ctx.fillText('+'+(s.list.length-shown.length)+' more',lx,top+shown.length*14*d)}})}
function render(){if(!data)return;if(!fitted&&here().length){fit(false);fitted=true}const zones={};data.chars.forEach(c=>zones[c.zone]=(zones[c.zone]||0)+1);
 if(!zones[zone]&&Object.keys(zones).length)zone=Object.keys(zones).sort((a,b)=>zones[b]-zones[a])[0];
 document.getElementById('tabs').innerHTML=Object.keys(zones).sort().map(z=>`<button class="${z===zone?'on':''}" data-z="${z}">${z} · ${zones[z]}</button>`).join('');
 const age=data.who_age==null?'?':data.who_age<90?data.who_age+' s':Math.round(data.who_age/60)+' min';
 const live=data.chars.filter(c=>c.kind==='bot'&&c.pos_s!=null&&c.pos_s<10).length;
 document.getElementById('status').textContent=(data.error||`${data.chars.length} online · ${live} bots live (under 10 s) · server list ${age} old · ${data.time}`);
 document.getElementById('people').innerHTML=here().sort((a,b)=>(a.kind>b.kind?-1:1)||a.name.localeCompare(b.name)).map(c=>
  `<tr data-n="${c.name}" class="${picked===c.name?'pick':''}"><td><span class="dot" style="background:${color(c)}"></span><b>${c.name}</b> <span class="small">${c.group||''}</span><div class="small">${esc(says(c))}</div></td><td class="n">${Math.round(c.x)}, ${Math.round(c.y)}<div>${c.pos_s!=null?ago(c.pos_s):''}</div></td></tr>`).join('')||'<tr><td class="small">nobody</td></tr>';
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
function esc(t){return String(t).replace(/[&<>"]/g,ch=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[ch]))}
addEventListener('resize',draw);poll();setInterval(poll,1500);
</script></body></html>
'''


# Floor plan of a building interior (owner, 15 Oct: "try and find a way to actually track them and map the navmesh"):
# the cells' floor meshes from tools/navmap.py (pale: where a body can stand; dark lines: walls, Core3's uncrossable
# edges; orange: blocking edges), the bots inside at their cell-local spots with labels and trails, the escorted
# player, and an X wherever a bot reported itself stuck.
FLOOR_PAGE = r'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Floor Plans</title>
<style>
:root{--bg:#f6f5f2;--panel:#ffffff;--ink:#1d1d1b;--muted:#6b6a65;--line:#e2e0da;--floor:#e9eef6;--floor2:#f3f2ee;
--wall:#3a3a36;--block:#d9822b;--you:#c98a00;--stuck:#d1495b;--accent:#2f6fde}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#141413;--panel:#1d1d1b;--ink:#ecebe6;--muted:#9c9a92;
--line:#2e2d2a;--floor:#22303f;--floor2:#1f1f1d;--wall:#cfcdc5;--block:#f0a050;--you:#f2b632;--stuck:#ff6b7d;--accent:#6c9cff}}
:root[data-theme="dark"]{--bg:#141413;--panel:#1d1d1b;--ink:#ecebe6;--muted:#9c9a92;--line:#2e2d2a;--floor:#22303f;
--floor2:#1f1f1d;--wall:#cfcdc5;--block:#f0a050;--you:#f2b632;--stuck:#ff6b7d;--accent:#6c9cff}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:14px/1.4 system-ui,-apple-system,"Segoe UI",sans-serif}
header{display:flex;flex-wrap:wrap;gap:8px 16px;align-items:center;padding:10px 16px;border-bottom:1px solid var(--line)}
h1{font-size:16px;margin:0;font-weight:600}#status{color:var(--muted);font-size:13px}
.bar{display:flex;flex-wrap:wrap;gap:6px}.bar button,.tool{border:1px solid var(--line);background:var(--panel);color:var(--ink);
border-radius:6px;padding:4px 10px;font:inherit;cursor:pointer;text-decoration:none}.bar button.on{border-color:var(--accent);color:var(--accent);font-weight:600}
main{display:grid;grid-template-columns:minmax(0,1fr) 320px;gap:12px;padding:12px 16px}@media (max-width:860px){main{grid-template-columns:1fr}}
#wrap{position:relative;background:var(--panel);border:1px solid var(--line);border-radius:8px;overflow:hidden;aspect-ratio:1/1;max-height:82vh}
canvas{width:100%;height:100%;display:block;cursor:grab;touch-action:none}
#tip{position:absolute;pointer-events:none;background:var(--panel);border:1px solid var(--line);border-radius:6px;padding:4px 8px;font-size:12px;display:none;white-space:nowrap}
aside{display:flex;flex-direction:column;gap:12px;min-width:0}section{background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:10px 12px}
h2{font-size:13px;margin:0 0 6px;color:var(--muted);font-weight:600;text-transform:uppercase;letter-spacing:.04em}
table{width:100%;border-collapse:collapse;font-size:13px}td{padding:3px 4px;border-top:1px solid var(--line);vertical-align:top}
.small{font-size:12px;color:var(--muted)}.dot{display:inline-block;width:9px;height:9px;border-radius:50%;margin-right:6px;vertical-align:middle}
</style></head><body>
<header><h1>Floor plans</h1><div class="bar" id="maps"></div><div class="bar" id="levels"></div><div id="status">loading…</div>
<a class="tool" href="/">World map</a></header>
<main><div id="wrap"><canvas id="map"></canvas><div id="tip"></div></div>
<aside><section><h2>Inside</h2><table><tbody id="inside"></tbody></table></section>
<section><h2>Stuck spots</h2><table><tbody id="stuck"></tbody></table>
<div class="small" style="margin-top:6px">Pale: the floor mesh Core3 paths over. Dark lines: walls (uncrossable edges). Orange: blocking edges. X: a bot said it was stuck there. Trails are kept while this page is open.</div></section></aside></main>
<script>
const COLORS={Aurek:'#d1495b',Besh:'#2f9e44',Cresh:'#2f6fde',Dorn:'#8e5bd6',Esk:'#e07b00',Forn:'#c2185b',Kael:'#0ca5a5'};
const cv=document.getElementById('map'),ctx=cv.getContext('2d'),tip=document.getElementById('tip');
let maps=[],plan=null,planName=null,cellInfo={},data=null,view=null,drag=null,hits=[],level='all',trails={},stuck=[],autoPicked=false;
function css(n){return getComputedStyle(document.documentElement).getPropertyValue(n).trim()}
function esc(t){return String(t).replace(/[&<>"]/g,ch=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[ch]))}
function lvl(h){return h==null?null:Math.round(h/4)*4}
function inside(){if(!data||!plan)return[];const out=[];data.chars.forEach(c=>{if(c.cell&&cellInfo[c.cell])out.push(c)});
 (data.escorted||[]).forEach(p=>{if(cellInfo[p.cell])out.push({name:p.name,kind:'player',cell:p.cell,lx:p.lx,ly:p.ly,lz:p.lz,doing:'',group:''})});return out}
function shown(cell){return level==='all'||lvl(cell.height)===level}
function fit(){if(!plan)return;let x0=1e9,x1=-1e9,y0=1e9,y1=-1e9;plan.cells.filter(shown).forEach(c=>c.tris.forEach(t=>t.forEach(p=>{
 x0=Math.min(x0,p[0]);x1=Math.max(x1,p[0]);y0=Math.min(y0,p[1]);y1=Math.max(y1,p[1])})));if(x0>x1){view={cx:0,cy:0,span:100};return}
 view={cx:(x0+x1)/2,cy:(y0+y1)/2,span:Math.max(20,Math.max(x1-x0,y1-y0)*1.1)}}
function toS(x,y){const s=cv.width/view.span;return[(x-view.cx)*s+cv.width/2,(view.cy-y)*s+cv.height/2]}
function toW(px,py){const s=cv.width/view.span;return[(px-cv.width/2)/s+view.cx,view.cy-(py-cv.height/2)/s]}
function draw(){const r=cv.getBoundingClientRect(),d=devicePixelRatio||1;cv.width=r.width*d;cv.height=r.height*d;ctx.clearRect(0,0,cv.width,cv.height);
 if(!plan||!view)return;hits=[];const s=cv.width/view.span;
 plan.cells.forEach(c=>{const on=shown(c);ctx.fillStyle=on?css('--floor'):css('--floor2');ctx.globalAlpha=on?1:.35;
  c.tris.forEach(t=>{ctx.beginPath();t.forEach((p,i)=>{const[x,y]=toS(p[0],p[1]);i?ctx.lineTo(x,y):ctx.moveTo(x,y)});ctx.closePath();ctx.fill()})});
 ctx.globalAlpha=1;plan.cells.filter(shown).forEach(c=>{[['walls','--wall',1.4],['blocks','--block',1.6]].forEach(([k,col,w])=>{
  ctx.strokeStyle=css(col);ctx.lineWidth=w*d;ctx.beginPath();c[k].forEach(e=>{const[a,b]=toS(e[0],e[1]),[p,q]=toS(e[2],e[3]);ctx.moveTo(a,b);ctx.lineTo(p,q)});ctx.stroke()})
  if(s*8>40*d&&c.tris.length){let sx=0,sy=0,n=0;c.tris.forEach(t=>t.forEach(p=>{sx+=p[0];sy+=p[1];n++}));const[x,y]=toS(sx/n,sy/n);
   ctx.fillStyle=css('--muted');ctx.font=(10*d)+'px system-ui';ctx.fillText(c.room,x-12*d,y)}});
 Object.entries(trails).forEach(([name,t])=>{const pts=t.filter(p=>cellInfo[p[0]]&&shown(cellInfo[p[0]]));if(pts.length<2)return;
  ctx.strokeStyle=COLORS[t.group]||css('--accent');ctx.globalAlpha=.4;ctx.lineWidth=2*d;ctx.beginPath();
  pts.forEach((p,i)=>{const[x,y]=toS(p[1],p[2]);i?ctx.lineTo(x,y):ctx.moveTo(x,y)});ctx.stroke();ctx.globalAlpha=1});
 stuck.forEach(st=>{if(!cellInfo[st.cell]||!shown(cellInfo[st.cell]))return;const[x,y]=toS(st.x,st.y);ctx.strokeStyle=css('--stuck');ctx.lineWidth=2.5*d;
  ctx.beginPath();ctx.moveTo(x-5*d,y-5*d);ctx.lineTo(x+5*d,y+5*d);ctx.moveTo(x+5*d,y-5*d);ctx.lineTo(x-5*d,y+5*d);ctx.stroke();
  hits.push({x,y,label:'stuck: '+st.name+' at '+st.time+' ('+st.room+')'})});
 inside().forEach((c,i)=>{if(c.lx==null)return;const[x,y]=toS(c.lx,c.ly);const col=c.kind==='player'?css('--you'):(COLORS[c.group]||css('--accent'));
  ctx.fillStyle=col;ctx.beginPath();ctx.arc(x,y,(c.kind==='player'?7:5)*d,0,7);ctx.fill();ctx.strokeStyle=css('--panel');ctx.lineWidth=2*d;ctx.stroke();
  const text=c.name+(c.doing?' — '+(c.doing.length>34?c.doing.slice(0,33)+'…':c.doing):'');ctx.font=(c.kind==='player'?'600 ':'')+(12*d)+'px system-ui';
  ctx.lineWidth=3*d;ctx.strokeStyle=css('--panel');ctx.strokeText(text,x+9*d,y+4*d+i%2*12*d);ctx.fillStyle=css('--ink');ctx.fillText(text,x+9*d,y+4*d+i%2*12*d);
  hits.push({x,y,label:c.name+' · '+(cellInfo[c.cell]||{}).room+' · height '+(c.lz!=null?c.lz.toFixed(1):'?')+(c.doing?' · '+c.doing:'')})})}
function sideList(){const rows=inside();document.getElementById('inside').innerHTML=rows.map(c=>`<tr><td><span class="dot" style="background:${c.kind==='player'?css('--you'):(COLORS[c.group]||css('--accent'))}"></span><b>${esc(c.name)}</b>
 <div class="small">${esc((cellInfo[c.cell]||{}).room||'')} · height ${c.lz!=null?c.lz.toFixed(1):'?'}${c.doing?' · '+esc(c.doing):''}</div></td></tr>`).join('')||'<tr><td class="small">nobody inside</td></tr>';
 document.getElementById('stuck').innerHTML=stuck.slice(-12).reverse().map(s=>`<tr><td>${esc(s.name)}<div class="small">${s.time} · ${esc(s.room)} · ${s.x.toFixed(1)}, ${s.y.toFixed(1)}</div></td></tr>`).join('')||'<tr><td class="small">none yet</td></tr>'}
function levels(){if(!plan)return;const hs=[...new Set(plan.cells.filter(c=>c.height!=null).map(c=>lvl(c.height)))].sort((a,b)=>b-a);
 document.getElementById('levels').innerHTML=['all',...hs].map(h=>`<button class="${h===level?'on':''}" data-l="${h}">${h==='all'?'all levels':'level '+h}</button>`).join('')}
async function loadPlan(name){const r=await fetch('navmap/'+name+'.json',{cache:'no-store'});plan=await r.json();planName=name;cellInfo={};
 plan.cells.forEach(c=>{if(c.oid)cellInfo[c.oid]=c});level='all';levels();fit();renderMaps();draw()}
function renderMaps(){document.getElementById('maps').innerHTML=maps.map(m=>`<button class="${m.name===planName?'on':''}" data-m="${m.name}">${esc(m.template.replace('shared_','').replace('.iff',''))} · ${m.planet}</button>`).join('')||'<span class="small">no floor plans yet: python tools/navmap.py build &lt;planet&gt; &lt;building id&gt;</span>'}
async function poll(){try{data=await(await fetch('data.json',{cache:'no-store'})).json()}catch(e){document.getElementById('status').textContent='map server not answering';return}
 if(!autoPicked&&maps.length){const counts=maps.map(m=>data.chars.filter(c=>c.cell&&m.cells.includes(c.cell)).length);const best=counts.indexOf(Math.max(...counts));
  if(counts[best]>0||!plan){autoPicked=counts[best]>0;await loadPlan(maps[best].name)}}
 const now=new Date().toTimeString().slice(0,8);inside().forEach(c=>{if(c.lx==null)return;const t=trails[c.name]||(trails[c.name]=Object.assign([],{group:c.group}));
  const last=t[t.length-1];if(!last||last[0]!==c.cell||Math.hypot(last[1]-c.lx,last[2]-c.ly)>0.3){t.push([c.cell,c.lx,c.ly]);if(t.length>200)t.shift()}
  if(String(c.doing).startsWith('stuck')&&!stuck.some(s=>s.name===c.name&&Math.hypot(s.x-c.lx,s.y-c.ly)<1&&s.cell===c.cell))
   stuck.push({name:c.name,cell:c.cell,x:c.lx,y:c.ly,time:now,room:(cellInfo[c.cell]||{}).room||''})});
 document.getElementById('status').textContent=`${inside().length} inside · ${data.time}`;sideList();draw()}
document.getElementById('maps').onclick=e=>{const n=e.target.dataset.m;if(n){autoPicked=true;loadPlan(n)}};
document.getElementById('levels').onclick=e=>{const l=e.target.dataset.l;if(l!==undefined){level=l==='all'?'all':Number(l);levels();fit();draw()}};
cv.addEventListener('wheel',e=>{e.preventDefault();if(!view)return;const d=devicePixelRatio||1,r=cv.getBoundingClientRect(),[wx,wy]=toW((e.clientX-r.left)*d,(e.clientY-r.top)*d);
 view.span=Math.min(2000,Math.max(5,view.span*(e.deltaY>0?1.25:.8)));const[nx,ny]=toW((e.clientX-r.left)*d,(e.clientY-r.top)*d);view.cx+=wx-nx;view.cy+=wy-ny;draw()},{passive:false});
cv.addEventListener('pointerdown',e=>{if(view){drag={x:e.clientX,y:e.clientY,cx:view.cx,cy:view.cy};cv.setPointerCapture(e.pointerId)}});
cv.addEventListener('pointerup',()=>drag=null);
cv.addEventListener('pointermove',e=>{const d=devicePixelRatio||1,r=cv.getBoundingClientRect();
 if(drag){const s=view.span/cv.width*d;view.cx=drag.cx-(e.clientX-drag.x)*s;view.cy=drag.cy+(e.clientY-drag.y)*s;draw();return}
 const px=(e.clientX-r.left)*d,py=(e.clientY-r.top)*d,h=hits.filter(h=>Math.hypot(h.x-px,h.y-py)<10*d).pop();
 if(h){tip.style.display='block';tip.textContent=h.label;tip.style.left=(e.clientX-r.left+12)+'px';tip.style.top=(e.clientY-r.top+12)+'px'}else tip.style.display='none'});
addEventListener('resize',draw);
(async()=>{try{maps=await(await fetch('navmaps.json',{cache:'no-store'})).json()}catch(e){}renderMaps();await poll();setInterval(poll,1500)})();
</script></body></html>
'''


def main():
    parser = argparse.ArgumentParser(description='Live map of the test galaxy (read-only).')
    parser.add_argument('--port', type=int, default=8765)
    args = parser.parse_args()
    load_roster()
    threading.Thread(target=record, args=({},), daemon=True).start()
    server = ThreadingHTTPServer(('127.0.0.1', args.port), Handler)
    print(f'live map on http://localhost:{args.port} (who.json: {WHO})', flush=True)
    server.serve_forever()


if __name__ == '__main__':
    main()
