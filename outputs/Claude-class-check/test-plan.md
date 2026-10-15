# Class check: proposed bot test plan

Status: proposal. Nothing here has been run. Everything about the server is read from the source (Core3-dev, commit in `matrix.md`); everything marked UNTESTED is a code reading, not an observation.
Data: `professions.json` (boxes, `proposed_run_order`), `commands.json` (one entry per ability: `slash`, `test_kind`, `setup_tags`, `readiness`, `bot_call`, `messages`, `handler`). Line numbers below are `file:line` in `MMOCoreORB/`; the list is regenerated in `matrix.md` ("Reference lines").

## 1. What gets tested

Tables are read in the server's `TreFiles` order (`bin/conf/config.lua`). The live client also loads `local_planets.tre`, whose `skills.iff` adds `outdoors_botanist` (one box, no abilities) and `species_chiss`; those are not in this plan or in the counts (`matrix.md` header). If the server loads that archive through config-local.lua (not read), add a botanist run with nothing to try.

* 54 professions, 948 boxes, 916 ability tokens. 409 of them are not passive (something to try); 507 are passive (certifications, `private_*` flags, permission flags: nothing to run).
* A run grants one profession, then tries every non-passive ability granted by that profession's own boxes, once. 54 runs, 547 tries (an ability granted by two professions is tried in both runs).
* Rough size: 547 tries at about 5 s of command time each is about 50 minutes (default command times in the table are 0 to 5 s, mean 1.5 s for attacks, plus a margin); with grants, walking, HAM regeneration and target changes plan on 3 to 4 hours for one pair of bots, less if the five groups split the run order. This is an estimate, not a measurement.
* Crafting professions (armorsmith, weaponsmith, chef, tailor, architect, droid engineer, merchant, shipwright) grant no slash command at all. Their run only checks that the grant worked. Crafting itself is not testable: the bot body has no crafting session (`tools/bots/scenarios/README.md`, "Remaining body gaps").

## 2. Granting one profession at a time

The test galaxy already has the tool for this (committed 15 Oct, `6f3ce06f`):

| step | call | source | what to read in the answer |
|---|---|---|---|
| clear | `bot.slash('agentGear', 'profession clear', wait=0)` | AgentGearCommand.h:104 | `[agentgear] {json}`: `surrendered`, `failed` |
| grant | `bot.slash('agentGear', 'profession combat_marksman', wait=0)` | AgentGearCommand.h:172 | `granted`, `failed` (must be empty), `skills` (every box now held) |
| list | `bot.slash('agentGear', 'profession list', wait=0)` | AgentGearCommand.h:141 | `skills` |

Read the answer the way `Bot.gear()` does (`tools/bots/squad.py:391`): `bot.wait_for(lambda e: str(e.get('text','')).startswith('[agentgear]'), 8)`, then `json.loads(text[len('[agentgear] '):])`.

* It grants every box of the profession plus its prerequisites, including boxes of other professions (a bounty hunter run also holds the marksman and scout boxes it needs). No XP, no skill-point limit.
* It refuses god-only professions (AgentGearCommand.h:117). That is the five `jedi_*` professions. For those use `/agentskill <top box>` (cap 250 points; the padawan tree costs exactly 250, SkillManager.cpp:428). `/agentskill` does not check the god-only flag (UNTESTED).
* The `force_*` professions (sensitive, discipline, rank, title) need Jedi state or the Jedi manager (SkillManager.cpp:940, :948). Expect `failed` to list them. `matrix.md` marks 36 abilities `blocked_jedi`. Do not spend time on them until a Jedi state exists.
* `pilot_*` professions should grant, but all of their commands (22 distinct, 23 tries) are space-only: defined only in `command_table_space.iff`. Grant check only.
* UNTESTED: the answer lists every box held (a profession with its prerequisites is up to 54 boxes, 20 to 30 characters each); if the chat line is cut off, judge by the command results instead.
* Do not use `Bot.gear()` after the first call in a run: it returns "already has armor_bone" and gives nothing (`squad.py:396`), so a new profession would get no weapon. Send `/agentgear basic` directly. The weapon it picks depends on the skills held at that moment (AgentGearCommand.h, `basic` branch): `combat_marksman_novice` gives rifle_cdef and pistol_cdef; otherwise `combat_brawler_novice` gives knife_dagger; otherwise pistol_cdef. So grant first, gear second.

Fallback if `/agentgear profession` is off or breaks: `proposed`/`suggested_builds` in `professions.json` pack professions into characters of 250 points for `/agentskill` (no revoke, so one fresh character per build).

## 3. Order

`professions.json -> proposed_run_order` has the 54 rows (also in `matrix.md`, "Proposed run order"). The logic:

| phase | professions | why here |
|---|---|---|
| P0 control | a cleared bot | proves the negative signal (section 5) before any profession is judged |
| P1 | marksman, brawler, scout, medic, entertainer, artisan | starters; every elite sits on one of them; kits for most of their commands exist today |
| P2 | rifleman, pistol, 1h sword, dancer, musician, ranger, doctor, squad leader, smuggler, bio-engineer, creature handler, image designer, politician | weapons and items mostly available: 84 of its 102 tries are ready (P1: 70 of 103) |
| P3 | carbine, 2h sword, polearm, unarmed, commando, bounty hunter, combat medic | blocked on weapon or medicine kits that do not exist yet (section 4): 7 of 75 tries are ready |
| P4 | the eight crafting professions | grant check only |
| P5 | `jedi_*` via `/agentskill`, then `force_*` | Jedi is the least ready: 51 of 244 tries ready, 112 blocked on Jedi state (the `force_*` professions) |
| P6 | `pilot_*` | grant check only |

Inside a run the abilities go in box order (novice, the four branches, master) as listed in `abilities`. In the current tables every ability tried in a run is granted by none of the prerequisite professions' boxes (`exclusive_to_this_profession` equals `tries` in all 54 rows), so a success cannot come from a prerequisite profession; it shows the profession's own boxes grant it. Which of the profession's boxes does it is in `commands.json -> granted_by`. Telling boxes apart by test (grant one box, try its ability) is possible with `/agentskill <box>` after a clear, at the cost of one more clear and grant per box; not proposed.

## 4. What the bots need, by test kind

Counts are abilities (409 non-passive), `readiness` as computed in `commands.json`.

| kind | count | needs | ready now | blocked on |
|---|---|---|---|---|
| attack | 222 | a weapon of the class in Lua `weaponType`; a live hostile creature in range and line of sight; armor (`basic` kit); HAM | 90 | 115 weapon kits (below); 16 Jedi; Force commands also need Force power and no armor |
| self | 65 | usually only the weapon class (berserk, centerOfBeing, aim); a few need a state (feignDeath: in combat; powerBoost: meditating) | 33 | 11 need staging (an affliction or incapacitation on the bot); 19 Jedi; 2 pet |
| heal_other | 25 | a second bot within range, wounded or afflicted; the pack item for packs | 6 | 12 need a specific affliction; 7 need medicine kit items |
| target_friendly | 6 | a second bot (diagnose, healEnhance with enhancement packs, rescue in a group, transferForce) | 3 | the rest |
| performance | 53 | dancer: nothing. Musician: an equipped instrument. Effects (dazzle, spotlight, ...) need a running dance or song first | 53 | |
| item | 16 | survey tool + resource point; instruments; vehicle; city | 2 | 9 kits, 3 city/pet/vehicle |
| unknown | 22 | all space-only | 0 | a ship |
| passive | 507 | nothing to run | n/a | |

Kits that do not exist (`matrix.md`, "Kits the scenario needs"): carbine, polearm, two-hand, unarmed (unequip), special heavy, three lightsaber kits, "medicine2" (wound, state, cure, dot and revive packs), and eight instruments. Proposed template paths are in `matrix.md` and were checked against the client data, not tried on the server. The existing kits: `basic`, `boss`, `support`, `survey` (AgentGearCommand.h:178).

* Species certs let every character use pistol_cdef, carbine_cdef, rifle_cdef, knife_stone, axe_heavy_duty, lance_staff_wood_s1 (`matrix.md`, "Weapon classes"). So only heavy weapons and lightsabers need profession-box certs.
* One weapon is held at a time. Changing it: `bot.slash('transferItemWeapon', args='<destination oid> 4 0 0 0', target=<weapon oid>)` equips (TransferItemWeaponCommand.h:44, `4` = equip); the source comment guesses `-1` removes. UNTESTED, including which destination oid an unequip needs (probably the inventory). Instruments go through the same command (the handler accepts them).
* Training target: no dummy exists. Use a weak creature near the staging point: `bot.find('', radius=100, type='CREO', where=lambda o: o['name'].startswith('@mob/creature_names:'))` (README example). A kill ends the target, so look for the next one before each attack and stop an attack batch when action is under about 30% (`status()['me']['ham']` against `max_ham`).
* Second bot: another member of the same squad group, standing next to the tester. To give it something to heal it fights a creature for a few seconds first (`fight(oid, timeout=10)`) and stops when its health is under about 80%. Wounds, states, poison, disease, fire and bleeding are not producible on demand; abilities that need them are `needs_staging` and should be reported as BLOCKED, not FAIL.
* Squad leader commands: the tester must lead a group. `squad.py setup` fixes the leaders; either re-form the group with the tester as leader (UNTESTED: `/invite`, `/join`) or make the squad leader's group leader the tester.

## 5. Works or fails: what the server says

The bot body (`AgentControl.cpp`) turns server traffic into events that `bot.slash(...)` returns (it waits `wait` seconds): `system` (`text`, either plain text or `@file:key`, AgentControl.cpp:701), `combat` (`attacker_name`, `defender_name`, `amount`, `what` = `@cbt_spam:<spam>_hit|miss|evade|...`, :772), `command_failed` (`command`, `error`, `reason`, `detail`, :830), `posture`, `combat_started`/`combat_ended` (:668). `status()` gives `me.ham`, `me.max_ham`, `me.posture`, `me.states`.

The one event that identifies a class failure:

| signal | meaning | source |
|---|---|---|
| `command_failed` with `error` 2, reason "missing ability or not allowed" | the character does not hold the ability. This is the answer the whole test is after | check: ObjectControllerImplementation.cpp:94-95 (`hasAbility(characterAbility)` then `clearQueueAction(..., 2)`); names: AgentControl.cpp:820 |

It is sent for every command, queued or not. Other `command_failed` codes are setup problems: 1 posture (`detail` = locomotion; sent for every command, QueueCommand.cpp `onLocomotionFail`), and 3 target, 4 range (the body prints it as "unknown"), 5 state (`detail` = state bit), which QueueCommand.cpp only sends for commands with `add_to_combat_queue` true in the command table (`commands.json -> command_table`). 50 of the 335 ground command abilities are not queued; for them a target, range or state problem is silent, and so is every ordinary handler failure (return GENERALERROR sends error 0, which the body does not report); read the system messages.

Verdicts to record per ability:

| verdict | rule |
|---|---|
| WORKS | no error 2, and the evidence for its kind below |
| RAN | no error and no failure message, but nothing observable (many buffs). Report separately; do not count it as WORKS |
| NOT_GRANTED | `command_failed` error 2 after a successful grant. Report as FAIL (`g.check(..., False)`) |
| NO_EFFECT | setup verified, no error, no message, no change within the wait. For a stub handler this is the expected result (`matrix.md`, stub table). FAIL |
| BLOCKED | a setup message below, or a missing kit/staging item. `g.note('BLOCKED: <reason>')`, not FAIL, as `scenarios/README.md` asks |

Evidence by kind:

| kind | WORKS evidence | BLOCKED messages (examples) |
|---|---|---|
| attack | a `combat` event with `attacker_name == 'me'`: any `_hit`, `_miss`, `_evade` proves the attack ran (`amount > 0` for a hit); keys listed in `combat_spam_keys` | `@cbt_spam:no_attack_wrong_weapon` ("This attack cannot be done with this weapon!"); `@error_message:target_out_of_range`; `@cbt_spam:los_fail` |
| self | the handler's success message if `messages` has one; else `me.states` or `me.ham` changed against the `status()` taken before | the handler's failure message; `@jedi_spam:not_with_armor` |
| heal_other, target_friendly | the second bot's `ham` rose (heal) or its `max_ham` rose (enhancement); success texts are `@healing_response:*` | `@healing_response:healing_response_60` "No valid medicine found."; `@healing:no_line_of_sight`; `@jedi_spam:no_help_target` |
| performance | `@performance:music_start_self` for a song (StartMusicCommand.h:127); `@performance:dance_start_self` for a dance (EntertainingSessionImplementation.cpp:417) | `@performance:music_no_instrument`; `@performance:effect_not_performing` |
| item | the tool's own result (for example a `survey_results` event) | `@error_message:insufficient_skill` from the survey tool |

Three examples, checked in the source:

1. **Self buff (berserk1).** Success `@cbt_spam:berserk_success_single` ("You go berserk!") at `Berserk1Command.h:63`. Failure text `@cbt_spam:berserk_fail_single` ("You fail to go berserk.") at `Berserk1Command.h:28` is sent for a wrong weapon (the handler then returns INVALIDWEAPON, which `QueueCommand.cpp:180` answers with `@cbt_spam:no_attack_wrong_weapon`) and again, with the same text, when the random roll (random(100) plus the berserk skill mod, below 25) or the HAM check fails. A roll failure is not a class failure: retry up to three times before calling it RAN or NO_EFFECT.
2. **Attack (unarmedHit1 and the other 216 queued combat commands).** `CombatQueueCommand.h:166` returns INVALIDWEAPON when the equipped weapon does not match the Lua `weaponType`; `:140` sends `@error_message:target_out_of_range`; `:233` sends `@cbt_spam:los_fail`; hits are announced with `@cbt_spam:<combatSpam>_hit` (`:792`; `commands.json -> combat_spam_keys`, for unarmedHit1 `steelhands`), which the bot sees as a `combat` event. Out of range and weapon problems are BLOCKED, a `combat` event is WORKS.
3. **Performance (startMusic).** `StartMusicCommand.h:127` sends `@performance:music_start_self` ("You prepare to begin playing."); `:58` sends `@performance:music_no_instrument` ("You must have an instrument equipped to play music."), which means BLOCKED (no instrument), not NOT_GRANTED. A missing `startMusic+<song>` ability gives `@performance:music_lack_skill_song_self` (`StartMusicCommand.h:122`; the check is PerformanceManager::canPlaySong) and that one does count as NOT_GRANTED; likewise `@performance:dance_lack_skill_self` for a dance.

Commands the table lets anyone run (`gate.ungated` in `commands.json`: customizeVehicle, grantZoningRights, sampleDNA, startDance, startMusic, stopDance, stopMusic, tame) cannot show a class failure at the command level. For the dances and songs the per-name abilities (`startDance+basic`, `startMusic+rock`, ...) are the gate; test those.

Two stub-looking handlers are granted by a profession: `customizeVehicle` (artisan) and `survey` (artisan, padawan). Expect NO_EFFECT from `/survey`; the real gate for surveying is the survey tool's own `hasAbility("survey")` check (`SurveyToolImplementation.cpp:45`, answer `@error_message:insufficient_skill`), so test it by using a tool from `/agentgear survey`.

## 6. Control runs

* **P0, before profession runs.** Cleared bot (`profession clear`, then `profession list`): try `unarmedHit1` on a creature and `healDamage` on the ally. Expected: `command_failed` error 2 for both, and no `combat` event. If the cleared bot can still run them, the negative signal is broken and nothing after it means anything.
* **Start of each run.** Before granting, try the first ability of the previous run. Expected: error 2.
* **Positive control.** One command with no ability gate (`gate.ungated` in `commands.json`), for example `stopDance` with no dance running: expect `@performance:dance_not_performing` (StopDanceCommand.h:30), which shows messages reach the bot on a character that holds nothing.

## 7. Skeleton (uses only methods that exist)

```python
"""Class check, one profession per run. PROPOSED, not run."""
import json
GROUP = 'Aurek'

def agentgear(bot, args):
    bot.slash('agentGear', args, wait=0)
    ev = bot.wait_for(lambda e: str(e.get('text', '')).startswith('[agentgear]'), 8)
    try:
        return json.loads(ev['text'][len('[agentgear] '):])
    except (TypeError, KeyError, ValueError):
        return None

def run(g):
    tester, ally = g['Aurek'], g['Jesh']
    plan = json.load(open('.../Claude-class-check/professions.json'))['proposed_run_order']
    cmds = {e['ability']: e for e in json.load(open('.../commands.json'))['commands']}
    for row in plan:                       # slice by phase / group
        if not row['grant'].startswith('/agentgear'):
            g.note('BLOCKED: %s via %s' % (row['profession'], row['grant'])); continue
        agentgear(tester, 'profession clear')
        got = agentgear(tester, 'profession ' + row['profession'])
        if not g.check(row['profession'] + ' granted', got and not got['failed'], got and got['failed']):
            continue
        agentgear(tester, 'basic')          # after the grant, so the weapon matches
        for ability in row['abilities']:
            e = cmds[ability]
            if e['readiness'] != 'ready':
                g.note('BLOCKED: %s %s %s' % (ability, e['readiness'], e['readiness_missing'])); continue
            # find target / stage ally by e['setup_tags'], then:
            before = tester.status()['me']
            wait = max(3, 2 * (e.get('command_table') or {}).get('default_time', 1.5))
            events = tester.slash(e['slash'], e.get('args', ''), target=0, wait=wait)
            failed = [x for x in events if x.get('event') == 'command_failed']
            # classify with the tables in section 5; g.check(...) for WORKS / NOT_GRANTED / NO_EFFECT
```

Unchecked parts of the skeleton: how the target oid for `target=` is handed to commands that read the current target instead (UNTESTED), and the ally staging. Each of them is a small first scenario of its own.

## 8. Open points for the engineering side

1. Kits for carbine, polearm, two-hand, special heavy, lightsabers, medicine2 and the eight other instruments (`matrix.md`) unlock 131 more tries. Without them P3 is mostly BLOCKED.
2. `Bot.gear()` skips when armor is carried (`squad.py:396`); the plan bypasses it with a raw `slash('agentGear', ...)`.
3. The body cannot read the ability list. `profession list` gives boxes only; abilities are inferred from `skills.iff`. An `/agentgear profession list` answer with abilities would remove one assumption.
4. Whether the `[agentgear]` answer survives a 40-box `skills` list.
5. A way to hurt a bot on purpose (a wound, a state, poison) would turn 27 `needs_staging` tries into runnable ones.
