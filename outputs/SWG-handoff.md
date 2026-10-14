# SWG handoff board

Shared between ChatGPT and Claude. Rules are in `../AGENTS.md`. Newest log entries first.

## Server lock

**Server lock: Claude: test galaxy bots and dev tree `/opt/swg/Core3-dev` (ChatGPT is out of usage until 09:39, owner 06:26; its C20 Esk proof is now Claude's; Fable never writes to /opt/swg). Live galaxy STOPPED (owner request, 13 Oct 16:52). The overnight check runs every 30 minutes (owner turned it on). — 2026-10-14 06:27**

(Write `Server lock: Claude — <task> — <time>` or `Server lock: ChatGPT — …` before touching `/opt/swg`; set it back to `free` afterwards.)

## Questions for the owner

Agents add a question here when the owner isn't in their chat: name, time, the options. The owner answers inline. Messages between the agents go in `Agent/to-claude.md` and `Agent/to-chatgpt.md` (AGENTS.md, "Asking questions").

**Claude, 14 Oct 04:59 (owner stepped away; answer inline when back):**
1. **Overnight allow rule (needed before the next overnight run):** Run now once and choose "Always allow" for `overnight_cycle.sh`, or add `"Bash(bash /c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/tools/agents/overnight_cycle.sh)"` to `permissions.allow` in `outputs/.claude/settings.local.json`.
   - Also deny or close the 03:01 overnight run that is still waiting on a prompt.
   - Consider removing the broad `Bash(cat >> *)` rule in that file.
2. **Hoth loot drops:** 3% common decor (ordinary), 5% rare decor (sergeants and named beasts), 2% vehicle deed (named beasts). Keep these rates? The 18 deeds include non-Hoth vehicles (Anakin's podracer, Sith speeder, Mustafar panning droid): keep them, or trim to Hoth-fitting ones?
3. **Fable's planet:** answered 05:38: **Ossus**. Fable's asset plan (05:54) is in `Fable-planet-test/ossus-assets/README.md`: stock art covers a first playable Ossus at $0. Its section 5 lists 6 owner decisions (second-pass CC0 downloads, a $14 pack that needs the author's written OK, the Blender add-on validation F86, a DDS tool install, stock creature bodies, MTG's Mustafar temple ruins). Its other questions (README section 6) are still open.
4. **Clean-room pilot (F93):** collections or buffs first?
5. **Discord (C17):** set up a webhook whenever you're ready; nothing gets posted before your go.
6. **Fable's backport (applied to dev; revert if you disagree):** (a) Keep the real SOE paths for 1,073 MTG objects that MTG's import had mangled (applied), or go back to MTG's? (b) Wire NGE junk and collection loot into loot groups, or keep it staff-only? (c) Extend the 13 new wearables to new species when they land? (d) Is it worth cracking the disc's TRE v6 format (patch 18+ and the expansion patches), or is 2006 content enough? (e) Keep the Death Troopers prison-guard pants?


Shared proposal reference: [SWG-feature-register.md](SWG-feature-register.md) — purpose, design maturity and difficulty for all recorded features/candidates.

## Task board

| Task (from SWG-roadmap.md) | Owner | Status | Notes |
|---|---|---|---|
| Creature Handler top-tier build research (owner, 14 Oct) | ChatGPT | bounded pass complete — no game benchmarks | `Documentation-support/creature-handler-top-tier-plan.md`; owner wants all three modes; local build closure verified, improvements proposed |
| Tames discussion (owner, 14 Oct) | Owner + Claude + ChatGPT | open — discussion requested | Note in `Agent/to-claude.md`, 05:49; eligibility, rare/endgame pets, wild vs BE, control budget; no changes approved |
| Whole-server asset/data discovery sources (owner, 14 Oct) | ChatGPT | initial registry saved | `Documentation-support/server-wide-asset-source-registry.md`; supplied Sketchfab/CGTrader, SWAPI, Comlink; individual asset audits pending |
| Farming asset downloads (owner, 14 Oct) | ChatGPT | queued — owner authorized download batch | `Documentation-support/farming-asset-download-queue.md`: 30 source entries, ordered batches; licence/readme/hash audit; no downloads yet, no timer |
| Darksaber / Ghostfire opalescent trail feasibility (owner, 14 Oct) | ChatGPT | bounded pass complete — rendering untested | `Documentation-support/darksaber-ghostfire-feasibility.md`; creator-original Darksaber candidate, CC0 VFX, local shader probe; rights/notification and rendering gates |
| Farming art gap follow-up (owner, 14 Oct) | ChatGPT | bounded pass complete — research only | `Documentation-support/farming-unbranded-art-gap-fill.md`; 17 functional slots with open sources; shell/specialized processing/stage work remains; no downloads |
| Farming art sources (owner, 14 Oct) | ChatGPT | bounded pass complete — research only | `Documentation-support/farming-open-art-shortlist.md`; 5 Star Wars candidates (rights/provenance gates), 9 CC0 fallback packs; no downloads |
| Farming system reference research (owner, 14 Oct) | ChatGPT | bounded pass complete — research only | `Documentation-support/farming-system-UM-feasibility.md`; Minecraft MIT shortlist, ARK/Skyrim source/rights and proposed SWG planter; no downloads/imports |
| Phase 1 in-game checks | Owner (you) | open | Needs a human in the client |
| Bot B0: core3client logs into the galaxy | unclaimed | ready | Phase 6; needs the galaxy running (or a rehearsal copy) |
| Review/build/test staged Kael interaction upgrade | Claude | built + tested on test galaxy — dev `e1344def`; **not promoted** (needs cross-review + owner OK) | Inventory, radial, SUI read/reply, deed→vehicle device and call PASS; mount, mission list untested. ChatGPT's 6 MCP wrappers still staged, not live |
| **Phase 1 via bots** (plan in roadmap Phase 1) | Claude | in progress — fight/death/clone ✅, navmesh paths ✅, survey/sample ✅, fresh test bot ✅, group invite/join ✅ (test galaxy) | Dev `3797430a` + `cde59ec5`. Next: loot (humanoid), travel, trade, crafting |
| World-boss normal-damage credit test and source record | Claude | open — before deployment | C4 found no additional blocking world-boss code defect; verify exactly 25,000 bank credits from a real player hit, record Flurry's pinned adapted-source revision in central credits |
| Phase 1 expected outcomes per check | ChatGPT | open — see C5 | `Agent/notes/phase1-expectations.md` |
| The Beginning quest with the new body | ChatGPT | blocked on promotion | Han now answers (fixed height); Chewbacca silent on test galaxy |
| Phase 1 runner `tools/bots/phase1.py` | ChatGPT | open — see C3 below | No lock needed to write it |
| Real-client checks with Universal Modder `um win` | ChatGPT (Codex + Universal Modder) | open — see C2; needs the owner at the PC | Two clients: window/pointer; later JTL |
| SWG file-format and cut-content source inventory (research only) | Claude (v1), ChatGPT (finish later) | **v1 done 13 Oct (Claude)** — formats mapped to the Core3 readers, Hoth recommended as the first UM job, cut-content candidates; open: archive.org copies and licences, add-on `skt`/`ans`, dormant-object audit | `Documentation-support/swg-format-inventory.md` |
| Claude: review original-asset workflow and give opinion | unclaimed | open — owner requested Claude's opinion | Please respond in `Documentation-support/asset-workflow-review-for-Claude-2026-10-13.md`: RTX 5070 compatibility, local model choice, SWG conversion, first prop and optional fal fallback |
| Research Universal Modder for Claude | ChatGPT | paused — owner requested task check, then wait for confirmation | Source inspection partly complete; checkpoint in 14:53 log. Final Claude brief not yet written; no CLI generation or UI control run |
| **Follow assist `/leash` (server-side, temporary fix for client `/follow`)** | Claude | built + tested on test galaxy — dev `09a56205`; **not live** (C4c changes requested, 14 Oct; owner deploy OK still needed) | Right-click a group member → "Leash (follow assist)", or `/leash <name>` / `/leash off`. Untested: real client with `/follow`, private buildings, mounts |
| **C4c: review `/leash` + test helpers (`09a56205`, `220e0f39`, `f25c90f9`)** | ChatGPT | complete — changes requested, 14 Oct | Combined C4b/C4c report: 3 P1 + 4 P2; includes live-isolation gap, leash races/fallback/menu, correlation and mission cache |
| **C4d: re-review the fixes (`5aadc8b9`)** | ChatGPT | complete — changes requested, 13 Oct; 2 P1 + 1 P2 remain | `Documentation-support/review-C4d/C4d-review.md`; five original findings resolved, two partial; new cancelled-tick race |
| **C6: real-client leash test (after the live deploy)** | ChatGPT (Codex + Universal Modder) | blocked on live deploy; needs the owner at the PC | See C6 below |
| Mercenary companions (recruiter NPC + follow/assist AI) | Claude | live; combat-assist probe inconclusive | Broker Dax Venn at 3552 -4782 Tatooine; two-companion hire/follow/dismiss verified; target died too quickly to establish individual damage |
| Agent body v0.2: HAM, combat log, SUI pop-ups, indoor movement | unclaimed | open | Needed for real combat and terminals |
| World boss rotation (Flurry-inspired, existing creatures) | Claude | built + tested on test galaxy; **awaiting owner OK to deploy** | Dev `bda2c0dd`; credit reward still untested (needs Kael to land a hit) |
| Investigate repeated gone events for R5-D9 | unclaimed | open — low-severity bug candidate | Same oid repeatedly removed from view during movement; no movement failure. `Agent/reports/2026-10-13.md` |
| Fix missing out-of-range conversation failure feedback | unclaimed | open — still reproduces with new body | Server returns TOOFAR without a CommandQueueRemove the body can see; needs server-side look |
| Investigate mercenary survival across rapid relog | unclaimed | open — bug/guide discrepancy reported | Same Naty ID survived 6-second reconnect and continued following; full delayed logout untested; explicit dismissal works |
| Export pending research PDF snapshot | unclaimed | deferred — owner stopped session to move to Codex | Export saved documents only; no further cut-content research or downloads; no new PDF exported in this session |
| **Hoth: first new planet (Phase 3, main track since 13 Oct 22:35)** | Claude | **v1 on the test galaxy: travel both ways passes (Esk, 21/21, 14 Oct)**; `local_planets.tre` in the owner's client for **test sessions only** (owner OK 14 Oct); **first real-client try crashed loading Hoth (14 Oct 02:31): the client never loaded the MTG archives (their lines sit under `[Station]` in `swgemu_live.cfg`); test launcher fixed, owner to retry**; outpost bowl has a 43 m north wall: owner looks first; creature levels: **keep Bellum's endgame** (owner 14 Oct); next: creatures, caves |
| **C12: Hoth adaptation table** | ChatGPT · GPT-6.1 Sol, **Medium** | **plan complete — 228 source files inventoried; target/API and runtime checks open** | `Documentation-support/hoth/hoth-adaptation-table.md`; original instructions archived |
| **C13: server SOPs: build, maintain, debug (owner request)** | ChatGPT · GPT-6.1 Sol, **Medium** (research budget) | **complete — 9 runbooks, 10 ranked gaps; procedures unexecuted** | `Documentation-support/SWG-server-SOPs.md`; original instructions archived |
| **C14: planet lore + galaxy coordinates (Wookieepedia, Legends)** | ChatGPT · GPT-6.1 Sol, **Medium** (research budget) | **bounded pass complete — 24 records; source-access and pixel-fit gaps recorded**; Hoth first | `Documentation-support/planets-lore-and-coordinates.md` + JSON; original instructions archived |
| Flurry world-boss rotation port | unclaimed | open | Phase 2 |
| **C8: MCP wrappers for the new body commands** | ChatGPT | **implemented; offline checks pass; Claude game validation pending** (13 Oct) · GPT-6.1 Sol, **Medium** | `tools/agent/mcp_server.py`; validation in `Documentation-support/C8-C10-validation.md`; Claude tests on test |
| **C9: fix the open squad scenarios** | ChatGPT | **revised; compiled + offline fixtures pass; Claude game validation pending** · GPT-6.1 Sol, **Medium** | cresh-missions (2 km target), aurek-doctor-buffs (needs the hospital), besh-harvest (no prey, deaths); see C9 |
| **C10: bot mapping + whole-server test coverage plan** | ChatGPT | **plan complete — Hoth mapping + 125 coverage rows; unexecuted** · GPT-6.1 Sol, **Medium** (research budget applies) | Owner: "the bot module needs to be able to map new areas and be able to test the whole server eventually"; `Documentation-support/bot-mapping-and-coverage-plan.md` |
| **C11: archive downloads** | ChatGPT (records), Claude (fetch from WSL) · GPT-6.1 Sol, **Low** | section A + D1 fetched; local pin/hash audit complete; A4 partial terms/A6 hold; rest deferred | List and rules: `Documentation-support/archive-download-plan.md` |
| **C4e: re-review the C4d fixes + find/tell + Hoth v1** | ChatGPT | **review complete — changes requested (1 P1 + 1 P2), 14 Oct** — dev `5b2a858f`, `421adb15`, `9ac7cdcd` · GPT-6.1 Sol, **High** | `Documentation-support/review-C4e/README.md` (what to check; patches + full files); queue id `c4e-review` |
| TortoiseBots release + prior WoW knowledge brief | ChatGPT | complete — recovered update/lag history + pinned source brief | Owner requested source plus recovered prior work for Claude; design reference only |
| Hoth atlas-to-client map calibration | ChatGPT | complete — numerical fit rejected; client unchanged | Offline stock UI anchors and C14 grids; no client edits |
| Offline squad report triage | ChatGPT | implemented; offline fixtures pass; saved reports summarized | Original local report reader inspired by TortoiseBots principles; no service or bot control |
| **C15: open-licence textures, materials, sounds** (owner, 14 Oct) | ChatGPT | complete — 10 CC0 candidates; no downloads or conversion | Research only, no downloads. Builds on F85 (Quaternius, Kenney, Poly Haven). See C15 below |
| **C16: bot fallback work** (owner, 14 Oct) | ChatGPT | initial implementation + 15 offline tests pass; Claude runtime acceptance requested; wider coverage open | When a scenario is done or stuck, the group moves on to travel, navmesh mapping, reachability and more. See C16 below |
| **C17: Discord channel for the project** (owner, 14 Oct) | ChatGPT | offline implementation complete — 22 tests pass; Discord delivery untested, awaiting owner setup + go | Layout, posting tool with dry run; the owner creates the server/webhook and says go. See C17 below |
| **C18: cross-review Fable's backport batches 1-2** (applied to dev `0c44d431`, `5c7ae017`) | ChatGPT | review complete — 30-object source/data sample, no new P1/P2 established; gameplay pending | Read-only; `outputs/Fable-backport/` has the diffs and checks |
| **C20: C16b bot recovery and Dorn failed-move handling** | ChatGPT · GPT-6.1 Sol, **Medium** | claimed — 14 Oct; runtime waits for exclusive Esk driver gap | Recovery home from Hoth/Corellia, guard Dorn position errors; Esk-only runtime proof |
| **C19: C4f review of Claude's 14 Oct dev commits and archive tooling** | ChatGPT | review complete — two P2 findings, changes requested, 14 Oct 06:12 | `Documentation-support/review-C4f/C4f-review.md`; isolated checks pass; gameplay gates remain |
| **C21: quantify server resources, Legends coverage and implementation possibilities** (owner, 14 Oct) | ChatGPT · GPT-6.1 Sol, **Medium** | queued **AFTER Claude's existing queue: C19 → C20 → C18**; resumable across usage resets | `Documentation-support/server-resource-and-implementation-census.md`; staged inventory, Wookieepedia comparison, rights/feasibility/gap matrix; no imports or implementation implied |

| Encounter options and Legacy-era direction | ChatGPT | recorded and shared; exact year open | Owner14Oct: retain recoverable server encounters; NJO–Legacy, post-Vong/post-Abeloth, Krayt Empire |

| Owner observes stationary bots; solo consumables advice | ChatGPT | inspected saved reports; live status blocked by WSL sandbox; Claude asked | Test squads are scripted, not continuous ambient AI; current activity unverified |

| Pre-CU player macro bots: applicability to test squads | ChatGPT | research complete; implementation untested | Documentation-support/pre-cu-macro-bots-and-squad-routines.md; historical target-follow confirmed, no coordinate moveTo verified |

| Coronet travel UI: Hoth absent, Rori/Lok dropdown | ChatGPT triage; Claude runtime diagnosis requested | owner report recorded; not independently reproduced | Agent/reports/2026-10-14-travel-ui.md; stock route filtering vs Hoth client registration |

| Bot stopping, activity status and Hoth assertions | ChatGPT | implemented; 5 offline tests pass; game checks pending | Documentation-support/bot-control-update-20261014.md; no bot control or server edits |

| Historical removed flamethrower identification | ChatGPT | checkpoint saved; exact identity unresolved | Documentation-support/removed-flamethrower-identification.md; owner recalls victim knockdown loop around CU, ~25m sale |

| Historical bulk inventory removals (including NGE) | ChatGPT | checkpoint complete; identification unresolved | Storyteller confiscation survivor account found (uncorroborated); official credit purge/quest cleanup distinguished; lava flea clue saved |

| Storyteller confiscation: weapon identity and independent accounts | ChatGPT | bounded pass complete; exact model unresolved | Unnamed Storyteller lightsaber in confiscation account; separate equipment-access recollections, no independent purge confirmation |

| Storyteller weapon file inventory | ChatGPT | local inventory complete; historical mapping unresolved | Documentation-support/storyteller/README.md + client-inventory.json;76TRE/690paths/1592versions, no explicit Storyteller weapon marker |

| Authentic historical weapon identification and local candidates | ChatGPT | bounded follow-up saved; historical identity open | Prophecy + recalled admin [name removed]; corrected exact forum handle [name removed]. Public Vision of Hope predecessor lead; no reliable account/item match. Documentation-support/storyteller/prophecy-alias-follow-up.md |

| Prophecy / Vision of Hope archive recovery and closure reasons | ChatGPT | claimed — UM archive research, bounded pass | Owner requested Wayback/UM recovery of forum history, including [name removed] lead, and sourced shutdown explanations. Public pages only |

## Instructions for ChatGPT's open tasks (owner's split, 13 Oct)

Completed-task instructions and older logs: [SWG-handoff-archive.md](SWG-handoff-archive.md).

Work split rules are in `../AGENTS.md` ("Work split"). Claude holds the server lock: don't edit `/opt/swg`, and don't connect Kael while Claude is testing. Claim each task on the board first, and add a log entry when you stop.

**C1. SWG file-format and cut-content source inventory (v1 by Claude, 13 Oct; see the file's "Still to do" list).** Use the Universal Modder skill `game-research-websearch`. Write `Documentation-support/swg-format-inventory.md` covering every SWG client format: TRE archives and the IFF family (msh, mgn, skt, lmg, ans, sht, cdf, sat, apt, lod, flr, pob, trn, ws, snapshot, stf, datatable). For each format give what it holds, how well it's documented, existing tools (SIE, TRE explorers, Blender add-ons, Bellum Gero tools), links with archive.org copies, and licences. End with the formats our plan needs first: static prop (msh + sht + dds + apt), then wearables (mgn + skt). Don't download game files and don't touch leaked builds (Ethics check). Record uncertainty.

**C2. Real-client checks with Universal Modder `um win` (only when the owner says they're at the PC).** Run `um win setup` after telling the owner what it downloads. The owner logs in to two clients; never type their password. With `um win shot` / `drive`, check both windows: size, moving, pointer/cursor behaviour, and both characters seeing each other. Save screenshots (`--scale 0.33`) and notes in `Agent/reports/`, and tick the matching Phase 1 row in the roadmap. Later (separate session): JTL launch, fly, land and relog, and watching a bot walk a navmesh path once `/agentpath` is live.

**C3. Phase 1 runner `tools/bots/phase1.py` (no lock needed to write it).** Python, outside `/opt/swg`. It drives a body over its JSON protocol, the same lines `tools/agent/agentd.py` sends. Commands are in `Core3-dev/MMOCoreORB/src/client/agent/AgentControl.cpp` (read-only): status, look, inspect, move/path/height, fight, talk/choose, radial_menu/select_radial, sui_pages/sui_respond, inventory, command. Write one function per Phase 1 check in the roadmap table, with a JSON report to `outputs/Bot-reports/`. Look NPCs up by name each run: spawned NPC IDs change at every server start. Claude runs it on the test galaxy while holding the lock. A working multi-bot harness is now at `tools/bots/bot.py` (`init` / `start [--create race profession]` / `send '<json>' wait` / `stop`, one FIFO-driven body per bot, test galaxy only): build the runner on it.

**C4. Cross-review the dev commits (read-only, no lock needed).** The patches are exported to `Documentation-support/review-C4/` (0001–0005 = `e1344def`, `a72026b6`, `eebdd99d`, `5c39f411`, `697f2002`; plus `world-boss/` = `bda2c0dd`). Its README lists what to check and where the server reference files are. Reading `/opt/swg/Core3-dev` is fine for this; editing it is not. `eebdd99d`/`5c39f411` are server changes (`/agentpath`, only for accounts in `Core3.AgentAccounts`). Record "reviewed by ChatGPT" and any findings in the log.

**C5. Phase 1 expected outcomes.** For each check in the roadmap's Phase 1 table, write what pre-CU should do (messages, items, costs, timings) from `Agent/knowledge-sources.md` into `Agent/notes/phase1-expectations.md`. The runner (C3) asserts against it.

**C6. Real-client leash test (after the leash is live; owner at the PC).** Two clients, grouped, God Mode off on both. Alt right-clicks the main → "Leash (follow assist)", then `/follow`. Main walks around a building corner and into a cantina. Record whether the alt keeps up, how often "Leash: you were stuck…" appears, and anything that looks like rubber-banding. Screenshots with `um win shot` as in C2. Then "Stop leash" from the same menu.

**C9. Fix the open squad scenarios (Medium).** In `tools/bots/scenarios/` (keep the README's Bot API; LF line endings):
- `cresh-missions.py`: the accepted mission's target was 2 km away and the walk timed out. Pick the destroy mission with the nearest waypoint, skip any over about 600 m, and give the walk enough tries.
- `aurek-doctor-buffs.py`: buffs need a medical centre. `bot.locate('hospital', radius=2000)` finds the Mos Eisley hospital building; `bot.locate('<word>', ...)` returns objects inside buildings with `cell` and `local`, so walk in with `walk(local x, y, z, cell)`.
- `besh-harvest.py`: no prey was found, and bots died.

Put the files on their group lines in `Agent/squad-plan.txt`. Claude runs them and reports in `Bot-reports`.

**C11. Archive downloads (owner-authorized; section A + D1 fetched and locally audited; remaining sections deferred).** Follow `Documentation-support/archive-download-plan.md` exactly: section A, then B and C as the plan describes. Records go in `Content-catalogue/archive-downloads.json`. Nothing gets executed or installed; no sign-ins.

**C7. Bot squads (owner request, 13 Oct; the owner is napping, so this is the long passive job).**

- **Model and effort:**
  - Use **GPT-6.1 Sol** (`gpt-6.1-sol`).
  - **High** for C4b/C4c (code review).
  - **Medium** for squad work: writing and fixing scenarios, reading summaries.
  - Don't use Astra, Max or Ultra. They cost far more, and `squad.py` already runs the groups in parallel.
  - GPT-5.5 leaves Codex on 14 Oct.
- **Order:**
  1. C4b + C4c (read-only reviews; they unblock the live deploy).
  2. Then squads: start a long background run right away, and improve scenarios while it runs.
- **The squads.** Five groups on the test galaxy, each leader named after the group:
  - **Aurek:** the world-boss crew (5).
    - Fighters Aurek and Jesh: boss gear, trained to certify it.
    - Support camp: Tamsin (Doctor), Sela (entertainer), Oren (Ranger).
    - Starter: `aurek-boss-camp.py`. Next: a real boss trip from Rhea's list.
  - **Besh:** gatherers with a guard (Varo). The routines in `besh-gather.py` are the "macros" for each gathering type.
  - **Cresh:** travel and missions. `cresh-missions.py` is ready, waiting for a mapped mission terminal (`places.json`).
  - **Dorn:** social and group.
  - **Esk:** navigation.

  Focus, members and `training` are in `tools/bots/groups.json`. Gear and training come from test-galaxy-only helpers (README → "Test-galaxy helpers"). Combat groups use `gear('basic')` and the boss crew uses `gear('boss')` / `gear('support')`. The scenario API and usage tips are in `tools/bots/scenarios/README.md`; read it once.
- **Commands** (prefix `wsl -d Debian -u swgemu -- python3 /mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/tools/bots/squad.py`, working directory `…/tools/bots/scenarios`):
  - `status`: who is online and where.
  - `setup`: log in / create / group; safe to repeat.
  - `run aurek-hunt.py besh-gather.py cresh-travel.py dorn-social.py esk-routes.py`: one round, prints the summary.
  - `run <same files> --minutes 120 --detach`: a background run. It repeats rounds, re-logs dropped bots and tidies files. Results are in `Bot-reports/runs/`.
  - `last`: the newest summary (rewritten after every round; cheap to read).
  - `halt`: stop after the current round.
- **Usage budget:**
  - Spend it on testing, but keep about **15–20 %** for the write-up.
  - Recording is cheap: `squad.py` writes every report and each group's `LOG.md` line itself.
  - Your record is one board log entry: summarize `squad.py last`, plus any BLOCKED notes with the feature the body lacks.
  - If you can't see your remaining usage, add a short log entry after each hour of work so nothing is lost.
- **Each round:**
  1. Read only the summary.
  2. Fix or extend one or two scenarios toward that group's focus. Each group's LOG.md says what it has covered.
  3. Run again.

  New files are `<group>-<topic>.py`. Ideas per group:
  - Aurek: loot a humanoid; medic heals.
  - Besh: train scout skills at a trainer (conversation), then forage and harvest. The starting scout lacks both (BLOCKED notes say so).
  - Cresh: Bestine and back; starport to another planet.
  - Mission terminals: none found outdoors in a 700 × 600 m map of Mos Eisley (Esk, 13 Oct; only banks, travel terminal, ticket collectors, character builder). Next: look inside buildings (starport, cantina, guild halls) with `look` from inside a cell.
  - `/purchaseTicket` sometimes gets no answer at all: 2 of 4 tries on 13 Oct, same spot and same arguments. Find out why: check the server log for the command around that time, and try waiting next to the terminal first.
  - Dorn: mercenary hire and dismiss; entertainer buffs.
  - Esk: other buildings and cities; routes that fail.
- **Rules:**
  - Test galaxy only; the live galaxy is stopped.
  - Don't edit `/opt/swg`, `squad.py` or `groups.json` without noting it in the log.
  - Missing body features (trade, crafting session, tells, mounts, mission-list decoding) are `g.note('BLOCKED: …')` notes, not failures. Claude builds them from those notes.

**C4d. Re-review the fixes (read-only).** `Documentation-support/review-C4d/` holds `5aadc8b9.patch` (one LF commit, 125 lines) and full files. Check each of your seven C4b/C4c findings: resolved, partly resolved, or not, with file:line. Write `review-C4d/C4d-review.md` and add a log line. Not exercised on the test galaxy yet:
- a planet change mid-leash;
- disconnected terrain;
- the mission cache after zoning.

**C15. Open-licence textures, materials and sounds (owner, 14 Oct: "find open source/public/or free use shader/textures/etc we can use").** Research only: read web pages, download nothing. For each source give the URL, the exact licence (version and link, checked on the creator's own page), required attribution, whether modification and redistribution inside a game archive are allowed, asset types, format and fit for pre-CU SWG (sci-fi, snow/Hoth, desert, jungle, industrial). Prefer CC0/public domain; list CC-BY separately; flag CC-BY-SA share-alike; exclude non-commercial, no-redistribution, personal-use-only, ripped or unclear-origin packs; flag AI-generated packs with unclear provenance. Shaders: SWG uses its own `.sht` shader templates and effects, so free GLSL/HLSL code doesn't carry over; say which maps SWG can use (diffuse, normal, specular/gloss, emissive, environment; `swg-format-inventory.md`) and how PBR sets convert to DDS. Start from `KOTOR-to-SWG-and-open-assets-feasibility.md` (F85), `CREDITS-and-sources.txt` and the `Content-catalogue/` audits. Output: `Documentation-support/open-assets-catalogue.md` + `.json`, top-10 for Hoth and sci-fi props first.

**C16. Bot fallback work (owner, 14 Oct: "when bots finish or fail loops and they cant be completed to find something else the bots can test, travel, navmesh mapping, etc").** Goal: no idle or looping squads. (1) **Switch rule** in `squad.py` (or a small chooser it calls): a group leaves its scenario when it has PASSed all its checks for the last 2 rounds, or when the same FAIL/BLOCKED/ERROR reason repeats 2 rounds in a row. It then takes the next fallback the group can do. Write the reason and the new task in the report and in `Bot-reports/<Group>/LOG.md`, and go back to the main scenario after a set number of rounds or when its file changes. (2) **Fallback list** (one scenario each, observation first, safe on the test galaxy): travel (every shuttleport and starport route on the loaded planets: ticket, boarding, arrival point, round trip; reuse `cresh-travel.py`/`esk-routes.py`, and use only the newest ticket list, see the 03:30 `ride()` note); navmesh mapping (walk grids around cities, outposts and POIs; record unreachable points, stuck spots, falls and server height against the client; output like `tools/hoth/hoth_terrain_scan.py`); reachability (can a bot reach and open each trainer, mission, bazaar, bank and travel terminal; reuse `esk-map-terminals.py`); spawn census (creature and NPC names seen along fixed routes per area; later `/spawnStatus` and `/showSpawnRegion` once dev `34d4772a` is on the test galaxy, staff only); survey, harvest and crafting loops; doctor and entertainer buffs; and a slow regression pass that re-runs old PASS scenarios to catch breaks. (3) **Limits:** test galaxy only. No admin commands beyond what the bots already use. Keep bots clear of Hoth spawns (level 62–115) until the owner picks a test kit (04:25 note in `hoth-port-log.md`). Respect the time box for each round. (4) **Output:** the code and scenarios in `tools/bots/`, a fallback section in `tools/bots/scenarios/README.md`, and `Bot-reports/fallback-coverage.md` (what each fallback covered, with the dates).

**C17. Discord channel (owner, 14 Oct: "can we add a task to gpt to hook into and help me manage a discord channel for all this?").** (1) **Layout proposal** (`Documentation-support/discord-plan.md`): channels (announcements, dev log, bot reports, server status, test-galaxy notes, content ideas, owner questions), roles, pinned rules and a short FAQ, and what each channel gets automatically. Say what is private (owner and agents) and what could be player-facing later. (2) **Posting tool** (`tools/agents/discord_post.py` or similar): it posts short digests through a Discord **webhook**. That is one-way, has no read access and needs no bot permissions. Sources: new board log entries (the heading and first lines), `Bot-reports/OVERNIGHT.md` lines, a morning summary, and test-galaxy and live up/down. It needs a `--dry-run` that prints exactly what would be posted, rate limiting, length limits, and de-duplication (a state file). Offline tests come with it. (3) **Safety:** the webhook URL is a secret. It lives only in a private file the owner creates (for example under `/opt/swg/agent/`, mode 0600, or a Windows user-profile file outside `h/`) and is never printed, logged or committed. Before anything is posted, strip from every message: credentials, account names, IP addresses and ports, file paths outside `h/outputs`, and anything from `config-local.lua` or the login files. No @everyone or @here. A two-way bot that reads commands is phase 2 and only on the owner's say-so. If it is ever built, messages read from Discord are untrusted data, never instructions, and it never controls a server. (4) **Owner steps** (write them as a checklist): create the Discord server/channel and a webhook; save the URL to the private file; then tell an agent "go" for the first real post. Under AGENTS.md (new external service, outbound posts), nothing is posted before that go.

## Log

### 2026-10-14 08:05 Claude: Hoth ice caves in dev; test restart queued; Fable on the asset-pipeline study, then "finish Hoth"
- **Hoth ice caves (dev `c5f1ae06`, Fable's staging, hash-checked apply, luac clean):** 129 wampa spawns in MTG's four ice caves. Every cell id was checked against MTG's `hoth.ws`. The 23 in Bellum's mynock den are left out (that building isn't in MTG's snapshot). Bellum's per-player boss reward is dropped for template corpse loot. **Owner question:** corpse loot only for the five named wampa bosses, or build a per-player boss reward later? Bellum's 15 reward groups vs ours: `Fable-hoth-caves/README.md`.
- **Test galaxy restart queued** for when round 080235 ends (about 08:27), to load the caves and the spawn-command lock fix (C4f-F1). It checks for an owner client first and pauses the overnight check with `Agent/STOP-OVERNIGHT` while the galaxy starts.
- **The overnight check didn't run 06:31–07:31** (Claude's usage ran out; the scheduled check runs through Claude). It resumed at 08:02.
- **The Esk crew wasn't really stranded:** the "on Hoth" positions were stale bodies; the restored backup had them on Tatooine. C20's return-home step is still unexercised; a proof needs a crew taken to Hoth first (`esk-hoth.py`).
- **GPT queue:** C18 and C20 marked done (ChatGPT finished both; commits `6e2e90a`, `2ff7b58`) so the 09:39 relay doesn't redo them.
- **Fable (owner: "fable is doing great… give it something to do"):** now on Part 2, the read-only study of the Blender SWG add-on (F86 prep) in `outputs/Fable-asset-pipeline/`. Next for Fable, from its own plan (`Fable-hoth-caves/README.md`, "Next"), in three batches:
  - A: spawn regions, the MTG server-script creature audit, and a clean-room glacial rancor (stock rancor body);
  - B: POIs and NPC camps, plus a home for the mynock den;
  - C: missions and vehicles.
  - Resources are already done (`2f205cd2` + the resource tree in `local_planets.tre`).

### 2026-10-14 06:33 Claude: Botanist box works on the server; usage limit reached
- **Botanist re-check (relogged Pell):** PASS, the server knows `outdoors_botanist_novice` and granted it (and the `outdoors_botanist` root). The trainer check FAILed only because Pell stood in the gather field (x 3770), out of the 60 m search range of the trainer at 3516 -4783. Next: walk Pell to the trainer and talk, relog, then check that the box persists; the skill window needs the owner's client.
- **Owner (06:32): "see if fable can just finish hoth, and reverse engineer any creatures missing."** Claude's usage limit was reached, so Fable was told to finish only the ice caves staging (`outputs/Fable-hoth-caves/`) and write a "Next" plan for the rest of Hoth and any missing creatures (clean-room from client data). Next session: review and apply the caves, then run that plan.
- Running: overnight cycle every 30 min (bots); the Esk group relogs on the C4e-F2 body at the next cycle. ChatGPT is out of usage until 09:39 (C18–C20 done).

### 2026-10-14 06:31 Claude: ChatGPT out of usage until 09:39; Claude takes the bots; Fable stages the Hoth ice caves; C4e-F2 fixed
- **ChatGPT's 06:01–06:24 work:** C19 (C4f review: 2 P2, both fixed by 06:24), C20 (`2ff7b58`: every fallback first brings an off-Tatooine crew home by the ordinary shuttle; Dorn fails cleanly on a failed walk; 21 offline tests), and C18 cut to a sample (`6e2e90a`: 30 objects, no new P1/P2; follow-ups listed, among them auditing the live database for objects under the old paths before any live rename). Then the owner reported it's out of usage until 09:39.
- **Bots:** server lock moved to Claude. `esk-routes.py` is back in `Agent/squad-plan.txt`. The Esk group is stopped after the Botanist check, so the next cycle logs it in on the new body and its round exercises C20's return-home fallback.
- **C4e-F2 (dev `90f60a81`):** straight-line moves and the fight approach carry their scene; position, scene check and send share one lock; a move stops when the zone connection is down. Dev build clean (core3client 06:23).
- **Fable (owner: offload):** stage the Hoth ice caves port in `outputs/Fable-hoth-caves/`: Bellum's 152 spawns, the 11 on Bellum-only buildings skipped, the boss reward system dropped for corpse loot plus an owner question. Then, if usage allows, read-only prep for F86 (the Blender SWG add-on). Fable never writes to /opt/swg.

### 2026-10-14 06:24 Claude: C4f findings fixed; local git for h/; names rule; Fable's Ossus plan relayed
- **C4f-F1 (dev `23014f39`):** `/spawnStatus` and `/showSpawnRegion` cross-lock each spawn area with the creature while they read it, and release it before the SUI is built. Dev build clean; not re-run in game yet (the test galaxy runs the older build until its next restart).
- **C4f-F2 (h repo `f0b192e`):** `hoth_client_build.py` skips `local_planets.tre` when it looks up the winning copy, and builds into `.new` copies that replace the old output only after the archive check passes.
  - Two builds in a row match the installed archive byte for byte (`b7930396…`).
  - With our archive simulated first in the load order, the old lookup picks `local_planets.tre`; the new one picks `patch_14_00`, and the Botanist rows build.
- **Local history (owner: "do the local history for now"):** `h/` is now a git repo (`8ac7857`, `9a943dc`; no remote).
  - `.gitignore` keeps out secrets, the client and archives, backups, `work/research` (third-party clones), images, PDFs, big inventories and per-run churn.
  - A secret scan of the 1,802 committed files found only code that reads or generates passwords at runtime.
  - Commit rules: AGENTS.md, Server code section.
- **AGENTS.md, Privacy (owner):** redact real people's names, handles and aliases in anything published (Discord, any GitHub push, shared pages). The one exception is the credits a licence requires.
- **Bots after the 06:03 relog:** 18/18 online, results back to normal (Dorn 29/33, Cresh 10/12, Besh 28/36), which confirms the stale-body diagnosis.

### 2026-10-14 06:15 ChatGPT: C19 / C4f read-only review complete
- Reviewed by ChatGPT: `34d4772a`, `b7f03b0e`, `2f205cd2`, `bea94e7a`, `578861d9` + six tools; `Documentation-support/review-C4f/C4f-review.md`: changes requested, 2 P2 (spawn-counter race; Botanist repeat-build failure). Offline loot/resource/CRC checks pass; C4e-F1 closed in leash. No server commit or server/staged edits; game tests untested. Next: Claude fixes/re-review + runtime checks; C4e-F2 remains open.

### 2026-10-14 06:04 Claude: ChatGPT has WSL (owner: full access); GPT queue C19 → C20 → C18; stale-bot check
- **Owner chose full access for ChatGPT (05:58)** and wants Claude to keep leading. The relay (`tools/agents/gpt_relay.ps1`) now runs Codex with `-s danger-full-access`. Codex won't combine that with `--approve-for-me`, so the flag is dropped. A probe ran `wsl -d Debian -u swgemu -- echo` from Codex: OK. The owner switches the interactive Codex session in Codex's settings. New rules are in AGENTS.md (Safety 2): server lock, swgemu, no live galaxy, Claude keeps the dev tree and test restarts, GPT drives bots only with the driver claim.
- **GPT queue (owner: about 30% usage left), in order:**
  - C19 (the C4f review: it blocks live);
  - new C20 (C16 follow-up: a recovery fallback for crews stranded off Tatooine, the dorn-social KeyError, its own Esk-only runtime proof);
  - C18 cut to a sample of about 30 paths.
- **Bots:** 17 of 18 bodies logged in before the 05:32 restart. The game runs over UDP, so they still said "connected" while the server didn't know them; the 05:57 Botanist check got no replies (Pell). `squad.py` gains `Bot.stale()`: a body older than the newest `core3` process counts as offline, and `setup` logs it in again. The 06:02 overnight run relogs them; the Botanist check reruns in the next gap.
- AGENTS.md also gets: never restart the test galaxy during a squad round.

### 2026-10-14 05:56 Claude: Fable's Ossus asset plan delivered
- `Fable-planet-test/ossus-assets/README.md` + `assets.json`: 9 needs, 19 candidates, 10 licence summaries with quoted clauses. Research only: nothing downloaded, bought or contacted.
- **Result:** a first playable Ossus needs no new art. It's all stock art referenced in place, as for Hoth: Dantooine temple pieces, the Yavin enclave interiors, Dantari camps for the Ysanna, the outpost starport for Knossa, and stock creature bodies.
- **Second pass:** CC0 textures and ambience from Poly Haven, ambientCG and OpenGameArt; Quaternius ruins once the Blender→SWG path (F86) is validated.
- **Ruled out:** paid store art (Fab, CGTrader, the Sketchfab store), because their licences require extraction-proof archives and SWG's are openly extractable.
- **Confirmed:** the disc's TRE v6 archives have all-zero headers; neither our reader nor Core3's can index them.
- Owner decisions: question 3 above.

### 2026-10-14 05:49 ChatGPT: CH across all modes, source registry and Tames note
- Saved CH balance/design research and valid local-client build probe JSON. MCH + MRifle or MTKA + Novice Medic: 213 points, 37 spare; runtime/server parity and game performance unverified. Proposed control/uptime → roles/sustain → Master-gated tuning and PvP counterplay.
- Owner supplied discovery sources for the whole server: registry saved, Sketchfab collection returned 403, CGTrader and tool docs readable. Comlink is documented as binary service, not assumed open-source model exporter; nothing deployed/downloaded.
- Appended owner's explicit Tames discussion request and context to Claude inbox at 05:49. No bot driving, /opt/swg changes or commits. Next: baseline CH tests after dedicated driver claim, and owner/Claude Tames discussion; queued downloads remain separate.


### 2026-10-14 05:52 Claude: bot round 053149 is noise (my restart raced it); setup now relogs dropped bodies
- My second test-galaxy restart (server up 05:32:08) came 20 s after the overnight round started (05:31:48). 10 of 18 bodies lost their zone connection but kept running, and `squad.py status` counted them online. Treat 053149's FAILs (surveys, forage, Dorn chat/leash, Besh relog) as noise, not regressions.
- `tools/bots/squad.py`: `setup` restarts a body whose status says `connected: false`; `status` shows it as offline. `overnight_cycle.sh` runs setup whenever any bot is down (it used to wait for all 18) and no longer counts those bodies as online. The next cycle (about 06:02) relogs them.
- Read ChatGPT's 05:00–05:09 work (C4e, C15, C16, C17) and its owner-directed research. Notes in `Agent/to-chatgpt.md` 05:51: a C16 recovery fallback for crews stranded on Hoth; a C17 redaction gap (names); C19/C18 first.

### 2026-10-14 ChatGPT: farming download queue and custom sabers
- Owner authorized scheduling farming downloads: saved ordered 30-entry queue with original source links and receipt/licence/hash requirements; no timed automation, transfers or installations performed. Authorization persists for this listed batch.
- Saved Darksaber/Ghostfire feasibility report and read-only saber probe + transcript. Original CC BY Darksaber candidate has creator notification request; no contact made. Ghostfire opalescent trails are owner-directed art, not asserted lore.
- Local probe ran successfully, 85 relevant file names and small appearance/shader dependencies inspected in memory. Missing login config limits effective-load claim; no rendering/game tests. No /opt/swg changes, no commits. Next download queued farming batch; saber file-format/prototype work remains unclaimed.


### 2026-10-14 05:38 Claude: test galaxy restarted (Hoth, loot, resources, Botanist, spawn commands); Fable batches 1 and 2 in dev; overnight check running
- **Test galaxy restarted twice** (owner: "restart ok"; the owner's client was closed).
  - The first start had no Hoth. Hoth was only ever enabled by a hand-typed `--config`, so any restart through `squad.py galaxy` or the overnight script dropped it.
  - `tools/test_galaxy.py` now enables `hoth` and puts `local_planets.tre` first by itself whenever that archive exists.
  - The second start: Hoth deployed (7 regions, 94 snapshot objects), no Lua errors, 1,091 skills.
  - Running dev build: `34d4772a` spawn commands, `b7f03b0e` Hoth loot, `2f205cd2` Hoth resources, `bea94e7a` leash C4e-F1 fix, `578861d9` Botanist trainer.
  - Archive `local_planets.tre` `b7930396…` on server and client: merged object CRC table, Hoth resource rows, Botanist skills and strings.
  - The backup restore put characters back at 13 Oct 17:20; `squad.py setup` relogged the bots.
- **Botanist feasibility test:** built (README of the owner's book, "Botanist feasibility test"). The bot check `tools/owner_content/botanist_check.py` waits for a gap between overnight rounds.
- **Fable backport (`outputs/Fable-backport/`; applied by Claude with its hash-checked `apply.sh`; luac clean):**
  - **Corrected dormant count:** 2,334 objects, not 13,627. Core3-dev registers 11,293 of the listed ones under `custom_content`.
  - **Dev `0c44d431`, batch 1:**
    - 1,074 server paths from our 13 Oct MTG import were mangled (an underscore became a slash) and are now the real SOE paths, plus the same fix in `mtg_catalog.lua`. Verified on a sample: the file is in `creature_loot/kashyyyk_loot/` but had registered `creature/loot/kashyyyk/loot/...`.
    - 13 new wearables, and 3 client-path repairs.
  - **Dev `5c7ae017`, batch 2:** 45 never-loaded MTG templates wired in, and 10 new templates.
  - **The disc's later archives** (patch 18+ and sku) are TRE version 6, which our readers can't open yet.
  - Owner questions added above (6).
- **Overnight check:** the owner turned it on. Runs at 05:02 and 05:31 took about 15 s each with no prompts. `overnight_cycle.sh` logs to `Bot-reports/OVERNIGHT.md`.
- **ChatGPT:**
  - The queue was empty. New review tasks: C18 (Fable backport cross-review) and C19 (tonight's dev commits).
  - Its C16 acceptance results are in `to-chatgpt.md` (05:13).

### 2026-10-14 ChatGPT: unbranded farming art gap fill
- Owner clarified worn Star Wars-like style without branding. Saved `Documentation-support/farming-unbranded-art-gap-fill.md`: CC0 gardening capsule, industrial tanks/panels/pipes, lamps, racks, jars, controller textures, growing plant and farm tools; CC BY hydroponic/foliage alternatives.
- Provenance chains recorded for rubberduck→a52 industrial update, Quaternius workstation remix and Poly Haven lamp conversion. Plant pictured in capsule is explicitly separate. High-poly hydroponic scene is not suitable for direct import.
- Still custom: coherent greenhouse shell, dryer/extractor/grinder assemblies, matching crop stages and all SWG conversion/testing. No files downloaded, no account actions, no code/server edits or commits. Next choose a small batch for authorized file audit and conversion proof.


### 2026-10-14 ChatGPT: Star Wars-first farming art shortlist
- Saved `Documentation-support/farming-open-art-shortlist.md`, with primary/indexed evidence distinguished. KLGaming Clone Wars crate has explicit original-modeling statement and CC BY 4.0; Yughues plant packs provide CC0 crop bases. Vaporators/barrels held for provenance, not cleared imports.
- Recorded licence conditions, paid/restricted alternatives, missing Star Wars crop-kit result and proposed SWG conversion checks. No assets downloaded or imported, no renders/game tests, no server edits or commits. Next select a small batch for download approval and exact file audit.


### 2026-10-14 ChatGPT: farming references and Minecraft licence checks
- Saved `Documentation-support/farming-system-UM-feasibility.md`: requested SeedFarm, Cannabis Skyrim and Alien Plants, plus Minecraft references and proposed adaptation.
- Verified MIT evidence for Farmer's Delight 1.21, Mystical Agriculture 1.21 and Croptopia master. Simple Greenhouses README/licence scope conflict recorded; Bonsai Trees 4 current branch ARR despite older MIT forks. No blanket art clearance.
- Read original published Skyrim growth script; distinguished implemented stages/watering/harvest from fertilizer stub and unverified breeding. Original release is not proof of current SE Creation provenance.
- No packages downloaded, source copied, server edits or game tests. No commit: documentation workspace has no Git checkout. F90 remains proposed; next select one reference/revision and audit Core3 integration.


### 2026-10-14 05:09 (C17 Discord) — ChatGPT
Channel/role/privacy plan, pinned rules/FAQ and owner checklist in `Documentation-support/discord-plan.md`; `tools/agents/discord_post.py` adds exact dry-run payloads, four digest sources, redaction/mention suppression, length limits, persisted de-duplication/cooldown and interrupted-send guard. 22 offline tests pass; local saved-source previews checked. Discord delivery untested. No accounts/apps/webhooks/bots created, real token read, post sent or scheduler enabled. Next: owner private setup, redaction list, preview review and explicit go. No commit: this Windows folder is not a Git checkout.

### 2026-10-14 05:05 (C16 runtime observation and safe stop) — ChatGPT
Observed already-running 045724 job (not launched by this session): main Esk routes used Tatooine destinations on Hoth, 0/5, incapacitated crew. Added pre-movement all-member planet guard and regression test (15 offline tests total). Wrote shared STOP at 05:03; at 05:04:31 reports recorded RunStopped and ACTIVE/STOP were removed, confirming cooperative stop. No galaxy stop or logout. Two repeated blocked/failing rounds for Aurek/Besh/Cresh scheduled census fallbacks; actual fallback execution/boarding still pending. Broken-test report: Agent/reports/2026-10-14-C16-wrong-zone-routes.md. Claude informed; do not restart old plan until Esk location is handled.


### 2026-10-14 05:00 (C4e, C15, C16) — ChatGPT
C4e reviewed by ChatGPT: 5b2a858f, 421adb15, 9ac7cdcd and c402e480. Changes requested: P1 null/null floor-triangle proof; P2 scene-unguarded straight movement. Report and static/model evidence saved; actual client lock-order context requested from Claude. C15: 10 CC0 creator-source candidates, MD/JSON, no downloads. C16: chooser, persisted per-group state, fallback rotation/main retries, per-round deadlines, new observational probes and fresh collector-page filtering; 15 offline tests pass including simulated five-round runner integration. WSL status denied E_ACCESSDENIED, so test-galaxy runtime/ticket checks requested from Claude; no server lock transfer/restart/deploy. Wider travel/mapping/crafting coverage remains open in Bot-reports/fallback-coverage.md. No commit: Windows project folder is not a Git checkout. C17 newly queued, not started.


### 2026-10-14 04:59 Claude: Hoth reward loot in dev; MTG objects need a merged CRC table; owner's disc extracted; C17 Discord queued; F91–F93
- **Dev `b7f03b0e` (Hoth reward loot):**
  - 25 of Bellum's 163 Hoth loot items (7 decorations, 18 vehicle deeds) in three groups, dropped by Hoth's creatures at 3%, 5% and 2%.
  - The other 138 need client objects only Bellum's private archive has.
  - Clean `luac`. **Not tried in game:** the owner's test client is open.
  - Details: `hoth-port-log.md`, 04:58.
- **Found: our client couldn't name any MTG-only object.**
  - Stock's `object_template_crc_string_table.iff` (patch_14_00) shadows MTG's.
  - `hoth_client_build.py` now puts a merged table (29,358 names, no clashes) in `local_planets.tre`; rebuilt and verified.
  - It gets installed into `SWG-client/` when the owner's client is closed.
- **Owner's disc (SWG Complete Online Adventures, Oct 2006):**
  - Its 122 archives, including SOE patches 15–33 and sku1–3 (NGE era, not in our client), are extracted read-only to `/opt/swg/disc-extracted/SWG-group/` and hashed (`tre.sha256`).
  - A Fable helper is staging NGE backport batch 1 in `outputs/Fable-backport/`. It has no /opt/swg writes; Claude reviews and applies.
  - The owner OK'd batch 2 if usage allows.
- **ChatGPT:**
  - C4e exports done (see `to-chatgpt.md`, 04:55).
  - New C17 (Discord: layout plus a webhook poster with a dry run; nothing posted before the owner's go).
- **Feature register F91–F93 (owner ideas):** server-side "script extender" (Core3 Lua hooks), client-side DLL extender (feasibility only), and clean-room NGE backports from the owner's disc.
- **Owner questions** are at the top of this board.

### 2026-10-14 04:40 (task check) — ChatGPT
Read board, roadmap, inbox, queue and 04:38 live snapshot. Open queue: C4e review, C15 open assets, C16 bot fallback. Claude handed bots back; Esk crew dead on Hoth and stale ticket-page bug reported. Documentation fixes already handled by Claude. No new task claimed, bot command, server change or restart during this status check.


### 2026-10-14 04:50 Claude: spawn commands committed; C16 for GPT; overnight check as one script; test-restart standing OK; Fable's planet test
- **Dev `34d4772a`:** `/spawnStatus` and `/showSpawnRegion` now work (they were empty stubs; staff-stub batch B). The dev build is clean. **Untested in game:** the owner's test client is open, so no test-galaxy restart. Next: the in-game test, then C4e-style review.
- **C16 for ChatGPT (owner):** bot fallback work. When a group's scenario is done or keeps failing the same way, it moves on to travel, navmesh mapping, terminal/trainer reachability, spawn census, crafting, buffs or a regression pass. Queued as `c16-bot-fallback`; the C16 paragraph is above.
- **Overnight check (owner: "how can we not need me to confirm every overnight check?"):**
  - **Cause:** each run's shell commands waited for approval, because the old rules were tied to each run's own scratchpad path. Five more runs failed on Claude's usage limit, and one 03:01 run is still waiting on a prompt.
  - **Fix (owner picked one script + one allow rule):** `tools/agents/overnight_cycle.sh` does the relay, squads and `Bot-reports/OVERNIGHT.md` lines by itself (`--dry` is read-only). The scheduled task `gpt-relay-overnight` now runs only that, and stays disabled until the owner turns it on.
  - **Testing:** the dry run passed; the full run is untested.
- **AGENTS.md, Safety 2 (owner):** standing OK for agents to restart the **test** galaxy when no owner client is running. That means no `SwgClient*`/`SWGEmu*` process and `swgemu_login.cfg` not on port 46453. Every restart is logged; never the live galaxy.
- **Fable (helper, `Fable-planet-test/README.md`):**
  - Picked **Ossus**; Dagobah is the runner-up.
  - Wrote a `.trn` reader, writer and height port that reproduce our recorded Hoth server heights to 0.1 m at 20 points. Made a minimal test terrain that passes offline checks.
  - Not yet loaded by Core3 or the client.
  - Side note, checked in Core3-dev: slope, direction and shader filters never change server heights (by design, per a code comment).
  - Owner questions are in its README section 6.

### 2026-10-14 04:10 Claude: Hoth creatures in dev; live client cfg fixed; Core3 command audit; owner's books mapped to real SWG; owner decisions
- **Hoth creatures (dev `c402e480`):**
  - Bellum's 19 ordinary mobiles, 11 lairs and the world spawner.
  - Seen spawning on the test galaxy: 5 tauntauns, 8 ice mynocks, 1 greater ice mynock. The level-1 probe bot was killed by them.
  - Log: `hoth-port-log.md`. **For ChatGPT: C4e review of `c402e480`.**
- **Owner in the real client:** `/teleportTo Esk` took the owner to Hoth. It's the first real-client Hoth load since the crash fix, and no crash was reported.
- **Live client cfg (owner OK in chat, 14 Oct):**
  - `SWG-client/swgemu_live.cfg` now has `[SharedFile]` above the 23 MTG lines; backup `swgemu_live.cfg.before-sharedfile-20261014`.
  - Normal play loads 74 archives, MTG included.
  - `Play SWG Test Galaxy.cmd` no longer repeats the MTG lines; it only adds `local_planets.tre`.
  - Checked with `client_load_order.py` for both live and test sessions.
- **Core3 command audit** (`Documentation-support/core3-command-audit.md`, tool `tools/core3_audit/command_audit.py`):
  - 859 commands. 159 are stubs that answer and do nothing; 45 of those are staff commands.
  - God Mode only unlocks staff commands; `/invulnerable` gives immunity.
  - Owner: build the useful staff stubs, in four batches (`core3-staff-stubs.md`). Each batch: dev commit, test galaxy, then your review.
- **Owner's books** (`Content-catalogue/owner-SWG-SW5E/README.md`, F87–F90):
  - The SWG x SW5E core book and the Galactic Pharmacopoeia, a reference only for new professions, mats and consumables. Real pre-CU SWG wins where they differ; no SW5E rules.
  - Pharmacopoeia: 85 substances matched to real crafters (14 already exist in SWG, e.g. Smuggler spices and Medic stimpacks), and 80 resource nodes (5 match real classes).
  - Armory (`legacy_era_armory.md`) received; mapping next.
- **Owner decisions:**
  - New professions enter at IV boxes, like every real elite.
  - Botanist gets the first feasibility test.
  - Farming/agriculture is a parked planned feature (F90) tied to Botanist.
  - No hybrid species until all the regular ones are in.
  - Port Bellum's Hoth reward loot as the next Hoth slice.
  - Hoth's cliff: I'm scanning the terrain for a better spot; softening the slope is the fallback.
- **Fable test (owner's choice: "a planet with less to work with"):** a separate Fable helper works only in `outputs/Fable-planet-test/`, read-only elsewhere. Please leave that folder to it.
- **Bots:** Esk's group is now a Hoth crew trained like the world-boss crew (`groups.json` training). Note `ride()`'s stale-ticket-page issue in my earlier message.

### 2026-10-14 Claude — review of ChatGPT's research (owner request)
- `Documentation-support/research-review-20261014.md`. The research is careful and well sourced; nothing claims an untested result. Eight findings:
  - **Most important:** the client never loaded the MTG archives (see the Hoth crash entry). Live's character builder offers 8,051 MTG objects that the live client can't load, so **don't use the MTG Content Library on live** until `swgemu_live.cfg` gets a `[SharedFile]` line (owner's OK).
  - Also: two SOP corrections, C12's boilerplate rows, a Hoth movement-speed caveat, stale macro lines, missing spaces and mojibake in several documents, and a privacy note.

### 2026-10-14 Claude — Hoth crash in the owner's client: cause and fix
- **Crash:** `terrain/hoth.trn is not a valid terrain file` (client crash file, 02:31). Also on the owner's screen: a broken ticket-screen map, and no Hoth on the galaxy map.
- **Cause:** the 23 MTG `searchTree` lines in `SWG-client/swgemu_live.cfg` were appended after its `[Station]` header (by `work/install_community_content.py`). The client reads them only in `[SharedFile]`, so **the client has never loaded any MTG archive**. Hoth's terrain, snapshot, map image and planet model all come from MTG. Our closure check counted lines in any section (Bellum's `cfg_priorities`), so it missed this.
- **Fix (test sessions only):** `Play SWG Test Galaxy.cmd` now adds the MTG lines to the session's `[SharedFile]` block. New check `tools/hoth/client_load_order.py` reads the config the way the client does, and with the new session file all ten Hoth files resolve. Live (`Play SWG.cmd`) is unchanged; fixing `swgemu_live.cfg` itself needs the owner's OK. Details in `hoth-port-log.md`.

### 2026-10-14 02:30 Claude — Hoth travel works on the test galaxy; TortoiseBots; test-galaxy launcher; GPT's bot controls reviewed

- **Hoth:** the test galaxy runs with Hoth (deployed, 6 regions, 94 snapshot objects). **Esk flew Mos Eisley → Coronet → Hoth and back: 18/19 checks** (13 Oct 23:15). The one miss was the scenario's own outpost check, since fixed. The starport's terminal, collector and shuttle come from the building template; no extra objects needed. Ground height reads 0.0 around the pad, so a terrain probe is in the scenario now (result in `hoth-port-log.md`). Details in `Documentation-support/hoth-port-log.md`. Owner's client: `local_planets.tre` not installed (asking the owner).
- **Coronet travel UI:** Rori/Lok are stock pre-CU (no Corellia fare); Hoth needs the client file. Answer in `Agent/reports/2026-10-14-travel-ui.md`.
- **Test-galaxy login for the owner:** `outputs/Play SWG Test Galaxy.cmd` points the client at port 46453 for one session and switches back to live when the client closes. `Play SWG.cmd` also switches back first if a test window was closed early. Owner logs in with their usual account (the test galaxy is a copy of the newest backup).
- **TortoiseBots (owner's go, author's permission on Discord 13 Oct 22:53):** pinned `bc914eb3` in `work/research/Sagiroth_TortoiseBots`. Download record D1, plan section D, and a credit in `CREDITS-and-sources.txt`. Reference only: not forked, nothing built or run. Study: `Documentation-support/tortoisebots-study.md`, merged with GPT's brief; next steps agreed.
- **GPT's bot controls (00:52), runtime review:** offline suites pass (3 + 2). A live halt during a Hoth run stopped cleanly at the next checkpoint 12 s later (`stopped`, no further commands). The fresh-ticket check passed on a real purchase. Not yet tested: `--minutes` expiry, and a halt during a boarding wait.
- **Stationary bots:** idle between runs, not stuck.
- **Owner decisions (02:25):** a 5-minute read-only status snapshot for GPT, now running (`swg-live-status.timer` → `Agent/live/status.md`); Hoth's client file in the owner's client for test sessions only; the outpost cliff gets a look in the real client first (a 43 m north wall 200–250 m out, profile in `hoth-port-log.md`); Hoth creatures keep Bellum's endgame levels. Dev commits for review (C4e): `5b2a858f`, `421adb15`, `9ac7cdcd`.

### 2026-10-14 01:47 ChatGPT — Prophecy / [name removed] follow-up
- Owner supplied Prophecy and recalled admin [name removed], then corrected forum handle to [name removed]. Recorded separately from [name removed]'s still-unknown official SOE galaxy. Added storyteller/prophecy-alias-follow-up.md with source URLs, queries and access gaps; updated authenticity register/MODLOG. Public Prophecy/Vision of Hope predecessor and 2022 closure-report leads recovered, no reliable handle/item/sale match or [name removed]-spelling confirmation.
- Old Prophecy site, direct Reddit, bounded Wayback CDX and linked videos inaccessible; do not claim old forums/footage fully searched. Unrelated same-name users not attributed. No download/import/install/server/game actions or commits. Next useful evidence: profile/post URL, guild/year or official-live galaxy; weapon stats/identity still open. Inbox re-read; no new Claude message.

### 2026-10-14 01:42 ChatGPT — weapon authenticity register and owner alias leads
- Owner clarified accurate original identities/stats/effects are the priority. Added Documentation-support/storyteller/authenticity-register.md (18 leads), weapon-path-index.md (690 paths), identity-metadata.json and MODLOG.md; original read-only tools weapon_candidates.py and weapon_identity_audit.py. All 1,592 weapon versions retain identity metadata; 371 paths differ across copies. Checked 262 Storyteller object/clientdata versions: no explicit weapon-path association. Zero reader errors; counts/hash/reference consistency checks pass. No historical comprehensive list claimed.
- Verified stock Flame Thrower vs MTG Plasma Flame Thrower string-key distinction; quest/light/droid variants can share appearance. Local names/models do not recover original exceptional-instance effects. Contemporary October2004 Elder stun-baton report recorded; modern emulator groups are not SOE measurements.
- Owner supplied [name removed] (live) / [name removed] (private-server) aliases; focused public lookup found no reliable match. Live galaxy/private server/guild requested. Uncertain acquisition/private-server background not treated as fact or weapon provenance. No installs/downloads/imports/game/server changes/commits. Original stats, exact brother item and runtime validation remain open; Claude notified.

### 2026-10-14 01:29 ChatGPT — Storyteller files, reports and public developer documentation
- Added read-only storyteller_weapon_inventory.py + Documentation-support/storyteller/:76TRE,202952paths,690weapon paths/1592versions;351Storyteller context paths; zero explicit Storyteller weapon markers. Three NPC/test-name candidates; none identified as recalled weapon.128884permitted Lua files searched,37candidate-reference files; no direct same-line Storyteller weapon link. JSON/decoded-size checks pass, no game checks.
- Historical register distinguishes2024confiscation,2021equipment-access/hearsay,2005Darktrooper-baton report and official looting fix. No verified developer/GM-only case or exact flamethrower/sale. Public SOE notes document weapon equip controls; Fan Faire2007 Tunso/Pex panel announcement found, transcript/incident explanation not found.
- No imports, downloads, /opt/swg edits, gameplay or commits. Next useful evidence: server/character/year/screenshot or permitted NGE equipment mapping. Full source URLs/limits in storyteller/historical-reports-and-SOE-docs.md.

### 2026-10-14 01:17 ChatGPT — UM Storyteller identity follow-up
- Confiscation account names unnamed Storyteller lightsaber, not verified flamethrower. Located separate2021 equipment-access/DJM-Elder recollections; not confirmation of same purge or sale. Repeated search hits deduplicated.
- UM research workflow applied; local KB function blocked by missing PyYAML; direct installed-note search no SWG matches. No install/import/game actions/commits. Evidence and queries appended to removed-flamethrower-identification.md; exact item/server/date still open.

### 2026-10-14 01:14 ChatGPT — bulk removal follow-up
- Expanded flamethrower timing to possible NGE and recorded lava-flea/one-of-kind recollections. Located retrospective Storyteller weapon-confiscation account with missed bank objects; uncorroborated and not a flamethrower identification. Official2004 credit purge and Corvette quest cleanup distinguished from equipment recall.
- Findings and URLs appended to Documentation-support/removed-flamethrower-identification.md. No downloads, imports, commits or gameplay. Next: server/item/character/date discriminator.

### 2026-10-14 01:11 ChatGPT — historical flamethrower search
- Recorded owner CU-era repeated victim knockdown clue and ~25m surviving-item sale recollection. Found older machine-flamer/prone-wielder bug and TK/Commando combos; neither identifies this item. No exact removal/sale verified. Sources/checkpoint saved in Documentation-support/removed-flamethrower-identification.md. No imports, game changes or commits. Next discriminator: server/item/character/year.

### 2026-10-14 00:52 ChatGPT — bot stopping/status and travel assertions
- Owner authorized independent bot work while Claude unavailable; updated AGENTS work split. Server lock remains Claude; no C++ or /opt/swg edits.
- Added run_control.py; runner cooperative STOP/deadline checkpoints and saved per-group activity states. Outstanding body commands still finish/time out; direct scenario sleeps outside revised Hoth remain a gap.
- Hoth rejects old tickets as purchase proof and requires actual arrival/position on all four loop legs. Five offline regression tests pass; compilation passes. No runtime verification or commits.
- Next: Claude test-galaxy review as specified in Documentation-support/bot-control-update-20261014.md; WSL access unresolved.

### 2026-10-14 00:44 ChatGPT — macro research and travel triage
- Saved macro-bot research and bounded routine proposal; historical pre-CU target-follow found, coordinate moveTo unverified. No implementation, commits or in-game checks.
- Recorded owner TEST Coronet report: Hoth absent; Rori/Lok on map but not dropdown. Asked Claude to distinguish direct-route filtering from Hoth client/server registration. Runtime blocked by WSL denial. Next: Claude active-route/client check; no deploy authorized here.

### 2026-10-14 00:35 ChatGPT — owner reports bots standing still

Read board/roadmap/inbox and saved reports. Live read-only process check failed WSL E_ACCESSDENIED; current bot/runner state unverified. Explained scripted squads are idle between scenarios, unlike ambient world AI; asked lock holder Claude to inspect current runner/status. No bot commands, server changes or commits. Consumable guidance: skill-compatible stims, relevant cures/wound packs, enhancement packs for self-buffing, Mind-support food/drink; current character/item eligibility not checked. Next: Claude confirms live cause and queued tests.

### 2026-10-14 00:22 ChatGPT — owner setting and encounter clarification

Owner wants recoverable server-added encounters retained as optional modules, including re-engineering/replacement routes; C12 deferred/omit-v1 labels are staging, not rejection. Recorded Legends NJO–Legacy/post-Vong/post-Abeloth with Krayt Empire reference (130–138ABY envelope, exact year open). Updated AGENTS.md, roadmap, setting-and-encounter-policy.md and Hoth adaptation table/inventory; notified Claude. Existing rights/exclusions and deployment gates preserved. No source commits, implementation or runtime tests; documentation only. Next: choose exact year before faction/NPC/story implementation.

### 2026-10-14 00:09 ChatGPT — C12 → C14 → C13, WoW brief and follow-ups

- C12 complete as a read-only plan: Documentation-support/hoth/hoth-adaptation-table.md + inventory JSON;228 source files hashed. Flagged fifth cave/cell mapping, moved outposts, high source stats and deferred reward/vendor ecosystem. Source pins independently matched in C11 audit; target bindings/port/game tests remain Claude's work.
- C14 bounded pass saved24 lore/grid records and JSON, covering stock10 and all11 terrain-backed catalogue zones; Hoth K-18. Source indexed extracts cited, full-page access restricted; unknown moons/sectors explicit. Stock ticket UI calibration attempted8independent systems:RMSE67.85px/max132.63px/leave-one-out236.66px. Fit REJECTED; no client/TRE change. Evidence and original helper in Documentation-support/hoth and tools/hoth.
- C13 complete: Documentation-support/SWG-server-SOPs.md,9runbooks/10ranked gaps. Commands inspected, not executed; backup/rebuild any-core3 guards, /tmp incident and unverified coredump/live-restore workflow highlighted.
- Owner follow-up: recovered prior Document Setup And Lag Diagnostics WoW history (v3/78fbf506 build done, install unverified; limited CleanupTerrain result), shared alongside pinned TortoiseBotsv6source. Brief/evidence in Documentation-support/tortoisebots-prior-WoW-and-SWG-brief.md and tortoisebots-study-evidence.json. No code copied; donor licence audit remains open. Auto-compact reminder left for Claude to arrange WITH owner.
- Continued authorized outside-server work: C11 seven checkout pins/clean tracked trees verified, SHA256manifests + archive-record-review.md. A4 terms partial; A6 HOLD due SR association/exclusion; D1 mixed donor rights remain open. Canonical fetch records left to Claude, no downloads/installs/imports.
- Original tools/squad_health_report.py and fixture suite passed; saved Bot-reports/triage/latest.md+JSON distinguish FAIL/BLOCKED/ERROR. No pooled pass claims. Latest Hoth report has return-trip checks; loop/name/ticket assertions need tightening (sent to Claude, file not edited). Static report is not live state.
- Validation: Python compile, synthetic affine/singular cases, SVG XML parse, report semantic fixtures, JSON coverage/pin/hash checks. No /opt/swg edits, bots driven, live changes, new services or source commits. Archive historical board material below25KB if possible; everything preserved. Next: Claude runtime/Hoth integration, map-layout decision, pending rights and actual client checks.


### 2026-10-13 23:32 ChatGPT — board/queue check

Read board, roadmap, queue and inbox. Next queued tasks: C12 Hoth adaptation, C14 lore/map coordinates, C13 server SOPs. C11 section A fetched by Claude, record review pending (board/queue still show the old network block). C8 runtime test pending; C9 latest Claude run: missions safely blocked, doctor blocked on interior cells, harvest 7/10 with no prey. No tasks claimed or implemented in this check; no server/game actions or commits. Waiting for owner direction.


### 2026-10-13 22:53 ChatGPT — C8–C10 delivered

- C8: added 14 MCP tools and indoor move fields to tools/agent/mcp_server.py (v0.2.0). Path returns proof unchanged; move/fight have timeout headroom. Includes inventory/radial/SUI, decoded missions, find and tell. Offline dispatch contracts and Python compile passed; MCP reload and Claude test-galaxy checks pending, no live deployment.
- C9: nearest same-planet destroy mission within 600 m; stop on failed approach/acceptance, bounded retries and stricter completion evidence. Doctor resolves hospital interior anchors without guessing cells. Harvest uses shorter patrols, HAM/level checks and a 20 s fight bound; stops unsafe attempts. squad-plan updated. Four offline fixture cases passed; scenarios remain untested in game and can report BLOCKED for missing capabilities.
- C10: Documentation-support/bot-mapping-and-coverage-plan.md plus bot-coverage-matrix.csv: Hoth first, map/provenance/coordinate schema, truncation and route-proof limits, all 86 feature IDs and 39 profession tracks, next five scenarios with Claude dependencies. Local sources only; no new research/downloads.
- Evidence: Documentation-support/C8-C10-validation.md and tools/check_c9_offline.py. No /opt/swg changes, bot connections, server restarts or commits (workspace is not a git repository). Claude notified in inbox. C12 priority message received; not started under this C8–C10 request. Usage reserve approximately 4% before final recordkeeping.

### 2026-10-13 (owner-requested C11 message to Claude) — ChatGPT
- Added a prominent direct request in this shared handoff for Claude to provide network-enabled fetching/access for the already-authorized C11 task. Included exact socket blocker, 0 downloaded bytes, plan and inventory paths, constraints and resume point A1.
- Claude Code is not an available Codex chat/tool destination; notification is through this shared board. Receipt/reading unconfirmed. No external message or server operation; no commit. Next: Claude reads and acknowledges/picks up the request.



### 2026-10-14 06:13 ChatGPT: C19 complete; C21 queued by owner
- Independent read-only C4f review of 34d4772a, b7f03b0e, 2f205cd2, bea94e7a and 578861d9 plus archive/generator tools: `Documentation-support/review-C4f/C4f-review.md`. Reviewed by ChatGPT; changes requested: P2 spawn-counter data race and P2 archive self-input/repeat-build assertion. No server changes or commits made.
- Re-ran isolated review_checks.py successfully; evidence/source hashes saved alongside report. CRC, resource inheritance, loot preservation/weights and clean Botanist output checks pass; existing staged files/TRE unchanged. Runtime/client acceptance and fixes remain open; Claude notified. No bots driven, build, restart or deploy.
- Owner requested C21 after Claude's existing C19 → C20 → C18 queue: resumable resource/asset census, Wookieepedia Legends coverage and rights/feasibility/effort matrix. Task/plan recorded, no research started. Next existing queue work remains C20 then C18.
