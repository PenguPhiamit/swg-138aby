Written by Claude Haiku and Claude Opus, 15 Oct 2026, from Core3-dev 90044b8e.

Paths are relative to MMOCoreORB/. Short forms: HE = src/server/zone/objects/creature/commands/HealEnhanceCommand.h, HW = .../commands/HealWoundCommand.h, QC = .../commands/QueueCommand.cpp (QCh = .h), EP/WP = src/server/zone/objects/tangible/pharmaceutical/EnhancePackImplementation.cpp / WoundPackImplementation.cpp, PM = src/server/zone/managers/player/PlayerManagerImplementation.cpp, CO = src/server/zone/objects/creature/CreatureObjectImplementation.cpp, BO = src/server/zone/objects/building/BuildingObjectImplementation.cpp.

## 1. Short answer
Both commands only check the doctor's `private_medical_rating` skill mod, minus any part that comes from a player city. That number must be above 0 (HE:91-95, HW:114-117). The server never checks a room, cell or "treatment anchor". Entering any cell of a building whose template lists the mod gives it to the doctor (CellObjectImplementation.cpp:208-217, BO:910-919, StructureObjectImplementation.cpp:711-728). The Tatooine hospital template gives 100 (bin/scripts/object/building/tatooine/hospital_tatooine.lua:45). A camp (CampSiteActiveAreaImplementation.cpp:77) or a medical droid module (DroidMedicalModuleDataComponent.cpp:98) also gives it. Enhance range is 7 m and wound healing 6 m (HE:25, HW:25). Both share one cooldown of about 20 s (HE:28-48).

## 2. How it works
**Location.** If the rating not counting the city part is 0 or less, the doctor sees `@healing_response:must_be_near_droid` (HE:91-95, HW:114-117). If the rating is above 0 but the doctor's top-level container is a client object, the part from the structure must also be above 0, or the doctor sees `must_be_in_hospital` (HE:97-104, HW:119-127). Client objects are made by createClientObject (src/server/zone/ZoneServerImplementation.cpp:755). Building mods are added on entry and removed on exit (BO:919, BO:1046). City mods are SkillModManager::CITY (src/server/zone/objects/region/CityRegionImplementation.cpp:908) and do not count.
**Common checks** (QC:261-279): state mask, locomotion, prone, meditating, swimming or mounted. Then come distance (world positions minus both template radii, QCh:126-127), line of sight, and cell entry permission (QC:75-112).
**healEnhance checks, in order** (HE:77-137): patient dead, cooldown (`enhancement_must_wait`), no pack (`healing_response_60`), location, doctor in combat, patient neither a player nor a pet (`healing_response_77`), patient in combat, mind below the cost, no line of sight. With no target the doctor buffs themself (HE:269-271). A dead or mounted patient is swapped for the doctor (HE:367-368). Mind cost is 150 before the focus adjustment (HE:24, HE:370). A pack needs medicine use no higher than `healing_ability` (HE:54-68). The argument `attr|objectId` picks that pack (HE:290-311). With no argument the server takes the first attribute below MIND that has no medical buff and has a pack (HE:317-331).
**Buff strength.** For a stat buff: power = pack effectiveness × battle-fatigue ratio × (rating ÷ 100) × (100 + `healing_wound_treatment`) ÷ 100 (EP:8-41). The rating is the city part plus the structure part, or the droid part when there is no structure part (EP:13-23). It also adds `private_faction_medical_rating` if the doctor is registered in the building, overt, and of the same faction (EP:25-36). With hospital 100 and no city part, the multiplier is 1.0. Protection (resist) packs use only effectiveness × fatigue ratio (HE:207-209). Battle-fatigue ratio: 1 up to 250 shock, otherwise (1250 − shock) ÷ 1000, kept between 0.25 and 1 (CO:2644-2655).
**Buff and duration.** The buff is named `medical_enhance_<attr>`, its type is MEDICAL, and it lasts the pack's duration. A Twi'lek patient gets ×1.10 (PM:3291, PM:3313-3317). A stat buff is an attribute modifier with fill-on-buff (PM:3327-3328). A protection buff is a skill modifier plus absorption (PM:3321-3325). A weaker new buff is refused with "...current enhancements are of greater power..." (HE:387-393). An equal or stronger one replaces the old buff, and the command returns only the increase (PM:3305-3308, PM:3335).
**What players see.** The doctor sees "You enhance <name>'s <Attr> by N." and the patient sees "<doctor> enhances your <Attr> by N." N is the increase. When N is 0 the text says "re-apply" (HE:177-201). Battle-fatigue warnings appear when shock is 250 or more (PM:3268-3287). The patient shows the effect clienteffect/healing_healenhance.cef and the doctor plays heal_other (HE:241-248). The doctor gets medical XP of round(N × 2.5), none for self-buffs (HE:226-238, HE:423-424). One pack use is spent (HE:418-421).
**healWound.** Mind cost is 50 (HW:24). The target becomes the doctor if it is a non-pet AI, droid, vehicle, dead, mounted or attackable (HW:252-253). Extra checks: arena duel (HW:140-143) and isHealableBy, which fails with `pvp_no_help` (HW:145-148, CO:3811-3842). Auto mode picks the first pool with wounds that has a pack (HW:288-302). Power = effectiveness × fatigue ratio × (1 + rating ÷ 100) × (100 + `healing_wound_treatment`) ÷ 100 (WP:11-48). Unlike enhancement, the rating here adds to the base. Wounds go down by that power but not below 0 (CO:1327-1351). Messages: "You heal <name> for N <pool> wound damage." and "<doctor> heals you for N..." (HW:75-100). If that pool has no wounds, the doctor sees "...has no wounds of that type to heal." and the command returns 0, which is SUCCESS (HW:310-324, QCh:60).
**Cooldown.** delay = round(20 − 0.08 × `healing_wound_speed`) s. A heal_recovery food buff reduces it by its percent, and the minimum is 3 s (HE:28-44, HW:28-44). Both commands use the pending task "woundTreatment" (src/server/zone/objects/creature/CreatureObject.idl:1354-1356). When the task ends the doctor sees `healing_response_59`.
**Error codes** (QCh:60-76): 1 GENERALERROR, 2 INVALIDLOCOMOTION, 6 TOOFAR.

## 3. What a bot test should check
Setup:
- The doctor has the `healenhance` command (registered at src/server/zone/managers/objectcontroller/command/CommandConfigManager2.cpp:750).
- The doctor carries packs whose medicine use is no higher than `healing_ability`.
- Both bots are standing, out of combat and not mounted, within 7 m (6 m for wounds) with line of sight.
- The doctor has at least 150 mind.
- The doctor stands in **any cell** of the hospital building. The bot only needs one cell ID that belongs to that building; no medical room is required. A camp or a medical droid also works.
Observable results:
- (a) The doctor's message "You enhance <name>'s Health by N" and the patient's "enhances your".
- (b) The patient's max HAM rises (inferred from the fill-on-buff attribute modifier). The rise should be the full buff value on a first buff, not N on a re-apply.
- (c) The doctor's mind drops by about 150.
- (d) For wounds, the patient's wounds in that pool drop by min(power, wounds), plus the message.
- (e) `healing_response_59` after the cooldown.
Negative checks: outdoors in a city gives `must_be_near_droid`; a second command within 20 s gives `enhancement_must_wait`.
Changes to aurek-doctor-buffs.py:
- Replace the 'medical'/'healer' interior search (lines 26-33) with "walk into any cell whose parent is the hospital".
- Wait at least 20 s between attempts, or wait for `healing_response_59`. The current 5 s idle (line 84) makes the second buff fail.
- Error 2 means INVALIDLOCOMOTION, not a missing command (lines 68-71), if the harness passes the server codes through (inferred).
- Treat "re-apply" as no change in max HAM.
- Use system messages as the primary signal.

## 4. Likely reasons a test sees no effect
- The doctor is not inside the building (only a city rating applies), or is inside a client-object building with no structure mod.
- The 20 s cooldown is still running.
- The patient is dead or mounted, so the buff lands on the doctor. In healWound, an attackable target is replaced by the doctor.
- The patient already has an equal or stronger buff. That gives "re-apply" (no max-HAM change) or a refusal.
- No usable pack: the medicine level is too high, or the pack's attribute doesn't match.
- Either bot is in combat, or the doctor's mind is too low.
- Battle fatigue cuts power as low as 25%. A small rating or effectiveness can round down to 0, which shows as "re-apply" (inferred, from uint32 truncation).
- Protection packs change resists, not HAM.
- The target is out of range or out of sight, or the bot is in the wrong locomotion state (error 2).

## 5. Open questions
- Is the static Tatooine hospital built through createClientObject (client object) or as a normal BuildingObject? (BuildingObject.idl:75 sets the flag false.) Does a client building also run onEnter? Not traced.
- Which skill boxes grant `healenhance` and `healwound`, and at what `healing_ability`? A search of bin/scripts/skills found no command names.
- What pack values (effectiveness, duration) does Tamsin carry? This needs an in-game examine.
- How the buff changes max HAM (Buff with fill-on-buff) was not read. Does addBuff replace a buff with the same CRC? Inferred yes.
- What do `private_med_wound_health` and `private_med_wound_action` do (hospital_tatooine.lua:46-47)? What ratings do camps give?
- The actual client texts of the string IDs: only the code comments were read.
- Does the bot harness's `error` field equal the server's QueueCommand codes?


## ChatGPT's review (2026-10-18 02:25)

Checked the report against Core3-dev `aa52cc647a2129096011eb122fe98c7794db4c2b` (read only, paths relative to MMOCoreORB/) (this topic has no `src/` snapshot); no in-game checks. The original draft remains above; corrections below take precedence.

**Holds:** stock location rating checks, 7 m enhancement/6 m wound range, focus-adjusted mind, shared woundTreatment cooldown, skill-filtered packs, combat/LOS restrictions and re-apply semantics are supported (HealEnhanceCommand.h:24-48,54-68,78-137,368-425; HealWoundCommand.h:104-163,310-357). Enhancement multiplies by rating/100; wound healing uses 1+rating/100 (EnhancePackImplementation.cpp:42-45; WoundPackImplementation.cpp:50-52). The test must accept a re-apply without a max-HAM increase.

**Corrections/current-source changes:**
- 'Must be above 0' is no longer unconditional. Both commands allow medicalAnywhere for an eligible test player (HealEnhanceCommand.h:92-107; HealWoundCommand.h:115-129). SandboxTestGalaxy.h:18-32,45-49 requires a _test DB, god mode or an allowlisted account, and Core3.MedicalAnywhere. It is not permission to use this on live.
- When no structure/droid rating exists, that switch supplies rating 100 while retaining the city bonus (EnhancePackImplementation.cpp:26-27; WoundPackImplementation.cpp:34-35). Outdoors is therefore not always a negative test.
- Auto enhancement also tries already-buffed attributes ordered by duration when no unbuffed candidate has a pack (HealEnhanceCommand.h:334-362); it does not stop with only the first unbuffed-attribute pass.
- The named scenario and original line numbers describe an earlier harness. Current behavior must be read before applying its proposed edits; no scenario edits or runtime sign-off were done here.

**Limit:** source formulas and messages are verified; actual carried pack values, client display and hospital entry remain untested.

**Verdict:** Stock mechanics mostly hold; qualify current MedicalAnywhere test-only behavior and auto-refresh selection; gameplay untested.
