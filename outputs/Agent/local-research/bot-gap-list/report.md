# Local model: bot-gaps (draft)

Written by the local model through `tools/agents/local/local_jobs.py`; 237 input lines. A local model's draft: check each item before acting on it.


## body

| Gap | Notes | Seen | Last | Example |
|---|---|---|---|---|
| bot failed recovery causing test skip | 24 | 24x | 10/15 06:19 | BLOCKED: melee1hLunge1: tester did not recover (action/health) twice running; the rest of the profession is skipped |
| bot cannot see target due to line of sight | 2 | 9x | 10/17 05:38 | FAIL: ?: ["@healing:no_line_of_sight"] |
| tester fails to recover health twice | 7 | 7x | 10/15 06:19 | BLOCKED: polearmLegHit1: tester did not recover (action/health) twice running; the rest of the profession is skipped |
| bot cannot reach cloning terminal location | 1 | 2x | 10/17 03:26 | BLOCKED: could not reach the cloning terminal |
| health enhancement not applied | 2 | 2x | 10/15 16:29 | FAIL: Aurek receives health enhancement: {"max_ham_before": 1235, "max_ham_after": 1235, "messages": ["You re-apply Aure |
| action enhancement not applied | 2 | 2x | 10/15 16:29 | FAIL: Aurek receives action enhancement: {"max_ham_before": 1035, "max_ham_after": 1035, "messages": ["You re-apply Aure |
| bot health or action below required threshold | 2 | 2x | 10/15 06:19 | BLOCKED: polearmLunge1: action below 30% or health below 50% after bounded regeneration |
| bot cannot execute unarmed lunge action | 2 | 2x | 10/15 05:00 | BLOCKED: unarmedLunge1: action below 30% or health below 50% after bounded regeneration |
| bot cannot execute melee one-handed lunge | 2 | 2x | 10/15 05:00 | BLOCKED: melee1hLunge1: action below 30% or health below 50% after bounded regeneration |
| crew buff not applied | 1 | 1x | 10/15 10:09 | FAIL: Mirren buffs the crew: {"Forn health": 200, "Forn action": 200, "Brask health": 200, "Brask action": 200, "Ressa h |
| healenhance action fails twice | 1 | 1x | 10/15 09:12 | BLOCKED: healEnhance: tester did not recover (action/health) twice running; the rest of the profession is skipped [abili |
| reviveplayer action fails twice | 1 | 1x | 10/15 09:12 | BLOCKED: revivePlayer: tester did not recover (action/health) twice running; the rest of the profession is skipped [abil |
| crafting api unavailable for session | 1 | 1x | 10/15 08:44 | BLOCKED: full crafting session/ingredient/assembly body API unavailable; no crafting success claimed |
| strafeshot1 halted by owner request | 1 | 1x | 10/15 06:25 | BLOCKED: strafeShot1: RunStopped: owner requested halt |
| strafeshot2 halted by owner request | 1 | 1x | 10/15 06:25 | BLOCKED: strafeShot2: RunStopped: owner requested halt |
| mindshot2 halted by owner request | 1 | 1x | 10/15 06:25 | BLOCKED: mindShot2: RunStopped: owner requested halt |
| headshot3 halted by owner request | 1 | 1x | 10/15 06:25 | BLOCKED: headShot3: RunStopped: owner requested halt |
| surpriseshot halted by owner request | 1 | 1x | 10/15 06:25 | BLOCKED: surpriseShot: RunStopped: owner requested halt |
| snipershot halted by owner request | 1 | 1x | 10/15 06:25 | BLOCKED: sniperShot: RunStopped: owner requested halt |
| concealshot halted by owner request | 1 | 1x | 10/15 06:25 | BLOCKED: concealShot: RunStopped: owner requested halt |
| flushingshot1 halted by owner request | 1 | 1x | 10/15 06:25 | BLOCKED: flushingShot1: RunStopped: owner requested halt |
| startleshot1 halted by owner request | 1 | 1x | 10/15 06:25 | BLOCKED: startleShot1: RunStopped: owner requested halt |
| flushingshot2 halted by owner request | 1 | 1x | 10/15 06:25 | BLOCKED: flushingShot2: RunStopped: owner requested halt |
| startleshot2 halted by owner request | 1 | 1x | 10/15 06:25 | BLOCKED: startleShot2: RunStopped: owner requested halt |
| flurryshot1 halted by owner request | 1 | 1x | 10/15 06:25 | BLOCKED: flurryShot1: RunStopped: owner requested halt |
| flurryshot2 halted by owner request | 1 | 1x | 10/15 06:25 | BLOCKED: flurryShot2: RunStopped: owner requested halt |
| curedisease halted by owner request | 1 | 1x | 10/15 06:25 | BLOCKED: cureDisease: RunStopped: owner requested halt |
| healenhance halted by owner request | 1 | 1x | 10/15 06:25 | BLOCKED: healEnhance: RunStopped: owner requested halt |
| reviveplayer halted by owner request | 1 | 1x | 10/15 06:25 | BLOCKED: revivePlayer: RunStopped: owner requested halt |
| owner halted bot healing action early | 1 | 1x | 10/15 06:25 | BLOCKED: quickHeal: RunStopped: owner requested halt |
| owner halted bot dragging incapacitated player | 1 | 1x | 10/15 06:25 | BLOCKED: dragIncapacitatedPlayer: RunStopped: owner requested halt |
| bot cannot execute polearm lunge action | 1 | 1x | 10/15 05:00 | BLOCKED: polearmLunge2: RunStopped: owner requested halt |
| bot cannot execute melee two-handed lunge | 1 | 1x | 10/15 05:00 | BLOCKED: melee2hLunge2: RunStopped: owner requested halt |
| bot cannot execute warcry action | 1 | 1x | 10/15 05:00 | BLOCKED: warcry2: RunStopped: owner requested halt |
| bot cannot execute intimidate action | 1 | 1x | 10/15 05:00 | BLOCKED: intimidate2: RunStopped: owner requested halt |
| bot cannot execute unarmed hit action | 1 | 1x | 10/15 05:00 | BLOCKED: unarmedHit1: RunStopped: owner requested halt |
| bot cannot execute unarmed stun action | 1 | 1x | 10/15 05:00 | BLOCKED: unarmedStun1: RunStopped: owner requested halt |
| bot cannot execute unarmed blind action | 1 | 1x | 10/15 05:00 | BLOCKED: unarmedBlind1: RunStopped: owner requested halt |
| bot cannot execute unarmed spin attack | 1 | 1x | 10/15 05:00 | BLOCKED: unarmedSpinAttack1: RunStopped: owner requested halt |
| bot cannot execute melee one-handed hit | 1 | 1x | 10/15 05:00 | BLOCKED: melee1hHit1: RunStopped: owner requested halt |
| bot cannot execute melee one-handed body hit | 1 | 1x | 10/15 05:00 | BLOCKED: melee1hBodyHit1: RunStopped: owner requested halt |
| bot cannot execute melee one-handed dizzy hit | 1 | 1x | 10/15 05:00 | BLOCKED: melee1hDizzyHit1: RunStopped: owner requested halt |
| bot cannot execute melee one-handed spin attack | 1 | 1x | 10/15 05:00 | BLOCKED: melee1hSpinAttack1: RunStopped: owner requested halt |
| bot cannot execute melee two-handed hit | 1 | 1x | 10/15 05:00 | BLOCKED: melee2hHit1: RunStopped: owner requested halt |
| bot cannot execute melee two-handed head hit | 1 | 1x | 10/15 05:00 | BLOCKED: melee2hHeadHit1: RunStopped: owner requested halt |
| bot cannot execute melee two-handed sweep | 1 | 1x | 10/15 05:00 | BLOCKED: melee2hSweep1: RunStopped: owner requested halt |
| bot cannot execute melee two-handed spin attack | 1 | 1x | 10/15 05:00 | BLOCKED: melee2hSpinAttack1: RunStopped: owner requested halt |
| bot cannot execute polearm hit action | 1 | 1x | 10/15 05:00 | BLOCKED: polearmHit1: RunStopped: owner requested halt |
| bot cannot execute polearm leg hit action | 1 | 1x | 10/15 05:00 | BLOCKED: polearmLegHit1: RunStopped: owner requested halt |
| bot cannot execute polearm stun action | 1 | 1x | 10/15 05:00 | BLOCKED: polearmStun1: RunStopped: owner requested halt |
| bot cannot execute polearm spin attack | 1 | 1x | 10/15 05:00 | BLOCKED: polearmSpinAttack1: RunStopped: owner requested halt |
| bot cannot execute berserk action | 1 | 1x | 10/15 05:00 | BLOCKED: berserk1: RunStopped: owner requested halt |
| bot cannot execute center of being action | 1 | 1x | 10/15 05:00 | BLOCKED: centerOfBeing: RunStopped: owner requested halt |
| bot cannot execute second berserk action | 1 | 1x | 10/15 05:00 | BLOCKED: berserk2: RunStopped: owner requested halt |
| bot cannot execute headshot action | 1 | 1x | 10/15 04:34 | BLOCKED: headShot1: action below 30% after bounded regeneration |

## server

| Gap | Notes | Seen | Last | Example |
|---|---|---|---|---|
| target lacks required buff minds for dance | 2 | 9x | 10/17 05:38 | FAIL: ?: no performance_enhance message: does Dorn have private_buff_mind and healing_dance_mind (novice entertainer onl |
| bazaar terminal not reachable locally | 3 | 9x | 10/15 08:44 | BLOCKED: no terminal_bazaar within local reachability sample |
| character gets stuck or dies repeatedly | 4 | 6x | 10/15 16:31 | FAIL: Tovan reaches the plateau: {"seconds": 57.8, "legs": null, "points": null, "cell": 0, "z": null, "error": "the ser |
| bank terminal not reachable locally | 3 | 5x | 10/15 08:37 | BLOCKED: no terminal_bank within local reachability sample |
| hospital lacks interior treatment anchor | 1 | 4x | 10/15 08:48 | BLOCKED: hospital found but no interior treatment anchor; Claude should expose building cells/medical rating. No guessed |
| character height fails to reach plateau | 1 | 3x | 10/15 16:31 | FAIL: Tovan is up on the plateau (z > 150): z 5.0 |
| characters fail to return to square area | 1 | 3x | 10/15 16:31 | FAIL: all three back in the square: [["Esk", 68.2], ["Lira", 9.1], ["Tovan", 34.0]] |
| gate target location unreachable | 3 | 3x | 10/15 16:31 | FAIL: ?: z 5.0 |
| moisture survey concentration null | 1 | 3x | 10/15 09:42 | FAIL: Besh moisture survey finds a concentration: [null, 0] |
| wind survey concentration null | 1 | 3x | 10/15 09:42 | FAIL: Besh wind survey finds a concentration: [null, 0] |
| ticket purchase between cities blocked | 1 | 3x | 10/15 08:56 | FAIL: Mos Eisley -> Bestine: buy a ticket: |
| instrument equip confirmation missing | 3 | 3x | 10/15 06:02 | BLOCKED: nalargon: instrument equip not confirmed: nalargon |
| path trip fails to arrive at destination | 1 | 2x | 10/17 05:46 | FAIL: every path trip arrives: 5 of 8 failed |
| waypoint fails to move to destination | 2 | 2x | 10/17 05:38 | FAIL: general/deliver: the waypoint moves to the destination: {"from": {"planet": "tatooine", "x": 3293.10009765625, "y" |
| share reward fails to reach bank account | 2 | 2x | 10/17 05:38 | FAIL: general/destroy: the share reaches the bank: {"reward": 383, "divisor": 3, "expected": 127, "paid": null, "bank_be |
| schematic fails to open with inventory slots | 2 | 2x | 10/17 03:17 | FAIL: generic tool: the schematic opens with its slots: null |
| mission completion flag remains false | 2 | 2x | 10/17 02:25 | FAIL: the mission completes: {"mission_removed": false, "message": null} |
| short patrol route unreachable | 1 | 2x | 10/15 16:29 | BLOCKED: short patrol unreachable; stop before further exposure. |
| health regeneration below threshold | 2 | 2x | 10/15 09:12 | BLOCKED: healState: action below 30% or health below 50% after bounded regeneration |
| poison cure recovery failed | 2 | 2x | 10/15 09:12 | BLOCKED: curePoison: action below 30% or health below 50% after bounded regeneration |
| fire extinguish recovery failed | 2 | 2x | 10/15 09:12 | BLOCKED: extinguishFire: tester did not recover (action/health) twice running; the rest of the profession is skipped |
| disease cure recovery failed | 2 | 2x | 10/15 09:12 | BLOCKED: cureDisease: tester did not recover (action/health) twice running; the rest of the profession is skipped |
| fallback restricted to mapped center | 1 | 2x | 10/15 08:56 | BLOCKED: fallback is restricted to mapped Mos Eisley centre |
| wild prey found returns null | 1 | 2x | 10/15 08:52 | FAIL: bone ordinary wild prey found: null |
| gas survey lists empty resources | 1 | 2x | 10/15 08:44 | FAIL: Besh gas survey lists resources: [] |
| organic survey lists empty resources | 1 | 2x | 10/15 08:44 | FAIL: Besh organic survey lists resources: [] |
| server roots player inside cantina | 1 | 2x | 10/15 08:11 | FAIL: Esk reaches the cantina (indoors): {"seconds": 57.8, "legs": null, "points": null, "cell": 0, "z": null, "error":  |
| regeneration does not restore health enough | 2 | 2x | 10/15 06:17 | BLOCKED: areatrack: action below 30% or health below 50% after bounded regeneration |
| pet action blocked by world state | 2 | 2x | 10/15 05:06 | BLOCKED: emboldenpets: blocked_world: pet |
| pickup action fails to hand over item | 1 | 1x | 10/17 05:38 | FAIL: general/deliver: the pickup hands something over: [] |
| bot still holds insured item after test | 1 | 1x | 10/17 03:32 | FAIL: Dova still has the insured Flared Cuff Shirt: Flared Cuff Shirt |
| lair destruction event fails to occur | 1 | 1x | 10/17 02:25 | FAIL: the lair is destroyed: |
| mission terminal blocked or rooted | 1 | 1x | 10/15 16:30 | FAIL: reach the mission terminal: [{"cell": 0, "error": "the server keeps putting us back (blocked, rooted or dead)", "o |
| hide patrol route unreachable | 1 | 1x | 10/15 16:29 | FAIL: hide patrol reached: ["{'cell': 0, 'error': 'the server keeps putting us back (blocked, rooted or dead)', 'ok': F" |
| mission area target unreachable | 1 | 1x | 10/15 16:19 | FAIL: reach the mission area: [["Cresh", 248.9], ["Ilsa", 248.9], ["Kor", 170.7]] |
| gate target location timeout | 1 | 1x | 10/15 16:19 | FAIL: ?: ["{'cell': 0, 'error': 'timeout', 'ok': False, 'reply': 'move', 'x': 3481.40234375, 'y': -47", "{'arrived': Tru |
| dax options not offered | 1 | 1x | 10/15 16:18 | FAIL: Dax offers options: null |
| meat patrol route unreachable | 1 | 1x | 10/15 16:17 | FAIL: meat patrol reached: ["{'cell': 0, 'error': 'timeout', 'ok': False, 'reply': 'move', 'x': 3481.40234375, 'y': -47" |
| health enhancement recovery failed | 1 | 1x | 10/15 09:12 | BLOCKED: healEnhance: tester did not recover (action/health) twice running; the rest of the profession is skipped |
| revive player recovery failed | 1 | 1x | 10/15 09:12 | BLOCKED: revivePlayer: tester did not recover (action/health) twice running; the rest of the profession is skipped |
| cannot return outdoors after probe | 1 | 1x | 10/15 08:44 | BLOCKED: could not return outdoors after reachability probe |
| healstate command rejected with error | 1 | 1x | 10/15 06:25 | BLOCKED: healState: command setup rejection: [{"command": "healState", "detail": 0, "error": 4, "event": "command_failed |
| curepoison produces no observable effect | 1 | 1x | 10/15 06:25 | NO_EFFECT: curePoison: verified setup; no error, message or observable result in wait |
| medicalforage lacks foraging room | 1 | 1x | 10/15 06:25 | BLOCKED: medicalForage: setup message: @skl_use:sys_forage_start; @skl_use:sys_forage_noroom |
| healing response must be near droid | 1 | 1x | 10/15 05:32 | BLOCKED: healWound: setup message: @healing_response:must_be_near_droid |
| forage system lacks room or start | 1 | 1x | 10/15 05:32 | BLOCKED: medicalForage: setup message: @skl_use:sys_forage_start; @skl_use:sys_forage_noroom |
| city zoning rights blocked by world | 1 | 1x | 10/15 05:06 | BLOCKED: grantZoningRights: blocked_world: city |
| mission terminal install blocked by world | 1 | 1x | 10/15 05:06 | BLOCKED: installMissionTerminal: blocked_world: city |
| skill trainer recruit blocked by world | 1 | 1x | 10/15 05:06 | BLOCKED: recruitSkillTrainer: blocked_world: city |
| survey command produces no observable result | 1 | 1x | 10/15 04:45 | NO_EFFECT: survey: verified setup; no error, message or observable result in wait |
| vehicle customization blocked by world state | 1 | 1x | 10/15 04:45 | BLOCKED: customizeVehicle: blocked_world: vehicle |

## scenario

| Gap | Notes | Seen | Last | Example |
|---|---|---|---|---|
| owner requested test run stop manually | 12 | 12x | 10/15 06:09 | BLOCKED: healthShot2: RunStopped: owner requested halt |
| gate test lacks specific failure reason | 3 | 8x | 10/17 05:38 | FAIL: ?: null |
| bot stops running on owner request halt | 4 | 4x | 10/15 05:00 | BLOCKED: melee2hLunge1: RunStopped: owner requested halt |
| health enhancement outcome remains unverified | 3 | 3x | 10/17 05:31 | FAIL: Jesh receives health enhancement: {"max_ham_before": 1000, "max_ham_after": 1000, "outcome": "unverified", "messag |
| action enhancement outcome remains unverified | 2 | 2x | 10/15 16:31 | FAIL: ?: {"max_ham_before": 1035, "max_ham_after": 1035, "messages": ["You re-apply Aurek's Action enhancement."], "fail |
| healing response near droid needed | 2 | 2x | 10/15 09:36 | BLOCKED: healEnhance: setup message: @healing_response:must_be_near_droid |
| healing response setup missing | 2 | 2x | 10/15 09:36 | BLOCKED: revivePlayer: setup message: @healing_response:healing_response_a4 |
| healing response outcome remains unverified | 1 | 1x | 10/17 05:38 | FAIL: ?: {"max_ham_before": 1000, "max_ham_after": 1000, "outcome": "unverified", "messages": ["@healing_response:healin |
| destroy mission waypoint missing | 1 | 1x | 10/15 09:38 | BLOCKED: no same-planet destroy mission with a known waypoint within 2300 m (offered: ['0', 'deliver', 'destroy']); no m |

## staging

| Gap | Notes | Seen | Last | Example |
|---|---|---|---|---|
| no target creature within melee range | 12 | 12x | 10/15 06:20 | BLOCKED: melee1hHit2: no live creature reachable within 3 m |
| leash stops short of target distance | 1 | 11x | 10/17 05:32 | FAIL: leash brings Nima to Dorn after he stops: 12.0 m from Dorn |
| wild prey spawn fails to appear | 2 | 9x | 10/17 05:30 | FAIL: meat ordinary wild prey found: null |
| bapaium resource units unavailable | 2 | 6x | 10/15 09:42 | BLOCKED: Besh mineral core sample of Bapaium: numeric resource units unavailable |
| target is out of leash range distance | 1 | 5x | 10/17 05:38 | FAIL: ?: 12.0 m from Dorn |
| medpack_dizzy kit item missing | 2 | 5x | 10/15 09:51 | BLOCKED: healState: missing kit item: medpack_dizzy |
| medical building staging required | 2 | 4x | 10/15 09:36 | BLOCKED: registerWithLocation: needs_staging: building:medical_or_entertainment |
| destroy mission waypoint too far | 1 | 4x | 10/15 08:52 | BLOCKED: no same-planet destroy mission with a known waypoint within 600 m; no mission accepted. |
| fresh corpses needed for coverage | 1 | 3x | 10/15 09:42 | BLOCKED: full meat/hide/bone coverage needs three separate fresh corpses |
| namaite resource units unavailable | 1 | 3x | 10/15 09:42 | BLOCKED: Besh solar core sample of Namaite: numeric resource units unavailable |
| no live creature reachable within 3 m | 3 | 3x | 10/15 05:33 | BLOCKED: applyPoison: no live creature reachable within 3 m |
| prey level unknown or too high for test | 1 | 2x | 10/17 05:30 | BLOCKED: prey level unknown or above 5; need a mapped weak-animal spawn. |
| missing medical or entertainment building | 1 | 2x | 10/15 06:02 | BLOCKED: registerWithLocation: needs_staging: building:medical_or_entertainment |
| ally health below fifty percent before affliction | 2 | 2x | 10/15 05:32 | BLOCKED: firstAid: ally below 50% health before the afflict |
| creature target staging not verified | 2 | 2x | 10/15 05:06 | BLOCKED: sampleDNA: special staging not verified: creature_target |
| corpse missing for harvest staging test | 2 | 2x | 10/15 04:45 | BLOCKED: harvestCorpse: needs_staging: corpse |
| cloning terminal missing at bound facility | 1 | 1x | 10/17 03:32 | FAIL: Dova clones at the bound facility: tatooine, posture upright, cell 0, bound building 1106500 cells [1106502] |
| cloning terminal missing within range distance | 1 | 1x | 10/17 03:27 | FAIL: Dova: a cloning terminal within 1.5 km: null |
| no resource containers found in inventory | 1 | 1x | 10/17 03:13 | BLOCKED: no resource containers with units in the inventory |
| location registration needs medical staging | 1 | 1x | 10/15 06:25 | BLOCKED: registerWithLocation: needs_staging: building:medical_or_entertainment |
| healwound needs wound affliction staging | 1 | 1x | 10/15 06:25 | BLOCKED: healWound: needs_staging: affliction:wounds |
| tendwound needs wound affliction staging | 1 | 1x | 10/15 06:25 | BLOCKED: tendWound: needs_staging: affliction:wounds |
| ally out of healing range | 1 | 1x | 10/15 05:07 | BLOCKED: rescue: ally out of healing range |
| resource point missing for staging test | 1 | 1x | 10/15 04:45 | BLOCKED: sample: needs_staging: resource_point |
