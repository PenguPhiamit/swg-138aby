# Ossus gem names: the Adegan grades (Claude, 14 Oct 2026)

The owner asked for the placeholder Ossus gems to be renamed. Fable ran out of weekly usage, so Claude did it as the
next step of Fable's chain. This is staging only: nothing here touches /opt/swg.

| path | what |
|---|---|
| `stage_gem_names.py` | `stage_gem_names(stage_dir, base)`: the five name changes, the last chain step after `stage_lore_materials` |
| `build_names_archive.py` | runs the chain and packs `local_planets-names.tre` (gitignored); compares it with the installed lore archive; writes `checks.json` |
| `checks.json` | the comparison |

**Names.** All five Adegan grades on Wookieepedia, one per Ossus gem leaf, most common first:

| enum | old name | new name |
|---|---|---|
| `crystalline_ossus_1` | Ossus Type 1 Crystalline Gemstone | Kathracite Crystalline Gemstone |
| `armophous_ossus_1` | Ossus Type 1 Amorphous Gemstone | Relacite Crystal Amorphous Gemstone |
| `armophous_ossus_2` | Ossus Type 2 Amorphous Gemstone | Danite Crystal Amorphous Gemstone |
| `crystalline_adegan_ossus` | Adegan Crystal Crystalline Gemstone | Mephite Crystalline Gemstone |
| `crystalline_ossus_2` | Ossus Type 2 Crystalline Gemstone | Pontite Crystalline Gemstone |

The sources and the reasons are in `../lore/ossus-resource-map.md` §1.

**Verified (checks.json).** `local_planets-names.tre`:

- sha256 `39a89e6c1bfdf72811e6b68be035d0228542f6dd9886c2c0ca1438a780d977db`, 3,785,376 B, 55 entries;
- compared with the installed `lore/local_planets-lore.tre` (fbf62971…, sha256 checked), only
  `datatables/resource/resource_tree.iff` changes;
- in that table: 845 rows, the same rows in the same order, and exactly five cells differ, all the deepest CLASS text
  of the rows above;
- every other entry is byte-identical, Chiss included;
- the step is idempotent.

**The base files.** The chain reads its base files from the client's load order. While the test launcher's
`swgemu_login.cfg` is in place, that order includes our own `local_planets.tre`. The first build therefore found Chiss
already present and staged nothing for it. `build_names_archive.py` drops `local_planets.tre` from the load order
before building. Any other chain build run while a test session is configured has the same trap.

**In game.** Core3 copies the class text into a spawn when it creates it. Spawns already in the test galaxy keep their
old names until they expire or are despawned; new spawns get the new names. The ENUMs don't change, so the dev pool
lines (R3 part 2, C29) need no change.

**Install.** At the next test-galaxy restart, which only happens when the owner's client is closed:

1. copy the archive to `/opt/swg/tre/local_planets.tre` and to `SWG-client/local_planets.tre`;
2. back up fbf62971 first.
