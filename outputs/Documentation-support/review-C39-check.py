#!/usr/bin/env python3
"""Offline C39 source regressions; no server process, build or bot access.

Run in Debian as swgemu: python3 review-C39-check.py [--repo /opt/swg/Core3-gpt].
Narrow stand-ins exercise actual extracted helpers; they do not prove server ABI,
locking, persistence, network delivery or in-game behavior.
"""
import argparse
from pathlib import Path
import subprocess
import tempfile

ap = argparse.ArgumentParser()
ap.add_argument('--repo', type=Path, default=Path('/opt/swg/Core3-gpt'))
args = ap.parse_args()
root = args.repo / 'MMOCoreORB'


def function(text, signature):
    start = text.index(signature)
    pos = text.index('{', start)
    depth, end = 1, pos + 1
    while depth:
        depth += (text[end] == '{') - (text[end] == '}')
        end += 1
    return text[start:end]


header = (root/'src/server/zone/objects/creature/commands/SandboxTestGalaxy.h').read_text()
helpers = '\n'.join(line for line in header.splitlines() if not line.startswith('#'))
cpp = r'''
#include <cassert>
#include <string>
#include <iostream>
struct String : std::string {
 using std::string::string;
 String(std::string s):std::string(s){}
 static String valueOf(int v){return std::to_string(v);}
 bool endsWith(const char* suffix) {return size()>=std::string(suffix).size() && compare(size()-std::string(suffix).size(), std::string(suffix).size(), suffix)==0;}
};
constexpr unsigned STRING_HASHCODE(const char*) {return 123;}
struct Names {bool allowed=false; bool contains(const String&) const {return allowed;}};
struct ConfigManager {
 String db="swgemu"; Names names; bool enabled=false;
 static ConfigManager* instance(){static ConfigManager c;return &c;}
 String getDBName(){return db;}
 const Names& getStringVector(const char*){return names;}
 bool getBool(const char*,bool){return enabled;}
};
struct Account {String getUsername(){return "agent";}};
struct AccountManager {static bool present; static Account* getAccount(int,bool){static Account a;return present?&a:nullptr;}};
bool AccountManager::present=true;
struct PlayerObject {
 bool god=false,priv=false;
 bool hasGodMode(){return god;} bool isPrivileged(){return priv;} int getAccountID(){return 1;}
};
struct SceneObject {unsigned crc=123; unsigned getServerObjectCRC(){return crc;}};
struct SkillModManager {enum {CITY,DROID,STRUCTURE};};
struct FactionStatus {static constexpr int OVERT=1;};
struct BuildingObject {bool isPlayerRegisteredWithin(int){return true;} unsigned getFaction(){return 1;}};
template<class T>T cast(BuildingObject* p){return static_cast<T>(p);}
template<class T>using ManagedReference=T;
struct CreatureObject {
 bool player=true; PlayerObject* ghost=nullptr; int city=0,droid=0,structure=0,treatment=0,perk=0;
 float fatigue=1; BuildingObject* building=nullptr;
 bool isPlayerCreature(){return player;} PlayerObject* getPlayerObject(){return ghost;}
 float calculateBFRatio(){return fatigue;}
 int getSkillModOfType(const char*,int type){return type==SkillModManager::CITY?city:type==SkillModManager::DROID?droid:structure;}
 int getSkillMod(const char* key){return std::string(key)=="private_faction_medical_rating"?perk:treatment;}
 BuildingObject* getRootParent(){return building;}
 int getObjectID(){return 1;}unsigned getFaction(){return 1;}int getFactionStatus(){return 1;}
};
using uint32=unsigned;
'''
cpp += helpers
for pack in ['EnhancePack', 'WoundPack']:
    path = f'MMOCoreORB/src/server/zone/objects/tangible/pharmaceutical/{pack}Implementation.cpp'
    old = subprocess.check_output(['git','-C',str(args.repo),'show',f'90044b8e:{path}'],text=True)
    dev = subprocess.check_output(['git','-C',str(args.repo),'show',f'81384b90:{path}'],text=True)
    new = (args.repo/path).read_text()
    for prefix, source in [('Old', old), ('Dev', dev), ('New', new)]:
        name = prefix + pack
        cpp += f'struct {name} {{float getEffectiveness(){{return 100;}} bool isDroidReconstructionKit(){{return false;}} uint32 calculatePower(CreatureObject*,CreatureObject*,bool);}};\n'
        body = function(source, f'uint32 {pack}Implementation::calculatePower(')
        body = body.replace(f'{pack}Implementation::', name+'::')
        if prefix == 'Dev':
            body = body.replace('medicalAnywhere()', 'medicalAnywhere(healer)')
        cpp += body+'\n'
cpp += r'''
int main(){
 auto cfg=ConfigManager::instance(); PlayerObject ghost; CreatureObject player; player.ghost=&ghost; SceneObject pad;
 int cases=0;
 for(bool test:{false,true}) for(bool enabled:{false,true}) for(bool god:{false,true})
 for(bool allowed:{false,true}) for(bool account:{false,true}) {
  cfg->db=test?"swgemu_test":"swgemu";cfg->enabled=enabled;cfg->names.allowed=allowed;
  ghost.god=god;AccountManager::present=account;
  bool expected=test&&(god||(allowed&&account));
  assert(isSandboxTestPlayer(&player)==expected);
  assert(medicalAnywhere(&player)==(expected&&enabled));++cases;
 }
 cfg->db="swgemu_test"; assert(!isSandboxTestPlayer(nullptr));
 player.ghost=nullptr;assert(!isSandboxTestPlayer(&player));player.ghost=&ghost;
 player.player=false;assert(!isSandboxTestPlayer(&player));player.player=true;
 for(bool test:{false,true}) for(bool privileged:{false,true}) {
  cfg->db=test?"swgemu_test":"swgemu";ghost.priv=privileged;
  assert(canUseSandboxDatapad(&pad,&player)==(test&&privileged));
  pad.crc=456;assert(canUseSandboxDatapad(&pad,&player));pad.crc=123;
 }
 assert(!canUseSandboxDatapad(nullptr,&player));assert(!canUseSandboxDatapad(&pad,nullptr));
 std::cout<<"gate matrix "<<cases<<" + null/NPC/datapad controls PASS\n";
 OldEnhancePack oe;NewEnhancePack ne;DevEnhancePack de;
 OldWoundPack ow;NewWoundPack nw;DevWoundPack dw;
 BuildingObject building;int balance=0;
 for(bool test:{false,true}) for(int city:{0,10,100}) for(int droid:{0,50,100}) for(int structure:{0,50,100})
 for(int skill:{0,100}) for(bool fatigue:{false,true}) for(bool inside:{false,true}) {
  cfg->db=test?"swgemu_test":"swgemu";cfg->enabled=false;ghost.god=true;
  player.city=city;player.droid=droid;player.structure=structure;player.treatment=skill;player.fatigue=.5;
  player.building=inside?&building:nullptr;player.perk=inside?10:0;
  assert(oe.calculatePower(&player,&player,fatigue)==ne.calculatePower(&player,&player,fatigue));
  assert(ow.calculatePower(&player,&player,fatigue)==nw.calculatePower(&player,&player,fatigue));++balance;
 }
 cfg->db="swgemu_test";cfg->enabled=true;ghost.god=true;
 player.city=10;player.droid=0;player.structure=0;player.treatment=0;player.building=nullptr;player.perk=0;
 assert(de.calculatePower(&player,&player,false)==10);assert(ne.calculatePower(&player,&player,false)==110);
 assert(dw.calculatePower(&player,&player,false)==110);assert(nw.calculatePower(&player,&player,false)==uint32(100.f*(1.f+110.f/100.f)));
 std::cout<<"medical flag-off exact baseline equivalence "<<balance<<" cases per pack PASS; city-only override enhance 10 -> 110, wound 110 -> "<<nw.calculatePower(&player,&player,false)<<" PASS\n";
}
'''

lua = r'''
local root = assert(arg[1]) .. '/MMOCoreORB/bin/scripts/'
local base = {new = function(self, t) return t end}
SharedTangibleObjectTemplate = base
object_tangible_terminal_shared_terminal_character_builder = base
ObjectTemplates = {addTemplate = function() end}
CHARACTERBUILDERTERMINAL = 1
includeFile = function(p) dofile(root .. 'object/' .. p) end
includeFile('tangible/terminal/terminal_character_builder.lua')
local pageCollisions, maxRows, leaves = 0, 0, 0
local function walk(list)
 assert(#list % 2 == 0)
 maxRows=math.max(maxRows,#list/2)
 local seen={}
 for i=1,#list,2 do
  local label,value=list[i],list[i+1]
  if type(value)=='table' then
   if seen[label] then pageCollisions=pageCollisions+1 end
   walk(value)
  else leaves=leaves+1 end
  seen[label]=true
 end
end
walk(object_tangible_terminal_terminal_character_builder.itemList)
assert(pageCollisions==0, 'colliding submenu/page names: '..pageCollisions)
assert(maxRows<=50, 'actual character-builder list exceeds 50')
-- Exercise the actual local paging/tidying functions with synthetic boundary lists.
local f=assert(io.open(root..'object/sandbox/tools_datapad.lua'))
local source=f:read('*a');f:close()
local tidy,paged=assert(load(source..'\nreturn tidy,paged'))()
for _,n in ipairs({0,1,49,50,51,100,101,10001}) do
 local input={}
 for i=1,n do input[#input+1]='Same prefix '..i;input[#input+1]='item'..i end
 local out=tidy(input,'boundary',{},false)
 local count=0
 local function sum(t)
  assert(#t%2==0)
  for i=1,#t,2 do
   if type(t[i+1])=='table' then assert(#t[i+1]/2<=50);sum(t[i+1]) else count=count+1 end
  end
 end
 sum(out); assert(count==n, 'lost boundary item')
 local seen={}
 for i=1,#out,2 do assert(not seen[out[i]]);seen[out[i]]=true end
end
dofile(root..'screenplays/sandbox/sandbox_creatures.lua')
local n,maxPage=0,0
for _,folder in ipairs(SandboxCreatureFolders) do
 for _,page in ipairs(folder[3]) do n=n+#page[2];maxPage=math.max(maxPage,#page[2]) end
end
assert(n==1052 and maxPage<=60)
-- Execute actual Lua callbacks with minimal scene/player stand-ins.
CreatureObject=function(p)return p end
PlayerObject=function(p)return p end
SceneObject=function(p)return p end
local player={getPlayerObject=function(self)return self end,isPrivileged=function()return true end,
 sendSystemMessage=function()end,switchZone=function(self,...) self.jumps=self.jumps+1 end,jumps=0}
local pad={getObjectID=function()return 1 end}
isZoneEnabled=function(zone)return zone=='tatooine' end
local point=''
readScreenPlayData=function()return point end
local cell=nil
getSceneObject=function()return cell end
dofile(root..'screenplays/sandbox/sandbox_tools_datapad.lua')
for _,bad in ipairs({'','garbage','removed 1 2 3 0','tatooine word 2 3 0','tatooine 1 2 3 99'}) do
 point=bad;SandboxTestDatapad:teleportCallback(player,nil,0,'0');assert(player.jumps==0)
end
point='tatooine 1 2 3 99'
cell={isCellObject=function()return false end,getZoneName=function()return 'tatooine' end}
SandboxTestDatapad:teleportCallback(player,nil,0,'0');assert(player.jumps==0)
cell={isCellObject=function()return true end,getZoneName=function()return 'naboo' end}
SandboxTestDatapad:teleportCallback(player,nil,0,'0');assert(player.jumps==0)
cell={isCellObject=function()return true end,getZoneName=function()return 'tatooine' end}
SandboxTestDatapad:teleportCallback(player,nil,0,'0');assert(player.jumps==1)
point='tatooine 1 2 3 0';SandboxTestDatapad:teleportCallback(player,nil,0,'0');assert(player.jumps==2)
for _,index in ipairs({'-1','99999','garbage'}) do
 assert(SandboxTestDatapad:picked(0,index,{1,2})==nil)
end
assert(SandboxTestDatapad:picked(0,'0',{})==nil)
assert(SandboxTestDatapad:picked(1,'0',{1})==nil)
print('menu audit PASS: '..leaves..' leaves; max builder rows '..maxRows..'; 1052 creatures, max page '..maxPage)
print('paging 0/1/49/50/51/100/101/10001, callback bounds, Lua back stale/valid cases PASS')
'''

with tempfile.TemporaryDirectory(prefix='c39-') as temp:
    tmp = Path(temp)
    (tmp/'gates.cpp').write_text(cpp)
    subprocess.run(['g++', '-std=c++17', str(tmp/'gates.cpp'), '-o', str(tmp/'gates')], check=True)
    subprocess.run([str(tmp/'gates')], check=True)
    (tmp/'menus.lua').write_text(lua)
    subprocess.run(['lua5.3', str(tmp/'menus.lua'), str(args.repo)], check=True)

for name in ['ObjectManager.cpp', 'ActivateQuestCommand.h']:
    files = subprocess.check_output(['git','-C',str(args.repo),'ls-files',f'*{name}'],text=True).splitlines()
    for file in files:
        before = subprocess.check_output(['git','-C',str(args.repo),'rev-parse',f'90044b8e:{file}'],text=True).strip()
        after = subprocess.check_output(['git','-C',str(args.repo),'rev-parse',f'81384b90:{file}'],text=True).strip()
        assert before == after, file
        print('unchanged baseline/reviewed blob:', file, before)

commits = subprocess.check_output(['git','-C',str(args.repo),'rev-list','--reverse','90044b8e..81384b90'],text=True).splitlines()
assert len(commits) == 10
for commit in commits:
    # Read each full commit, including its patch, in addition to the combined diff.
    subprocess.check_output(['git','-C',str(args.repo),'show','--format=fuller',commit],text=True)
numstat = subprocess.check_output(['git','-C',str(args.repo),'diff','--numstat','90044b8e','81384b90'],text=True)
rows = [line.split('\t') for line in numstat.splitlines()]
assert (len(rows),sum(int(r[0]) for r in rows),sum(int(r[1]) for r in rows)) == (19,1770,47)
diff = subprocess.check_output(['git','-C',str(args.repo),'diff','90044b8e','81384b90'],text=True)
import re
paths = set()
for line in diff.splitlines():
    if line.startswith('+') and not line.startswith('+++'):
        paths.update(re.findall(r'"(object/[^"\n]+\.iff)"',line))
for path in sorted(paths):
    p = root/'bin/scripts'/path.replace('.iff','.lua')
    if path == 'object/tangible/sandbox/tools_datapad.iff':
        p = root/'bin/scripts/object/sandbox/tools_datapad.lua'
    assert p.is_file() and path in p.read_text(), path
print(f'pinned scope: {len(commits)} commits, 19 files, +1770/-47; {len(paths)} added literal templates registered')

# Use the project's Lua checker with only its checkout/user plumbing adapted in memory.
checker = Path(__file__).resolve().parent.parent/'tools/check_lua.py'
source = checker.read_text().replace("SERVER = Path('/opt/swg/Core3')", f'SERVER = Path({str(args.repo)!r})')
source = source.replace("['runuser','-u','swgemu','--','git'", "['git'")
import sys
sys.argv = [str(checker), '--since', '90044b8e']
try:
    exec(compile(source, str(checker), 'exec'), {'__name__': '__main__'})
except SystemExit as e:
    if e.code:
        raise
print('C39 offline checks PASS; server build/runtime/persistence NOT TESTED')
