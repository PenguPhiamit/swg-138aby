# Nal Hutta life (PL-06): townsfolk, wildlife, places to find, a kajidic job, resources

Claude, 17 Oct 2026, morning. **Staged only, nothing installed, untested in game.** Core3-dev was only read, through
script files.

**Why.** After walking run 25 (about 6:10 AM), the owner said: "nal hutta works, better than expected. but also feels
empty". They picked four fixes: townsfolk, more wildlife, places to find, and "dungeons and or quests". The main session
also asked for Nal Hutta's missing resources.

This batch sits on top of PL-04 (dev `7be8837a`, archive `f0191ab5`). PL-04 is described in `nal-hutta-home.md`.

## What changed

### Townsfolk in Bilbousa (`screenplays/sandbox/hutta_life.lua`)

The new screenplay is a stock `CityScreenPlay`, the same patrol and standing code Mos Espa uses.

- **Walking:** 10 people on five street routes.
  - Seven are stock commoners and NPCs.
  - Three are a kajidic watch (Weequay). They walk but never fight.
  - The routes are the avenue, the bazaar, the cantina, and the east and west kajidic seats.
- **Standing:** 24 people about the town. Each spot draws a stock commoner (Tatooine commoners, Nikto, Twi'lek
  attendants) or now and then an NPC (trader, pilot, noble, smuggler's cargo hand and so on), as stock cities do.
- **People who talk:** five townsfolk with their own lines.
  - Teeso, a Rodian trader;
  - an old Weequay, who points at the swamp sites;
  - Lyssa, a Twi'lek attendant;
  - a swamp beggar, who points at the Kessoth job;
  - a Nikto dockhand.
- **Two Hutt retinues:** Orruba Kessoth and Gorga Dromuul. Each Hutt has two Gamorrean guards and a Twi'lek attendant,
  and will say a line through the attendant.
- **The cantina:** two dancers doing Oola's dance from Jabba's palace (stock mood `themepark_oola`), plus eight drinkers
  in the main hall.
  - The cantina is Darklight's own (a stock `cantina_tatooine`), so it has the same cells as the one in Mos Eisley.
  - The positions are the Mos Eisley cantina's.

**Layout.** `nal-hutta-life/tools/make_life.py` lays everything out and writes `hutta_life_places.lua` and `life.json`.
- The routes are found on a 2 m grid of free ground (A*). The tool avoids Darklight's buildings, PL-04's statics and
  PL-04's people, with every footprint padded 1.2 m.
- Each route is then thinned to the corners whose straight legs stay clear.
- Standing spots are at least 3 m apart and 2.5 m clear of everything.
- Problems: none.

### More wildlife (`mobile/spawn/hutta/*.lua`, `hutta_regions.lua`)

- **Higher spawn limits.** Each of PL-04's three swamp rings gets a higher limit: the near ring 48 -> 96, the lowlands
  64 -> 112, the deep swamp 64 -> 96.
- **Wandering packs.** Each ring's group gains four packs of stock creatures that roam between the lairs:

| Ring | Levels | Added (stock `creature_dynamic`) |
|---|---|---|
| near, 650-1,600 m | 19-26 | swamp tusk cats, rot mites, borgle packs, fynocks |
| lowlands, 1,600-3,200 m | 31-38 | guf drolgs, leviasqualls, diseased sharupats, jungle fynocks |
| deep swamp, 3,200-5,200 m | 40-52 | savage guf drolgs, midnight vir vurs, mutated kahmurras, veermok marauders |

### Places to find

There are five sites out in the swamp. Each one stands on dry, flat ground that `tools/find_swamp_sites.py` found: the
lowest point is at least 77 m (the water is at 75 m) and the relief is at most 2.5 m over a 22 m radius. No terrain
edits. Every spawn point at a site is dry.

| Site | Where (from Bilbousa) | Art (stock) | Who is there |
|---|---|---|---|
| Smugglers' camp | (-1267, 756), 950 m south-west | Naboo swamp rat camp | smugglers, guards, a Weequay enforcer, **Vekk Tano, smuggler chief** (24) |
| Burned freighter | (493, 1956), 1,300 m east | a starship wreck and a burned cargo hulk | looters and their boss |
| Spice den | (-2747, 2556), 2,240 m north-west | Tatooine spice fiend den | spice guards, bruisers, addicts, **Kreeg, the Nikto spice baron** (36) |
| Old ruins | (373, 36), 1,890 m south-east, on a 108 m rise | Naboo ruins | a kajidic dig team and their dig master |
| Rival kajidic camp | (-2467, -44), 2,350 m south-west | Tatooine Hutt assassin camp | a Bessolo hit squad |

- **Loot:** the stock loot of these NPCs. The two named foes roll Weequay, thug and (Kreeg only) Aa'kuan tier-1 loot.
- **Respawns:**
  - site NPCs: 5 minutes;
  - Vekk: 10 minutes;
  - Kreeg: 15 minutes.

### The quest: the Kessoth job

Bezzik, the Kessoth majordomo, stands by the Kessoth seat's door at (-658, 1628). I chose a quest over a dungeon
because stock caves sink into hillsides: the Hoth mynock cave needed a terrain patch (flatten plus mouth exclusion), and
terrain edits need the owner's OK.

The job has four steps, with a yellow waypoint at each:
1. **The smugglers' camp.** Kill Vekk Tano. His papers show the smugglers never had the spice.
2. **The wreck.** Walk into the burned freighter, within 25 m. You find the manifest: the spice went to Kreeg.
3. **The spice den.** Kill Kreeg.
4. **Back to Bezzik.** The reward is 6,000 credits and a Kessoth crew vest (stock `vest_hutt_gang_s01`).

How it works:
- Kills count for the killer and for any group members within 128 m who are on that step.
- The job can be done once per character.
- The state is kept in the player's screenplay data.

### Resources: why Nal Hutta had none, and the fix

**Cause.** `resource_manager.lua`'s `activeZones` never named `hutta`. The spawner therefore gave Nal Hutta nothing,
and the test galaxy logged `backfillZones: hutta is not in activeZones, ignored`.

That alone wouldn't have been enough. Water, flora, creature and energy resources are planet types: each planet has its
own leaves in `resource_tree.iff`, such as `water_vapor_rori` or `meat_herbivore_rori`. Core3 restricts each one to the
planet whose name follows the underscore (`ResourceTree::setZoneRestriction`). Nal Hutta had no such types.

**Fix, in two parts:**
1. **The Lua patch** adds `hutta` to `activeZones`, with a comment saying why. Minerals, gas and chemicals then reach
   Nal Hutta, and the backfill gives it a fair share of what is already in spawn at the next start.
2. **The archive step** `nal-hutta-life/build_nal_hutta_life.py` adds the planet types.
   - Darklight's Nal Hutta was made from Rori's terrain, so Rori's 45 planet rows are cloned as `*_hutta`, for example
     "Nal Hutta Water Vapor" and "Nal Hutta Wild Meat".
   - It uses Ossus's own merge (Fable O4's `merge_resource_tree`, which cloned Dantooine), and 77 ancestor type counts are
     raised.
   - **Base:** `work/chain-1017/local_planets-chain-1017.tre`, sha256 `f0191ab5…`, 201 entries. The step checks the sha.
   - **Candidate:** `work/nal-hutta-life/local_planets-nalhutta-life.tre`, 5,308,921 B, 201 entries.
     - **sha256 `b01e9f44aeba99f2ceb9878d1328792da0707a53dba3f30de4e657ea66e47f87`** (also in the `.sha256` file beside
       it).
     - 200 of the base's 201 entries are byte-identical. Only `datatables/resource/resource_tree.iff` changes, from 845
       rows to 890, and every old row is kept.
     - The report is in `nal-hutta-life/checks.json`.

**Side effect.** `poolScaleZones` scales each galaxy-wide type's planet count by active zones / 10. With 13 active
zones instead of 12, each type lands on slightly more planets.

### The server patch: `nal-hutta-life/core3-dev-nal-hutta-life.patch`

The patch is against Core3-dev HEAD `7be8837a`. It changes 8 files and adds 4, with 977 lines added and 5 removed.

- **Changed:**
  - `hutta_regions.lua`;
  - `resource_manager.lua`;
  - the three spawn groups;
  - the include lines in `screenplays.lua`, `mobile/serverobjects.lua` and `mobile/conversations.lua`.
- **New:**
  - `screenplays/sandbox/hutta_life.lua`;
  - `hutta_life_places.lua` (generated);
  - `mobile/sandbox/hutta_life.lua` (12 templates);
  - `mobile/conversations/sandbox/hutta_life_conv.lua`.

**Checks:**
- `tools/make_patch.sh` builds the patch from `git show` copies, runs `git apply --check` (passes) and runs `luac -p` on
  all 12 files (passes).
- `tools/server_check.sh` writes `server-check.txt`: **121 checks pass and 0 fail.** It confirms that every mobile, lair,
  object template, loot group, conversation and Lua call the files name exists in dev or in the patch, and that the new
  names clash with nothing.

No C++ change, so no build is needed.

## Install order (for the session that holds the server lock)

1. **Check first.**
   - You hold the server lock.
   - No owner client is running.
   - No squad round is running (`pgrep -f "squad.py run"`).
   - The owner has OKed the restart.
2. **Server scripts.** As swgemu:
   - `runuser -u swgemu -- git -C /opt/swg/Core3-dev apply /mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Fable-species/s7-hutt/nal-hutta-life/core3-dev-nal-hutta-life.patch`
   - Commit it with `Agent: Claude`.
   - Run `check_lua.py`.
3. **Archive, both sides.** The server needs the new tree to restrict the `*_hutta` types, and the client needs it to
   name them.
   - Back up the current file on each side first, as `.bak-f0191ab5`.
   - Copy `work/nal-hutta-life/local_planets-nalhutta-life.tre` over `/opt/swg/tre/local_planets.tre` and
     `SWG-client/local_planets.tre`.
   - Check the sha256 on both sides.
4. **Restart** the test galaxy. A resumed copy is fine.
5. **Log checks:**
   - no `HuttaLifeScreenPlay:` error lines;
   - the `backfillZones: hutta` warning is gone;
   - a `Resource backfill:` line counts hutta;
   - no lair template errors for the 12 added packs.

## The owner's checklist

Answer in your own words.

1. Walking Bilbousa, what is the town like now? Who do you see walking and standing, and does anyone walk into a wall
   or get stuck?
2. What did the people who talk say, and did any of it read wrong?
3. What happens in the cantina? Are the dancers dancing, and where are the drinkers?
4. How do the two Hutts and their retinues look? Is anyone standing inside a wall or a prop?
5. Out in the swamp, how much wildlife do you meet now, and at what levels? Is it too much, too little, or about right?
6. Which of the five places did you find, and what did each look like? Is anything floating, buried or in the water?
7. Can you attack or destroy the freighter wreck? (It is a stock "destructible" wreck.)
8. Take the Kessoth job from Bezzik. What happened at each step, and did the waypoints, messages and reward arrive?
9. Survey on Nal Hutta, for minerals and for water or flora. What do you find, and what are the resources called?
10. Anything else that struck you?

## Known gaps

- **Low-level NPCs in the lowlands.** The site NPCs are stock humanoids of levels 8 to 27. At the lowlands sites (the
  spice den, the ruins and the rival camp), the creatures around them are 31 to 56. Kreeg (36) is the exception. Raising
  them needs new templates or level scaling.
- **The job waypoint** uses the stock quest-task type, so it replaces any other quest-task waypoint the player has, as
  stock quest tasks do.
- **Unchecked placements.** The retinue guards and attendants stand at fixed offsets round each Hutt. Those offsets
  weren't checked against footprints; only the Hutt's own spot was.
- **Untested movement.** Townsfolk walk straight legs between thinned corners. How the AI follows them in the real town
  is untested.
- **The ruins' rise.** The old ruins stand on a perfectly level 108 m rise in `hutta.trn`. It looks like a terrain
  plateau, but nobody has seen it in game.
