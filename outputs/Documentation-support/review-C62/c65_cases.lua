-- Additional acceptance cases for the pinned repair. The host is deliberately
-- small: these exercise real Lua handlers, not the C++ engine or real relog.
local failures = 0
local function case(name, fn)
  local ok, err = pcall(fn)
  if not ok then failures = failures + 1 end
  print("CASE\t" .. (ok and "PASS" or "FAIL") .. "\t" .. name .. "\t" ..
    (ok and "actual Lua / substitute engine" or tostring(err):gsub("[\n\t]", " ")))
end
local function copy(t)
  if type(t) ~= "table" then return t end
  local out = {}; for k,v in pairs(t) do out[k] = copy(v) end; return out
end
local function relog(p)
  local q = player()
  q.states, q.waypoints = copy(p.states), copy(p.waypoints)
  q.cash, q.bank = p.cash, p.bank
  q.zone, q.x, q.y = p.zone, p.x, p.y
  return q
end
local function screen(s)
  function s:getScreenID() return self.id end
  return s
end
local function nearPlayer(zone, x)
  local p = player(); p.zone, p.x, p.y = zone or "hoth", x or 0, 0
  function p:isInRangeWithObject(v, radius)
    return self.zone == v.zone and (self.x-v.x)^2 + (self.y-v.y)^2 <= radius^2
  end
  return p
end
local function ownedPet(owner, isPet)
  return {isPlayerCreature=function() return false end, isAiAgent=function() return true end,
    isPet=function() return isPet ~= false end, getOwner=function() return owner end}
end
local function group(members)
  for _,p in ipairs(members) do
    function p:isGrouped() return true end
    function p:getGroupSize() return #members end
    function p:getGroupMember(i) return members[i+1] end
  end
end
local function marker(p, id)
  for _,w in ipairs(p.waypoints) do if w.id == id then return w end end
end

case("F1 all loaded heat/electricity damage is nonnegative", function()
  for _,t in pairs(creatureTemplates) do
    for _,i in ipairs({1,2,4,6}) do
      local encoded = t.resists[i]
      local resistance = encoded > 100 and encoded - 100 or encoded
      assert(1000 * (1 - math.min(resistance,100)/100) >= 0)
    end
  end
  assert(creatureTemplates.hoth_wampa.resists[4] == 180)
  assert(creatureTemplates.hoth_elder_wampa.resists[4] == 185)
end)

local archivist = conversations.ossus_vault_archivist_convo_template
local function start(p)
  return screen(OssusVaultArchivistConvoHandler:getInitialScreen(p,nil,archivist))
end
local function choose(p, id)
  return OssusVaultArchivistConvoHandler:runScreenHandlers(archivist,p,nil,0,screen(archivist:getScreen(id)))
end
local function offered(s, id)
  for _,option in ipairs(s.options) do if option[2] == id then return true end end
  return false
end
case("F2 lead before road survives reward and simulated relog", function()
  local p = player(); assert(offered(start(p),"ghostfire_lead")); choose(p,"ghostfire_lead")
  writeScreenPlayData(p,"OssusPeople","roadStep",#OssusPeople.road)
  choose(p,"road_reward"); local paid = p.bank
  local q = relog(p); assert(start(q).id == "greet_done")
  choose(q,"ghostfire_lead"); choose(q,"road_reward")
  assert(readScreenPlayData(q,"OssusPeople","ghostfire") == "lead" and q.bank == paid)
end)
case("F2 road before lead on reward screen", function()
  local p = player(); writeScreenPlayData(p,"OssusPeople","roadStep",#OssusPeople.road)
  local s = start(p); assert(s.id == "road_reward" and offered(s,"ghostfire_lead"))
  choose(p,s.id); choose(p,"ghostfire_lead")
  assert(readScreenPlayData(p,"OssusPeople","ghostfire") == "lead")
end)
case("F2 paid before update and simulated relog", function()
  local p = player(); p.states.OssusPeople = {roadPaid="1",roadStep="3"}
  local q = relog(p); assert(offered(start(q),"ghostfire_lead")); choose(q,"ghostfire_lead")
  local r = relog(q); choose(r,"ghostfire_lead")
  assert(readScreenPlayData(r,"OssusPeople","ghostfire") == "lead" and #r.waypoints == 3)
end)

-- The earlier test overwrote this data table. Restore production step names and
-- supply site coordinates, which are the only fixture data this quest needs.
HuttaKessothJob.waypoints = {{"swamp_rat_camp","camp"},{"freighter_wreck","wreck"},{"spice_den","den"}}
HuttaLifePlaces.sites.swamp_rat_camp = {x=10,z=0,y=10}
HuttaLifePlaces.sites.spice_den = {x=20,z=0,y=20}
for _,job in ipairs({"echo","rimefang",1,3}) do
  local hoth = type(job) == "string"
  local function set(p) if hoth then HothFillJobs:setStep(p,job,1) else HuttaKessothJob:setStep(p,job) end end
  local function step(p) return hoth and HothFillJobs:getStep(p,job) or HuttaKessothJob:getStep(p) end
  local function kill(v,a) if hoth then HothFillJobs:creditKill(v,a,job) else HuttaKessothJob:creditKill(v,a,job) end end
  local before, after = hoth and 1 or job, hoth and 2 or job+1
  local zone = hoth and "hoth" or "hutta"
  case("F3 "..tostring(job).." solo pet, direct player and unowned NPC", function()
    local v = {zone=zone,x=0,y=0}
    local p = nearPlayer(zone,0); set(p)
    kill(v,ownedPet(nil,false)); assert(step(p) == before)
    kill(v,ownedPet(nil)); assert(step(p) == before)
    kill(v,nil); assert(step(p) == before)
    kill(v,ownedPet(ownedPet(nil,false))); assert(step(p) == before)
    kill(v,ownedPet(p,false)); assert(step(p) == before) -- a link alone does not make it a pet
    kill(v,ownedPet(p)); assert(step(p) == after)
    kill(v,ownedPet(p)); assert(step(p) == after) -- only advance once
    local q = nearPlayer(zone,0); set(q); kill(v,q); assert(step(q) == after)
  end)
  case("F3 "..tostring(job).." grouped pet with range, zone and quest eligibility", function()
    local owner,edge,far,other,idle = nearPlayer(zone,0),nearPlayer(zone,128),nearPlayer(zone,129),nearPlayer("naboo",0),nearPlayer(zone,1)
    for _,p in ipairs({owner,edge,far,other}) do set(p) end
    group({owner,edge,far,other,idle})
    kill({zone=zone,x=0,y=0},ownedPet(owner))
    assert(step(owner) == after and step(edge) == after)
    assert(step(far) == before and step(other) == before and step(idle) == 0)
  end)
  case("F3 "..tostring(job).." distant grouped owner does not deny nearby helper", function()
    local owner,helper = nearPlayer(zone,129),nearPlayer(zone,0)
    set(owner); set(helper); group({helper,owner})
    kill({zone=zone,x=0,y=0},ownedPet(owner))
    assert(step(owner)==before and step(helper)==after)
  end)
  case("F3 "..tostring(job).." direct grouped player uses same eligibility", function()
    local owner,helper = nearPlayer(zone,0),nearPlayer(zone,1)
    set(owner); set(helper); group({helper,owner})
    kill({zone=zone,x=0,y=0},owner)
    assert(step(owner)==after and step(helper)==after)
  end)
end

case("F5 simultaneous jobs, stock marker, travel, rewards and simulated relog", function()
  local p = player()
  local stock = p:addWaypoint("tatooine","stock quest task","",0,0,0,1,true,true,WAYPOINTQUESTTASK)
  for _,job in ipairs({"echo","rimefang","pryce"}) do HothFillJobs:accept(p,job) end
  HuttaKessothJob:accept(p)
  local q = relog(p); q.zone = "hutta"; assert(#q.waypoints == 5 and marker(q,stock))
  for _,job in ipairs({"echo","rimefang"}) do HothFillJobs:creditKill({},q,job) end
  for _,job in ipairs({"echo","rimefang","pryce"}) do assert(HothFillJobs:reward(q,job)) end
  assert(q.cash == 15500 and #q.waypoints == 2 and marker(q,stock))
  HuttaKessothJob:advance(q,1); HuttaKessothJob:advance(q,2); HuttaKessothJob:advance(q,3)
  local r = relog(q); assert(HuttaKessothJob:reward(r))
  assert(r.cash == 21500 and #r.waypoints == 1 and marker(r,stock))
  assert(readScreenPlayData(r,"HuttaKessothJob","waypoint") == "0")
end)
case("F5 existing quest-task marker is retained by deliberate migration policy", function()
  local p = player(); HothFillJobs:setStep(p,"echo",1)
  local legacy = p:addWaypoint("hoth","legacy Echo Base","",0,0,0,1,true,true,WAYPOINTQUESTTASK)
  HothFillJobs:retrack(p,"echo"); assert(#p.waypoints == 2 and marker(p,legacy))
end)
case("F5 all active stages recover exactly one owned marker after simulated relog", function()
  local t = {getScreen=function(_,id) return {id=id} end}
  for _,job in ipairs({"echo","rimefang","pryce"}) do
    local p=player(); HothFillJobs:accept(p,job)
    p.waypoints={}; local q=relog(p)
    HothFillJobs:retrack(q,job); HothFillJobs:retrack(q,job)
    assert(#q.waypoints==1)
  end
  for stage=1,3 do
    local p=player(); HuttaKessothJob:setStep(p,stage)
    local q=relog(p)
    HuttaKessothMajordomoConvoHandler:getInitialScreen(q,nil,t)
    HuttaKessothMajordomoConvoHandler:getInitialScreen(q,nil,t)
    assert(#q.waypoints==1)
  end
end)
for _,job in ipairs({"echo","rimefang"}) do
  case("F5 restore deleted report-back marker for "..job, function()
    local p = player(); HothFillJobs:accept(p,job); HothFillJobs:creditKill({},p,job)
    local id = tonumber(readScreenPlayData(p,"HothFillJobs",job.."Waypoint"))
    p:removeWaypoint(id,true); local q = relog(p)
    HothFillJobs:retrack(q,job)
    assert(#q.waypoints == 1,"step 2 report-back marker was not restored")
  end)
end
case("F5 restore deleted report-back marker for Kessoth", function()
  local p = player(); HuttaKessothJob:accept(p)
  for i=1,3 do HuttaKessothJob:advance(p,i) end
  p:removeWaypoint(tonumber(readScreenPlayData(p,"HuttaKessothJob","waypoint")),true)
  local q = relog(p)
  local t = {getScreen=function(_,id) return {id=id} end}
  HuttaKessothMajordomoConvoHandler:getInitialScreen(q,nil,t)
  assert(#q.waypoints == 1,"step 4 report-back marker was not restored")
end)
print("Extended Lua acceptance failures: "..failures)
