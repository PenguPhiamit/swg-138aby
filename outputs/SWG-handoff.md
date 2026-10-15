# SWG handoff board

Shared between ChatGPT and Claude. Rules are in `../AGENTS.md`. Newest log entries first.

## Server lock

**Server lock: Claude: test galaxy, bots and dev tree `/opt/swg/Core3-dev`. ChatGPT owns `/opt/swg/Core3-gpt` (C41 packet writer claimed 2026-10-15 12:49). Bot driver: Claude (the 30-minute cycle is paused by the owner, 08:35). Fable never writes to /opt/swg. Live galaxy STOPPED. Test galaxy restarted ~10:05 on dev `bb51ec97` (afflict restore, crew kits, who.json every 2 s) with the Forn crew accounts. Live map on http://localhost:8765 (unit `swg-live-map`) with labels. - 2026-10-15 10:05. Claude (botpop session), 13:55: `/botpop` committed (dev `e6749a9e`, `7f58804d`); this session no longer uses the test galaxy (stopped at 13:51 for the owner's full-fleet run by the main session).**

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

**Owner's answers, 15 Oct 14:24 (in Claude's chat; questions above by set and number):**
- **14 Oct set:**
  - 1 overnight allow rule: not now, the cycle stays paused.
  - 2 Hoth loot: keep the 3% / 5% / 2% rates (and all 18 deeds, answered earlier).
  - 4 clean-room pilot: **collections first**.
  - 5 Discord: still open (the owner sets up the webhook).
  - 7 first model import: **yes to all three**. Install Blender 3.6 LTS and the SWG add-on, download Quaternius Ultimate Modular Ruins (CC0), get texconv. Then Claude stages one ruin piece for the owner to view.
  - 8 wampa bosses: corpse loot now, a per-player boss reward later.
  - 9 mynock den: **the ice-cave building** (Option 1, with the added flatten layer in Hoth's terrain in the test archive). Map names and camp vendors were not asked.
  - 10 Ossus: an **Imperial garrison, yes**; **rare hidden Jedi** encounters.
    - Fares **cheaper than Hoth** if Ossus is further from endgame.
    - **All planets should sit where they really are in the galaxy: a rework of the galactic map may be in order** (see C14's coordinates and the rejected Hoth atlas fit).
    - Story point, owner 14:24: **the ruins version.** The academy was ruined in the 130 ABY attack, Krayt's garrison holds Ossus, and a hidden sanctuary under the ruins is where the rare Jedi are met.
  - 11 species:
    - order: Chiss, Nautolan, Togruta, then Hutt;
    - Zeltron held;
    - a Hutt on the human skeleton is **not acceptable**: hold Hutt until it has a proper body;
    - **our own name tables and a real attribute profile**.
  - 6 Fable's backport:
    - (a) keep the SOE paths. The owner asked whether this is a problem; it is a fix, not a problem.
    - (b) wire the NGE junk and collection loot into loot groups.
    - (c) extend the 13 wearables to the new species.
    - (d) yes, work out a read-only TRE v6 reader.
    - (e) the prison-guard pants stay staff-only.
- **15 Oct set:**
  - 1 adegan: real tiers (kathracite, relacite, danite lower; pontite at the top).
  - 2 voxyn: a new tame line regrown by Nei Rin's Shapers, possibly breedable once traditional line breeding works.
  - 3 flora names: yes.
  - 4 Ossus solar: raise the PE floor to 500-1000.

Shared proposal reference: [SWG-feature-register.md](SWG-feature-register.md) — purpose, design maturity and difficulty for all recorded features/candidates.

## Task board

| Task (from SWG-roadmap.md) | Owner | Status | Notes |
|---|---|---|---|
| **C42: Fable return prep + housekeeping** | ChatGPT, Medium | complete 2026-10-15 12:45 | Docs 8c795f7; three checked briefs; cleanup proposals unapplied; no server writes/bots/downloads/restarts |
| **Escort crew and crew vendor (owner, 15 Oct)** | Claude | escort mode built, offline tests pass; first live run with the owner pending | Owner: "the dungeon crew was meant to run with me"; "this function can lead into the crew vendor, and future solo features". `tools/bots/escort.py` (generic: any group, any player): follow in formation into buildings, fight the player's target with real rotations, defend, heal the lowest, chat orders (follow, stay, attack, passive, heal, status, dismiss), play data in `Bot-reports/play/` (escort only). Run: `squad.py run scenarios/forn-escort.py --round-minutes 125`. **Next:** travel-following (shuttles), a crew vendor NPC that hires a crew to a player (Dax Venn's mercenary broker is the model), solo-player features. Owner's build for Creature Handler play data: Master CH + Rifleman + Marksman (246) |
| **Remote access + second owner account (owner, 15 Oct)** | Claude | prep done 10:15, docs only; nothing opened or changed; waits for the owner's go | `Documentation-support/remote-access-and-second-owner.md`: ports read from the configs (forward UDP login/zone/ping only; never ORB, status, MariaDB, live map); mirrored WSL with the Hyper-V firewall blocking inbound today; the owner's router and firewall checklist with exact PowerShell; the hairpin catch (a public galaxy address also sends the owner's client and the bots through the router); the friend makes their own account by AutoReg login, then one `UPDATE` to admin_level 15 by the lock holder. Test galaxy first, short window, rules limited to the friend's IP |
| **C39: dev since C34r independent review** | ChatGPT, High | complete; changes requested 2026-10-15 | 1 P1 / 4 P2 / 2 P3; review-C39.md; five gpt/work source fixes ready for Claude; full build/gameplay/persistence untested; no bots/restarts |
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

## C40 ? roof-ledge pathing (Medium)

ChatGPT source/offline complete; Claude review/build/gameplay pending. Server fix `7c68e39f` (gpt/work, dev merged first); h implementation/report `e86fcf7`. See `Documentation-support/C40-roof-ledge.md`. C40 source slice idle; Claude retains dev/runtime lock and bot driver. No bots/build/restart by ChatGPT.

## C41 - bot net-status packet (Low to Medium)

Claimed ChatGPT 2026-10-15 12:49: owned gpt/work source and offline packet test only; Claude reviews/builds/game-tests. No bots or restarts.

## Log

### 2026-10-15 14:45 Claude: first outside-art prop staged (F86): a CC0 ruined wall, in the test archive, ready for the owner to look at

- Done: Blender 3.6.23 (portable, official site, hash matches), the SWG add-on, texconv and the Quaternius Ultimate Modular Ruins pack (CC0, via the author's Drive folder; the per-file links hit Drive's quota, the folder's Download all worked) are in; recorded as F86a/b/c in `Content-catalogue/archive-downloads.json`. `Wall_Broken` (976 triangles) converted to `.msh`, `.apt`, two `.sht` and two DXT1 `.dds`, and added to the client's `local_planets.tre` (166 -> 173 entries, read back exact, reference closure OK; previous archive saved as `Local-content/old-client-local_planets.tre.8ad04fec`).
- How the owner sees it, no server change or restart: the piece replaces the stock campfire log's appearance, so `/createSpawningElement spawn object/static/structure/general/campfire_fresh.iff` in a test session shows the wall. Steps: `Fable-asset-pipeline/how-to-view-first-ruin.md`.
- Findings: the pack has no texture atlas (two flat material colours, no UVs), so the textures are flat colours; the exporter writes no collision (walk-through), as the plan expected. Not done: own object template, CRC entry and server Lua (needs a restart by the galaxy owner), LODs, a stone texture.
- Not verified in the real client yet. Any session that rebuilds `local_planets.tre` from its own staging drops these files: re-run `Fable-asset-pipeline/stage_ruin.py` (inputs in `Fable-asset-pipeline/converted/`).

### 2026-10-15 14:00 Claude: test galaxy restarted for the full fleet (owner: "restart and ... deploy the full fleet")

- Restarted 13:5x on dev with `BotPop=true` (ready in 66 s, 0 error lines). The botpop scale series (owner OK earlier) was stopped at its 500 step for this; its 100 and 250 results stand (`Bot-reports/botpop-scale-test.md`).
- Up now: 23 squad bots, the Forn escort run (20261015-135721, waits up to 3 h for Benny), 77 load bots (`load_fleet.py step 77 60 7200`: 2 h of fights with the memory guard), and the server-side population at 500 throttled, going to 1,000 only if the load average stays under 9 of 12 threads. Results: `/var/tmp/swg-bots/load/*fullfleet*`. Client logs over 200 MB are emptied every 5 min for 4 h.
- Earlier today: the crew answers every order, Mirren's heal loop, Forn's crouch (`dd9febe`); `/tame train` (dev `398744b5`); the pet follow gap (dev `57a52553`) is live since 13:26 but untested in game.
- **Full fleet result (14:05):** 100 client bodies + 500 server-side bots (165 active, throttled). core3 3.9 cores avg (4.7 max), 4.8 GB; WSL 10.1 GB free, commit headroom 9.3 GB; chat 107 ms avg, 450 ms max; no safety stop. Load average reached 10 of 12 threads, so it held at 500 and did not go to 1,000: CPU binds first, as projected.
- Open: Benny's "disengaging scripts brok" (asked in game, no answer yet); "better zoom" (client side).

### 2026-10-15 13:55 Claude: server-side population bots (/botpop), milestone 1 built; 100 and 250 measured

- Owner's go 13:00 (Claude weekly usage 83%). Dev `e6749a9e` (SuiPageData::sendTo null guard) and `7f58804d` (`/botpop`), both on the test galaxy since 13:39. All bot code is in `src/server/zone/managers/botpop/` (header-only, movable into a TortoiseBots fork). Core3 hooks: the command registration, the observer flag (AiAgent insert/disappear, SpawnArea position update) and `ClientlessLogin.h`, the one login/logout boundary. Sagiroth's TortoiseBots is the design reference; no code copied.
- `/botpop spawn N [here|mos_eisley|coronet|split] [radius] | despawn [N|all] | status | mode [all|throttled]`; `_test` database plus `Core3.BotPop = true`, then god mode or an AgentAccounts account. Bots are transient `Popbot<n>` player characters with no client, rows or account; they wander the navmesh, sit, emote, fight back. Throttled mode: only bots near a real player (150), a rotating 50 and fighters act, and they don't wake AI or spawns. All mode: every bot acts and counts as a player. One `[BotPop]` line a minute in core3.log.
- Measured (throttled, split Mos Eisley/Coronet, 23 squads idle): 100 bots: 1.26 cores, 4.57 GB; 250 bots: 2.03 cores, 4.78 GB (4.52 GB with none); about 0.005 cores and 1.4 MB per extra bot; chat round trip 80 ms; no errors. Report: `Bot-reports/botpop-scale-test.md`; driver `tools/bots/botpop_scale.py` (load_fleet.py's sampler and memory stops).
- **Not done:** 500 and 1,000, the all mode, the 30-minute 1,000-bot hold and the class check alongside. The main session stopped the series at 13:51 for the owner's full-fleet run; it uses `botpop_scale.py` with BotPop on. About half the walk attempts find no path (not investigated). Escort run: halted twice for /botpop restarts (owner OK) and restarted each time until 17:47.

### 2026-10-15 13:50 Claude: name filter: only non-name words stay out (test galaxy)

- Owner: "non name names can stay out, but censors can begone". Core3's active name list (`oldFilterWords` in `bin/scripts/managers/name/name_manager.lua`) matched every entry anywhere in a name, case-insensitively, so plain entries like "ec", "ct", "dev", "gm", "mod", "christ" and "ass" refused Rebecca, Hector, Victor, Devon, Sigmund, Modesto, Christopher and Cassandra (23 of 319 common names). The unused `filterWords` list was worse (refused Jesse, Felix, 4 bots; let GM and Dev through).
- Dev `d1cd02c6` (Lua only, appended to name_manager.lua): the default table is rebuilt from stock. Profanity, slurs and religious names dropped; ranks, titles, species, staff and game words kept as reserved; canon names kept as fiction; plain words match whole words only; Admin, Administrator and Moderator added. Offline: 1 of 319 real names refused (Carl, a stock canon entry), no bot name, no swear word. Stock list kept as `stockOldFilterWords`.
- **On the test galaxy now** without a restart (console `reloadmanager name`: 634 -> 466 patterns). Not yet tried in game with a character name. Live needs the owner's deploy OK.
- 13:50, owner: "Allow canon names too". Dev `0f045a47`: the default table keeps only stock developer and reserved entries (whole words), the non-name words stock filed as profanity, and Admin/Administrator/Moderator: 71 entries. Offline: no real name (319), bot name (100), canon name or swear word refused; every non-name word refused. The test galaxy (restarted by another session at 13:48) loaded it at 77 s: `Loaded 71 regex filter patterns`. Slurs now pass too; the owner was told.

### 2026-10-15 13:18 Claude: fleet-scale test, 100 bots run comfortably (recommend up to 100)

- 23 -> 50 -> 100 bodies fighting on Tatooine/Naboo/Corellia: core3 0.89 -> 1.22 -> 1.49 cores, 4.76 -> 4.87 GB; bodies 1.28 GB RSS (370 MB PSS) at 100; WSL MemAvailable never under 10.0 GB, commit headroom never under 11.6 GB; chat round trip flat 81 ms; no lag lines. No galaxy restart: the load bots need no AgentAccounts, so the Forn escort run kept going. Report `Bot-reports/fleet-scale-test.md`.
- New `tools/bots/load_fleet.py` + `load-groups.json` (77 plain bots, Grek-Qek, kept out of groups.json). Watch for long big runs: each fighting body writes ~2 MB/min of client log to /var/tmp (12 GB/h at 100); `load_fleet.py down` deletes them.

### 2026-10-15 13:07 Claude: plan to fork TortoiseBots with the new public repo

- `Documentation-support/tortoisebots-fork-plan.md` (`7128ade`; roadmap row B8). Fork Sagiroth's TortoiseBots on GitHub when the new public repo is made. The fork's `main` mirrors upstream; a `swg` branch holds our Core3 module in a new `swg/` folder, pinned as a submodule in the new repo. Core3 keeps only the hooks and builds with the module off.
- Port only Sagiroth's original AGPL work for now: the host boundary, `BotTurnScheduler` and `ActionFailureBackoff`. The engine waits on TortoiseBots' open licence audit (its `cmangos/playerbots` lineage is unresolved). The attribution term needs credit in `core3.log`, at login and in `/bot about`. A fork of a public repo is public, so every push gets the export checks. Owner decisions: fork name, submodule vs in-tree, and whether to ask Sagiroth about the engine files.

### 2026-10-15 13:05 Claude: the bot tracker is now a fleet dashboard (http://localhost:8765)

- The owner sent three screenshots of a WoW bot dashboard as the look they want. `tools/live_map.py` now has a sidebar and six pages:
  - **Overview:** bots online, players, bots indoors, issues and squads.
  - **Bots:** all 100 roster bots (groups.json plus the fleet test's load-groups.json). Search takes fields such as `planet:naboo prof:rifleman doing:stuck squad:forn role:healer`, with Online/Offline, state and profession chips. Click a bot to see species, professions, combat role, planet and area, what it is doing, health/action/mind bars, credits, target, gear, XP grants per hour, and an Activity tab (recent labels, refused commands, falls). "Show on map" centres the map on it.
  - **Map:** each planet's own map image, decoded from the client's `ui_map_<planet>.dds` and cached in `/var/tmp/swg-bots/mapimg` (not in git). Planet tabs and area chips with counts, dots coloured by profession with a legend, a path-trails toggle, and "N bots indoors" linking to /floor.
  - **Activity:** each squad's state and every change of a bot's label. **Issues:** stuck now, dead or incapacitated, refused commands (squad reports, last 24 h; escort play data). **Server:** uptime, who.json, and core3.log error lines with repeats folded and IPs removed.
- Bars, credits and target need a small `tools/bots/squad.py` change (same commit): a bot now publishes them from its status and fight replies. Running squads pick it up on their next start; until then the panel says "not reported".
- Labels, /floor, the tracker logs and the 1.5 s refresh are unchanged. All assets are inline (no CDN). Tests: `tools/test_live_map.py` 11/11. Tracker restarted 13:05 as a plain background process (log `/var/tmp/swg-bots/live_map.log`), not the `swg-live-map` unit. Nothing under /opt/swg was written.

### 2026-10-15 12:57 Claude: research: what 1,000+ bots would take (server-side bots)

- `Documentation-support/server-side-bots.md` (`ef46438`), research only. WoW playerbots scale because each bot is an in-server player with no socket, and by default only about 10% are active. Our one-client-per-bot design tops out in the low hundreds (estimate; the fleet test is measuring it). Core3 already drops packets sent to a player with no client. The gaps are a client-less login, a driver, an active-bot budget and one unguarded `SuiPageData::sendTo`.
- Recommendation: a hybrid. Real-client squads stay for tests; server-side bots provide population. Milestone 1 is about 5 days on Core3-dev: `/botpop spawn N`, a wander and fight-back tick, the active budget, then measure 100 to 1,000 bots. Nothing is built; it needs the owner's go-ahead.
- 13:00 (`4d14de7`): Sagiroth's TortoiseBots is now credited by name as the comparison point. The owner says Sagiroth gave permission and has no SWG ties. A correction from TortoiseBots' own source: it ships with every bot fully active and throttling is opt-in, so the gain comes mainly from bots living inside the server with no client. Milestone 1 now measures both modes.

### 2026-10-15 12:49 ChatGPT: C40 roof-floor source fix ready

- Server `7c68e39f` on gpt/work after dev merge `7df4f2c7`; h `e86fcf7`: nearest outdoor floor, route-relative samples, explicit world-z forwarding, safe missing-height errors and escort trail-floor preservation. Report `Documentation-support/C40-roof-ledge.md`. Offline: Python 6/6, existing escort 11/11, compiled actual selector 7 assertions; old 9.5-vs-5 choice reproduced with synthetic surfaces. Unbuilt/game-untested; Claude reviews/cherry-picks/builds and verifies roof descent plus bunker/Warren escort. No bots, restarts, deployments or downloads. Source slice idle.

### 2026-10-15 12:45 ChatGPT: C42 Fable return prep complete

- Docs commit `8c795f7`: `Documentation-support/fable-return-brief.md` (18 folders, 842 words), `owner-decisions-for-fable.md`, `board-housekeeping-1015.md`. Checked dev HEAD `398744b5`, README/owner-answer records and archive hashes: installed client/server both `8ad04fec`; Local-content copy remains `aee83cc6`. Chiss played; E0 visual/habitat/full gameplay acceptance UNVERIFIED. References/CRLF checked; no downloads, bots, restarts or writes under /opt/swg. Next: owner decision batch, then Fable design and delegated mechanical checks. Housekeeping proposals unapplied; oldest 11:40 log preserved in archive, newest four retained. Board/log record committed separately.

### 2026-10-15 12:40 Claude: the crew answers every order; Mirren's heal loop and Forn's rubber-banding fixed; /tame train

- **Owner in game, 12:15-12:25: "things dont seem to be working", "Forn is rubber banding kinda bad".** Three bugs, all in `tools/bots/` (`dd9febe`):
  - Orders were heard, but only the leader (Forn) could answer them, and he skipped any line another bot heard first. Benny's heal, buff and status got silence. Now the bot that hears an order answers it, and a tell gets a tell back. `invite` is queued for the leader, the only one who can invite. New order `help` (also `commands`, `orders`) lists the orders. `passive` now also sends `/peace`.
  - Mirren sent heals 65 times at a patient she could not see, and 19 times at herself with only wounds left. She never stopped "healing", so the buff order never ran. Now a refusal leaves that patient alone for 15-60 s, and low mind rests her for 20 s; she buffs or fights in the meantime.
  - Forn was crouched, and the server puts a crouched bot's steps back. Every bot now stands before walking.
  - Tests: escort and combat 12/12 (4 new), class-check 70/70. The crew run restarted with the galaxy (run 20261015-123727) and waits up to 3 h for Benny (`ESCORT_WAIT`, `36a249f`). Esk mailed Benny a one-line note with a waypoint to the crew.
- **`/tame train` (owner, in game: "can you train my pets"; dev `398744b5`, live: test galaxy restarted 12:36, ready in 86 s, 0 error lines, Benny offline):** god mode, no target. Every called pet learns every command it has no word for yet:
  - the doc's words: sic, heel, stay, guard;
  - plain words for the rest: store, friend, follow other, trick one/two, patrol, patrol point, clear patrol, wedge, column, special one/two, ranged, group, transfer.
  - Words Benny trained are kept. God mode also always passes the training roll when training by hand.
- **Owner's notes from play, open:**
  - pets need a follow distance that depends on their size (the AI's follow range is in `ai/bt/leaf/FollowActions.h`, `UpdateRangeToFollow`);
  - better camera zoom in and out (client side);
  - "disengaging scripts brok" (asked in game which: the crew not stopping, or Benny's macros).

### 2026-10-15 12:39 ChatGPT: C39 review complete

- Reviewed 90044b8e..81384b90: 1 P1 / 4 P2 / 2 P3; report `Documentation-support/review-C39.md`. Source fixes on owned gpt/work after merge 22408da4: d8c9d668, 1b276fa4, 6647e5f8, b556c061, a9fb5cfe (Claude review/cherry-pick in that order). Offline gates, 432 medical cases per pack, paging/stale-cell Lua checks and six Lua syntax checks pass; restored files match baseline blobs. Full server build/gameplay/restart persistence untested. Dev/runtime/bots untouched; later dev 398744b5 is outside scope. Source slice idle; next: Claude review and separate acceptance. Older logs moved to the archive; newest four retained.
