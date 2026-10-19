"""Pinned C62 repair checks and C65 edge cases; run in WSL as swgemu.

Lua handlers run with substitute engine objects, not a galaxy. Relog cases copy
the persisted fields only; they do not test the database or network. C++ checks
are source contracts / predicate models, not compiled engine execution.
Exit 1 when any extended acceptance case fails, preserving all case results.
"""
import json, math, os, pathlib, re, subprocess, sys

ROOT = pathlib.Path('/opt/swg/Core3-dev')
REV = '35e7dbe64c235befc3f1da3fd3aa0d0301c36a08'
os.environ['GIT_OPTIONAL_LOCKS'] = '0'

def source(path):
    return subprocess.check_output(['git', '-C', str(ROOT), 'show', f'{REV}:MMOCoreORB/{path}'], text=True)

host = r'''
local function new(self, t) return t end
ScreenPlay={new=new}; CityScreenPlay={new=new}; conv_handler={new=new}
HuttaLifePlaces={patrolPoints={},patrolMobiles={},stationaryMobiles={},sites={freighter_wreck={x=1,y=2,z=3}},questGiver={0,5,6}}
Creature={new=new}; creatureTemplates={}
CreatureTemplates={addCreatureTemplate=function(self,t,name) creatureTemplates[name]=t end}
MOB_CARNIVORE=1; MOB_HERBIVORE=2; PACK=1; KILLER=2; HERD=4; NONE=0; STALKER=8
AGGRESSIVE=1; ATTACKABLE=2; ENEMY=4; AIENABLED=1; CARNIVORE=1; HERBIVORE=2
ConvoScreen={new=new}
ConvoTemplate={new=function(self,t)
  t.screens={}
  function t:addScreen(s) self.screens[s.id]=s end
  function t:getScreen(id) return assert(self.screens[id], id) end
  return t
end}
conversations={}
function addConversationTemplate(name,t) conversations[name]=t end
function registerScreenPlay() end
function LuaConversationTemplate(p) return p end
function LuaConversationScreen(p) return p end
function CreatureObject(p) return p end
function SceneObject(p) return p end
function PlayerObject(p) return p end
function AiAgent(p) return p end
function readScreenPlayData(p,sp,k) return (p.states[sp] or {})[k] or "" end
function writeScreenPlayData(p,sp,k,v)
  p.states[sp]=p.states[sp] or {}; p.states[sp][k]=tostring(v)
end
WAYPOINTQUESTTASK=123; WAYPOINT_YELLOW=1
local nextId=1000
function player()
  local p={states={},waypoints={},cash=0,bank=0}
  function p:isPlayerCreature() return true end
  function p:isAiAgent() return false end
  function p:isGrouped() return false end
  function p:getPlayerObject() return self end
  function p:sendSystemMessage() end
  function p:addBankCredits(v) self.bank=self.bank+v end
  function p:addCashCredits(v) self.cash=self.cash+v end
  function p:getSlottedObject() return {isContainerFullRecursive=function() return false end} end
  function p:removeWaypointBySpecialType(kind)
    for i=#self.waypoints,1,-1 do
      if self.waypoints[i].kind==kind then table.remove(self.waypoints,i) end
    end
  end
  function p:addWaypoint(planet,name,desc,x,z,y,color,a,b,kind)
    nextId=nextId+1
    -- Real PlayerObject::addWaypoint replaces the matching nonzero special type.
    if kind ~= 0 then self:removeWaypointBySpecialType(kind) end
    table.insert(self.waypoints,{id=nextId,name=name,kind=kind,planet=planet,x=x,z=z,y=y})
    return nextId
  end
  function p:removeWaypoint(id,notify)
    for i=#self.waypoints,1,-1 do
      if self.waypoints[i].id==id then table.remove(self.waypoints,i) end
    end
  end
  return p
end
function createLoot() end
function giveItem() end
function has(p,pattern) for _,w in ipairs(p.waypoints) do if w.name:find(pattern) then return true end end return false end
'''
files = ['mobile/hoth/hoth_fill_creatures.lua'] + [f'mobile/hoth/{n}.lua' for n in (
    'hoth_wampa', 'hoth_elder_wampa', 'hoth_wampa_matriarch', 'hoth_wampa_snowblind', 'hoth_mynock_broodmother',
    'hoth_wampa_icemaw', 'hoth_wampa_patriarch', 'hoth_wampa_frostfang')] + [
    'mobile/conversations/sandbox/ossus_people_conv.lua', 'screenplays/sandbox/ossus_people.lua',
    'screenplays/sandbox/hoth_world.lua', 'screenplays/sandbox/hutta_life.lua']
loaded = '\n'.join(source('bin/scripts/' + f) for f in files)
tests = r'''
-- F1: no resistance over 200 on any Hoth creature loaded; the bosses keep their order of toughness.
local n=0
for name,t in pairs(creatureTemplates) do
  for i,v in ipairs(t.resists or {}) do assert(v<=200, name.." resist "..i.."="..v) end
  n=n+1
end
local function heat(name) return creatureTemplates[name].resists[4] end
assert(heat("hoth_wampa_rimefang")==190 and heat("hoth_wampa_old_echo")==195)
print("F1 fixed: "..n.." templates, none over 200; Rimefang heat "..heat("hoth_wampa_rimefang")..", Old Echo "..heat("hoth_wampa_old_echo"))

-- F2: road walked and paid, then the lead; also lead from the reward screen; lead before the road still works.
local t=conversations.ossus_vault_archivist_convo_template
local function sid(s) function s:getScreenID() return self.id end return s end
local function offers(s, target) for _,o in ipairs(s.options) do if o[2]==target then return true end end return false end
local p=player(); p.states.OssusPeople={roadStep="3"}
local first=sid(OssusVaultArchivistConvoHandler:getInitialScreen(p,nil,t))
assert(first.id=="road_reward" and offers(first,"ghostfire_lead") and first.stopConversation=="false")
OssusVaultArchivistConvoHandler:runScreenHandlers(t,p,nil,0,first)
local after=sid(OssusVaultArchivistConvoHandler:getInitialScreen(p,nil,t))
assert(after.id=="greet_done" and offers(after,"ghostfire_lead"))
OssusVaultArchivistConvoHandler:runScreenHandlers(t,p,nil,0,sid(t:getScreen("ghostfire_lead")))
assert(readScreenPlayData(p,"OssusPeople","ghostfire")=="lead")
local q=player()
assert(OssusVaultArchivistConvoHandler:getInitialScreen(q,nil,t).id=="greet")
OssusVaultArchivistConvoHandler:runScreenHandlers(t,q,nil,0,sid(t:getScreen("ghostfire_lead")))
assert(readScreenPlayData(q,"OssusPeople","ghostfire")=="lead")
print("F2 fixed: paid road -> greet_done offers the lead and it sets 'lead'; lead before the road unchanged")

-- F3: an owned pet's kill credits its owner on both jobs; a creature nobody owns gives nothing.
local function pet(owner) return {isPlayerCreature=function() return false end, isAiAgent=function() return true end,
  isPet=function() return owner~=nil end, getOwner=function() return owner end} end
local h=player(); HothFillJobs:accept(h,"rimefang")
HothFillJobs:creditKill({},pet(nil),"rimefang"); assert(HothFillJobs:getStep(h,"rimefang")==1)
HothFillJobs:creditKill({},pet(h),"rimefang"); assert(HothFillJobs:getStep(h,"rimefang")==2)
local k=player(); HuttaKessothJob.waypoints={{"freighter_wreck","w1"},{"freighter_wreck","w2"},{"freighter_wreck","w3"}}
HuttaKessothJob:setStep(k,1)
HuttaKessothJob:creditKill({},pet(nil),1); assert(HuttaKessothJob:getStep(k)==1)
HuttaKessothJob:creditKill({},pet(k),1); assert(HuttaKessothJob:getStep(k)==2)
print("F3 fixed: an owned pet's kill advances both jobs for its owner; an unowned creature's does not")

-- F5: two Hoth jobs keep both markers; a stock quest-task marker survives; finishing one job removes only its own.
local w=player()
w:addWaypoint("tatooine","stock quest task","",0,0,0,1,true,true,WAYPOINTQUESTTASK)
HothFillJobs:accept(w,"echo"); HothFillJobs:accept(w,"rimefang"); HothFillJobs:accept(w,"pryce")
assert(has(w,"Hask") and has(w,"Tavi") and has(w,"Dellan") and has(w,"stock quest task") and #w.waypoints==4)
HothFillJobs:reward(w,"pryce")
assert(not has(w,"Dellan") and has(w,"Hask") and has(w,"Tavi") and has(w,"stock quest task"))
HuttaKessothJob:setStep(w,0); HuttaKessothJob:accept(w)
assert(has(w,"w1") and has(w,"Hask") and has(w,"stock quest task"))
HuttaKessothJob:advance(w,1)
assert(has(w,"w2") and not has(w,"w1") and has(w,"Tavi"))
-- retrack: a lost marker comes back when the player talks to the giver, without a duplicate
for i=#w.waypoints,1,-1 do if w.waypoints[i].name:find("Hask") then table.remove(w.waypoints,i) end end
HothFillJobs:retrack(w,"echo"); HothFillJobs:retrack(w,"echo")
local c=0; for _,x in ipairs(w.waypoints) do if x.name:find("Hask") then c=c+1 end end
assert(c==1)
print("F5 fixed: each job keeps its own marker; stock quest-task markers survive; talking to the giver restores one")
'''
extra = pathlib.Path(__file__).with_name('c65_cases.lua').read_text()
run = subprocess.run(['lua5.3', '-'], input=host + loaded + tests + extra, text=True, capture_output=True)
print(run.stdout.strip())
if run.stderr:
    print(run.stderr.strip())
cases = []
for line in run.stdout.splitlines():
    if line.startswith('CASE\t'):
        _, status, name, detail = line.split('\t', 3)
        cases.append({'name': name, 'ok': status == 'PASS', 'detail': detail})

def check(name, ok, detail):
    cases.append({'name': name, 'ok': bool(ok), 'detail': detail})
    print(('PASS' if ok else 'FAIL') + ': ' + name + ' - ' + detail)

binding = source('src/server/zone/objects/player/LuaPlayerObject.cpp')
check('F5 real waypoint binding returns an ID and defaults persistent',
      'lua_pushinteger(L, waypoint->getObjectID())' in binding and 'persistence = 1' in binding,
      'Static binding contract, not a persistence run')
callback = source('src/server/zone/objects/player/sui/callbacks/BankTerminalSuiCallback.h')
check('F6 submitted-window state guard precedes range and transfer',
      callback.index('player->isDead() || player->isIncapacitated()') < callback.index('player->isInRange(bankObject, 8)')
      < callback.index('transferCredits'), 'Pinned callback source order; no SUI dispatched')
combat = source('src/server/zone/managers/combat/CombatManager.cpp')
check('F1 NPC resistance upper cap',
      re.search(r'if \(resist > 100\.f\)\s+resist = 100\.f;', combat) is not None,
      'Pinned cap source contract; damage arithmetic exercised by Lua')

# Evaluate the actual pinned bool expressions after substituting engine values.
# This checks their logic, not C++ execution, observer dispatch or engine vectors.
mission = source('src/server/zone/objects/mission/MissionObjectiveImplementation.cpp')
expressions = {name: re.search(r'bool ' + name + r' = ([^;]+);', mission).group(1)
               for name in ('sameZone', 'nearOwner', 'endPointCounts', 'nearEnd')}
def eligibility(kind, same_zone, owner, member, endpoint):
    values = {'memberZone': 'same' if same_zone else 'other', 'ownerZone': 'same',
              'ownerDistance': math.dist(member[:2], owner[:2]),
              'endDistance': math.dist((*member[:2],0) if kind == 'BOUNTY' else member, endpoint),
              'missionType': kind}
    substitutions = {'groupMember->getZone()': 'memberZone',
                     'memberFlat.distanceTo(ownerPoint)': 'ownerDistance',
                     'memberPosition.distanceTo(missionEndPoint)': 'endDistance',
                     'MissionTypes::DESTROY': repr('DESTROY'),
                     'MissionTypes::HUNTING': repr('HUNTING')}
    for name, expression in expressions.items():
        for old, new in substitutions.items():
            expression = expression.replace(old, new)
        values[name] = eval(expression.replace('&&', ' and ').replace('||', ' or '),
                            {'__builtins__': {}}, values)
    decision = re.search(r'if \((nearEnd \|\| nearOwner)\)', mission).group(1)
    return eval(decision.replace('||', ' or '), {'__builtins__': {}}, values)

kinds = ('DESTROY','HUNTING','DELIVER','CRAFTING','DANCER','MUSICIAN','RECON','SURVEY','BOUNTY')
check('F4 matching coordinates on another planet across nine implemented mission types',
      all(not eligibility(k,False,(250,0,0),(0,0,0),(0,0,0)) for k in kinds),
      'Pinned eligibility expressions evaluated with substitute distances/zones')
check('F4 stale destroy and hunting listing locations are excluded',
      all(not eligibility(k,True,(250,0,0),(0,0,0),(0,0,0)) for k in ('DESTROY','HUNTING')),
      'Owner 250 m away; member at the stale endpoint')
check('F4 delivery/crafting/recon/performance completion anchors retained',
      all(eligibility(k,True,(300,0,0),(20,0,0),(0,0,0)) for k in ('DELIVER','CRAFTING','RECON','DANCER','MUSICIAN')),
      'Same-zone members near the intended endpoint can qualify when away from owner')
check('F4 near-owner eligibility ignores height and life state by policy; strict 128 m',
      eligibility('DESTROY',True,(250,0,0),(260,0,100),(0,0,0))
      and not eligibility('DESTROY',True,(0,0,0),(128,0,0),(0,0,0)),
      'No dead/alive input in the pinned predicate; distance is flat and <128')
check('F4 actual destroy helper paid after owner retreats',
      eligibility('DESTROY',True,(300,0,0),(20,0,0),(0,0,0)),
      'FAIL case: helper at actual lair (20,0), owner at (300,0); old endpoint (0,0)')
check('F4 whole-group divisor and integer split retained',
      'playerCount = group->getNumberOfPlayerMembers()' in mission
      and 'divisor = playerCount' in mission
      and 'mission->getRewardCredits() / Math::max(divisor, 1)' in mission
      and 1000//max(2,2,1)==500 and 1001//max(2,3,1)==333,
      'Source contract and arithmetic: 1000/2=500 each; 1001/3=333, even with only two eligible players')

state_expression = re.search(r'if \((player->isDead\(\) \|\| player->isIncapacitated\(\))\)', callback).group(1)
state_expression = state_expression.replace('player->isDead()', 'dead').replace('player->isIncapacitated()', 'incap').replace('||', ' or ')
range_source = source('src/server/zone/objects/scene/SceneObjectImplementation.cpp')
range_body = range_source[range_source.index('bool SceneObjectImplementation::isInRange('):]
range_body = range_body[:range_body.index('\n}')]
check('F6 real range helper is same-zone, horizontal and inclusive',
      'getZone() != object->getZone()' in range_body and range_body.count('setZ(0)') == 2
      and re.search(r'<=\s*range\s*\*\s*range', range_body) is not None,
      'Static contract for callback/radial isInRange(...,8)')
def bank_allowed(dead, incap, same_zone, distance):
    blocked = eval(state_expression, {'__builtins__': {}}, {'dead': dead, 'incap': incap})
    return not blocked and same_zone and distance <= 8
check('F6 alive to dead/incap submitted window and 8 m boundary model',
      all(not bank_allowed(dead,incap,True,d) for dead,incap in ((True,False),(False,True)) for d in (0,8))
      and bank_allowed(False,False,True,7.99) and bank_allowed(False,False,True,8)
      and not bank_allowed(False,False,True,8.01) and not bank_allowed(False,False,False,0),
      'Source-derived state predicate plus source-verified range model; no bank transaction executed')

# H1: the new radius is calculated before database fields are restored. The IDL
# declares radius persistent; neither building transient init nor load callback
# recalculates it. Model that ordering, without reading any world database.
H1_REV = '0262d8deb36c9ced07b9a226e0aa8614335ad3ee'
def h1_source(path):
    return subprocess.check_output(['git','-C',str(ROOT),'show',f'{H1_REV}:MMOCoreORB/{path}'], text=True)
building = h1_source('src/server/zone/objects/building/BuildingObjectImplementation.cpp')
tree_idl = h1_source('src/server/zone/TreeEntry.idl')
manager = h1_source('src/server/zone/managers/object/ObjectManager.cpp')
check('H1 source has persistent radius and template-before-deserialization order',
      'protected float radius;' in tree_idl
      and manager.index('object = instantiateSceneObject(serverObjectCRC, objectID, true)')
          < manager.index('deSerializeObject(scene, &objectData)')
      and 'setRadius(reach)' in building,
      'Static lifecycle contract, not a database load test')
transient_body = building[building.index('void BuildingObjectImplementation::initializeTransientMembers()'):building.index('void BuildingObjectImplementation::loadTemplateData(')]
check('H1 database restore has no building radius refresh',
      'setRadius' not in transient_body and 'loadTemplateData(' not in transient_body
      and 'BuildingObjectImplementation::notifyLoadFromDatabase' not in building,
      'Pinned building load lifecycle; generated TreeEntry reader also inspected separately')
def building_range(radius, quad=False):
    base = 768 if quad else 192
    return max(base,192+radius) if radius > 96 else base
check('H1 fresh layout radius boundaries and quad-range preservation',
      building_range(96)==192 and building_range(96.01)>288
      and building_range(769.8468)>961
      and building_range(126.53,True)==768,
      'Source formula model; does not benchmark range updates')
computed_radius = 483.01  # stock Jabba palace floor bounds
saved_pre_fix_radius = 0.5
restored_radius = saved_pre_fix_radius  # persistent field read follows template load
check('H1 existing saved building retains newly calculated reach',
      building_range(restored_radius) == building_range(computed_radius),
      'FAIL lifecycle model: 483.01 m reach is overwritten by saved radius 0.5; range returns to 192 m')

result = {'revision': REV, 'h1_revision': H1_REV, 'kind': 'offline substitute Lua / static C++ contracts',
          'original_lua_checks_ok': run.returncode == 0, 'cases': cases,
          'lua_error': run.stderr.strip()}
out = pathlib.Path(__file__).with_name('C65-checks.json')
out.write_text(json.dumps(result, indent=2) + '\n')
failed = sum(not c['ok'] for c in cases)
print(f'C65 extended cases: {len(cases)-failed}/{len(cases)} pass; {failed} fail; evidence: {out.name}')
sys.exit(1 if failed or run.returncode else 0)
