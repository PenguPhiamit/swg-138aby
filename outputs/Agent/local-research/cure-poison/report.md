Written by Claude Haiku, 15 Oct 2026, from Core3-dev 90044b8e.
(The run was interrupted and Claude Opus finished writing it from the same reading. Paths are relative to MMOCoreORB/.)

# Cure poison (/curePoison with a cure pack)

## 1. Short answer

`/curePoison` is the generic cure-pack command with its state fixed to POISONED (src/server/zone/objects/creature/commands/CurePoisonCommand.h:13-16). It only acts on a patient who carries the POISONED state. The patient must also be within 7 m, in line of sight and healable. The healer needs a poison cure pack lying directly in their inventory whose medicine-use requirement is no higher than their `healing_ability` skill mod. On success the healer gets the plain-text line "You apply poison antidote to <name>." and pays mind. The pack loses a charge and a 4-20 s "conditionTreatment" cooldown starts. The poison DoT is cut by the pack's power and the state is cleared if the power covers the poison's strength. Almost every failure sends the healer a message. The silent exits are range, an invalid target, an arena duel and the building-entry check, so a NO_EFFECT verdict (no text at all) points to one of those or to a message the bot did not capture. A missing pack would give "No valid medicine found", not silence.

## 2. How it works

**Choosing the target** (src/server/zone/objects/creature/commands/CurePackCommand.h)
- Common medic checks run first: state mask, locomotion, prone/meditating/swimming ("@error_message:wrong_state"), mounted ("@error_message:survey_on_mount") (QueueCommand.cpp:261-279, called at CurePackCommand.h:359).
- A target that is not a creature gives INVALIDTARGET (366-367). With no target the healer treats themselves (368-369).
- The target falls back to the healer when it is a non-pet AI, a droid, dead, riding a mount, or attackable by the healer (375-376).

**Finding the pack**
- If the command's argument is all digits, that inventory object is used. Otherwise the command searches for a pack (41-52, 380-392).
- The search only checks the inventory's direct children, so a pack inside a bag is not found. It takes the first cure pack whose `getState()` equals POISONED and whose `getMedicineUseRequired()` is no higher than the healer's `healing_ability` skill mod (54-77).
- The pack's state, effectiveness, medicine use and area come from its template (CurePack.idl:50-63). Crafted packs take them from the crafting values instead (CurePack.idl:33-41).
- Using the pack from its radial menu checks `healing_ability` ("@error_message:insufficient_skill") and then sends the command with the pack's object ID (CurePack.idl:73-91).

**Range**: 7 m (CurePackCommand.h:27). The distance between world positions, minus both template radii, must be at most 7 (QueueCommand.h:126-128). Out of range returns TOOFAR (CurePackCommand.h:394-395).

**Checks in canPerformSkill, in order, with the healer's message** (CurePackCommand.h:268-355)
1. Patient not poisoned: "@healing_response:healing_response_82" when curing yourself, "@healing_response:healing_response_84" for a player patient, or plain "<name> is not poisoned." (270-284). `isPoisoned()` tests the state bit (CreatureObject.idl:2176-2178).
2. Cooldown running: "@healing_response:healing_must_wait" (320-323). This checks the pending task "conditionTreatment" (CreatureObject.idl:1359-1361).
3. No pack: "@healing_response:healing_response_60" (325-328).
4. Arena duel: the check fails with **no message** (330-331).
5. Patient not healable: "@healing:pvp_no_help" (333-336).
6. Not enough mind: "@healing_response:not_enough_mind" (338-341).
7. No line of sight: "@healing:no_line_of_sight" (345-348).
8. `playerEntryCheck` fails: **no message** (350-352). No message appears in QueueCommand.cpp:75-104.

**On success** (CurePackCommand.h:402-431)
- Mind cost = `calculateCostAdjustment(FOCUS, 100)` (28, 397), taken from MIND (406).
- Messages (80-122):
  - Curing someone else: the healer gets plain text "You apply poison antidote to <name>." (96, 117). A player patient gets "<healer> applies poison antidote to you." (97, 119-120).
  - Curing yourself: the healer gets "@healing_response:poison_antidote_self" (98, 115).
- Power = `(100 + healing_wound_treatment) / 100 * effectiveness` (CurePack.idl:126-129). `healDot(POISONED, power)` is applied (CurePackCommand.h:404, CreatureObject.idl:834-836).
- `healState`:
  - It returns at once if the patient has no DoT entries (DamageOverTimeList.cpp:255-256).
  - Otherwise it subtracts the power from each active poison DoT's strength (DamageOverTimeList.cpp:260-291). When the power exceeds a DoT's strength, that DoT expires (DamageOverTime.cpp:503-517).
  - If the power covered every poison DoT, the POISONED state is cleared (DamageOverTimeList.cpp:293-300). If not, the patient stays poisoned and gets "@dot_message:decrease_poisoned" (303-304, 466-467).
- Cooldown: "conditionTreatment" task of round(20 - healing_injury_speed/5) s. The food buff `heal_recovery` shortens it, and it is never under 4 s. When it ends the healer gets healing_response_58 (CurePackCommand.h:124-143).
- The pack loses one use (410-413). The healer gets 50 "medical" XP unless curing themselves or a pet (415-416).
- An area pack also cures nearby players and pets that are not attackable (418-423, 201-248).
- Effects and other steps: the client effect "clienteffect/healing_healdamage.cef" plays, with the animation "heal_self" or "heal_other" (425, 32-39). Then MEDPACKUSED observers fire and the TEF check runs (427-429).

**Poison itself**
- A poison DoT ticks every 10 s, the first tick 10 s after it is applied (DamageOverTime.cpp:155-157, 202-204). Victim absorption from `absorption_poison` is capped at 50 (203).
- Poison applied with potency above 0 is resisted on a roll; potency below 0 cannot be resisted (DamageOverTimeList.cpp:124-126).
- The start message is "@dot_message:start_poisoned" (399-400).

**Failure codes**: TOOFAR and INVALIDTARGET only clear the queue action with an error code and send no chat text (QueueCommand.cpp:160-163, 188-191).

## 3. What a bot test should check

**Setup**
- `/agentgear afflict poison` on the partner adds a POISONED DoT: strength 30, HEALTH pool, 120 s, potency -1, which bypasses the roll (src/server/zone/objects/creature/commands/AgentGearCommand.h:183-185). The target must be a player on an agent account (142-152).
- Confirm the partner's states include `poisoned` before curing. class-check already does this (class-check.py:623-625).
- Confirm the tester has a cure pack as a direct child of the inventory. The gear kit lists "object/tangible/medicine/crafted/medpack_cure_poison_a.iff" (AgentGearCommand.h:102).
- Confirm the tester's `healing_ability` is at least the pack's medicine use. You can read that on the pack as the `healing_ability` attribute (CurePack.idl:112-114).
- Partner within 7 m and in line of sight, not attackable by the tester, and no "conditionTreatment" cooldown running.
- Cure within 120 s of the afflict.

**Observable results**
- Tester system text matching "You apply poison antidote to " (already matched by `HEAL_TEXT` "You apply ", class-check.py:88-89).
- The partner's states lose `poisoned` (class-check.py:215-217). This only happens if power ≥ 30 (inferred from the strength above).
- The tester's mind drops by about 100 after FOCUS adjustment.
- The pack's use count drops by 1.
- A second cure within 4-20 s answers "@healing_response:healing_must_wait".
- The bot sees string-table messages as "@file:key" (src/client/agent/AgentControl.cpp:704-725). Treat any of the failure keys above as BLOCKED with that reason, not NO_EFFECT.

## 4. Likely reasons a test sees no effect

1. **A silent exit in the server:**
   - Partner over 7 m once radii are counted (TOOFAR).
   - Target object is not a creature (INVALIDTARGET).
   - Arena duel.
   - `playerEntryCheck` failing because tester and partner are in different cells or a building.

   None of these sends text.
2. **The healer's text came after the probe's wait**, which is min(12, max(3, 2 × default_time)) s (class-check.py:396-397) (inferred possibility).
3. **A missing pack (full inventory)** gives "@healing_response:healing_response_60" if the partner is poisoned. If the partner is not poisoned it gives the "not poisoned" text. By these rules that is BLOCKED or RAN, not NO_EFFECT, unless the text was lost.
4. **A failed afflict before 15 Oct** should have been caught by the `poisoned` state check in `stage_partner` (BLOCKED, class-check.py:623-625), unless the status was stale (inferred).
5. **The partner has the POISONED bit but no DoT entry.** `healState` then returns early and the state stays (DamageOverTimeList.cpp:255-256). The tester still gets the "You apply" text, so this would look like a partial success, not NO_EFFECT.
6. **The pack's power is below 30.** The cure only lowers the DoT and the state stays, but the "You apply" text still appears.

## 5. Open questions

- I did not check the effectiveness and medicine-use values in the template for `medpack_cure_poison_a`, or whether medic skills grant enough `healing_ability` and `healing_wound_treatment`.
- I did not check whether the agent client turns `clearQueueAction` error codes (TOOFAR = 4, INVALIDTARGET = 3) into `command_failed` events. If it does, those cases become BLOCKED rather than NO_EFFECT.
- I did not check whether `clearState(POISONED)` after a full cure sends "@dot_message:stop_poisoned" to the patient. `sendStopMessage` exists (DamageOverTimeList.cpp:414-436), but I did not find its caller.
- I did not check the `default_time` and queue rules in the command table for curePoison, or what `onFail` does with GENERALERROR.
- I did not check which gear-kit name hands out the cure pack, or what happens to it when the inventory is full (AgentGearCommand.h:95-110 not fully read).
- I did not read the rest of `playerEntryCheck` (QueueCommand.cpp:104 onward).
- The log of the run that reported NO_EFFECT was not examined. It would show the distance, cell and wait window.
