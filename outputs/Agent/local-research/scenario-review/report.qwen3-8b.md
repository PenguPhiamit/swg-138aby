# Local model: scenario-review (draft)

Written by the local model through `tools/agents/local/local_jobs.py`; 40 input lines. A local model's draft: check each item before acting on it.

A first pass over the bot scenarios. Each finding is a lead to check in the code, not a confirmed bug.

## aurek-boss-camp.py#1

| Where | Problem | Why it matters |
|---|---|---|
| def text_of(events): | Potential infinite loop in string slicing | The slice [:220] may not capture the full message if it exceeds 220 characters, leading to incomplete information. |
| def run(g): | Potential infinite loop in camp placement | The loop runs for 4 steps, but if the camp is never placed, it may not retry enough times or handle refusals properly. |
| if g.check('camp placed', camp, camp and camp['name'] or '; '.join(refusals)) | Incorrect use of logical operators | The expression camp and camp['name'] or ... may not evaluate as intended, leading to potential incorrect results. |
| for bot in fighters: bot.idle(25) ... bot.slash('stopwatching', wait=1) | Potential for bot to be stuck | If the 'stopwatching' command fails or takes too long, the bot may be left in an idle state without proper handling. |
| def wild(o): ... prey = next(iter([o for o in aurek.look(120, 'CREO', 400) if wild(o)]), None) | Potential for no prey to be found | If no creature meets the 'wild' criteria, the 'prey' variable will be None, leading to a failed check and no fight. |
| g.parallel(*[lambda b=b: b.fight(prey['oid'], 90) for b in fighters]) | No timeout for fight results | The fight may take longer than expected, and without a timeout, the test could hang indefinitely. |

## aurek-doctor-buffs.py#1

| Where | Problem | Why it matters |
|---|---|---|
| doctor.slash('healenhance', attribute, target=before['self'], wait=8) | Command 'healenhance' is misspelled | The server does not recognize the command 'healenhance' (likely a typo for 'healEnhance'), leading to potential command failures or unhandled errors. |
| if not g.check('doctor and fighters enter mapped hospital cell', all(isinstance(t, dict) and t.get(' | The check may fail due to incorrect trip status | The condition checks if all trips are dictionaries with 'arrived' key, but the actual trip status may not be in this format, leading to a false negative. |
| if not g.check('Tamsin carries enhancement packs', bool(packs), len(packs)): | The check may fail due to incorrect logic | The check uses 'bool(packs)' as the expected value, but the actual expected value is 'len(packs)', which could be zero or more, leading to a potential false negative. |
| if not g.check(f'{fighter.first} {attribute} buff prerequisites', ready(healer) and ready(before) an | The check may fail due to incorrect expected value | The expected value is a dictionary, but the actual check is against a boolean condition, leading to a potential false negative. |
| if not isinstance(initial, (int, float)): | The variable 'initial' may not be set before use | The variable 'initial' is used in the 'enhancement_result' function, but it is only set if 'before' has 'max_ham' and 'attribute', which may not be guaranteed. |
| if not doctor.wait_for(lambda e: 'healing_response_59' in str(e.get('text', '')), 25): | The wait may not be sufficient or the condition may not be met | The wait time of 25 seconds may not be enough for the server to respond, or the condition may not be met if the server does not emit the expected event. |

## aurek-hunt.py#1

| Where | Problem | Why it matters |
|---|---|---|
| g.check('a creature in range', prey, prey and f"{prey['name']} at {prey['distance']} m") | wrong comparison | The check is using a boolean expression as the second argument, which is incorrect. The second argument should be the expected value, not a condition. |

## besh-crafting.py#1

| Where | Problem | Why it matters |
|---|---|---|
| craft(g, bot, tool, schematic, label, experiment=None) | The 'craft_add' command may not be correctly handled by the server | The server may not respond as expected to the 'craft_add' command, leading to incorrect filling of slots and potential failure in the crafting process. |

## besh-death-insurance.py#1

| Where | Problem | Why it matters |
|---|---|---|
| def clone_at_bind(g, bot, terminal, other, planet): | The check for 'here.get('cell')' may not correctly determine if the bot is inside a cell | The 'here.get('cell')' check assumes that the bot's status contains 'cell' information, but if the bot is not in a cell (e.g., outdoors), this check will fail, leading to incorrect logic for determini |

## besh-fallback-crafting.py#1

| Where | Problem | Why it matters |
|---|---|---|
| CODE: """Observe inventory, explicitly report unsupported crafting sessions.""" | Missing actual test logic | The code comment describes the purpose but does not contain any actual test steps or commands to execute. |

## besh-gather.py#1

| Where | Problem | Why it matters |
|---|---|---|
| def survey_and_sample(g, bot, kind): | Potential infinite loop in survey_and_sample if no resources are found | The loop runs for names[:5], but if no resources are found, the code may not handle the case where names is empty, leading to an unexpected behavior. |

## besh-harvest.py#1

| Where | Problem | Why it matters |
|---|---|---|
| resources(reply, kind) | Potential KeyError for 'name' key in dictionary | The code assumes that 'name' is always present in the dictionary, but if it's missing, it will raise a KeyError. |
| resources(reply, kind) | Potential KeyError for 'oid' key in dictionary | The code assumes that 'oid' is always present in the dictionary, but if it's missing, it will raise a KeyError. |
| resources(reply, kind) | Potential KeyError for 'items' key in dictionary | The code assumes that 'items' is always present in the dictionary, but if it's missing, it will raise a KeyError. |
| resources(reply, kind) | Potential KeyError for 'get' method in dictionary | The code uses 'i.get('name', '')' which is safe, but the code may not handle cases where 'i' is not a dictionary. |
| resources(reply, kind) | Potential KeyError for 'lower()' method on string | The code uses 'str(i.get('name', '')).lower()' which is safe, but the code may not handle cases where 'i.get('name', '')' is not a string. |
| resources(reply, kind) | Potential KeyError for 'split(':') method on string | The code uses 'str(o.get('name', '')).split(':')[-1] in PREY' which is safe, but the code may not handle cases where 'o.get('name', '')' is not a string. |

## besh-missions.py#1

| Where | Problem | Why it matters |
|---|---|---|
| def run(g): | Potential infinite loop or blocking behavior | The code does not include any timeout or condition to break out of the loop if the server does not respond, which could cause the bot to hang indefinitely. |

## class-check.py#1

| Where | Problem | Why it matters |
|---|---|---|
| def classify(...): | The function 'classify' is incomplete and cuts off mid-definition | The code provided ends abruptly in the middle of the 'classify' function definition, making it impossible to determine its full behavior or correctness. |

## class-check.py#2

| Where | Problem | Why it matters |
|---|---|---|
| drops = [pool for pool, old in (before.get('ham') or {}).items() | wrong comparison | The code uses 'old - (after.get('ham') or {}).get(pool, old) >= 3' which is incorrect; it should be checking if the difference is >= 3, but the expression is not properly structured. |

## class-check.py#3

| Where | Problem | Why it matters |
|---|---|---|
| objects = [o for o in seen if alive(o) and not crowded(o) and not contested(o)] | The condition 'not crowded(o)' and 'not contested(o)' may not correctly filter objects based on proximity to others and rivals. | The logic for determining if an object is crowded or contested may not account for all possible scenarios, leading to incorrect filtering of objects. |

## class-check.py#4

| Where | Problem | Why it matters |
|---|---|---|
| class-check.py#4 | The code contains a string formatting operation with a percentage sign, which is not valid in Python 3. Use .format() or f-strings instead. | The use of % for string formatting is deprecated in Python 3 and will raise a syntax error. |

## class-check.py#5

| Where | Problem | Why it matters |
|---|---|---|
| if instrument: ... | Potential infinite loop in repositioning logic | If the bot keeps failing to see the ally due to line of sight issues and repositioned reaches the length of LOS_OFFSETS, the loop will continue indefinitely unless the condition is properly handled. |

## class-check.py#6

| Where | Problem | Why it matters |
|---|---|---|
| incomplete (full inventory?): %s; weapons already carried are used' | Potential incorrect string formatting | The format string uses %s but the arguments may not match the expected types, leading to unexpected output or errors. |

## claude-probe-c34r.py#1

| Where | Problem | Why it matters |
|---|---|---|
| run(g) | The check for 'afflict bleeding on self lands' may never pass | The check assumes that the 'afflict bleeding' command on self will always land, but the server may return an error or no DOT, depending on the game state and mechanics. |

## claude-probe-kits.py#1

| Where | Problem | Why it matters |
|---|---|---|
| g.check('profession list has abilities', ...) | The check condition is always true | The condition checks if 'abilities' is a list and has length > 0, but the actual result may not meet this condition, making the check unreliable. |

## claude-probe-movement.py#1

| Where | Problem | Why it matters |
|---|---|---|
| def leg(bot, x, y, speed): | The 'reply' variable is used before it is set | The 'reply' variable is assigned after the 'fixes' list is created, but 'fixes' is used before 'reply' is defined, which could lead to errors or incorrect data. |

## claude-probe-pathwalk.py#1

| Where | Problem | Why it matters |
|---|---|---|
| def trip(bot, label, x, y, z=None, cell=None): | The 'reply' variable is not properly initialized in the loop | The 'reply' variable is assigned inside the loop, but the initial value is not set, which could lead to unexpected behavior if the loop does not execute. |

## claude-probe-stall.py#1

| Where | Problem | Why it matters |
|---|---|---|
| def lane(bot, y, deadline): | Potential infinite loop if time.time() never reaches deadline | The while loop runs until time.time() < deadline, but if the deadline is not met, it could cause an infinite loop. |
| g.check('no walk failed', failed == 0, {'legs': legs, 'failed': failed}) | Check may always fail if the test is designed to have failed legs | The check 'no walk failed' assumes that no legs should fail, but the test scenario may intentionally include failed legs. |
| def run(g): | Bot may be blocked if not on Tatooine | The test skips bots not on Tatooine, but this could lead to incomplete results if all bots are blocked. |
| def movement_lines(offset): | Reading from console.log may not capture all movement lines | The code reads from a specific offset, which may miss lines if the log file is rotated or not fully read. |
| def leg(bot, x, y): | Potential division by zero if start or end coordinates are not set | The calculation of 'walked' uses start and end coordinates, which may not be set if the bot's status is incomplete. |
| def run(g): | No timeout for the parallel execution of lane functions | The parallel execution of lane functions may hang indefinitely if one of the bots is unresponsive. |

## creation-sweep.py#1

| Where | Problem | Why it matters |
|---|---|---|
| def data_checks(tables): | Incomplete check for Hutt's description text | The code checks the Hutt's racial row and limits but does not verify that the description text matches S7's text (C54 F3), which is part of the required data checks. |

## creation-sweep.py#2

| Where | Problem | Why it matters |
|---|---|---|
| prose = text.split('ATTRIBUTES', 1)[0].strip() | result read before it can arrive | The code splits the text on 'ATTRIBUTES' before the server has had a chance to process the full response, which may not be available yet. |

## creation-sweep.py#3

| Where | Problem | Why it matters |
|---|---|---|
| newest = ', '.join(f'COALESCE((SELECT UNIX_TIMESTAMP(max(t.creation_date)) FROM {table} t WHERE t.ac | Potential SQL injection vulnerability | The code directly interpolates the GALAXY variable into the SQL query without proper sanitization, which could allow an attacker to inject malicious SQL code. |

## creation-sweep.py#4

| Where | Problem | Why it matters |
|---|---|---|
| sql_rows(f'SELECT firstname FROM characters WHERE galaxy_id = {GALAXY} AND account_id = {int(free[0] | SQL injection vulnerability | The code directly interpolates user input into the SQL query, which can lead to SQL injection attacks. |

## cresh-fallback-travel.py#1

| Where | Problem | Why it matters |
|---|---|---|
| CODE: """Mapped Mos Eisley/Bestine round trip, restricted starting location.""" | Missing test logic | The code snippet only contains a comment and imports, but no actual test steps or assertions to validate the bot's behavior. |

## cresh-missions.py#1

| Where | Problem | Why it matters |
|---|---|---|
| g.check('Cresh reaches the general terminal', M.arrived(trips[0]), ...) | The check may never pass | The check is for 'Cresh reaches the general terminal', but the condition is based on M.arrived(trips[0]), which is not directly tied to Cresh's status. This could lead to incorrect pass/fail outcomes. |

## cresh-travel.py#1

| Where | Problem | Why it matters |
|---|---|---|
| def ride(g, bot, origin, destination): | The 'purchaseTicket' command may not be recognized by the server. | The server may not know the 'purchaseTicket' command, which could cause the bot to fail to buy a ticket. |
| def ride(g, bot, origin, destination): | The 'select' command may not be recognized by the server. | The server may not know the 'select' command, which could cause the bot to fail to interact with the ticket collector. |
| def ride(g, bot, origin, destination): | The 'sui_respond' command may not be recognized by the server. | The server may not know the 'sui_respond' command, which could cause the bot to fail to respond to the ticket page. |
| def ride(g, bot, origin, destination): | The 'go' command may not be recognized by the server. | The server may not know the 'go' command, which could cause the bot to fail to move to the travel terminal or ticket collector. |
| def ride(g, bot, origin, destination): | The 'talk' command may not be recognized by the server. | The server may not know the 'talk' command, which could cause the bot to fail to interact with the NPC. |
| def ride(g, bot, origin, destination): | The 'request' command may not be recognized by the server. | The server may not know the 'request' command, which could cause the bot to fail to request the mission list. |

## dorn-missions.py#1

| Where | Problem | Why it matters |
|---|---|---|
| def take(bot, trip, mtype): | Potential infinite loop or stuck if mission is not found | The function returns None, None if the check fails, but there's no mechanism to retry or handle failure gracefully, which could leave the bot stuck. |

## dorn-social.py#1

| Where | Problem | Why it matters |
|---|---|---|
| g.parallel(*[lambda b=b, i=i: b.walk(SQUARE[0] + 2 * i, SQUARE[1]) for i, b in enumerate(g.bots)]) | Potential race condition or incorrect parallel walk logic | The parallel walk may not be properly synchronized, leading to unpredictable bot movement. |
| g.check('spatial chat heard by both', all(heard), [h and h.get('text') for h in heard]) | Incorrect comparison in check | The check uses 'all(heard)' which is always True if 'heard' is a list, but the actual condition is whether the chat was heard. |
| g.check('tell arrives', tell and 'with me' in str(tell.get('text')), tell or sent) | Incorrect check logic | The check condition is not properly structured to verify if the 'tell' message contains 'with me'. |
| if not all(isinstance(start.get(k), (int, float)) for k in ('x', 'y')): | Unnecessary check for leader position | The check is redundant and may not be necessary for the test logic. |
| if not isinstance(end, dict) or not end.get('ok', True) or not end.get('arrived') or not all(...): | Incorrect handling of walk result | The condition is too broad and may incorrectly reject valid walk results. |
| g.check('leash brings Nima to Dorn after he stops', gap < 10 or (capped and gap < 20), ...) | Ambiguous condition | The condition is unclear and may not accurately reflect the intended behavior of the leash. |

## esk-fallback-census.py#1

| Where | Problem | Why it matters |
|---|---|---|
| CODE: """Visible creature/NPC census; no movement, combat or staff commands.""" | Missing command description | The comment is incomplete and does not clearly describe the purpose or expected behavior of the scenario. |

## esk-fallback-grid.py#1

| Where | Problem | Why it matters |
|---|---|---|
| from fallback_scenarios import grid as run | Incorrect import statement | The import statement incorrectly assigns the imported module to 'run', which may lead to confusion or incorrect usage of the grid scenario. |

## esk-fallback-reach.py#1

| Where | Problem | Why it matters |
|---|---|---|
| CODE: """Bounded terminal/trainer approach and radial-menu checks.""" | Missing documentation or explanation | The comment is vague and does not provide useful information about the purpose of the code. |

## esk-hoth.py#1

| Where | Problem | Why it matters |
|---|---|---|
| def ride(g, bot, origin, destination): | The check for 'at the terminal (8 m to buy)' uses gap <= 8, but the code calculates gap as the distance between the bot's position and the terminal's local position, which may not be accurate if the t | The calculation of gap does not account for the cell difference, which can lead to incorrect distance measurements and false negatives in the check. |

## esk-map-terminals.py#1

| Where | Problem | Why it matters |
|---|---|---|
| g.check('mission terminals found', missions, missions[:4]) | wrong comparison | The second argument to g.check is expected to be the expected result, but missions is used as both the actual and expected values, which is incorrect. |

## esk-recover-home.py#1

| Where | Problem | Why it matters |
|---|---|---|
| run(g) | Missing test logic | The function 'run(g)' calls 'recover_home(g)' but does not include any test assertions or checks to validate the outcome of the recovery process. |

## esk-recovery-proof.py#1

| Where | Problem | Why it matters |
|---|---|---|
| g.check('mixed-location crew recovered home', recover_home(g)) | The check is dependent on a function that may not be defined or available | The function 'recover_home(g)' is called without ensuring it is defined or imported, which could lead to an error or incorrect check result. |

## esk-routes.py#1

| Where | Problem | Why it matters |
|---|---|---|
| g.parallel(lambda: esk.walk(**CANTINA), lambda: lira.walk(*STARPORT), lambda: tovan.walk(*PLATEAU)) | The server does not know the 'walk' command | The 'walk' command is not recognized by the server, leading to potential errors or no movement. |

## forn-crew.py#1

| Where | Problem | Why it matters |
|---|---|---|
| def ready(g): | Potential infinite loop or blocking in parallel execution | The use of g.parallel with lambda functions that may not complete or have side effects could lead to blocking or unexpected behavior if not properly synchronized. |

## forn-escort.py#1

| Where | Problem | Why it matters |
|---|---|---|
| import importlib.util | Unused import | The 'importlib.util' module is imported but not used in the code. |
| import json | Unused import | The 'json' module is imported but not used in the code. |
| import os | Unused import | The 'os' module is imported but not used in the code. |
| import escort | Unused import | The 'escort' module is imported but not used in the code. |
| g.check('a player to escort is named', owner, owner or 'set ESCORT_OWNER or escort_owner in groups.j | Potential incorrect check | The check may not be reliable if the 'owner' variable is not properly set or if the server response is not as expected. |
| g.check(f'{owner} is online', escort.who(owner), f'waited {wait:.0f} minutes') | Potential incorrect check | The 'escort.who(owner)' function may not return a reliable result, leading to incorrect pass/fail status. |

## forn-missions.py#1

| Where | Problem | Why it matters |
|---|---|---|
| def scout(bot, slot, mtype): | Potential infinite loop or blocking behavior | The function uses M.take and M.hunt/M.recon which may not return properly if the mission is not completed, leading to potential blocking or infinite loop if the bot is not able to complete the mission |

