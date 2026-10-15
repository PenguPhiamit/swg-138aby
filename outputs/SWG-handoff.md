# SWG handoff board

Shared between ChatGPT and Claude. Rules are in `../AGENTS.md`. Newest log entries first.

## Server lock

**Server lock: Claude: test galaxy, bots and dev tree `/opt/swg/Core3-dev`. ChatGPT owns `/opt/swg/Core3-gpt`. Bot driver: Claude (the 30-minute cycle is paused by the owner, 08:35). Fable never writes to /opt/swg. Live galaxy STOPPED. Test galaxy restarted ~10:05 on dev `bb51ec97` (afflict restore, crew kits, who.json every 2 s) with the Forn crew accounts. Live map on http://localhost:8765 (unit `swg-live-map`) with labels. - 2026-10-15 10:05**

(Write `Server lock: Claude — <task> — <time>` or `Server lock: ChatGPT — …` before touching `/opt/swg`; set it back to `free` afterwards.)

## Questions for the owner

Agents add a question here when the owner isn't in their chat: name, time, the options. The owner answers inline. Messages between the agents go in `Agent/to-claude.md` and `Agent/to-chatgpt.md` (AGENTS.md, "Asking questions").

**Claude, 14 Oct 04:59 (owner stepped away; answer inline when back):**
1. **Overnight allow rule (needed before the next overnight run):** Run now once and choose "Always allow" for `overnight_cycle.sh`, or add `"Bash(bash /c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/tools/agents/overnight_cycle.sh)"` to `permissions.allow` in `outputs/.claude/settings.local.json`.
   - Also deny or close the 03:01 overnight run that is still waiting on a prompt.
   - Consider removing the broad `Bash(cat >> *)` rule in that file.
2. **Hoth loot drops:** 3% common decor (ordinary), 5% rare decor (sergeants and named beasts), 2% vehicle deed (named beasts). Keep these rates? The 18 deeds include non-Hoth vehicles (Anakin's podracer, Sith speeder, Mustafar panning droid): keep them, or trim to Hoth-fitting ones? **Owner, 14:56: keep all 18 deeds.**
3. **Fable's planet:** answered 05:38: **Ossus**. Fable's asset plan (05:54) is in `Fable-planet-test/ossus-assets/README.md`: stock art covers a first playable Ossus at $0. Its section 5 lists 6 owner decisions (second-pass CC0 downloads, a $14 pack that needs the author's written OK, the Blender add-on validation F86, a DDS tool install, stock creature bodies, MTG's Mustafar temple ruins). Its other questions (README section 6) are still open.
4. **Clean-room pilot (F93):** collections or buffs first?
5. **Discord (C17):** set up a webhook whenever you're ready; nothing gets posted before your go.
6. **Fable's backport (applied to dev; revert if you disagree):** (a) Keep the real SOE paths for 1,073 MTG objects that MTG's import had mangled (applied), or go back to MTG's? (b) Wire NGE junk and collection loot into loot groups, or keep it staff-only? (c) Extend the 13 new wearables to new species when they land? (d) Is it worth cracking the disc's TRE v6 format (patch 18+ and the expansion patches), or is 2006 content enough? (e) Keep the Death Troopers prison-guard pants?
7. **First real model into the client (F86; Fable's plan: `Fable-asset-pipeline/README.md`, section 5):** OK to:
   - install Blender 3.6 LTS (free) and the SWG add-on from the copy we already have (MIT);
   - download one CC0 pack (Quaternius Ultimate Modular Ruins);
   - get a DDS tool (Microsoft `texconv`, MIT, no account), or let us try our own writer first?
   Then Claude stages one ruin piece into the test archive and you look at it in the client. Every external art list we have waits on this one test.
8. **Hoth wampa bosses:** corpse loot only (as staged), or a per-player boss reward later (`Fable-hoth-caves/README.md`)?
9. **Hoth mynock den (Fable batch B2, `Fable-hoth-batchB/README.md`):**
   - Option 1: a stock ice-cave building in the mynock fields. It needs one added flatten layer in Hoth's terrain file, which your client loads from our test archive.
   - Option 2: an outdoor den, with no client change.
   - Also: should camps and dens get planetary-map names? That needs map-marker support in the server code first. And vendors at wilderness camps, or at the starport only?
10. **Ossus (Fable's O1 is staged, `Fable-ossus/README.md`):** **Owner, 14:56: yes, put Ossus into the test-session archive for a first look; Ossus is the next content after Echo Base E0.**
    - **Story point:** ruins after 137 ABY with the Jedi gone to ground, or the Temple standing with Jedi hiding inside?
    - **Imperial garrison** (Krayt's Empire) or not? **Jedi encounters** here at all?
    - **Placement:** fares Corellia ↔ Ossus 3000/1750 like Hoth? Galaxy-map spot near Yavin IV?
    - **Look:** region names (Knossa, Academy Benchland, Imhar Canyon, Eocho Mountains, Adega Lake); the benchland/canyon scale; the placeholder globe and loading tiles until the map art.
    - **May Claude put `ossus.trn` into the test-session `local_planets.tre`** for a first look in your client?
11. **Species (Fable's research, `Fable-species/README.md`):** **Owner, 14:56: Chiss first.**
    - **Order:** Chiss first (stock art on the human rig, no art risk), then Nautolan and Togruta (the package's art), then Hutt? Or Hutt, Nautolan, Togruta?
    - **Zeltron:** no Zeltron package exists, only EiF's art (held). Hold it, or try a stand-in (a red-skinned human palette)?
    - **Hutt:** a Hutt standing on the human skeleton; acceptable?
    - **Names and stats:** human random names or our own name tables? Chiss's attribute profile: the package's flat 100s, or a real profile?
    - **Claude decides the technical questions unless you object:** splice only the new entries into today's customization table (not the package's 2016 copy), and let human-rig species wear human clothing through one C++ rule rather than editing 703 wearables.


**Claude, 2026-10-15 00:01 (era content; the owner answered the raid, beskar and coral questions in chat, below):**
1. **Adegan grades:** the five Ossus gems now carry the five grade names, but all have the same ranges. Should kathracite, relacite and danite get lower floors, with pontite at the top (a stated variant)?
2. **Voxyn pets:** Wookieepedia has the last voxyn dying in 28 ABY (clones of one queen; they could not breed). For 138 ABY: invent a tame line grown by Nei Rin's Shapers, or pick another Vong-bred creature?
3. **Ossus flora names** (text only, new spawns only): "Kingwood Deciduous Wood", "Bambwood Evergreen Wood", "Potam Tubers" (potam is our reading). Yes or no?
4. **Ossus solar:** the twin suns give weeks without night. Raise Ossus solar's PE floor (stock 200–600, e.g. to 500–1000)?

Shared proposal reference: [SWG-feature-register.md](SWG-feature-register.md) — purpose, design maturity and difficulty for all recorded features/candidates.

## Task board

| Task (from SWG-roadmap.md) | Owner | Status | Notes |
|---|---|---|---|
| **Escort crew and crew vendor (owner, 15 Oct)** | Claude | escort mode built, offline tests pass; first live run with the owner pending | Owner: "the dungeon crew was meant to run with me"; "this function can lead into the crew vendor, and future solo features". `tools/bots/escort.py` (generic: any group, any player): follow in formation into buildings, fight the player's target with real rotations, defend, heal the lowest, chat orders (follow, stay, attack, passive, heal, status, dismiss), play data in `Bot-reports/play/` (escort only). Run: `squad.py run scenarios/forn-escort.py --round-minutes 125`. **Next:** travel-following (shuttles), a crew vendor NPC that hires a crew to a player (Dax Venn's mercenary broker is the model), solo-player features. Owner's build for Creature Handler play data: Master CH + Rifleman + Marksman (246) |
| **Remote access + second owner account (owner, 15 Oct)** | Claude | prep done 10:15, docs only; nothing opened or changed; waits for the owner's go | `Documentation-support/remote-access-and-second-owner.md`: ports read from the configs (forward UDP login/zone/ping only; never ORB, status, MariaDB, live map); mirrored WSL with the Hyper-V firewall blocking inbound today; the owner's router and firewall checklist with exact PowerShell; the hairpin catch (a public galaxy address also sends the owner's client and the bots through the router); the friend makes their own account by AutoReg login, then one `UPDATE` to admin_level 15 by the lock holder. Test galaxy first, short window, rules limited to the friend's IP |
| **C34r: independent item-kit and affliction review** | ChatGPT, High; Claude integrated | **in dev `90044b8e` and on the test galaxy (07:33); bot probe 41/41 DOTs land, no errors (07:36)** | Report `Documentation-support/review-C34r.md`; cure retest BLOCKED by staging (07:38: tester's inventory full, so no cure pack; allies out of view): C33 follow-up for GPT; gate denials and logout not re-run |
| **C33b: cure staging + science_doctor rerun** | ChatGPT, Medium; finished by Claude | **5 of 7 WORKS** (09:44): curePoison, extinguishFire, cureDisease, healEnhance, revivePlayer; registerWithLocation RAN; healState BLOCKED (dizzy pack not delivered, open) | `tools/bots/scenarios/class-check.py` (`090c1dd`, `8bb6e70`); results in `Bot-reports/Aurek/class-check-science_doctor.json` |
| **C33: owner class check P0/P1** | ChatGPT, Medium; finished by Claude's Sonnet helper | scenario and 52 offline tests committed by Claude (07:4x); runs on Aurek since 04:3x: P0, brawler, marksman, scout, medic, rifleman, pistol, ranger, image designer | `tools/bots/scenarios/class-check.py`, `tools/bots/test_class_check.py`; results per profession in `Bot-reports/Aurek/class-check-*.json` |
| **C24b: R2 idempotence + poolScaleZones re-review** | ChatGPT - GPT-6.1 Sol, **High** | complete 2026-10-15 08:06; R2-F1 resolved in source; release NO-GO | dev 98ad1d1d + 3a0b154f at 90044b8e; 16/16 offline checks, 74-row inventory; repeated-start/gameplay untested; no builds, restarts or bots |
| **C30: six reviewed Ossus fauna + habitat spawns** | ChatGPT, Medium | in dev `80b66e65` (01:40) and on the test galaxy since then; names in archive `8ad04fec` | Six unchanged creatures, six dynamic lairs, three groups/five habitats; a bot visit to each habitat is still open |
| **C32: agent profession kits + squad wrappers** | ChatGPT, Medium | **passed on the test galaxy** (Claude, 01:40: grant, list, refusal, clear, 4/4) | C++ 4a340565 after dev merge 220700d0; gated profession grant/clear/list + Bot wrappers; 7 offline tests pass |
| **C23: Hoth gameplay acceptance** (ChatGPT owns it end to end) | ChatGPT | first pass BLOCKED; normal cleanup 11/11, all home; readiness/telemetry open | Instructions above the log. Scenario `tools/hoth/hoth_gameplay_check.py`, written offline now, run after Claude's next restart; ChatGPT keeps the fail list until it is empty |
| **C24: Hoth release gate** (go/no-go) | ChatGPT | checkpoint complete — NO-GO, 14 Oct; C23/owner/client gates open | Instructions above the log. `Documentation-support/hoth-release-gate.md`; ChatGPT gives the "reviewed by" for any Hoth live deploy |
| **C29: pre-CU resources/crafting + Galaxy Harvester** | ChatGPT, Medium | mechanics/books checkpoint complete; lore pass queued | 265 owner-book material rows + 28 husbandry/16 recipe references; source-backed mechanics and GH/SWGAide briefs; no integration yet |
| **C28: browser planet/squad/fleet monitor** | ChatGPT outside tools/UI; Claude telemetry review/build | owner idea; design scoped, implementation pending | Documentation-support/bot-fleet-browser-monitor.md; F100. Map-first fleet view, optional selected-squad observer video; no service/capture started |
| **C27: player report inbox and agent-to-Discord relay** | Claude server intake; ChatGPT outside tools/review | owner requested; design scoped, implementation pending | Documentation-support/player-bug-inbox-design.md; native Mantis route inspected, no local queue today; F98 |
| **C26: acceptance telemetry** | ChatGPT | source committed; Claude review/build/runtime pending | Resource units/spawn IDs, own cash/bank credits, own quest waypoints, Hoth/Ossus planet names; `Documentation-support/C26-telemetry.md` |
| **C25: ChatGPT's server-code worktree** | ChatGPT | first patch committed 5c41ed62; Claude review/build/game test pending | `/opt/swg/Core3-gpt`, branch `gpt/work` (AGENTS.md rule). First job: the silent ticket failure while a travel point has no shuttle (`PurchaseTicketCommand.h:132`) |
| **C22: independent Hoth + C4 fix review** | ChatGPT - GPT-6.1 Sol, **High** | complete - changes requested, 14 Oct | `Documentation-support/review-C22/C22-review.md`: 2 P2 + 1 P3; dev `c5f1ae06`, `69eb77fe`, `de1b679a`, `23014f39`, `90f60a81`; h `f0b192e`; report `b4472b8`; gameplay untested |
| Creature Handler top-tier build research (owner, 14 Oct) | ChatGPT | bounded pass complete — no game benchmarks | `Documentation-support/creature-handler-top-tier-plan.md`; owner wants all three modes; local build closure verified, improvements proposed |
| Tames discussion (owner, 14 Oct) | Owner + Claude + ChatGPT | open — discussion requested | Note in `Agent/to-claude.md`, 05:49; eligibility, rare/endgame pets, wild vs BE, control budget; no changes approved |
| Whole-server asset/data discovery sources (owner, 14 Oct) | ChatGPT | initial registry saved | `Documentation-support/server-wide-asset-source-registry.md`; supplied Sketchfab/CGTrader, SWAPI, Comlink; individual asset audits pending |
| Farming asset downloads (owner, 14 Oct) | ChatGPT | partial — 14 ZIPs / 391 MB retained, 14 Oct | `Documentation-support/farming-asset-download-queue.md`: 30 source entries, ordered batches; licence/readme/hash audit; Farming-assets/README.md receipts; remainder queued |
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
| **C21: quantify server resources, Legends coverage and implementation possibilities** (owner, 14 Oct) | ChatGPT · GPT-6.1 Sol, **Medium** | open - checkpoint 2a complete: 25 world/place records, 7 fresh lore extracts; remaining lore/dependency audit pending | `Documentation-support/server-resource-and-implementation-census.md`; staged inventory, Wookieepedia comparison, rights/feasibility/gap matrix; no imports or implementation implied |

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

**C23. Hoth gameplay acceptance (owner, 14 Oct: "you can probably give GPT some more responsibility"). ChatGPT owns it end to end: the scenario, the runs, the report and the fail list.** The owner checked the client side today: Hoth loads, stormtroopers and wampas, region names on entry, all 18 map markers in the right places. Nobody has seen these yet: surveying (no minerals until dev `1c4c24fb` is on the test galaxy), harvesting, loot, the missions, Vell's job.
- (1) **Write `tools/hoth/hoth_gameplay_check.py` now, offline.** Reuse `besh-gather.py` (`survey_and_sample`, `harvest`), `esk-hoth.py` (`ride`) and `hoth_content_check.py`; add offline fixture tests as in C20. Checks:
  - (a) On Hoth, outside the outpost, a survey of each class (mineral, chemical, gas, water, flora, energy) lists at least one type. Record every type name and concentration. Mineral and gas must include MTG's Hoth types ("Hothian Steel", "Hothian Reactive Gas" and so on: ten `*_hoth` types in all). A raw or blank name is a FAIL.
  - (b) Sample one mineral: units arrive in the inventory.
  - (c) Kill a tauntaun (250–350 m south of the pad) and harvest meat, hide and bone. Record the types and units.
  - (d) Count the loot over every Hoth kill in the run. This is a note, not a check (3% a kill).
  - (e) The two mission terminals (48, -1996 and 48, -2002) list Hoth missions. Accept one destroy mission and check that its target is on Hoth.
  - (f) Quartermaster Vell's first job end to end: Ria Baxx appears 600–900 m out with a waypoint, two ice mynocks (67) guard her, she hands over the "Salvaged Power Regulator", 1,500 credits on return. If the crew can't win a fight at that level, report BLOCKED with the reason, not FAIL. No staff commands.
  - (g) Come home (C20's return).
- (2) **Run it after my "restart done" note in `Agent/to-chatgpt.md`.** I restart when the owner logs off; that puts `1c4c24fb` and the rebuilt archive on the test galaxy. Driver claim on the board, Esk out of `Agent/squad-plan.txt` for the run and back afterwards.
- (3) **Report:** `Documentation-support/C23-hoth-gameplay.md` (what passed, what failed, the evidence), a log line, and each failure as its own item in `Agent/to-claude.md` with the exact evidence. I fix the server side; you re-run and close the items. The fail list is yours until it is empty or the owner waives an item.

**C24. Hoth release gate (go/no-go). ChatGPT owns it and gives the "reviewed by" line for any Hoth live deploy.** Write `Documentation-support/hoth-release-gate.md`:
- (1) Every commit on `dev` that is not on the live branch `sandbox` (`git -C /opt/swg/Core3-dev log sandbox..dev`, as swgemu, read-only) and touches Hoth or a system it shares, plus the h-side tools that build the client archive. One row each: what it does, its review (C19, C22 or none), its gameplay evidence (the owner's client check, the 13:43 content check 32/33, C23).
- (2) Review the unreviewed ones yourself, as in C22: at least dev `1c4c24fb` (Hoth minerals in the minimum pool), h `2009167` and `c2573e3` (map markers; the archive builder on our own format tools), and Fable's R2 resource backfill when I post it.
- (3) Release blockers that aren't code: owner questions 2, 8 and 9, and how live players get `local_planets.tre`. The live launcher doesn't load it today, and without it a client has no Hoth.
- (4) Verdict: go, or no-go with the list. Nothing deploys without the owner's go anyway; your verdict is what the owner reads first.

**C25. ChatGPT's server-code worktree.** `/opt/swg/Core3-gpt`, branch `gpt/work`, made from dev `1c4c24fb` (rules: AGENTS.md, "ChatGPT's server-code worktree").
- **First job:** `PurchaseTicketCommand.h:132` returns GENERALERROR with no message when the arrival point has no shuttle. That is the "silent" ticket failure in the first 5 minutes after every start (live keeps the stock delay). Send the player a system message (a stock `@travel:` string if one fits, otherwise a plain sentence), and check the departure side for the same gap. One commit, then a note in `Agent/to-claude.md`. I build, test with `--dev-server` and cherry-pick.
- **Next jobs are yours to propose:** from your C22 P3, the C16/C20 findings or the bots' BLOCKED notes. One topic per commit.

**Order for ChatGPT:** C23's scenario (offline, now), then C24, then C25; C21 continues after them unless the owner says otherwise. With usage short, checkpoint after each.

## Log

### 2026-10-15 11:40 Claude (side session): names sweep second half done; local-model background jobs

- **Names sweep, second half (owner asked for Haiku and the local model; GPT's C36 put on hold, `f0584c6`):** all 942 remaining chunks read. Local model qwen3:8b on every chunk (937, plus 2 read by Claude), two Haiku agents on the 162 prose chunks, and a pattern pass for URL usernames and e-mails. **152 new candidates** beyond the first half's list, 16 found by two methods. They are in `work/names-sweep/new-names.json` (git-ignored, local only) for the owner's decisions before going public.
- **The local model is a drafter, not a checker:** on the same prose chunks it found 41% of what Haiku found. Use it for drafts and first passes that something stronger checks, not for privacy, reviews or research a test relies on.
- **Memory cause found:** Ollama keeps each request's KV state in a host-RAM prompt cache (about 0.5 GB per 4K-token request with qwen3:8b). It grew commit by ~15 GB in 25 requests, very likely what crashed the PC at 07:31. New `tools/agents/local/memguard.py`: the local-model scripts unload the model every 5 requests (empties the cache), pause under 6 GB of commit headroom, and idle research won't start under 8 GB. On this PC, `ollama-model.txt` = qwen3:8b and `ollama-ctx.txt` = 16384 (per-PC, git-ignored).
- **Chunk jobs for idle research:** queue topics of `"kind": "map"` run `local_jobs.py` (input and report) and `local_map.py` (one request per chunk, resumable, yields to the owner's client and to low memory). Queued: `bot-gap-list` (192 de-duplicated BLOCKED/NO_EFFECT/FAIL notes sorted into gaps) and `proofread-player-text` (488 strings: our archive strings that differ from stock and MTG, plus messages added on dev since sandbox). Reports land in `Agent/local-research/<id>/report.md` as drafts. **The STOP file is removed**, so idle research runs again when the owner's client is closed; create `Agent/local-research/STOP` to pause it.
- Tests: `test_local_map.py` 10/10 (Windows and WSL); `test_ollama_url.py` 61/61 (one expectation changed: local_agent now unloads the model when it finishes). A 2-chunk live run from WSL worked (lowest headroom 8.6 GB). The full jobs run when the PC is idle; untested end to end through the timer.

### 2026-10-15 11:25 Claude: the crew plays with the owner (Benny); planet jumps, waypoint mail, indoor following, floor plans

- **Escort live with the owner** (as Benny: Master CH + Rifleman + Marksman, `Documentation-support/benny-ch-rifleman-macros.md`, server-best gear macros). Owner chats with Claude in game: `/tell Esk` (Claude watches Esk's log).
- **Dev `0bf4ad1d`, `425e8590`** (test galaxy restarted 10:45): `/agentgear goto` (the crew follows across planets), `mail` (waypoint attachments: the dungeon list), `vehicle` (swoop) and `mandohelmet` kits. Death Watch mines poison anyone without the Mandalorian helmet or an "Advanced Rebreather" in the eyes slot.
- **Pathing** (owner: "the bots are hitting walls"): measured against the bunker's floor meshes, bots stood up to 2.5 m inside walls because escort aimed for formation slots beside the player. Indoors they now walk the player's own path, single file (`30898fe`); outdoors walk timeouts scale with distance and a pinned bot jumps to the player (`3d766d1`).
- **Floor plans** (owner: "actually track them and map the navmesh"): `tools/navmap.py` builds a building's floor plan from the client's floor meshes; http://localhost:8765/floor shows walls, every bot inside with label and trail, the escorted player and stuck spots (`aa213a6`). Built: Death Watch bunker, Warren, Geonosian lab.
- Pets obey trained chat phrases (`PetManager::handleChat`): the 17 "missing" Creature Handler pet orders are trainable commands, not slash commands.

### 2026-10-15 10:05 Claude: wounds fixed (afflict restore); Doctor 5/7 works; dungeon crew Forn; live labels on the tracker

- **Why every Doctor ability was BLOCKED:** the bots carried wounds nothing on the test galaxy removes. Each clone adds 100 per pool (`PlayerManagerImplementation.cpp:1823`), afflict staging adds more, and regen stops at max minus wounds. Jesh had 499 mind wounds of 500. **`/agentgear afflict restore`** (dev `407db849`) clears wounds, shock, DOTs and states and fills HAM; all 18 bots were restored at 09:26, and class-check's `rest()` asks for it.
- **Doctor (C33b), third run:** 5 WORKS (curePoison, extinguishFire, cureDisease, healEnhance +200 in the hospital, revivePlayer on a patient that really died), registerWithLocation RAN, healState BLOCKED (the dizzy pack still did not arrive; open). Setup added (`8bb6e70`): hospital cell for healEnhance/registerWithLocation, a dead patient for revive (third incapacitation), spare copies banked, never dropped. GPT's C33b work committed in `090c1dd`. 69 offline tests.
- **Fixed-scenario round (09:38):** aurek-doctor-buffs **10/10** (it ran no checks before); besh-gather 14/16 (moisture and wind found no concentration); dorn-social 9/12 (Nima's /watch: no line of sight; the known leash miss); cresh-missions offered 36 missions but none it could take (open).
- **Dungeon crew Forn** (owner: "give me a crew and we can test their combat more and their movement and mapping"; `64a83b8`, `b2a3206`): five bots on accounts forn1–5 with full 250-point templates from the server's skill table (Squad Leader/Rifleman, Fencer/Pikeman/Medic, Teras Kasi/Fencer/Medic, Commando/Rifleman, Doctor/Combat Medic). `tools/bots/crew_combat.py` fights with real special-attack rotations; the body's own fight reflex only sends the default attack in melee. New kits onehand/lance/knuckler (dev `0901664a`). Builds, dungeons and monster levels: `Documentation-support/dungeon-builds.md`. Round 1 (`forn-crew.py`) runs after the restart.
- **Tracker** (owner: "relabel the tracker so i can read what everyone is doing ... closer to a live view"): every bot command writes what the bot is doing and its own position (`/var/tmp/swg-bots/now`); the map labels every marker and row, uses the fresher position, refreshes every 1.5 s; who.json every 2 s (dev `bb51ec97`). Readable snapshots in `Bot-reports/tracker/<hour>.txt` (48 h, not in git; bots only).
- **Damage repaired:** at 08:55 a research agent's command overwrote `ActivateQuestCommand.h` in the dev tree with three lines of grep output; restored from git (a copy of the damaged file is in Claude's scratchpad).
- **Valve research** saved in `Documentation-support/valve-open-source-assets.md`: Wine + DXVK runs our client (it is 32-bit Direct3D 9, not large-address-aware); Valve's wiki allows first-party assets in non-commercial fangames (low value for us).
- Test galaxy restarted ~10:05 on dev `bb51ec97` with the crew accounts (owner offline). The cycle stays paused.
- **Escort mode** (owner: the crew was meant to run with them; it can lead into a crew vendor and solo features): `tools/bots/escort.py` + `scenarios/forn-escort.py`, see the task row. The owner wants Creature Handler play data: their build is Master CH + Rifleman + Marksman (246); the escort logs the combat around them to `Bot-reports/play/`.
- **Forn round 1 (10:20): 21/22.** All five templates granted and confirmed, role weapons in hand, hospital buffs +200 (7 of 8; Mirren likely ran out of mind on the last), three kills (13, 6 and 6 s), nobody down; Mirren healed Forn from 29 %. The plateau only had scyks, so the fights were too short to test rotations or the tank: next is harder content (the Warren on Dantooine). Fixed meanwhile: cresh-missions read the empty waypoint of listed missions (`ab0fbbc`), the dizzy pack name for healState (`66aae60`), Nima's /watch line of sight.

### 2026-10-15 09:10 Claude: 13 mechanics reports; scenario fixes from them; relay lanes; C33b taken over (GPT out of usage)

- **Research (owner: "another haiku to research crafting, resources, OQ, and faction", "add the HAM and lacking professions"):** 13 reports in `Agent/local-research/<topic>/report.md`, status review; **start with `Agent/local-research/FINDINGS.md`**. Written by Haiku agents and finished by Opus after a session restart. The first run hung for 40 min because its searches went through the WSL network share (`\\wsl.localhost`); the reruns grep inside WSL.
- **Scenario fixes from them** (`1c301a4`, `adc67da`): cresh-missions accepts destroy missions up to 2300 m (the 600 m bound refused every one), uses general terminals only, follows the moved waypoint and checks the bank payout. besh-gather skips the organic tool (toolType 0 on this server), treats an empty gas/moisture/wind list as server state, and checks mind. dorn-social has a real entertainer buff check (70 s watch). aurek-doctor-buffs walks into any hospital cell (checked live: the trainers stand in cell 9655496) and waits out the 20 s cooldown. **The gate will call the changed checks NEW, not regressions.**
- **GPT relay tuned** (`c403b6b`): a bots lane and a desk lane (one task each), a memory guard (6 GB commit headroom), one retry for an early crash, recovery of orphaned "running" tasks. Status shows lanes and memory.
- **C24b done** by GPT (08:07, `4458b42`). **C33b:** GPT hit its usage limit at 08:59 (resets 12:01) halfway. Claude took it over (63 offline tests pass) and runs science_doctor on Aurek; Aurek stays out of the squad plan until that run ends. Queue: only C36 (names sweep) is open, for 12:01.
- **Remote Ollama** (helper session; `ebadb4f`, and part of `7674330` by a shared-checkout slip): OLLAMA_URL/MODEL/CTX settings, remote idle detection, `tools/agents/local/REMOTE-OLLAMA.md` for the friend's PC (tomorrow). `qwen3:8b` pulled (owner): it runs fully on the GPU, but its research is too weak. Idle research stays paused (`Agent/local-research/STOP`).

### 2026-10-15 08:06 ChatGPT: C24b re-review complete

- Reviewed dev `98ad1d1d` + `3a0b154f` at `90044b8e`: R2-F1 resolved in source, no new blocking source defect; 16/16 offline checks (20,000 multi-zone cases/five loads, rounding/caps/defaults/top-up), inventory refreshed to 74 rows. `Documentation-support/hoth-release-gate.md` stays NO-GO: C23/client/owner gates open. Backfill is conservative migration, not exact creation-time odds (comment clarification for Claude). Repeated-start persistence and gameplay untested here; no builds/restarts/bots/server edits. Next: Claude runtime evidence when scheduled; GPT queue per latest inbox. Review/tools and handoff recorded in this local commit.

### 2026-10-15 08:15 Claude: regression gate; C34r in dev and passing in game; a route for the month; board trimmed

- **Regression gate (route, week 1):** `tools/bots/gate.py` checks the server (running, initialized, dev commit, archive), logs in missing bots, runs one 10-minute round of `Agent/squad-plan.txt` without fallbacks, and compares every check with its own history (`Bot-reports/gate/baseline.json`, seeded from recent reports). A check that passed before and fails now is a regression and fails the gate; flaky, fixed, new and still-failing checks are listed; a scenario with no checks or a BLOCKED note is a WARN line. Verdict: **`Bot-reports/GATE.md`; read it first after any restart.** First gate 08:02: **PASS**, 27/28 (the known leash miss). Aurek's doctor scenario runs no checks at all (BLOCKED: no hospital treatment anchor), so it now shows as WARN. Offline tests `tools/bots/test_gate.py`.
  - **`overnight_cycle.sh` changed** (its header asks for a board note): step 4 runs `gate.py start` once per server start (`gate.py due`) instead of a squad round, and every cycle entry carries a 'Gate:' line.
- **Local model:** owner pulled `qwen3:8b` (5.2 GB): 100% on the GPU at 32K context, 1 GB of RAM (10.6 GB committed, against 22.6 GB for gpt-oss:20b). Its creature-harvest report is weaker (1.7 KB, never opened the C++ file), so it suits light jobs; mechanics research waits for gpt-oss:20b on the friend's PC (tomorrow). Idle research stays paused until then.
- **GPT queue:** C24b (running again since 08:01), then C33b (class-check staging for cures plus the Doctor rerun, owner wants bots first), then C36 (names sweep).
- **C34r** (`19cfb3a5`): reviewed (potency -1 is Core3's own "can't be resisted" path, `DamageOverTimeList.cpp:124-126`), cherry-picked as dev `90044b8e`, built. Test galaxy restarted 07:33 by resume after the 07:01 squad round (no owner client, client config on 44453); `squad.py setup` 18/18.
  - Probe `scenarios/claude-probe-c34r.py` on Aurek: poison, disease, fire and bleeding 10/10 each plus one on self, no errors (`Bot-reports/Aurek/20261015-073623-claude-probe-c34r.json`). The old roll would pass that about once in 9,000 tries.
  - Cure retest (class check science_doctor, 07:38, 11/11 checks): the grant works, but every cure was BLOCKED by staging. The tester's inventory was full, so medicine2 came without its cure-poison pack, and the allies were out of the tester's view ("in another scene") after setup spread them around Mos Eisley. curePoison stays untested: a C33 follow-up (gather the group, make inventory room) for GPT. Aurek driver: ChatGPT C33b (08:31), removed from squad plan; waiting for active rounds before commands.
- **C30** was already in dev as `80b66e65` (cherry-picked 01:40 without -x), so cherry-picking 6f25b704 came out empty. Its names are in archive `8ad04fec`; the habitat visit is still open.
- **C33** committed: the class-check scenario (GPT, finished by the Sonnet helper) and its 52 offline tests.
- **Route for the month** (owner asked how to get the most out of the Max plan in the first month; awaiting the owner's OK): `SWG-roadmap.md`, "Route for the first month". Lanes, waste to cut, four weekly milestones.
- **Board trimmed** from 150 KB to about 50 KB: log entries older than the newest four are in `SWG-handoff-archive.md`. The task board and the C-task instructions still hold about 38 KB; finished rows go next.
- **Windows ran out of memory at 07:31** (commit 50.2 of 51.5 GB, 0.7 GB free; the Ollama runner held 22.6 GB, WSL 12 GB). That crashed GPT's C24b run at once ("memory allocation failed") and very likely restarted this Claude session. Owner, 07:57: the names sweep moves to GPT (C36, after the C24b retry): the local sweep is stopped at 1,037 of 1,979 chunks, the model unloaded, idle research paused (`Agent/local-research/STOP`; delete it to resume). Commit is back to 27 GB. The local model should run on the friend's PC (helper session on remote-Ollama support) or after a RAM upgrade.
- The 07:31 cycle saw the galaxy down mid-restart and wrote its own restart, which (as at 06:35) never ran from the detached shell. Harmless this time; a restart must not overlap a cycle slot (:01/:31; the scheduled-task list's next-run time was stale).

### 2026-10-15 07:09 ChatGPT: C34r review complete

- Reviewed dev 60ed8971 + 9b93665d: one P2 (silent random DOT staging failure), fixed on gpt/work in 19cfb3a5 after dev merge cb4e2b9e; report `Documentation-support/review-C34r.md`. Extracted-code regression: missing DOTs 84/404 -> 0/404, swimming/fire errors 0/101 -> 101/101; 63 kit paths registered. No demonstrated gate bypass/crash defect; full build/in-game checks untested here. Claude: review/cherry-pick 19cfb3a5, build/test; dev, bots and runtime untouched.

