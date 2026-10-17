# Nal Hutta: first look on the test galaxy (PL-03)

Claude, 16 Oct 2026. **Staged only, nothing installed, untested in game.** It follows README section 8, steps 1 to 5. The
main session installs it at a restart the owner OKs, together with the floater fix.

## What changed

**Server: `nal-hutta/core3-dev-nal-hutta.patch`** (Core3-dev at `724809fa`; `git apply --check` passes, all three files
parse in Lua, and the tables load):
- `managers/planet/planet_manager.lua`: a new `hutta` block.
  - Weather on, GCW off.
  - One travel point, "Bilbousa Starport", at (-788.0, 80, 1776.3), landing range 6.
  - A nav area `hutta_bilbousa` of r 400 round the town.
- `managers/weather_manager.lua`: a new `hutta` block. It starts in light rain (weather 1), stability 55, changes every 2,400 s.
- `managers/planet/hutta_regions.lua` (new):
  - the four edge strips, the same as on Ossus;
  - Bilbousa as `CITY + NOSPAWNAREA`, r 400, with a `NOBUILDZONEAREA` circle of r 600;
  - no spawn areas, so nothing spawns on the planet.
- No change to `resource_manager.lua`. Nal Hutta has no resource types yet, so it stays out of `activeZones` and gets no
  resources.

**Test galaxy: `nal-hutta/test-galaxy-hutta.patch`** (h repo; `git apply --check` passes). It adds `hutta` to `TEST_ZONES`
in `tools/test_galaxy.py`, which writes the `Core3.ZonesEnabled` line into config-local.lua at every start. Hoth and Ossus
get theirs the same way. It also puts hutta in the `backfillZones` line. Because hutta isn't in `activeZones`, the server
then logs one harmless warning: `backfillZones: hutta is not in activeZones, ignored`.

**Client: `nal-hutta/build_nal_hutta.py`.** This step goes on top of the newest Hutt archive. The floater folder wasn't
committed when this was built, so it builds on `6ff21312`.
- **Base:** `work/nal-hutta/base-6ff21312.tre`, a copy of the installed archive (4,662,363 B).
- **Candidate:** `work/nal-hutta/local_planets-nalhutta.tre`, 4,663,445 B, 180 entries.
  - sha256 `d804d98ab7d367932a2c8dc459e82e80a578df314b5670611c619a3d42a7a68d` (also in the `.sha256` file beside it).
  - The build is deterministic: two builds gave the same bytes.
- **What it adds:**
  - 171 of the base's 176 entries are byte-identical.
  - 5 entries change and 4 are new. The builder fails if anything else differs.
  - The full report is in `nal-hutta/checks.json`.

| Entry | Change |
|---|---|
| `string/en/hutta_region_names.stf` | new: `bilbousa` "Bilbousa" (the key MTG's `datatables/clientregion/hutta.iff` row points at) |
| `string/en/planet_n.stf` | + `hutta` "Nal Hutta" |
| `datatables/travel/travel.iff` | + hutta column and row: Tatooine -> Nal Hutta 3000, Nal Hutta -> Tatooine 1750, Nal Hutta -> Nal Hutta 100 (placeholders, the Corellia/Ossus pattern) |
| `datatables/player/waypoint_planets.iff` | + `hutta` / `ui_planet_sel_rori.apt`, after ossus |
| `ui/ui_ticketpurchase.inc`, `ui/ui_planet_map.inc` | Endor's blocks cloned for Nal Hutta after Ossus's (`swgfmt/ui_inc.py`): the galaxy-map button at (425, 355), below Ossus's (placeholder); the label reads "Nal Hutta"; the planetary map uses MTG's `texture/ui_map_nalhutta.dds` |
| `datatables/loading/hutta.iff`, `string/en/loading/hutta.stf`, `hutta_n.stf` | new: three loading screens with our own text (Nal Hutta, Bilbousa, the Hutta Lowlands) on the stock generic tile |

**Images.** MTG ships `texture/ui_planet_sel_nalhutta.dds` but no `.apt`, mesh or shader for it, so the ticket screen's
3D globe uses the Rori placeholder. Ossus's O3 step built its own globe chain (apt -> msh -> sht -> dds), and the same
could point at MTG's texture later. The planetary map image does exist and is used.

**Already on the client (checked, not changed):**
- `terrain/hutta.trn` (mtg_planets.tre);
- `snapshot/hutta.ws`, `terrain/environment/hutta.iff` and `nalhutta.iff` (mtg_patch_022.tre);
- `datatables/environment/hutta.iff`;
- the planet CRC rows `hutta` and `nalhutta`.

The server has `mtg_planets.tre` and `mtg_patch_022.tre` in `/opt/swg/tre`.

**Credit.** The Darklight line, in the catalogue row's wording, is now at the end of
`Community-content/CREDITS-and-sources.txt`. That folder is git-ignored, so the line exists only on this PC and isn't in
the commit. Tracking the credits file is the owner's call.

### Changes from README section 8

- **Travel point.** Bilbousa's starport is the full `starport_tatooine` (node 390000001 at (-767, 80, 1795), yaw 180),
  not an outpost, so the README's +20.3/+17.8 outpost offset doesn't apply. All four Tatooine starports put their pad at
  (21.0, 18.7) in building space: Mos Eisley, Bestine, Mos Espa and Mos Entha agree to within 0.03 m. At yaw 180 that
  gives (-788.0, 1776.3), not (-746.7, 1812.8).
- **City centre.** The city circle is centred on the snapshot's town box at (-747, 1556), not the client's name point
  (-746, 1645). With r 400 it then covers every corner of the town, including Jabba's palace at the south end. The client
  name point is MTG's and stays as it is.

## How the main session installs it

1. **Check first.**
   - You hold the server lock.
   - No owner client is running.
   - No squad round is running (`pgrep -f "squad.py run"`).
   - The owner has OKed this restart.
2. **Floater first?** If the hutt-floater candidate is ready, rebuild this on top of it:
   `C:/Users/Pengw/miniconda3/python.exe -I outputs/Fable-species/s7-hutt/nal-hutta/build_nal_hutta.py --base <floater .tre>`
   - The two steps touch different entries. Note the new sha.
   - It fails loudly if the floater already changed one of this step's five tables (`travel`, `planet_n`,
     `waypoint_planets` and the two UI files). In that case, merge by hand instead.
3. **Server scripts.** As swgemu:
   - `runuser -u swgemu -- git -C /opt/swg/Core3-dev apply /mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Fable-species/s7-hutt/nal-hutta/core3-dev-nal-hutta.patch`
   - Commit it with `Agent: Claude`.
   - Run `check_lua.py`.
   - No C++ build is needed.
4. **Test galaxy tool.** In h, run `git apply outputs/Fable-species/s7-hutt/nal-hutta/test-galaxy-hutta.patch` and commit
   it.
5. **Archive, both sides.** Copy the candidate over `/opt/swg/tre/local_planets.tre` (the server reads `travel.iff` from
   it) and over `SWG-client/local_planets.tre`.
   - Back up the current file on each side first, as `.bak-6ff21312`.
   - Check the sha256 on both sides afterwards.
6. **Restart.** Restart the test galaxy (`test_galaxy.py start --dev-server`, or `squad.py galaxy`). A resumed copy is
   fine: the new zone has no saved objects. Then:
   - check that the console log loads `hutta` without region or terrain errors;
   - check for the one backfill warning above;
   - run `server_status.py`.
7. **Getting there.** The owner flies from any Tatooine starport.
   - Wait for the shuttle boot delay first (30 s on the test galaxy).
   - If the ticket screen fails, a staff teleport to `hutta -788 1776` gets them there and is a finding in itself.

## The owner's in-game checklist (step 6)

Answer in your own words. Each answer goes into the follow-up.

1. On Tatooine's ticket screen, what did you see for Nal Hutta: the button, the label, the globe? Could you buy the
   ticket?
2. What did the loading screen show?
3. Where did you arrive: on the landing pad, beside it, or somewhere else? Did a shuttle, terminals and a ticket
   collector stand at the starport?
4. What colour is the swamp water, and does it look like Nal Hutta to you?
5. What is the sky like, and does it read as Nal Hutta (it is Dathomir's misty-falls sky)?
6. Walking Bilbousa: which buildings, if any, float above or sink into the 80 m shelf?
7. How do the four Jabba-palace towers look, and where do they stand out or clash?
8. At night, how dense and how bright are the green street lamps?
9. How tall is the swamp flora next to the walkways and streets: under, at or over your head?
10. What does the overhead map, and the region name as you walk in, call the town?
11. Anything else that struck you, good or bad?

## Open questions (from the README)

1. **Which sky file did Darklight mean?** There are two in MTG 022: `terrain/environment/hutta.iff` and
   `terrain/environment/nalhutta.iff`. The client picks the one the terrain's environment block names. This step changes
   neither, so the owner's answer to question 5 tells us whether the current sky works. Comparing the two files is the
   next check if it doesn't.
2. **Do any `hutta_*` string files exist?**
   - None in any client archive: checked, no string file with "hutta" in its name.
   - MTG's server package wasn't checked in this step.
   - The region name now comes from our own `string/en/hutta_region_names.stf`. If MTG's package does have one, its
     wording can replace ours later.
