# Nal Hutta as the Hutt home (PL-04)

Claude, scheduled run, 17 Oct 2026, 1:55 to about 3:00 AM. **Staged only, nothing installed, untested in game.**
Nothing under `/opt/swg`, `SWG-client/`, the galaxy or the bots was touched. Core3-dev was only read, through script
files. The design is `README.md` sections 1 and 8; the first look (PL-03) is `nal-hutta-first-look.md`.

**Credit.** Nal Hutta's terrain and the Bilbousa layout are Darklight's work. The catalogue credits them as
"Levarrishawk/Darklight public version" (status P, credit required; release source
https://github.com/Levarrishawk/DLSWG5). Our copy of the snapshot keeps all 281 of Darklight's nodes and adds ours.
A PL-04 line now follows the first look's credit at the end of `Community-content/CREDITS-and-sources.txt`. That folder
is git-ignored, so the line exists only on this PC.

## What changed

### Bilbousa, dressed as a Hutt city (client and server archive)

Bilbousa is laid out along one avenue:
- the starport at the north end, with its front on y 1711;
- the bank's round plaza;
- a bazaar of ten merchant tents;
- the gate of Jabba's palace shell at the south end, here the **council palace**.

Four Jabba-palace towers already stand around it. Each one's entrance is marked by one of Darklight's green lamps, so
these four are the first **kajidic seats**. Two new towers on the flat 80 m shelf make six seats. The kajidic names are
the S7 README's own (section 5.5), not Legends clans.

| Seat | Tower | Entrance |
|---|---|---|
| Kessoth | Darklight's, (-652, 1680) | south face, at lamp 390000225 |
| Vollaka | Darklight's, (-984, 1562), inside Nym's stronghold | the stronghold's gate, at x -937 (lamp 390000221) |
| Dromuul | Darklight's, (-889, 1812) | south face, at lamp 390000278 |
| Narissik | Darklight's, (-540, 1501) | west face, at lamp 390000270 |
| Tashuga | **new**, (-750, 1920), north shelf behind the starport | south face |
| Bessolo | **new**, (-1050, 1690), west shelf | east face, towards the hotel street |

Each seat's entrance gets:
- two stock banners (`all_banner_generic_s01`);
- two warm street lamps (`streetlamp_medium_style_02_on`, the same lamp as Darklight's green ones, in the plain light);
- two Gamorrean guards (server side, below).

The head of the bazaar, in front of the council palace, gets a round fountain (`corl_fountain_circle_s01`) and two
warm lamps.

**Build:** `nal-hutta-home/build_nal_hutta_home.py`, a builder step on the installed archive.
- **Base:** `work/chain-1016/local_planets-chain-1016.tre`, sha256 `df1d538e…`, 186 entries. The step checks the sha.
  This is still the archive the server-lock line names.
- **Candidate:** `work/nal-hutta-home/local_planets-nalhutta-home.tre`, 4,845,095 B, 188 entries.
  - **sha256 `5e43386dc604937570f9c85ee9337bb79c24a0f4fb271b4b5fd5f2e5f52d766c`** (also in the `.sha256` file beside it).
  - Two builds gave the same hash.
- **Checks** (all in `nal-hutta-home/checks.json`):
  - all 186 base entries are byte-identical, and there are exactly two new entries;
  - the snapshot round-trips through the writer;
  - all 281 of Darklight's nodes read back unchanged;
  - the new ids 7170001-7170029 clash with no snapshot the client loads;
  - every new template is in the stock CRC table and has a server template in dev.

| Entry | Change |
|---|---|
| `snapshot/hutta.ws` | new in `local_planets.tre`. It is Darklight's file (MTG 022, 25,795 B, 281 nodes) plus 29 statics: 310 nodes, 28,439 B. |
| `datatables/clientregion/hutta.iff` | new in `local_planets.tre`. MTG's one Bilbousa row moves from (-746, 1645) r 300 to (-747, 1590) r 400, so the town name also covers the council palace and the two new seats. The key is the same. |

**Why the override works.** Both sides read `local_planets.tre` before the MTG archives: it is at priority 49 in the
test-session client and first in the server's `Core3.TreFiles`.

**Placement data.** `nal-hutta-home/tools/make_home.py` lays everything out and checks it, then writes `home.json`.
- Every static sits on dry, flat ground. The ground comes from `hutta.trn` through Fable's Core3 port; Core3 skips five
  BREC boundaries in this file, and so does the tool.
- No static overlaps any of Darklight's footprints or another new static.
- The towers have under 2 m of relief over r 38.
- One allowance: the Vollaka props stand inside Nym's stronghold's loose client box, where Darklight's own gate lamps
  also stand.
- No terrain edits.

### Server patch: `nal-hutta-home/core3-dev-nal-hutta-home.patch`

The patch is against Core3-dev HEAD `07d9f61e`, which is the dev the lock line names. The 8 files it changes are
identical at `69f5c879`, so it fits both.

The checks are in `nal-hutta-home/server-check.txt`, written by `tools/server_check.sh` (read-only):
- `git apply --check` passes;
- `luac -p` passes on all 16 files;
- 59 more checks pass: every lair, mobile, object template and conversation the files name exists in dev or in the patch.

No C++ change, so no build is needed.

**People and terminals** (`screenplays/sandbox/hutta_home.lua`, positions in the generated `hutta_home_places.lua`):
- **The council herald**, a protocol droid at the starport end of the avenue. They tell arrivals about the city, the six
  seats and where the work is.
- **Two Hutt vendors** in the bazaar, one in front of a tent each. They sell stock items for cash through a list box (the
  event promoter's pattern). Hutt players pay 90% (the "kin price").
  - Dessuk Kessoth, outfitter: the three stock Hutt gang vests, 2,500 credits each.
  - Garulla Vollaka, broker: three spice jars at 600, two candlestick lamps at 900, a Tatooine hall lamp at 750.
  - **The floater deed is not sold.** The owner decided on 15 Oct that Artisans craft it.
- **Four general mission terminals.** "Kajidic contracts" stand on both sides of the avenue, and "Smuggling runs" stand by
  the cantina door.
  - Pre-CU has no smuggler mission type, so these give the general destroy and deliver missions.
  - Destroy targets: `hutta_destroy_missions`, eight lowland lairs of levels 19 to 34.
  - Deliver missions: Bilbousa is in `mission_cities.lua`, with eight NPC points 3 m off Darklight's street lamps in
    `mission_npc_spawn_points.lua`.
- **Other people:**
  - the stock smuggler trainer at the cantina door;
  - 12 Gamorrean guards, two per seat (stock `gamorrean_guard`, not attackable, named "a Kessoth guard" and so on);
  - five Nikto idlers and cargo runners.
- **The east trade yard:** Tatooine's Hutt businessmen camp, a stock POI whose tents and crates are its child objects, at
  (-440, 1530).
- The spawns are not persistent: they are made again at every start, as on Hoth.

**Swamp spawns** (`hutta_regions.lua`; groups in `mobile/spawn/hutta/`). There are three rings round Bilbousa, habitat
spawners only, with no world fallback. Lairs never spawn in the 75 m water (`isSpawningPermittedAt`).

| Ring | Distance | Levels | Creatures (stock) |
|---|---|---|---|
| `hutta_lowlands_near` | 650-1,600 m | 19-25 | putrid borgle, noxious squill, famished and greater sludge panthers, borgle life sapper |
| `hutta_lowlands_mid` | 1,600-3,200 m | 31-38 | festering squill, fierce borgle, swamp tusk cat stalker, fambaa (herds and lairs), diseased blurrg, rogue fambaa |
| `hutta_deep_swamp` | 3,200-5,200 m | 37-56 | rogue fambaa, dreaded vir vur, diseased blurrg, mire marauder (56) |

- **Why these levels.** The newbie worlds' town spawns run 1 to about 11. In run 21's `Bot-reports/planet-data/`, the
  highest creature is 11 on Rori and 7 to 10 on Tatooine, Naboo, Corellia and Talus; the medians are 5 to 7. Their medium tables run into the 20s, and Talus's northern table reaches 45-55. Nal Hutta starts above
  the newbie spread and climbs to the 50s.
- **The rest of the planet stays empty**, beyond 5,200 m and outside the rings.
- **The new-character spawn gate** (`LevelGateCreatureMargin`) applies here as everywhere: a level 5 character draws
  nothing above level 12.

### Why "0 nav areas loaded for hutta", and the fix

- **The `navAreas` line was never read.** Core3 doesn't read `navAreas` from `planet_manager.lua` at all.
  `PlanetManagerImplementation` builds nav areas from only two sources:
  - regions flagged `NAVAREA` (`buildRegionNavAreas`);
  - city regions (`buildCityNavMeshes`).
  The `hutta_bilbousa` line was dead config, and Hoth's and Ossus's lines are dead the same way.
- **Bilbousa still has a mesh.** It is the city region's own: `hutta_city_bilbousa`, from `CityRegion::createNavMesh`.
  - "0 nav areas loaded" counts the meshes read back from `navareas.db`, and the first look's copy was fresh.
  - Run 21's log (1:02 AM) says "1 nav areas loaded for hutta".
  - Hoth and Ossus show the same 1, their own city meshes.
- **The fix:** the patch empties hutta's `navAreas` list and says why in a comment. Hoth's and Ossus's lines are left
  alone (out of scope; also harmless).
- **The city radius stays 400.** A persisted city mesh is reused by name with its old bounds, so changing the radius would
  not take effect without a rebuild.
- **New buildings need a rebuild.** Snapshot objects are loaded before the persisted mesh is read back. The stored
  `hutta_city_bilbousa` mesh therefore won't contain the two new towers or the fountain until it is rebuilt (see the
  install steps).

## Install order (for the session that holds the server lock)

1. **Check first.**
   - You hold the server lock.
   - No owner client is running.
   - No squad round is running (`pgrep -f "squad.py run"`).
   - The owner has OKed the restart.
2. **Server scripts.**
   - As swgemu: `runuser -u swgemu -- git -C /opt/swg/Core3-dev apply /mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Fable-species/s7-hutt/nal-hutta-home/core3-dev-nal-hutta-home.patch`
   - Commit it with `Agent: Claude`.
   - Run `check_lua.py`.
   - No C++ build is needed.
3. **Archive, both sides.**
   - Back up the current `df1d538e` file on each side as `.bak-df1d538e`.
   - Copy `work/nal-hutta-home/local_planets-nalhutta-home.tre` over `/opt/swg/tre/local_planets.tre` and
     `SWG-client/local_planets.tre`.
   - Check sha256 `5e43386d…` on both sides. The server reads the snapshot and the client reads the region table, so
     both sides need it.
4. **Restart the test galaxy.** A resumed copy is fine: the new objects have new ids.
   - **Nav mesh.** For the first start, use core3's `deleteNavMeshes` argument (ServerCore) if you can. It rebuilds every
     planet's meshes, so the boot takes longer. `test_galaxy.py` has no switch for it yet.
   - Without it, Bilbousa's stored mesh lacks the two new towers and the fountain. AI paths may then cut through them
     until the next rebuild.
5. **After the start, check the console:**
   - `hutta` loads its snapshot with **192 world objects** (163 before);
   - no `HuttaHome:` errors (the screenplay prints one for any spawn that fails);
   - the three spawn regions load;
   - `server_status.py`.
6. **If the owner rebuilds an earlier step**, rerun the builder with
   `C:/Users/Pengw/miniconda3/python.exe -I outputs/Fable-species/s7-hutt/nal-hutta-home/build_nal_hutta_home.py --base <new archive>`.
   - It refuses a base that already has either entry.
   - If the layout changes, rerun `tools/make_home.py` first. It also rewrites `hutta_home_places.lua`, so regenerate the
     patch too.

## Owner checklist (after the install; answer in your own words)

1. When you land at Bilbousa's starport, what do you see first, and who greets you?
2. Walk the avenue south to the palace. Does the town read as a Hutt city now, or still as Mos Eisley? What would change
   that most?
3. At each of the six kajidic seats, how do the banners, the warm lamps and the two guards look together? Are any of
   them floating, buried, inside a wall or blocking a door? Look hardest at Vollaka, at Nym's stronghold gate.
4. How do the two new towers north and west of the town look next to Darklight's four? Can you walk round them, or does
   anything block the way?
5. What did the two Hutt vendors offer you, and what happened when you bought something? Was the price right for your
   character?
6. What missions did the "Kajidic contracts" and "Smuggling runs" terminals offer? Did a deliver mission send you to
   someone in town, and a destroy mission to a lair in the swamp?
7. What does the east trade yard (the Hutt camp past the Narissik tower) look like? Is it there at all?
8. Walking out into the swamp: what creatures did you meet near the town, further out and deep in, and at what levels?
   Did any of it feel too easy or too hard for your character?
9. Where does the map name "Bilbousa" begin and end as you walk in and out?
10. Did any NPC or creature walk through a tower or the fountain?
11. Anything else that struck you, good or bad?

## Open questions (no answer blocks this step)

1. **Prices.** Vests are 2,500, jars 600 and lamps 750 to 900 credits, and Hutts pay 90%. Keep these, or set your own?
2. **Kajidic standing.** Fable-factions' `hutt_kajidic` side (FW-01) isn't built. The vendors and terminals are open to
   everyone. Once standing exists, should the vendors, the palace interiors or better contracts need it?
3. **Banners.** These are stock generic banners. Do you want kajidic seals as our own art later (an asset-pipeline job,
   no fal without your OK)?
4. **The rest of the planet.** Nothing spawns beyond 5,200 m from Bilbousa. Should a later pass add swamp beyond that, or
   a second settlement?
5. **The sky** (from PL-03). Is the Dathomir sky right for Nal Hutta? This step doesn't change it.

## Files

- `nal-hutta-home/core3-dev-nal-hutta-home.patch`: the server patch (16 files).
- `nal-hutta-home/server/`: the patch's new Lua files, for reading.
- `nal-hutta-home/build_nal_hutta_home.py`: the client builder step.
- `nal-hutta-home/checks.json`: the builder's checks.
- `nal-hutta-home/home.json`: every placement, with its checks.
- `nal-hutta-home/server-check.txt`: the read-only server checks.
- `nal-hutta-home/tools/`:
  - `make_home.py`: layout and checks;
  - `hutta_common.py`: snapshot and terrain readers;
  - `find_sites.py`: flat-site search;
  - `map_town.py`, `list_nodes.py`: diagnostics;
  - `server_check.sh`.
- Candidate (not committed; `work/` is ignored): `work/nal-hutta-home/local_planets-nalhutta-home.tre` and its `.sha256`.
