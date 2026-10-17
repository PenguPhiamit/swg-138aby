# Ossus O10: the ghostfire crystal quest (Claude, 17 Oct 2026)

The owner asked (17 Oct) for the ghostfire colour crystal with the hidden Jedi "actually hidden in a cave", earned through a quest and badges,
and linked to "one of the famous jedi of the era" who hid it from the Vong and Krayt. On the decision card the owner chose T'ra Saa,
a quest plus exploration badges, and a simple dim pearly colour first. Brief: `Documentation-support/ghostfire-quest-brief.md`.

**Staged, not installed, untested in game, and not built** (the patch has one C++ line, so it needs a dev build). The gates still apply:
Ossus is closed for the friends launch, and the owner's end-to-end test pass comes before new content. So this goes to dev and the test galaxy only,
and nothing goes live without the owner's OK.

## Lore (Wookieepedia, Legends) and what is ours

- **Ood Bnar** (https://starwars.fandom.com/wiki/Ood_Bnar, Legends) was a Neti Jedi Master and Head Librarian of the Great Jedi Library on Ossus.
  He became a tree to guard a trove of ancient lightsabers, and the Ysanna revered him for 4,000 years. He died on Ossus in 10 ABY, leaving
  **a sapling that grew where he fell**.
- **T'ra Saa** was a Neti Jedi Master on Krayt-era Jedi councils. She died at the Hidden Temple in 138 ABY, so she cannot appear in 138-139.
- **The keeper, alive (owner, 17 Oct: a Neti, "someone alive preferred"):** Ood Bnar's sapling, grown, now about 128 years old, a young age for a Neti.
  **Our invention, not canon:** T'ra Saa found the seedling and taught it. She found the ghostfire crystal during the Yuuzhan Vong War, and when
  Krayt's Sith came for the academy (130 ABY) she left it in the young Neti's keeping. The keeper appears as "a young Neti" in the sanctuary's
  deepest chamber (cave cell 11), about one hour in three to five, as before.
- **Look (owner, 17 Oct):** a robed stand-in body until there is Neti art. The client has no Neti body.
- The other option the owner named was a plausible Force ghost. Ood Bnar's own spirit would be the obvious one: he died on Ossus and is "one with the Force".
  It is not built; the alive keeper was preferred.

## The quest

1. **The lead.** Archivist Senn Oduro (vault dig, 2302 1987) has a new question: "Did any Jedi light survive here?" She names what to walk and marks
   three sites. Nothing counts before this lead.
2. **The walk.** Three old Jedi sites on Ossus are server trigger areas (no client strings needed): the vault mouth (2300 1925), the Eocho watch ruin (290 -6400)
   and the Ysanna stone circle (-980 -5610). Each one says so in the chat: "Old Jedi sites walked: 2 of 3". The **badges** are Ossus's memorial road
   badge (140, from PL-02) plus **any one** stock Jedi exploration badge: Dantooine's ruined Jedi temple (30), Exar Kun's temple on Yavin 4 (23),
   or Ben Kenobi's old home on Tatooine (12).
3. **The keeper (a young Neti).** Until you are ready, the keeper says exactly what you still lack. The keeper will not speak to Imperials.
4. **The record and the test.** The keeper plays T'ra Saa's record, in our own words, then asks one question. "Keep it safe, and let it shine as it will"
   passes. "Use it against my enemies" or "Keep its power for myself" fails, and the keeper waits an hour before asking again.
5. **The reward.** The **Ghostfire Crystal** (a colour crystal, colour 32, no stats), once per character. A full inventory gets "make room and come back".
6. **Afterwards.** A short farewell line on each visit.

The dialogue started from the local model's draft (`Agent/local-research/ghostfire-quest/draft.md`). It was reviewed and rewritten here:
the line close to a canon quote is gone, the two wrong answers are softer, and the text is teen-rated with no real-world references.

## What changes

**Server:** `server/core3-dev-ossus-ghostfire.patch` against Core3-dev `91cf87ed`. It passes `git apply --check`, and `luac -p` passes on every Lua file.
A stubbed walk through ten quest states also passes: fresh, the lead, sites refused before the lead, missing-item hints, the wrong answer and the
retry wait, a full pack, the reward given once, the farewell, and an Imperial refused.
- `screenplays/sandbox/ossus_people.lua`: the three site areas, the keeper's quest logic, and the archivist's lead.
- `mobile/conversations/sandbox/ossus_people_conv.lua`: the keeper's 14 screens, which replace the stranger's 5, and the archivist's new screen.
- `mobile/sandbox/ossus_people.lua`: the keeper's name, "a young Neti", which was "a robed stranger".
- `loot/items/ossus/ossus_ghostfire_crystal.lua` and `loot/groups/ossus/ossus_ghostfire_crystal.lua` (new), with an include line in `loot/items.lua` and `groups.lua`.
- **C++, one line:** `LightsaberCrystalComponentImplementation::updateCraftingValues` clamps every colour crystal to 0-11. It now lets exactly 32 through
  when the item asks for 32. **Needs a dev build**, and only compiles there.

**Client and server archive:** `build_ghostfire.py` works on any base archive (default: the installed `b01e9f44…`).
- `palette/wp_lightsaber.pal`: the stock palette (patch_09.tre, 32 entries, 0-31; 31 is the no-colour white `f2f2f2`) plus **entry 32 = `c4c0d4`**, a dim pearly white with a faint lavender sheen.
- `string/en/jedi_spam.stf`: + `saber_color_32` = "Saa's Ghostfire", in the stock naming style ("Kenobi's Legacy", "Windu's Guile").

All other 201 entries stay byte for byte. The candidate is **`work/ossus-ghostfire/local_planets-ghostfire.tre`, sha256 `b74267cf58f0aa40e6cd33d2e345ac115717117491ef30790ec9099dfefa5914`** (two builds, same hash).

## Install order (the main session, with the server lock, test galaxy only)

1. Chain `build_ghostfire.py --base <archive> --out <new>` with the other client steps. It only adds two entries, so the order doesn't matter.
2. Apply the patch to Core3-dev, run `check_lua.py`, then do a dev build (the C++ line).
3. Install the archive in both places, and restart the test galaxy with `--dev-server`.

## Render check first (please answer in your own words)

The open risk is whether the client draws palette index 32 or clamps to the stock 0-31. Before anyone does the quest, a staff-made crystal settles it.
In the test galaxy, put a colour-32 crystal in a lightsaber and turn it on.
1. What colour is the blade: pale pearly, white, red (index 0), or nothing?
2. What does the crystal's examine window say for its colour?
If the client clamps it, the fallback is to repaint a stock index nobody uses on this server (12-30 come only from the NGE).
That is one line in each half, and I would ask you which index first.

## Questions for the quest walk (please answer in your own words)

1. Ask the archivist about the Jedi light. Do the three waypoints appear, and are the sites easy to find?
2. At each site, did the chat say "Old Jedi sites walked"?
3. The keeper is in the sanctuary's deepest chamber (2057 2735, then down), about one hour in three to five. Is that too rare for a quest?
4. Did the keeper's hint name exactly what you were missing?
5. How did the record and the test read? Is anything out of place for 138-139 ABY?
6. Is the gate right: three sites, the memorial road, and one temple badge from another planet? Would you rather require more Jedi badges, or none?
