# Report: How an Entertainer Earns Experience (Core3, pre-CU)

## 1. Short Answer

In Core3, entertainers earn three types of experience per 10-second tick: dance or music XP from performing and flourishes, entertainer-healing XP from healing audience wounds, and buff-strength XP from increasing patron buffs. Dance XP is awarded when `isDancing()` is true; music XP when `isPlayingMusic()` is true (EntertainingSessionImplementation.cpp lines 1030-1033). Flourishes multiply healing amounts by `(flourishCount + 1)` per tick (line 85) but only the first flourish per tick counts toward dance/music XP for dancing (cap = 10/10s loop = 1, line 681); music has a cap of 2 flourishes per 5s loop. Audience size up to 50 listeners/watchers provides a linear multiplier `audienceSize / 50` (line 1062). A dancing-only bot cannot earn "music" XP type or any skill boxes that require music performance, since the code branches on `isPlayingMusic()` for all music-specific skill mods (lines 63-64, 67, 718).

## 2. How It Works

### Conditions and Skill Mods
- The entertainer must have an active entertaining session (`performanceIndex > 0`) and be either dancing or playing music (lines 59-68, 1173-1197).
- Healing skill mods differ by performance type: `healing_dance_wound` / `healing_dance_shock` for dancers (lines 60-61), `healing_music_wound` / `healing_music_shock` for musicians (lines 63-64).
- Building faction perk adds to healing if the entertainer is registered in a recreation/hotel/theater building matching their overt faction (lines 56-80).
- Buff strength cap is `healing_dance_mind` for dancers (line 716) or `healing_music_mind` for musicians (line 718), max 125% (line 722).

### Timings
- The tick task runs every 10,000 ms (10 seconds) via `tickTask->schedule(10000)` (line 236).
- Each tick calls `activateAction()` which invokes `doEntertainerPatronEffects()`, `awardEntertainerExperience()`, and `doPerformanceAction()` in sequence (lines 220-222).
- Flourish cooldown = `5s - knowledgeSkillMod / 30` (FlourishCommand.h lines 74-77), minimum 2s at master.
- Buff duration increases by `2.0 * buffAcceleration` per tick (line 997); max buff duration is 120s + 10/60s (lines 699-700).
- Patrons must listen/watch for at least 60 seconds before receiving buffs (lines 877-881).

### Audience Effect
- `getBandAudienceSize()` sums the entertainer's audience plus any band members' audiences, capped at 50 total (lines 1108-1141, line 1061).
- Audience multiplier: `audienceMod = audienceSize / 50.f` (line 1062).
- Applause multiplier: `applauseMod = applauseCount / 100.f` (line 1063).
- Group bonus: each entertainer in the same group within 40m who has `social_entertainer_novice` adds +5% (lines 1039-1057, line 1065).
- Total XP multiplier: `totalBonus = 1.f + groupMod + audienceMod + applauseMod` (line 1067).

### Flourishes
- Flourish number must be 1-8 and the entertainer must have the ability `"flourish+<N>"` (FlourishCommand.h lines 37, 49).
- Flourish action drain = half the base loop action drain (line 654).
- Only flourishes within the per-tick cap add to `flourishXp`: dance cap = 1 (loop 10s), music cap = 2 (loop 5s) (lines 681-684).
- Flourish XP added: `performance->getFlourishXpMod()` per counted flourish (line 684).

### Healing Battle Fatigue and Mind Wounds
- `doEntertainerPatronEffects()` heals the entertainer first, then each patron within `HEAL_RANGE` (lines 82-103).
- Mind wounds healed: MIND, FOCUS, WILLPOWER attributes (lines 162-170).
- Shock wounds (battle fatigue) healed if `private_med_battle_fatigue > 0` (lines 158-161).
- Healing amount = `performance->getHealMindWound() * (skillMod / 100.0f) * (flourishCount + 1)` (line 82, 85).
- Healing XP awarded to entertainer via `addHealingXp(amountHealed)` or to group members via `addHealingXpGroup()` if in a group (lines 174-199).

### Buff Strength XP
- When buff strength increases, `healingXp += strength` is added (line 739), capped at max buff strength (line 741).

### Messages the Player Sees
- "@performance:dance_start_self" — "You begin dancing." (line 417)
- "@performance:dance_stop_self" — "You stop dancing." (line 562)
- "@performance:flourish_perform" — "You perform a flourish." (line 690)
- "@performance:flourish_not_performing" when not in a performance session (lines 29, 636)
- "@performance:flourish_too_tired" when ACTION HAM is insufficient (line 659)
- "You must listen or watch a performer for at least 1 minute in order to gain the entertainer buffs." (line 879)

## 3. What a Bot Test Should Check

### Setup
1. Start an entertaining session with a dance performance (`startDancing(perfIndex)`).
2. Ensure the bot has `social_entertainer_novice` skill and relevant healing skill mods.
3. Have audience members (or test bots) within range who are watching/listening for at least 60 seconds.

### Observable Results
- **System messages**: "You begin dancing." on start, "You perform a flourish." on each flourish command.
- **Attributes**: ACTION HAM decreases per tick and per flourish; MIND/FOCUS/WILLPOWER wounds decrease on audience members with those wounds.
- **Buffs**: Audience members should gain `performance_enhance_dance_mind` buff after 60s of watching (lines 914-922).
- **Experience**: Check that "dance" XP is awarded per tick (not "music" or "entertainer_healing" for pure dance performance without healing). Verify audience multiplier by comparing XP with 0 vs 50 watchers.
- **Flourish cap**: After the first flourish in a tick, additional flourishes should not increase `flourishXp` (dance cap = 1).

### Verification Steps
1. Perform with 0 audience → verify base XP only.
2. Perform with 50 audience → verify XP is approximately double (audienceMod = 1.0).
3. Flourish multiple times in one tick → verify only first flourish adds to `flourishXp`.
4. Heal an audience member's battle fatigue → verify "entertainer_healing" XP awarded.
5. Check buff strength on patron after 60s → verify `performance_enhance_dance_mind` buff exists with correct strength.

## 4. Likely Reasons a Test Sees No Effect

- **No audience**: Without watchers/listeners, `audienceMod = 0` and no patrons receive buffs or healing XP (lines 87-88, 106).
- **Insufficient watch time**: Patrons must listen/watch for at least 60 seconds before buffs activate (lines 877-881).
- **Flourish cooldown**: Flourishes have a cooldown of `5s - knowledgeSkillMod/30`; attempting too many will fail with "@performance:flourish_too_tired" or simply not trigger due to cooldown.
- **Wrong performance type**: If the bot is playing music instead of dancing, dance-specific skill mods (`healing_dance_wound`, etc.) are not used (lines 59-68).
- **Not in a building for faction perk**: Building faction healing bonus only applies if registered in a recreation/hotel/theater building matching overt faction (lines 70-80).
- **Group members not entertaining**: Group XP bonus requires other group members to be entertaining and have `social_entertainer_novice` (lines 194-195, 1047-1049).

## 5. Open Questions

- **Performance table values**: The code references `performance->getBaseXp()`, `performance->getFlourishXpMod()`, `performance->getHealMindWound()`, `performance->getHealShockWound()`, and `performance->getLoopDuration()` but the Performance class definition is not in the provided files (missing file: likely `Performance.h` or `Performance.cpp`).
- **HEAL_RANGE constant**: The value of `PerformanceManager::HEAL_RANGE` is not defined in the provided files (missing file: `PerformanceManager.h`).
- **Entertainer tree structure**: The full list of entertainer skill boxes and their XP requirements is not available; only skill mod names are visible (e.g., `healing_dance_mind`, `healing_music_mind`). Missing file: likely a skill template or XML defining the entertainer tree.
- **Applause mechanics**: How `applauseCount` is incremented is not shown in these files (missing function/file).
- **Buff strength cap calculation**: The exact formula for `maxBuffStrength` beyond the 125% cap and faction perk addition is unclear without the skill template data.

## Claude's review (18 Oct 2:20 AM)

Checked against the copies in `src/`. The numbers it cites are right: the 10 s tick, the audience cap of 50 and `audienceSize / 50`, +5% per grouped entertainer within 40 m, the flourish cap of 1 (dance) or 2 (music) per tick, the flourish cooldown, and the 60 s watch time. Three things are wrong or missing, and the first one changes the bot test.

1. **No flourish, no dance or music XP.**
   - Performance XP is paid only while `flourishXp > 0` (EntertainingSessionImplementation.cpp:1027).
   - A flourish adds `getFlourishXpMod()` (683-684).
   - After that, the carried value falls by `max(1, flourishXpMod / 6)` each tick (1015-1024), so XP keeps coming for a few ticks and then stops.
   - So a bot that only dances earns nothing. "Perform with 0 audience: verify base XP only" must flourish at least once every few ticks. `getBaseXp()` is added only on a tick that pays (1059).
2. **Healing and buffs need two things the report leaves out.**
   - The entertainer needs `private_buff_mind` above 0 (608-611, checked at 152 for healing and at 866 for buffs). This is inferred to come from being inside an entertainment building, since the skill mod's source isn't in these files.
   - A patron gets buff time and strength only if grouped with the entertainer or chosen with /setperform (859-860 and 989-990).
   - So the test's watchers must be in the performer's group. Battle fatigue also needs `private_med_battle_fatigue` above 0 (602-605).
3. **Buff duration is in minutes, not seconds.**
   - The cap is 120 minutes plus 10 s ("2 hrs 10 seconds", 699-700).
   - Each tick adds `2 x buffAcceleration` minutes (997).
   - The buff is only given once the stored duration is at least 10 s (872).

Also:
- `applauseCount` is reset every tick (1090) and never raised in this file, so `applauseMod` is 0 here.
- A tick counts at most 5 flourishes toward buffs (674).

Verdict: usable for the scenario after these three corrections.
