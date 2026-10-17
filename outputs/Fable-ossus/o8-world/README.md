# Ossus O8: filling the planet (Claude, 17 Oct 2026)

The owner walked Ossus after run 25 (17 Oct, about 6:10 AM): it "is far from ready, it is VERY empty looking still", "feels empty", and the terrain may not
be accurate. The owner chose townsfolk, more wildlife, places to find, and dungeons or quests. This batch does those four.
It is **staged, not installed, and untested in game**. There are no terrain edits; the terrain questions are at the end.

## What is in it

**Server only.** `server/core3-dev-ossus-world.patch` against Core3-dev `7be8837a` (`git apply --check` clean, `luac -p` clean on all 11 files,
and a stubbed load resolves every template, conversation screen, spawn group and dungeon cell). **No client data is needed:**
the props are server objects made by the screenplay from stock static templates, and the dungeon uses the cave that the snapshot already has.
So there is no archive step, and the installed `f0191ab5` stays as it is.

New files (ours): `mobile/sandbox/ossus_world.lua` (6 fighters, 4 talkers), `mobile/conversations/sandbox/ossus_world_conv.lua`,
`screenplays/sandbox/ossus_world.lua`, and `mobile/spawn/ossus/ossus_mesa.lua`, `ossus_canyon.lua`, `ossus_highlands.lua`.
Edited: `managers/planet/ossus_regions.lua`, plus one include line in each of the four include lists.

| Part | What |
|---|---|
| **Townsfolk** | 16 more people: Knossa gets 10 (settlers, pilgrims, a scavenger, two traders, a traveller). Two of them talk: Sister Anwe, a pilgrim who points to the road, and Rab Okkon, a settler who mentions the scavengers, the poachers and the west cave. Two more at the hamlet, one Ysanna tracker, and three Hutt guards and handlers at the Hutt field. **An Imperial patrol** (two troopers and a lieutenant) walks the memorial road between the last two stones below the garrison. A killed trooper returns after 5 minutes. |
| **More wildlife** | Five new spawn areas where the census found no creature: the mesa east of Knossa (tribis, gokob, kirruk), Imhar Canyon (kaddyr bugs, tree frogs), the benchland around the ruins (400-1400 m out), the Eocho foothills (kirruk, gokob) and the south plains (the forest mix, levels 6-10). The five old areas allow more at once: 24 → 30-32 and 32 → 40. Creature levels are unchanged, and every no-spawn circle at the places is kept. |
| **Places to find (6)** | Each is a stock-art camp on flat ground (the terrain model gives 0.7-3.3 m of relief over r 20 m), 600-2,100 m from the nearest place, with its own no-spawn circle. **The scavengers' battle site** (1408, -640): Mother Gessa (L14) and 4 scavengers. **The poachers' camp** on the mesa (2944, -1408): Harl Dennick (L21) and 3 poachers. **The smugglers' drop** (4480, -1152): Captain Sava Rook (L19) and 3 smugglers. These three leaders are aggressive and drop stock loot (junk, kit parts, wearables, attachments, sometimes a pistol or rifle). **The deserters' camp** (-640, -384): Lieutenant Iden Sarr talks about the dungeon. **The pilgrims' rest** on the road (520, -1480). **The hermit's hollow** (-1408, 2432): a hermit who kept the academy's gardens. |
| **The dungeon** | **The One Sith cell** in the west foothill cave (POI 14, the old interrogation post, cave node 6900002). 22 acolytes (L18) and enforcers (L26) fill all 11 cells, 2 per cell and 3 at the bottom, with **Keeper Raskal Vonn** (L38, boss) in the deepest chamber. Respawns: 10 minutes; the Keeper 30 minutes. Keeper loot: colour crystals, armor and clothing attachments, melee weapons, plus junk and kit parts. Spawn points are floor-mesh points from the cave's own layout. The deserter and the settler point players to it. Era: after Krayt's death the One Sith went underground, and this cell keeps relics taken from the academy. |

The dungeon was chosen over a quest chain because PL-02 already gives Ossus three short quests, and the owner asked for places that feel lived in and dangerous.

## Install order (the main session, with the server lock)

1. Apply on Core3-dev `7be8837a` (as swgemu), then run `check_lua.py`:
   ```bash
   wsl -d Debian -u swgemu -- git -C /opt/swg/Core3-dev apply /mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Fable-ossus/o8-world/server/core3-dev-ossus-world.patch
   ```
2. Restart the test galaxy under the standing OK (no owner client, no squad round). No archive change.

## Questions for the owner's visit (please answer in your own words)

1. Knossa (0 -3600): how full does the town feel now? Is anyone standing inside a wall or a tent?
2. Walk out of Knossa east onto the mesa (3000 -1500) and into Imhar Canyon (5150 100). How much wildlife do you meet, and is it too much or too little?
3. Visit the six places: (1408 -640), (2944 -1408), (4480 -1152), (-640 -384), (520 -1480), (-1408 2432). How do the tents and props sit on the ground,
   how do the fights feel, and what loot dropped?
4. The patrol on the road below the garrison (between 1740 2304 and 1983 2694): does it walk, and does it get stuck?
5. The dungeon (west foothill cave, -2976 -4978): were the acolytes and enforcers standing on the floor in each chamber? How hard was it,
   and did the Keeper drop something?
6. What still feels empty, and where?

## Terrain: what might look inaccurate (questions only, nothing changed)

Ossus in the Legends sources is the Adega system's forested Jedi world, with the Eocho Mountains, the Knossa region and the Great Library ruins.
Our terrain is Fable's O2-O7 design. These are the spots I would ask about:
1. **Too little forest?** Most of the planet is open plains and meadow. Should Ossus be mostly forest, with trees around the benchland and the old road?
2. **The east mesa** is a flat 104 m plateau spanning several kilometres. Does it look like Ossus, or like Tatooine?
3. **The pink benchland meadow** around the ruins (the `jedi_temple` shader family). Does the colour look right?
4. **The Eocho Mountains** south of Knossa: are they high and rugged enough for mountains?
5. **The lakes:** the water sits at 38.5 m and fills every low basin, so the west looks like wetland. Is that right?
6. **Imhar Canyon:** 100 m walls with a flat floor. Does it look carved, or blocky?
7. Is anything else wrong: a white or purple patch, a seam at the map edge, a field that looks cut out?

Answers here would become a terrain batch, and only with your OK.
