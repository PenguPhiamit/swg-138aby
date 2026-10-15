# Ossus fauna: the local model's first content job (15 Oct 2026)

Six Ossus creature templates for Core3. They were written by the owner's local model (Ollama `gpt-oss:20b`) through
`tools/agents/local/local_agent.py`, from Claude's brief (`BRIEF.md`), and reviewed by Claude. Staged only: nothing is in
the dev tree or on a server.

**What the model was given.** Six stock creature templates as bases (falumpaset, dewback, womp rat, worrt, kaadu, bark
mite, copied from `/opt/swg/Core3-dev/MMOCoreORB/bin/scripts/mobile/`) and a table built from
`Fable-resources3/lore/ossus-resource-map.md` §3: name, social group, resource types, milk, herd or pack, diet, and the
Wookieepedia facts. It changed only the listed fields and wrote a one-line description of its own for each creature. Combat
numbers, level and appearance stay the base's.

**Run.** 18 model turns, 293 s, 9,330 output tokens, largest prompt 13.6K tokens. The model read every base file before
writing.

**Claude's review:**
- Diffed against each base with line endings ignored: only the fields the brief allows changed, and every change matches
  the table. For tribis, `milkType` was removed and `milk = 0` set, as asked.
- `luac5.3 -p` passes on all six.
- The only defects were Windows line endings and a missing final newline, and both came from the harness, not the model.
  `local_agent.py` now writes files exactly as given (`newline=''`) and adds the final newline. These files were
  normalised.

| file | var | base (body) | resources | type |
|---|---|---|---|---|
| `mobile/mud_yak.lua` | ossus_mud_yak | falumpaset | herbivore meat, wooly hide, horn, wild milk | herd herbivore |
| `mobile/kirruk.lua` | ossus_kirruk | dewback | reptilian meat, scaley hide, animal bone | pack carnivore, tameable |
| `mobile/gokob.lua` | ossus_gokob | womp rat | wild meat, leathery hide, animal bone | pack + herd |
| `mobile/ossus_tree_frog.lua` | ossus_tree_frog | worrt | reptilian meat, leathery hide, animal bone | solitary |
| `mobile/tribis.lua` | ossus_tribis | kaadu | avian meat, scaley hide, avian bone | herd |
| `mobile/kaddyr_bug.lua` | ossus_kaddyr_bug | bark mite | insect meat, scaley hide, animal bone | pack |

**Not done yet** (before they can appear on Ossus):

1. ~~Names for the client~~ **Staged (Claude, 15 Oct 01:5x):** `stage_creature_names.py` adds the six keys to
   `string/en/mob/creature_names.stf` the stock way ("a mud yak", "an Ossus tree frog"). `build_fauna_archive.py` builds
   `local_planets-fauna.tre` (sha256 `6556537d589c411f9b0c1697c2a4f5bdd792800f96d0ee517d38cd3cd3dcb072`, gitignored) and checks it against the installed names archive 39a89e6c:
   only that string file changes, by the six keys, with every existing key kept (`checks.json`). Install together with C30.
2. Server includes: a `mobile/ossus/` folder with `serverobjects.lua`, as for the other planets.
3. Spawn groups and lairs in Ossus's regions (swamps for the mud yak, forest canopy for the gokob and tree frog).
4. Levels for Ossus. They are the bases' levels for now: 19, 19, 10, 6, 10, 10.
5. Own appearances or hues. They use the stock bodies for now.
