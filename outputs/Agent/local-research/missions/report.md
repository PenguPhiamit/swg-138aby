Written by Claude Haiku, 15 Oct 2026, from Core3-dev 90044b8e.

# Missions (pre-CU, Core3)

## 1. Short answer
A terminal's `missionTerminalType` decides its list. General terminals give 6 destroy and 6 deliver missions. Artisan terminals give 6 survey and 6 crafting, entertainer terminals 6 dancer and 6 musician, scout terminals 6 recon and 6 hunting, and bounty terminals 10 bounty missions. Imperial and rebel terminals give destroy and deliver plus factional extras. A player may hold 2 missions in the datapad, and at most 1 of them may be a bounty. A destroy target is placed 1000-2000 m from where the list was requested and pays 375xL + rand(15xL) credits into the bank. Its lair spawns only when the owner comes within 128 m of the waypoint, and destroying the lair completes the mission. cresh-missions.py only accepts destroy missions within 600 m, so it should nearly always stop at BLOCKED (inferred from the numbers).

## 2. How it works
Paths are relative to MMOCoreORB/: MMI = src/server/zone/managers/mission/MissionManagerImplementation.cpp, OBJ = src/server/zone/objects/mission, DMO = OBJ/DestroyMissionObjectiveImplementation.cpp, MOI = OBJ/MissionObjectiveImplementation.cpp, lua = bin/scripts/managers/mission/mission_manager.lua.

**List request.** The server refuses it:
- at statue and newbie terminals (MMI:165-167);
- beyond 6 m (MMI:170-175);
- at bounty terminals without combat_bountyhunter_novice (MMI:178-182);
- when the player is city-banned (MMI:187-191);
- within 1400 ms of the last list, with "You can't request missions yet..." (MMI:194-200).

The mission bag is filled to 12 slots, plus 6, 6 and 12 when factional crafting, recon and entertainer missions are on (MMI:207-220). All three are on (lua:67-71). Slicers get x1.5 once, and the skill mod private_spec_missions adds a percentage (MMI:610-612, 634-639).

**Which terminal gives which types.** The type comes from the template field missionTerminalType (src/templates/tangible/MissionTerminalTemplate.h:26). terminal_mission.iff is "general" (bin/scripts/object/tangible/terminal/terminal_mission.lua:48). The dispatch is MMI:594-608. Slot rules by terminal:
- general: MMI:628-632
- artisan: MMI:657-661
- entertainer: MMI:686-690
- scout: MMI:715-719
- bounty: MMI:746-748
- imperial and rebel: MMI:774-792

Unused slots keep type 0 (MMI:626).

**Accept.** If the datapad already holds 2 missions, or the player tries to take a second bounty, the server refuses with mission/mission_generic:too_many_missions (MMI:256-273). Otherwise the mission moves to the datapad and its objective starts (MMI:291-293). It expires after 48 h (MISSIONDURATION 172800000 ms, OBJ/MissionObjective.idl:38; MOI:46-70), and the player then sees "Mission expired" (OBJ/events/FailMissionAfterCertainTimeTask.cpp:23-25). Abort is refused while the player is incapacitated or in combat (MMI:531-539).

**Destroy.**
- The lair comes from the spawn group "<planet>_destroy_missions". Its min difficulty must be at most level+5 and its max at least min(level-5, ceiling). The group level is used when the player is grouped (MMI:1833, 1880-1899).
- The difficulty level L is random between the lair's min and max (MMI:828).
- Distance is 1000 + rand(1000) at a random bearing from the player (lua:83-86, MMI:872-874). The spot must be inside the map, out of water and outside city regions. After 20 failed tries the slot stays empty (MMI:868-907).
- Reward is 375xL + rand(15xL) (lua:91-94, MMI:921-923).
- On accept, a 128 m area and the waypoint are placed at that spot (DMO:51-83).
- Only the owner entering that area spawns the lair (src/server/zone/objects/area/MissionSpawnActiveArea.idl:36-40). The lair lands up to about 256 m from the centre (DMO:96-124).
- The waypoint and start position then move to the lair, and the player sees "Transmission Received: Mission Target has been located.  Mission waypoint has been updated to exact location" (DMO:163-184).
- The lair is named @lair_n:<name>, is attackable, and has max condition Lx(900+rand(200)) (DMO:215-219).
- Creature lairs spawn waves when placed, at first damage and at half condition. NPC lairs spawn only when placed (src/server/zone/managers/mission/DestroyMissionLairObserverImplementation.cpp:84-121).
- Destroying the lair completes the mission. The code does not check who destroyed it (DMO:227, 300-306).
- If no spawn point is found, the mission fails with @mission/mission_generic:failed (DMO:126-130).

**Reward (all types).** On completion the server pays the reward, gives faction points and removes the mission from the datapad (OBJ/events/CompleteMissionObjectiveTask.h:27-31). In detail (MOI:192, 273-320, 348-364):
- music_mission_complete.snd plays.
- Group members within 128 m of the mission's end point share the credits. Anyone farther away triggers group_too_far. The owner is always paid.
- The player sees success_w_amount with the amount, and the credits go to the bank.

**Deliver.**
- The start NPC is 10-300 m from the player. The end NPC is in the same city or another one (MMI:1248-1257, 1310-1335).
- Reward is 40 + route length/10 (MMI:1358-1361).
- If the NPCs cannot spawn, the player sees mission_incomplete_0N and the mission is removed (OBJ/DeliverMissionObjectiveImplementation.cpp:27-40).
- Talking to the target NPC puts a datadisk in the inventory and moves the waypoint. Talking to the destination NPC while carrying it completes the mission (OBJ/DeliverMissionObjectiveImplementation.cpp:182-223; src/server/zone/objects/creature/conversation/screenhandlers/DeliverMissionScreenHandler.cpp:139-163).

**Survey.**
- The level runs from 50 to 95 in steps of 5 and rises with the surveying skill (MMI:974-1003). 75% of survey missions are mineral (MMI:1011-1016).
- Reward is 400 + (level-50)x20 + rand(100) (MMI:1035).
- The start position is where the player stood when the list was made (MMI:1040).
- It completes on a sample of the named family with density at least the level, taken more than 1024 m from the start. Closer samples give survey_too_close (OBJ/SurveyMissionObjectiveImplementation.cpp:66-81).

**Entertainer.**
- The target is a random performance location (MMI:1466-1475). Reward is 100 + distance/10 + rand(100) (MMI:1504-1506).
- It completes after 10 minutes of performing inside the 32 m area while inside a building. Leaving the area or stopping cancels the timer (OBJ/EntertainerMissionObjectiveImplementation.cpp:46-47, 139-153, 171-177).
- Starting and stopping a dance or song updates it (src/server/zone/objects/player/sessions/EntertainingSessionImplementation.cpp:320, 419, 529, 589).

**Crafting.**
- It is generated as a deliver mission and then retyped (MMI:1418-1452).
- The item is picked at accept from 5 quest items, avoiding one already held (MMI:351-361, lua:3-9).
- The target NPC gives the schematic and its components. Bringing the crafted item to the destination NPC completes the mission. Abort removes the schematic (OBJ/CraftingMissionObjectiveImplementation.cpp:36-76, 83-101).

## 3. What a bot test should check (destroy)
**Setup:**
- The owner bot stands within 6 m of a terminal_mission.iff (general) terminal.
- The datapad holds fewer than 2 missions. Abort leftovers out of combat.
- Request the list once, then wait at least 1.4 s.
- Accept a distance bound of at least 2000 m from where the list was requested (about 2300 m with the lair offset).
- Record bank credits first.

**Checks:**
- (a) The list has 6 destroy and 6 deliver missions; destroy slots can be empty.
- (b) Each destroy reward is between 375xL and 390xL, times the city bonus.
- (c) The accepted mission is in the datapad, and a 3rd accept gets too_many_missions.
- (d) When the owner comes within 128 m of the waypoint, "Transmission Received..." arrives and the waypoint moves.
- (e) A TANO named @lair_n:... exists near the new waypoint.
- (f) After the lair is destroyed, the mission is gone from the datapad, success_w_amount arrives, and the bank rises by the reward (solo). Grouped helpers must be within 128 m of the original spot to share it (the end point is not moved, MMI:914 vs DMO:175; inferred).

**Against cresh-missions.py:**
- The 600 m filter (lines 44, 59) excludes every destroy mission.
- The terminal filter (line 19) lets artisan and statue terminals through, and those offer no destroy missions.
- The lair search (lines 64, 68) uses the waypoint read before the lair spawned, with an 80 m radius. Re-read the waypoint after the "Transmission Received" message.
- Only Cresh, the owner, can trigger the spawn.
- The completion check (line 74) depends on how the bot renders string ids.
- The reward goes to the bank, so line 79 should compare bank credits.

## 4. Likely reasons a test sees no effect
- The distance bound is under 1000 m.
- The terminal is the wrong type (artisan, statue or newbie).
- The bot is over 6 m from the terminal, hit the list cooldown, or is city-banned.
- 2 missions are already held, for example ones kept by the BLOCKED path at line 60.
- A non-owner reached the spot first, so no lair spawned.
- The lair was searched for at the generated spot instead of the updated waypoint.
- Lair condition (about Lx1000) is too high for 150 s fights (line 72; inferred).
- Destroy slots are empty because of water, cities or the map edge, or the planet has no destroy group (MMI:905-907, 1852-1856).
- Cash was checked instead of the bank, or a grouped bot was too far from the end point.

## 5. Open questions
- What the bot's `missions` request reports as waypoint and start, and whether that updates after the spawn. This is bot-side code, not Core3 (squad.py:456-468 only forwards requests).
- How string-id messages such as success_w_amount and too_many_missions appear in the bot's text.
- Where the SURVEY event is raised. MissionObjectImplementation.cpp (updateMissionLocation, type strings) was not read.
- Whether slots 13-36 on a general terminal reach the client as empty missions.
- Whether System::random bounds are inclusive, and the exact getWorldCoordinate distance.
- Lair spawn limits per template. Hunting, recon and bounty completion were not covered.
- Whether the scenario's bots are grouped.
- Commit 90044b8e was taken from the brief; I did not check it.
