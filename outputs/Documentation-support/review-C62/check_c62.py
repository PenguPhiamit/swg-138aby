"""Read-only C62 evidence: pinned Lua syntax and actual-script counterexamples.

Run in WSL as swgemu. Writes only checks.json beside this script in h.
The small Lua host substitutes engine objects; these are not gameplay tests.
"""
import hashlib
import json
import os
from pathlib import Path
import subprocess

BASE = "a8ece12b6705158b1ec9706ba61077a4249be226"
TIP = "aa52cc647a2129096011eb122fe98c7794db4c2b"
ROOT = Path("/opt/swg/Core3-dev")
os.environ["GIT_OPTIONAL_LOCKS"] = "0"


def git(*args):
    return subprocess.check_output(["git", "-C", str(ROOT), *args], text=True)


def source(path):
    return git("show", f"{TIP}:MMOCoreORB/{path}")


report = {"base": BASE, "tip": TIP, "head_before": git("rev-parse", "HEAD").strip()}
commits = git("rev-list", "--reverse", f"{BASE}..{TIP}").splitlines()
report["commit_count"] = len(commits)
syntax = []
for commit in commits:
    paths = git("diff-tree", "--no-commit-id", "--name-only", "--diff-filter=ACMRT", "-r", commit).splitlines()
    for path in paths:
        if path.endswith(".lua"):
            data = git("show", f"{commit}:{path}")
            result = subprocess.run(["luac5.3", "-p", "-"], input=data, text=True, capture_output=True)
            syntax.append({"commit": commit[:8], "path": path, "sha256": hashlib.sha256(data.encode()).hexdigest(),
                           "ok": result.returncode == 0, "error": result.stderr.strip()})
report["lua_at_commit"] = syntax
paths = git("diff", "--name-only", "--diff-filter=ACMRT", BASE, TIP).splitlines()
report["changed_files_at_tip"] = len(paths)
current = []
for path in paths:
    if path.endswith(".lua"):
        data = git("show", f"{TIP}:{path}")
        result = subprocess.run(["luac5.3", "-p", "-"], input=data, text=True, capture_output=True)
        current.append({"path": path, "ok": result.returncode == 0, "error": result.stderr.strip()})
report["lua_at_tip"] = current

host = r'''
local function new(self, t) return t end
ScreenPlay={new=new}; CityScreenPlay={new=new}; conv_handler={new=new}
HuttaLifePlaces={patrolPoints={},patrolMobiles={},stationaryMobiles={}}
Creature={new=new}; creatureTemplates={}
CreatureTemplates={addCreatureTemplate=function(self,t,name) creatureTemplates[name]=t end}
MOB_CARNIVORE=1; MOB_HERBIVORE=2; PACK=1; KILLER=2; HERD=4
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
function readScreenPlayData(p,sp,k) return (p.states[sp] or {})[k] or "" end
function writeScreenPlayData(p,sp,k,v)
  p.states[sp]=p.states[sp] or {}; p.states[sp][k]=tostring(v)
end
WAYPOINTQUESTTASK=123; WAYPOINT_YELLOW=1
function player()
  local p={states={},waypoints={},cash=0,bank=0}
  function p:isPlayerCreature() return true end
  function p:isGrouped() return false end
  function p:getPlayerObject() return self end
  function p:sendSystemMessage() end
  function p:addBankCredits(v) self.bank=self.bank+v end
  function p:removeWaypointBySpecialType(kind)
    for i=#self.waypoints,1,-1 do
      if self.waypoints[i].kind==kind then table.remove(self.waypoints,i) end
    end
  end
  function p:addWaypoint(planet,name,desc,x,z,y,color,a,b,kind)
    table.insert(self.waypoints,{name=name,kind=kind})
  end
  return p
end
'''
loaded = "\n".join(source(p) for p in [
    "bin/scripts/mobile/hoth/hoth_fill_creatures.lua",
    "bin/scripts/mobile/conversations/sandbox/ossus_people_conv.lua",
    "bin/scripts/screenplays/sandbox/ossus_people.lua",
    "bin/scripts/screenplays/sandbox/hoth_world.lua",
    "bin/scripts/screenplays/sandbox/hutta_life.lua",
])
repros = r'''
for _,name in ipairs({"hoth_wampa_rimefang","hoth_wampa_old_echo"}) do
  local t=creatureTemplates[name]
  local heat=t.resists[4]; local electric=t.resists[6]
  -- CreatureTemplate::getHeat/getElectricity subtract the special-protection marker once.
  local resist=heat>100 and heat-100 or heat
  local damage=1000*(1-resist/100) -- CombatManager::getArmorReduction, after AP
  assert(heat==electric and resist>100 and damage<0)
  print("F1 data/arithmetic: "..name.." encoded="..heat.." resist="..resist.." damage="..damage)
end

local p=player()
p.states.OssusPeople={roadStep="3"}
local t=conversations.ossus_vault_archivist_convo_template
local first=OssusVaultArchivistConvoHandler:getInitialScreen(p,nil,t)
assert(first.id=="road_reward")
function first:getScreenID() return self.id end
OssusVaultArchivistConvoHandler:runScreenHandlers(t,p,nil,0,first)
local after=OssusVaultArchivistConvoHandler:getInitialScreen(p,nil,t)
assert(after.id=="greet_done" and #after.options==0 and after.stopConversation=="true")
assert(readScreenPlayData(p,"OssusPeople","ghostfire")=="")
print("F2 confirmed: road payment -> terminal greet_done; ghostfire lead absent")

local pet={isPlayerCreature=function() return false end}
local h=player(); HothFillJobs:accept(h,"rimefang")
HothFillJobs:creditKill({},pet,"rimefang")
assert(HothFillJobs:getStep(h,"rimefang")==1)
HothFillJobs:creditKill({},h,"rimefang")
assert(HothFillJobs:getStep(h,"rimefang")==2)
local n=player(); HuttaKessothJob:setStep(n,1)
HuttaKessothJob:creditKill({},pet,1)
assert(HuttaKessothJob:getStep(n)==1)
-- No waypoint data from the engine is needed to test the normal-player path.
HuttaKessothJob.setWaypoint=function() end
HuttaKessothJob:creditKill({},n,1)
assert(HuttaKessothJob:getStep(n)==2)
print("F3 confirmed: pet attacker is ignored by both jobs; player attacker advances")

local q=player()
HothFillJobs:accept(q,"echo")
assert(#q.waypoints==1 and q.waypoints[1].name:find("Hask"))
HothFillJobs:accept(q,"rimefang")
assert(#q.waypoints==1 and q.waypoints[1].name:find("Tavi"))
assert(HothFillJobs:getStep(q,"echo")==1 and HothFillJobs:getStep(q,"rimefang")==1)
-- A completed third job removes the active quests' one remaining marker too.
HothFillJobs:setWaypoint(q,nil)
assert(#q.waypoints==0)
print("F5 confirmed: accepting a second job removes the first job's marker; clearing removes the remaining one")
'''
run = subprocess.run(["lua5.3", "-"], input=host + loaded + repros, text=True, capture_output=True)
report["lua_counterexamples"] = {"ok": run.returncode == 0, "stdout": run.stdout.strip(), "stderr": run.stderr.strip(),
    "limit": "Actual pinned Lua functions, substitute engine objects; not an in-game reproduction."}

# The exact eligibility expression retained by cbd85fdf: show the cross-zone old-end branch.
report["group_pay_counterexample"] = {
    "owner": {"zone": "tatooine", "x": 250, "y": 0, "z": 0},
    "end_point": [0, 0, 0],
    "member": {"zone": "naboo", "x": 0, "y": 0, "z": 0},
    "old_end_distance": 0, "near_owner": False,
    "eligible_under_current_or": True,
    "limit": "Source arithmetic counterexample; preserved older branch, not a new game test."}
report["head_after"] = git("rev-parse", "HEAD").strip()
report["tracked_status_after"] = git("status", "--porcelain", "--untracked-files=no").strip()
Path(__file__).with_name("checks.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"commits": len(commits), "lua_at_commit": len(syntax), "lua_at_tip": len(current),
    "syntax_failures": [x for x in syntax + current if not x["ok"]], "counterexamples": report["lua_counterexamples"],
    "head_unchanged": report["head_before"] == report["head_after"], "tracked_status": report["tracked_status_after"]}, indent=2))
if any(not x["ok"] for x in syntax + current) or run.returncode:
    raise SystemExit(1)
