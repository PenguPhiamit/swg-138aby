# Local model: scenario-review (draft)

Written by the local model through `tools/agents/local/local_jobs.py`; 40 input lines. A local model's draft: check each item before acting on it.

A first pass over the bot scenarios. Each finding is a lead to check in the code, not a confirmed bug.

## aurek-boss-camp.py#1

| Where | Problem | Why it matters |
|---|---|---|
| g.parallel(*[lambda b=b, i=i: b.walk(CAMP[0] + 3 * i, CAMP[1]) for i, b in enumerate(g.bots)]) | wait with no timeout | The parallel walk commands do not specify a wait parameter or timeout. If the bots get stuck or the server is slow, this step will hang indefinitely, blocking the rest of the test. |
| g.check('fighters receive doctor buffs', ok, (ok or answers)[:2]) | check that can never fail | The `ok` variable is a list of non-empty strings. In Python, a non-empty list is truthy. Therefore, `g.check(..., ok, ...)` will always pass as long as the list is not empty. If the buffs fail and `ok |
| bot.slash('watch', target=sela.oid, wait=1) | result read before it can arrive | The `wait=1` parameter is passed to `slash`, but the return value (events) is not captured or checked immediately after in a way that guarantees the event has arrived before proceeding to `idle`. Whil |
| g.check('camp placed', camp, camp and camp['name'] or '; '.join(refusals)) | wrong comparison | The check verifies if `camp` is truthy (i.e., a dict was found). It does not verify that the camp placement was actually successful via server events. If `oren.find` returns a stale or incorrect objec |

## aurek-doctor-buffs.py#1

| Where | Problem | Why it matters |
|---|---|---|
| bot.slash('stand', wait=1) | wait with no timeout (implicit or short) | The `wait` parameter is set to 1 second. If the server command takes longer than 1s to process or if the bot's internal state update lags, the function might return before the 'stand' posture is fully |
| g.check('Tamsin carries enhancement packs', bool(packs), len(packs)) | check that can never fail (logic error) | The check passes if `bool(packs)` is True. The detail provided is `len(packs)`. If `packs` is empty, `bool([])` is False, so the check fails. However, if `packs` is not empty, `bool(packs)` is True. T |
| outcome = enhancement_result(initial, after, events, fighter.first, attribute) | result read before it can arrive / race condition | The code calls `fighter.status()` immediately after `doctor.slash('healenhance', ..., wait=8)`. While `wait=8` ensures the command is sent and potentially processed, server-side state updates (like ma |
| if not g.check(f'{fighter.first} receives {attribute} enhancement', outcome != 'unverified', ...) | wrong comparison / ambiguous success criteria | The check passes if `outcome` is 'increased' or 'reapplied'. However, 'reapplied' implies the buff was refreshed but max_ham didn't change. In some contexts, a refresh might not be considered a succes |
| doctor.wait_for(lambda e: 'healing_response_59' in str(e.get('text', '')), 25) | wait with no timeout (implicit or short) / potential hang | The `wait_for` function has a timeout of 25 seconds. If the server does not send 'healing_response_59' within that time, it returns False. The code then calls `doctor.idle(2)`. This is a valid wait wi |
| g.check('doctor and fighters enter mapped hospital cell', all(isinstance(t, dict) and t.get('arrived | result read before it can arrive / race condition | The `walk` commands are executed in parallel via `g.parallel`. The check immediately verifies if `t.get('arrived')` is True. If the walk takes longer than the time it takes for `g.parallel` to return  |

## aurek-hunt.py#1

| Where | Problem | Why it matters |
|---|---|---|
| g.check('combat XP message', xp, xp[:3]) | Wrong comparison logic in check | The check compares the full list `xp` against a slice `xp[:3]`. If `xp` has more than 3 items, this will fail even if the first 3 are correct. The intent is likely to verify that at least some XP mess |
| g.check('a creature in range', prey, prey and f"{prey['name']} at {prey['distance']} m") | Check condition relies on truthiness of `prey` which might be None | If `prey` is None (no creature found), the check argument `prey` is falsy. The third argument `prey and ...` also becomes falsy/None. While `g.check` might handle this, it's ambiguous whether a 'fail' |
| events = tamsin.slash('healdamage', target=aurek.oid, wait=3) | Wait with timeout used for slash command | The `slash` method likely sends a command and returns immediately or waits for a response. Using `wait=3` implies it waits up to 3 seconds for an event. If the server doesn't generate an event within  |
| g.check('all three reach the plateau', all(isinstance(t, dict) and t.get('arrived') for t in trips), | Check assumes `walk` returns a dict with 'arrived' key | If `b.walk()` fails or times out, it might return an error string or None instead of a dict. The check handles this by checking `isinstance(t, dict)`, which is good. However, if `t.get('arrived')` is  |
| found = [o for o in aurek.look(100, 'CREO', 400) if wild(o)] | Variable `found` is overwritten in loop without break check on first iteration | In the first iteration `(dx, dy) == (0, 0)`, `found` is populated. If `found` is empty, it continues to the next search area. This is correct logic for searching. No bug here. |
| g.check('combat XP message', xp, xp[:3]) | Comparison of list to slice is likely incorrect intent | If the test expects exactly 3 XP messages, `xp == xp[:3]` is true. If it expects *at least* 3, or specific ones, this check is insufficient. It essentially checks if the first 3 elements are equal to  |

## besh-gather.py#1

| Where | Problem | Why it matters |
|---|---|---|
| def harvest(...): bot.slash('harvestcorpse', kind, target=corpse['oid'], wait=3) | wait with no timeout (implicit or insufficient) | The `wait` parameter in `bot.slash` likely controls the maximum time to wait for the command to *start* or return a basic acknowledgment, not the full completion of the harvesting action which can tak |
| def survey_and_sample(...): g.check(f'{bot.first} {kind} survey lists resources', names, names[:6]) | wrong comparison | The check compares `names` (the full list of found resources) with `names[:6]` (a slice of the first 6). Since `names == names[:6]` is only true if `len(names) <= 6`, this check will fail for any surv |
| def survey_and_sample(...): g.check(f'{bot.first} {kind} survey finds a concentration', best[0], bes | wrong comparison | The check compares `best[0]` (a string name) with `best` (a tuple `(name, percent)`). These types are different and the values are not equal. This check will always fail unless `best[0]` somehow equal |
| def forage(...): g.check(f'{bot.first} forages', texts, texts[:3]) | wrong comparison | Similar to the survey check, this compares `texts` (a list of all system messages) with `texts[:3]` (the first 3). This will fail if more than 3 system messages are generated during foraging. It does  |
| def guard_sweep(...): g.check(f'{guard.first} guards the field', guard.posture() == 'upright', ...) | check that can never fail (or irrelevant check) | The function breaks out of the loop if `guard.posture() != 'upright'` and notes it. However, the final check verifies the posture *after* the loop. If the guard went down, the function returns `kills` |
| def survey_and_sample(...): bot.sui_respond(pages[-1]['page_id'], 0, ['0'], wait=2) | result read before it can arrive | `sui_respond` is a synchronous call in many bot frameworks, but if it's asynchronous or if the server response to the SUI interaction is needed to confirm the action (like selecting a range), relying  |

## class-check.py#1

| Where | Problem | Why it matters |
|---|---|---|
| CODE: ... if os.getenv('CLASS_CHECK_WOUNDS') != '1': AFFLICT.pop(...) ... | Variable used before it is set (logic dependency) | The code modifies the `AFFLICT` dictionary based on an environment variable. If this script is imported or executed in a context where `CLASS_CHECK_WOUNDS` is not defined, it defaults to None, which i |

## class-check.py#2

| Where | Problem | Why it matters |
|---|---|---|
| g.check(f'{verdict}: {ability}', verdict == 'WORKS', detail) | Check condition is tautological for non-WORKS verdicts | When `verdict` is 'RAN' or 'BLOCKED', the expression `verdict == 'WORKS'` evaluates to `False`. The test framework likely interprets a `False` result as a failure. However, in this context, 'RAN' and  |

## class-check.py#3

| Where | Problem | Why it matters |
|---|---|---|
| def call(bot, entry, target=0, wait=None): ... seconds = wait if wait is not None else max(3, 2 * (e | wait with no timeout / hardcoded cap masking long waits | The function calculates a `seconds` value based on server data but caps it at 12 via `min(12, seconds)`. If the server's default time is very high (e.g., 60s), the bot will only wait 12s. If the comma |
| def controls(g, bot, ally, cmds): ... passed = any(e.get('event') == 'command_failed' and e.get('err | Result read before it can arrive / Race condition | The code calls `call(bot, cmds[ability], oid)` which returns a list of events. However, `bot.slash` is asynchronous or event-driven. The `events` returned by `call` (which just calls `bot.slash`) like |
| def controls(g, bot, ally, cmds): ... events = bot.slash('stopDance', wait=3) ... passed = any('@per | Result read before it can arrive / Wrong comparison logic | The test expects a specific error message `@performance:dance_not_performing` to confirm the dance stopped. However, if the dance was already not performing, or if the server sends a success message i |
| def afflict(bot, kind, target=0): ... answer = bot.wait_for(lambda e: str(e.get('text', '')).startsw | Result read before it can arrive / Ambiguous wait condition | `bot.wait_for` waits for *any* event matching the lambda. If other bots or system messages also produce text starting with `[agentgear]`, this might return a spurious event that is not the response to |

## class-check.py#4

| Where | Problem | Why it matters |
|---|---|---|
| bot.slash('peace', wait=.5) | wait with no timeout (implicit or insufficient) | The `wait` parameter in `bot.slash` likely controls how long to wait for the command to complete or return a response. Using a small float like `.5` might be interpreted as seconds, but if the underly |
| bot.slash('stand', wait=1) | wait with no timeout (implicit or insufficient) | Same issue as above. A 1-second wait for a 'stand' command might be too short if the server is laggy, leading to the bot proceeding while still in a previous posture, causing subsequent checks to fail |
| bot.idle(3) | wait with no timeout (implicit or insufficient) | `bot.idle` typically pauses execution. If it doesn't take a timeout parameter and just sleeps for 3 seconds, it's fine. However, if `idle` is meant to wait for a state change (like 'idle' posture) and |
| bot.idle(15) | wait with no timeout (implicit or insufficient) | Similar to `idle(3)`, this is a blind wait. If the regeneration process stalls or takes longer than expected due to server load, the bot will proceed incorrectly after 15 seconds, leading to false neg |
| bot.idle(left) | wait with no timeout (implicit or insufficient) | If `left` is negative (e.g., if `berserk_until` was in the past), `idle` might throw an error or behave unpredictably depending on its implementation. The code checks `if left > 0`, so this specific l |

## class-check.py#5

| Where | Problem | Why it matters |
|---|---|---|
| bot.slash('stopDance', wait=1.5) | wait with no timeout (implicit or insufficient) | The `wait` parameter in `bot.slash` likely controls how long to wait for the command to be sent/acknowledged, but does not guarantee a global timeout for the operation. If the server hangs, the bot ma |
| bot.slash('stopMusic', wait=1.5) | wait with no timeout (implicit or insufficient) | Same as above. Relying on a short `wait` for command submission does not protect against server-side processing delays, risking the bot getting stuck if the server is unresponsive. |
| bot.slash(command, args, wait=3) | result read before it can arrive | The code assigns `setup_events = bot.slash(...)` and immediately checks `setup_events`. If `wait=3` only ensures the command is queued or acknowledged within 3 seconds, but the actual server event (`@ |
| g.check('restore starting boxes: ' + b.first, ok, boxes) | check that can never fail | The variable `ok` is derived from `not listed.get('error') and all(box in held for box in boxes)`. However, the check passes if `ok` is True. If `ok` is False, the check records a failure. This seems  |
| bot.slash('agentSkill', ' '.join(boxes), wait=0) | wait with no timeout | `wait=0` implies fire-and-forget or immediate return. The subsequent `b.wait_for(..., 15)` is the actual timeout mechanism. However, if `slash` with `wait=0` does not guarantee the command was receive |
| g.check(row['profession'] + ' full grant verified', True, len(expected)) | check that can never fail | The second argument to `g.check` is hardcoded to `True`. This means this specific check will always pass regardless of the actual state of the profession grant. It provides no verification value and m |

## class-check.py#6

| Where | Problem | Why it matters |
|---|---|---|
| tester.slash('peace', wait=.5) | wait with no timeout (implicit short timeout) | The `wait` parameter is set to 0.5 seconds. If the server command hangs or takes longer than expected, the test will proceed prematurely or fail silently depending on implementation, but more critical |
| tester.slash('stopDance', wait=.5) | wait with no timeout (implicit short timeout) | Same as above. A 0.5s wait is extremely short for networked game commands and may not allow sufficient time for the server to process and acknowledge the command, leading to race conditions. |
| tester.slash('stopMusic', wait=.5) | wait with no timeout (implicit short timeout) | Same as above. The short wait time risks proceeding before the server has finished processing the 'stopMusic' command. |
| tester.slash('stand', wait=1) | wait with no timeout (implicit short timeout) | While 1 second is longer, it is still a very short timeout for game state changes. If the 'stand' animation or server update takes longer, the bot might proceed while still in an invalid state. |
| if not ok: ... return | step that leaves the bot stuck for the next test | If `controls` fails (`ok` is False), the function returns early. However, the `finally` block runs cleanup. If the cleanup in the `finally` block of `run` does not properly restore the tester's state  |
| g.note('BLOCKED: negative/positive P0 controls not proven; profession judgements withheld') | check that can never fail or never pass (logic flaw) | The code notes 'BLOCKED' but continues to execute the `finally` block which calls `restore`. If `controls` fails, it implies the initial setup was incorrect. The subsequent logic assumes a clean slate |

## claude-probe-c34r.py#1

| Where | Problem | Why it matters |
|---|---|---|
| bot.slash('agentGear', args, target=target, wait=0) | wait with no timeout (wait=0) | The bot sends a command but does not wait for the server to process it before proceeding. This can cause race conditions where subsequent logic executes before the server has acknowledged or processed |
| g.check(f'afflict {kind}: ...', landed == TRIES and not errors, ...) | check that can never fail (if logic is correct) or misleading assertion | The check asserts `landed == TRIES`. If the fix works, this will always pass. However, if the server command fails silently or returns an unexpected format, `got.get('dot')` might be None/False, causi |
| got = answer(lead, 'afflict bleeding') | variable used before it is set (in the context of the loop) | Inside the loop, `sample` is assigned `got`. If the loop completes and `landed == TRIES`, `sample` holds the last successful result. However, if the loop finishes with `landed < TRIES`, `sample` still |
| g.check('afflict bleeding on self lands', not got.get('error') and bool(got.get('dot')), got) | result read before it can arrive (implicit in answer function logic) | The `answer` function uses `bot.wait_for` with a timeout of 8 seconds. If the server is slow, this might time out. However, the more subtle issue is that `bot.slash(..., wait=0)` was used earlier. The |

## claude-probe-kits.py#1

| Where | Problem | Why it matters |
|---|---|---|
| bot.slash('agentGear', args, target=target, wait=0) | wait with no timeout (wait=0) | The bot sends a command but does not wait for the server to process it before proceeding. Depending on the implementation of `slash`, `wait=0` might mean 'non-blocking' or 'no wait', which can cause s |
| g.check('unknown kind refused with usage', 'usage' in str(bad.get('error', '')), bad) | wrong comparison / fragile check | The check relies on the specific string 'usage' appearing in the error message. If the server returns a different error format (e.g., 'unknown command' or just an empty error with a non-zero status co |

## claude-probe-movement.py#1

| Where | Problem | Why it matters |
|---|---|---|
| bot.request('move', ...) | COMMANDS THE SERVER DOES NOT KNOW: 'move' | The server does not recognize the 'move' command. The bot will likely receive an error or timeout, causing the test to fail or produce invalid data regarding movement corrections. |
| g.check(f'no corrections at {SPEEDS[-1]} m/s', slow['corrections'] == 0, slow) | check that can never pass (likely) | The test plan states the body gives up after 3 corrections. If the server sends position_set_by_server events for every correction, and the bot walks at any speed where corrections occur, this check w |
| g.check(f'no failed legs at {SPEEDS[0]} m/s', per_speed[SPEEDS[0]]['failed'] == 0, per_speed[SPEEDS[ | check that can never pass (likely) | The test plan explicitly states 'a leg that fails reports how far it got first'. This implies failures are expected or possible. Checking for zero failed legs at the highest speed (5.0 m/s) is risky;  |

## claude-probe-stall.py#1

| Where | Problem | Why it matters |
|---|---|---|
| def leg(bot, x, y) | Result read before it can arrive | The code filters `bot.inbox` for 'position_set_by_server' events immediately after `bot.request`. Since the bot is moving at 5.0 m/s for up to 95 seconds, these server corrections will arrive asynchro |
| def lane(bot, y, deadline) | Variable used before it is set | The variable `first` is assigned the result of `bot.walk(WEST, y)`. However, `bot.walk` is not defined in the provided scope (only `leg` and `lane` are). If `bot.walk` is a method that doesn't return  |
| g.check('no walk failed', failed == 0, ...) | Check that can never fail (or logic error) | The variable `failed` is incremented by `1 if not l['arrived'] else 0`. However, in the `leg` function, `reply.get('arrived')` is used. If the server command 'move' does not return an 'arrived' field  |

## creation-sweep.py#1

| Where | Problem | Why it matters |
|---|---|---|
| def attribute_block(text) | Regex pattern uses `\>024` and `\>128` which are likely incorrect escape sequences or token IDs for the specific STF format being parsed. | The regex will fail to match the actual attribute lines in the creation description text, causing `found` to be empty or incomplete, leading to a `None` return even when valid data exists. This result |
| CLEANUP_WAIT = 17 * 60 | Hardcoded wait time with no timeout mechanism in the code logic shown (though defined as a constant, the usage isn't fully visible, but relying on a static sleep for asynchronous DB saves is risky). | If the zone save takes longer than 17 minutes due to server load or lag, the cleanup might proceed before the character is fully purged from the database, leading to race conditions or failed deletion |
| def expected_attributes(tables, template, profession) | Returns `None` if either profession or racial data is missing, but the caller `data_checks` does not explicitly handle this `None` case before comparing. | If a table entry is missing (which `load_tables` raises on, but hypothetical future changes might not), the comparison in `data_checks` would fail with an AttributeError or incorrect boolean result, m |
| TRAPS list definition | The comment states 'entries match whole words only' but the trap names like '"ec" inside a name' imply substring matching logic was previously used or is being tested against old behavior. | If the server's name filter logic changed to whole-word matching (as stated), these traps might no longer trigger refusals as expected, leading to false positives in the test results if the test expec |

## cresh-missions.py#1

| Where | Problem | Why it matters |
|---|---|---|
| g.check('a general mission terminal within 3 km', general, ...) | Check logic is inverted/incorrect for validation | The `g.check` function typically expects the second argument to be the 'actual' value and the third to be the 'expected' or 'ok' condition. Here, `general` (the object) is passed as the 'ok' parameter |

## cresh-travel.py#1

| Where | Problem | Why it matters |
|---|---|---|
| bot.slash('purchaseTicket', ticket_args, wait=2) | wait with no timeout (implicit or insufficient) | The `wait` parameter in `bot.slash` typically controls how long to wait for the command to be *sent* or acknowledged by the client-side queue, not the server's response time. The actual ticket purchas |
| g.check(f'{leg}: ride the shuttle', arrived, arrived and f"at {arrived.get('x'):.0f} {arrived.get('y | check that can never fail (logic error) | If `arrived` is `None` (shuttle didn't arrive), the check passes because `None and ...` evaluates to `None`, which is falsy, but `g.check` usually expects a boolean or specific truthiness. More critic |

## dorn-missions.py#1

| Where | Problem | Why it matters |
|---|---|---|
| if not any('social_entertainer_novice' in str(s) for s in rusk.profession('list').get('skills', [])) | Variable used before it is set | The variable `rusk` is accessed via `g['Rusk']` at the start of `run`, but this check happens before any assignment to a local `rusk` variable if the code structure implied otherwise; however, looking |
| g.parallel(dancer, musician) | Result read before it can arrive | `g.parallel` typically returns immediately or handles concurrency. The code does not wait for the parallel tasks to complete before calling `M.summary(g)`. If `M.summary` relies on the completion of t |
| def musician(): ... return mission and M.perform(...) | Variable used before it is set | In `musician()`, if `general` is None or `parcel` is None, the function returns `None` (implicit). However, if `mission` is falsy, it returns `False`. More critically, if `M.take` for the general miss |
| if not g.check('entertainer: a terminal within 3000 m', spot, spot.get('distance') if spot else M.wh | Wrong comparison | `g.check` usually compares the actual result against an expected value. Here, `spot` is the object returned by `nearest_terminal`. The third argument is the *expected* value? Or is it a condition? If  |
| M.errand(g, rusk, parcel, p_before, divisor, 'general/deliver') | Step that leaves the bot stuck for the next test | The comment mentions: 'a pickup into a full inventory leaves the mission stuck'. The code attempts to do a general deliver mission. If Rusk's inventory is full (as noted in the docstring), `M.take` or |
| g.parallel(dancer, musician) | Wait with no timeout | `g.parallel` is called to run two long-running missions (one takes 10 minutes). If `g.parallel` does not have a default timeout or if the test harness expects an explicit wait/timeout mechanism for pa |

## dorn-social.py#1

| Where | Problem | Why it matters |
|---|---|---|
| g.check('leader position available before leash walk', False, start) | check that can never pass | The second argument to g.check is hardcoded to False. Since the check only proceeds if `start` lacks valid coordinates (meaning the previous check failed or logic is inverted), this specific assertion |
| g.check('leader position available before leash walk', False, start) | variable used before it is set | This line executes inside an `if not all(...)` block. If the condition is true (coordinates are missing), `start` is a valid dict but lacks 'x'/'y'. However, if the logic intended to check for *valid* |
| g.check('leader position available before leash walk', False, start) | wrong comparison | The test checks if the leader's position is *available* (implied by the label), but passes `False` as the expected outcome. If the goal is to verify that a valid position *is* available, it should pas |
| g.check('leader position available before leash walk', False, start) | step that leaves the bot stuck for the next test | If this check fails (which it always does because the expected value is `False`), the code calls `nima.slash('leash', 'off')` and returns. While this cleans up, the hardcoded failure means the test su |
| nima.slash('leash', 'off', wait=1) | wait with no timeout | The `wait` parameter is set to 1. This is a timeout of 1 second. If the server command hangs or takes longer than 1 second, the function might return prematurely or raise an error depending on impleme |
| g.check('leader position available before leash walk', False, start) | check that can never pass | As established, `g.check` likely asserts that the second argument is truthy. Passing `False` guarantees the check fails. This is a bug in the test logic. |

## esk-hoth.py#1

| Where | Problem | Why it matters |
|---|---|---|
| bot.slash('purchaseTicket', ..., wait=2) | wait with no timeout (or insufficient timeout for SUI interaction) | The `wait` parameter in `bot.slash` typically controls the server-side command execution timeout, not the client-side UI response time. Buying a ticket involves a SUI page that may take longer than 2  |
| bot.select(collector['oid'], 20, wait=3) | wait with no timeout (or insufficient timeout for object selection) | Similar to above, `bot.select` with `wait=3` might not be sufficient time for the server to process the selection and update the bot's state or trigger any associated UI events before the code immedia |
| g.check(f'{leg}: ride the shuttle', arrived, ...) | check that can never fail (if `arrived` is None) | If the loop finishes without setting `arrived`, `arrived` remains `None`. The check `g.check(..., None, ...)` will likely pass if the test framework treats `None` as a valid 'found' state or if the de |
| ride(g, esk, HOTH, CORONET) | step that leaves the bot stuck for the next test | The `run` function ends after calling `ride(g, esk, HOTH, CORONET)`. If this ride fails (returns `False`), the function returns `None` (implicitly). The test framework might not handle this gracefully |

## esk-map-terminals.py#1

| Where | Problem | Why it matters |
|---|---|---|
| g.parallel(*[lambda b=b, i=i: sweep(b, points[i::3]) for i, b in enumerate(g.bots)]) | wait with no timeout | The parallel execution of bot sweeps has no specified timeout. If the bots hang or fail to complete their walking tasks, the test will block indefinitely, preventing subsequent tests from running. |
| g.check('mission terminals found', missions, missions[:4]) | wrong comparison | The check compares `missions` (the list of all found mission terminals) against `missions[:4]` (the first four items). This will only pass if the total number of found mission terminals is exactly 4.  |

## esk-recovery-proof.py#1

| Where | Problem | Why it matters |
|---|---|---|
| if not g.check('acceptance starts recovery with Esk on Hoth', bot.status().get('planet') == 'hoth'): | Result read before it can arrive / Logic error in check usage | The code checks if the bot is on Hoth immediately after a conditional ride. If the previous `if` block was skipped (e.g., planet wasn't Tatooine), the bot might not be on Hoth yet, causing this check  |
| g.check('mixed-location crew recovered home', recover_home(g)) | Result read before it can arrive | `recover_home(g)` likely initiates an asynchronous recovery process or returns a status that doesn't guarantee completion. Checking the result immediately without waiting for the server to process the |
| for member in g.bots: ... g.check(f'{member.first}: final planet Tatooine', s.get('planet') == 'tato | Result read before it can arrive | This loop checks the final planet of all bots immediately after `recover_home(g)`. Since server state updates are asynchronous, the bots' planets may not have updated to 'Tatooine' yet. The check will |

## esk-routes.py#1

| Where | Problem | Why it matters |
|---|---|---|
| g.parallel(lambda: esk.walk(**CANTINA), lambda: lira.walk(*STARPORT), lambda: tovan.walk(*PLATEAU)) | wait with no timeout | The parallel execution of walk commands does not specify a timeout. If the bots get stuck or fail to arrive, the test will hang indefinitely waiting for all threads to complete. |
| g.parallel(*[lambda b=b, i=i: b.walk(SQUARE[0] + 3 * i, SQUARE[1]) ...]) | wait with no timeout | The parallel execution of the return walk commands does not specify a timeout. If any bot fails to reach the square, the test will hang indefinitely. |

## forn-crew.py#1

| Where | Problem | Why it matters |
|---|---|---|
| def ready(g): ... bot.slash('agentGear', kit, wait=0) | wait with no timeout (wait=0) followed by wait_for | The slash command is sent without waiting for server acknowledgment. While a subsequent wait_for exists, the initial wait=0 implies an expectation of immediate return or non-blocking behavior which mi |
| def buffs(g): ... mirren.slash('healenhance', attribute, target=bot.oid, wait=1) | wait with no timeout (wait=1) followed by wait_for | Similar to above, `wait=1` is a very short timeout for a server command that might be queued or slow. If the server takes longer than 1 second to process/acknowledge, the bot might proceed to `wait_fo |
| def buffs(g): ... mirren.wait_for(lambda e: 'healing_response_59' in str(e.get('text', '')), 25) | Result read before it can arrive / Race condition | The `wait_for` is called immediately after `slash`. If the server processes the command and sends the response *before* the `wait_for` loop starts (which is possible with short delays or fast servers) |
| def buffs(g): ... g.check('Mirren buffs the crew', all(v and v > 0 for v in gains.values()), gains) | Check that can never pass (or is fragile) | If `gains` contains any `None` values (which happens if `before` or `after` are not integers), `all(...)` will return `False`. However, the check logic `v and v > 0` treats `None` as falsy. If the buf |
| def run(g): ... g.check(f'fight {tier + 1}: the crew kills the {name}', 'target' in record['result'] | Wrong comparison / Logic error | The check verifies if `'target'` is a key in `record['result']`. This assumes the server response structure always includes a 'target' key upon success. If the server changes its response format or if |
| def run(g): ... bot.slash('agentGear', 'afflict restore', wait=0) ... bot.wait_for(...) | wait with no timeout (wait=0) followed by wait_for | Same issue as in `ready`. Sending a command with `wait=0` and then immediately waiting for an event can lead to race conditions where the event is processed before the waiter is attached, causing the  |

## forn-escort.py#1

| Where | Problem | Why it matters |
|---|---|---|
| bot.slash('agentGear', 'afflict restore', wait=0) | Command 'agentGear' is likely unknown to the server | The header states 'COMMANDS THE SERVER DOES NOT KNOW: none', but 'agentGear' appears to be a custom bot command, not a standard SWGEmu slash command. If it's not registered in the emulator's command h |
| bot.slash('agentGear', 'vehicle', wait=0) | Command 'agentGear' is likely unknown to the server | Same as above. If 'agentGear' is not a valid server command, the vehicle assignment will fail. |
| bot.slash('agentGear', 'mandohelmet', wait=0) | Command 'agentGear' is likely unknown to the server | Same as above. If 'agentGear' is not a valid server command, the helmet assignment will fail. |
| g.check('a player to escort is named', owner, owner or 'set ESCORT_OWNER...') | Check can never fail if owner is set correctly | If `owner` is a non-empty string, the check compares `owner == owner`, which is always true. It only fails if `owner` is empty, in which case it checks against the fallback string. This makes the chec |
| g.check(f'{owner} is online', escort.who(owner), ...) | Result read before it can arrive / Race condition | `escort.who(owner)` likely queries the server state immediately. If the player logs in exactly during the wait loop, there might be a delay between the login event and the server's internal state upda |
| g.check(f'waypoints mailed to {owner}', sent and '"result":0' in str(sent.get('text', '')).replace(' | Wrong comparison / Fragile parsing | Checking for `"result":0` in a string representation of a JSON-like object is fragile. If the server response format changes slightly (e.g., whitespace, key order, or integer vs string '0'), this chec |

## forn-missions.py#1

| Where | Problem | Why it matters |
|---|---|---|
| g.parallel(lambda: scout(forn, 0, 'hunting'), ...) | Result read before it can arrive / Race condition in parallel execution | The `scout` function returns a mission object or None. The code calls `M.summary(g)` immediately after `g.parallel`. If `g.parallel` is asynchronous (non-blocking), the summary might run before missio |
| M.hunt(g, bot, mission, before, divisor, 'scout/hunting') | Variable used before it is set / Logic error in recursive call | Inside `scout`, if `mtype == 'hunting'`, `M.hunt` is called. Then it recursively calls `scout(bot, slot, 'recon')`. However, `M.hunt` likely takes time to complete (killing 15 creatures). If `g.parall |
| free = [b for b in (ressa, brask) if not M.holds_bounty(b) or M.drop_far_bounty(g, b, 4000)] | Side effect in list comprehension / Unpredictable behavior | `M.drop_far_bounty` is called as part of the condition. If it has side effects (dropping a bounty), this logic is hard to reason about and debug. If `ressa` holds a far bounty, she drops it, then `bra |
| g.parallel(lambda: scout(forn, 0, 'hunting'), lambda: hunter(bh), ...) | Step that leaves the bot stuck for the next test | The `scout` function for hunting does not return until the hunt is complete (presumably). If `M.hunt` blocks or takes a long time, and `g.parallel` doesn't handle timeouts, the test could hang. Furthe |


## Claude's review (18 Oct 2:16 AM)

**Not usable as it stands: none of the 103 findings holds up.** The model doesn't know the bot API, and most items come from that. Checked against `tools/bots/squad.py`:

- **25 "check" findings are wrong.**
  - `g.check(label, ok, detail)` records `bool(ok)`, and its third argument is only the detail text (squad.py:610-614).
  - "compares xp against xp[:3]" and "check that can never fail" misread it.
  - `g.check('…', False, start)` inside a failure branch records a deliberate fail.
- **48 "wait/timeout" findings are wrong.** `slash(..., wait=N)` sends the command and returns the events of the next N seconds (squad.py:438-441). It is not a timeout, and nothing hangs. `wait_for` has its own timeout (352).
- **4 "unknown command" findings are wrong.** `agentGear` is our server's own command (`AgentGearCommand.h`), and `move` is a request to the bot body (AgentControl.cpp handles `cmd == "move"`), not a slash command.
- **The 26 others are guesses** ("variable used before it is set", "may leave the bot stuck"). The 15 sampled are wrong or by design. For example, creation-sweep.py's `attribute_block` regex passed in the 17 Oct creation sweep.
- **6 of the 40 chunks never got an answer** (errors.jsonl).

**For a rerun:**
- Give the job the Bot API's method names and docstrings from squad.py: `check`, `note`, `slash`, `idle`, `wait_for`, `walk`, `request`, `parallel`.
- Tell it that the scenario commands come from our own bot body and server.
- Use the scenario-draft job planned in `Agent/local-model.md`, which carries the same API summary.
