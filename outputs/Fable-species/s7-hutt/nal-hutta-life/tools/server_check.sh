#!/bin/bash
# PL-06: check that every name the patch uses exists in Core3-dev (or in the patch). Read-only. Writes server-check.txt.
L=/mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Fable-species/s7-hutt/nal-hutta-life
B=/opt/swg/Core3-dev/MMOCoreORB/bin/scripts
SRC=/opt/swg/Core3-dev/MMOCoreORB/src
N=$L/server/MMOCoreORB/bin/scripts
ok=0; bad=0
pass() { ok=$((ok+1)); echo "ok   $1"; }
fail() { bad=$((bad+1)); echo "FAIL $1"; }
{
echo "Core3-dev $(git -c safe.directory='*' -C /opt/swg/Core3-dev rev-parse --short HEAD), $(date '+%-d %b %Y %-I:%M %p')"
for m in commoner_tatooine_patrol commoner_old_patrol commoner_fat_patrol commoner_technician_patrol explorer_patrol gambler_patrol \
  commoner_tatooine commoner_old commoner_fat commoner_technician patron_nikto twilek_slave businessman criminal gambler info_broker \
  mercenary pilot scavenger bounty_hunter noble smuggler_cargo_handler gamorrean_guard smuggler weequay_captain smuggler_guard \
  spice_collective_sentry spice_collective_foreman aakuan_spice_guard spice_collective_heavy_guard spice_fiend \
  hutt_expeditonary_force_member hutt_expeditonary_force_leader igbi_hutt_operative nurla_hutt_gangster; do
  grep -rq "addCreatureTemplate([a-z_0-9]*, \"$m\")" $B/mobile && pass "mobile $m" || fail "mobile $m"
done
for m in hutta_rodian_trader hutta_old_weequay hutta_twilek_attendant hutta_swamp_beggar hutta_nikto_dockhand hutta_hutt_noble_kessoth \
  hutta_hutt_noble_dromuul hutta_kessoth_majordomo hutta_weequay_watch hutta_cantina_dancer hutta_camp_boss hutta_spice_baron; do
  grep -q "\"$m\"" $N/mobile/sandbox/hutta_life.lua && pass "new mobile $m" || fail "new mobile $m"
  grep -rq "addCreatureTemplate([a-z_0-9]*, \"$m\")" $B/mobile && fail "name clash $m" || pass "no clash $m"
done
for l in $(grep -o 'lairTemplateName = "[a-z_0-9]*"' $L/core3-dev-nal-hutta-life.patch | cut -d'"' -f2 | sort -u); do
  grep -rq "addLairTemplate(\"$l\"" $B/mobile/lair && pass "lair $l" || fail "lair $l"
done
for o in $(grep -oh 'object/[a-z_0-9/]*\.iff' $N/screenplays/sandbox/hutta_life.lua $N/screenplays/sandbox/hutta_life_places.lua $N/mobile/sandbox/hutta_life.lua | sort -u); do
  f=$B/${o%.iff}.lua; test -f $f && pass "template $o" || fail "template $o"
done
for g in thug_tier_1 weequay_tier_1 aakuans_tier_1; do grep -rq "addLootGroupTemplate(\"$g\"" $B/loot && pass "loot $g" || fail "loot $g"; done
grep -rq 'socialGroup = "thug"' $B/mobile && pass "socialGroup thug" || fail "socialGroup thug"
grep -rq 'faction = "thug"' $B/mobile && pass "faction thug" || fail "faction thug"
grep -rq '"rebel_weapons_heavy"' $B/mobile && pass "weapon group rebel_weapons_heavy" || fail "weapon group"
grep -rq 'themepark_oola' $B/screenplays && pass "mood themepark_oola (stock use)" || fail "mood themepark_oola"
for c in hutta_rodian_trader hutta_old_weequay hutta_twilek_attendant hutta_swamp_beggar hutta_nikto_dockhand hutta_hutt_noble hutta_kessoth_majordomo; do
  grep -q "\"${c}_convo_template\"" $N/mobile/conversations/sandbox/hutta_life_conv.lua && pass "conversation ${c}" || fail "conversation ${c}"
done
for f in getWorldFloor spawnActiveArea readScreenPlayData writeScreenPlayData getSceneObject; do
  grep -rq "\"$f\"" $SRC/server/zone/managers/director/DirectorManager.cpp && pass "lua global $f" || fail "lua global $f"
done
for f in isInRangeWithObject isPlayerCreature getGroupSize getGroupMember isGrouped addCashCredits setCustomObjectName getSlottedObject isContainerFullRecursive; do
  grep -rq "{ *\"$f\"" $SRC/server/zone/objects/creature/LuaCreatureObject.cpp $SRC/server/zone/objects/scene/LuaSceneObject.cpp && pass "method $f" || fail "method $f"
done
grep -q "removeWaypointBySpecialType" $SRC/server/zone/objects/player/LuaPlayerObject.cpp && pass "removeWaypointBySpecialType" || fail "removeWaypointBySpecialType"
grep -q "getCell" $SRC/server/zone/objects/building/LuaBuildingObject.cpp && pass "BuildingObject getCell" || fail "getCell"
grep -rq "WAYPOINTQUESTTASK" $B/../scripts/screenplays/quest_tasks && pass "WAYPOINTQUESTTASK constant (stock use)" || fail "WAYPOINTQUESTTASK"
echo "$ok passed, $bad failed"
} > $L/server-check.txt 2>&1
tail -1 $L/server-check.txt; grep FAIL $L/server-check.txt
