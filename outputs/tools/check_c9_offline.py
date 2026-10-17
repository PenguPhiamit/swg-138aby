"""C9 offline failure-path checks. No clients, credentials or server access."""
import importlib.util
from pathlib import Path
BASE = Path(__file__).resolve().parent / 'bots' / 'scenarios'

def load(name):
    spec = importlib.util.spec_from_file_location(name, BASE / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

class Bot:
    def __init__(self, name, offers=()):
        self.first, self.offers, self.accepted, self.walks = name, offers, [], []
    def gear(self, kit): return {'ok': True}
    def status(self):
        return {'ok':True,'planet':'tatooine','x':0,'y':0,'z':0,'cell':0,
                'me':{'posture':'upright','ham':dict.fromkeys(('health','action','mind'),100),
                      'max_ham':dict.fromkeys(('health','action','mind'),100)}}
    def locate(self, text, **kw):
        if text=='terminal_mission':return [{'oid':1,'x':0,'y':0}]
        if not kw.get('x'):return [{'oid':2,'x':10,'y':10}]
        return []
    def walk(self,*args,**kw):self.walks.append(args);return {'arrived':True}
    def mission_list(self,oid):return self.offers
    def accept_mission(self,oid,terminal):self.accepted.append(oid)
    def missions(self):return []  # stop after selection; acceptance not confirmed
    def inventory(self):return {'ok':True,'items':[]}
    def find(self,*args,**kw):return {'oid':99,'name':'@mob/creature_names:rill','health_pct':100}
    def inspect(self,oid):return {'ok':True,'creature':{'level':30}}
    def fight(self,*args):raise AssertionError('unsafe prey was attacked')

class Group:
    def __init__(self,names,offers=()):self.bots=[Bot(n,offers) for n in names];self.notes=[]
    def __getitem__(self,name):return next(b for b in self.bots if b.first==name)
    def parallel(self,*jobs):return [j() for j in jobs]
    def check(self,label,ok,detail=None):return bool(ok)
    def note(self,text):self.notes.append(text)

def mission(oid,x,planet='tatooine'):
    return {'oid':oid,'type':'destroy','difficulty':1,'container_name':'mission_bag',
            'waypoint':{'x':x,'y':0,'planet':planet}}

# cresh-missions.py: the 600 m rule went on 15 Oct (targets are 1000-2000 m out) and the scenario was rewritten on
# 17 Oct for every mission terminal type; its offline tests are bots/test_missions.py (Claude).

g=Group(['Aurek','Jesh','Tamsin'])
load('aurek-doctor-buffs').run(g)
assert not any(b.walks for b in g.bots) and any('interior treatment anchor' in n for n in g.notes)

g=Group(['Besh','Dova','Pell','Varo'])
load('besh-harvest').run(g)
assert any('above 5' in n for n in g.notes)
print('PASS: missing hospital cell, strong-prey refusal (offline); missions: bots/test_missions.py')
