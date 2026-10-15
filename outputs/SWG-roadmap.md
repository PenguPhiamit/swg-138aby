# SWG sandbox roadmap

Private, single-owner pre-CU galaxy (SWGEmu Core3 on WSL Debian). Last updated 13 October 2026, 15:10 PDT, by Claude. Whoever picks this up (you, Claude or ChatGPT) should update the checkboxes as work lands.

**Who does what:** see "Work split" in `../AGENTS.md`. In short, Claude does the engineering inside `/opt/swg` (bot body, server helpers, test galaxy, deploys). ChatGPT, using Codex and Universal Modder, does review, tools outside `/opt/swg`, play-testing through MCP, real-client checks with `um win`, research and file formats. Current tasks are on the board in `SWG-handoff.md` (ChatGPT's tasks are C1–C5 there).

Shared ideas, purpose, maturity and effort: [SWG-feature-register.md](SWG-feature-register.md). References: [professions/gameplay](Documentation-support/SWG-professions-and-gameplay-reference.md), [Universal Modder](Documentation-support/universal-modder-reference-for-Claude.md).

## Route for the first month (15 Oct – 11 Nov; Claude, 15 Oct, for the owner's OK)

Owner, 15 Oct: get as much done as possible with the Claude plan, doing the heavy lifting in the first month to shorten the whole project. (Max 5x. Even so, Claude's weekly limit is the scarcest resource, and the 30-minute cycle spends it too. Claude does what only Claude can do, and everything else goes to the lanes that cost no Claude usage.) Three days in, making things is not what holds us back. **Closing them is**: about ten items wait on a Claude game check, about twenty owner questions are open, and nothing new is live (the live galaxy is stopped). So the order is:
1. the things that make every later change cheap: a regression gate, a release train, pipelines;
2. then volume: planets and species;
3. then life: ambient NPCs and friends.

**How the usage is spent (lanes that run side by side):**

| Lane | Who | Does | Never waits on |
|---|---|---|---|
| 1. Integration | Claude main session (holds the server lock) | review → build → restart → bot acceptance → live release | research; offline staging |
| 2. Staging | one Claude helper session (Sonnet for mechanical work), while the weekly limit has room | content data, tools and offline checks in h; first review of GPT's source before lane 1 takes it | the lock |
| 3. Review and source | ChatGPT (relay) | cross-reviews (required for live), source fixes in `Core3-gpt`, offline tests | Claude's runtime |
| 4. Bulk reading | local model (Ollama) | idle research on game mechanics, examine texts, string tables, sweeps | anyone (free) |
| 5. Nights | the 30-minute cycle and bots | squad regression rounds; class-check slices: one profession per round on Aurek, so the whole profession matrix fills in over a few nights for no usage | — |
| 6. Owner | you | one decision batch a day (about 15 minutes); one real-client session every 2–3 days from `Owner-test-list.md` | — |

**Waste to cut first (usage that buys nothing):**
- The board is 150 KB and both agents read all of it every session (the house rule says about 25 KB). Archive finished rows and old log entries to `SWG-handoff-archive.md`.
- Park research tracks that feed nothing this month (owner's call): the Storyteller weapon, the Prophecy archive, the Darksaber trail, KOTOR authors and farming art. Keep their records; they come back as tracks.
- Every owner question carries a default and a date ("Claude does X unless you object by …"), so a missing answer never stalls a lane.

**Week 1, close the loops (to 21 Oct):**
- Empty the integration queue:
  - C34r (dev `90044b8e`) and the C30 Ossus fauna game check;
  - runtime acceptance for C25, C26, C9, C16 and the C8 wrappers;
  - C23 Hoth acceptance;
  - the open leash and body findings (C4d, C4e, C4f).
- **Regression gate:** one command after every restart (the squads, class check P0, Hoth/Ossus acceptance) gives one pass/fail report. The cycle runs it automatically. It is what makes every later change cheap. **Built 15 Oct:** `tools/bots/gate.py`, verdict in `Bot-reports/GATE.md`; first gate PASS (27/28).
- **First live release:** the bot body and `/agentpath`, `/leash`, the world boss, and Hoth if the C24 gate turns GO. Cross-review plus the owner's OK, as a batch, then weekly.

**Week 2, Ossus and Chiss playable; long-lead items started (to 28 Oct):**
- Ossus: NPCs (C35), missions, resources, caves; the bots map it (B6) and it passes the gate.
- Chiss: playable in the client.
- Phase 1 baseline finished by bots: loot, trade, craft, housing (R4/R5).
- **Asset converter, first static prop round trip (F86).** Needs owner question 7 (Blender, one CC0 pack, texconv). It is the longest-lead risk and unlocks all original art.
- **Client patch distribution for friends.** Players need `local_planets.tre` for Hoth and Ossus. This is a release blocker for anyone but the owner.

**Week 3, pipelines at scale (to 4 Nov):**
- The third planet goes through the Hoth/Ossus playbook as a repeatable kit; the owner picks Kashyyyk or Mustafar. Measure it: it should take days, not a week.
- Species 2 (Nautolan or Togruta).
- Resources and crafting (C29) integrated; the resource board terminal.

**Week 4, a galaxy that feels alive (to 11 Nov):**
- Ambient adventurers v1 (B3).
- Discord and the player bug inbox (C17, C27).
- The first playtest with friends on live.

Done means live and passing the gate, not "built on the test galaxy". The board keeps the daily detail; this section changes only when the route does.

- [x] Farming reference and permission research checkpoint (14 Oct): [Minecraft, Skyrim and ARK comparison](Documentation-support/farming-system-UM-feasibility.md). F90 implementation remains proposed and untested.
- [x] Farming art source shortlist (14 Oct): [Star Wars candidates and CC0 crop/prop fallbacks](Documentation-support/farming-open-art-shortlist.md). No assets downloaded/imported; individual provenance gates recorded.
- [x] Unbranded farming art follow-up (14 Oct): [Functional gap/source matrix](Documentation-support/farming-unbranded-art-gap-fill.md); industrial frontier direction, remaining custom shell/machine/stage work identified. No imports or game validation.
- [ ] Fetch authorized [farming asset download batch](Documentation-support/farming-asset-download-queue.md) and retain licence/readme/hash manifests (queued 14 Oct; no downloads yet).
- [x] [Darksaber/Ghostfire feasibility research](Documentation-support/darksaber-ghostfire-feasibility.md), 14 Oct: assets + read-only local dependency probe; effects unimplemented and untested.
- [x] [Creature Handler top-tier research](Documentation-support/creature-handler-top-tier-plan.md), 14 Oct: all three modes, local point costs, improvement priorities and test plan; no gameplay benchmarks.
- [ ] Discuss Tames with owner and Claude (owner request 14 Oct; note sent to shared inbox).
- [x] Record owner's [whole-server asset/data source leads](Documentation-support/server-wide-asset-source-registry.md), 14 Oct; item-level audits pending.

## House rules for anyone working on the server

- [x] C22 independent Hoth and C4 fix review (14 Oct): 2 P2 + 1 P3; [report](Documentation-support/review-C22/C22-review.md), offline evidence saved; gameplay remains untested.
- [x] C19/C4f independent review (14 Oct): two P2 findings; [report](Documentation-support/review-C4f/C4f-review.md). Fixes and in-game acceptance remain open.
- [x] C21 checkpoint 1 saved-manifest baseline (14 Oct): reproducible counts and finite follow-up batches; overall census remains open.
- [ ] C21 [resource/Legends/implementation census](Documentation-support/server-resource-and-implementation-census.md), queued after Claude's C19 → C20 → C18 queue; resumable across usage resets.

1. All server changes go on the local `sandbox` branch in `/opt/swg/Core3`, **one commit per change**. Experimental C++ goes on `dev` in `/opt/swg/Core3-dev` first. Pushing is disabled; keep it that way until you decide otherwise.
2. Before a rebuild or risky edit, run **Back Up SWG Galaxy.cmd**. It briefly stops the galaxy, so check that nobody is playing.
3. After Lua edits, run `tools/check_lua.py`. Then restart and run **Server Status.cmd**.
4. Record new sources, credits and permissions in `Content-catalogue/` and `Community-content/CREDITS-and-sources.txt`.
5. A gameplay feature only counts as working once it's been tested in-game. Mark things "untested" until then. "Test galaxy only" is not live.
6. Before any live deploy: the other agent cross-reviews it and the owner says OK (AGENTS.md, Ethics check).

## Phase 0: Foundation ✅ (done)

- [x] Core3 built and running; pre-CU client with an owner account (ChatGPT session)
- [x] Sandbox profile, MTG content library, example quest, two verified backups (ChatGPT session)
- [x] Private Git: `sandbox` branch, `upstream-base` tag, 4 logical commits, push disabled (Claude)
- [x] Launcher moved into `outputs/tools`; the Start window now says when the galaxy is ready (Claude)
- [x] Backup patch diffs against `upstream-base` and lists local commits (Claude)
- [x] **Server Status.cmd** health check and `check_lua.py` syntax gate (Claude)
- [x] Gap-check research: [SWG-gap-check-research.md](SWG-gap-check-research.md) (Claude)

## Phase 0.5: Finish hardening ✅ (done)

- [x] Full backup run with the updated script (`galaxy-20261013T160706Z`, verified, 2 min 13 s)
- [x] **Restore rehearsal passed**: that backup restored into a disposable copy (ports 45xxx, database `swgemu_rehearsal`) started in 30 s with matching resources (15,020), characters and zones, 0 errors, a clean shutdown, and the live galaxy untouched; the copy was then deleted. Re-run anytime with **Rehearse Restore.cmd**. Report: `Documentation-support/restore-rehearsal-20261013T161005Z.json`
- [x] Separate dev checkout `/opt/swg/Core3-dev` (git worktree, branch `dev`, Debug + `ENABLE_BUILD_CLIENT=ON`) via `tools/dev_build.py`. Built in 18 min. A second build directory inside the live checkout is unsafe: Core3's build copies `core3` into `bin/` and generates code into `src/autogen`.
- [x] Upstream sync routine: **Check SWGEmu Updates.cmd** (`tools/upstream_sync.py`) lists new upstream commits and the Gerrit changes worth watching; `upstream_sync.py apply` rebases `sandbox` safely (backup required, `pre-sync-*` tag, aborts on conflicts). Then **Rebuild Server.cmd**.
- [x] Backup reminder: the Start window and Server Status warn when the newest backup is 7+ days old.
- [x] Disposable **test galaxy** (`tools/test_galaxy.py`, ports 46xxx): newest backup, dev scripts. `--dev-server` runs the dev C++ build; `--config` adds config-local lines (13 Oct, Claude).

## Phase 1: Prove the basics (in progress, mostly by bots)

- [x] C39 independent dev review (15 Oct): [report](Documentation-support/review-C39.md), 1 P1 / 4 P2 / 2 P3; five source fixes on gpt/work, offline checks pass. Claude review/full build/in-game/persistence acceptance pending; no bots or restarts during review.

- [x] C34r independent item-kit/affliction review (15 Oct): [report](Documentation-support/review-C34r.md), one P2 fixed in gpt/work `19cfb3a5` after dev merge `cb4e2b9e`; extracted-code regression passes. Claude review/build/in-game acceptance pending.

- [x] C30 Ossus fauna source wiring (15 Oct): `6f25b704`, six reviewed creatures/six dynamic lairs/three groups/five habitat regions; 20 Lua syntax checks + stubbed loading pass. In dev as `80b66e65` and on the test galaxy since 15 Oct 01:40; its client names are in archive `8ad04fec`. A bot visit to each habitat is still pending.

- [x] C32 profession kit source + bot wrappers (15 Oct): `4a340565`, after dev merge `220700d0`; 7 offline wrapper tests pass. In dev and passed on the test galaxy (Claude, 15 Oct 01:40: grant, list, refusal, clear, 4/4).

The checklist from [SWG-developer-baseline.md](SWG-developer-baseline.md):

- [ ] Log in, teleport, use the character builder, relog to the same character
- [ ] Tutorial, travel, fight, loot, die and clone on a normal (non-owner) character
- [ ] Survey, sample, craft, experiment; item survives a relog; `/resource perfect` works
- [ ] Two clients, separate accounts: trade and group
- [ ] House placement and storage; The Beginning quest (Han/Chewie); JTL launch, fly, land, relog

### Plan: finish Phase 1 with bots, the real client and the owner (owner request, 13 Oct)

Most checks are run by bots once the agent body has the needed abilities.

- **Subjects:** the test subject is a **fresh non-staff bot character** (Kael has staff skills, so he isn't a "normal" character), plus a second bot for trade and group. `Core3.AutoReg = 1`, so a bot account is created by its first login.
- **Proving order:** each ability is built in the dev worktree and proven on the test galaxy first. The live run happens after the new body is cross-reviewed and the owner approves it.
- **Real-client checks** use Universal Modder's `um win` (window screenshots and input) after the owner logs in. Agents never type the owner's password.
- **Runner:** `tools/bots/phase1.py` (milestone B1/B2) re-runs every bot check and writes a JSON report, so Phase 1 doubles as a regression test after rebuilds.

| Check | Method | Body / server work | Who | Status |
|---|---|---|---|---|
| Log in, relog to same character | bot | none | — | ✅ live, Kael (13 Oct) |
| Character builder | bot | radial + SUI (`e1344def`) | Claude → ChatGPT | ✅ test galaxy; live after promotion |
| Owner teleport, `/resource perfect` | owner account | none | owner (or ChatGPT via `um win`) | `/resource perfect` ✅ live (owner, 13 Oct: Sloviboiam / Galiium, all stats 1000 in the resource dump); teleport open |
| Fight | bot | HAM/posture/combat log, `fight` reflex (`a72026b6`) | Claude | ✅ test galaxy (rockmite kill) |
| Loot | bot | `/loot all`; needs a humanoid kill (animals carry no loot) | Claude | open |
| Die and clone | bot | death state + clone SUI | Claude | ✅ test galaxy (Kael and Tobin: incap → dead → clone at Mos Eisley) |
| Travel between planets | bot | ticket SUI, board shuttle, zone change | Claude (or ChatGPT slice) | shuttle ✅ test galaxy (Cresh: `/purchaseTicket` at Mos Eisley shuttleport → ride to Bestine); other planets open (C7) |
| Group and trade | 2 bots | group commands ✅ events in body; secure-trade messages | Claude | group ✅ test galaxy (Tobin + Mirra: `/invite`, `/join`, `/leaveGroup`); trade open |
| Survey and sample | bot | survey list/results messages, `/requestCoreSample` (`3797430a`) | Claude | ✅ test galaxy (Tobin: Iron container + XP) |
| Craft, experiment, survives relog | bot | crafting-session messages | Claude | planned |
| Tutorial | bot (Rook) | indoor paths ✅ in (`/agentpath`); cell → world path open | Claude | in progress |
| House placement and storage | bot | placestructure, indoor paths, item transfer | Claude | planned |
| The Beginning quest | bot | conversations fixed (Han answers) | ChatGPT (MCP) | after promotion |
| Two real clients: window/pointer | real client | `um win` | ChatGPT + owner (C2) | open |
| JTL launch, fly, land, relog | real client | `um win`; JTL enabled (`LaunchFromDevice`) | ChatGPT + owner | later |
| Runner + expected outcomes | — | `tools/bots/phase1.py`, `Agent/notes/phase1-expectations.md` | ChatGPT (C3, C5) | open |

### Navigation for bots (owner question, 13 Oct)

The body has no terrain or navmeshes. It asks the server: `/agentpath path|height` (dev `eebdd99d`) returns routes from Core3's own PathFinderManager, the one the NPCs use. That covers Recast navmeshes for cities and outposts and floor meshes inside buildings, plus ground heights. Only accounts in `Core3.AgentAccounts` can use it. The body re-plans partial routes and walks cell-local points through doors. Going live needs the server change deployed and `Core3.AgentAccounts = {"agent01", …}` added to the live `config-local.lua`, after cross-review and the owner's OK.

## Phase 2: Content wave 1 (server-side only, no client changes)

These are low-risk ports because they need no new client art. Do each one as: port, `check_lua`, restart, test, commit.

- [x] **Mercenary companions**: broker Dax Venn in Mos Eisley; hire up to 3, follow, dismiss (live `9f74dd57`, `28aa46d8`). Combat assist still inconclusive.
- [ ] **World boss rotation** (Flurry-inspired, existing creatures) + Rhea Tannor the big game hunter: built and tested on the test galaxy (dev `bda2c0dd`); **awaiting cross-review and the owner's OK to deploy**. Credit reward untested.
- [ ] **Follow assist `/leash`** (temporary fix for client `/follow`, which steers in a straight line and gets stuck): right-click a group member → "Leash (follow assist)". The server moves a follower who stops closing the gap to 3 m behind the leader along the navmesh. Built and tested with bots on the test galaxy (dev `09a56205`); **C4d re-review requests changes (13 Oct): 2 P1 + 1 P2 remain; fixes/re-review, the owner's OK to deploy, then a real-client test (C6) remain**. A proper client-side follow (pathing in the client, possibly a Universal Modder mod) is a later option.
- [ ] **POI waypoint helpers** from Flurry (`events/poi/*_poi_waypoints.lua`)
- [ ] Bellum QoL: vendor/bazaar search waypoints, house pack-up, character name-change service
- [ ] Extra Jedi abilities from Return of the Force (Force Lightning 3–5, Force Throw 3), only if they fit the Jedi plan
- [ ] Triage the 2,537 startup warnings: fix or suppress the MTG ones we actually use; leave the ship-chassis warnings for the JTL work

## Phase 3: New planets

**Main track since 13 Oct 22:35 (owner: "content first, start hoth, utilize UM where applicable").** Start with **Hoth**. Working record: `Documentation-support/hoth-port-log.md`. We already have MTG Hoth terrain and snapshot, Bellum Gero has current-Core3 Hoth server scripts and a planet toolchain, and Flurry has Echo Base and the Imperial base.

0. [ ] **SWG file-format and source inventory** (ChatGPT, Codex + Universal Modder research, task C1). This feeds steps 1–2 and Phase 5's converter.
1. [x] Dependency inventory against our client + MTG (13 Oct, Claude, `tools/hoth/hoth_closure.py`): the terrain and snapshot are complete apart from 2 shader names to confirm; MTG supplies the wampa, snowtroopers and rebel snow soldiers; only the rancor boss look is missing. Details: `Documentation-support/hoth-port-log.md`.
2. [ ] Client side: register Hoth in the planet CRC table, `travel.iff`, `planet_n.stf`, ticket-purchase UI and planetary map. Build a local `local_planets.tre` with `tre_pack.py --merge`, installed on both server and client at a **higher** priority than the stock archives (a higher searchTree number wins). Pre-check done: Hoth is in none of those files yet.
3. [ ] Server side: enable the zone, add travel points to `planet_manager.lua`, port Bellum's Hoth mobiles, caves, POIs and missions. Add Hoth resources. Use Universal Modder's `port-a-mod` method: pin the source version, keep an adaptation table, test unit by unit.
4. [ ] Test travel there and back, terrain, spawns, a cave boss, a mission. Then commit.
5. [ ] Next: **Kashyyyk** and **Mustafar**. Assets are on your Complete Online Adventures disc patches and in MTG; Flurry has Kachirho and Mustafar screenplays. After that, Taanab and Mandalore, which have the most Flurry scripting.

## Phase 4: Species

- [ ] Port the original public species package (newspecies, Halyn/Phoenix) first; Zeltron next (packages already downloaded)
- [ ] Resolve the client-art terms recorded in the EiF research before importing EiF species art

## Phase 5: Original content and restoring cut or incomplete assets

Universal Modder is installed for both agents (Claude Code and Codex, 13 Oct). The plan for art:

- **Concept and textures:** images locally through ComfyUI (free).
- **3D models:** image-to-3D through fal. It's pay-as-you-go with no subscription, which the owner prefers; get the owner's OK for each batch.
- **SWG converter:** built with Universal Modder's `reverse-engineering` method (rebuild the format, write a converter, prove it by converting back and forth). This is the piece nobody has, and it also unlocks fixing cut or incomplete assets that are in our own client files.
- Universal Modder doesn't touch leaked builds (Ethics check), and client art keeps its own permission check.

- [x] Document subscription/local asset-generation options and optional fal endpoints (`Documentation-support/asset-workflow-review-for-Claude-2026-10-13.md`, ChatGPT)
- [x] Check ComfyUI's official model support (FLUX.2 Klein 4B / Hunyuan3D candidates) in the same note (ChatGPT); no local benchmark yet
- [x] Install Universal Modder for Codex (ChatGPT) and Claude Code (Claude), 13 Oct. The fal MCP is idle until a key is added.
- [ ] Claude's written review in the asset note (opinion given to the owner in chat on 13 Oct: start with one static prop; converter first; fal for 3D only)
- [ ] SWG format inventory (C1), then a static-prop converter (msh + sht + dds + apt) proven by round trip; first prop: one original cargo crate
- [ ] Owner developer datapad (adapted from Halyn's public datapad) for spawning and testing our own screenplays
- [ ] **Resource/recipe board** terminal: in-game list of current spawns with stats and survey waypoints. Optionally feed a self-hosted Galaxy Harvester via Bellum's live resource exporter.
- [ ] Our own questline: start small (3-step courier/combat chain on one planet) using `a_screenplay_library/blank_screenplay_base.lua`

## Phase 6: Bots and the AI agent player (in progress)

Goals: (1) **automated regression tests** after every rebuild, (2) make a one-person galaxy **feel inhabited**, (3) an **AI agent that plays and tests**, and (4) optionally a **Discord bridge** for status and chat.

### Architecture

```
            ┌───────────────────────── scenario runner (tools/bots/) ─────────────────────────┐
            │  Phase 1 checks → JSON report in outputs/Bot-reports                          │
            └───────────────┬─────────────────────────────────────────────┬──────────────────┘
                            │ drives                                      │ checks
            ┌───────────────▼──────────────┐                ┌─────────────▼──────────────┐
  Layer A   │ headless client "bodies"     │  SOE protocol  │ Core3 galaxy               │
            │ real bot accounts, non-admin │ ─────────────► │ + /agentpath helper        │
            └──────────────────────────────┘                │   (bot accounts only)      │
  Layer C   in-world "ambient adventurer" NPCs  ───────────► │ AiAgent + behavior trees   │
            (server-side Lua, no network)                   └────────────────────────────┘
```

- **Layer A: headless clients.** Core3's own `core3client` in `--agent-control` mode (C++, dev worktree `src/client/agent/`): JSON commands on stdin, events on stdout. Unreal SWGEmuClient and swgxr's docs are reading material only; Borrie's D20 repo and Progor-Chat are excluded.
- **Layer B: scenario runner.** `tools/bots/phase1.py` (ChatGPT, C3) runs the Phase 1 checks against the test galaxy or live.
- **Layer C: ambient adventurers.** NPCs with player species templates, generated names and wearable loadouts, driven by a behavior tree: travel between city waypoints, hunt, idle in cantinas, short chat lines. Server-side Lua only, easy to switch off.
- **Layer D (optional, later): personality.** Rule-based chatter first; an LLM brain only behind an owner toggle, local-only, rate-limited, off by default.

### Safety rules

- Bots use dedicated non-admin accounts, never the owner. Credentials go in private files (`/opt/swg/agent/`), never in Git or chat.
- Localhost only. Hard cap on bot count. One-switch kill (config flag plus an owner command).
- Server helpers for bots (`/agentpath`) only work for accounts listed in `Core3.AgentAccounts`.
- Ambient NPCs are flagged so they never hold structures, vendors or bazaar items.

### Milestones

| # | Milestone | Done when |
|---|---|---|
| B0 ✅ | Protocol spike | `core3client` logs into our galaxy, zones in, logs out (13 Oct, via Kael) |
| B1 | Smoke bot | One command runs login → chat → relog → verify, with a pass/fail report (part of `phase1.py`) |
| B2 | Scenario runner | Every bot check in the Phase 1 table, one report |
| B3 | Ambient adventurers v1 | 10 NPC adventurers roam Mos Eisley/Coronet with idle, travel and chat behaviors; off switch works |
| B4 | Ambient v2 | Hunting, grouping-looking behavior, city density config, persistence across restarts |
| B5 | Optional | Discord bridge (status + chat); persona chatter |
| B6 | Map new areas (owner, 13 Oct) | Bots survey a planet or town on their own: towns, buildings and cells, terminals, trainers, travel points, NPCs, creature spawns by level, unreachable ground. Written to a shared map file the scenarios use. Hoth is the first real job. Plan: C10 |
| B7 | Test the whole server (owner, 13 Oct) | A coverage matrix links every feature group and profession to a scenario. Runs as a regression suite after each rebuild, with one report. Plan: C10 |
| B8 | Server-side population bots, then the TortoiseBots fork (owner, 15 Oct) | 1,000 client-less bots on the test galaxy, measured ([plan](Documentation-support/server-side-bots.md)); with the new public repo, the bot module moves into a fork of TortoiseBots by Sagiroth ([fork plan](Documentation-support/tortoisebots-fork-plan.md)) |

- [x] C7 unattended scenario authoring (14 Oct, ChatGPT): doctor max-HAM evidence and fresh-kill harvesting added to the squad plan; Python compilation/offline mocks passed, in-game validation pending Claude?s overnight check.

### Track 2: an AI agent that plays a character and learns (owner idea, 13 Oct)

Goal: an AI agent (Claude or ChatGPT) plays its own character, hires companions, runs dungeons repeatedly, gets better through its notes, and writes test reports (bugs, balance, clear times).

```
 Brain: a Claude Code or Codex session the owner starts   ("play a session: clear the Warren")
   MCP tools (swg-agent): status look move_to talk choose command events wait notes report …
        │
 Agent daemon (Python, WSL)        keeps the character logged in between orders; logs every event
   Reflexes                        fight (keep attacking), later heal/flee thresholds, follow, hold
        │
 Body: core3client --agent-control (C++)     real SWG protocol, real non-admin account
        │                                     + /agentpath server helper (navmesh path, ground height)
 Galaxy (Core3)  ── companions: server-side mercenary NPCs
```

- **Session-based play:** the owner starts a session; everything needed to resume lives in files (playbooks, run state, event log).
- **LLM as commander, code as reflexes:** orders minutes apart; deterministic code executes them.
- **"Learning" is memory, not training:** playbooks in `outputs/Agent/notes/`, reports in `outputs/Agent/reports/`.
- **Advantage:** we have the server source, so every packet format is known exactly, and bot-only server helpers replace reverse-engineering.
- **Model-agnostic brain:** Claude or ChatGPT in owner-started sessions first; later a local model (Ollama on the RTX 5070) for unattended runs; optionally a paid API player.

#### Readiness bar before ChatGPT plays (owner, 13 Oct)

ChatGPT waits until Kael can **fight, navigate the world, test dungeons, sample resources and craft**. Each step is built in the dev worktree and proven on the test galaxy before it reaches the live body.

| Step | What Kael gains | Status |
|---|---|---|
| R1 Fight & survive | Planet-change movement ✅, readable system messages ✅, own and others' HAM/posture/states ✅, combat log ✅, `fight` reflex ✅, death → clone ✅ | ✅ dev `a72026b6` (test galaxy); combat build/gear for Kael still to grant |
| R2 Interact | SUI read/reply ✅, radial menus with option names ✅, inventory ✅, vehicle deed → call ✅ (mount unverified), loot (`/loot all`) untested | mostly ✅ dev `e1344def`/`a72026b6` |
| R3 Navigate | `/agentpath` navmesh paths + ground height ✅, into buildings ✅, out of buildings ✗ ("no path"), starport travel planned | in progress |
| R4 Resources | Survey tool via radial + SUI results, `/sample` loop, resource containers | planned |
| R5 Crafting | Schematic, slots, assembly, experimentation, prototype | planned |
| R6 Dungeons | Full runs with mercenaries, loot, death/clone recovery, playbooks | planned |

Session preparation and checks so far:

- [x] Public pre-CU knowledge-source list (`Agent/knowledge-sources.md`, ChatGPT)
- [x] First Kael sessions, two-mercenary follow/dismiss, chat, mercenary cap, ten-minute sweep (ChatGPT, 13 Oct; notes in `Agent/notes/`)
- [x] Staged interaction upgrade (ChatGPT), then reviewed, fixed, built and tested by Claude (dev `e1344def`)
- [x] Sweep findings fixed in dev: NPC speech decoded, stale conversation choices refused, silent Han/greeters (cause: wrong height broke the server's line-of-sight check), "z 180" (a real plateau north-east of Mos Eisley)
- [ ] Promote the new body to live: ChatGPT cross-review (C4) + owner OK; then ChatGPT plays The Beginning
- [x] C4 cross-review of `e1344def`, `a72026b6`, `eebdd99d`, `5c39f411`, `697f2002` and world-boss `bda2c0dd` (13 Oct, ChatGPT). Review in `Documentation-support/review-C4/C4-review-2026-10-13.md`; changes requested, not promotion approval.
- [x] Fix original C4 F1–F3 (total movement deadline, dead/incap path guard, strict 256-point cap): dev `3797430a`/`cde59ec5`, Claude's test-galaxy results, ChatGPT source re-review and compiled cap reproduction (14 Oct).
- [x] C4b + C4c exported-packet cross-reviews (14 Oct, ChatGPT): `Documentation-support/review-C4b/C4b-C4c-review.md`; 3 P1 + 4 P2 findings, changes requested. Runtime checks untested by ChatGPT; fixes and re-review remain before promotion.
- [ ] Mercenary survival across rapid relog (open); failed-command feedback for out-of-range talk (open); mercenary combat assist (now measurable with the combat log)

| # | Milestone | Done when |
|---|---|---|
| A1 ✅ | Body | v0.1 13 Oct (outdoors move, look, say, commands, conversations, events). v0.2 in dev: SUI, radial, inventory, HAM/combat, fight, navmesh paths, indoors |
| A2 | Daemon + reflexes + MCP | Daemon and MCP work from Codex ✅; reflexes: `fight` ✅, heal/flee/hold planned; MCP wrappers for the v0.2 commands after promotion |
| A3 | Brain | Claude or ChatGPT completes a goal ("finish The Beginning quest") via MCP with notes and a run report; a later session resumes |
| A4 | Party | Mercenaries live (hire/follow/dismiss verified); combat assist to verify with the combat log |
| A5 | Dungeon tester | Runs one dungeon repeatedly, improves clear time via the playbook, files bug reports |

## Housekeeping and optimization (owner request, 13 Oct)

Files that grow without limit get slow to read, for us and for the game tools. Rules:

- **Shared docs.**
  - `SWG-handoff.md` stays under about 25 KB: open tasks, the C-task instructions and the newest four log entries. Move finished rows and older entries to `SWG-handoff-archive.md`; nothing gets deleted. Both agents read the board every session, so its size is paid in usage every time.
  - This roadmap is the plan, not a log: one line of status per item, details in the log.
- **Bot reports** (`Bot-reports/`): `squad.py tidy` (also run every 5 rounds of a long run)
  - keeps the newest 20 JSON reports per group and zips older ones by month (`archive-YYYYMM.zip`);
  - keeps 300 lines in each `LOG.md` (older lines go to `LOG-archive.md`) and 30 background-run files;
  - drops the body logs of offline bots.
  Agents read `squad.py last` and `LOG.md`, not JSON, unless a failure needs it.
- **Bots at run time.** Each body is about 12 MB of RAM. A body whose debug log passes 50 MB is logged out and back in between rounds (fresh log). Reads are incremental, so a big log doesn't slow the harness, only the disk.
- **Galaxies.** A galaxy uses about 4.4 GB of RAM. Stop the test galaxy when nobody is testing (`test_galaxy.py stop`), and stop live when nobody plays (as on 13 Oct).
- **To decide (owner OK needed, because it deletes):** a retention rule for `/opt/swg/backups` (e.g. keep the newest 5 plus one a week). Also: clearing old build directories in the dev worktree, and pruning `/opt/swg/agent/logs`.
- **Server performance**, when it matters: triage the 2,537 startup warnings (Phase 2 item), check `/agentpath` cost with many bots (16 so far, fine), and watch zone CPU on the test galaxy during long squad runs.
- **Processes.** `Check Processes.cmd` (`tools/proc_check.py --clean`) reports the galaxies, bots, relay workers and memory. It stops only known-safe leftovers: bot input holders whose client has exited, and scratchpad scripts stuck for more than an hour. The newest report is `Agent/proc-check.md`, with history in `proc-check-history.log`. Claude runs it at every check-in.
- **Agent usage.** See C7 on the board: GPT-6.1 Sol, Medium for squad work, High for reviews. Batch scenarios into one run, and read summaries only.

## Backlog / known issues

- Bot body: out-of-range `talk` gives no failure event; Chewbacca silent; vehicle mount unverified. (Fixed on dev: cell → world paths `5c39f411`/`697f2002`, indoor `look` `3797430a`.)
- Client `/follow` is straight-line steering the server never sees; it sticks on corners (God Mode on the leader makes it worse). Server-side `/leash` is the stopgap (Phase 2).
- 33 unresolved asset paths, mostly JTL ship chassis. Revisit with the JTL acceptance tests.
- `the_tutorial_0001_the_beginning-Clean and formatted.lua` is MTG's unmodified reference copy. It isn't loaded, so it's harmless. Remove it in its own commit if it causes confusion.
- The client needs Run as administrator on this PC (registry access). Investigate a non-elevated fix.
- Debian 13 vs the documented Debian 12: fine so far; note it if a build dependency breaks.

- [x] C7 owner-requested single round (13 Oct 20:17, ChatGPT): all five squads completed in 226 s; 30/35 checks, limitations in Agent/reports/2026-10-13-C7-one-round.md. Further coverage remains open.


- [x] Shared profession/gameplay and installed UM references; feature register and first official planned/cut-content research pass (13 Oct, ChatGPT). Detailed per-box/runtime and release-rights validation remain open.

- [x] KOTOR/mod/open-asset feasibility research (13 Oct, ChatGPT): existing import/export route, original/CC0 shortlist and rights gaps documented; conversion and in-game validation untested (feature register F82–F86).

- [x] KOTOR author/reuse research first audit (13 Oct, ChatGPT): [26 releases and author statements](Documentation-support/KOTOR-mod-reuse-audit.md), RedHawke site history; unresolved original permissions and per-file rights remain open. No imports.

- [x] Additional bounded KOTOR author research (13 Oct, ChatGPT): [30 more entries](Documentation-support/KOTOR-mod-reuse-audit-additional-authors.md), combined 56 releases/resources; per-file rights and conversion remain unverified.

- [x] C4d re-review of dev 5aadc8b9 (13 Oct, ChatGPT): [report](Documentation-support/review-C4d/C4d-review.md); five original findings resolved in source, two partial and one new race; changes requested (2 P1 + 1 P2). Offline route-fallback repro verified; runtime regressions remain untested.

- [ ] C11 archive downloads: owner authorized 13 Oct; blocked by sandbox network at first metadata check. 0 bytes downloaded; archive-downloads.json records pending items.

- [x] C8 MCP wrappers implemented and offline dispatch checks passed (13 Oct, ChatGPT); runtime validation/reload pending Claude, no live promotion.
- [x] C9 three squad scenarios revised, compile + four offline failure-path fixtures passed (13 Oct, ChatGPT).
- [ ] C9 runtime acceptance: nearest destroy mission completion, hospital enhancement, safe harvest receipt (Claude test galaxy).
- [x] C10 Hoth-first mapping design and complete inventory matrix (86 feature groups + 39 profession/track rows); mapping/scenarios are proposed, not executed.

- [x] C12 Hoth adaptation plan:228 hashed source files, per-file targets/gates, cave-ID and balance deviations recorded (ChatGPT,13–14Oct). No port or target-binding/runtime acceptance claimed.
- [x] C14 bounded lore/grid pass:24 records, all11 local-terrain catalogue zones plus stock10 and orientation worlds; Legends preferred/Jakku exception. Unknown details recorded. Follow-up stock UI affine fit rejected; no client edits.
- [x] C13 server SOPs:9 local-tool runbooks and10 ranked gaps; commands inspected, not executed.
- [x] Owner-requested TortoiseBots source/prior WoW brief shared with Claude; main/date tagbc914eb3,VERSIONv6; earlierv3build and limited terrain-cleanup lag result recovered.
- [x] C11 local source audit:7 pins match, tracked clean, per-file hashes saved; downloaded-source review only. A4 per-component terms/A6 excluded-source hold/D1 donor audit open; A7/B/C deferred.
- [x] Original offline squad triage reader + regression fixtures; summarizes saved reports without bot control or new service. Hoth smoke assertion gaps sent to Claude.

- [x] Owner14Oct setting/encounter policy recorded: Legends NJO–Legacy, post-Vong/post-Abeloth/Krayt Empire reference; exact year open. Pre-CU mechanics retained. Server-added encounters remain optional/re-engineering candidates, not discarded by C12 deferral. See Documentation-support/setting-and-encounter-policy.md.

- [x] Historical pre-CU macro-bot research and bounded routine proposal (14 Oct; Documentation-support/pre-cu-macro-bots-and-squad-routines.md). Implementation and runtime verification remain open.

- [x] Python squad cooperative stop/deadline, saved activity status and stronger Hoth ticket/walking assertions implemented14Oct; five offline tests pass. Test-galaxy verification pending.

- [x] Storyteller/NPC/test weapon local inventory and historical/public-SOE documentation pass14Oct;76TRE/690weapon paths/1592versions inspected. Exact live-instance identity and comprehensive official NGE mapping remain unresolved. Documentation-support/storyteller/.

- [x] Weapon authenticity evidence register and all-690-path readable index (14 Oct); all1,592 versions retain name/appearance/hash references.18 highlighted leads; original exceptional-instance stats and Storyteller assignment remain open. [name removed]/[name removed] owner alias leads recorded, no verified public match.

- [x] Bounded Prophecy/[name removed]/[name removed] alias follow-up (14 Oct); public Vision of Hope predecessor lead and access gaps documented. Brother/weapon identity, original stats and official-live galaxy remain unresolved.

- [x] C4e source review (14 Oct, ChatGPT): three original dev patches plus c402e480; changes requested (1 P1 + 1 P2). Runtime/actual client lock audit remain open.
- [x] C15 bounded CC0 art/audio shortlist (14 Oct): 10 creator-source candidates and SWG adaptation plan; no downloads or imports.
- [x] C16 initial fallback chooser/probes and fresh ticket filtering implemented (14 Oct); 15 offline tests passed.
- [ ] C16 test-galaxy acceptance, full travel graph, expanded mapping, profession/crafting coverage; see Bot-reports/fallback-coverage.md.

- [x] C17 Discord layout and webhook posting tool implemented (14 Oct, ChatGPT); 22 offline tests pass, saved-source dry runs checked. See Documentation-support/discord-plan.md.
- [ ] C17 owner setup, private redaction list, reviewed first post and explicit go; real Discord delivery untested.

- [x] C19 / C4f read-only review (14 Oct, ChatGPT): five dev commits + six tools; 2 P2 findings, C4e-F1 resolved in leash; offline checks saved, fixes/runtime acceptance open. See Documentation-support/review-C4f/C4f-review.md.

- [x] C18 reduced independent backport review (14 Oct): 30-object sample; no new P1/P2 established, runtime/migration gates remain. `Documentation-support/C18-backport-sample-review.md`, local commit `6e2e90a`.

- [x] C21 checkpoint 2a (14 Oct): world/place identity and implementation matrix, 25 records/7 fresh article extracts. `Documentation-support/server-world-census.md`; full world lore/dependency audit and overall C21 remain open.

- [x] C23a offline Hoth acceptance scenario + five evidence fixtures (14 Oct); gameplay run underway, full acceptance open.
- [x] C24 release gate checkpoint: NO-GO; 48-row inventory, R2 multi-zone P2 counterexample and four format/arithmetic fixtures. No live approval.
- [x] C25 initial isolated ticket-feedback source patch `5c41ed62` prepared; Claude review/build/runtime pending, not deployed.

## ChatGPT checkpoint, 14 Oct afternoon

- [x] Prepare isolated C26 resource/credit/waypoint/secondary-stat source commits and review protocol notes; unbuilt and game-untested.
- [x] C17 privacy correction: raw text local-only, fixed-vocabulary curated feed, 24 offline fixtures; no posts.
- [x] Authorized farming download checkpoint: 19 retained archives / 414 MB; remaining downloads and five 7z full audits open. No imports.
- [x] C21 species classification checkpoint: 36 biological candidates, two human faction options, two droid options; complete census remains open.
- [ ] Claude review/build/runtime C25/C26 and crew armor/tool prerequisites, then C23 acceptance.


## ChatGPT resource/crafting checkpoint, 14 Oct evening

- [x] C24b resource re-review (15 Oct): `98ad1d1d` + `3a0b154f`; R2-F1 resolved in source, 16 offline checks pass, 74-row inventory refreshed; repeated-start/gameplay gates remain open and release stays NO-GO.
- [x] C29 mechanics + Galaxy Harvester/SWGAide research reference saved; 15-file source manifest and eight client class leads, no installs or gameplay claims.
- [x] Owner TTRPG resource handoff: all 265 existing extracted rows, 28 husbandry and 16 recipe input references listed in clean Markdown and JSON; source/coverage checks pass.
- [ ] Remaining C29 Legends/era material audit and implementation integration, after C24b independent resource-fix review and C23c runtime acceptance; owner-book routes are proposals only.

- [x] C40 roof-height source/offline fix (15 Oct): server `7c68e39f`, h `e86fcf7`; Python 6/6, escort 11/11, selector 7 assertions. Claude review/build/starport recovery and bunker/Warren gameplay pending.
