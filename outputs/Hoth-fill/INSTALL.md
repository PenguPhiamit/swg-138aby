# Hoth fill: what is staged and how to install it

Claude, 17 Oct 2026. **Staged only: nothing installed, nothing run on a galaxy, untested in game.**
Owner, 17 Oct about 9:20 AM: "lets get a session to flush out hoth. using the local models we have". The owner's
answers to the plan cards (17 Oct):

| Card | Owner's answer | What this build does |
|---|---|---|
| What to fill | all four (places, townsfolk, wildlife, quests), and "mid, late and end game planet, no low levels need to be wandering hoth ... a rougher planet" | everything new is level 60-108; the low-level townsfolk stand still inside the starport |
| Echo Base | "Use the NGE building" | the ruin's people inside the E0 building, on its own cell floors |
| Rancor | "option one and two but lower those drop rates a bit" | site and colour as staged in PL-05; respawn 2 hours; rare decor 60% of kills (was 100%), deed 25% (was 50%) |
| The 24 drops | "add what exists, we will rebuild what doesnt later" | **nothing to add: all 25 exist** (below) |

## The "broken" Hoth drops are not broken

`Documentation-support/item-sources-audit.md` lists 25 Hoth loot items whose objects the server lacks. Checked
17 Oct: every one of them, and for the 18 deeds their vehicle control device and vehicle, has a server template in
Core3-dev under `object/custom_content/` (included from `object/serverobjects.lua` line 92) and a client file in the
MTG archives (`mtg_patch_019`/`022`). `tools/core3_audit/item_sources.py` names each object by its file's path
(`object/custom_content/...`) instead of the path in its `addTemplate` call, so it misses all of `custom_content`.
That is a bug in the audit, not in the loot. Whether they drop and show proper names is still untested in game.

## Server patch

`hoth-fill.patch`, 17 files, +993 / -9, against Core3-dev `91cf87ed`. Lua only, so no C++ build.
`tools/build_patch.sh` (WSL, as swgemu; read-only on `/opt/swg`) rebuilds it from the staged tree in `MMOCoreORB/` and
runs the checks: `git apply --check` clean, `luac5.3 -p` clean on all 17 files, and `tools/load_test.lua` (loads the
new files with stand-ins for the Core3 globals: every template a place, lair or spawn group names exists, every
conversation option leads to a screen, every handler exists). The sha256 is printed by the build; the file in the
commit is the one it last wrote.

| Part | Files | What |
|---|---|---|
| Wildlife | `mobile/hoth/hoth_fill_creatures.lua`, `mobile/lair/creature_dynamic/hoth/hoth_fill_lairs.lua`, `mobile/spawn/hoth/hoth_fill_areas.lua`, `hoth_regions.lua`, `hoth_world.lua` (spawn) | Legends Hoth fauna (Wookieepedia, Hoth/Legends, its fauna list): pantran whitefang 82 and stalker 90 (ice cats, packs), Hoth hog 62 and boar 68 (families), ice scrabbler 60 (swarms), icetromper 88 and bull 96 (herds). Stock bodies until there is art: sand panther, zucca boar, womp rat, bolle bol. Three new areas: the vent fields (1800, -700, r 700), the western glacier (-5000, -1500, r 1500), the northern reaches on the way to Echo Base (-3500, 3900, r 900); whitefangs, hogs and scrabblers also join the world spawner at low weights |
| Townsfolk | `mobile/sandbox/hoth_world.lua`, `mobile/conversations/sandbox/hoth_world_conv.lua`, `screenplays/sandbox/hoth_world.lua` | at the Scavenger Starport: Hask Moor, Tavi Renn, Ysa Volt, Medic Orrin Dask, Kesh the pilot, and six who stand about; Brother Tamm at the Scavengers' Camp; Corporal Jeth Ardo at the Rebel Forward Camp |
| Places to find | `screenplays/sandbox/hoth_world.lua`, no-spawn circles in `hoth_regions.lua` | the crashed freighter (-4200, -2600: Lucky Despot debris, looters 76, mynocks, the survivor Dellan Pryce); the Imperial wreck (3800, 1800: Captain Tarsk Venn 94 and five holdouts 82); the Generator Field (-4400, 5400: the destroyed shield generator, AT-AT debris, scrappers 80, a probe droid); the salvagers' camp at Echo Base's main door; Rimefang's hollow (-2400, -5200); the vent hollow (1800, -700: a whitefang matriarch 95) |
| Echo Base | `screenplays/poi/hoth_echo_base.lua` | 33 spawns and the baron in 20 of the building's 41 cells: mynocks in the hangar, Vorn Skarrel's salvagers (78) and cutters (84) through the corridors and upper rooms, wampas in the lower halls, Old Echo (108) in the deep halls under the hangar, Vorn Skarrel (98) in his hall |
| Jobs | `screenplays/sandbox/hoth_world.lua` | Hask Moor: kill Skarrel in Echo Base, bring the command log (7,000 credits and a rare decor roll). Tavi Renn: kill Rimefang (5,000 and a common decor roll). Dellan Pryce at the freighter: tell Ysa Volt he is alive (3,500 and a common decor roll). Each once per character, with a quest waypoint; group members within 128 m get the kill |
| Rancor | `hoth_glacial_rancor_den.lua`, `hoth_glacial_rancor.lua` | respawn 7200 s; drops 60% / 25% |

Positions inside Echo Base are floor-mesh triangle centres of `appearance/echo_base_pob.pob`, in cell-local
coordinates (cells by number with `BuildingObject:getCell`). Outdoor sites were checked for flat ground with
`Fable-hoth-batchA/tools/hoth_survey.py`; heights come from `getWorldFloor` at spawn.

**Local models:** the eight NPCs' lines were drafted by WaifuGemma4 on this PC
(`Agent/local-research/npc-dialogue-hoth/`, 3 chunks, 1.9 minutes) from Claude's briefs, then reviewed and edited by
Claude (the job lines, waypoints and rewards are Claude's). The friend's PC queue had about a dozen topics ahead, so
the run was by hand, as the Ossus one was. No client archive step: nothing here needs client data.

## Install (for the session holding the server lock)

1. Lua only: no archive, no C++ build. Galaxy stopped or at the next restart.
2. `wsl -d Debian -u swgemu -- git -C /opt/swg/Core3-dev apply --check /mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Hoth-fill/hoth-fill.patch`,
   then `apply`, commit on dev, and run `check_lua.py`. If dev has moved past `91cf87ed` and the check fails, rerun
   `tools/build_patch.sh` (it rebuilds against the new HEAD, as long as the 11 edited files' anchors still match).
3. Restart the test galaxy (standing OK only with no owner client running and no squad round in progress).

## Checks after install (untested so far)

- Server log: no `HothWorld: could not spawn`, no `HothEchoBaseScreenPlay: the building has no cell` or `could not
  spawn ... in cell`. If every Echo Base cell fails, the screenplay-placed building has no cells on this server, and
  the interior needs the snapshot route (`Fable-echo-base/README.md`).
- A bot or `/teleport` visit to each site: people and props present, nothing under the ice.
- In the client (the owner): the talkers answer; the three jobs give their waypoint, finish and pay once; inside Echo
  Base the salvagers and wampas stand on floors and move without falling through; the stand-in bodies look acceptable
  for whitefangs, hogs, scrabblers and icetrompers.
- A rancor kill does not always drop a rare decor; loot from the 25 Hoth items shows proper names.

## Later

- Map markers and labels for the new places need keys in the client's `hoth_region_names.stf` and `clientpoi`
  rows: a small archive step, on the owner's OK.
- Real bodies for the four new species.
- Fix `tools/core3_audit/item_sources.py` to read the `addTemplate` path, so `custom_content` objects count.
