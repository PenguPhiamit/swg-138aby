# C4f: review of Claude's 14 Oct dev commits and client-archive tooling

Five dev commits (branch `dev`, LF endings except where noted), one patch each, plus two Windows-side tools in `outputs/tools/`. All are running on the test galaxy since 05:31 on 14 Oct. Not promoted; live needs this review and the owner's OK.

| Patch | Commit | What |
|---|---|---|
| 0001 | `34d4772a` | `/spawnStatus` and `/showSpawnRegion` (were empty staff stubs) + read-only IDL getters on SpawnArea and CreatureManager |
| 0002 | `b7f03b0e` | Hoth reward loot: 25 Bellum items, 3 groups, drops on Hoth's creatures; two vehicle deeds under `custom_content` (CRLF files kept CRLF) |
| 0003 | `2f205cd2` | `hoth` in the resource manager's `activeZones` |
| 0004 | `bea94e7a` | Leash: an indoor step needs both ends on the floor mesh (your C4e-F1) |
| 0005 | `578861d9` | Botanist feasibility test: trainer data, conversation, trainer mobile, Mos Eisley spawn |

Tools, read directly in `outputs/tools/`:
- `hoth/hoth_client_build.py`: builds the test-only `local_planets.tre`. New on 14 Oct:
  - `object_crc_table()`: merges the client's object CRC string tables, because stock patch_14_00 shadowed MTG's;
  - `resource_tree()`: stock rows plus MTG's 50 `*_hoth` rows, plus solar and wind cloned from Endor;
  - `botanist()`: two skills.iff rows and strings.
- `test_galaxy.py`: now puts `local_planets.tre` first in the server's TreFiles and enables `hoth` by itself. The Lua lines go into the disposable copy's `config-local.lua`.
- `hoth/hoth_loot_inventory.py`, `hoth/hoth_loot_core3_check.py`, `hoth/hoth_port_loot.py`, `owner_content/botanist_server.py`: the generators.

## What to check
1. **0001:** both commands are read-only and staff-only through their command entries. Bounded output (40 areas, 20 spawn entries)? Any race reading `spawnAreaMap` or the active areas without a lock? `dynamic_cast` on a ManagedReference's `get()`: safe for lifetime?
2. **0002:**
   - The equal re-weighting (each group totals 10,000,000).
   - The `lootGroups` insertion (does `add_drop` keep existing entries intact?).
   - The two deed templates' fields against Core3's other vehicle deeds.
   - Anything in the Bellum items that our Core3 version doesn't understand.
3. **0003 + `resource_tree()`:**
   - Is inserting rows mid-table safe for Core3's `ResourceTree::buildTreeFromClient` (carried-forward container/name columns, `INDEX` renumbering)?
   - Is raising ancestors' Maximum/Minimum # types right? Stock matches the leaf count on only 538 of 725 rows.
   - Does anything key on row index?
4. **0004:** the guard against your counterexample.
5. **0005 + `botanist()`:**
   - The skills.iff row defaults (enum/bool/int columns, `ENDER`).
   - Does the client's skill browser need more than a root + Novice for a 4x4 (GRAPH_TYPE 4) profession?
   - The trainer spawn line format.
6. **`object_crc_table()`:** is a 29,358-name table safe for the pre-CU client (sorted by CRC, no clashes)? Anything else the client keys on (for example `misc/object_template_crc_string_table.iff` vs per-object CRC lookups)?

Write findings to `C4f-review.md` (P1/P2/P3 as in C4d/C4e, each with file:line and a concrete failure scenario). Read-only: don't edit /opt/swg.
