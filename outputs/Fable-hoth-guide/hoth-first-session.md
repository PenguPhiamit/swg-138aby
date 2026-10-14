# Your first Hoth session (test galaxy) — one route, 14 Oct 2026

Log in with `Play SWG Test Galaxy.cmd` (it loads `local_planets.tre` and the MTG archives; the live launcher does not).
"Verified" below means a bot did it on the test galaxy (Esk's trips on 14 Oct, the 09:48 content check, Pell's Botanist
check at 08:39). Everything else is staged and read-only checked, not yet seen in a client. Lines marked **[admin]** need
a staff character. Hoth creatures are level 62–115: take a geared character, or **[admin]** `/invulnerable` (God Mode
does not stop attacks). Bots walk on Hoth at normal speed; so should you.

## 1. Mos Eisley → Coronet → Hoth (verified: Esk, both directions)
- Mos Eisley Starport, pad at **3600, -4780**. The travel terminal stands inside the starport building, the ticket
  collector beside the landing pad. Ticket to Corellia: **600 credits**. Board the shuttle when it lands.
- Coronet Starport, pad at **-67, -4711**. Ticket to **Hoth: 3,000 credits**. Hoth must be in the destination list and
  on the galaxy map (a provisional spot on the right). If Hoth is missing: the client is not loading `local_planets.tre`.
- You land on the Scavenger Starport pad at **21, -1982** (height 0, in a flat bowl; the 43 m wall to the north is
  scenery, leave by the south). Return fare Hoth → Corellia: 1,750 credits.

## 2. The outpost: terminals and Quartermaster Vell (verified 09:48)
- `/waypoint 48 -1996` and `/waypoint 48 -2002`: two mission terminals (destroy and deliver missions, Hoth groups).
- `/waypoint 44 -2010`: Quartermaster Vell, standing still. His conversation opens with a choice. Take the first job:
  salvage tech Ria Baxx went out to the wreck's engine spur for a power regulator; she appears 600–900 m out with a
  waypoint, two ice mynocks (level 67) guard her, she hands over the "Salvaged Power Regulator"; 1,500 credits on return.
  Only the conversation is bot-verified; the job itself is not. If Vell says nothing or walks away: tell Claude (fix e9094960).

## 3. The planetary map (not yet verified: client-side files)
- Open the planetary map and tick **Points of Interest**: 18 Hoth markers with names and a description each (4 cave
  dens, 6 camps, 8 zones). Your location line at the outpost should read "Scavenger Starport".
- If the list is empty, or a name shows as `@clientpoi_n:hoth_...`: tell Claude which, and what Tatooine's list shows.

## 4. The salvage detail (verified 09:48: 5 NPCs)
- `/waypoint -100 -1960`, 150 m west of the pad: three Imperial salvage technicians and two snowtroopers among MTG's
  crash debris (Lucky Despot hull and engine, transport wreckage). No spawned props here by design, so the bot's
  "0 props" failure is the scenario's expectation, not a bug. Map marker and label: "Lucky Despot Wreck".

## 5. A camp (verified 09:48: NPCs and props at all six)
- `/waypoint -1400 -3300`, the Scavengers' Camp, 1.9 km south-west (walk out of the bowl to the south, then west, or
  **[admin]** `/teleport -1400 -3300 hoth`): six Hoth scavengers, a junk dealer, two tents, a campfire, a spit, cots.
  The Raiders' Camp 400 m east (**-1200, -3600**) is hostile: six scavenger raiders. Label: "Scavengers' Camp".

## 6. The ice caves (verified: spawns found in two caves; bosses not fought)
- 4.5 km north in the massif, each mouth a no-build circle. **[admin]** `/teleport -622 2292 hoth` for the first.
  Frostfang's Cavern (-622, 2292): Frostfang, 105. Icemaw's Den (-385, 2436): Icemaw, 105. Snowblind's Lair
  (-543, 2674): Snowblind the Ravager, 107. The Matriarch's Cavern (-75, 2969): the wampa patriarch, 115, and the
  matriarch, 110. Wampas 90 and elder wampas 98 fill the tunnels (129 spawns; 7-minute respawn, bosses 30 minutes).
- If a cave is empty or you fall through its floor: tell Claude the cave and the cell.

## 7. Surveying (not yet verified)
- Use any survey device anywhere outside the outpost. Hoth has its own 52 resource types, named "Hoth ..." (Wild Meat,
  Wooly Hide, Fiberplast, Water Vapor, Wind and Solar Renewable Energy, the foods and woods).
- Eleven MTG rows have no name in any client file (steel, iron, aluminum, copper, both ores, reactive gas, both
  petrochem fuels, radioactive, wild wheat): if a survey lists a blank or raw name, tell Claude which.

## 8. Loot (designed, not yet tried in game: dev b7f03b0e)
- Tauntauns (65) and ice mynocks (67) graze 250–350 m south of the pad. Ordinary Hoth creatures: 3% a common
  decoration. Sergeants and the named beasts (85–115): 5% a rare one. Named beasts only: 2% a vehicle deed (Bellum's
  18-deed list, some non-Hoth vehicles; the owner may trim it). A dropped item must show a proper name (merged CRC table).

## 9. Back in Mos Eisley: the Botanist (verified 08:39: Pell holds the box, the trainer answers)
- Hoth → Corellia (1,750), Corellia → Tatooine (600). The Botanist trainer stands at **3516, -4783** (dev 578861d9);
  the Novice box needs Hunting IV (`outdoors_scout_harvest_04`). Ask to train, then open the Skills window: "Botanist"
  under Outdoors, Novice plus four branches, with real names. A raw `@skl_n:outdoors_botanist...` means the skill
  strings in `local_planets.tre` are not loading: tell Claude.
