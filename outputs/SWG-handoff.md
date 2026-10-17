# SWG handoff board

Shared between ChatGPT and Claude. Rules are in `../AGENTS.md`. Newest log entries first.

## Server lock

**Server lock: Claude: test galaxy, bots and dev tree `/opt/swg/Core3-dev`. ChatGPT owns `/opt/swg/Core3-gpt` (no galaxy ownership). Fable is retired (owner, 16 Oct: Opus 5.5 and GPT 6.1 Sol only). Live galaxy STOPPED. Test galaxy: **run 23 since 3:12 AM 17 Oct** (WSL stopped at 1:22 AM; gate PASS 39/46 at 2:25 AM; crafting check 21/21 at 3:19 AM), optimised core3, dev `fc3bb3e2` (crafting body API and /agentgear resources; missions up to level + 2; `d4b9d9a1` + Ossus O7 regions, Ossus people, spawn gate by creature level, C61 fight-back, starport-pad routes); archive `df1d538e` on client and server (floater v2 → Ossus O7 → Ossus people, on `9ce108a0`: Hutt walk fix, floater, Nal Hutta with Tatooine and Corellia routes; backups `.bak-9ce108a0`, `.bak-503401b4`). BotPop "all" **300** (owner gaming; cap 600), no Ossus explorers; the 7 AM job writes the run23 report set (numbers, findings, travel, morning, planet data). Findings: `Bot-reports/FINDINGS-2026-10-16.md`. Scheduled 17 Oct: Nal Hutta home 1:55 AM, Hoth leftovers 2:00 AM (staged only). **GPT out until 22 Oct 1:13 AM.** Live map on http://localhost:8765. - 2026-10-17 3:20 AM.**

**Overnight 16 Oct (owner, 02:15): the bots are handed to GPT and the local model.** Claude's 5-hour usage is spent until 05:30. GPT (usage back at 03:45) runs C46 (Discord feed and public map, staging only) and then C48 (overnight analysis and the owner's morning sheet). The local model (Ollama qwen3:8b, `tools/agents/local/idle_research.py`, every 5 minutes when idle) keeps researching `Agent/local-research/queue.json`. **Rule: when no agent has usage, the local model researches until usage resumes; anyone may add open topics to its queue.** The test galaxy (run 8: 1,500 multiclass new players + 200 Ossus explorers, dev `8b48a044`) runs unattended; the memory watchdog despawns the bots if WSL memory falls below 2 GB; no restarts until the owner or Claude is back. Fable is paused (owner, 00:05).

**Owner back 16 Oct (afternoon): release track first (Claude); GPT does C55 (done), C56 full-datapad gate, C57 client patch for friends, then C58 (re-review of the C55 fixes); GPT is out of usage until it resets, and `gpt_chain5.sh` retries every 10 minutes.** Run 13 is healthy (1,700 online, ticks ~6 ms). Release plan: `Documentation-support/live-release-1.md` (after C55: a small first release cut from live `920203d8`, not all of dev; owner decides). C55 F1 (helper droid lock order, reached real new players) and F2 (spawn gate removed krayts for solo masters) are fixed in dev `c5d713b8` (built 4:30 PM, not on run 13). C46 reviewed and fixed (`ccf9519`): fit to start; waits for the owner's webhook file and OK.

**Hutt (16 Oct): creation fixed (4:12 PM crash: missing skin palette row and clothing/hair blocks; archive `6ff21312` on client and server). The created Hutt cannot be played** (no movement even locally, no chat, commands or menus; the server is fine, checked with an agent-client Hutt). Our animation table is not the cause (A/B). Likely: the pre-CU client cannot control the Hutt rig as a player (no human bone names, no `hold_l`, no face skeleton). Later tests (6:00-6:45 PM): the owner's **Chiss** could not interact either on today's archives, and works again on the pre-Hutt archive `f1046025` (now on the client). A bisect round then failed and worked minutes later with no change: the interaction loss is **intermittent**: CPU starvation on Miniverse (97% CPU, WSL load 9.7/12 from 1,700 active bots), not an archive file or the server (server radial round trips 0.05 s at 6:56 PM; a probe logs them every 15 s until ~9 PM). The client goes back to the full Hutt archive `6ff21312` at its next restart. Owner, 16 Oct ~7 PM: after the Hutt and this, **test the game end to end before new content** (Claude agrees). Bots run through walls (BotPop moves by position, no building collision). Details: `Documentation-support/hutt-c54.md`, last section. Owner decides next.

(Write `Server lock: Claude — <task> — <time>` or `Server lock: ChatGPT — …` before touching `/opt/swg`; set it back to `free` afterwards.)

## Questions for the owner

Agents add a question here when the owner isn't in their chat: name, time, the options. The owner answers inline. Messages between the agents go in `Agent/to-claude.md` and `Agent/to-chatgpt.md` (AGENTS.md, "Asking questions").

**Claude, 17 Oct 6:00 AM (BotPop social play, `Documentation-support/botpop-social/README.md`; answer inline):**
1. **Factions for bots beyond Imperial and Rebel:** only the two GCW sides for now (recommended; the seven standing-only sides from `Fable-factions` come when their data exists); or the seven new sides too, as standing only, in the same stage; or no factions for bots at all?
2. **Bot guild names:** our own 138-139 ABY list, written by Claude and checked for uniqueness (recommended); generated by Core3's name generator; or names you give?
3. **Bots going overt:** covert only, so real players are never flagged against them (recommended); overt on the test galaxy only, for base and PvP tests; or overt anywhere?
4. **Groups patch (stage 1, off by default):** build it on dev and test with 50% of hunters grouping in the next run (recommended); or hold it until your movement feedback (5:35 AM: "nowhere near looking like an actual population") has been worked on first?

**Claude, 17 Oct 2:30 AM (PL-05 Hoth leftovers, staged in `Hoth-leftovers/`; answer inline):**
1. **Glacial rancor's den site:** the Glacial Rancor Grounds, an open valley at 600, -4600 (staged, no client change); or one cell of the new mynock ice cave; or a second stock ice cave at the grounds (needs a second flatten layer and your OK)?
2. **Rancor colour:** the Chiss skin palette's lightest blue (staged; a true blue, not pastel); or our own pastel-blue palette file (one new `.pal` in the archive)?
3. **Rancor respawn:** 30 minutes (staged, like the cave bosses); 2 hours; or 6 hours? Each kill drops a rare decor item every time and a vehicle deed half the time.

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
    - **Hutt:** a Hutt standing on the human skeleton; acceptable? **Owner, 15 Oct 15:25:** the Hutt has its own skeleton (Claude's correction); it launches as a playable with remapped animations (sit, dance, riding); gear and new animations follow; Fable designs it tonight (`Documentation-support/fable-return-brief.md`, Hutt).
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

**Owner's answers, 15 Oct 15:30-16:10 (Claude's chat, the six open design questions):**
- **Q1, Ossus layout:** keep it; add scorch marks and craters to the ruins (130 ABY attack); add some flat areas for player settlements (terrain flatten layers); add as many lore-friendly POIs as possible. Caves stay on the hillsides until the owner looks.
- **Q2, Ossus creature levels: shelved** until more planets are implemented. A draft level ladder covering the existing and planned planets is in Claude's chat; Ossus keeps its current levels (6-19) for now.
- **Q3, resource uses:** a Smuggler lumni-spice recipe; beskar stays the rare best iron but waits for Mandalore; corusca comes from a GemDiver trader on Yavin 4 (not a ground spawn).
- **Q4, Hoth leftovers (Claude's picks, one change):**
  - density 1024; the glacial rancor in a fixed den with a respawn timer, **coloured pastel or pale blue, ideally the Chiss skin palette** instead of cream;
  - map names for the areas, camps and cave dens;
  - the quest chain also gives a badge and a rare-decor roll;
  - artisan and entertainer terminals at the starport; no lower mission band;
  - delivery points at the camps; a junk dealer at the camps, recruiters at the starport only;
  - tauntaun riding as its own test batch.
- **Q5, art downloads:** CC0 packs approved one at a time; skip the $14 pack; MTG's Mustafar temple ruins only if the catalogue rates them P. **Blender installed** (owner's 14:24 OK, repeated 15:43):
  - Blender 3.6.23 portable at `C:/Users/Pengw/Tools/blender-3.6.23-windows-x64` (388 MB zip from download.blender.org, SHA-256 checked; settings inside its own folder; no system install);
  - NSG SWG Tools 3.1.4 (MIT, our copy in `work/research/nostyleguy_io_scene_swg_msh`) enabled: import and export of msh, mgn, lod and pob, plus skt loading, sat/mgn setup, flr floors and pob rooms, portals and lights;
  - proven by a round trip of our wall model (`Fable-asset-pipeline/converted/fable_ruin_01.msh`: 940 triangles, 2 materials, 1.99 x 0.29 x 1.95 m), whose export has the identical IFF structure (37 records);
  - `export_ans.py` (an animation exporter) is in the add-on but not registered: the starting point for new Hutt animations (level 3).
  - texconv was already at `C:/Users/Pengw/Tools/texconv`.
  - Scripting quirk: the importers loop over `files`, so pass `files=[{'name': ...}]` with `filepath`.
- **Q6, the month's route:** approved as written plus the day's additions (Hutt launch and photo studio in week 2, a KOTOR clean-room planet in week 3, Battlefront-style battles in week 4); `SWG-roadmap.md` updated.
- Also: KOTOR 1/2 places to be rebuilt clean-room (descriptions from public sources and observation only, built with SWG's own art; never KOTOR's files); pilot is the Dantooine Jedi Enclave ruins; then Nar Shaddaa or Taris.

Shared proposal reference: [SWG-feature-register.md](SWG-feature-register.md) — purpose, design maturity and difficulty for all recorded features/candidates.

**Owner's answers, 15 Oct 23:15 (Claude's chat, prompt cards; the launch simulation's reports and Fable's Hutt and Ossus questions):**
- Launch economy: stock starting credits (100 cash, 1,000 bank) with training at x0.25. The test galaxy keeps its test values; from run 6 the simulated players get the launch purse (`Core3.BotPopLaunchCash`, `BotPopLaunchBank`).
- XP: keep 5x; add per-type XP multipliers (code only; nothing changes until a rate is set). Claude builds it overnight for the 06:45 restart.
- Spawns: the level gate and the five spawn-data fixes, yes (dev `b20a46d7`). Bots take missions near their level, yes (same commit).
- Restart: one before bed (run 6, about 23:30, done) and one at about 06:45 after the overnight analysis, with whatever else is approved and built.
- Six active missions: in the next live release once GPT's C44 review is clean; the owner still OKs the release.
- Hutt: Claude picks the species ID; chairs refused until new animations exist; Huttese at creation, yes; **the floater is crafted by Artisans** (not free at creation); Nal Hutta's first look in the same restart as the Hutt check.
- Ossus: craters 2-4 m deep as designed; start with two settlement fields (Westmarch and Knossa Fields); Krayt's garrison on the benchland rim over the ruins; the Vong project fields held until the voxyn content exists.

**Owner's answers, 16 Oct 05:40 (Claude's chat, prompt cards; GPT's C48 morning sheet `Bot-reports/launch-sim/MORNING-SHEET.md` and `Documentation-support/player-cities-research.md`):**
- **Team:** Claude Opus 5.5 and GPT 6.1 Sol only. Fable is retired (its scheduled tasks stay disabled); no Sonnet or Haiku helper fleets. The local Ollama model stays as the idle-research fallback.
- Housekeeping (sheet 1-3): approved as GPT recommended (targeted ignore rules; untrack rotating run output and process checks; queues stay tracked; each author commits their own finished work; nothing deleted without its author).
- Spawns (sheet 4-10): **test all of them** in the next run: T1, T2 and S1-S5 (`Bot-reports/launch-sim/city-spawn-proposals.patch`).
- Ossus (sheet 11-13): accept all: 2 m crater floors, the pod on crater 2, field feather 0.3, POI 17 to the flat foothills (x 1,850-2,450 / y -4,800 to -4,500), and the terrain-driven moves of POIs 5, 6, 8, 9, 10, 16.
- Six-mission live release (27): **hold** until Claude's in-game checks (shared crafting recipes, relog, six missions and the seventh refused, the full-datapad gate).
- Playable Hutt (28): **full build now**, by Claude and GPT only; the owner checks it in the client.
- Multiclass (29): bots heal others for medical XP, the researched buying orders, a real 250-point cap (the server reset 250-point bots to 1,000 in run 8, so run 8's split is void); restart when built.
- AGENTS.md's 'stop the test galaxy when nobody is testing' stays as written (an unattended simulation does not count as testing).
- Player cities: Q1 disposable simulation towns first, persistent ones later from a staff Town Keeper; Q2 a 6-minute simulated week on the test copy only; Q3 bots use at most 30% of a planet's city slots, never on the planet being tested; Q4 political XP grants only in labeled accelerated runs; Q5 bots donate plus logged treasury top-ups, with a no-top-up baseline, upkeep x0.5 kept; Q6 a monthly Home Show / Best Dressed City with a modest credit prize; Q7 test 30 decorations per rank and zero decoration upkeep; Q8 make Clone Lab and Entertainment District work at their configured values; **Q9 the CitiesAllowed guard only: no player cities on Hoth or Ossus**; **Q10 no terrain edits for founding sites**; Q11 a pilot of 10 static event props per city; Q12 era-fitting names and themes from our own lists; **Q13 do not cite Legends or Restoration pages** (remove those citations).

## Task board

**C48 — done ChatGPT, 16 Oct 4:03 AM (Medium): [morning sheet](Bot-reports/launch-sim/MORNING-SHEET.md), [run-8 numbers](Bot-reports/launch-sim/numbers-run8.md), [style/SP and watchdog](Bot-reports/launch-sim/run8-style-watchdog.md); report commit `bc166df`. Active-run checkpoint through 3:59 AM; no bot commands or galaxy changes.**

| Task (from SWG-roadmap.md) | Owner | Status | Notes |
|---|---|---|---|
| **C55: first-release independent non-bot dev review** | ChatGPT, High | complete; changes requested 2026-10-16 16:08 | `fbee3aa`: [report](Documentation-support/review-C55/C55-review.md); open inherited helper P1 + global spawn-gate P2; XP/delivery/city-guard source shortlist; 74 Lua checks pass; gameplay untested; no galaxy actions |
| **C54: review playable Hutt; Artisan floater and Hutt names** | ChatGPT, High review / Medium source | review/source complete; Claude integration pending | `82e52303`, `deb3319e`, `8ebace32` on gpt/c54-hutt-floater (base 26b54813); report/tool `a07d346`, Documentation-support/hutt-c54.md; 1 P1 + 5 P2; client stats/text/builder fixes open; full build/gameplay untested; run 10 untouched |
| **C53: apply accepted Ossus o7 decisions** | ChatGPT, Medium | staging complete 2026-10-16 | `3f64720`; POI 17 (2200, -4725), accepted settings retained; run_all ALL CHECKS PASS (119 s), 90 server references pass; client untested; nothing packed or deployed |
| **C52: owner city answers, source cleanup and M1 probe plan** | ChatGPT, Medium | complete 2026-10-16 | `dc469f8`; excluded citations/sole-source claims removed, Q1-Q13 recorded, ordered M1 plan; documentation checks pass; implementation/runtime untested |
| **C51: approved checkout housekeeping (morning sheet 1-3)** | ChatGPT, Low | complete 2026-10-16 | `a5b7604`; targeted ignores, 45 cached-only removals, author inventory; queues/history/local files kept; 23 ignore checks pass |
| **C50: verify idle-model medic/scout/entertainer XP research** | Claude | superseded by C54, owner 16 Oct | Claude completed the audit while ChatGPT was at its usage limit |
| **C49: Claude Python follow-ups: escort range, doctor reapply, movement evidence** | ChatGPT interactive, Medium | source/offline complete; Claude runtime pending | b5cdbb6; 21 offline checks; C49-python-followups.md; no bot/server actions |
| **C46: Discord feed + public bot map** | ChatGPT, Medium | offline complete 2026-10-16; staged for Claude review | `3150acf`; 53 tests pass + PNG visual/shell syntax checks; public serving/Discord/tunnel untested; nothing started or posted; start/stop docs in `Documentation-support/C46-discord-public-map.md` |
| **C45: C44-F1 crafting recipe fix + mission-type audit** | ChatGPT, High | source/offline complete 2026-10-15 23:46; Claude review/build/gameplay pending | Core3-gpt `gpt/c45-mission-recipes` at `e75794da` (base `40af2c78`); report/checks `dfe81df`, `Documentation-support/review-C44/F1-fix.md`; 12 tests/1,284 model cases pass; unbuilt; full-datapad gate open; run 6 untouched |
| **C44: launch simulation + mission independent review** | ChatGPT, High | complete 2026-10-15 22:57; changes requested | Report `2de5175`: `Documentation-support/review-C44/C44-review.md`; 7 P2 + 1 P3; crafting recipe collision blocks live mission-cap approval; bot cleanup/lifecycle/telemetry and memory measurements open; no server writes, bots, builds or restarts |
| **C43: BF2 2005 battles and AI design** | ChatGPT, Medium | complete 2026-10-15 17:40; research/design only | Report `86f9200`: `Documentation-support/bf2-battles-and-ai-for-swg.md`; Hoth pilot, Core3 mapping and behavior priorities; implementation/in-game untested; no server/bot changes |
| **C42: Fable return prep + housekeeping** | ChatGPT, Medium | complete 2026-10-15 12:45 | Docs 8c795f7; three checked briefs; cleanup proposals unapplied; no server writes/bots/downloads/restarts |
| **Escort crew and crew vendor (owner, 15 Oct)** | Claude | escort mode built, offline tests pass; first live run with the owner pending | Owner: "the dungeon crew was meant to run with me"; "this function can lead into the crew vendor, and future solo features". `tools/bots/escort.py` (generic: any group, any player): follow in formation into buildings, fight the player's target with real rotations, defend, heal the lowest, chat orders (follow, stay, attack, passive, heal, status, dismiss), play data in `Bot-reports/play/` (escort only). Run: `squad.py run scenarios/forn-escort.py --round-minutes 125`. **Next:** travel-following (shuttles), a crew vendor NPC that hires a crew to a player (Dax Venn's mercenary broker is the model), solo-player features. Owner's build for Creature Handler play data: Master CH + Rifleman + Marksman (246) |
| **Remote access + second owner account (owner, 15 Oct)** | Claude | prep done 10:15, docs only; nothing opened or changed; waits for the owner's go | `Documentation-support/remote-access-and-second-owner.md`: ports read from the configs (forward UDP login/zone/ping only; never ORB, status, MariaDB, live map); mirrored WSL with the Hyper-V firewall blocking inbound today; the owner's router and firewall checklist with exact PowerShell; the hairpin catch (a public galaxy address also sends the owner's client and the bots through the router); the friend makes their own account by AutoReg login, then one `UPDATE` to admin_level 15 by the lock holder. Test galaxy first, short window, rules limited to the friend's IP |
| **C39: dev since C34r independent review** | ChatGPT, High | complete; **GPT's five fixes reviewed by Claude and in dev 15 Oct 16:30** (`8a00b08b`, `01b94e13`, `f5462270`, `e5c56727`, `1f8982f3`) plus Claude's follow-up `b9653a73` (/goto back releases the cell lock before switchZone); build and gate after the Forn escort run | 1 P1 / 4 P2 / 2 P3; review-C39.md; five gpt/work source fixes ready for Claude; full build/gameplay/persistence untested; no bots/restarts |
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
| **C26: acceptance telemetry** | ChatGPT | **reviewed by Claude and in dev since 14 Oct 18:09** (`58797fdf`, `788e456f`, `7e6625c0`, `7817437a`, `e9a8a6c0`; no findings); runtime use by the scenarios open | Resource units/spawn IDs, own cash/bank credits, own quest waypoints, Hoth/Ossus planet names; `Documentation-support/C26-telemetry.md` |
| **C25: ChatGPT's server-code worktree** | ChatGPT | first patch **reviewed by Claude and in dev since 14 Oct 18:09** (`7267cf3c`, ticket messages); worktree in use (C39, C40) | `/opt/swg/Core3-gpt`, branch `gpt/work` (AGENTS.md rule). First job: the silent ticket failure while a travel point has no shuttle (`PurchaseTicketCommand.h:132`) |
| **C22: independent Hoth + C4 fix review** | ChatGPT - GPT-6.1 Sol, **High** | complete; **all three findings fixed in dev 14 Oct** (F1 `c046e633`, F2 `54a33063`, F3 `5eb140ce`); re-review and the in-game checks open | `Documentation-support/review-C22/C22-review.md`: 2 P2 + 1 P3; dev `c5f1ae06`, `69eb77fe`, `de1b679a`, `23014f39`, `90f60a81`; h `f0b192e`; report `b4472b8`; gameplay untested |
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
| **C4d: re-review the fixes (`5aadc8b9`)** | ChatGPT | complete; **F1-F3 fixed in dev 14 Oct** (`421adb15`, `9ac7cdcd`; checked by C4e) | `Documentation-support/review-C4d/C4d-review.md`; five original findings resolved, two partial; new cancelled-tick race |
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
| **C4e: re-review the C4d fixes + find/tell + Hoth v1** | ChatGPT | review complete, 14 Oct; **both findings fixed in dev** (F1 `bea94e7a`, confirmed by C19; F2 `90f60a81` and C22-F1 `c046e633`) — GPT-6.1 Sol, **High** | `Documentation-support/review-C4e/README.md` (what to check; patches + full files); queue id `c4e-review` |
| TortoiseBots release + prior WoW knowledge brief | ChatGPT | complete — recovered update/lag history + pinned source brief | Owner requested source plus recovered prior work for Claude; design reference only |
| Hoth atlas-to-client map calibration | ChatGPT | complete — numerical fit rejected; client unchanged | Offline stock UI anchors and C14 grids; no client edits |
| Offline squad report triage | ChatGPT | implemented; offline fixtures pass; saved reports summarized | Original local report reader inspired by TortoiseBots principles; no service or bot control |
| **C15: open-licence textures, materials, sounds** (owner, 14 Oct) | ChatGPT | complete — 10 CC0 candidates; no downloads or conversion | Research only, no downloads. Builds on F85 (Quaternius, Kenney, Poly Haven). See C15 below |
| **C16: bot fallback work** (owner, 14 Oct) | ChatGPT | initial implementation + 15 offline tests pass; Claude runtime acceptance requested; wider coverage open | When a scenario is done or stuck, the group moves on to travel, navmesh mapping, reachability and more. See C16 below |
| **C17: Discord channel for the project** (owner, 14 Oct) | ChatGPT | offline implementation complete — 22 tests pass; Discord delivery untested, awaiting owner setup + go | Layout, posting tool with dry run; the owner creates the server/webhook and says go. See C17 below |
| **C18: cross-review Fable's backport batches 1-2** (applied to dev `0c44d431`, `5c7ae017`) | ChatGPT | review complete — 30-object source/data sample, no new P1/P2 established; gameplay pending | Read-only; `outputs/Fable-backport/` has the diffs and checks |
| **C20: C16b bot recovery and Dorn failed-move handling** | ChatGPT · GPT-6.1 Sol, **Medium** | claimed — 14 Oct; runtime waits for exclusive Esk driver gap | Recovery home from Hoth/Corellia, guard Dorn position errors; Esk-only runtime proof |
| **C19: C4f review of Claude's 14 Oct dev commits and archive tooling** | ChatGPT | review complete; **both findings fixed and re-reviewed by ChatGPT, 14 Oct** (dev `23014f39`, h `f0b192e`) | `Documentation-support/review-C4f/C4f-review.md`; isolated checks pass; gameplay gates remain |
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

## C47 - launch simulation report tools (Medium)

Claimed ChatGPT 2026-10-15 23:50: report/analysis Python tools, offline tests and early run 6 sample only. Claude retains all server/runtime ownership; no restarts or bot commands.

## Log

### 2026-10-17 4:25 AM Claude: local model on the friend's PC: installer, fallback to this PC, shared workflow

- **Commits:** `cb6c487` (installer, server list with fallback, workflow), `f2b63e1` (names delta sweep in the workflow), `54391cd` (the installer pulls every model we use). Another session set up the friend's PC itself at about 4:20 AM with the older manual steps (`c97a500`): Ollama 0.40.5 and qwen3:8b only, plus a firewall rule for the whole subnet.
- **Installer:** `tools/agents/local/friend-pc/install-ollama-lan.ps1` (how-to in `README.md` there, and a private page for the owner to open at the friend's PC). It admits only Miniverse (Private profile, ollama.exe only), offers to switch off the older subnet rule, pulls qwen3.6:35b-a3b, qwen3.5:9b, gemma4:12b, qwen3:8b and gpt-oss:20b, builds gpt-oss-20b-64k, and self-tests each one. `-CheckOnly` and `-Remove` are there too. **It has not been run at the friend's PC yet.**
- **Fallback:** `ollama-url.txt` (gitignored) now lists the friend's PC (qwen3:8b, 32K) and then this PC (qwen3:8b, 16K, with the memory guard). The 32768 in `ollama-ctx.txt` is only a default now, since each line sets its own size. The model is unloaded every 5 requests on the friend's PC too.
- **Workflow:** `Agent/local-model.md`, linked from AGENTS.md: which jobs go there, how both agents queue them (topic fields `model`, `local_only`, `review_by`), and how reports are reviewed.
- **Verified:**
  - 76 offline tests in WSL and 10 chunk-job tests.
  - A real 2-chunk job on the friend's PC: 44 s including the model load. As a draft, qwen3:8b caught a doubled word, missed a misspelling, and flagged one correct line.
  - Over the real network, a server that doesn't answer is skipped after 3.0 s.
  - `idle_research.py status` counts the friend's quiet minutes. The timer starts the first of the 5 open topics there after 10.
- **Not verified:**
  - The installer run (firewall tightening, the downloads, whether Ollama 0.40.5 can pull the qwen3.6, qwen3.5 and gemma4 tags, speed and GPU share).
  - A real fallback with the friend's PC off.
  - A research topic run there.
  - The friend's RAM under long runs. It can't be read from here; the unloads are the only guard.
- **Next (owner):** at the friend's PC, run the installer from the page, and answer yes to switching off "Ollama LAN 11434". After its self-test, Claude switches the friend's line to qwen3.6:35b-a3b at 65536.
- **Owner's call:** the names delta sweep. The checklist below sends it to the friend's PC. The workflow keeps it on this PC, because real names don't leave this PC and the friend agreed to source, bot notes and game text. Nothing is queued until a `names-delta` job exists in `local_jobs.py`.

### 2026-10-17 4:04 AM Claude: going-public check, assets clear; licence, credits and the checklist

- **Assets (whole history, which is what the export publishes):** no image, model, texture, sound, archive or SWG client file was ever committed.
  - The only asset files are ours: the Ossus `.tga` bitmaps and `.ws` snapshots from `tools/ossus_terrain.py`, and `SpeciesColorLock.fx`.
  - Kenney (CC0): only receipts and notices are in git; the Quaternius art (CC0) isn't in git. TortoiseBots: with permission, credited. EiF: reference indexes only.
- **Owner's decisions (17 Oct):**
  - **AGPL-3.0 for the whole repo** (`LICENSE`), with credits in `NOTICE.md` (`01fb0de`).
  - The **SWG×SW5E books and the material extracted from them stay out** of the public copy (export drop list).
  - **MTG: credited and published now**, removed if an author objects.
  - Names: keep credits, whole source links, brother mentions with no name, and the characters Benny and Tulde Dedra. "Bill" (a first name in a quoted comment) is reworded in the export. Decisions are in `work/names-sweep/decisions-2026-10-17.json` (local).
- **Test export build** (local, no push): 347 commits, no dropped paths, no handles or e-mail, messages clean, the SW5E files in no version, LICENSE and NOTICE at the top.
- **Before going public (checklist):**
  1. **Names delta sweep:** the 324 files changed since 15 Oct 11:40 AM. It waits for the local model on the friend's PC (owner: "save it for the local model we are setting up"); Claude or GPT reviews its list.
  2. The owner makes a **fresh public repo** and runs `github_export.py push <new url>`. Then check it on GitHub.
  3. **Purge the old repo** (owner, 17 Oct: "dont forget we need to purge the old github"): after the new one checks out, the owner deletes the old private repo (Settings, Danger Zone, Delete this repository). It may still hold early commits by hash. Check it has no forks first. Claude doesn't delete repositories.
  4. Then the TortoiseBots fork (`Documentation-support/tortoisebots-fork-plan.md`).

### 2026-10-17 2:30 AM Claude: PL-05 Hoth leftovers staged (scheduled run; nothing installed)

Built only what the owner answered (15 Oct Q4; 14 Oct question 9). Folder `Hoth-leftovers/`: `hoth-leftovers.patch` (13 Lua files against Core3-dev `07d9f61e`; `git apply --check` and `luac -p` pass, read-only), `build_hoth_leftovers.py` (chains on the installed `df1d538e`; candidate `work/hoth-leftovers/local_planets-hoth-leftovers.tre`, sha256 `108d4234...`, 178 entries byte-identical, 8 changed, 13 new) and `LEFTOVERS-INSTALL.md` (install order: archive on both sides first, then the patch). Adds: the mynock ice cave with Fable's flatten layer; Hoarfang in a fixed spot with a 30-minute respawn, blue through a `rancor_ice` chain on the Chiss skin palette; badge 141 and a rare-decor roll at the end of Vell's chain; artisan and entertainer terminals plus both recruiters at the starport (recruiters off the camps); deliveries to three camps; map names for the two dens. Density, area and camp names and the camp junk dealer were already in dev. Untested; three owner questions at the top. Tauntaun riding stays its own batch.

### 2026-10-16 16:40 Claude: Hutt crash fixed, C55 answered, release plan, C46 reviewed

- Hutt creation crash fixed and installed (above). C55 F1/F2 fixed in dev `c5d713b8`; C58 re-review queued for GPT. `live-release-1.md` revised to GPT's verdicts (small first release from live; T1/T2/S1-S5 and BotPop stay on test; missions held). C46 (`ccf9519`): a failed minute PATCH retries, previews overwrite, success spacing fixed, no version banner; 56 tests pass. Opus took Fable's content job (`7a99802`): 16 owner questions to bring as cards.

### 2026-10-16 16:28 Claude: Fable's content-design job: ranked backlog and faction plan

- `Fable-backlog/README.md` + `backlog.json`: 73 cut and custom items by theme (71 ranked, Hutt and world boss in flight), client archives surveyed with swgfmt. Top 5: Ossus O7 build, Hoth leftovers, Nal Hutta first look, faction foundation, Ossus people; next to design: faction data, Ossus people, Nautolan/Togruta/Chiss names and profiles. `Fable-factions/README.md`: the 138-139 ABY sides checked on Wookieepedia (Legends), Core3 faction code read-only (dev `a8ece12b`), options A/B/C, recommends A (two GCW sides as Triumvirate and Krayt's holdouts, seven NPC standing sides), 13 owner questions with defaults. Design only; nothing built, run or written under /opt/swg. Board commit includes ChatGPT's finished C55 row and entry (report `fbee3aa`). Oldest Log entry archived.

### 2026-10-16 16:08 ChatGPT: C55 release review complete

- Reviewed by ChatGPT: seven requested non-bot commits; report/evidence `fbee3aa`, `Documentation-support/review-C55/C55-review.md`. Open inherited helper lock P1 and global spawn-gate P2; original Hutt defects already corrected by excluded C54 source. XP, delivery-on-C45 and isolated city guard fit in source; spawn experiments/bot workaround stay on test. 74 Lua checks pass; gameplay/mission/Hutt gates remain untested here. No server writes or galaxy commands. Next: Claude fixes/splits, acceptance, exact release cross-review and owner OK. Oldest Log entry archived.

### 2026-10-16 09:12 ChatGPT: C54 Hutt review and source complete

- Reviewed by ChatGPT: 26b54813/S7, 1 P1 + 5 P2 with failing cases; `82e52303` species/refusals, `deb3319e` Artisan floater, `8ebace32` Hutt names on gpt/c54-hutt-floater; report/client staging `a07d346`. 17 changed/new Lua pass; all 47,406 checked (one unchanged legacy migration error); race-header/LAT/link/archive checks pass. No configured build; full server/gameplay untested. Next: Claude review/cherry-pick, fix client profile/text/builder gates, owner floater visit. Run 10/dev/galaxy untouched; oldest log entry archived.
