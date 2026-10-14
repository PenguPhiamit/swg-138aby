# Hoth port log

The working record for Phase 3: the first new planet. Newest step last, one entry per step: what was done, the evidence, and what's next. Owner decision, 13 Oct 22:35: **"go, content first, start hoth, utilize UM where applicable."**

## Sources

| Source | What we take | Licence | Where |
|---|---|---|---|
| Mod the Galaxy archives (already collected) | `terrain/hoth.trn` (in `mtg_patch_022.tre`, `mtg_planets.tre`), `snapshot/hoth.ws` (in `mtg_planets.tre`) | MTG reuse statement, with credit | `outputs/Community-content/MTG-assets/` |
| Bellum Gero (`Miphstoe/BellumGero-Live`) | Hoth server scripts (mobiles, caves, POIs, missions, world boss), planet tools in `MMOCoreORB/tools/newplanets` | AGPL-3.0 | `work/research/Miphstoe_BellumGero-Live` (partial checkout, pinned) |
| SWGFlurry (`Thrax989/SWGFlurry`) | Echo Base and Imperial base screenplays (old AI system, so they need porting) | AGPL-3.0 | `work/research/Thrax989_SWGFlurry` |
| Our client (Complete Online Adventures disc) | stock shaders, flora, creatures and structures that Hoth refers to | owner's own install | `outputs/SWG-client/` |

**Not used:** Bellum's private `bg_custom1.tre` (Hoth art ported from another server, not in the repo, provenance unclear) and Flurry's own TRE download. Client art comes only from the MTG archives and our own client.

## How we use Universal Modder

- **The `port-a-mod` method for the server scripts:** pin the source revision; keep an adaptation table (source file → our file, what changed and why: AI templates, API differences, template names); port and test one unit at a time on the test galaxy.
- **The reverse-engineering method** for any client file we have to change: a reader, a writer and a round trip (reader → writer → reader gives the same file) before anything is packed into a TRE.
- **`um win`** for the real-client checks (travel UI, planet map, terrain on screen), only when the owner is at the PC and has logged in.
- UM's `game-research-websearch` is for questions about the original Hoth design. Lore and design facts only, no leaked material.

## Steps

The numbers follow `SWG-roadmap.md`, Phase 3.

| Step | What | Who | Status |
|---|---|---|---|
| 0 | File-format inventory (C1 v1) | Claude | done 13 Oct (`swg-format-inventory.md`) |
| 0.5 | Archive downloads: Bellum, Flurry and tools (C11, section A) | Claude (fetch), ChatGPT (records review) | Bellum done (pinned `1f4438a1`); the rest in progress |
| 1 | Dependency inventory: every file `hoth.trn` and `hoth.ws` refer to, and which of them our client plus MTG archives have | Claude | **done 13 Oct**: terrain and snapshot complete (2 shader names to confirm); creature templates all present except the rancor boss |
| 2 | Client side (pre-check done: Hoth is in none of the six planet-listing files): planet CRC table, `travel.iff`, `planet_n.stf`, ticket UI, planetary map, packed as `local_planets.tre` loading **above** the stock archives | Claude (build), owner + ChatGPT (`um win` check) | **built 13 Oct**; on the test server since 13 Oct 23:05; in the owner's client for test sessions since 14 Oct 02:25. **First real-client try crashed (14 Oct 02:31): the client never loaded the MTG archives; launcher fixed 14 Oct, retry pending** |
| 3 | Server side: zone in config, travel points in `planet_manager.lua`, Bellum's Hoth mobiles, caves, POIs and missions, Hoth resources | Claude | **v1 in dev, running on the test galaxy** (planet entry, regions, travel); **ordinary creatures, lairs and world spawner in dev (c402e480), seen spawning**; caves, resources and reward chains next |
| 4 | Test: travel there and back, terrain, spawns, a cave boss, a mission. Bots: a Hoth smoke scenario plus mapping (C10) | Claude + bots, then the owner in the real client | **travel there and back passes with a bot** (14 Oct, 18/19 checks); terrain heights, spawns, cave, mission still to do |
| 5 | Live deploy (after review and the owner's OK) | Claude | not started |

## Log

### 13 Oct 22:40, Claude: start
- The owner switched the main track to content, starting with Hoth. Bot work now follows content: each piece ships with one smoke scenario.
- Downloads started from WSL/Git Bash, because Codex's sandbox has no network: `tools/archive_fetch.sh`, partial and pinned checkouts, records in `Content-catalogue/archive-downloads.json`. Nothing downloaded is run or installed.

### 13 Oct 22:45, Claude: step 0.5, Bellum downloaded
- `Miphstoe/BellumGero-Live` at `1f4438a129c0e07d05871fccfb2ed30b21da9539`, partial checkout of `MMOCoreORB/bin/scripts`, `bin/conf` and `tools`: 209 MB. The AGPL-3.0 licence is in `COPYING`.
- Found in its tools README: **Bellum's Hoth client files were ported from another server (SWG Infinity) into their private `bg_custom1.tre`.** We use MTG's `hoth.trn` and `hoth.ws` instead. Anything in Bellum's scripts tied to their snapshot (cave cell IDs in `cave_points.py`, outpost coordinates) has to be re-derived from our `hoth.ws`. This goes in the adaptation table.
- Before running anything, I read the Bellum tools we use (`tre_inventory.py`, `iff_tool.py`, `dep_closure.py`, `chain_check.py`): standard library only, read-only, no network. Their paths point at Bellum's machine, so we drive their readers from our own scripts in `tools/hoth/`, run with `python -I`.

### 13 Oct 22:47, Claude: step 1, dependency inventory
- `tools/hoth/hoth_closure.py` follows every reference from `terrain/hoth.trn` and `snapshot/hoth.ws` through our client's real load order (`SWG-client/swgemu_live.cfg`; the MTG archives already load below the stock ones).
  - **487 files: 444 in the stock client, 41 from MTG (mostly `mtg_planets.tre` and `mtg_patch_022.tre`), 2 missing:** `shader/rock.sht` and `shader/snow.sht`, both named by the terrain's shader families. They may be family names the reader took for files; the real-client check in step 2 will show.
  - Full list: `Documentation-support/hoth/hoth-closure.tsv`.
- **Creatures and NPCs.** Bellum's 21 Hoth mobiles use 13 templates; 881 files reached from them (`hoth-closure-mobiles.tsv`).
  - The MTG archives supply the **wampa, snowtroopers and rebel snow soldiers**.
  - The **tauntaun, salt mynock and probe droid** are stock, and so are the human NPC looks.
  - **Missing:** `object/mobile/shared_exotic_rancor.iff`, the Glacial Rancor boss. Use a stock rancor look instead.
  - 16 missing pain and death sound files are named by creature definitions (`.cdf`). At worst those creatures are silent; not a blocker.
- **Conclusion:** our client plus the MTG archives can draw Hoth and nearly all of Bellum's Hoth creatures. No new art is needed for a first playable Hoth.

### 13 Oct 22:48, Claude: step 2 pre-check, client registration
- `tools/hoth/hoth_registration_check.py` checks each file the client uses to list planets, in its winning version:
  - `string/en/planet_n.stf`;
  - `datatables/travel/travel.iff`;
  - `ui/ui_ticketpurchase.inc`;
  - `ui/ui_planet_map.inc`;
  - `misc/planet_crc_string_table.iff`;
  - `datatables/player/waypoint_planets.iff`.
- **None mentions Hoth.** The stock versions win, and the MTG archives add only `datatables/environment/hoth.iff`.
- So step 2 builds our own copies of those files with Hoth added. Method (UM reverse engineering): for each file, read the stock copy, write it back unchanged and prove the bytes match (round trip); only then add Hoth. Tools: Bellum's `stf_tool.py`, `dt_tool.py` and `cstb_tool.py`, plus the `merge_ticket_ui.py` helpers, read before use. Then pack them into a small archive of our own (`local_planets.tre`).
- **Correction to the roadmap:** the new archive must load **above** the stock archives, because a higher searchTree number wins. The roadmap said "lower".
- Putting it into the owner's client (a new TRE plus one line in `swgemu_live.cfg`) needs the owner's OK at that step. The real-client look (travel UI, planet map, terrain) is done with `um win`, with the owner at the PC.

### 13 Oct 22:50, Claude: our Hoth snapshot differs from Bellum's
- `tools/hoth/hoth_snapshot.py` lists MTG's `snapshot/hoth.ws` (from `mtg_planets.tre`): **94 objects, 17 at world level.**
  - **one outpost starport at 0, -2000**, with a cloning facility (-8, -2025), a pirate warehouse (8, -2025), crash debris and a camp;
  - **four ice caves**: `cave_01_ice` (-623, 2292), `cave_02_ice` (-543, 2674), `cave_03_ice` (-75, 2969), `cave_04_ice_s01` (-385, 2436).
- **Nothing is at Bellum's three outpost coordinates** (Scavenger -4010 -2062, Imperial 3840 -3062, Rebel -416 627); those came from Infinity's snapshot. Our Core3 also lacks Bellum's `allowAllDepartures` planet setting.
- **Decision:** lay out our own Hoth around MTG's snapshot. Travel points and terminals go at the MTG starport, placed the way Core3 places Yavin IV's Labor Outpost (the same building), and Bellum's caves and creatures map onto the four MTG ice caves. Other outposts are later additions, built with our own world-builder step. All of this goes in the adaptation table (C12).
- Lore source: Wookieepedia, Legends first (`Agent/knowledge-sources.md` item 13). ChatGPT's C14 gives Hoth's lore and grid square, and the same for the other planets, for the ticket galaxy map.

### 13 Oct 22:58, Claude: step 2, client files built (not installed)
- Round trip first (UM rule): `tools/hoth/hoth_client_files.py extract` + `roundtrip`. All six stock files are rewritten **byte-identical** by Bellum's format tools.
- `tools/hoth/hoth_client_build.py` adds only Hoth; everything else stays byte-for-byte stock:
  - `planet_n.stf`: "Hoth";
  - the planet CRC table: `hoth` = 0x02263558;
  - `travel.iff`: Corellia → Hoth 3,000 credits, Hoth → Corellia 1,750, Hoth → Hoth 100 (the same pattern as Yavin IV, reached only from Corellia);
  - `waypoint_planets.iff`: MTG's `ui_planet_sel_hoth.apt`;
  - the ticket UI: Endor's label, button, 3D planet, map page (`ui_map_hoth`, from MTG) and data source cloned for Hoth, plus its code-data entry. No route line yet;
  - the planetary map UI: Endor's page cloned for Hoth.
- Packed with Bellum's `tre_pack.py`: `outputs/Local-content/local_planets.tre`, 6 files, 14.5 KB. Every file read back from the archive matches its staging copy.
- **Provisional:** Hoth's galaxy-map spot (425, 225) sits in free space on the right of the map, until ChatGPT's C14 grid squares let us place it in proportion to the stock planets.
- **Unknown until the real-client check:** whether the stock client program accepts a new planet button from data alone. Bellum's tooling suggests it does.
- **Not installed anywhere yet.** The client needs the TRE in `SWG-client/` plus a `searchTree` line above the stock archives (owner's OK). The server needs it first in `TreFiles`; the test galaxy comes first.

### 13 Oct 23:02, Claude: step 3 v1, server side (dev worktree, test galaxy only)
- **Bellum's ice caves are MTG's ice caves.** Bellum's cave regions sit at exactly MTG's cave coordinates, so their snapshot is MTG's with the outposts moved (their tools include `move_outposts.py`; the crash debris shifted by the same amount). Bellum's cave content will fit our caves unchanged. For v1 we keep MTG's outpost where it is.
- **Travel point:** the starport's landing pad sits at a fixed offset in the building's own frame (20.3 m, 17.8 m), the same at Yavin IV's two outposts and Dantooine's Imperial one. MTG's Hoth starport faces 180°, so the point is **20.3, -1982.2**. z = 0 for now; the bot reads the real ground height on arrival.
- Dev scripts (`/opt/swg/Core3-dev/MMOCoreORB/bin/scripts/managers/planet/`), both `luac5.3 -p` clean:
  - `planet_manager.lua`: new `hoth` entry with weather and GCW on, the "Scavenger Starport" travel point, and a navmesh area over the outpost;
  - `hoth_regions.lua` (new): edge no-build strips, the outpost as a city ("@hoth_region_names:hothstarport", MTG's string), and a no-build zone over the caves.
- **Server archives:** live's `config-local.lua` already appends the 23 MTG archives (lowest priority), so the server has Hoth's terrain. `local_planets.tre` is copied to `/opt/swg/tre`; live doesn't list it, so live is unaffected. The test galaxy puts it first in `TreFiles` and adds `hoth` to `ZonesEnabled`, through `test_galaxy.py --config`.
- **Server code:** zones are data-driven. Only the resource manager (and FRS/Jedi) hard-code planet lists in C++, so resources on Hoth are a later step.
- **Smoke test:** `tools/bots/scenarios/esk-hoth.py`. Esk flies Mos Eisley → Coronet → Hoth, checks the outpost and the ground, walks a loop and flies back.

### 13 Oct 23:05 to 14 Oct 02:15, Claude: first test-galaxy start with Hoth, and the first trip there
- **Server start:** the test galaxy logged "Ground Zone: Hoth deployed", loaded Hoth's 6 regions and 94 snapshot objects, and started its GCW manager. The only Hoth-related warnings are two MTG collectible templates (`col_hoth_frozen_tauntaun`, `col_hoth_meteorite_01`) that refer to a base template missing from our scripts (`retrieve_quest_base`); they are harmless for now and listed for the creatures step.
- **The starport works without extra objects.** Hoth's snapshot has no terminal, collector or shuttle, but the `outpost_starport` building's own child objects create them, as Bellum Gero's notes say. Esk found a travel terminal (18 m from the pad), a ticket collector (23 m), the shuttle (`player_transport`, 27 m), and a cloning and an insurance terminal.
- **Esk's trip** (`tools/bots/scenarios/esk-hoth.py`, report `Bot-reports/Esk/20261013-231520-esk-hoth.json`): **18 of 19 checks passed in 290 s.** Mos Eisley → Coronet → Hoth (landing at 21, -1983) → a 60 m walking loop on the snow → back to Coronet. Every leg: terminal found indoors, ticket bought, collector used, shuttle boarded.
  - The one failure was the scenario's own outpost check (it looked for names that `look` doesn't report). ChatGPT has since fixed it to accept the starport terminals.
  - Two scenario fixes were needed first, both bot-side: starport travel terminals stand **inside** the terminal building, so the scenario now finds them with the server's search (`locate`) and walks in by cell; and the 8 m purchase range is measured in the cell's own coordinates when indoors.
- **Ground height: 0.0 everywhere Esk walked** (the pad and the four points of the 60 m loop). MTG's outpost sits at height 0, so this may simply be the flattened ground around it. **Checked 14 Oct 02:25: the server reads Hoth's terrain.** Server heights are 44.8 m at 500 m north of the pad, 45.0 m at 2 km east and 3 km west, 163.5 m at the ice caves, and 51.6 m far north (0, 6000). So **the outpost sits on flattened ground at 0, about 45 m below the plain around it**. MTG's snapshot also puts every object within 136 m at height 0. Whether that is a gentle slope or a crater wall is the next check: the scenario now records a height profile every 50 m out to 600 m in four directions, and fails if any 50 m step rises more than 25 m.
- **Travel UI in the owner's client (owner report, 14 Oct, via ChatGPT):** on the test galaxy at Coronet, Hoth isn't in the ticket list. That is expected: `local_planets.tre` isn't in the owner's client yet. Rori and Lok missing from Coronet's list is stock pre-CU: the stock `travel.iff` has no Corellia → Rori or Corellia → Lok fare (Rori is reached from Naboo; Lok from Naboo or Tatooine).
- **Next:** the owner's OK to add `local_planets.tre` to the client for test-galaxy sessions (then a `um win` look at the ticket screen and the planetary map); terrain height probe; then creatures, starting with the wampa.

### 14 Oct 02:20, Claude: the outpost sits in a flat bowl with a cliff to the north
- Server heights every 50 m from the pad (20.3, -1982.2), out to 600 m (`esk-hoth.py`, 14 Oct 02:19 run):

  | Direction | 0–200 m | 250 m | 300 m | 350 m | 400 m | 450 m | 500 m | 550 m | 600 m |
  |---|---|---|---|---|---|---|---|---|---|
  | north | 0 | **43.4** | 38.6 | 35.3 | 34.4 | 37.2 | 44.9 | 35.6 | 28.5 |
  | east | 0 | **22.5** | 23.6 | 26.7 | 31.7 | 37.9 | 44.0 | 38.9 | 32.5 |
  | south | 0 | 8.7 | 16.2 | 15.1 | 10.0 | 10.0 | 10.1 | 10.8 | 10.9 |
  | west | 0 | 5.1 | 13.5 | 15.6 | 20.5 | 28.7 | 39.6 | 39.6 | 33.3 |

- So the terrain's flatten area holds the outpost at height 0 for about 200 m around the pad, then **jumps 43 m within 50 m to the north and 22 m to the east**. South and west rise gently. This is MTG's `hoth.trn` (it came from SWG Infinity, per Bellum's tool notes), not something we changed.
- **Bellum Gero hit the same site and moved it.** Their `tools/newplanets/move_outposts.py` starts from the "pristine Infinity terrain/snapshot". It moves the Scavenger outpost from (0, -2000) to (-4030, -2080), and moves or re-creates the terrain's flatten layers there. Their Hoth therefore ships a changed `hoth.trn` (in a private archive we don't use).
- **To confirm in the real client before choosing:** whether the client draws a cliff there too, or blends it (the client and server read the same file, so a wall is likely).
- **Options for the owner:**
  - **A. Keep it and leave by the south or west.** No client change. Players walk out the gentle sides; the north wall is scenery.
  - **B. Move the outpost to a flatter site,** Bellum's way: a changed `hoth.trn` and `hoth.ws` in `local_planets.tre`, made with their AGPL tools on our MTG copy. That is a client-side terrain change, done with UM's round-trip method.
  - **C. Soften the bowl:** widen the flatten layer's feather where the outpost is, so the edge becomes a ramp. Also a terrain change; a smaller edit than B.

### 14 Oct 02:25, owner decisions
- **Client file:** `local_planets.tre` is in `SWG-client/` (sha256 `45d47575…c7c29c`, the same as `Local-content/`). Only `Play SWG Test Galaxy.cmd` loads it, for that session, at search priority 49: `default_patch.tre` shares 49 but holds none of its six files. `Play SWG.cmd` (live) never loads it. **Untested in the real client:** the ticket list, the galaxy-map button, the planetary map.
- **The cliff: look first.** Someone looks at the bowl's north edge in the real client (the owner, or ChatGPT with `um win` when the owner is at the PC). Then choose: keep it, soften the edge, or move the outpost.
- **Creature levels: keep Bellum Gero's endgame levels.** Tauntauns 65, tauntaun bulls 72, mynocks 67–76, scavengers 62–74, snowtroopers and rebel snow soldiers 76–85, wampas 90, named wampas 105–115, the mynock broodmother 100, and the glacial rancor world boss 400. Hoth is an endgame planet. The squads' beginner bots stay away unless geared and trained for it (C12 acceptance rule).

### 14 Oct, Claude: the owner's client crashed loading Hoth; cause and fix
- **Owner report:** the client crashed while loading into Hoth. The map on the ticket screen was broken, and Hoth wasn't on the galaxy map.
- **Crash file** `SWG-client/SWGEmu.exe-stage.119798-20261014093144.txt` (02:31, 197 s after start, player at Coronet's starport): `FATAL 1e2ed75b: terrain/hoth.trn is not a valid terrain file`.
- **Cause: the client never loaded the 23 MTG archives.** `work/install_community_content.py` appended their `searchTree` lines to the end of `swgemu_live.cfg`, after its `[Station]` header. The client reads `searchTree` only inside `[SharedFile]`, so it ignored them. In that session the client had `local_planets.tre` (the ticket list showed Hoth, so the ticket could be bought), but not:
  - Hoth's terrain and snapshot (`terrain/hoth.trn`, `snapshot/hoth.ws`): the crash;
  - the map image `texture/ui_map_hoth.dds`: the broken map;
  - the planet model `appearance/ui_planet_sel_hoth.apt`, which is what the galaxy map draws: no Hoth there.
- **Why our checks missed it:** `hoth_closure.py` used Bellum's `cfg_priorities()`, which counts every `searchTree` line in any `.cfg` file, whatever its section. So step 1's "the client has every file" was true of the files on disk but not of what the client loads.
- **New check:** `tools/hoth/client_load_order.py` reads the config chain the way the client does: `swgemu.cfg` and its includes, sections, and `maxSearchPriority`. It prints the loaded archives, the ignored lines, and which archive each Hoth file comes from. `--login FILE` checks a session's login file. With the session file the old launcher wrote, the four files above came out as NOT LOADED.
- **Fix, test sessions only:** `Play SWG Test Galaxy.cmd` now writes the 23 MTG lines into the session's `[SharedFile]` block, next to `local_planets.tre`, at the priorities the installer meant (23 down to 1, below every stock archive, so a stock file always wins). A dry run of the launcher's config lines gives CRLF output with no trailing spaces. The new check then finds all ten Hoth files:
  - `hoth.trn` from `mtg_patch_022.tre` (it beats `mtg_planets.tre`'s copy; the server picks the same one);
  - the snapshot, map image and planet model from `mtg_planets.tre`;
  - the six planet-list files from `local_planets.tre`.
- **Format:** MTG's `hoth.trn` is `PTAT` version `0014`, the same as stock Tatooine and Yavin IV, so the client can read it.
- **Live client (`Play SWG.cmd`), unchanged:** it still ignores the MTG lines, exactly as in every live session so far. If MTG objects are ever to show on live (the installer's "MTG Content Library" in the character builder), `swgemu_live.cfg` needs a `[SharedFile]` header before those lines, which needs the owner's OK.
- **Still to see in the real client:** whether the galaxy-map button sits well at the provisional spot (425, 225) inside the 498 × 481 map (ChatGPT's calibration rejected a computed spot); the planetary map; the cliff; and the two shader names from step 1 (`shader/rock.sht`, `shader/snow.sht`; if they are real files, expect a warning, maybe a crash).
- **Watch list from ChatGPT's cut-content research** (`SWG-official-plans-cut-content-and-backports.md`): the Hoth author reported bitmap-region instability at high admin speeds (2017), plus Echo Base and mount caveats (2016). Test Hoth movement at normal speed, and keep bots at walking or running speed there; no speed-boosted traversal.

### 14 Oct 03:30, Claude: Hoth creatures spawn on the test galaxy (dev commit c402e480)
- **Port:** `tools/hoth/hoth_port_mobiles.py` copied Bellum's 19 ordinary Hoth mobiles (stats and levels as published), 11 lairs and the `hoth_world` spawn group into the dev tree.
  - Loot groups our server lacks are removed.
  - The glacial rancor is left out: its body isn't in any archive the client loads.
  - A world-spawner region in `hoth_regions.lua` (SPAWNAREA + WORLDSPAWNAREA, 1024 at most). The outpost's 200 m no-spawn circle is unchanged.
  - Each copied file names its source, licence and changes; Bellum is in `CREDITS-and-sources.txt`.
- **Checks:** `luac5.3 -p` on every file; the test galaxy booted clean ("hoth Loaded 7 total regions").
- **Probe** (`tools/hoth/hoth_creature_probe.py`, bot Esk, observation only):
  - Esk flew Coronet → Hoth and walked out 258–362 m south of the pad.
  - It saw **5 Hoth tauntauns, 8 ice mynocks and 1 greater ice mynock**. Template levels: 65, 67, 76. The bot's `look` doesn't show levels.
  - The level-1 bot was incapacitated, then killed. It was still dead there afterwards (`tools/hoth/hoth_return.py` exists for the walk home).
- **Probe fixes, in my files only:**
  - The bot keeps every SUI page it's sent, and `esk-hoth.py`'s `ride()` can answer an old ticket list. The probe shows `ride()` only the newest list, and boarding then worked first try. ChatGPT has been told.
  - Bot status keeps posture under `me`, so my first "still alive?" check missed the death.
- **Owner in the real client, 03:34:** `/teleportTo Esk` took the owner's own client to Hoth. This is the first real-client Hoth load since the crash fix (`[SharedFile]` in the test launcher), and no crash has been reported.
  - God Mode doesn't stop attacks; `/invulnerable` does. See `core3-command-audit.md`.
- **Next:**
  - the owner's look at the planetary map and the north cliff;
  - caves and resources;
  - Bellum's reward chains (their loot groups) as a later slice.

### 14 Oct 04:15, Claude: terrain scan around the outpost; owner keeps the outpost and the south exit
- **Owner asked:** "are you able to anylze the terrain somehow? find a spot? if not we can soften the slope".
- **Scan:** `tools/hoth/hoth_terrain_scan.py` (read-only). Esk asked the server's terrain for heights on a 50 m grid, 3 km square around the pad: 3,721 points at about 0.2 s each. The 125 m outer ring was only partly sampled before the 15-minute budget ran out.
- **Analysis:** `tools/hoth/hoth_terrain_analyse.py`; map `Documentation-support/hoth-terrain-map.png`; data `tools/hoth/data/`.
  - **The pad is in a flat bowl at 0 m.** Walls rise 200–250 m out: north at an 87% grade (the 43 m cliff), south-west 72%, north-north-east and south-south-west 57%.
  - **The bowl opens to the south:** a 17% grade at most, rising 10 m by 500 m, with no wall. West is walkable too (22%) but climbs 40 m in 500 m.
  - **The north is a honeycomb of ridges and hollows. The south is a broad flat plain at about 10 m.** Best flat, open sites:
    - (270, −2532), 600 m south-south-east of the pad;
    - (−330, −2582), 700 m south-south-west.
    - Both vary under 2 m in height across a 300 m circle and are walkable 800 m in every direction.
- **Owner decision:** keep the outpost where it is and use the south exit. No terrain or layout change; the walls stay as scenery, to revisit with the owner's custom deco. Optional later: a marker or waypoint for the south route.

### 14 Oct 04:25, Claude: Esk's crew on Hoth (owner: "give esk a crew similar to the world boss crew")
- **Crew setup:** trained like Aurek's world-boss crew through `groups.json` (`/agentskill`):
  - Esk: Master Marksman + Novice Rifleman;
  - Tovan: Master Brawler + Novice Swordsman;
  - Lira: Novice Doctor + wound healing (Medic master as prerequisite).
  - All three took the boss kit: composite armor, T-21 rifle or battleaxe, stimpacks.
- **Run** (`tools/hoth/hoth_crew_probe.py`):
  - **Travel:** all three flew to Hoth. With the newest-ticket-list filter, boarding worked for every bot.
  - **Spawns seen:** 7 ice mynocks, 1 greater ice mynock, 4 Hoth tauntauns, a tauntaun bull and three named scavenger raiders (Bellum's NPC lair).
- **Fight:**
  - One ice mynock (level 67) against the two fighters: Tovan landed 9 attacks and Esk 2.
  - Tovan was incapacitated and Esk dropped to 31/900 health; the mynock lived.
  - The crew fell back and all three died near the pad.
- **Finding:** trained boxes don't make a bot strong. The bots are combat level 1–7 with about 900 health, and Bellum's Hoth creatures are level 62–115 (the owner's choice: keep his endgame levels). The world-boss crew design doesn't carry over to Hoth without real levels or buffs.
- **Options (owner):**
  1. Observation-only probes, with bots kept away from spawns.
  2. A stronger test kit: full masters, Doctor buffs, Entertainer buffs.
  3. Lower Hoth levels on the test galaxy only.

### 14 Oct 04:58, Claude: Hoth reward loot (dev commit b7f03b0e) and the object CRC table
- **Owner:** "port Bellum's Hoth reward loot as the next Hoth slice".
- **Inventory** (`tools/hoth/hoth_loot_inventory.py` on Windows, then `hoth_loot_core3_check.py` in WSL; data in `tools/hoth/data/`):
  - Bellum's 9 Hoth groups hold 163 items. Following every template each one needs (loot schematic → draft schematic → crafted object; deed → control device → vehicle) gives 611 templates.
  - Both tools index templates by the path they register, not by file location: Bellum keeps TCG objects under `furniture/hoth/`, and Core3-dev keeps later-era objects under `object/custom_content/`. My first pass looked only at file locations, which made 23 objects look missing that Core3-dev already had.
  - **25 items can be shown by our client.** Core3-dev registers all their templates except two deeds (Organa speeder, Sith speeder; their control devices and vehicles exist).
  - **138 can't yet:**
    - Bellum's own art, ice decor and paintings (10 + 16 + 24), from SWG Infinity via Bellum's private archive;
    - the snowtrooper and rebel snow armour schematics (22). Every armour piece is in our client; only the loot-schematic and draft-schematic objects are missing, so these are worth a later slice with our own client objects;
    - 30 vehicle schematics (the loot-schematic objects are missing);
    - 12 deeds (11 with no client object; the Grievous bike lacks its control device).
- **Ported (`tools/hoth/hoth_port_loot.py`, dev `b7f03b0e`, 54 files):**
  - the 25 items unchanged;
  - groups `hoth_decor_common` (4), `hoth_decor_rare` (3) and `hoth_vehicle_deeds` (18), cut to those items with equal weights;
  - the two deeds under `custom_content`, Core3 style. Their CRLF files keep CRLF: the first run had rewritten them as LF, so I restored and re-ran it.
- **Drops** (our design, easy to change in the script's `TIERS`):
  - ordinary Hoth life (levels 62–90): a common decoration, 3%;
  - the two sergeants and the named beasts (85–115): a rare one, 5%;
  - named beasts (98–115): a vehicle deed, 2%.
  - The deed list is Bellum's and includes non-Hoth vehicles (Anakin's podracer, Sith speeder, Mustafar panning droid); the owner may trim it.
- **Checks:**
  - `luac5.3 -p` is clean on every changed file;
  - a plain-Lua load of the groups and items finds all 25 items, and each group's weights total 10,000,000.
  - **Not tried in game yet.** The owner's test client is open, so there was no restart.
- **Found while checking: the client couldn't name any MTG-only object.**
  - The client names each object the server sends by looking up its CRC in `misc/object_template_crc_string_table.iff`.
  - The winning copy is stock `patch_14_00.tre` (15,792 names). MTG's tables (`mtg_patch_022`/`023`, about 29k names) load below stock, so they never win.
  - This affects the 23 MTG objects above that Core3-dev already had, and any MTG backport.
  - **Fix:** `hoth_client_build.py` now adds a merged table (stock + both MTG tables: 29,358 names, no CRC clashes; every source table round-trips exactly) to `local_planets.tre`, which loads above stock on test sessions.
  - Rebuilt and read back: 7 files, verified. The staging copy is `Local-content/local_planets.tre` (sha256 `da8a9968…b888`). The previous build is saved in Claude's scratchpad.
  - **Not installed yet:** it goes into `SWG-client/` when the owner's client is closed.
  - The live client doesn't load `local_planets.tre`, so live has the same gap. That's for the live deploy step.

### 14 Oct 05:17, Claude: Hoth resources (dev commit 2f205cd2) and the server's archive list
- **No hard-coded planets block it:** the resource planets come from `resource_manager.lua` (`activeZones`), and the C++ list is only a fallback. Bellum also adds `hoth` there.
- **The native pool** (meat, hide, bone, milk, flora, wood, energy and so on) looks up `<type>_<planet>` in `datatables/resource/resource_tree.iff`.
  - MTG's `mtg_planets.tre` has a tree with 50 `*_hoth` rows, but stock `patch_14_00` shadows it: the same problem as the CRC table.
  - MTG's tree also adds 45 Dromund Kaas and about 25 JTL space rows. No active zone would restrict those, so they could leak into ordinary spawns, and I left them out.
- **The fix** (`hoth_client_build.py` → `resource_tree()`): stock's 725 rows keep their values and order, and MTG's 50 Hoth rows go where MTG put them, beside their siblings.
  - Core3 reads the rows in order: the hierarchy comes from the CLASS columns, and the container and random-name columns carry forward from the row above.
  - Ancestors' type counts rise by the Hoth leaves added.
  - MTG's Hoth set lacked solar and wind energy, which the native pool asks every planet for, so both are cloned from Endor. MTG's `resource_names.stf`, which wins in the client, already names all 52.
  - Result: 777 rows, and both source tables round-trip exactly.
- **Dev `2f205cd2`:** `hoth` added to `activeZones`.
- **Server archive list:** the server needs this tree too. `test_galaxy.py` now puts `/opt/swg/tre/local_planets.tre` first in the test galaxy's `TreFiles` by itself. An earlier start had done that through a `--config` option. Live's config doesn't list the archive.
- **Installed (owner's client closed):**
  - server `/opt/swg/tre/local_planets.tre` and client `SWG-client/local_planets.tre`, both sha256 `21c44a0b…2d`;
  - it carries the merged object CRC table and the Hoth resource rows.
  - Restarted the test galaxy at 05:16 with the owner's "restart ok". It runs the dev build: `/spawnStatus`, `/showSpawnRegion`, the leash fix `bea94e7a`, the Hoth loot and resources.
