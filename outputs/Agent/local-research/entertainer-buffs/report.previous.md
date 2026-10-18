Written by Claude Haiku, 15 Oct 2026, from Core3-dev 90044b8e.
(Research begun by Claude Haiku 5.5; the run was resumed and the report finished by Claude Opus 5.5.)

# Entertainer buffs: dance and music

Paths are under MMOCoreORB/. ES = src/server/zone/objects/player/sessions/EntertainingSessionImplementation.cpp; PM = src/server/zone/managers/player/PlayerManagerImplementation.cpp; PB = src/server/zone/objects/creature/buffs/PerformanceBuffImplementation.cpp; FC = src/server/zone/objects/creature/commands/FlourishCommand.h.

## 1. Short answer
A patron uses /watch on a dancing player or /listen on a playing one. Every 10 s the performer heals mind, focus and willpower wounds and battle fatigue on every patron within 60 m. It also builds up a stored buff duration and strength, but only for patrons in the performer's group or set with /setPerformanceBuffTarget. The buff is applied only when the watching ends (the patron stops, the performer stops, or the patron goes out of range), and only after at least 60 s of watching. Dance gives a Mind buff; music gives Focus and Willpower buffs, each a percentage of the patron's base pool. dorn-social.py tests none of this: it only starts and stops a dance and writes a note.

## 2. How it works
**Starting.** /watch and /listen call startWatch/startListen (WatchCommand.h:29, ListenCommand.h:29). The command is refused if there is no line of sight (PM:3563, PM:3628), if the patron is performing (PM:3575, PM:3698), if the target is an NPC (PM:3558, PM:3686), or if the target isn't dancing or playing (PM:3583, PM:3705). If it succeeds, the patron is added with a fresh start time (PM:3601, ES:1156-1162, EntertainingData.h:21) and their mood is set to "entertained" (PM:3600, ES:820-821).

**Each tick (10 s).** The task reschedules every 10000 ms (ES:236, EntertainingSessionTask.h:35) and runs patron effects, XP and action drain (ES:220-222).
- Healing: woundHeal = ceil(healMindWound x healing_dance_wound/100) (music: healing_music_wound). shockHeal = ceil(healShockWound x (healing_dance_shock or healing_music_shock + private_med_battle_fatigue)/100) (ES:59-64, ES:82-83). If the performer is overt and in a registered building of their own faction, private_faction_mind_heal is added to both (ES:72-79). Both amounts are multiplied by (flourishes this tick + 1) and go to the performer and to each patron within HEAL_RANGE = 60 (ES:85, ES:102-103, PerformanceManager.h:28). Wound healing covers mind, focus and willpower (ES:162-167). Nothing heals unless the performer has private_buff_mind > 0 and the patron isn't on the deny-service list (ES:152-156, ES:608-612). Battle fatigue also needs the performer's private_med_battle_fatigue > 0 (ES:158, ES:602-606). Healing has no group check (inferred: healWounds, ES:145-179, never tests the group).
- Buff growth applies to in-range patrons who are grouped with the performer or are the buff target (ES:989). Duration grows by 2 min x (1 + accelerate_entertainer_buff/100), up to 120 min 10 s (ES:995-997, ES:699-700). Strength grows by the performance's healShockWound column (ES:998, Performance.h:191). The cap is healing_dance_mind or healing_music_mind, at most 125, plus private_faction_buff_mind in the faction case (ES:713-735). If the cap is 0, strength is held at 0 (ES:738-745). Both values are stored as whole numbers (EntertainingData.h:14-15), so fractions are dropped (inferred).
- A patron beyond 60 m is stopped as out of range (ES:106-119).

**Flourishes.** /flourish N accepts 1-8 and needs the ability flourish+N (FC:37-52). Each of the first 5 flourishes in a tick adds one more buff-growth step to every patron (ES:674-676, ES:614-626) and raises the healing multiplier. The count resets every tick (ES:1092). A flourish costs action and prints flourish_perform (ES:648-662, ES:690). The command delay is a default (5 s, per the comment) minus healing_dance_ability or healing_music_ability divided by 30 (FC:65-77). /bandflourish also flourishes group members within 50 m who accept band flourishes (BandFlourishCommand.h:75-113).

**Granting the buff.** stopWatch/stopListen call activateEntertainerBuff before removing the patron (PM:3495, PM:3408). They run when the patron stops, when the performer stops (ES:571-576, ES:303-308), or when the patron goes out of range (ES:110, ES:115). The checks, in order (ES:853-889):
1. The patron isn't on the deny list.
2. The patron is grouped with the performer or is the buff target.
3. The patron isn't incapacitated or dead.
4. The performer has private_buff_mind.
5. The stored duration is at least 10 s.
6. At least 60 s have passed since the watch began. If not, the patron gets the hard-coded message "You must listen or watch a performer for at least 1 minute in order to gain the entertainer buffs." (ES:877-881)
7. Strength is above 0.

An existing stronger buff is kept (ES:899-900, ES:916-917). Dance adds performance_enhance_dance_mind; music adds performance_enhance_music_focus and _willpower (ES:893-923). Size = round(strength/100 x base pool) (PB:16, PB:22, PB:28). Length = stored minutes x 60, which I take to be seconds (ES:901, ES:918; seconds inferred).

**What people see.**
- Performer: dance_start_self (ES:417), flourish_perform (ES:690), dance_stop_self (ES:562), and dance_too_tired or music_too_tired when action runs out (ES:266-275). /setPerformanceBuffTarget sends buff_set_target_self to the performer and buff_set_target_other to the target (SetPerformanceBuffTargetCommand.h:53-59).
- Patron: dance_watch_self or music_listen_self (PM:3606, PM:3739). On stop: dance_watch_stop_self, dance_stop_other if the performer stopped, or "You stop watching X because they are too far away." (PM:3515-3527; music PM:3427-3439).
- On a buff: @healing:performance_enhance_dance_mind_d (or _music_focus_d, _music_willpower_d) (PB:18, PB:24, PB:30).
- Music flourishes broadcast a Flourish packet; dance flourishes play skill_action_N (ES:664-671).

**Other ends.** A posture change (EntertainingObserver.idl:21-26, CreatureObjectImplementation.cpp:3326) or combat (CombatManager.cpp:429, :601) cancels the session.

**Same buff names elsewhere.** enhanceCharacter (character builder) adds plain buffs with the same three names and prints "An unknown force strengthens you for battles yet to come." (PM:6668-6686).

## 3. What a bot test should check
Setup:
- A performer whose skills give private_buff_mind > 0, healing_dance_mind > 0 and the dance's ability.
- A patron in the performer's group, or the performer runs /setPerformanceBuffTarget on the patron.
- Both standing, within 60 m and in line of sight; the patron not performing.
- For healing: give the patron mind wounds or battle fatigue first, and give the performer the battle-fatigue skill mods.

Steps:
1. Performer runs /startdance; expect dance_start_self.
2. Patron runs /watch; expect dance_watch_self.
3. Wait at least 70 s (seven ticks). Optionally the performer flourishes a few times; expect flourish_perform.
4. The patron stops watching, or the performer runs /stopdance.
5. Proof of a buff: the patron receives @healing:performance_enhance_dance_mind_d and their maximum mind rises. Whether the bot can read maximum HAM is inferred; aurek-doctor-buffs.py:83 notes the bot exposes no buff list.

Controls:
- Stop after 30 s: expect the 1-minute message and no buff message.
- A patron who is neither grouped nor the buff target: expect no message at all.
- For healing, compare wounds or battle fatigue before and after a few ticks.
- Don't count "An unknown force strengthens you" as proof.

Current scenarios:
- dorn-social.py:75-78 only runs /startdance basic and /stopdance and writes a note. No patron watches and nothing is checked.
- aurek-boss-camp.py:65-69 watches for 25 s and then stops. That is under the 60 s rule (ES:877), so no buff can be granted.

## 4. Likely reasons a test sees no effect
- The patron isn't grouped with the performer and isn't the buff target. Silent (ES:859, ES:989).
- The patron watched for less than 60 s (ES:877-881).
- The performer lacks private_buff_mind or healing_dance_mind/healing_music_mind, so strength stays 0. Silent (ES:866, ES:738-745, ES:889).
- The test checks while the patron is still watching. The buff arrives only on stop (PM:3495, PM:3408).
- The watch was refused: no line of sight, patron performing, NPC target, or target not performing (PM:3558-3589).
- The performance ended early: posture change, combat, or no action left (ES:266-275).
- A stronger buff is already present (ES:899-900, ES:916-917), or the patron is incapacitated or on the deny list (ES:853-863).
- Healing only: the patron has nothing to heal, or the performer lacks private_med_battle_fatigue (ES:158-162).

## 5. Open questions
- The skill-mod values per entertainer skill box aren't in the tree: a grep of bin/scripts/skills found none of these names. They probably come from the client skills datatable (inferred).
- datatables/performance/performance.iff isn't in the tree, so healMindWound and healShockWound for "basic" are unknown.
- I didn't read cancelSession, which posture changes and combat use. Whether it gives patrons their buffs is unconfirmed.
- Re-running /watch probably resets the 60 s clock, because addPatron replaces the patron's data (ES:1157-1162; inferred).
- I didn't check whether "stopwatching" (aurek-boss-camp.py:69) is a server command, or read the code for the startdance command.
