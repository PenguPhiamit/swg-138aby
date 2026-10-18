"""Offline check of Claude's C62 fixes (18 Oct 2026), the reverse of GPT's check_c62.py: the same substitute engine,
the fixed Lua from the dev working tree, and each of GPT's failing cases asserted to pass now. Run in WSL as swgemu."""
import pathlib, subprocess, sys

S = pathlib.Path('/opt/swg/Core3-dev/MMOCoreORB/bin/scripts')
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
    table.insert(self.waypoints,{id=nextId,name=name,kind=kind})
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
loaded = '\n'.join((S / f).read_text() for f in files)
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
run = subprocess.run(['lua5.3', '-'], input=host + loaded + tests, text=True, capture_output=True)
print(run.stdout.strip())
if run.returncode:
    print(run.stderr.strip())
    sys.exit(1)
