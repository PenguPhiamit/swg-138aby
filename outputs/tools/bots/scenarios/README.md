# Bot squad scenarios

Five groups of three bots play on the **test galaxy**. Each group has a focus (see `../groups.json`), and its leader carries the group's name: Aurek, Besh, Cresh, Dorn, Esk. A scenario is a short Python file that one group runs. `../squad.py` runs any number of them at once and writes the results.

## Running (from Codex, one command for all five groups)

```
wsl -d Debian -u swgemu -- python3 /mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/tools/bots/squad.py status
wsl -d Debian -u swgemu -- python3 /mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/tools/bots/squad.py run aurek-hunt.py besh-survey.py cresh-travel.py dorn-social.py esk-routes.py
```

Run it from this folder, or give full paths. `run` prints one short block per scenario: PASS/FAIL lines, notes, any error, and the report path. **Read that summary, not the JSON.** Open a report (`outputs/Bot-reports/<Group>/…json`) only when a failure needs its steps and events. Each group's `outputs/Bot-reports/<Group>/LOG.md` gets one line per run, so you or Claude can see what every group has done.

If a bot is offline, run `squad.py setup` (or `setup Aurek`). It logs everyone in, creates missing characters, leaves the tutorial room and regroups. It's safe to repeat. If the test galaxy itself is down, `squad.py galaxy` prints the two root commands that restart it. A restart restores the newest backup, so run `setup` again afterwards.

## Writing a scenario

```python
"""What this checks, in one or two lines."""
GROUP = 'Aurek'            # the group that runs it (or run any file with --group NAME)

def run(g):
    aurek, jesh, tamsin = g['Aurek'], g['Jesh'], g['Tamsin']   # bots by first name; g.leader, g.bots
    aurek.walk(3830, -4520)                                      # navmesh walk (repeats long routes)
    prey = aurek.find('', radius=100, type='CREO', where=lambda o: o['name'].startswith('@mob/creature_names:'))
    if not g.check('a creature in range', prey, prey and prey['name']):
        return
    result = aurek.fight(prey['oid'], 90)
    g.check('it goes down', 'target' in str(result.get('result')), result)
    g.note('anything worth reading later')
```

**Bot methods.** Each returns the body's reply dict unless noted. The full protocol is in `Core3-dev/MMOCoreORB/src/client/agent/AgentControl.cpp`.

| Method | Use |
|---|---|
| `status()` | planet, x, y, z, cell, `me.ham`/`max_ham`/`posture`/`states`, `self` (oid) |
| `look(radius, type, limit)` → list | nearby objects: oid, name, type (`CREO` creatures/NPCs/players, `TANO` items/terminals, `BUIO` buildings), x, y, z, distance, posture, health_pct |
| `find(name, radius, type, where)` → object or None | nearest whose name contains `name` (any case) |
| `locate(text, radius=800, x=None, y=None)` → list | the **server's** object search (`/agentpath find`), up to 30 nearest whose template, name key or shown name contains `text` (one word, 3+ letters), anywhere in range, **inside buildings too**: those come with `cell`, `local` {x,y,z} and `building`. E.g. `locate('terminal_mission', 1500)`, `locate('hospital', 2000)` |
| `tell(name, text)` | a private message to a character by first name; the receiver gets a `tell` event |
| `walk(x, y, z=None, cell=None)` | navmesh route, indoors with `cell` (cell-local x/y/z) |
| `move(...)` | one move, at most 95 s |
| `go(obj)` | walk to a `look`/`find` object |
| `fight(oid, timeout)` | attack until `result` = "target dead/incapacitated", "we are …" or timeout |
| `slash(name, args='', target=0, wait=2)` → events | any slash command; returns what arrived within `wait` s |
| `say(text)` | spatial chat |
| `talk(oid)` / `choose(index)` → events | NPC conversation; look for `conversation_options`, `npc_says` |
| `radial(oid)` | right-click menu: `items` with `radial_id`, `name`, `label` |
| `select(oid, radial_id)` → events | pick a menu item (20 = use) |
| `sui_pages()` / `sui_respond(page_id, event, args)` | pop-up windows |
| `inventory()` | `items`: oid, name, type |
| `inspect(oid)` | details of one object |
| `gear(kit)` | test-galaxy kit via `/agentgear`: `basic` (combat groups), `boss` (world-boss fighters), `support` (doctor packs, camp kits, instrument). Skipped if already worn |
| `missions()` / `mission_list(terminal)` / `accept_mission(mission, terminal)` | mission terminals: each mission has type, title, reward, difficulty, start/end/waypoint, target, container (mission bag = offered, datapad = accepted) |
| `recover()` | wait out incapacitation, clone if dead (every run does this first) |
| `request(cmd, within, **args)` | any other body command, raw (`within` = seconds to wait for the reply) |
| `wait_for(text_or_fn, timeout)` → event or None | first event since the last command that matches |
| `messages()` → list | system-message texts since the last command |
| `idle(seconds)` → events | wait, then return everything since the last command |

**Group.** `g.check(label, ok, detail)` records PASS/FAIL. `g.note(text)` records a note. `g.parallel(f1, f2, …)` runs bot actions at the same time; give each job its own bot. Don't let two jobs drive the same bot.

## Test-galaxy helpers (never on live)

`Core3.AgentGear = true` (the test galaxy sets it; `squad.py galaxy` prints the restart command) turns on two server helpers for bot accounts:
- **`/agentgear basic|boss|support`** gives gear.
- **`/agentskill <box> …`** grants skill boxes and their prerequisites. `groups.json` `training` lists what each member gets; `setup` applies it.

Aurek is the world-boss crew. Aurek and Jesh are the fighters, trained so their boss weapons are certified. Tamsin is the Doctor, Sela the entertainer and Oren the Ranger: the support camp. **Training at real trainers is a separate test.** Use a fresh character without `training` for it.

`../places.json` holds terminal positions that bots mapped (`esk-map-terminals.py`). Scenarios read it to find mission terminals and banks. City objects come from the world snapshot, so walking is the only way to map them.

## Getting the most from limited usage

- **Batch.** Put several checks in one scenario and run all five groups in one `run` call. Each extra tool call costs more than a longer scenario.
- **Read summaries only.** Never cat a report or the bot logs unless a FAIL needs it, and then read only its `steps` and that bot's `events`.
- **Edit, don't rewrite.** Change the failing lines of a scenario and run that one scenario again.
- **Name new files `<group>-<topic>.py`**, e.g. `aurek-loot.py`, so reports group by topic.
- **Write facts.** Only PASS/FAIL and notes count. If something can't be tested because the body lacks a feature, write `g.note('BLOCKED: …')` and move on. Claude adds body features from those notes.

## Regression gate (Claude, 15 October)

`tools/bots/gate.py` answers one question after every test-galaxy start: does everything that passed before still pass? It checks the server (running, initialized, dev commit, archive), logs in any missing bot, runs one 10-minute round of `Agent/squad-plan.txt` without fallbacks, and compares each check with its own history. A check that passed before and fails now, and never failed before, is a **regression** and fails the gate. Flaky, fixed, new and still-failing checks are listed but don't fail it. The verdict is in `Bot-reports/GATE.md`. The 30-minute cycle starts it once per server start (`gate.py due`, then `gate.py start`), so after a restart, read `GATE.md` before anything else. **Keep check labels stable:** the history is keyed by group, scenario and label, so renaming a check starts a new history.

## Class check (C33, 15 October)

`class-check.py` grants a test bot one whole profession at a time (`Bot.profession`), tries each of that profession's abilities once and records which ones the server accepts. Plan: `Claude-class-check/test-plan.md`; results: `Documentation-support/class-check-results.md`. It always runs the P0 control first (a cleared bot must be refused `unarmedHit1` and `healDamage` with error 2; `stopDance` must still answer), then one profession per run:

```
CLASS_CHECK_PHASE=P1 CLASS_CHECK_PROFESSIONS=combat_marksman \
  python3 squad.py run scenarios/class-check.py --group Aurek --rounds 1 --round-minutes 30 --no-fallback
```

`CLASS_CHECK_PHASE=P0` (default) runs only the controls. `CLASS_CHECK_TESTER` names the group member (default: the member who started as that profession, else the leader); `CLASS_CHECK_MINUTES` caps the slice (default and maximum 23). Verdicts: WORKS, RAN, NOT_GRANTED (error 2 after a verified grant, a FAIL), NO_EFFECT (a FAIL), BLOCKED (a note, never a FAIL). A BLOCKED result carries `gate_passed` when the command was sent and no error 2 came back: the server checks the ability first, so the profession holds it. Per-profession JSON goes to `Bot-reports/<Group>/class-check-<profession>.json`; at the end the tester is cleared and every member's starting boxes (`groups.json` training) are granted again. Attacks need live wildlife: the scenario walks to the sevorrt plateau and uses only passive animals (dwarf eopie, worrt, rill, eopie); the server's `locate` cannot see live spawns. Offline tests: `python -I tools/bots/test_class_check.py`.

## Fallback scheduling (C16, 14 October)

Repeated `squad.py run` rounds now use `../fallback-plan.json`. After two consecutive all-PASS rounds, or the same FAIL/BLOCKED/ERROR twice, the group switches to the next available fallback. Empty-check scenarios count as blocked. Round timeouts count as repeated blockage; an owner halt never starts fallback work. The main scenario is retried after three fallback rounds or when its contents change. State is kept in `Bot-reports/runs/fallback-state.json`, independently per group.

Assignments and reasons are recorded in each JSON report and group LOG; `Bot-reports/fallback-coverage.md` receives links to actual runs. `--no-fallback` explicitly repeats only the requested scenarios. `--round-minutes 10` is the default per-round budget; `--minutes` still bounds the whole run. Outstanding body commands must return before cancellation completes.

New fallback probes sample safe local navigation, terminal/trainer approach and menus, and stationary creature counts. Existing group-specific travel, gathering, harvest, doctor and social scenarios provide regression work. Full crafting is explicitly blocked pending body support. The movement probes require Tatooine and the local grid/reach/travel probes require mapped Mos Eisley centre; they never wander Hoth spawns. A stationary census is allowed elsewhere. This is a first bounded coverage set, not proof that every route, port or profession has been tested; see the coverage document for gaps.

Both travel scenarios now select a newly received `msgSelected` collector list, ignoring pre-existing pages and purchase confirmations. Boarding and profession runtime acceptance remain pending; offline chooser/ticket/runner tests pass.

### Remaining body gaps

Secure trade, the crafting session (schematic list, ingredient slots, assembly, experimentation) and mounting vehicles aren't supported yet. Missions are decoded (13 Oct) but untested end to end. No mission terminal has been found in central Mos Eisley yet. Talking out of range gives no failure event. Tell and other features may have gaps of their own; record them as BLOCKED notes.
