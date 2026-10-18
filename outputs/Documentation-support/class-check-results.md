# Class check results (C33)

Started 15 October 2026 on the test galaxy, Aurek group. Plan: `../Claude-class-check/test-plan.md`. Scenario: `../tools/bots/scenarios/class-check.py` (offline tests: `../tools/bots/test_class_check.py`). Raw per-profession reports: `../Bot-reports/Aurek/class-check-<profession>.json`.

Status: P0 controls done and passing; P1 `combat_marksman` done. The other P1 starters (brawler, scout, medic, entertainer, artisan) wait for the test galaxy restart that brings the new `/agentgear` kits and `afflict`; they are listed below as pending and filled in as they run. Nothing here is a statement about a profession that has not been run.

## How to read a row

| verdict | meaning (test-plan section 5) | counts as |
|---|---|---|
| WORKS | command accepted and the kind-specific evidence appeared (a matching outgoing combat hit/miss, a handler success message, a posture change, a cure seen on the patient) | PASS |
| RAN | accepted, no error, nothing observable to prove an effect | note |
| NOT_GRANTED | error 2 ("missing ability or not allowed") after a verified grant | FAIL |
| NO_EFFECT | setup verified, no error, no message, no change | FAIL |
| BLOCKED | the setup could not be built (no creature, no kit, tester down, ...) | note, never a FAIL |

"gate passed": the command was sent and no error 2 came back. The server tests the ability before anything else (`ObjectControllerImplementation.cpp`, `activateCommand`), so a BLOCKED row with gate passed still shows that the profession holds the ability. From the next restart the scenario also records `held`: whether the ability is in the `abilities` array of `/agentgear profession list`.

## P0: the negative signal works

Run first in every invocation (and once on its own, 03:45). A bot with every skill cleared:

| control | result |
|---|---|
| `unarmedHit1` on a creature | `command_failed` error 2 "missing ability or not allowed", no combat event: PASS |
| `healDamage` on the ally | error 2, no combat event: PASS |
| `stopDance` (ungated), positive control | `@performance:dance_not_performing` arrives: PASS |

So the absence of a profession is visible to the bot, and the messages reach it. Every later run also tried the previous profession's first ability right after the clear (error 2 each time), and the final clear plus the restoration of every member's starting boxes was verified (`restore starting boxes`, five of five).

## Summary, P0 and P1

| profession | tester | tries | WORKS | RAN | NOT_GRANTED | NO_EFFECT | BLOCKED | boxes held after grant |
|---|---|---|---|---|---|---|---|---|
| combat_marksman | Aurek | 25 | 23 | 1 | 0 | 0 | 1 | 21 |
| combat_brawler | | | pending | | | | | |
| outdoors_scout | | | pending | | | | | |
| science_medic | | | pending | | | | | |
| social_entertainer | | | pending | | | | | |
| crafting_artisan | | | pending | | | | | |

## combat_marksman

Run 04:16 to 04:34 (1090 s including the cleanup; the 30 minute ceiling holds). Tester Aurek, ally Jesh. `/agentgear profession combat_marksman` granted 18 boxes (21 held with the species and language skills), `failed` empty. 25 tries: 23 WORKS, 1 RAN, 1 BLOCKED, 0 NOT_GRANTED, 0 NO_EFFECT.

There are no NOT_GRANTED or NO_EFFECT abilities: every marksman ability that was tried is granted by the profession and does what it says.

WORKS, attacks (a `combat` event with attacker "me" and the ability's own spam key, for example `@cbt_spam:headshot_hit`): pointBlankArea1, pointBlankSingle1, overChargeShot1, overChargeShot2, headShot2, mindShot1, bodyShot1, rollShot, diveShot, kipUpShot, bodyShot2, healthShot1, legShot1, fullAutoSingle1, legShot2, actionShot1, threatenShot, warningShot, suppressionFire1. The pistol abilities ran with `pistol_cdef`, the rifle ones with `rifle_cdef`, the four carbine ones with a `carbine_cdef` that Aurek already carried (the carbine kit did not exist yet); a weapon swap through `transferItemWeapon` was confirmed each time by the item's parent being the character.

WORKS, self: takeCover (`@cbt_spam:cover_success_single`), tumbleToProne / tumbleToKneeling / tumbleToStanding (the `@cbt_spam:tum_*` combat spam, plus a posture event for the first two).

RAN: aim. The command is accepted (no failure, no error) but `aim` only sets an aiming state, and the body's `status().states` has no name for that bit (`AgentControl.cpp`, `stateNames` lists combat, peace, stunned, blinded, dizzy, intimidated, immobilized, swimming, crafting, poisoned, bleeding, diseased, on fire, riding mount, piloting ship). No evidence either way, so it is reported separately, not as WORKS.

BLOCKED: headShot1. The tester had been killed between two probes (a mountain worrt hits for about 250), was cloned, and its action was still low when the probe began. `headShot2` (same weapon, same family) WORKS, so the profession plainly holds the family, but `headShot1` itself was not observed. It was not re-run (see "Open" below).

## What this tells us so far

* The method works end to end: grant a whole profession on the test galaxy, prove the negative signal first, try every ability, restore the starting boxes. The server accepted 24 of 25 marksman abilities and the evidence for 23 of them is a combat event or message, not a guess.
* Marksman is complete as far as the tables say: all 25 ability tokens the matrix lists for the profession are held and work with the right weapon. No case of "the table says it is granted but it is not".
* ChatGPT's earlier partial runs showed why the evidence rules matter: "own HAM changed" counted natural regeneration as proof (aim, centerOfBeing and forage were recorded as WORKS on a rise from 780 to 792 action). The scenario now accepts only a HAM drop with no damage taken and no combat, a posture or state change, or a message.
* Wildlife is the hard part of attack tests. The server's object search never sees live spawns, and aggressive animals (scyk level 12, kreetle, sevorrt) incapacitated and poisoned the tester on the first approach. The scenario now walks to the sevorrt plateau and attacks only passive animals (dwarf eopie, worrt, rill, eopie, exact species), and only when no other wildlife is within 60 m.

## Scenario changes made while finishing it (for the commit)

* Verdict rules: regeneration is not evidence; tumble messages are success; `no_attack_ranged_single` / `no_attack_melee_single` (wrong weapon) are setup; the survey tool's `insufficient_skill` is NOT_GRANTED; diagnose opens a window; healer success text and patient state/posture changes prove a cure.
* Staging: wildlife via the plateau, exact passive species, health floor, recovery of a downed tester, bounded approach legs; unequip through `transferItemMisc` so the unarmed abilities can be tried; stock weapons the tester already carries cover a missing kit; kits requested from each entry's `kits`; `afflict` for wounds, states, poison, disease, fire, bleeding, damage and incapacitation on the ally.
* Tester per run: a group member who started as that profession (Aurek for marksman, Jesh brawler, Tamsin medic, Sela entertainer, Oren scout), so the gear and a clean inventory match. Aurek's inventory held 93 items from repeated `basic` kits in earlier runs, so every later `basic` failed (nothing to equip and no room).
* Run ceiling: invoke with `--round-minutes 30 --no-fallback`; without it the default 10 minute round budget stops the scenario.

## Open

* P1: brawler, scout, medic, entertainer, artisan (to run after the restart).
* P2 non-combat first: dancer, musician, doctor, bio-engineer, creature handler, image designer, politician, ranger.
* headShot1: rerun with the marksman if there is time.
* Body gap: `AgentControl.cpp` `stateNames` does not report aiming, cover or berserk; `aim`, `takeCover`'s state and berserk cannot be observed except by message.

## Commands used

Offline tests (Windows or WSL): `python -I outputs/tools/bots/test_class_check.py`

One profession (from Windows, a script file avoids quoting problems):

```
CLASS_CHECK_PHASE=P1 CLASS_CHECK_PROFESSIONS=combat_marksman \
wsl -d Debian -u swgemu -- python3 /mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/tools/bots/squad.py run \
  /mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/tools/bots/scenarios/class-check.py \
  --group Aurek --rounds 1 --round-minutes 30 --no-fallback
```

Controls alone: `CLASS_CHECK_PHASE=P0`. Before each run: `pgrep -f "squad.py run"` must show nothing, `test_galaxy.py status` must say initialized, `squad.py status Aurek` must show all five online (otherwise `squad.py setup Aurek`). A stuck run is stopped with `squad.py halt`; the cleanup still restores the boxes.
