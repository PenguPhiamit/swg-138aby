Written by Claude Haiku and Claude Opus, 15 Oct 2026, from Core3-dev 90044b8e.

# Quests on Core3-dev: how they work, and how a bot can test them

Paths are relative to MMOCoreORB/. Short names: DM = src/server/zone/managers/director/DirectorManager.cpp; LCO = src/server/zone/objects/creature/LuaCreatureObject.cpp; TPL = bin/scripts/screenplays/themepark/themeParkLogic.lua; TUT = bin/scripts/screenplays/tutorial/tutorial.lua; TB = bin/scripts/screenplays/custom_screenplays/the_tutorial/the_tutorial_0001_the_beginning.lua; HC = bin/scripts/mobile/custom_content/conversations/the_tutorial/tutorial_0001_han_solo_conv.lua.

## 1. Short answer
Quests are Lua screenplays run by the C++ DirectorManager. There is no src/server/zone/managers/quest folder. An NPC conversation handler gives the quest by setting a per-player "screenplay state" bit. Observers (entering an area, a kill, a room change) record progress, and a second conversation pays the reward and sets the next bit. Theme parks share one engine (TPL), which adds a purple waypoint, spawns a 100 m quest area and pays credits, faction, loot, badges or items. "The Beginning" with Han Solo and Chewbacca is a custom Tatooine screenplay: one task ("Checking the Falcon"), 10,000 cash credits and no waypoint. The old newbie tutorial (TutorialScreenPlay) is separate, a per-player building driven by room changes.

## 2. How it works
Loading and running
- DM loads scripts/screenplays/screenplays.lua (DM:927). registerScreenPlay(name, start) records a name and an auto-start flag (DM:1326-1331). At boot each flagged screenplay's start runs (DM:365-378, 3520-3526). A reload only bumps a version number that each Lua thread checks (DM:946-948, 3504-3508).
- createEvent schedules a later call to screenplay:function(object, args) (DM:3566-3594). createObserver (DM:3274) hooks events such as ENTEREDAREA, PARENTCHANGED, OBJECTDESTRUCTION and STOPCONVERSATION (TUT:44, 59, 343, 382).
- Lua errors go to log/lua.log (DM:421).

Conversations
- An NPC is talkable when its template sets CONVERSABLE and a conversationTemplate (bin/scripts/mobile/custom_content/the_tutorial/tutorial_0001_han_solo.lua:27, 33). The template names a Lua handler class (HC:1-6). Each screen has an id, text and options of the form {text, next screen id} (HC:8-16).
- On each choice the server calls the handler's getNextConversationScreen and runScreenHandlers (DM:3529-3564). The quest logic lives in those Lua functions (TB:86-135).

State storage
- Per-player screenplay state is a bitmask per name. setScreenPlayState ORs bits in and fires SCREENPLAYSTATECHANGED, removeScreenPlayState clears bits, and hasScreenPlayState tests them (LCO:545-551, 554-561, 461-469). It is stored on the creature, so it probably persists with the character (inferred).
- Per-player strings: writeScreenPlayData stores them on the PlayerObject ("ghost") (DM:950-978).
- Server-wide quest status: setQuestStatus and getQuestStatus. These are saved in the "questdata" database and reloaded at start (DM:186-233, 4158-4192).
- readData and writeData hold short-lived values keyed by object ID (used at TUT:29, 61). Their binding is not among the registrations I read (DM:432-525).
- Quest journal: Lua can call getPlayerQuestID, getQuestInfo and getQuestTasks, which PlayerManager backs (DM:4360-4406, 4932-4961). Lua task helpers are in quest_tasks/ (bin/scripts/screenplays/screenplays.lua:78-84). I did not trace who uses them.

Theme parks (TPL)
- Current mission = number of set bits in "<screenPlayState>_mission_<npc template>", plus 1 (TPL:455-464).
- Accepting a mission (TPL:491-554):
  - stores the active screenplay
  - spawns a quest area near the player (100 m, or 350 m for destroy missions)
  - adds a waypoint and an ENTEREDAREA observer
  - gives the items for deliver missions
  - sets activeMission=1
  The waypoint is purple, of type WAYPOINTTHEMEPARK, with the mission description as its text (TPL:1605).
- Complete: shows a system message (missionCompletionMessageStf, or @theme_park/messages:static_completion_message), adds a "return" waypoint to the giver and sets activeMission=2 (TPL:1801-1834).
- Fail: shows @theme_park/messages:generic_fail_message and sets activeMission=-1 (TPL:1847, 1876).
- Reward types are credits, faction, loot, loot_set, badge, permission and item (TPL:1892-1910). Credits show @theme_park/messages:theme_park_credits_pp (TPL:1970). Faction goes through increaseFactionStanding (TPL:1980). Items show theme_park_reward (TPL:1999).
- Moving to the next mission sets bit 2^(n-1). After the giver's last mission, the giver's number is set in the main state (TPL:2116-2124).

Newbie tutorial (TUT)
- Registered without auto-start (TUT:18). Start runs when the player zones into a tutorial building with CRC 3369536646 (TUT:20, 40).
- Each room change (PARENTCHANGED) marks a room done and sends @newbie_tutorial/system_messages:part_2 to part_9 (TUT:522-579).
- Room 1 advances on timers and on chat and holocron events (TUT:619-666).

## 3. What a bot test should check: "The Beginning"
The script loads from bin/scripts/screenplays/custom_screenplays/screenplays.lua:4 (included at screenplays.lua:742) and starts automatically (TB:14). A second copy ("...the_beginning-Clean and formatted.lua") sits in the same folder but is not included.

Setup
- Tatooine is enabled (TB:20).
- The character has no "tutorial_one" state.
- The bot stands near Han at Tatooine x 3565, y -4795 (TB:48). Chewbacca (npe_chewbacca) is at 3568, -4795 (TB:51).
- The Falcon static is at 3863, -4856 with a 40 m active area (TB:32, 41), roughly 300 m east (inferred from the numbers).

Steps and what to observe
1. Converse with Han. The first screen is "first_screen", with options "Why" and "What if I don't want to?" (HC:8-16). The second option ends the conversation (HC:20-24).
2. Choose in order: "Why", "It's what i need to do, count me in!", "What's the deal", "Go on", "I'm on my way" (HC:14, 33, 44, 54, 64). The screen "accept_task_one" closes the conversation (HC:69-73).
   - Observe: tutorial_one bit 1 is set, sound ui_npe2_quest_received.snd plays, and the system message "Quest received: Checking the Falcon." arrives with colour codes (TB:129-131).
   - No waypoint is given, so the bot must walk to the coordinates.
3. Optional: talking to Han again now shows task_one_active, "Have you checked the Falcon yet?" (TB:93-95, HC:77-82).
4. Walk within 40 m of 3863, -4856.
   - Observe: the system message "<Communicator> Ok Kid, looks like she's all in one piece..." and sound ui_quest_waypoint_patrol.snd; bit 1 is cleared and bit 2 is set (TB:65-75).
   - The server prints "notifyEnteredAreaOne function started" on every entry, from any object (TB:59).
5. Return to Han and converse.
   - Observe: +10,000 cash credits (cash, not bank), sound ui_npe2_quest_credits.snd, the message "Quest completed: Checking the Falcon.", state becomes 4, and the screen is task_one_complete (TB:100-107).
6. Converse again: the screen is quest_complete, "Did you ever meet Lando in Theed?" (TB:110-111). The file has no later step.

What to assert
- Cash rises by exactly 10000.
- The tutorial_one state goes 1, then 2, then 4.
- The three system messages arrive in order.

## 4. Likely reasons a test sees no effect
- Tatooine is disabled, so nothing spawns (TB:20). Spawning happens only in start, so script edits probably need a server restart, not just a reload (inferred from DM:946-948).
- The character still holds a state from an earlier run. Han then opens at task_one_active or quest_complete, and never pays again (TB:93-111).
- The bot enters the Falcon area without bit 1 set: nothing happens (TB:65).
- A wrong option leads to exit_one, which ends the conversation with no state change (HC:15, 34).
- Message text contains colour codes (TB:68, 102, 131). Strip them before matching.
- The test checks the bank instead of cash (TB:100).
- Theme parks: getSpawnPoint can fail, and the accept then returns false with no waypoint (TPL:519-528). There are also inventory-full and faction checks (TPL:224, 283).
- The newbie tutorial only runs inside its building, and only once per player (TUT:29, 40).
- Lua errors appear only in log/lua.log (DM:421).

## 5. Open questions
- Where readData and writeData are bound, and whether their values survive a restart.
- Whether screenplay states are saved with the character (inferred yes), and how a test resets "tutorial_one" between runs. I found no reset path.
- The journal quest system was not read: PlayerManager quest info and tasks, src/server/zone/objects/player/variables/PlayerQuestData.h, and the ActivateQuest/CompleteQuest commands. I also got an inconsistent read of ActivateQuestCommand.h.
- What starts the newbie tutorial (the comment names StartTutorialTask, TUT:20). The later rooms (TUT after line 1206) were not read.
- Whether npe_chewbacca can be talked to. I did not read its template.
- How a bot client receives conversation options and system messages at the packet level.


## ChatGPT's review (2026-10-18 02:27)

Checked the report against Core3-dev `aa52cc647a2129096011eb122fe98c7794db4c2b` (read only, paths relative to MMOCoreORB/) (this topic has no `src/` snapshot); no in-game checks. The original draft remains above; corrections below take precedence.

**Holds:** Lua screenplay registration, bitwise state updates, theme-park area/waypoint/reward mechanisms and the specific Beginning quest's 1->2->4 progression/+10000 cash hold (LuaCreatureObject.cpp:461-469,545-560; themeParkLogic.lua:491-554,1892-1910; the_tutorial_0001_the_beginning.lua:14-41,48-75,93-131). custom_screenplays/screenplays.lua:4 includes the named script. The reward is paid on getInitialScreen when state 2 is present, not on a later reward-option click (97-107).

**Corrections/qualifications:**
- The introductory 'quests are Lua screenplays' is only one subsystem; this report itself names the separate quest-journal APIs and does not establish a census of all quest implementations. Absence of a managers/quest directory proves no missing feature.
- Theme-park current mission is the length of the contiguous completed prefix, not general popcount: stateToCheck advances only when the current bit is found (themeParkLogic.lua:455-464). Sparse later bits do not advance it. Hunt missions take a separate acceptance path before the general area/waypoint path (493-495).
- 'Lua errors appear only in log/lua.log' is stronger than the cited registration of a file logger (DirectorManager.cpp:421). That line establishes an output destination, not exclusive routing.
- Registering auto-start does not prove successful runtime spawn; enabled zone, loaded templates, non-null spawns and current state still matter. The receiver callback filters player creatures before changing state (the_tutorial_0001_the_beginning.lua:61-75).
- The 10000 cash delta is exact for the isolated reward operation, not for a test with concurrent income/spending. The quest text is legacy content evidence, not approval of its era suitability.

**Not established:** state persistence across restart, reset route, journal implementation, event bindings not read, and runtime conversation packets. No restart or quest interaction occurred.

**Verdict:** Beginning quest flow supported; scope is not all quests, fix contiguous-bit counting and exclusive-log claim; persistence/runtime remain open.
